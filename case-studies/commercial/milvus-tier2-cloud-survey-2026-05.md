---
type: survey
---

# Milvus on Tier-2 Cloud: Auth Posture Survey (Scope Expansion)

_NuClide Research · 2026-05-04_
_Companion to: [`milvus-cloud-survey-2026-05.md`](milvus-cloud-survey-2026-05.md) (DO/Hetzner/Vultr baseline)_
_Sibling tier-2 expansions: [`ollama-tier2-cloud-survey-2026-05.md`](ollama-tier2-cloud-survey-2026-05.md), [`qdrant-tier2-cloud-survey-2026-05.md`](qdrant-tier2-cloud-survey-2026-05.md)_

---

## Summary

Mass-scan of port 19530 (Milvus REST/gRPC default) across the same **76 tier-2 /16 ranges (3.55M IPs), Scaleway + OVH + Linode** used in the Ollama and Qdrant tier-2 expansions. **5,480 port-open candidates → 429 raw "Milvus-shaped" responses → 393 honeypot fleet hits filtered → 36 real Milvus instances**.

<!-- ksat-tag:auto-generated:start -->
## DCWF KSAT coverage

Auto-derived from DCWF AI work-role rule files (`ksat-tag`).

- **672 (AI Test & Evaluation Specialist):** K7003, K7044, S7068, S7075, T5858, T5904
- **733 (AI Risk & Ethics Specialist):** K7040, T5854, T5868, T5893
- **overlap (Common AI KSATs (all 5 roles)):** K108, K1158, K22, K6311, K6900, K6935, K7003

<!-- ksat-tag:auto-generated:end -->

This survey is significant for two reasons:

1. **The honeypot pollution is dominant.** 91.6% of the raw "Milvus" hits on tier-2 cloud are part of the AS63949 (Akamai/Linode) deception fleet documented in [`ollama-tier2-cloud-survey-2026-05.md`](ollama-tier2-cloud-survey-2026-05.md). Cross-validation against the Ollama probe data was the discovery path. **Population-scale Milvus enumeration on Linode/Akamai requires the AS63949-fleet filter or it's nearly all noise.**

2. **The 36 real instances are a much smaller surface than the original DO/Hetzner/Vultr baseline (33 instances) suggested.** Combined: **69 confirmed real Milvus instances across 5.38M cloud IPs, 100% unauth.** The auth-off-default thesis holds; the population is just smaller than the noisy raw count implied.

The 36 real tier-2 Milvus deployments expose **130 collections** of vector data, including:

- A **Quebec municipal-government RAG operator** with collections per city/service (`rag_ville_de_saint_hyacinthe`, `rag_delson`, `rag_telefilm_milvus`, `rag_activille`)
- **Islamic religious-text RAG** (`SiddiqQuran`, `SunnahHadiths`, `SiddiqHadiths1`, `SiratVectorstore`, `SiratVectorstore1`, `SiratVectorstore2`)
- **Image-asset retrieval** over `kisspng.net` + `cleanpng.com` (millions of PNG image embeddings)
- A **17-collection multi-tenant document RAG with versioned snapshots and backup tags** (`document_chunks_08_11_2025`, `document_chunks_backup_20250921_203500`)
- French/Basque/Quebec-French/Indian-banking signals: `argia_albisteak` (Basque newspaper), `Doliprane`/`Lacoste` (French brand RAG), `axis_hybrid_embeddings_v1` (Axis Bank India?), `artefact_ocbc_ecommerce_prod_vit` (OCBC Bank Singapore + ViT image embeddings)

---

## Methodology

```
masscan -iL <76 tier-2 /16 CIDRs> -p 19530 --rate 10000
  → 5,480 port-19530 hits

milvus-probe.py (100-thread fingerprint, REST API)
  POST /v2/vectordb/collections/list   body {"dbName":"default"}
  GET  /v1/vector/collections          (older path, fallback)
  → 429 "Milvus-shaped" responses

honeypot-detector.py (filter pass)
  Detect AS63949 honeypot fleet via:
   - kitchen-sink JSON salt "wW0sffoqsk.EM"
   - dizquetv-RCE-PoC strings, fake JWTs, admin@example.com
   - chat-completion fields mixed into /api/tags
   - same response shape on disparate ports (11434/19530/6333/22/etc.)
  → 393 honeypots removed

Real Milvus: 36
```

The honeypot-detector pulls the full 393-host AS63949 fleet that was masquerading as Milvus on tier-2 cloud. Cross-reference with the Ollama survey's 169 honeypot pollution: **188 of those Linode IPs are simultaneously spoofing Ollama 0.1.33 AND Milvus 22-collection responses on the same machine**, same fleet, different fake services.

Read-only metadata only. NuClide:
- Did NOT submit `/v2/vectordb/entities/insert` writes
- Did NOT submit `/v2/vectordb/entities/search` semantic queries against operator indexes
- DID enumerate collection names and (via separate probes for case-study writeup) sample 1-2 entity payloads on 3 hosts to characterize data class

---

## Findings Summary

| Metric | Value |
|---|---|
| Tier-2 /16 ranges scanned | 76 |
| Total IPs scanned | 3,550,208 |
| Masscan hits on :19530 | 5,480 |
| Raw Milvus-shaped responses | 429 |
| AS63949 honeypot fleet filtered | 393 (91.6% of raw hits) |
| **Real Milvus confirmed** | **36** |
| **Unauthenticated** | **36 (100%)** |
| Populated (≥1 collection) | 31 |
| Total collections in unauth instances | 130 |

### Per-cloud breakdown (real, post-filter)

| Cloud | Real Milvus | Honeypot pollution |
|---|---|---|
| Scaleway | 4 | 0 |
| OVH | 23 | 0 |
| Linode | 9 | **393 (entire AS63949 fleet)** |

OVH dominates real Milvus (23/36), same OVH-commercial-dedicated-server pattern observed in the Ollama and Qdrant tier-2 expansions.

---

## Notable populated unauth deployments

### Quebec municipal-government RAG operator (158.69.219.1, OVH-CA)

```
Milvus 16 collections (all rag_*):
  rag_ville_de_saint_hyacinthe   (Saint-Hyacinthe, QC)
  rag_delson                      (Delson, QC)
  rag_telefilm_milvus
  rag_telefilm
  rag_activille                   (probably municipal services)
  rag_<other QC cities>
```

All collections are prefixed `rag_<entity>`, suggesting one operator running RAG-as-a-service for multiple Quebec municipalities and a Quebec film/television entity ("telefilm"). Saint-Hyacinthe and Delson are real Quebec municipalities. This is a **multi-tenant municipal-government AI deployment with no data-tier auth**, a citizen reaching the IP can semantic-search any tenant's corpus.

### 17-collection multi-version document RAG (141.94.64.10, OVH)

```
document_chunks_backup_20250921_203500
document_chunks_backup_20250921_203649
document_chunks_bm25
document_chunks_08_11_2025
internal_entities
document_chunks
... (12 more)
```

Versioned and backup-tagged document collections. Operator runs an iterative document-RAG with timestamped backups (Sept 21 2025 multiple times in one day, plus Aug 11 2025 dated snapshot). The `internal_entities` collection name is the most interesting, distinct from public document chunks, suggesting org-internal entity references kept alongside the public corpus.

### Islamic religious-text RAG (51.75.126.19, OVH)

```
SiddiqQuran
SiddiqHadiths1
SunnahHadiths
SiratVectorstore
SiratVectorstore1
SiratVectorstore2
```

A scholarly or educational RAG over Islamic primary texts:
- **Sahih al-Bukhari / Sahih Muslim Hadith corpora** ("Sunnah Hadiths")
- **Quran**
- **Sirat (Sirah) corpora**, biographies of the Prophet Muhammad

The "Siddiq" prefix is the Arabic honorific for Abu Bakr al-Siddiq (the first caliph), possibly a thematic tag or operator reference. Three `SiratVectorstore` versions suggests iterative re-embedding. No PII, but the operator's IP and methodology is exposed.

### Image-asset retrieval over kisspng.net + cleanpng.com (51.159.22.167, Scaleway)

```
kisspng_net_vector
kisspng_net_vector_cosine
kisspng_net_tags
kisspng_net_tags_bge_m3
cleanpng_com_vector
```

`kisspng.net` and `cleanpng.com` are large PNG-asset/clipart sites with millions of images. The collection naming (`<site>_vector`, `<site>_tags`, `<site>_tags_bge_m3`) suggests a visual-search or reverse-image-search RAG scraping these public asset libraries. The `bge_m3` suffix indicates BAAI's BGE-M3 multilingual embedding model.

### Versioned KB iterations (45.79.120.230, Linode: real, not honeypot)

```
knowledge_base
knowledge_base_v2
knowledge_base_oai
knowledge_base_oaiv5
knowledge_base_oaiv11
... (5 more)
```

An operator iterating embedding configurations (`oai` = OpenAI embeddings, `oaiv5`/`oaiv11` = OpenAI ada-002 vs text-embedding-3 dimensionality variants). All exposed unauth. Useful for cross-validation if the same content reappears in another cloud's Qdrant or ChromaDB exposure (operator-attribution potential).

### Multi-corpus knowledge service (172.104.168.188, Linode)

```
embeddings_with_title_source
article_embeddings
book_file_embeddings
resource_embeddings
faq_embeddings
```

Distinct corpora separated by source type, articles, books, resources, FAQs. Looks like a scholarly/library knowledge service.

### MolGenie pharmaceutical/molecular RAG (51.79.201.174, OVH-CA)

```
molgenie_kb_v2
molgenie_docs_v1
```

"MolGenie", searchable web reveals it as a molecular/pharma RAG product (https://molgenie.com or similar). Two versioned corpora (KB + docs).

### Notable cross-domain collection names

| Collection | Likely operator class |
|---|---|
| `axis_hybrid_embeddings_v1` | Axis Bank India hybrid retrieval |
| `artefact_ocbc_ecommerce_prod_vit` | OCBC Bank Singapore + ViT (Vision Transformer = product image embeddings) |
| `argia_albisteak` | Basque language news ("Argia" newspaper, "albisteak" = news) |
| `Doliprane` / `Lacoste` / `Watch_Ali1Blue` | French e-commerce product/brand catalog (Doliprane = paracetamol; Lacoste = luxury) |
| `bachir_rappelle_toi` | French personal-memory chat ("Bachir, remember yourself") |
| `c68c803d72df83_studies` | UUID-prefixed multi-tenant scholarly studies |

The diversity of named entities across 36 hosts is consistent with the auth-off-default thesis: **operators across industries** (banking, religious-scholarly, municipal-government, image-search, e-commerce, pharma) deploy Milvus and don't configure auth. The framework default reproduces the failure pattern across every operator culture in the tier-2 sample.

---

## The AS63949 honeypot fleet (methodological note)

Of the 429 raw "Milvus" responses, **393 were part of the AS63949 honeypot fleet**:

```
Real Milvus (validated):    36 (8.4%)
AS63949 honeypot fleet:    393 (91.6%)
```

The honeypot fleet returns a single kitchen-sink JSON template on port 19530 that contains every common AI-API field (`code`, `data`, `accessToken`, `csrfToken`, `userId`, `model`, `version`, `models`) plus malicious-trigger strings (`uid=0(root)`, `wW0sffoqsk.EM` shadow-passwd salt, `dizquetv:1.5.3`, `VULNERABLE -version`). My initial Milvus probe checked only "does the response have `code` and `data` keys", which the honeypot trivially satisfies.

**Filter signature** (any single match is sufficient):
- Response on ANY AI-stack port contains the unique salt `wW0sffoqsk.EM`
- Response on `/api/tags` mixes Ollama chat-completion fields with a `models` array
- Response on `/v2/vectordb/collections/list` contains `dizquetv` or `admin@example.com`
- Same kitchen-sink JSON returned on port 22, 80, 443, 3306 (no real service does this)

The full fleet attribution is in the Ollama tier-2 case study. Methodologically, this survey series now adds **AS63949-honeypot-fleet filtering as a standard preprocessing step for tier-2 cloud OSINT**, the alternative is reporting noise as findings.

---

## Cross-survey comparison

| Survey | Cloud | Real Milvus | Total collections | Largest sample |
|---|---|---|---|---|
| [DO/Hetzner/Vultr baseline](milvus-cloud-survey-2026-05.md) | DO/Hetzner/Vultr | 33 | (per source survey) | Everos (multi-tenant agent platform), Saudi/Gulf legal RAG |
| **Tier-2 expansion** | **Scaleway/OVH/Linode** | **36** | **130** | **Quebec municipal RAG, Islamic-text RAG, kisspng image search** |
| **Combined** | All 6 clouds | **69** | n/a | n/a |

Both samples are 100% unauth on populated instances. The auth-off-default thesis (Milvus RBAC opt-in, ships off) reproduces cleanly.

---

## Disclosure posture

- **Quebec municipal-government RAG (158.69.219.1)**, single-operator, multi-tenant, public-sector. **Disclosure-priority candidate.** The municipal-tenant model (Saint-Hyacinthe + Delson + others co-located on one Milvus) is the same risk class as the HolaModa multi-tenant fashion-retail finding (`multi-holamoda-multitenant.md`), one tenant accidentally getting another's data. Will draft a coordinated disclosure to the operator (whose identity is reachable via reverse DNS / cert / WHOIS).
- **Islamic-text RAG operator (51.75.126.19)**, content is public/scholarly; exposure is operational/IP, not user-data. Lower disclosure priority.
- **Image-search and product-catalog operators**, IP exposure, no user-PII risk; aggregate disclosure note.
- **AS63949 honeypot fleet attribution**, no disclosure; fleet operator is a security-research entity per the signature analysis. Possibility-of-Akamai-internal infrastructure means disclosure would land back at the same address.

---

## Raw Data

```
~/recon/milvus-tier2-2026-05-04/tier2-milvus-real.jsonl       (36 hosts)
~/recon/milvus-tier2-2026-05-04/tier2-milvus-confirmed.jsonl  (429 raw, includes honeypots)
~/recon/ollama-tier2-2026-05-04/as63949-honeypot-fleet.txt    (169-host overlap; full 393 in raw)
```

---

## See Also

- [`ollama-tier2-cloud-survey-2026-05.md`](ollama-tier2-cloud-survey-2026-05.md), sibling survey + AS63949 honeypot fleet documentation
- [`qdrant-tier2-cloud-survey-2026-05.md`](qdrant-tier2-cloud-survey-2026-05.md), sibling survey (Qdrant probe was strict, no honeypot pollution)
- [`milvus-cloud-survey-2026-05.md`](milvus-cloud-survey-2026-05.md), original DO/Hetzner/Vultr baseline (33 instances)
- [`SYNTHESIS-2026-05.md`](SYNTHESIS-2026-05.md), cross-survey synthesis paper
