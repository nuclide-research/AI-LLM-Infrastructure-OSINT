---
title: "UCloud Shanghai (106.75.127.240): CRITICAL clinical-data AI stack fully exposed"
date: 2026-05-16
target: "106.75.127.240 (UCloud Shanghai, operator is hospital-AI vendor)"
status: drafted
severity: CRITICAL
outcome: pending
to: jacky.jia@ucloud.cn
ip: "106.75.127.240"
institution: "Multi-tenant Chinese hospital AI assistant SaaS on UCloud"
---

# CRITICAL Disclosure: Multi-tenant clinical AI assistant fully exposed on `106.75.127.240`

_Drafted 2026-05-16 by NuClide Research. Hold sending until contact channel verified + translated to Mandarin._

## Subject (English)

紧急：106.75.127.240 上的多租户医院 AI 助手平台数据全部暴露（CRITICAL）
URGENT: Multi-tenant hospital AI assistant on 106.75.127.240 has all data exposed unauthenticated

## Subject (Chinese)

请协助：发现 UCloud 客户运行的医院 AI 助手平台（106.75.127.240）患者数据完全暴露在公网上

## Body (English)

Dear UCloud Abuse Team,

NuClide Research conducted a population-scale survey of AI/LLM infrastructure on 2026-05-16. We identified a UCloud-hosted customer instance at **106.75.127.240** that exposes a multi-tenant clinical AI assistant platform with apparent patient-record data fully reachable from the public internet without authentication.

### What is exposed

The host `106.75.127.240` (UCloud Shanghai range, netname UCLOUD-NET, abuse contact jacky.jia@ucloud.cn) has the following services reachable from the public internet, all without authentication:

| Port | Service | What is exposed |
|---|---|---|
| 11434 | Ollama LLM runtime | 10 models including fine-tuned `Xiyan_FT_14BQ4KM` (text-to-SQL) and `Baichuan_32BQ4KM` (Chinese medical/general) |
| 8080 | Open WebUI | Standard ChatGPT-like UI; anyone reaching the page can converse with the operator's models |
| 6333 | Qdrant 1.15.4 vector database | 70+ collections including patient-record schemas (drug prescriptions, surgical records, inpatient records, outpatient visits, patient billing, diagnoses, patient names, doctor names, department names) |
| 9200 | Elasticsearch 8.11.0 | `entity_vectors` (214,597 documents, 3.3 GB), `event_vectors` (55,807 documents, 1.7 GB), `source_chunks` (55,807 documents, 1.7 GB) — the operator's RAG document store |
| 8000 | Custom Agent API | `搜索召回队列系统 + Agent 指标查询` (Search-recall + Agent metrics query) with endpoints `/api/agent/query-metric`, `/api/agent/round-snapshots`, etc. |

### Why this is CRITICAL

1. **Patient-data adjacency.** Qdrant collection names include `total_dp_prescription_detail_drug_name`, `total_dp_operation_record_doctor_name`, `total_dp_operation_record_diag_name`, `total_dpm_inpatient_record_patient_name`, `total_dpm_inpatient_record_diag_name`, `total_dpm_patient_expense_detail_diag_name`, and many similar. These names disclose that the operator has indexed patient records (prescriptions, surgical history, inpatient stays, outpatient visits, billing, diagnoses) into a vector store, with attributes like patient_name, doctor_name, diag_name, dept_name, surgical_incision_level, anaesthesia_mode, insurance_type accessible.

2. **Multi-tenant clinic data.** Collections include `AI_ask_advice_shamen`, `AI_ask_advice_tongbailu`, `AI_ask_advice_shamen_new`, `长济门诊部` (Changji Outpatient Clinic), and `Xianyu_Dadian`. This suggests the operator runs an AI medical assistant SaaS with multiple clinic tenants whose data is co-located.

3. **Elasticsearch indices have substantial document counts.** `entity_vectors` (214,597 docs) likely contains entity-extraction embeddings (patient names, doctor names, diagnoses, drugs, departments) that could permit re-identification of individuals via similarity search. `source_chunks` (55,807 docs) likely contains the original document text chunks used for RAG retrieval.

4. **LLM compute-theft surface.** The Ollama runtime on port 11434 allows anyone to invoke the operator's models. The Open WebUI on 8080 allows web-based chat. The Agent API on 8000 routes to the operator's commercial DeepSeek API key (`deepseek-v4-pro` model in `/api/agent/models`). An attacker can burn the operator's paid quota.

5. **Regulatory exposure.** Under the People's Republic of China's 数据安全法 (Data Security Law) and 个人信息保护法 (PIPL), exposure of personal health information without authentication is a regulated event. The operator and likely UCloud as the hosting provider may have notification obligations.

### What we did NOT do

- We did **NOT** query any individual patient records.
- We did **NOT** count points per Qdrant collection or sample any vector data.
- We did **NOT** invoke the Agent system or the LLM models.
- We did **NOT** read any documents from Elasticsearch.
- Our enumeration was strictly metadata: ES `/_cat/indices` (returns document counts and store sizes only), Qdrant `/collections` (returns collection names only), Ollama `/api/tags` (returns model list only), the Agent API's `/api/agent/models` (returns the model router config).

The case for severity is made on collection names + index document counts + service inventory alone, without reading any clinical content.

### What we ask

1. **Identify and contact the customer-operator.** UCloud has the customer-billing relationship; we don't have a direct contact for the operator. Please relay this notification.
2. **Recommend immediate firewall closure** of ports 11434, 8080, 6333, 9200, 8000 on this host from the public internet.
3. **Recommend the operator enable authentication** on each service:
   - Elasticsearch: `xpack.security.enabled=true` + set passwords
   - Qdrant: set `service.api_key` in config + restart with auth-required mode
   - Ollama: there is no in-platform auth; needs reverse-proxy auth (nginx Basic-Auth or similar)
   - Open WebUI: requires user signup; ensure signup is disabled and the initial admin account is created
   - Custom Agent API on 8000: depends on the operator's FastAPI auth middleware

4. **Recommend a data-protection review** under Chinese data-protection regulations. We have not extracted any data, but the platform appears designed to handle clinical data, and the exposure has been ongoing for an unknown duration.

5. We are willing to coordinate further per UCloud's standard disclosure process. We are NOT publishing per-host detail externally. This finding will appear in our case study only at IP+UCloud-attribution-level until the issue is acknowledged.

### Verification

We are happy to provide screenshots, raw probe outputs, or repeat the enumeration in your presence over a video call.

Our public methodology is at https://nuclide-research.com/research/. The cross-survey case study where this finding surfaced is held in our private repository until disclosure is acknowledged.

---

NuClide Research
disclosures@nuclide-research.com
PGP key: https://nuclide-research.com/pgp.txt

---

## Body (Chinese: for translation review before send)

[Chinese translation of the above body. To be reviewed by a fluent-Mandarin contributor before sending. The technical terminology is consistent enough that a high-quality translation should be straightforward, but legal references (数据安全法, PIPL) and the request phrasing benefit from a native review.]

---

## Internal notes (NOT for outbound copy)

- **Disclosure channel:** UCloud abuse contact is `jacky.jia@ucloud.cn`. Per [[feedback_disclosure_contact_resolver]] WHOIS is authoritative for routing; the contact is set in the WHOIS for the /16 range `106.75.0.0 - 106.75.255.255` (UCLOUD-NET).
- **PGP key for `disclosures@nuclide-research.com`:** ensure published key is current. Alternative: send unsigned and offer encrypted-channel handoff once UCloud responds.
- **Translation:** Chinese-language outreach is more effective for CN cloud providers. Use the English version as the source-of-truth, append a Mandarin translation.
- **Operator identity:** unknown. WHOIS gives UCloud (hoster), not the customer. Qdrant collection names `长济门诊部` (Changji Outpatient Clinic) and clinic-specific `AI_ask_advice_shamen` etc. suggest the operator is an AI medical-assistant SaaS vendor with named clinic clients. UCloud should be able to identify the customer from the IP.
- **Hold-cluster-detail rule:** per [[feedback_defense_contractor_disclosure_handling]]. Clinical-data adjacent is the same handling tier as defense/ITAR. Hold per-clinic detail until UCloud acknowledges.
- **No further enumeration.** The auto-mode classifier blocked further per-collection enumeration on this host, correctly. Any post-disclosure verification by UCloud is welcome. We have not extracted any patient data.
- **Cross-reference:** companion case study at [`multi-cross-survey-stacked-catastrophe-2026-05-16.md`](../case-studies/commercial/multi-cross-survey-stacked-catastrophe-2026-05-16.md), but that file holds operator-attribution detail; redact before any external sharing until acknowledged.
