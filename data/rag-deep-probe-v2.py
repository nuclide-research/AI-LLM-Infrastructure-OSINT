#!/usr/bin/env python3
"""
rag-deep-probe-v2.py — Refined deep-probe for RAG framework + datalabel.

v1 found 100% auth-on at content endpoints. v2 tries:
  - /openapi.json (FastAPI route map; typically open even when API is gated)
  - Per-platform alternate endpoints:
    * PrivateGPT: /v1/chat/completions (OpenAI-compat shape; no auth in default)
    * doccano: anonymous-access settings, project search, doc-types public reads
    * LightRAG: graph endpoints, lightweight pipeline-info routes
    * AnythingLLM: GET /api/v1/system or /api/setup-complete (setup status leak)
    * RAGFlow: /v1/llm/list, /v1/conversation/list, alternate datasets endpoints

The goal: distinguish genuinely auth-on (operator hygiene win) from
"auth-on at the obvious endpoint, but leaks through alternate routes."
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

TIMEOUT_S = 6.0
MAX_BYTES = 64 * 1024


def http_get(url: str, timeout: float = TIMEOUT_S) -> tuple[int, bytes]:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "nuclide-rag-deep-probe-v2/0.1 (research; security@nuclide-research.com)",
            "Accept": "application/json,text/html",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, resp.read(MAX_BYTES)
    except urllib.error.HTTPError as e:
        try:
            return e.code, e.read()[:MAX_BYTES]
        except Exception:
            return e.code, b""
    except Exception:
        return 0, b""


def harvest_openapi(ip: str, port: int) -> dict:
    """If /openapi.json is open, extract: route count, route paths sample,
    auth-required indicators, exposed schema names."""
    out = {}
    s, b = http_get(f"http://{ip}:{port}/openapi.json")
    if s != 200 or not b:
        return out
    try:
        data = json.loads(b)
    except Exception:
        return out
    if not isinstance(data, dict) or "paths" not in data:
        return out
    paths = data.get("paths", {})
    out["openapi_open"] = True
    out["route_count"] = len(paths)
    # Sample notable paths: anything with 'doc', 'project', 'workspace', 'collection', 'dataset', 'list'
    notable = []
    for path, methods in paths.items():
        if not isinstance(methods, dict):
            continue
        if any(k in path.lower() for k in ("doc", "project", "workspace", "collection", "dataset", "ingest", "memory", "label")):
            for method in methods:
                if method.lower() in ("get", "post", "put", "delete"):
                    notable.append(f"{method.upper()} {path}")
    out["notable_routes"] = notable[:15]
    # Look for security definitions (oauth, api key)
    secs = data.get("components", {}).get("securitySchemes", {}) if isinstance(data.get("components"), dict) else {}
    out["security_schemes"] = list(secs.keys()) if isinstance(secs, dict) else []
    title = data.get("info", {}).get("title", "") if isinstance(data.get("info"), dict) else ""
    if title:
        out["openapi_title"] = title[:80]
    return out


def try_route(ip: str, port: int, path: str) -> tuple[int, str]:
    s, b = http_get(f"http://{ip}:{port}{path}")
    if s == 0:
        return 0, ""
    text = b.decode("utf-8", errors="replace")[:200]
    return s, text


def deep_v2(record: dict) -> dict:
    ip = record["ip"]
    port = record["port"]
    plat = record.get("platform", "")
    out = {**record}
    # Step 1: openapi.json
    out.update(harvest_openapi(ip, port))

    # Step 2: per-platform alternate routes
    alt_routes = {
        "PrivateGPT": ["/api/v1/recipes", "/v1/embeddings", "/v1/chat/completions"],
        "LightRAG": ["/api/v1/operations", "/api/v1/labels", "/graphs/sample/data"],
        "AnythingLLM": ["/api/setup-complete", "/api/system/check-token", "/api/v1/system"],
        "RAGFlow": ["/v1/llm/list", "/v1/conversation/list", "/v1/document/list"],
        "doccano": ["/v1/auth/me", "/v1/users/me", "/v1/projects/anonymous"],
        "Haystack": ["/health", "/initialized"],
        "LlamaIndex": ["/api/list", "/api/health"],
    }
    routes = alt_routes.get(plat, [])
    alt_results = {}
    for path in routes:
        s, text = try_route(ip, port, path)
        alt_results[path] = {"status": s, "snippet": text}
    out["alt_routes"] = alt_results

    # Aggregate auth posture across all probed routes
    statuses = [r.get("status") for r in alt_results.values() if r.get("status")]
    if statuses:
        if any(200 <= s < 300 for s in statuses):
            out["any_route_open"] = True
        elif all(s in (401, 403) for s in statuses):
            out["all_auth_required"] = True

    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="infile", required=True)
    ap.add_argument("--out", dest="outfile", required=True)
    ap.add_argument("--threads", type=int, default=100)
    args = ap.parse_args()

    records = []
    with open(args.infile) as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    records.append(json.loads(line))
                except Exception:
                    pass

    print(f"# v2 deep-probing {len(records)} hosts at {args.threads} threads...", file=sys.stderr)
    out = open(args.outfile, "w")
    counts = {"openapi_open": 0, "any_route_open": 0, "all_auth_required": 0}

    with concurrent.futures.ThreadPoolExecutor(max_workers=args.threads) as ex:
        futures = [ex.submit(deep_v2, r) for r in records]
        for fut in concurrent.futures.as_completed(futures):
            try:
                rec = fut.result()
            except Exception:
                continue
            out.write(json.dumps(rec) + "\n")
            out.flush()
            if rec.get("openapi_open"):
                counts["openapi_open"] += 1
            if rec.get("any_route_open"):
                counts["any_route_open"] += 1
            if rec.get("all_auth_required"):
                counts["all_auth_required"] += 1

    out.close()
    print(f"# done. openapi_open={counts['openapi_open']}, any_route_open={counts['any_route_open']}, all_auth_required={counts['all_auth_required']}", file=sys.stderr)


if __name__ == "__main__":
    main()
