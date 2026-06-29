# Cat-33 Expanded -- OSS Guardrail Platform Research
Date: 2026-06-29
Source: OSINT agents (web/GitHub, no active probing)

## Platform Inventory

### LLM Guard (protectai/llm-guard)

- **Port:** 8000, `laiyer/llm-guard-api:latest`
- **Command:** `uvicorn app.app:create_app --host=0.0.0.0 --port=8000`
- **Auth:** `AUTH_TOKEN` env var. DEFAULT = empty string. Bearer check compares against `""` -- any request with no token OR empty bearer passes.
- **Bind:** `0.0.0.0` (explicit in uvicorn startup)
- **Unauth endpoints:** `GET /`, `GET /healthz`, `GET /readyz`; `/analyze/prompt`, `/scan/prompt`, `/analyze/output` when AUTH_TOKEN empty
- **Prometheus:** `/metrics` -- separate auth from API layer. Always open in default config.
- **Fingerprint:** `GET /` -> `{"name":"LLM Guard API"}` -- CLEAN, vendor-unique
- **Best dork:** `http.html:"LLM Guard API" port:8000`
- **Scanner -1.0 tell:** When model weights not loaded, all scanners return -1.0. is_valid=true always. Null guardrail pattern.
- **CORS:** `allow_origins=['*']` hardcoded
- **Notable:** rate-limit disabled by default; X-Forwarded-For spoofable

### NeMo Guardrails (NVIDIA/NeMo-Guardrails)

- **Port:** 8000, commands: `nemoguardrails server --config ./config`
- **Auth:** NONE. Zero auth decorators. 0.0.0.0 bind HARDCODED in `cli/__init__.py:212` -- no CLI flag or env var to override.
- **Key unauth endpoints:**
  - `GET /openapi.json` -> full spec, `info.title="Guardrails Server API"`
  - `GET /v1/rails/configs` -> array of config IDs (policy names)
  - `POST /v1/chat/completions` -> chat with guardrails (unauth)
  - `GET /v1/challenges` -> red team prompt corpus
  - `GET /v1/models` -> model list
- **Fingerprint:** `GET /openapi.json` -> `"title":"Guardrails Server API"` -- vendor-unique
- **Best dork:** `http.html:"Guardrails Server API" port:8000` (0 hits currently -- not indexed)
- **Actions server:** Port 8001 when actions enabled (second unauth surface)
- **Config ID attack:** enumerate rail IDs -> craft inputs targeting gaps between loaded rails

### Guardrails AI (guardrails-ai/guardrails-api)

- **Port:** 8000
- **Auth:** OpenAPI spec declares ApiKeyAuth BUT implementation has ZERO enforcement. CORS `allow_origins=['*']`. Optional `GR_MIDDLEWARE_FILE_PATH` for custom auth.
- **Docker bind:** `0.0.0.0` in Dockerfile CMD
- **Key unauth endpoints:**
  - `GET /health-check` -> `{"status":200,"message":"Ok"}` (integer status, not string)
  - `GET /guards` -> full guard configurations + validator logic
  - `GET /guards/{id}/validate` -> trigger validation
  - `GET /openapi.json` -> spec with `info.title="Guardrails API"`
- **Fingerprint:** `/health-check` path (not `/health`) + `info.title` in openapi.json
- **Best dork:** `http.html:"/health-check" http.html:"Guardrails API" port:8000` (0 hits -- not widely deployed)
- **CVEs:** HiddenLayer-2024-09 (eval() injection in RAIL XML); CVE-2026-45758 (supply chain)

### Vigil (deadbits/vigil-llm)

- **Port:** 5000
- **Auth:** NONE. Flask with zero auth decorators. No API key mechanism in codebase.
- **Bind:** 0.0.0.0
- **Key unauth endpoints:**
  - `GET /settings` -> full server config dict
  - `POST /analyze/prompt` -> `{prompt_entropy, uuid, status, results, elapsed, cached}`
  - `POST /analyze/response`, `POST /canary/add`, `POST /canary/check`, `POST /add/texts`
- **Fingerprint:** `prompt_entropy` field in JSON response -- vendor-unique
- **Best dork:** `http.html:"prompt_entropy" http.html:"elapsed" port:5000` (0 hits -- no Docker image, Shodan-dark)
- **Docker:** No official image. Builds are ad-hoc from source.

### Arthur GenAI Engine (arthur-ai/arthur-engine)

- **Port:** 3030 (env: `GENAI_ENGINE_PORT`)
- **Auth:** `GENAI_ENGINE_ADMIN_KEY=changeme123` (default in source); `changeme_genai_engine_admin_key` (compose template)
  - `ALLOW_ADMIN_KEY_GENERAL_ACCESS=enabled` -- admin key valid for ALL endpoints
  - PostgreSQL on 5435: `postgres/changeme_pg_password`, db `arthur_genai_engine`
- **Unauth endpoints:**
  - `GET /health` -> `{"message":"ok","build_version":"X.Y.Z"}`
  - `GET /api/v2/engine-config` -> `{"demo_mode":bool}`
  - `GET /api/v2/display-settings` -> `{"chatbot_enabled":bool,...}`
  - `GET /docs` -> Swagger UI titled "Arthur GenAI Engine - Swagger UI"
  - `POST /api/v2/tenant/signup` (when demo_mode=true) -> issues live API key unauthed
- **Best dork:** `http.title:"Arthur GenAI Engine - Swagger UI"` -- 6 AWS hits (stale at survey time)
- **MIT OSS**, 50K+ Docker pulls

### Rebuff (protectai/rebuff)

- **Port:** 3000 (Next.js)
- **Auth:** ON by default (Supabase session + Bearer API key)
- **Status:** Largely abandoned (last meaningful commits 2023)
- **Dork confidence:** LOW -- unique fields only in JS bundle, not raw HTTP
- Skip for active survey; auth-on and dead project

### Enkrypt AI Secure MCP Gateway

- **Port:** 8001 (admin REST API, FastAPI)
- **Auth:** `apikey` header (256-char auto-generated; no static default)
- **Unauth on 8001:** `GET /health`, `GET /docs`, `GET /openapi.json`
- **Best dork:** `http.title:"Enkrypt Secure MCP Gateway API" port:8001` (0 hits -- low adoption)
- **Sandbox:** disabled by default -- MCP tools execute in host context
- **Docker:** `enkryptai/secure-mcp-gateway:v2.2.1-1`

## Enterprise/SaaS Summary (not surveyed)

| Platform | Self-hosted | Auth | Notes |
|----------|-------------|------|-------|
| Aporia | Enterprise K8s | X-APORIA-API-KEY | No public fingerprint |
| WhyLabs Secure | Yes (private registry) | CONTAINER_PASSWORD required | Min 16vCPU |
| RIME AI Firewall | Enterprise K8s | API token | Port 5002, /v1/rime-info |
| Lakera Guard | Enterprise (Triton) | Contract | Ports 8000/8001/8002 |
| Patronus AI | Enterprise K8s | OAuth2/OIDC | Multiple NodePort 8000 |
| Prompt Security | SaaS-only | -- | Israeli vendor |
| Alibaba CM | SaaS-only | -- | No self-hosted |
| Baidu ContentCensor | SaaS-only | -- | No self-hosted |

## Chinese Market Gap

No Chinese-market equivalent of LLM Guard or NeMo Guardrails exists as
open-source self-hosted. Vendors (Alibaba, Baidu) are API-only SaaS.
Single observed self-hosted Chinese guardrail: Guoshun Tech 大模型安全护栏检测平台
at 43.134.236.109:8080 (built with Coze Code/ByteDance).
