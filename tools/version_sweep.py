#!/usr/bin/env python3
"""LiteLLM version sweeper — CVE-2026-42208 triage.
Probes /openapi.json (info.version) then /health/readiness (litellm_version).
Outputs CSV: target,version,auth_state,vulnerable,method
"""

import asyncio
import csv
import json
import re
import sys
import time
from packaging.version import Version, InvalidVersion

import aiohttp

VULN_LOW = Version("1.81.16")
VULN_HIGH = Version("1.83.6")
TIMEOUT = aiohttp.ClientTimeout(total=8, connect=4)
CONCURRENCY = 80

VERSION_RE = re.compile(r'"version"\s*:\s*"([^"]+)"')
LITELLM_VER_RE = re.compile(r'"litellm_version"\s*:\s*"([^"]+)"')


def classify(ver_str: str):
    try:
        v = Version(ver_str)
        if VULN_LOW <= v <= VULN_HIGH:
            return "VULNERABLE"
        elif v > VULN_HIGH:
            return "PATCHED"
        else:
            return "BELOW_RANGE"
    except InvalidVersion:
        return "UNKNOWN"


async def probe_host(session: aiohttp.ClientSession, target: str) -> dict:
    base = target.rstrip("/")
    result = {"target": target, "version": "", "auth_state": "", "vulnerable": "", "method": ""}

    for path, extractor in [
        ("/openapi.json", lambda t: VERSION_RE.search(t)),
        ("/health/readiness", lambda t: LITELLM_VER_RE.search(t)),
    ]:
        url = base + path
        try:
            async with session.get(url, ssl=False, allow_redirects=True) as r:
                if r.status in (200, 206):
                    body = await r.text(errors="ignore")
                    m = extractor(body)
                    if m:
                        ver = m.group(1)
                        result["version"] = ver
                        result["vulnerable"] = classify(ver)
                        result["method"] = path
                        result["auth_state"] = "unauth"
                        return result
                    # Got 200 but no version field — still open
                    result["auth_state"] = "unauth"
                elif r.status in (401, 403):
                    result["auth_state"] = "auth"
        except Exception:
            pass

    return result


async def run(targets: list[str], out_path: str):
    sem = asyncio.Semaphore(CONCURRENCY)
    rows = []

    connector = aiohttp.TCPConnector(ssl=False, limit=CONCURRENCY + 20)
    async with aiohttp.ClientSession(connector=connector, timeout=TIMEOUT) as session:

        async def bounded(t):
            async with sem:
                return await probe_host(session, t)

        tasks = [bounded(t) for t in targets]
        total = len(tasks)
        done = 0
        for coro in asyncio.as_completed(tasks):
            r = await coro
            rows.append(r)
            done += 1
            if done % 50 == 0 or done == total:
                vuln = sum(1 for x in rows if x["vulnerable"] == "VULNERABLE")
                print(f"  [{done}/{total}] vulnerable so far: {vuln}", file=sys.stderr)

    with open(out_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["target", "version", "auth_state", "vulnerable", "method"])
        w.writeheader()
        # sort: vulnerable first, then patched, then rest
        order = {"VULNERABLE": 0, "PATCHED": 1, "BELOW_RANGE": 2, "UNKNOWN": 3, "": 4}
        rows.sort(key=lambda x: (order.get(x["vulnerable"], 9), x["target"]))
        w.writerows(rows)

    vuln = [r for r in rows if r["vulnerable"] == "VULNERABLE"]
    unauth_vuln = [r for r in vuln if r["auth_state"] == "unauth"]
    print(f"\nTotal probed: {len(rows)}")
    print(f"Vulnerable (1.81.16-1.83.6): {len(vuln)}")
    print(f"  - Unauth + Vulnerable: {len(unauth_vuln)}")
    print(f"Patched: {sum(1 for r in rows if r['vulnerable'] == 'PATCHED')}")
    print(f"Below range: {sum(1 for r in rows if r['vulnerable'] == 'BELOW_RANGE')}")
    print(f"Unknown/no version: {sum(1 for r in rows if not r['version'])}")
    print(f"Output: {out_path}")


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("input", help="File with one target URL per line, or - for stdin")
    p.add_argument("-o", "--output", default="litellm-cve-triage.csv")
    args = p.parse_args()

    if args.input == "-":
        targets = [l.strip() for l in sys.stdin if l.strip()]
    else:
        with open(args.input) as f:
            targets = [l.strip() for l in f if l.strip()]

    print(f"Probing {len(targets)} targets...", file=sys.stderr)
    asyncio.run(run(targets, args.output))
