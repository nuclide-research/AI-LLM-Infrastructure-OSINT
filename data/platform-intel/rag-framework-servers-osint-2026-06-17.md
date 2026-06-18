---
type: platform-intel
category: rag-framework-servers
date: 2026-06-17
status: stage-minus-1-complete
---

# Cat-RAG-Framework-Servers: Stage -1 Pre-Assessment OSINT

_NuClide Research · 2026-06-17 · slug `rag-framework-servers`_

The RAG **framework** tier (LlamaIndex, Haystack, LightRAG, Microsoft GraphRAG) is
the pipeline ABOVE the vector DBs. Distinct from Cat-34 RAG-**builders**
(R2R/Cognita/RAGFlow, 2026-06-13). Four parallel OSINT lanes, research-only, no
live probing. Each leaks system prompts, retrieval logic, ingested documents, and
embedded provider keys even when the underlying vector store is locked.

---

## Headline posture (auth-on-default thesis check)

| Platform | Default posture | Server reality | aimap FP | Verification primitive |
|---|---|---|---|---|
| **LlamaIndex** | **Tier-A** (no auth concept; CORS `*`) | Real: LlamaIndex Server :8000, llama_deploy apiserver :4501 | **GAP, build** | `GET :4501/status` -> `max_deployments`+`deployments[]`+`status:healthy` |
| **Haystack / hayhooks** | **Tier-A\*** (no auth primitive ships) | Real: hayhooks :1416/:1417, legacy rest_api :8000 | **GAP, build** | `GET /status` -> `{"status":"Up!","pipelines":[...]}` |
| **LightRAG** | **Tier-A\*** (auth exists, OFF default; `auth_mode:"disabled"` self-reports) | Real: lightrag-server :9621 | **EXISTS, harden** | `GET :9621/health` -> `status:healthy`+`core_version`+`webui_title`+`auth_mode:disabled` |
| **Microsoft GraphRAG** | **Tier-B as-designed / Tier-C on misdeploy** | Core = CLI-only (negative); accelerator FastAPI behind APIM; community wrappers :8000 unauth | **build (server forms only)** | `GET /manpage/openapi.json` -> `info.title=="GraphRAG"` + `/graph/graphml/{index_name}` route |

**Thesis read:** three of four are auth-off-default (Tier-A/A*), confirming the
thesis on a new platform class before a single probe. GraphRAG is the interesting
case. Its core is CLI-only (a publishable negative, like Aider/BabyAGI), and its
*server* form pushes auth to an APIM gateway the app itself does not enforce, so a
direct-to-ingress misdeploy collapses Tier-B to Tier-C.

---

## Per-platform intel

### LlamaIndex (Tier-A)
- **Ports:** 8000 (LlamaIndex Server / create-llama), 4501 (llama_deploy apiserver control plane).
- **Verification primitive:** `GET :4501/status` -> 200 JSON, conjunction `max_deployments` + `deployments[]` + `status:"healthy"`. Unique + unauth-reachable.
- **High-value:** `/api/chat` (LLMjacking + context leak, HIGH), `/api/files/data/*` (RAG source-doc read + traversal risk, HIGH), apiserver `/deployments` POST (unauth workflow execution, CRITICAL if write reachable).
- **Dorks:** `http.html:"/api/chat/config"` (low FP), `http.title:"LlamaIndex" http.html:"/api/chat"` (low FP), `port:4501 http.html:"deployments"` (low FP).
- **CVEs:** all library-level, not server-auth. CVE-2025-1793 (SQLi, 9.8), CVE-2024-3271 (cmd-inj), CVE-2024-23751 (SQLi). No server-exposure nuclei template (gap).
- **Shadow ports:** 11434 (Ollama), 6333 (Qdrant), 8080 (Weaviate), 3000 (Next.js UI), 6379.
- **NEGATIVE SPACE:** llama_deploy is **deprecated**; live population may be shifting to LlamaAgents/`llamactl` whose default auth was NOT confirmable. JSON roots are Shodan-dark -> Censys/active-scan for control-plane tier.

### Haystack / hayhooks (Tier-A*)
- **Ports:** 1416 (hayhooks REST), 1417 (hayhooks MCP), 8000 (legacy rest_api).
- **Verification primitive:** `GET /status` -> `{"status":"Up!","pipelines":[...]}`. The literal `"Up!"` + pipelines array is hayhooks-unique and leaks every pipeline name in one read. Legacy: `/openapi.json` title `"Haystack REST API"`. `GET /initialized`->`true` is generic, must be title-gated.
- **High-value:** `POST /deploy_files` (**unauth arbitrary code execution by design, CRITICAL**), `POST /deploy-yaml` (HIGH/CRITICAL), `POST /undeploy/{name}` (destructive, HIGH), pipeline `/run` + `/v1/chat/completions` (CVE-2024-41950 SSTI->RCE chain on <=2.3.0).
- **Dorks:** `http.title:"Hayhooks"`, `http.html:"Hayhooks makes it easy to deploy and serve Haystack pipelines"` (very low FP), `http.title:"Haystack REST API"` (legacy fleet).
- **CVEs:** CVE-2024-41950 SSTI->RCE (7.5, fixed 2.3.1); Zip-Slip RCE in farm-haystack 1.x (no CVE, EOL unpatched). No published advisories for hayhooks itself; no nuclei template (gap).
- **Shadow ports:** 1416/1417 first (niche, under-indexed), 9200 (OpenSearch), 8080/50051 (Weaviate), 6333 (Qdrant), 19530 (Milvus).
- **NEGATIVE SPACE:** OpenAI-compat route prefix unconfirmed; deepset Cloud self-host auth (likely Tier-C) not source-confirmed. Open findings apply to OSS hayhooks/rest_api only.

### LightRAG (Tier-A*, roadmap said Tier-A, CORRECTED)
- **Ports:** 9621 (API + WebUI + Ollama-emulation, all same port).
- **Verification primitive:** `GET :9621/health` -> `status:healthy` + `core_version` + `webui_title` + **`auth_mode:"disabled"`**. The `auth_mode` field is a machine-readable auth-state decoder; it confirms platform AND unauth in one read, no exfiltration. Names ARE the finding.
- **High-value:** `/query`,`/query/stream` (RAG-query exfil of ingested docs + system prompts, HIGH), `/documents` (full corpus inventory, HIGH), `/graphs` (knowledge-graph dump, HIGH), `/documents/upload` (corpus poisoning + CVE-2025-6773 traversal sink, HIGH), Ollama-emulation -> LLMjacking of operator's provider (HIGH, no key disclosure).
- **Dorks:** `port:9621 "status":"healthy" "core_version"` (low FP), `port:9621 "auth_mode"` (pre-selects unauth subpop), `http.html:"LightRAG Server API"` (stable OpenAPI title).
- **CVEs:** CVE-2025-6773 path-traversal (4.8, fixed 1.3.8), CVE-2026-30762 hardcoded JWT secret (`lightrag-jwt-default-secret-key!`, fixed 1.4.13, NVD RESERVED), CVE-2026-39413 JWT alg:none (fixed 1.4.14). No nuclei template, no prior population survey. **Greenfield**.
- **Shadow ports:** 11434 (Ollama, top priority, paired LLM often itself unauth), 5432 (pgvector), 7474/7687 (Neo4j), 6333 (Qdrant), 19530 (Milvus), 6379, 27017.
- **aimap action:** existing 9621 FP likely keys on port+title only -> FP on renamed WebUI, misses auth-state. HARDEN: anchor on `/health` json_field `core_version`+`webui_title`, wire `auth_mode` straight into auth_status.
- **NEGATIVE SPACE:** no published population count; default `WEBUI_TITLE` not pinned (configurable); `/health` may be Shodan-dark (route to Censys); exact graph/document route strings need `/docs` pull at scan time.

### Microsoft GraphRAG (Tier-B designed / Tier-C misdeploy)
- **Server reality:** **microsoft/graphrag core = CLI/library only (publishable negative).** Real HTTP surface = `Azure-Samples/graphrag-accelerator` (FastAPI on AKS behind APIM) + community wrappers (`ms-graphrag-api`, uvicorn :8000 no-auth).
- **Auth:** accelerator pushes auth to APIM `Ocp-Apim-Subscription-Key` at the gateway; the FastAPI app enforces NO app-layer auth on data routes (`subscription_key_check` is a documented no-op placeholder), CORS `*`. Direct-to-ingress exposure (APIM not in Internal VNet mode) = fully unauth Tier-C.
- **Verification primitive:** `GET /manpage/openapi.json` (renamed from `/openapi.json`!) -> `info.title=="GraphRAG"` + `/graph/graphml/{index_name}` + `/source/report/{index_name}/{report_id}` routes. **LightRAG disambiguation is mandatory.** Exclude if title contains "LightRAG" or `/webui/` route present.
- **High-value:** `GET /graph/graphml/{index_name}` (whole knowledge-graph exfil, HIGH), `POST /query/global|local` (corpus exfil + Azure-OpenAI LLMjacking, HIGH), `GET /source/text/*` (raw source chunks, HIGH).
- **Dorks:** `http.html:"/manpage/openapi.json"` (highest-signal, near-zero collision), `http.html:"Ocp-Apim-Subscription-Key required"` (placeholder-auth 400 string), `http.title:"LightRAG Server API"` (INVERSE/exclusion dork, subtract LightRAG to keep the count honest).
- **CVEs:** none found (no GHSA/CVE/KEV). Bypass-APIM misconfig class is unpublished. Open ground.
- **Shadow ports:** 8000 (wrapper), 80/8080 (AKS ingress if LB-exposed), 443 (APIM), 8501 (Streamlit unified-search-app).
- **NEGATIVE SPACE:** suspect near-zero direct accelerator exposure (APIM-default + "demo not supported"); real exposure tier is community :8000 wrappers; no host evidence of the bypass-APIM path yet.

---

## Cross-cutting findings for the survey

1. **GraphRAG/LightRAG dork collision is the central FP trap.** "graphrag" as a token catches LightRAG (which brands itself a GraphRAG server), MS GraphRAG wrappers, and marketing pages. The survey MUST run an exclusion dork (`http.title:"LightRAG Server API"`) and subtract, per Insight #15 (~50% rule) and Insight #102 (dork-stage schema anchor for name-collision platforms). This is a live test of #102 on a third platform class.
2. **Three Shodan-dark JSON-root tiers** (LlamaIndex :4501, hayhooks JSON, LightRAG /health) route to Censys (0b) / scanner (0c), not the Shodan web UI. Expect web-UI dork hits near 0 for JSON-field tokens. That is a logged result, not absence.
3. **Two as-designed unauth-RCE surfaces** (hayhooks `/deploy_files`, LlamaIndex apiserver `/deployments` write) are CRITICAL by design, not misconfig. Restraint ethic: confirm reachability and enumerate, do NOT execute.
4. **aimap fingerprint gaps:** build LlamaIndex (2 probes), Haystack/hayhooks (1416/1417/8000), GraphRAG-accelerator (`/manpage/openapi.json`); harden existing LightRAG 9621.
5. **Ollama is the dominant co-deploy** for LightRAG (11434); shadow-sweep 11434 on every confirmed LightRAG host; Insight #12 (operators who ship one service auth-off ship others auth-off).

## DCWF tags
672 (T&E): K7044 (V&V tools, the new aimap FPs), T5919 (adversarial test op env, verify primitives). 733 (Risk/Ethics): T5854/K7040 (PHI/PII surface in ingested corpora, names-only).
