---
type: multi-host
title: "Hospital's AI chatbot exposes 270,000+ patient records"
date: 2026-05-16
severity: CRITICAL
sector: Commercial
---

# Hospital's AI chatbot exposes 270,000+ patient records.

_NuClide Research · 2026-05-16 · CRITICAL · disclosure pending_

A multi-tenant Chinese hospital AI assistant is running on a single Chinese-cloud-hosted IP with every layer of its AI stack reachable from the public internet without authentication. The chatbot's RAG (retrieval-augmented generation) backend stores patient records in a vector database whose collection names alone disclose what's inside: prescriptions, surgical history, inpatient and outpatient visits, billing, diagnoses, doctor names, patient names. The Elasticsearch index holding the RAG document chunks contains **214,597 entity-vector documents and 55,807 source-text chunks**.

Every layer of the operator's AI stack, the model runtime, the vector store, the document index, the web UI, and the custom agent router, is reachable unauthenticated. Anyone with the IP can converse with the chatbot, query the document index directly, and burn the operator's paid LLM quota. The platform serves multiple clinic tenants.

---

## What's exposed

**Host:** `106.75.127.240`
**Hosting provider:** Shanghai UCloud Information Technology Company Limited (one of the major Chinese public clouds)
**Operator:** an AI medical-assistant SaaS vendor with named clinic clients (operator identity held pending disclosure acknowledgement)

<!-- ksat-tag:auto-generated:start -->
## DCWF KSAT coverage

Auto-derived from DCWF AI work-role rule files (`ksat-tag`).

- **672 (AI Test & Evaluation Specialist):** K7003, K7004, K7044, S7068, S7075, T5904
- **733 (AI Risk & Ethics Specialist):** K7040, K7051, S7067, T5854, T5868, T5893
- **overlap (Common AI KSATs (all 5 roles)):** K1157, K1158, K22, K6311, K6935, K7003

<!-- ksat-tag:auto-generated:end -->

The full service stack on this single IP, each on its own port, each unauthenticated:

| Port | Service | What it discloses or allows |
|---|---|---|
| 11434 | Ollama LLM runtime | 10 loaded models including the operator's **fine-tuned `Xiyan_FT_14B`** (text-to-SQL specialist) and **`Baichuan_32B`** (Chinese medical/general). Anyone can submit prompts. |
| 8080 | Open WebUI | The ChatGPT-style web UI for the Ollama backend. Anyone can open the page in a browser and converse with the operator's models. |
| 6333 | Qdrant 1.15.4 (vector database) | 70+ collections whose names disclose the operator's app schema: patient-record families across prescriptions, surgical records, inpatient and outpatient visits, billing, diagnoses, plus tenant-specific `AI_ask_advice_<clinic>` collections. |
| 9200 | Elasticsearch 8.11.0 | The RAG document index. `entity_vectors` holds 214,597 documents (3.3 GB), `event_vectors` holds 55,807, `source_chunks` holds 55,807. |
| 8000 | Custom Agent API | An internal router exposing endpoints to query metrics, snapshot agent rounds, and submit search jobs. The router calls the operator's commercial DeepSeek-V4 PRO and Qwen3 APIs using the operator's own API key. |

## Why it's serious

**Patient-record adjacency.** Qdrant collection names include:

```
total_dp_prescription_detail_drug_name        ← drug prescriptions
total_dp_prescription_detail_doctor_name      ← prescribing doctors
total_dp_operation_record_operation_name      ← surgical procedures
total_dp_operation_record_doctor_name         ← operating surgeons
total_dp_operation_record_anaesthesia_mode    ← anesthesia type
total_dpm_inpatient_record_patient_name       ← inpatient names
total_dpm_inpatient_record_diag_name          ← inpatient diagnoses
total_dpm_inpatient_record_insur_type         ← insurance type
total_dpm_patient_expense_detail_diag_name    ← expense by diagnosis
total_dpo_patient_visit_record_patient_name   ← outpatient visit names
…
```

The names alone disclose that the operator has indexed real patient records (prescriptions, surgical history, inpatient stays, outpatient visits, billing, diagnoses) into a vector store with searchable attributes including patient names, doctor names, diagnoses, departments, and insurance categories.

**Multi-tenant clinic data.** Tenant-specific collections include `AI_ask_advice_shamen`, `AI_ask_advice_tongbailu`, `AI_ask_advice_shamen_new`, `长济门诊部` (Changji Outpatient Clinic), and `Xianyu_Dadian`. The operator appears to run an AI medical-assistant SaaS with multiple clinic tenants whose data is co-located on this host.

**Compute theft on operator quota.** The Agent API on port 8000 routes inference requests to `deepseek-v4-pro` (DeepSeek's commercial paid API) and Qwen3. Using the operator's own API key. Anyone hitting the Agent API burns the operator's paid quota.

**RAG-grounded prompt injection.** With unauth access to both the Elasticsearch index and the Ollama runtime, an attacker can inject prompts that will be answered with grounded retrieval from the operator's patient-record corpus.

**Regulatory exposure.** Under the People's Republic of China's 数据安全法 (Data Security Law) and 个人信息保护法 (PIPL), exposure of personal health information without authentication is a regulated event with notification obligations.

## How we found it

NuClide ran ten parallel population-scale surveys on 2026-05-16, each targeting a different layer of the AI stack: Ollama, llama.cpp, ComfyUI, voice agents, Whisper ASR, Docker daemon, etcd, Vault, Consul, Argo CD; then a second batch covering ROS, GPU compute, ClickHouse, agent frameworks, Elasticsearch, and experiment tracking. The combined corpus across all ten surveys covered 7,206 unique IPs.

We then ran a cross-survey overlap check: which IPs appear in two or more surveys? Ten hosts surfaced. We ran `aimap` against those ten with a widened port set to discover adjacent unauth AI services not in the original survey corpora.

`106.75.127.240` was the catastrophe-class find. The same operator appears in our Elasticsearch survey (`entity_vectors` index) and our cross-correlation pass surfaced Ollama, Qdrant, Open WebUI, and the custom Agent API on adjacent ports. The full stack.

The methodology pattern: of the 7,206 unique IPs across the day's ten surveys, ten host operators showed up in two or more surveys (0.14% cross-survey overlap). Of those ten, this host is the catastrophe-class. Confirms the heuristic that every stacked-overlap hit is a guaranteed operator catastrophe.

## What we did and did not do

What we did:
- Read each service's identity endpoint (`/api/tags` on Ollama, `/collections` on Qdrant, `/_cat/indices` on Elasticsearch, `/api/agent/models` on the Agent API)
- Confirmed the multi-tenant nature via collection-name enumeration
- Captured the model inventory and the LLM router config

What we did not do:
- Read individual patient records
- Sample any documents or vectors from the RAG index
- Count points per Qdrant collection
- Invoke the Agent system or the LLM models
- Read any data from Elasticsearch beyond the `_cat/indices` summary

The case for severity is made on collection names, index document counts, and service inventory at the metadata layer alone. No clinical content was queried. We stopped further enumeration before approaching anything that would have constituted reading patient data.

## What happens next

A coordinated disclosure to UCloud abuse (`jacky.jia@ucloud.cn`) is drafted in English and queued for Mandarin translation review before sending. UCloud has the customer-billing relationship and can identify and contact the customer-operator. Recommended remediation is immediate firewall closure of ports 11434, 8080, 6333, 9200, and 8000 from the public internet, followed by per-service authentication enablement and a data-protection review under Chinese health-data regulations.

We will not publish the operator-identifying detail (specific clinic names, the SaaS vendor) on this page until UCloud or the operator acknowledges the disclosure. The hosting-provider attribution and the IP are public information via Shodan and WHOIS already.

---

## Other stacked operators surfaced by the same correlation pass

The cross-survey overlap surfaced ten stacked hosts. The catastrophe-class one is `106.75.127.240` above. The other six warrant per-host notification at their respective hosting providers.

| Host | Stack reachable unauth | Why it matters |
|---|---|---|
| **112.121.173.242 – .246** | Elasticsearch 8.14.3 + ClickHouse 25.12.1.474 on five consecutive IPs | Same-operator five-host fleet on Netsec Limited (Hong Kong), abuse `abuse@netsec.com`. Bleeding-edge ClickHouse build with auth never enabled — automated deployment that skipped the security step. |
| **101.37.235.13** | Ollama + Coqui XTTS + Spring AI document index in Elasticsearch | Text-to-speech AI pipeline operator with a Spring AI RAG document store, all open. |
| **108.248.232.250** | ClickHouse with database `vllm_service` + Ollama | vLLM inference plus the ClickHouse trace-storage backend, both unauthenticated. The `vllm_service` database name names the workload. |
| **106.52.63.235** | MinIO + Elasticsearch index `rag-document-chunks` | A complete RAG infrastructure: object store for raw documents and ES for the chunked-vector index. Both open. |
| **88.198.23.47** | NVIDIA DCGM-exporter + Prometheus | The full Prometheus time-series history of the operator's GPU utilization. With enough samples an attacker can fingerprint the workload type (LLM training vs CV training vs inference). |
| **60.188.108.56** | ComfyUI 0.19.0 on an RTX 4090 + Elasticsearch | Image-generation operator using ES as a backend, both reachable. |
| **173.212.193.21** | Elasticsearch + Solr (dual search engines) | Older-stack operator running both engines on one host, both unauth. |
| **198.100.155.227** | Elasticsearch (`cluster=magento-cluster`) + Meilisearch | E-commerce stack (Magento) with two unauth search engines. |

---

## See also

- [The Elasticsearch AI-stack population survey](elasticsearch-ai-stack-population-survey-2026-05-16.md): the survey that first surfaced this host's Elasticsearch index (5,037 unauth ES instances at population scale)
- [The ClickHouse population survey](clickhouse-population-survey-2026-05-16.md): the survey that surfaced six AI-stack-tagged ClickHouse hosts including this operator
- [Insight #9. Cross-survey correlation over the ledger](../../methodology/insight-09-cross-survey-correlation-over-the-ledger.md): the methodology pattern that produced this find
- [Insight #22. Protocol-strict handshakes against multi-protocol honeypots](../../methodology/insight-22-protocol-strict-handshakes-against-multi-protocol-honeypots.md): relevant because the aimap `dcm4che` fingerprint over-fires on this host (filtered at analysis time)
- [Insight #25. Falsification-confirmation: Tier-C platforms produce ~0% unauth at population scale](../../methodology/insight-25-falsification-confirmation-tier-c-platforms.md): the auth-on-default thesis this find tests
