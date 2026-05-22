# 24. LLM Observability / Training Telemetry

_Section created: 2026-05-09_

LLM observability platforms (Phoenix/Arize, Langfuse) and ML training telemetry tools (TensorBoard, Weights & Biases self-hosted) ship with no authentication by default. Exposed instances leak: LLM call traces (including user prompts and PII in inputs), model performance metrics, training loss curves, hyperparameter sweeps, operator application names, and sometimes training data samples.

**Survey result (2026-05-04):** 4,314 port-6006 candidates across 76 tier-2 ranges (3.55M IPs) → **9 confirmed AI/ML observability instances** (after filtering 38 non-AI services — Juniper firewalls, ASUS routers, USG Flex ATP). **6 Phoenix (Arize), 3 TensorBoard, all unauthenticated.** Notable: active SDXL distillation + LoRA fine-tuning research visible on `51.159.189.219` (Scaleway); two-host Phoenix deployment for `made-doc-analysis-llm-app` at `51.159.138.130` + `51.159.162.241`.

**Langfuse** (covered in §5, gateways-monitoring) deferred here: `"Langfuse" port:3000` returns ~1,131 Shodan hits; full population survey deferred pending Shodan API access. See `langfuse-cross-survey-2026-05-06.md` for the single-host correlation finding.

**Auth posture:**
- **Phoenix (Arize)**: T1 — no auth, `--host 0.0.0.0` default, no auth flag.
- **TensorBoard**: T1 — no auth concept in standalone mode.
- **Weights & Biases self-hosted**: T2 — auth on by default, but version disclosure on `/api/health`.
- **ClearML server**: T2 — `/version` endpoint open, dashboard sometimes misconfigured.

---

## Phoenix (Arize AI)

| Shodan Query | Notes |
|---|---|
| `port:6006 "phoenix"` | Phoenix on default port (shared with TensorBoard) |
| `port:6006 http.html:"phoenix"` | HTML-scoped on port 6006 |
| `port:6006 http.html:"arize"` | Arize identifier |
| `port:6006 http.html:"Phoenix"` | Capitalized form |
| `port:6006 http.html:"arize-phoenix"` | Package identifier in page source |
| `http.html:"/v1/projects"` | Phoenix projects API endpoint path |
| `http.html:"/v1/traces"` | Phoenix traces endpoint (OTLP JSON) |
| `"arize" "phoenix" port:6006` | Conjunctive match on default port |
| `"arize-phoenix"` | Package name in any indexed source |
| `http.title:"Phoenix"` | Page title; note false-positive risk (Phoenix AZ city sites) |
| `http.title:"Phoenix" port:6006` | Title + default port reduces FP significantly |
| `http.title:"Arize Phoenix"` | Full product title; highest precision |
| `hostname:"phoenix" port:6006` | rDNS + default port |
| `ssl.cert.subject.cn:"phoenix" port:6006` | TLS cert CN + port |
| `port:6006 org:"scaleway"` | Scaleway (primary survey provider for Phoenix finds) |
| `port:6006 org:"ovh"` | OVH |
| `port:6006 org:"linode"` | Linode/Akamai |
| `port:6006 org:"hetzner"` | Hetzner |
| `port:6006 org:"digitalocean"` | DigitalOcean |
| `port:6006 org:"amazon"` | AWS |

---

## TensorBoard

| Shodan Query | Notes |
|---|---|
| `port:6006 "tensorboard"` | TensorBoard on default port |
| `port:6006 http.html:"tensorboard"` | HTML-scoped |
| `port:6006 http.html:"TensorBoard"` | Capitalized form |
| `port:6006 http.html:"tensorflow"` | TensorFlow co-occurrence |
| `http.html:"/data/runs"` | TensorBoard runs endpoint path in source |
| `http.html:"/data/experiments"` | TensorBoard experiments endpoint path |
| `http.html:"/data/plugin/scalars"` | TensorBoard scalars plugin path |
| `http.html:"tensorboard" port:6006` | HTML-scoped on default port |
| `"TensorBoard" port:6006` | Bare-string on default port |
| `"TensorBoard"` | Bare-string broadest (TensorBoard also runs on 6007, 6008, etc.) |
| `http.title:"TensorBoard"` | Page title; reliable |
| `http.title:"TensorBoard" port:6006` | Title + default port |
| `http.html:"lightning_logs"` | PyTorch Lightning log path (common in training setups) |
| `http.html:"lightning_logs" port:6006` | Lightning logs on TensorBoard default port |
| `hostname:"tensorboard"` | rDNS pattern |

---

## Weights & Biases (self-hosted / wandb-local)

| Shodan Query | Notes |
|---|---|
| `port:8080 "wandb"` | W&B self-hosted on alt port |
| `port:8080 "weights-and-biases"` | Full name |
| `http.html:"wandb" port:8080` | HTML-scoped |
| `http.html:"/api/health" http.html:"wandb"` | W&B health endpoint + identifier |
| `"wandb-local"` | Self-hosted container identifier |
| `"wandb" "api/health"` | Health endpoint conjunction |
| `http.title:"Weights & Biases"` | Page title |
| `http.title:"W&B"` | Abbreviated title |
| `hostname:"wandb"` | rDNS pattern |
| `ssl.cert.subject.cn:"wandb"` | TLS cert CN |
| `http.html:"wandb" org:"amazon"` | AWS W&B deployments |

---

## ClearML Server

| Shodan Query | Notes |
|---|---|
| `port:8080 "clearml"` | ClearML on default web port |
| `port:8008 "clearml"` | ClearML API server port |
| `port:8081 "clearml"` | ClearML app port |
| `http.html:"clearml" port:8080` | HTML-scoped |
| `http.html:"/version" port:8008` | ClearML version endpoint (`/version` returns ClearML version JSON) |
| `"clearml"` | Bare-string in any field |
| `http.title:"ClearML"` | Page title |
| `hostname:"clearml"` | rDNS |
| `ssl.cert.subject.cn:"clearml"` | TLS cert CN |

---

## MLflow Tracking Server (additional queries beyond §4)

| Shodan Query | Notes |
|---|---|
| `http.html:"/api/2.0/mlflow/experiments/list"` | MLflow experiment list API path in source |
| `http.html:"/api/2.0/mlflow/runs/search"` | MLflow run search API path |
| `port:5000 "mlflow" http.html:"experiments"` | MLflow on port 5000 with experiment UI |
| `port:5000 "mlflow" http.html:"/v2"` | MLflow v2 API (newer versions) |

---

## Evidently ML Monitoring

_Fingerprinted live: evidently/evidently-service:latest (v0.7.21), 2026-05-22._
_Identity marker: GET /api/version → `{"application":"Evidently UI","version":"...","commit":"..."}` — unambiguous, unauth, available on default deploy. Use this for verification; do NOT claim a hit from title dork alone._
_Auth posture: Tier-A (no auth concept in default deploy — /api/version and /api/projects both 200 with no credentials)._
_Default port: 8000 (uvicorn). Also seen on 3000 and behind :80/:443._

| Shodan Query | Notes |
|---|---|
| `http.title:"Evidently"` | Page title; 6 hits observed Session 30. Generic English word — ~50% FP expected, verify with /api/version probe (Insight #15) |
| `http.title:"Evidently - ML Monitoring"` | More specific title substring; reduces FP vs bare "Evidently" |
| `ssl.cert.subject.cn:evidently` | TLS cert CN; 10 hits Session 30. Per Insight #47, CN hits are attribution-only — likely reverse-proxy-fronted, auth-on |
| `http.html:"Evidently.AI"` | Manifest short_name; Shodan may not index manifests |
| `http.html:"Evidently.AI Dashboards"` | Manifest full name; same caveat |
| `port:8000 "uvicorn" "Evidently"` | Port + server header + brand (needs conjunctive Shodan syntax) |
| `hostname:evidently port:8000` | rDNS + default port |

---

## Combined

| Shodan Query | Notes |
|---|---|
| `port:6006 (http.html:"tensorboard" OR http.html:"phoenix" OR http.html:"arize")` | Full port-6006 AI observability sweep |
| `(http.title:"TensorBoard" OR http.title:"Phoenix" OR http.title:"Arize Phoenix")` | Title sweep, any port |
| `(http.html:"/v1/projects" OR http.html:"/data/runs") port:6006` | Endpoint-based sweep |
| `port:6006 -http.html:"juniper" -http.html:"fortinet" -http.html:"asus"` | Port-6006 sweep with network-gear false-positive filter |
| `(hostname:"tensorboard" OR hostname:"wandb" OR hostname:"clearml" OR hostname:"mlflow")` | rDNS sweep |
| `port:6006 org:"scaleway"` | Scaleway sweep (6/9 survey finds were Scaleway) |
| `port:6006 org:"university"` | Academic research telemetry (active fine-tuning research) |
