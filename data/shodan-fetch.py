#!/usr/bin/env python3
"""
shodan-fetch — authenticated Shodan web scraper.

Harvests Shodan's web UI through a real logged-in browser session, so it returns
the same per-host data and facets the API would, without spending API query
credits or a token.

How it works (the method this tool automates, exactly as it was derived):
  1. ONE AUTHENTICATED BROWSER. A persistent Chrome profile holds a real
     logged-in Shodan session (cookies), reused across every run. Not a token,
     not a frozen snapshot — a durable browser login, the way a human stays
     signed in. `--login` opens it once; it persists.
  2. ASSETS STRIPPED. The harvest uses fetch(), which pulls only the search
     HTML. Images / CSS / fonts / the map widget are never requested, so each
     query is a single small round-trip instead of a 5-10s full page load.
  3. EVERYTHING IN PARALLEL. All queries — and all pages of each query — fire at
     once via Promise.all inside the page context, where the session cookie
     rides automatically (credentials:'include').
  4. PARSE THE SSR HTML. Shodan renders every result card, facet, and the
     country breakdown server-side, so the one HTML response IS the data. There
     is no hidden API (verified at the DevTools network layer).

Usage:
  shodan-fetch --login                             # once: log in, profile persists
  shodan-fetch 'http.title:"MLflow"'               # single dork — auto-paginates
  shodan-fetch --file dorks.txt                    # batch from file
  shodan-fetch --file dorks.txt --max-pages 50     # cap pages per query (default: all)
  shodan-fetch --file dorks.txt --ips-only         # flat IP list
  shodan-fetch --file dorks.txt --ips-only | jaxen import --no-lookup
"""

import argparse
import asyncio
import json
import sys
from pathlib import Path
from urllib.parse import quote

from playwright.async_api import async_playwright

CONFIG_DIR = Path.home() / ".config" / "shodan-fetch"
PROFILE_DIR = CONFIG_DIR / "profile"          # persistent logged-in browser profile
LEGACY_SESSION = CONFIG_DIR / "session.json"  # old storage_state snapshot (auto-imported once)

_EXTRACT_HOSTS = r"""
function extractHosts(doc) {
  return [...doc.querySelectorAll('div.result')].map(card => {
    // IP + port
    const ip = card.querySelector('.heading a[href^="/host/"]')
      ?.getAttribute('href').replace('/host/', '') ?? null;
    const extHref = card.querySelector('.heading a.text-danger')?.getAttribute('href') ?? '';
    const portMatch = extHref.match(/:(\d+)$/);
    const port = portMatch ? parseInt(portMatch[1], 10) : null;
    const timestamp = card.querySelector('.heading .timestamp')?.textContent.trim() ?? null;

    // Identity
    const hostnames = [...card.querySelectorAll('li.hostnames.text-secondary')]
      .map(li => li.textContent.trim()).filter(h => h && h !== ip);
    const org     = card.querySelector('a.filter-org')?.textContent.trim() ?? null;
    const country = card.querySelector('a[href*="country%3A"]')?.textContent.trim() ?? null;
    const city    = card.querySelector('a[href*="city%3A"]')?.textContent.trim() ?? null;

    // HTTP banner (raw response headers)
    const banner = card.querySelector('div.banner-data pre')?.textContent.trim() ?? null;

    // SSL certificate
    const sslEl = card.querySelector('div.tile-ssl');
    let ssl = null;
    if (sslEl) {
      const tlsEl = sslEl.querySelector('strong:last-of-type');
      ssl = {
        issuer_org:    sslEl.querySelector('li span + ul li strong')?.textContent.trim() ?? null,
        subject_cn:    [...sslEl.querySelectorAll('li')].find(li => li.textContent.includes('Common Name:') && !li.textContent.includes('Issued By'))
                         ?.querySelector('strong')?.textContent.trim() ?? null,
        tls_versions:  tlsEl?.textContent.trim() ?? null,
      };
    }

    // Technology stack
    const components = [...card.querySelectorAll('li.components a[aria-label]')]
      .map(a => a.getAttribute('aria-label')).filter(Boolean);

    // Tags
    const tags = [...card.querySelectorAll('a.tag')]
      .map(a => a.textContent.trim()).filter(Boolean);

    return { ip, port, hostnames, org, country, city, timestamp, banner, ssl, components, tags };
  }).filter(h => h.ip);
}
"""

JS_FIRST_PAGE = f"""
async (queries) => {{
  {_EXTRACT_HOSTS}
  const responses = await Promise.all(
    queries.map(q =>
      fetch(`https://www.shodan.io/search?query=${{q}}&page=1`, {{ credentials: 'include' }})
        .then(r => r.text())
    )
  );
  return responses.map((html, i) => {{
    const parser = new DOMParser();
    const doc = parser.parseFromString(html, 'text/html');
    const countText = doc.querySelector('h4.total-results')?.textContent.trim().replace(/,/g, '') ?? '0';
    const total = parseInt(countText, 10) || 0;
    const countFmt = doc.querySelector('h4.total-results')?.textContent.trim() ?? null;

    // World map country breakdown (full population)
    const worldMatch = html.match(/const WORLD_MAP_DATA = ({{[^}}]+}})/);
    const countries = worldMatch ? JSON.parse(worldMatch[1]) : null;

    // Facet summaries from sidebar
    const facets = {{}};
    const WANTED = new Set(['Top Countries','Top Ports','Top Organizations','Top Products','Top Operating Systems']);
    doc.querySelectorAll('h6').forEach(h6 => {{
      const label = h6.textContent.trim();
      if (!WANTED.has(label)) return;
      const ul = h6.nextElementSibling;
      if (!ul || ul.tagName !== 'UL') return;
      facets[label] = [...ul.querySelectorAll('li:not(:last-child)')].map(li => {{
        const link = li.querySelector('a');
        const count = li.querySelector('span');
        return {{ label: link?.textContent.trim(), count: count?.textContent.trim() }};
      }}).filter(f => f.label && f.count);
    }});

    // Auth signal: the logged-out search page serves the "Login with Shodan" form.
    const authed = !html.includes('Login with');

    return {{ query: decodeURIComponent(queries[i]), total, count: countFmt, countries, facets, authed, hosts: extractHosts(doc) }};
  }});
}}
"""

JS_PAGES = f"""
async (args) => {{
  {_EXTRACT_HOSTS}
  const {{ query, pages }} = args;
  const responses = await Promise.all(
    pages.map(p =>
      fetch(`https://www.shodan.io/search?query=${{query}}&page=${{p}}`, {{ credentials: 'include' }})
        .then(r => r.text())
    )
  );
  return responses.flatMap(html => {{
    const parser = new DOMParser();
    const doc = parser.parseFromString(html, 'text/html');
    return extractHosts(doc);
  }});
}}
"""


async def login() -> None:
    """Open the persistent profile headed so the user logs in once; the login
    then lives in the profile and is reused by every subsequent run."""
    PROFILE_DIR.mkdir(parents=True, exist_ok=True)
    async with async_playwright() as p:
        ctx = await p.chromium.launch_persistent_context(str(PROFILE_DIR), headless=False)
        page = ctx.pages[0] if ctx.pages else await ctx.new_page()
        await page.goto("https://account.shodan.io/login")
        print("Log in to Shodan in the browser window, then press Enter here...", flush=True)
        input()
        await ctx.close()
    print(f"Login persisted -> {PROFILE_DIR}", file=sys.stderr)


async def _open_authed(p, headless=True):
    """Open the persistent (logged-in) context and verify the session is live.
    One-time: if the profile is fresh but a legacy session.json snapshot exists,
    import its cookies so the upgrade from the old format is seamless."""
    if not PROFILE_DIR.exists() and not LEGACY_SESSION.exists():
        print("No login found. Run: shodan-fetch --login", file=sys.stderr)
        sys.exit(1)
    ctx = await p.chromium.launch_persistent_context(str(PROFILE_DIR), headless=headless)
    page = ctx.pages[0] if ctx.pages else await ctx.new_page()

    # Seamless migration from the legacy storage_state snapshot.
    existing = await ctx.cookies("https://www.shodan.io")
    if not existing and LEGACY_SESSION.exists():
        try:
            state = json.loads(LEGACY_SESSION.read_text())
            if state.get("cookies"):
                await ctx.add_cookies(state["cookies"])
                print("[*] imported legacy session.json into persistent profile", file=sys.stderr)
        except Exception as e:
            print(f"warn: legacy import failed: {e}", file=sys.stderr)

    # Auth gate: the account page bounces to /login when the session is dead.
    await page.goto("https://account.shodan.io/", wait_until="domcontentloaded")
    if "/login" in page.url:
        print("Session expired or not logged in. Run: shodan-fetch --login", file=sys.stderr)
        await ctx.close()
        sys.exit(3)
    return ctx, page


async def run(queries: list[str], max_pages: int, batch_size: int) -> list[dict]:
    async with async_playwright() as p:
        ctx, page = await _open_authed(p, headless=True)

        # Step 2: strip assets. Speeds the one bootstrap navigation below; the
        # fetch() harvest never requests images in the first place.
        await page.route("**/*", lambda route: (
            route.abort()
            if route.request.resource_type in ("image", "stylesheet", "font", "media")
            else route.continue_()
        ))

        await page.goto("https://www.shodan.io", wait_until="domcontentloaded")

        encoded = [quote(q, safe="") for q in queries]
        results: dict[str, dict] = {}

        # Phase 1: page 1 of every query, all in parallel — counts + first hosts.
        for i in range(0, len(encoded), batch_size):
            batch = encoded[i : i + batch_size]
            batch_results = await page.evaluate(JS_FIRST_PAGE, batch)
            for r in batch_results:
                if not r.get("authed", True):
                    print("Session expired mid-run. Run: shodan-fetch --login", file=sys.stderr)
                    await ctx.close()
                    sys.exit(3)
                key = r["query"]
                total_pages = min(
                    (r["total"] + 9) // 10,
                    max_pages if max_pages else 100
                )
                results[key] = {
                    "query": key,
                    "count": r["count"],
                    "total": r["total"],
                    "pages": total_pages,
                    "countries": r.get("countries"),
                    "facets": r.get("facets", {}),
                    "hosts": r["hosts"],
                }
                print(
                    f"[*] {r['count'] or '?':>8}  ({total_pages} pages)  {key}",
                    file=sys.stderr,
                )

        # Phase 2: remaining pages per query, all in parallel.
        for enc_query, meta in zip(encoded, results.values()):
            remaining = list(range(2, meta["pages"] + 1))
            if not remaining:
                continue
            more_hosts = await page.evaluate(
                JS_PAGES, {"query": enc_query, "pages": remaining}
            )
            meta["hosts"].extend(more_hosts)

        await ctx.close()

    # Dedup by IP, strip internal fields
    for r in results.values():
        seen: set[str] = set()
        deduped = []
        for h in r["hosts"]:
            if h["ip"] not in seen:
                seen.add(h["ip"])
                deduped.append(h)
        r["hosts"] = deduped
        r.pop("pages", None)
        r.pop("total", None)

    return list(results.values())


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Authenticated Shodan web scraper — persistent logged-in browser, no API tokens."
    )
    ap.add_argument("queries", nargs="*", help="Shodan dork(s)")
    ap.add_argument("--login", action="store_true", help="Open browser, log in once (persists)")
    ap.add_argument("--file", "-f", help="File with one dork per line (# = comment)")
    ap.add_argument("--max-pages", type=int, default=0,
                    help="Cap pages per query (default: 0 = all, hard cap 100)")
    ap.add_argument("--batch-size", type=int, default=20,
                    help="Queries per parallel batch (default: 20)")
    ap.add_argument("--ips-only", action="store_true", help="Output flat deduplicated IP list")
    ap.add_argument("--output", "-o", help="Write IPs to file (implies --ips-only)")
    args = ap.parse_args()

    if args.login:
        asyncio.run(login())
        return

    queries = list(args.queries)
    if args.file:
        lines = Path(args.file).read_text().splitlines()
        queries += [l.strip() for l in lines if l.strip() and not l.startswith("#")]

    if not queries:
        ap.print_help()
        sys.exit(1)

    results = asyncio.run(run(queries, max_pages=args.max_pages, batch_size=args.batch_size))

    if args.output or args.ips_only:
        all_ips = list(dict.fromkeys(h["ip"] for r in results for h in r["hosts"]))
        if args.output:
            Path(args.output).write_text("\n".join(all_ips) + "\n")
            print(f"\n{len(all_ips)} IPs -> {args.output}", file=sys.stderr)
        else:
            print("\n".join(all_ips))
    else:
        print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
