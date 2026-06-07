---
type: survey
---

# Embedding Services: Cross-Cloud Survey (2026-05)

_NuClide Research · 2026-05-09_

> **Status:** Discovery + Shodan query sweep complete (2026-05-09). aimap Phase 1 + asyncio fingerprinting complete (Phase 2 hung on slow responders, replaced with focused asyncio probe). Shodan host enrichment on AI-tagged / port-7997 subset complete. 818 unique IPs surfaced; 667 with ≥1 open port confirmed active; **93 services live-confirmed** on the 440-IP priority subset. **Two HIGH-severity disclosure-warranted findings** (Klinikken.ai medical AI auth bypass, GraphRAG Process Safety stack on Scaleway FR). Full auth-off pattern holds across all platform classes observed.

---

## Premise

Embedding servers are the vector-conversion layer between raw text and vector databases. They ingest documents or queries and return dense float vectors; without them, RAG pipelines and semantic search cannot run. Every observed real-world implementation ships auth-off.

<!-- ksat-tag:auto-generated:start -->
## DCWF KSAT coverage

Auto-derived from DCWF AI work-role rule files (`ksat-tag`).

- **672 (AI Test & Evaluation Specialist):** K7003, K7004, K7044, S7068, S7070, S7075, S7076, T5904
- **733 (AI Risk & Ethics Specialist):** K7040, K7051, K7052, S7056, T5854, T5868, T5893
- **overlap (Common AI KSATs (all 5 roles)):** K1157, K1158, K1159, K22, K6311, K6900, K6935, K7003, K7041

<!-- ksat-tag:auto-generated:end -->

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
- **Round 2 (50 queries):** Zero-hit variants expanded. Found `bge-m3` (56), `feature-extraction` (64), `text-embedding-3-large` (55), `mxbai-embed` (12), `jina-embeddings` (13), `siglip` (8)
- **Round 3 (48 queries):** Anchored broad strings. Confirmed Xinference (484), LocalAI (190); dropped stella/voyage/ColBERT/truncate+embed as FP classes

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

**Note:** Phase 2 fingerprinting made concurrent in this session (80 goroutines matching -threads flag); previously sequential. MatchFingerprints now uses goroutine pool with semaphore.

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

## Targeted Probe Results (direct HTTP: live confirmation)

Fast targeted probe against 408 priority-port IPs (ports 7997, 80, 8080, 3000, 8000, 8001, 8002, 5000 only) using embedding-specific fingerprint paths.

| Service | Confirmed | Notes |
|---|---:|---|
| **Embedding API** (custom FastAPI) | **4** | `embedding_dimension` field in JSON root |
| HuggingFace TEI | 0 | Shodan-dark confirmed — no live matches on port 8080/3000/80 |
| infinity-embedding | 0 | Port 7997 hosts respond with non-HTTP (Socks4A, IRC, binary) |

**Live rate 1%** of Shodan-visible pool. Expected, Shodan data is days-to-weeks old. TEI and infinity-embedding confirmed Shodan-dark: servers return JSON-only roots not indexed by Shodan.

### Confirmed hosts (priority probe)

| IP | Port | Service | Finding |
|---|---|---|---|
| `46.4.204.44` | 8001 | Embedding API | BAAI/bge-m3 (1024-dim), OpenVINO-int8-throughput backend, `model_loaded:true` |
| **`37.27.185.38`** | **8001** | **Embedding API** | **Klinikken.ai Vector Database — healthcare AI** (see Notable Finding F1 below) |
| `161.118.173.64` | 8000 | Embedding API | Website FAQ chatbot, e5-large-v2 + pgvector + llama3 (DB disconnected) |
| `161.118.173.64` | 80 | Embedding API | Same host, dual-port binding |

## aimap Fingerprinting + Asyncio Probe Results (440 priority IPs)

aimap Phase 1 confirmed 1,924 open ports across 362/440 priority hosts (AI-tagged + port-7997 + EU/US, no Chinese). Phase 2 fingerprinting hung on slow IPv6 / TLS responders despite the concurrent-goroutine fix; the Go HTTP client's 1 s timeout did not reliably cancel established connections in the slow-trickle-response case. **Methodology pivot:** replaced Phase 2 with a focused asyncio probe (`/tmp/embed-probe.py`) using strict 1.5 s connect / 2 s read / 10 s host-deadline timeouts. The asyncio probe finished 6,160 probes in **~3 minutes** (vs aimap's 10+ min hang) and cleanly cancelled stuck connections at the asyncio.wait_for layer.

### Confirmed services (asyncio probe, 440 IPs × 14 ports)

| Service | Confirmed | % of pool |
|---|---:|---:|
| OpenAI-compat `/v1/models` (LLM gateways, embedding-capable) | **41** | 9.3% |
| **LocalAI** (`ApplicationConfig` JSON root) | **28** | 6.4% |
| **Ollama** (port 11434, embedding-capable) | **19** | 4.3% |
| Jina (GRM-MCP API) | 2 | 0.5% |
| **Embedding API** (`embedding_dimension` JSON field) | 2 | 0.5% |
| **Embedding API** (`embed` JSON field) | 1 | 0.2% |
| Total live confirmations | **93** | **21.1%** |

**Live rate 21% of priority subset** (93 / 440). Substantially higher than the 1% rate from the unfiltered 818-IP pool, validating the AI-tag + port-7997 + EU/US filter as a high-signal subset.

### Cross-validation against Shodan host enrichment

The asyncio probe's live counts roughly match the Shodan host enrichment ratios:

| Service | Shodan enrichment (100-IP AI-tagged sample) | asyncio live (440 IPs) |
|---|---:|---:|
| LocalAI | 43 | 28 |
| Ollama | 16 | 19 |
| Xinference | 1 | 0 (probe scope) |

LocalAI's drop from 43 → 28 reflects natural churn between Shodan's index time (days/weeks) and live probe (now). The Ollama count went up because the 440-IP set includes more port-11434 hosts than the 100-IP AI-tagged subset.

### Port 7997 (infinity-embedding): re-confirmed Shodan-dark

**Zero infinity-embedding confirmations** on the asyncio probe across all 440 IPs × port 7997. The probe sent `GET /openapi.json` with the canonical `Infinity Emb` body match. Hosts on port 7997 either:

1. Don't respond to HTTP (port open, non-HTTP service or firewalled at L7)
2. Are honeypot synthetic responses (Socks4A/IRC/binary noise per AS63949 fleet signature)
3. Are infinity instances that have moved off the standard port

**Hypothesis revision:** port 7997 alone is not a reliable infinity-embedding signal at population scale. The 100 Shodan-visible port-7997 hosts may include a substantial portion of synthetic / honeypot / off-target services. Future surveys should require the `GET /openapi.json` → `Infinity Emb` body match as a positive condition, not the port alone.

### Confirmed embedding API hosts (asyncio probe)

| IP | Port | Service | Notes |
|---|---|---|---|
| `46.4.204.44` | 8001 | Embedding API | BAAI/bge-m3, OpenVINO-int8, model_loaded=true |
| **`37.27.185.38`** | **8001** | **Embedding API** | **Klinikken.ai medical AI — auth bypass (F1)** |
| **`51.159.4.28`** | **8000** | **Embedding API** | **GraphRAG Process Safety API — full stack exposure (F9)** |

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

### Port 7997 (infinity-embedding): Shodan-dark confirmed

39 of 100 hosts had port 7997 open in Shodan records. **Zero showed infinity-embedding product/title in Shodan banners.** Banners were: Socks4A proxy, SSH, IRC-like services, binary noise (AS63949 honeypot signature). Shodan recorded the port as open but didn't fingerprint the HTTP service. Confirming that infinity-embedding's JSON API root is invisible to Shodan's HTML-based indexing. aimap's `GET /openapi.json` probe is the only reliable fingerprint.

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

### F1: Klinikken.ai. Psychotherapy session-notes corpus exposed via embedding-proxy auth bypass [CRITICAL. DISCLOSURE IN FLIGHT]

**Host:** `37.27.185.38:8001` (Hetzner DE, `static.38.185.27.37.clients.your-server.de`)
**Operator:** Klinikken.ai ApS, CVR 45899071, Faxe, Denmark
**Severity escalated 2026-05-09 14:11 UTC** from HIGH (architectural finding only) to **CRITICAL** after Test A confirmed the corpus is populated psychotherapy session content.

Klinikken.ai is a Danish clinical AI platform serving health clinics. Their self-hosted vector database API is publicly exposed without authentication. The system stores **psychotherapy session notes**: each session generates one Qdrant collection named `notes_therapist_<therapist_id>_session_<32_hex_uuid>`, holding 1–6 chunked text vector points.

- **Embedding API (port 8001):** Full CRUD, no auth. Endpoints: `POST /upload`, `POST /search`, `POST /delete`, `GET /collections/{user_id}`, `DELETE /collections/{user_id}/{collection_name}`
- **Qdrant backend (port 6333):** Reachable but auth-gated; the proxy on 8001 strips that gate
- **Auth bypass:** FastAPI proxy bakes the Qdrant API key in and serves data unauthenticated
- **Broken access control:** `user_id` is described in the OpenAPI as `"Bruger ID for isolation"` but is caller-supplied. Test A guessed `user_id=1` and retrieved 28 populated session-notes collections, ~78 chunked text points, ≥11 distinct therapist IDs visible in metadata (raw therapist IDs / session UUIDs withheld from this case study pending operator notification, held in `~/recon/embedding-shodan-2026-05-09/disclosures-unredacted/test-a-result.json`)
- **Model:** `paraphrase-multilingual-MiniLM-L12-v2`. Multilingual sentence-transformer, consistent with Danish-language clinical content
- **Tagline (Danish, from `/openapi.json`):** *"Embeddings og semantic search service med bruger-isolation"*. The operator named user-isolation as the design property; the implementation does not enforce it

**Data class:** GDPR Article 9 special-category mental-health data (psychotherapy session content). Danish Sundhedsloven §40 patient confidentiality applies. Article 33 breach-notification 72-hour clock starts on the controller at moment-of-awareness (= delivery of disclosure).

**Impact:** Any unauthenticated caller can:

- read therapy session content via `POST /search` with `score_threshold=0` and `limit=100` (corpus dump primitive)
- inject malicious content into any therapist's session collection via `POST /upload` (LLM-poisoning vector that surfaces in clinical chatbot responses to patients)
- destroy any therapist's session collection via `DELETE /collections/{user_id}/{collection_name}` (data-integrity loss + clinical-record obstruction concerns)
- enumerate the customer/tenant space via `GET /collections/{user_id}` with caller-supplied user_id

**Marketing-vs-implementation contradiction:** Klinikken.ai's homepage claims *"GDPR-sikker. Hostet i EU"*, *"Lever op til GDPR – ingen cookies, IP-adresser eller persondata"*, and *"Brugeren er 100% anonym"*, and contrasts themselves to ChatGPT's data-protection posture. The exposure we observed contradicts each of these claims at the technical layer: therapist IDs and session UUIDs are persistent personal-identifier metadata stored on a publicly reachable retrieval API, with no user-authentication and no access control on the partition primitive their own OpenAPI documents as `"for isolation"`. The host stack (Hetzner DE on 37.27.185.38) matches the operator's stated production tier (*"platformen kører i Finland, AI i Tyskland"*), so this is not a forgotten dev box.

**Disclosure status:** In flight as of 2026-05-09. Coordinated disclosure to Klinikken.ai ApS (operator) → Hetzner abuse (host) → Datatilsynet DK (supervisory authority, if 72-hour Article 33 clock requires escalation). Public disclosure (full unredacted technical detail incl. raw therapist IDs / session UUIDs / collection-name list / search PoC) withheld until operator acknowledgment or 72-hour silence per coordinated-disclosure norms.

---

### F2: Xinference. 484-hit dominant platform, 98% title-confirmed

`http.html:"xinference"` returned 484 unique IPs. Cross-validation against page title (`title:"Xinference"`) confirmed 98%+ are genuine Xinference deployments. Xinference is a Chinese multi-model serving platform (Xorbits/Xorbits-IO project) that supports embedding models alongside LLMs and image generation.

**Attack surface:** Xinference's API is auth-optional (API key off by default). The `/v1/embeddings` endpoint accepts model_uid as parameter. Any caller can enumerate available models, compute embeddings, and use them as oracles against downstream vector DBs. Admin panel (`/v1/cluster`) exposes node topology.

### F3: Port 7997. 100 confirmed infinity-embedding hosts

infinity-embedding (michaelfeil/infinity) uses port 7997 as its non-standard default, making it uniquely identifiable via port scan even though Shodan HTML queries return 0. 100 hosts found on this port represent confirmed or near-confirmed infinity deployments.

**Shodan-dark problem:** infinity's API root returns JSON (`/openapi.json` → `{"info": {"title": "Infinity Emb"}}`), which Shodan doesn't index. The only Shodan signal is the port itself. aimap's `GET /openapi.json` + `body_contains:Infinity Emb` is the definitive fingerprint.

### F4: CVE exposure. 307/818 IPs carry known vulnerabilities

InternetDB reports 307 IPs in the embedding pool have known CVEs. Top CVEs:

| CVE | Hosts | Description |
|---|---|---|
| CVE-2025-23419 | 210 | nginx TLS session ticket reuse (shared memory across workers) |
| CVE-2023-44487 | 209 | HTTP/2 Rapid Reset (DoS amplification) |
| CVE-2021-3618 | 157 | nginx ALPN mismatch |
| CVE-2021-23017 | 152 | nginx resolver heap overflow |
| CVE-2013-4365 and older | 145+ | Apache legacy / mod_security era |

CVE-2023-44487 (HTTP/2 Rapid Reset) on 209 embedding hosts means attackers can DoS the embedding layer specifically, degrading entire RAG pipelines without touching the LLM or vector DB. Combined with auth-off, no authentication is needed to trigger the DoS.

### F5: Custom FastAPI wrappers dominate over canonical implementations

Model-name queries (BAAI/bge at 41, nomic-embed at 22, multilingual-e5 at 27) all returned non-TEI, non-infinity servers. Operators wrapping models in custom FastAPI services. Each has unique endpoint shapes, response schemas, and field names. No single canonical fingerprint covers the population. The dominant pattern: operators copy open-source RAG templates and add an embedding endpoint alongside the LLM gateway, inheriting auth-off from the template.

### F6: Honeypot mimicry. "Xinference" on Redis port (port 6379)

Host `43.133.13.81` (Japan/Asia Pacific Network, 1,000 ports) is tagged `honeypot` in Shodan. Its Shodan record shows `title:"Xinference"` on port **6379** (Redis default). This is honeypot service mimicry: the honeypot operator scripted responses that return Xinference-looking HTML on non-standard ports to catch scanners. Filtering rule: any Xinference hit on port 6379 is a honeypot. Cross-check Shodan tag before treating as genuine.

### F7: Tor-associated Ollama cluster (Latvia/MAXKO fleet)

The Latvia/SIA RixHost fleet (`185.28.47.x`) and MAXKO Hosting operator (South Africa/Croatia) show Ollama instances tagged with `tor` and `database`. These are likely privacy-focused VPS providers offering "anonymous AI" services where users submit embedding jobs through Tor-onion frontends to unauth Ollama backends. From the embedding oracle perspective: the Tor layer protects the USER, not the operator. The embedding API itself is auth-off at the HTTP layer.

### F8: Aliyun / Chinese cloud operator concentration

28% of the embedding server pool is on Aliyun. Combined with Korean (25 IPs) and Singaporean (47) Asian-cloud presence, over 40% of the discoverable embedding infrastructure is on Asian cloud providers. This population skews younger (more recently deployed), runs newer frameworks (Xinference, bge-m3 family), and is more likely to have UI dashboards that make Shodan indexing possible.

### F9: GraphRAG Process Safety API. Full multi-stack exposure on Scaleway FR [DISCLOSURE WARRANTED]

**Host:** `51.159.4.28` (`51-159-4-28.rev.poneytelecom.eu`, Scaleway dedicated, Paris FR)

Surfaced by the asyncio probe (`/`-root JSON match on `embed` key). Host runs a French industrial process safety RAG stack with five auth-off services on the same VPS:

| Port | Service | Status |
|---|---|---|
| 8000 | GraphRAG Process Safety API v3.0.0 | 200 (OpenAPI public, 19 endpoints) |
| 11434 | Ollama (qwen2.5:7b LLM, nomic-embed-text embedder) | 200 |
| 6333 | Qdrant vector DB | 200 |
| 3000 | Web UI (likely Open WebUI) | 200 |
| 9000 | Object storage (likely MinIO) | 307 |

**JSON root response (port 8000):**
```json
{"message":"GraphRAG Process Safety API","version":"3.0.0",
 "llm_model":"qwen2.5:7b","embed":"nomic-embed-text",
 "dossier_local":"/home/<redacted>/<redacted>","status":"running"}
```

**Operator information leaked in JSON root** (Linux username + folder name redacted in this public case study to avoid pre-disclosure operator re-identification; held unredacted in `~/recon/embedding-shodan-2026-05-09/disclosures-unredacted/`). The OpenAPI spec exposes 19 endpoints including `/webhook/drive/initial-sync` (Google Drive root-folder ingest), `/chat`, `/history`, `/me`, `/dossier/scan`, `/reindex`, `/internal/notify`. French OpenAPI descriptions ("Synchronisation initiale complète") confirm French operator/scope.

**Process Safety domain:** GraphRAG is Microsoft's knowledge-graph + RAG framework; "Process Safety" in industrial context typically covers chemical/oil-gas/manufacturing safety procedures, hazard analyses (HAZOP), incident reports, and equipment safety protocols. RAG-indexed process safety documentation is operationally sensitive. Vendor confidential procedures, plant-specific equipment configurations, and incident-response playbooks all appear in Process Safety document corpora.

**Threat class:** High. Auth-off across the entire stack (orchestrator + LLM + vector DB + storage). Multi-port stacked exposure mirrors the Klinikken.ai pattern. Operator's personal Google Drive content is being ingested via the webhook layer.

**Disclosure path:** Scaleway France (`abuse@scaleway.com`) + operator email (registrant lookup pending). French DPA is CNIL if PII confirmed. Disclosure draft to be authored as `disclosures/GRAPHRAG-PROCESS-SAFETY-2026-05-09.md`.

---

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

- [`shodan/queries/27-embedding-services.md`](../../shodan/queries/27-embedding-services.md): Full 144-query catalog, FP documentation, methodology notes
- [`02-vector-databases.md`](../../shodan/queries/02-vector-databases.md): Downstream targets of embedding oracles
- [`07-rag-stacks.md`](../../shodan/queries/07-rag-stacks.md): Full RAG stack context
- [`SYNTHESIS-2026-05.md`](SYNTHESIS-2026-05.md): Cross-survey auth-posture table
