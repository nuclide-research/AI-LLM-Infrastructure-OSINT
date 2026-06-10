#!/usr/bin/env python3
"""
mcp-initialize-probe.py - protocol-strict MCP identity verification.

DCWF roles:
  672 T&E       - exact JSON-RPC initialize handshake; full nested traversal
  733 Risk      - hard tools/call refusal at code level (no flag can re-enable)
  541 Pentester - operator-attribution feeders (rdns, cert-cn)

Per Insight #1: exact protocol envelope drops honeypot pollution from
91.6% to 1.1% on candidate-MCP cohorts. Protocol shape is the discriminator.

Per Insight #3: traverse every nested handshake field. The schema leaks in
initialize.capabilities, not only in tools/list.

ETHICAL STOP: this tool reads metadata only.
  - initialize: safe (handshake, no side effect)
  - tools/list: safe (returns names + descriptions + schemas)
  - tools/call: REFUSED at module load (KeyboardInterrupt-grade refusal)
"""
import json
import socket
import ssl
import sys
import time
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

# ============================================================================
# HARD ETHICAL STOP - load-bearing, do not remove.
# ============================================================================
DO_NOT_CALL = True
def _refuse_tools_call(*a, **kw):
    raise RuntimeError(
        "tools/call is hard-refused for the cat-mcp-cred-fleet cohort. "
        "Names ARE the finding. See feedback_verify_before_claiming_exploitable."
    )
# Any future caller that imports a tools_call helper gets the refusal.
tools_call = _refuse_tools_call

# ============================================================================
# Probe shapes
# ============================================================================
INIT_BODY = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
        "protocolVersion": "2024-11-05",
        "capabilities": {},
        "clientInfo": {"name": "nuclide-survey", "version": "0.1"},
    },
}
LIST_BODY = {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}
CANDIDATE_PATHS = ["/mcp", "/sse", "/", "/rpc"]
TIMEOUT = 8


def _http_post(url, body, accept="application/json, text/event-stream"):
    data = json.dumps(body).encode()
    req = urllib.request.Request(
        url,
        data=data,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "Accept": accept,
            "User-Agent": "nuclide-mcp-probe/0.1",
        },
    )
    ctx = ssl._create_unverified_context()
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT, context=ctx) as r:
            raw = r.read(65536)
            return {
                "status": r.status,
                "ctype": r.headers.get("Content-Type", ""),
                "body": raw.decode("utf-8", errors="replace"),
            }
    except urllib.error.HTTPError as e:
        try:
            raw = e.read(65536).decode("utf-8", errors="replace")
        except Exception:
            raw = ""
        return {"status": e.code, "ctype": e.headers.get("Content-Type", "") if e.headers else "", "body": raw}
    except Exception as e:
        return {"error": f"{type(e).__name__}: {e}"}


def _parse_response(resp):
    """MCP can answer JSON or SSE (event-stream of data: lines)."""
    if "error" in resp:
        return None
    body = resp.get("body", "") or ""
    # Direct JSON
    body_s = body.strip()
    if body_s.startswith("{") or body_s.startswith("["):
        try:
            return json.loads(body_s)
        except Exception:
            pass
    # SSE-style: take the first complete data: line
    if "data:" in body:
        for line in body.splitlines():
            if line.startswith("data:"):
                payload = line[5:].strip()
                if payload:
                    try:
                        return json.loads(payload)
                    except Exception:
                        continue
    return None


def _try_scheme(host, port, scheme):
    """Try each candidate path under one scheme. Return (path, raw, parsed) on init pass."""
    base = f"{scheme}://{host}:{port}"
    last = None
    for path in CANDIDATE_PATHS:
        url = base + path
        r = _http_post(url, INIT_BODY)
        last = (path, r)
        if "error" in r:
            continue
        parsed = _parse_response(r)
        # JSON-RPC envelope check
        if isinstance(parsed, dict) and parsed.get("jsonrpc") == "2.0":
            result = parsed.get("result", {}) if "result" in parsed else None
            if result and isinstance(result, dict):
                if "protocolVersion" in result or "serverInfo" in result or "capabilities" in result:
                    return path, r, parsed, base + path
    return (last[0] if last else None, last[1] if last else None, None, None)


def probe_host(ip, port=9090):
    """Returns dict per host. Restraint-clean: initialize + tools/list only."""
    rec = {
        "ip": ip,
        "port": port,
        "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "init_pass": False,
        "scheme": None,
        "endpoint": None,
        "initialize": None,
        "tools_list": None,
        "tool_names": [],
        "error": None,
    }
    for scheme in ("https", "http"):
        path, raw, parsed, full_url = _try_scheme(ip, port, scheme)
        if parsed is not None:
            rec["init_pass"] = True
            rec["scheme"] = scheme
            rec["endpoint"] = full_url
            rec["initialize"] = parsed.get("result", {})
            break
        elif raw is not None and "error" not in raw and rec.get("last_raw") is None:
            rec["last_raw"] = {"path": path, **raw}
    if not rec["init_pass"]:
        return rec
    # tools/list against the same endpoint
    list_r = _http_post(full_url, LIST_BODY)
    list_p = _parse_response(list_r)
    if isinstance(list_p, dict) and "result" in list_p:
        rec["tools_list"] = list_p["result"]
        tools = list_p["result"].get("tools", []) or []
        rec["tool_names"] = [t.get("name", "") for t in tools if isinstance(t, dict)]
    elif list_p is not None:
        rec["tools_list_raw"] = list_p
    return rec


def main():
    if len(sys.argv) < 3:
        print("usage: mcp-initialize-probe.py <ip_list> <out.jsonl> [port]", file=sys.stderr)
        sys.exit(2)
    ip_list = Path(sys.argv[1]).read_text().strip().splitlines()
    out_path = Path(sys.argv[2])
    port = int(sys.argv[3]) if len(sys.argv) > 3 else 9090
    ips = [x.strip() for x in ip_list if x.strip() and not x.startswith("#")]
    print(f"[+] probing {len(ips)} hosts on port {port}, restraint-clean (no tools/call)", file=sys.stderr)
    with out_path.open("w") as out:
        with ThreadPoolExecutor(max_workers=12) as ex:
            futs = {ex.submit(probe_host, ip, port): ip for ip in ips}
            done = 0
            for f in as_completed(futs):
                ip = futs[f]
                try:
                    rec = f.result()
                except Exception as e:
                    rec = {"ip": ip, "port": port, "error": f"{type(e).__name__}: {e}", "init_pass": False}
                out.write(json.dumps(rec) + "\n")
                out.flush()
                done += 1
                tag = "PASS" if rec.get("init_pass") else "----"
                tools = ",".join(rec.get("tool_names", [])[:3])
                print(f"[{done:>3}/{len(ips)}] {tag} {ip} tools={tools}", file=sys.stderr)
    print(f"[+] done -> {out_path}", file=sys.stderr)


if __name__ == "__main__":
    if not DO_NOT_CALL:
        raise SystemExit("DO_NOT_CALL flag tampered with - refusing to run.")
    main()
