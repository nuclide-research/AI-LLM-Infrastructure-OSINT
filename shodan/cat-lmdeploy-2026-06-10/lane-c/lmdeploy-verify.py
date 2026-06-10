#!/usr/bin/env python3
"""
Stage 3v VERIFY — Cat-LMDeploy marker-anchored verification.

Lane C (DCWF 672 AI Test & Evaluation Specialist) load-bearing probe.
Lane D (DCWF 733 AI Risk & Ethics Specialist) restraint enforcement is built in:
  the do-not-call set is hard-coded and the script refuses to issue those endpoints
  against any host. The do-not-call set is checked at code level, BEFORE any
  request is constructed.

LMDeploy is documented as auth_default=none (api_server.py:1486 in OpenMMLab/lmdeploy).
This script tests the auth-on-default thesis against the live population.

Discipline (per methodology Stage 3v):
  - Sandbox-MITM gate run first (mitm-shape-probe.py) — load-bearing
  - 200 is identity, not auth state (Insight #16). Every 200 needs data-layer probe
  - Conjunctive marker-anchored matchers, never naked single-word body_contains
    (Insight #6). LMDeploy schema markers used: "/distserve/engine_info" AND
    "/v1/chat/interactive" — platform-unique combination
  - Verification rung pair A/B × 0/1/2 per finding (Insight #68)
  - Sample minimally; names ARE the finding (restraint ethic)

Usage:
  python3 lmdeploy-verify.py --ips ips.txt -o verify.jsonl
"""
import argparse
import json
import ssl
import socket
import urllib.request
import urllib.error
import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# Lane D ETHICAL-STOP set — these endpoints are compute-exfil, state-changing,
# or model-tampering. Hard-refused against any survey-set host at code level
# BEFORE any request is constructed. Per Lane C brief.
DO_NOT_CALL = {
    "/terminate":                  "process termination",
    "/sleep":                      "engine state change",
    "/wakeup":                     "engine state change",
    "/update_weights":             "model-tampering",
    "/abort_request":              "in-flight state change",
    "/v1/chat/completions":        "compute-exfil, GPU cost on operator",
    "/v1/completions":             "compute-exfil, GPU cost on operator",
    "/v1/embeddings":              "compute-exfil",
    "/generate":                   "compute-exfil legacy alias",
    "/v1/chat/interactive":        "compute-exfil, stateful session",
    "/distserve/p2p_initialize":   "P2P state change",
    "/distserve/p2p_connect":      "P2P state change",
    "/distserve/p2p_drop_connect": "P2P state change",
    "/distserve/free_cache":       "engine state change",
    "/pooling":                    "compute-exfil (pooling op)",
}

# Read-only enumeration primitives — restraint-clean
LMDEPLOY_PROBES = [
    ("/",                       "GET", "lmdeploy_swagger_ui"),
    ("/openapi.json",           "GET", "lmdeploy_schema"),
    ("/v1/models",              "GET", "lmdeploy_model_list"),
    ("/health",                 "GET", "lmdeploy_health"),
    ("/metrics",                "GET", "lmdeploy_prometheus"),
    ("/distserve/engine_info",  "GET", "lmdeploy_engine_info"),
]

# LMDeploy-unique schema markers. Conjunctive: BOTH must appear for a 200 to be
# a confirmed LMDeploy schema. /distserve/engine_info alone is too generic.
# /v1/chat/interactive is LMDeploy-specific (vs the openai-style /v1/chat/completions
# which everyone serves). The pair makes a marker that no FastAPI clone could
# accidentally emit.
LMDEPLOY_SCHEMA_MARKERS = ("/distserve/engine_info", "/v1/chat/interactive")

TIMEOUT = 10

def _check_do_not_call(path: str) -> None:
    """Hard-refuse at code level BEFORE the request goes out. Raises if violated."""
    for forbidden, reason in DO_NOT_CALL.items():
        if path == forbidden or path.startswith(forbidden + "?"):
            raise RuntimeError(
                f"REFUSED — {path} is in DO_NOT_CALL ({reason}). "
                f"Lane D restraint at code level."
            )

def probe(url, method="GET", body=None, headers=None, path_for_check=None):
    """Single HTTP probe. Returns (status, headers, body[:4096], err).

    Hard-refuses any path in DO_NOT_CALL at code level before constructing
    the request. This is the Lane D ethical-stop guard.
    """
    if path_for_check is not None:
        _check_do_not_call(path_for_check)
    req = urllib.request.Request(
        url,
        method=method,
        data=body.encode() if body else None,
        headers=headers or {"User-Agent": "nuclide-lane-c/1.0"},
    )
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT, context=ctx) as r:
            return r.status, dict(r.headers), r.read(16384).decode(errors='replace'), None
    except urllib.error.HTTPError as e:
        body_text = e.read(4096).decode(errors='replace') if e.fp else ""
        return e.code, dict(e.headers or {}), body_text, None
    except (urllib.error.URLError, socket.timeout, ConnectionError, TimeoutError, OSError) as e:
        return None, {}, "", str(e)

def verify_lmdeploy(ip, ports):
    """LMDeploy verify — marker-anchored, conjunctive, restraint-respecting.

    Identity classification:
      A. /openapi.json returns 200 + BOTH schema markers present
         → CONFIRMED LMDeploy
      B. / returns 200 + swagger UI title 'FastAPI' (weak — many clones)
         → CANDIDATE only
      C. /v1/models returns 200 + 'data' list with non-empty model ids
         → COMPATIBLE (openai-style API surface — could be LMDeploy, vLLM,
           sglang, llama.cpp; needs (A) to disambiguate)

    Auth-state classification:
      UNAUTH-OPENAPI — /openapi.json returned 200 + schema markers without bearer
                       (auth-on-default thesis CONFIRMED)
      UNAUTH-MODELS  — /v1/models returned 200 + data unauth (model list leak)
      UNAUTH-ENGINE  — /distserve/engine_info 200 unauth (infra leak)
      AUTH-GATED     — /openapi.json or /v1/models returned 401/403
      MIXED          — some open, some gated (partial-auth deployment)
      INCONCLUSIVE   — identity not confirmed
    """
    results = []
    for port in ports:
        # LMDeploy default is HTTP (uvicorn no-TLS). 443/8443 are unusual but possible.
        scheme = "https" if port in (443, 8443, 9443) else "http"
        base = f"{scheme}://{ip}:{port}"
        host_record = {
            "ip": ip,
            "port": port,
            "scheme": scheme,
            "platform_hypothesis": "lmdeploy",
            "probes": {},
            "verdict": None,
            "auth_state": None,
            "evidence_score": 0,
            "identity_signals": [],
            "restraint_compliance": "OK — no DO_NOT_CALL endpoints exercised",
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "verification_rung": None,
        }

        is_lmdeploy = False
        unauth_signals = 0
        gated_signals = 0

        # Probe 1: GET / — Swagger UI / FastAPI shell
        status, _, body, err = probe(f"{base}/", path_for_check="/")
        host_record["probes"]["/"] = {
            "status": status,
            "body_excerpt": body[:300],
            "err": err,
        }
        if status == 200 and ("Swagger UI" in body or "swagger-ui" in body or "FastAPI" in body):
            host_record["identity_signals"].append("/ 200 + Swagger/FastAPI UI shell (weak)")
        elif status is None:
            host_record["verdict"] = f"unreachable: {err}"
            results.append(host_record)
            continue

        # Probe 2: GET /openapi.json — LOAD-BEARING schema identity probe
        status, _, body, err = probe(f"{base}/openapi.json", path_for_check="/openapi.json")
        host_record["probes"]["/openapi.json"] = {
            "status": status,
            "body_len": len(body),
            "body_excerpt": body[:500],
            "err": err,
        }
        openapi_unauth_confirmed = False
        if status == 200 and body:
            marker_a, marker_b = LMDEPLOY_SCHEMA_MARKERS
            if marker_a in body and marker_b in body:
                is_lmdeploy = True
                openapi_unauth_confirmed = True
                unauth_signals += 1
                host_record["identity_signals"].append(
                    f"/openapi.json 200 + BOTH schema markers ({marker_a!r} AND {marker_b!r})"
                )
                host_record["evidence_score"] = 3
                # Pull schema metadata (title, version) — restraint-clean
                try:
                    schema = json.loads(body)
                    info = schema.get("info", {})
                    host_record["openapi_title"] = info.get("title")
                    host_record["openapi_version"] = info.get("version")
                    # Enumerate path names ONLY (don't fetch them)
                    paths = list(schema.get("paths", {}).keys())
                    host_record["openapi_path_count"] = len(paths)
                    host_record["openapi_paths_sample"] = sorted(paths)[:30]
                except (json.JSONDecodeError, AttributeError):
                    pass
            elif marker_a in body or marker_b in body:
                host_record["identity_signals"].append(
                    f"/openapi.json 200 + ONE marker only (partial — possible fork)"
                )
                host_record["evidence_score"] = 1
        elif status in (401, 403):
            gated_signals += 1
            host_record["identity_signals"].append(f"/openapi.json {status} — gated")

        # Probe 3: GET /v1/models — model list (NO INFERENCE)
        status, _, body, err = probe(f"{base}/v1/models", path_for_check="/v1/models")
        host_record["probes"]["/v1/models"] = {
            "status": status,
            "body_excerpt": body[:400],
            "err": err,
        }
        if status == 200 and body:
            try:
                ml = json.loads(body)
                if isinstance(ml, dict) and "data" in ml and isinstance(ml["data"], list):
                    unauth_signals += 1
                    host_record["models_enumerable_count"] = len(ml["data"])
                    host_record["model_ids"] = [m.get("id") for m in ml["data"][:10] if isinstance(m, dict)]
                    host_record["identity_signals"].append(
                        f"/v1/models 200 + data[{len(ml['data'])}] unauth"
                    )
                    if not is_lmdeploy:
                        # openai-style API surface — not LMDeploy-unique
                        host_record["evidence_score"] = max(host_record["evidence_score"], 1)
            except (json.JSONDecodeError, KeyError):
                pass
        elif status in (401, 403):
            gated_signals += 1

        # Probe 4: GET /health — liveness
        status, _, body, err = probe(f"{base}/health", path_for_check="/health")
        host_record["probes"]["/health"] = {
            "status": status,
            "body_excerpt": body[:200],
            "err": err,
        }

        # Probe 5: GET /metrics — Prometheus (only if --enable-metrics)
        status, _, body, err = probe(f"{base}/metrics", path_for_check="/metrics")
        host_record["probes"]["/metrics"] = {
            "status": status,
            "body_excerpt": body[:300],
            "err": err,
        }
        if status == 200 and body and ("# HELP" in body or "# TYPE" in body):
            unauth_signals += 1
            host_record["identity_signals"].append("/metrics 200 + Prometheus format unauth")
            # Pull HELP lines only (counter names, no values dumped exhaustively)
            help_lines = [ln for ln in body.splitlines()[:50] if ln.startswith("# HELP")]
            host_record["metrics_help_sample"] = help_lines[:10]

        # Probe 6: GET /distserve/engine_info — P2P infra (LMDeploy distserve mode)
        status, _, body, err = probe(
            f"{base}/distserve/engine_info",
            path_for_check="/distserve/engine_info",
        )
        host_record["probes"]["/distserve/engine_info"] = {
            "status": status,
            "body_excerpt": body[:500],
            "err": err,
        }
        if status == 200 and body:
            is_lmdeploy = True  # this endpoint is LMDeploy-unique
            unauth_signals += 1
            host_record["identity_signals"].append("/distserve/engine_info 200 unauth (infra leak)")
            host_record["evidence_score"] = max(host_record["evidence_score"], 3)
            try:
                ei = json.loads(body)
                if isinstance(ei, dict):
                    host_record["engine_info_keys"] = list(ei.keys())[:20]
            except (json.JSONDecodeError, KeyError):
                pass
        elif status in (401, 403):
            gated_signals += 1

        # Final auth-state classification
        if not is_lmdeploy and host_record["evidence_score"] == 0:
            host_record["verdict"] = "refuted: no LMDeploy schema markers, no Swagger UI, no /distserve/engine_info"
            host_record["evidence_score"] = -1
            host_record["verification_rung"] = ("A", 1)
            results.append(host_record)
            continue

        if unauth_signals >= 2 and openapi_unauth_confirmed:
            host_record["auth_state"] = (
                f"UNAUTH-OPENAPI — openapi.json + {unauth_signals - 1} other endpoint(s) unauth"
            )
            host_record["verification_rung"] = ("A", 2)  # binary unauth confirmed at host level
        elif openapi_unauth_confirmed:
            host_record["auth_state"] = "UNAUTH-OPENAPI — schema unauth (other endpoints not checked here)"
            host_record["verification_rung"] = ("A", 1)
        elif unauth_signals >= 1 and gated_signals >= 1:
            host_record["auth_state"] = f"MIXED — {unauth_signals} unauth, {gated_signals} gated"
            host_record["verification_rung"] = ("B", 1)
        elif gated_signals >= 2:
            host_record["auth_state"] = f"AUTH-GATED — {gated_signals} endpoint(s) returned 401/403"
            host_record["verification_rung"] = ("B", 1)
        elif unauth_signals >= 1:
            host_record["auth_state"] = f"UNAUTH-PARTIAL — {unauth_signals} endpoint(s) unauth, no openapi.json verify"
            host_record["verification_rung"] = ("A", 1)
        else:
            host_record["auth_state"] = "INCONCLUSIVE — no clear unauth/gated signal"
            host_record["verification_rung"] = (None, 0)

        host_record["verdict"] = (
            f"confirmed LMDeploy; auth_state={host_record['auth_state'].split(' — ')[0]}"
            if is_lmdeploy
            else f"openai-style API present (NOT confirmed LMDeploy); auth_state={host_record['auth_state'].split(' — ')[0]}"
        )
        results.append(host_record)
    return results


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ports", default="23333,8000,80,443",
                    help="comma-separated ports to probe (LMDeploy default 23333)")
    ap.add_argument("--ips", required=True, help="file with one target IP per line")
    ap.add_argument("-o", "--output", default="lmdeploy-verify.jsonl")
    ap.add_argument("--threads", type=int, default=10)
    args = ap.parse_args()

    print(f"# Lane D enforced DO_NOT_CALL set ({len(DO_NOT_CALL)} endpoints):")
    for ep, why in DO_NOT_CALL.items():
        print(f"#   {ep:35s} -- {why}")
    print()
    print(f"# Restraint-clean ALLOWED probes:")
    for path, method, label in LMDEPLOY_PROBES:
        print(f"#   {method} {path:30s} -- {label}")
    print()

    with open(args.ips) as f:
        ips = sorted({line.strip() for line in f if line.strip() and not line.startswith("#")})
    ports = [int(p) for p in args.ports.split(",")]
    print(f"# Targets: {len(ips)} IPs × {len(ports)} ports = {len(ips) * len(ports)} host:port combos")
    print(f"# Output: {args.output}")
    print()

    out = open(args.output, "w")
    n_confirmed = n_refuted = n_unauth = n_gated = n_inconclusive = 0
    n_restraint_violations = 0
    n_lmdeploy_unique = 0
    with ThreadPoolExecutor(max_workers=args.threads) as ex:
        futures = [ex.submit(verify_lmdeploy, ip, ports) for ip in ips]
        for fut in as_completed(futures):
            for rec in fut.result():
                out.write(json.dumps(rec) + "\n")
                if rec.get("evidence_score", 0) == -1:
                    n_refuted += 1
                elif rec.get("evidence_score", 0) >= 3:
                    n_confirmed += 1
                    n_lmdeploy_unique += 1
                elif rec.get("evidence_score", 0) >= 1:
                    n_confirmed += 1
                auth = rec.get("auth_state") or ""
                if "UNAUTH" in auth:
                    n_unauth += 1
                    print(f"[!] {rec['ip']}:{rec['port']:5d} {auth}")
                elif "GATED" in auth:
                    n_gated += 1
                elif "INCONCLUSIVE" in auth:
                    n_inconclusive += 1
                if rec.get("restraint_compliance", "").startswith("VIOLATION"):
                    n_restraint_violations += 1
    out.close()

    print()
    print("=" * 70)
    print("Lane C VERIFY summary")
    print("=" * 70)
    print(f"  confirmed (any LMDeploy-style):  {n_confirmed}")
    print(f"  confirmed (LMDeploy-unique):     {n_lmdeploy_unique}")
    print(f"  refuted (no LMDeploy signal):    {n_refuted}")
    print(f"  unauth open:                     {n_unauth}")
    print(f"  auth-gated:                      {n_gated}")
    print(f"  inconclusive:                    {n_inconclusive}")
    print(f"  RESTRAINT VIOLATIONS:            {n_restraint_violations} (MUST be 0)")
    print(f"  output: {args.output}")


if __name__ == "__main__":
    main()
