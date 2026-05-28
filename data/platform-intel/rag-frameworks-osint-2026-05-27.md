# RAG Framework / Private AI Platform OSINT — Pre-Survey Intelligence
**Date:** 2026-05-27
**Purpose:** Tune dork queries, understand auth posture, identify verification probes, document data exposure classes before Shodan harvests.
**Scope:** 15 platforms — RAG pipelines, private document Q&A, self-hosted AI search, GraphRAG implementations.
**Status:** Pre-survey. No active probing conducted.

**Already covered (not duplicated here):**
- Open WebUI — surveyed, cat-01 LLM orchestration corpus
- LangChain, LlamaIndex — frameworks only, no persistent server exposure
- Chroma, Qdrant, Weaviate, Milvus — surveyed, cat-02 vector DBs
- OpenHands — surveyed, cat-09 code assistants

---

## AnythingLLM

**Category:** Private AI / Document Q&A / All-in-One RAG Workspace
**Default Ports:** 3001 (web UI + API)
**Auth Default:** off in single-user mode (password protect is optional toggle; ships unlocked); multi-user mode requires account creation
**Shodan Dork (primary):** `http.title:"AnythingLLM" port:3001`
**Shodan Dork (secondary):** `port:3001 http.html:"anythingllm" http.html:"workspace"`
**Verification Probe:** `GET /api/v1/workspace` with `Authorization: Bearer <token>` → 200 + `{"workspaces":[...]}` with `slug`, `chatModel`, `openAiTemp` fields; unauthenticated instances return 200 on `/` with React bundle containing `AnythingLLM` string
**Data Exposure Class:** Document contents uploaded to workspaces, full chat history, connected LLM API keys (OpenAI, Anthropic, etc.) stored in backend config, embedded document chunks, workspace system prompts
**Known CVEs:** CVE-2026-21484 — username enumeration via differential error messages in password recovery endpoint (medium; fixed in commit e287fab)
**Default Credentials:** none (single-user: optional password; multi-user: first account becomes admin)
**Notes:** Single-user mode ships with no auth by default — most Docker deployments skip the password toggle. The `/api/v1/` path with Bearer token is distinctive. FP risk on port 3001 is high (many Node/React apps use it); conjunct with `AnythingLLM` HTML string. Desktop version binds to localhost only; Docker deployments bind to 0.0.0.0.

---

## RAGFlow

**Category:** RAG Pipeline / Enterprise Document Understanding
**Default Ports:** 80 (nginx frontend, proxied to internal 9380 Python API)
**Auth Default:** on (signup/login required; default admin account: `admin@ragflow.io` / `admin` — must be changed on first login)
**Shodan Dork (primary):** `http.html:"ragflow" port:80`
**Shodan Dork (secondary):** `http.html:"RAGFlow" http.favicon.hash:-1467534538`
**Verification Probe:** `GET /api/v1/datasets` → 401 with `{"code":401,"message":"authentication required"}` confirms RAGFlow; fields `chunk_count`, `document_count`, `parser_config`, `llm_setting` in 200 responses are distinctive
**Data Exposure Class:** Indexed document chunks (deep OCR/layout parsing of PDFs/slides), knowledge bases, chat session history, API keys for connected LLM providers, tenant API tokens (CVE-2024-12880: cross-tenant token leak)
**Known CVEs:** CVE-2024-12433 (RCE via pickle deserialization + hardcoded RPC AuthKey, fixed v0.14.0); CVE-2024-12450 (SSRF + arbitrary file read via web_crawl endpoint); CVE-2024-12880 (partial account takeover — cross-tenant API token access); CVE-2024-12871 (XSS via malicious PDF upload); CVE-2025-27135 (SQL injection, affects ≤0.15.1)
**Default Credentials:** `admin@ragflow.io` / `admin` (first-run default; forced change prompt exists but not enforced)
**Notes:** The internal port 9380 may be exposed directly in misconfigured deployments. RPC service (internal) used a hardcoded AuthKey — CVE-2024-12433 is a critical pre-auth RCE chain. `doc_aggs`, `vector_similarity`, `term_similarity` fields in `/api/v1/retrieval` responses are RAGFlow-specific. FP risk on port 80 is very high; use `ragflow` body string conjunct.

---

## LightRAG

**Category:** GraphRAG / Knowledge-Graph RAG Pipeline
**Default Ports:** 9621 (FastAPI server)
**Auth Default:** off (ships fully open; API key and JWT auth exist as optional config via env vars `AUTH_ACCOUNTS`, `TOKEN_SECRET`)
**Shodan Dork (primary):** `port:9621 http.html:"LightRAG"`
**Shodan Dork (secondary):** `port:9621 http.html:"/query" http.html:"lightrag"`
**Verification Probe:** `GET /health` → 200 + JSON with operational state; `POST /query` → 200 + response with `references` array and `enable_rerank` field — both are LightRAG-specific; `/docs` exposes Swagger UI
**Data Exposure Class:** Knowledge graph nodes and edges derived from ingested documents, query results with full retrieved chunks, document upload queue via `/documents/scan`, arbitrary file read if inputs directory is exposed
**Known CVEs:** No CVEs on record as of 2026-05-27
**Default Credentials:** none
**Notes:** Ollama compatibility endpoints (`/api/chat`, `/api/generate`) are whitelisted from API key checks by default — even when key auth is enabled, Ollama-compatible paths remain open. Health check endpoint at `/health` is always unauthenticated. The `track_id` field in upload responses and `references` array in query responses are distinctive LightRAG signals. EMNLP 2025 paper origin (HKUDS lab) means academic/research deployments are common.

---

## PrivateGPT

**Category:** Private AI / Document Q&A / Offline RAG
**Default Ports:** 8001 (FastAPI, uvicorn)
**Auth Default:** off (`auth: enabled: false` in default settings.yaml)
**Shodan Dork (primary):** `port:8001 http.html:"PrivateGPT"`
**Shodan Dork (secondary):** `port:8001 http.html:"/v1/completions" http.html:"private"`
**Verification Probe:** `GET /docs` → 200 + Swagger UI listing `/v1/completions`, `/v1/chat/completions`, `/v1/embeddings`, `/v1/ingest/file` — the `/v1/ingest/file` endpoint does not exist in standard OpenAI, making it a clean PrivateGPT identity signal
**Data Exposure Class:** Ingested document contents (stored locally via vector DB), chat history, model context (system prompts), full document text retrievable via `/v1/ingest/list` and chunk endpoints
**Known CVEs:** No CVEs on record as of 2026-05-27
**Default Credentials:** none (auth disabled; when enabled: username `secret`, password `key` via Basic auth — hardcoded in default config)
**Notes:** The encoded credential `Basic c2VjcmV0OmtleQ==` in settings.yaml is a known default — any instance with auth enabled but default creds is trivially bypassed. OpenAI-compatible API surface means FP risk is elevated; conjunct with `/v1/ingest` path or `PrivateGPT` HTML string. Gradio UI accessible at root when UI profile is active.

---

## txtai

**Category:** AI Search / Semantic Indexing / RAG Pipeline Framework
**Default Ports:** 8080 (API service; documentation examples reference 8000 for some profiles)
**Auth Default:** off ("the default implementation of an API service runs via HTTP and is fully open")
**Shodan Dork (primary):** `port:8080 http.html:"txtai"`
**Shodan Dork (secondary):** `port:8080 http.html:"/workflow" http.html:"txtai"`
**Verification Probe:** `GET /docs` → 200 + FastAPI Swagger UI with `/search`, `/batchsearch`, `/add`, `/index`, `/upsert`, `/workflow` endpoints — the `/workflow` endpoint is txtai-specific and not present in generic FastAPI deployments
**Data Exposure Class:** Indexed document embeddings and full text, search query history, workflow pipeline configurations, any data ingested via `/add` or `/upsert` endpoints
**Known CVEs:** No CVEs on record as of 2026-05-27
**Default Credentials:** none
**Notes:** When auth is configured, token is passed as `Authorization: Bearer <sha256-token>`. No auth by default means any instance reachable on the network exposes all indexed content. FP risk on port 8080 is very high; `txtai` body string is the discriminating signal. NeuML project; primarily academic/research deployments.

---

## Cognita

**Category:** RAG Pipeline / Production RAG Framework
**Default Ports:** 8000 (backend FastAPI), 5001 (frontend)
**Auth Default:** off (compose.env ships with `LOCAL=true`, placeholder API keys, no JWT configured; auth is not wired in default local deployment)
**Shodan Dork (primary):** `port:8000 http.html:"cognita" http.html:"truefoundry"`
**Shodan Dork (secondary):** `port:8000 http.html:"/collections" http.html:"cognita"`
**Verification Probe:** `GET /` → 200 or `GET /docs` → FastAPI Swagger listing `/collections`, `/data_sources`, `/apps` endpoints; `truefoundry` string in page body or JS bundle confirms operator
**Data Exposure Class:** RAG collections and their document contents, data source credentials (database connection strings, S3 credentials stored in pipeline config), query results with retrieved chunks, model configurations
**Known CVEs:** No CVEs on record as of 2026-05-27
**Default Credentials:** `POSTGRES_USER=postgres` / `POSTGRES_PASSWORD=test` in default compose.env; `UNSTRUCTURED_IO_API_KEY='test'`; `INFINITY_API_KEY='test'`
**Notes:** Default deployment uses test credentials throughout. The `collections` and `data_sources` API paths are Cognita-specific. FP risk on port 8000 is very high; require `cognita` or `truefoundry` body string. The TrueFoundry cloud version (cognita.truefoundry.com) is separate from self-hosted; this survey targets self-hosted instances.

---

## R2R (SciPhi)

**Category:** Production RAG Framework / Agentic Retrieval System
**Default Ports:** 7272 (REST API)
**Auth Default:** off by default (`require_authentication: false` in r2r.toml); when enabled, default admin is `admin@example.com` / `change_me_immediately`
**Shodan Dork (primary):** `port:7272 http.html:"r2r"`
**Shodan Dork (secondary):** `port:7272 http.html:"/v3/" http.html:"SciPhi"`
**Verification Probe:** `GET /v3/health` → 200 + `{"results":{"response":"ok"}}` or similar; `GET /v3/system/settings` → exposes config when auth disabled; `/v3/` path prefix with endpoint pattern `/v3/documents`, `/v3/collections`, `/v3/graphs` is R2R-specific
**Data Exposure Class:** Ingested document contents, document collections, knowledge graph data, user accounts list (admin endpoints), full system configuration including connected LLM API keys when auth is disabled
**Known CVEs:** No CVEs on record as of 2026-05-27
**Default Credentials:** `admin@example.com` / `change_me_immediately` (publicly documented; users report inability to change — broken flow in some versions)
**Notes:** Auth defaults to false — any instance without explicit `require_authentication: true` is fully open. The `/v3/` path prefix distinguishes R2R from other FastAPI apps on port 7272. Default admin password `change_me_immediately` is publicly documented in the GitHub repo and in user issues. When auth is disabled, `/v3/system/settings` exposes the full config including connected provider API keys.

---

## Kotaemon

**Category:** Document Q&A / RAG Chat UI
**Default Ports:** 7860 (Gradio server)
**Auth Default:** default-creds (`admin` / `admin` — hardcoded in first-run setup)
**Shodan Dork (primary):** `port:7860 http.html:"kotaemon"`
**Shodan Dork (secondary):** `port:7860 http.html:"Kotaemon" http.html:"gradio"`
**Verification Probe:** `GET /` → 200 + Gradio HTML with `kotaemon` string in page title or body; login prompt with username/password fields — `admin`/`admin` default credentials valid on unpatched instances
**Data Exposure Class:** All uploaded documents and their indexed chunks, chat sessions across all users (admin view), connected LLM API key configs, multi-user document collections (private and public)
**Known CVEs:** No CVEs on record as of 2026-05-27
**Default Credentials:** `admin` / `admin`
**Notes:** Default admin/admin is well-documented and trivially exploited. Gradio on port 7860 is a shared port with many other apps (Stable Diffusion, Whisper UIs, etc.); `kotaemon` body string is the discriminating signal. FP risk on port 7860 without body filter is very high. Supports SSO (Google, Keycloak) but only when explicitly configured.

---

## Quivr

**Category:** Private AI / Second Brain / Document Q&A
**Default Ports:** 5050 (FastAPI backend uvicorn)
**Auth Default:** on (Supabase JWT required; `AUTHENTICATE=true` default; anonymous access not supported in standard deployment)
**Shodan Dork (primary):** `port:5050 http.html:"quivr"`
**Shodan Dork (secondary):** `port:5050 http.html:"second brain" http.html:"quivr"`
**Verification Probe:** `GET /docs` → FastAPI Swagger UI; `GET /healthz` → 200 confirms service up; unauthenticated API calls return 401 with Supabase JWT error; body containing `quivr` string in Swagger or error response is the identity signal
**Data Exposure Class:** When auth is misconfigured (AUTHENTICATE=false or exposed Supabase anon key): all uploaded brains and documents, full chat history, connected integration credentials; Supabase anon key in frontend JS exposes DB schema if RLS is misconfigured
**Known CVEs:** No CVEs on record as of 2026-05-27
**Default Credentials:** none (Supabase auth required; Supabase anon key is public by design but not a credential)
**Notes:** Quivr's v2 rebranded as "Opiniated RAG" — older self-hosted instances may run the "second brain" version at port 5050. Auth is on by default, but misconfigured RLS on Supabase + exposed anon key = full data leak. The `NEXT_PUBLIC_SUPABASE_URL` in frontend JS is a secondary signal for operator attribution.

---

## Danswer / Onyx

**Category:** Enterprise AI Search / Document QA / Internal Knowledge Base
**Default Ports:** 3000 (nginx → Next.js frontend), 8080 (API server internal)
**Auth Default:** configurable; `AUTH_TYPE=disabled` is a documented valid option; default out-of-box requires first-user registration (no hardcoded creds), but `AUTH_TYPE=disabled` bypasses all auth
**Shodan Dork (primary):** `http.title:"Onyx" port:3000`
**Shodan Dork (secondary):** `http.title:"Danswer" port:3000`
**Verification Probe:** `GET /` → 200 + Next.js app with `Onyx` or `Danswer` in HTML; `GET /api/me` → 401 or 200 with user object; `GET /api/connector/gmail/app-credential` (if Slack/Gmail connectors configured) may expose OAuth credentials
**Data Exposure Class:** When `AUTH_TYPE=disabled`: all indexed documents from connected sources (Slack, Google Drive, Confluence, GitHub, etc.), full chat and search history, connector OAuth tokens, user directory; first-user-registration instances may have weak admin passwords
**Known CVEs:** No CVEs on record as of 2026-05-27
**Default Credentials:** none (first-user registration flow; no hardcoded creds)
**Notes:** `AUTH_TYPE=disabled` is explicitly supported and documented — instances deployed this way are fully open with all connectors readable. The Vespa index (port 8081/19071) and Postgres (5432) are internal-only in standard Docker deployments but may be exposed in misconfigured cloud deployments. Onyx replaced Danswer branding in 2024; both `http.title` dorks are valid. FP risk on port 3000 is very high; require `Onyx` or `Danswer` title match.

---

## Verba

**Category:** RAG App / Document Q&A / Weaviate-native
**Default Ports:** 8000 (FastAPI backend serving Next.js frontend)
**Auth Default:** off (no auth layer; "Verba does not offer any useful API endpoints to interact with the application" per docs — frontend/backend are tightly coupled with no external auth)
**Shodan Dork (primary):** `port:8000 http.html:"Verba"`
**Shodan Dork (secondary):** `port:8000 http.html:"goldenverba" http.html:"weaviate"`
**Verification Probe:** `GET /` → 200 + Next.js + FastAPI app with `Verba` or `goldenverba` in HTML body; `GET /api/get_components` or similar FastAPI endpoint confirms identity
**Data Exposure Class:** All documents loaded into Weaviate, chat conversation history, configured Weaviate API keys in backend environment (visible if env is leaked via misconfigured debug endpoints), OpenAI/Cohere API keys in backend config
**Known CVEs:** No CVEs on record as of 2026-05-27
**Default Credentials:** none
**Notes:** Verba wraps a Weaviate backend; misconfigured deployments may also expose the Weaviate port (8080) separately. The Python package name `goldenverba` is a strong discriminating signal. FP risk on port 8000 is very high; `goldenverba` or `Verba` body string required. No auth is by design for local use — production recommendation is reverse proxy.

---

## DocsGPT

**Category:** Documentation QA / Private AI / Enterprise Knowledge
**Default Ports:** 5001 (Flask/Gunicorn backend); 5173 (Vite frontend in dev)
**Auth Default:** off (no auth on API endpoints in default deployment; API key management endpoint `GET /api/get_api_keys` is accessible without credentials in some versions)
**Shodan Dork (primary):** `port:5001 http.html:"DocsGPT"`
**Shodan Dork (secondary):** `port:5001 http.html:"docsgpt" http.html:"conversation"`
**Verification Probe:** `GET /api/task_status?task_id=test` → 200 + `{"result":"...","status":"..."}` — the `name_job`, `filename`, `formats`, `directory` fields in task responses are DocsGPT-specific; `GET /api/get_api_keys` exposes API key list on unpatched instances
**Data Exposure Class:** Indexed documentation content, chat conversation history, API keys stored in backend (exposed via `/api/get_api_keys` on vulnerable versions), document upload queue, configured LLM provider credentials
**Known CVEs:** CVE-2024-31451 (unauthenticated limited file write in routes.py, fixed v0.8.1); CVE-2025-0868 (unauthenticated RCE, affects v0.8.1–v0.12.0)
**Default Credentials:** none
**Notes:** CVE-2025-0868 is a critical pre-auth RCE affecting a wide version range. The `arc53/DocsGPT` Docker image on Docker Hub is the standard deployment path. `/api/get_api_keys` being unauthenticated is the highest-value probe. FP risk on port 5001 is elevated (Flask apps common); `DocsGPT` or `docsgpt` body string is discriminating.

---

## Ragapp

**Category:** Agentic RAG / Document Q&A / LlamaIndex-based
**Default Ports:** 8000 (unified admin + chat + API)
**Auth Default:** off ("Ragapp container doesn't come with any authentication layer by design")
**Shodan Dork (primary):** `port:8000 http.html:"ragapp" http.html:"/admin"`
**Shodan Dork (secondary):** `port:8000 http.html:"RAGapp" http.html:"llamaindex"`
**Verification Probe:** `GET /admin` → 200 + admin UI (unauthenticated); `GET /docs` → FastAPI Swagger; `GET /api/management/config` → exposes full RAG configuration including connected LLM API keys
**Data Exposure Class:** Full admin interface (document upload, model config, tool config), all indexed document contents, connected LLM API keys (OpenAI key, Anthropic key visible in `/api/management/config`), agentic tool configurations, chat history
**Known CVEs:** No CVEs on record as of 2026-05-27
**Default Credentials:** none (no auth by design)
**Notes:** No auth is an explicit architectural decision — the `/admin` path requires protection at the API gateway layer, which is almost never done in self-hosted deployments. `/api/management` is the high-value path. FP risk on port 8000 is very high; `ragapp` + `/admin` conjunct required. LlamaIndex-based = common research/prototype deployment pattern.

---

## Perplexica

**Category:** AI Search / Private Perplexity Alternative
**Default Ports:** 3000 (Next.js frontend), 3001 (SearXNG-backed search API backend)
**Auth Default:** off (ships with no authentication; "anyone with the URL can use the instance and consume your AI API credits")
**Shodan Dork (primary):** `http.title:"Perplexica" port:3000`
**Shodan Dork (secondary):** `port:3000 http.html:"Perplexica" http.html:"focusMode"`
**Verification Probe:** `POST http://host:3001/api/search` with body `{"query":"test","focusMode":"webSearch","chatModel":{...},"embeddingModel":{...}}` → `focusMode` field in request body is a unique Perplexica signal not present in standard search APIs; `GET /` on port 3000 → HTML with `Perplexica` title
**Data Exposure Class:** All search queries run against the instance, connected LLM API keys (OpenAI, Ollama, Groq, etc. configured in `config.toml`), search history, SearXNG instance URL
**Known CVEs:** No CVEs on record as of 2026-05-27
**Default Credentials:** none
**Notes:** Perplexica devs explicitly advise against public exposure "at the current point of development." The `focusMode` field (`webSearch`, `academicSearch`, `writingAssistant`, `youtubeSearch`, `redditSearch`) in the search API is the strongest identity signal. FP risk on port 3000 is very high; `Perplexica` title is the primary discriminator. SearXNG runs on port 4000 internally.

---

## FreedomGPT

**Category:** Local LLM / Private AI / Uncensored Chat
**Default Ports:** 8080 (llama.cpp HTTP server, internal); Electron app (desktop-only, no network server by default)
**Auth Default:** off (llama.cpp server has no auth; Electron app binds to localhost)
**Shodan Dork (primary):** `port:8080 http.html:"FreedomGPT"`
**Shodan Dork (secondary):** `port:8080 http.html:"freedomgpt" http.html:"llama"`
**Verification Probe:** `GET /` → Electron-served React UI with `FreedomGPT` string; underlying llama.cpp server responds to `POST /completion` or `GET /health`; `FreedomGPT` in HTML body is the primary identity signal
**Data Exposure Class:** If network-accessible: all chat conversations, loaded model identity, system prompt configurations; the uncensored model posture means any data submitted is processed without safety filters
**Known CVEs:** No CVEs on record as of 2026-05-27
**Default Credentials:** none
**Notes:** FreedomGPT is primarily a desktop Electron app (Mac/Windows) — network-facing instances are likely developer/research deployments where the underlying llama.cpp server has been exposed. Shodan population is expected to be small. The `gpt-llama.cpp` API wrapper that FreedomGPT uses can expose an OpenAI-compatible endpoint at port 8080. Low survey priority vs. other platforms on this list.
