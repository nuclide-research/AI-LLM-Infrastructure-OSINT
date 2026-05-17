---
type: survey
---

# Cross-stack 24-hour follow-up on Elasticsearch and ClickHouse (2026-05-17)

_NuClide Research · 2026-05-17_
_Companion to: [`elasticsearch-ai-stack-population-survey-2026-05-16.md`](elasticsearch-ai-stack-population-survey-2026-05-16.md), [`clickhouse-population-survey-2026-05-16.md`](clickhouse-population-survey-2026-05-16.md)_

---

## Summary

Yesterday's surveys produced raw counts of 5,037 unauthenticated Elasticsearch hosts and 1,832 unauthenticated ClickHouse hosts. The verification ran through bespoke Python scripts. This survey ships **aimap v1.9.8** (`enumElasticsearch` and `enumClickHouse`) and re-runs both host lists.

Three findings.

**One.** 4,776 of the 5,037 ES hosts still respond to fingerprinting. 4,564 of those are still unauthenticated. **0 operators added authentication in the 24-hour window.** 92.4% already carried a Meow `read_me` index at first observation. The "71.6% wiped in 24 hours" framing from this morning was wrong as a rate. It is the equilibrium of a long-running campaign. The correction lives in Insight #28 (retracted) and Insight #29 (snapshot vs delta).

**Two.** The deep `_mapping` probe confirms **22 ES hosts** with `dense_vector` or `knn_vector` field types. **70 ClickHouse hosts** with AI-stack DB or table names (SigNoz, PostHog, Plausible, vllm_service, RAG chunks, LLM prompts). The embedding dimensions disclose the LLM provider. Operators using OpenAI sit at 256, 1536, or 3072 dimensions. Operators using bge or m3e Chinese open-source models sit at 768 or 1024.

**Three.** The hospital host from yesterday (`106.75.127.240`) carries a `read_me` index now. Its `entity_vectors`, `event_vectors`, and `source_chunks` indices are still alive at 6.7 GB total. The attacker has marked the host. The data is not yet wiped.

---

## Re-probe deltas

| Yesterday (2026-05-16) | Today (2026-05-17) | Δ |
|---|---|---|
| 5,037 confirmed unauthenticated ES | 4,564 still unauthenticated | 473 dropped offline or port closed |
| 0 wiped | 3,604 with `read_me` index only | 3,604 (state, not rate) |
| 0 operators added auth | 0 operators added auth | 0 |

The 92.4% / 1.7% / 5.4% / 6.0% four-cell breakdown of state-change between probes is in Insight #29.

---

## Productized tooling. aimap v1.9.8

The bespoke `fast_enum_es.py` and `fast_enum_clickhouse.py` from yesterday are replaced by two new aimap enumerators.

**Elasticsearch fingerprint.** Conjunctive matcher on GET `/`: status 200, `version` object, `cluster_name`, `cluster_uuid`, body contains "lucene_version." The four-conjunct anchor matches both Elasticsearch and OpenSearch.

**`enumElasticsearch`.** Pulls cluster identity, `/_cluster/health`, `/_cat/indices`, and per-index `_mapping` (capped at 30 per host). Walks one level of nested-object schemas to catch the chunks pattern that Spring AI and LangChain Java use. Captures both ES `dims` and OpenSearch `dimension` spellings of `dense_vector`, `knn_vector`, and `sparse_vector`.

**`enumClickHouse`.** Issues `SHOW DATABASES` and `SHOW TABLES` over the HTTP GET query interface. Caps at 60 databases and 200 tables per host. Scans names for AI-stack markers.

Both enumerators are GET-only. The ES probe never reads documents. The ClickHouse probe never reads rows.

Repo: `Nicholas-Kloster/aimap` commit `f586217`. Tests clean.

---

## Elasticsearch AI-stack confirmations

22 hosts with at least one vector field in at least one index. Full per-host table in [`22-ai-stack-attribution-2026-05-17.md`](22-ai-stack-attribution-2026-05-17.md).

Named operators include:

- **103.69.124.214** (cert SAN `ocl.hmis.gov.np`). Nepal Ministry of Health. 318,114 clinical concepts. Mid-wipe.
- **106.75.127.240**. Multi-tenant hospital AI on UCloud Shanghai. 270,000 patient-record vectors. Mid-wipe.
- **135.125.201.31** (cluster `newsblur-local`). NewsBlur. `discover-stories-openai-index` at 256d. Mid-wipe.
- **84.247.170.209**. German multilingual AI travel. `article_de` through `article_ru` at 1536d. Mid-wipe.
- **120.26.18.206** (cluster `torchv-cluster`). ZLMediaKit Chinese streaming SDK running TorchV RAG. Clean.
- **8.147.113.203** (cluster `xiaoicedemo`). XiaoIce demo cluster, virtual-human FAQ at 512d. Mid-wipe.
- **84.247.189.64** (cert `aitalkx.com`). AItalkx DMS RAG. OpenSearch 2.19.1. `chunks_768.vector_embedding_768`. Mid-wipe.
- **112.124.16.227** (cert `gxota.com`). Guangxi OTA, 53 SAN multi-tenant Chinese tourism. Clean.
- **161.97.148.0** (cert `lms.equant-tech.com`). Egyptian LMS, Waffarha deals. ES 2.11.0 (ancient unauth-RCE class). Wiped.

The morning's earlier claim of "12 named hits will expand to 100s or 1000s" did not pan out. The reason: 3,604 wiped hosts cannot be probed for schema. The 22 confirmed AI-stack hosts are the ones whose data is still alive.

---

## ClickHouse AI-stack confirmations

70 hosts surface AI-stack workloads in DB or table names. 11.7× expansion from yesterday's 6 named hits.

| Category | Hosts | Examples |
|---|---:|---|
| Observability (SigNoz / Helicone) | 18 | `signoz_logs`, `signoz_metrics`, `signoz_traces` on 17 operators |
| LLM workload (chat / prompt / completion) | 28 | `yoto_cms.llm_prompts`, `analytics_prod_core.character_bots_chats`, `domestic.prompt_info`, `aggregation.ai_chat_intent`, `twitch_analytics_v2.chat_messages_by_viewer` |
| RAG (vector / embedding / retrieval) | 10 | `vectorengine_log`, `pearlman.rag_section_text`, `posthog.distributed_posthog_document_embeddings_text_embedding_3_large_3072` |
| Inference (vLLM / Ollama) | 1 | `108.248.232.250` with `vllm_service` DB + RAG-section + RAG-chunks across `pearlman`, `phl`, `phlDB` |
| Analytics (PostHog / Plausible) | 20 | 9 PostHog + 9 Plausible |

Notable per-host:

- **159.195.79.109**. PostHog with table `distributed_posthog_document_embeddings_text_embedding_3_large_3072`. The table name names the OpenAI model. A parallel table is at 1536d for text-embedding-3-small.
- **108.248.232.250**. vLLM operator with `vllm_service` DB and RAG-section + RAG-chunks tables across three tenant databases. Multi-tenant vLLM-as-a-service.
- **129.153.24.132**. Yoto CMS with `llm_prompts` table. Yoto produces a children's audio device.
- **111.231.19.122**. Five `prompt_info` tables across `domestic`, `domestic_test`, `wisdom`, `wisdom_test`, `yaya_testt`. Chinese AI assistant with prod + test envs visible.

### ClickHouse 22.3.20.29 dominance

1,354 of 2,008 fingerprinted ClickHouse hosts run version 22.3.20.29. That is 67.4%. Yesterday measured 55%. The `clickhouse/clickhouse-server:22.3` LTS Docker tag accounts for the cluster. Insight #27 confirms at scale.

### No ClickHouse extortion

Zero ClickHouse hosts wiped between yesterday and today. The campaign is Elasticsearch-specific. The Meow / Indexrm family targets ES + MongoDB + Redis but not ClickHouse at meaningful scale.

---

## BARE exploit-module ranking on ES 2.9.x

Yesterday's 95 ES 2.9.0 hosts ran through BARE. All 95 top-rank `exploits_multi_elasticsearch_search_groovy_script` (CVE-2014-3120 Groovy RCE). Cosine score 0.58 ± 0.02. BARE's semantic match is deterministic at population scale when the finding's exploit class is unambiguous.

---

## Output

- Probe outputs: `~/recon/elasticsearch-ai-stack-2026-05-17/es-v198-results.json` (17 MB), `~/recon/clickhouse-2026-05-17/ch-v198-results.json` (6 MB)
- BARE output: `/tmp/es29x-bare-output.json` (95 ranked module matches)
- aimap v1.9.8 source: `Nicholas-Kloster/aimap` `f586217`
- VisorLog ingest: 3,666 events into `data/nuclide.db`. 3,597 ES hosts marked `archived` with reason `wiped-by-extortion-campaign`. 69 ES + CH AI-stack confirmations severity-upgraded.

---

## Toolchain provenance

```
JAXEN          [—] not run. Re-used yesterday's empire.db harvest.
aimap v1.9.8   [x] ES + CH fingerprint + enumElasticsearch + enumClickHouse.
aimap-profile  [—] used in 22-ai-stack-attribution follow-up.
VisorGraph     [—] used in 22-ai-stack-attribution follow-up.
VisorBishop    [—] not run. Single-platform follow-up.
VisorSD        [—] not run. ASN sweep already done yesterday.
VisorGoose     [—] not applicable. No .gov in this corpus until cert pivot surfaced ocl.hmis.gov.np.
menlohunt      [—] not applicable. No GCP-hosted hosts.
recongraph     [—] not run.
nu-recon       [—] not run.
VisorPlus      [—] not used.
VisorLog       [x] 3,666 events ingested.
VisorScuba     [x] auto-computed inside aimap (risk_level field).
BARE           [x] 95/95 ES 2.9.x → CVE-2014-3120 Groovy RCE.
VisorCorpus    [—] not applicable.
VisorAgent     [—] ethical-stop. Lab targets only.
VisorRAG       [—] not applicable.
VisorHollow    [—] not applicable. Windows-only.
cortex         [—] not run. Auth context uniform.
JS-bundle      [—] not applicable. JSON APIs.
```

---

## See also

- [`elasticsearch-ai-stack-population-survey-2026-05-16.md`](elasticsearch-ai-stack-population-survey-2026-05-16.md)
- [`clickhouse-population-survey-2026-05-16.md`](clickhouse-population-survey-2026-05-16.md)
- [`22-ai-stack-attribution-2026-05-17.md`](22-ai-stack-attribution-2026-05-17.md)
- [`meow-multi-actor-campaign-scope-2026-05-17.md`](meow-multi-actor-campaign-scope-2026-05-17.md)
- [`../../methodology/insight-28-survey-shelf-life-exposure-to-extortion.md`](../../methodology/insight-28-survey-shelf-life-exposure-to-extortion.md)
- [`../../methodology/insight-29-overwhelming-prior-state-look-at-deltas-not-snapshots.md`](../../methodology/insight-29-overwhelming-prior-state-look-at-deltas-not-snapshots.md)
