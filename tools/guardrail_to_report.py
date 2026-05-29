#!/usr/bin/env python3
"""
guardrail_to_report.py - adapter: guardrail-probe NDJSON -> visor-report schema.

Per-category adapter (copy-of-finops_to_report pattern). Usage:
    python3 guardrail_to_report.py /tmp/guardrail-probe-results.ndjson | visor-report.py render - -o report.html
"""
import json, sys

# Attribution hints are SURVEY DATA (real IPs) and are NOT committed (OSINT redaction discipline).
# Load from a local gitignored JSON via ATTR_FILE=<path> ({"attr": {ip:[op,conf,note]}}); empty
# here so the committed tool carries no harvested data.
import os as _os
_af = _os.environ.get("ATTR_FILE", "")
_ad = json.load(open(_af)) if (_af and _os.path.exists(_af)) else {}
ATTR = {ip: tuple(v) for ip, v in _ad.get("attr", {}).items()}  # {ip: (operator, confidence, note)}


def build(rows):
    hosts = {}
    for r in rows:
        ip = r['ip']
        conf = r.get('confirmed'); auth = r.get('auth_state'); plat = r.get('platform')
        a = ATTR.get(ip)
        flags = []
        if conf and auth == 'OPEN_API': flags.append({"cls": "cred", "title": "unauthenticated safety layer"})
        elif conf: flags.append({"cls": "attr", "title": "guardrail confirmed (auth-enforced)"})
        badges = []
        if plat: badges.append({"text": plat, "cls": ""})
        if auth == 'OPEN_API': badges.append({"text": "OPEN_API", "cls": "cred"})
        elif auth == 'AUTH': badges.append({"text": "auth enforced", "cls": ""})
        elif not conf: badges.append({"text": "not confirmed live", "cls": ""})
        spec = [["Platform", plat or '—', ""], ["Port", str(r.get('port') or '—'), ""],
                ["Auth state", auth or '—', "cy" if auth == 'OPEN_API' else ""],
                ["Confirm signal", r.get('signal') or '—', ""],
                ["Server", r.get('server') or '—', ""],
                ["Scan endpoint status", str(r.get('scan_endpoint_status') or '—'), ""],
                ["Live HTTP ports", ", ".join(map(str, r.get('live_http_ports') or [])) or '—', ""]]
        tag_groups = []
        sc = r.get('scanners_exposed')
        if isinstance(sc, list) and sc:
            tag_groups.append({"label": "Scanner config exposed (operator threat model)",
                               "legend_html": "<span style='color:var(--hi)'>active scanners</span>",
                               "tags": [{"name": s, "cls": "sec"} for s in sc]})
        hosts[ip] = {"label": ip, "chip": {"note": (auth if auth in ('OPEN_API', 'AUTH') else ''), "flags": flags},
                     "badges": badges, "spec": spec, "tag_groups": tag_groups,
                     "attribution": ({"op": a[0], "conf": a[1], "note": a[2]} if a else None),
                     "_conf": conf, "_auth": auth, "_plat": plat}

    def ips(p): return sorted([ip for ip, h in hosts.items() if p(h)])
    findings = [
     {"id": "F1", "tier": "MEDIUM", "title": "Unauthenticated LLM Guard - the safety layer itself is open and bypassable",
      "why": "A guardrail server exposed with no auth means the safety control is not enforcing on its callers: the guard can be queried freely (bypass-recon + compute abuse), and its scanner configuration is readable - which publishes the operator's threat model. This is the auth-on-default thesis in the one place you would most expect auth: a security tool.",
      "basis": "platform==llm-guard AND POST /analyze/prompt returns 200 with no auth (one benign test prompt); scanners_results returned the active scanner list.",
      "hosts": ips(lambda h: h['_conf'] and h['_auth'] == 'OPEN_API')},
     {"id": "F2", "tier": "INFO", "title": "Confirmed live LLM Guard instances (population)",
      "why": "Hosts that the Shodan dork flagged AND verified as live LLM Guard servers (OpenAPI title / root body match).",
      "basis": "platform==llm-guard AND confirmed.",
      "hosts": ips(lambda h: h['_conf'] and h['_plat'] == 'llm-guard')},
     {"id": "F3", "tier": "INFO", "title": "Auth-enforced LLM Guard (the control is configured correctly)",
      "why": "Confirmed LLM Guard servers that return 401/403 on the scan endpoint - the operator set AUTH_TOKEN. The positive control: auth-on-default is opt-in, and these operators opted in.",
      "basis": "platform==llm-guard AND auth_state==AUTH.",
      "hosts": ips(lambda h: h['_conf'] and h['_auth'] == 'AUTH')},
     {"id": "F4", "tier": "INFO", "title": "Dork hits not confirmed live (stale index / no signal)",
      "why": "Shodan flagged the LLM Guard / Guardrails marker but the host did not verify as a live guardrail API on the probed ports - stale Shodan index, host down, or the marker was in non-API HTML.",
      "basis": "not confirmed by the verification probe.",
      "hosts": ips(lambda h: not h['_conf'])},
    ]
    for h in hosts.values():
        for k in [k for k in h if k.startswith('_')]: del h[k]
    nconf = sum(1 for r in rows if r.get('confirmed'))
    nopen = sum(1 for r in rows if r.get('confirmed') and r.get('auth_state') == 'OPEN_API')
    meta = {"org": "NuClide Research", "kind": "// Field Survey", "date": "2026-05-29",
            "title_html": "The safety layer ships <span class='em'>auth-off</span>, too.",
            "subtitle_html": "LLM guardrail engines (LLM Guard, Guardrails AI, NeMo, Vigil) almost all ship with auth off by default and assume a trusted network. This survey verified the handful that are internet-exposed. The category is Shodan-thin; the finding is what happens when a <b>security control itself</b> is the unauthenticated service.",
            "stats": [{"value": len(rows), "label": "harvested", "style": ""},
                      {"value": nconf, "label": "live guardrails", "style": "cyan"},
                      {"value": nopen, "label": "unauthenticated", "style": "hot"},
                      {"value": nconf - nopen, "label": "auth enforced", "style": ""}]}
    panels = [
     {"title": "What an exposed guardrail gives an attacker", "kind": "steps", "items": [
       "Find the guardrail server (here: LLM Guard's 'LLM Guard API' OpenAPI title on :8000).",
       "If unauthenticated, POST /analyze/prompt freely - the safety layer does not gate callers.",
       "Read the active scanner config (PromptInjection, Secrets, Toxicity) = the operator's threat model.",
       "Probe the guard for bypasses, or abuse its compute. Work stopped at the config read (one benign prompt)."]},
     {"title": "Honest negative space", "kind": "bullets", "items": [
       "Category is Shodan-thin: 21 dorks, 10 hits, only LLM Guard's OpenAPI title indexes reliably.",
       "Only 1 of 4 live LLM Guard servers is unauthenticated; 3 correctly enforce AUTH_TOKEN.",
       "No CRITICAL: no scan-cache (user prompts) was read, no upstream LLM key extracted, no exec.",
       "5 dork hits did not confirm live - stale Shodan index or non-API HTML matches.",
       "Probing done read-only through Mullvad; one benign test prompt per open host, scan cache untouched."]},
    ]
    return {"meta": meta, "findings": findings, "hosts": hosts, "panels": panels}


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else '-'
    rows = [json.loads(l) for l in (sys.stdin if src == '-' else open(src)) if l.strip()]
    json.dump(build(rows), sys.stdout, ensure_ascii=False)


if __name__ == "__main__":
    main()
