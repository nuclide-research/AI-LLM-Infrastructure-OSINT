# Cat-53 NVIDIA FLARE (NVFlare) Pre-Assessment OSINT

**Date:** 2026-06-09
**Target class:** Federated learning coordinator (Overseer + FL Server + FL Clients + Admin + Dashboard)
**Repo:** github.com/NVIDIA/NVFlare. Stable line: 2.7.x (patched 2.7.2, April 2026).
**Scope:** doc/source research only. No live probing performed.

## Lane 1 — Auth modes & deploy config

NVFlare ships two provisioning modes. **Secure (production):** `nvflare provision` builds startup kits containing per-participant x509 + a root CA; communication between Overseer, FL Server, FL Clients, and Admin uses **mTLS**. Identity is the cert CN. Admin clients require their own provisioned cert.

**POC mode** (`nvflare poc prepare`) emits kits to `/tmp/nvflare/poc`, "limited security to allow simplified connection" — confirmed via the 2.7 POC docs. POC is "intended for POC and does not perform authorization checks on its APIs" (per Overseer source comment). BYOC (bring-your-own-code, custom job code execution) is **enabled by default in POC, disabled by default in secure mode**.

**Overseer:** the 2.1+ docs state "the Overseer must only accept authenticated communications… implemented with mTLS." However the Flask source paths (`nvflare.ha.overseer.overseer`) show DEBUG-mode short-circuits on `/api/v1/promote` (X-USER header trust), and `/api/v1/heartbeat` has no explicit auth check at the route level — auth is enforced at the TLS layer, so a misconfigured/POC-deployed Overseer exposes both routes unauthenticated.

**Dashboard:** Flask + SQLAlchemy. Serves HTTPS on :443 only if `cert/web.crt` + key exist, else falls back to plain HTTP. Hosts the provisioning flow (register → approve → download startup kit).

## Lane 2 — Shodan fingerprint & population signal

**Default ports:**
- **8002/tcp** — FL Server, gRPC to FL Clients (`fed_learn_port`)
- **8003/tcp** — FL Server, admin/FLARE-Console (TCP, not gRPC — per docs)
- **443/tcp** — Dashboard (HTTPS if certs present, else HTTP)
- **8443/tcp** — Dashboard local dev (`/nvflare-dashboard/api/v1`)
- 2.7 added **single-port deployment** consolidating FL+admin onto one port; will fragment the port signal going forward.

**Strings (HTTP/TLS body):**
- `nvflare-dashboard/api/v1` path on Dashboard
- Provision-tool TLS cert CNs typically `overseer`, `server1`/`server2`, `<site>.<project>`, signed by a `nvflare-rootca`-style self-signed root — unknown exact subject string, source X not nailed down; flag for cert-CN fingerprinting at scan time.
- gRPC reflection default state on FL Server: **unknown** — docs reference `max_message_size` in `comm_config.json` but do not state reflection default. Confirm by source diff or active probe in lab.

**Dorks (ranked, FP risk):**
1. `http.html:"nvflare-dashboard/api/v1"` — low FP, Dashboard surface
2. `http.title:"NVFLARE Dashboard"` — low FP, vendor-unique
3. `ssl.cert.subject.cn:"overseer"` + `port:8002,8003` — medium FP, generic CN
4. `port:8002 port:8003` co-occurrence on same host — medium FP, narrows to FL-Server shape
5. `http.html:"/api/v1/heartbeat" "/api/v1/promote"` — low FP, Overseer-specific

**Shodan-dark:** 8002/8003 are gRPC-over-TLS — Shodan typically banners only the TLS cert, not the gRPC frame. Route to Step 0c scanner (tiptoe / zgrab2 with gRPC reflection probe) and to Censys host.services.banner.

## Lane 3 — API surface & data exposure

**Overseer (Flask, /api/v1):**
- `GET/POST /heartbeat` — project + role + sp_end_point params; **no explicit route-level auth**; in mTLS-on deployments the TLS handshake gates it, in POC/misconfig it does not. Reveals project name, server endpoints, role inventory.
- `GET/POST /promote` — X-USER header check vs privilege dict; bypassed in DEBUG. Lets an attacker pick the active FL server (HA failover hijack).
- `GET /state`, `GET /refresh` — service state, project metadata.

**FL Server (gRPC :8002):** model exchange + job dispatch. Metadata reads (job listing, run history) sit behind the Admin channel, not the FL-Client channel. Reflection default: unknown.

**Admin (:8003, TCP):** FLARE Console protocol. Job submission, run start/stop, log fetch. Cert-gated in secure mode.

**Dashboard:** project metadata, participant list, **startup kit download endpoint** — the high-value target. **CVE-2026-24178** (CVSS 9.8) is exactly this surface: authz bypass through user-controlled key on the user management routes, no auth needed. Patched 2.7.2.

**Metadata-only vs training-trigger:** Overseer heartbeat/state/promote and Dashboard read routes = metadata-only. FL Server gRPC `submitJob`/`startRun` and Admin TCP commands = training-trigger; do not invoke.

## Lane 4 — CVEs & prior research

**NVIDIA Security Bulletin, April 2026 (a_id/5819), fixed in 2.7.2:**
- **CVE-2026-24178** — Dashboard authz bypass via user-controlled key (CWE-639), CVSS 9.8. Unauth, network-exploitable. Privilege escalation, info disclosure, RCE, DoS. Credited EyeR SEC LTD.
- **CVE-2026-24186** — FOBS (Federated Object Binary Serialization) insecure deserialization → RCE on receipt of a crafted FOBS message. Affects FL Server and Clients. High severity.
- **CVE-2026-24204** — listed in same bulletin; specific class **unknown — source X (NVIDIA bulletin) lists CVE but the public summaries do not break out the technical detail**; NVD entry not yet detailed at search time.

**Prior research:** medical-imaging FL benchmarking (arxiv 2511.00037, Owkin Substra vs NVFlare vs Flower); BraTS + MONAI FL training as the canonical NVFlare demo. No public exploit code located for the 2026 CVEs as of this writeup.

## Lane 5 — Deployment patterns

Healthcare-heavy: Mass General Brigham (with Rhino Health), Lahey, NIHR Cambridge; Mayo + Case Western + Georgetown + UCSD + Florida + Vanderbilt renal-cell-carcinoma consortium; Owkin uses its own Substra but benchmarks against FLARE. Pharma + MONAI/Clara Holoscan stacks integrate FLARE for cross-site imaging training.

K8s pattern: provisioned Helm chart (`HelmChartBuilder` in project.yml) puts Overseer + Servers in-cluster; clients/admin connect from outside. Ingress is operator-supplied — typical gap.

**Sensitive data flow:** PHI never crosses the wire by design, but **imaging metadata** (DICOM headers in run logs), **model gradients** (gradient-inversion reconstruction risk on medical images), **job configs** (site names, dataset paths, study IDs) all transit Admin/FL-Server channels. The Dashboard's startup-kit download is the crown jewel — kit theft = silent client impersonation = poisoned gradient injection.

## Lane 6 — Ecosystem co-deployment

Expect on adjacent ports on the same host/cluster:
- **MONAI Label / MONAI Deploy** — medical imaging service
- **Triton Inference Server** — 8000 (HTTP), 8001 (gRPC), 8002 (metrics) — **collides with NVFlare FL-Server 8002**; expect operators to remap one. Triton's 8000/8001 are a strong co-tenancy signal.
- **MLflow** — :5000, FLARE has first-class MLflow streaming integration
- **TensorBoard** — :6006
- **W&B** — outbound only

**TLS chain:** NVFlare provision tool emits a **self-signed project-internal root CA**. NVIDIA does not run a public root for these. Cert CN sweep should pivot on observed CN patterns + intermediate signer.

## Stop-condition notes

- gRPC reflection default state on FL Server: unknown from docs. Confirm by source read of `nvflare/fuel/f3/drivers/grpc_driver.py` before probing.
- CVE-2026-24204 technical class: unknown from public sources at time of writing; NVIDIA bulletin is the only authoritative anchor.
- Cert CN exact strings: unknown — provisioning is project-name-templated; harvest from observed certs at scan time, do not pre-commit a regex.

## Sources

- NVIDIA Security Bulletin April 2026 — nvidia.custhelp.com/app/answers/detail/a_id/5819
- CVE-2026-24178 — sentinelone.com/vulnerability-database/cve-2026-24178/
- CVE-2026-24186 — nvd.nist.gov/vuln/detail/CVE-2026-24186, sentinelone.com/vulnerability-database/cve-2026-24186/
- TheHackerWire writeup — thehackerwire.com/nvidia-nvflare-dashboard-critical-auth-bypass/
- NVFlare docs 2.7 (main) — nvflare.readthedocs.io/en/main/ (security, provisioning, POC command, dashboard_api, server_port_consolidation, communication_configuration, high_availability)
- Overseer source — nvflare.readthedocs.io/en/stable/_modules/nvflare/ha/overseer/overseer.html
- GitHub repo — github.com/NVIDIA/NVFlare
- arxiv 2511.00037 — FL framework benchmarking (FLARE / Flower / Substra)
- NVIDIA blogs — federated learning in healthcare, Mass General + Rhino, Mayo renal-cell-carcinoma consortium
