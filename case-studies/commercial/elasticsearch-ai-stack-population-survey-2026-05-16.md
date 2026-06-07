---
type: survey
---

# Elasticsearch AI-Stack Population Survey (2026-05-16)

_NuClide Research · 2026-05-16 (Survey 9 of the day's 10-category batch)_
_Closes: category 25 (elasticsearch) with AI-stack focus_

---

## Summary

Population survey of Elasticsearch clusters with focus on AI-stack adjacency. RAG vector stores, langchain/llama-index indices, embedding caches, prompt history. Elasticsearch has been a major exposure surface for ~8 years (the original "exposed Elasticsearch" panic was 2015); the novel angle here is the **AI-stack-specific index-naming** as an operator-attribution channel.

<!-- ksat-tag:auto-generated:start -->
## DCWF KSAT coverage

Auto-derived from DCWF AI work-role rule files (`ksat-tag`).

- **672 (AI Test & Evaluation Specialist):** K7003, K7004, K7044, S7068, S7070, S7075, T5858, T5904
- **733 (AI Risk & Ethics Specialist):** T5868, T5893
- **overlap (Common AI KSATs (all 5 roles)):** K1158, K1159, K22, K6311, K6935, K7003, K942, S7065

<!-- ksat-tag:auto-generated:end -->

- 9,263 candidates harvested via `port:9200 elastic` Shodan filter
- Probed via `fast_enum_es.py` (threads=120, ~12 min)
- **5,037 confirmed unauth Elasticsearch instances** (54% real-rate, high)
- 573 partial-open (root `/` returns 200 but `/_cat/indices` blocked)
- 50 auth-gated, 3,564 dead, 39 unknown
- **12 confirmed with explicit AI-stack index markers** (conservative, many more probably AI-adjacent under generic index names like `documents`, `vector_data`)

**Headline:** 5,037 unauth Elasticsearch instances at population scale. Of those, 12 have indices explicitly named with AI-stack terminology (langchain, llama-index, vector, embedding, rag, prompt, etc.). The real AI-stack overlap is likely 5–10× larger. Most operators use generic index naming.

---

## The AI-stack indices found unauth

| Cluster name | AI-stack indices | Operator inference |
|---|---|---|
| `docker-cluster` (101.37.235.13:9200) | `spring-ai-document-index` | Spring AI RAG application |
| `docker-cluster` (106.52.63.235:9200) | `rag-document-chunks` | RAG chunking pipeline output |
| `docker-cluster` (106.53.114.113:9200) | `tourism_vector` | Tourism vertical's vector embeddings |
| `docker-cluster` (106.75.127.240:9200) | `entity_vectors`, `event_vectors` | Entity-extraction + event-classification pipeline |
| **`chipmong-kb-cluster`** (109.123.236.152:9200) | `kb_documents_v1` | **Likely Chipmong** (Cambodian conglomerate) **knowledge-base RAG** |
| `docker-cluster` (115.190.215.237:9200) | `easymall-index-vectorstore` | E-commerce ("EasyMall") vector store |
| `my-application` (115.239.230.165:9200) | `es_resource_vector_402880c494f943f30194f943f3f50001` | Templated multi-tenant vector index (UUID-suffixed) |
| `newsblur-local` (135.125.201.31:9200) | `discover-stories-openai-index` | **NewsBlur** "discover stories" feature running on OpenAI embeddings |
| `opensearch-cluster` (212.132.124.128:9200) | `pimcore_document-even` | **Pimcore CMS** document indexing |
| `docker-cluster` (36.135.53.26:9200) | `test_pic_vector` | Dev/test image-vector pipeline |
| `docker-cluster` (84.247.189.64:9200) | `dms_documentvectors`, `dms_vectors` | Document Management System with vectorization |
| `docker-cluster` (87.106.168.100:9200) | `pimcore_arplan_document-odd` | Pimcore CMS — "arplan" (architectural plan?) docs |

The cluster name + index names disclose the operator's stack and use case. `chipmong-kb-cluster` is a direct operator-attribution hit (Cambodian construction conglomerate Chipmong). `newsblur-local` discloses the RSS-reader service NewsBlur is running a development cluster with their OpenAI-embedding-driven "discover stories" feature publicly reachable. `pimcore_arplan_document-odd` discloses Pimcore CMS running an architectural-plan document workload.

---

## Why most AI-stack workloads ARE in the 5,025 generic unauth set

Of the 5,037 unauth Elasticsearch hosts, only 12 use index names with explicit AI-stack markers. The other 5,025 use generic index names like `documents`, `posts`, `users`, `logs`, `metrics`, `app_data`. But many of these almost certainly back AI workloads. RAG document stores are commonly named just `documents`, vector indices just `embeddings` (no prefix), prompt history just `chat_messages`.

Without sampling document contents (which crosses the restraint line), we can't distinguish AI-backed from non-AI workloads at scale. **The 12 explicit-marker count is the lower bound. The actual AI-stack unauth Elasticsearch population is likely 100s to 1000s.**

This is a methodology lesson: AI-stack workloads at this layer (RAG document stores backed by general-purpose document indices) are not separable from generic document workloads via index naming alone. The auth-state finding is independent of AI adjacency.

---

## Elasticsearch version distribution (top of unauth set)

```
  239  7.17.0    (largest single-version cluster — 7.x is EOL since 2024-08)
  178  8.11.0
  159  7.17.6
  112  8.12.0
  109  7.12.1
  101  7.17.28
   95  2.9.0     (ancient — pre-X-Pack era, has multiple unauth RCEs)
   86  8.13.4
   85  8.15.0
   79  7.17.29
```

Heavy 7.x concentration. Elasticsearch 7.x reached end-of-life August 2024; operators on 7.x are unmaintained. The 95 hosts on **2.9.0** (released ~2017) are exposed to multiple unauthenticated RCEs including CVE-2015-1427 (Groovy scripting RCE).

The dominant `cluster_name: "docker-cluster"` (observed across most hosts) is the default name in the official Elasticsearch Docker image. Operators using the official Docker image without customizing the cluster name. Same pattern as the Solr 7.6.0 cluster from the prior batch. Docker-image-deployed at scale, never customized.

---

## Methodology placement

Elasticsearch is **Tier-A* (auth optional, off-by-default in the official Docker image)**. Elastic Stack ships with X-Pack security available but DISABLED by default in the open-source Docker image (`elasticsearch:7.x`, `elasticsearch:8.x`). To enable, operators must:

1. Set `xpack.security.enabled=true` in elasticsearch.yml
2. Run `elasticsearch-setup-passwords` to set the elastic user password
3. Configure TLS for transport (newer versions force this)

Step 1 is a single line of config. The fact that **54% of Shodan-reachable Elasticsearch instances skip it** is a Tier-A* signature (LiveKit-template-pattern: framework auth available, default deployment skips it).

This survey adds Elasticsearch (Docker default) to:

| Tier | Definition | Member platforms |
|---|---|---|
| A* | Auth optional, off-by-default in default deployment template | LiveKit `/api/connection-details`, Airflow `AUTH_ROLE_PUBLIC=Admin`, **Elasticsearch (Docker default)** |

---

## Cross-survey colocation

| Pair | Overlap |
|---|---|
| Elasticsearch ∩ ComfyUI (548) | 0 |
| Elasticsearch ∩ Solr+Meili (881 from Survey 4 prior batch) | TBD via ledger diff |
| Elasticsearch ∩ Vault (912 from 2026-05-15) | TBD |

Elasticsearch operators are mostly distinct from the AI-tier-direct operator population. They're general-purpose document-search ops who happen to be storing AI workload data, vs the AI-tier operators who run dedicated vector DBs.

---

## Toolchain Provenance

```
0. shodan download (port:9200 elastic) → 9,263 unique ip:port
1. fast_enum_es.py (threads=120) → 9,263 probed in ~12 min
2. /_cat/indices?format=json on each unauth host → 5,037 confirmed unauth, 12 with AI-stack markers
3. /_cluster/health follow-up sampling (deferred)
4. (queued) visorlog ingest → 5,037 events into nuclide.db source='elasticsearch-ai-stack-survey-2026-05-16'
```

---

## Honest negative space

- **AI-stack index marker list is incomplete.** The 12-explicit-marker count uses a 25-substring marker list. Real RAG / vector workloads frequently use generic names (`docs`, `embeddings`, `data`). A second pass with a tighter "vector + dimension > 100" Mapping API probe would catch them, but requires `_mapping` API calls per index. High-touch and out-of-scope for this survey.
- **5,037 unauth hosts are not all "AI-stack"**: many are generic log/document/metric search workloads. The number's value is in the auth-on-default Tier-A* confirmation, not in the AI-relevance claim.
- **No document sampling.** Restraint: `GET /<index>/_search?size=1` would return a sample doc and prove or refute AI-stack adjacency, but reading data crosses the restraint line. Index names + cluster names are the finding.
- **Honeypot filter not yet applied.** Some Linode IPs in the 5,037 set likely belong to AS63949 honeypot fleet (~393 hosts globally). Filter pass pending.
- **OpenSearch overlap**: some of the candidates may be Amazon OpenSearch (the AWS-forked Elasticsearch). They expose the same shape; the fingerprint catches both. Per AWS's documentation, OpenSearch is generally deployed with auth enforced via IAM; the 12 AI-stack hits include 1 `opensearch-cluster` named instance.

---

## Disclosure posture

- **Aggregate Tier-A* disclosure recommended** to Elastic.co and to Docker Hub maintainers of `elasticsearch:7.x` / `elasticsearch:8.x` official images. The default-off Docker image is the load-bearing cause; both maintainers control this.
- **Targeted per-host disclosure** for the 12 explicit-AI-stack hosts. The NewsBlur and Chipmong hosts in particular are operator-attribution-rich; coordinated disclosure to the named organizations is appropriate.

---

## See also

- [[insight-13-shipping-defaults-are-load-bearing]]. Docker-image default (auth-off) drives 54% unauth rate
- [[insight-25-falsification-confirmation-tier-c-platforms]]. Elasticsearch is the largest Tier-A* surface measured to date
- [`vectordb-stragglers-population-survey-2026-05-16.md`](vectordb-stragglers-population-survey-2026-05-16.md): Solr 7.6.0 Docker-image-template parallel
- [`clickhouse-population-survey-2026-05-16.md`](clickhouse-population-survey-2026-05-16.md): companion specialty-data-layer survey same day
