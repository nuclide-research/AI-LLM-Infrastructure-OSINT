#!/usr/bin/env python3
"""Probe /api/version on Ollama hosts with null version, patch state files in place.
CVE-2024-37032 (Probllama): path traversal -> RCE, affected < 0.1.34
"""

import asyncio
import json
import sys
from pathlib import Path
from packaging.version import Version, InvalidVersion

import aiohttp

CVE_FIX = Version("0.1.34")
TIMEOUT = aiohttp.ClientTimeout(total=7, connect=3)
CONCURRENCY = 80

STATE_FILES = [
    "ollama-state.json",
    "ollama-state-fresh.json",
    "ollama-univ-state.json",
    "ollama-gov-state.json",
    "ollama-health-state.json",
    "ollama-inst-state.json",
]
DATA_DIR = Path("/home/cowboy/AI-LLM-Infrastructure-OSINT/data")


def classify(ver: str) -> str:
    try:
        return "VULNERABLE" if Version(ver) < CVE_FIX else "PATCHED"
    except InvalidVersion:
        return "UNKNOWN"


async def probe(session: aiohttp.ClientSession, ip: str) -> str | None:
    url = f"http://{ip}:11434/api/version"
    try:
        async with session.get(url, ssl=False) as r:
            if r.status == 200:
                data = await r.json(content_type=None)
                return data.get("version")
    except Exception:
        pass
    return None


async def run():
    # Load all state files, collect null-version IPs
    states = {}
    null_ips = []

    for fname in STATE_FILES:
        path = DATA_DIR / fname
        with open(path) as f:
            data = json.load(f)
        states[fname] = data
        for ip, host in data.items():
            if not host.get("version"):
                null_ips.append(ip)

    print(f"Probing {len(null_ips)} null-version Ollama hosts...", file=sys.stderr)

    results = {}
    sem = asyncio.Semaphore(CONCURRENCY)
    connector = aiohttp.TCPConnector(ssl=False, limit=CONCURRENCY + 20)

    async with aiohttp.ClientSession(connector=connector, timeout=TIMEOUT) as session:
        async def bounded(ip):
            async with sem:
                ver = await probe(session, ip)
                return ip, ver

        tasks = [bounded(ip) for ip in null_ips]
        done = 0
        found = 0
        for coro in asyncio.as_completed(tasks):
            ip, ver = await coro
            results[ip] = ver
            done += 1
            if ver:
                found += 1
            if done % 100 == 0 or done == len(tasks):
                print(f"  [{done}/{len(tasks)}] resolved: {found}", file=sys.stderr)

    # Patch state files
    patched = 0
    for fname, data in states.items():
        changed = False
        for ip, host in data.items():
            if ip in results and results[ip]:
                host["version"] = results[ip]
                changed = True
                patched += 1
        if changed:
            path = DATA_DIR / fname
            with open(path, "w") as f:
                json.dump(data, f, indent=2)
            print(f"  patched {fname}")

    # Summary
    resolved = {ip: v for ip, v in results.items() if v}
    vuln = {ip: v for ip, v in resolved.items() if classify(v) == "VULNERABLE"}
    print(f"\nResolved: {len(resolved)}/{len(null_ips)}")
    print(f"Vulnerable (<0.1.34, CVE-2024-37032): {len(vuln)}")
    print(f"Patched (>=0.1.34): {len(resolved) - len(vuln)}")
    print(f"Still unknown: {len(null_ips) - len(resolved)}")

    if vuln:
        print("\nVULNERABLE HOSTS:")
        for ip, ver in sorted(vuln.items()):
            print(f"  {ip}:11434  v{ver}")

    # Write triage report
    out = Path("/home/cowboy/recon/ollama-version-sweep/ollama-version-triage.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w") as f:
        json.dump({
            "probed": len(null_ips),
            "resolved": len(resolved),
            "vulnerable": vuln,
            "results": results,
        }, f, indent=2)
    print(f"\nTriage saved: {out}")


if __name__ == "__main__":
    asyncio.run(run())
