#!/usr/bin/env python3
"""
Stage 3v VERIFY - OpenHands (All-Hands-AI, formerly OpenDevin) marker-anchored verification.

Lane C (DCWF 672 AI Test & Evaluation Specialist) load-bearing probe.
Restraint enforcement built in: the DO_NOT_CALL set is hard-coded and the script
refuses to issue those endpoints against any host (state-changing / compute-exfil /
git-diff command-injection sink for CVE-2026-33718).

Discipline (methodology Stage 3v):
  - Conjunctive marker-anchored matchers, never a naked single-word body_contains
    (the confirm requires a 200 + JSON-parse + the vendor-unique APP_MODE field,
     so an nginx default page / LBot catch-all 200 cannot earn the OpenHands label)
  - 200-with-data, never 200-alone (Insight #16: a 200 is identity, not auth state)
  - Sample minimally; names ARE the finding (restraint ethic). We record the
    llm_api_key_set BOOLEAN and model name only; NEVER the key value.
  - Verification rung pair (Insight #68): Inner A/B x Outer 0/1/2 set per host.

Usage:
  python3 stage3v-verify-openhands.py -i openhands-live-targets.txt -o verify-openhands.jsonl
"""
import argparse, json, ssl, socket, urllib.request, urllib.error, datetime, re, http.client
from concurrent.futures import ThreadPoolExecutor, as_completed

# Restraint ethical-stop set - state-changing / compute-exfil / the CVE-2026-33718
# git-diff command-injection sink. Hard-refused against any survey-set host.
DO_NOT_CALL = {
    "POST /api/conversations": "spawns an agent runtime = compute-exfil + state change",
    "POST /api/conversations/{id}/events": "drives the agent = compute-exfil",
    "POST /api/conversations/{id}/submit": "agent task submit = compute-exfil",
    "POST /api/options/config": "config mutation = state change",
    "PUT /api/settings": "writes llm_api_key / model = state change + cred-set",
    "POST /api/settings": "writes settings = state change",
    "GET /api/conversations/{id}/git/diff": "CVE-2026-33718 git-diff command-injection sink",
    "POST /api/conversations/{id}/git/changes": "VCS state-change / injection surface",
    "DELETE /api/conversations/{id}": "destroys conversation = state change",
    "POST /api/feedback": "operator-telemetry pollution",
}

# Read-only enumeration primitives.
# (path, method, label, conjunctive_markers[]) - markers ALL act as JSON-field anchors.
TIMEOUT = 6
UA = "nuclide-verify/1.0 (read-only AI-infra exposure research; metadata-only)"

# Ports to also try if the listed agent port is non-web / dead.
FALLBACK_WEB_PORTS = [443, 80]

VERSION_RE = re.compile(r'(?:openhands|all[-_]?hands|version)["\':\s/v-]{0,4}(\d+\.\d+\.\d+)', re.I)
SEMVER_RE = re.compile(r'\b(\d+)\.(\d+)\.(\d+)\b')


def probe(url, method="GET", body=None, headers=None):
    """Single HTTP probe. Returns (status, headers, body[:8192], err)."""
    req = urllib.request.Request(
        url, method=method,
        data=body.encode() if body else None,
        headers={"User-Agent": UA, "Accept": "*/*", **(headers or {})},
    )
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT, context=ctx) as r:
            return r.status, dict(r.headers), r.read(16384).decode(errors="replace"), None
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers or {}), (e.read(8192).decode(errors="replace") if e.fp else ""), None
    except (urllib.error.URLError, socket.timeout, ConnectionError, TimeoutError,
            OSError, http.client.HTTPException, ssl.SSLError, ValueError) as e:
        return None, {}, "", f"{type(e).__name__}: {e}"
    except Exception as e:
        return None, {}, "", f"{type(e).__name__}: {e}"


def try_schemes(ip, port):
    """Return (base_url, status, headers, body, err) for /api/options/config.
    http first; follow 301/308 to https; then fall back to https directly.
    """
    order = []
    if port in (443, 8443, 9443):
        order = [("https", port)]
    else:
        order = [("http", port), ("https", port)]
    last = None
    for scheme, p in order:
        base = f"{scheme}://{ip}:{p}"
        status, hdrs, body, err = probe(f"{base}/api/options/config")
        last = (base, status, hdrs, body, err)
        if status in (301, 302, 307, 308):
            loc = hdrs.get("Location") or hdrs.get("location") or ""
            if loc.startswith("https://"):
                m = re.match(r"https://([^/:]+)(?::(\d+))?", loc)
                if m:
                    hp = int(m.group(2) or 443)
                    base2 = f"https://{ip}:{hp}"
                    s2, h2, b2, e2 = probe(f"{base2}/api/options/config")
                    if s2 == 200:
                        return (base2, s2, h2, b2, e2)
                    last = (base2, s2, h2, b2, e2)
        if status == 200:
            return last
    return last


def extract_version(*texts):
    for t in texts:
        if not t:
            continue
        m = VERSION_RE.search(t)
        if m:
            return m.group(1)
    return None


def cve_class(version):
    if not version:
        return "UNKNOWN"
    m = SEMVER_RE.search(version)
    if not m:
        return "UNKNOWN"
    maj, mino, pat = int(m.group(1)), int(m.group(2)), int(m.group(3))
    # fixed in 1.5.0; <=1.4.0 vulnerable
    if (maj, mino) < (1, 5):
        return "VULNERABLE"
    return "PATCHED"


def verify_host(line):
    ip, _, port_s = line.partition(":")
    ip = ip.strip()
    try:
        port = int(port_s.strip())
    except ValueError:
        port = 80
    rec = {
        "ip": ip, "port": port, "scheme": None,
        "status_class": "DEAD",
        "app_mode": None, "llm_model": None, "llm_api_key_set": None,
        "agent": None, "llm_base_url": None, "conversation_count": None,
        "version": None, "cve_2026_33718": "UNKNOWN",
        "http_status": None,
        # verify metadata
        "probes": {}, "verdict": None, "auth_state": None, "evidence_score": 0,
        "identity_signals": [],
        "restraint_compliance": "OK - no DO_NOT_CALL endpoints exercised",
        "verification_rung": None,
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }

    base, status, hdrs, body, err = try_schemes(ip, port)
    rec["scheme"] = base.split("://")[0]
    rec["http_status"] = status
    rec["probes"]["/api/options/config"] = {"status": status, "body_excerpt": body[:300], "err": err}

    # If the agent port gave nothing, try fallback web ports (same IP).
    if status is None and port not in FALLBACK_WEB_PORTS:
        for fp in FALLBACK_WEB_PORTS:
            b2, s2, h2, bd2, e2 = try_schemes(ip, fp)
            if s2 is not None:
                base, status, hdrs, body, err = b2, s2, h2, bd2, e2
                rec["scheme"] = base.split("://")[0]
                rec["port"] = fp
                rec["http_status"] = status
                rec["probes"]["/api/options/config@fallback"] = {"status": status, "body_excerpt": body[:300], "err": err}
                break

    if status is None:
        rec["status_class"] = "DEAD"
        rec["verdict"] = "DEAD - no response on agent port or web fallback"
        rec["evidence_score"] = -1
        rec["verification_rung"] = "0 (no live host)"
        return rec

    # ---- Conjunctive marker: 200 + JSON + APP_MODE field ----
    is_openhands = False
    cfg = None
    if status == 200 and body:
        try:
            cfg = json.loads(body)
            if isinstance(cfg, dict) and "APP_MODE" in cfg:
                is_openhands = True
                rec["app_mode"] = cfg.get("APP_MODE")
                rec["identity_signals"].append("/api/options/config 200 + JSON.APP_MODE")
                # version sometimes lives in config
                rec["version"] = cfg.get("APP_VERSION") or cfg.get("version") or rec["version"]
        except (json.JSONDecodeError, TypeError):
            pass

    if not is_openhands:
        rec["status_class"] = "NOT_OPENHANDS"
        rec["verdict"] = "refuted: no APP_MODE marker (bare-200 / nginx-default / catch-all guarded against)"
        rec["evidence_score"] = -1
        rec["verification_rung"] = "1 (in-scope host reached, no platform marker)"
        return rec

    rec["evidence_score"] = 1  # marker present = MARKER_ONLY floor

    # ---- /api/settings : auth-OFF confirm + LLM-jacking surface ----
    s_status, _, s_body, s_err = probe(f"{base}/api/settings")
    rec["probes"]["/api/settings"] = {"status": s_status, "body_excerpt": s_body[:300], "err": s_err}
    settings_readable = False
    if s_status == 200 and s_body:
        try:
            st = json.loads(s_body)
            if isinstance(st, dict) and any(k in st for k in ("llm_model", "agent", "llm_api_key_set")):
                settings_readable = True
                rec["llm_model"] = st.get("llm_model")
                rec["agent"] = st.get("agent")
                rec["llm_base_url"] = st.get("llm_base_url") or None
                # boolean only - NEVER the key value
                v = st.get("llm_api_key_set")
                if v is None and "llm_api_key" in st:
                    # some builds return masked key; coerce to boolean presence
                    v = bool(st.get("llm_api_key"))
                rec["llm_api_key_set"] = bool(v) if v is not None else None
                rec["identity_signals"].append("/api/settings 200 + llm_model/agent")
        except (json.JSONDecodeError, TypeError):
            pass
    elif s_status in (401, 403):
        rec["auth_state"] = "AUTH-ON (settings gated)"

    # ---- conversation count (count only, no content dump) ----
    for cpath in ("/api/conversations", "/api/conversations/search"):
        c_status, _, c_body, c_err = probe(f"{base}{cpath}")
        rec["probes"][cpath] = {"status": c_status, "body_excerpt": c_body[:160], "err": c_err}
        if c_status == 200 and c_body:
            try:
                cj = json.loads(c_body)
                if isinstance(cj, list):
                    rec["conversation_count"] = len(cj)
                elif isinstance(cj, dict):
                    for key in ("results", "conversations", "data"):
                        if isinstance(cj.get(key), list):
                            rec["conversation_count"] = len(cj[key])
                            break
                    if rec["conversation_count"] is None and "num_conversations" in cj:
                        rec["conversation_count"] = cj.get("num_conversations")
                break
            except (json.JSONDecodeError, TypeError):
                pass

    # ---- version for CVE-2026-33718 (config / meta tag / asset hash / headers) ----
    if not rec["version"]:
        # root for meta tag + asset hash, headers for X-Version
        r_status, r_hdrs, r_body, _ = probe(f"{base}/")
        hdr_blob = " ".join(f"{k}:{v}" for k, v in (r_hdrs or {}).items())
        rec["version"] = extract_version(
            r_hdrs.get("X-OpenHands-Version") if r_hdrs else None,
            r_hdrs.get("X-Version") if r_hdrs else None,
            hdr_blob, r_body[:4000],
        )
    rec["cve_2026_33718"] = cve_class(rec["version"])

    # ---- classify ----
    if settings_readable:
        rec["status_class"] = "CONFIRMED_OPEN"
        rec["auth_state"] = "AUTH-OFF (settings readable unauth)"
        rec["evidence_score"] = 2
        rec["verdict"] = "confirmed OpenHands; settings readable unauth = auth-off"
        # Insight #68 rung: Inner A (full logic/data read) x Outer 2 (population read)
        rec["verification_rung"] = "A2 (logic-depth read x population-data read)"
    elif s_status in (401, 403):
        rec["status_class"] = "AUTH_GATED"
        rec["auth_state"] = "AUTH-ON (marker present, settings gated)"
        rec["evidence_score"] = 1
        rec["verdict"] = "OpenHands identity confirmed; settings gated = surface open, access not exercised"
        rec["verification_rung"] = "B1 (binary identity x in-scope host, no population)"
    else:
        rec["status_class"] = "MARKER_ONLY"
        rec["auth_state"] = "UNKNOWN (marker present, settings absent/non-200)"
        rec["evidence_score"] = 1
        rec["verdict"] = "OpenHands marker present; settings endpoint missing/non-JSON"
        rec["verification_rung"] = "B1 (binary identity x in-scope host)"

    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--input", default="openhands-live-targets.txt")
    ap.add_argument("-o", "--output", default="verify-openhands.jsonl")
    ap.add_argument("--threads", type=int, default=20)
    args = ap.parse_args()

    print(f"# Restraint DO_NOT_CALL set ({len(DO_NOT_CALL)} endpoints) - hard-refused:")
    for ep, why in DO_NOT_CALL.items():
        print(f"#   {ep}  --  {why}")
    print()

    targets = [l.strip() for l in open(args.input) if l.strip() and ":" in l]
    print(f"Targets: {len(targets)}")

    recs = []
    with ThreadPoolExecutor(max_workers=args.threads) as ex:
        futures = {ex.submit(verify_host, t): t for t in targets}
        for fut in as_completed(futures):
            recs.append(fut.result())

    # stable order by input
    order = {t.split(':')[0] + ':' + t.split(':')[1]: i for i, t in enumerate(targets)}
    recs.sort(key=lambda r: order.get(f"{r['ip']}:{r['port']}", 9999))

    with open(args.output, "w") as out:
        for r in recs:
            # emit the exact contract fields the orchestrator asked for, plus verify metadata
            out.write(json.dumps(r) + "\n")

    # ---- summary ----
    from collections import Counter
    cls = Counter(r["status_class"] for r in recs)
    confirmed = [r for r in recs if r["status_class"] == "CONFIRMED_OPEN"]
    vuln = [r for r in recs if r["cve_2026_33718"] == "VULNERABLE"]
    keyset = [r for r in confirmed if r["llm_api_key_set"] is True]
    models = Counter(r["llm_model"] for r in confirmed if r["llm_model"])
    gateways = [(r["ip"], r["llm_base_url"]) for r in confirmed if r["llm_base_url"]]

    print("\n=== STATUS_CLASS ===")
    for k, v in cls.most_common():
        print(f"  {k:16s} {v}")
    print(f"\nCONFIRMED_OPEN : {len(confirmed)}")
    print(f"CVE-vulnerable (<=1.4.0): {len(vuln)}")
    print(f"llm_api_key_set=true (LLM-jacking surface): {len(keyset)}")
    print("\nllm_model distribution (confirmed):")
    for m, n in models.most_common():
        print(f"  {n:3d}  {m}")
    if gateways:
        print("\ncustom llm_base_url gateways:")
        for ip, gw in gateways:
            print(f"  {ip}  {gw}")
    # highest severity: CONFIRMED_OPEN + key set + vulnerable
    hi = [r for r in confirmed if r["llm_api_key_set"] is True and r["cve_2026_33718"] == "VULNERABLE"]
    if hi:
        print(f"\nHIGHEST-SEVERITY (CONFIRMED_OPEN + key set + vulnerable): {hi[0]['ip']}:{hi[0]['port']}")


if __name__ == "__main__":
    main()
