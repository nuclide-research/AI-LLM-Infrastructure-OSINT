# RAG Framework Servers — Cross-Cloud Survey (2026-05)

_NuClide Research · 2026-05-04 (in progress)_

> **Status:** Methodology + scaffolding complete. Discovery scan in progress (masscan + probe). Synthesis section will fill as data lands.

---

## Premise

RAG (Retrieval-Augmented Generation) framework servers sit between vector databases and LLM clients. They orchestrate the document-ingestion → chunking → embedding → retrieval → context-injection pipeline. The vector DB layer below them has already been surveyed (Qdrant, ChromaDB, Milvus tier-2 surveys). The framework layer **above** the vector DB is its own attack surface:

- **Embedded prompts** — RAG framework configs include the system prompts and persona instructions used to generate retrieval responses
- **Retrieval logic** — query rewriting, hybrid-search fusion weights, reranker configs
- **Document pipelines** — what corpora the operator has ingested, file paths, ingestion schedules
- **Sometimes operator credentials** — embedding API keys, LLM provider keys for the generation step

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

Auth-on-default thesis: LightRAG, PrivateGPT, LocalGPT (no auth concept) → 100% unauth at population scale. AnythingLLM trends moderate (auth concept exists but signup-open is common). Haystack/LlamaIndex/RAGFlow are highly variable — operator-dependent.

---

## Methodology

### Discovery

Same tier-2 cross-cloud pattern as prior surveys: Scaleway 7 + OVH 33 + Linode 36 = 76 prefixes ≈ 3.55M IPs (1,017 deduped CIDRs combined).

**Ports scanned:** 3001 (AnythingLLM), 8001 (PrivateGPT), 9380 (RAGFlow), 9621 (LightRAG). **Port 8000 hits reused from the MCP cross-cloud survey** — ~80K port-8000 IPs already enumerated. No need to re-scan.

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

- **AS63949 honeypot fleet** — apply standard filter
- **MCP cross-survey overlap** — port-8000 hits already in MCP scan; deduped at target-list assembly
- **Auth-required** — record presence with `auth_required: true` but exclude from "exposed-data" enumeration

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

_(populated as the masscan + probe pipeline completes)_

| Source | Hits | Confirmed | Auth-on | Auth-off |
|---|---|---|---|---|
| Scaleway tier-2 | TBD | TBD | TBD | TBD |
| OVH tier-2 | TBD | TBD | TBD | TBD |
| Linode tier-2 | TBD | TBD | TBD | TBD |
| **Total unique** | TBD | TBD | TBD | TBD |

### By platform

| Platform | Confirmed | Auth-off | Median doc count | Notes |
|---|---|---|---|---|
| LightRAG | TBD | TBD | TBD | TBD |
| PrivateGPT | TBD | TBD | TBD | TBD |
| AnythingLLM | TBD | TBD | TBD | TBD |
| RAGFlow | TBD | TBD | TBD | TBD |
| Haystack | TBD | TBD | TBD | TBD |
| LlamaIndex | TBD | TBD | TBD | TBD |
| Microsoft GraphRAG | TBD | TBD | TBD | TBD |

---

## Notable findings

_(populated)_

---

## Cross-reference: vector DB surveys

The vector-DB layer has already been surveyed extensively (`qdrant-cloud-survey-2026-05.md`, `chromadb-cloud-survey-2026-05.md`, `milvus-cloud-survey-2026-05.md`, plus tier-2 expansions). RAG frameworks orchestrate **above** that layer. Where this survey finds a RAG framework on the same host as a previously-surveyed unauth vector DB, it's the same operator's full stack exposed end-to-end — the framework reveals what's in the vector DB, the DB confirms the volume.

Cross-host correlation candidates for the synthesis section:
- Scaleway hosts already in the qdrant-tier2-confirmed.jsonl
- OVH hosts already in chroma-tier2 / milvus-tier2 confirmed
- Linode hosts (small, but worth checking)

---

## Threat classes

1. **Corpus exfil** — what documents the operator has ingested. The collection names alone often disclose business domain (e.g. `legal_corpus`, `patient_records`, `contracts_2024`).
2. **Embedded-prompt + retrieval-logic exfil** — the operator's RAG configuration (system prompts, query rewriting, reranker weights) is proprietary tuning.
3. **API-key leak via config endpoints** — many frameworks expose configuration endpoints that include OpenAI/Anthropic/Cohere keys (HIGH if found).
4. **Document upload abuse** — frameworks with unauth `POST /ingest` allow attackers to **inject documents into the operator's RAG corpus** (poisoning the retrieval pool — affects everything the operator's LLM application returns).
5. **Compute theft via inference endpoints** — frameworks that proxy LLM calls expose the operator's provider keys to anyone who hits `/chat`, `/query`, or equivalent.

---

## Honest negative space

- **Hosted SaaS RAG products** (Vectara, Glean, Pinecone Knowledge, AWS Bedrock KB, etc.) — out of scope. Self-hosted only.
- **AnythingLLM auth-enforced instances** — many AnythingLLM operators have configured auth correctly. We expect a non-zero auth-on rate similar to Open WebUI's 99.1% finding.
- **Haystack pipelines without /initialized** — older Haystack versions or custom pipelines may not expose the `/initialized` endpoint we fingerprint on. Underestimate risk for older deployments.

---

## Disclosure plan

For each unauthenticated instance with high-severity content classes (healthcare, legal, financial, personal), draft coordinated-disclosure email per the standard NuClide template. Where the framework reveals operator identity (collection names like `<company>_internal_kb`), pursue direct operator contact via WHOIS / cert-pivot.

---

## See also

- [`SYNTHESIS-2026-05.md`](SYNTHESIS-2026-05.md) — companion cross-survey synthesis
- [`FUTURE-SURVEYS.md`](FUTURE-SURVEYS.md) — broader unsurveyed roadmap
- [`qdrant-cloud-survey-2026-05.md`](qdrant-cloud-survey-2026-05.md), [`chromadb-cloud-survey-2026-05.md`](chromadb-cloud-survey-2026-05.md), [`milvus-cloud-survey-2026-05.md`](milvus-cloud-survey-2026-05.md) — vector-DB-layer companion surveys
- [`data/rag-framework-probe.py`](../../data/rag-framework-probe.py) — multi-platform fingerprint prober used for this survey
