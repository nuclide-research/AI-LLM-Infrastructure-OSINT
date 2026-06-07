---
type: survey
---

# Mem0 Agent Long-Term Memory: Cross-Survey of Exposed Instances

_NuClide Research · 2026-05-03_

---

## Summary

Mem0 ([github.com/mem0ai/mem0](https://github.com/mem0ai/mem0)) is a Python framework that turns any vector store into agent long-term memory: structured per-user JSON payloads with `user_id`, `data`, `hash`, `created_at` fields, embedded and stored alongside the vector. The framework itself is not network-exposed, but its backend (Qdrant or ChromaDB) is, and the resulting collections, `mem0_memories`, `mem0migrations`, `<custom>_memory`, `user_memory_<id>`, `<persona>_longterm_memory`, are recognizable across operator deployments.

<!-- ksat-tag:auto-generated:start -->
## DCWF KSAT coverage

Auto-derived from DCWF AI work-role rule files (`ksat-tag`).

- **672 (AI Test & Evaluation Specialist):** K7003, K7004, K7044, S7068, S7070, S7075, T5904
- **733 (AI Risk & Ethics Specialist):** K7040, K7051, S7067, S7069, T5854, T5868, T5893
- **overlap (Common AI KSATs (all 5 roles)):** K108, K1157, K1158, K22, K6311, K6935, K7003

<!-- ksat-tag:auto-generated:end -->

Cross-referencing the prior Qdrant cloud sweep (61 instances) and ChromaDB cloud sweep (48 instances) for Mem0-typed collections surfaces **8 confirmed Mem0-class instances**, all unauthenticated. Three contain extensive personal/professional history of identifiable individuals, direct CRITICAL findings independent of the underlying vector-DB-vendor classification.

---

## Methodology

```
For each instance from /tmp/qdrant-deep.json + /tmp/chroma-confirmed.jsonl:
  match collection name against:
    mem0|mem0_memories|mem0migrations|user_memory_*
    *_memory (claude_memory, sovereign_memory, etc.)
    *_longterm_memory|*_long_term_memory
    my_journal|*_journal
  → 8 instances identified

For 3 unique-identity instances not previously case-studied:
  GET /collections/<name> → vectors_count + points_count
  POST /collections/<name>/points/scroll {limit:3, with_payload:true}
  → sample 3 records to classify content sensitivity
```

The Mem0 schema is distinctive enough that the first sampled record is sufficient to confirm classification:

```json
{
  "user_id": "<id>",
  "data": "<plaintext memory content>",
  "hash": "<md5/sha-style hash>",
  "created_at": "<ISO-8601 timestamp>"
}
```

Variants observed: `category` field for grouping, `role` + `conversation_index` + `original_text` for chat-replay-style storage.

---

## Confirmed Mem0-Class Instances

### Backend: Qdrant (port 6333)

| Host | Hoster | Memory collections | Total points | Status |
|---|---|---|---|---|
| `45.76.20.46` | Vultr | `pingu_*` (10), `mol_*` (8), `mem0_memories`, `mem0migrations` | (multi-collection) | Documented in [multi-pingu-trading-ai.md](multi-pingu-trading-ai.md) |
| `149.28.77.155` | Vultr | `watzis_longterm_memory`, `hybrid_watzis_longterm_memory`, `longterm_memory`, `working_memory`, `file_context`, `watzis_file_context`, `mem0migrations` | (multi-collection) | Documented in [VN-watzis-ai-pii-memory.md](VN-watzis-ai-pii-memory.md) |
| `104.131.189.88` | DigitalOcean | `openclaw_memories`, `mem0migrations` | 0 | Empty / fresh install |
| `206.189.97.116` | DigitalOcean | `mem0`, `mem0migrations` | **8,984** | **NEW, see F1 below** |
| `65.109.11.40` | Hetzner | `claude_memory`, `mem0migrations` | **424** | **NEW, see F2 below** |
| `188.166.208.148` | DigitalOcean | `my_journal`, `mem0migrations` | **1,199** | **NEW, see F3 below** |

### Backend: ChromaDB (port 8000)

| Host | Hoster | Memory collections | Status |
|---|---|---|---|
| `135.181.177.80` | Hetzner | `sovereign_memory`, `genesis_blueprint` | Documented in [chromadb-cloud-survey-2026-05.md](chromadb-cloud-survey-2026-05.md), `sovereign_memory` empty at probe |
| `159.203.117.193` | DigitalOcean | `user_memory_1`, `user_memory_4`, `user_memory_7`, `user_memory_38` | Documented in [multi-crypto-agent-user-memory.md](multi-crypto-agent-user-memory.md) |

---

## New Findings

### F1: "Friday" Personal Assistant: 8,984 Memory Points (CRITICAL)

**Host:** `206.189.97.116:6333` (DigitalOcean)
**Collection:** `mem0` (8,984 points, plus `mem0migrations`)

Sampled records show single user `friday` (likely a Marvel-themed personal assistant alias) with a multi-month log of professional interactions:

```json
{"user_id":"friday","data":"Received an update from Stefaan Arryn",
 "created_at":"2026-01-28T19:58:29.776361-08:00"}

{"user_id":"friday","data":"Had a Slack DM with Hanne Rogge regarding
 approving 2 payments in WISE on 2025-08-28",
 "created_at":"2026-01-28T21:53:23.948366-08:00"}

{"user_id":"friday","data":"User is building something and will include
 a screenshot of it.","created_at":"2026-01-30T07:11:54.523077-08:00"}
```

**Risk:** Real-name interaction history (Stefaan Arryn, Hanne Rogge, Belgian/Flemish names), specific financial-platform references (WISE, international money transfer with KYC), payment approval workflow context. 8,984 points across multi-year history is a full professional profile of the operator's working life. Spear-phishing, social engineering, or competitive intelligence harvesting all become trivial with this dataset.

The `-08:00` timezone suffix indicates Pacific Time (US West Coast operator).

---

### F2: "Claude Memory": Italian Marketing-Agency Operator with Self-Documenting Tech Stack (CRITICAL)

**Host:** `65.109.11.40:6333` (Hetzner)
**Collection:** `claude_memory` (424 points, plus `mem0migrations`)

Single user `francesco`, Italian-language. Sampled records reveal:

**Client work and pricing:**
```json
{"category":"progetto","user_id":"francesco","data":"Luca Bolognini è
 cliente potenziale NOSY (settore uscite turistiche/pesca in barca),
 con brief del 15/04/2026 via audio a Simone: sito + social FB/IG/TikTok
 + ads + riprese drone + uscite settimanali con sketch, target ~1.800
 €/mese... videomaker Giorgio Figliate 80-100 €/giornata con drone..."}
```

Translation: prospect details (Luca Bolognini, NOSY brand, fishing-tourism sector), project brief date, internal contact (Simone), pricing target (~1,800€/month), subcontractor name + day rate (Giorgio Figliate, 80-100€/day with drone). The category `progetto` and explicit "REGOLA: preventivo NON va inviato senza approvazione esplicita di Simone" (rule: quote must NOT be sent without Simone's explicit approval) reveal internal approval workflows.

**Self-documenting infrastructure:**
```json
{"category":"progetto","user_id":"francesco","data":"Il servizio mem0 è
 diretto dal server e si trova in src/services/mem0.js, salva in Qdrant
 (localhost:6333) con embedding Ollama nomic-embed-text (localhost:11434),
 utilizzato per salvare automaticamente modifiche chat AI sui siti..."}
```

Translation: *"The mem0 service is run from the server, located at src/services/mem0.js, saves to Qdrant (localhost:6333) with Ollama nomic-embed-text embeddings (localhost:11434), used to automatically save AI chat changes on sites..."*

The exposed memory describes the operator's own architecture: Mem0 → Qdrant → Ollama nomic-embed-text. The reason this Qdrant is exposed is that the operator deployed `localhost:6333` to a VPS with no firewall, exactly what the memory describes.

**Security audit results:**
```json
{"category":"progetto","user_id":"francesco","data":"Audit completo OWASP
 con 4 agenti paralleli... trovate 50 issue, tutte 50 fixate, bug critico:
 generate.js passava MODELS.smart (stringa modello) invece di 'smart'
 (routing key)... Password admin hardcodata 'admin' sostituita con
 randomBytes... IDOR reorder-batch fixato..."}
```

Translation: full OWASP audit with 4 parallel agents, 50 issues found and all fixed; the `'admin'` hardcoded admin password replaced with `randomBytes`; an IDOR in `reorder-batch` fixed.

**Risk:** This dataset describes the operator's internal codebase, security posture, client portfolio, employee names, day rates, pricing strategy, approval workflows, and self-described infrastructure. A competitor or attacker has the operator's complete working context. The "claude_memory" naming suggests the operator uses Claude as their primary assistant and stores its session memory here, meaning future sessions and historical sessions all flow through this single exposed collection.

---

### F3: "My Journal": Chinese-Language Personal Diary, 1,199 Entries (CRITICAL: GDPR Article 9 / China PIPL)

**Host:** `188.166.208.148:6333` (DigitalOcean)
**Collection:** `my_journal` (1,199 points, plus `mem0migrations`)

Schema variant: `{role, conversation_index, conversation_date, timestamp, original_text}`. Records are first-person diary entries in Mandarin Chinese, daily-cadence with timestamps spanning at least November 2025 through February 2026 (likely longer based on the 1,199-record count).

Sampled excerpt (translated):

> *"Today I actually didn't have anything to record, I think it was a meaningless day. In the morning I got up very early, woke up at 8, slept 6 hours, felt energetic. I wanted to try moving my workout to the morning, so I tried it, and discovered it doesn't work, I'm not familiar enough with the movements, I need help in the afternoon when I go with friends... I had to sleep 2 hours at noon today. The biological clock reform was a complete failure. ...In the evening, another accident, I followed Sangfor support's instructions and installed a piece of software, and the computer just wouldn't boot up. I was frantic..."*

Another entry (translated):

> *"I accepted Baidu's AI product offer, and I'm starting next Wednesday, well, the internship. I know I'll definitely run into many problems later. ...At the end of vacation, a girl asked for my WeChat, because my friend posted a Douyin of our trip, and the girl saw my photo and wanted my WeChat..."*

**Risk:** Direct personal diary of an identifiable individual (Chinese university student / early-career Baidu AI product intern). Content includes:

- Sleep schedule, fitness routine, mental-state self-reports
- Employment history (Baidu AI product offer, internship start date)
- Romantic / dating context (girl wanting WeChat, communication with senior female colleague, *"shijie"*)
- Software-troubleshooting (Sangfor SSL VPN client, computer boot failure)
- VPN usage discussion (configuring Android phone VPN to access Western internet)
- Reading lists (Nassim Taleb's *Antifragile*)

Under China's PIPL (Personal Information Protection Law), this data class includes "personal information of natural persons" subject to consent and security requirements (PIPL Article 4-5, Article 51). Under GDPR (if any EU subject is depicted in the entries), Article 9 may apply for any health-related self-disclosures within the diary.

The `my_journal` naming pattern is a private personal-AI-diary application, possibly a self-built diary chat-bot using Mem0 as backend memory. The exposure is unintentional from the operator's perspective: they likely set up Mem0 → Qdrant locally for development, then deployed to a VPS without realizing port 6333 was internet-exposed.

---

### F4: `openclaw_memories` (Empty)

**Host:** `104.131.189.88:6333` (DigitalOcean)
**Collection:** `openclaw_memories` (0 points), `mem0migrations`

Collection is provisioned but empty at probe time. Provisioning indicates an active Mem0 deployment; empty state at this moment may mean fresh install, recent wipe, or the agent hasn't yet stored memory. Re-probe warranted in 7-14 days. Severity: MEDIUM (auth gap, no current data, but provisioning intent confirmed).

---

## Cross-Cutting Risk Pattern: "Localhost-Deployed-To-Production"

All three of the new findings (F1-F3) share a common root cause distinct from the per-instance auth-disabled problem:

1. Operator builds an AI agent locally with Mem0 → Qdrant on `localhost:6333`
2. Operator deploys agent to a public VPS, copying the `localhost:6333` configuration
3. Cloud VPS has no host-level firewall by default; port 6333 binds to all interfaces
4. The agent works in production; the exposed memory database goes unnoticed

The F2 case is particularly direct: the operator's own memory contains a self-description of this exact deployment (`localhost:6333`). The configuration was correct for development, became wrong when ported to production, and the operator never re-read the architectural assumption.

This is the same root cause as the Elasticsearch + ChromaDB defaults: the framework documentation focuses on getting started, deployment guides skip the firewall step, and the local-first defaults persist.

---

## Remediation Pattern

For any Mem0 user, the checklist:

1. **Firewall the vector DB.** ChromaDB/Qdrant/PGVector, whichever Mem0 backend, must not be reachable on its default port from the public internet. Add `iptables`/`ufw` rule restricting to localhost or the application backend's CIDR.

2. **Enable the vector DB's auth primitive.** Qdrant API key, ChromaDB token, etc. Make Mem0's connection string include the credential.

3. **Use a Mem0-compatible application gateway.** Don't expose the raw vector DB even with auth, front it with a thin auth-validating proxy that only allows the Mem0-needed endpoints.

4. **Encrypt memory payloads at write-time.** Each user's memory should be encrypted with a per-user envelope key before reaching the vector DB. Embedding the plaintext for vector search is fine, but the stored payload should be ciphertext, recoverable only with the user's authenticated session.

5. **Audit the collection list.** A vector DB containing one collection per user (`user_memory_<id>`, `<persona>_longterm_memory`) leaks the user count even if individual records are protected. Consolidate into a single collection with `user_id` in metadata + `where` filter.

---

## Disclosure Posture

For the three new identifiable-individual findings (F1-F3), operator identification before outreach is required, none of them have direct domain attribution from the IP alone. Pivots:

- F1 (`206.189.97.116`): reverse-DNS, TLS cert SAN check on adjacent ports, search for "Stefaan Arryn" + "WISE" professional context (likely European based on naming)
- F2 (`65.109.11.40`): Italian operator, search for "NOSY" tourism brand or "Bolognini" + fishing tourism
- F3 (`188.166.208.148`): Chinese student writing about Baidu AI product offer; identification via the personal nature of the diary itself is not appropriate; outreach should target the platform/SaaS if a Mem0-based personal-diary chatbot product is identifiable, otherwise leave to opportunistic contact via DigitalOcean abuse channel

---

## NuClide Pipeline Artifacts

| Stage | Tool | Notes |
|---|---|---|
| Discovery | Cross-reference of prior Qdrant + ChromaDB sweeps | No new network probes; Mem0 is a content fingerprint |
| Sampling | Direct Qdrant `/points/scroll` on 3 newly-identified instances | 3 records per collection, sufficient for content classification |
| Findings ledger | VisorLog | Will be ingested into `data/nuclide.db` (Mem0 tag) |
| Compliance scoring | VisorScuba | All instances fail AI.C1 (unauth-baseline) |
| Adversarial corpus | Existing `data/visorcorpus-chromadb-rag-adversarial-2026-05.json` applies, kb_exfiltration + prompt_injection categories transfer to Mem0-based agents |

---

## References

- Mem0 framework: https://github.com/mem0ai/mem0
- Qdrant survey context: [qdrant-cloud-survey-2026-05.md](qdrant-cloud-survey-2026-05.md)
- ChromaDB survey context: [chromadb-cloud-survey-2026-05.md](chromadb-cloud-survey-2026-05.md)
- Cross-survey index: [index.md](index.md)
