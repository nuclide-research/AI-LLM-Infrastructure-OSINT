#!/usr/bin/env python3
"""Kubeflow auth-posture verifier — restraint-bounded.

Per public record (CVE-2026-47237 + multiple disclosed Kubeflow exposures):
  - Central Dashboard + Pipelines commonly exposed via misconfigured ingress
  - Dex OIDC authservice optional and often left out of the stack
  - Istio gateway misconfig is the recurring root cause

Verification chain (GET-only, names + counts):
  1. GET / → HTML containing "Kubeflow" (identity)
  2. GET /pipeline/apis/v1beta1/healthz → {"multi_user":..., "host":...} (Pipelines alive)
  3. GET /pipeline/apis/v1beta1/experiments → {"experiments":[...]} (unauth read; auth-needed shape returns 401/403 OR Dex login redirect)
  4. GET /pipeline/apis/v1beta1/runs → {"runs":[...]} (pipeline run enumeration)

Restraint:
  - Never POST any pipeline create / run trigger
  - Never view individual run payloads via /runs/{id}
  - Never read notebook contents via /jupyter
  - Capture experiment NAMES + run NAMES + counts only
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
HEADERS = {"User-Agent": "NuClide-Research/kubeflow-survey-2026-06-08"}
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
        # Step 1: confirm Kubeflow identity at /
        try:
            r = get(f"{base}/")
            body = r.read(8192).decode("utf-8", "replace")
            out["scheme"] = sc
            out["root_status"] = r.status
            if "Kubeflow" not in body and "kubeflow" not in body.lower():
                out["verdict"] = "fp_root_not_kubeflow"
                return out
            out["root_ok"] = True
        except urllib.error.HTTPError as e:
            # 302 to Dex login is the auth-correct path
            if e.code in (302, 303):
                # follow only enough to see if it's Dex
                loc = e.headers.get("Location", "")
                if "dex" in loc.lower() or "/auth" in loc.lower():
                    out["verdict"] = "auth_via_dex_redirect"
                    return out
            if e.code in (401, 403):
                out["verdict"] = f"root_auth_gated_{e.code}"
                return out
            continue
        except (urllib.error.URLError, socket.timeout, ConnectionResetError,
                ConnectionRefusedError, ssl.SSLError, OSError):
            continue
        except Exception as e:
            out["verdict"] = f"err_{type(e).__name__}"
            return out

        # Step 2: Pipelines API healthz
        try:
            r2 = get(f"{base}/pipeline/apis/v1beta1/healthz")
            hbody = r2.read(8192).decode("utf-8", "replace")
            try:
                hdoc = json.loads(hbody)
                out["pipelines_healthz"] = hdoc
            except json.JSONDecodeError:
                out["pipelines_healthz_raw"] = hbody[:200]
        except urllib.error.HTTPError as e:
            if e.code in (401, 403):
                out["verdict"] = "pipelines_healthz_auth_gated"
                return out
            out["pipelines_healthz_status"] = f"http_{e.code}"
        except Exception:
            pass

        # Step 3: experiments list (the load-bearing unauth read)
        try:
            r3 = get(f"{base}/pipeline/apis/v1beta1/experiments?page_size=20")
            ebody = r3.read(100_000).decode("utf-8", "replace")
            try:
                edoc = json.loads(ebody)
            except json.JSONDecodeError:
                out["verdict"] = "fp_experiments_not_json"
                return out
            if isinstance(edoc, dict) and "experiments" in edoc:
                exps = edoc.get("experiments") or []
                out["verdict"] = "unauth_kubeflow_confirmed"
                out["experiment_count"] = edoc.get("total_size", len(exps))
                out["experiment_names_sample"] = [e.get("display_name") or e.get("name") for e in exps[:20] if isinstance(e, dict)]
            elif isinstance(edoc, dict) and "error" in edoc:
                out["verdict"] = "experiments_error"
                out["error_msg"] = str(edoc.get("error", ""))[:200]
                return out
            else:
                out["verdict"] = "fp_experiments_shape"
                return out
        except urllib.error.HTTPError as e:
            if e.code in (401, 403):
                out["verdict"] = "experiments_auth_gated"
                return out
            out["experiments_status"] = f"http_{e.code}"
            return out
        except Exception as e:
            out["verdict"] = f"experiments_err_{type(e).__name__}"
            return out

        # Step 4: runs list (only if experiments returned unauth)
        if out["verdict"] == "unauth_kubeflow_confirmed":
            try:
                r4 = get(f"{base}/pipeline/apis/v1beta1/runs?page_size=20")
                rbody = r4.read(100_000).decode("utf-8", "replace")
                try:
                    rdoc = json.loads(rbody)
                    if isinstance(rdoc, dict) and "runs" in rdoc:
                        runs = rdoc.get("runs") or []
                        out["run_count"] = rdoc.get("total_size", len(runs))
                        out["run_names_sample"] = [r.get("display_name") or r.get("name") for r in runs[:20] if isinstance(r, dict)]
                        statuses = {}
                        for r in runs:
                            if isinstance(r, dict):
                                s = r.get("status") or "?"
                                statuses[s] = statuses.get(s, 0) + 1
                        out["run_status_mix"] = statuses
                except json.JSONDecodeError:
                    pass
            except Exception:
                pass
        return out
    out["verdict"] = "dead"
    return out


def main(pair_file: str, out_file: str, workers: int = 200):
    pairs = [l.strip() for l in Path(pair_file).read_text().splitlines() if l.strip() and ":" in l]
    print(f"[*] probing {len(pairs)} Kubeflow candidates (workers={workers})...", file=sys.stderr)
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
