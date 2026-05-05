#!/usr/bin/env python3
"""
rag-framework-probe.py — Probe for exposed RAG framework servers.

Platforms detected (port → ordered list of platform handlers):
  - LlamaIndex     — port 8000; /api/health + llama_index in OpenAPI
  - Haystack       — port 8000; /initialized returns {"initialized":true}
  - LightRAG       — port 9621; /health + LightRAG-specific endpoints
  - Microsoft GraphRAG — varies; OpenAPI signature
  - AnythingLLM    — port 3001; /api/ping returns "pong"
  - RAGFlow        — port 9380; /v1/health + FastAPI surface
  - PrivateGPT     — port 8001/8000; /health + ingestion endpoints

Output JSONL per confirmed host:
  {ip, port, platform, version, doc_count, collection_count, auth_required, raw_signature}

Usage:
  python3 rag-framework-probe.py --in ips.txt --out confirmed.jsonl --threads 200
"""
import argparse
import concurrent.futures
import json
import re
import socket
import sys
import time
import urllib.error
import urllib.request
from typing import Optional

DEFAULT_PORTS = [3001, 8000, 8001, 9380, 9621]
TIMEOUT_S = 5.0
MAX_BYTES = 65536


def parse_target(s: str) -> tuple[str, int]:
    s = s.strip()
    if ":" in s:
        ip, port_s = s.rsplit(":", 1)
        return ip, int(port_s)
    return s, 0


def http_get(url: str, timeout: float = TIMEOUT_S) -> tuple[int, dict, bytes]:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "nuclide-rag-framework-probe/0.1 (research; security@nuclide-research.com)",
            "Accept": "application/json,text/html",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, dict(resp.headers), resp.read(MAX_BYTES)
    except urllib.error.HTTPError as e:
        try:
            body = e.read()[:MAX_BYTES]
        except Exception:
            body = b""
        return e.code, dict(e.headers or {}), body
    except (urllib.error.URLError, socket.timeout, ConnectionError, TimeoutError, OSError):
        return 0, {}, b""


def try_anythingllm(ip: str, port: int) -> Optional[dict]:
    # AnythingLLM: /api/ping returns plain text "pong" (or JSON)
    s, _, b = http_get(f"http://{ip}:{port}/api/ping")
    if s != 200 or not b:
        return None
    text = b.decode("utf-8", errors="ignore").strip().lower()
    if "pong" not in text:
        return None
    # Confirm via /api/system/system-vectors or /api/system/check-token
    s2, _, b2 = http_get(f"http://{ip}:{port}/api/system/check-token")
    auth_required = (s2 == 401 or s2 == 403)
    s3, _, b3 = http_get(f"http://{ip}:{port}/api/system/system-vectors")
    vec_info = None
    if s3 == 200:
        try:
            vec_info = json.loads(b3)
        except Exception:
            pass
    return {
        "platform": "AnythingLLM",
        "version": "",
        "auth_required": auth_required,
        "doc_count": (vec_info or {}).get("vectorCount") if isinstance(vec_info, dict) else None,
        "raw_signature": "/api/ping returns pong",
    }


def try_haystack(ip: str, port: int) -> Optional[dict]:
    # Haystack: /initialized returns {"initialized": true/false}
    s, _, b = http_get(f"http://{ip}:{port}/initialized")
    if s != 200 or not b:
        return None
    try:
        data = json.loads(b)
    except Exception:
        return None
    if not isinstance(data, dict) or "initialized" not in data:
        return None
    # Cross-check FastAPI shape with /openapi.json
    s2, _, b2 = http_get(f"http://{ip}:{port}/openapi.json")
    is_haystack = False
    if s2 == 200 and b2 and (b"haystack" in b2.lower() or b"document_store" in b2.lower()):
        is_haystack = True
    if not is_haystack:
        return None
    return {
        "platform": "Haystack (deepset)",
        "version": "",
        "auth_required": None,
        "raw_signature": "/initialized + haystack/document_store in openapi",
    }


def try_lightrag(ip: str, port: int) -> Optional[dict]:
    # LightRAG: /health returns {"status": ...} but distinctively /api shape
    s, _, b = http_get(f"http://{ip}:{port}/health")
    if s == 200 and b:
        try:
            data = json.loads(b)
        except Exception:
            return None
        if isinstance(data, dict):
            # LightRAG-specific check: /api/v1/graph/label/list returns JSON list
            s2, _, b2 = http_get(f"http://{ip}:{port}/api/v1/graph/label/list")
            is_lightrag = False
            if s2 == 200 and b2:
                try:
                    d2 = json.loads(b2)
                    if isinstance(d2, list):
                        is_lightrag = True
                except Exception:
                    pass
            # Alternate check: /docs FastAPI swagger references LightRAG
            if not is_lightrag:
                s3, _, b3 = http_get(f"http://{ip}:{port}/docs")
                if s3 == 200 and b3 and (b"LightRAG" in b3 or b"lightrag" in b3.lower()):
                    is_lightrag = True
            if is_lightrag:
                # Try to get document count
                s4, _, b4 = http_get(f"http://{ip}:{port}/documents/count")
                doc_count = None
                if s4 == 200:
                    try:
                        d4 = json.loads(b4)
                        if isinstance(d4, dict):
                            doc_count = d4.get("count")
                        elif isinstance(d4, int):
                            doc_count = d4
                    except Exception:
                        pass
                return {
                    "platform": "LightRAG",
                    "version": "",
                    "auth_required": None,
                    "doc_count": doc_count,
                    "raw_signature": "/health + LightRAG markers in /docs or /api/v1/graph",
                }
    return None


def try_ragflow(ip: str, port: int) -> Optional[dict]:
    # RAGFlow: /v1/health returns specific shape
    s, _, b = http_get(f"http://{ip}:{port}/v1/health")
    if s != 200 or not b:
        return None
    try:
        data = json.loads(b)
    except Exception:
        return None
    if not isinstance(data, dict):
        return None
    # RAGFlow returns nested {"data": {"status": ...}}
    s2, _, b2 = http_get(f"http://{ip}:{port}/")
    is_ragflow = b"ragflow" in b2.lower() if b2 else False
    if not is_ragflow:
        # Try /api/v1/datasets or distinctive RAGFlow path
        s3, _, b3 = http_get(f"http://{ip}:{port}/v1/dataset/list")
        if s3 in (200, 401, 403):
            is_ragflow = True
    if not is_ragflow:
        return None
    return {
        "platform": "RAGFlow",
        "version": "",
        "auth_required": None,
        "raw_signature": "/v1/health + ragflow markers",
    }


def try_privategpt(ip: str, port: int) -> Optional[dict]:
    # PrivateGPT: /health returns {"status": "ok"} but distinctively has /v1/ingest endpoint
    s, _, b = http_get(f"http://{ip}:{port}/health")
    if s != 200 or not b:
        return None
    try:
        data = json.loads(b)
    except Exception:
        return None
    if not isinstance(data, dict):
        return None
    # PrivateGPT-distinctive: /v1/ingest/list or /openapi.json containing privategpt
    s2, _, b2 = http_get(f"http://{ip}:{port}/openapi.json")
    is_pgpt = False
    if s2 == 200 and b2 and (b"privategpt" in b2.lower() or b"PrivateGPT" in b2 or b"ingest" in b2.lower()):
        # Also check it's not Haystack (which also has FastAPI openapi)
        if b"document_store" not in b2.lower():
            is_pgpt = True
    if not is_pgpt:
        return None
    return {
        "platform": "PrivateGPT",
        "version": "",
        "auth_required": None,
        "raw_signature": "/health + privategpt/ingest in openapi",
    }


def try_llamaindex(ip: str, port: int) -> Optional[dict]:
    # LlamaIndex servers vary widely; FastAPI surface with llama_index in openapi
    s, _, b = http_get(f"http://{ip}:{port}/openapi.json")
    if s != 200 or not b:
        return None
    if b"llama_index" not in b.lower() and b"llamaindex" not in b.lower():
        return None
    # Try /api/health or /health
    s2, _, b2 = http_get(f"http://{ip}:{port}/api/health")
    if s2 == 0:
        s2, _, b2 = http_get(f"http://{ip}:{port}/health")
    return {
        "platform": "LlamaIndex",
        "version": "",
        "auth_required": None,
        "raw_signature": "llama_index in /openapi.json",
    }


PLATFORM_HANDLERS = {
    3001: [try_anythingllm],
    8000: [try_haystack, try_privategpt, try_llamaindex],
    8001: [try_privategpt, try_haystack, try_llamaindex],
    9380: [try_ragflow],
    9621: [try_lightrag],
}


def probe_target(target: str, ports: list[int]) -> Optional[dict]:
    ip, hint_port = parse_target(target)
    sweep = [hint_port] if hint_port else ports
    for p in sweep:
        handlers = PLATFORM_HANDLERS.get(p) or [
            try_anythingllm, try_haystack, try_privategpt, try_llamaindex,
            try_ragflow, try_lightrag,
        ]
        for h in handlers:
            t0 = time.monotonic()
            try:
                res = h(ip, p)
            except Exception:
                res = None
            if res:
                res["ip"] = ip
                res["port"] = p
                res["url"] = f"http://{ip}:{p}"
                res["elapsed_ms"] = int((time.monotonic() - t0) * 1000)
                return res
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("target", nargs="?")
    ap.add_argument("--in", dest="infile")
    ap.add_argument("--out", dest="outfile")
    ap.add_argument("--threads", type=int, default=100)
    ap.add_argument("--ports", default=",".join(str(p) for p in DEFAULT_PORTS))
    args = ap.parse_args()

    ports = [int(p) for p in args.ports.split(",") if p.strip()]
    targets: list[str] = []
    if args.target:
        targets.append(args.target)
    if args.infile:
        with open(args.infile) as f:
            targets.extend(line.strip() for line in f if line.strip())
    if not targets and not args.target:
        targets.extend(line.strip() for line in sys.stdin if line.strip())

    if not targets:
        ap.print_help()
        sys.exit(1)

    out = open(args.outfile, "w") if args.outfile else sys.stdout
    confirmed = 0
    by_platform = {}

    with concurrent.futures.ThreadPoolExecutor(max_workers=args.threads) as ex:
        futures = {ex.submit(probe_target, t, ports): t for t in targets}
        for fut in concurrent.futures.as_completed(futures):
            try:
                res = fut.result()
            except Exception:
                continue
            if res:
                out.write(json.dumps(res) + "\n")
                out.flush()
                confirmed += 1
                p = res.get("platform", "?")
                by_platform[p] = by_platform.get(p, 0) + 1

    if args.outfile:
        out.close()
    print(f"# probed: {len(targets)} hosts, confirmed: {confirmed}", file=sys.stderr)
    for plat, n in sorted(by_platform.items(), key=lambda kv: -kv[1]):
        print(f"#   {plat}: {n}", file=sys.stderr)


if __name__ == "__main__":
    main()
