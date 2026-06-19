#!/usr/bin/env python3
"""Discriminate REAL Langflow from the catch-all deception fleet.
REAL Langflow: /api/v1/version returns "package":"Langflow" AND nonsense path 404s AND auto_login JWT works.
Fleet: catch-all 200, fake Gitea version, fake expired JWT."""
import asyncio, aiohttp, json, ssl
ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
TIMEOUT=10

# 3 port:7860 candidates from the earlier successful Shodan query (NOT in the 93 deception cohort)
CANDS = [
    ("172.241.24.136", [7860, 443, 80]),
    ("34.105.173.255", [7860, 443, 80]),
    ("24.152.39.20",   [7860, 443, 80]),
]

async def get(session, ip, port, path):
    scheme="https" if port==443 else "http"
    u=f"{scheme}://{ip}:{port}{path}"
    try:
        async with session.get(u, ssl=ctx, timeout=aiohttp.ClientTimeout(total=TIMEOUT)) as r:
            return r.status, (await r.text())
    except Exception as e:
        return None, str(e)[:80]

async def classify(session, ip, port):
    res={"ip":ip,"port":port,"verdict":"?","package":None,"version":None}
    vs, vb = await get(session, ip, port, "/api/v1/version")
    ns, nb = await get(session, ip, port, "/api/v1/zzz-catchall-nonsense-77")
    res["version_status"]=vs; res["nonsense_status"]=ns
    # Real Langflow: package:Langflow in version body, nonsense 404
    if vs==200 and '"package"' in (vb or "") and "Langflow" in (vb or ""):
        try:
            d=json.loads(vb); res["package"]=d.get("package"); res["version"]=d.get("version") or d.get("main_version")
        except: pass
        if ns in (404, 401, 403):
            res["verdict"]="REAL_LANGFLOW"
        else:
            res["verdict"]="AMBIGUOUS_catchall200_but_package"
    elif vs==200 and "gitea" in (vb or "").lower():
        res["verdict"]="DECEPTION_FLEET (fake gitea)"
    elif ns==200:
        res["verdict"]="CATCH-ALL (nonsense 200)"
    else:
        res["verdict"]="NOT_LANGFLOW / down"
    return res

async def main():
    conn=aiohttp.TCPConnector(limit=15, ssl=ctx)
    async with aiohttp.ClientSession(connector=conn) as session:
        for ip, ports in CANDS:
            print(f"\n{ip}:")
            for port in ports:
                r=await classify(session, ip, port)
                print(f"  :{port:5d} ver[{r['version_status']}] nonsense[{r['nonsense_status']}] -> {r['verdict']} pkg={r['package']} v={r['version']}")

asyncio.run(main())
