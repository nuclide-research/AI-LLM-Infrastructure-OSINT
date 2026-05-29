#!/usr/bin/env python3
"""
guardrail-probe.py — LLM safety/guardrail engine verification probe.

WHY THIS EXISTS: aimap has no guardrail fingerprint (Insight #20 gap, same as the
Kubecost/OpenCost case). This is the manual->productize step: a single-purpose,
read-only verifier for guardrail API servers. Output is NDJSON that feeds
`visorlog ingest`, not a terminal print (STOP-and-check rule).

THE FINDING (per safety-guardrail intel): an exposed, unauthenticated guardrail
server gives an attacker three things:
  1. the safety layer is BYPASSABLE (send straight to the upstream LLM);
  2. the policy/scanner CONFIG reveals the operator's threat model;
  3. prompt-scan logs expose user inputs.

RESTRAINT (#38/#41): we confirm (1) auth state with ONE benign test prompt of our
own ("guardrail exposure check"), and (2) read CONFIG NAMES only (scanner list,
guard names, settings keys). We do NOT read the scan cache / prompt history (#3 =
user data) — we record only whether such an endpoint exists. We never write
(no /add/texts, no /canary/add).

Platforms + signals (from platform-intel/safety-guardrail-osint):
  LLM Guard      :8000  GET /swagger.json -> info.title "LLM Guard API"; POST /analyze/prompt
  Guardrails AI  :8000  GET /guards -> JSON array of guard defs; GET /health-check
  Vigil          :5000  GET /settings -> scanner/embedding/cache config JSON
  Rebuff         :3000  (POST /api/detect -> injectionScore) — presence check only
  NeMo Guardrails:8000  GET /v1/rails/configs -> JSON array of rail config names

Usage: python3 guardrail-probe.py targets.txt > findings.ndjson
"""
import sys, json, subprocess, concurrent.futures as cf
import urllib.request, urllib.error


def vpn_up():
    """Fail-closed egress guard: only probe while the Mullvad tunnel is up.
    Checked per-host so a mid-run tunnel drop skips the remaining hosts rather
    than leaking probes over the residential IP (Intentional Movement)."""
    try:
        return b"Connected" in subprocess.run(["mullvad", "status"], capture_output=True, timeout=5).stdout
    except Exception:
        return False

TIMEOUT = 6
THREADS = 8
UA = "NuClide-Research/guardrail-probe (read-only safety-layer exposure check; nicholas@nuclide-research.com)"
PORTS = [8000, 80, 443, 8080, 8001, 8443, 5000, 3000, 8888]
BENIGN = json.dumps({"prompt": "guardrail exposure check"}).encode()


def _get(url, method="GET", data=None, ctype=None):
    req = urllib.request.Request(url, data=data, method=method, headers={"User-Agent": UA})
    if ctype:
        req.add_header("Content-Type", ctype)
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            return r.status, r.read(120_000).decode("utf-8", "replace"), dict(r.headers)
    except urllib.error.HTTPError as e:
        return e.code, "", dict(e.headers or {})
    except Exception:
        return None, "", {}


def _json(txt):
    txt = (txt or "").lstrip()
    if not txt or txt[0] not in "{[":
        return None
    try:
        return json.loads(txt)
    except Exception:
        return None


def probe_host(ip):
    if not vpn_up():
        return {"ip": ip, "confirmed": False, "auth_state": "skipped-vpn-down"}
    live = []  # ports that answered HTTP at all, for honest reporting
    for port in PORTS:
        scheme = "https" if port in (443, 8443) else "http"
        base = f"{scheme}://{ip}:{port}"
        rst, rbody, rhdr = _get(f"{base}/")
        if rst is None:
            continue  # nothing listening / not HTTP
        live.append(port)
        server = rhdr.get("Server", "")
        # ---- LLM Guard: APP_NAME 'LLM Guard' in openapi/docs/root (FastAPI = /openapi.json, Swagger UI = /docs) ----
        sig = None
        for path in ("/openapi.json", "/swagger.json", "/docs"):
            st, b, h = _get(f"{base}{path}")
            if b and "llm guard" in b.lower():
                sig = path; break
        if not sig and "llm guard" in (rbody or "").lower():
            sig = "/"
        if sig:
            rec = {"platform": "llm-guard", "ip": ip, "port": port, "confirmed": True,
                   "server": server, "signal": f"'LLM Guard' in {sig}"}
            sa, sb, _ = _get(f"{base}/analyze/prompt", method="POST", data=BENIGN, ctype="application/json")
            rec["scan_endpoint_status"] = sa
            rec["auth_state"] = "OPEN_API" if sa == 200 else ("AUTH" if sa in (401, 403) else f"other:{sa}")
            so = _json(sb)
            if isinstance(so, dict):
                sr = so.get("scanners_results") or so.get("scanners") or {}
                rec["scanners_exposed"] = sorted(sr.keys()) if isinstance(sr, dict) else bool(sr)
            return rec
        # ---- Guardrails AI ----
        sg, gb, gh = _get(f"{base}/guards")
        gobj = _json(gb)
        if sg == 200 and isinstance(gobj, list):
            rec = {"platform": "guardrails-ai", "ip": ip, "port": port, "confirmed": True,
                   "server": server, "signal": "/guards -> JSON array",
                   "auth_state": "OPEN_API", "guard_count": len(gobj),
                   "guard_names": [g.get("name") for g in gobj if isinstance(g, dict)][:20]}
            rec["health_check"] = _get(f"{base}/health-check")[0]
            return rec
        # ---- NeMo Guardrails ----
        sn, nb, _ = _get(f"{base}/v1/rails/configs")
        nobj = _json(nb)
        if sn == 200 and isinstance(nobj, list):
            return {"platform": "nemo-guardrails", "ip": ip, "port": port, "confirmed": True,
                    "auth_state": "OPEN_API", "signal": "/v1/rails/configs -> JSON array",
                    "rail_configs": nobj[:20], "config_exposed": True}
        # ---- Vigil ----
        sv, vb, _ = _get(f"{base}/settings")
        vobj = _json(vb)
        if sv == 200 and isinstance(vobj, dict) and ("scanner" in vobj or "embedding" in vobj):
            return {"platform": "vigil", "ip": ip, "port": port, "confirmed": True,
                    "auth_state": "OPEN_API", "signal": "/settings -> scanner config",
                    "settings_keys": sorted(vobj.keys())[:20], "config_exposed": True}
    return {"ip": ip, "confirmed": False, "auth_state": "no-guardrail-signal",
            "live_http_ports": live,
            "note": "HTTP answered but no guardrail signal" if live else "no HTTP on probed ports"}


def main():
    if len(sys.argv) < 2:
        print("usage: guardrail-probe.py targets.txt", file=sys.stderr); sys.exit(2)
    targets = [t.strip().split(":")[0] for t in open(sys.argv[1]) if t.strip() and not t.startswith("#")]
    with cf.ThreadPoolExecutor(max_workers=THREADS) as ex:
        for rec in ex.map(probe_host, targets):
            if rec:
                print(json.dumps(rec))


if __name__ == "__main__":
    main()
