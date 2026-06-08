#!/usr/bin/env python3
"""Ray Dashboard auth-posture verifier — restraint-bounded.

Ray's Dashboard at default port 8265 exposes the Jobs API and the
cluster status API without authentication (CVE-2023-48022 / "ShadowRay").
Anyscale considers this expected behavior — Ray is designed to run in
"tightly controlled environments." When operators expose it on the
public internet, the unauth surface is what attackers find.

Verification chain:

  GET /api/cluster_status   → JSON with "cluster_status" / nodes summary
  GET /api/jobs/            → JSON list of past + active job IDs

200 + JSON-shape on either endpoint = unauthenticated Ray Dashboard.

ShadowRay 2.0 IoCs (Oligo Security, Nov 2025): botnet families RondoDox,
MooBot, KmsdBot — they submit jobs via the Jobs API. We do not read job
payloads; we only count visible job entries (the count alone is a signal,
deep job lists with no recent operator history look like attacker fleet).

NuClide restraint: cluster metadata only. NO job submission, NO job
payload reads (we list IDs and a count), NO worker-node interaction.
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
HEADERS = {"User-Agent": "NuClide-Research/ray-dashboard-2026-06-08"}
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE


def get(url, timeout=TIMEOUT):
    return urllib.request.urlopen(
        urllib.request.Request(url, headers=HEADERS),
        timeout=timeout, context=CTX
    )


def probe(ip_port: str) -> dict:
    ip, port = ip_port.split(":")
    port = int(port)
    out = {"ip": ip, "port": port, "verdict": "unknown"}
    schemes = ("https",) if port in (443, 8443) else ("http", "https")
    for sc in schemes:
        base = f"{sc}://{ip}:{port}"
        try:
            r = get(f"{base}/api/cluster_status")
            body = r.read(200_000).decode("utf-8", "replace")
            try:
                doc = json.loads(body)
            except json.JSONDecodeError:
                continue
            # Ray /api/cluster_status returns {"cluster_status": {...}}
            # or {"data": {...}}; we accept either with cluster-shape keys
            looks_ray = False
            if isinstance(doc, dict):
                # Common shapes
                d = doc.get("cluster_status") or doc.get("data") or doc
                if isinstance(d, dict):
                    if any(k in d for k in ("node_id_to_ip", "node_id_to_ip_map",
                                             "ray_resources", "ray_resources_per_node",
                                             "loadMetricsReport", "node_states")):
                        looks_ray = True
                    if "result" in d and isinstance(d.get("result"), dict):
                        rd = d["result"]
                        if any(k in rd for k in ("clusterStatus", "node_id_to_ip_map")):
                            looks_ray = True
            if not looks_ray:
                out["verdict"] = "fp_cluster_shape"
                out["scheme"] = sc
                return out
            out["verdict"] = "unauth_ray_confirmed"
            out["scheme"] = sc
            # Capture summary metadata
            d = doc.get("cluster_status") or doc.get("data") or doc
            if isinstance(d, dict):
                # Try to count nodes
                nim = d.get("node_id_to_ip_map") or {}
                if isinstance(nim, dict):
                    out["node_count"] = len(nim)
                rrpn = d.get("ray_resources_per_node") or {}
                if isinstance(rrpn, dict):
                    # Sum GPUs across nodes
                    gpu_total = 0
                    cpu_total = 0
                    for node_id, res in rrpn.items():
                        if isinstance(res, dict):
                            gpu_total += res.get("GPU", 0) or 0
                            cpu_total += res.get("CPU", 0) or 0
                    out["gpu_total"] = gpu_total
                    out["cpu_total"] = cpu_total
            # Now /api/jobs/ for job-count signal
            try:
                r2 = get(f"{base}/api/jobs/")
                jbody = r2.read(500_000).decode("utf-8", "replace")
                try:
                    jdoc = json.loads(jbody)
                except json.JSONDecodeError:
                    return out
                if isinstance(jdoc, list):
                    out["jobs_total"] = len(jdoc)
                    # Job IDs alone are metadata
                    out["job_ids_sample"] = [
                        j.get("submission_id") or j.get("job_id") or ""
                        for j in jdoc[:10]
                        if isinstance(j, dict)
                    ][:10]
                    # Status mix
                    statuses = {}
                    for j in jdoc:
                        if isinstance(j, dict):
                            s = j.get("status") or j.get("driver_info", {}).get("status") or "?"
                            statuses[s] = statuses.get(s, 0) + 1
                    out["job_status_mix"] = statuses
            except urllib.error.HTTPError as e:
                out["jobs_status"] = f"http_{e.code}"
            except Exception:
                pass
            return out
        except urllib.error.HTTPError as e:
            if e.code in (401, 403):
                out["verdict"] = f"auth_gated_{e.code}"
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


def main(pair_file: str, out_file: str, workers: int = 300):
    pairs = [l.strip() for l in Path(pair_file).read_text().splitlines() if l.strip() and ":" in l]
    print(f"[*] probing {len(pairs)} Ray Dashboard candidates (workers={workers})...", file=sys.stderr)
    results = []
    with cf.ThreadPoolExecutor(max_workers=workers) as ex:
        for i, r in enumerate(ex.map(probe, pairs)):
            results.append(r)
            if (i + 1) % 250 == 0:
                print(f"[*] {i+1}/{len(pairs)}", file=sys.stderr)
    Path(out_file).write_text("\n".join(json.dumps(r) for r in results))
    tally = {}
    for r in results:
        tally[r["verdict"]] = tally.get(r["verdict"], 0) + 1
    print("\n[TALLY]", file=sys.stderr)
    for k, v in sorted(tally.items(), key=lambda x: -x[1]):
        print(f"  {v:5d}  {k}", file=sys.stderr)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 300)
