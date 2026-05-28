# Workflow Orchestration Platform — Shodan Query Catalog
_Generated: 2026-05-27 from pre-survey OSINT pass (16 platforms)_
_See: data/platform-intel/workflow-orchestration-osint-2026-05-27.md for full intel_

---

## Argo Workflows
**Auth default:** off (`--auth-mode=server` in quickstart; binary default is `client` but official docs override it)
**Exposure class:** Unauth workflow execution, arbitrary container exec, artifact download, credential plaintext in parameters

| Label | Query | Rationale | FP Risk |
|-------|-------|-----------|---------|
| primary | `port:2746 http.title:"Argo"` | Port 2746 is Argo-exclusive. Live page title is `"Argo"`, NOT `"Argo Workflows"` — docs/readthedocs sites use the longer form | Low |
| secondary | `port:2746 "argoproj"` | JS bundle string from argoproj GitHub org; locks to port | Low |
| cert-pivot | `ssl.cert.issuer.cn:"Argo Workflows"` | Default self-signed cert issuer on HTTPS deployments; Shodan-indexable, zero collision | Low |
| version-json | `"gitTag" "gitTreeState" "compiler" "platform"` | Unique field combination from `/api/v1/version` JSON; catches reverse-proxied instances without port lock | Low |
| html-anchor | `http.html:"assets/favicon/favicon-32x32.png" "noindex"` | Distinctive HTML body strings present in Argo UI; catches instances proxied on 80/443 | Low |
| identity-probe | `/api/v1/userinfo` → `serviceAccountName` non-empty | 200 + non-empty `serviceAccountName` = server mode (unauth) confirmed; empty `{}` = auth enforced | — |

**FP note:** `port:2746 http.title:"Argo Workflows"` is WRONG — hits readthedocs mirror sites, not live servers.

---

## Temporal (self-hosted only)
**Auth default:** off (`noopAuthorizer` compiled in; OIDC requires a custom Go plugin)
**Exposure class:** Full workflow execution history in plaintext, namespace topology, task queue structure, worker hostnames

| Label | Query | Rationale | FP Risk |
|-------|-------|-----------|---------|
| primary | `port:7243 "buildIdBasedVersioning"` | Unique capability field in `/api/v1/system-info` response; HTTP REST port added v1.22+, near-zero collision | Low |
| secondary | `port:7243 "serverVersion" "capabilities"` | Broader field pair, still unique to Temporal HTTP REST; catches any `system-info` response body indexed by Shodan | Low |
| port-only | `port:7243` | Port added in v1.22; distinctive but no body anchor — use to find un-indexed hosts | Med |
| web-ui | `http.title:"Temporal" port:8080 -ssl.cert.subject.cn:"temporal.io"` | Web UI title; excludes Temporal Cloud customer deployments (auth-on) which use temporal.io certs | Med |
| identity-probe | `/api/v1/system-info` → `buildIdBasedVersioning` field | Confirms self-hosted; field absent on Temporal Cloud proxy responses | — |

**FP note:** `ssl.cert.subject.cn:"temporal"` finds Temporal Cloud customers (auth-on, wrong target). Never use it for self-hosted surveys.

---

## Mage.ai
**Auth default:** off (pre-v0.9.78 — ~1,045 confirmed unauth at CVE-2025-2129 disclosure)
**Exposure class:** Pipeline source code, execution history, env vars, interactive Jupyter kernel (RCE), terminal WebSocket (shell)

| Label | Query | Rationale | FP Risk |
|-------|-------|-----------|---------|
| primary | `http.title:"Mage" port:6789` | Port 6789 is non-standard and Mage-specific; title anchor eliminates residual port collisions | Low |
| secondary | `port:6789 http.html:"mage-ai"` | Brand string embedded in JS bundle; catches instances where title differs | Low |
| port-only | `port:6789` | Low expected FP on this non-standard port; cast-wide before anchoring | Med |
| api-path | `http.html:"/api/kernels" port:6789` | Kernel API path reference in page source; surfaces instances where body indexing caught the API path | Low |
| identity-probe | `GET /api/kernels` → 200 + `kernels` field | Confirms unauth RCE surface — kernel endpoint = Jupyter execution plane open | — |

---

## Apache DolphinScheduler
**Auth default:** default-creds (`admin` / `dolphinscheduler123`, no forced rotation)
**Exposure class:** All datasource connection strings in plaintext, workflow definitions, execution history, SSRF via connect-test endpoint

| Label | Query | Rationale | FP Risk |
|-------|-------|-----------|---------|
| primary | `port:12345 http.html:"/dolphinscheduler/ui"` | Port 12345 + UI path anchor; path `/dolphinscheduler/` is unique to this project | Low |
| secondary | `port:12345 http.html:"dolphinscheduler"` | Broader path anchor; catches partial URL in source or API response | Low |
| title | `http.title:"DolphinScheduler" port:12345` | Page title match locked to default port | Low |
| brand-full | `port:12345 http.html:"Apache DolphinScheduler"` | Full branded name in page source; high confidence, low recall | Low |
| identity-probe | `POST /dolphinscheduler/users/login` with `admin`/`dolphinscheduler123` → token | Default creds confirmed; then `/dolphinscheduler/datasources/list` returns all datasource passwords | — |

**FP note:** Port 12345 is used by some game servers. Always require the `dolphinscheduler` HTML anchor — port alone is not sufficient.

---

## Flyte
**Auth default:** off (`useAuth:false`, `secure:false`, `CORS allowedOrigins:*` all explicit defaults)
**Exposure class:** Execution history + inputs/outputs, MinIO artifacts via hardcoded creds, K8s dashboard (`--enable-skip-login`)

| Label | Query | Rationale | FP Risk |
|-------|-------|-----------|---------|
| primary | `http.title:"Flyte Console"` | Unique page title across all ports; catches proxied instances with no port lock needed | Low |
| sandbox | `port:30080 http.title:"Flyte"` | Sandbox port 30080 is distinctive; `flytectl demo start` deploys full auth-off stack here | Low |
| version-field | `http.html:"flyteadmin"` | Appears in `/api/v1/version` response body; unique field name with no plausible collision | Low |
| production | `port:8088 http.html:"flyte"` | FlyteAdmin HTTP production port with brand anchor | Med |
| identity-probe | `GET /api/v1/version` → 200 + `controlPlaneVersion` field | Confirms open FlyteAdmin; then GET `/api/v1/executions` dumps all run inputs/outputs | — |

---

## ZenML
**Auth default:** default-creds (`default` / `` empty string — auth theater)
**Exposure class:** MLOps pipeline topology, artifact storage URIs, service connector configs with cloud provider credentials verbatim

| Label | Query | Rationale | FP Risk |
|-------|-------|-----------|---------|
| primary | `port:8237 http.title:"ZenML"` | Port 8237 is ZenML-specific; non-standard, very low FP | Low |
| port-only | `port:8237` | Port alone is distinctive enough; cast-wide first pass | Low |
| brand-anchor | `port:8237 http.html:"zenml"` | Brand string in page source; secondary confirmation | Low |
| api-path | `port:8237 http.html:"/api/v1/info"` | API path reference indexed from page source or docs; unique path | Low |
| identity-probe | `GET /api/v1/info` → 200 + `version` field (unauthenticated) | Version exposed without auth — use for CVE window classification; then authenticate as `default`/`""` | — |

**Auth note:** Empty-password default is not auth — login as `default`/`""` after fingerprinting, then enumerate service connectors for cloud credentials.

---

## Kestra
**Auth default:** off (pre-v0.24.0; `basic-auth: enabled: false` shipped explicitly in default config)
**Exposure class:** Workflow YAML with hardcoded credentials, execution history, KV store (operators store secrets here), unauthenticated execution trigger

| Label | Query | Rationale | FP Risk |
|-------|-------|-----------|---------|
| primary | `port:8080 http.title:"Kestra"` | Page title is unique; port 8080 is shared but title discriminates | Med |
| field-anchor | `port:8080 http.html:"taskRunList"` | Unique Kestra field in API responses indexed by Shodan; near-zero collision | Low |
| docker-ref | `http.html:"kestra/kestra"` | Docker image reference (`kestra/kestra`) sometimes appears in page source or error output | Low |
| api-path | `port:8080 http.html:"/api/v1/flows"` | Flow API path anchor in page source | Med |
| identity-probe | `GET /api/v1/flows` → 200 = pre-0.24 open; 401 = auth configured | Binary auth status check; then GET `/api/v1/namespaces` enumerates all namespace secrets | — |

**FP note:** Port 8080 is extremely crowded. `taskRunList` is the discriminating anchor — never ship a query without it or the title.

---

## Windmill
**Auth default:** default-creds (`admin@windmill.dev` / `changeme`)
**Exposure class:** Script source code, job execution history with logs, resource definitions (DB connections, API configs)

| Label | Query | Rationale | FP Risk |
|-------|-------|-----------|---------|
| primary | `http.title:"Windmill"` | Page title; Windmill serves on port 80 via Caddy so port-locking is less useful | Med |
| brand-domain | `http.html:"windmill.dev"` | Brand domain embedded in default config and UI source; specific to Windmill | Low |
| health-fields | `http.html:"worker_count" http.html:"windmill"` | Unique field from `/api/health` response + brand anchor; health endpoint is always open even on auth-enabled instances | Low |
| health-path | `http.html:"/api/health" http.html:"windmill"` | Health endpoint path reference in source + brand anchor | Low |
| identity-probe | `GET /api/health` → 200 + `db` + `worker_count` fields | Always unauthenticated regardless of auth state; confirms instance; then attempt `admin@windmill.dev`/`changeme` | — |

**FP note:** `http.title:"Windmill"` may catch wind energy dashboards. Always add an HTML anchor for production harvests.

---

## Restate
**Auth default:** off (no auth mechanism exists for admin API — network perimeter is the only documented protection)
**Exposure class:** Service catalog, complete invocation journal (inputs/outputs, retry history), K/V object state, OpenAPI specs per service

| Label | Query | Rationale | FP Risk |
|-------|-------|-----------|---------|
| primary | `port:9070 http.html:"Restate"` | Port 9070 is Restate admin API (distinctive); brand anchor in UI response body | Low |
| org-anchor | `port:9070 http.html:"restatedev"` | GitHub org name (`restatedev`) surfaces in service catalog responses and error pages | Low |
| port-only | `port:9070` | Port is distinctive; cast-wide first pass before body anchoring | Low |
| deployment-field | `port:9070 http.html:"deployments"` | `/deployments` endpoint response field indexed from body; unique in context of port 9070 | Low |
| identity-probe | `GET /deployments` on port 9070 → 200 + `deployments` field | Full unauth admin access confirmed; any hit = complete service catalog + invocation journal access | — |

---

## Hatchet
**Auth default:** default-creds (`admin@example.com` / `Admin123!!`; RabbitMQ: `guest`/`guest`)
**Exposure class:** Workflow definitions, run history with inputs/outputs, API tokens for all tenants, direct PostgreSQL access on port 5435

| Label | Query | Rationale | FP Risk |
|-------|-------|-----------|---------|
| primary | `port:8080 http.html:"hatchet"` | Brand string in dashboard source; port 8080 + anchor combo | Med |
| title | `port:8080 http.title:"Hatchet"` | Page title match; secondary confirmation | Med |
| rabbitmq-coloc | `port:15673 http.title:"RabbitMQ Management"` | Default compose maps RabbitMQ management to 15673 (from 15672); co-location fingerprint is distinctive — finding this port strongly suggests Hatchet stack nearby | Low |
| grpc-port | `port:7077 "hatchet"` | gRPC engine port without TLS in default compose; banner or body reference | Low |
| identity-probe | `GET /healthz` on port 8733 → 200 | Unauthenticated health endpoint confirms instance; then attempt `admin@example.com`/`Admin123!!` | — |

**Pivot note:** Any host with port 15673 open and RabbitMQ management title is a strong Hatchet co-location candidate. Also check port 5435 for direct PostgreSQL access with default credentials.

---

## Dagster
**Auth default:** off (auth absent in OSS since 2020; GitHub issue #2219 open since 2020-02-27, maintainer-labeled "decidedly low priority")
**Exposure class:** `runConfigYaml` field contains all DB connection strings and API keys; single GraphQL query dumps all run credentials

| Label | Query | Rationale | FP Risk |
|-------|-------|-----------|---------|
| primary | `http.html:"dagster_webserver_version"` | Unique field from `/server_info` JSON response; appears in Shodan body index; zero plausible collision | Low |
| graphql-type | `http.html:"DagsterRunStatus"` | GraphQL schema type unique to Dagster; surfaces in any page that includes schema introspection output | Low |
| title-port | `http.title:"Dagster" port:3000` | Page title + default port; broader, lower precision | Med |
| legacy | `http.html:"dagit_version"` | Legacy field name from pre-rename deployments (`dagit` was the old UI name) | Low |
| identity-probe | `GET /server_info` → 200 + `dagster_webserver_version` field | Confirms open instance; then POST `/graphql` with `{ runs { runConfigYaml } }` dumps all resource credentials | — |

---

## Netflix Conductor (conductor-oss)
**Auth default:** off (`security.enabled=false` in Helm; no auth path without explicit IdP config)
**Exposure class:** Workflow definitions with owner emails, full task I/O history (credentials in HTTP task payloads), queue topology

| Label | Query | Rationale | FP Risk |
|-------|-------|-----------|---------|
| primary | `http.title:"Conductor UI"` | Netflix OSS UI title; unique to Conductor | Low |
| v3-title | `http.title:"Workflow UI"` | conductor-oss v3+ renamed UI title | Med |
| owner-field | `port:8080 http.html:"ownerApp"` | Unique field in `/api/metadata/workflow` response; owner attribution field specific to Conductor schema | Low |
| express-ui | `port:5000 http.html:"Conductor" http.header:"X-Powered-By: Express"` | Express UI fingerprint on v2 UI port; Express header + brand anchor | Low |
| api-path | `http.html:"/api/metadata/workflow"` | API path reference indexed from page source | Med |
| identity-probe | `GET /api/metadata/workflow` → 200 + `ownerApp` field | Confirmed open; then check `/api/tasks/queue/all` for queue topology and `/api/workflow/{id}` for task I/O | — |

**CVE note:** CVE-2020-9296 = unauth RCE on versions < 2.25.3. Netflix OSS archived December 2023 — lagging deployments may still run vulnerable versions. Check Swagger UI at `/swagger-ui/index.html` for version disclosure.

---

## Cadence (Uber)
**Auth default:** off (`CADENCE_WEB_AUTH_STRATEGY=disabled`; `noop` authorizer default)
**Exposure class:** All workflow history, inputs/outputs, domain configuration, full write access (start/terminate/signal)

| Label | Query | Rationale | FP Risk |
|-------|-------|-----------|---------|
| primary | `port:8088 http.title:"Cadence"` | Web UI default port + title; port 8088 is distinctive for this | Low |
| next-data | `http.html:"cadenceClusters"` | v4 Next.js `__NEXT_DATA__` blob key — only appears in Cadence v4 UI page source; highest precision signal untested against live index | Low |
| brand-web | `port:8088 http.html:"cadence-workflow"` | Brand string from GitHub org in page source | Low |
| package-name | `port:8088 http.html:"cadence-web"` | npm package name embedded in v3 UI build artifacts | Low |
| identity-probe | `GET /api/v1/domains` → 200 + `domains` field | Confirms open; lists all workflow domains (equivalent to namespaces); then enumerate executions per domain | — |

**Population note:** Prior generic dork pass found 0 confirmed instances. `cadenceClusters` is an untested precision signal that may recover hidden population. Run it first.

---

## Kubeflow Pipelines
**Auth default:** off (single-user standalone mode has no auth; multi-user relies on Istio RBAC misconfiguration)
**Exposure class:** Pipeline run parameters, artifact URIs (S3/GCS paths), pipeline definitions, MLMD provenance graph

| Label | Query | Rationale | FP Risk |
|-------|-------|-----------|---------|
| primary | `http.title:"Kubeflow Central Dashboard"` | 617 confirmed hits in prior pass; high-precision title match | Low |
| ml-pipeline | `http.html:"ml-pipeline"` | Pipeline service reference; 8 hits in prior pass = maximum precision subset | Low |
| broad | `http.html:"kubeflow" port:8080` | Broader catch for deployments on non-standard ingress | Med |
| identity-probe | `GET /pipeline/apis/v1beta1/runs` → 200 + `runs` field | Single-user mode open confirmed; then POST `/pipeline/apis/v1beta1/runs` to enumerate full execution history | — |

---

## Prefect
**Auth default:** off (2.x: no auth; 3.x: `PREFECT_SERVER_API_AUTH_STRING` exists but not set by default)
**Exposure class:** Block documents (primary credential store — cloud keys, DB URIs, API tokens), flow run parameters, deployment configs

| Label | Query | Rationale | FP Risk |
|-------|-------|-----------|---------|
| primary-3x | `http.title:"Prefect Server" port:4200` | 3.x page title + default port; distinguishes from proxied/custom-title deployments | Low |
| primary-2x | `http.title:"Prefect Orion" port:4200` | 2.x codename title; catches older deployments that never migrated branding | Low |
| broad | `port:4200 http.html:"prefect"` | Port + brand anchor; catches instances with non-standard titles | Med |
| identity-probe | `POST /api/block_documents/filter` with `{"include_secrets":true}` | Single highest-value API call — returns all stored credentials verbatim; no auth required on open instances | — |

---

## Apache Airflow
**Auth default:** on (with 8 documented bypass patterns; CVE-2020-13927 is the highest-impact pre-auth bypass)
**Exposure class:** Connections tab = all DB URIs, AWS keys, SSH keys, OAuth tokens; DAG source code; full execution history

| Label | Query | Rationale | FP Risk |
|-------|-------|-----------|---------|
| primary | `http.title:"Airflow" port:8080` | Standard title + default port combination | Med |
| dag-anchor | `port:8080 http.html:"dag-runs" http.html:"airflow"` | DAG-specific field name + brand anchor; narrows to instances where API response is indexed | Low |
| expose-config | `http.html:"Airflow Configuration" port:8080` | `expose_config=True` instances — full `airflow.cfg` dump accessible (includes `secret_key` and DB URI) | Low |
| experimental-api | `port:8080 http.html:"/api/experimental"` | CVE-2020-13927 surface — experimental API path in page source; operators who upgraded without editing config retain the fully-open endpoint | Low |
| identity-probe | `GET /api/v1/health` → 200 (unauthenticated) | Health endpoint always open; then attempt bypass patterns in order: default creds → static `secret_key` session forge → experimental API → `AUTH_ROLE_PUBLIC='Admin'` | — |

**Bypass priority order:** (1) `admin`/`admin` or `admin`/`airflow` default creds; (2) CVE-2020-13927 `/api/experimental/` fully open; (3) CVE-2020-17526 static `secret_key='temporary_key'` → session cookie forge; (4) `expose_config=True` → full config dump.
