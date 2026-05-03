# Commercial AI Infrastructure Exposures

_NuClide Research — ongoing · Updated 2026-05-03_

Commercial / SaaS Ollama and AI infrastructure exposures discovered during OSINT sweeps. These differ from university and research-network exposures in that the operators are commercial entities with paying customers and PII pipelines.

---

## Confirmed Findings

| File | Operator | Country | Severity | Key Finding |
|------|----------|---------|----------|-------------|
| [FR-emails-pro-rdv-bot.md](FR-emails-pro-rdv-bot.md) | emails-pro.fr (hosted on Romanian ICI IP space) | France / Romania | CRITICAL | Production French commercial appointment-booking SaaS — full system prompt + PII collection schema + function-call format exposed |
| [elasticsearch-cloud-survey-2026-05.md](elasticsearch-cloud-survey-2026-05.md) | sanctionscanner.com (168.119.90.62, Hetzner DE) | Turkey / Germany | CRITICAL | AML/KYC compliance SaaS — 79M KYB records + 6.2M individual sanctions list entries unauth; active ransom compromise; disclosed 2026-05-03 |
| [qdrant-cloud-survey-2026-05.md](qdrant-cloud-survey-2026-05.md) | Multiple operators | Various | HIGH | 61/61 Qdrant instances unauth across DO/Hetzner/Vultr — crypto trading AI, Vietnamese PII in agent memory, internal SOPs, legal compliance platform |

---

## Cross-Provider Surveys

Aggregate auth-posture studies across cloud-hosting providers (DigitalOcean, Hetzner, Vultr, etc.) for specific platform classes.

| File | Platform | Sample | Result |
|------|----------|--------|--------|
| [flowise-cloud-survey-2026-05.md](flowise-cloud-survey-2026-05.md) | Flowise | 43 instances across DO/Hetzner/Vultr | 0 unauthenticated — operator hygiene post-CVE-2024-36420 has improved on cloud platforms |
| [qdrant-cloud-survey-2026-05.md](qdrant-cloud-survey-2026-05.md) | Qdrant | 61 instances across DO/Hetzner/Vultr | 100% unauthenticated — ships auth-off by default; 48/61 contain live data |
| [elasticsearch-cloud-survey-2026-05.md](elasticsearch-cloud-survey-2026-05.md) | Elasticsearch / OpenSearch | 42 instances across DO/Hetzner/Vultr | Mixed — ~18 ransomed/wiped, ~16 live production data; ES 7.x default-no-auth still common |

---

## Why Separate from Universities

Commercial exposures carry distinct risk profiles:
- **Paying customers** — direct financial / contractual liability when PII is exposed
- **Live PII pipelines** — system prompts often reveal the exact data-collection schema
- **Competitive intel** — proprietary business logic in plain text
- **Cross-border attribution** — host country (e.g., Romania) often differs from operator country (e.g., France), complicating regulatory disclosure
