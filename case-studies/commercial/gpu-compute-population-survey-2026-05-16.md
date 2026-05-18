---
type: survey
---

# GPU-Compute Population Survey (2026-05-16)

_NuClide Research · 2026-05-16 (Survey 6 of the day's 10-category batch)_
_Closes: category 14 (gpu-compute). Run:ai / DCGM-exporter / NVIDIA Fleet / cluster managers_

---

## Summary

Survey of the GPU-compute orchestration tier: Run:ai (Nvidia's enterprise GPU scheduler), DCGM-exporter (Prometheus exporter for NVIDIA GPU metrics), NVIDIA Bright Cluster Manager, Slurm REST API. Smaller surface than image-gen / vector-DB but operator-rich. These are dashboards and exporters that disclose the operator's full GPU topology.

- 439 candidates harvested across Run:ai / NVIDIA-SMI / cluster-manager / DCGM dorks
- Probed via `fast_enum_gpu_compute.py` (threads=80, ~3 min)
- **9 DCGM-exporter unauth**: each exposes GPU model + operator hostname via Prometheus `/metrics`
- 2 Run:ai consoles confirmed by HTML shell (auth state on data endpoints partial-open)
- 0 Bright Cluster Manager unauth, 0 Slurmrestd
- 428 other (dead, unrelated, generic NVIDIA marketing/documentation pages)

**Headline finding:** DCGM-exporter is **Tier-A* (by-design auth-free, framework expects operator-set network ACL)** and the 9 confirmed hosts disclose high-value GPU fleet inventory.

---

## What DCGM-exporter leaks unauth

Every confirmed DCGM-exporter host returns Prometheus text on `GET /metrics` with:

- GPU model (`modelName="NVIDIA L40S"` etc.)
- Operator-set hostname (`Hostname="video-gpu007-mojo-mia.vs3.com"`)
- GPU utilization, memory utilization, temperature, power draw (per-GPU, time-series)
- DCGM_FI_DEV_COUNT, DCGM_FI_DEV_GPU_UTIL, DCGM_FI_DEV_MEM_COPY_UTIL gauges

Per-host findings:

| Host | GPU model | Operator hostname | Inferred operator |
|---|---|---|---|
| `122.11.227.212:9400` | **NVIDIA H200** | `f8bcefe6ae83` | High-end AI training rig — H200 is current data-center flagship (~$40K MSRP); operator hostname is a container ID, suggesting Kubernetes deployment |
| `195.242.10.201:9400` | **NVIDIA H100 80GB HBM3** | `computeinstance-e00kd0mz50zwgst389` | $30K+ H100 — operator using a managed compute service (the long uuid-suffixed hostname is template-generated) |
| `171.226.10.154:9400` | NVIDIA L40S | `8a7881b0fef9` | Same L40S class as the ComfyUI cluster from earlier today |
| `199.59.95.140:9400` | NVIDIA A16 | `video-gpu007-mojo-mia.vs3.com` | **vs3.com video-GPU rental cluster, Miami location** |
| `89.187.191.229:9400` | NVIDIA A16 | `video-gpu001-dp-prg.vs3.com` | **Same vs3.com operator, Prague location** — multi-continent GPU fleet |
| `88.198.23.47:9400` | NVIDIA RTX 4000 SFF Ada Generation | `gpu01.xaas.int` | "GPU-as-a-Service" internal hostname; commercial rental ops |
| `107.150.106.98:9400` | Tesla T4 | `10-11-86-59` | Inference-tier card on a 10.11.86.59 internal IP — operator's internal range disclosed via hostname |
| `93.182.29.250:9400` | Tesla T4 | `cd-server-gpu-1` | Generic GPU server |
| `59.47.238.37:9400` | Tesla P4 | `123pan-tc11` | **123 Pan** (Chinese cloud storage) — `tc11` suggests Tencent Cloud Tianjin-11 region |

**The vs3.com pattern is the standout operator-attribution find.** Two GPU hosts on widely separated IPs (199.59.95.140 in Miami, 89.187.191.229 in Prague), both running NVIDIA A16, both with the operator's hostname template `video-gpu<NNN>-<role>-<city>.vs3.com`. This is a video-AI / streaming-AI operator with multi-continent infrastructure, fully exposed at the metrics layer.

---

## Methodology placement

DCGM-exporter is a **Prometheus exporter. By-design auth-free.** Prometheus exporters are designed for scrape-only metrics endpoints assumed to be inside a private network. The framework expects operator-configured network ACLs (firewall rules, kubernetes NetworkPolicy, Tailscale ACL) to gate access. Operators exposing :9400 to the public internet have made a deployment-config mistake, not a framework-default mistake.

Adds DCGM-exporter to the Tier-A* family (auth optional in framework, off-by-design when reachable):

| Tier | Definition | Member platforms |
|---|---|---|
| A* | Auth-by-network-not-app, off when reachable | LiveKit `/api/connection-details`, Airflow `AUTH_ROLE_PUBLIC=Admin`, Elasticsearch (Docker default), **DCGM-exporter** |

The risk class is intel-disclosure (operator GPU topology) rather than compute-theft (DCGM-exporter doesn't accept job submissions). For chained risk, an attacker can:

1. Fingerprint operator's GPU fleet via DCGM-exporter metrics
2. Cross-reference with the operator's likely orchestration layer (Run:ai / SLURM / native K8s). If also exposed, lateral movement
3. Time-series mining of utilization can fingerprint *what's being trained* (utilization patterns differ for LLM training vs CV training vs inference)

---

## Cross-survey colocation

| Pair | Overlap |
|---|---|
| GPU-compute ∩ ComfyUI (548) | Same-day check — TBD diff |
| GPU-compute ∩ DCGM cluster intersection | N/A |

The 9 DCGM hosts are distinct from the 548 ComfyUI hosts. DCGM exposure is the metrics-layer (port 9400) while ComfyUI is the application-layer (port 8188 + randomized high ports). An operator running ComfyUI on the same host as DCGM-exporter would appear on both, but no overlap surfaced in this small set.

---

## Toolchain Provenance

```
0. shodan search × 7 dorks → 439 unique candidates
1. fast_enum_gpu_compute.py (threads=80) → 9 DCGM + 2 Run:ai + 0 cluster-mgr + 0 slurmrestd
2. operator-hostname extraction from DCGM metrics → vs3.com multi-region pattern + xaas.int + 123pan
3. (queued) visorlog ingest → 9 events
```

---

## Honest negative space

- **DCGM-exporter is severely under-surveyed at population scale.** Real DCGM-exporter deployments are likely 1000s. Operators running NVIDIA GPU monitoring at scale. The 9 we found are the slice indexed by Shodan; port-first masscan on :9400 across tier-2 cloud (3.55M IPs) would surface the full population.
- **Run:ai console population not measured.** Run:ai is closed-source enterprise software with a small market footprint; only 2 shell-only matches surfaced. The product is mostly deployed inside customer K8s clusters with operator-managed auth.
- **NVIDIA Fleet Command / Bright Cluster Manager populations were 0** in the Shodan-seeded survey. These are enterprise-tier deployments (closed source, hardware-bundled) and usually deployed behind operator-managed ingress. Port-first masscan on :22425 / :8081 might surface them.
- **No metrics-history scraping.** Each DCGM-exporter host's `/metrics` returns instantaneous data; a longitudinal scrape (every-minute pull) would surface utilization patterns and let an attacker fingerprint workloads. Not pursued. Would cross into multi-day data-collection.

---

## Disclosure posture

- Per-host outreach for the 9 confirmed DCGM hosts is appropriate (low N, the disclosure is "your :9400 port is publicly reachable; firewall it").
- The vs3.com operator's multi-region exposure warrants a coordinated note (their Miami + Prague hosts visible).
- 123 Pan / Chinese-cloud hosts go via the cloud-provider's abuse channel.

---

## See also

- [[insight-13-shipping-defaults-are-load-bearing]]. DCGM-exporter is auth-by-network-not-app; default ACL isn't part of the framework, it's the operator's job
- [`image-generation-population-survey-2026-05-16.md`](image-generation-population-survey-2026-05-16.md): same day's L40S finding (same GPU class on a different layer)
- [`elasticsearch-ai-stack-population-survey-2026-05-16.md`](elasticsearch-ai-stack-population-survey-2026-05-16.md): same day's largest unauth-population survey
