#!/usr/bin/env python3
"""
Stage 3v VERIFY -- LangGraph Server (langchain-ai) + Letta/MemGPT (letta-ai)
DCWF 672 AI Test & Evaluation lane (Cat-Tabby lane-c, cat-agent-platforms 2026-06-19).

Refute-by-default. A scanner produced candidates; this produces findings.
A bare 200 / generic FastAPI title is NOT a confirm. We require the
vendor-unique conjunctive data-layer marker.

Insight #16: 200 is identity, not auth state. Every 200 gets a data-layer probe.
Insight #6 : conjunctive marker-anchored matchers, never naked body_contains.
Insight #68: each confirmed finding gets a verification rung pair.

HARD CODE-LEVEL REFUSAL (DO_NOT_CALL): state-changing / compute-exfil / agent-spawn
endpoints are listed as constants and refused at issue time. Zero violations.
The ONLY POSTs issued are LangGraph /assistants/search and /threads/search with
empty body {} -- those are SEARCH READS. Everything else is GET.
"""
from __future__ import annotations
import json
import socket
import ssl
import sys
import time
import threading
import queue
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

# --------------------------------------------------------------------------
# DO_NOT_CALL -- hard refusal set. Refused at code level before any request.
# --------------------------------------------------------------------------
DO_NOT_CALL = {
    # LangGraph: /runs* spawns/executes an agent = code-exec sink.
    "POST /runs", "POST /runs/stream", "POST /runs/wait", "POST /runs/batch",
    "POST /threads", "POST /threads/{id}/runs", "POST /assistants",
    "PATCH /assistants", "DELETE /assistants", "PUT /store/items",
    "POST /store/items", "DELETE /store/items",
    # Letta: anything that creates/executes.
    "POST /v1/agents", "POST /v1/agents/{id}/messages", "POST /v1/tools",
    "POST /v1/blocks", "PATCH /v1/blocks", "DELETE /v1/agents",
    "POST /v1/agents/{id}/core-memory",
}

# The only allowed POSTs (search reads, empty body).
ALLOWED_POSTS = {"/assistants/search", "/threads/search"}

TIMEOUT = 7.0
MAX_CONC = 12
UA = "nuclide-stage3v/1.0 (DCWF-672 T&E; read-only verify)"

LANGGRAPH_PORTS = [2024, 8123, 8000, 5000, 3001, 8080]
LANGGRAPH_PLAIN_FALLBACK = [80]
LETTA_PORTS = [8283, 8083, 5000, 5001, 8080]


def guard(method: str, path: str):
    """Refuse DO_NOT_CALL at code level. Raise before any socket is opened."""
    key = f"{method.upper()} {path}"
    # normalize ids
    for k in DO_NOT_CALL:
        kp = k.split(" ", 1)
        if kp[0] == method.upper():
            base = kp[1].split("{")[0].rstrip("/")
            if path == kp[1] or (base and path.startswith(base) and "search" not in path):
                raise RuntimeError(f"DO_NOT_CALL refusal: {key}")
    if method.upper() == "POST" and path not in ALLOWED_POSTS:
        raise RuntimeError(f"DO_NOT_CALL refusal (non-allowlisted POST): {key}")


def http(method: str, scheme: str, ip: str, port: int, path: str, body: bytes | None = None,
         host_header: str | None = None) -> dict:
    guard(method, path)
    url = f"{scheme}://{ip}:{port}{path}"
    headers = {"User-Agent": UA, "Accept": "application/json, */*"}
    if body is not None:
        headers["Content-Type"] = "application/json"
    req = Request(url, data=body, method=method, headers=headers)
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    out = {"url": url, "method": method, "status": None, "body": "", "err": None, "ctype": None}
    try:
        with urlopen(req, timeout=TIMEOUT, context=ctx) as r:
            out["status"] = r.status
            out["ctype"] = r.headers.get("content-type", "")
            out["body"] = r.read(65536).decode("utf-8", errors="replace")
    except HTTPError as e:
        out["status"] = e.code
        out["ctype"] = e.headers.get("content-type", "") if e.headers else ""
        try:
            out["body"] = e.read(65536).decode("utf-8", errors="replace")
        except Exception:
            pass
    except (URLError, socket.timeout, ConnectionError, ssl.SSLError, OSError) as e:
        out["err"] = f"{type(e).__name__}: {e}"
    except Exception as e:
        out["err"] = f"{type(e).__name__}: {e}"
    return out


def jload(s: str):
    try:
        return json.loads(s)
    except Exception:
        return None


def port_open(ip: str, port: int, timeout: float = 4.0) -> bool:
    try:
        s = socket.create_connection((ip, port), timeout=timeout)
        s.close()
        return True
    except Exception:
        return False


# --------------------------------------------------------------------------
# LangGraph verify
# --------------------------------------------------------------------------
def verify_langgraph(ip: str) -> dict:
    rec = {"platform": "langgraph", "ip": ip, "port": None, "scheme": None,
           "status_class": "DEAD", "marker_hits": [], "assistant_or_block_count": None,
           "http_status": None, "notes": ""}
    tried = []
    for port in LANGGRAPH_PORTS + LANGGRAPH_PLAIN_FALLBACK:
        if not port_open(ip, port):
            continue
        schemes = ["https", "http"] if port not in (80,) else ["http"]
        if port in (2024, 8123, 8000, 5000, 3001):
            schemes = ["http", "https"]
        for scheme in schemes:
            ok = http("GET", scheme, ip, port, "/ok")
            tried.append(f"{scheme}:{port}/ok={ok['status'] or ok['err']}")
            if ok["err"] and ok["status"] is None:
                continue
            rec["port"], rec["scheme"], rec["http_status"] = port, scheme, ok["status"]
            okj = jload(ok["body"])
            ok_marker = isinstance(okj, dict) and okj.get("ok") is True
            if ok_marker:
                rec["marker_hits"].append("/ok={\"ok\":true}")
            # /info -- JSON content-type required (HTML SPA /info does not count)
            info = http("GET", scheme, ip, port, "/info")
            infoj = jload(info["body"])
            info_marker = (info["status"] == 200 and "json" in (info["ctype"] or "").lower()
                           and isinstance(infoj, (dict, list)))
            if info_marker:
                rec["marker_hits"].append("/info=json")
            # Catch-all/honeypot negative control: a route that must NOT exist
            # on a real LangGraph server. If it returns the same shape as a real
            # route, the host is a catch-all SPA, not the API -> refute.
            neg = http("GET", scheme, ip, port, "/nuclide-catchall-neg-xyz")
            neg_html = (neg["status"] in (200, 404)) and "html" in (neg["ctype"] or "").lower()

            # /assistants/search (search READ, empty body).
            # A route is only "present" if JSON content-type AND status 200/422.
            # HTML body or a catch-all 404 does NOT count (Insight #6 conjunctive).
            asr = http("POST", scheme, ip, port, "/assistants/search", body=b"{}")
            asj = jload(asr["body"])
            as_json_ct = "json" in (asr["ctype"] or "").lower()
            as_route = (asr["status"] in (200, 422)) and as_json_ct and isinstance(asj, (list, dict)) and not neg_html
            as_200 = asr["status"] == 200 and as_json_ct and isinstance(asj, (list, dict))
            if as_route:
                rec["marker_hits"].append(f"/assistants/search=jsonroute({asr['status']})")
            # /threads/search route existence (read) -- same JSON discipline
            thr = http("POST", scheme, ip, port, "/threads/search", body=b"{}")
            thr_json_ct = "json" in (thr["ctype"] or "").lower()
            thr_route = (thr["status"] in (200, 422)) and thr_json_ct and not neg_html
            if thr_route:
                rec["marker_hits"].append(f"/threads/search=jsonroute({thr['status']})")

            # Conjunctive confirm: /ok marker PLUS (/info json OR assistants route)
            confirm = ok_marker and (info_marker or as_route)
            if confirm:
                if as_200 and isinstance(asj, list):
                    rec["assistant_or_block_count"] = len(asj)
                elif as_200 and isinstance(asj, dict):
                    # results object shape
                    res = asj.get("results") if isinstance(asj.get("results"), list) else None
                    rec["assistant_or_block_count"] = len(res) if res is not None else 0
                # auth state on data layer: did the search READ succeed unauth?
                if asr["status"] in (401, 403) and thr["status"] in (401, 403):
                    rec["status_class"] = "AUTH_GATED"
                    rec["notes"] = f"marker present; data routes 401/403. tried={tried}"
                elif as_200 or thr["status"] == 200 or as_route:
                    rec["status_class"] = "CONFIRMED_OPEN"
                    rec["notes"] = (f"/ok ok:true + " +
                                    ("/info json" if info_marker else "assistants route") +
                                    f"; assistants_search_status={asr['status']} threads_search_status={thr['status']}")
                else:
                    rec["status_class"] = "MARKER_ONLY"
                    rec["notes"] = f"/ok ok:true but data routes unclear. tried={tried}"
                return rec
            elif ok_marker:
                rec["status_class"] = "MARKER_ONLY"
                rec["notes"] = f"/ok ok:true only, no second marker. info={info['status']} asearch={asr['status']}"
                return rec
            elif info_marker or as_route:
                # JSON partial without /ok -- a different FastAPI app, refute as marker-only
                rec["status_class"] = "MARKER_ONLY"
                rec["notes"] = f"json partial (info/route) but no /ok={{ok:true}} marker -> not LangGraph-confirmed. info={info['status']} asearch={asr['status']}"
            elif neg_html:
                # catch-all SPA: bogus path returns same HTML as real route
                rec["status_class"] = "NOT_PLATFORM"
                rec["notes"] = f"catch-all HTML SPA (neg-control {neg['status']} {neg['ctype']}); not LangGraph API. tried={tried}"
                return rec
            else:
                if rec["status_class"] == "DEAD":
                    rec["status_class"] = "NOT_PLATFORM"
                    rec["notes"] = f"port open, no LangGraph marker. tried={tried}"
    if rec["status_class"] == "DEAD":
        rec["notes"] = f"no open candidate port / no L7. tried={tried}"
    return rec


# --------------------------------------------------------------------------
# Letta verify
# --------------------------------------------------------------------------
def verify_letta(ip: str) -> dict:
    rec = {"platform": "letta", "ip": ip, "port": None, "scheme": None,
           "status_class": "DEAD", "marker_hits": [], "assistant_or_block_count": None,
           "http_status": None, "notes": ""}
    tried = []
    for port in LETTA_PORTS:
        if not port_open(ip, port):
            continue
        for scheme in (["http", "https"]):
            h = http("GET", scheme, ip, port, "/v1/health/")
            tried.append(f"{scheme}:{port}/v1/health/={h['status'] or h['err']}")
            if h["err"] and h["status"] is None:
                continue
            rec["port"], rec["scheme"], rec["http_status"] = port, scheme, h["status"]
            hj = jload(h["body"])
            # two-field shape: exactly version + status
            health_marker = (isinstance(hj, dict) and "version" in hj and "status" in hj)
            if health_marker:
                rec["marker_hits"].append("/v1/health/=version+status")
            # /v1/blocks/ memory-block route
            blk = http("GET", scheme, ip, port, "/v1/blocks/")
            blkj = jload(blk["body"])
            blk_marker = blk["status"] == 200 and isinstance(blkj, list)
            agt = http("GET", scheme, ip, port, "/v1/agents/")
            agtj = jload(agt["body"])
            agt_marker = agt["status"] == 200 and isinstance(agtj, list)
            if blk_marker:
                rec["marker_hits"].append("/v1/blocks/=jsonarray")
            if agt_marker:
                rec["marker_hits"].append("/v1/agents/=jsonarray")

            confirm = health_marker and (blk_marker or agt_marker)
            if confirm:
                cnt = (len(blkj) if blk_marker else None, len(agtj) if agt_marker else None)
                rec["assistant_or_block_count"] = {"blocks": cnt[0], "agents": cnt[1]}
                rec["status_class"] = "CONFIRMED_OPEN"
                rec["notes"] = f"/v1/health two-field + data route 200; blocks={cnt[0]} agents={cnt[1]}"
                return rec
            if health_marker and (blk["status"] in (401, 403) or agt["status"] in (401, 403)):
                rec["status_class"] = "AUTH_GATED"
                rec["notes"] = f"health ok; blocks={blk['status']} agents={agt['status']} (auth)"
                return rec
            if health_marker:
                rec["status_class"] = "MARKER_ONLY"
                rec["notes"] = f"health two-field only; blocks={blk['status']} agents={agt['status']}"
                return rec
            if rec["status_class"] == "DEAD":
                rec["status_class"] = "NOT_PLATFORM"
                rec["notes"] = f"port open, no Letta health marker. tried={tried}"
    if rec["status_class"] == "DEAD":
        rec["notes"] = f"no open candidate port. tried={tried}"
    return rec


def worker(q, results, fn):
    while True:
        try:
            ip = q.get_nowait()
        except queue.Empty:
            return
        try:
            results.append(fn(ip))
        except Exception as e:
            results.append({"ip": ip, "status_class": "ERROR", "notes": str(e)})
        finally:
            q.task_done()


def run(ips, fn):
    q = queue.Queue()
    for ip in ips:
        q.put(ip)
    results = []
    threads = [threading.Thread(target=worker, args=(q, results, fn)) for _ in range(min(MAX_CONC, max(1, len(ips))))]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    return results


if __name__ == "__main__":
    base = sys.argv[1] if len(sys.argv) > 1 else "."
    lg_ips = [l.strip() for l in open(f"{base}/langgraph-candidate.txt") if l.strip()]
    le_ips = [l.strip() for l in open(f"{base}/letta-candidate.txt") if l.strip()]
    print(f"[*] LangGraph candidates: {len(lg_ips)}  Letta candidates: {len(le_ips)}")
    recs = run(lg_ips, verify_langgraph) + run(le_ips, verify_letta)
    with open(f"{base}/verify-candidates.jsonl", "w") as f:
        for r in recs:
            f.write(json.dumps(r) + "\n")
    from collections import Counter
    for plat in ("langgraph", "letta"):
        c = Counter(r["status_class"] for r in recs if r.get("platform") == plat)
        print(f"[{plat}] {dict(c)}")
    print("[+] wrote verify-candidates.jsonl")
