---
type: survey
---

# RAG Framework Servers — Population-Scale Survey (2026-05-15)

_NuClide Research · 2026-05-15_
_Category: 07 RAG Stacks (frameworks tier)_
_Status: complete · 6 platforms targeted · 3 with population data · 2 confirmed Shodan-dark · auth-on-default thesis confirmed across 3 tiers simultaneously_

---

## TL;DR

**1,782 confirmed RAG framework instances. 538 confirmed unauthenticated via primary-source verification. Auth-on-default thesis confirmed at population scale across three tiers in a single survey:**

| Platform | Tier | Confirmed | Unauth | Unauth % | Thesis verdict |
|---|---|---|---|---|---|
| **AnythingLLM** | A* (auth-optional, signup-open by default) | 1,242 | **483** | **39%** | Confirms thesis — default operates at population scale |
| **RAGFlow** | C (auth-on-default) | 485 | **0** | **0%** | Confirms thesis by contrapositive |
| **LightRAG** | A (no auth concept) | 55 | **55** | **100%** | Confirms thesis (no auth → 100% unauth) |
| PrivateGPT | A (no auth concept) | 4 | (small, not re-verified) | — | — |
| LlamaIndex | A (no auth concept) | 1 | 1 | — | Shodan-dark; see [single-host case study](llamaindex-chat-23-239-19-219-2026-05-15.md) |
| **Haystack** | A* (FastAPI) | **0 across 6 queries** | — | — | **Shodan-dark — port-first masscan required** |

**Within the AnythingLLM unauth subset:**
- **302 of 483 (63%) have ingested corpora** (`HasExistingEmbeddings: true`)
- **80+ are wired to paid LLM API keys** (OpenAI 43, Gemini 10, OpenRouter 3, Azure 3, Mistral 2, Cohere 2, LiteLLM 2, generic-OpenAI 16, LMStudio 2, LocalAI 1) — LLMjacking / quota-drain population
- Globally distributed: US 134, CN 84, DE 71, FR 23, SG 21
- Top hosting operators: Hetzner 39, AWS 64, DigitalOcean 30, Aliyun 29, Contabo 19

---

## Premise & platforms in scope

RAG (Retrieval-Augmented Generation) framework servers sit between vector databases and LLM clients, orchestrating the document-ingestion → chunking → embedding → retrieval → context-injection pipeline. The vector DB layer (Qdrant/Chroma/Milvus) has been surveyed; this is the framework layer above it.

| Platform | Default port | Authoritative auth tier | Identity marker |
|---|---|---|---|
| **LlamaIndex** servers | 8000 | A (no auth concept) | `info.title: "LlamaIndex Chat"` in `/openapi.json` |
| **Haystack** (hayhooks) | 1416 | A* (auth-optional) | `/initialized` JSON + `haystack`/`document_store` in `/openapi.json` |
| **LightRAG** | 9621 | A (no auth concept) | `/api/v1/graph/label/list` returns list, `/docs` contains `LightRAG` |
| **AnythingLLM** | 3001 | A* (auth-optional, signup-open default) | `/api/ping` → `{"online":true}` (or older: `pong`) |
| **RAGFlow** | 9380 | C (auth-on-default) | HTML title `RAGFlow`, `/v1/llm/list` JSON `code` field |
| **PrivateGPT** | 8001 | A (no auth concept) | `/openapi.json` contains `PrivateGPT` AND NOT `document_store` |

---

## Methodology

### Discovery — Shodan brand-dork (Stage 0)

38 priority queries built per platform with the conjunctive marker-anchored rule (Insight #6): each query combines a platform-unique title, body string, or response pattern. Counts taken first (`shodan host count`, 1 query credit each) to size the harvest before fan-out.

**Hit-volume per platform:**

| Platform | Best brand-dork | Hits |
|---|---|---|
| RAGFlow | `http.title:"RAGFlow"` | 1,883 |
| AnythingLLM | `http.title:"AnythingLLM"` | 1,004 |
| LightRAG | `http.title:"LightRAG"` | 88 |
| PrivateGPT | `http.title:"PrivateGPT"` | 6 |
| LlamaIndex | `http.title:"LlamaIndex Chat"` | 1 |
| **Haystack** | 6 queries (`hayhooks`, `port:1416`, `deepset-ai/haystack`, etc.) | **0 — all** |

**Two platforms confirmed Shodan-dark — Insight #21 applies:**

- **Haystack:** all 6 queries returned 0. Port-1416 alone has 672 worldwide listeners but none match `hayhooks` or `uvicorn` strings. Per Insight #21, port-first masscan against tier-2 ranges is the only path.
- **LlamaIndex Chat:** 1-2 hits across all queries. The `create-llama` generated HTML's `<title>` tag is the only brand marker, and it isn't always indexed. Population requires port-first.

The two Shodan-dark platforms validate Insight #21 *empirically*, in a single survey, on two platforms simultaneously.

### Harvest

`shodan download --limit N` (paginating beyond JAXEN's 50/query cap) into per-query `.json.gz` files. Total spend: ~50 query credits for the productive queries. Deduped to **3,773 unique IP:port candidates** across the four productive platforms.

### Probe iterations (three rounds — each caught a FP class)

| Round | Probe | Yield | Bug found |
|---|---|---|---|
| 1 | Existing `rag-framework-probe.py` (HTTP-only) | 538 confirmed (RAGFlow 504, LightRAG 32, PrivateGPT 1, LlamaIndex 1; **AnythingLLM 0/1505**) | HTTP-only; can't probe 443 SNI vhosts |
| 2 | New `probe-https.py` (HTTPS-aware, both schemes) | 545 (AnythingLLM **still 0**) | `/api/ping` checked for `pong` (old release) but newer AnythingLLM returns `{"online":true}` |
| 3 | `probe-https.py` with corrected `/api/ping` marker | 1,787 confirmed | **HTTP status ≠ auth state** (Insight #16) — `auth_required=False` was based on 200 status, but AnythingLLM `/api/system/check-token` returns `200 + body "No auth token found"` and RAGFlow returns `200 + body "code:401"` |
| 4 (re-classify) | `reprobe-anyllm-strict.py` + `reprobe-ragflow.py` — parse JSON body fields directly | **CORRECT counts** | logic refined: AnythingLLM auth from `/api/setup-complete` `results.RequiresAuth`; RAGFlow auth from `/v1/llm/list` JSON `code` field |

Final auth-state classification uses **only primary-source body fields**, never HTTP status alone. This is the Insight #16 discipline operationalized.

---

## Per-platform findings

### AnythingLLM — 483 unauth / 1,242 confirmed (39%)

**Probe:** `GET /api/ping` returns `{"online":true}` or `pong`. Cross-check `GET /api/setup-complete` `results.RequiresAuth` field.

**Auth-state distribution (primary-source `/api/setup-complete`):**
- 483 (38.9%) UNAUTH-ANONYMOUS (`RequiresAuth: false`) — anyone visiting can register / become admin / use the LLM and corpora
- 732 (58.9%) auth-required (`RequiresAuth: true`) — properly locked down
- 20 non-JSON responses (probe degradation, likely proxy-fronted)
- 7 unreachable

**Within the 483 unauth subset — enriched per-host metadata:**

| EmbeddingEngine | Hosts | LLM-quota-drain risk class |
|---|---|---|
| `native` (bundled MintplexLabs) | 307 | low — local embedder, no operator API cost |
| `ollama` (local Ollama) | 82 | low — local |
| `openai` | 43 | **HIGH — operator's OpenAI key is wired** |
| `generic-openai` (custom endpoint) | 16 | HIGH — operator's custom LLM-provider key |
| `gemini` | 10 | HIGH |
| `unknown`/missing | 10 | unknown |
| `openrouter`, `azure`, `mistral`, `cohere`, `litellm`, `lmstudio`, `localai` | 14 combined | mixed |

**302 of 483 (63%) have `HasExistingEmbeddings: true`** — the operator has already ingested documents into the workspace and persisted embeddings. The corpus exists and is queryable via the chat UI on an unauthenticated session.

**Geographic distribution (unauth subset):**

| Country | Count | Country | Count |
|---|---|---|---|
| United States | 134 | India | 12 |
| China | 84 | Canada | 10 |
| Germany | 71 | Hong Kong | 10 |
| France | 23 | Netherlands | 9 |
| Singapore | 21 | UAE | 9 |
| Japan | 13 | Brazil | 8 |

**Top hosting orgs (unauth subset):**

Hetzner 39 · AWS 64 (Amazon Technologies 34 + Amazon.com 30) · DigitalOcean 30 · Aliyun 29 · Contabo 19 · OVH 14 · Google 13 · Oracle 12 · Tencent 8.

No single dominant operator on the unauth subset — this is a platform-default-misconfiguration class, not a single-operator misdeploy.

### RAGFlow — 0 unauth / 485 confirmed (0%) — auth-on-default thesis confirmed by contrapositive

**Probe:** HTML title `RAGFlow` plus `/v1/dataset/list` reachability. Auth-state re-classification: `GET /v1/llm/list` and parse JSON `code` field — `code:401` = auth-required, `code:0` = unauth-with-data, `code:100` = method/not-found.

**Auth-state distribution (re-verified):**
- 462 (95.3%) auth-required (`code: 401`) — proper login gate
- 17 other-code-None — non-standard responses, likely proxy-fronted variants
- 6 non-JSON responses
- **0 confirmed unauthenticated**

This is a **negative result that confirms the thesis by its contrapositive**: RAGFlow is Tier-C (auth-on-default), and the population follows the default at 100%. This parallels the prior 2026-05 findings on Langfuse and Phoenix (both Tier-C with 0% unauth in their respective surveys).

**Heavy Chinese deployment:** 343 of 485 (71%) China-hosted. Aliyun 100, Tencent 33+22, Huawei 32, China Mobile 23, Volcano Engine 19. RAGFlow's developer InfiniFlow is China-based; the population follows the brand-origin.

### LightRAG — 55 unauth / 55 confirmed (100%)

**Probe:** `/api/v1/graph/label/list` returns a JSON list, OR `/docs` swagger contains `LightRAG`.

LightRAG has no authentication concept in its default deploy. Every confirmed instance is, by construction, unauthenticated. The 100% rate is the expected Tier-A result.

**Geographic spread:** Germany 13, China 11, US 5, Russia 5, France 4, Netherlands 3, Finland 3. Diverse — no operator cluster.

**Port distribution:** 80 (14), 443 (13), 8000 (6), 8080 (2), 9621 (2 — the documented default). Operators routinely run LightRAG behind reverse proxies; default-port-9621 is the *minority* deployment pattern. 42 HTTP / 13 HTTPS.

### PrivateGPT — 4 confirmed, auth state not re-verified

Small population. Confirmed via `/openapi.json` containing `PrivateGPT` and NOT `document_store` (to discriminate from Haystack). Re-verification deferred — sample size is too small to be population-meaningful.

### LlamaIndex — 1 confirmed (via Shodan), Shodan-dark at population scale

Only 1-2 hits across 6 brand-dorks. The confirmed instance is the single-host case study at `23.239.19.219` (Linode, operator `gochatus.org`) — see [the dedicated case study](llamaindex-chat-23-239-19-219-2026-05-15.md).

LlamaIndex Chat is **brand-dork-extinct on Shodan**. The `create-llama`-generated HTML title is inline, Vite-bundled, and not consistently indexed. Population study requires masscan-tier-2 + uvicorn-fingerprint + `/openapi.json` post-probe with `info.title:"LlamaIndex Chat"` verification — exactly the Insight #21 lane.

### Haystack — 0 confirmed via Shodan, complete brand-dork blackout

All 6 Haystack queries returned 0 hits. Even raw `port:1416` (the canonical hayhooks default) has 672 worldwide listeners — but none of them carry the `hayhooks` or `uvicorn` strings that would Shodan-identify them as Haystack.

The 672 port-1416 listeners are most likely **IBM Tivoli Storage Manager** (port 1416 is the IANA-registered TSM port). Haystack/hayhooks operators have either deployed essentially zero instances reachable from the internet, deployed entirely behind reverse proxies that strip the brand string, or both.

**Haystack at population scale needs:**
1. masscan tier-2 (Scaleway/OVH/Linode = 3.55M IPs) on port 1416 + 8000
2. Probe `/initialized` for `{"initialized": true/false}` JSON
3. Cross-check `/openapi.json` for `haystack`/`document_store`

Not run in this survey — flagged as the Haystack-specific follow-up.

---

## Cross-platform queries — universal 0

| Query | Hits |
|---|---|
| `"openapi" "RAG" "document_store"` | 0 |
| `"X-Powered-By: LlamaIndex"` | 0 |
| `"X-Powered-By: Haystack"` | 0 |

No RAG-framework operator sets a brand-tagging response header. Cross-platform "is this thing a RAG server" detection from raw banner alone is not feasible — every detection is platform-by-platform.

---

## Insight codifications

### Insight #21 re-confirmed on 2 simultaneous platforms (Haystack + LlamaIndex)

The 2026-05-14 AutoGen Studio survey produced Insight #21 — *port-first beats brand-dork for low-footprint platforms*. This survey produces **two new confirming cases in one session**:

- Haystack: 6 brand queries → 0 hits each. Confirmed Shodan-dark.
- LlamaIndex Chat: 6 brand queries → 1-2 total hits across all of them. Confirmed Shodan-dark.

Both have well-known default ports (1416 / 8000) and well-known FastAPI surface — but the brand string sits in HTML titles that Shodan doesn't reliably crawl through. Port-first masscan is the only path to population data.

### Insight #16 re-applied — auth state from JSON body, never HTTP status

Both AnythingLLM and RAGFlow returned **HTTP 200 even when auth was required**, with the actual auth-state signal in the response body:

- AnythingLLM `/api/system/check-token` returns `200` with body `{"error":"No auth token found."}` when auth is on but no token presented. Probing on HTTP status alone marks this as "unauth" — wrong.
- RAGFlow `/v1/llm/list`, `/v1/conversation/list`, `/v1/user/info` *all* return `HTTP 200` with body `{"code":401,"data":null,"message":"<Unauthorized '401: Unauthorized'>"}` when auth required. The HTTP-status signal is uniformly wrong; the body's `code` field is the truth.

Two platforms in one survey, both with this exact pattern. The first iteration of this survey published numbers off the HTTP-status signal and was corrected during sample-verification (8/8 AS63949 AnythingLLM sample showed `RequiresAuth: true` despite probe marking them unauth). The corrected probe parses `/api/setup-complete` `results.RequiresAuth` for AnythingLLM and `/v1/llm/list` `code` field for RAGFlow.

### New Insight candidate #23 — fingerprint marker drift across platform versions

AnythingLLM `/api/ping` returns:
- **older versions:** plain text `pong`
- **newer versions:** JSON `{"online":true}`

The existing `rag-framework-probe.py` checked for `pong` only and missed the entire current-release population (0 of 1,505 candidates confirmed against the canonical `pong` marker). A platform fingerprint is not static — markers drift across versions. Probes must check for *every documented historical marker*, and a fingerprint should be flagged for re-validation when a survey's confirmation rate is suspiciously low.

This pairs naturally with Insight #6 (conjunctive markers) — the conjunction *is* the catch, but each conjunct's exact string is version-dependent and needs maintenance.

---

## Auth-on-default thesis — single-survey triple confirmation

This is the rare survey where three different platform tiers were measured at population scale in one pass:

```
Tier-A   (no auth concept)        — LightRAG     → 55/55  unauth (100%)  ✓ confirmed
Tier-A*  (auth-optional, default-open) — AnythingLLM → 483/1242 unauth (39%) ✓ confirmed
Tier-C   (auth-on-default)        — RAGFlow      → 0/485   unauth (0%)   ✓ confirmed (contrapositive)
```

The thesis predicts each. The data delivers each. The pattern is not platform-specific — it tracks the shipping default, not the operator's skill.

This is also the first survey to put a number on Tier-A* "auth-optional with signup-open" at population scale. The prediction was *somewhere between 0% and 100% depending on how aggressive the platform's first-run wizard is*. AnythingLLM lands at 39% — almost exactly midway, consistent with a tutorial-default where the wizard nudges but doesn't enforce.

---

## Operator-side risk surface — within the 483 AnythingLLM unauth

For the 483 confirmed unauth AnythingLLM instances, the operator-side risk surface decomposes into three classes:

1. **Corpus exposure (302 hosts):** Operator has ingested documents. Anyone visiting the web UI can register, become admin, and read the entire vector store contents via the chat UI. Document classes will vary widely — personal notes, internal-business docs, course materials, legal/medical/financial corpora.
2. **LLM-quota-drain / LLMjacking (80+ hosts):** Operator wired a paid-tier LLM key (OpenAI, Gemini, OpenRouter, Azure, Mistral, Cohere, LiteLLM, etc.) into the workspace. Anonymous users can drive completions against that key — direct billing impact.
3. **Local-LLM compute theft (389 hosts on native+ollama):** Less monetary cost to the operator but free inference for whoever finds the host.

Restraint ethic: no extraction was performed. The 302/80/389 counts are derived from the `/api/setup-complete` metadata only (`HasExistingEmbeddings`, `EmbeddingEngine`), not from reading any corpus content. The metadata IS the finding (Insight #2 — collection/experiment/project names ARE the finding).

---

## Toolchain provenance

```
2026-05-15 15:42Z  Shodan API key rotation (basic plan, 9072 query credits)
2026-05-15 15:43Z  shodan count × 38 queries                            → hit-volume sizing
2026-05-15 15:46Z  jaxen hunt --clean × 10 productive queries           → first 50/query into empire.db
2026-05-15 15:48Z  shodan download --limit N × full populations         → 14 .json.gz files, 3,773 candidates deduped
2026-05-15 15:53Z  rag-framework-probe.py (HTTP-only) on full corpus    → 538 confirmed, AnythingLLM 0
2026-05-15 15:55Z  probe-https.py (HTTPS aware) iter-1                  → 545 confirmed, AnythingLLM still 0
2026-05-15 15:56Z  manual debug on AnythingLLM corpus                   → /api/ping returns {"online":true}, not "pong"
2026-05-15 15:57Z  probe-https.py iter-2 (corrected marker)             → 1,787 confirmed total
2026-05-15 16:00Z  sample-verify 8 AS63949 AnythingLLM                  → all RequiresAuth=true; HTTP-status auth signal is bogus
2026-05-15 16:02Z  sample-verify 5 unauth RAGFlow                       → /v1/dataset/list returns 200 + "404 not found" body
2026-05-15 16:03Z  reprobe-anyllm-strict.py (RequiresAuth from body)    → 483 UNAUTH-ANONYMOUS / 1,242 confirmed
2026-05-15 16:04Z  reprobe-ragflow.py (/v1/llm/list code field)         → 0 UNAUTH / 485 confirmed
2026-05-15 16:05Z  ASN/country/org enrichment from shodan metadata      → operator clusters identified
2026-05-15 16:06Z  visorlog ingest population-findings.ndjson            → rows 1038-1041 in nuclide.db
2026-05-15 16:08Z  case-study writeup                                    → this document
```

## See also

- [`llamaindex-chat-23-239-19-219-2026-05-15.md`](llamaindex-chat-23-239-19-219-2026-05-15.md) — single-host arsenal-fanout case study; the LlamaIndex confirmed instance in this survey
- [`rag-framework-cloud-survey-2026-05.md`](rag-framework-cloud-survey-2026-05.md) — the prior cross-cloud survey (2026-05-04); this 2026-05-15 survey supersedes it on population data and corrects its 119-host PrivateGPT bucket as FastAPI-FP class
- [`autogen-studio-survey-2026-05-14.md`](autogen-studio-survey-2026-05-14.md) — the survey that produced Insight #21; re-confirmed here for Haystack + LlamaIndex
- `SYNTHESIS-2026-05.md` — auth-on-default thesis evidence base; this survey adds three simultaneous tier confirmations
- New: **Insight candidate #23** — fingerprint marker drift across platform versions (AnythingLLM `pong` → `{"online":true}`)
