# Commercial AI Infrastructure Exposures

_NuClide Research — ongoing · Updated 2026-05-03_

Commercial / SaaS Ollama and AI infrastructure exposures discovered during OSINT sweeps. These differ from university and research-network exposures in that the operators are commercial entities with paying customers and PII pipelines.

---

## Confirmed Findings

| File | Operator | Country | Severity | Key Finding |
|------|----------|---------|----------|-------------|
| [FR-emails-pro-rdv-bot.md](FR-emails-pro-rdv-bot.md) | emails-pro.fr (hosted on Romanian ICI IP space) | France / Romania | CRITICAL | Production French commercial appointment-booking SaaS — full system prompt + PII collection schema + function-call format exposed |
| [TR-sanctionscanner-aml-kyc.md](TR-sanctionscanner-aml-kyc.md) | sanctionscanner.com (168.119.90.62, Hetzner DE) | Turkey / Germany | CRITICAL | AML/KYC compliance SaaS — 79M KYB records + 6.2M individual sanctions list entries unauth; active ransom compromise; disclosed 2026-05-03 |
| [VN-watzis-ai-pii-memory.md](VN-watzis-ai-pii-memory.md) | Watzis / Calmio AI assistant (149.28.77.155, Vultr) | Vietnam | HIGH | Vietnamese AI assistant — Mem0 long-term memory store unauth; citizen ID card + VND wallet + student PII in plaintext; multiple users confirmed |
| [multi-pingu-trading-ai.md](multi-pingu-trading-ai.md) | Unknown operator (45.76.20.46, Vultr) | Unknown | HIGH | Pingu crypto trading AI + Nova molecular optimization — 25 Qdrant collections unauth; live trade PnL, full LLM reasoning traces, competition leaderboard |
| [multi-legal-compliance-investigation.md](multi-legal-compliance-investigation.md) | Unknown operator (167.172.120.218, DigitalOcean) | Unknown | CRITICAL (if populated) | Legal/compliance investigation platform schema exposed unauth — investigation_data, case_drafts, attachments collections; empty at probe time; flagged for re-probe |
| [multi-auto-fi-sales-training.md](multi-auto-fi-sales-training.md) | Unknown operator (104.131.60.234, DigitalOcean) | Unknown (Sean McNally methodology) | HIGH | Auto F&I sales training RAG — real customer dialogues with names + vehicles + dollar figures, Sean McNally methodology IP, 1,608 docs unauth ChromaDB |
| [multi-crypto-agent-user-memory.md](multi-crypto-agent-user-memory.md) | Unknown operator (159.203.117.193, DigitalOcean) | Spanish-language LatAm/Spain | HIGH | Crypto investment agent — per-user financial profiles ($50K targets, exchange affinity, asset allocation) in user_memory_<id> collections; 12 collections, 15.9K docs unauth |
| [multi-holamoda-multitenant.md](multi-holamoda-multitenant.md) | HolaModa + Delta701 (46.101.118.246, DigitalOcean) | Unknown (Mexican/Spanish?) | CRITICAL | Multi-tenant fashion retail RAG — 2 tenants + dev/prod co-located on one ChromaDB; 1.53M docs across 7 collections unauth; Vertex AI text-embedding-gecko |
| [multi-personal-diary-corpus.md](multi-personal-diary-corpus.md) | Unknown Prisma SaaS (188.166.71.44, DigitalOcean) | Belgium/France inferred | HIGH | Multi-tenant document SaaS — Prisma CUID per-user collections expose personal alcohol-cessation diary (GDPR Art. 9), theater scripts with author emails + Belgian phones, public-domain texts |
| [elasticsearch-cloud-survey-2026-05.md](elasticsearch-cloud-survey-2026-05.md) | sanctionscanner.com (168.119.90.62, Hetzner DE) | Turkey / Germany | CRITICAL | AML/KYC compliance SaaS — 79M KYB records + 6.2M individual sanctions list entries unauth; active ransom compromise; disclosed 2026-05-03 |
| [qdrant-cloud-survey-2026-05.md](qdrant-cloud-survey-2026-05.md) | Multiple operators | Various | HIGH | 61/61 Qdrant instances unauth across DO/Hetzner/Vultr — crypto trading AI, Vietnamese PII in agent memory, internal SOPs, legal compliance platform |

---

## Cross-Provider Surveys

Aggregate auth-posture studies across cloud-hosting providers (DigitalOcean, Hetzner, Vultr, etc.) for specific platform classes.

| File | Platform | Sample | Result |
|------|----------|--------|--------|
| [flowise-cloud-survey-2026-05.md](flowise-cloud-survey-2026-05.md) | Flowise | 43 instances across DO/Hetzner/Vultr | 0 unauthenticated — operator hygiene post-CVE-2024-36420 has improved on cloud platforms |
| [n8n-cloud-survey-2026-05.md](n8n-cloud-survey-2026-05.md) | n8n | 1,006 instances across DO/Hetzner/Vultr | 0 unauthenticated — mandatory auth since v0.166.0 fully adopted on cloud platforms |
| [jupyter-survey-2026-05.md](jupyter-survey-2026-05.md) | Jupyter / JupyterHub | 18 confirmed university instances (Berkeley, ETH, Cambridge, NTU, INHA, NCCU) | 0 unauthenticated — JupyterHub PAM/LDAP auth standard across all surveyed institutions |
| [qdrant-cloud-survey-2026-05.md](qdrant-cloud-survey-2026-05.md) | Qdrant | 61 instances across DO/Hetzner/Vultr | 100% unauthenticated — ships auth-off by default; 48/61 contain live data |
| [chromadb-cloud-survey-2026-05.md](chromadb-cloud-survey-2026-05.md) | ChromaDB | 48 instances across DO/Hetzner/Vultr | 100% unauthenticated — ships auth-off by default; 22/48 populated; **2.67M documents** total exposed |
| [elasticsearch-cloud-survey-2026-05.md](elasticsearch-cloud-survey-2026-05.md) | Elasticsearch / OpenSearch | 42 instances across DO/Hetzner/Vultr | Mixed — ~18 ransomed/wiped, ~16 live production data; ES 7.x default-no-auth still common |

---

## Why Separate from Universities

Commercial exposures carry distinct risk profiles:
- **Paying customers** — direct financial / contractual liability when PII is exposed
- **Live PII pipelines** — system prompts often reveal the exact data-collection schema
- **Competitive intel** — proprietary business logic in plain text
- **Cross-border attribution** — host country (e.g., Romania) often differs from operator country (e.g., France), complicating regulatory disclosure
