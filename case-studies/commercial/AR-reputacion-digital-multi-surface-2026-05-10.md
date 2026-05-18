---
type: host
title: "reputacion.digital: Multi-surface chained exposure (Phoenix + NFS + Prometheus + dev SMTP)"
date: 2026-05-10
class: substrate
category: single-host-deep-dive
status: research-active
methodology: shodan-driven + visorgraph + ct-log subdomain enum + per-port auth-posture probe
---

# reputacion.digital: multi-surface chained exposure · 2026-05-10

NuClide Research · 2026-05-10

## Summary

reputacion.digital (Argentinian AI-driven online-reputation-management SaaS) operates a Kubernetes cluster on a single bare-metal host at `190.210.105.193` (Buenos Aires, NSS S.A. / iplannetworks.net). The operator has deployed authentik SSO with OAuth outposts in front of 27 internal services accessed by hostname (Phoenix, Grafana, MLflow, Jupyter, Postgres, Airflow, etc.). That domain-level SSO is correctly configured.

The exposure is **what bypasses the SSO front-end**: the IP-direct path. Services that listen on `190.210.105.193` answer requests by IP regardless of the SSO outpost binding, because the outpost is hostname-routed and the underlying services are not. The SSO-fronted Phoenix at `phoenix.reputacion.digital` redirects to authentik. The same Phoenix listening on `190.210.105.193:6006` does not.

This case study walks the IP-direct shadow stack: Phoenix unauth read+write+export of 1.21B LLM tokens, NFS server at port 2049 exporting 31 Kubernetes persistent volumes (including the Postgres data volume) to `*` with no IP restriction, Prometheus unauth on 9090 with 58 scrape targets revealing 39 internal endpoints and a one-request DoS primitive, and a MailCatcher dev SMTP intercept on port 1080. Surfaced from the broader Phoenix population sweep ([phoenix-llm-observability-survey-2026-05-10.md](phoenix-llm-observability-survey-2026-05-10.md)) where this host ranked #1 by token volume.

## Discovery context

Host surfaced on the Shodan dork `http.html:"arize-phoenix"` during the 2026-05-10 LLM-observability survey. Initial finding: 1.21B GPU_REPORTS tokens publicly readable on port 6006 GraphQL, plus Prometheus on port 9090 leaking infrastructure topology.

VisorGraph trace then mapped 58 Prometheus scrape targets across the operator's k8s cluster (CoreDNS, Elasticsearch, Flower/Celery, MinIO, Postgres, Traefik, vLLM, GPU exporters), pointing at a much larger k8s deployment than the single Phoenix exposure suggested. CT-log enumeration via crt.sh returned **126 unique hostnames** under `*.reputacion.digital`. Per-port and per-subdomain probing surfaced the chained exposure profile documented below.

## Operator profile (per public marketing)

reputacion.digital is an Argentinian AI/data SaaS positioning around social-media monitoring, brand sentiment, and citizen-complaint platforms. Self-tagline: "Transformamos datos en valor" (we transform data into value). Public-facing products visible in subdomain naming:

- **Reputación Digital Master** (`reclamos.*`, `dev.reclamos.*`). Citizen-complaint / civic-issues reporting platform: *"Reporta problemas en tu ciudad y sigue el estado de los reclamos"* (report problems in your city and follow the status of claims). Likely a SaaS sold to municipal governments.
- **Senti** (`senti.*`, `senti-app.*`, `sentitest.*`). Branded sentiment-analysis product surface
- **Tablero / Dashboard** (`tablero.*`, `tablero2.*`, `dashboard.*`). Analytical dashboards
- **GPU_REPORTS** project on Phoenix (1.21B tokens). Internal AI inference workload tied to one of the customer products

Hosting: single bare-metal `190.210.105.193` on Buenos Aires AS27747 (NSS S.A.) advertised as `customer-static-210-105-193.iplannetworks.net`. Port 22 OpenSSH 8.9p1 Ubuntu (patched). Cloudflare proxy fronts the apex `reputacion.digital` (Penpot+marketing).

## Layer 1: Phoenix unauth (LLM data plane)

Already characterized in the [Phoenix population survey](phoenix-llm-observability-survey-2026-05-10.md). Summary for this host:

| Project | Records | Traces | Tokens | Latest |
|---|--:|--:|--:|---|
| GPU_REPORTS | 878,986 | 3,353 | **1.21B** | 2025-07-10 |
| TEST_GPU_REPORTS | — | 1,463 | 31.3M | 2025-05-30 |
| evaluators | — | 431 | 0 | 2025-04-16 |
| gpu_reports_dev | — | 7 | 308 | 2025-05-09 |
| default | — | 0 | 0 | — |

Per the cross-version posture analysis in the survey, this host is on Phoenix v8.6.0. Too old to expose the `secrets` GraphQL query or the `Secret.value` field that newer versions added. The exposure is read+write of trace data plus the bulk-export REST primitive at `POST /v1/spans`.

## Layer 2: NFS exports. Kubernetes persistent volumes exposed to the public internet

Port 2049 (NFSv3 + NFSv4) is open. `rpcinfo -p` returns the full RPC service map (portmapper, mountd, nfs, nfs_acl, nlockmgr, status). `showmount -e` returns 31 exports, all exported to `*` (any client, no IP/host restriction):

```
/home/operador/volumes/data-500mi-rwo-{1..5}    *
/home/operador/volumes/data-500mi-rwx-{1..5}    *
/home/operador/volumes/data-1gi-rwo-{1..5}      *
/home/operador/volumes/data-1gi-rwx-{1..5}      *
/home/operador/volumes/data-10gi-rwo-{1..5}     *
/home/operador/volumes/data-10gi-rwx-{1..5}     *
/home/operador/volumes/postgres                 *
```

The naming convention is the standard k8s manual-PV pattern: `data-<size>-<accessmode>-<index>`. RWO = ReadWriteOnce, RWX = ReadWriteMany. The pre-allocated pool of 30 generic PVs in three sizes is what gets bound to PVCs as the cluster's workloads request storage. The **`/home/operador/volumes/postgres`** export backs the cluster's Postgres database directly.

NFSv3 has no transport-level authentication. Access control is by client IP (which is open to `*` here) and UNIX UID/GID matching once mounted. An attacker with root on any internet-connected Linux host can:

- `mount -t nfs 190.210.105.193:/home/operador/volumes/postgres /mnt/x`. Mount the Postgres data files directly (read+write since these are hosting `data` paths)
- Read raw Postgres heap files, recover all data offline (no SQL-layer auth), bypassing application-layer authorization
- Read+modify any of the 30 generic PVs depending on which workloads are bound (Phoenix's SQLite backing store, MinIO buckets, Elasticsearch indices, Kafka logs, etc.)

This is by far the most severe primitive in the exposure stack. **It bypasses every other auth layer the operator has installed.** The application-layer SSO (authentik) and the API-layer auth (FastAPI dependency injection on `accounts` and `manager`) become irrelevant if the underlying file storage is publicly mountable.

We did not mount any export. The `showmount -e` query is RPC-level metadata enumeration, not a write or read of actual file contents.

## Layer 3: Prometheus monitoring plane

Already mapped via VisorGraph trace. Summary:

- 58 scrape targets across the operator's k8s cluster
- Internal RFC-1918 endpoints exposed in scrape config: 39 unique addresses across `192.168.40.x` private subnet
- Job names visible: `akamai`, `coredns`, `elasticsearch_cluster_logs`, `elasticsearch_cluster_prod`, `elasticsearch_dev`, `extension`, `flower`, `gpu_exporter`, `iplan`, `minio`, `nvidia_exporter`, `postgres`, `prometheus`, `traefik`, `vllm`
- vLLM scrape targets: `192.168.40.44:8007`, `192.168.40.45:8006`, `192.168.40.45:8007`. Confirms multi-GPU vLLM inference farm
- GPU/NVIDIA exporters at `192.168.40.44:9400` and `192.168.40.45:9400`. Confirms 2 GPU compute nodes
- Akamai CDN node monitoring at 13 external IPs (`45.79.213.150:9100`, etc.). Linode Akamai endpoints, possibly the operator's content-delivery footprint
- `minio.reputacion.digital:9000/minio/v2/metrics/cluster`. MinIO is scraped by hostname

`/-/quit` and `/-/reload` Prometheus admin endpoints are reachable. `/-/quit` is a one-request DoS primitive on the monitoring plane. `/-/reload` is a configuration-reload trigger that can be used to thrash the operator's monitoring without needing to crash it.

Combined with the Phoenix data plane, an attacker has both the operator's AI customer data (read) AND the operator's monitoring (DoS). Coordinated exfil + monitoring blackout would let an attacker work undetected for as long as it takes the operator to notice metrics gaps.

## Layer 4: MailCatcher dev SMTP intercept (port 1080)

`http://190.210.105.193:1080/` returns the MailCatcher web UI (`thin` Ruby server). MailCatcher is a development tool that sniffs SMTP locally and exposes captured messages through a web interface. Typically used to test that an application's email-sending logic works without actually sending mail to real recipients.

The MailCatcher web UI is exposed to the public internet without authentication. Currently the message store is empty (`GET /messages` returns `[]`), so there's nothing to read right now. The exposure is latent: any time the operator's application points at this MailCatcher (during a staging deploy, a failed switch back to real SMTP after dev work, a forgotten test webhook), captured emails become publicly readable.

Available MailCatcher primitives once a message lands:

- `GET /messages`: list all captured messages (sender, recipient, subject, body)
- `GET /messages/<id>.html`: full HTML body of message <id>
- `GET /messages/<id>.source`: raw RFC822 source
- `GET /messages/<id>.eml`: downloadable email
- `GET /messages/<id>/parts/<cid>`: attachments
- `DELETE /messages/<id>`: wipe one message (data-loss primitive)
- `DELETE /messages`: wipe entire store (data-loss primitive)
- `GET /quit`: terminate MailCatcher (DoS primitive)

The exposure window is whenever the application sends mail. Categories of mail typically routed through MailCatcher in dev/staging:

- Password-reset tokens
- Account verification emails
- Invitation tokens
- Notification emails containing customer data
- Internal admin alerts

We did not retrieve any messages. The store was empty at probe time.

## Layer 5: MinIO + authentik (auth-protected)

- **MinIO API (port 9000)**: 403 on `/` (auth-required); some health endpoints (`/minio/health/live`, `/minio/health/ready`, `/minio/health/cluster`) return 200/0. Standard MinIO public health endpoints, expected behavior.
- **MinIO Console (port 9001)**: SPA login page. The pre-auth `/api/v1/login` endpoint discloses the OAuth SSO redirect including `client_id=JlyR28pyPRUDHI5JmlkB4vVkIvgjSR3erFpvzZJJ` for `minio.reputacion.digital` SSO via `auth.reputacion.digital`. Minor info disclosure; not exploitable directly.
- **authentik (ports 9443 + 9009)**: provisioned, branded `RD`, Enterprise license. Login flow reachable. Initial-setup flow returns 200 but is the standard redirect-to-login state, not a fresh-deploy. Admin/system API endpoints return 403 (properly auth-gated). No further primitive.

The MinIO + authentik posture is a **counterexample to the rest of the host**. These services are auth-fronted correctly.

## Layer 6: Domain footprint via CT logs

`crt.sh` enumeration across `*.reputacion.digital` returned **126 unique hostnames**. Categorized:

| Category | Examples | Count |
|---|---|--:|
| AI/ML/LLM | phoenix, mlflow, metaflow, evidentlyai, zenml, llm, generic-llama, chatllm, jupyter, jupyterironman, qdrant, voice2text | 12+ |
| Workflow/automation | airflow, dagu, n8n, automation8n, argocd | 5 |
| Storage/data | minio, kafka, postgres, elastic, es, registry, container.artifacts | 7 |
| Monitoring/dashboards | grafana, prometheus, flower, monitor, uptime, dashboard, dashboardserver2, dev.dashboard | 8 |
| Apps | accounts, manager, reclamos, dev.reclamos, senti, sentitest, senti-app, promocion, coronavirus | 9 |
| Networking | vpn, traefik (×8 named instances), serverq, pdf | 11 |
| Identity | auth, sso-dashboard | 2 |
| Misc tooling | wiki, draw (Penpot), tabby, zammad, gitlab, portainer, devpi, odoo | 8 |
| Internal naming | mrrobot, theoden, frodo.traefik, galadriel.traefik, hulk.traefik, mazinger.traefik, sam.traefik, piquin.traefik | 8 |

Internal-naming patterns (LOTR characters, superheroes, anime references like Mazinger and Ironman) suggest the cluster's k8s nodes are individually named after pop-culture characters. This is an operator-attribution signal. The same naming convention will appear in their internal documentation, logs, etc.

## Layer 7: Public APIs with auth-fronted endpoints

Two services expose their full OpenAPI specs publicly while gating the actual endpoints behind auth:

### accounts.reputacion.digital (Account Manager v0.2.39, uvicorn/SvelteKit)

- 38 paths exposed in `/openapi.json`
- Endpoint test: returns `{"detail":"Inactive user"}` HTTP 400 → session-based auth, properly rejecting anonymous
- Path categories visible from spec: `/auth/apikey/`, `/auth/oidc/`, `/proxy/`, `/reports/{social-network}` (twitter, facebook, instagram, tiktok, youtube, telegram, reddit, twitter_blu, twitter_publisher, google_search), `/sn/v2/{sn_name}`, `/user_account/`, `/vpn/`
- Notable: the `/reports/*` endpoints suggest an internal social-media-account-management product (likely sock-puppet or content-monitoring infrastructure given the name "Account Manager" and the per-platform breakdown)
- Notable: `/vpn/` endpoints suggest the operator manages VPN nodes programmatically. Chains with their `vpn.reputacion.digital` NetBird Dashboard

### manager.reputacion.digital (RD_Manager, uvicorn)

- 120 paths exposed in `/openapi.json` (152KB)
- All endpoints return 307 redirect or 401 unauth → auth-fronted
- Path prefixes: `/admin/` (26 ops), `/workspace/` (15), `/user/` (14), `/apikey/` (10), `/data/` (9), `/notification/` (9), `/report/` (8), `/alerts/` (8), `/tasks/` (7), `/stripe/` (7), `/templates/` (7), `/storage/` (6), `/form/` (6), `/crontasks/` (5), `/modules/` (5), `/chat_agent/` (5)
- `/stripe/` prefix indicates billing integration
- `/chat_agent/` prefix indicates LLM-backed automation features
- `/admin/` (26 ops) is the largest category. Internal admin tooling

The OpenAPI exposure is a **reconnaissance gift**: an attacker who finds a credential through any other channel (the NFS Postgres dump, the MailCatcher leak window, the Phoenix LLMjacking, etc.) gets a full API surface map without further blind probing.

## Layer 8: LiteLLM proxy

`https://llm.reputacion.digital/` exposes the LiteLLM v1.80.5 Swagger UI. 342 endpoints. The actual API is auth-protected (`/v1/models` returns 401 "No api key passed in"). Two unauth metadata endpoints disclose minor config:

- `/.well-known/litellm-ui-config` → `{"server_root_path":"/","proxy_base_url":"https://llm.reputacion.digital"}`
- `/.well-known/openid-configuration` → standard OIDC config with auth/token endpoints

This is the operator's LLM-provider proxy (centralizes OpenAI/Anthropic/etc. API keys). Properly fronted, but the OpenAPI exposure tells an attacker which providers and which features are configured (the spec includes per-provider passthrough endpoints `/openai/{endpoint}`, `/anthropic/{endpoint}`, `/azure/{endpoint}`, `/bedrock/{endpoint}`, `/vertex_ai/{endpoint}`, `/assemblyai/{endpoint}`).

## Chain summary

The exposure stack tells a coherent story about how a competent operator's defensive posture can still leave a major surface area open:

1. **Operator did the SSO right.** authentik with OAuth outposts, branded UI, 27 services properly fronted by hostname.
2. **Operator did the API auth right.** accounts and manager apps both reject unauth requests with the right HTTP semantics.
3. **Operator missed the IP-direct shadow.** Every service on `190.210.105.193:<port>` answers requests by IP regardless of the SSO outpost binding. Phoenix on 6006, Prometheus on 9090, MailCatcher on 1080, NFS on 2049. All bypass the hostname-routed SSO front-end.
4. **The NFS exposure is the deepest.** No matter how good the application-layer auth is, exposing the underlying k8s persistent volumes (especially the Postgres one) to `*` makes everything above it auditable / readable / writable by any attacker with a Linux mount client.

## Severity ranking (research grade)

Ordering by likely real-world impact if exploited:

1. **NFSv3/v4 unauth exports including `/postgres`**, full database compromise primitive, bypasses application-layer auth entirely
2. **Phoenix unauth read+write+export of 1.21B tokens**, customer LLM data plane, write primitive enables trace poisoning
3. **Prometheus unauth + DoS primitive (`/-/quit`)**, internal infra topology disclosure + monitoring blackout
4. **MailCatcher dev SMTP intercept**, latent, currently empty, but trivially captures any application email if the operator points at it
5. **Open OpenAPI specs on auth-fronted apps**, reconnaissance enabler, not a primitive on its own

## Evidence pack

`~/recon/reputacion-digital-2026-05-10/`

- `evidence/crtsh.json`: 126-hostname CT-log enumeration
- `evidence/subdomains.txt`: sorted subdomain list
- `evidence/subdomain-fingerprint.tsv`: HTTP fingerprint of all 126
- `evidence/nfs-exports.txt`: full `showmount -e` output (31 exports)
- `evidence/litellm-openapi.json`: 342-endpoint spec
- `evidence/accounts-openapi.json`: 38-endpoint spec
- `evidence/manager-openapi.json`: 120-endpoint spec
- `evidence/litellm-ui-config.json`, `evidence/litellm-oidc.json`. Minor info disclosures
- `evidence/accounts.html`, `evidence/manager-docs.html`. Landing-page captures

Cross-references:

- Population context: [phoenix-llm-observability-survey-2026-05-10.md](phoenix-llm-observability-survey-2026-05-10.md). Host #1 by token volume in the 94-host unauth Phoenix population
- VisorGraph trace: `~/recon/2026-05-10-llm-sweep/phoenix/visorgraph-output/190.210.105.193.json`. Prometheus scrape topology + 39 internal endpoints

## What this case study illustrates (cross-cutting)

This single host is a clean example of a class of failure mode worth surfacing in cross-survey methodology notes:

> **Hostname-routed auth doesn't protect the IP-direct shadow.** When an operator deploys SSO at the application layer (authentik, OAuth proxy, or similar) and binds it via the reverse proxy's hostname routing, every service that listens on the underlying host's IP, at any port, answers requests by IP and bypasses the SSO front-end. The operator's mental model of "everything is auth-fronted" is wrong by exactly the count of services that don't have their own auth in addition to the reverse-proxy-level auth.

The fix at the operator side is layered: each service needs its own auth in addition to the reverse-proxy auth, OR firewall rules need to block direct IP access at every port except 443. The fix at the vendor side (Phoenix, Prometheus, etc.) is to make auth the shipping default. The Phoenix population survey makes that case in detail.
