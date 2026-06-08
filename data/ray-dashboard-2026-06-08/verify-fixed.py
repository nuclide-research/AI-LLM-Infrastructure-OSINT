#!/usr/bin/env python3
"""Ray Dashboard auth verifier — corrected to /api/jobs/ (ShadowRay primitive)."""
import concurrent.futures as cf, json, socket, ssl, sys, urllib.request, urllib.error
from pathlib import Path
TIMEOUT, HEADERS = 6, {"User-Agent": "NuClide-Research/ray-dashboard-2026-06-08-fixed"}
CTX = ssl.create_default_context(); CTX.check_hostname=False; CTX.verify_mode=ssl.CERT_NONE
def probe(ip_port):
    ip, port = ip_port.split(":"); port = int(port)
    out = {"ip": ip, "port": port, "verdict": "unknown"}
    for sc in (("http","https") if port not in (443,8443) else ("https",)):
        try:
            req = urllib.request.Request(f"{sc}://{ip}:{port}/api/jobs/", headers=HEADERS)
            with urllib.request.urlopen(req, timeout=TIMEOUT, context=CTX) as r:
                body = r.read(500_000).decode("utf-8","replace")
                try: doc = json.loads(body)
                except json.JSONDecodeError:
                    out["verdict"]="fp_jobs_not_json"; return out
                if isinstance(doc, list):
                    out["verdict"]="unauth_ray_jobs_confirmed"; out["scheme"]=sc
                    out["job_count"] = len(doc)
                    statuses = {}
                    submission_prefixes = []
                    for j in doc[:200]:
                        if isinstance(j, dict):
                            s = j.get("status") or "?"
                            statuses[s] = statuses.get(s,0)+1
                            sid = j.get("submission_id","") or ""
                            if sid:
                                submission_prefixes.append(sid[:25])
                    out["job_status_mix"] = statuses
                    out["job_id_sample"] = submission_prefixes[:10]
                    return out
                out["verdict"]="fp_jobs_shape"; return out
        except urllib.error.HTTPError as e:
            if e.code in (401,403): out["verdict"]=f"auth_gated_{e.code}"; return out
            continue
        except (urllib.error.URLError, socket.timeout, ConnectionResetError, ConnectionRefusedError, ssl.SSLError, OSError): continue
        except Exception as e: out["verdict"]=f"err_{type(e).__name__}"; return out
    out["verdict"]="dead"; return out

pairs = [l.strip() for l in Path(sys.argv[1]).read_text().splitlines() if l.strip()]
print(f"[*] probing {len(pairs)} hosts (workers=300)...", file=sys.stderr)
results = []
with cf.ThreadPoolExecutor(300) as ex:
    for i,r in enumerate(ex.map(probe, pairs)):
        results.append(r)
        if (i+1)%250==0: print(f"[*] {i+1}/{len(pairs)}", file=sys.stderr)
Path(sys.argv[2]).write_text("\n".join(json.dumps(r) for r in results))
from collections import Counter
tally = Counter(r["verdict"] for r in results)
print("\n[TALLY]", file=sys.stderr)
for k,v in tally.most_common(): print(f"  {v:5d}  {k}", file=sys.stderr)
