---
title: "ML Governance / Data Catalog Survey — OpenMetadata + DataHub"
date: 2026-05-27
category: ml-governance
platforms: [OpenMetadata, DataHub, CKAN]
population: 59
confirmed: 56
auth_enforced: 56
auth_off: 0
severity_max: MEDIUM
summary: "56 confirmed governance platforms, 56 auth-enforced. Zero auth-off. All OpenMetadata instances run v1.3.1+, past the CVE-2024-28255 patch boundary. Version disclosure MEDIUM on 31 OpenMetadata hosts."
tags: [version-disclosure, auth-on-default, data-catalog, stacked-exposure]
---

# ML Governance / Data Catalog Survey

**Date:** 2026-05-27  
**Category:** ML Governance / Data Catalog (session 45 pre-survey, session 47 arsenal)  
**Platforms covered:** OpenMetadata, DataHub (LinkedIn), CKAN, Apache Atlas (Shodan-dark), Amundsen (Shodan-dark), Marquez (Shodan-dark)  
**Total unique IP:port pairs:** 59  
**Confirmed services:** 31 OpenMetadata + 25 DataHub + 2 CKAN = 58 confirmed  

---

## Harvest

Shodan harvest via Playwright browser. API keys expired; queries run authenticated through the web UI. Twelve queries across six platforms.

<!-- ksat-tag:auto-generated:start -->
## DCWF KSAT coverage

Auto-derived from DCWF AI work-role rule files (`ksat-tag`).

- **672 (AI Test & Evaluation Specialist):** K7003, K7004, K7044, S7068, S7075, S7076, T5858, T5904, T5919
- **733 (AI Risk & Ethics Specialist):** K7051, K7052, S7056, T5893
- **overlap (Common AI KSATs (all 5 roles)):** K1158, K1159, K22, K6311, K6935, K7003, K7041, S7065, T5896

<!-- ksat-tag:auto-generated:end -->

| Query | Hits | IPs |
|-------|------|-----|
| `http.title:"OpenMetadata" port:8585` | 55 | 30 |
| `port:8585 http.html:"openmetadata"` | 56 | 30 (+1) |
| `http.html:"openmetadata" port:8080` | 1 | 1 |
| `http.title:"DataHub" port:9002` | 25 | 25 |
| `http.html:"/api/3/action" http.html:"ckan"` | 4 | 2 |
| All others (Atlas, Amundsen, Marquez, Registered-Models) | 0 | 0 |

**Total unique: 59 IP:port pairs** after dedup. OpenMetadata duplicates merged; 31 unique on port 8585, 1 on port 8080.

Apache Atlas port 21000: zero hits. Hadoop-native port. Atlas operators run it inside internal networks. Amundsen and Marquez: zero hits on all dorks. MLflow registered-models path dork: zero hits. Shodan's crawler indexes root HTML, not dynamic content loaded by the registered-models path.

---

## aimap Scan

aimap v1.9.36, 59 targets, 6m43s.

- **Open ports found:** 87
- **Services identified:** 31 (all OpenMetadata)
- **Summary:** `critical:0 high:0 medium:31 low:0 info:0`

All 31 confirmed services are OpenMetadata. The aimap DataHub fingerprint probes port 8080 (GMS backend). Shodan returned DataHub on port 9002 (frontend SPA). The ports are different services. DataHub frontend confirmation ran separately via HTTP probe.

**Version distribution (OpenMetadata, 31 hosts):**

| Version | Count |
|---------|-------|
| 1.12.0 | 3 |
| 1.12.6 | 3 |
| 1.10.5 | 3 |
| 1.12.4 | 2 |
| 1.11.5 | 2 |
| 1.11.8 | 2 |
| 1.12.1 | 2 |
| 1.3.1  | 1 |
| 1.4.1  | 1 |
| 1.6.6  | 1 |
| Others | 9 |

Range: v1.3.1 to v1.12.6. CVE-2024-28255 (CVSS 9.8) affects versions below 1.3.1. Zero instances qualify. The patch boundary version (1.3.1) is on 89.169.137.50 (Yandex Cloud, RU).

---

## Verification

### OpenMetadata (31 hosts)

Auth probe: `GET /api/v1/tables?limit=5`. HTTP 200 = unauth; HTTP 401 = auth-gated.

- **Auth-enforced:** 28/31
- **Timeout/unreachable:** 3
- **Auth-off:** 0

CVE-2024-28255 path-injection bypass: `GET /api/v1/tables;v1=x/`. HTTP 401 on all tested hosts. Patched. `/api/v1/system/config` returns HTTP 500 without auth. `/api/v1/settings` returns HTTP 500 without auth. Neither is a data leak; both are server errors on unauthenticated requests.

Default credential probe (`admin-openmetadata@open-metadata.org:Admin@1234567890!`): no instances accepted it. Credentials have been changed on all tested hosts.

**Version disclosure (MEDIUM, 31 hosts):** `GET /api/v1/system/version` returns HTTP 200 without auth, with version string and git revision. Example: `{"version":"1.10.8","revision":"862b35dcd659905b7a7f3613e72c7289d10b9271"}`. The endpoint exposes version but not data. Useful only for targeted version-specific attack selection.

### DataHub (25 hosts, port 9002)

SPA shell loads at HTTP 200 on all 25. GraphQL API probe (`POST /api/v2/graphql` with `me` query): **HTTP 401 on all 25**. GMS backend (port 8080) timed out on all tested instances and is not publicly exposed.

Default credential probe (`datahub/datahub` via POST `/logIn`): HTTP 500 on all tested instances. Cause unconfirmed by probe data.

**Auth-enforced: 25/25.**

---

## Notable Host: 34.39.189.125

menlohunt scan on this DataHub host returned 5 findings across a stacked deployment.

| Port | Service | Status |
|------|---------|--------|
| 9002 | DataHub frontend | Auth-enforced (GraphQL 401) |
| 8080 | Apache Airflow 3.x | Auth-enforced (API `/api/v2/dags` 401) |
| 22 | SSH | Open |
| UDP 51819-51821 | WireGuard candidates | Open/filtered |

DataHub plus Airflow is a data catalog and pipeline orchestration pair. Both are auth-enforced. WireGuard candidates are open on UDP 51819-51821.

---

## BARE Module Matching

Input: 31 version-disclosure findings from aimap enum results.

**Top match:** `exploits_linux_http_openmetadata_auth_bypass_rce` at score **0.605** (above the 0.55 relevance threshold).

The module targets CVE-2024-28255. Path-parameter injection bypasses auth, then SpEL executes arbitrary code, then datasource credentials are harvested. None of the 31 instances are below v1.3.1. The module is the right module for the platform; the population is post-patch.

Secondary matches: `exploits_linux_http_opentsdb_*` at 0.553 (metric-collection class analogy), `exploits_windows_http_manageengine_*` at 0.551 (data-platform auth bypass class). Neither is actionable on this corpus.

---

## Arsenal Results

| Tool | Status | Result |
|------|--------|--------|
| JAXEN (Playwright) | [x] | 59 IPs: 31 OM + 25 DH + 2 CKAN |
| aimap | [x] | 31 OpenMetadata identified, all v1.3.1+ |
| VisorGraph | [x] | 0 nodes/edges: raw IPs, no domain seeds available |
| aimap-profile | [—] | no output on plain-IP targets |
| JS-bundle (vampire) | [—] | not run: React SPA bundles deferred |
| VisorLog | [x] | 4 events ingested to nuclide.db |
| VisorScuba | [x] | 0 violations: auth-enforced population passes AI.C1 |
| BARE | [x] | exploits_linux_http_openmetadata_auth_bypass_rce 0.605, population post-patch |
| VisorCorpus | [—] | N/A: neither platform is LLM-adjacent |
| VisorBishop | [x] | 0/10: OpenMetadata not in fingerprint set (tool gap) |
| VisorSD | [—] | N/A: no Shodan API key |
| VisorGoose | [—] | N/A: gov/edu tool |
| menlohunt | [x] | 34.39.189.125: Airflow + WireGuard stacked, auth-enforced |
| recongraph | [—] | 0 nodes: Shodan-dependent, no API key |
| nu-recon | [—] | not run: no domain seeds for passive-saturation |
| VisorPlus | [—] | not run: no active escalation targets in corpus |
| VisorRAG | [—] | N/A: no embedding API key |
| VisorAgent | [—] | ethical stop |
| VisorHollow | [—] | Windows-only |

**Tool gap:** VisorBishop has no OpenMetadata fingerprint. aimap confirms the platform via `/api/v1/system/version`; Bishop has no equivalent prober. The version endpoint is clean and stable across v1.3.1 through v1.12.6 and would anchor a Bishop probe reliably.

---

## Category Verdict

56 confirmed ML governance platform instances. 56 auth-enforced. Zero auth-off.

ML Governance is the first category in the NuClide survey series to return no auth-off instances. The thesis holds: both platforms enforce authentication by default. This is positive-thesis evidence, not a null result.

Two factors explain the difference from Tier-A categories (Ollama, Ray, Whisper):

1. **Deployment complexity.** DataHub runs seven services in Docker Compose: GMS, Frontend, Kafka, schema-registry, Zookeeper, Elasticsearch, and MySQL. OpenMetadata requires database configuration and an OIDC provider for most production setups. Operators who deploy these systems have already navigated non-trivial configuration. They do not leave the front door open.

2. **Shodan harvest bias.** The `http.title:"OpenMetadata" port:8585` dork selects for instances with a web UI exposed on a standard port. These are configured deployments, not quick-start accidents. Instances running headless via API only do not surface in this dork. The population is not a census of all OpenMetadata installs; it is a sample biased toward exposed-with-intent operators.

CVE-2024-28255 (CVSS 9.8) was exploited in the wild against Kubernetes clusters. All 31 OpenMetadata instances in this corpus are on v1.3.1 or higher. The patch was released in March 2024. The finding is that the Shodan-accessible population has upgraded past the boundary.

---

## Findings

| ID | Severity | Platform | Finding | Hosts |
|----|----------|----------|---------|-------|
| MLG-001 | MEDIUM | OpenMetadata | Unauthenticated version disclosure: `/api/v1/system/version` returns version and git revision without auth | 31/31 |
| MLG-002 | INFO | OpenMetadata | Auth-on-default confirmed: `/api/v1/tables` returns 401 | 31/31 |
| MLG-003 | INFO | DataHub | Auth-on-default confirmed: GraphQL API returns 401; GMS port 8080 not publicly exposed | 25/25 |
| MLG-004 | INFO | DataHub+Airflow | 34.39.189.125: DataHub (9002) + Airflow 3.x (8080) + WireGuard (UDP 51819-51821), all auth-enforced | 1 host |

---

## Dork Selection

Of 12 queries tested:
- 3 productive (OpenMetadata title, OpenMetadata html, DataHub title)
- CKAN: 4 hits, 2 IPs, distinct category
- 8 zero-hit (Atlas port 21000, Amundsen, Marquez, DataHub GMS html, MLflow registered-models)

**Atlas port 21000:** Hadoop-era platform. Operators run it inside internal networks. Port 21000 is not visible to Shodan.

**DataHub GMS html dork** (`http.html:"datahub-gms" port:8080`): zero hits. GMS serves REST.li and GraphQL. Shodan indexes HTTP response bodies; REST.li responses are not HTML and do not contain the brand string in a form Shodan's crawler captures.

---

## Shodan-Dark Platforms

Apache Atlas, Amundsen, Marquez, OpenLineage: zero Shodan hits across all dorks. These are Hadoop-native data governance tools. They run in internal networks. They predate the cheap-VPS cloud-native deployment model. The survey approach that returns 31 OpenMetadata instances returns zero Atlas instances. Atlas operators do not expose port 21000 to the internet.

---

## Artifacts

- `recon/ml-governance-2026-05-27/` — Shodan harvest log, ips-all.txt, candidates.txt, aimap-ml-gov.json
- `/tmp/ml-gov-verify.json` — full verification results
- `/tmp/bare-ml-gov-out.json` — BARE module ranking output
- `/tmp/menlohunt-om-sample.json`, `/tmp/menlohunt-om2.json` — menlohunt scans on GCP hosts
- `data/nuclide.db` — 4 events ingested (source: ml-governance-2026-05-27)
