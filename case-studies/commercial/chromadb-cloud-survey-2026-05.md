# ChromaDB on Public Cloud: Auth Posture Survey

_NuClide Research · 2026-05-03_

---

## Summary

Sweep of 1.83M IPs across 28 cloud-provider /16 ranges (DigitalOcean, Hetzner, Vultr) on port 8000 → 22,765 masscan hits → **48 confirmed ChromaDB instances** via `/api/v{1,2}/heartbeat` → `{"nanosecond heartbeat": <int>}` fingerprint. **All 48 unauthenticated.** 22 of 48 contain non-empty collections.

Aggregate document exposure across the 22 populated instances: **2,677,724 documents**, production RAG knowledge bases, agent memory stores, multi-tenant SaaS document corpora, sales-call transcripts with PII, live restaurant phone reservations, internal architecture standards, pediatric clinical assessment templates, F&I auto-finance dialogues with customer names + dollar figures.

This mirrors the Qdrant result: ChromaDB ships with auth disabled by default and operators who deploy it directly to the public internet on its default port retain that default. Port 8000 has heavy non-ChromaDB traffic (Django, FastAPI, uvicorn, Plex, MinIO console), so the `nanosecond heartbeat` body match is the critical fingerprint, it cuts 22,765 candidates down to 48 actual ChromaDBs.

---

## Methodology

```
masscan -iL <28 cloud /16 CIDRs> -p 8000 --rate 10000
  → 22,765 masscan hits on :8000

chroma-probe.py (200-thread heartbeat fingerprint)
  GET /api/v2/heartbeat  (or v1 fallback)
  match body for "nanosecond heartbeat"
  → 48 confirmed ChromaDB instances

chroma-deep.py (count + 3-doc sample per collection)
  v2 path: /api/v2/tenants/default_tenant/databases/default_database/collections/<uuid>/count
  v2 path: /api/v2/tenants/default_tenant/databases/default_database/collections/<uuid>/get
  → per-collection document counts + content samples
```

---

## Findings Summary

| Metric | Value |
|---|---|
| Cloud /16 ranges scanned | 28 (DO/Hetzner/Vultr) |
| Masscan hits on :8000 | 22,765 |
| ChromaDB heartbeat confirmed | **48** |
| Unauthenticated | **48 (100%)** |
| With non-empty collections | 22 |
| Empty / fresh installs | 26 |
| **Total documents exposed** | **2,677,724** |

### API version split

| Version family | Count | Notes |
|---|---|---|
| v2 (1.0.x, 0.6.x) | 41 | Current default; collections accessed by UUID, not name |
| v1 (0.3.x – 0.5.x) | 7 | Legacy; deprecated path still served by older deployments |

### Hosting provider split (by /16 prefix)

| Provider | Confirmed | Populated |
|---|---|---|
| DigitalOcean | 24 | 11 |
| Hetzner | 14 | 8 |
| Vultr | 10 | 3 |

---

## High-Value Exposures

### 1. Auto F&I Sales Training: Real Customer Dialogues with PII

**Host:** `104.131.60.234:8000` (DigitalOcean) · v2 · ChromaDB 1.0.0

**Collections (3, all populated):**

| Collection | Docs |
|---|---|
| `sarah_training_data` | 1,538 |
| `sarah_deal_history` | 34 |
| `sean_mcnally_methodology` | 36 |

**What's exposed:**

Real auto-dealership F&I (Finance & Insurance) sales transcripts used as agent training data. Sample from `sarah_deal_history`:

```
F&I Manager: Hi Mrs. Patterson, I'm Sean and I'll be helping you finalize
everything today. Congratulations on the new Highlander!
Customer: Thanks, I'm excited about it.
F&I Manager: That's great! So tell me, what made you choose the Highlander?
Customer: We have three kids and needed something reliable for the family.
```

`sarah_training_data` contains role-play transcripts:

```
FM: Now, for the backend products. You have a payment of $450, but if
you want the warranty and GAP, it goes up to $520.
Customer: Whoa, $70 more? That's way too much.
```

`sean_mcnally_methodology` exposes proprietary sales methodology authored by Sean McNally (real-name F&I sales consultant):

> Passionate Consulting Core Philosophy by Sean McNally: Passion creates connection, and connection creates trust. That trust is the bedrock of every great sale and every meaningful client relationship…

**Risk:** Customer first/last names + vehicle purchases + dollar figures from real deals. Proprietary sales methodology IP exposed. If Mrs. Patterson is a real customer (vs. role-play), the operator has a privacy breach. Even if the dialogues are training-only, the methodology IP belongs to a paying instructor and is worth competitive intelligence to a rival F&I training vendor.

---

### 2. Crypto Investment Agent + Per-User Financial Memory

**Host:** `159.203.117.193:8000` (DigitalOcean) · v2 · ChromaDB 1.0.0

**Collections (12, 9 populated, 15,936 total docs):**

| Collection | Docs | Type |
|---|---|---|
| `crypto_tokens_full` | 15,560 | Token database |
| `crypto_tokens` | 100 | Subset |
| `cgdoc_endpoints_v1` | 73 | CoinGecko API endpoint docs |
| `cgdoc_params_v1` | 57 | CoinGecko API params |
| `cg_vs_currencies` | 126 | Quote currencies |
| `cg_networks` | 0 | (empty) |
| `cg_network_dexes` | 0 | (empty) |
| `user_memory_1` | 8 | **Per-user agent memory** |
| `user_memory_4` | 1 | **Per-user agent memory** |
| `user_memory_7` | 7 | **Per-user agent memory** |
| `user_memory_38` | 0 | (empty) |
| `test_chroma_collection` | 4 | Dev scratch |

**What's exposed:**

The `user_memory_*` collections contain Spanish-language agent memory entries with explicit financial intent and account preferences:

```
user_memory_4: "El objetivo del usuario es invertir $50,000 en crypto con
la estrategia de 40% en Bitcoin, 30% en Ethereum, 20% en Solana y 10% en
stablecoins."
```

Translation: *"The user's goal is to invest $50,000 in crypto with the strategy of 40% Bitcoin, 30% Ethereum, 20% Solana, and 10% stablecoins."*

```
user_memory_1: "El exchange preferido del usuario es Kraken"
user_memory_7: "La cripto favorita del usuario es Ethereum"
```

**Risk:** Each `user_memory_<id>` is a separate ChromaDB collection per user, the integer suffixes (1, 4, 7, 38) imply user IDs in a sequential schema, allowing enumeration of all users. Per-user financial profile with target investment amounts, exchange preferences, and asset allocation strategy is direct PII under most jurisdictions. An attacker with this data has a target list of crypto investors with self-disclosed five-figure target capital.

---

### 3. Romanian Legislation Corpus: 1M Documents

**Host:** `45.55.79.137:8000` (DigitalOcean) · v2 · ChromaDB 1.0.0

**Collection:** `romanian_legislation`, **1,024,794 documents**

Sample:

```
[OG nr. 83/1999 - ORDONANŢĂ DE URGENŢĂ nr. 83 din 8 iunie 1999 (republicată)(actualizată)]
Articolul 1
(1) Imobilele care au aparţinut comunităţilor minorităţilor naţionale din
România şi care au fost preluate în mod abuziv... în perioada 6 septembrie
1940 - 22 decembrie 1989, se restituie...
```

Translation: *"Real estate that belonged to national minority communities in Romania and was abusively taken… between September 6, 1940, December 22, 1989, shall be restituted…"*

**Risk:** The base content (Romanian government ordinances) is public-record law, but the curation, embedding, and chunking represent significant ingestion engineering. If this is a Romanian law firm's commercial RAG product, the embedded corpus is a competitive trade secret. The per-document metadata (not sampled here but routinely present in RAG ingestion) often includes proprietary annotations, classifications, or internal notes that wouldn't exist in public sources.

---

### 4. HolaModa: Multi-Tenant Fashion Retail with Dev/Prod Co-Located

**Host:** `46.101.118.246:8000` (DigitalOcean) · v2 · ChromaDB 0.6.3

**Collections (7, all populated, 1,533,095 total docs):**

| Collection | Docs |
|---|---|
| `holamoda_google_multi_002` | 736,711 |
| `holamoda_google` | 652,435 |
| `chroma_delta701_textembedding-gecko` | 65,324 |
| `chroma_delta701dev_textembedding-gecko` | 64,658 |
| `chroma_hmdev_textembedding-gecko` | 9,500 |
| `chroma_demorep_textembedding-gecko` | 2,217 |
| `holamoda_google_005` | 2,250 |

**What's exposed:**

The naming pattern indicates **dev and production environments share the same ChromaDB instance**, with no environment isolation: `chroma_hmdev` (HolaModa dev) and `holamoda_google` (HolaModa prod) co-located alongside `chroma_delta701dev` and `chroma_delta701` (a second tenant's dev/prod). The `_textembedding-gecko` suffix indicates Google Cloud Vertex AI embeddings being indexed.

**Risk:** Dev/prod isolation gap is the headline. A second tenant ("delta701") shares the same ChromaDB host as HolaModa, multi-tenant SaaS without database-level tenant isolation. If either tenant's frontend has an IDOR or prompt-injection bypass that lets a query name an arbitrary collection, all tenants leak. Aggregate exposure: 1.5M+ embedded documents.

---

### 5. Restaurant Phone Reservations: Live Customer Bookings

**Host:** `65.109.100.94:8000` (Hetzner) · v2 · ChromaDB 1.0.0

**Collections (3, all populated):**

| Collection | Docs |
|---|---|
| `phone-conversations` | 260 |
| `restaurant-knowledge` | 8 |
| `test-embeddings` | 1 |

**Sample from `phone-conversations`:**

```
Reserva número 1001. Cliente: Test User 3. Teléfono: 34600000003.
Fecha: 2026-03-20. Hora: 16:00. Número de personas: 4. Tipo de arroz:
Paella Valenciana. Raciones de arroz: 2.
```

`+34` prefix = Spanish phone number format. Despite the "Test User" naming the phone and reservation IDs are populated as if real-world records.

**Risk:** Even if the sampled record is test data, a `phone-conversations` collection at this scale (260 records) on a production-style instance suggests real reservation data is being captured by a phone-bot agent and embedded. Voice-to-vector reservation pipelines were a 2025 startup wave; this looks like one of those operators with no auth in front of the vector store.

---

### 6. Multi-Tenant Personal Diary + Theater Scripts + Philosophy

**Host:** `188.166.71.44:8000` (DigitalOcean) · v1 · ChromaDB 0.4.13

**Collections (3, CUID-style tenant IDs):**

| Collection | Docs | Content |
|---|---|---|
| `corpus_cln4mq3w4000rka2lyt792a32` | 1,487 | **Personal diary (alcohol cessation log, French)** |
| `corpus_cln2yf6py0001mp2kk7t63amf` | 68 | Theater scripts with author names + emails + Belgian phone numbers |
| `corpus_cln2zh86b0001p82knhrr7hlk` | 643 | Nietzsche, *Beyond Good and Evil* (French translation, 1913 ed.) |

**Sample from `cln4mq3w4000rka2lyt792a32` (personal diary):**

```
18/04/22: arrêt de l'alcool.
18/06/22: bu Orval 3° (édition spéciale à l'Abbaye)
```

Translation: *"04/18/22: stopped drinking alcohol. 06/18/22: drank Orval 3° (special abbey edition)."*

**Sample from `cln2yf6py0001mp2kk7t63amf` (theater script):**

```
LES FORMES VIDES - LE THÉÂTRE DE LA VACUITÉ
Sébastien Lacomblez
sebastien.lacomblez@gmail.com
0497/75.31.02
Emmanuel Pire
piremmanuel@gmail.com
0486/77.69.87
```

Real names + email addresses + Belgian mobile numbers (0497, 0486 prefixes).

**Risk:** The CUID naming pattern (`cln*`) is a Prisma/Hasura convention indicating an auto-generated tenant ID per user. This is a multi-tenant SaaS where each user's collection is named by their generated user ID, and the contents range from highly personal (alcohol cessation log) to identifying (real names + emails + phones in creative IP) to public-domain (Nietzsche). The alcohol cessation log in particular is GDPR Article 9 special category data (health-related).

---

### 7. School Parent Portal RAG (ParentLocker)

**Host:** `104.131.49.48:8000` (DigitalOcean) · v2 · ChromaDB 1.0.0

**Collection:** `parentlocker_rag_poc`, 1,264 docs

**Sample:**

> # Attendance Numbers Look Incorrect on My Report Card #
> If attendance totals on your report cards look unusually high or don't seem accurate, the issue is almost always related to your **term dates**...

ParentLocker is a real K-12 student information system. The collection name suggests this is a vendor's PoC / demo for adding RAG-backed support, but the doc count (1,264) is well past PoC, it's loaded with operator support documentation. Risk class: vendor-PoC environments routinely contain live customer data after demos; the "PoC" naming creates false sense of safety while the data is real.

---

### 8. Pediatric Speech-Language Therapy Templates (Spanish)

**Host:** `104.236.20.253:8000` (DigitalOcean) · v2 · ChromaDB 0.6.3

**Collection:** `jcj_playbooks_v1`, 27 docs

**Sample:**

```
TOPIC_NUCLEO: ['Lenguaje/Pronunciacion']
SUBHABILIDAD: Articulación de la /s/
SEÑAL_OBSERVABLE: No pronuncia la s | cuando una palabra tiene s no realiza el fonema...
EDAD: 2–5
HIPOTESIS_FUNCIONAL: Dificultad en la alineación y cierre de la mordida...
```

Structured clinical assessment templates for child speech-language therapy (ages 2–5). Likely a LatAm clinical-practice operator. While not tied to identified patients in the sample, the template structure is professional clinical IP and the deployment posture (unauth, public internet) signals that any patient-facing usage of the same instance would be similarly exposed.

---

### 9. Internal Architecture Standards

**Host:** `135.181.177.80:8000` (Hetzner) · v2 · ChromaDB 1.0.0

**Collections:**

| Collection | Docs |
|---|---|
| `genesis_blueprint` | 10 |
| `sovereign_memory` | 0 |

**Sample from `genesis_blueprint`:**

```
[PILLAR]: communication_spine
[STANDARD]: NATS JetStream & NATS KV
[CONSTRAINT]: Synchronous HTTP/REST between internal microservices is
STRICTLY FORBIDDEN. All inter-component communication must be event-driven
pub/sub.
[PARENT]: baseplate.universal.v1
[VERSION]: 1.2.2
```

**Risk:** Internal architecture decision records being embedded into a RAG so that an LLM coding assistant can enforce them. Exposure reveals (a) the operator's internal platform name (`baseplate.universal.v1`), (b) the explicit architectural commitment to NATS over HTTP/REST, (c) versioning of internal standards. For a competitor or attacker doing reconnaissance on the org's tech stack, this is a primary source.

---

### 10. Other Notable Exposures (one-line)

| Host | Highlight |
|---|---|
| `45.63.66.121` | Empty `demo` collection, fresh install |
| `65.108.106.126` | `hub-prescribed` (1,906), Nam Le literary text *"Love and Honour and Pity and Pride and Compassion and Sacrifice"* + `sta_project` (4,438) |
| `116.203.108.41` | German Federal Ministry of Finance (BMF) monthly report content, 7,710 docs |
| `135.181.22.247` | Recruiting RAG, `candidate_embeddings` (8) + `job_embeddings` (2) |
| `135.181.6.58` | Russian VPN consumer-support content (MegaFon, T-Mobile, Beeline references) |
| `138.68.189.152` | `userprompts` (5), captured user prompts from a developer-LLM tool, including ERP/Odoo integration requests |
| `138.68.83.9` | `lessons` (566), Arabic language-learning content |
| `144.202.20.161` | Security recon tooling, `scans` (59) with whatweb output for cytex.io |
| `144.202.99.216` | `news-bge` (27,102), news article RAG with BGE embeddings |
| `157.90.79.91` | Multi-tenant Hungarian restaurant menus, `restaurant_1837/1839/1799_vectors` |
| `167.172.70.7` | Argentine university foundation (Universidad Nacional del Sur) statutes, Qwen3-Embedding-0.6B |
| `167.71.197.197` | Russian YouTube transcripts (`transcripts`, 157) |
| `167.71.240.98` | Spanish auto-financing legal docs |
| `188.166.241.9` | Asian/SE Asian public company directory, 22,512 records |
| `206.189.167.254` | Saudi agentic-AI vendor marketing copy (`Hadir AI`) |
| `65.109.13.140` / `65.109.165.220` | SEO keyword RAGs (30,903 + 805 docs) |

---

## Root Cause: Default-Off Authentication

ChromaDB ships with authentication disabled by default. Enabling it requires server-side configuration:

```yaml
# config.yaml (or environment)
CHROMA_SERVER_AUTHN_PROVIDER: chromadb.auth.token_authn.TokenAuthenticationServerProvider
CHROMA_SERVER_AUTHN_CREDENTIALS: <strong-token>
CHROMA_AUTH_TOKEN_TRANSPORT_HEADER: X-Chroma-Token
```

Or for v1.0+:

```bash
chroma run --host 0.0.0.0 --port 8000 \
  --auth-provider chromadb.auth.token \
  --auth-credentials <strong-token>
```

None of the 48 confirmed instances had this configured. All were directly internet-reachable on port 8000 with no token requirement, `/api/v2/heartbeat`, `/api/v2/version`, `/api/v2/tenants/default_tenant/databases/default_database/collections`, and per-collection `/get` all returned 200 with no credentials.

The ChromaDB documentation does mention authentication, but the default configuration files and most "deploy ChromaDB on a VPS" tutorials skip it, the operator has to opt in explicitly. Compare with Flowise (auth made mandatory by upstream after CVE-2024-36420, 0/43 unauth in our sweep) and n8n (mandatory auth since v0.166.0, 0/1006 unauth). Vector DBs as a category have not made the same shift; both Qdrant (0/61 had auth) and ChromaDB (0/48 had auth) ship and stay open.

---

## Cross-Survey Pattern: Vector DB Auth Posture

| Platform | Sample | Unauthenticated | Default | Survey |
|---|---|---|---|---|
| Qdrant | 61 | 100% | auth-off | [qdrant-cloud-survey-2026-05.md](qdrant-cloud-survey-2026-05.md) |
| ChromaDB | 48 | 100% | auth-off | this file |
| Elasticsearch | 42 | mixed (~40% live unauth) | auth-off in 7.x | [elasticsearch-cloud-survey-2026-05.md](elasticsearch-cloud-survey-2026-05.md) |
| Flowise | 43 | 0% | auth-on (since CVE-2024-36420) | [flowise-cloud-survey-2026-05.md](flowise-cloud-survey-2026-05.md) |
| n8n | 1,006 | 0% | auth-on (since v0.166.0) | [n8n-cloud-survey-2026-05.md](n8n-cloud-survey-2026-05.md) |
| Jupyter | 18 (univ) | 0% | PAM/LDAP standard | [jupyter-survey-2026-05.md](jupyter-survey-2026-05.md) |

**Summary:** Orchestration / workflow tools have moved to auth-on by default. Vector databases, the data layer of the modern RAG stack, have not. Operators inheriting a "Chroma is ephemeral / for local dev" mental model deploy them with the same posture on production VPSes, and the data is real production data.

---

## Disclosure Posture

48 instances, 22 populated, multiple jurisdictions (US, EU, LatAm, Asia, MENA, Russia), most with no immediate operator attribution from the IP alone. NuClide is not initiating individual disclosure to all 48, that is well past triage capacity. The high-value individual writeups (where operator identity can be inferred from collection content) will receive targeted disclosure where possible. Operators reading this who recognize their instance: enable token auth and firewall port 8000.

---

## Methodology Validation

The `nanosecond heartbeat` body match is the necessary and sufficient ChromaDB fingerprint for port-8000 sweeps. Without it, the prober gets ~22,000 false positives from Django, FastAPI, uvicorn, Plex, MinIO console, and other port-8000 occupants. With it, signal-to-noise jumps to 48/22765 = 0.21%, but every one of those 48 is a real ChromaDB and 100% of those real ChromaDBs are unauthenticated.

---

## NuClide Pipeline Artifacts

The 48 confirmed instances were processed end-to-end through the NuClide AI/LLM security toolchain:

| Stage | Tool | Output |
|---|---|---|
| Discovery | masscan + custom heartbeat probe | `/tmp/chroma-confirmed.jsonl` (48 instances) |
| Enumeration | custom v2 deep-prober | `/tmp/chroma-deep.jsonl` (collections + counts + samples) |
| Findings ledger | [VisorLog](https://github.com/Nicholas-Kloster/VisorLog) | 48 events ingested into `data/nuclide.db` (commercial sector, severity-tiered) |
| Compliance scoring | [VisorScuba](https://github.com/Nicholas-Kloster/VisorScuba) | All 48 score 0/10, 100% AI.C1 (unauth-baseline) violations. Report: `data/scuba-report-2026-05-03.html` |
| Adversarial corpus | [VisorCorpus](https://github.com/Nicholas-Kloster/VisorCorpus) | 137 adversarial test cases generated for downstream RAG/LLM red-team, `data/visorcorpus-chromadb-rag-adversarial-2026-05.json`. Categories: kb_exfiltration (18), prompt_injection (16), tenant_cross_leak (15), system_prompt (15), jailbreak (15), config_secrets (13), infra_discovery (15) |

This is the discovery → ledger → score → adversarial-corpus pipeline that closes the loop: each finding is logged with normalized severity, scored against the NuClide AI Security Baseline (OPA/Rego), and paired with an adversarial corpus an operator can run against their own frontend to verify the defensive posture *upstream* of the exposed vector store.

---

## References

- ChromaDB authentication: https://docs.trychroma.com/production/administration/auth
- v1 → v2 API migration: https://docs.trychroma.com/docs/run-chroma/client-server (default tenant/database structure)
- Cross-survey index: [../commercial/index.md](index.md)
- NuClide pipeline: [VisorPlus](https://github.com/Nicholas-Kloster/VisorPlus) (orchestrator), [VisorSD](https://github.com/Nicholas-Kloster/VisorSD), [VisorLog](https://github.com/Nicholas-Kloster/VisorLog), [VisorScuba](https://github.com/Nicholas-Kloster/VisorScuba), [VisorCorpus](https://github.com/Nicholas-Kloster/VisorCorpus)
