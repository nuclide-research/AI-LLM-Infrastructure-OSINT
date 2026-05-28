# Workflow Orchestration Platform OSINT — Pre-Survey Intelligence
**Date:** 2026-05-27  
**Purpose:** Tune dork queries, understand auth posture, identify verification probes, document data exposure classes before Shodan harvests.  
**Scope:** 16 platforms — workflow orchestration, data pipelines, ML orchestration.  
**Status:** Pre-survey. No active probing conducted.

---

## Temporal

**Category:** Workflow Orchestration / Data Pipeline  
**Default Ports:** 7233 (gRPC), 7243 (HTTP REST, v1.22+), 8080/8233 (Web UI)  
**Auth Default:** off  
**Shodan Dork (primary):** `port:7243 "buildIdBasedVersioning"`  
**Shodan Dork (secondary):** `http.title:"Temporal" port:8080`  
**Verification Probe:** `GET /api/v1/system-info` → 200 + `serverVersion` + `capabilities` fields  
**Data Exposure Class:** Full workflow execution history in plaintext (inputs/outputs/credentials), namespace list, task queue topology, worker hostnames  
**Known CVEs:** CVE-2026-5724 (streaming interceptor bypass), CVE-2025-14987 (namespace escape), CVE-2023-3485 (task token namespace escape)  
**Default Credentials:** none (no auth mechanism active)  
**Notes:** Auth requires OIDC provider + custom Go plugin — the `noopAuthorizer` is the compiled-in default. Path of least resistance is no auth. `ssl.cert.subject.cn:"temporal"` finds Temporal Cloud customers (auth-on), NOT self-hosted — wrong dork.

---

## Cadence (Uber)

**Category:** Workflow Orchestration / Data Pipeline  
**Default Ports:** 8088 (Web UI), 7833 (gRPC), 7933 (TChannel), 8800 (HTTP API v1.2+), 8001-8003 (Prometheus)  
**Auth Default:** off  
**Shodan Dork (primary):** `http.title:"Cadence" port:8088`  
**Shodan Dork (secondary):** `http.html:"cadenceClusters"` (v4 Next.js `__NEXT_DATA__` blob — distinctive)  
**Verification Probe:** `GET /api/v1/domains` → 200 + `domains` field  
**Data Exposure Class:** All workflow history, inputs/outputs, domain configuration, full write access (start/terminate/signal workflows)  
**Known CVEs:** none specific; dependency CVEs in v0.24/v1.2 release images  
**Default Credentials:** none (noop authorizer; `CADENCE_WEB_AUTH_STRATEGY=disabled`)  
**Notes:** Shodan population appears near-zero based on prior searches. The `cadenceClusters` dork has not been tried against the live index. `__NEXT_DATA__` blob in v4 UI is a distinctive signal with low collision probability.

---

## Netflix Conductor (conductor-oss)

**Category:** Workflow Orchestration / Data Pipeline  
**Default Ports:** 8080 (API server + Swagger), 5000 (UI v2 Express), 3000 (UI v3 React), 9200 (Elasticsearch)  
**Auth Default:** off  
**Shodan Dork (primary):** `http.title:"Conductor UI"`  
**Shodan Dork (secondary):** `port:8080 http.html:"ownerApp"` (unique Conductor JSON field)  
**Verification Probe:** `GET /api/metadata/workflow` → 200 + `ownerApp` + `tasks` fields  
**Data Exposure Class:** Workflow definitions with `ownerEmail`/task graphs, full task I/O history (credentials in HTTP task payloads), queue topology via `/api/tasks/queue/all`, CORS `*`  
**Known CVEs:** CVE-2020-9296 (CVSS HIGH — unauthenticated RCE via EL injection, pre-2.25.3)  
**Default Credentials:** none (security.enabled=false in Helm; no auth path without explicit IdP config)  
**Notes:** Netflix OSS archived December 2023. Lagging enterprise deployments may run pre-2.25.3 (RCE-vulnerable). 4 hosts confirmed in prior recon pass.

---

## Flyte

**Category:** Workflow Orchestration / Data Pipeline  
**Default Ports:** 8088 (FlyteAdmin HTTP), 8089 (FlyteAdmin gRPC), 30080 (sandbox all-in-one), 30084 (MinIO)  
**Auth Default:** off  
**Shodan Dork (primary):** `http.title:"Flyte Console"`  
**Shodan Dork (secondary):** `http.title:"Flyte Console" port:30080`  
**Verification Probe:** `GET /api/v1/version` → 200 + `controlPlaneVersion` field  
**Data Exposure Class:** Execution history + inputs/outputs, MinIO artifacts via hardcoded creds `minio`/`miniostorage`, K8s dashboard (`--enable-skip-login`), gRPC reflection ON  
**Known CVEs:** CVE-2022-39273 (hardcoded Propeller OAuth client secret)  
**Default Credentials:** MinIO: `minio` / `miniostorage`  
**Notes:** `flytectl demo start` launches full stack on port 30080 with zero security. Single probe confirms the entire exposure surface. `useAuth:false`, `secure:false`, `CORS allowedOrigins:*` are all explicit defaults across the stack.

---

## Mage.ai

**Category:** Workflow Orchestration / Data Pipeline  
**Default Ports:** 6789 (UI + API + WebSocket)  
**Auth Default:** off  
**Shodan Dork (primary):** `http.title:"Mage" port:6789`  
**Shodan Dork (secondary):** none  
**Verification Probe:** `GET /api/kernels` → 200 + `kernels` field = confirmed unauth RCE surface  
**Data Exposure Class:** Pipeline source code, execution history, secrets/env vars, interactive Jupyter kernel (RCE), terminal WebSocket (shell)  
**Known CVEs:** CVE-2025-2129 (insecure auth default, pre-0.9.78), CVE-2023-31143 (terminal auth bypass even when auth enabled), CVE-2024-45188/45189/45190 (path traversal chain)  
**Default Credentials:** none required — full access without credentials pre-v0.9.78  
**Notes:** CRITICAL-class exposure: unauth → RCE in one probe. 1,045 confirmed publicly accessible at CVE-2025-2129 disclosure. Kernel endpoint confirms the exposure; terminal WebSocket delivers the shell.

---

## ZenML

**Category:** Workflow Orchestration / Data Pipeline  
**Default Ports:** 8237 (UI + REST API)  
**Auth Default:** default-creds  
**Shodan Dork (primary):** `http.title:"ZenML" port:8237`  
**Shodan Dork (secondary):** none  
**Verification Probe:** `GET /api/v1/info` → 200 + `version` field (unauthenticated)  
**Data Exposure Class:** MLOps pipeline topology, artifact storage URIs (S3/GCS paths), service connector configs (AWS/GCP/Azure credentials), stack configurations  
**Known CVEs:** CVE-2024-25723 (Critical — account takeover via `/activate` endpoint), CVE-2024-2083 (Critical — path traversal via `logs` param: login as default/blank → read `/etc/passwd`)  
**Default Credentials:** username `default`, password `` (empty string)  
**Notes:** Empty-password default is auth-theater. Compound chain: `default`/blank login → CVE-2024-2083 path traversal. Service connector configs are the high-value target — they hold cloud provider credentials verbatim.

---

## Kestra

**Category:** Workflow Orchestration / Data Pipeline  
**Default Ports:** 8080 (UI + API), 8081 (management/health)  
**Auth Default:** off  
**Shodan Dork (primary):** `port:8080 http.title:"Kestra"`  
**Shodan Dork (secondary):** none  
**Verification Probe:** `GET /api/v1/flows` → 200 = open, 401 = auth configured  
**Data Exposure Class:** All workflow YAML (may contain hardcoded credentials), execution history, KV store (operators put secrets here), namespace files, unauthenticated execution trigger  
**Known CVEs:** none assigned; Docker socket mount as root in default compose = RCE → host escape  
**Default Credentials:** PostgreSQL password `k3str4` (hardcoded in default compose)  
**Notes:** All pre-v0.24.0 instances are fully open — `basic-auth: enabled: false` shipped explicitly in the distributed config. v0.24+ introduced mandatory setup wizard. Docker socket mount in default compose file creates workflow execution → host escape chain.

---

## Apache DolphinScheduler

**Category:** Workflow Orchestration / Data Pipeline  
**Default Ports:** 12345 (API + UI), 5678 (Master), 1234 (Worker), 50053 (Alert)  
**Auth Default:** default-creds  
**Shodan Dork (primary):** `port:12345 http.html:"/dolphinscheduler/ui"`  
**Shodan Dork (secondary):** none  
**Verification Probe:** `POST /dolphinscheduler/users/login` with `{"userName":"admin","userPassword":"dolphinscheduler123"}` → token  
**Data Exposure Class:** All datasource connection strings with plaintext passwords (MySQL/PostgreSQL/Hive/ClickHouse/Kafka), workflow definitions, execution history, SSRF via datasource connect-test endpoint  
**Known CVEs:** CVE-2024-43202 (CVSS 9.8 — unauthenticated RCE, fixed in 3.2.2), CVE-2023-48796 (actuator endpoints expose DB credentials without auth), CVE-2022-45875 (post-auth RCE via alert plugin), CVE-2023-49299 / CVE-2024-29831 (JS execution RCE chain)  
**Default Credentials:** `admin` / `dolphinscheduler123` (all versions, no forced rotation)  
**Notes:** CVE-2024-43202 = unauth RCE on versions < 3.2.2. Default creds + CVE-2024-43202 = one-step full compromise on unpatched instances. Datasource connect-test SSRF works post-auth with default creds.

---

## Windmill

**Category:** Workflow Orchestration / Data Pipeline  
**Default Ports:** 80 (Caddy reverse proxy, only external port), 8000 (internal server)  
**Auth Default:** default-creds  
**Shodan Dork (primary):** `http.title:"Windmill"`  
**Shodan Dork (secondary):** none  
**Verification Probe:** `GET /api/health` → 200 + `db` + `worker_count` fields (unauthenticated)  
**Data Exposure Class:** Script source code, job execution history with logs, resource definitions (DB connections, API configs)  
**Known CVEs:** CVE-2026-29059 (CVSS 10.0 — path traversal → RCE, no auth required; "Windfall" public exploit), CVE-2026-23696 (CVSS 9.4 — SQLi → privilege escalation), CVE-2026-47107 (CVSS 9.6 — sandbox escape → workspace takeover)  
**Default Credentials:** `admin@windmill.dev` / `changeme`; PostgreSQL password: `changeme`  
**Notes:** "Windfall" public exploit automates the CVE-2026-29059 chain with log deletion for cleanup. Community Edition (CE) sandbox disabled at compile time. Health endpoint is always open regardless of auth state.

---

## Restate

**Category:** Workflow Orchestration / Data Pipeline  
**Default Ports:** 9070 (admin API + Web UI), 8080 (HTTP ingress), 9071 (admin gRPC), 5122 (cluster management)  
**Auth Default:** off  
**Shodan Dork (primary):** `port:9070 http.html:"Restate"`  
**Shodan Dork (secondary):** `port:9070 http.html:"restatedev"`  
**Verification Probe:** `GET /services` on port 9070 → 200 + `services` field  
**Data Exposure Class:** Service catalog (all registered services + endpoints), complete invocation journal (inputs/outputs, retry history), K/V object state, workflow execution history, OpenAPI specs per service  
**Known CVEs:** none public  
**Default Credentials:** none (no auth mechanism documented anywhere on admin API or HTTP ingress)  
**Notes:** Auth is absent by design — network perimeter is the only documented protection. Admin API on 9070 is fully open with no credential path. No authentication mechanism exists in the codebase for this interface.

---

## Hatchet

**Category:** Workflow Orchestration / Data Pipeline  
**Default Ports:** 8080 (dashboard + API), 7077 (gRPC external), 8733 (health), 9090 (Prometheus), 5435 (PostgreSQL exposed), 15673 (RabbitMQ management UI)  
**Auth Default:** default-creds  
**Shodan Dork (primary):** `port:8080 http.html:"hatchet"`  
**Shodan Dork (secondary):** none  
**Verification Probe:** `GET /healthz` on port 8733 (unauthenticated)  
**Data Exposure Class:** Workflow definitions, run history (inputs/outputs), API tokens for all tenants, direct PostgreSQL access via port 5435  
**Known CVEs:** none public  
**Default Credentials:** `admin@example.com` / `Admin123!!`; RabbitMQ: `guest` / `guest`  
**Notes:** Default compose exposes PostgreSQL (5435) and RabbitMQ management (15673) to external interfaces. gRPC (7077) runs without TLS. Direct database access on 5435 with default PostgreSQL credentials bypasses application-layer auth entirely.

---

## Argo Workflows

**Category:** Workflow Orchestration / Data Pipeline  
**Default Ports:** 2746 (Argo Server UI + REST API — distinctive, near-zero port collision), 9090 (metrics, always unauth even on hardened instances)  
**Auth Default:** off  
**Shodan Dork (primary):** `port:2746 http.title:"Argo Workflows"`  
**Shodan Dork (secondary):** `port:2746 "argoproj"`  
**Verification Probe:** `GET /api/v1/userinfo` → 200 + `serviceAccountName` field = confirmed unauth (server mode)  
**Data Exposure Class:** Workflow parameters (API keys/credentials in inputs), artifact download (S3/GCS content proxied directly), workflow templates, container image paths, execution logs  
**Known CVEs:** CVE-2024-53862 (HIGH — archived workflow auth bypass on v3.5.7-3.5.12 / v3.6.0-3.6.1)  
**Default Credentials:** none required — quickstart ships `--auth-mode=server` which disables auth  
**Notes:** ~3,000 publicly accessible instances confirmed by E.V.A Security November 2024. In-wild cryptominer deployment via workflow submission documented. Port 9090 metrics always open regardless of auth configuration — secondary recon surface even on hardened instances. v3.0+ default changed to `client` mode but quickstart docs override it back to `server`.

---

## Kubeflow Pipelines

**Category:** Workflow Orchestration / Data Pipeline  
**Default Ports:** 8080 (ml-pipeline-ui), 8888 (API server HTTP), 80/443 (Istio IngressGateway)  
**Auth Default:** off  
**Shodan Dork (primary):** `http.title:"Kubeflow Central Dashboard"`  
**Shodan Dork (secondary):** `http.html:"ml-pipeline"`  
**Verification Probe:** `GET /pipeline/apis/v1beta1/runs` → 200 + `runs` field = open  
**Data Exposure Class:** Pipeline run parameters, artifact URIs (S3/GCS paths to models/datasets), pipeline definitions, MLMD provenance graph  
**Known CVEs:** no dedicated CVEs; Microsoft (2020) + Intezer (2021) documented in-wild exploitation for cryptomining  
**Default Credentials:** none (single-user standalone mode has no auth; multi-user relies on Istio RBAC which misconfiguration exposes)  
**Notes:** 617 confirmed hits on title dork in prior pass. Single-user standalone mode ships with zero auth. Multi-user mode is gated by Istio RBAC; the exposure path is `kubectl patch` to promote IngressGateway to LoadBalancer. Notebook server creation in an open instance gives arbitrary container execution.

---

## Dagster

**Category:** Workflow Orchestration / Data Pipeline  
**Default Ports:** 3000 (dagster-webserver), 4266 (gRPC code location — CVE-2025-51481)  
**Auth Default:** off  
**Shodan Dork (primary):** `http.html:"dagster_webserver_version"` (unique field, zero false positives)  
**Shodan Dork (secondary):** `http.title:"Dagster" port:3000`  
**Verification Probe:** `GET /server_info` → 200 + `dagster_webserver_version` field  
**Data Exposure Class:** `runConfigYaml` (DB connection strings + API keys in resource configs), full run history, asset materialization metadata, op-level logs (printed secrets), loaded code location structure  
**Known CVEs:** CVE-2025-51481 (Medium — LFI via gRPC notebook endpoint, `.ipynb` suffix bypass, up to 1.10.14)  
**Default Credentials:** none (auth absent in OSS; GitHub issue #2219 open since 2020-02-27, marked "decidedly low priority")  
**Notes:** `runConfigYaml` is the primary credential dump surface. A single GraphQL query for all run configs returns all resource credentials in one response. Auth is not a roadmap priority per maintainer statements. The gRPC code location port (4266) is a separate LFI surface via CVE-2025-51481.

---

## Prefect

**Category:** Workflow Orchestration / Data Pipeline  
**Default Ports:** 4200 (Prefect Server)  
**Auth Default:** off  
**Shodan Dork (primary):** `http.title:"Prefect Server"` (3.x); `http.title:"Prefect Orion"` (2.x)  
**Shodan Dork (secondary):** none  
**Verification Probe:** `POST /api/block_documents/filter` with `{"include_secrets":true}` → returns all stored credentials in plaintext  
**Data Exposure Class:** Flow run parameters (credentials passed as inputs), block documents (primary credential store with cloud keys/DB URIs/API tokens), variables, deployment configs, logs  
**Known CVEs:** none assigned; no-auth-by-default is a design decision  
**Default Credentials:** none required (2.x has no auth; 3.x added `PREFECT_SERVER_API_AUTH_STRING` but it is not set by default)  
**Notes:** Block documents with `include_secrets:true` is the single highest-value API call on an unauth Prefect instance. Returns all stored credentials verbatim. Dork `http.title:"Prefect Orion"` catches older 2.x deployments that never migrated branding.

---

## Apache Airflow

**Category:** Workflow Orchestration / Data Pipeline  
**Default Ports:** 8080 (webserver)  
**Auth Default:** on (with documented bypass patterns)  
**Shodan Dork (primary):** `http.title:"Airflow" port:8080`  
**Shodan Dork (secondary):** none  
**Verification Probe:** `GET /api/v1/health` → 200 (unauthenticated); then attempt bypass patterns  
**Data Exposure Class:** Connections tab = all DB URIs, AWS keys, SSH keys, OAuth tokens stored for DAG use; full DAG source code; execution history  
**Known CVEs:** CVE-2020-17526 (static `secret_key='temporary_key'` → forge session cookie), CVE-2020-13927 (CVSS 9.8 — experimental API `auth_backend=default` → fully open `/api/experimental/*`)  
**Default Credentials:** `admin` / `admin` or `admin` / `airflow` (common across older installs and dev deployments)  
**Notes:** 8 documented bypass patterns:
1. `AUTH_ROLE_PUBLIC='Admin'` in `webserver_config.py` → anonymous user = admin
2. CVE-2020-17526: static `secret_key='temporary_key'` → forge valid session cookie
3. CVE-2020-13927 (CVSS 9.8): experimental API `auth_backend=default` → `/api/experimental/*` fully open
4. `expose_config=True` → full `airflow.cfg` dump including `secret_key` and DB URI
5. Basic auth with default creds `admin`/`admin` or `admin`/`airflow`
6. Airflow 3.x SimpleAuthManager dev default (no setup wizard enforcement)
7. Misconfigured reverse proxy stripping auth headers
8. Forgotten `.htpasswd` entries or open `/admin` path on older deployments

CVE-2020-13927 operators who upgraded without editing `airflow.cfg` retain the fully-open experimental API regardless of webserver auth state.

---

*Generated: 2026-05-27. Pre-survey intelligence only. No active probing conducted against any target.*
