# ML Experiment Tracking Platform OSINT — Pre-Survey Intelligence
**Date:** 2026-05-27
**Purpose:** Tune dork queries, understand auth posture, identify verification probes, document data exposure classes before Shodan harvests.
**Scope:** 12 platforms — ML experiment tracking, hyperparameter optimization, model comparison dashboards, distributed training management.
**Status:** Pre-survey. No active probing conducted.

---

## Weights & Biases (W&B) Local / wandb/local

**Category:** Experiment Tracker / Full MLOps Platform
**Default Ports:** 8080 (HTTP); 8082 (secondary service in some deployments)
**Auth Default:** on — requires API key (`WANDB_API_KEY`) and `wandb login --host=http://...`
**Shodan Dork (primary):** `http.title:"Weights & Biases" port:8080`
**Shodan Dork (secondary):** `http.html:"wandb" port:8080`
**Verification Probe:** `GET /api/v1/users/me` with `Authorization: Basic <base64(api_key:)>` → 200 + `entity` field
**Data Exposure Class:** Experiment runs, model weights artifacts, API keys stored in run configs, training hyperparameters, evaluation metrics, dataset references
**Known CVEs:** None specific to wandb/local server; production license required for SSO/access controls
**Default Credentials:** None — initial setup requires explicit API key generation
**Notes:** Docker image `wandb/local` ships without production controls by default; described as "not appropriate for production." SSL termination must be external. FP risk: any generic web app on 8080 could superficially match `http.html:"wandb"` — narrow with `http.title`. The `/static/` path structure is branded but generic-looking; API endpoint at `/api/v1/` is more distinctive. Older `vwxyzjn/local` image variant also in use.

---

## ClearML Self-Hosted

**Category:** Experiment Tracker / MLOps Platform
**Default Ports:** 8080 (Web UI), 8008 (API server), 8081 (File server)
**Auth Default:** off by default — ships with "free access" login that is "inherently unsecure" per vendor documentation; auth must be explicitly enabled. File server token auth added in v1.16.0.
**Shodan Dork (primary):** `http.title:"ClearML" port:8080`
**Shodan Dork (secondary):** `http.html:"clearml" port:8008`
**Verification Probe:** `GET /api/v2.*/system.company_info` on port 8008 → 200 + `company_name` field; `GET /auth.login` accepts `Basic <base64(key:secret)>` with default keys
**Data Exposure Class:** Full experiment metadata, model files via file server (8081), training artifacts, dataset versions, hyperparameter sweeps, pipeline DAGs, queue contents
**Known CVEs:** No dedicated CVEs; exposure is auth-configuration class. CVE-2025-14847 (MongoBleed) affects the MongoDB backend if port 27017 is exposed separately — unauthenticated heap memory leak of cleartext credentials, API keys, session tokens.
**Default Credentials:** Default API server ships with hardcoded default user keys/secrets in `apiserver.conf` (`default_key`/`default_secret`) — must be rotated for production
**Notes:** Auth-off-by-default makes this a high-yield survey target. API versioning uses `/api/v2.X/` pattern on port 8008. ClearML was previously "Trains" — some banners may reflect old branding. Port 8008 is the most distinctive signal: the combination of API traffic on a non-standard port is a cleaner Shodan signal than the web UI on 8080. Elasticsearch and Redis are internal-only by default; MongoDB exposure via port 27017 is a secondary risk path.

---

## Comet ML Self-Hosted (Comet Enterprise / Comet Server)

**Category:** Experiment Tracker / Model Evaluation
**Default Ports:** 5000 (primary web + API); may vary in enterprise
**Auth Default:** default-creds — default username and password are both `admin` (changed in versions ≥ 24.9.8); older deployments have plaintext `admin:admin`
**Shodan Dork (primary):** `http.title:"Comet" port:5000`
**Shodan Dork (secondary):** `http.html:"comet-ml" port:5000`
**Verification Probe:** `GET /api/v2/experiment` → 200 + `experiment_key` field; or `GET /healthcheck` → `{"status":"ok"}`
**Data Exposure Class:** Experiment runs, model evaluation results, dataset versions, API keys in user profiles, code snapshots, hyperparameters
**Known CVEs:** No dedicated CVEs on public record; default-creds class is the primary risk
**Default Credentials:** `admin:admin` (pre-24.9.8 deployments); passwords stored as MD5 — weak at-rest protection
**Notes:** Comet Backup (cometbackup.com) is a completely different product — same brand, different company. Filter FPs by looking for `/api/v2/` paths and ML-specific terms. No SSL required to start — HTTP deployments are common. Comet also ships "Opik" (LLM observability tool, separate product), which may appear on same hosts with auth disabled by default (GitHub issue #976 confirms auth is optional in Opik).

---

## Neptune.ai Self-Hosted

**Category:** Experiment Tracker / Model Registry
**Default Ports:** 30080 (NodePort via embedded ingress controller, K8s deployments); 80/443 behind external LB
**Auth Default:** on — uses Keycloak as identity management; admin username/password configured at install time
**Shodan Dork (primary):** `http.html:"neptune" port:30080`
**Shodan Dork (secondary):** `http.title:"Neptune" port:30080`
**Verification Probe:** `GET /api/experiments` with `X-nephele-api-token: <token>` → 200; Keycloak login page at `/auth/` confirms identity
**Data Exposure Class:** Experiment metadata, model versions, dataset references, API tokens, training metrics
**Known CVEs:** No dedicated CVEs; Keycloak auth layer means exposure requires misconfigured Keycloak or token leakage
**Default Credentials:** Keycloak admin credentials set at install time; no hardcoded defaults documented
**Notes:** NodePort 30080 is a niche signal — few other services use this port combination. K8s-deployed instances exposed directly (misconfigured NodePort) skip the ingress LB entirely. Keycloak at `/auth/` is a secondary confirmation signal. Low expected population due to enterprise-only self-hosted model; worth running but expect low hit counts.

---

## Aim (aimhubio/aim)

**Category:** Experiment Tracker (Lightweight, Open Source)
**Default Ports:** 43800 (UI server via `aim up`); 53800 (remote tracking server via `aim server`)
**Auth Default:** off — no authentication mechanism in the default deployment; SSL optional via `--ssl-keyfile`/`--ssl-certfile` flags
**Shodan Dork (primary):** `port:43800 http.html:"aim"`
**Shodan Dork (secondary):** `port:43800 "Aim"`
**Verification Probe:** `GET /api/runs/search/run` → 200 + JSON array of run objects; `GET /api/projects` → 200 + `name` field
**Data Exposure Class:** All experiment runs, metrics timeseries, training code, hyperparameters, system metrics (CPU/GPU/memory during training), custom metadata
**Known CVEs:** No CVEs on record; security model relies entirely on network isolation
**Default Credentials:** None — no auth layer
**Notes:** Port 43800 is highly distinctive — almost nothing else uses it. Aim's REST API is fully open with no auth. Docker image `aimstack/aim` starts with `0.0.0.0` binding by default in container context. The remote tracking server on 53800 accepts arbitrary metric writes from any client — data integrity risk alongside confidentiality. Low FP risk on port 43800.

---

## DVCLive + DVC Studio Self-Hosted

**Category:** Experiment Tracker (DVCLive) + ML Collaboration Dashboard (DVC Studio)
**Default Ports:** 80/443 via ingress (K8s Helm deployment); internal services on 3000 (UI), 5000 (API), 8000 (worker)
**Auth Default:** on — Studio self-hosted requires OAuth/SSO configuration via `values.yaml`; auth is not optional in the Helm chart
**Shodan Dork (primary):** `http.html:"iterative" http.html:"studio"`
**Shodan Dork (secondary):** `http.title:"Studio" http.html:"dvc"`
**Verification Probe:** `GET /api/user` → redirect to OAuth provider confirms identity; login page with "Sign in with GitHub/GitLab" is distinctive
**Data Exposure Class:** Experiment metadata, model metrics, dataset versions, git commits tied to runs, pipeline configs
**Known CVEs:** None on record
**Default Credentials:** None — OAuth/SSO required, no local auth fallback documented
**Notes:** Lowest standalone risk in this category — auth is on by default and OAuth-gated. Exposed instances would be misconfiguration-class rather than default-open. DVCLive itself is a local-only library with no server component. Population likely small; enterprise-focused. FP risk moderate — `http.html:"studio"` alone is very broad.

---

## Determined.ai (HPE Machine Learning Development Environment)

**Category:** Distributed Training Platform / Experiment Tracker / HPO
**Default Ports:** 8080 (HTTP, master); 8443 (HTTPS/TLS, if enabled)
**Auth Default:** default-creds — admin user exists by default with username `admin` and **blank password**; documentation explicitly states admin must set a strong password post-install
**Shodan Dork (primary):** `http.title:"Determined" port:8080`
**Shodan Dork (secondary):** `http.html:"Determined" port:8080`
**Verification Probe:** `GET /api/v1/auth/login` POST `{"username":"admin","password":""}` → 200 + `token` field; `GET /api/v1/experiments` unauthenticated on fresh deployments returns 200
**Data Exposure Class:** Distributed training jobs, model checkpoints, hyperparameter search results, GPU cluster topology, SSH key configurations, notebook contents, training code
**Known CVEs:** No CVEs on public record; admin/blank-password default is an untracked configuration-class finding. Communication is unencrypted by default (no TLS unless explicitly configured).
**Default Credentials:** `admin:` (admin with blank password)
**Notes:** This is a high-value target — admin/blank-password on a distributed GPU training cluster means access to all training jobs, model checkpoints, and potentially cloud credentials used for storage. `http.title:"Determined"` already has 60 confirmed hits in the existing survey catalog (see `04-training-experiments.md`). The API is REST at `/api/v1/`; job submission, checkpoint access, and agent management are all available once authenticated. HPE acquired Determined AI in 2021; enterprise deployments add SAML/SCIM but community editions retain the default.

---

## Guild AI

**Category:** Experiment Tracker (Lightweight, Local-First)
**Default Ports:** No server component — Guild AI runs as a local CLI tool; no persistent web server by default
**Auth Default:** N/A — local filesystem only in standard deployment
**Shodan Dork (primary):** N/A — no network-exposed server component
**Shodan Dork (secondary):** N/A
**Verification Probe:** N/A
**Data Exposure Class:** Local experiment runs, operation configs, metrics (only if manually shared/exported)
**Known CVEs:** None
**Default Credentials:** N/A
**Notes:** Guild AI is a pure-CLI local tool (Apache 2.0 license). No built-in server, no web UI, no network listener. Not a Shodan survey target. Guild AI (guildai.com/guildai) should not be confused with the separate "Guild.ai" (guild.ai) which is an AI agent control plane — different product, different company. Population = 0 expected on Shodan.

---

## Sacred + Omniboard

**Category:** Experiment Tracker (Sacred) + Dashboard (Omniboard)
**Default Ports:** 9000 (Omniboard Docker default); 27017 (MongoDB backend)
**Auth Default:** off — Omniboard ships with no authentication; vendor documentation confirms "there are plenty of Omniboard instances exposed on the Internet"
**Shodan Dork (primary):** `http.title:"Omniboard" port:9000`
**Shodan Dork (secondary):** `port:9000 http.html:"omniboard"`
**Verification Probe:** `GET /api/v1/Metrics` → 200 + JSON array; `GET /api/v1/Runs` → run list with source code fields
**Data Exposure Class:** Experiment source code (captured at run time), hyperparameters, metrics, configuration snapshots, MongoDB connection strings (sometimes hardcoded in source snapshots), model artifacts
**Known CVEs:** CVE-2025-14847 (MongoBleed) — affects MongoDB backend if port 27017 is accessible; unauthenticated remote attacker can leak heap memory containing cleartext credentials, API keys, session tokens. Affects MongoDB Server < 8.0.11 / 7.0.19 / 6.0.22.
**Default Credentials:** None for Omniboard UI (no auth); MongoDB default is often `localhost:27017:sacred` with no credentials
**Notes:** Omniboard's source code exposure is the distinctive risk — Sacred captures the full Python source of each experiment at run time. These captures frequently contain hardcoded credentials to databases, cloud storage, and APIs. The Omniboard → MongoDB chain means the web dashboard is the access vector but the MongoDB backend is the data store — check for port 27017 co-exposure on same host. Sacred is largely abandoned; low active development since 2021.

---

## Optuna Dashboard

**Category:** Hyperparameter Optimization Dashboard
**Default Ports:** 8080 (default; `--host 127.0.0.1` by default — localhost only)
**Auth Default:** off — no authentication mechanism; default host binding is localhost but container/cloud deployments routinely bind to 0.0.0.0
**Shodan Dork (primary):** `http.title:"Optuna Dashboard" port:8080`
**Shodan Dork (secondary):** `http.html:"optuna" port:8080`
**Verification Probe:** `GET /api/studies` → 200 + JSON array of study objects with `study_name`, `directions`, `n_trials` fields
**Data Exposure Class:** HPO study configurations, all trial hyperparameters and objective values, best trial parameters, sampler configurations, optimization history
**Known CVEs:** None — wsgiref (default WSGI server) is explicitly noted as not production-safe; Gunicorn/uWSGI recommended
**Default Credentials:** None
**Notes:** Default `--host 127.0.0.1` means locally run instances are not exposed; exposure occurs when deployed in containers without explicit host restriction or behind a reverse proxy. Storage backends include SQLite (common in research), MySQL, and PostgreSQL — connection strings sometimes visible in dashboard config. FP risk: port 8080 is extremely common. `http.title:"Optuna Dashboard"` is distinctive enough to keep FP risk low.

---

## Ray Dashboard (Ray Tune)

**Category:** Distributed Computing Dashboard / HPO (Ray Tune) / Model Serving (Ray Serve)
**Default Ports:** 8265 (dashboard); 10001 (Ray Client API); 6379 (Redis/GCS); 8076/8077 (Ray Serve)
**Auth Default:** off — no built-in authentication or authorization; explicitly documented as providing "read and write access to the Ray Cluster"
**Shodan Dork (primary):** `http.html:"ray dashboard" port:8265`
**Shodan Dork (secondary):** `port:8265 http.html:"ray"`
**Verification Probe:** `GET /api/jobs/` → 200 + JSON job list; `GET /nodes?view=summary` → node topology including SSH public keys
**Data Exposure Class:** Running job details, distributed task metadata, actor states, cluster GPU/CPU topology, system metrics, log files via path traversal, AWS/GCP IAM credentials via SSRF to metadata endpoints
**Known CVEs:**
- CVE-2023-48022 — Missing auth on `/api/jobs/` (port 8265 + 10001): unauthenticated job submission/deletion/enumeration. CVSS 9.8.
- CVE-2023-48023 — SSRF via `/log_proxy?url=` on port 8265: proxy arbitrary HTTP, fetch AWS instance metadata (169.254.169.254) for IAM credentials. Unauthenticated.
- CVE-2023-6021 — Path traversal via `/api/v0/logs/file?filename=` on port 8265: arbitrary filesystem read including SSH private keys. Unauthenticated. Requires `node_id` obtainable from `/nodes?view=summary`.
- CVE-2026-32981 — Additional advisory (2026).
**Default Credentials:** None — no auth layer at all
**Notes:** This is the highest-severity target in this catalog. CVE-2023-48022 (ShadowRay) is actively exploited in the wild. Ray patch in 2.8.1 addressed SSRF and path traversal but authentication remains unsupported — exposure is architectural, not patch-addressable without external controls. `http.html:"ray dashboard"` has 54 confirmed hits per existing survey catalog. SSRF to 169.254.169.254 on cloud-hosted instances produces IAM credential access — direct path to cloud account compromise. Any Ray dashboard on the public internet should be treated as compromised.

---

## SigOpt Self-Hosted

**Category:** Hyperparameter Optimization / Experiment Optimization
**Default Ports:** 443/80 (HTTPS/HTTP); internal services vary
**Auth Default:** on — SigOpt self-hosted is an enterprise product; auth required; no public documentation of unauthenticated access paths
**Shodan Dork (primary):** `http.html:"sigopt" http.title:"SigOpt"`
**Shodan Dork (secondary):** `http.html:"sigopt.com" port:443`
**Verification Probe:** `GET /api/v1/experiments` with `Authorization: Basic <base64(api_token:)>` → 200 or 401 confirms presence
**Data Exposure Class:** HPO experiments, observation results, parameter configurations, model performance data
**Known CVEs:** None on public record; Intel acquired SigOpt in 2020; Intel-maintained CVE surface
**Default Credentials:** None documented; enterprise provisioned
**Notes:** SigOpt self-hosted is effectively discontinued as a separate commercial product following Intel acquisition; most deployments have migrated to Intel-hosted or open-source alternatives. sigopt.org (open source release) has a different deployment model. Population likely very low. The open-source variant at sigopt.org uses a similar API structure. Low survey priority.

---

## MLflow Tracking Server

**Note:** MLflow is covered in existing survey catalog `04-training-experiments.md`. Included here for completeness as it is the most widely deployed experiment tracker and has active critical CVEs.

**Category:** Experiment Tracker / Model Registry
**Default Ports:** 5000 (default); configurable
**Auth Default:** off — MLflow built-in server is unauthenticated and unencrypted by default; `--host 0.0.0.0` required to expose beyond localhost
**Shodan Dork (primary):** `http.title:"MLflow" port:5000`
**Shodan Dork (secondary):** `http.html:"mlflow" port:5000`
**Verification Probe:** `GET /api/2.0/mlflow/experiments/list` → 200 + `{"experiments": [...]}` with `experiment_id` and `name` fields
**Data Exposure Class:** All experiment runs, model artifacts, registered models, run parameters, metrics, tags (frequently include API keys as tags), dataset references, artifact URIs pointing to S3/GCS buckets
**Known CVEs:**
- CVE-2025-11201 — Directory traversal RCE via `source` parameter in model version creation endpoint. No auth required. Write arbitrary files to server filesystem; execute code if `.pth` or `.py` dropped in sys.path. All versions prior to patch commit 2e02bc7.
- CVE-2024-37054 — Deserialization RCE, patched in 2.14.2.
- CVE-2023-1177, CVE-2023-6018, CVE-2024-1483 — Prior path traversal and injection chain.
**Default Credentials:** None — no auth layer
**Notes:** MLflow 3.5.0+ added security middleware (DNS rebinding protection, CORS, clickjacking) but only with FastAPI/uvicorn backend — gunicorn deployments remain unprotected. Auth plugin requires explicit install and configuration. This is a primary target in the broader training/experiments survey.

---

## Summary Table

| Platform | Auth Default | Key Port(s) | CVEs | Survey Priority |
|---|---|---|---|---|
| W&B Local | on (API key req.) | 8080 | None specific | Medium |
| ClearML | **off** | 8080/8008/8081 | MongoBleed (backend) | **High** |
| Comet ML | default-creds (admin:admin) | 5000 | None specific | **High** |
| Neptune.ai | on (Keycloak) | 30080 | None specific | Low |
| Aim | **off** | 43800/53800 | None | **High** |
| DVC Studio | on (OAuth) | 80/443 | None | Low |
| Determined.ai | default-creds (admin:blank) | 8080/8443 | None (config-class) | **High** |
| Guild AI | N/A (local only) | N/A | None | Not applicable |
| Sacred + Omniboard | **off** | 9000 (UI) / 27017 (DB) | CVE-2025-14847 (backend) | **High** |
| Optuna Dashboard | **off** (localhost-default) | 8080 | None | Medium |
| Ray Dashboard | **off** | 8265/10001 | CVE-2023-48022/23/6021 | **Critical** |
| SigOpt | on (enterprise) | 443 | None | Low |
| MLflow | **off** | 5000 | CVE-2025-11201 (RCE) | **Critical** |
