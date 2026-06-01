#!/usr/bin/env python3
"""
shodan-fetch — authenticated Shodan web scraper.
Uses browser session cookies to bypass API rate limits.

Usage:
  shodan-fetch --login                             # first run: save session
  shodan-fetch 'http.title:"MLflow"'               # single dork
  shodan-fetch --file dorks.txt                    # batch from file
  shodan-fetch --file dorks.txt --pages 5          # paginate results
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

JS_FETCH = """
async (args) => {
  const { queries, page_num } = args;
  const responses = await Promise.all(
    queries.map(q =>
      fetch(`https://www.shodan.io/search?query=${q}&page=${page_num}`, { credentials: 'include' })
        .then(r => r.text())
    )
  );
  return responses.map((html, i) => {
    const parser = new DOMParser();
    const doc = parser.parseFromString(html, 'text/html');
    const count = doc.querySelector('h4.total-results')?.textContent.trim() ?? null;
    const ips = [...html.matchAll(/href="\\/host\\/(\\d+\\.\\d+\\.\\d+\\.\\d+)"/g)].map(m => m[1]);
    return { query: decodeURIComponent(queries[i]), count, ips: [...new Set(ips)] };
  });
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


async def run(queries: list[str], pages: int, batch_size: int) -> list[dict]:
    if not SESSION_FILE.exists():
        print(f"No session found. Run: shodan-fetch --login", file=sys.stderr)
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

        for page_num in range(1, pages + 1):
            for i in range(0, len(encoded), batch_size):
                batch = encoded[i : i + batch_size]
                batch_results = await page.evaluate(JS_FETCH, {"queries": batch, "page_num": page_num})
                for r in batch_results:
                    key = r["query"]
                    if key not in results:
                        results[key] = {"query": key, "count": r["count"], "ips": []}
                    results[key]["ips"].extend(r["ips"])
                    if r["count"] and results[key]["count"] is None:
                        results[key]["count"] = r["count"]

        await browser.close()

    for r in results.values():
        r["ips"] = list(dict.fromkeys(r["ips"]))

    return list(results.values())


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Authenticated Shodan web scraper — no API tokens needed."
    )
    ap.add_argument("queries", nargs="*", help="Shodan dork(s)")
    ap.add_argument("--login", action="store_true", help="Open browser, save session")
    ap.add_argument("--file", "-f", help="File with one dork per line (# = comment)")
    ap.add_argument("--pages", "-p", type=int, default=1, help="Result pages per query (default: 1)")
    ap.add_argument("--batch-size", type=int, default=20, help="Parallel fetch batch size (default: 20)")
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

    results = asyncio.run(run(queries, pages=args.pages, batch_size=args.batch_size))

    if args.output or args.ips_only:
        all_ips = list(dict.fromkeys(ip for r in results for ip in r["ips"]))
        if args.output:
            Path(args.output).write_text("\n".join(all_ips) + "\n")
            print(f"{len(all_ips)} IPs → {args.output}", file=sys.stderr)
            for r in results:
                print(f"  {r['count']:>8}  {r['query']}", file=sys.stderr)
        else:
            print("\n".join(all_ips))
    else:
        print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
