#!/usr/bin/env python3
"""
shodan-fetch — authenticated Shodan web scraper.
Uses browser session cookies to bypass API rate limits.

Usage:
  shodan-fetch --login                             # first run: save session
  shodan-fetch 'http.title:"MLflow"'               # single dork — auto-paginates all results
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

SESSION_FILE = Path.home() / ".config" / "shodan-fetch" / "session.json"

_EXTRACT_HOSTS = """
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
      const items = [...sslEl.querySelectorAll('li')].map(li => li.textContent.replace(/\\s+/g, ' ').trim());
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

    return {{ query: decodeURIComponent(queries[i]), total, count: countFmt, countries, facets, hosts: extractHosts(doc) }};
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
    SESSION_FILE.parent.mkdir(parents=True, exist_ok=True)
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        ctx = await browser.new_context()
        page = await ctx.new_page()
        await page.goto("https://account.shodan.io")
        print("Log in to Shodan, then press Enter here...", flush=True)
        input()
        await ctx.storage_state(path=str(SESSION_FILE))
        await browser.close()
    print(f"Session saved → {SESSION_FILE}", file=sys.stderr)


async def run(queries: list[str], max_pages: int, batch_size: int) -> list[dict]:
    if not SESSION_FILE.exists():
        print("No session found. Run: shodan-fetch --login", file=sys.stderr)
        sys.exit(1)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        ctx = await browser.new_context(storage_state=str(SESSION_FILE))
        page = await ctx.new_page()

        await page.route("**/*", lambda route: (
            route.abort()
            if route.request.resource_type in ("image", "stylesheet", "font", "media")
            else route.continue_()
        ))

        await page.goto("https://www.shodan.io", wait_until="domcontentloaded")

        encoded = [quote(q, safe="") for q in queries]
        results: dict[str, dict] = {}

        # Phase 1: page 1 for all queries in parallel — get counts + first hosts
        for i in range(0, len(encoded), batch_size):
            batch = encoded[i : i + batch_size]
            batch_results = await page.evaluate(JS_FIRST_PAGE, batch)
            for r in batch_results:
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

        # Phase 2: remaining pages per query, all in parallel
        for enc_query, meta in zip(encoded, results.values()):
            remaining = list(range(2, meta["pages"] + 1))
            if not remaining:
                continue
            more_hosts = await page.evaluate(
                JS_PAGES, {"query": enc_query, "pages": remaining}
            )
            meta["hosts"].extend(more_hosts)

        await browser.close()

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
        description="Authenticated Shodan web scraper — auto-paginates all results, no API tokens needed."
    )
    ap.add_argument("queries", nargs="*", help="Shodan dork(s)")
    ap.add_argument("--login", action="store_true", help="Open browser, save session")
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
            print(f"\n{len(all_ips)} IPs → {args.output}", file=sys.stderr)
        else:
            print("\n".join(all_ips))
    else:
        print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
