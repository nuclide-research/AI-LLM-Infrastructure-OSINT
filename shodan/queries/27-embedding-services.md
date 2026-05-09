# 27. Embedding Services

_Section verified: 2026-05-09_

The vector-conversion layer that sits between raw text and vector databases. Embedding servers ingest documents or queries and return dense float vectors; without them, RAG pipelines and semantic search cannot run. They ship auth-off across every observed implementation — the attack class is compute theft and embedding oracle (pre-computing query vectors to probe downstream vector stores).

**Survey note:** Embedding services are Shodan-dark compared to LLM inference servers. The root `/` path of canonical servers (TEI, infinity) returns either a redirect or API JSON rather than HTML, so Shodan's HTTP crawler indexes thin banners. Model-name queries (`BAAI/bge`, `nomic-embed`) are the highest-signal Shodan approach; the population-scale survey is masscan-driven on tier-2 cloud ranges, not Shodan-driven.

---

## HuggingFace Text Embeddings Inference (TEI)

The canonical standalone embedding server from HuggingFace. Single Rust binary, ships without auth, exposes `/info` (model metadata), `/embed` (POST), `/rerank` (optional), and `/metrics` (Prometheus).

**Warning — Docker Registry false positive:** `"text-embeddings-inference"` in Shodan banner (6 hits) matches Docker Registry catalog responses that list `ghcr.io/huggingface/text-embeddings-inference` as a cached image. These are not live TEI servers. Narrow with port constraints or `model_pipeline_tag` checks.

| Shodan Query | Hits | Notes |
|---|---|---|
| `http.html:"text-embeddings-inference"` | 2 | Low — Shodan rarely indexes the HTML body of API-only roots |
| `"text-embeddings-inference"` | 6 | **FP-heavy** — mostly Docker Registry catalogs, not live TEI |
| `product:"Text Embeddings Inference"` | 0 | No Shodan product facet registered |
| `port:80 http.html:"embed" http.html:"model_id"` | 0 | TEI /info fields not indexed in HTML |

**Live fingerprint (aimap / curl):** `GET /info` → `{"model_id": "BAAI/bge-small-en-v1.5", "model_pipeline_tag": "feature-extraction", "max_concurrent_requests": 512, "max_batch_total_tokens": 16384, "version": "2.x.x"}`. The `model_pipeline_tag: "feature-extraction"` field is unique to TEI and not present in any LLM inference server.

**Canonical aimap fingerprint:** `status_code:200` + `json_field:model_pipeline_tag` + `body_contains:feature-extraction` on `GET /info`.

**Ports:** 80 (Docker default internal), 8080 (common Docker mapping `-p 8080:80`), 3000 (older versions).

---

## infinity-embedding (michaelfeil/infinity)

OpenAI-compatible embedding server. Default port 7997. FastAPI with `/v1/embeddings` (POST), `/v1/models` (GET), and `/openapi.json`. OpenAPI title is `"Infinity Emb"`.

| Shodan Query | Hits | Notes |
|---|---|---|
| `http.html:"infinity_emb"` | 0 | Python package name not indexed |
| `"Infinity Emb"` | 0 | Not in Shodan index |
| `port:7997 http.html:"embedding"` | 0 | Default port not crawled |
| `http.html:"infinity" http.html:"/v1/embeddings"` | 1 | Combined term, 1 confirmed hit |

**Live fingerprint:** `GET /openapi.json` → body contains `"Infinity Emb"`. Alt: `GET /v1/models` → JSON with `data[]` and `infinity_emb` in model paths.

**Canonical aimap fingerprint:** `status_code:200` + `body_contains:Infinity Emb` on `GET /openapi.json`.

---

## Custom FastAPI Embedding APIs

The dominant shape in the wild. Operators wrap BAAI/bge, nomic-embed, multilingual-e5, and other embedding models in custom FastAPI services. Root `GET /` returns a JSON status object that leaks: embedding model name, embedding dimension, reranker model, LLM backend, and internal filesystem paths (index_dir, docs_dir). Auth-off on every observed instance.

**Fingerprint by model name** (Shodan-indexed because model names appear in HTML pages that embed API response data, e.g., Swagger UI and React dashboards):

| Shodan Query | Hits | Notes |
|---|---|---|
| `http.html:"BAAI/bge"` | 41 | **Best signal** — BAAI/bge family dominates; Contabo/Hetzner/Scaleway hosts |
| `http.html:"nomic-embed"` | 22 | nomic-embed-text model family; uvicorn-served FastAPI |
| `http.html:"multilingual-e5"` | 27 | intfloat multilingual-e5 family |
| `http.html:"all-MiniLM"` | 404 | sentence-transformers MiniLM — high count, **heavily polluted by Reposify/honeypot fleet** |
| `http.html:"sentence-transformers"` | 31 | sentence-transformers library reference |
| `"sentence-transformers"` | 4 | banner match, higher confidence |
| `http.html:"jina" http.html:"embedding"` | 12 | Jina embedding models in HTML |
| `http.html:"jinaai"` | 9 | Jina AI package name in page source |

**Pollution note:** `http.html:"all-MiniLM"` at 404 hits is dominated by `Server: Reposify` honeypots returning identical `Content-Length: 3151` across disparate IPs and ASNs. Filter: exclude `server:"Reposify"` and `Content-Length:3151` responses.

**Fingerprint by endpoint shape:**

| Shodan Query | Hits | Notes |
|---|---|---|
| `http.html:"/v1/embeddings" -http.html:"chat"` | 46 | OpenAI-compat embedding-only (excludes LLM gateways) |
| `http.html:"/embed" http.html:"model"` | 1,541 | Too broad — includes any page with "embed" + "model" |
| `http.html:"/embedding" http.html:"llama"` | 480 | llama.cpp `/embedding` endpoint in HTML |
| `http.html:"fastembed"` | 5 | fastembed library reference |

**Live fingerprint (aimap):** `GET /` → `json_field:embedding_dimension` (OpenVINO pattern) OR `json_field:embed` (RAG config pattern). `GET /health` → `json_field:embedding_dimension`.

**Ports:** 8000, 8001 (most common), 8002, 8080, 8100, 5000.

---

## Sentence-Transformers / bert-as-service

Older embedding infrastructure. bert-as-service uses ZMQ (port 5555 pull, 5556 push) rather than HTTP — not directly Shodan-scannable. Newer sentence-transformers HTTP wrappers are indistinguishable from Custom FastAPI Embedding APIs above.

| Shodan Query | Hits | Notes |
|---|---|---|
| `http.html:"sentence-transformers"` | 31 | Library reference in page HTML |
| `"sentence-transformers"` | 4 | Banner match |
| `port:5555 "sentence"` | 0 | bert-as-service ZMQ not HTTP-indexed |

---

## Jina Embeddings Self-Hosted

Jina provides self-hosted `jina-embeddings-v3` and `jina-reranker` via their `jinaai` package. Typically runs on 8080/8000, FastAPI.

| Shodan Query | Hits | Notes |
|---|---|---|
| `http.html:"jinaai"` | 9 | Package name in page source |
| `http.html:"jina" http.html:"embedding"` | 12 | Combined term |
| `"jina" "embeddings"` | 4 | Banner match |
| `"Jina" "embeddings" port:8080` | 2 | Default port, higher confidence |

---

## llama.cpp Embedding Server Mode

llama.cpp exposes `/embedding` (POST) when started with `--embedding` flag. Frequently co-deployed with the chat endpoint on the same instance.

| Shodan Query | Hits | Notes |
|---|---|---|
| `http.html:"/embedding" http.html:"llama"` | 480 | llama.cpp embedding endpoint in HTML |
| `"llama.cpp" http.html:"/embedding"` | 0 | Banner + HTML combined — 0 (banner and HTML rarely co-indexed) |

---

## OpenAI-compat Embedding Endpoints (Generic)

Any service emulating the OpenAI `/v1/embeddings` interface. Catches TEI, infinity, LocalAI, and custom wrappers.

| Shodan Query | Hits | Notes |
|---|---|---|
| `http.html:"/v1/embeddings" -http.html:"chat"` | 46 | Embedding-only, excludes LLM gateways |
| `http.html:"/v1/embeddings"` | 90 | Includes LLM gateways that also serve embeddings |

---

## Methodology Notes

**Why masscan beats Shodan here:** TEI, infinity, and custom FastAPI embedding servers all return API JSON at `GET /`, not HTML. Shodan's crawler indexes the root path HTTP response; a JSON blob with `{"model_pipeline_tag":"feature-extraction"}` looks like a non-page and gets minimal indexing. Port-targeted masscan on tier-2 cloud ranges (`8000,8001,8080,3000,7997`) followed by aimap fingerprinting is the correct discovery chain.

**aimap fingerprints (3 new — count 66 → 69):**
- `HuggingFace TEI` — `GET /info` → `json_field:model_pipeline_tag` + `body_contains:feature-extraction`
- `infinity-embedding` — `GET /openapi.json` → `body_contains:Infinity Emb`
- `Embedding API` — `GET /` → `json_field:embedding_dimension` OR `json_field:embed`

**Threat class:** Compute theft (GPU/CPU cost borne by operator) + embedding oracle (attacker pre-computes query vectors to probe downstream vector DBs semantically without holding the embedding key). Severity: medium on auth-off; elevated to high when paired with an exposed vector DB on the same host (dual-stack attack surface).

**Key population finding from Shodan sample:** Custom FastAPI wrappers around BAAI/bge and nomic-embed dominate over canonical TEI and infinity deployments. Operators build their own embedding servers rather than deploying the reference implementation, which means varied endpoint shapes and no canonical fingerprint covers the full population — aimap's multi-probe approach is necessary.

---

## See also

- [`02-vector-databases.md`](02-vector-databases.md) — downstream targets of embedding oracles
- [`03-model-serving.md`](03-model-serving.md) — Embedding / Reranking subsection with initial counts
- [`07-rag-stacks.md`](07-rag-stacks.md) — full RAG stack context
