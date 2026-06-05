# Model Serving & Inference — Cat-03 OSINT Intelligence
**Date:** 2026-06-05
**Status:** Pre-survey. No active probing conducted.
**Scope:** Consumer OpenAI-compat inference servers, embedding servers, audio/speech inference
**Prior art:** `model-serving-registry-osint-2026-05-27.md` (registry/management tier; Triton, TorchServe, TF Serving, Ray, BentoML, Seldon, KServe, ONNX, TGI, vLLM, MLflow), `model-serving-management-survey-2026-05-29.md` (Shodan-dark confirmed for JSON-body dorks)
**New coverage:** KoboldCpp, LM Studio, GPT4All, Aphrodite Engine, LMDeploy, TGI (updated), faster-whisper, Jina Embedding, PaddleOCR, Bark
**Key shift from prior surveys:** The 05-28/29 surveys used JSON-body dorks against specific ports — all returned 0 (Shodan-dark). This survey uses `http.html:` dorks that capture HTML-embedded path references. `http.html:"/v1/chat/completions"` = 6,238 hits; `"SillyTavern"` = 9,030 hits. The accessible population was always there; the dork approach was wrong.

---

## Dork Catalog (Cat-03 Primary Queries)

From `shodan/queries/03-model-serving.md`:

| Query | Hits | Platform | Approach |
|---|---|---|---|
| `"SillyTavern"` | 9,030 | SillyTavern | Banner match |
| `http.html:"/v1/chat/completions"` | 6,238 | All OpenAI-compat | HTML-embedded path |
| `http.html:"/v1/models"` | 6,089 | All OpenAI-compat | HTML-embedded path |
| `"llama.cpp"` | 1,483 | llama.cpp | Banner match |
| `"llama.cpp" port:8080` | 461 | llama.cpp | Port-narrowed |
| `"vLLM"` | 356 | vLLM | Banner match |
| `http.html:"lm studio"` | 173 | LM Studio | HTML-embedded |
| `http.html:"TEI"` | 332 | HuggingFace TEI | HTML-embedded |
| `http.html:"faster-whisper"` | 190 | faster-whisper | HTML-embedded |
| `http.html:"sglang"` | 74 | SGLang | HTML-embedded |
| `http.html:"/v1/embeddings"` | 90 | Embedding servers | HTML path |
| `"koboldcpp" port:5001` | 54 | KoboldCpp | Banner+port |
| `"koboldcpp"` | 59 | KoboldCpp | Banner match |
| `http.title:"Whisper"` | 444 | Whisper ASR | Title match |
| `http.title:"Bark"` | 120 | Bark | Title match |
| `http.title:"Piper"` | 103 | Piper TTS | Title match |
| `http.html:"coqui"` | 55 | Coqui | HTML-embedded |
| `http.html:"jina"` | 83 | Jina AI | HTML-embedded |
| `http.html:"sentence-transformers"` | 31 | sentence-transformers | HTML-embedded |
| `"Triton Inference Server"` | 7 | Triton | Banner (exact phrase) |
| `"sglang"` | 60 | SGLang | Banner match |
| `"koboldai"` | 46 | KoboldAI | Banner match |
| `http.html:"nvidia nim"` | 12 | NVIDIA NIM | HTML-embedded |
| `port:1234 "model"` | 71 | LM Studio | Port+term |
| `"lmdeploy"` | 5 | LMDeploy | Banner match |
| `"Aphrodite Engine"` | 1 | Aphrodite | Exact phrase |
| `http.html:"GPT4All"` | 2 | GPT4All | HTML-embedded |
| `"GPT4All"` | 1 | GPT4All | Banner match |

**Canonical harvest queries (execute in order, de-dupe by IP):**
1. `"SillyTavern"` (9,030)
2. `http.html:"/v1/chat/completions"` (6,238)
3. `"llama.cpp"` (1,483)
4. `http.html:"lm studio"` + `port:1234 "model"` (173+71)
5. `http.html:"TEI"` (332)
6. `http.html:"faster-whisper"` (190)
7. `http.title:"Whisper"` (444)
8. `http.html:"sglang"` + `"sglang"` (74+60)
9. `"koboldcpp"` + `"koboldai"` (59+46)
10. `http.html:"nvidia nim"` (12)
11. `"lmdeploy"` (5), `"Aphrodite Engine"` (1), `http.html:"GPT4All"` (2)

**Do NOT use:** `"aphrodite"` (362 hits, Greek-mythology noise), `http.html:"infinity"` (7,794 hits, generic English word)

---

## Platform Intelligence

### KoboldCpp
- **Port:** 5001 (default), also 5000 (AI Horde worker mode)
- **Auth default:** none; `--password` flag optional (only gates generation endpoints)
- **Auth tier:** A*
- **Verification probe:** `GET /api/extra/version` → `{"result":"KoboldCpp","version":"X.Y.Z","protected":bool,...}`
- **Fingerprint discriminator:** Literal string `"KoboldCpp"` in `result` field — zero FP, unique across all AI/ML servers
- **Data exposure:** Unauth inference via /v1/chat/completions, /api/v1/generate; capability flags (vision, audio, TTS); when `--horde` flag active, instance serves AI Horde compute network (global public inference jobs)
- **CVEs:** None known
- **aimap gap:** YES — needs new fingerprint
- **Shodan dork:** `"koboldcpp" port:5001` (54 hits)

---

### LM Studio
- **Port:** 1234 (default)
- **Auth default:** none; API tokens optional
- **Auth tier:** A*
- **Verification probe:** `GET /api/v1/models` → model list on native LM Studio path (not standard OpenAI)
- **Fingerprint discriminator:** `/api/v1/models` path is LM Studio-exclusive; no other OpenAI-compat server uses this native path. Port 1234 is LM Studio-exclusive.
- **Data exposure:** Unauth inference; `/api/v1/models/load` and `/api/v1/models/download` allow unauth model management including HuggingFace downloads
- **CVEs:** None known
- **aimap gap:** YES
- **Shodan dork:** `http.html:"lm studio"` (173 hits), `port:1234 "model"` (71 hits)

---

### GPT4All
- **Port:** 4891 (GPT4All-exclusive)
- **Auth default:** serverChat disabled by default (off=safe); when enabled, no auth gate
- **Auth tier:** A*
- **Verification probe:** `GET /v1/models` → `{"object":"list","data":[{...,"owned_by":"humanity",...}]}`
- **Fingerprint discriminator:** `"owned_by":"humanity"` is hardcoded in server.cpp — unique across all OpenAI-compat servers surveyed
- **Data exposure:** When serverChat=true: unauth inference, model listing. Returns 401 when disabled (not a credential gate — the service is disabled).
- **CVEs:** None known
- **aimap gap:** YES
- **Shodan dork:** `http.html:"GPT4All"` (2 hits); low Shodan surface (localhost-default)

---

### Aphrodite Engine
- **Port:** 2242 (Aphrodite-exclusive default)
- **Auth default:** none; `--api-key` optional
- **Auth tier:** A*
- **Verification probe:** `GET /v1/models` → `{"object":"list","data":[{...,"owned_by":"pygmalionai",...}]}`
- **Fingerprint discriminator:** `"owned_by":"pygmalionai"` hardcoded in protocol.py 0.6.4+ — unique; distinguishes from vLLM ("vllm"), llama.cpp ("llamacpp"), LMDeploy ("lmdeploy")
- **Data exposure:** Unauth inference; inherits vLLM management plane bypass (/pause, /resume); models are commonly RP/creative-writing fine-tunes (PygmalionAI origin community)
- **CVEs:** None known specific to Aphrodite; inherits vLLM CVE patterns
- **aimap gap:** YES — do NOT use body_contains:"aphrodite" (362-hit noise); use owned_by:"pygmalionai"
- **Shodan dork:** `"Aphrodite Engine"` (1 hit exact phrase)

---

### LMDeploy
- **Port:** 23333 (LMDeploy-exclusive)
- **Auth default:** none
- **Auth tier:** A*
- **Verification probe:** `GET /v1/models` → `{"object":"list","data":[{...,"owned_by":"lmdeploy",...}]}`
- **Fingerprint discriminator:** `"owned_by":"lmdeploy"` + port 23333; non-standard endpoints `/sleep`, `/wakeup`, `/is_sleeping`, `/distserve/*` are LMDeploy-exclusive
- **Data exposure:** Unauth inference; `/update_weights` unauth model weight updates; `/terminate` unauth server shutdown; `/distserve/*` exposes distributed serving topology; primarily InternLM/Chinese AI Lab deployments
- **CVEs:** None known specific to LMDeploy
- **aimap gap:** YES
- **Shodan dork:** `"lmdeploy"` (5 hits); primarily Chinese cloud (Alibaba Cloud, Tencent Cloud)

---

### HuggingFace TGI (Text Generation Inference) — UPDATED
- **Port:** 8080 (Docker -p 8080:80 host mapping)
- **Auth default:** none
- **Auth tier:** A
- **Verification probe:** `GET /info` → `{"model_id":"...","model_dtype":"...","model_sha":"...","max_total_tokens":...,"tokenization_workers":...,"version":"..."}`
- **Fingerprint discriminator:** `tokenization_workers` (integer) + `model_sha` (40-char hex) — absent from all other serving platforms
- **Data exposure:** Model ID including private/gated HF models; inference via /generate and /generate_stream; full generation config; HF_TOKEN if misconfigured in pod spec
- **Deployment status:** Maintenance mode as of 2026; new deployment rate declining (migrating to vLLM/SGLang)
- **CVEs:** None high-profile specific to TGI REST API
- **aimap gap:** YES — needs fingerprint
- **Shodan dark:** `port:8080 "model_id" "model_dtype"` returns 0 (JSON body not indexed). Correct approach: masscan port 8080, httpx filter on /info path.
- **Note:** aimap already has this in fingerprints? Check — if present, verify probe matches /info + tokenization_workers

---

### TorchServe (ShellTorch)
- **Port:** 8081 (management — critical), 8080 (inference), 8082 (Prometheus)
- **Auth default:** none; management port ships 0.0.0.0 despite localhost-only docs
- **Auth tier:** A
- **Verification probe:** `GET /models` on port 8081 → `{"models":[{"modelName":"...","modelUrl":"...","minWorkers":...,"maxWorkers":...}],"nextPageToken":"..."}`
- **Fingerprint discriminator:** `nextPageToken` field is TorchServe-exclusive
- **Data exposure:** Full model inventory; model .mar file paths/origin URLs; `POST /models?url=<external>` = SSRF post-CVE-2023-43654-patch (RCE pre-patch)
- **CVEs:** CVE-2023-43654 (CVSS 9.8, ShellTorch), CVE-2022-1471 (CVSS 9.9, SnakeYAML RCE), Kroll 2025 (stack overflow + unsafe deserialization, v0.11 fix)
- **aimap gap:** NO FP gap — port 8081 Shodan-dark (not crawled); correct approach: masscan 8081
- **Shodan dark:** All port 8081 dorks return 0. Confirmed empirically.

---

### Seldon Core
- **Port:** 9000 (pod), 80 (via Istio/Ambassador ingress)
- **Auth default:** none; Istio auth opt-in
- **Auth tier:** A
- **Verification probe:** `POST /seldon/{namespace}/{deployment}/api/v1.0/predictions` with `{"data":{"ndarray":[[1]]}}` → response contains `{"data":{"ndarray":[...]},"meta":{}}`
- **Fingerprint discriminator:** `/seldon/{ns}/{dep}/api/v1.0/predictions` path structure is globally unique; `meta` wrapper object is Seldon-specific
- **Status:** v1 EOL; v2 (Seldon AI/MLServer) uses different architecture. Red Hat OpenShift AI bundles Seldon (enterprise = IAP).
- **Shodan dark:** K8s-native, pods behind cluster network. 20 Shodan hits for prediction path URL — all offline at probe (stale index). Correct approach: K8s LoadBalancer/NodePort misconfiguration scan.

---

### ONNX Runtime Server
- **Port:** 8001 (conflicts with Triton gRPC)
- **Auth default:** none
- **Auth tier:** A
- **Verification probe:** `GET /v1/health/ready` → 200. Discriminate from TF Serving by error response format.
- **Shodan surface:** Low; primarily kibae community fork (Docker Hub: kibaes/onnxruntime-server)
- **aimap gap:** YES but low population

---

### faster-whisper (speaches / faster-whisper-server)
- **Port:** 8000 (speaches default), 10300 (linuxserver/faster-whisper)
- **Auth default:** none
- **Auth tier:** A
- **Verification probe:** `GET /v1/models` → model list with `Systran/` prefix model IDs (e.g. `Systran/faster-distil-whisper-large-v3`) — distinguishes from openai-whisper-asr-webservice (openai/whisper-* IDs) and whisper.cpp (ggml-* IDs)
- **Fingerprint discriminator:** Systran/ model ID prefix in /v1/models response; speaches adds /v1/speech (TTS) endpoint not present in other Whisper wrappers
- **aimap gap:** partial — current Whisper ASR fingerprint may not cover faster-whisper server specifically

---

### Jina AI Embedding Server (jina-serve)
- **Port:** 8080 (default), 8081 (multi-protocol)
- **Auth default:** none (jina-serve) or optional
- **Auth tier:** B
- **Verification probe:** `GET /status` → `{"jina":{"jina":"3.x.x","docarray":"...","python":"3.x"},"envs":{...}}`
- **Fingerprint discriminator:** `jina` top-level key in /status response — unique; no other embedding server returns this key
- **Data exposure:** Embedding vectors; unauth /search exposes vector index; /index allows unauth document ingestion
- **aimap gap:** YES

---

### PaddleOCR (PaddleX serving)
- **Port:** 8080 (basic serving), 8000 (Triton high-stability)
- **Auth default:** none
- **Auth tier:** A
- **Verification probe (basic):** `POST /ocr` with test image → `{"success":true,"text":"...","rec_texts":[...],"rec_scores":[...]}`
- **Verification probe (Triton):** `POST /v2/models/ocr/infer` → nested `ocrResults` in outputs[0].data[0]
- **Fingerprint discriminator:** `rec_texts` + `rec_scores` array pair (community wrappers); `ocrResults` (Triton path)
- **Data exposure:** Arbitrary document text extraction — medical records, financial docs, ID cards depending on operator
- **CVEs:** CVE-2024-0917 (PaddlePaddle code injection CVSS 9.8), CVE-2022-46742 (eval() injection), PDSA-2022-002 (path traversal file overwrite)
- **aimap gap:** YES

---

### Bark (suno-ai/bark)
- **Port:** 5000 (Flask bark-tts-api), 8000 (FastAPI community wrappers)
- **Auth default:** none
- **Auth tier:** A (community wrappers)
- **Note:** No official suno-ai HTTP server mode. All serving is third-party community wrappers. /bark-inference endpoint (POST, returns WAV binary) is the canonical community wrapper path. Low population.
- **aimap gap:** YES but low yield

---

## aimap Coverage Summary

| Platform | In aimap | Status |
|---|---|---|
| Ollama | YES | v1.9.x |
| llama.cpp | YES | v1.9.x |
| vLLM | YES | v1.9.x |
| SGLang | YES | v1.9.x |
| Triton | YES | v1.9.x |
| SillyTavern | YES | v1.9.x |
| BentoML | YES | v1.9.x |
| Whisper ASR | YES | v1.9.x (check faster-whisper coverage) |
| Coqui XTTS | YES | v1.9.x |
| Piper TTS | YES | v1.9.x |
| WhisperLive | YES | v1.9.x |
| HuggingFace TEI | YES | v1.9.x |
| NVIDIA NIM | YES | v1.9.x |
| LLaMA-Factory | YES | v1.9.x |
| LocalAI | YES | v1.9.x |
| text-generation-webui | YES | v1.9.x |
| MLflow | YES | v1.9.x |
| TensorFlow Serving | YES | v1.9.x |
| Ray Serve | YES | v1.9.x |
| Ray Dashboard | YES | v1.9.x |
| infinity-embedding | YES | v1.9.x |
| **KoboldCpp** | **NO** | NEW — /api/extra/version → result:"KoboldCpp" |
| **LM Studio** | **NO** | NEW — port 1234, /api/v1/models |
| **GPT4All** | **NO** | NEW — port 4891, owned_by:"humanity" |
| **Aphrodite Engine** | **NO** | NEW — port 2242, owned_by:"pygmalionai" |
| **LMDeploy** | **NO** | NEW — port 23333, owned_by:"lmdeploy" |
| **TGI** | **NO** | NEW — /info, tokenization_workers + model_sha |
| **faster-whisper** | partial | Check Whisper ASR probe covers Systran/ IDs |
| **Jina Embedding** | **NO** | NEW — GET /status, jina key |
| **PaddleOCR** | **NO** | NEW — POST /ocr, rec_texts+rec_scores |
| **Bark** | **NO** | LOW YIELD — community wrappers only |
| TorchServe | NO FP needed | Shodan-dark — masscan 8081 approach |
| Seldon Core | NO FP needed | K8s-dark |
| ONNX Runtime Server | **NO** | LOW POPULATION |

---

## Thesis Relevance

All 5 new OpenAI-compat servers (KoboldCpp, LM Studio, GPT4All, Aphrodite, LMDeploy) are **auth_tier A*** — auth concept exists but is off by default. These are consumer inference servers designed for local use, deployed at internet scale without auth. The thesis predicts: any platform in the auth-off-default tier will show meaningful unauth exposure at population scale. KoboldCpp (54 Shodan hits, port 5001) is the highest-confidence new platform for the survey.

The 6,238-hit `http.html:"/v1/chat/completions"` dork is a catch-all for OpenAI-compat surfaces — this is the primary harvest query. Most hits will be vLLM/llama.cpp/Ollama (already fingerprinted), but the long tail (SGLang, LM Studio, KoboldCpp, Aphrodite, LMDeploy) is the new signal. aimap will disambiguate by port + owned_by.
