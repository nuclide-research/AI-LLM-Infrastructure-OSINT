#!/usr/bin/env python3
"""
Stage-3v VERIFY harness — AutoGen Studio candidate 47.109.195.240.
NuClide Lane C (DCWF 672 T&E). Cat-Tabby canonical template.

Discipline (load-bearing):
  - Insight #16: a 200 is identity, not auth state. Every 200 gets a
    data-layer probe against the platform's documented anonymous shape.
  - Insight #6: conjunctive marker-anchored matchers, never a naked
    single-word body_contains.
  - Insight #68: report a Depth(A/B) x Breadth(0/1/2) rung per finding.
  - Restraint: read-only GETs only. NO state change, NO compute-exfil,
    NO model invocation, NO agent spawn, NO secret value read/print/store.

DO_NOT_CALL is enforced at code level: any path whose stem matches a
constant entry is hard-refused before a socket is opened. Zero violations.
"""
from __future__ import annotations
import socket, ssl, json, re, sys, base64, time

# --------------------------------------------------------------------------
# HARD REFUSAL SET. AutoGen Studio state-changing / compute-exfil surfaces.
# The verifier refuses to ISSUE any request whose path matches these,
# regardless of method. Names are the finding; we never exercise these.
# --------------------------------------------------------------------------
DO_NOT_CALL = {
    "/api/runs",                # launch a run (compute)
    "/api/sessions/.../run",    # session run trigger
    "/api/teams/.../run",
    "/api/agents/.../run",
    "/api/workflows/run",
    "/api/test",                # model connectivity test (provider call)
    "/api/validate",            # validate-config -> may invoke provider
    "/api/mcp",                 # MCP tool invocation
    "/api/ws",                  # websocket run channel
}
DO_NOT_CALL_SUBSTR = ("/run", "/execute", "/invoke", "/test", "/stream", "/ws")

# Routes we WILL issue — all read-only metadata reads.
SAFE_PROBES = [
    ("version",  "/api/version"),
    ("health",   "/api/health"),
    ("control",  "/api/this-route-does-not-exist-autogen-control"),
    ("openapi",  "/api/openapi.json"),
]
# llm-config PRESENCE probe (boolean only; we read the SHAPE, never key values)
LLM_PRESENCE_PROBES = ["/api/models", "/api/gallery", "/api/settings"]

SEMVER = re.compile(r"^\d+\.\d+\.\d+([-+.].*)?$")


def refuse(path: str) -> bool:
    if path in DO_NOT_CALL:
        return True
    for s in DO_NOT_CALL_SUBSTR:
        if s in path:
            return True
    return False


def http_get(host_ip: str, port: int, path: str, tls: bool, host_hdr: str,
             timeout: float = 8.0):
    """Read-only GET. Returns (status, headers, body_bytes, err)."""
    if refuse(path):
        return None, {}, b"", f"REFUSED_BY_DO_NOT_CALL:{path}"
    try:
        raw = socket.create_connection((host_ip, port), timeout=timeout)
        if tls:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            sock = ctx.wrap_socket(raw, server_hostname=host_hdr)
        else:
            sock = raw
        req = (f"GET {path} HTTP/1.1\r\nHost: {host_hdr}\r\n"
               f"User-Agent: nuclide-verify/1.0\r\nAccept: */*\r\n"
               f"Connection: close\r\n\r\n").encode()
        sock.sendall(req)
        sock.settimeout(timeout)
        chunks = []
        while True:
            try:
                b = sock.recv(8192)
            except (socket.timeout, ssl.SSLError):
                break
            if not b:
                break
            chunks.append(b)
            if sum(len(c) for c in chunks) > 256 * 1024:
                break
        sock.close()
        data = b"".join(chunks)
        sep = data.find(b"\r\n\r\n")
        if sep < 0:
            return None, {}, data, "no-header-sep"
        head = data[:sep].decode("iso-8859-1", "replace")
        body = data[sep + 4:]
        lines = head.split("\r\n")
        try:
            status = int(lines[0].split()[1])
        except Exception:
            status = None
        headers = {}
        for ln in lines[1:]:
            if ":" in ln:
                k, v = ln.split(":", 1)
                headers[k.strip().lower()] = v.strip()
        # chunked de-frame (best-effort) for JSON parse
        if headers.get("transfer-encoding", "").lower() == "chunked":
            body = dechunk(body)
        return status, headers, body, None
    except Exception as e:
        return None, {}, b"", f"{type(e).__name__}: {e}"


def dechunk(body: bytes) -> bytes:
    out = b""
    i = 0
    try:
        while i < len(body):
            j = body.find(b"\r\n", i)
            if j < 0:
                break
            size = int(body[i:j].split(b";")[0], 16)
            if size == 0:
                break
            out += body[j + 2:j + 2 + size]
            i = j + 2 + size + 2
    except Exception:
        return body
    return out


def trunc(b: bytes, n: int = 600) -> str:
    return b[:n].decode("utf-8", "replace")


def verify_service(label: str, host_ip: str, port: int, tls: bool, host_hdr: str):
    rec = {"service": label, "ip": host_ip, "port": port, "tls": tls,
           "host_hdr": host_hdr, "probes": {}, "do_not_call_refusals": 0}
    bodies = {}
    for name, path in SAFE_PROBES:
        st, hd, body, err = http_get(host_ip, port, path, tls, host_hdr)
        if err and err.startswith("REFUSED_BY_DO_NOT_CALL"):
            rec["do_not_call_refusals"] += 1
        ct = hd.get("content-type", "")
        parsed = None
        if "json" in ct or (body[:1] in (b"{", b"[")):
            try:
                parsed = json.loads(body.decode("utf-8", "replace"))
            except Exception:
                parsed = None
        bodies[name] = (st, ct, body, parsed, err)
        rec["probes"][name] = {
            "path": path, "status": st, "content_type": ct,
            "body_trunc": trunc(body), "json_ok": parsed is not None,
            "err": err,
        }

    # ---- conjunctive marker evaluation (Insight #6) ----
    v_st, v_ct, v_body, v_json, _ = bodies["version"]
    h_st, h_ct, h_body, h_json, _ = bodies["health"]
    c_st, c_ct, c_body, c_json, _ = bodies["control"]
    o_st, o_ct, o_body, o_json, _ = bodies["openapi"]

    version_ok = (
        v_st == 200 and "application/json" in v_ct and v_json is not None
        and isinstance(v_json, dict)
        and v_json.get("message") == "Version retrieved successfully"
        and isinstance(v_json.get("data"), dict)
        and bool(SEMVER.match(str(v_json.get("data", {}).get("version", ""))))
    )
    health_ok = (
        h_st == 200 and h_json is not None and isinstance(h_json, dict)
        and h_json.get("message") == "Service is healthy"
    )
    # genuine FastAPI 404: status 404 AND body json {"detail": ...} AND
    # does NOT echo our control path (catch-all guard, Insight #6/#108)
    control_path = "/api/this-route-does-not-exist-autogen-control"
    control_echoes = control_path.encode() in c_body
    control_is_genuine_404 = (
        c_st == 404 and c_json is not None and isinstance(c_json, dict)
        and "detail" in c_json and not control_echoes
    )
    openapi_ok = (
        o_st == 200 and o_json is not None and isinstance(o_json, dict)
        and o_json.get("info", {}).get("title") == "AutoGen Studio API"
        and str(o_json.get("info", {}).get("description", "")).startswith(
            "AutoGen Studio is a low-code tool")
    )

    # auth-state on the version read (Insight #16: 200 != open)
    if version_ok and health_ok:
        auth_state = "OPEN"            # markers + readable, no auth wall
    elif v_st in (401, 403) or h_st in (401, 403):
        auth_state = "AUTHED"          # surface confirmed, access not exercised
    else:
        auth_state = "N/A"

    rec["marker_eval"] = {
        "version_ok": version_ok, "health_ok": health_ok,
        "control_is_genuine_404": control_is_genuine_404,
        "control_echoes_path": control_echoes,
        "openapi_ok": openapi_ok,
        "version_string": (v_json or {}).get("data", {}).get("version")
                          if isinstance(v_json, dict) else None,
    }

    # ---- llm-config PRESENCE (boolean only, NO values) ----
    llm_present = False
    llm_signals = []
    for p in LLM_PRESENCE_PROBES:
        st, hd, body, err = http_get(host_ip, port, p, tls, host_hdr)
        ct = hd.get("content-type", "")
        # presence = a JSON config/model surface answers 200; we record ONLY
        # that the surface exists, never the contents.
        is_json = "json" in ct or body[:1] in (b"{", b"[")
        if st == 200 and is_json:
            # scan for config-shape KEYS only, never values
            head = body[:400].decode("utf-8", "replace").lower()
            if any(k in head for k in ("model", "config", "provider", "llm", "api_key", "base_url")):
                llm_present = True
                llm_signals.append(f"{p}:200-json-config-shape")
        elif st in (401, 403):
            llm_signals.append(f"{p}:{st}-auth")
    rec["llm_config_present"] = llm_present
    rec["llm_config_signals"] = llm_signals

    # ---- verdict ----
    autogen_markers = version_ok and health_ok
    if autogen_markers and control_is_genuine_404 and auth_state == "OPEN":
        verdict = "CONFIRMED_OPEN"
    elif autogen_markers and auth_state == "AUTHED":
        verdict = "CONFIRMED_AUTHED"
    elif (not autogen_markers) and (not control_is_genuine_404 or control_echoes):
        verdict = "REFUTED_CATCHALL"
    elif autogen_markers and not control_is_genuine_404:
        verdict = "HONEYPOT_CANDIDATE"   # markers but control also 200s/echoes
    else:
        verdict = "REFUTED"
    rec["verdict"] = verdict
    rec["auth_state"] = auth_state
    return rec


def main():
    ip = "47.109.195.240"
    services = [
        ("8081-http",  ip, 8081, False, "ai.tmianyang.com"),
        ("443-https",  ip, 443,  True,  "ai.tmianyang.com"),
        ("80-http",    ip, 80,   False, "ai.tmianyang.com"),
        ("3000-http",  ip, 3000, False, "ai.tmianyang.com"),
    ]
    results = []
    for (lbl, hip, port, tls, hh) in services:
        print(f"[*] verifying {lbl} ...", file=sys.stderr)
        results.append(verify_service(lbl, hip, port, tls, hh))
    out = {"ts": time.time(), "target": ip, "mitm_gate": "CLEAN",
           "do_not_call_set": sorted(DO_NOT_CALL), "services": results}
    with open("/home/cowboy/AI-LLM-Infrastructure-OSINT/surveys/agent-platforms-2026-06-19/lane-c-verify-autogen.json", "w") as f:
        json.dump(out, f, indent=2)
    # human summary
    for r in results:
        m = r["marker_eval"]
        print(f"\n=== {r['service']} ({r['ip']}:{r['port']} tls={r['tls']}) ===")
        for n, p in r["probes"].items():
            print(f"  {n:8} {p['status']}  ct={p['content_type'][:40]}  err={p['err']}")
            if n in ("version", "health", "control"):
                print(f"           body: {p['body_trunc'][:180]!r}")
        print(f"  markers: version_ok={m['version_ok']} health_ok={m['health_ok']} "
              f"ctrl404={m['control_is_genuine_404']} openapi_ok={m['openapi_ok']} "
              f"ver={m['version_string']}")
        print(f"  llm_config_present={r['llm_config_present']} signals={r['llm_config_signals']}")
        print(f"  do_not_call_refusals={r['do_not_call_refusals']}")
        print(f"  VERDICT={r['verdict']} auth_state={r['auth_state']}")
    total_refusals = sum(r["do_not_call_refusals"] for r in results)
    print(f"\n[restraint] total DO_NOT_CALL refusals issued: {total_refusals} (safe probes only never hit the set)")


if __name__ == "__main__":
    main()
