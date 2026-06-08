#!/usr/bin/env python3
"""Meilisearch auth-posture verifier.

Strict verification chain (per tome/platforms/meilisearch.json):
  1. GET /health  → {"status":"available"} (identity)
  2. GET /stats   → {"databaseSize":N, "indexes":{...}} (200 = unauth read,
                    401/403 = auth-gated)

Restraint:
  - We do NOT read /indexes/{uid}/documents (record bodies).
  - We capture index NAMES and document COUNTS from /stats only.
  - Index NAMES are the finding (per the restraint ethic).
"""
import concurrent.futures as cf
import json
import socket
import ssl
import sys
import urllib.request
import urllib.error
from pathlib import Path

HONEYPOT_SALT = "wW0sffoqsk.EM"
TIMEOUT = 6
HEADERS = {"User-Agent": "NuClide-Research/meilisearch-survey-2026-06-08"}
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE


def get(url):
    req = urllib.request.Request(url, headers=HEADERS)
    return urllib.request.urlopen(req, timeout=TIMEOUT, context=CTX)


def probe(ip_port: str) -> dict:
    ip, port = ip_port.split(":")
    port = int(port)
    out = {"ip": ip, "port": port, "verdict": "unknown"}
    scheme = "https" if port in (443, 7700, 8443) else "http"
    # Try http first for non-443; if it fails, try https
    schemes = ("http", "https") if port != 443 else ("https",)
    for sc in schemes:
        try:
            base = f"{sc}://{ip}:{port}"
            r = get(f"{base}/health")
            body = r.read(8192).decode("utf-8", "replace")
            out["health_status"] = r.status
            if HONEYPOT_SALT in body:
                out["verdict"] = "honeypot_as63949"
                return out
            try:
                h = json.loads(body)
            except json.JSONDecodeError:
                continue
            if not (isinstance(h, dict) and h.get("status") == "available"):
                continue
            out["verdict_health"] = "meilisearch_health_ok"
            out["scheme"] = sc
            # Now /stats
            try:
                r2 = get(f"{base}/stats")
                sbody = r2.read(32768).decode("utf-8", "replace")
                try:
                    s = json.loads(sbody)
                except json.JSONDecodeError:
                    out["verdict"] = "fp_stats_not_json"
                    return out
                if isinstance(s, dict) and "indexes" in s and ("databaseSize" in s or "isIndexing" in s):
                    out["verdict"] = "unauth_meilisearch_confirmed"
                    out["database_size_bytes"] = s.get("databaseSize")
                    out["used_database_size_bytes"] = s.get("usedDatabaseSize")
                    indexes = s.get("indexes") or {}
                    out["index_count"] = len(indexes)
                    # capture index names + doc counts only
                    out["indexes"] = {
                        k: {"docs": v.get("numberOfDocuments"), "isIndexing": v.get("isIndexing")}
                        for k, v in list(indexes.items())[:50]
                    }
                    return out
                else:
                    out["verdict"] = "fp_stats_shape"
                    return out
            except urllib.error.HTTPError as e:
                if e.code in (401, 403):
                    out["verdict"] = f"auth_gated_{e.code}"
                else:
                    out["verdict"] = f"stats_http_{e.code}"
                return out
        except urllib.error.HTTPError as e:
            if e.code in (401, 403):
                out["verdict"] = f"health_auth_gated_{e.code}"
                return out
            continue
        except (urllib.error.URLError, socket.timeout, ConnectionResetError,
                ConnectionRefusedError, ssl.SSLError, OSError):
            continue
        except Exception as e:
            out["verdict"] = f"err_{type(e).__name__}"
            return out
    out["verdict"] = "dead"
    return out


def main(pair_file: str, out_file: str, workers: int = 200):
    pairs = [l.strip() for l in Path(pair_file).read_text().splitlines() if l.strip() and ":" in l]
    print(f"[*] probing {len(pairs)} meilisearch candidates (workers={workers})...", file=sys.stderr)
    results = []
    with cf.ThreadPoolExecutor(max_workers=workers) as ex:
        for i, r in enumerate(ex.map(probe, pairs)):
            results.append(r)
            if (i + 1) % 200 == 0:
                print(f"[*] {i+1}/{len(pairs)} done", file=sys.stderr)
    Path(out_file).write_text("\n".join(json.dumps(r) for r in results))
    tally = {}
    for r in results:
        tally[r["verdict"]] = tally.get(r["verdict"], 0) + 1
    print("\n[TALLY]", file=sys.stderr)
    for k, v in sorted(tally.items(), key=lambda x: -x[1]):
        print(f"  {v:5d}  {k}", file=sys.stderr)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 200)
