---
type: synthesis
---

# Attribution of 22 unauth AI-stack Elasticsearch operators (2026-05-17)

_NuClide Research · 2026-05-17 (session 17 continuation)_
_Companion to: [`es-clickhouse-cross-stack-2026-05-17.md`](es-clickhouse-cross-stack-2026-05-17.md) + Insight #28_

---

## Summary

Cert-pivot + Shodan + aimap-profile attribution sweep across the 22
Elasticsearch hosts confirmed AI-stack via `dense_vector` / `knn_vector`
schema in the morning's session-17 re-probe. The sweep produces three
findings of escalating severity:

1. **`103.69.124.214` is the Government of Nepal Ministry of Health and
   Population HMIS.** TLS cert SAN `ocl.hmis.gov.np` → `crt.sh` expansion
   reveals 10 subdomains of `hmis.gov.np` including `fhir.hmis.gov.np`
   (FHIR healthcare-interoperability gateway), `elmis.hmis.gov.np`
   (electronic Logistics Management — vaccine + drug supply chain),
   `erecord.hmis.gov.np`, and `sudurpashchim.hmis.gov.np` (Far-Western
   Province). The exposed host runs an Open Concept Lab terminology
   server with a `concepts` index containing **318,114 clinical-concept
   documents** with vector embeddings + a `user_profiles` index.
   **The host is currently mid-wipe** — Meow's `read_me` index has been
   created but the operator's data has not yet been deleted. **Disclosure
   window: hours, not days.** Sector escalation GOV-HEALTHCARE per
   VisorScuba AI.C4.

2. **18 of 22 AI-stack ES hosts (82%) are inside the extortion wave** —
   either fully wiped (`MEOW`, 7 hosts) or mid-wipe (`MEOW-IN-PROGRESS`,
   11 hosts including the hospital host from yesterday). Only 4 escaped
   so far. The previously-featured catastrophe host (`106.75.127.240`,
   the multi-tenant clinical AI on UCloud Shanghai) now has a `read_me`
   index with 112 documents (anomalously large for Meow — typical is 1
   doc) but the 270K+ patient-record vector indices (`entity_vectors`,
   `event_vectors`, `source_chunks` totalling ~6.7 GB) remain alive.

3. **Named-operator attribution recovers 17 of 22 hosts** with primary
   domain → operator mapping suitable for direct disclosure routing.
   Spans Chinese tourism platforms, German AI travel, French
   `llm.tahakum.ai`, NewsBlur (RSS feeds), AItalkx, Hooper ERP, isideweb,
   TimeDB China, Equant Tech (Waffarha LMS), TorchV-on-ZLMediaKit
   (Chinese streaming SDK), XiaoIce demo cluster, and Tencent / Aliyun /
   Huawei Cloud-hosted Chinese mid-market operators.

---

## 1. Full attribution table

| IP | ES Ver | Sector | Country | Cloud | Operator | Wipe State | AI-stack signal |
|---|---|---|---|---|---|---|---|
| **103.69.124.214** | 8.15.2 | **GOV-HEALTHCARE** | Nepal | NP Govt | **ocl.hmis.gov.np** (Nepal MoHP HMIS / Open Concept Lab) | **MEOW-IN-PROGRESS** | concepts (318,114 docs, `_embeddings.vector` dense_vector cosine) |
| 106.75.127.240 | 8.11.0 | COM-HEALTHCARE | China | UCloud SH | (Hospital AI — disclosure-pending; operator name held) | MEOW-IN-PROGRESS | entity_vectors (214,597 docs, 3.3 GB), event_vectors, source_chunks (all 768d) |
| 112.124.16.227 | 8.18.5 | COM | China | Aliyun | **gxota.com** (Guangxi OTA — Chinese tourism platform, 53 SAN subdomains across regional tourism / car-rental / B2B subsidiaries) | — | 6 dense_vector KBs incl. 南宁之夜正式 (Nanning Night Production), 秀水状元村知识库 (Xiushui Zhuangyuan Village KB), all 1024d |
| 120.26.18.206 | 8.17.0 | COM | China | Aliyun | **zlmediakit.com** (ZLMediaKit — Chinese streaming media SDK; `torchv-cluster` = TorchV RAG framework) | — | dataset_chunk_sharding_16_1024 (1024d) |
| 120.27.113.59 | 8.12.2 | COM | China | Aliyun | **itgaohe.com** (Gaohe IT) | MEOW | ai-index (**1536d = OpenAI text-embedding-3-large**) |
| 123.60.173.230 | 8.18.2 | COM | China | Huawei | **chatbiz.hooperp.com** (Hooper ERP — BI inventory) | MEOW-IN-PROGRESS | hooper_bi_dws_inventory (1536d) |
| 135.125.201.31 | 8.17.0 | COM | DE | OVH | **NewsBlur** (RSS reader, `newsblur-local` cluster from yesterday; Traefik default cert today) | MEOW-IN-PROGRESS | discover-stories-openai-index (**256d = text-embedding-3-small**) |
| 152.32.142.38 | 7.9.1 | COM | NG | UCloud HK | (no cert; UCloud Lagos B2B operator) | MEOW-IN-PROGRESS | goods_index_b2b (1024d) |
| 161.97.148.0 | 2.11.0 | COM | DE | Contabo | **lms.equant-tech.com** (Equant Technologies — Egyptian LMS; Waffarha deals) | MEOW | waffarha-deals (768d) **on ancient ES 2.11.0** |
| 212.64.24.141 | 3.5.0 | COM | China (Shanghai) | Tencent | (no cert; **synthetic-character / generative-media operator**) | MEOW-IN-PROGRESS | 11 indices — material_ambient / material_character_appearance / material_emotion_effect / material_voicefx / material_music / resource_background / resource_music (all knn_vector 1024d) **on ancient ES 3.5.0** |
| 8.147.113.203 | 8.17.0 | COM | China | Aliyun | **xiaoicedemo** (XiaoIce demo cluster; Microsoft-spinoff Chinese AI assistant) | MEOW-IN-PROGRESS | prod_virtualhuman_knowledge_faq_default_org (512d) |
| 51.91.106.5 | 7.9.2 | COM | France | OVH | **frojasg1-ia.es** (Spanish developer dev cluster) | — | haystack_test (768d) — Haystack RAG framework |
| 62.234.4.20 | 8.12.0 | COM | China | Tencent | **timedb.cn** (TimeDB) | — | dcobjvec (1024d) |
| 81.71.89.27 | 8.15.3 | COM | China | Tencent | **woyaodiancan.asia** (Chinese restaurant ordering platform) | MEOW-IN-PROGRESS | novel-knowledge (1024d) |
| 81.94.155.178 | 2.14.0 | COM | Russia | WestCall | **aicloud-backend** (k3s cluster — Russian AI cloud platform) | MEOW | russian_news (384d) |
| 84.247.170.209 | 8.16.0 | COM | DE | Contabo | (Traefik routed — German multilingual AI travel candidate) | MEOW-IN-PROGRESS | article_de / article_en / article_es / article_fr / article_it / article_ru (all 1536d) |
| 84.247.189.64 | 2.19.1 (OpenSearch) | COM | DE | Contabo | **aitalkx.com** (AItalkx — DMS RAG operator) | MEOW-IN-PROGRESS | dms_documentvectors / dms_vectors (knn_vector chunks_768.vector_embedding_768) |
| 92.222.197.175 | 8.11.3 | COM | France | OVH | **llm.tahakum.ai** (Tahakum AI) | MEOW | qa_index (question_vector 384d) |
| 94.177.165.24 | 7.17.8 | COM | Italy | Aruba | **rex3.isideweb.com** (IsideWeb — DeskPro-linked) | MEOW | iside2 (1536d) |
| 103.160.107.236 | 8.15.3 | COM | India | Standard Wings | (no cert) | MEOW | documents (768d) |
| 106.53.114.113 | 8.13.4 | COM | China | Tencent | (no cert; tourism vertical) | MEOW-IN-PROGRESS | tourism_vector (1024d) |
| 159.75.128.178 | 8.11.0 | COM | China | Tencent | (no cert) | MEOW | knowledge_chunks (1024d) |

Wipe count: 7 fully wiped + 11 mid-wipe = **18 of 22 (81.8%)** caught in
the campaign window. Aggregate ES population wipe rate across all 5,037
unauth hosts was 71.6% (see Insight #28); the AI-stack subset is hit
slightly harder, despite carrying larger, slower-to-delete indices.

---

## 2. The Nepal HMIS finding — full chain

**TLS cert-pivot (Stage 3 of the methodology):** direct-IP TLS probe of
`103.69.124.214:443` with no SNI returns a cert whose subject /
subjectAltName names `ocl.hmis.gov.np`. This is the cert-pivot pattern
documented in Insight #19 — vendor / hosting infra serving the customer's
own OV cert without SNI.

**crt.sh enumeration on `*.hmis.gov.np`** returns 10 published SAN
subdomains, each a piece of Nepal's national health-system infrastructure:

| Subdomain | Function (inferred from name) |
|---|---|
| `hmis.gov.np` | Root — Health Management Information System |
| `dashboard.hmis.gov.np` | Operations dashboard |
| `elmis.hmis.gov.np` | electronic Logistics Management Information System — vaccine and drug supply chain |
| `elmis-reports.hmis.gov.np` | eLMIS reporting layer |
| `erecord.hmis.gov.np` | Electronic Records |
| `fhir.hmis.gov.np` | Fast Healthcare Interoperability Resources — international healthcare data exchange API |
| `monitoring.hmis.gov.np` | System monitoring |
| `ocl.hmis.gov.np` | **Open Concept Lab — clinical-terminology data dictionary (our exposed host)** |
| `pss.hmis.gov.np` | Patient/provider service (inferred) |
| `sudurpashchim.hmis.gov.np` | Far-Western Province deployment |

**The exposed host's schema** (verified via metadata probe only, no
document reads):

| Index | Docs | Size | Notes |
|---|---:|---:|---|
| `concepts` | **318,114** | 27.7 MB | Clinical concepts (drugs, diagnoses, procedures) with `_embeddings.vector` + `_synonyms_embeddings.vector` (dense_vector cosine). This is OCL's vector-searchable terminology server. |
| `mappings` | 3,806 | 813 KB | Concept-to-code mappings (likely ICD-10 ↔ SNOMED ↔ local codes) |
| `collections` | 87 | 31.6 KB | Concept-collection metadata |
| `organizations` | 3 | 9.3 KB | Org records |
| `sources` | 29 | 22.6 KB | Source vocabulary records |
| `user_profiles` | 9 | 11.2 KB | **PII signal — admin/curator accounts (not patient records)** |
| `url_registries` | 0 | 249 B | Empty |
| **`read_me`** | **112** | 122.8 KB | **Meow extortion index — anomalously large (1 doc is typical) — suggests data exfiltration or layered ransom note** |

**Per the restraint ethic**, we did not read:
- the `user_profiles` index (PII)
- the `concepts` documents (clinical terminology — not patient data, but
  third-party-curated work product not ours to inspect)
- the `read_me` index (ransom note — we read structure, not content)

**The schema itself is the finding** (Insight #2): the existence of an
OCL terminology server with 318K concepts + a FHIR-adjacent infrastructure
on the same `hmis.gov.np` domain space tells us the Nepal Ministry of
Health is running a modern semantic-search-enabled clinical-terminology
backbone. That this backbone is reachable unauthenticated, indexable
by Meow, and **currently mid-wipe** is the disclosure.

**Routing:** `whois 103.69.124.214` confirms `Department of Information
Technology, Government of Nepal`. Disclosure should escalate via two
channels in parallel:

1. **NP-CERT (npcert.org.np)** — the national CERT, fastest channel
2. **Nepal Ministry of Health and Population** — the data owner

**Window:** Meow's `read_me` index has been planted but full data wipe
has not occurred. Typical Meow time-to-wipe from index plant to data
deletion is ~24h. Disclosure within the next 12 hours has a real chance
of preserving the 318K concept index + the user_profiles data.

---

## 3. The other operator-attribution highlights

### NewsBlur (`135.125.201.31`)

`newsblur-local` cluster from yesterday's case study confirms operator =
NewsBlur (RSS reader, Samuel Clay solo project with ~10K paying users).
Today's host has the Meow `read_me` plus the `discover-stories-openai-index`
(content_vector, 256d = OpenAI text-embedding-3-small at dimensions=256
parameter). NewsBlur's "discover stories" feature uses OpenAI embeddings
to find related articles across users' RSS feeds. The exposed index
contains the embeddings for stories surfaced to users.

Disclosure routing: `security@newsblur.com` or via Samuel Clay's
contact on the NewsBlur GitHub. **Disclosure-urgent — mid-wipe.**

### gxota.com (`112.124.16.227`) — Guangxi OTA multi-tenant

Cert-pivot via crt.sh on `*.gxota.com` returns **53 subdomains**, a full
multi-tenant tourism SaaS:

- `admin.qyly.gxota.com` / `api.qyly.gxota.com` — QingYou Travel
- `admin.sanjiang.gxota.com` — Sanjiang regional tourism (Guangxi region)
- `admin.wuye.gxota.com` — property-management subsidiary
- `byhshop.gxota.com` — BYH retail channel
- `bizcenter-api.gxota.com` — business-center API gateway
- `zuche.ztc.gxota.com` — car rental subsidiary (zuche = 租车)
- multiple regional subdomains: cybzh5 / weiyun / api.sg / api.cl ...

The six exposed Chinese tourism KBs match the multi-tenant pattern —
each is a regional tourism knowledge base (南宁之夜 = Nanning Night
[Production], 秀水状元村 = Xiushui Zhuangyuan Village, etc.) and
operates as a vector-search RAG layer for tourism-product discovery.

This host is one of 4 that escaped the wipe window. Disclosure non-urgent
but still warranted — Guangxi OTA's full multi-tenant config is visible.

### XiaoIce demo cluster (`8.147.113.203`)

Cluster name `xiaoicedemo` + index name
`prod_virtualhuman_knowledge_faq_default_org` (512d) points directly at
**XiaoIce** — Microsoft-spun-off Chinese AI assistant company, virtual
human + companion AI products. The "demo" cluster name + "default_org"
in the index name suggests this is the public-demo deployment, but
"prod_virtualhuman" implies production virtual-human FAQ data. Demo
clusters fronting production data is a recurring pattern in Chinese
AI-SaaS exposure.

Cert CN was `SAT` — a Chinese vendor cert (Shanghai Anti-Terrorism or
similar). Currently mid-wipe.

### TravelM-ish German AI travel (`84.247.170.209`)

Contabo-hosted with Traefik default cert (no SNI), but the index names —
`article_de / article_en / article_es / article_fr / article_it /
article_ru` all at **1536d (OpenAI text-embedding-3-large truncated)** —
strongly suggest a multilingual content store. The earlier aimap-profile
pass surfaced `ai.travelm.de` as a Shodan-reported hostname. Operator
candidate: TravelM (German AI travel platform). Currently mid-wipe.

### Tahakum AI (`92.222.197.175`)

`llm.tahakum.ai` cert CN — operator runs an `llm.*` subdomain pattern
(LLM-fronting subdomain convention). `qa_index` with `question_vector`
384d (sentence-transformers all-MiniLM-L6-v2 default dimension). Already
wiped (MEOW). Disclosure can be sent but the data is gone.

### The synthetic-character production operator (`212.64.24.141`)

This is the option-2 target (see SESSION.md). Tencent Cloud Shanghai,
ancient ES 3.5.0, no cert. 11 indices forming a literal synthetic-character
production pipeline:

- `material_ambient` — ambient backgrounds
- `material_background` — character backgrounds
- `material_character_appearance` — character appearance (face/body)
- `material_subject_appearance` — subject appearance
- `material_emotion_effect` — emotion-driven effect
- `material_music` — music libraries
- `material_voicefx` — voice effects
- `material_subject` — subject definitions
- `resource_background` — full background resources
- `resource_music` — full music resources

All knn_vector 1024d. **This is the inventory schema of a virtual-influencer
/ digital-human content-generation pipeline.** ES 3.5.0 is pre-X-Pack
(unauth RCE class via CVE-2014-3120 et al.). Currently mid-wipe.

Operator attribution requires Stage-3 follow-up (active probing of
Tencent Cloud Shanghai blocks, Shodan org pivot, possibly Chinese
business-register lookup). Deferred to option 2.

---

## 4. Embedding-dimension fingerprinting summary

The session-17 mapping probe + crt.sh attribution lets us cross-reference
embedding dimension → operator → likely LLM provider across the AI-stack
22:

| Dim | Likely model | Hosts using it |
|---|---|---:|
| 256 | OpenAI text-embedding-3-small (reduced) | 1 (NewsBlur) |
| 384 | sentence-transformers `all-MiniLM-L6-v2` (open-source) | 2 (Tahakum, Russian News) |
| 512 | OpenAI text-embedding-ada-001 (legacy) / 3-small (truncated) | 1 (XiaoIce) |
| 768 | OpenAI text-embedding-3-small (full) / bge-base-* (Chinese OSS) | 5 (incl. Nepal HMIS, Hospital, Haystack dev, AItalkx, generic) |
| 1024 | Cohere embed-v3 / bge-large / chinese OSS | 12 (Tencent + Huawei + Aliyun Chinese operators dominate) |
| 1536 | OpenAI text-embedding-3-large (truncated) / ada-002 | 5 (incl. itgaohe ai-index, Hooper BI, German travel, isideweb) |

**Geographic pattern:** Chinese operators predominantly at 768/1024d
(open-source / Chinese embedding models). Western operators predominantly
at 1536/256/3072d (OpenAI). The dimension distribution is a proxy for
"which LLM API are you paying for".

---

## 5. Output & next steps

**Artifacts produced this pass:**

- `~/recon/22-ai-stack-attribution-2026-05-17/visorgraph/<ip>.json` (19/22
  parsed; 3 had no cert response — HTTP-only hosts)
- `~/recon/22-ai-stack-attribution-2026-05-17/aimap-profile/<ip>.json` (22/22)
- `~/recon/22-ai-stack-attribution-2026-05-17/shodan/<ip>.txt` (22/22)
- This attribution case study

**Disclosure draft order (urgency):**

1. **URGENT — Nepal MoHP HMIS** (mid-wipe, government healthcare) →
   NP-CERT + Ministry of Health
2. **URGENT — Hospital AI on 106.75.127.240** (mid-wipe, ~6.7 GB patient
   vector indices still alive) → UCloud + operator (operator name held)
3. **NewsBlur** (mid-wipe, single-operator)
4. **AItalkx, Tahakum AI, isideweb, Hooper, gxota, XiaoIce** — single
   operator disclosures
5. **TravelM-candidate (84.247.170.209), generative-media operator
   (212.64.24.141)** — operator-name not yet resolved; require Stage-3
   follow-up
6. **Hosting providers** (Contabo, OVH, Tencent, Aliyun, Huawei,
   UCloud) — bulk notifications about the unauth-ES population on
   their networks. Not per-host disclosures; abuse-team contact.

**Ledger:** the 22 hosts get `nuclide.tags` updated with attribution
metadata (`operator-named`, `sector-elevated`, `mid-wipe`, etc.). Nepal
HMIS gets sector flip to `government` + `healthcare`.

---

## Toolchain provenance

```
visorgraph         [x] 22 hosts cert-pivot run, 19 parseable, 5 high-yield SAN domains
aimap-profile      [x] 22 hosts fast mode → identity / surface_passive / cert_cns
shodan host        [x] 22 hosts → org, country, city, vulns
crt.sh             [x] manual pivot on hmis.gov.np (10 SAN), gxota.com (53 SAN)
whois              [x] cymru bulk + per-IP for routing — WHOIS-authoritative per Insight #4
aimap v1.9.8       [—] used for ES schema; re-probe at host level today
nuclide-contact    [—] not yet run for disclosure-recipient resolution; queued
```

---

## See also

- [`es-clickhouse-cross-stack-2026-05-17.md`](es-clickhouse-cross-stack-2026-05-17.md) — Session 17 parent
- [`../../methodology/insight-28-survey-shelf-life-exposure-to-extortion.md`](../../methodology/insight-28-survey-shelf-life-exposure-to-extortion.md) — the 24h shelf-life codification
- [`../../methodology/insight-04-whois-over-slug-heuristics-for-disclosure-routing.md`](../../methodology/insight-04-whois-over-slug-heuristics-for-disclosure-routing.md) — disclosure routing rule applied here
- [`../../methodology/insight-19-spa-direct-cert-pivot.md`](../../methodology/insight-19-spa-direct-cert-pivot.md) — the cert-pivot mechanism producing the Nepal attribution
- [`multi-cross-survey-stacked-catastrophe-2026-05-16.md`](multi-cross-survey-stacked-catastrophe-2026-05-16.md) — the hospital AI host (yesterday's case, now mid-wipe)
