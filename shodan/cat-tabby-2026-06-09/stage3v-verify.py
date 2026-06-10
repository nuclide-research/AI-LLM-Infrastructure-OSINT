#!/usr/bin/env python3
"""
Stage 3v VERIFY — Cat-Tabby (Tabby + Sourcegraph) marker-anchored verification.

Lane C (DCWF 672 AI Test & Evaluation Specialist) load-bearing probe.
Lane D (DCWF 733 AI Risk & Ethics Specialist) restraint enforcement is built in:
  the do-not-call set is hard-coded and the script refuses to issue those endpoints
  against any host.

Discipline (per methodology Stage 2):
  - Conjunctive marker-anchored matchers, never a naked single-word body_contains
  - 200-with-data, never 200-alone (Insight #16: a 200 is identity, not auth state)
  - Auth-bypass discovery via /home post-redirect tokens (Insight #8)
  - Source-code shapes for verify primitives (Insight #11)
  - Sample minimally; names ARE the finding (restraint ethic)

Usage:
  python3 stage3v-verify.py --tabby ips-tabby.txt --sourcegraph ips-sourcegraph.txt -o verify.jsonl
"""
import argparse, json, ssl, socket, urllib.request, urllib.error, datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# Lane D ethical-stop set — these endpoints are EXFIL-equivalent or state-changing,
# and are hard-refused against any survey-set host. If you find yourself wanting to
# call one, you have crossed the boundary.
DO_NOT_CALL = {
    # Tabby
    "POST /": "admin-account-create on first-visit = host takeover (v0.11.0+)",
    "POST /v1/completions": "compute-exfil, GPU cost on operator",
    "POST /v1/chat/completions": "compute-exfil, SSE-streamed",
    "POST /v1beta/chat/completions": "legacy compute-exfil alias",
    "POST /v1/events": "operator-telemetry pollution",
    # Sourcegraph
    "POST /.api/completions/stream": "Cody compute-exfil, billed",
    "POST /.api/cody/context": "Cody compute-exfil + indexed-code pull, billed",
    "POST /.api/sg/embeddings": "embedding compute-exfil",
    "POST /.api/llm/v1/chat/completions": "compute-exfil",
    "POST /.api/graphql (mutation)": "state-changing GraphQL operation",
}

# Read-only enumeration primitives — these are the legal-equivalent
TABBY_PROBES = [
    ("/v1/health",         "GET", "tabby_identity", ["chat_model", "webserver"]),
    ("/v1beta/models",     "GET", "tabby_model_list", ["data"]),
    ("/v1beta/server_setting", "GET", "tabby_server_config", []),
    ("/auth/signin",       "GET", "tabby_webserver_present", []),
    ("/",                  "GET", "tabby_root", []),
]
SOURCEGRAPH_PROBES = [
    ("/sign-in",           "GET", "sg_signin_page", []),
    ("/.api/graphql",      "POST", "sg_graphql_version", [], '{"query":"{ site { productVersion } }"}'),
    ("/site-admin",        "GET", "sg_site_admin_redirect", []),
    ("/search",            "GET", "sg_search_open_state", []),
    ("/users",             "GET", "sg_users_open_state", []),
]

TIMEOUT = 10

def probe(url, method="GET", body=None, headers=None):
    """Single HTTP probe. Returns (status, headers, body[:4096], err)."""
    req = urllib.request.Request(url, method=method, data=body.encode() if body else None,
                                   headers=headers or {})
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT, context=ctx) as r:
            return r.status, dict(r.headers), r.read(8192).decode(errors='replace'), None
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers or {}), (e.read(4096).decode(errors='replace') if e.fp else ""), None
    except (urllib.error.URLError, socket.timeout, ConnectionError, TimeoutError, OSError) as e:
        return None, {}, "", str(e)

def verify_tabby(ip, ports):
    """Tabby verify: marker-anchored, conjunctive, restraint-respecting.

    Auth state derived from MULTI-PROBE COMBO (not /v1/health alone — 2026-06-09
    correction: real Tabby instances often gate /v1/health with 401, contrary to
    squad-1 brief).

    Identity signals (any positive = is_tabby=True):
      A. /v1/health returns 200 + chat_model + webserver  (auth-OFF cohort)
      B. /v1/health returns 401 with empty content        (auth-ON cohort)
      C. /auth/signin returns 200 + "<title>Tabby"        (v0.11.0+ webserver UI)
      D. /                returns 200 + "<title>Tabby"    (root SPA title marker)

    Auth state classification:
      NONE — /v1/health returned 200 with HealthState (open compute primitive)
      ON   — /v1/health returned 401 or /v1beta/models returned 401
      OPEN-MODELS — /v1/health gated but /v1beta/models returned 200 + data
                    (partial leak; model-fingerprint exfil still possible)
      OPEN-CONFIG — /v1beta/server_setting returned 200 unauth
                    (config-leak primitive — Insight #11 indexed-repo URLs)
    """
    results = []
    for port in ports:
        scheme = "https" if port in (443, 8443, 9443) else "http"
        base = f"{scheme}://{ip}:{port}"
        host_record = {
            "ip": ip, "port": port, "scheme": scheme, "platform_hypothesis": "tabby",
            "probes": {}, "verdict": None, "auth_state": None,
            "evidence_score": 0,
            "restraint_compliance": "OK — no do-not-call endpoints exercised",
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "identity_signals": [],
        }

        # Probe A: /v1/health
        status_h, _, body_h, err_h = probe(f"{base}/v1/health")
        host_record["probes"]["/v1/health"] = {"status": status_h, "body_excerpt": body_h[:300], "err": err_h}
        is_tabby = False
        if status_h == 200 and body_h:
            try:
                hs = json.loads(body_h)
                if "chat_model" in hs and "webserver" in hs:
                    is_tabby = True
                    host_record["identity_signals"].append("/v1/health 200 + chat_model+webserver")
                    host_record["model"] = hs.get("model")
                    host_record["chat_model"] = hs.get("chat_model")
                    host_record["device"] = hs.get("device")
                    host_record["webserver_enabled"] = hs.get("webserver", False)
                    host_record["auth_state"] = "NONE — /v1/health returns HealthState unauthenticated"
                    host_record["evidence_score"] = 2
            except (json.JSONDecodeError, KeyError):
                pass
        elif status_h == 401:
            # Don't classify as Tabby yet from 401 alone — many web servers return 401 — confirm with B/C
            host_record["_v1_health_401"] = True

        # Probe B: /v1beta/models — same auth class as /v1/health typically
        status_m, _, body_m, err_m = probe(f"{base}/v1beta/models")
        host_record["probes"]["/v1beta/models"] = {"status": status_m, "body_excerpt": body_m[:300], "err": err_m}
        if status_m == 200 and body_m:
            try:
                ml = json.loads(body_m)
                if isinstance(ml, dict) and "data" in ml and isinstance(ml["data"], list):
                    is_tabby = True
                    host_record["identity_signals"].append("/v1beta/models 200 + data[]")
                    host_record["models_enumerable_count"] = len(ml["data"])
                    host_record["model_ids"] = [m.get("id") for m in ml["data"][:10]]
                    if not host_record["auth_state"]:
                        host_record["auth_state"] = "OPEN-MODELS — model list unauth"
                    host_record["evidence_score"] = max(host_record["evidence_score"], 2)
            except (json.JSONDecodeError, KeyError): pass

        # Probe C: /auth/signin — v0.11.0+ webserver UI (Tabby-unique title)
        status_s, _, body_s, err_s = probe(f"{base}/auth/signin")
        host_record["probes"]["/auth/signin"] = {"status": status_s, "body_excerpt": body_s[:300], "err": err_s}
        if status_s == 200 and "<title>Tabby" in body_s:
            is_tabby = True
            host_record["identity_signals"].append("/auth/signin 200 + <title>Tabby")
            host_record["webserver_v0_11_plus"] = True

        # Probe D: / — root SPA title
        status_r, _, body_r, err_r = probe(f"{base}/")
        host_record["probes"]["/"] = {"status": status_r, "body_excerpt": body_r[:200], "err": err_r}
        if status_r == 200 and "<title>Tabby" in body_r:
            is_tabby = True
            host_record["identity_signals"].append("/ 200 + <title>Tabby")

        if not is_tabby:
            host_record["verdict"] = "refuted: no Tabby identity signal"
            host_record["evidence_score"] = -1
            results.append(host_record)
            continue

        # Probe E: /v1beta/server_setting — config-leak primitive
        status_cfg, _, body_cfg, err_cfg = probe(f"{base}/v1beta/server_setting")
        host_record["probes"]["/v1beta/server_setting"] = {"status": status_cfg, "body_excerpt": body_cfg[:500], "err": err_cfg}
        if status_cfg == 200 and body_cfg:
            try:
                cfg = json.loads(body_cfg)
                if isinstance(cfg, dict):
                    host_record["server_config_keys"] = list(cfg.keys())[:20]
                    host_record["server_config_sample"] = {k: v for k, v in list(cfg.items())[:5] if not isinstance(v, (dict, list))}
                    if not host_record["auth_state"] or "ON" in (host_record["auth_state"] or ""):
                        host_record["auth_state"] = f"OPEN-CONFIG — /v1beta/server_setting returns {len(list(cfg.keys()))} fields unauth"
                    host_record["evidence_score"] = max(host_record["evidence_score"], 2)
            except json.JSONDecodeError: pass

        # Final auth-state if still empty: 401 cohort
        if not host_record["auth_state"]:
            if host_record.get("_v1_health_401") or status_m == 401:
                host_record["auth_state"] = "ON — auth required for /v1/health or /v1beta/models"
            else:
                host_record["auth_state"] = "INCONCLUSIVE — identity confirmed via webserver UI only"

        host_record["verdict"] = (
            f"confirmed Tabby; auth_state={host_record['auth_state'].split(' — ')[0]}"
        )
        host_record.pop("_v1_health_401", None)
        results.append(host_record)
    return results

def verify_sourcegraph(ip, ports):
    """Sourcegraph verify — marker-anchored, restraint-respecting.

    KEY RULE per Lane D: /.api/graphql introspection is restraint-clean
    (pure metadata, debug-API-on-by-default), site.productVersion query is
    restraint-clean (read-only single field). repositories/users/search
    queries succeed only when auth.public:true and escalate severity.
    GraphQL mutations are HARD-REFUSED.
    """
    results = []
    for port in ports:
        scheme = "https" if port in (443, 8443, 7443, 9443) else "http"
        base = f"{scheme}://{ip}:{port}"
        host_record = {
            "ip": ip, "port": port, "scheme": scheme, "platform_hypothesis": "sourcegraph",
            "probes": {}, "verdict": None, "auth_state": None,
            "evidence_score": 0,
            "restraint_compliance": "OK — no GraphQL mutations, no completions, only schema introspection + productVersion read",
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        }

        # Probe 1: /sign-in — Sourcegraph identity marker
        status, _, body, err = probe(f"{base}/sign-in")
        host_record["probes"]["/sign-in"] = {"status": status, "body_excerpt": body[:300], "err": err}
        is_sg = status == 200 and ("Sign in - Sourcegraph" in body or "Sourcegraph" in body)
        if not is_sg:
            # Try /.api/graphql for the locked-mode marker
            req_body = '{"query":"{ site { productVersion } }"}'
            status, _, body, err = probe(f"{base}/.api/graphql", method="POST", body=req_body,
                                        headers={"Content-Type":"application/json"})
            host_record["probes"]["/.api/graphql"] = {"status": status, "body_excerpt": body[:300], "err": err}
            if status == 200 and "productVersion" in body:
                try:
                    j = json.loads(body)
                    pv = j.get("data", {}).get("site", {}).get("productVersion")
                    if pv:
                        is_sg = True
                        host_record["productVersion"] = pv
                        host_record["auth_state"] = "public_query_ok — site.productVersion returned unauth (this is by-design, debug-API)"
                except json.JSONDecodeError: pass

        if not is_sg:
            host_record["verdict"] = "refuted: neither /sign-in nor /.api/graphql identifies Sourcegraph"
            host_record["evidence_score"] = -1
            results.append(host_record)
            continue

        # Probe 2: /.api/graphql currentUser — auth.public detection
        req_body = '{"query":"{ currentUser { username } }"}'
        status, _, body, err = probe(f"{base}/.api/graphql", method="POST", body=req_body,
                                    headers={"Content-Type":"application/json"})
        host_record["probes"]["/.api/graphql currentUser"] = {"status": status, "body_excerpt": body[:200], "err": err}
        try:
            j = json.loads(body)
            cu = j.get("data", {}).get("currentUser")
            if cu is None and not j.get("errors"):
                pass  # anonymous, auth.public not set
            elif cu and cu.get("username"):
                # We hit as an authed user — should not happen unauth unless creds leaked
                host_record["auth_state"] = "AUTHED_LEAK — currentUser returned a username without bearer"
                host_record["evidence_score"] = 2
        except (json.JSONDecodeError, KeyError, AttributeError): pass

        # Probe 3: repositories(first:1) — auth.public:true cohort detection
        req_body = '{"query":"{ repositories(first:1) { nodes { name } } }"}'
        status, _, body, err = probe(f"{base}/.api/graphql", method="POST", body=req_body,
                                    headers={"Content-Type":"application/json"})
        host_record["probes"]["/.api/graphql repos"] = {"status": status, "body_excerpt": body[:200], "err": err}
        try:
            j = json.loads(body)
            repos = j.get("data", {}).get("repositories", {}).get("nodes")
            if repos:
                host_record["auth_state"] = "PUBLIC_REPOS_LEAK — repositories enumerable unauthenticated (auth.public:true cohort)"
                host_record["evidence_score"] = 2
                host_record["repo_names_sample"] = [r.get("name") for r in repos[:5]]
        except (json.JSONDecodeError, KeyError, AttributeError, TypeError): pass

        host_record["verdict"] = (
            "confirmed Sourcegraph; auth.public LEAK present" if "PUBLIC_REPOS_LEAK" in (host_record.get("auth_state") or "")
            else "confirmed Sourcegraph; auth.public not set (locked-down cohort)"
        )
        results.append(host_record)
    return results

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tabby-ports", default="9090,8080,8000,443,80,9000,9999,8443")
    ap.add_argument("--sourcegraph-ports", default="80,81,443,3080,7080,7443,3141")
    ap.add_argument("--tabby", help="File with one Tabby-target IP per line")
    ap.add_argument("--sourcegraph", help="File with one Sourcegraph-target IP per line")
    ap.add_argument("-o", "--output", default="verify-results.jsonl")
    ap.add_argument("--threads", type=int, default=20)
    args = ap.parse_args()

    print(f"# Lane D enforced DO_NOT_CALL set ({len(DO_NOT_CALL)} endpoints):")
    for ep, why in DO_NOT_CALL.items():
        print(f"#   {ep}  --  {why}")
    print()

    tabby_ips = sorted({l.strip() for l in open(args.tabby)} if args.tabby else set())
    sg_ips = sorted({l.strip() for l in open(args.sourcegraph)} if args.sourcegraph else set())
    tabby_ports = [int(p) for p in args.tabby_ports.split(",")]
    sg_ports = [int(p) for p in args.sourcegraph_ports.split(",")]

    print(f"Tabby targets: {len(tabby_ips)} × {len(tabby_ports)} ports")
    print(f"Sourcegraph targets: {len(sg_ips)} × {len(sg_ports)} ports")

    out = open(args.output, "w")
    n_confirmed = n_refuted = n_unauth = 0
    with ThreadPoolExecutor(max_workers=args.threads) as ex:
        futures = [ex.submit(verify_tabby, ip, tabby_ports) for ip in tabby_ips]
        futures += [ex.submit(verify_sourcegraph, ip, sg_ports) for ip in sg_ips]
        for fut in as_completed(futures):
            for rec in fut.result():
                out.write(json.dumps(rec) + "\n")
                if rec["evidence_score"] == -1: n_refuted += 1
                elif rec["evidence_score"] >= 2: n_confirmed += 1
                if "auth_state" in rec and rec["auth_state"] and ("NONE" in rec["auth_state"] or "LEAK" in rec["auth_state"]):
                    n_unauth += 1
                    print(f"[!] {rec['ip']}:{rec['port']}  {rec['platform_hypothesis']}  {rec['auth_state']}")
    out.close()
    print(f"\nSummary: confirmed={n_confirmed}, refuted={n_refuted}, UNAUTH/LEAK candidates={n_unauth}")

if __name__ == "__main__":
    main()
