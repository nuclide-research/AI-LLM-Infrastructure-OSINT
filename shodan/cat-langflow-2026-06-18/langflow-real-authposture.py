#!/usr/bin/env python3
"""Auth posture of CONFIRMED-REAL Langflow. Restraint: functional JWT test + NAMES/COUNTS only."""
import asyncio, aiohttp, json, ssl
ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
TIMEOUT=12

REAL = [("172.241.24.136",443),("24.152.39.20",7860)]

async def get(session, ip, port, path, hdr=None):
    scheme="https" if port==443 else "http"
    try:
        async with session.get(f"{scheme}://{ip}:{port}{path}", ssl=ctx, headers=hdr or {},
                               timeout=aiohttp.ClientTimeout(total=TIMEOUT)) as r:
            return r.status, (await r.text())
    except Exception as e:
        return None, str(e)[:80]

async def assess(session, ip, port):
    r={"ip":ip,"port":port}
    # version
    vs,vb=await get(session,ip,port,"/api/v1/version")
    try: r["version"]=json.loads(vb).get("version")
    except: r["version"]=None
    # auto_login
    als,alb=await get(session,ip,port,"/api/v1/auto_login")
    r["auto_login_status"]=als
    token=None
    if als==200 and "access_token" in (alb or ""):
        try: token=json.loads(alb).get("access_token")
        except: pass
    r["got_token"]=bool(token)
    hdr={"Authorization":f"Bearer {token}"} if token else {}
    # flows with token -> functional check + NAME/COUNT only
    fs,fb=await get(session,ip,port,"/api/v1/flows/?header_flows=true",hdr)
    r["flows_status"]=fs
    if fs==200:
        try:
            d=json.loads(fb); flows=d if isinstance(d,list) else d.get("flows",[])
            r["flow_count"]=len(flows); r["flow_names"]=[f.get("name","?") for f in flows][:25]
            r["jwt_works"]=True
        except: r["jwt_works"]=False
    else:
        r["jwt_works"]=False
    # variables -> NAME+TYPE only (NEVER values)
    vrs,vrb=await get(session,ip,port,"/api/v1/variables/",hdr)
    r["variables_status"]=vrs
    if vrs==200:
        try:
            d=json.loads(vrb); vs2=d if isinstance(d,list) else d.get("variables",[])
            r["var_count"]=len(vs2)
            r["var_names"]=[{"name":v.get("name","?"),"type":v.get("type","?")} for v in vs2][:25]
        except: pass
    # config keys
    cs,cb=await get(session,ip,port,"/api/v1/config",hdr)
    r["config_status"]=cs
    if cs==200:
        try: r["config_keys"]=sorted(json.loads(cb).keys())
        except: pass
    return r

async def main():
    conn=aiohttp.TCPConnector(limit=10, ssl=ctx)
    async with aiohttp.ClientSession(connector=conn) as session:
        out=[]
        for ip,port in REAL:
            r=await assess(session, ip, port)
            out.append(r)
            print(f"\n{'='*60}\n{ip}:{port}  Langflow v{r.get('version')}\n{'='*60}")
            print(f"  auto_login: [{r['auto_login_status']}] token={r['got_token']}")
            print(f"  JWT authenticates flow API: {r['jwt_works']}  (THE open-superuser proof)")
            print(f"  flows:     [{r['flows_status']}] count={r.get('flow_count')}")
            if r.get('flow_names'): print(f"    flow NAMES: {r['flow_names']}")
            print(f"  variables: [{r['variables_status']}] count={r.get('var_count')}")
            if r.get('var_names'): print(f"    var NAMES+TYPES (key inventory): {r['var_names']}")
            print(f"  config:    [{r['config_status']}] keys={r.get('config_keys')}")
        with open("/home/cowboy/AI-LLM-Infrastructure-OSINT/shodan/cat-langflow-2026-06-18/real-langflow-authposture.json","w") as f:
            json.dump(out,f,indent=2)

asyncio.run(main())
