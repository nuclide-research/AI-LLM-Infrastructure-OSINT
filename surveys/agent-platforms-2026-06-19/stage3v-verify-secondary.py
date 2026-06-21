#!/usr/bin/env python3
"""
Stage 3v VERIFY - secondary agent platforms (SuperAGI / AgentGPT / CrewAI Studio / BabyAGI).

Lane C (DCWF 672 AI Test & Evaluation Specialist) load-bearing probe.
MITM gate run separately (mitm-gate-secondary.json) BEFORE any L7 conclusion: CLEAN.

Discipline (methodology Stage 3v):
  - Conjunctive marker-anchored matchers, never a naked single-word body_contains.
    Each platform's confirm requires a vendor-unique marker (title/DOM-id/literal-JSON
    string) AND a data-layer 200, so an nginx default / LBot catch-all / tarpit 200
    cannot earn the platform label.
  - 200-with-data, never 200-alone (Insight #16: a 200 is identity, not auth state).
  - Sample minimally; names ARE the finding (restraint ethic). Record provider-key
    presence as a BOOLEAN and model/tool names only; NEVER a secret value.
  - Verification rung pair (Insight #68): Inner A/B x Outer 0/1/2 per host.
  - DO_NOT_CALL hard-refused at code level: every state-changing / RCE primitive is a
    constant and the issuer refuses it. Zero violations. (BabyAGI write-then-run is the
    sharp edge: PUT /api/function/* + POST /api/execute/* = arbitrary code exec.)

Read-only GET only. http->https follow. Low concurrency. One pass.
"""
import argparse, json, ssl, socket, urllib.request, urllib.error, datetime, re, http.client
from concurrent.futures import ThreadPoolExecutor, as_completed

# ----- Restraint: state-changing / RCE / compute-exfil set. Hard-refused. -----
DO_NOT_CALL = {
    # BabyAGI new-framework write-then-run RCE primitive
    "PUT /api/function/{name}": "BabyAGI: registers arbitrary function body = code-write half of RCE",
    "POST /api/function/{name}": "BabyAGI: function create/update = code-write",
    "POST /api/execute/{name}": "BabyAGI: executes a registered function = RCE run half",
    "POST /api/functions": "BabyAGI: function create = code-write",
    # SuperAGI state-change / agent-run
    "POST /api/agents": "SuperAGI: creates an agent = compute-exfil + state change",
    "POST /api/agentexecutions": "SuperAGI: runs an agent = compute-exfil",
    "PUT /api/organisations/get/user": "SuperAGI: org mutation = state change",
    "POST /api/configs": "SuperAGI: writes provider/model keys = cred-set + state change",
    # AgentGPT (Reworkd) agent-run / chain-exec
    "POST /api/agent": "AgentGPT: starts an autonomous agent chain = compute-exfil",
    "POST /api/agent/start": "AgentGPT: agent start = compute-exfil",
    "POST /api/agent/analyze": "AgentGPT: LLM analyze call = compute-exfil",
    "POST /api/agent/execute": "AgentGPT: task execute = compute-exfil",
    # CrewAI Studio (Streamlit) crew kickoff
    "POST /_stcore/upload_file": "CrewAI Studio: file upload = state change",
    "*kickoff*": "CrewAI Studio: crew kickoff via Streamlit = compute-exfil",
}

TIMEOUT = 8
UA = "nuclide-verify/1.0 (read-only AI-infra exposure research; metadata-only)"


def _refuse_guard(method, path):
    """Code-level hard refusal. Returns True if the call must be refused."""
    m = method.upper()
    if m in ("POST", "PUT", "DELETE", "PATCH"):
        return True  # this lane issues GET only, full stop
    low = path.lower()
    for bad in ("/api/execute", "/api/function/", "kickoff", "/api/agent/start",
                "/api/agent/analyze", "/api/agent/execute"):
        if bad in low:
            return True
    return False


def probe(url, method="GET", headers=None):
    """Single read-only HTTP probe. Returns (status, headers, body[:16384], err)."""
    from urllib.parse import urlparse
    p = urlparse(url)
    if _refuse_guard(method, p.path):
        return None, {}, "", "REFUSED-BY-DO_NOT_CALL"
    req = urllib.request.Request(
        url, method="GET",
        headers={"User-Agent": UA, "Accept": "*/*", **(headers or {})},
    )
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT, context=ctx) as r:
            return r.status, dict(r.headers), r.read(32768).decode(errors="replace"), None
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers or {}), (e.read(8192).decode(errors="replace") if e.fp else ""), None
    except (urllib.error.URLError, socket.timeout, ConnectionError, TimeoutError,
            OSError, http.client.HTTPException, ssl.SSLError, ValueError) as e:
        return None, {}, "", f"{type(e).__name__}: {e}"
    except Exception as e:
        return None, {}, "", f"{type(e).__name__}: {e}"


def get_root(ip, port):
    """GET / with http->https follow. Returns (base, status, hdrs, body, err)."""
    order = [("https", port)] if port in (443, 8443) else [("http", port), ("https", port)]
    last = None
    for scheme, p in order:
        base = f"{scheme}://{ip}:{p}"
        status, hdrs, body, err = probe(f"{base}/")
        last = (base, status, hdrs, body, err)
        if status in (301, 302, 307, 308):
            loc = (hdrs.get("Location") or hdrs.get("location") or "")
            if loc.startswith("https://"):
                m = re.match(r"https://([^/:]+)(?::(\d+))?", loc)
                if m:
                    hp = int(m.group(2) or 443)
                    base2 = f"https://{ip}:{hp}"
                    s2, h2, b2, e2 = probe(f"{base2}/")
                    last = (base2, s2, h2, b2, e2)
                    if s2 and s2 < 400:
                        return last
        if status and status < 400:
            return last
    return last


def title_of(body):
    if not body:
        return None
    m = re.search(r"<title[^>]*>(.*?)</title>", body, re.I | re.S)
    return m.group(1).strip() if m else None


def jload(body):
    try:
        return json.loads(body)
    except (json.JSONDecodeError, TypeError):
        return None


def base_rec(platform, ip, port):
    return {
        "platform": platform, "ip": ip, "port": port, "scheme": None,
        "status_class": "DEAD", "marker_hit": False, "http_status": None,
        "title": None, "provider_key_present": None,
        "models": [], "tools": [],
        "probes": {}, "verdict": None, "auth_state": None,
        "evidence_score": 0, "identity_signals": [],
        "restraint_compliance": "OK - GET-only, no DO_NOT_CALL endpoints exercised",
        "verification_rung": None, "notes": "",
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }


# ---------------- SuperAGI ----------------
def verify_superagi(ip, ports):
    rec = base_rec("superagi", ip, None)
    for port in [p for p in (3000, 443, 80) if p in ports] or ports:
        base, status, hdrs, body, err = get_root(ip, port)
        rec["scheme"] = base.split("://")[0]; rec["port"] = int(base.split(":")[-1])
        rec["http_status"] = status
        rec["probes"]["/"] = {"port": rec["port"], "status": status, "err": err}
        if status is None:
            continue
        title = title_of(body); rec["title"] = title
        title_hit = bool(title and "superagi" in title.lower())
        # data layer: org/user or toolkit list unauth
        data_hit = False
        for dp in ("/api/organisations/get/user", "/api/toolkits/get/list"):
            ds, _, db, de = probe(f"{base}{dp}")
            rec["probes"][dp] = {"status": ds, "err": de, "len": len(db)}
            dj = jload(db) if ds == 200 else None
            if ds == 200 and dj is not None and (isinstance(dj, dict) or isinstance(dj, list)):
                data_hit = True
                rec["identity_signals"].append(f"{dp} 200 + JSON")
                if isinstance(dj, list):
                    for t in dj[:25]:
                        n = t.get("name") if isinstance(t, dict) else None
                        if n: rec["tools"].append(n)
                if isinstance(dj, dict) and "organisation_id" in str(dj):
                    rec["identity_signals"].append("org context returned")
                break
            if ds in (401, 403):
                rec["auth_state"] = "AUTH-ON (data gated)"
        if title_hit:
            rec["marker_hit"] = True
            rec["identity_signals"].insert(0, "<title>SuperAGI</title>")
        _classify_secondary(rec, title_hit, data_hit, status)
        if rec["status_class"] != "DEAD":
            return rec
    if rec["status_class"] == "DEAD":
        rec["verdict"] = "DEAD - no web response on SuperAGI ports"
        rec["verification_rung"] = "0 (no live host)"
        rec["evidence_score"] = -1
    return rec


# ---------------- AgentGPT (Reworkd) ----------------
AGENTGPT_TOOL_LITERAL = 'TODO: Change to image of tool'
def verify_agentgpt(ip, ports, honeypot_flag):
    rec = base_rec("agentgpt", ip, None)
    if honeypot_flag:
        rec["notes"] = ("ALL-16-PORTS-OPEN tarpit/honeypot tell; require vendor-unique "
                        "literal marker to confirm, else NOT_PLATFORM")
    for port in [p for p in (3000, 8000, 443, 80) if p in ports] or ports:
        base, status, hdrs, body, err = get_root(ip, port)
        rec["scheme"] = base.split("://")[0]; rec["port"] = int(base.split(":")[-1])
        rec["http_status"] = status
        rec["probes"]["/"] = {"port": rec["port"], "status": status, "err": err}
        if status is None:
            continue
        title = title_of(body); rec["title"] = title
        title_hit = bool(title and "agentgpt" in title.lower())
        # data-layer + VENDOR-UNIQUE literal: /api/agent/tools must contain the TODO literal
        data_hit = False
        ts, _, tb, te = probe(f"{base}/api/agent/tools")
        rec["probes"]["/api/agent/tools"] = {"status": ts, "err": te, "len": len(tb)}
        literal_hit = (ts == 200 and AGENTGPT_TOOL_LITERAL in tb)
        if literal_hit:
            data_hit = True
            rec["identity_signals"].append("/api/agent/tools 200 + literal 'TODO: Change to image of tool'")
            tj = jload(tb)
            if isinstance(tj, dict):
                tools = tj.get("tools") or tj.get("data") or []
                if isinstance(tools, list):
                    for t in tools[:25]:
                        n = t.get("name") if isinstance(t, dict) else None
                        if n: rec["tools"].append(n)
            elif isinstance(tj, list):
                for t in tj[:25]:
                    n = t.get("name") if isinstance(t, dict) else None
                    if n: rec["tools"].append(n)
        elif ts in (401, 403):
            rec["auth_state"] = "AUTH-ON (tools gated)"
        # auth-off tell: /signin renders insecure dev banner
        ss, _, sb, se = probe(f"{base}/signin")
        rec["probes"]["/signin"] = {"status": ss, "err": se}
        if ss == 200 and ("Development Only (Insecure)" in sb or "Username" in sb and "Insecure" in sb):
            rec["identity_signals"].append("/signin 'Development Only (Insecure)' auth-off tell")
            rec["notes"] += " | dev-insecure signin banner present"
        if title_hit:
            rec["marker_hit"] = True
            rec["identity_signals"].insert(0, "<title>AgentGPT</title>")
        # honeypot guard: marker_hit requires the literal (vendor-unique) for the all-ports host
        conjunct_marker = (title_hit and data_hit) if honeypot_flag else (title_hit or data_hit)
        if honeypot_flag and not data_hit:
            rec["marker_hit"] = False
            rec["status_class"] = "NOT_PLATFORM"
            rec["verdict"] = ("HONEYPOT/tarpit: all 16 ports open, no vendor-unique AgentGPT "
                              "literal on /api/agent/tools = NOT_REAL")
            rec["auth_state"] = "N/A (honeypot)"
            rec["evidence_score"] = -1
            rec["verification_rung"] = "1 (in-scope host, no platform marker - honeypot)"
            return rec
        rec["marker_hit"] = bool(title_hit or data_hit)
        _classify_secondary(rec, conjunct_marker if honeypot_flag else (title_hit or data_hit), data_hit, status)
        if rec["status_class"] != "DEAD":
            return rec
    if rec["status_class"] == "DEAD":
        rec["verdict"] = "DEAD - no web response on AgentGPT ports"
        rec["verification_rung"] = "0 (no live host)"
        rec["evidence_score"] = -1
    return rec


# ---------------- CrewAI Studio (Streamlit) ----------------
def verify_crewai(ip, ports):
    rec = base_rec("crewai_studio", ip, None)
    for port in [p for p in (8080, 8501, 443, 80) if p in ports] or ports:
        base, status, hdrs, body, err = get_root(ip, port)
        rec["scheme"] = base.split("://")[0]; rec["port"] = int(base.split(":")[-1])
        rec["http_status"] = status
        rec["probes"]["/"] = {"port": rec["port"], "status": status, "err": err}
        if status is None:
            continue
        title = title_of(body); rec["title"] = title
        title_hit = bool(title and "crewai studio" in title.lower())
        streamlit_hit = bool(body and ("/static/" in body or "stStatusWidget" in body or "streamlit" in body.lower()))
        # data-layer: streamlit health
        hs, _, hb, he = probe(f"{base}/_stcore/health")
        rec["probes"]["/_stcore/health"] = {"status": hs, "body": hb[:32], "err": he}
        health_hit = (hs == 200 and "ok" in hb.lower())
        data_hit = health_hit and streamlit_hit
        if health_hit:
            rec["identity_signals"].append("/_stcore/health 200 ok")
        if streamlit_hit:
            rec["identity_signals"].append("Streamlit framing (/static/ or stStatusWidget)")
        if title_hit:
            rec["marker_hit"] = True
            rec["identity_signals"].insert(0, "<title>CrewAI Studio</title>")
        # CrewAI title is conjunctive with streamlit; streamlit alone is not CrewAI
        marker = title_hit and (streamlit_hit or health_hit)
        rec["marker_hit"] = marker
        if not title_hit and streamlit_hit:
            rec["status_class"] = "NOT_PLATFORM"
            rec["verdict"] = "Streamlit app present but no CrewAI Studio title marker = not confirmed CrewAI"
            rec["auth_state"] = "N/A"
            rec["evidence_score"] = -1
            rec["verification_rung"] = "1 (in-scope host, generic Streamlit, no CrewAI marker)"
            rec["notes"] = "Streamlit framework detected; CrewAI-specific title absent"
            return rec
        _classify_secondary(rec, marker, data_hit, status)
        if rec["status_class"] != "DEAD":
            return rec
    if rec["status_class"] == "DEAD":
        rec["verdict"] = "DEAD - no web response on CrewAI ports"
        rec["verification_rung"] = "0 (no live host)"
        rec["evidence_score"] = -1
    return rec


# ---------------- BabyAGI (new framework) ----------------
def verify_babyagi(ip, ports):
    rec = base_rec("babyagi", ip, None)
    rec["notes"] = "RCE primitive PUT /api/function/* + POST /api/execute/* hard-refused; GET-only"
    for port in [p for p in (8080, 80, 443) if p in ports] or ports:
        base, status, hdrs, body, err = get_root(ip, port)
        rec["scheme"] = base.split("://")[0]; rec["port"] = int(base.split(":")[-1])
        rec["http_status"] = status
        rec["probes"]["/"] = {"port": rec["port"], "status": status, "err": err}
        if status is None:
            continue
        title = title_of(body); rec["title"] = title
        title_hit = bool(title and "function dashboard" in title.lower())
        dom_hit = bool(body and 'functionGrid' in body)
        # data-layer: GET /api/functions (read-only) returns a JSON array
        fs, _, fb, fe = probe(f"{base}/api/functions")
        rec["probes"]["/api/functions"] = {"status": fs, "err": fe, "len": len(fb)}
        fj = jload(fb) if fs == 200 else None
        data_hit = False
        if fs == 200 and isinstance(fj, (list, dict)):
            data_hit = True
            rec["identity_signals"].append("/api/functions 200 + JSON array")
            arr = fj if isinstance(fj, list) else (fj.get("functions") or fj.get("data") or [])
            if isinstance(arr, list):
                for f in arr[:25]:
                    n = f.get("name") if isinstance(f, dict) else None
                    if n: rec["tools"].append(n)
        elif fs in (401, 403):
            rec["auth_state"] = "AUTH-ON (functions gated)"
        if title_hit:
            rec["identity_signals"].insert(0, "<title>Function Dashboard</title>")
        if dom_hit:
            rec["identity_signals"].append("DOM id functionGrid")
        marker = (title_hit and dom_hit) or data_hit
        rec["marker_hit"] = bool(marker)
        _classify_secondary(rec, marker, data_hit, status)
        if rec["status_class"] != "DEAD":
            return rec
    if rec["status_class"] == "DEAD":
        rec["verdict"] = "DEAD - no web response on BabyAGI ports"
        rec["verification_rung"] = "0 (no live host)"
        rec["evidence_score"] = -1
    return rec


def _classify_secondary(rec, marker_hit, data_hit, status):
    """Shared classifier. CONFIRMED_OPEN only on marker + data-layer 200 (auth-off)."""
    if marker_hit and data_hit:
        rec["status_class"] = "CONFIRMED_OPEN"
        rec["auth_state"] = rec["auth_state"] or "AUTH-OFF (data readable unauth)"
        if "OFF" not in (rec["auth_state"] or ""):
            rec["auth_state"] = "AUTH-OFF (data readable unauth)"
        rec["evidence_score"] = 2
        rec["verdict"] = "confirmed; vendor marker + data-layer 200 unauth = auth-off"
        rec["verification_rung"] = "A2 (logic-depth read x population-data read)"
    elif marker_hit and not data_hit:
        if rec["auth_state"] and "AUTH-ON" in rec["auth_state"]:
            rec["status_class"] = "AUTH_GATED"
            rec["evidence_score"] = 1
            rec["verdict"] = "identity confirmed; data gated = surface open, access not exercised"
            rec["verification_rung"] = "B1 (binary identity x in-scope host, no population)"
        else:
            rec["status_class"] = "MARKER_ONLY"
            rec["evidence_score"] = 1
            rec["auth_state"] = rec["auth_state"] or "UNKNOWN (marker present, data endpoint absent/non-200)"
            rec["verdict"] = "marker present; data endpoint missing/non-JSON - not confirmed open"
            rec["verification_rung"] = "B1 (binary identity x in-scope host)"
    else:
        rec["status_class"] = "NOT_PLATFORM"
        rec["evidence_score"] = -1
        rec["auth_state"] = rec["auth_state"] or "N/A"
        rec["verdict"] = "refuted: no vendor-unique marker (bare-200/default-page/catch-all guarded)"
        rec["verification_rung"] = "1 (in-scope host reached, no platform marker)"


def parse_line(line):
    # format: "IP ports=[a, b, c]"
    ip = line.split()[0].strip()
    m = re.search(r"ports=\[([^\]]*)\]", line)
    ports = []
    if m:
        ports = [int(x) for x in re.findall(r"\d+", m.group(1))]
    return ip, ports


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-d", "--dir", default=".")
    ap.add_argument("-o", "--output", default="verify-secondary.jsonl")
    ap.add_argument("--threads", type=int, default=6)
    args = ap.parse_args()

    print(f"# Restraint DO_NOT_CALL set ({len(DO_NOT_CALL)} endpoints) - hard-refused (GET-only lane):")
    for ep, why in DO_NOT_CALL.items():
        print(f"#   {ep}  --  {why}")
    print()

    import os
    def load(fn):
        path = os.path.join(args.dir, fn)
        return [parse_line(l) for l in open(path) if l.strip()]

    jobs = []
    for ip, ports in load("superagi-live.txt"):
        jobs.append(("superagi", ip, ports))
    for ip, ports in load("agentgpt-live.txt"):
        hp = (ip == "82.156.224.203") or (len(ports) >= 14)
        jobs.append(("agentgpt", ip, ports, hp))
    for ip, ports in load("crewai_studio-live.txt"):
        jobs.append(("crewai_studio", ip, ports))
    for ip, ports in load("babyagi-live.txt"):
        jobs.append(("babyagi", ip, ports))

    def run(job):
        plat = job[0]
        if plat == "superagi":
            return verify_superagi(job[1], job[2])
        if plat == "agentgpt":
            return verify_agentgpt(job[1], job[2], job[3])
        if plat == "crewai_studio":
            return verify_crewai(job[1], job[2])
        if plat == "babyagi":
            return verify_babyagi(job[1], job[2])

    recs = []
    with ThreadPoolExecutor(max_workers=args.threads) as ex:
        futs = {ex.submit(run, j): j for j in jobs}
        for f in as_completed(futs):
            recs.append(f.result())

    plat_order = {"superagi": 0, "agentgpt": 1, "crewai_studio": 2, "babyagi": 3}
    recs.sort(key=lambda r: (plat_order.get(r["platform"], 9), r["ip"]))

    with open(os.path.join(args.dir, args.output), "w") as out:
        for r in recs:
            slim = {
                "platform": r["platform"], "ip": r["ip"], "port": r["port"],
                "scheme": r["scheme"], "status_class": r["status_class"],
                "marker_hit": r["marker_hit"], "http_status": r["http_status"],
                "title": r["title"], "auth_state": r["auth_state"],
                "provider_key_present": r["provider_key_present"],
                "models": r["models"], "tools": r["tools"][:30],
                "evidence_score": r["evidence_score"],
                "identity_signals": r["identity_signals"],
                "verification_rung": r["verification_rung"],
                "restraint_compliance": r["restraint_compliance"],
                "verdict": r["verdict"], "notes": r["notes"],
                "probes": r["probes"], "timestamp": r["timestamp"],
            }
            out.write(json.dumps(slim) + "\n")

    from collections import Counter
    print("=== per-platform status_class ===")
    for plat in ("superagi", "agentgpt", "crewai_studio", "babyagi"):
        sub = [r for r in recs if r["platform"] == plat]
        c = Counter(r["status_class"] for r in sub)
        print(f"  {plat:15s} n={len(sub):2d}  " + "  ".join(f"{k}={v}" for k, v in c.most_common()))
    conf = [r for r in recs if r["status_class"] == "CONFIRMED_OPEN"]
    print(f"\nCONFIRMED_OPEN auth-off: {len(conf)}")
    for r in conf:
        print(f"  {r['platform']} {r['ip']}:{r['port']} {r['scheme']} rung={r['verification_rung']} tools={r['tools'][:6]}")
    refused = sum(1 for r in recs for p in r["probes"].values() if isinstance(p, dict) and p.get("err") == "REFUSED-BY-DO_NOT_CALL")
    print(f"\nDO_NOT_CALL refusals triggered: {refused} (expected 0 - lane is GET-only by construction)")
    print(f"restraint_compliance OK: {sum(1 for r in recs if r['restraint_compliance'].startswith('OK'))}/{len(recs)}")


if __name__ == "__main__":
    main()
