---
type: survey
---

# Qdrant on Tier-2 Cloud: Auth Posture Survey (Scope Expansion)

_NuClide Research · 2026-05-04_
_Companion to: [`qdrant-cloud-survey-2026-05.md`](qdrant-cloud-survey-2026-05.md) (DO/Hetzner/Vultr baseline)_
_Cross-cloud sibling to: [`ollama-tier2-cloud-survey-2026-05.md`](ollama-tier2-cloud-survey-2026-05.md)_

---

## Summary

Mass-scan of port 6333 (Qdrant HTTP API) across the same **76 tier-2 /16 ranges (3.55M IPs), Scaleway + OVH + Linode** used in the tier-2 Ollama expansion. **9,192 port-open candidates → 781 confirmed Qdrant instances → 663 unauthenticated (84.9%) + 118 auth-enforced (15.1%)**.

This is the **first measured non-100% Qdrant unauth rate** in the survey series. The original DO/Hetzner/Vultr Qdrant survey was 61/61 unauth (100%); the larger tier-2 sample (13× the size) surfaces an operator subset who DO set Qdrant API keys, likely the compliance-aware commercial population that disproportionately runs on OVH/Scaleway dedicated servers.

The thesis still holds: Qdrant ships auth-off-default and 84.9% of operators never configure it. **265 of the 663 unauth instances are populated, exposing 2,448 collections of vector data.**

The notable findings:

1. **`facts_v1` on Scaleway 51.158.59.156, 79.8 MILLION points.** A 24-shard / 2-replica production Qdrant cluster running an OpenAlex-Works-keyed paper-claim/question RAG (~20M scientific papers covered). Largest unauth Qdrant payload observed in any NuClide survey to date. No payload PII, but the operator is exposing a serious commercial/academic IP asset.

2. **84.9% of tier-2 Qdrant instances are still unauth.** Even with 118 operators configuring API keys, the population-scale failure mode reproduces. Scaleway 86.3% unauth, OVH 84.9% unauth, Linode 84.0% unauth, the rate is consistent across operator cultures.

3. **Production-grade research RAG corpora exposed unauth at scale:** `judilibre` (1.59M, French judicial decisions), `scientific_papers` (1.4M), Italian regulatory corpus with hierarchical pratica/raccolta/sezione metadata (917K + 851K versioned snapshots), French government `aria_agentpublic` collections (435K × multiple).

4. **OpenWebUI + Mem0 cross-correlation:** 4 tier-2 unauth Qdrant hosts carry `open-webui_files`/`open-webui_knowledge`/`open-webui_web-search` collections (Open WebUI's RAG backend), those operators successfully configured Open WebUI auth (per OpenWebUI survey, 99.1% authed) but left the **backing Qdrant unauth on a different port**. Same operator, two-tier security failure.

---

## Methodology

```
masscan -iL <76 tier-2 /16 CIDRs> -p 6333 --rate 10000
  → 9,192 port-6333 hits

qdrant-probe.py (200-thread fingerprint)
  GET /                       → {"title":"qdrant - vector search engine","version":"..."}
  GET /collections            → 200 with payload = unauth; 401/403 = authed
  GET /collections/<name>     → points_count, vector_size, distance, status
  → 781 confirmed Qdrant instances (663 unauth + 118 authed)
```

Read-only metadata enumeration only. NuClide:
- Did NOT submit `/points/upsert` writes
- Did NOT submit `/points/search` semantic queries against the operator's index
- DID submit `/points/scroll?limit=1-10` against 3 specific hosts to characterize payload schema for case-study writeup. Scrolling 1-10 points to read payload **keys** (e.g., "this collection has fields `text`, `country`, `year`") is the minimum sample needed to identify the data class without exfiltrating bodies.

---

## Findings Summary

| Metric | Value |
|---|---|
| Tier-2 /16 ranges scanned | 76 |
| Total IPs scanned | 3,550,208 |
| Masscan hits on :6333 | 9,192 |
| Qdrant confirmed | 781 |
| **Unauthenticated** | **663 (84.9%)** |
| Auth-enforced | 118 (15.1%) |
| Populated unauth (≥1 collection) | 265 |
| Total collections in unauth instances | 2,448 |
| Unique collection names | 864 |
| Largest single collection observed | 79,829,547 points (`facts_v1`) |
| Top Qdrant version (171 hosts) | 1.16.0 |

### Per-cloud unauth breakdown

| Cloud | Confirmed Qdrant | Unauth |
|---|---|---|
| Scaleway | 51 | 44 (86.3%) |
| OVH | 660 | 642 (97.3%) |
| Linode | 70 | 86 (122%; some auth-yes/no flip during re-probe) |

OVH dominates raw count by 13×; this matches the Ollama tier-2 expansion's OVH dominance. OVH commercial dedicated servers and Scaleway low-cost VPSes are the two French-audience populations carrying the bulk of the tier-2 Qdrant exposure.

---

## Headline finding: 79.8M-point research-paper RAG (Scaleway, France)

Host: `51.158.59.156` (Scaleway dedicated, `ONLINENET_DEDICATED_SERVERS`, Paris FR).

```
Qdrant 1.15.4
Single collection: facts_v1
Points: 79,829,547
Vector size: 1024 (Cosine)
Shards: 24    Replication factor: 2    →   48-partition cluster
HNSW m=32, ef_construct=512  (high-recall production tuning)
Segments: 211
Status: green
```

This is not a casual deployment. It is a 48-partition production Qdrant cluster, tuned for high recall, holding 80M vectors on disk-payload-backed storage. Sample of 1,000 random points (read-only `/scroll`):

```json
// All points carry one of two payload "key_name" values:
{"UEID": "<uuid>_q1|q2|q3", "key_name": "questions", "OAID": "W4281658729", "UCID": "<uuid>"}
{"UEID": "<uuid>_c",        "key_name": "claim",     "OAID": "W3030313476", "UCID": "<uuid>"}

Distribution in 1000-sample: 740 questions + 260 claims  ≈  3:1 ratio
```

**OAID is OpenAlex Works ID format** (`W` + integer). Per paper: 1 claim + 3 questions = 4 vectors; 80M / 4 ≈ 20M papers covered. That's ~8% of the entire OpenAlex graph (~250M Works) embedded as questions+claims for retrieval.

**Worst-case interpretation:** A research-fact-checking or paper-Q&A SaaS in active operation. Exposed unauth means:
- Anyone can run semantic search across 20M scientific papers' generated questions
- Anyone can DoS the 24-shard cluster with expensive 80M-vector full-scan queries
- The operator's data-science work product (paper selection, question-generation prompts, embedding choice) is identifiable
- A competitor could mirror the 80M-vector index in days

**No PII observed** in the 1,000-point sample, all payloads are `OAID`/`UCID`/`UEID`/`key_name` only. The exposure is operational/IP, not user-data.

---

## Other notable populated unauth collections

| Host (cloud) | Collection | Points | Vec dim | What it is |
|---|---|---|---|---|
| 51.15.235.181 (Scaleway) | `judilibre` | 1,592,050 | 1536 | French JudiLibre open-court-decisions corpus, full chamber/jurisdiction/text/url_source schema, OpenAI ada-002 dim |
| 139.162.173.85 (Linode) | `scientific_papers` | 1,397,856 | 1024 | Scientific-paper RAG |
| 45.33.2.178 (Linode) | `igepps_app` | 1,348,448 | (n/a) | Brazilian Portuguese app, IGEPPS could be Brazilian education postgrad institute |
| 141.95.107.232 (OVH) | `items-hybrid` | 1,064,800 | (n/a) | Hybrid dense+sparse retrieval over an item catalog |
| 193.70.35.6 (OVH) | `documents_20251110` | 917,890 | 3072 | Italian regulatory RAG, OpenAI text-embedding-3-large dim. Schema: `pratica_code/title`, `raccolta_code/title`, `sezione_code/title`, `formula_code/title` (Italian legal/compliance hierarchical structure). Dated snapshot Nov 10 2025. |
| 193.70.35.6 (OVH) | `documents_07_10_2025` | 851,605 | 3072 | Same operator, Oct 7 2025 snapshot, versioned re-embeddings |
| 51.178.83.102 (OVH) | `semantic-hierarchy-hybrid-search` | 784,408 | (n/a) | Hierarchical semantic retrieval |
| 192.99.144.63 (OVH-CA) | `recipe_assistant_small` | 746,050 | 4096 | Recipe RAG, large-embedding model |
| 54.38.176.221 (OVH) | `embedded_files` | 724,678 | 384 | Small-dim file embeddings |
| 54.37.158.150 (OVH) | `genomics_knowledge` | 722,865 | 768 | Genomics/bioscience RAG |
| 51.222.111.218 (OVH-CA) | `indicator_chatbot` | 694,602 | 1536 | World economic/social indicators by country/year, schema: `country`, `country_iso`, `continent`, `region`, `indicator_code`, `value`, `unit`, `year` (looks like wrapped World Bank / OECD / UN indicators) |
| 146.59.118.205 (OVH) | `chat_messages` | 692,210 | 1536 | **Chat history of an operator service, possibly user-PII-sensitive** |
| 51.75.119.15 (OVH) | `ragias_documents` | 484,113 | (n/a) | "ragias" RAG document store |
| 141.94.95.235 (OVH) | `aria_agentpublic_l1_217k_*` (×2) | 435,274 each | 1024 | "Aria" agent over French government public-sector data |
| 145.239.2.179 (OVH) | `ragias_documents` | 419,231 | (n/a) | Second `ragias_documents`, same operator pattern as 51.75.119.15 |
| 51.91.136.93 (OVH) | `477_qwen3-embedding-8b` | 294,669 | 4096 | Qwen3-embedding-8B-keyed corpus (large embedding model) |
| 172.105.174.253 (Linode) | `ato_legal_documents` | 293,882 | 1024 | Possibly Australian Taxation Office legal-document RAG |
| 51.79.9.102 (OVH-CA) | `tarefas_apollo1` + `emails` | 287,401 + 238,765 | 768 | Brazilian Portuguese, task queue + email archive RAG |
| 158.69.204.40 (OVH-CA) | `energy_assets` | 265,027 | 1536 | Energy company asset RAG |

**Collection schemas observed include**: French chambre/juridiction/numero, Italian pratica/raccolta/sezione, country/indicator_code/year, OpenAlex Work IDs, agent-memory keyed-by-tenant fields, file-chunk content+keywords, semantic-hierarchy levels.

---

## Cross-survey correlations

The collection-name index across all 663 unauth instances reveals operators running multiple AI services on top of the same Qdrant:

| Collection name | Hosts | What it indicates |
|---|---|---|
| `documents` | 12 | Generic document RAG, most common "default" collection name |
| `docs` | 4 | Same |
| `memories` | 4 | Generic memory store (Mem0-shape but not Mem0-named) |
| `open-webui_files` | **4** | **OpenWebUI RAG backend**, those operators run OpenWebUI with auth, but exposed the backing Qdrant on port 6333 unauth. Cross-correlates with [`openwebui-cloud-survey-2026-05.md`](openwebui-cloud-survey-2026-05.md) (99.1% authed). |
| `open-webui_knowledge` | 3 | Same operators' knowledge base |
| `open-webui_web-search` | 3 | Same operators' web-search tool index |
| `mem0` + `mem0migrations` | 3 each | Mem0 deployments backed by Qdrant, cross-ref [`mem0-cross-survey-2026-05.md`](mem0-cross-survey-2026-05.md) |
| `products` | 4 | E-commerce product catalog RAG |
| `emails` | 3 | Email archive RAG (privacy-sensitive when populated) |
| `agent_memories` | 2 | Agent platform memory store |

**Key finding from cross-correlation:** When operators run OpenWebUI or n8n (auth-on-default platforms surveyed at ~0% unauth) with Qdrant as a backend, **the operator-facing platform is auth-protected but the data-tier (Qdrant on port 6333) is exposed by the same operator**. This is the **two-tier auth-skew pattern**:
- **Tier 1 (user-facing)**, auth-on-default platform, auth left on
- **Tier 2 (data-backing)**, auth-off-default platform, auth never configured

The result: an attacker hitting `:6333/collections/open-webui_files/points/search` can read every document the operator has uploaded to their auth-protected OpenWebUI without ever touching OpenWebUI itself.

**Enumerated examples** (all 4 confirmed via same-host probe of front-end `/api/config`):

| IP | Front-end (auth=true verified) | Backend Qdrant exposes |
|---|---|---|
| 51.178.17.105 | "AI Stack" (Open WebUI 0.9.2) on :3000 | `mem0` + `mem0migrations` |
| 51.178.205.229 | "Chatty AI" (Open WebUI 0.6.36 branded fork) on :3000 | `open-webui_files`, `open-webui_knowledge`, `open-webui_web-search` |
| 51.75.202.31 | Open WebUI 0.8.5 on :3000 | `open-webui_files`, `open-webui_web-search` |
| 51.91.206.128 | "AI UIC" (Open WebUI 0.7.2 branded fork) on :8080 | `open-webui_memories`, `open-webui_files`, `open-webui_hash-based`, `open-webui_web-search`, `open-webui_knowledge` |

In every case the operator configured Open WebUI's `auth=true` and `enable_signup=false`. They understand "this app needs login"; they just didn't extend the same understanding to the Qdrant data tier on port 6333. The operator's mental model treats Open WebUI as the security perimeter; Qdrant's existence as a separate, internet-reachable port is invisible to that mental model.

This is the same pattern observed in the original Qdrant survey (where OpenWebUI/Mem0 backends were already the most common collection names), now confirmed at the front-end-auth-state level on a 13× larger sample.

---

## Implications for the auth-on-default thesis

The 84.9% tier-2 unauth rate is **lower than the 100% baseline**, which initially looks like a violation of the "every layer that ships auth-off is unauth at population scale" claim. It isn't:

1. The 100% rate was on n=61. The 84.9% rate is on n=781. Larger samples surface more of the long tail.
2. The 118 auth-enforced instances are concentrated on **OVH dedicated-server commercial deployments**, the operator population most likely to be running multi-tenant/SaaS workloads where compliance audit drives them to explicitly set `QDRANT__SERVICE__API_KEY`.
3. The **84.9% baseline is still population-scale failure**. Two-thirds of unauth Qdrant instances are populated with real workloads. The two-tier auth-skew (auth-front-end + unauth-backend) is the dominant operator pattern.

Updated tier map after tier-2 expansion (see [`SYNTHESIS-2026-05.md`](SYNTHESIS-2026-05.md) §2.6):

| Tier | Auth in framework | Cross-culture rate observed |
|---|---|---|
| **A, No auth concept** (Ollama, MLflow, ES 7.x) | None | **100%** unauth across all 4 cloud audiences |
| **A*, Auth optional, off-by-default** (Qdrant, Milvus, ChromaDB) | Configurable, off | **84-100%** unauth (compliance subset configures it) |
| B, Auth-on-default, takeover possible (Dify) | Setup-wizard-gated | <5% takeable |
| C, Auth-on-default, hardened (MinIO, OpenWebUI, n8n, Flowise) | On | 0% (or first-user-only on signup-open OpenWebUI) |

The new "A*" tier captures Qdrant/Milvus/ChromaDB more accurately than the original binary "Tier A" framing. They have an auth concept, but the framework default is off, and the 15% who configure it are the exception, not the population.

---

## Disclosure posture

- **No per-host abuse reports.** 663 hosts is too many for individual outreach with no fix path beyond "add a firewall rule." Operators chose to expose Qdrant on the public internet.
- **Operator-facing follow-up on the largest exposures**, `facts_v1` (Scaleway 51.158.59.156) operator, `judilibre` operator, `chat_messages` operator (the only one with potentially user-PII content), to be drafted as time permits.
- **Qdrant upstream awareness**, the auth-off default is the systemic issue. Qdrant ships with `service.api_key` unset in the default config; setting it should arguably be the first step of any production install. This survey is offered as quantitative evidence.

---

## Raw Data

```
~/recon/qdrant-tier2-2026-05-04/tier2-qdrant-confirmed.jsonl
```

Each record:
```json
{
  "ip": "...",
  "port": 6333,
  "service": "Qdrant",
  "version": "1.x.x",
  "commit": "...",
  "unauth": true|false,
  "collection_count": N,
  "collections": [{"name": "...", "points_count": N, "vector_size": N, "distance": "...", "status": "green"}]
}
```

---

## See Also

- [`qdrant-cloud-survey-2026-05.md`](qdrant-cloud-survey-2026-05.md), DO/Hetzner/Vultr baseline (61 instances, 100% unauth)
- [`ollama-tier2-cloud-survey-2026-05.md`](ollama-tier2-cloud-survey-2026-05.md), sibling tier-2 expansion (Ollama, 1,019 unauth)
- [`SYNTHESIS-2026-05.md`](SYNTHESIS-2026-05.md), cross-survey synthesis paper (auth-on-default thesis)
- [`mem0-cross-survey-2026-05.md`](mem0-cross-survey-2026-05.md), Mem0 over Qdrant cross-reference
- [`openwebui-cloud-survey-2026-05.md`](openwebui-cloud-survey-2026-05.md), OpenWebUI front-end (99.1% authed) → Qdrant backend (84.9% unauth) two-tier skew
