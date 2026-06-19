#!/usr/bin/env python3
"""Insight #96 MITM gate: probe known-good CONTROL hosts through the same path.
If controls return NORMAL content -> observation position clean -> suspect fleet is real deception.
If controls ALSO return the canned page -> VPN/local L7 rewriting contamination."""
import asyncio, aiohttp, json, ssl, base64
ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
TIMEOUT=12

CONTROLS = [
    ("example.com", 443, "/"),
    ("www.wikipedia.org", 443, "/"),
    ("api.github.com", 443, "/"),                       # real JSON API control
    ("scanme.nmap.org", 80, "/"),
]
SUSPECTS = [
    ("101.200.142.223", 7860, "/api/v1/version"),       # re-probe for stability
    ("104.237.139.130", 7860, "/api/v1/version"),
]

async def probe(session, host, port, path):
    scheme = "https" if port==443 else "http"
    u = f"{scheme}://{host}:{port}{path}"
    try:
        async with session.get(u, ssl=ctx, timeout=aiohttp.ClientTimeout(total=TIMEOUT)) as r:
            body = await r.text()
            import re
            title = re.search(r'<title[^>]*>(.*?)</title>', body, re.I|re.S)
            return {"host": host, "status": r.status, "server": r.headers.get("Server",""),
                    "ct": r.headers.get("Content-Type",""), "len": len(body),
                    "title": (title.group(1).strip()[:80] if title else None),
                    "head": body[:120]}
    except Exception as e:
        return {"host": host, "error": str(e)[:100]}

async def main():
    conn = aiohttp.TCPConnector(limit=10, ssl=ctx)
    async with aiohttp.ClientSession(connector=conn) as session:
        print("=== CONTROL HOSTS (known-good; must return NORMAL content) ===")
        for h,p,path in CONTROLS:
            r = await probe(session, h, p, path)
            if "error" in r: print(f"  {h}: ERR {r['error']}")
            else: print(f"  {h}: [{r['status']}] srv={r['server'][:25]} len={r['len']} title={r['title']!r}")
        print("\n=== SUSPECT HOSTS (re-probe for stability) ===")
        for h,p,path in SUSPECTS:
            r1 = await probe(session, h, p, path)
            r2 = await probe(session, h, p, path)
            print(f"  {h}{path}: probe1 srv={r1.get('server','')[:20]} len={r1.get('len')}  |  probe2 srv={r2.get('server','')[:20]} len={r2.get('len')}")
            print(f"      same body len both probes: {r1.get('len')==r2.get('len')}")

    # Decode the canned JWT
    jwt = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxMjMsInVzZXJuYW1lIjoiamFjayIsImV4cCI6MTc2MzcxNjY2NH0.ZtX7k3RJbWh919WUHQIDT39U0t6pEzTIdO24ED"
    parts = jwt.split(".")
    def b64d(s):
        s += "=" * (-len(s) % 4)
        return base64.urlsafe_b64decode(s)
    print("\n=== CANNED JWT DECODE (from /api/v1/auto_login) ===")
    print(f"  header:  {b64d(parts[0])}")
    print(f"  payload: {b64d(parts[1])}")
    import datetime
    pl = json.loads(b64d(parts[1]))
    exp = datetime.datetime.utcfromtimestamp(pl['exp'])
    print(f"  exp:     {exp} UTC  (now: 2026-06-18; expired={exp < datetime.datetime(2026,6,18)})")

asyncio.run(main())
