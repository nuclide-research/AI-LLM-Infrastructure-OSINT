# LLM Safety / Guardrail Engine OSINT — Pre-Survey Intelligence
**Date:** 2026-05-27
**Purpose:** Tune dork queries, understand auth posture, identify verification probes, document data exposure classes before Shodan harvests.
**Scope:** 12 platforms — LLM guardrails, safety classifiers, prompt injection detection, content filtering APIs.
**Status:** Pre-survey. No active probing conducted.

**Key finding across the category:** guardrail engines that run as API servers almost universally assume trusted-network deployment and ship with auth off by default. `AUTH_TOKEN` in LLM Guard, `GUARDRAILS_API_KEY` in Guardrails AI, and the `MASTER_API_KEY` in Rebuff are all opt-in environment variables. An exposed guardrail server gives an attacker three things: (1) the safety layer is bypassable — send directly to the upstream LLM; (2) prompt scan logs expose user inputs; (3) the policy/guard config reveals the operator's threat model.

---

## LlamaGuard / Llama Guard 3 (Meta)

**Category:** Safety Classifier (model, not a standalone server)
**Default Ports:** 8000 (vLLM), 8080 (TGI), 11434 (Ollama)
**Auth Default:** off — no auth concept on the underlying inference server unless `--api-key` passed to vLLM or equivalent
**Shodan Dork (primary):** `http.html:"Llama-Guard-3"`
**Shodan Dork (secondary):** `http.html:"meta-llama/Llama-Guard" port:8000`
**Verification Probe:** `GET /v1/models` → 200 + JSON `id` field containing `"Llama-Guard"` or `"llama-guard"`
**Data Exposure Class:** model roster (confirms safety classifier loaded), inference endpoint usable without auth to call the classifier or extract its behavior
**Known CVEs:** none specific to LlamaGuard; vLLM/TGI hosting servers have separate CVE history
**Default Credentials:** none
**Notes:** LlamaGuard is a model, not a server. Discovery runs through the underlying inference server (`/v1/models` endpoint). The model name appears in the `id` field of the models list. Llama Guard 4 12B variant also in circulation. Self-hosted deployments typically use vLLM on port 8000 with the Hugging Face model path `meta-llama/Llama-Guard-3-8B`. When exposed without auth, the safety classifier itself can be queried — attacker learns guardrail taxonomy and can probe for bypass. Also visible via `/api/show` on Ollama if the model is named `llama-guard`. FP risk: other models served on port 8000 with vLLM — must confirm model name in `/v1/models` response.

---

## NeMo Guardrails (NVIDIA)

**Category:** Guardrail API Server (policy DSL + LLM call routing)
**Default Ports:** 8000
**Auth Default:** off — no built-in auth; `Authorization` header is forwarded upstream to the LLM provider, not checked by NeMo itself
**Shodan Dork (primary):** `http.html:"/v1/rails/configs"`
**Shodan Dork (secondary):** `http.html:"nemoguardrails" port:8000`
**Verification Probe:** `GET /v1/rails/configs` → 200 + JSON array (empty `[]` or list of config names)
**Data Exposure Class:** rail config names and structure, deployed Colang policy logic, upstream LLM provider configuration (via `/v1/models`), conversation state (via threaded completions endpoint)
**Known CVEs:** none specific; research shows prompt injection attacks can bypass NeMo rails via specially crafted inputs
**Default Credentials:** none
**Notes:** Started with `nemoguardrails server --config ./config --port 8000`. The `/v1/rails/configs` endpoint returns the names of loaded rail configurations — leaks the operator's threat taxonomy. The `/v1/chat/completions` endpoint accepts a `guardrails` key with `config_id` — this uniquely identifies a NeMo Guardrails server vs a standard OpenAI-compatible endpoint. The Chat UI is served at `/` and the docs at `/redoc`. CORS is disabled by default (`NEMO_GUARDRAILS_SERVER_ENABLE_CORS: False`). FP risk: low on `/v1/rails/configs` — path is unique to NeMo. Body match on `"colang"` (NeMo's policy DSL) is also high-signal but rare in Shodan indexes.

---

## Lakera Guard (Commercial — self-hosted enterprise variant)

**Category:** Guardrail API Server (commercial, SaaS-primary with self-hosted enterprise option)
**Default Ports:** 443 (SaaS), self-hosted port undisclosed in public docs (gated behind enterprise access)
**Auth Default:** on (API key required for SaaS); self-hosted variant details are under NDA/enterprise access — assume requires customer API key
**Shodan Dork (primary):** `http.html:"lakera-guard"`
**Shodan Dork (secondary):** `http.html:"/v1/guard" http.html:"lakera"`
**Verification Probe:** `POST /v1/guard` → 200 or 4xx + JSON with Lakera-specific fields (`"flagged"`, `"categories"` with `"prompt_injection"`, `"jailbreak"`)
**Data Exposure Class:** caller-side: customer apps embed the `api.lakera.ai` URL in HTML/JS — reveals which orgs use Lakera; self-hosted: guard policy config if exposed
**Known CVEs:** none public
**Default Credentials:** none (API key required)
**Notes:** Primary attack surface is caller-side discovery — customer apps hardcoding `api.lakera.ai` in JS bundles or HTML reveal the Lakera deployment population. Self-hosted variant requires GPU-backed Triton inference server stack; public docs gated. The `Server: lakera` response header is the highest-precision signal for actual self-hosted instances. Response fields include `"prompt_injection"`, `"jailbreak_attempt"`, `"unknown_links"`, `"relevant_language"`, `"pii"` as category keys. FP risk on body matches: `"lakera"` appears in unrelated content; combine with `/v1/guard` path for precision.

---

## Guardrails AI

**Category:** Guardrail API Server (output validation against Pydantic-style guard definitions)
**Default Ports:** 8000
**Auth Default:** off — `GUARDRAILS_API_KEY` is optional; when not set, all endpoints publicly accessible
**Shodan Dork (primary):** `http.html:"guardrails-ai" port:8000`
**Shodan Dork (secondary):** `http.html:"guardrailsai.com" port:8000`
**Verification Probe:** `GET /guards` → 200 + JSON array of guard definitions; `GET /health-check` → 200 + `{"status": "ok"}`
**Data Exposure Class:** all configured guard definitions (validation logic and schemas), guard names, associated LLM configurations, prompt/response scan history if a persistence layer is configured
**Known CVEs:** none specific
**Default Credentials:** none
**Notes:** Started with `guardrails start` or `guardrails-api start`. FastAPI server — Swagger UI at `/docs` and OpenAPI spec at `/openapi.json`. When `GUARDRAILS_API_KEY` is not set, `GET /guards` returns all guard definitions with full validation logic. `POST /guards/{guard_name}/validate` runs validation without auth. The `/guards/{guard_name}/openai/v1/chat/completions` endpoint proxies to the configured LLM — if the upstream LLM key is embedded in guard config, it may be retrievable. The `guardrails-lite-server` variant is a minimal deployment. FP risk on `/guards`: 1,048 hits on Shodan (any app with a `/guards/` route). Must confirm via JSON array response shape, not URL match alone.

---

## LLM Guard (Protect AI)

**Category:** Guardrail API Server (input/output scanner with 20+ pluggable scanners)
**Default Ports:** 8000
**Auth Default:** off — `AUTH_TOKEN` environment variable is optional; when unset, API is open
**Shodan Dork (primary):** `http.html:"llm-guard" port:8000`
**Shodan Dork (secondary):** `http.html:"laiyer/llm-guard" OR http.html:"protectai/llm-guard"`
**Verification Probe:** `GET /swagger.json` → 200 + JSON with `"info"` field containing `"LLM Guard API"`; `GET /docs` available in DEBUG mode
**Data Exposure Class:** scanner configuration (which scanners are active, thresholds, model names), prompt scan results if caching is enabled (LRU cache of last 100 scans), scanner model paths
**Known CVEs:** none specific; see Protect AI security advisories for related products
**Default Credentials:** none
**Notes:** Docker image `laiyer/llm-guard-api:latest`. Auth is configured via `-e AUTH_TOKEN='my-token'` at runtime — when omitted, all `/analyze/*` endpoints are open. `/analyze/prompt` and `/analyze/output` are the primary scan endpoints. The API exposes `APP_NAME = "LLM Guard API"` in the OpenAPI spec — this is the high-precision Shodan signal. Scan responses include `is_valid`, `scanners_results`, and per-scanner scores. Configuration supports HTTP bearer or basic auth but neither is default. Deployed alongside LiteLLM as a scan middleware in many setups. FP risk: `"llm-guard"` matches the GitHub repo URL in many unrelated pages — body match must be on port 8000 or paired with API structure signals.

---

## Rebuff (Protect AI)

**Category:** Prompt Injection Detection API (self-hardening, uses canary tokens + VectorDB + LLM)
**Default Ports:** 3000
**Auth Default:** off by default in dev — `MASTER_API_KEY=12345` is a placeholder example in `.env.local`; production deployments should set their own key
**Shodan Dork (primary):** `http.html:"rebuff" port:3000`
**Shodan Dork (secondary):** `http.html:"rebuff.ai" port:3000`
**Verification Probe:** `POST /api/detect` → response with `injectionScore`, `heuristicScore`, `vectorScore` fields
**Data Exposure Class:** injection detection scores and history, canary token corpus (reveals which prompts were flagged), vector DB contents (prior attack embeddings), OpenAI/Pinecone/Supabase API keys in environment if `.env.local` is accessible
**Known CVEs:** none specific; project archived May 2025 (no further patches)
**Default Credentials:** `MASTER_API_KEY=12345` (example placeholder — deployments that copy example config verbatim are vulnerable)
**Notes:** Repository archived 2025-05-16 — no further security patches. Node.js server on port 3000. Requires Supabase, OpenAI, and Pinecone credentials at setup. The `MASTER_API_KEY=12345` placeholder in the example `.env.local` is the primary default-creds risk — operators who copy the example without changing the key expose the API. The canary token database (`/api/canary/add`, `/api/canary/check`) is particularly interesting: it reveals which prompts have been instrumented for leakage detection. FP risk: `"rebuff"` matches unrelated content; port 3000 narrows it but is also common for Node.js dev servers.

---

## ShieldLM (Tsinghua University / thu-coai)

**Category:** Safety Classifier (LLM-based, bilingual CN/EN — not a standalone server; typically deployed via vLLM or custom inference script)
**Default Ports:** 8000 (if deployed via vLLM), no fixed port for custom deployments
**Auth Default:** off — no built-in server; auth posture depends entirely on the hosting framework
**Shodan Dork (primary):** `http.html:"ShieldLM" port:8000`
**Shodan Dork (secondary):** `http.html:"thu-coai/ShieldLM"`
**Verification Probe:** `GET /v1/models` → JSON with `id` containing `"ShieldLM"` or `"shieldlm"`; `POST /v1/chat/completions` → response text containing `"safe"`, `"unsafe"`, or `"controversial"` (ShieldLM's three output classes)
**Data Exposure Class:** safety classification labels and scores, classification explanations (ShieldLM returns reasoning), bilingual content flag (CN/EN detection)
**Known CVEs:** none specific; academic model with no CVE track record
**Default Credentials:** none
**Notes:** ShieldLM (EMNLP 2024, Tsinghua) is not an Alibaba product — attribution error common in secondary sources. Available in 6B, 7B, 13B, and 14B parameter variants. Typically served via `infer_shieldlm.sh` (CLI) or vLLM. Shodan visibility is low — primarily surfaces in research or internal deployments. The three output classes (`0=safe`, `1=unsafe`, `2=controversial`) and Chinese-language capability make it distinctive. FP risk: high for generic vLLM-based searches; body match on `"ShieldLM"` is specific but rare.

---

## Llama-Recipes Safety Demos (Meta)

**Category:** Demo/Reference Implementations (not production guardrail servers)
**Default Ports:** variable (Flask typically 5000, FastAPI typically 8000)
**Auth Default:** off — demo code, no auth
**Shodan Dork (primary):** `http.html:"llama-recipes" port:5000 OR port:8000`
**Shodan Dork (secondary):** `http.html:"meta-llama/llama-recipes"`
**Verification Probe:** `GET /` → HTML response referencing `"llama-recipes"` or `"PurpleLlama"`
**Data Exposure Class:** demo prompt/response logs, any hardcoded API keys in demo config, model interaction history
**Known CVEs:** none specific (demo code)
**Default Credentials:** none
**Notes:** `llama-recipes` is Meta's recipe collection for Llama deployments, including safety demos. These are reference implementations intended to run locally — any internet-exposed instance is accidental. Risk class is primarily information disclosure (API keys, prompt logs) rather than a security bypass. The PurpleLlama sub-project (which includes CyberSecEval and PromptGuard) is the more targetable surface. FP risk: high — generic demo identifiers.

---

## OpenShield (AI Firewall)

**Category:** AI Firewall / Proxy (transparent proxy between clients and AI model APIs)
**Default Ports:** 8080 (main API), 8085 (Adminer database management)
**Auth Default:** on — Bearer token required for `/openai/v1/*` endpoints; API key auto-generated at startup and displayed in Docker Compose output
**Shodan Dork (primary):** `port:8080 http.html:"openshield"`
**Shodan Dork (secondary):** `port:8085 http.html:"adminer" http.html:"openshield"`
**Verification Probe:** `GET /openai/v1/models` with no auth → 401; `GET /openai/v1/models` with `Authorization: Bearer <key>` → 200
**Data Exposure Class:** port 8085 Adminer interface is the primary risk — database management UI with no separate auth in default config; reveals content filter rules, request logs, rate limit configs
**Known CVEs:** none; project archived Feb 3, 2026 (read-only)
**Default Credentials:** none static; API key generated at runtime and printed to Docker Compose logs
**Notes:** Project explicitly stated "not ready for production use" and was archived 2026-02-03. The main API (port 8080) requires Bearer auth, making it lower priority than the Adminer DB UI on port 8085. Adminer at port 8085 in the default docker-compose has no separate auth layer — any operator who exposes port 8085 publicly has a full DB management interface open. Content filter rules, blocked keyword lists, and API key entries would all be accessible. FP risk on `"openshield"`: low — specific product name. FP risk on port 8085 Adminer: high — Adminer is used by many apps.

---

## PromptGuard / Llama Prompt Guard 2 (Meta)

**Category:** Safety Classifier (prompt injection / jailbreak detector, 86M parameter mDeBERTa model)
**Default Ports:** 8000 (when served via FastAPI/vLLM-style wrapper)
**Auth Default:** off — reference deployments use no auth; only `HF_TOKEN` is required at startup to pull the gated model, not for API access
**Shodan Dork (primary):** `http.html:"Llama-Prompt-Guard" port:8000`
**Shodan Dork (secondary):** `http.html:"prompt-guard" port:8000 http.html:"injection"`
**Verification Probe:** `GET /v1/models` → JSON `id` containing `"Prompt-Guard"` or `"prompt-guard"`; `POST /v1/chat/completions` → response with `"INJECTION"`, `"JAILBREAK"`, or `"BENIGN"` classification
**Data Exposure Class:** classification results (exposes which prompts were flagged as injection/jailbreak), model version (Prompt-Guard-86M vs Llama-Prompt-Guard-2-86M), confidence scores for three classes (benign, injection, jailbreak)
**Known CVEs:** none specific
**Default Credentials:** none
**Notes:** Meta's PromptGuard 2 is the successor to Prompt-Guard-86M (released ~April 2026). Both are mDeBERTa-based sequence classifiers — very small (86M params), CPU-deployable. Typical self-hosted pattern: FastAPI or Flask wrapper exposing `/v1/chat/completions` and `/health` + `/v1/models`. The Red Hat quickstart reference implementation runs on port 8000 with no API authentication. Part of the PurpleLlama / LlamaFirewall suite. FP risk: `"prompt-guard"` is generic; combine with port 8000 and injection-related terms for precision.

---

## AIShield (Bosch)

**Category:** AI Security API (model vulnerability scanning and runtime protection)
**Default Ports:** API endpoint undisclosed (enterprise product; GUARDIAN_API_ENDPOINT is customer-configured)
**Auth Default:** on — `GUARDIAN_API_KEY` required for all operations; contact-based access provisioning
**Shodan Dork (primary):** `http.html:"aishield" http.html:"guardian"`
**Shodan Dork (secondary):** `http.html:"bosch-aisecurity" OR http.html:"AIShield Guardian"`
**Verification Probe:** N/A — no known public default endpoint pattern; API key required
**Data Exposure Class:** model vulnerability scan results, AI supply chain inventory, agentic workflow policy configs
**Known CVEs:** none public
**Default Credentials:** none
**Notes:** Bosch AIShield has two relevant products: AIShield Watchtower (model scanning, open source) and AIShield Guardian (runtime protection API, enterprise/commercial). Guardian requires `GUARDIAN_API_ENDPOINT` + `GUARDIAN_API_KEY` — no self-service registration. Watchtower is open source and CLI-based. Primary Shodan angle: find customer deployments referencing `GUARDIAN_API_ENDPOINT` in HTML/JS, or organizations running Watchtower scan results exposed via Jupyter or Streamlit. FP risk: `"guardian"` and `"aishield"` both match unrelated content — must use conjunctive matches.

---

## Vigil (deadbits/vigil-llm)

**Category:** Prompt Injection Scanner (multi-scanner REST API: YARA, vector similarity, transformer, sentiment)
**Default Ports:** 5000 (Flask default, bound to 0.0.0.0)
**Auth Default:** off — no authentication implemented in any version; zero auth checks in server code
**Shodan Dork (primary):** `port:5000 http.html:"vigil"`
**Shodan Dork (secondary):** `port:5000 http.html:"prompt injection" http.html:"analyze"`
**Verification Probe:** `GET /settings` → 200 + JSON with `"scanner"`, `"embedding"`, and `"cache"` keys; `POST /analyze/prompt` with `{"prompt": "test"}` → JSON with `"uuid"`, `"prompt_entropy"`, `"results"` keys
**Data Exposure Class:** full scanner configuration (`/settings` exposes active scanner list, model names, thresholds, embedding API keys), prompt scan history (LRU cache of 100 recent scans), YARA rule paths, vector DB collection names, embedding API key if stored in config
**Known CVEs:** none; project in alpha/experimental state
**Default Credentials:** none
**Notes:** Flask server bound to `0.0.0.0:5000` — the 0.0.0.0 binding means any internet-exposed Docker host running Vigil has the API open to the world. The `/settings` endpoint returns the current server config including the embedding model configuration, which may include the OpenAI API key used for embeddings. The `/add/texts` endpoint writes directly to the vector DB — writable without auth. The project is alpha/experimental and explicitly not production-ready. LRU cache (capacity 100) stores recent prompt analysis results — readable by anyone who calls `/analyze/prompt` on a cached input. FP risk on `"vigil"` + port 5000: moderate — "vigil" is a common English word; combine with `/analyze` path or `"prompt injection"` body match.

---

## Summary Table

| Platform | Category | Default Port | Auth Default | Primary Signal | Priority |
|---|---|---|---|---|---|
| LlamaGuard 3 | Safety Classifier (via model server) | 8000/11434 | off | `"Llama-Guard"` in `/v1/models` | MEDIUM — surfaces in existing model-server surveys |
| NeMo Guardrails | Guardrail API | 8000 | off | `GET /v1/rails/configs` | HIGH — unique endpoint, no auth |
| Lakera Guard | Commercial Guardrail | 443/unknown | on (SaaS), unknown (self-host) | `Server: lakera` header | LOW-MEDIUM — self-host rare |
| Guardrails AI | Guardrail API | 8000 | off | `GET /guards` → JSON array | HIGH — no auth, guard defs exposed |
| LLM Guard | Scanner API | 8000 | off | `"LLM Guard API"` in `/swagger.json` | HIGH — auth optional, scanner config exposed |
| Rebuff | Injection Detector | 3000 | off (default creds risk) | `injectionScore` field in `/api/detect` | MEDIUM — archived, default creds risk |
| ShieldLM | Safety Classifier (via vLLM) | 8000 | off | `"ShieldLM"` in `/v1/models` | LOW — research/internal deployments only |
| Llama-Recipes | Demo code | 5000/8000 | off | `"llama-recipes"` in body | LOW — accidental exposure only |
| OpenShield | AI Firewall | 8080 (API), 8085 (Adminer) | on (API), off (Adminer) | Adminer on 8085 | MEDIUM — archived, Adminer exposure |
| PromptGuard | Safety Classifier (via wrapper) | 8000 | off | `"Prompt-Guard"` in `/v1/models` | MEDIUM — part of LlamaFirewall suite |
| AIShield | Enterprise AI Security | unknown | on | `"aishield"` + `"guardian"` conjunct | LOW — enterprise, no self-service |
| Vigil | Injection Scanner | 5000 | off | `GET /settings` → scanner config JSON | HIGH — no auth, config+cache fully exposed |
