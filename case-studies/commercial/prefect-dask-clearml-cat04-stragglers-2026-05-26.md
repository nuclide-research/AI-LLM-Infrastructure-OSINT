# Cat-04 Stragglers: Prefect Auth-Off-Default, Dask University Clusters, ClearML Ransomed ES

**Survey:** Category 04 — Training, Experiments, Compute Orchestration (stragglers)  
**Date:** 2026-05-26  
**Platforms:** Prefect, Dask Dashboard, BentoML, ClearML  
**Method:** Shodan harvest (Playwright) + aimap v1.9.30/31 + manual verification

---

## Summary

Prefect workflow orchestration is auth-off-default. `/api/admin/settings` is world-readable on all instances. `/api/flows/filter` and `/api/deployments/filter` return complete workflow inventories without credentials. Nine of fifteen sampled instances returned full unauth access; extrapolated across 66 confirmed live instances, ~40 are likely unauth.

<!-- ksat-tag:auto-generated:start -->
## DCWF KSAT coverage

Auto-derived from DCWF AI work-role rule files (`ksat-tag`).

- **672 (AI Test & Evaluation Specialist):** K7003, K7004, K7044, S7068, S7070, S7075, S7076, T5858, T5904, T5919
- **733 (AI Risk & Ethics Specialist):** K7051, K7052, S7056, S7067, T5868, T5893
- **overlap (Common AI KSATs (all 5 roles)):** K1158, K22, K6311, K6935, K7003, K7024, K7041, S7065

<!-- ksat-tag:auto-generated:end -->

Dask Dashboard has no auth concept. Six university and cloud research clusters returned full cluster state without credentials — Cambridge, UC Berkeley, UC Santa Barbara, DigitalOcean (active 2026-05-26), OVH France, IONOS Germany.

ClearML is auth-on-default. One exception: the data tier at `37.230.233.135` (Cloud.ru, Russia) had Elasticsearch exposed on port 9200 — already ransomed and wiped before we arrived.

---

## F1: Prefect auth-off-default — ~40 unauth instances (HIGH)

**Population:** `http.title:"Prefect"` = 457 Shodan results. 66 confirmed live. 9/15 sampled unauth.

Prefect v3.x ships with no authentication in the default install. The API server binds to `0.0.0.0:4200` with `csrf_protection_enabled: false` and `cors_allowed_origins: "*"`.

**Unauthenticated endpoints (confirmed across all tested instances):**
- `GET /api/admin/settings` — full server config, DB pool size, event retention, CORS/CSRF state
- `POST /api/flows/filter` — full workflow inventory (names, IDs, versions)
- `POST /api/deployments/filter` — all deployments with cron schedules, work pool names, parameters
- `GET /api/workers/filter` — worker fleet (connection strings, internal IPs)

---

## F1a: Italian LLM procurement pipeline (CRITICAL)

Host: `185.25.207.230:4200`  
Provider: Servereasy, Italy  
Prefect: v3.6.25

35 flows, 47 deployments, all running in `scrapers-isolated` work pool. Active LLM-enrichment pipeline scraping Italian and Spanish public procurement data:

| Deployment | Schedule | Source |
|---|---|---|
| AI Tender Enrichment | every 2h | ANAC (IT), MePA (IT) |
| AI Recipe Autogen | daily | — |
| Lot AI Summary Enrichment | hourly | PLACSP (ES), PVL (IT) |
| Lot Requirements Extraction | daily | Gazzetta Ufficiale (IT) |

Full deployment configs — including work pool assignments, parameter schemas, and flow run history — are readable without credentials. The operator is running LLM-based document enrichment against live government procurement feeds.

---

## F1b: Energy grid pipeline (HIGH)

Host: `51.15.137.116:4200`  
Provider: OVH, France  
Prefect: v3.6.22

33 flows, 17 deployments. Ingests, transforms, and forecasts European energy grid data:

| Flow pattern | Schedule |
|---|---|
| `ingest_*` (prices, load, cross-border, reservoir, generation, weather) | every 30–60 min |
| `transform_*` | every 15/45 min |
| `run_*_forecast` | hourly |

`transform-all-scheduled` runs every 15 minutes. Full schedule and deployment config readable unauth.

---

## F1c: MLS sports data — CORS + CSRF disabled (HIGH)

Host: `134.122.1.125:4200`  
Provider: DigitalOcean, US  
Domain: `prefect.knowthedata.com`  
Prefect: confirmed via `/api/admin/settings`

`/api/admin/settings` response:
```json
{
  "csrf_protection_enabled": false,
  "cors_allowed_origins": "*"
}
```

9 flows: "download-all-games", "persist-game-to-database", "mls-staging". The `cors_allowed_origins: "*"` combined with `csrf_protection_enabled: false` means a cross-site page can POST to the Prefect API and trigger flow runs against the authenticated user's session in any browser.

---

## F1d: LlamaTel pipeline (HIGH)

Host: `104.196.175.70:4200`  
Provider: GCP, US  
Prefect: v3.6.23

Single flow: `llamatel-pipeline`. Deployment: `llamatel-monthly`, runs `0 8 1 * *` (first of each month). Parameters: `start_date`, `end_date`. Work pool: `my-work-pool`. Telecom + LLM integration pipeline, full config readable unauth.

---

## F2: Dask Dashboard — 6 unauth cluster dashboards (HIGH)

Dask has no authentication at any layer. The dashboard at port 8787 exposes full cluster state to anyone.

| Host | Org | Workers | Status |
|---|---|---|---|
| 128.232.235.67:8787 | University of Cambridge | 2+ | Last active 2026-04-13 |
| 128.32.3.74:8787 | UC Berkeley | 2+ | Last active 2026-04-21 |
| 128.111.45.74:8787 | UC Santa Barbara | — | Degraded (missing bokeh) |
| 162.243.219.39:8787 | DigitalOcean | 2+ | **Active 2026-05-26** |
| 51.75.201.80:8787 | OVH FR | 1 | Last active 2026-04-14 |
| 217.160.76.115:8787 | IONOS DE | 0 | Idle |

The DigitalOcean instance (`162.243.219.39`) is actively running — log timestamps match the scan date. Worker naming: `dask-11-00`, connected at `10.128.9.201`.

Each dashboard exposes: worker connection strings (internal IPs), scheduler event logs, task state (pending/processing/complete), memory and CPU per worker.

Cambridge and UCB are academic research deployments — likely idle sessions left exposed after a compute job completed.

---

## F3: ClearML — auth-on-default, ransomed ES backend (INFO/HIGH)

**Population:** 102 Shodan title hits. 81 scanned. Auth holds at the API layer — all `POST` endpoints return 401.

**Exception: `37.230.233.135` (Cloud.ru, Russia)**

ClearML API server on port 8008: auth-enforced (401).  
Elasticsearch backend on port 9200: unauth, already ransomed.

`read_me` index content:
```
Your database has been deleted from your server...
send 0.0041 BTC to bc1q38rjul6gdamfflf6p4ukz0ymtvfgfv2j9saf6r
contact: wendy.etabw@gmx.com
code: 0SH7HH1Q72JL
```

Remaining indices: `worker_stats` (4,344 docs, CPU/temp telemetry for `pd01-srv-055`) and `queue_metrics` (3,308 docs). Original experiment and task data wiped. The ClearML operator locked the application layer but left the data tier exposed. Standard split-auth failure.

**26 of 81 hosts** expose `server.info` without credentials — version disclosure only, no experiment data. Notable: Brno University of Technology (`185.62.108.93`) runs v1.15.0 (18+ months old).

---

## F4: BentoML — narrative.io NarrativeLLMService (MED)

Host: `32.193.18.123:443`  
Operator: narrative.io (Narrative I/O, US data marketplace)  
Model: `narrative-io/Rosetta-Unified-Marketing` (4-bit quantized)

`GET /v1/config` (unauth) returns runtime config confirming deployment.  
`GET /docs.json` (unauth) leaks:
- AWS account ID: `704349335716`
- ECR registry: `704349335716.dkr.ecr.us-east-1.amazonaws.com`
- AWS SSO profile: `t-engineering-704349335716`
- Full `docker run` deployment command

No live credentials in response. Inference endpoints (`/v1/taxonomy/suggest`, `/v1/rosetta_stone/suggest_mappings`) accessible — auth status not confirmed.

---

## Insight candidate: Prefect auth-off-default

Prefect is the fourth major workflow/orchestration platform found auth-off-default in this survey corpus (after n8n, Airflow anonymous-mode, and Ray Dashboard). The pattern: platforms that run on a single-node `pip install + run` default bind to `0.0.0.0` with no auth. Multi-tenant SaaS-first platforms (MLflow, ClearML, Dagster) ship with auth on because their use cases assume shared deployment.

**Candidate Insight #63:** Workflow orchestrators with single-binary local-first design (Prefect, n8n, Ray) default to no auth; MLOps platforms with managed-cloud heritage (ClearML, Weights & Biases) default to auth. The install experience predicts the auth posture.

---

## Recon artifacts

```
~/AI-LLM-Infrastructure-OSINT/recon/cat04-stragglers-2026-05-26/
  shodan-clearml-finetuning.txt       305 IP:PORT (ClearML + noise)
  shodan-prefect-temporal-dask-bentoml.txt  189 IP:PORT
  ips-clearml.txt                     81 IPs
  ips-prefect.txt                     62 IPs
  ips-dask.txt                        48 IPs
  ips-bentoml.txt                     10 IPs
  aimap-clearml.json                  81 targets, 3 findings
  aimap-prefect.json                  62 targets, 0 findings (no Prefect fingerprint)
  aimap-dask.json                     48 targets, 9 services, 1 finding
  aimap-bentoml.json                  10 targets, 8 services, 1 finding
```

**aimap gap noted:** Prefect fingerprint exists in fingerprints.go but the enumerator has no Prefect-specific deep probe — the unauth workflow data was found via manual verification, not the automated chain. Add enumPrefect to close the gap.
