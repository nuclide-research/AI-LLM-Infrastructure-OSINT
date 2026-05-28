# RAG Frameworks — Shodan Query Catalog
_Generated: 2026-05-27 from pre-survey OSINT pass (15 platforms)_
_See: data/platform-intel/rag-frameworks-osint-2026-05-27.md for full intel_

**Already covered (not duplicated here):**
- Open WebUI — cat-01 LLM orchestration queries
- Chroma, Qdrant, Weaviate, Milvus — cat-02 vector DB queries

---

## AnythingLLM
**Auth default:** off (single-user mode ships with password protect disabled)
**Exposure class:** Workspace documents, chat history, connected LLM API keys, embedded document chunks

| Label | Query | Rationale | FP Risk |
|-------|-------|-----------|---------|
| primary | `http.title:"AnythingLLM" port:3001` | App sets `<title>AnythingLLM</title>`; port 3001 is the default Docker bind | Low |
| secondary | `port:3001 http.html:"anythingllm" http.html:"workspace"` | Catches instances with non-standard title; workspace string is app-specific | Med |
| identity-probe | `GET /` → React bundle containing `AnythingLLM` string; `GET /api/v1/auth` → 200 with `{"authenticated":true/false}` indicates single-user mode | — |

---

## RAGFlow
**Auth default:** default-creds (`admin@ragflow.io` / `admin`); login required but known creds
**Exposure class:** Indexed document chunks, knowledge bases, chat history, cross-tenant API tokens (CVE-2024-12880); pre-auth RCE via RPC pickle chain (CVE-2024-12433)

| Label | Query | Rationale | FP Risk |
|-------|-------|-----------|---------|
| primary | `http.html:"ragflow" port:80` | RAGFlow serves React SPA on port 80 via nginx; `ragflow` string in bundle | Med |
| secondary | `http.html:"RAGFlow" http.favicon.hash:-1467534538` | Favicon hash avoids port-80 FP flood; RAGFlow sets distinctive favicon | Low |
| tertiary | `port:9380 http.html:"ragflow"` | Internal Python API port exposed directly in misconfigured deployments | Low |
| identity-probe | `GET /api/v1/datasets` → 401 `{"code":401,...}` with `doc_aggs` / `parser_config` fields in 200 responses confirms RAGFlow | — |

---

## LightRAG
**Auth default:** off (open by default; JWT/API key auth is opt-in via env vars)
**Exposure class:** Knowledge graph nodes/edges, indexed document chunks, document upload queue, Ollama-compatible endpoints open even when API key auth is configured

| Label | Query | Rationale | FP Risk |
|-------|-------|-----------|---------|
| primary | `port:9621 http.html:"LightRAG"` | Port 9621 is LightRAG-specific; `LightRAG` string in Swagger/React UI | Low |
| secondary | `port:9621 http.html:"/query"` | `/query` endpoint path appears in Swagger UI loaded on root | Med |
| identity-probe | `GET /health` → 200 + operational JSON; `GET /docs` → Swagger listing `/query`, `/documents/upload`, `/documents/scan` with `references` field in query responses | — |

---

## PrivateGPT
**Auth default:** off (`auth.enabled: false` in default settings.yaml)
**Exposure class:** Ingested documents, full document text via `/v1/ingest/list`, chat history, model context

| Label | Query | Rationale | FP Risk |
|-------|-------|-----------|---------|
| primary | `port:8001 http.html:"PrivateGPT"` | Port 8001 is PrivateGPT default; `PrivateGPT` in Swagger title | Low |
| secondary | `port:8001 http.html:"/v1/ingest"` | `/v1/ingest/file` is PrivateGPT-specific — not in OpenAI API schema | Low |
| identity-probe | `GET /docs` → FastAPI Swagger with `/v1/ingest/file`, `/v1/ingest/list`, `/v1/chunks` paths — `/v1/ingest/*` endpoints do not exist in stock OpenAI-compatible servers | — |

---

## txtai
**Auth default:** off ("default implementation runs via HTTP and is fully open")
**Exposure class:** All indexed document embeddings and full text, search query results, workflow pipeline configs

| Label | Query | Rationale | FP Risk |
|-------|-------|-----------|---------|
| primary | `port:8080 http.html:"txtai"` | txtai string in Swagger/app UI; port 8080 is common but `txtai` discriminates | Med |
| secondary | `port:8080 http.html:"/workflow" http.html:"txtai"` | `/workflow` endpoint is txtai-specific within the FastAPI surface | Low |
| identity-probe | `GET /docs` → FastAPI Swagger listing `/search`, `/batchsearch`, `/add`, `/index`, `/upsert`, `/workflow` — the `/workflow` path is the strongest txtai identity signal | — |

---

## Cognita
**Auth default:** off (default `compose.env` has `LOCAL=true`, no JWT, placeholder test creds)
**Exposure class:** RAG document collections, data source credentials (DB connection strings, S3 keys), query results with retrieved chunks

| Label | Query | Rationale | FP Risk |
|-------|-------|-----------|---------|
| primary | `port:8000 http.html:"cognita" http.html:"truefoundry"` | Both strings appear in the React SPA bundle for Cognita | Low |
| secondary | `port:8000 http.html:"/collections" http.html:"cognita"` | `/collections` API path is Cognita-specific within FastAPI surface | Low |
| identity-probe | `GET /docs` → FastAPI Swagger with `/collections`, `/data_sources`, `/apps` endpoints; `truefoundry` string in page body confirms operator | — |

---

## R2R (SciPhi)
**Auth default:** off (`require_authentication: false` in r2r.toml); default admin `admin@example.com` / `change_me_immediately` when auth enabled
**Exposure class:** Document collections, knowledge graph, user list, full system config including connected LLM API keys (when auth disabled)

| Label | Query | Rationale | FP Risk |
|-------|-------|-----------|---------|
| primary | `port:7272 http.html:"r2r"` | Port 7272 is R2R-specific; `r2r` string in API responses | Low |
| secondary | `port:7272 http.html:"/v3/"` | The `/v3/` path prefix is R2R-specific API versioning | Low |
| identity-probe | `GET /v3/health` → 200 + `{"results":{"response":"ok"}}`; `GET /v3/system/settings` → full config dump when auth disabled | — |

---

## Kotaemon
**Auth default:** default-creds (`admin` / `admin` on first run)
**Exposure class:** All uploaded documents and indexed chunks, chat sessions across all users (admin has global view), connected LLM API key configs

| Label | Query | Rationale | FP Risk |
|-------|-------|-----------|---------|
| primary | `port:7860 http.html:"kotaemon"` | Port 7860 is Gradio default; `kotaemon` string in app HTML | Low |
| secondary | `port:7860 http.html:"Kotaemon" http.html:"gradio"` | Gradio framework string + Kotaemon name; filters Gradio FPs | Low |
| identity-probe | `GET /` → Gradio login page with `kotaemon` in HTML title/body; test `admin`/`admin` credentials | — |

---

## Quivr
**Auth default:** on (Supabase JWT required by default; `AUTHENTICATE=true`)
**Exposure class:** When auth misconfigured: all brains and documents, chat history, Supabase anon key in frontend JS (RLS bypass risk if misconfigured)

| Label | Query | Rationale | FP Risk |
|-------|-------|-----------|---------|
| primary | `port:5050 http.html:"quivr"` | Port 5050 is Quivr backend default; `quivr` string in error/Swagger responses | Low |
| secondary | `port:5050 http.html:"second brain" http.html:"quivr"` | "Second brain" branding appears in older v1 Quivr deployments | Low |
| identity-probe | `GET /docs` → FastAPI Swagger; `GET /healthz` → 200; auth-on instances return 401 on protected endpoints; look for `NEXT_PUBLIC_SUPABASE_URL` leak in frontend JS on port 3000 | — |

---

## Danswer / Onyx
**Auth default:** configurable; `AUTH_TYPE=disabled` documented option; default first-run requires user registration (no hardcoded creds)
**Exposure class:** When `AUTH_TYPE=disabled`: all indexed documents from connected sources (Slack, Google Drive, Confluence, GitHub), connector OAuth tokens, user directory, full chat/search history

| Label | Query | Rationale | FP Risk |
|-------|-------|-----------|---------|
| primary | `http.title:"Onyx" port:3000` | Onyx sets page title; port 3000 is nginx frontend | Low |
| secondary | `http.title:"Danswer" port:3000` | Legacy branding (pre-2024 rename); still deployed in many instances | Low |
| tertiary | `port:3000 http.html:"danswer" http.html:"connector"` | "connector" appears in UI for doc source management — Danswer-specific | Med |
| identity-probe | `GET /api/me` → 401 (auth enabled) or 200 with user object (auth disabled); `GET /api/connector` → connector list when auth disabled | — |

---

## Verba
**Auth default:** off (no auth layer; designed for local use)
**Exposure class:** All documents loaded into Weaviate, chat conversation history, Weaviate/OpenAI API keys in backend environment

| Label | Query | Rationale | FP Risk |
|-------|-------|-----------|---------|
| primary | `port:8000 http.html:"Verba"` | `Verba` string in Next.js/FastAPI app HTML; port 8000 | Med |
| secondary | `port:8000 http.html:"goldenverba"` | PyPI package name `goldenverba` appears in page source/JS bundles | Low |
| identity-probe | `GET /` → Next.js app with `Verba` or `goldenverba` string; Weaviate endpoint `/api/get_components` or similar FastAPI path confirms backend | — |

---

## DocsGPT
**Auth default:** off (no auth on API endpoints in default deployment)
**Exposure class:** Indexed documentation, chat history, API keys via `/api/get_api_keys` (unauthed on vulnerable versions), document upload queue; pre-auth RCE (CVE-2025-0868)

| Label | Query | Rationale | FP Risk |
|-------|-------|-----------|---------|
| primary | `port:5001 http.html:"DocsGPT"` | `DocsGPT` string in React SPA; port 5001 is the Flask backend | Low |
| secondary | `port:5001 http.html:"docsgpt" http.html:"conversation"` | "conversation" appears in DocsGPT chat UI HTML | Low |
| identity-probe | `GET /api/task_status?task_id=test` → 200 + JSON with `name_job`, `filename`, `formats`, `directory` fields — DocsGPT-specific task response shape; `GET /api/get_api_keys` → API key list if unpatched | — |

---

## Ragapp
**Auth default:** off (no auth by design; documented explicit non-feature)
**Exposure class:** Full admin UI access, all indexed document contents, connected LLM API keys visible in `/api/management/config`, agentic tool configs, chat history

| Label | Query | Rationale | FP Risk |
|-------|-------|-----------|---------|
| primary | `port:8000 http.html:"ragapp" http.html:"/admin"` | `/admin` path + `ragapp` string in page source; both ship in default build | Low |
| secondary | `port:8000 http.html:"RAGapp" http.html:"llamaindex"` | LlamaIndex attribution string appears in RAGapp UI/docs | Low |
| identity-probe | `GET /admin` → 200 unauthenticated admin UI; `GET /api/management/config` → LLM API key exposure | — |

---

## Perplexica
**Auth default:** off (ships with no auth; explicit developer advisory against public exposure)
**Exposure class:** All search queries and results, connected LLM API keys in `config.toml`, SearXNG instance configuration, search history

| Label | Query | Rationale | FP Risk |
|-------|-------|-----------|---------|
| primary | `http.title:"Perplexica" port:3000` | Perplexica sets page title; port 3000 is Next.js frontend | Low |
| secondary | `port:3000 http.html:"Perplexica" http.html:"focusMode"` | `focusMode` is a Perplexica-specific API field that appears in frontend source | Low |
| identity-probe | `GET /` → HTML with `Perplexica` title; backend `POST :3001/api/search` with `focusMode` field in body is the functional identity probe — `focusMode` values `webSearch`/`academicSearch`/`writingAssistant` are Perplexica-specific | — |

---

## FreedomGPT
**Auth default:** off (llama.cpp server has no auth; Electron app localhost-only by default)
**Exposure class:** Chat conversations, loaded model identity, uncensored model outputs (no safety filtering on data submitted)

| Label | Query | Rationale | FP Risk |
|-------|-------|-----------|---------|
| primary | `port:8080 http.html:"FreedomGPT"` | `FreedomGPT` string in Electron-served React app; port 8080 is llama.cpp default | Med |
| secondary | `port:8080 http.html:"freedomgpt" http.html:"llama"` | Combined signals reduce FP on general llama.cpp deployments | Low |
| identity-probe | `GET /` → Electron React app with `FreedomGPT` string; underlying llama.cpp at `GET /health` or `POST /completion` — low expected Shodan population | — |
