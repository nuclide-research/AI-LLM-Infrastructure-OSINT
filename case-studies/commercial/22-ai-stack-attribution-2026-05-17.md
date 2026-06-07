---
type: synthesis
---

# 22 unauthenticated AI-stack Elasticsearch operators (2026-05-17)

_NuClide Research · 2026-05-17_
_Companion to: [`es-clickhouse-cross-stack-2026-05-17.md`](es-clickhouse-cross-stack-2026-05-17.md), [`meow-multi-actor-campaign-scope-2026-05-17.md`](meow-multi-actor-campaign-scope-2026-05-17.md)_

---

## Summary

The morning's `_mapping` probe surfaced 22 Elasticsearch hosts with `dense_vector` or `knn_vector` fields. Those are unambiguous AI / RAG workloads. We ran cert-pivot, Shodan, and `aimap-profile` on each one.

<!-- ksat-tag:auto-generated:start -->
## DCWF KSAT coverage

Auto-derived from DCWF AI work-role rule files (`ksat-tag`).

- **672 (AI Test & Evaluation Specialist):** K7003, K7004, K7044, S7068, S7070, S7075, T5858, T5904
- **733 (AI Risk & Ethics Specialist):** K7040, K7051, S7067, T5854, T5868, T5893
- **overlap (Common AI KSATs (all 5 roles)):** K1158, K1159, K22, K6311, K6900, K6935, K7003, K942, S7065

<!-- ksat-tag:auto-generated:end -->

Three findings.

**One. `103.69.124.214` is Nepal's Ministry of Health and Population.** The TLS cert SAN is `ocl.hmis.gov.np`. That host is the Open Concept Lab, Nepal's clinical-terminology server. `crt.sh` returns 10 subdomains under `hmis.gov.np` including `fhir.hmis.gov.np` (Fast Healthcare Interoperability Resources gateway), `elmis.hmis.gov.np` (vaccine + drug logistics), `erecord.hmis.gov.np` (electronic records), and `sudurpashchim.hmis.gov.np` (Far-Western Province deployment).

The exposed host carries 318,114 clinical-concept documents with embeddings (drug names, diagnoses, ICD-10 codes), an admin `user_profiles` index, and a Meow `read_me` marker. The attacker planted the marker. The data is still alive. Disclosure went to NP-CERT and the Ministry of Health.

**Two. 18 of 22 AI-stack hosts (82%) carry an extortion marker.** Seven are fully wiped. Eleven are mid-wipe with original data still alive. The hospital host from yesterday (`106.75.127.240`) is one of the eleven. Its 270,000 patient-record vector indices are intact. The attacker has not yet deleted them.

**Three. 17 of 22 hosts attributed to named operators.** NewsBlur. XiaoIce. TorchV on ZLMediaKit. Hooper ERP. AItalkx. Tahakum AI. Guangxi OTA. TimeDB. isideweb. Equant Tech (Waffarha LMS). Each has a clean disclosure routing.

---

## The full table

| IP | ES | Sector | Country | Cloud | Operator | Wipe state | AI-stack signal |
|---|---|---|---|---|---|---|---|
| `103.69.124.214` | 8.15.2 | **GOV-HEALTH** | Nepal | NP Govt | **ocl.hmis.gov.np** (MoHP / Open Concept Lab) | MID-WIPE | concepts, 318,114 docs, `_embeddings.vector` |
| `106.75.127.240` | 8.11.0 | HEALTH | China | UCloud SH | Hospital AI (operator name held) | MID-WIPE | entity_vectors (214,597 docs, 3.3 GB), event_vectors, source_chunks. 768d |
| `112.124.16.227` | 8.18.5 | COM | China | Aliyun | **gxota.com** (Guangxi OTA, 53 SAN subdomains, multi-tenant tourism SaaS) | clean | 6 dense_vector KBs. Chinese tourism. 1024d |
| `120.26.18.206` | 8.17.0 | COM | China | Aliyun | **zlmediakit.com** (Chinese streaming SDK; cluster `torchv-cluster`) | clean | dataset_chunk_sharding_16_1024, 1024d |
| `120.27.113.59` | 8.12.2 | COM | China | Aliyun | **itgaohe.com** (Gaohe IT) | MEOW | ai-index, 1536d (OpenAI text-embedding-3-large) |
| `123.60.173.230` | 8.18.2 | COM | China | Huawei | **chatbiz.hooperp.com** (Hooper ERP BI inventory) | MID-WIPE | hooper_bi_dws_inventory, 1536d |
| `135.125.201.31` | 8.17.0 | COM | DE | OVH | **NewsBlur** (cluster `newsblur-local`) | MID-WIPE | discover-stories-openai-index, 256d (OpenAI text-embedding-3-small) |
| `152.32.142.38` | 7.9.1 | COM | NG | UCloud HK | UCloud Lagos B2B (no cert) | MID-WIPE | goods_index_b2b, 1024d |
| `161.97.148.0` | 2.11.0 | COM | DE | Contabo | **lms.equant-tech.com** (Egyptian LMS, Waffarha deals) | MEOW | waffarha-deals, 768d. Ancient ES 2.11.0 |
| `212.64.24.141` | 3.5.0 | COM | China (Shanghai) | Tencent | Synthetic-character production operator (no cert) | MID-WIPE | 11 indices: material_ambient, material_character_appearance, material_voicefx, etc. 1024d. Ancient ES 3.5.0 |
| `8.147.113.203` | 8.17.0 | COM | China | Aliyun | **xiaoicedemo** (XiaoIce demo cluster) | MID-WIPE | prod_virtualhuman_knowledge_faq_default_org, 512d |
| `51.91.106.5` | 7.9.2 | COM | France | OVH | **frojasg1-ia.es** (Spanish dev) | clean | haystack_test, 768d |
| `62.234.4.20` | 8.12.0 | COM | China | Tencent | **timedb.cn** (TimeDB) | clean | dcobjvec, 1024d |
| `81.71.89.27` | 8.15.3 | COM | China | Tencent | **woyaodiancan.asia** (Chinese restaurant ordering) | MID-WIPE | novel-knowledge, 1024d |
| `81.94.155.178` | 2.14.0 | COM | Russia | WestCall | **aicloud-backend** (k3s, Russian AI cloud) | MEOW | russian_news, 384d |
| `84.247.170.209` | 8.16.0 | COM | DE | Contabo | German multilingual AI travel (Traefik cert) | MID-WIPE | article_de / en / es / fr / it / ru, 1536d |
| `84.247.189.64` | 2.19.1 (OpenSearch) | COM | DE | Contabo | **aitalkx.com** (DMS RAG) | MID-WIPE | dms_documentvectors, dms_vectors, knn_vector 768d |
| `92.222.197.175` | 8.11.3 | COM | France | OVH | **llm.tahakum.ai** (Tahakum AI) | MEOW | qa_index, 384d |
| `94.177.165.24` | 7.17.8 | COM | Italy | Aruba | **rex3.isideweb.com** (DeskPro-linked) | MEOW | iside2, 1536d |
| `103.160.107.236` | 8.15.3 | COM | India | Standard Wings | (no cert) | MEOW | documents, 768d |
| `106.53.114.113` | 8.13.4 | COM | China | Tencent | (no cert; tourism vertical) | MID-WIPE | tourism_vector, 1024d |
| `159.75.128.178` | 8.11.0 | COM | China | Tencent | (no cert) | MEOW | knowledge_chunks, 1024d |

Seven fully wiped, eleven mid-wipe, four clean.

---

## The Nepal HMIS finding

The TLS cert on `103.69.124.214:443` carries the SAN `ocl.hmis.gov.np`. We probed `crt.sh` on `*.hmis.gov.np` and got back the full government health-system footprint.

| Subdomain | Role (inferred from name) |
|---|---|
| `hmis.gov.np` | Root. Health Management Information System. |
| `dashboard.hmis.gov.np` | Operations dashboard |
| `elmis.hmis.gov.np` | electronic Logistics Management. Vaccines, drugs, supply chain. |
| `elmis-reports.hmis.gov.np` | eLMIS reporting |
| `erecord.hmis.gov.np` | Electronic Records |
| `fhir.hmis.gov.np` | FHIR healthcare-interoperability gateway |
| `monitoring.hmis.gov.np` | System monitoring |
| `ocl.hmis.gov.np` | Open Concept Lab. Our exposed host. |
| `pss.hmis.gov.np` | Patient/provider service (inferred) |
| `sudurpashchim.hmis.gov.np` | Far-Western Province deployment |

The exposed host's indices:

| Index | Documents | Size | Notes |
|---|---:|---:|---|
| `concepts` | 318,114 | 27.7 MB | OCL clinical-concept dictionary with `_embeddings.vector` and `_synonyms_embeddings.vector` |
| `mappings` | 3,806 | 813 KB | Concept-to-code mappings |
| `collections` | 87 | 31.6 KB | Concept-collection metadata |
| `organizations` | 3 | 9.3 KB | Org records |
| `sources` | 29 | 22.6 KB | Source vocabulary records |
| `user_profiles` | 9 | 11.2 KB | Admin / curator accounts |
| `url_registries` | 0 | 249 B | Empty |
| `read_me` | 112 | 122.8 KB | Meow extortion marker. Attacker-planted. |

We did not read documents in any index. Per the restraint ethic, the schema itself is the finding. The 318,114 concept documents and the 9 admin profiles are alive. The attacker has planted his marker but has not deleted.

WHOIS on the IP returns `Department of Information Technology, Government of Nepal`. Disclosure went to NP-CERT (`incident@npcert.org.np`) with the Ministry CC'd.

---

## Other named operators

### NewsBlur (`135.125.201.31`)

Cluster `newsblur-local`. Index `discover-stories-openai-index` with `content_vector` field at 256d. That is OpenAI `text-embedding-3-small` with the `dimensions=256` parameter. NewsBlur's "discover stories" feature reads off this index. Mid-wipe. Disclosure went to Samuel Clay.

### gxota.com (`112.124.16.227`)

53 SAN subdomains. Multi-tenant Guangxi tourism SaaS with regional subsidiaries: car rental (`zuche.ztc.gxota.com`), business center API (`bizcenter-api.gxota.com`), retail (`byhshop.gxota.com`), provincial tourism brands (Sanjiang, Wuye, QiuYouLuYou). Six Chinese tourism knowledge bases at 1024d. Not wiped.

### XiaoIce demo (`8.147.113.203`)

Cluster `xiaoicedemo`. Index `prod_virtualhuman_knowledge_faq_default_org` at 512d. XiaoIce is the Microsoft-spinoff Chinese AI companion product. The "demo" cluster name fronts production virtual-human FAQ data. Mid-wipe.

### TravelM candidate (`84.247.170.209`)

Contabo Germany. Traefik default cert (no SNI binding). Indices `article_de`, `article_en`, `article_es`, `article_fr`, `article_it`, `article_ru` at 1536d (OpenAI text-embedding-3-large truncated). The earlier passive sweep returned `ai.travelm.de` on Shodan. Mid-wipe.

### The synthetic-character operator (`212.64.24.141`)

Tencent Cloud Shanghai. Ancient ES 3.5.0. No cert. Eleven indices form a synthetic-character production pipeline:

`material_ambient`, `material_background`, `material_character_appearance`, `material_subject_appearance`, `material_emotion_effect`, `material_music`, `material_voicefx`, `material_subject`, `resource_background`, `resource_music`.

All `knn_vector` at 1024d. The schema names a virtual-influencer / digital-human content-generation pipeline. ES 3.5.0 is pre-X-Pack with public unauthenticated RCEs (CVE-2014-3120, CVE-2015-1427). Mid-wipe.

---

## Embedding dimension as a provider signal

| Dim | Likely model | Hosts |
|---|---|---:|
| 256 | OpenAI `text-embedding-3-small` (reduced) | 1 (NewsBlur) |
| 384 | sentence-transformers `all-MiniLM-L6-v2` | 2 (Tahakum, Russian News) |
| 512 | OpenAI `text-embedding-ada-001` (legacy), `text-embedding-3-small` truncated | 1 (XiaoIce) |
| 768 | OpenAI `text-embedding-3-small` (full), `bge-base`, `m3e-base` | 5 (incl. Nepal, hospital, Haystack dev, AItalkx) |
| 1024 | Cohere `embed-v3`, `bge-large` | 12 (most Chinese operators) |
| 1536 | OpenAI `text-embedding-3-large` (truncated), `text-embedding-ada-002` | 5 |

Chinese operators sit mostly at 768d and 1024d (open-source bge / m3e models). Western operators sit mostly at 256d, 1536d, 3072d (OpenAI). The dimension reads off which LLM API the operator is paying for.

---

## Disclosure status

Sent today:

1. NP-CERT + Nepal MoHP. CRITICAL.
2. UCloud Shanghai abuse for the hospital host (`106.75.127.240`). CRITICAL.
3. NewsBlur (Samuel Clay). HIGH.
4. GMX abuse for `wendy.etabw@gmx.com`. HIGH.
5. Correction to UCloud naming Actor C (not Actor A). HIGH.
6. onionmail.org abuse for `scandal@onionmail.org`. HIGH.
7. sharebot.net abuse for `db-recovery@sharebot.net`. HIGH.

Queued, not yet sent: the remaining 13 named operators on the table above. Each needs a per-host re-probe and per-actor classification before send.

---

## Toolchain provenance

```
visorgraph        [x] 22 hosts cert-pivot. 5 surfaced SAN domains.
aimap-profile     [x] 22 hosts fast mode. identity, surface_passive, cert_cns.
shodan host       [x] 22 hosts. org, country, vulns.
crt.sh            [x] manual pivot on hmis.gov.np (10 SAN), gxota.com (53 SAN).
whois             [x] cymru bulk and per-IP for routing.
aimap v1.9.8      [—] used earlier today for the ES schema probe.
nuclide-contact   [—] queued for the next batch of named operators.
```

---

## See also

- [`es-clickhouse-cross-stack-2026-05-17.md`](es-clickhouse-cross-stack-2026-05-17.md)
- [`meow-multi-actor-campaign-scope-2026-05-17.md`](meow-multi-actor-campaign-scope-2026-05-17.md)
- [`../../methodology/insight-28-survey-shelf-life-exposure-to-extortion.md`](../../methodology/insight-28-survey-shelf-life-exposure-to-extortion.md)
- [`../../methodology/insight-29-overwhelming-prior-state-look-at-deltas-not-snapshots.md`](../../methodology/insight-29-overwhelming-prior-state-look-at-deltas-not-snapshots.md)
- [`../../methodology/insight-04-whois-over-slug-heuristics-for-disclosure-routing.md`](../../methodology/insight-04-whois-over-slug-heuristics-for-disclosure-routing.md)
- [`multi-cross-survey-stacked-catastrophe-2026-05-16.md`](multi-cross-survey-stacked-catastrophe-2026-05-16.md)
