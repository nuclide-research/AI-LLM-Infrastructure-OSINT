# Model Serving / Registry — Shodan Query Catalog
_Generated: 2026-05-27 from pre-survey OSINT pass (13 platforms)_
_See: data/platform-intel/model-serving-registry-osint-2026-05-27.md for full intel_

---

## Triton Inference Server (NVIDIA)
**Auth default (mgmt):** off (management and inference share port 8000, no auth)
**Exposure class:** Model names/versions/config, shared memory ops, server stats, GPU metrics; CVE-2024-0087/0088 file write and memory read chains

| Label | Query | Rationale | FP Risk |
|-------|-------|-----------|---------|
| primary | `port:8000 "/v2/health/ready"` | KServe V2 health path; Triton is primary implementor | Med (KServe/other V2 servers share path) |
| secondary | `port:8002 "nv_inference_request_success"` | Prometheus metric name unique to Triton | Low |
| tertiary | `port:8000 "triton-inference-server" http.status:200` | Server banner or HTML reference | Low |
| model-enum | `port:8000 "/v2/models" "extensions"` | `/v2` metadata response includes `extensions` array unique to Triton | Low |
| identity-probe | `GET /v2` → `{"name":"triton","extensions":["classification","sequence","model_configuration",...]}` | `extensions` array discriminates from generic V2 impls | — |

---

## NVIDIA Merlin (Recommendation Models via Triton)
**Auth default (mgmt):** off (inherits Triton posture)
**Exposure class:** Recommendation model architecture, item/user feature schemas, ensemble pipeline topology

| Label | Query | Rationale | FP Risk |
|-------|-------|-----------|---------|
| primary | `port:8000 "/v2/models" "recsys" OR "ranking" OR "retrieval"` | Merlin model naming conventions in model list response | Low |
| secondary | `port:8000 "candidate_retrieval" OR "item_retrieval" OR "session_based"` | Merlin ensemble model name patterns | Low |
| identity-probe | `GET /v2/models` → model names containing `ranking`, `retrieval`, `recsys`, `candidate` | Model naming convention distinguishes Merlin from generic Triton | — |

---

## TorchServe (PyTorch)
**Auth default (mgmt):** off — binds `0.0.0.0:8081` despite docs claiming localhost-only (ShellTorch, CVE-2023-43654)
**Exposure class:** Full model inventory with file paths and worker config; pre-patch: arbitrary remote model registration RCE

| Label | Query | Rationale | FP Risk |
|-------|-------|-----------|---------|
| primary | `port:8081 "nextPageToken" "models" http.status:200` | `nextPageToken` in `GET /models` response is TorchServe-unique | Low |
| secondary | `port:8081 "modelName" "modelUrl" "minWorkers"` | Model descriptor JSON field set unique to management API | Low |
| tertiary | `port:8082 "ts_" http.status:200` | TorchServe Prometheus metrics use `ts_` prefix (e.g. `ts_inference_requests_total`) | Low |
| inference | `port:8080 "torchserve" OR "pytorch serve"` | Inference port banner; lower confidence | High |
| identity-probe | `GET /models` on 8081 → `{"models":[{"modelName":"...","modelUrl":"..."}],"nextPageToken":"..."}` | `nextPageToken` field confirms TorchServe management API | — |

---

## TensorFlow Serving
**Auth default (mgmt):** off (no management API; inference port has no auth; binds 0.0.0.0)
**Exposure class:** Model names, versions, load state, signature definitions (I/O tensor schemas), unauthenticated predictions

| Label | Query | Rationale | FP Risk |
|-------|-------|-----------|---------|
| primary | `port:8501 "model_version_status" "AVAILABLE"` | Protobuf-to-JSON field name unique to TF Serving status response | Low |
| secondary | `port:8501 "/v1/models/" http.status:200` | REST API root path | Med (shared with ONNX Runtime Server pattern) |
| tertiary | `port:8501 "signature_name" "serving_default"` | Default signature name in TF SavedModel metadata | Low |
| grpc-banner | `port:8500 "tensorflow"` | gRPC port banner may contain TF references | Med |
| identity-probe | `GET /v1/models/{name}` → `{"model_version_status":[{"version":"1","state":"AVAILABLE","status":{}}]}` | `model_version_status` array structure unique to TF Serving | — |

---

## Ray Serve / Ray Dashboard
**Auth default (mgmt):** off — Jobs API has no auth; actively exploited (ShadowRay, CVE-2023-48022, CVSS 9.8)
**Exposure class:** Cluster topology, all jobs/actors/tasks, cloud credentials in worker env, SSH keys, API tokens, training data

| Label | Query | Rationale | FP Risk |
|-------|-------|-----------|---------|
| primary | `port:8265 "ray_version" http.status:200` | `/api/version` field unique to Ray dashboard | Low |
| secondary | `port:8265 http.title:"Ray Dashboard"` | Dashboard HTML title | Low |
| tertiary | `port:8265 "/api/jobs" OR "/api/actors"` | Ray dashboard API path structure | Low |
| serve-proxy | `port:8000 "ray" "/serve/" http.status:200` | Ray Serve HTTP proxy on port 8000 with serve path prefix | Med |
| identity-probe | `GET /api/version` on 8265 → `{"ray_version":"2.x.x","ray_commit":"..."}` | `ray_commit` field unique to Ray | — |

---

## BentoML / BentoServer
**Auth default (mgmt):** off — no auth by default; ASGI middleware required for any auth
**Exposure class:** Full inference API, OpenAPI spec at /docs.json, all endpoint input/output schemas, service name/version in headers

| Label | Query | Rationale | FP Risk |
|-------|-------|-----------|---------|
| primary | `port:3000 "bentoml" http.status:200` | Server header or body reference | Med (port 3000 common) |
| secondary | `port:3000 "/docs.json" "bentoml" OR "bento"` | BentoML OpenAPI spec endpoint | Low |
| tertiary | `port:3000 "Bento-Name" OR "Yatai-Bento-Deployment-Namespace"` | HTTP response headers unique to BentoML | Low |
| identity-probe | `GET /docs.json` → OpenAPI `info` object with BentoML vendor fields; or `Server: BentoML` response header | Header is most reliable discriminator | — |

---

## Seldon Core
**Auth default (mgmt):** off — SeldonDeployment pods expose port 9000 with no auth; Istio auth is opt-in
**Exposure class:** Model predictions (no auth), K8s namespace/deployment topology in URL paths, model graph structure

| Label | Query | Rationale | FP Risk |
|-------|-------|-----------|---------|
| primary | `port:9000 "/api/v1.0/predictions" http.status:200` | Seldon-specific API path | Low |
| secondary | `port:9000 "seldon" "/seldon/" http.status:200` | Namespace-prefixed Seldon path | Low |
| tertiary | `port:80 "/seldon/" "/api/v1.0/predictions"` | Via Istio/Ambassador ingress on port 80 | Low |
| identity-probe | `POST /seldon/{ns}/{name}/api/v1.0/predictions` with `{"data":{"ndarray":[[1]]}}` → `{"data":{"ndarray":[...]},"meta":{}}` | `meta` wrapper field is Seldon-specific | — |

---

## KServe / KFServing
**Auth default (mgmt):** off — InferenceService endpoint publicly accessible by default; auth requires Istio + Dex (opt-in)
**Exposure class:** Model metadata (input/output schemas, platform/framework, versions), inference results

| Label | Query | Rationale | FP Risk |
|-------|-------|-----------|---------|
| primary | `port:80 "/v2/models" "platform" "inputs" "outputs" http.status:200` | KServe V2 model metadata response fields | Low |
| secondary | `port:8080 "/v2/health/ready" "ready":true` | V2 health endpoint on predictor port | Med (Triton shares path) |
| tertiary | `http.title:"KServe" OR "/v2/models/" "versions" "platform"` | Model metadata `platform` field in combination | Low |
| identity-probe | `GET /v2/models/{name}` → `{"name":"...","versions":["1"],"platform":"sklearn","inputs":[...],"outputs":[...]}` | `platform` field distinguishes from raw Triton | — |

---

## ONNX Runtime Server
**Auth default (mgmt):** off — binds 0.0.0.0:8001; no auth layer
**Exposure class:** Model inference results, model path leakage in error messages

| Label | Query | Rationale | FP Risk |
|-------|-------|-----------|---------|
| primary | `port:8001 "/v1/models/" "onnx" http.status:200` | ONNX-specific path with model directory | Low |
| secondary | `port:8001 "onnxruntime" OR ".onnx" http.status:200` | Runtime identifier in response body | Low |
| tertiary | `port:8001 "/v1/models/" "/versions/" ":predict"` | URL pattern unique to ONNX Runtime Server | Low |
| identity-probe | `GET /v1/models/{name}/versions/1:predict` (invalid method) → error containing `"onnxruntime"` or ONNX-specific error text | Error message discriminates from TF Serving 404 | — |

---

## Hugging Face Text Generation Inference (TGI)
**Auth default (mgmt):** off — no auth; model loaded at startup
**Exposure class:** Model ID (including private/gated models), model dtype/sha, full inference via /generate, generation config

| Label | Query | Rationale | FP Risk |
|-------|-------|-----------|---------|
| primary | `port:8080 "/info" "model_id" "model_dtype"` | TGI `/info` response field combination | Low |
| secondary | `port:8080 "tokenization_workers" "max_total_tokens"` | TGI-specific `/info` response fields | Low |
| tertiary | `port:80 "/info" "model_sha" "model_dtype"` | Container-internal port 80 variant | Low |
| quaternary | `port:8080 "text-generation-inference" http.status:200` | Explicit TGI reference in banner | Low |
| identity-probe | `GET /info` → `{"model_id":"...","model_dtype":"bfloat16","model_sha":"...","max_total_tokens":...,"tokenization_workers":...}` | `tokenization_workers` + `model_sha` combo is TGI-unique | — |

---

## vLLM
**Auth default (mgmt):** off by default; `--api-key` optional and bypassed by control endpoints even when set
**Exposure class:** Model name/ID (private fine-tunes), inference via /v1/chat/completions, unauthenticated control ops (/pause, /resume, /update_weights) even with API key set

| Label | Query | Rationale | FP Risk |
|-------|-------|-----------|---------|
| primary | `port:8000 "/v1/models" "owned_by":"vllm"` | `owned_by` field value `"vllm"` in model list response | Low |
| secondary | `port:8000 "/version" "vllm"` | `/version` endpoint returns vLLM version, no auth | Low |
| tertiary | `port:8000 "max_model_len" "tokenizer" http.status:200` | vLLM-specific fields in model metadata | Low |
| quaternary | `port:8000 "/v1/completions" "vllm" http.status:200` | Inference endpoint with vLLM banner | Med |
| identity-probe | `GET /version` → `{"version":"0.x.x"}` (no auth required); `GET /v1/models` → `{"data":[{"owned_by":"vllm",...}]}` | `"owned_by":"vllm"` is definitive discriminator | — |

---

## MLflow Model Registry
**Auth default (mgmt):** off — auth is opt-in plugin; not enabled by default; entire registry API is open
**Exposure class:** All registered model names/versions/aliases/tags, experiment runs with metrics and artifact paths, training data references, model artifact download (local filesystem deployments)

| Label | Query | Rationale | FP Risk |
|-------|-------|-----------|---------|
| primary | `port:5000 "/api/2.0/mlflow/registered-models" http.status:200` | MLflow registry API path | Low |
| secondary | `port:5000 "mlflow" "registered_models" http.status:200` | MLflow response field in banner | Low |
| tertiary | `port:5000 http.title:"MLflow" "experiment_id"` | MLflow web UI with experiment data | Low |
| quaternary | `port:5000 "run_id" "artifact_uri" "params"` | MLflow run record fields in API response | Low |
| identity-probe | `GET /api/2.0/mlflow/registered-models/list` → `{"registered_models":[{"name":"...","creation_timestamp":...,"latest_versions":[...]}]}` | `registered_models` array with `creation_timestamp` is MLflow-unique | — |

---

## Cortex (cortexlabs) — Legacy/Archived
**Auth default (mgmt):** off within cluster; AWS IAM for operator; largely moot (project archived)
**Exposure class:** Model inference results; Nucleus server error messages may expose cortex config

| Label | Query | Rationale | FP Risk |
|-------|-------|-----------|---------|
| primary | `port:8080 "cortex" "/predict" http.status:200` | Cortex inference path with branding | High |
| secondary | `port:8080 "cortexlabs" OR "nucleus" "/predict"` | Cortexlabs-specific references | Med |
| identity-probe | Check HTTP response headers or error body for `cortex` version strings; no reliable unique fingerprint | Cortex wraps arbitrary containers — fingerprint is application-level | — |

---

## Comet Opik (Self-hosted LLM Observability)
**Auth default (mgmt):** off — auth was a feature request as of 2025 (GitHub issue #949); self-hosted instances likely open
**Exposure class:** LLM traces, prompts, completions, experiment results, dataset contents

| Label | Query | Rationale | FP Risk |
|-------|-------|-----------|---------|
| primary | `port:5173 "opik" http.status:200` | Opik UI default port | Low |
| secondary | `port:5173 "comet" "opik" http.title:"Opik"` | Opik branding in UI title | Low |
| tertiary | `port:3000 "opik" "/api/v1/private" http.status:200` | Opik API port with health path | Med (port 3000 common) |
| identity-probe | `GET /api/v1/private/health` on port 5173 or 3000 → 200 + Opik health response | Health endpoint confirms Opik identity | — |

---

## Notes on Port Conflicts and FP Management

- **Port 8000**: Triton (HTTP), Ray Serve (proxy), vLLM, and general web services all share this port. Use path-based discriminators (`/v2/` = Triton/KServe, `/v1/models` + `owned_by:vllm` = vLLM, `/api/jobs` = Ray).
- **Port 8001**: Triton gRPC and ONNX Runtime Server (HTTP) both use 8001. HTTP service on 8001 with `/v1/models/` path = ONNX Runtime; gRPC service = Triton gRPC.
- **Port 8080**: TorchServe inference, Cortex, KServe predictor, TGI (host-mapped), and general web traffic. Path and banner discrimination required.
- **Port 3000**: BentoML and Opik API both default here. Use `/docs.json` vs `/api/v1/private` to discriminate.
- **Port 5000**: MLflow. Low conflict risk — few other services default here. High-confidence target.
- **Port 8265**: Ray Dashboard. Very low FP risk — distinctive SPA and API structure.
- **Port 8081**: TorchServe Management API. Very low FP risk — `nextPageToken` field is definitive.
