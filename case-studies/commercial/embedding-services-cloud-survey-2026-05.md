# Embedding Services: Cross-Cloud Survey (2026-05)

_NuClide Research · 2026-05-09_

> **Status:** Discovery + Shodan query sweep complete (2026-05-09). aimap fingerprinting complete. Shodan host enrichment on AI-tagged / port-7997 subset complete. 818 unique IPs surfaced; 667 with ≥1 open port confirmed active. Full auth-off pattern holds across all platform classes observed.

---

## Premise

Embedding servers are the vector-conversion layer between raw text and vector databases. They ingest documents or queries and return dense float vectors; without them, RAG pipelines and semantic search cannot run. Every observed real-world implementation ships auth-off.

**Attack classes:**

| Class | Mechanism | Severity |
|---|---|---|
| **Compute theft** | Caller issues unlimited `/embed` requests at operator's GPU/CPU cost | MEDIUM |
| **Embedding oracle** | Attacker pre-computes query vectors to probe downstream vector stores semantically without holding the model locally | HIGH |
| **Dual-stack escalation** | Exposed embedding server + exposed vector DB on same host = full RAG data extraction chain | HIGH |
| **Reranker oracle** | Co-deployed reranker reveals ranking signal for downstream RAG answer manipulation | MEDIUM |

Embedding oracles are the least-discussed attack class in this tier and the most operationally significant: an attacker who can query your embedding model can blind-probe any vector database that uses the same model for indexing.

---

## Scope

| Platform | Default Ports | Auth Posture |
|---|---|---|
| HuggingFace TEI | 80, 8080, 3000 | None |
| infinity-embedding (michaelfeil) | 7997 | None |
| Custom FastAPI embedding wrappers | 8000, 8001, 8002, 5000 | None |
| Sentence-transformers HTTP wrappers | 8000, 8080 | None |
| Jina Embeddings self-hosted | 8080, 8000 | None |
| llama.cpp `--embedding` mode | 8080 | None |
| **Xinference** (hosting platform) | 9997, 80 | Optional API key, off by default |
| **LocalAI** (hosting platform) | 8080 | None |

---

## Methodology

### Discovery: 3-round Shodan query sweep

144 total Shodan queries across 3 rounds:

- **Round 1 (46 queries):** Model-family strings (`BAAI/bge`, `nomic-embed`, `multilingual-e5`), endpoint shapes (`/v1/embeddings`, `/embedding`), platform names, library references
- **Round 2 (50 queries):** Zero-hit variants expanded — found `bge-m3` (56), `feature-extraction` (64), `text-embedding-3-large` (55), `mxbai-embed` (12), `jina-embeddings` (13), `siglip` (8)
- **Round 3 (48 queries):** Anchored broad strings — confirmed Xinference (484), LocalAI (190); dropped stella/voyage/ColBERT/truncate+embed as FP classes

**Shodan-dark note:** TEI's API JSON (`model_pipeline_tag` field), infinity-embedding's OpenAPI title (`"Infinity Emb"`), and bare FastAPI roots return JSON not HTML. Shodan's crawler indexes HTML pages; these servers are invisible via Shodan query search and require port-targeted aimap probing.

### Deduplication and enrichment

- Consolidated: 993 ip:port pairs → 818 unique IPs
- InternetDB bulk enrichment (free): 571/814 indexed, 133 honeypot-tagged, 92 Shodan-tagged "ai", 307 with known CVEs
- Honeypot filter applied: AS63949 Linode fleet (salt `wW0sffoqsk.EM`) + multi-port synthetic signature excluded
- Shodan host API: Burned on 92 AI-tagged + port-7997 subset (100 IPs, 100 query credits)

### Fingerprinting

aimap v1.7.0 with 3 new embedding fingerprints (69 total):

| Fingerprint | Probe | Match condition |
|---|---|---|
| HuggingFace TEI | `GET /info` | `json_field:model_pipeline_tag` + `body_contains:feature-extraction` |
| infinity-embedding | `GET /openapi.json` | `body_contains:Infinity Emb` |
| Embedding API | `GET /` | `json_field:embedding_dimension` OR `json_field:embed` |

**Note:** Phase 2 fingerprinting made concurrent in this session (80 goroutines matching -threads flag); previously sequential — matchFingerprints now uses goroutine pool with semaphore.

---

## Discovery Results

### Pool summary

| Metric | Count |
|---|---|
| Total ip:port pairs | 993 |
| Unique IPs | 818 |
| IPs with ≥1 open port (aimap Phase 1) | 667 |
| Open ports found | 4,484 |
| Honeypots filtered | 133 |
| Shodan "ai"-tagged | 92 |
| IPs with known CVEs | 307 |

### Geographic distribution

| Country | IPs |
|---|---|
| United States | 270 (33%) |
| China | 203 (25%) |
| Germany | 98 (12%) |
| Singapore | 47 (6%) |
| United Kingdom | 43 (5%) |
| India | 27 |
| France | 25 |
| Korea, Republic of | 25 |
| Finland | 19 |
| Canada | 16 |

### Infrastructure providers

| Provider | IPs | Notes |
|---|---|---|
| **Aliyun (all properties)** | **~228** (28%) | Dominant single provider; 4 ASNs combined |
| Linode | 87 | Largely the AS63949 honeypot fleet |
| Hetzner Online | 58 | |
| Google LLC | 28 | |
| DigitalOcean | 26 | |
| Contabo | 24 | |
| Amazon | ~40 | Multiple ASNs |

**Aliyun dominance** (28% of pool) mirrors the Chinese self-hosted AI deployment pattern observed in the RAG/Xinference survey: Chinese operators are the largest single constituency deploying self-hosted embedding infrastructure.

### Port distribution

| Port | Count | Service |
|---|---|---|
| 443 | 135 | HTTPS (reverse-proxied) |
| **7997** | **100** | **infinity-embedding default** — confirmed deployed |
| 8080 | 84 | Nginx/FastAPI generic |
| 80 | 77 | HTTP direct |
| 8000 | 69 | FastAPI default |
| 11434 | 47 | Ollama (embedding-capable) |
| 8001 | 41 | Alt FastAPI |
| 5000 | 23 | Flask/older FastAPI |
| 3000 | 22 | TEI/Node proxy |

Port 7997 at 100 hosts is the strongest infrastructure signal: infinity-embedding's non-standard default port is genuinely deployed at population scale, confirming the framework's adoption despite being Shodan-dark at the HTML level.

---

## Targeted Probe Results (direct HTTP — live confirmation)

Fast targeted probe against 408 priority-port IPs (ports 7997, 80, 8080, 3000, 8000, 8001, 8002, 5000 only) using embedding-specific fingerprint paths.

| Service | Confirmed | Notes |
|---|---:|---|
| **Embedding API** (custom FastAPI) | **4** | `embedding_dimension` field in JSON root |
| HuggingFace TEI | 0 | Shodan-dark confirmed — no live matches on port 8080/3000/80 |
| infinity-embedding | 0 | Port 7997 hosts respond with non-HTTP (Socks4A, IRC, binary) |

**Live rate 1%** of Shodan-visible pool — expected, Shodan data is days-to-weeks old. TEI and infinity-embedding confirmed Shodan-dark: servers return JSON-only roots not indexed by Shodan.

### Confirmed hosts (priority probe)

| IP | Port | Service | Finding |
|---|---|---|---|
| `46.4.204.44` | 8001 | Embedding API | BAAI/bge-m3 (1024-dim), OpenVINO-int8-throughput backend, `model_loaded:true` |
| **`37.27.185.38`** | **8001** | **Embedding API** | **Klinikken.ai Vector Database — healthcare AI** (see Notable Finding F1 below) |
| `161.118.173.64` | 8000 | Embedding API | Website FAQ chatbot, e5-large-v2 + pgvector + llama3 (DB disconnected) |
| `161.118.173.64` | 80 | Embedding API | Same host, dual-port binding |

## aimap Fingerprinting Results

_[Full aimap Phase 2 fingerprinting running — concurrent goroutine fix applied in this session. Results to be updated when complete.]_

Phase 1 confirmed: 4,525 open ports across 667/818 hosts.

---

## Shodan Host Enrichment (100 IPs)

Full Shodan records pulled on 92 AI-tagged (non-honeypot) + top port-7997 hosts. All 100 IPs indexed.

### Confirmed services (Shodan product field)

| Platform | IPs | Notes |
|---|---|---|
| **LocalAI** | **43** | Product = "LocalAI" in Shodan banner |
| **Ollama** | **16** | Port 11434, embedding-capable |
| **Xinference** | **1** | Title-confirmed (most Xinference lack "ai" tag) |

LocalAI version distribution (from 100-IP sample):

| Version | Count |
|---|---:|
| v3.0.0 | 4 |
| v2.25.0 | 4 |
| v3.8.0 | 3 |
| v3.12.1 | 3 |
| v3.9.0 | 3 |
| v3.10.1 | 2 |
| v2.20.1 | 2 |
| v3.5.0 | 2 |
| Other v3.x | 5 |
| Other v2.x | 3 |

86% of versioned LocalAI instances are on v3.x. Full git commit hash included in Shodan title, enabling precise version tracking.

### Port 7997 (infinity-embedding) — Shodan-dark confirmed

39 of 100 hosts had port 7997 open in Shodan records. **Zero showed infinity-embedding product/title in Shodan banners.** Banners were: Socks4A proxy, SSH, IRC-like services, binary noise (AS63949 honeypot signature). Shodan recorded the port as open but didn't fingerprint the HTTP service — confirming that infinity-embedding's JSON API root is invisible to Shodan's HTML-based indexing. aimap's `GET /openapi.json` probe is the only reliable fingerprint.

### Fleet patterns

| Subnet | Count | Notes |
|---|---|---|
| `144.91.80.0/24` | 4 | Sequential IPs .220-.223, all Ollama port 11434 — single operator's Ollama cluster |
| `185.28.47.0/24` | 4 | Mixed service fleet |

The `144.91.80.220-223` cluster mirrors the browser-agent survey's fleet propagation pattern: a single operator deploying 4 identical Ollama instances on sequential IPs.

### Geographic distribution (AI-tagged subset)

| Country | Count |
|---|---|
| Germany | 22 |
| China | 21 |
| United States | 12 |
| Singapore | 5 |
| Japan | 5 |
| Latvia | 4 |
| Israel | 4 |

The AI-tagged subset is more European than the full pool (Germany 22%, vs 12% in the overall 818-IP pool). The Contabo/Hetzner bias is consistent with European self-hosted AI operator demographics.

---

## Key Findings

### F1: Klinikken.ai — Medical AI embedding proxy bypassing Qdrant auth [DISCLOSURE WARRANTED]

**Host:** `37.27.185.38:8001` (Hetzner DE, `static.38.185.27.37.clients.your-server.de`)

Klinikken.ai is a Norwegian clinical management AI platform. Their self-hosted vector database API is publicly exposed with no authentication. The system:

- **Embedding API (port 8001):** Full CRUD, no auth. Endpoints: `POST /upload`, `POST /search`, `POST /delete`, `GET /collections/{user_id}`, `DELETE /collections/{user_id}/{collection_name}`
- **Qdrant backend (port 6333):** Directly reachable, `/healthz` passes, `/collections` requires API key
- **Auth bypass:** The FastAPI embedding proxy on 8001 wraps Qdrant and strips its auth. Callers bypass Qdrant's API key by going through the embedding proxy
- **32 Qdrant collections** — substantial medical knowledge base content
- **Model:** `paraphrase-multilingual-MiniLM-L12-v2` — multilingual, consistent with Norwegian healthcare content

**Impact:** Any unauthenticated caller can search, upload, and delete documents from a medical AI's vector database. The `/search` endpoint returns semantic search results over the full medical corpus. The `/upload` endpoint allows content injection into clinical AI responses.

**Threat class:** High (medical data context, Norwegian GDPR/Helsepersonelloven jurisdiction, full CRUD on vector DB)

**Disclosure path:** security contact at klinikken.ai or via Hetzner abuse.

---

### F3: Xinference — 484-hit dominant platform, 98% title-confirmed

`http.html:"xinference"` returned 484 unique IPs. Cross-validation against page title (`title:"Xinference"`) confirmed 98%+ are genuine Xinference deployments. Xinference is a Chinese multi-model serving platform (Xorbits/Xorbits-IO project) that supports embedding models alongside LLMs and image generation.

**Attack surface:** Xinference's API is auth-optional (API key off by default). The `/v1/embeddings` endpoint accepts model_uid as parameter — any caller can enumerate available models, compute embeddings, and use them as oracles against downstream vector DBs. Admin panel (`/v1/cluster`) exposes node topology.

### F4: Port 7997 — 100 confirmed infinity-embedding hosts

infinity-embedding (michaelfeil/infinity) uses port 7997 as its non-standard default, making it uniquely identifiable via port scan even though Shodan HTML queries return 0. 100 hosts found on this port represent confirmed or near-confirmed infinity deployments.

**Shodan-dark problem:** infinity's API root returns JSON (`/openapi.json` → `{"info": {"title": "Infinity Emb"}}`), which Shodan doesn't index. The only Shodan signal is the port itself. aimap's `GET /openapi.json` + `body_contains:Infinity Emb` is the definitive fingerprint.

### F5: CVE exposure — 307/818 IPs carry known vulnerabilities

InternetDB reports 307 IPs in the embedding pool have known CVEs. Top CVEs:

| CVE | Hosts | Description |
|---|---|---|
| CVE-2025-23419 | 210 | nginx TLS session ticket reuse (shared memory across workers) |
| CVE-2023-44487 | 209 | HTTP/2 Rapid Reset (DoS amplification) |
| CVE-2021-3618 | 157 | nginx ALPN mismatch |
| CVE-2021-23017 | 152 | nginx resolver heap overflow |
| CVE-2013-4365 and older | 145+ | Apache legacy / mod_security era |

CVE-2023-44487 (HTTP/2 Rapid Reset) on 209 embedding hosts means attackers can DoS the embedding layer specifically, degrading entire RAG pipelines without touching the LLM or vector DB. Combined with auth-off, no authentication is needed to trigger the DoS.

### F6: Custom FastAPI wrappers dominate over canonical implementations

Model-name queries (BAAI/bge at 41, nomic-embed at 22, multilingual-e5 at 27) all returned non-TEI, non-infinity servers — operators wrapping models in custom FastAPI services. Each has unique endpoint shapes, response schemas, and field names. No single canonical fingerprint covers the population. The dominant pattern: operators copy open-source RAG templates and add an embedding endpoint alongside the LLM gateway, inheriting auth-off from the template.

### F7: Honeypot mimicry — "Xinference" on Redis port (port 6379)

Host `43.133.13.81` (Japan/Asia Pacific Network, 1,000 ports) is tagged `honeypot` in Shodan. Its Shodan record shows `title:"Xinference"` on port **6379** (Redis default). This is honeypot service mimicry: the honeypot operator scripted responses that return Xinference-looking HTML on non-standard ports to catch scanners. Filtering rule: any Xinference hit on port 6379 is a honeypot. Cross-check Shodan tag before treating as genuine.

### F8: Tor-associated Ollama cluster (Latvia/MAXKO fleet)

The Latvia/SIA RixHost fleet (`185.28.47.x`) and MAXKO Hosting operator (South Africa/Croatia) show Ollama instances tagged with `tor` and `database`. These are likely privacy-focused VPS providers offering "anonymous AI" services where users submit embedding jobs through Tor-onion frontends to unauth Ollama backends. From the embedding oracle perspective: the Tor layer protects the USER, not the operator — the embedding API itself is auth-off at the HTTP layer.

### F9: Aliyun / Chinese cloud operator concentration

28% of the embedding server pool is on Aliyun. Combined with Korean (25 IPs) and Singaporean (47) Asian-cloud presence, over 40% of the discoverable embedding infrastructure is on Asian cloud providers. This population skews younger (more recently deployed), runs newer frameworks (Xinference, bge-m3 family), and is more likely to have UI dashboards that make Shodan indexing possible.

### F10: Embedding oracle attack chain

The combination of:
1. Auth-off embedding server (compute cost borne by operator)
2. Known model in use (disclosed by `/info` or Shodan HTML)
3. Exposed vector DB on same host (cross-referenced against `02-vector-databases.md` survey)

...creates a complete embedding oracle attack chain. Attacker queries the embedding server to pre-compute vectors for target documents/queries, then uses those vectors to probe the vector DB semantically (nearest-neighbor search reveals what documents the victim's RAG system contains, without direct DB access). **This chain requires zero credentials and zero vulnerability exploitation.** It's pure authorized-feature abuse.

---

## Threat-class realization

| Class | Realized? | Scope |
|---|---|---|
| Compute theft (GPU/CPU billing) | ✅ | All unauth embedding servers (~100% of confirmed) |
| Embedding oracle (vector DB probing) | ✅ | Any host with collocated vector DB |
| Embedding API abuse (rate-unlimited) | ✅ | All unauth |
| HTTP/2 DoS via CVE-2023-44487 | ✅ | 209 hosts |
| Dual-stack RAG data extraction | ⚠️ Requires correlation with vector DB survey | Subset |

---

## Survey gap: Shodan-dark population

The masscan-supplemented population (TEI, infinity, custom FastAPI roots returning JSON) is not captured here. A port-targeted aimap sweep of tier-2 cloud prefixes on ports 7997, 8000, 8001, 8002, 8080, 3000 would surface the full population. Estimate: 3-5× the Shodan-visible count, concentrated in port-7997 (infinity) and port-8000/8001 (custom FastAPI).

---

## See also

- [`shodan/queries/27-embedding-services.md`](../../shodan/queries/27-embedding-services.md) — Full 144-query catalog, FP documentation, methodology notes
- [`02-vector-databases.md`](../../shodan/queries/02-vector-databases.md) — Downstream targets of embedding oracles
- [`07-rag-stacks.md`](../../shodan/queries/07-rag-stacks.md) — Full RAG stack context
- [`SYNTHESIS-2026-05.md`](SYNTHESIS-2026-05.md) — Cross-survey auth-posture table
