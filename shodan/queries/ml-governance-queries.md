# ML Governance / Data Catalog — Shodan Query Catalog
_Generated: 2026-05-27 from pre-survey OSINT pass (13 platforms)_
_See: data/platform-intel/ml-governance-osint-2026-05-27.md for full intel_

---

## OpenMetadata

**Auth default:** on — but CVE-2024-28255 (CVSS 9.8) allows auth bypass on all versions < 1.3.1; exploited in wild against Kubernetes clusters
**Exposure class:** Full data catalog — table schemas, PII tags, database connection metadata, pipeline lineage, env vars with credentials on compromised container

| Label | Query | Rationale | FP Risk |
|-------|-------|-----------|---------|
| primary | `http.title:"OpenMetadata" port:8585` | Default port + page title unique to OpenMetadata | Low |
| secondary | `http.html:"open-metadata" port:8585` | HTML class/asset paths contain `open-metadata` | Low |
| tertiary | `html:"openmetadata" port:8585` | Broader catch for customized installs | Low-Med |
| k8s-variant | `http.html:"openmetadata" port:8080` | Some K8s ingress rewrites on 8080 | Med |
| identity-probe | `GET /api/v1/system/version` → `{"version":"...","revision":"..."}` | Unauthenticated version disclosure; confirms identity | — |
| bypass-probe | `GET /api/v1/tables;v1=x/` → 200 | Path param injection — confirms pre-1.3.1 vulnerable instance | — |

---

## DataHub (LinkedIn)

**Auth default:** off on GMS backend (port 8080) by default; frontend accepts datahub/datahub; JWT not cryptographically verified even when auth "enabled"
**Exposure class:** Full org data inventory — all database entities, table/column lineage, ownership maps, PII classification, ingestion source configs

| Label | Query | Rationale | FP Risk |
|-------|-------|-----------|---------|
| primary | `http.title:"DataHub" port:9002` | Frontend UI title unique to DataHub | Low-Med |
| secondary | `http.html:"datahubproject" port:9002` | React bundle contains datahubproject references | Low |
| gms-direct | `port:8080 http.html:"datahub-gms"` | GMS container banner/health endpoint | Med |
| gms-restli | `port:8080 "X-RestLi-Protocol-Version"` | Distinctive Rest.li header emitted by GMS | Low |
| identity-probe-ui | `GET /authenticate` with `datahub/datahub` → session cookie | Confirms default creds on frontend | — |
| identity-probe-gms | `GET /config` on port 8080 → JSON with `"noCode"` field | Unauthenticated GMS config endpoint | — |
| gms-entity | `GET /entities?urns[0]=urn:li:corpuser:datahub` on 8080 → entity JSON | Confirms unauth GMS access | — |

---

## Apache Atlas

**Auth default:** default-creds (admin/admin) — no unauthenticated access, but creds are universally known and rarely changed
**Exposure class:** Full Hadoop/big data inventory — Hive tables, HDFS paths, HBase, Kafka topics, Spark jobs, PII classification, entity lineage

| Label | Query | Rationale | FP Risk |
|-------|-------|-----------|---------|
| primary | `port:21000 http.title:"Atlas"` | Port 21000 is nearly exclusive to Apache Atlas | Low |
| secondary | `port:21000 html:"Apache Atlas"` | Page content contains Apache Atlas branding | Low |
| api-path | `http.html:"/api/atlas/v2" port:21000` | API path in HTML links/JS confirms Atlas | Low |
| https-variant | `port:21443 http.title:"Atlas"` | HTTPS variant (SSL enabled deployments) | Low |
| identity-probe | `GET /api/atlas/admin/version` with `-u admin:admin` → `{"Description":"Metadata Management...","Version":"2.x.x"}` | Default creds confirm; `Description` field unique | — |
| entity-dump | `GET /api/atlas/v2/search/basic?typeName=hive_table` with admin:admin → returns table inventory | Data access confirmation | — |

---

## Amundsen (Lyft)

**Auth default:** off — auth is entirely absent unless flaskoidc manually configured for all three microservices
**Exposure class:** Table/column metadata, ownership, PII tags, table statistics, data lineage — full catalog read without credentials

| Label | Query | Rationale | FP Risk |
|-------|-------|-----------|---------|
| primary | `http.title:"Amundsen" port:5000` | Title match on frontend port | Med (port 5000 busy) |
| secondary | `http.html:"amundsen" port:5000` | HTML body contains `amundsen` class names | Med |
| multi-port | `http.html:"amundsen" port:5001` | Search service port — less FP noise | Low-Med |
| identity-probe | `GET /healthcheck` on 5001 and 5002 → `{"status":"ok"}` | Confirms metadata + search services running | — |
| data-probe | `GET /api/metadata/v0/table_detail/<table_key>` → table JSON | Confirms unauthenticated catalog read | — |

---

## Marquez (OpenLineage)

**Auth default:** off — documented as having no auth by default
**Exposure class:** Full pipeline lineage graph — job names, dataset names, run history, SQL queries in facets, schema snapshots, connection URIs in OpenLineage facets

| Label | Query | Rationale | FP Risk |
|-------|-------|-----------|---------|
| primary | `http.html:"marquez" port:5000` | HTML references Marquez on default port | Med (port 5000 busy) |
| secondary | `http.html:"marquezproject" port:5000` | More specific — MarquezProject branding | Low |
| ui-port | `http.html:"openlineage" port:3000` | UI on port 3000 with OpenLineage references | Med |
| jar-variant | `http.html:"marquezproject" port:8080` | Java jar deployment on 8080 | Med |
| graphql | `http.html:"graphql-playground" port:5000 html:"marquez"` | GraphQL playground is a distinctive co-signal | Low |
| identity-probe | `GET /api/v1/namespaces` → `{"namespaces":[{"name":"...","createdAt":"..."}]}` | Unauthenticated; `namespaces` array unique to Marquez | — |
| lineage-read | `GET /api/v1/jobs?namespace=<name>` → job list with run history | Confirms full lineage access | — |

---

## OpenLineage (Ecosystem)

**Auth default:** depends on server — Marquez (off), Airflow transport (inherits Airflow auth)
**Exposure class:** Pipeline topology, dataset schemas, job runs, SQL query text in facets

| Label | Query | Rationale | FP Risk |
|-------|-------|-----------|---------|
| primary | `http.html:"openlineage" port:5000` | OpenLineage server (Marquez) on 5000 | Med |
| airflow-variant | `http.html:"openlineage" port:8080` | Airflow with OpenLineage integration | High (Airflow also on 8080) |
| identity-probe | `POST /api/v1/lineage` with minimal OpenLineage event → 201 | Confirms write access to lineage store | — |

---

## Great Expectations

**Auth default:** off when Data Docs are served externally; library mode has no server
**Exposure class:** Validation results, expectation suite definitions, column statistics, null rates, value distributions — schema fingerprint of all profiled datasets

| Label | Query | Rationale | FP Risk |
|-------|-------|-----------|---------|
| primary | `http.html:"great_expectations" port:5000` | CSS class name unique to GX Data Docs | Med (port 5000) |
| secondary | `http.title:"Data Docs" http.html:"great_expectations"` | Title + class combo narrows FP | Low |
| any-port | `http.html:"great_expectations"` | Catch deployments on 80/443 via proxy | Med |
| identity-probe | `GET /` → HTML with `great_expectations` in `<link>` or `<script>` tags | Confirms GX Data Docs page | — |

---

## Monte Carlo

**Auth default:** N/A — SaaS only; no self-hosted server
**Exposure class:** Not applicable

_Not a Shodan target. Monte Carlo agent is outbound-only. Skip._

---

## Soda Core / Soda Cloud

**Auth default:** N/A — SaaS; self-hosted agent is outbound-only
**Exposure class:** Not applicable

_Not a Shodan target. Soda Agent listens on no public port. Skip._

---

## Atlan

**Auth default:** on (OAuth2) — SaaS primary; self-deployed runtime is outbound worker only
**Exposure class:** Not applicable for survey purposes

_Not a meaningful Shodan target. Self-deployed runtime is a Kubernetes worker pod with no inbound listener._

---

## Collibra

**Auth default:** on — default creds `Admin/Admin` documented; session-based auth enforced at login
**Exposure class:** Full enterprise data governance inventory — all data assets, business glossary, lineage policies, PII rules, stewardship assignments

| Label | Query | Rationale | FP Risk |
|-------|-------|-----------|---------|
| primary | `port:4402 http.html:"Collibra"` | Console port distinctive; Collibra in HTML | Low |
| secondary | `port:4402 http.title:"Collibra"` | Title match on console UI port | Low |
| search-api | `port:4421 http.html:"collibra"` | Search REST API port | Low |
| agent-port | `port:4401 http.html:"collibra"` | Agent port — less likely public-facing | Low |
| identity-probe | `POST /rest/2.0/auth/sessions` `{"username":"Admin","password":"Admin"}` → session cookie | Default creds; `JSESSIONID` confirms auth | — |
| data-probe | `GET /rest/2.0/assets` with session → asset list | Confirms full governance inventory access | — |

---

## CKAN

**Auth default:** partially open by design — read operations unauthenticated; write requires API token
**Exposure class:** Full dataset inventory, organization structure, resource URLs (may embed API keys/tokens in dataset records), public government data catalogs

| Label | Query | Rationale | FP Risk |
|-------|-------|-----------|---------|
| primary | `http.html:"ckan" port:5000` | Development server on 5000 with CKAN in HTML | Med |
| secondary | `http.html:"/api/3/action" http.html:"ckan"` | API path reference in HTML unique to CKAN | Low |
| prod-80 | `http.title:"CKAN" port:80` | Production on 80 via proxy | Med |
| version-field | `http.html:"ckan_version"` | `ckan_version` field in API response HTML/JSON | Low |
| identity-probe | `GET /api/3/action/status_show` → `{"success":true,"result":{"ckan_version":"...","site_title":"..."}}` | Unauthenticated; `ckan_version` is definitive | — |
| dataset-dump | `GET /api/3/action/package_list` → full dataset name list | Unauthenticated enumeration of entire catalog | — |

---

## MLflow (Model Registry — registry-specific gaps)

**Auth default:** off — no auth unless explicitly configured with auth plugin; default server exposes registry read/write
**Exposure class:** Model names, versions, stages (Staging/Production), artifact URIs (s3://, gs://, azure:// paths), model signatures — model poisoning vector via unauthenticated registry write

| Label | Query | Rationale | FP Risk |
|-------|-------|-----------|---------|
| primary | `http.html:"registered-models" port:5000` | Model registry UI contains this string | Low-Med |
| secondary | `http.html:"/api/2.0/mlflow/registered-models" port:5000` | API path in UI JS references | Low |
| ui-registry | `http.title:"MLflow" http.html:"Model Registry" port:5000` | UI page title + registry tab | Low |
| identity-probe | `GET /api/2.0/mlflow/registered-models/list` → `{"registered_models":[...]}` | Registry-specific endpoint; array key unique to MLflow registry | — |
| artifact-leak | `GET /api/2.0/mlflow/model-versions/get-download-uri?name=<model>&version=1` → presigned URI | Cloud storage URI exposure — s3:// bucket enumeration | — |
| write-probe | `POST /api/2.0/mlflow/registered-models/create` with `{"name":"test"}` → 200 | Confirms unauthenticated write = model poisoning possible | — |

---

## Priority Ranking for Harvest

| Rank | Platform | Reason |
|------|----------|--------|
| 1 | OpenMetadata | CVE-2024-28255 actively exploited; auth bypass confirmed; high K8s prevalence |
| 2 | DataHub | GMS auth off by default; JWT non-verification even when "on"; LinkedIn pedigree = widespread enterprise use |
| 3 | Apache Atlas | Famous default creds; Hadoop ecosystem ubiquity; high-value targets |
| 4 | Marquez | No auth documented; full lineage graph exposed; growing OpenLineage adoption |
| 5 | Amundsen | No auth by default; full catalog read; Lyft-influenced orgs |
| 6 | MLflow (registry) | Auth off by default; model poisoning vector; prior surveys show large Shodan population |
| 7 | CKAN | Massive government deployment footprint; read is open by design; credential leak in resources |
| 8 | Collibra | Low population but extremely high-value enterprise targets |
| 9 | Great Expectations | Low population; exposure only when Data Docs served externally |
| — | Monte Carlo | Not a Shodan target |
| — | Soda Core/Cloud | Not a Shodan target |
| — | Atlan | Not a Shodan target |
