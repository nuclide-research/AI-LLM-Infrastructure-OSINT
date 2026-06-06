# Disclosure Pipeline

State tracking for findings worth disclosing. **No disclosure is ever sent autonomously.** This index tracks pipeline state; Nicholas Kloster decides what proceeds and when.

Disclosures from earlier surveys are referenced in `~/AI-LLM-Infrastructure-OSINT/disclosures/` (existing directory). This index extends that with research-program-relevant state.

## States

- **QUEUED** — finding identified, not yet decided
- **PREPARED** — disclosure artifact drafted, awaiting send
- **SENT** — disclosure sent, awaiting response
- **ACK** — recipient acknowledged
- **RESOLVED** — fix confirmed
- **EXPIRED** — no response within disclosure window
- **DECLINED** — researcher decided not to disclose

## Active (2026-06-06)

### Institutional findings (operator-direct)

| Target | Platform | Severity | State | Detail |
|---|---|---|---|---|
| Harvard University | Langfuse | HIGH | QUEUED | `surveys/2026-06-06-langfuse.md` |
| Arizona State University | Langfuse | HIGH | QUEUED | Same; previously flagged in Cat-05 |
| UC Santa Barbara | Langfuse | HIGH | QUEUED | Same |
| Khajeh Nasir Toosi U (Iran) | Langfuse | HANDLING | QUEUED | OFAC consultation required |
| Northeastern University | Phoenix | HIGH | QUEUED | `surveys/2026-06-06-phoenix.md`; "Essaybot" project (FERPA-class) |
| HKUST (Hong Kong) | RAGFlow | HIGH | QUEUED | `surveys/2026-06-06-ragflow.md` |
| Brno University of Technology | RAGFlow | HIGH | QUEUED | Same |
| Indiana University (2 ports) | RAGFlow | HIGH | QUEUED | Same |
| Shenzhen Middle School (K-12) | RAGFlow | HIGH | QUEUED | Same; jurisdiction-mediated |
| SENAI Brazil (national vocational ed) | Phoenix | HIGH | QUEUED | LGPD-class |

### Consolidated CERT-level

| Target | Findings consolidated | State |
|---|---|---|
| TWCERT/CC | Taiwan Ministry of Education Computer Center: Langfuse `140.115.59.61:3000` + RAGFlow `140.128.122.64:443` + RAGFlow `163.15.166.54:80` (3 instances same agency, same day) | QUEUED |
| CERT.br | SENAI national education infrastructure | QUEUED |

### Upstream maintainer (population-level)

| Vendor | Recommendation | State |
|---|---|---|
| Langfuse (Berlin) | Change `LANGFUSE_AUTH_DISABLE_SIGNUP` default from `false` to `true` | QUEUED |
| InfiniFlow (Shanghai, RAGFlow) | Change `register_enabled` default from `True` to `False`. Also: surface RAGFlow version on unauth endpoint to enable CVE-2024-12433 audit | QUEUED |
| Arize (US, Phoenix) | Make `PHOENIX_ENABLE_AUTH=true` the default; gate `/v1/projects` and `/v1/users` even when auth is disabled | QUEUED |
| Flowise (DK Maintainer) | Require auth plugin opt-out (not opt-in) for `/api/v1/chatflows` | QUEUED |

### Carryover from earlier surveys (research-program-relevant)

| Source | Detail |
|---|---|
| Pre-2026-06-06 disclosures | See `~/AI-LLM-Infrastructure-OSINT/disclosures/` directory for the existing log |
| Strategion GmbH (Langfuse Cat-05 partner) | medical AI; kardiointerakt subdomain; QUEUED |
| Earlier Vespa velutina beekeeper survey | See `MEMORY-archive.md` for context |

## Disclosure-policy notes

- **OFAC/sanctions:** Iran-based findings (KNTU Tehran) require legal review before contact. Default action: DECLINED unless legal pathway exists.
- **FERPA:** US university student data findings (Northeastern Essaybot) trigger heightened care; disclosure path is the institution's CISO, not faculty.
- **LGPD:** Brazil PII findings (SENAI) route through CERT.br for in-jurisdiction coordination.
- **GDPR:** EU university findings route through the institution's DPO when one exists.
- **Bug-bounty programs:** Verify on the org's *own canonical site* before recommending a bounty submission (per `feedback_verify_program_on_org_site_before_recommendation`). Listicles fabricate programs.

## Disclosure-preparation discipline

Per CLAUDE.md and feedback memory: **never offer, prep, or recommend disclosure**. This index tracks state when Nicholas decides to act on a finding. The analyst's role here is metadata management, not pipeline operation.
