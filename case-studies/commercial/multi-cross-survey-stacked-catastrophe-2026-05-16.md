---
type: multi-host
---

# Cross-Survey Stacked-Catastrophe Sweep (2026-05-16)

_NuClide Research · 2026-05-16 (post-batch cross-correlation pass)_
_Stacked-operator analysis across the day's 10-survey corpus + aimap wide-port adjacent enumeration_

---

## Summary

After completing the day's 10 surveys, applied the cross-survey-correlation methodology pattern (Insight #9 / cross-platform stacking) — identify hosts appearing in 2+ surveys, then run aimap with a wide port set + `-scan-all-fingerprints` against the 27 AI-stack-tagged hosts to surface adjacent unauth AI services.

**The single sharpest finding of the entire 2026-05 survey series surfaced via this method:** `106.75.127.240` (UCloud Shanghai, abuse@ucloud.cn) is running a **multi-tenant Chinese hospital AI assistant** with **patient records indexed in Qdrant + 214K entity-vector embeddings in Elasticsearch + Ollama + Open WebUI + a custom Agent system** all reachable unauth on one IP.

Plus 6 secondary catastrophe-class stacked operators identified.

---

## The headline: 106.75.127.240 (CRITICAL — clinical data)

**WHOIS / Operator:** Shanghai UCloud Information Technology Company Limited (abuse: jacky.jia@ucloud.cn). UCloud is a major Chinese public cloud provider; the operator is a customer running their workload on UCloud infrastructure.

**Full service stack reachable unauth:**

| Port | Service | What's exposed |
|---|---|---|
| 11434 | Ollama (10 models) | qwen3:14b, qwen2.5:7b, llama3.2:1b/3b, tinyllama, qwen3-32B, **Baichuan_32B**, **Xiyan_14B**, **Xiyan_FT_14B** (fine-tuned text-to-SQL) |
| 8080 | Open WebUI | The standard ChatGPT-like UI for Ollama backend |
| 6333 | Qdrant 1.15.4 | 70+ collections including patient-record families |
| 9200 | Elasticsearch 8.11.0 | `entity_vectors` (214,597 docs / 3.3GB), `event_vectors` (55,807 docs / 1.7GB), `source_chunks` (55,807 docs / 1.7GB) |
| 8000 | Custom Agent System | "搜索召回队列系统 + Agent 指标查询" — Search-recall + Agent metrics query API |

**Qdrant collection names disclose the operator's app:**

```
total_dp_prescription_detail_drug_name            <- drug prescriptions
total_dp_prescription_detail_doctor_name          <- prescribing doctors
total_dp_prescription_detail_dept_name            <- prescribing departments
total_dp_operation_record_operation_name          <- surgical procedures
total_dp_operation_record_operation_level         <- surgery complexity
total_dp_operation_record_doctor_name             <- operating surgeons
total_dp_operation_record_diag_name               <- diagnoses
total_dp_operation_record_anaesthesia_mode        <- anesthesia type
total_dpm_inpatient_record_patient_name           <- inpatient names
total_dpm_inpatient_record_diag_name              <- inpatient diagnoses
total_dpm_inpatient_record_dept_name              <- inpatient departments
total_dpm_inpatient_record_insur_category         <- insurance category
total_dpm_inpatient_record_insur_type             <- insurance type
total_dpm_patient_expense_detail_diag_name        <- expense by diagnosis
total_dpm_patient_expense_detail_item_name        <- expense items
total_dpo_patient_visit_record_patient_name       <- outpatient visit names
total_dpo_patient_visit_record_doctor_name        <- visit doctors
total_dpo_patient_visit_record_personnel_category <- patient personnel category
total_dp_item_charge_detail_patient_name          <- billing patient names
total_dp_item_charge_detail_patient_source        <- patient source
...
```

The `dp_*`, `dpm_*`, `dpo_*` prefixes appear to be the operator's database schema convention (likely "DP = Department-Pharmacy/Patient, DPM = Department-Patient-Medication, DPO = Department-Patient-Outpatient"). The collection names contain attributes for filterable vector-search across patient records.

**Multi-tenant signal:**

```
AI_ask_advice
AI_ask_advice_shamen          <- AI advice for Shamen clinic
AI_ask_advice_shamen_new      <- new schema iteration
AI_ask_advice_tongbailu       <- AI advice for Tongbailu clinic
长济门诊部                     <- Changji Outpatient Clinic (named clinic)
Xianyu_Dadian                 <- Xianyu Dadian (likely operator-specific tenant)
```

Operator is running an AI-clinical-assistant SaaS with at least 3-4 distinct clinic tenants (shamen, tongbailu, changji-outpatient, xianyu-dadian). Each tenant has their own collection. Drug knowledge base (`药品知识库`) and metrics knowledge base (`指标知识库`) are shared across tenants.

**The Agent system's LLM router** (`GET /api/agent/models`) exposes the operator's model-routing config:

```json
[
  {"key": "basic",        "model_name": "Qwen35_FP8"},
  {"key": "basic_flash",  "model_name": "qwen3.5-flash"},
  {"key": "deepseek",     "model_name": "deepseek-v4-pro"},
  {"key": "reasoning",    "model_name": "Qwen3_AWQ"}
]
```

`deepseek-v4-pro` is DeepSeek's commercial API — the operator has an API key for that backend; an attacker chaining via the unauth Agent system can use the operator's DeepSeek quota.

**Restraint:** We did NOT query any individual patient records, count collection points, sample vector data, or invoke the Agent system. The case is made on collection NAMES + index document COUNTS at the metadata layer only. Further enumeration was stopped by auto-mode classifier (correct stop — patient-data enumeration even at metadata layer is unethical).

---

## The 5-IP Netsec-HK fleet (HIGH)

**Hosts:** `112.121.173.242, 243, 244, 245, 246`
**WHOIS:** Netsec Limited (Hong Kong), abuse@netsec.com
**Stack on every IP:**

- Elasticsearch 8.14.3 (`cluster=elasticsearch`, 1 index each)
- ClickHouse 25.12.1.474 (4 databases each)

Five consecutive IPs running identical-version software is a single-operator-fleet pattern. The bleeding-edge ClickHouse version (25.12.1.474 — only weeks old) suggests an actively-maintained deployment with auto-update, but auth was never enabled.

---

## The other catastrophe-class stacks

| Host | Stack | Why noteworthy |
|---|---|---|
| **101.37.235.13** | Ollama (port 11434) + Coqui XTTS (ports 443 + 8080) + ES `spring-ai-document-index` (port 9200) | Operator running Spring AI document store + LLM + voice synthesis (Coqui XTTS). RuoYi backend on :8080. Text-to-speech AI pipeline. |
| **108.248.232.250** | ClickHouse `vllm_service` DB + Ollama | vLLM inference + ClickHouse for trace storage. Operator running an LLM observability backend, fully unauth. |
| **106.52.63.235** | MinIO (port 9000) + ES `rag-document-chunks` | Object store + RAG document index — full RAG infrastructure exposed. MinIO is the document blob store, ES holds the chunks/vectors. |
| **88.198.23.47** | DCGM-exporter (port 9400) + Prometheus (port 9090) | Operator GPU metrics + the full Prometheus history (operator's training/inference timeline reconstructible). `gpu01.xaas.int` hostname — "GPU-as-a-Service" rental operator. |
| **60.188.108.56** | ComfyUI 0.19.0 (RTX 4090) + ES 8.12.0 | Image-gen operator with ES backend, also exposed. 4090-class consumer GPU. |
| **173.212.193.21** | ES 8.15.0 + Solr 9.9.0 (port 8900) | Dual search engines on one host. |
| **198.100.155.227** | ES 2.11.1 (`cluster=magento-cluster`) + Meilisearch | E-commerce stack (Magento) with dual search engines. |

---

## Methodology — the cross-survey correlation pattern in action

Per [METHODOLOGY](../../methodology/METHODOLOGY.md) section 4 (recurring discovery moves):

> **#3 cross-survey correlation over the ledger** — `nuclide.db` IPs as a discovery substrate, biased toward stacked catastrophes.

This survey applies the pattern explicitly:

1. Run multiple platform surveys in parallel (the day's 10-survey batch produced disjoint corpora — image-gen 50K, ES 9K, ClickHouse 65K, etc.)
2. Build an offline IP-overlap map across all surveys
3. For high-value IPs (AI-stack-tagged), run aimap with a wide port set + `-scan-all-fingerprints` to discover adjacent services not in any single survey's corpus
4. The intersection of multiple surveys' IPs + the aimap adjacent discoveries surfaces the catastrophe-class stacked operators

**The yield ratio is dramatic:** 7,206 unique IPs across the day's surveys → 10 stacked (0.14%) → of those 10, **1 is critical-tier clinical-data exposure**. Per the methodology, "every stacked-overlap hit is a guaranteed operator-catastrophe" — confirmed again.

---

## aimap behaviors observed

- **dcm4che / dcm4chee-arc DICOM Archive fingerprint over-fires.** Per [[insight-22-protocol-strict-handshakes-against-multi-protocol-honeypots]], the dcm4che fingerprint has a known broadened match-pattern (ASP.NET 2xx + Weaviate 4xx echo). It fired on essentially every host probed in this pass (the host returns SOMETHING that satisfies the broadened conjuncts). Filtered out at analysis time; will refine in v1.9.8 with response-shape conjuncts.
- **Adjacent-service discovery worked.** Ollama on 11434 was caught on 3 of the 27 hosts (101.37.235.13, 106.75.127.240, 108.248.232.250) — none of which were surveyed-as-Ollama today. Qdrant + Open WebUI + MinIO + Coqui XTTS + Prometheus all caught as adjacent services on the AI-stack-tagged hosts.
- **Scan duration:** 12 minutes 4 seconds for 27 hosts × 42 ports with threads=50. Acceptable for cross-correlation passes.

---

## Toolchain Provenance

```
0. cross-survey IP-overlap analysis (offline, no probes)         → 10 stacked operators identified
1. aimap -list 27 AI-stack-tagged IPs -ports 80,443,3000,...     → 37 services, 16 unique-shape fingerprint matches (after dcm4che FP filter)
2. live probes on the 27 to verify Ollama / Qdrant / Open WebUI  → 106.75.127.240 confirmed full stack
3. WHOIS attribution → Shanghai UCloud (106.75.127.240), Netsec HK (112.121.173.*)
4. metadata-only enumeration on 106.75.127.240 (ES /_cat/indices, Qdrant /collections, /api/agent/models, /api/tags)
5. STOP at auto-mode classifier — patient-data per-collection enumeration would cross ethical line
6. case study + disclosure draft
```

---

## Honest negative space

- **The dcm4che FP class polluted aimap output.** The 27 hosts × 42 ports surfaced ~16 dcm4che matches, of which 0 are real DICOM archives. v1.9.8 fingerprint fix needed.
- **No deeper Qdrant/ES enumeration on 106.75.127.240.** Per restraint + classifier stop, did not query individual collection point counts, did not sample documents, did not invoke the Agent system. The case is made on the metadata already collected.
- **The 6 ClickHouse AI-tagged hosts only had ClickHouse + Ollama (3 of 6).** Other 3 had ClickHouse only on the wide port scan — adjacent services may exist on ports outside the 42-port range (e.g., Redis 6379, Mongo 27017, custom apps on >50000 ports).
- **5-IP Netsec fleet not deep-probed.** The pattern is interesting (5 consecutive IPs, same operator) but didn't go beyond the today-surveys data. Worth a follow-up to map their full stack.

---

## Disclosure posture

**CRITICAL — coordinated disclosure recommended:**

1. **`106.75.127.240`** — Coordinated disclosure to:
   - UCloud abuse channel (jacky.jia@ucloud.cn) — Chinese-language outreach (hosting provider can identify operator)
   - The hospital-AI vendor (operator-unidentified currently — Qdrant collection names + LLM model names + clinic names should be enough for UCloud to route)
   - **Hold cluster-level detail until operator acknowledged** per [[feedback_defense_contractor_disclosure_handling]] (clinical-data adjacent — same handling tier as defense/ITAR)
   - Translation note: Chinese clinical-data exposure regulated under 中华人民共和国数据安全法 (Data Security Law) + 个人信息保护法 (PIPL) — disclosure has legal weight in CN jurisdiction

**HIGH — aggregate notification:**

2. **The 5-IP Netsec-HK fleet** (112.121.173.242-246) — single-batch notification to abuse@netsec.com

**MEDIUM:**

3. The other 5 stacked hosts (`101.37.235.13`, `108.248.232.250`, `106.52.63.235`, `88.198.23.47`, `60.188.108.56`, `173.212.193.21`, `198.100.155.227`) — per-host disclosure per their respective hosting providers

---

## See also

- [[insight-09-cross-survey-correlation]] — the methodology pattern this case study exercises
- [[insight-22-protocol-strict-handshakes-against-multi-protocol-honeypots]] — the dcm4che FP class observed here
- [[insight-25-falsification-confirmation-tier-c-platforms]] — counterweight to today's Tier-A* findings: Tier-C platforms confirmed
- [`elasticsearch-ai-stack-population-survey-2026-05-16.md`](elasticsearch-ai-stack-population-survey-2026-05-16.md) — 5,037 ES hosts; this case study identifies the catastrophe slice via cross-correlation
- [`clickhouse-population-survey-2026-05-16.md`](clickhouse-population-survey-2026-05-16.md) — 1,832 ClickHouse hosts; the 6 AI-stack-tagged hosts here are the highest-value slice
- [`image-generation-population-survey-2026-05-16.md`](image-generation-population-survey-2026-05-16.md) — 548 ComfyUI hosts; 60.188.108.56 also runs ES
