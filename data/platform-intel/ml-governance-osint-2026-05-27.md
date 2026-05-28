# ML Governance / Data Catalog / Lineage Platform OSINT — Pre-Survey Intelligence
**Date:** 2026-05-27
**Purpose:** Tune dork queries, understand auth posture, identify verification probes, document data exposure classes before Shodan harvests.
**Scope:** 13 platforms — data catalogs, ML metadata stores, lineage trackers, governance platforms.
**Status:** Pre-survey. No active probing conducted.

---

## OpenMetadata

**Category:** Data Catalog / Lineage / Governance  
**Default Ports:** 8585 (HTTP), 8586 (HTTPS admin)  
**Auth Default:** on (JWT required) — but CVE-2024-28255 allows bypass on all versions < 1.3.1  
**Shodan Dork (primary):** `http.title:"OpenMetadata" port:8585`  
**Shodan Dork (secondary):** `http.html:"open-metadata" port:8585`  
**Shodan Dork (tertiary):** `html:"openmetadata" port:8585`  
**Verification Probe:** `GET /api/v1/system/version` → 200 + `{"version":"...","revision":"...","timestamp":...}` — no auth required; `GET /api/v1/system/config/jwks` → returns public keys  
**Auth Bypass Probe (patched < 1.3.1):** `GET /api/v1/tables;v1=bypass/` — path parameter injection bypasses JwtFilter  
**Data Exposure Class:** Full data catalog: table schemas, column PII tags, database connection metadata (host/port/db name), lineage graphs linking upstream/downstream pipelines. Environment variables on compromised container may contain credentials for connected data sources.  
**Known CVEs:**
- CVE-2024-28255 (CVSS 9.8) — auth bypass via path parameter injection in JwtFilter, affects < 1.3.1, exploited in wild against Kubernetes clusters for cryptomining
- CVE-2024-28253 (CVSS 9.4) — authenticated RCE via SpEL injection at `/api/v1/policies/validation/condition`
- CVE-2024-28254 — authenticated RCE via SpEL injection at `/api/v1/events/subscriptions`
- CVE-2024-28847 — additional SpEL injection vector
- CVE-2024-28848 — additional auth bypass vector  
**Default Credentials:** admin/admin on fresh installs (documented default; change recommended)  
**Notes:** Actively exploited (Microsoft TI report April 2024). Chain: auth bypass → SpEL RCE → env var harvest → lateral movement to all connected data sources. The platform stores connection strings for every ingested data source — Snowflake, BigQuery, Postgres, etc. Do not anchor dorks on port alone; look for the `/api/v1` path in banners. FP risk: other Java services on 8585 are rare.

---

## DataHub (LinkedIn)

**Category:** Data Catalog / Metadata Platform  
**Default Ports:** 9002 (frontend UI), 9001 (internal), 8080 (GMS / Generalized Metadata Service backend)  
**Auth Default:** off by default on GMS (port 8080) — `METADATA_SERVICE_AUTH_ENABLED` must be explicitly set; frontend requires login but uses `DummyLoginModule` by default accepting any credentials  
**Shodan Dork (primary):** `http.title:"DataHub" port:9002`  
**Shodan Dork (secondary):** `http.html:"datahubproject" port:9002`  
**Shodan Dork (tertiary):** `http.html:"datahub-frontend" port:8080`  
**Verification Probe:** `GET http://<host>:8080/config` → 200 + JSON with `"noCode"` field; `GET http://<host>:8080/entities?urns[0]=urn:li:corpuser:datahub` → returns user entity without auth token when auth is default-off  
**Auth Bypass (GMS default):** Direct requests to port 8080 bypass frontend login entirely; `X-DataHub-Actor` header accepted as identity with no signature verification when auth disabled  
**JWT Bypass:** Even with auth enabled, GMS does not verify JWT cryptographic signatures (GitHub Security Lab finding) — forge any user  
**Data Exposure Class:** Full organizational data inventory: all database entities, schema metadata, table/column lineage, ownership maps, PII classification tags, ingestion source configs (may include connection strings). REST.li API at `/restli/docs` documents all queryable surfaces.  
**Known CVEs:** No formal CVE numbers assigned to the JWT non-verification or NoOpAuthenticator issues; GitHub Security Lab audit published findings without CVE assignment. Check GitHub Security Advisories for datahub-project/datahub.  
**Default Credentials:** datahub/datahub (frontend; documented, widely known)  
**Notes:** Two attack surfaces: frontend on 9002 (datahub/datahub creds) and GMS on 8080 (no auth by default). Production deployments frequently leave GMS exposed. The `X-RestLi-Protocol-Version: 2.0.0` response header is a distinctive fingerprint for the GMS API. FP risk: port 9002 conflicts with some other services; anchor on `datahub` in title/html.

---

## Apache Atlas

**Category:** Metadata / Governance (Hadoop ecosystem)  
**Default Ports:** 21000 (HTTP), 21443 (HTTPS)  
**Auth Default:** default-creds — admin/admin baked in; no unauthenticated access by design, but default creds are universally known  
**Shodan Dork (primary):** `port:21000 http.title:"Atlas"`  
**Shodan Dork (secondary):** `port:21000 html:"Apache Atlas"`  
**Shodan Dork (tertiary):** `http.html:"api/atlas/v2" port:21000`  
**Verification Probe:** `GET /api/atlas/admin/version` with `-u admin:admin` → `{"Description":"Metadata Management and Data Governance Platform","Revision":"...","Version":"2.x.x"}` — unique `Description` field  
**Data Exposure Class:** Full Hadoop/big data inventory: Hive tables, HDFS paths, HBase tables, Kafka topics, Spark jobs, Storm topologies. Entity search exposes schema, PII classification tags (if configured), lineage from source to sink. In Cloudera/HDP deployments: integration credentials for connected services.  
**Known CVEs:**
- CVE-2022-34271 — authenticated user can write to web server filesystem (path traversal in import module), affects 0.8.4–2.2.0
- Multiple XSS CVEs in versions ≤ 2.3.0 (impersonation possible)
- No publicly documented unauth RCE; attack surface is default-creds → API → data exfil  
**Default Credentials:** admin/admin (famous; ships in default `users-credentials.properties`)  
**Notes:** Common in Cloudera CDH/CDP, Hortonworks HDP, and standalone Hadoop deployments. SSL disabled by default (`atlas.enableTLS=false`). Port 21000 is distinctive to Atlas — low FP risk. The REST API path `/api/atlas/v2/` is unique. Typical enterprise deployment: Atlas on internal network, but cloud-hosted Hadoop clusters frequently expose it.

---

## Amundsen (Lyft)

**Category:** Data Discovery / Catalog  
**Default Ports:** 5000 (frontend Flask app), 5001 (search service), 5002 (metadata service)  
**Auth Default:** off — "by default does not have any form of authentication software/configuration"; auth requires installing flaskoidc separately for each of three microservices  
**Shodan Dork (primary):** `http.html:"amundsen" port:5000`  
**Shodan Dork (secondary):** `http.title:"Amundsen" port:5000`  
**Shodan Dork (tertiary):** `http.html:"amundsen_application" port:5000`  
**Verification Probe:** `GET /api/metadata/v0/table_detail/<table_key>` → returns table name, columns, descriptions, owners — no auth required on default installs; `GET /healthcheck` on port 5001 (search) and 5002 (metadata)  
**Data Exposure Class:** Table/column metadata, descriptions, ownership, tags, table-level statistics, data lineage (source system, upstream/downstream). In organizations using Amundsen with Lyft-style PII tagging: direct PII field inventory exposed. Search API on 5001 allows full-text search across all catalog entries.  
**Known CVEs:** None published (niche platform, limited security research).  
**Default Credentials:** None — auth is simply absent by default.  
**Notes:** Port 5000 high FP risk (Flask apps, MLflow, CKAN, Marquez all use 5000). Anchor on `amundsen` in HTML body or title. Three-port footprint (5000/5001/5002) is distinctive when all three appear on one host. Largely replaced by more polished catalogs but still runs in Lyft-ecosystem-influenced orgs.

---

## Marquez (OpenLineage)

**Category:** Lineage API Server / Data Lineage  
**Default Ports:** 5000 (HTTP API, or 8080 when run via Java jar), 5001 / 8081 (admin interface), 3000 (UI)  
**Auth Default:** off — "by default, the HTTP API does not require any form of authentication or authorization" (documented)  
**Shodan Dork (primary):** `http.html:"marquez" port:5000`  
**Shodan Dork (secondary):** `http.html:"openlineage" port:3000`  
**Shodan Dork (tertiary):** `http.html:"marquezproject" port:8080`  
**Verification Probe:** `GET /api/v1/namespaces` → 200 + `{"namespaces":[{"name":"...","createdAt":"...","updatedAt":"...","description":...}]}` — `namespaces` array is distinctive; `GET /api/v1-beta/graphql` for GraphQL surface; `/healthcheck` on admin port  
**Data Exposure Class:** Full pipeline lineage graph: all job names, dataset names, run history, job facets (often includes SQL queries, schema definitions, Spark configs). The `/api/v1/jobs` and `/api/v1/datasets` endpoints dump entire pipeline inventory. Facets in OpenLineage events can contain connection URIs, schema snapshots, and column-level lineage.  
**Known CVEs:** None published.  
**Default Credentials:** None — no auth layer.  
**Notes:** Used as backend for Airflow's OpenLineage provider, dbt-ol, and Spark OpenLineage integration. Deployments often co-located with Airflow (port 8080). Port 5000 conflict with Flask/MLflow/CKAN is high FP risk — use `marquezproject` or `openlineage` HTML anchor. The GraphQL playground at `/graphql-playground` is a strong identity signal if indexed.

---

## OpenLineage (Standard / Ecosystem)

**Category:** Lineage Standard — look for Marquez server and Airflow plugin endpoints  
**Default Ports:** Varies by implementation — Marquez (5000/8080), Airflow OpenLineage transport (Airflow's own port 8080), standalone HTTP transport server (configurable)  
**Auth Default:** Depends on implementation — Marquez is off by default; Airflow OpenLineage transport endpoint inherits Airflow's auth  
**Shodan Dork (primary):** `http.html:"openlineage" port:5000`  
**Shodan Dork (secondary):** `http.html:"openlineage" port:8080`  
**Verification Probe:** `POST /api/v1/lineage` with OpenLineage event body → 201 on Marquez; look for `X-OpenLineage-Transport-Type` response header on some implementations  
**Data Exposure Class:** Same as Marquez — pipeline topology, dataset schemas, job runs, SQL query text in facets.  
**Known CVEs:** None for the standard itself.  
**Default Credentials:** None.  
**Notes:** OpenLineage is a specification; the exposure surface is any compatible server (Marquez being the reference). Also look for Airflow deployments that forward lineage to an open HTTP endpoint. The `/api/v1/lineage` POST endpoint accepting unauthenticated events allows lineage poisoning — write false lineage records into the store.

---

## Great Expectations

**Category:** Data Quality / Validation  
**Default Ports:** No persistent server mode in open-source (GX Core is a library); GX Cloud uses managed SaaS; community Data Docs serve static HTML on ephemeral local ports  
**Auth Default:** N/A for open-source library mode; GX Cloud is SaaS-only with API key auth  
**Shodan Dork (primary):** `http.html:"great_expectations" port:5000` (Data Docs served via Flask in some CI integrations)  
**Shodan Dork (secondary):** `http.title:"Data Docs" http.html:"great_expectations"`  
**Verification Probe:** `GET /` → HTML containing `great_expectations` class names or `<title>Data Docs</title>`  
**Data Exposure Class:** When Data Docs are served: validation results (pass/fail counts per dataset), expectation suite definitions, profiler output (column statistics, null rates, value distributions). Does not expose raw data, but exposes schema + statistical fingerprint of every profiled dataset.  
**Known CVEs:** None for the serving component.  
**Default Credentials:** None.  
**Notes:** Primary exposure vector is Data Docs accidentally served on a public IP (GitHub Actions + `--serve`, Docker Compose without port scoping). FP risk: generic Flask server on 5000. The HTML contains `great_expectations` as a CSS class and in script imports — use that as the anchor. GX Cloud is SaaS and not in scope for Shodan.

---

## Monte Carlo

**Category:** Data Observability  
**Default Ports:** SaaS-only — no self-hosted server component. Agent is deployed in customer VPC (Kubernetes/ECS) and calls out to `api.getmontecarlo.com` on 443.  
**Auth Default:** N/A — no inbound listener; agent initiates outbound connections only  
**Shodan Dork (primary):** N/A — no self-hosted server to fingerprint  
**Shodan Dork (secondary):** N/A  
**Verification Probe:** N/A  
**Data Exposure Class:** N/A (SaaS — data stays in customer environment; Monte Carlo agent reads but doesn't serve)  
**Known CVEs:** None published for the agent.  
**Default Credentials:** N/A  
**Notes:** Monte Carlo is pure SaaS. The self-hosted "Data Collector" agent is an outbound-only Kubernetes pod — no listening port. Not a Shodan target. Skip for survey purposes.

---

## Soda Core / Soda Cloud

**Category:** Data Quality  
**Default Ports:** Soda Core is a CLI/library (no server); Soda Cloud is SaaS (`cloud.us.soda.io` / `cloud.soda.io`); self-hosted Soda Agent runs in Kubernetes and listens on no public port  
**Auth Default:** Agent uses API keys to authenticate to Soda Cloud; no inbound listener  
**Shodan Dork (primary):** N/A — no self-hosted server  
**Shodan Dork (secondary):** `http.html:"soda-agent"` (speculative — unlikely indexed)  
**Verification Probe:** N/A  
**Data Exposure Class:** N/A (agent is outbound-only)  
**Known CVEs:** None.  
**Default Credentials:** N/A  
**Notes:** Like Monte Carlo, Soda's architecture deliberately avoids exposing any inbound listener. The self-hosted Soda Runner (v4) is also outbound-only. Not a viable Shodan target. Skip.

---

## Atlan

**Category:** Data Catalog / Governance  
**Default Ports:** SaaS platform; self-deployed runtime uses Temporal worker + Dapr on internal ports (8000 referenced in docs for workflow auth); no public-facing listener by design  
**Auth Default:** OAuth 2.0 client credentials (Client ID + Client Secret) for self-deployed runtime; SaaS uses bearer tokens  
**Shodan Dork (primary):** N/A — SaaS-primary, self-deployed component is outbound worker  
**Shodan Dork (secondary):** `http.html:"atlan" port:8000` (low confidence — speculative)  
**Verification Probe:** N/A  
**Data Exposure Class:** N/A if deployed correctly. The self-deployed runtime syncs to Atlan SaaS — no data served locally.  
**Known CVEs:** None published.  
**Default Credentials:** None.  
**Notes:** Atlan is enterprise SaaS. The "Self-Deployed Runtime" is a worker component, not a catalog server. Not a meaningful Shodan target in the same class as OpenMetadata/DataHub. Skip for bulk survey.

---

## Collibra

**Category:** Enterprise Data Catalog / Governance  
**Default Ports:** 4402 (Console web UI), 4401 (agent), 4421 (Search REST API), 4420 (Console database)  
**Auth Default:** on — requires login; REST API uses session-based auth via `POST /rest/2.0/auth/sessions` or Basic Auth  
**Shodan Dork (primary):** `port:4402 http.html:"Collibra"`  
**Shodan Dork (secondary):** `port:4402 http.title:"Collibra"`  
**Shodan Dork (tertiary):** `port:4421 http.html:"collibra"`  
**Verification Probe:** `POST /rest/2.0/auth/sessions` with `{"username":"Admin","password":"Admin"}` → session cookie; `GET /rest/2.0/assets` → returns asset inventory  
**Data Exposure Class:** When auth bypassed or default creds work: full enterprise data governance inventory — all data assets, business glossary, data lineage policies, stewardship assignments, PII classification rules. Collibra stores the organization's complete data governance posture.  
**Known CVEs:** Enterprise product; CVEs typically handled under coordinated disclosure. No high-profile public CVEs found.  
**Default Credentials:** `Admin/Admin` documented in installation guides (must be changed post-install).  
**Notes:** Collibra is on-prem/private cloud. Port 4402 is distinctive. Typical deployment: enterprise intranet but cloud-hosted instances with misconfigured firewall rules do appear. Low expected population on Shodan but high-value targets when found.

---

## CKAN

**Category:** Open Data Portal / Data Catalog  
**Default Ports:** 5000 (development server), 80/443 (production via nginx/Apache proxy)  
**Auth Default:** Partially open — read operations (dataset listing, search, package metadata) require no auth; write operations require API token. Anonymous API access is by design for public data portals.  
**Shodan Dork (primary):** `http.html:"ckan" port:5000`  
**Shodan Dork (secondary):** `http.html:"/api/3/action" http.html:"ckan"`  
**Shodan Dork (tertiary):** `http.title:"CKAN" port:5000`  
**Verification Probe:** `GET /api/3/action/status_show` → 200 + `{"success":true,"result":{"site_title":"...","ckan_version":"...","error_messages_shim":...}}` — `ckan_version` field is definitive identity signal; `GET /api/3/action/package_list` → returns all dataset names unauthenticated  
**Data Exposure Class:** Full dataset inventory, organization structure, all dataset metadata (titles, descriptions, resource URLs, tags). In government deployments: may link to sensitive data resources. API tokens sometimes appear in public dataset descriptions or resource URLs (credential leak vector).  
**Known CVEs:**
- CVE-2023-32321 — path traversal + RCE + information disclosure via crafted resource IDs
- CVE-2023-50248 — DoS via crafted dataset form submission
- CVE-2025-24372 — XSS via user/org images
- CVE-2025-54384 — stored XSS in Markdown description fields  
**Default Credentials:** N/A — admin account set during install wizard.  
**Notes:** Powers catalog.data.gov, open.canada.ca, data.humdata.org, and thousands of government open data portals. The `/api/3/action/status_show` endpoint is the cleanest identity probe — returns `ckan_version` with no auth required. Development instances on port 5000 are high FP risk from generic Flask; anchor on `ckan_version` JSON field. Production instances on 80/443 with nginx are fingerprinted via HTML content, not port.

---

## MLflow (Model Registry gaps)

**Category:** ML Experiment Tracking / Model Registry  
**Default Ports:** 5000 (tracking server UI + API)  
**Auth Default:** off by default — no authentication on the REST API or UI unless `--serve-artifacts` + auth plugin explicitly configured  
**Shodan Dork (primary):** `http.html:"mlflow" port:5000` (note: covered in prior surveys — focus here on registry-specific signals)  
**Shodan Dork (secondary):** `http.html:"registered-models" port:5000`  
**Shodan Dork (tertiary):** `http.html:"/api/2.0/mlflow/registered-models" port:5000`  
**Verification Probe (model registry specific):** `GET /api/2.0/mlflow/registered-models/list` → `{"registered_models":[{"name":"...","creation_timestamp":...,"last_updated_timestamp":...,"latest_versions":[...]}]}` — `registered_models` array is the registry-specific signal distinct from basic tracking  
**Data Exposure Class (registry-specific):** Model names, versions, stages (Staging/Production), artifact URIs (s3://, gs://, azure:// paths — may contain bucket names and key prefixes), model signatures (input/output schema), tags and descriptions. Artifact paths can reveal cloud storage structure. Some deployments embed model serving endpoints in tags.  
**Known CVEs:** No MLflow-specific CVEs for the registry component in public databases; broader MLflow exposure is established (prior surveys). The primary risk is unauthenticated read/write of model registry — attacker can register a backdoored model version and promote it to Production stage without auth.  
**Default Credentials:** None.  
**Notes:** Prior surveys covered MLflow tracking. This entry focuses on the model registry surface specifically: the `/api/2.0/mlflow/registered-models/` endpoint family and artifact URI leakage. An exposed registry + write access is a model poisoning vector — register a malicious model, set stage=Production, wait for downstream serving infrastructure to pick it up. Also: `/api/2.0/mlflow/model-versions/get-download-uri` can yield presigned cloud storage URLs.

---

## Summary: Auth Posture by Platform

| Platform | Auth Default | Primary Risk |
|----------|-------------|--------------|
| OpenMetadata | on (bypassable < 1.3.1) | CVE-2024-28255 auth bypass + RCE chain |
| DataHub | off (GMS) / weak (frontend) | Unauthenticated GMS + JWT non-verification |
| Apache Atlas | default-creds (admin/admin) | Known creds → full Hadoop metadata |
| Amundsen | off | Full catalog read with no creds |
| Marquez | off | Full lineage graph with no creds |
| OpenLineage | off (Marquez backend) | Lineage read + write/poison |
| Great Expectations | off (when Data Docs served) | Schema/stats exposure |
| Monte Carlo | N/A (SaaS/outbound agent) | Not a Shodan target |
| Soda Core/Cloud | N/A (SaaS/outbound agent) | Not a Shodan target |
| Atlan | on (OAuth2) | Not a meaningful Shodan target |
| Collibra | on (default-creds Admin/Admin) | Enterprise governance posture exposed |
| CKAN | partial (reads open by design) | Dataset inventory + credential leak in resources |
| MLflow (registry) | off | Model registry read/write, artifact URI leak, model poisoning |

---

## Key Insight: Data Catalog as Reconnaissance Goldmine

An exposed data catalog reveals the entire organizational data inventory in a single API call:
- Every database that exists (names, hosts, ports, engines)
- Schema of every table (column names, types, PII tags)
- Lineage: which pipelines read/write which tables
- Ownership: who owns what data (personnel enumeration)
- Connection strings: in some platforms (OpenMetadata, Atlas), ingestion configs store full JDBC/connection URIs

This makes a single exposed OpenMetadata or DataHub instance worth more recon value than a dozen exposed databases individually — it's the map to the entire data estate.
