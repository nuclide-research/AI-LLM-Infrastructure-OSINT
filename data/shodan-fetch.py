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

# First-page fetch: returns count + page-1 IPs for each query.
JS_FIRST_PAGE = """
async (queries) => {
  const responses = await Promise.all(
    queries.map(q =>
      fetch(`https://www.shodan.io/search?query=${q}&page=1`, { credentials: 'include' })
        .then(r => r.text())
    )
  );
  return responses.map((html, i) => {
    const parser = new DOMParser();
    const doc = parser.parseFromString(html, 'text/html');
    const countText = doc.querySelector('h4.total-results')?.textContent.trim().replace(/,/g, '') ?? '0';
    const total = parseInt(countText, 10) || 0;
    const countFmt = doc.querySelector('h4.total-results')?.textContent.trim() ?? null;
    const ips = [...html.matchAll(/href="\\/host\\/(\\d+\\.\\d+\\.\\d+\\.\\d+)"/g)].map(m => m[1]);
    return { query: decodeURIComponent(queries[i]), total, count: countFmt, ips: [...new Set(ips)] };
  });
}
"""

# Bulk page fetch: fires arbitrary page numbers for a single query in parallel.
JS_PAGES = """
async (args) => {
  const { query, pages } = args;
  const responses = await Promise.all(
    pages.map(p =>
      fetch(`https://www.shodan.io/search?query=${query}&page=${p}`, { credentials: 'include' })
        .then(r => r.text())
    )
  );
  const allIPs = responses.flatMap(html =>
    [...html.matchAll(/href="\\/host\\/(\\d+\\.\\d+\\.\\d+\\.\\d+)"/g)].map(m => m[1])
  );
  return [...new Set(allIPs)];
}
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

        # Phase 1: fetch page 1 for all queries in parallel — get counts + first IPs
        for i in range(0, len(encoded), batch_size):
            batch = encoded[i : i + batch_size]
            batch_results = await page.evaluate(JS_FIRST_PAGE, batch)
            for r in batch_results:
                key = r["query"]
                total_pages = min(
                    (r["total"] + 9) // 10,  # ceil(total / 10)
                    max_pages if max_pages else 100
                )
                results[key] = {
                    "query": key,
                    "count": r["count"],
                    "total": r["total"],
                    "pages": total_pages,
                    "ips": list(r["ips"]),
                }
                print(
                    f"[*] {r['count'] or '?':>8}  ({total_pages} pages)  {key}",
                    file=sys.stderr,
                )

        # Phase 2: fire all remaining pages in parallel per query
        for enc_query, meta in zip(encoded, results.values()):
            remaining = list(range(2, meta["pages"] + 1))
            if not remaining:
                continue
            more_ips = await page.evaluate(
                JS_PAGES, {"query": enc_query, "pages": remaining}
            )
            meta["ips"].extend(more_ips)

        await browser.close()

    # Final dedup
    for r in results.values():
        r["ips"] = list(dict.fromkeys(r["ips"]))
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
        all_ips = list(dict.fromkeys(ip for r in results for ip in r["ips"]))
        if args.output:
            Path(args.output).write_text("\n".join(all_ips) + "\n")
            print(f"\n{len(all_ips)} IPs → {args.output}", file=sys.stderr)
        else:
            print("\n".join(all_ips))
    else:
        print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
