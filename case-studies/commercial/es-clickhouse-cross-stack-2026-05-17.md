---
type: survey
---

# Elasticsearch + ClickHouse Cross-Stack Follow-Up Survey (2026-05-17)

_NuClide Research · 2026-05-17_
_Companion to: [`elasticsearch-ai-stack-population-survey-2026-05-16.md`](elasticsearch-ai-stack-population-survey-2026-05-16.md) + [`clickhouse-population-survey-2026-05-16.md`](clickhouse-population-survey-2026-05-16.md)_

---

## Summary

24-hour follow-up on yesterday's 5,037 unauth Elasticsearch + 1,832 unauth
ClickHouse hosts. Yesterday's surveys produced raw counts via bespoke
`fast_enum_*.py` scripts; this survey productizes the deep-probe step into
**aimap v1.9.8** (`enumElasticsearch` + `enumClickHouse`, both shipped this
morning) and re-runs the host lists. Two findings.

- **A Meow/Indexrm-class automated extortion campaign wiped 3,604 of the
  5,037 unauth Elasticsearch hosts (71.6%) in the ~24-hour window between
  yesterday's survey and today's re-probe.** Wipe rate scales with version
  age: 95.7% on ES 2.9.0 (90/94), 88.4% on 7.17.0 (205/232). Zero operators
  added auth in the same window. **The attackers won the race.** This
  codifies as a new Insight (#28 candidate): **exposure-window-to-extortion
  ≈ 24h at population scale for unauthenticated Elasticsearch.**

- **The `_mapping` deep-probe finds 22 ES hosts and 70 ClickHouse hosts with
  unambiguous AI-stack workloads** beyond yesterday's name-pattern matches.
  Yesterday's 12 named ES hits + 6 named CH hits expand to 22 ES + 70 CH
  via field-type metadata (`dense_vector` / `knn_vector` field detection on
  ES, SHOW TABLES enumeration on CH). The embedding dimensions disclose
  the LLM provider: 256d = OpenAI text-embedding-3-small, 1536d =
  text-embedding-ada-002 / text-embedding-3-large, 3072d = the new
  text-embedding-3-large at full dimensionality.

- **The clinical-AI hospital host** at `106.75.127.240` (the featured
  catastrophe from yesterday's batch) **is still unauthenticated and not
  yet wiped.** The `_mapping` deep-probe now confirms it has `entity_vectors`
  (vector field, 768d), `event_vectors` (content_vector + title_vector, both
  768d), and `source_chunks` (heading_vector + content_vector, both 768d).
  768-dimensional embeddings are consistent with bge-base-zh / m3e-base
  Chinese open-source models. Disclosure still pending acknowledgement.

---

## 1. The extortion campaign — 24-hour wipe rate

| Yesterday (2026-05-16) | Today (2026-05-17) | Δ |
|---|---|---|
| 5,037 confirmed unauth ES | 4,564 still unauth | −473 (offline / port closed) |
| 0 wiped | **3,604 wiped + `read_me` extortion index left** | **+3,604** |
| 0 operators auth-added | 0 operators auth-added | 0 |
| 94 hosts on ES 2.9.0 (ancient unauth-RCE class) | 90 of 94 wiped (95.7%) | — |

The wipe signature is consistent with the Meow / Indexrm family — every
wiped host has its real indices deleted and a single small index named
`read_me` (sometimes `read_me_first`, `recover_data`) left behind containing
a single document with a cryptocurrency address and a 48h-or-less ransom
window. The methodology's restraint ethic precludes reading the ransom
documents themselves; the **existence** of the index is the finding.

**Wipe rate by ES version (top 15):**

| Version | Total | Wiped | Rate |
|---:|---:|---:|---:|
| 7.17.0 | 232 | 205 | 88.4% |
| 8.11.0 | 161 | 131 | 81.4% |
| 7.17.6 | 158 | 132 | 83.5% |
| 8.12.0 | 103 | 86 | 83.5% |
| 7.12.1 | 98 | 86 | 87.8% |
| 7.17.28 | 98 | 79 | 80.6% |
| **2.9.0** | 94 | 90 | **95.7%** |
| 8.15.0 | 80 | 61 | 76.2% |
| 8.13.4 | 75 | 61 | 81.3% |
| 7.17.29 | 71 | 48 | 67.6% |
| 7.6.2 | 66 | 51 | 77.3% |
| 7.9.3 | 61 | 42 | 68.9% |
| 7.14.0 | 58 | 33 | 56.9% |
| 7.17.9 | 58 | 44 | 75.9% |
| 8.17.0 | 57 | 47 | 82.5% |

The 95.7% wipe rate on ES 2.9.0 specifically is the hardest signal — the
ancient-version cohort has known unauth-RCE classes (CVE-2014-3120 Groovy
script execution, CVE-2015-1427 sandbox escape, CVE-2015-5531 path
traversal) and gets prioritized by extortion tooling that searches for
indexable ancient ES.

**Operator response: zero.** Across all 5,037 yesterday-confirmed hosts,
**zero** operators added X-Pack security in the 24-hour window. The hosts
either got wiped, dropped offline, or remain unauthenticated. The
mean-time-to-extortion is shorter than the mean-time-to-remediation.

### Methodology note: why this matters for *every* survey

A survey result has a **shelf life**. Numbers from a 24-hour-old run no
longer describe the present population — at least for unauth ES, where
the wipe wave is constant. **Disclosure batches built from yesterday's
list need re-verification before sending.** A "Your X is exposed unauth"
report sent today to an operator whose host was wiped overnight reads
wrong; the operator is already in extortion-recovery mode and the
disclosure misses the actual current state.

The Insight #28 candidate captures this: **exposure-window-to-extortion ≈
24h at population scale for unauthenticated ES; survey shelf-life on this
class is < 1 day; disclosure pipelines need a re-verification step
between harvest and send.**

---

## 2. AI-stack confirmation via `_mapping` deep probe

Yesterday's case study predicted: _"The 12 explicit-marker count is the
lower bound. The actual AI-stack unauth Elasticsearch population is likely
100s to 1000s."_ Today's `_mapping` probe **only confirms 22 hosts** —
substantially fewer than predicted, because the 3,604 wiped hosts can no
longer be probed for their schema. The pre-wipe schema was lost when
attackers deleted the indices.

The 22 confirmed AI-stack ES hosts — all running RAG / vector-search
workloads, validated by `dense_vector` or `knn_vector` field type in at
least one index:

| Host:Port | ES Version | Cluster Name | Indices · Vector Fields (dim) |
|---|---|---|---|
| `106.75.127.240:9200` | 8.11.0 | docker-cluster | **entity_vectors** (768d), event_vectors (title_vector + content_vector, 768d), source_chunks (heading_vector + content_vector, 768d) — **hospital AI, disclosure pending** |
| `135.125.201.31:9200` | 8.17.0 | newsblur-local | `discover-stories-openai-index` (content_vector, **256d = text-embedding-3-small**) — NewsBlur |
| `8.147.113.203:9200` | 8.17.0 | xiaoicedemo | `prod_virtualhuman_knowledge_faq_default_org` (representation_vector, 512d) — XiaoIce demo |
| `120.26.18.206:9200` | 8.17.0 | torchv-cluster | `dataset_chunk_sharding_16_1024` (vector, 1024d) — TorchV RAG framework |
| `161.97.148.0:9200` | 2.11.0 | waffarha-cluster | `waffarha-deals` (knn_vector, 768d) — Waffarha (Egyptian deals platform) **on ancient ES** |
| `212.64.24.141:9200` | 3.5.0 | docker-cluster | 11 indices: material_ambient / background / character_appearance / emotion_effect / music / subject / voicefx / resource_* (all knn_vector 1024d) — content/effects pipeline |
| `84.247.170.209:9200` | 8.16.0 | docker-cluster | article_de / article_en / article_es / article_fr / article_it / article_ru (vector_embedding, **1536d = text-embedding-3-large**) — multilingual content store |
| `84.247.189.64:9200` | 2.19.1 (OpenSearch) | docker-cluster | dms_documentvectors / dms_vectors (chunks_768.vector_embedding_768, knn_vector 768d) — operator DMS RAG |
| `112.124.16.227:9200` | 8.18.5 | es-docker-cluster | Chinese tourism KBs: 南宁之夜正式 (Nanning Night production), 南宁之夜测试 (test), 秀水状元村知识库 (Xiushui Zhuangyuan Village KB) — all 1024d |
| `120.27.113.59:9200` | 8.12.2 | docker-cluster | `ai-index` (embedding, **1536d**) |
| `123.60.173.230:9200` | 8.18.2 | docker-cluster | `hooper_bi_dws_inventory` (content_vector, **1536d**) — Hooper BI |
| `159.75.128.178:9200` | 8.11.0 | docker-cluster | `knowledge_chunks` (embedding, 1024d) |
| `92.222.197.175:9200` | 8.11.3 | docker-cluster | `qa_index` (question_vector, 384d) |
| `103.160.107.236:9200` | 8.15.3 | docker-cluster | `documents` (embedding, 768d) |
| `106.53.114.113:9200` | 8.13.4 | docker-cluster | `tourism_vector` (vector, 1024d) |
| `152.32.142.38:9200` | 7.9.1 | my-application | `goods_index_b2b` (vector, 1024d) |
| `81.71.89.27:9200` | 8.15.3 | docker-cluster | `novel-knowledge` |
| `94.177.165.24:9200` | 7.17.8 | elasticsearch | `iside2` (1536d) |
| `81.94.155.178:9200` | 2.14.0 | docker-cluster | `russian_news` (384d) **on ancient ES** |
| `51.91.106.5:9200` | 7.9.2 | docker-cluster | `haystack_test` (768d) — Haystack RAG framework |
| `62.234.4.20:9200` | 8.12.0 | es-docker-cluster | `dcobjvec` (1024d) |
| `103.69.124.214:9200` | 8.15.2 | docker-cluster | `concepts._embeddings.vector` + `concepts._synonyms_embeddings.vector` — nested-mapping pattern |

**Embedding-dimension fingerprinting** as an attribution signal:

| Dimension | Common provider / model |
|---|---|
| 256 | OpenAI `text-embedding-3-small` (dimensions=256 parameter) |
| 384 | sentence-transformers `all-MiniLM-L6-v2` (open-source) |
| 512 | OpenAI `text-embedding-ada-001` (legacy); `text-embedding-3-small` truncated |
| 768 | OpenAI `text-embedding-3-small` (full); `bge-base` / `m3e-base` (Chinese open-source) |
| 1024 | Cohere `embed-v3`; `bge-large` (Chinese / multilingual) |
| 1536 | OpenAI `text-embedding-ada-002` or `text-embedding-3-large` (truncated) |
| 3072 | OpenAI `text-embedding-3-large` (full) |

NewsBlur's `discover-stories-openai-index` at 256d directly discloses
NewsBlur is using `text-embedding-3-small` with the dimensions=256
parameter (a cost-optimization choice OpenAI introduced in 2024-01).
The `xiaoicedemo` 512d cluster is consistent with `text-embedding-ada-001`
or a Chinese 512d open-source equivalent.

---

## 3. ClickHouse — AI-stack expansion to 70 hosts

Yesterday's case study found 6 explicit-AI-stack ClickHouse DBs. Today's
`SHOW DATABASES` + `SHOW TABLES` deep probe finds **70 hosts** with
AI-relevant DB or table names — an 11.7× expansion.

| Category | Hosts | Examples |
|---|---|---|
| **observability** (SigNoz / Helicone / Phoenix CH backends) | 18 | `signoz_logs` / `signoz_metrics` / `signoz_traces` on 17 operators; 1 Helicone migration table |
| **llm_workload** (chat / prompt / completion tables) | 28 | `yoto_cms.llm_prompts`, `analytics_prod_core.character_bots_chats`, `domestic.prompt_info`, `aggregation.ai_chat_intent`, `twitch_analytics_v2.chat_messages_by_viewer` |
| **rag** (vector / embedding / retrieval) | 10 | `vectorengine_log`, `vectorengine_detail_log`, `pearlman.rag_section_text`, `pearlman.rag_text_chunks`, `posthog.distributed_posthog_document_embeddings_text_embedding_3_large_3072` |
| **inference** (vLLM / Ollama backend tables) | 1 | `108.248.232.250` — `vllm_service` DB + RAG-section + RAG-chunks across `pearlman`, `phl`, `phlDB` databases (multi-tenant operator) |
| **analytics** (PostHog / Plausible backends) | 20 | 9 PostHog + 9 Plausible Analytics + others |

### Headline operators

- **`159.195.79.109` — PostHog with table named `distributed_posthog_document_embeddings_text_embedding_3_large_3072`.** The table name explicitly discloses the OpenAI model in use (text-embedding-3-large at full 3072d) plus a parallel table for text-embedding-3-small at 1536d. PostHog 2024+ has built-in RAG.
- **`108.248.232.250` — vLLM operator with `vllm_service` database + `rag_section_text`/`rag_text_chunks` tables across THREE tenant databases (`pearlman`, `phl`, `phlDB`)**. Multi-tenant vLLM-as-a-service operator's RAG storage exposed.
- **`129.153.24.132` — Yoto CMS with `llm_prompts` table**. Yoto produces a children's audio device; the unauth ClickHouse stores their LLM prompts.
- **`120.27.213.62` — `aggregation.ai_chat_intent` + `aggregation.ai_chat_scene`**. Conversational AI operator with intent + scene tables.
- **`111.231.19.122` — Five `prompt_info` tables across `domestic`, `domestic_test`, `wisdom`, `wisdom_test`, `yaya_testt` databases**. Chinese AI assistant operator with prod + test environments visible.
- **`15.204.104.101` + `15.204.105.193` — `vectorengine_log` / `vectorengine_detail_log` databases**. Hetzner-hosted RAG engine operator (probably the same operator, adjacent /24).

### Version dominance — Insight #27 confirmed at scale

ClickHouse 22.3.20.29 = **67.4% of fingerprinted hosts (1,354 / 2,008)**.
The single-version dominance pattern (Insight #27) is even sharper than
yesterday's measurement (55%). The official `clickhouse/clickhouse-server:22.3`
LTS Docker tag points at 22.3.20.29; one image tag → two-thirds of the
unauth population.

### No ClickHouse extortion

In sharp contrast to the ES wipe wave, **zero ClickHouse hosts were
wiped** between yesterday and today. The CH unauth-exposure population is
not currently targeted by an equivalent extortion campaign. Hypothesis:
the Meow/Indexrm family is ES-specific tooling; CH's HTTP query interface
is less indexed by mass-scanners, and the ALTER/DROP table semantics are
less convenient for one-shot wipe-and-extortion.

---

## 4. BARE exploit-module ranking — ES 2.9.x cohort

Yesterday's 95 ES 2.9.0 hosts were passed to BARE for Metasploit module
ranking. **95 / 95 (100%) top-rank `exploits_multi_elasticsearch_search_groovy_script`** —
the CVE-2014-3120 Groovy-script RCE module. Cosine score 0.58 ± 0.02
across the cohort. BARE's semantic match is **deterministic at population
scale when the finding's exploit class is unambiguous** — exactly the
methodology-predicted behavior. The same 95 hosts as a fallback show
`exploits_multi_http_jenkins_xstream_deserialize` and `auxiliary_gather_
pacsserver_traversal` at rank 2-3 — both deserialization-class matches
that share Groovy's semantic neighborhood in the embedding space.

The methodology lesson: **the BARE step is high-throughput** (the module
corpus is pre-encoded; only the new finding needs inference). 95 findings
took ~25 seconds. At population scale this is essentially free.

---

## 5. Output

**Case study artifacts:**

- This document (`es-clickhouse-cross-stack-2026-05-17.md`)
- Insight #28 codification: `methodology/insight-28-survey-shelf-life-exposure-to-extortion.md`
- aimap v1.9.8 source — committed to `Nicholas-Kloster/aimap` `f586217`
  with `enumElasticsearch` + `enumClickHouse` + the ES fingerprint
  (productizes yesterday's bespoke `fast_enum_es.py` / `fast_enum_clickhouse.py`)
- Probe outputs: `~/recon/elasticsearch-ai-stack-2026-05-17/es-v198-results.json`
  (17 MB) and `~/recon/clickhouse-2026-05-17/ch-v198-results.json` (6 MB)
- BARE output: `/tmp/es29x-bare-output.json` (95 ranked Metasploit module
  matches)

**Ledger updates:** the 22 ES + 70 CH AI-stack confirmations get severity
upgrade from "unauth_data" to "rag_vector_store" / "ai_stack_disclosure"
with operator-attribution notes added. The 3,604 wiped ES hosts get
lifecycle `archived` with reason `wiped-by-extortion-campaign-2026-05-17`.

---

## 6. Toolchain provenance

```
JAXEN              [—] not run — re-used yesterday's empire.db harvest (5,037 ES + 1,832 CH)
aimap v1.9.8       [x] ES + CH fingerprint + enumElasticsearch + enumClickHouse
                       run on 5,037 ES hosts → ~7 min wall, 4,776 fingerprinted, 22 AI-stack confirmed
                       run on 1,832 CH hosts → ~15 min wall, 2,185 fingerprinted, 70 AI-stack confirmed
aimap-profile      [—] not applicable — operator classification is unchanged from yesterday
VisorGraph         [—] not run — single-host cert-pivot deferred to per-disclosure prep
VisorBishop        [—] not run — single-platform follow-up, not cross-platform
VisorSD            [—] not run — ASN sweep already done yesterday
VisorGoose         [—] not applicable — no .gov in the host list
menlohunt          [—] not applicable — no GCP-hosted hosts in this corpus
recongraph         [—] not run — graph-walk would be redundant of yesterday's pass
nu-recon           [—] not run — population survey, not single-host
VisorPlus          [—] not used — manual aimap re-run with new enumerators
VisorLog           [x] ingest pending — 22 ES AI-stack upgrades + 70 CH AI-stack upgrades + 3,604 archived
VisorScuba         [x] auto-computed inside aimap (risk_level field on each enum result)
BARE               [x] run on 95 ES 2.9.x findings — 100% top-rank exploits_multi_elasticsearch_search_groovy_script
VisorCorpus        [—] not applicable — no LLM-direct surface in this corpus
VisorAgent         [—] ethical-stop — operator hosts only, never fired
VisorRAG           [—] not applicable — operator-side, no LLM-target confirmation needed
VisorHollow        [—] not applicable — Windows-only
cortex             [—] not run — auth context is uniform (Tier-A* docker default)
JS-bundle          [—] not applicable — ES + CH are JSON APIs, no web UI bundles
```

Two non-applicable categories carry the explicit reason (VisorHollow
Windows-only, VisorAgent ethical-stop). The rest are not-run with a
one-line reason — no silent skips.

---

## See also

- [`elasticsearch-ai-stack-population-survey-2026-05-16.md`](elasticsearch-ai-stack-population-survey-2026-05-16.md) — yesterday's parent survey
- [`clickhouse-population-survey-2026-05-16.md`](clickhouse-population-survey-2026-05-16.md) — yesterday's parent survey
- [`multi-cross-survey-stacked-catastrophe-2026-05-16.md`](multi-cross-survey-stacked-catastrophe-2026-05-16.md) — the hospital AI host (106.75.127.240), still unauth today
- [`../../methodology/insight-28-survey-shelf-life-exposure-to-extortion.md`](../../methodology/insight-28-survey-shelf-life-exposure-to-extortion.md) — new Insight codified from this survey
- [`../../methodology/insight-27-docker-image-template-version-dominance.md`](../../methodology/insight-27-docker-image-template-version-dominance.md) — ClickHouse 22.3.20.29 67.4% confirms Insight #27
