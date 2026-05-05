#!/usr/bin/env python3
"""
rag-deep-probe.py — Per-platform deep-content probe for confirmed RAG framework
and data-labeling instances.

Reads a confirmed.jsonl (output of rag-framework-probe.py or datalabel-probe.py)
and, per host, fetches the platform's content-disclosure endpoint(s):

  - PrivateGPT     → GET /v1/ingest/list  (list of ingested documents)
  - LightRAG       → GET /documents (recently-ingested), /api/v1/graph/label/list
  - AnythingLLM    → GET /api/system/system-vectors, /api/workspaces
  - RAGFlow        → GET /v1/dataset/list
  - LlamaIndex     → GET /openapi.json, look for content-disclosure routes
  - Haystack       → GET /openapi.json
  - doccano        → GET /v1/projects (project name + member count)
  - LabelStudio    → GET /api/projects
  - Argilla        → GET /api/v1/workspaces, /api/v1/datasets
  - CVAT           → GET /api/projects

Output JSONL: per-host enrichment with content-disclosure fields. Redacts
credential patterns from any captured strings.

Usage:
  python3 rag-deep-probe.py --in confirmed.jsonl --out deep-confirmed.jsonl --threads 100
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

KEY_PATTERNS = [
    (re.compile(rb'sk-[A-Za-z0-9_-]{16,}'), b'sk-REDACTED'),
    (re.compile(rb'sk-ant-[A-Za-z0-9_-]{16,}'), b'sk-ant-REDACTED'),
    (re.compile(rb'Bearer [A-Za-z0-9._~+/-]{16,}'), b'Bearer REDACTED'),
    (re.compile(rb'AIza[A-Za-z0-9_-]{20,}'), b'AIza-REDACTED'),
    (re.compile(rb'(?i)api[_-]?key[":= ]+[A-Za-z0-9._-]{12,}'), b'api_key=REDACTED'),
]


def redact(b: bytes, length: int = 200) -> str:
    for pattern, replacement in KEY_PATTERNS:
        b = pattern.sub(replacement, b)
    return b.decode("utf-8", errors="replace")[:length]


def http_get(url: str, timeout: float = TIMEOUT_S) -> tuple[int, bytes]:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "nuclide-rag-deep-probe/0.1 (research; security@nuclide-research.com)",
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


def deep_privategpt(ip: str, port: int) -> dict:
    base = f"http://{ip}:{port}"
    out = {}
    s, b = http_get(f"{base}/v1/ingest/list")
    if s == 200 and b:
        try:
            data = json.loads(b)
            if isinstance(data, dict) and "data" in data:
                items = data["data"]
                if isinstance(items, list):
                    out["ingested_doc_count"] = len(items)
                    # Sample document names if present
                    sample = []
                    for item in items[:10]:
                        if isinstance(item, dict):
                            doc = item.get("doc_metadata", {}) or item.get("metadata", {})
                            if isinstance(doc, dict):
                                fname = doc.get("file_name") or doc.get("filename") or doc.get("source")
                                if fname:
                                    sample.append(redact(str(fname).encode("utf-8"), 80))
                    out["doc_samples"] = sample
        except Exception:
            pass
    elif s in (401, 403):
        out["auth_required"] = True
    return out


def deep_lightrag(ip: str, port: int) -> dict:
    base = f"http://{ip}:{port}"
    out = {}
    # /documents endpoint returns list with metadata
    s, b = http_get(f"{base}/documents")
    if s == 200 and b:
        try:
            data = json.loads(b)
            if isinstance(data, list):
                out["doc_count"] = len(data)
                sample = [redact(str(d.get("file_path") or d.get("source") or "").encode("utf-8"), 80) for d in data[:5] if isinstance(d, dict)]
                out["doc_samples"] = [s for s in sample if s]
            elif isinstance(data, dict) and "statuses" in data:
                # Newer LightRAG returns {"statuses": [...]}
                statuses = data.get("statuses", [])
                if isinstance(statuses, list):
                    out["doc_count"] = len(statuses)
        except Exception:
            pass
    elif s in (401, 403):
        out["auth_required"] = True

    # Graph labels (entity types)
    s2, b2 = http_get(f"{base}/api/v1/graph/label/list")
    if s2 == 200 and b2:
        try:
            labels = json.loads(b2)
            if isinstance(labels, list):
                out["graph_labels_count"] = len(labels)
                out["graph_labels_sample"] = labels[:8]
        except Exception:
            pass
    return out


def deep_anythingllm(ip: str, port: int) -> dict:
    base = f"http://{ip}:{port}"
    out = {}
    s, b = http_get(f"{base}/api/system/system-vectors")
    if s == 200 and b:
        try:
            data = json.loads(b)
            if isinstance(data, dict):
                out["vector_count"] = data.get("vectorCount")
        except Exception:
            pass
    s2, b2 = http_get(f"{base}/api/workspaces")
    if s2 == 200 and b2:
        try:
            data = json.loads(b2)
            if isinstance(data, dict) and "workspaces" in data:
                ws = data["workspaces"]
                if isinstance(ws, list):
                    out["workspace_count"] = len(ws)
                    out["workspace_names"] = [redact(str(w.get("name", "")).encode("utf-8"), 60) for w in ws[:8] if isinstance(w, dict)]
        except Exception:
            pass
    elif s2 in (401, 403):
        out["auth_required"] = True
    return out


def deep_ragflow(ip: str, port: int) -> dict:
    base = f"http://{ip}:{port}"
    out = {}
    s, b = http_get(f"{base}/v1/dataset/list")
    if s == 200 and b:
        try:
            data = json.loads(b)
            if isinstance(data, dict):
                if data.get("code") == 0 and "data" in data:
                    items = data.get("data", [])
                    if isinstance(items, list):
                        out["dataset_count"] = len(items)
                        out["dataset_names"] = [redact(str(d.get("name", "")).encode("utf-8"), 60) for d in items[:8] if isinstance(d, dict)]
                elif data.get("code") in (401, 102):
                    out["auth_required"] = True
        except Exception:
            pass
    return out


def deep_doccano(ip: str, port: int) -> dict:
    base = f"http://{ip}:{port}"
    out = {}
    s, b = http_get(f"{base}/v1/projects")
    if s == 200 and b:
        try:
            data = json.loads(b)
            items = data.get("results") if isinstance(data, dict) else data
            if isinstance(items, list):
                out["project_count"] = len(items) if not isinstance(data, dict) else data.get("count", len(items))
                out["project_samples"] = [{
                    "name": redact(str(p.get("name", "")).encode("utf-8"), 60),
                    "type": p.get("project_type", ""),
                    "description": redact(str(p.get("description", "")).encode("utf-8"), 100),
                } for p in items[:8] if isinstance(p, dict)]
        except Exception:
            pass
    elif s in (401, 403):
        out["auth_required"] = True
    return out


def deep_labelstudio(ip: str, port: int) -> dict:
    base = f"http://{ip}:{port}"
    out = {}
    s, b = http_get(f"{base}/api/projects")
    if s == 200 and b:
        try:
            data = json.loads(b)
            items = data.get("results") if isinstance(data, dict) else data
            if isinstance(items, list):
                out["project_count"] = data.get("count", len(items)) if isinstance(data, dict) else len(items)
                out["project_samples"] = [redact(str(p.get("title", "")).encode("utf-8"), 60) for p in items[:8] if isinstance(p, dict)]
        except Exception:
            pass
    elif s in (401, 403):
        out["auth_required"] = True
    return out


def deep_argilla(ip: str, port: int) -> dict:
    base = f"http://{ip}:{port}"
    out = {}
    s, b = http_get(f"{base}/api/v1/workspaces")
    if s == 200 and b:
        try:
            data = json.loads(b)
            items = data.get("items") if isinstance(data, dict) else data
            if isinstance(items, list):
                out["workspace_count"] = len(items)
                out["workspace_names"] = [redact(str(w.get("name", "")).encode("utf-8"), 60) for w in items[:8] if isinstance(w, dict)]
        except Exception:
            pass
    elif s in (401, 403):
        out["auth_required"] = True
    return out


def deep_cvat(ip: str, port: int) -> dict:
    base = f"http://{ip}:{port}"
    out = {}
    s, b = http_get(f"{base}/api/projects")
    if s == 200 and b:
        try:
            data = json.loads(b)
            if isinstance(data, dict):
                out["project_count"] = data.get("count")
                results = data.get("results", [])
                if isinstance(results, list):
                    out["project_samples"] = [redact(str(p.get("name", "")).encode("utf-8"), 60) for p in results[:8] if isinstance(p, dict)]
        except Exception:
            pass
    elif s in (401, 403):
        out["auth_required"] = True
    return out


PLATFORM_DEEP = {
    "PrivateGPT": deep_privategpt,
    "LightRAG": deep_lightrag,
    "AnythingLLM": deep_anythingllm,
    "RAGFlow": deep_ragflow,
    "doccano": deep_doccano,
    "LabelStudio": deep_labelstudio,
    "Argilla": deep_argilla,
    "CVAT": deep_cvat,
}


def deep_one(record: dict) -> dict:
    plat = record.get("platform", "")
    handler = PLATFORM_DEEP.get(plat)
    if not handler:
        return {**record, "deep_skipped": True}
    t0 = time.monotonic()
    try:
        deep = handler(record["ip"], record["port"])
    except Exception as e:
        deep = {"deep_error": f"{type(e).__name__}: {e}"}
    deep["deep_elapsed_ms"] = int((time.monotonic() - t0) * 1000)
    return {**record, **deep}


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

    print(f"# deep-probing {len(records)} hosts at {args.threads} threads...", file=sys.stderr)

    out = open(args.outfile, "w")
    counts = {"deepened": 0, "skipped": 0, "errors": 0}

    with concurrent.futures.ThreadPoolExecutor(max_workers=args.threads) as ex:
        futures = [ex.submit(deep_one, r) for r in records]
        for fut in concurrent.futures.as_completed(futures):
            try:
                rec = fut.result()
            except Exception:
                counts["errors"] += 1
                continue
            out.write(json.dumps(rec) + "\n")
            out.flush()
            if rec.get("deep_skipped"):
                counts["skipped"] += 1
            else:
                counts["deepened"] += 1

    out.close()
    print(f"# done. deepened={counts['deepened']}, skipped={counts['skipped']}, errors={counts['errors']}", file=sys.stderr)


if __name__ == "__main__":
    main()
