#!/usr/bin/env python3
"""Label Studio auth-posture verifier — restraint-bounded.

Default deploy: ships with admin signup at /user/signup. Operators commonly
run --no-auth or leave admin creds default. Self-hosted Heartex/Humansignal
LS-OS is the surveyed population.

Verification chain (GET-only, names + counts):
  1. GET /version → JSON with "release":..." or "label-studio-os-package":...
                    confirms identity, captures version
  2. GET /api/projects/ → 200 + JSON with "results":[...] = unauth confirmed
                          401/403 = auth-gated (normal)
  3. (Only if unauth confirmed) GET /api/users/ → list of annotator accounts (PII)
  4. GET /api/projects/{id}/  for each project to get title + members count

Restraint:
  - Never POST tasks, annotations, or modify project state
  - Capture project TITLES, project COUNTS, user counts, member counts
  - NEVER read tasks/annotations payload (that's the labeled training data)
  - NEVER download exports via /api/projects/{id}/export
"""
import concurrent.futures as cf
import json
import socket
import ssl
import sys
import urllib.request
import urllib.error
from pathlib import Path

TIMEOUT = 6
HEADERS = {"User-Agent": "NuClide-Research/label-studio-2026-06-08"}
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE


def get(url):
    return urllib.request.urlopen(
        urllib.request.Request(url, headers=HEADERS),
        timeout=TIMEOUT, context=CTX
    )


def probe(ip_port: str) -> dict:
    ip, port = ip_port.split(":")
    port = int(port)
    out = {"ip": ip, "port": port, "verdict": "unknown"}
    schemes = ("https",) if port in (443, 8443) else ("http", "https")
    for sc in schemes:
        base = f"{sc}://{ip}:{port}"
        # Step 1: /version for identity
        try:
            r = get(f"{base}/version")
            body = r.read(8192).decode("utf-8", "replace")
            # Label Studio wraps /version JSON in <pre>...</pre> HTML
            stripped = body.strip()
            if stripped.startswith("<pre>"):
                stripped = stripped[5:]
            if stripped.endswith("</pre>"):
                stripped = stripped[:-6]
            try:
                doc = json.loads(stripped)
            except json.JSONDecodeError:
                continue
            if not isinstance(doc, dict):
                continue
            # Must look like LS
            if not any(k in doc for k in ("release", "label-studio-os-package", "label_studio", "label-studio")):
                out["verdict"] = "fp_version_shape"
                return out
            out["scheme"] = sc
            out["version"] = (doc.get("release")
                              or (doc.get("label-studio-os-package") or {}).get("version", "")
                              or doc.get("label_studio", {}).get("version", ""))
            # Step 2: /api/projects/
            try:
                r2 = get(f"{base}/api/projects/?page_size=50")
                pbody = r2.read(500_000).decode("utf-8", "replace")
                try:
                    pdoc = json.loads(pbody)
                except json.JSONDecodeError:
                    out["verdict"] = "fp_projects_not_json"
                    return out
                if isinstance(pdoc, dict) and "results" in pdoc:
                    out["verdict"] = "unauth_label_studio_confirmed"
                    results = pdoc.get("results") or []
                    out["project_count"] = pdoc.get("count", len(results))
                    # Names + member counts only, no task data
                    out["project_titles_sample"] = [p.get("title", "") for p in results[:20] if isinstance(p, dict)]
                    out["project_members_sample"] = [(p.get("title", ""), p.get("members_count", p.get("num_tasks", 0))) for p in results[:10] if isinstance(p, dict)]
                    # Step 3: /api/users/ for annotator-count signal (PII = no payloads)
                    try:
                        r3 = get(f"{base}/api/users/")
                        ubody = r3.read(50_000).decode("utf-8", "replace")
                        try:
                            udoc = json.loads(ubody)
                            if isinstance(udoc, list):
                                out["user_count"] = len(udoc)
                            elif isinstance(udoc, dict):
                                out["user_count"] = udoc.get("count", len(udoc.get("results", [])))
                        except json.JSONDecodeError:
                            pass
                    except Exception:
                        pass
                    return out
                else:
                    out["verdict"] = "fp_projects_shape"
                    return out
            except urllib.error.HTTPError as e:
                if e.code in (401, 403):
                    out["verdict"] = f"projects_auth_gated_{e.code}"
                    return out
                out["projects_status"] = f"http_{e.code}"
                return out
            except Exception as e:
                out["verdict"] = f"projects_err_{type(e).__name__}"
                return out
        except urllib.error.HTTPError as e:
            if e.code in (401, 403):
                out["verdict"] = f"version_auth_{e.code}"
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
    print(f"[*] probing {len(pairs)} Label Studio candidates (workers={workers})...", file=sys.stderr)
    results = []
    with cf.ThreadPoolExecutor(max_workers=workers) as ex:
        for i, r in enumerate(ex.map(probe, pairs)):
            results.append(r)
            if (i + 1) % 100 == 0:
                print(f"[*] {i+1}/{len(pairs)}", file=sys.stderr)
    Path(out_file).write_text("\n".join(json.dumps(r) for r in results))
    tally = {}
    for r in results:
        tally[r["verdict"]] = tally.get(r["verdict"], 0) + 1
    print("\n[TALLY]", file=sys.stderr)
    for k, v in sorted(tally.items(), key=lambda x: -x[1]):
        print(f"  {v:5d}  {k}", file=sys.stderr)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 200)
