---
type: synthesis
---

# Vector database population survey, 2026-05-17

_NuClide Research, 2026-05-17 (overnight pass)_
_Survey #22 in the AI infrastructure series._

---

## Summary

We surveyed the public vector-database population: Qdrant, Weaviate, Milvus, ChromaDB. Vector DBs hold the embeddings for an operator's RAG pipeline — every document, customer transcript, support ticket, legal record, or PII row the operator has chunked and indexed for retrieval. The Meow / Indexrm extortion campaign hits Elasticsearch only, so unlike yesterday's ES population the vector-DB population is *not* wipe-contaminated. Operator data is alive.

From 917 candidate IPs harvested via protocol-strict Shodan dorks, aimap confirmed:

| Service | Unique IPs (unauth) |
|---|---:|
| Weaviate | 127 |
| Milvus | 59 |
| ChromaDB | 39 |
| Qdrant | 38 |

The Qdrant cohort is the most readable (the API exposes collection names + point counts at `/collections`). The Weaviate cohort is the most metadata-rich (the schema includes self-declared `pii_fields` markers). What follows is the headline-impact subset, schema-only enumeration, no document reads performed.

---

## Largest exposures by point count (Qdrant)

| IP | Hostname | Country | Total points | Notes |
|---|---|---|---:|---|
| `89.108.123.166` | `advocat-online.ru` | RU | **214,406,754** | 18 Russian legal collections (see below) |
| `35.154.114.115` | `vector.jezt.cloud` | IN | 10,782,632 | 264 collections, multi-tenant SaaS RAG |
| `204.10.144.25` | `bolt.kaychalabs.com` | US | 4,249,933 | Internal enterprise "jarvis_*" knowledge stack |
| `103.247.10.156` | `aishelter.underdog.my.id` | ID | 753,959 | HR system: payroll + employee detail |
| `20.127.155.10` | `eclipseassistance.eastus.cloudapp.azure.com` | US (Azure) | 659,116 | Eclipse/Prophet-21 ERP test cases |
| `148.113.212.12` | `fridayai.online` | CA (OVH) | 620,711 | 121 customer workspaces |

---

## advocat-online.ru — 214 million vector points

The single host at `89.108.123.166` (Reg.Ru hosting in Russia, TLS SAN `advocat-online.ru`) is the largest exposed vector store we have ever surveyed. The 18 collections describe a comprehensive Russian legal AI knowledge base:

| Collection | Points |
|---|---:|
| `regional_zakon` (regional law) | 104,297,989 |
| `law` | 32,446,259 |
| `law_zakonod_1_hybrid` | 24,508,936 |
| `arbitrazh_sud` (arbitration court) | 9,975,000 |
| `law_zakonod_2_hybrid` | 8,577,657 |
| `soi` (likely Сведения о Юридических Лицах — Legal Entity Records) | 8,454,000 |
| `comment_law` | 6,498,713 |
| `law_no_zakonod_hybrid` | 5,884,352 |
| `fin_kadr_consult` (financial/HR consulting) | 4,724,509 |
| `vushie_sud` (higher courts) | 4,456,858 |
| `tech_norm_pravila` (technical norms/rules) | 3,010,023 |
| `cons_budget` (budget consultations) | 890,267 |
| `forms_documents` | 570,512 |
| `svo` (empty) | 0 |
| `user` (empty) | 0 |
| `books` (empty) | 0 |

The empty `svo` collection is notable. "SVO" is the Russian-government abbreviation for "Specialnaya Voennaya Operatsia" — the official term for the Russia-Ukraine war. An advocate-services platform with a dedicated empty SVO collection suggests anticipated legal-services demand for the conflict (military exemptions, casualty claims, conscription appeals).

Additional ports on the same host: PostgreSQL (5432), POP/IMAP/SMTP mail stack (110/143/465/995/25), Nacos config server (8848). Likely a full LAMP-style deployment with the vector DB sitting alongside the relational and mail layers.

---

## RefugeeContent on Weaviate (`141.94.237.69`)

Weaviate's schema endpoint reports `pii_fields` as a per-property tag. One host carries this:

```json
{
  "name": "RefugeeContent",
  "vectorizer": "none",
  "properties": 24,
  "objects": 1,
  "pii_fields": ["source_username", "geo_address", "geo_phones", "geo_emails"]
}
```

The schema is **self-declared by the operator** to contain refugee identity records with geolocated contact info. The class name `RefugeeContent` plus four PII fields covering geographic address, phone numbers, and email addresses is among the most sensitive PII categories possible. Refugees often face active persecution from state actors or non-state armed groups; geolocation data plus phone/email exposes them to direct contact attack vectors.

The host is on OVH France (`vps-bbd11dc6.vps.ovh.net`). Adjacent open ports include **MongoDB (27017)** and **PostgreSQL (5432)**, both potentially carrying the underlying refugee records (Weaviate stores the embeddings; the source documents are typically in the relational DB).

Disclosure routing: OVH SAS abuse + cert-pivot to identify the operator. This is a humanitarian-emergency-class exposure.

---

## aishelter.underdog.my.id — Indonesian shelter HRIS

Indonesian host at `103.247.10.156` (Rumahweb Indonesia hosting, TLS SAN `aishelter.underdog.my.id`):

| Collection | Points |
|---|---:|
| `shelter_payroll` | 338,055 |
| `shelter_hris_employee_detail` | 208,053 |
| `shelter_hris_employee_site` | 207,851 |

754,000 employee/payroll records across what appears to be an HR information system for a shelter network. "Shelter" in this naming convention typically refers to humanitarian / NGO / homeless / domestic-violence shelter organizations. Adjacent ports include MySQL (3306), suggesting the relational source data is on the same host.

---

## bolt.kaychalabs.com — Internal enterprise AI knowledge stack

`204.10.144.25` (Revelex hosting, TLS SAN `bolt.kaychalabs.com`, prior cert `kaycha-ai.revelex.com`). 4.2M points across the "jarvis_*" naming pattern indicates a complete enterprise AI assistant:

| Collection | Points |
|---|---:|
| `jarvis_knowledge` | 3,589,311 |
| `jarvis_documents` | 463,716 |
| `jarvis_code` | 166,829 |
| `jarvis_tech_docs` | 11,082 |
| `jarvis_legal` | 8,714 |
| `jarvis_communications` | 6,170 |
| `jarvis_memory` | 2,522 |
| `jarvis_financial` | 1,164 |
| `jarvis_regulations` | 362 |
| `jarvis_schemas` | 63 |

`jarvis_legal`, `jarvis_financial`, `jarvis_communications` together imply the operator has embedded their internal legal, financial, and communications archives for AI retrieval. PostgreSQL (5432) is also open on this host.

Revelex is a travel-industry technology firm. Kaycha Labs appears to be the AI products arm.

---

## fridayai.online — 121-tenant SaaS exposure (`148.113.212.12`)

OVH Canada host, TLS SAN `fridayai.online`. 121 distinct workspace collections (`ws-XXX` UUIDs), plus a `conversation_archive` collection.

Largest workspaces:

| Collection | Points |
|---|---:|
| `ws-e6de74b1aaa8a683` | 116,401 |
| `ws-09d50e7a263d7f14` | 105,076 |
| `ws-6086420ff2d6d36f` | 59,041 |
| `ws-07fc084d74893079` | 46,733 |
| `ws-12ff6cc3ac637b3d` | 45,781 |
| `ws-dcaf72656044ac22` | 34,626 |
| `ws-57acd9f3a0a1a695` | 31,094 |
| `ws-dc1c04a01e6370de` | 27,721 |
| `ws-6a6c9569e4ffa1dc` | 21,904 |
| `ws-12fa45e33cdaac2d` | 16,171 |

The `ws-XXX` naming convention plus the count is the signature of a multi-tenant SaaS where each customer gets a workspace identifier. 121 customers' RAG data exposed to the internet on a single Qdrant cluster.

Adjacent ports are alarming: **MongoDB (27017)**, **Redis (6379)**, **kubelet (10250)** — exposed kubelet enables container-RCE on the Kubernetes node hosting all 121 workspaces. The data layer breach is one issue; the kubelet exposure means container escape to root on the cluster node is also reachable.

---

## vector.jezt.cloud — Multi-tenant SaaS, 264 collections

`35.154.114.115` (AWS Mumbai, TLS SAN `vector.jezt.cloud`). 10.7M points across 264 collections. Many of the collection names look like daily snapshots (`UV_special_1025_DDMMYYYY` running January through April 2026) and template data (`Json_data_NNNN`, `Unk_Rein_NNNN`). The `media_dubai_<uuid>` collections imply a Dubai-region media/PR customer dataset.

---

## Weaviate cohort highlights (other than RefugeeContent)

The Weaviate schema endpoint's `pii_fields` tagging revealed additional self-declared sensitive-data classes across the 127-host cohort:

| Host | Class | Self-declared PII fields |
|---|---|---|
| `141.94.237.69` | RefugeeContent | source_username, geo_address, geo_phones, geo_emails |
| `20.70.178.199` | MeetingTranscript / MeetingAI / CorrectionDelta | user_id, userId |
| `34.1.233.6` | EmployerBranding / Job / JobAzure | customer_id, city |
| `144.76.99.45` | LegalDocument / LegalDocumentChunk | court_name |
| `146.190.41.226` | Document / Sapb1dbdocs | original_filename, stored_filename, table_name |
| `164.90.195.110` | DocumentChunkBIS | user_id |
| `213.199.59.36` | DocumentChunk / Forge_memory / Test_memory | document_name |
| `109.123.243.170` | Documents | client_name |
| `100.42.179.216` | AssistantData / HistoryData | doc_name |
| `101.34.239.12` | QwenDocs | account_id |
| `118.145.107.162` | PolicyDocument | fileName |

The `pii_fields` declaration is a Weaviate schema feature operators *opt into*. Each of these hosts is a case where the operator has *acknowledged in code* that the class holds PII, and then exposed it without authentication. Twenty-three hosts in this Weaviate cohort had at least one class with non-empty `pii_fields`.

---

## Method

1. **Shodan harvest:** 6 protocol-strict dorks (`http.html:"qdrant"`, `product:"Weaviate"`, `port:8080+weaviate`, `product:"Milvus"`, `product:"Chroma"`, `port:8000+chroma`). Union: 917 candidates.
2. **aimap port scan:** 917 × 12 ports = 11,004 probe targets. 2,366 open ports surfaced.
3. **aimap fingerprint:** 699 service hits, 263 unique IPs identified across the four vendors.
4. **Per-vendor deep enumeration:** Qdrant `/collections` for point counts, Weaviate `/v1/schema` for collection schemas including `pii_fields`, ChromaDB `/api/v1/collections`, Milvus collection list.
5. **Restraint:** schema + metadata only. No `_search`, no `query`, no document reads. The class names and point counts are the finding.

---

## Disclosure pipeline

Three tiers:

**Tier 1 — critical, single-instance, humanitarian or large-scale PII:**
- `141.94.237.69` (RefugeeContent) → OVH abuse + operator-identification effort. Top priority.
- `103.247.10.156` (aishelter.underdog.my.id) → Rumahweb Indonesia abuse + operator. PII at scale.
- `148.113.212.12` (fridayai.online) → OVH Canada abuse + operator. 121 third-party customers affected; the operator must notify each.

**Tier 2 — large but single-organization:**
- `89.108.123.166` (advocat-online.ru) → Reg.Ru abuse + operator. Legal services data. Sensitive but single-operator.
- `204.10.144.25` (kaychalabs.com) → Revelex security + Kaycha Labs operator. Internal corporate.
- `20.127.155.10` (eclipseassistance.azure) → Microsoft Azure abuse + operator. Internal test data.

**Tier 3 — Weaviate PII-self-declared cohort (23 hosts):**
- Batch report to each respective hosting provider (OVH, Hetzner, DigitalOcean, GCP, AWS) listing affected customer IPs with the per-class `pii_fields` declarations.

---

## Toolchain provenance

```
JAXEN         [x] 917 candidates from 6 protocol-strict dorks
aimap v1.9.11 [x] 699 service hits in 1h50m
visorgraph    [ ] queued — cert-pivot on top 10 for operator IDs
aimap-profile [ ] queued — classification for the 23 PII-flagged Weaviate hosts
visorscuba    [ ] queued — compliance scoring (GDPR / refugee privacy / payroll)
visorlog      [ ] queued ingest
classifier    [x] Insight #30 multi-port honeypot filter (zero honeypots in this corpus)
```

---

## See also

- [`mcp-server-survey-2026-05-17.md`](mcp-server-survey-2026-05-17.md) — sibling survey
- [`llm-gateway-survey-2026-05-17.md`](llm-gateway-survey-2026-05-17.md) — sibling LLM-proxy survey
- [`../../methodology/insight-30-multi-port-identical-responses-identify-honeypots.md`](../../methodology/insight-30-multi-port-identical-responses-identify-honeypots.md)
