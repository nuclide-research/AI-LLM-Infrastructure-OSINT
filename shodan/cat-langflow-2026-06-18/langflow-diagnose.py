#!/usr/bin/env python3
"""Diagnose what the 'Langflow' cohort actually is. Catch-all test + full body capture."""
import asyncio, aiohttp, json, ssl
ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
TIMEOUT=10

# 2 cluster IPs + 3 single-port IPs
SAMPLES = [
    ("101.200.142.223", 7860),   # cluster
    ("104.237.139.130", 7860),   # cluster (Akamai US)
    ("23.239.11.153", 7860),     # single-port
    ("45.33.90.253", 443),       # single-port https
    ("97.107.132.190", 3000),    # single-port
]

PATHS = [
    "/api/v1/health_check",
    "/api/v1/version",
    "/api/v1/config",
    "/api/v1/auto_login",
    "/api/v1/flows/",
    "/api/v1/nonsense-catchall-xyz-12345",   # catch-all discriminator
    "/this-path-does-not-exist-99999",       # catch-all discriminator 2
    "/",                                       # root
]

async def get(session, ip, port, path):
    scheme = "https" if port==443 else "http"
    u = f"{scheme}://{ip}:{port}{path}"
    try:
        async with session.get(u, ssl=ctx, timeout=aiohttp.ClientTimeout(total=TIMEOUT)) as r:
            body = await r.text()
            server = r.headers.get("Server","")
            ct = r.headers.get("Content-Type","")
            return {"status": r.status, "server": server, "ct": ct, "len": len(body), "body": body[:240]}
    except Exception as e:
        return {"error": str(e)[:80]}

async def main():
    conn = aiohttp.TCPConnector(limit=20, ssl=ctx)
    async with aiohttp.ClientSession(connector=conn) as session:
        for ip, port in SAMPLES:
            print(f"\n{'='*70}\n{ip}:{port}\n{'='*70}")
            for path in PATHS:
                r = await get(session, ip, port, path)
                if "error" in r:
                    print(f"  {path:45s} ERR {r['error']}")
                else:
                    print(f"  {path:45s} [{r['status']}] srv={r['server'][:20]} ct={r['ct'][:25]} len={r['len']}")
                    print(f"      body: {r['body'][:160]!r}")

asyncio.run(main())
