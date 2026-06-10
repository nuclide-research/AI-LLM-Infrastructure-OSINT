#!/usr/bin/env python3
"""GET / on every host - what mask is the front-end wearing?"""
import json
import socket
import ssl
import sys
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path


def grab(ip, port=9090, timeout=6):
    ctx = ssl._create_unverified_context()
    out = {"ip": ip}
    for scheme in ("https", "http"):
        try:
            req = urllib.request.Request(f"{scheme}://{ip}:{port}/", headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=timeout, context=ctx) as r:
                body = r.read(4096).decode("utf-8", errors="replace")
                out["scheme"] = scheme
                out["status"] = r.status
                out["server"] = r.headers.get("Server", "")
                out["ctype"] = r.headers.get("Content-Type", "")
                # Title sniff
                lo = body.lower()
                title = ""
                if "<title>" in lo:
                    i = lo.index("<title>") + 7
                    j = lo.index("</title>", i) if "</title>" in lo[i:] else i + 80
                    title = body[i:j][:120]
                out["title"] = title
                out["body_head"] = body[:200]
                return out
        except urllib.error.HTTPError as e:
            try:
                body = e.read(2048).decode("utf-8", errors="replace")
            except Exception:
                body = ""
            out["scheme"] = scheme
            out["status"] = e.code
            out["server"] = e.headers.get("Server", "") if e.headers else ""
            out["body_head"] = body[:200]
            return out
        except Exception as e:
            out[f"{scheme}_err"] = f"{type(e).__name__}: {e}"
    return out


def main():
    ips = [x.strip() for x in Path(sys.argv[1]).read_text().splitlines() if x.strip()]
    results = []
    with ThreadPoolExecutor(max_workers=10) as ex:
        futs = {ex.submit(grab, ip): ip for ip in ips}
        for f in as_completed(futs):
            results.append(f.result())
    Path(sys.argv[2]).write_text(json.dumps(results, indent=2))
    from collections import Counter
    servers = Counter()
    titles = Counter()
    for r in results:
        servers[r.get("server") or "?"] += 1
        titles[(r.get("title") or "")[:80] or "?"] += 1
    print(f"servers: {dict(servers.most_common(20))}")
    print(f"titles: {dict(titles.most_common(20))}")


if __name__ == "__main__":
    main()
