---
type: survey
---

# RAG Framework Servers: Cross-Cloud Survey (2026-05)

_NuClide Research · 2026-05-04 (in progress)_

> **Status:** Discovery + deep-probe complete (2026-05-04). 169 confirmed cross-cloud, **inverse auth posture vs MCP/LLM-Gateway tier, content endpoints are auth-on at population scale, but `/openapi.json` leaks the API design at 51% of hosts**.

---

## Premise

RAG (Retrieval-Augmented Generation) framework servers sit between vector databases and LLM clients. They orchestrate the document-ingestion → chunking → embedding → retrieval → context-injection pipeline. The vector DB layer below them has already been surveyed (Qdrant, ChromaDB, Milvus tier-2 surveys). The framework layer **above** the vector DB is its own attack surface:

<!-- ksat-tag:auto-generated:start -->
## DCWF KSAT coverage

Auto-derived from DCWF AI work-role rule files (`ksat-tag`).

- **672 (AI Test & Evaluation Specialist):** K7003, K7004, K7044, S7068, S7075, T5858, T5904
- **733 (AI Risk & Ethics Specialist):** K7040, S7067, T5854, T5868, T5893
- **overlap (Common AI KSATs (all 5 roles)):** K108, K1157, K1158, K1159, K22, K6311, K6935, K7003, K942, S7065

<!-- ksat-tag:auto-generated:end -->

- **Embedded prompts**, RAG framework configs include the system prompts and persona instructions used to generate retrieval responses
- **Retrieval logic**, query rewriting, hybrid-search fusion weights, reranker configs
- **Document pipelines**, what corpora the operator has ingested, file paths, ingestion schedules
- **Sometimes operator credentials**, embedding API keys, LLM provider keys for the generation step

The platforms in scope:

| Platform | Default port | Tier | Auth posture |
|---|---|---|---|
| **LlamaIndex** servers | 8000 | A* | FastAPI surface; auth optional |
| **Haystack** (deepset) | 8000 | A* | FastAPI surface; auth optional |
| **LightRAG** | 9621 | A | No auth in default deploy |
| **Microsoft GraphRAG** | varies | A* | Custom HTTP API |
| **AnythingLLM** | 3001 | A* | Multi-user with auth, but `enable_signup` and `enable_first_setup` left on by default in tutorial deployments |
| **RAGFlow** | 9380 | A* | FastAPI; auth optional |
| **PrivateGPT / LocalGPT** | 8001, 8000 | A | No auth in default deploy |

Auth-on-default thesis: LightRAG, PrivateGPT, LocalGPT (no auth concept) → 100% unauth at population scale. AnythingLLM trends moderate (auth concept exists but signup-open is common). Haystack/LlamaIndex/RAGFlow are highly variable, operator-dependent.

---

## Methodology

### Discovery

Same tier-2 cross-cloud pattern as prior surveys: Scaleway 7 + OVH 33 + Linode 36 = 76 prefixes ≈ 3.55M IPs (1,017 deduped CIDRs combined).

**Ports scanned:** 3001 (AnythingLLM), 8001 (PrivateGPT), 9380 (RAGFlow), 9621 (LightRAG). **Port 8000 hits reused from the MCP cross-cloud survey**, ~80K port-8000 IPs already enumerated. No need to re-scan.

### Probe

`data/rag-framework-probe.py` is a multi-platform fingerprint prober. Per (ip, port) it tries port-specific handlers:

| Platform | Probe sequence | Match signature |
|---|---|---|
| **AnythingLLM** | `GET /api/ping` → `GET /api/system/check-token` → `GET /api/system/system-vectors` | `pong` body + system-vectors JSON |
| **Haystack** | `GET /initialized` → `GET /openapi.json` | `{"initialized": ...}` + `haystack`/`document_store` in OpenAPI |
| **LightRAG** | `GET /health` → `GET /api/v1/graph/label/list` or `GET /docs` | health JSON + LightRAG-specific graph API or Swagger HTML |
| **RAGFlow** | `GET /v1/health` → `GET /v1/dataset/list` or `GET /` | RAGFlow-specific data shape |
| **PrivateGPT** | `GET /health` → `GET /openapi.json` | `privategpt`/`PrivateGPT`/`ingest` markers in OpenAPI |
| **LlamaIndex** | `GET /openapi.json` → `GET /api/health` | `llama_index` / `llamaindex` in OpenAPI |

For each confirmed instance, capture: platform, version, document/collection counts (if reachable unauth), auth posture.

### Filters

- **AS63949 honeypot fleet**, apply standard filter
- **MCP cross-survey overlap**, port-8000 hits already in MCP scan; deduped at target-list assembly
- **Auth-required**, record presence with `auth_required: true` but exclude from "exposed-data" enumeration

### Content-class taxonomy

Per confirmed unauth instance, classify by the corpora ingested:

| Class | Examples | Severity |
|---|---|---|
| **Healthcare / clinical** | medical literature, drug databases, EHR-flavored docs | HIGH (HIPAA / GDPR Art. 9) |
| **Legal / regulatory** | case law, statutes, contracts | HIGH (client confidentiality, regulatory) |
| **Financial** | research reports, KYB docs, transaction analytics | HIGH |
| **Personal / consumer** | private notes, journals, diary corpora | HIGH |
| **Internal-business** | invoices, support tickets, customer-correspondence | MEDIUM-HIGH |
| **Technical documentation** | API docs, internal wikis, code documentation | MEDIUM |
| **Public-domain / research** | published papers, public datasets | LOW |

---

## Discovery results

Cross-cloud final. Masscan ports 3001 (AnythingLLM), 8001 (PrivateGPT), 9380 (RAGFlow), 9621 (LightRAG); port 8000 hits reused from MCP cross-cloud survey.

| Source | Probe targets | Confirmed | Notes |
|---|---|---|---|
| Combined tier-2 (3 providers) | 115,195 | **169** | 0.15% confirmation rate |

### By platform (fingerprint-confirmed)

| Platform | Confirmed | Notes |
|---|---|---|
| **PrivateGPT** | **119** (70.4%) | **Caveat:** ~98% are not stock PrivateGPT, they are *custom FastAPI RAG applications* that match on `/health` + the openapi marker but expose distinct service identities (e.g. `Hibrit RAG API v1`, `AI News Publisher API`, `CamV3 Prediction Service`, `MVP Chatbot API`, `Nexus Skill Graph API`, `Docling Ingest API`, `LlamaIndex Chat`). The 119 count is more accurately read as *"custom FastAPI-based RAG implementations exposing FastAPI's standard `/health` and `/openapi.json` endpoints publicly."* |
| **LightRAG** | 19 | Genuine LightRAG instances on port 9621; openapi titles consistently `LightRAG Server API` with 32 routes including `POST /documents/upload`, `POST /documents/scan` |
| **AnythingLLM** | 16 | Genuine AnythingLLM via `/api/ping` returning `pong` |
| **RAGFlow** | 13 | **Significant false-positive rate**, many port-9380 hits are unrelated services (Elasticsearch nodes, IoT router admin panels, GIS services, even one host serving `/etc/passwd` from `/v1/document/list`). Only ~4 of 13 returned authentic RAGFlow JSON shapes (`{"code":0,"message":"success","data":{...,"ragflow":true}}`). |
| **LlamaIndex** | 2 | Distinct from the PrivateGPT bucket; openapi titles named `LlamaIndex Chat` |

---

## Deep-probe content disclosure

After confirming 169 hosts, ran a per-platform deep-content probe (`data/rag-deep-probe-v2.py`) against each, hitting `/openapi.json` + alternate content endpoints (`/v1/projects`, `/v1/ingest/list`, `/api/workspaces`, etc.).

### Universal finding: API-design disclosure via `/openapi.json`

**87 of 169 RAG framework hosts (51%) expose `/openapi.json` publicly.** This is the dominant disclosure pattern, even when the operator gates the actual data-access endpoints, they leave the FastAPI auto-generated route map open. An attacker reading `/openapi.json` gets:

- Full route inventory (paths, methods, parameters, response shapes)
- Pydantic schema definitions for every endpoint's input/output
- Operator's API design conventions (revealing internal naming, business-logic structure)
- Sometimes the `securitySchemes` block declaring the *intended* auth model

Notable openapi titles that self-identify the operator's product:

| Title | Routes | Operator/product clue |
|---|---|---|
| `Hibrit RAG API v1` | 58 | Turkish "Hybrid RAG", production app |
| `AI News Publisher API` | 37 | Content-publishing RAG service |
| `CamV3 Prediction Service` | 36 | Image / camera prediction (CV-3rd-gen?) |
| `LightRAG Server API` | 32 | Stock LightRAG with full document-CRUD route map |
| `FastAPI + llama.cpp + RAG` | 23 | DIY self-host stack |
| `MVP Chatbot API` | 18 | Startup chatbot |
| `Docling Ingest API` | 5 | Docling-based document-ingestion pipeline |
| `Nexus Skill Graph API` | 4 | Skills-graph RAG |
| `RAG Chat API` | 6 | Generic |
| `LlamaIndex Chat` | 4 | Stock LlamaIndex |

### Content endpoints: 100% auth-on at population scale

For the 169 RAG framework instances probed, **content-disclosure endpoints were universally auth-gated**:

| Platform | Endpoint probed | Result |
|---|---|---|
| PrivateGPT | `/v1/ingest/list` | 404 Not Found (endpoint removed in newer versions) |
| LightRAG | `/documents` | `401 "No credentials provided. Please login."` |
| AnythingLLM | `/api/workspaces` | `401 "Missing Authorization Header"` |
| RAGFlow (genuine instances) | `/v1/dataset/list` | Mixed: some require auth, some return `{"code":401,"message":"<Unauthorized>"}` envelope |
| Custom FastAPI RAG | varied | Most returned 401/403; some served the SPA frontend's HTML shell |

**Auth-off-default thesis breaks here.** Unlike the MCP / LLM Gateway tier (97-100% unauth at content endpoints), RAG framework operators consistently auth-gate the data-access paths, even when the health-check / fingerprint endpoint stays open. The platform identity stays exposed (you can fingerprint the framework), but the corpus content is not directly exfiltrable.

---

## Notable findings

### F1: `/openapi.json` route-map disclosure at scale (UNIVERSAL: 87/169 hosts)

Documented above. The recon-value of this is significant: an attacker doesn't need to brute-force routes; the operator publishes them. `securitySchemes` blocks declare which routes intended to require auth, useful for finding routes the operator *didn't* gate.

### F2: Operator self-identification via openapi titles

The custom FastAPI RAG cohort has descriptive `info.title` fields in their openapi specs that disclose the operator's product name and likely business domain. Titles like `Hibrit RAG API v1`, `Nexus Skill Graph API`, `AI News Publisher API` are direct operator-attribution data without needing WHOIS or cert-pivot work.

### F3: Port 9380 false-positive rate is critical

Of 13 hosts fingerprint-classified as RAGFlow, only ~4 returned authentic RAGFlow JSON envelopes. The rest are unrelated services binding port 9380 (Elasticsearch, Magento commerce, IoT routers, GIS WFS endpoints, file-system misconfigs). **Methodology lesson:** port 9380 needs a stricter content-shape validator than `/v1/health` returning JSON. Future RAGFlow surveys should require the `ragflow:true` marker in the response body before counting a host as confirmed.

### F4: Selected genuine RAGFlow instances with content disclosure

Among the ~4 genuine RAGFlow hosts:

- `172.105.96.223:9380`, `139.162.37.233:9380`, `172.232.238.153:9380`, all returned `{"code":0,"message":"success","data":{"dataset_id":"default","embedding_model":"default","ragflow":true,...}}` for `/v1/llm/list`, `/v1/conversation/list`, `/v1/document/list`. Default-tenant exposure; deeper data-CRUD likely auth-gated but the system is enumerable.
- `62.210.145.182:9380`, `/v1/llm/list` returned `{"code":401,"message":"<Unauthorized>"}` JSON envelope, auth-on at the route, but the JSON shape confirms the platform identity.

### F5: `91.134.43.148:3001` AnythingLLM with French SPA frontend

AnythingLLM instance returning a French (`<html lang="fr">`) Single-Page App shell on every probed admin endpoint. Operator-attribution clue: French-speaking deployment.

### F6: `139.162.53.175:3001` AnythingLLM auth-config metadata leak

Returned `{"results":{"RequiresAuth":true,"AuthToken":true,"JWTSecret":true,"StorageDir":"/app/server/storage",...}}` to `/api/setup-complete`, auth IS enforced, and the response confirms it, but the metadata leak (storage path, token presence) is reconnaissance value.

---

## Cross-tier auth-posture comparison

This survey's headline negative finding, framed against the rest of the 2026-05 series:

| Tier | Auth posture at content endpoints | Sample size |
|---|---|---|
| Vector DB (Qdrant / ChromaDB / Milvus) | 84-100% unauth | 142 |
| Inference servers (vLLM / Triton / Ollama) | 100% unauth (no auth concept) | 388 |
| LLM Gateways (LiteLLM / generic OpenAI-compat) | 97.8% unauth-burnable | 1,899 |
| MCP servers | 70/30 auth-on/off split (auth-gated `tools/list`) | 95 |
| **RAG framework servers** | **~100% auth-on at content** | **169** |
| **Datalabel (doccano-dominant)** | **~99% auth-on at content** | **348** |
| Notebooks (Jupyter, university scope) | 0% unauth (PAM/LDAP standard) | 18 |

**The auth-off-default thesis is tier-dependent.** Platforms that ship as "infrastructure for engineers" (vector DBs, inference servers, gateways) consistently default to no-auth and operators keep that default. Platforms that ship as "applications for end-users" (RAG frameworks, labeling tools, notebooks) consistently default to auth-required and operators keep that.

The split tracks with whether the **default audience for the framework is technical/internal vs end-user/customer-facing**. Internal-tooling ships open and stays open at population scale; end-user-tooling ships closed and stays closed.

---

## Negative space

- **`PrivateGPT 119`** is misleading. Most of those hosts are not stock PrivateGPT but custom FastAPI RAG applications that match on a generic `/health` + openapi-existence fingerprint. Future PrivateGPT surveys should require a stricter discriminator (a PrivateGPT-specific route in openapi.json, like `/v1/recipes`) before counting.
- **Port 9380 false-positives** undermined the RAGFlow count. Stricter validator needed.
- **Microsoft GraphRAG**, 0 confirmed in this scan. Likely deployed as private K8s services rather than public VPSes.
- **Haystack**, 0 confirmed. Same K8s-private deployment profile.
- **Stdio-only / local-process RAG**, out of scope for network scanning; entire local-RAG population invisible.

---

## Disclosure plan

For RAG framework hosts where openapi.json discloses operator identity (named API titles, embedded company/product names), pursue **operator-direct contact** via WHOIS / cert pivot. Disclosure framing: "your `/openapi.json` is publicly readable and discloses your API design + business logic; recommend gating it via auth or removing it from production deployments."

The data-access auth posture is already correct on most operators, the disclosure is about the meta-disclosure layer (API design documentation), not the primary data exfil vector.

---

## See also

- [`SYNTHESIS-2026-05.md`](SYNTHESIS-2026-05.md), cross-survey synthesis (auth-posture-by-tier insight)
- [`mcp-cloud-survey-2026-05.md`](mcp-cloud-survey-2026-05.md), opposing-tier finding (97-100% unauth)
- [`llm-gateways-cloud-survey-2026-05.md`](llm-gateways-cloud-survey-2026-05.md), opposing-tier finding (97.8% burnable unauth)
- [`data/rag-framework-probe.py`](../../data/rag-framework-probe.py), discovery probe
- [`data/rag-deep-probe.py`](../../data/rag-deep-probe.py), [`rag-deep-probe-v2.py`](../../data/rag-deep-probe-v2.py), content-disclosure probes

---

## Notable findings

_(populated)_

---

## Cross-reference: vector DB surveys

The vector-DB layer has already been surveyed extensively (`qdrant-cloud-survey-2026-05.md`, `chromadb-cloud-survey-2026-05.md`, `milvus-cloud-survey-2026-05.md`, plus tier-2 expansions). RAG frameworks orchestrate **above** that layer. Where this survey finds a RAG framework on the same host as a previously-surveyed unauth vector DB, it's the same operator's full stack exposed end-to-end, the framework reveals what's in the vector DB, the DB confirms the volume.

Cross-host correlation candidates for the synthesis section:
- Scaleway hosts already in the qdrant-tier2-confirmed.jsonl
- OVH hosts already in chroma-tier2 / milvus-tier2 confirmed
- Linode hosts (small, but worth checking)

---

## Threat classes

1. **Corpus exfil**, what documents the operator has ingested. The collection names alone often disclose business domain (e.g. `legal_corpus`, `patient_records`, `contracts_2024`).
2. **Embedded-prompt + retrieval-logic exfil**, the operator's RAG configuration (system prompts, query rewriting, reranker weights) is proprietary tuning.
3. **API-key leak via config endpoints**, many frameworks expose configuration endpoints that include OpenAI/Anthropic/Cohere keys (HIGH if found).
4. **Document upload abuse**, frameworks with unauth `POST /ingest` allow attackers to **inject documents into the operator's RAG corpus** (poisoning the retrieval pool, affects everything the operator's LLM application returns).
5. **Compute theft via inference endpoints**, frameworks that proxy LLM calls expose the operator's provider keys to anyone who hits `/chat`, `/query`, or equivalent.

---

## Honest negative space

- **Hosted SaaS RAG products** (Vectara, Glean, Pinecone Knowledge, AWS Bedrock KB, etc.), out of scope. Self-hosted only.
- **AnythingLLM auth-enforced instances**, many AnythingLLM operators have configured auth correctly. We expect a non-zero auth-on rate similar to Open WebUI's 99.1% finding.
- **Haystack pipelines without /initialized**, older Haystack versions or custom pipelines may not expose the `/initialized` endpoint we fingerprint on. Underestimate risk for older deployments.

---

## Disclosure plan

For each unauthenticated instance with high-severity content classes (healthcare, legal, financial, personal), draft coordinated-disclosure email per the standard NuClide template. Where the framework reveals operator identity (collection names like `<company>_internal_kb`), pursue direct operator contact via WHOIS / cert-pivot.

---

## See also

- [`SYNTHESIS-2026-05.md`](SYNTHESIS-2026-05.md), companion cross-survey synthesis
- [`FUTURE-SURVEYS.md`](FUTURE-SURVEYS.md), broader unsurveyed roadmap
- [`qdrant-cloud-survey-2026-05.md`](qdrant-cloud-survey-2026-05.md), [`chromadb-cloud-survey-2026-05.md`](chromadb-cloud-survey-2026-05.md), [`milvus-cloud-survey-2026-05.md`](milvus-cloud-survey-2026-05.md), vector-DB-layer companion surveys
- [`data/rag-framework-probe.py`](../../data/rag-framework-probe.py), multi-platform fingerprint prober used for this survey
