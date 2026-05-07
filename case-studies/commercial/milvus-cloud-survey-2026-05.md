# Milvus on Public Cloud: Auth Posture Survey

_NuClide Research · 2026-05-03_

---

## Summary

Sweep of 1.83M IPs across 28 cloud-provider /16 ranges (DigitalOcean, Hetzner, Vultr) on port 19530 → 275 masscan hits → **33 confirmed Milvus instances** via the `/v2/vectordb/collections/list` REST API → all returned `code: 0` (success) with no authentication. **All 33 unauthenticated.** 27 of 33 contain non-empty collections.

Milvus 2.4+ unifies REST and gRPC on port 19530 via the proxy component. The REST API exposes collection list, schema (`describe`), and entity query (`/v2/vectordb/entities/query`) without authentication when RBAC is not configured, RBAC is opt-in, not default. This matches the Qdrant / ChromaDB pattern: the vector-DB layer of the modern RAG stack ships open and operators rarely close it.

---

## Methodology

```
masscan -iL <28 cloud /16 CIDRs> -p 19530 --rate 10000
  → 275 masscan hits on :19530

milvus-probe.py (100-thread REST API probe)
  POST /v2/vectordb/collections/list  body {"dbName":"default"}
  match {"code":0, "data":[<collections>]}
  fallback v1: GET /v1/vector/collections - match {"code":200, "data":[...]}
  → 33 confirmed Milvus instances (32 v2, 1 v1)

milvus-deep.py (per-collection schema describe)
  POST /v2/vectordb/collections/describe  body {dbName, collectionName}
  → field schemas for 28 of 33 instances (5 returned empty schemas - likely permission-gated describe)
```

---

## Findings Summary

| Metric | Value |
|---|---|
| Cloud /16 ranges scanned | 28 (DO/Hetzner/Vultr) |
| Masscan hits on :19530 | 275 |
| Milvus REST confirmed | **33** |
| Unauthenticated | **33 (100%)** |
| With non-empty collections | 27 |
| Empty / fresh installs | 6 |

### API version split

| Version family | Count |
|---|---|
| v2 (Milvus 2.4+) | 32 |
| v1 (Milvus 2.3.x and earlier) | 1 |

### Hosting provider split

| Provider | Confirmed |
|---|---|
| Hetzner | 16 |
| DigitalOcean | 11 |
| Vultr | 6 |

---

## High-Value Exposures

### 1. Everos AI Agent Platform: Multi-Tenant Episodic Memory + User Profiles

**Host:** `167.172.135.156:19530` (DigitalOcean) · v2 · multi-tenant

**Collections (6):**

| Collection (suffixed with creation timestamp) | Fields |
|---|---|
| `t_everos_v1_episodic_memory_*` | `id, vector, user_id, group_id, session_id, participants, sender_ids, type, timestamp, episode, search_content, parent_type, parent_id, tenant_id` |
| `t_everos_v1_foresight_record_*` | `id, vector, user_id, group_id, session_id, participants, sender_ids, type, start_time, end_time, duration_days, parent_type, parent_id, tenant_id` |
| `t_everos_v1_atomic_fact_record_*` | `id, vector, user_id, group_id, session_id, participants, timestamp, sender_ids, type, parent_type, parent_id, tenant_id` |
| `t_everos_v1_user_profile_*` | `id, vector, user_id, group_id, scenario, memcell_count, item_type, embed_text, tenant_id` |
| `t_everos_v1_agent_case_*` | `id, vector, user_id, group_id, session_id, timestamp, task_intent, parent_type, parent_id, tenant_id` |
| `t_everos_v1_agent_skill_*` | `id, vector, user_id, group_id, cluster_id, content, maturity_score, confidence` |

**What's exposed:**

The schema is sophisticated, this is a production AI agent platform with cognitive architecture worth describing:

- **Episodic memory**, full conversation episodes with participant lists, sender IDs, parent linkage
- **Foresight records**, agent-generated predictions/plans (start/end time, duration)
- **Atomic facts**, extracted assertions from conversations
- **User profiles**, scenario-keyed, with memcell counts indicating cognitive primitives stored per user
- **Agent cases**, task instances with `task_intent`
- **Agent skills**, learned behaviors with `maturity_score` + `confidence`

The `tenant_id` field on every collection confirms **multi-tenant SaaS**. Collection names are timestamped (`20260421060534632549` = April 21, 2026 06:05:34), provisioning creates fresh collections per deployment generation.

**Risk:** A complete AI-agent-platform dump is exposed. An attacker can:
- Enumerate all users (via `user_id` field on every collection)
- Enumerate all tenants (via `tenant_id`)
- Read full conversation history per user (`episodic_memory.episode` + `search_content`)
- Read agent's predictive plans (`foresight_record`)
- Read extracted personal facts (`atomic_fact_record`)
- Read learned agent behaviors and confidence levels (`agent_skill`)

This is the most architecturally complete exposure in the survey, Everos appears to be a real AI-agent SaaS startup; the deployment date suggests recent production launch.

---

### 2. Multi-Tenant "Intelbase" Platform: 25 Tenant Collections

**Host:** `167.71.232.155:19530` (DigitalOcean) · v2

**Collections (25):**
`intelbase_42`, `intelbase_59`, `intelbase_74`, `intelbase_77`, `intelbase_68`, … (25 numbered tenant collections)

**Schema:** Only `id` and `vector` exposed via `describe`, likely full schema requires auth, or the operator's collection definition is intentionally minimal (vector + ID only, all metadata in a sibling MongoDB/Postgres).

**What's exposed:** A multi-tenant SaaS with sequential tenant IDs starting from low numbers (42, 59, 68, 74, 77, gaps suggest churn). The "intelbase" naming + sequential customer IDs indicates a B2B intel/OSINT product where customers each get their own collection. Even without payload visibility, the **list of customer numbers** is itself competitive intelligence, a rival can enumerate the customer count and growth rate by polling `/collections/list` periodically.

---

### 3. Saudi/Gulf Legal RAG: `mahkamaty_prod`, `hakam_laws`

**Host:** `65.109.51.219:19530` (Hetzner) · v1

**Collections (10):** `law_collection`, `hakam_laws`, `mahkamaty_prod_new`, `mahkamaty_prod`, `hakam`, …

**What's exposed:** The Arabic naming is distinctive: *mahkamaty* (محكمتي) translates to *"my courts"* and is a known Saudi e-litigation portal brand. *hakam* means *"arbitrator"*. This appears to be a Gulf-region legal-tech operator running Milvus as the RAG backend for legal document retrieval. The `_new` suffix on `mahkamaty_prod_new` indicates active development (a v2 of the production index).

**Risk:** Saudi Arabia's PDPL (Personal Data Protection Law, in force 2024) requires controllers to implement security measures appropriate to data sensitivity. Legal/judicial data is high-sensitivity by any framework. If `mahkamaty_prod` contains case-related embeddings, exposure breaches PDPL Article 19 (security obligations) and likely Article 33 (breach notification within 72 hours).

---

### 4. Midea (Chinese Appliance MFG) Corporate Knowledge Base

**Host:** `65.108.127.99:19530` (Hetzner) · v2

**Collections (4):** `kb_midea`, `kb_midea_2`, `kb_midea__`, `kb_midea3`, four iterations of the same KB

**Schema fields per collection:**
`id`, `text`, `dense`, `sparse`, `pdf_id`, `chunk_index`, `page_number`, `folders`, `metadata`

**What's exposed:** Hybrid (dense + sparse) embedding indices over PDF documents with chunk-level + page-level addressing and folder hierarchy preserved in the `folders` field. Midea is a $50B+ Chinese household appliance manufacturer, exposure of corporate KB would include internal procedures, product specs, supplier documentation, M&A diligence material, etc. The four collection iterations indicate ongoing KB experimentation by an internal team.

---

### 5. Facial Recognition Doxing Primitive: `psos` + `onlyfans`: 1.21M face embeddings

**Host:** `65.108.107.240:19530` (Hetzner FI) · v2

**Operator:** `tweet-optimize.com` (per port-80 HTTP 301)

**Collections (2):**

| Collection | Count |
|---|---|
| `onlyfans` | **897,111** |
| `psos` | **313,066** |

**Schema:** `id, mongo_id, image_id, embedding, bbox1, bbox2, bbox3, bbox4`

This is the most impactful finding in the survey. 1.21M facial embeddings of OnlyFans content, plus a second `psos` dataset, exposed unauthenticated. The Milvus `/v2/vectordb/entities/search` endpoint accepts a face vector and returns nearest-neighbor matches: it is a **functional doxing primitive**. An attacker with a target's photo can compute a comparable face embedding locally and query the operator's index to find which OnlyFans accounts the person appears on.

Full writeup with operator-attributed disclosure path, embedding-space attack details, and sibling-MongoDB analysis: **[multi-tweet-optimize-facial-recognition.md](multi-tweet-optimize-facial-recognition.md)**

---

### 6. Multi-Tenant UUID-Named Collections (38 tenants)

**Host:** `168.119.242.46:19530` (Hetzner) · v1

**Collections (38):** `_3f2db519_1d10_447a_9c51_ed52a3fa1790`, `_06dc1637_2490_4a69_847d_e7f1ae4bc89f`, … (UUID-prefixed)

**What's exposed:** UUID-named collections imply auto-generated tenant IDs in a multi-tenant SaaS. The leading underscore is a Milvus naming convention, collections starting with a number must be prefixed. 38 tenants visible. Schema `describe` returned empty for all of these, suggesting RBAC may partially apply (list visible, describe gated), but the tenant count is itself competitive intelligence.

---

### 7. Other Notable Exposures (one-line)

| Host | Highlight |
|---|---|
| `144.202.73.63` | 11 collections including `meeting_memory`, `voice_registry`, `faq`, `cities_ingest`, `information_faq_collect`, voice + meeting AI agent stack |
| `45.63.7.3` | `investigator`, `organization`, `study`, `documents`, `fq`, research/investigation platform |
| `188.166.229.136` | `records`, `functions`, `knowledge_base`, generic LLM tool-use stack |
| `135.181.221.152` | `product_name`, `product_description`, `product_taxonomy`, ecommerce product RAG |
| `135.181.252.66` | `experience_memory`, `mem0migrations`, `all`, `all_v3`, Mem0-on-Milvus deployment |
| `165.227.8.44` | `psk_saree_finder_v3-v6`, Indian saree (garment) finder, 4 versions |
| `46.101.105.165` | `policy_chunks_v1`, policy/legal document RAG |
| `45.76.248.64` | `image_database`, `image_database_backup`, `image_database_backup_2`, image vector DB with backup co-located |
| `159.69.184.136` | `wdw_prod_hybrid`, `prod_hybrid`, production hybrid indices |
| `167.172.46.101` | `termex_ip_cosine`, IP/term-extraction cosine index |
| `65.108.226.74` | `teamboost_tasks_title`, `teamboost_tasks_description`, task management AI |
| `65.108.76.202` | `image_embeddings`, `image_embeddings_2`, duplicated image embeddings |
| `159.69.87.49` | `rostros` (faces, ES), possibly facial-recognition |
| `159.203.45.150` | `dev_cost_guard`, internal cost-guarding tool |
| `116.202.108.128` | `skynet_test`, interesting name choice for production |
| `168.119.102.222` | `legal_acts_e5_large`, legal corpus with E5-large embeddings |
| `165.227.182.149` | `documents_chunks`, generic chunked document RAG |
| `45.76.114.69` | `Vector_index_<uuid>_Node`, LlamaIndex-style indexed nodes |
| `168.119.141.25` | `screenshots`, likely OCR'd UI screenshots |
| `168.119.229.126` | `llamacollection`, LlamaIndex |
| `95.179.181.104` | `image_database_gpu/pq/cpu/_`, image embeddings with index variants (GPU vs CPU vs PQ) |

---

## Root Cause: Default-Off RBAC

Milvus ships with RBAC disabled by default. Enabling it requires:

```yaml
# milvus.yaml
common:
  security:
    authorizationEnabled: true

# Then create root user + permissions via:
# milvus_cli> create user -u root -p <password>
# milvus_cli> create role -r ro_role
# milvus_cli> grant role ro_role -u <user>
```

The `authorizationEnabled: true` flag must be explicitly set. The Milvus quickstart Docker Compose and the helm chart defaults both leave it false. None of the 33 confirmed instances had it enabled, `/v2/vectordb/collections/list` returned `code: 0` (success) with no token requirement.

The Milvus 2.4 REST API documentation does describe the auth header (`Authorization: Bearer <token>`), but the security-disabled default means the field is ignored when RBAC is off. This is the same pattern as Qdrant and ChromaDB.

---

## Cross-Survey Pattern: Vector DB Auth Posture

| Platform | Sample | Unauthenticated | Default | Survey |
|---|---|---|---|---|
| Qdrant | 61 | 100% | auth-off | [qdrant-cloud-survey-2026-05.md](qdrant-cloud-survey-2026-05.md) |
| ChromaDB | 48 | 100% | auth-off | [chromadb-cloud-survey-2026-05.md](chromadb-cloud-survey-2026-05.md) |
| **Milvus** | **33** | **100%** | **RBAC-off** | **this file** |
| Elasticsearch | 42 | mixed | auth-off in 7.x | [elasticsearch-cloud-survey-2026-05.md](elasticsearch-cloud-survey-2026-05.md) |
| Flowise | 43 | 0% | auth-on (since CVE-2024-36420) | [flowise-cloud-survey-2026-05.md](flowise-cloud-survey-2026-05.md) |
| n8n | 1,006 | 0% | auth-on (since v0.166.0) | [n8n-cloud-survey-2026-05.md](n8n-cloud-survey-2026-05.md) |
| Jupyter | 18 (univ) | 0% | PAM/LDAP standard | [jupyter-survey-2026-05.md](jupyter-survey-2026-05.md) |

**Observation:** Three independent vector DB vendors (Qdrant, ChromaDB, Milvus), three independent codebases, three independent leadership teams, and all three have the same default. The pattern is not a per-vendor oversight; it is the cultural inheritance of "vector DB is local development infrastructure" that has not yet adapted to "vector DB is production multi-tenant data layer."

---

## Remediation

```yaml
# milvus.yaml
common:
  security:
    authorizationEnabled: true
```

After enabling, create a root password, then non-root users with read-only or read-write roles per application. Firewall port 19530 to the application backend. If Pulsar/etcd metadata stores are on adjacent ports (9091, 9000, 2379), firewall those too, Milvus is a multi-component system; closing the proxy port alone leaves the metadata accessible.

---

## NuClide Pipeline Artifacts

| Stage | Tool | Output |
|---|---|---|
| Discovery | masscan + custom REST probe | `/tmp/milvus-confirmed.jsonl` (33 instances) |
| Schema enumeration | custom REST `describe` probe | `/tmp/milvus-deep.jsonl` (per-collection schemas) |
| Findings ledger | [VisorLog](https://github.com/Nicholas-Kloster/VisorLog) | To be ingested into `data/nuclide.db` |
| Compliance scoring | [VisorScuba](https://github.com/Nicholas-Kloster/VisorScuba) | Will fail AI.C1 (unauth-baseline) for all 33 |
| Adversarial corpus | [VisorCorpus](https://github.com/Nicholas-Kloster/VisorCorpus) | Existing chromadb adversarial corpus applies, categories `kb_exfiltration`, `tenant_cross_leak`, `prompt_injection` transfer |

---

## References

- Milvus authentication: https://milvus.io/docs/authenticate.md
- v2 REST API: https://milvus.io/api-reference/restful/v2.4.x/About.md
- RBAC enable: https://milvus.io/docs/rbac.md
- Cross-survey index: [index.md](index.md)
