#!/usr/bin/env python3
"""
GPT-SoVITS CVE surface probe — read-only.
CVE-2025-49833/34/35/36: unauthenticated RCE via command injection on ports 9871-9874/9880.
This script only checks port reachability and response content. No RCE paths invoked.
"""

import asyncio
import aiohttp
import json
from datetime import datetime

# All unique IPs harvested from Shodan
HOSTS = [
    # port:9872 dork
    "140.125.84.53",
    "117.50.138.228",
    # broad dork page 1
    "163.44.114.51",
    "167.179.114.97",
    "138.128.223.77",
    "160.251.201.109",
    "46.224.19.85",
    "47.96.133.226",
    "218.72.79.235",
    "43.167.209.235",
    "192.3.179.39",
    "114.55.73.133",
    # broad dork page 2
    "183.98.27.231",
    "104.171.202.229",
    "122.234.92.74",
    "106.75.1.212",
    "156.240.76.58",
    "47.108.192.1",
    "220.187.74.226",
    "125.125.133.225",
    # broad dork page 3
    "104.171.202.19",
    "173.231.48.180",
]

# CVE-affected ports
CVE_PORTS = [9871, 9872, 9873, 9874, 9880]
# All ports to check (including reverse-proxy common ports found in Shodan top ports)
ALL_PORTS = [9871, 9872, 9873, 9874, 9880, 80, 443, 8000, 8800]

TIMEOUT = 8
CONCURRENCY = 20

async def probe_port(session, ip, port):
    """Try GET / on a port, return (open, contains_sovits, status_code, server, title_snippet)."""
    for scheme in (["https", "http"] if port == 443 else ["http"]):
        url = f"{scheme}://{ip}:{port}/"
        try:
            async with session.get(url, allow_redirects=True, ssl=False) as resp:
                status = resp.status
                body = await resp.text(errors="replace")
                server = resp.headers.get("Server", "")
                body_lower = body.lower()
                contains_sovits = "gpt-sovits" in body_lower or "sovits" in body_lower
                # Extract title
                import re
                title_m = re.search(r"<title[^>]*>([^<]{0,100})</title>", body, re.I)
                title = title_m.group(1).strip() if title_m else ""
                return {
                    "port": port,
                    "scheme": scheme,
                    "open": True,
                    "status": status,
                    "server": server,
                    "contains_sovits": contains_sovits,
                    "title": title,
                }
        except Exception:
            continue
    return {"port": port, "open": False}

async def probe_9880_control(session, ip):
    """Check port 9880 /control endpoint — GPT-SoVITS API returns JSON."""
    url = f"http://{ip}:9880/control"
    try:
        async with session.get(url, ssl=False) as resp:
            body = await resp.text(errors="replace")
            return {"endpoint": "/control", "status": resp.status, "body_snippet": body[:200]}
    except Exception as e:
        return {"endpoint": "/control", "error": str(e)[:80]}

async def probe_host(session, ip, sem):
    async with sem:
        results = {"ip": ip, "ports": {}, "cve_surface": [], "notes": []}

        # Probe all ports
        tasks = [probe_port(session, ip, p) for p in ALL_PORTS]
        port_results = await asyncio.gather(*tasks)

        open_cve_ports = []
        for r in port_results:
            p = r["port"]
            results["ports"][p] = r
            if r.get("open") and p in CVE_PORTS:
                open_cve_ports.append(p)
                if r.get("contains_sovits"):
                    results["cve_surface"].append(p)

        # Extra check: port 9880 /control
        if results["ports"].get(9880, {}).get("open"):
            ctrl = await probe_9880_control(session, ip)
            results["ports"]["9880_control"] = ctrl

        if open_cve_ports:
            results["notes"].append(f"CVE-affected ports open: {open_cve_ports}")

        return results

async def main():
    sem = asyncio.Semaphore(CONCURRENCY)
    connector = aiohttp.TCPConnector(limit=CONCURRENCY, ssl=False)
    timeout = aiohttp.ClientTimeout(total=TIMEOUT)

    results = []
    async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
        tasks = [probe_host(session, ip, sem) for ip in HOSTS]
        results = await asyncio.gather(*tasks)

    # Summary
    total = len(results)
    open_any_cve = [r for r in results if any(r["ports"].get(p, {}).get("open") for p in CVE_PORTS)]
    sovits_confirmed = [r for r in results if r["cve_surface"]]

    print(f"\n=== GPT-SoVITS CVE Surface Probe ===")
    print(f"Total IPs probed: {total}")
    print(f"IPs with any CVE-port open: {len(open_any_cve)}")
    print(f"IPs with CVE-port open + GPT-SoVITS confirmed: {len(sovits_confirmed)}")
    print()

    for r in results:
        open_ports = [p for p in ALL_PORTS if r["ports"].get(p, {}).get("open")]
        cve_open = [p for p in CVE_PORTS if r["ports"].get(p, {}).get("open")]
        if open_ports:
            sovits_flag = " [GPT-SoVITS CONFIRMED]" if r["cve_surface"] else ""
            cve_flag = f" [CVE-PORTS: {cve_open}]" if cve_open else ""
            print(f"{r['ip']:20s}  open={open_ports}{cve_flag}{sovits_flag}")
            for p in open_ports:
                pr = r["ports"].get(p, {})
                if pr.get("open"):
                    print(f"  :{p}  {pr.get('status','')}  server={pr.get('server','')}  title={pr.get('title','')[:60]}")

    # Save full JSON
    out = {
        "timestamp": datetime.utcnow().isoformat(),
        "total_probed": total,
        "cve_ports_open_count": len(open_any_cve),
        "sovits_confirmed_on_cve_port": len(sovits_confirmed),
        "hosts": results,
    }
    with open("/home/cowboy/AI-LLM-Infrastructure-OSINT/recon/voice-audio-ai-2026-05-28/probe_results.json", "w") as f:
        json.dump(out, f, indent=2)
    print(f"\nFull results saved to probe_results.json")
    return out

if __name__ == "__main__":
    asyncio.run(main())
