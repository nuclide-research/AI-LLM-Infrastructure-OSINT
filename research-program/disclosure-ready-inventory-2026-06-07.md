# Disclosure-Ready Inventory — 2026-06-07

**Purpose:** Single page consolidating every disclosure currently QUEUED in the research-program pipeline, with target + recipient + severity + recommendation + supporting evidence link, so the decision step is the only remaining step. **No email-body content here.** Per the no-autonomous-disclosure-prep policy, body drafting is Nick's call per recipient.

**State as of 2026-06-07.** Compiled from `research-program/disclosures/INDEX.md` + Mitnick-pivot refinements + cohort response analysis.

---

## Tier 1 — Highest blast-radius (send first)

### 1. Capitol.ai — CRITICAL-ENTERPRISE

| Field | Value |
|---|---|
| Recipient | `security@capitol.ai` (published, verified) |
| Severity | CRITICAL-ENTERPRISE (multi-product, multi-tenant) |
| Surfaces | LibreChat + Langfuse customer-tenant fleet. **Customers confirmed via CT + probe:** Ernst & Young (9+ subdomains, 3 regions), UK HMG / Plexal, Politico, Dow Jones, Advance Local, Metric Media, "eont" (unidentified). |
| Posture | All Langfuse-customer instances SIGNUP_OPEN; LibreChat customer-tenants REG_OPEN. |
| Recommendation | Disable signup at the tenant template level; rotate tenant-customer auth posture defaults. |
| Supporting file | `case-studies/commercial/librechat-deep-dive-verification-2026-06-06.md` |
| Why this one first | Largest single enterprise-SaaS finding in the 2026-06-06 corpus. Customer-tenant fleet means downstream blast radius scales with customer count, not host count. |

---

## Tier 2 — Upstream maintainer (highest unit-leverage per cohort analysis)

The 2026-06-07 cohort analysis showed upstream-maintainer pathway is undersampled (n=1 in 104 sent disclosures). Per Insight #40, upstream pressure moves the population rate within 2-3 minor versions. These are the four entries.

### 2. Langfuse (Berlin) — UPSTREAM

| Field | Value |
|---|---|
| Recipient | TBD — Langfuse maintainer security path. Public security.txt or GitHub security advisory channel. |
| Recommendation | Change `LANGFUSE_AUTH_DISABLE_SIGNUP` default from `false` to `true`. |
| Population impact | ~800-820 instances currently open-signup (88.9% rate, 1,141 indexed). |
| Supporting file | `case-studies/commercial/langfuse-population-survey-2026-06-06.md` |

### 3. InfiniFlow (Shanghai, RAGFlow) — UPSTREAM

| Field | Value |
|---|---|
| Recipient | TBD — InfiniFlow security path. GitHub: github.com/infiniflow/ragflow |
| Recommendation | Two changes: (a) Change `register_enabled` default from `True` to `False`. (b) Surface RAGFlow version on unauth endpoint to enable CVE-2024-12433 audit (currently obscured, leaving 618 known-open hosts of unknown patch level). |
| Population impact | ~618 instances currently open-register (87.2% rate, 1,915 indexed). |
| Supporting file | `case-studies/commercial/ragflow-population-survey-2026-06-06.md` |

### 4. Arize (US, Phoenix) — UPSTREAM

| Field | Value |
|---|---|
| Recipient | TBD — Arize security path. |
| Recommendation | Make `PHOENIX_ENABLE_AUTH=true` the default; gate `/v1/projects` and `/v1/users` even when auth is disabled. |
| Supporting file | `case-studies/commercial/phoenix-population-survey-2026-06-06.md` |

### 5. Flowise (DK maintainer) — UPSTREAM

| Field | Value |
|---|---|
| Recipient | TBD — Flowise maintainer. |
| Recommendation | Require auth plugin opt-out (not opt-in) for `/api/v1/chatflows`. |
| Supporting file | `case-studies/commercial/flowise-population-survey-2026-06-06.md` |

### 6. LibreChat (danny-avila) — UPSTREAM

| Field | Value |
|---|---|
| Recipient | TBD — danny-avila maintainer security path. |
| Recommendation | Backport v0.8.x registration-disabled default to `main`; add brand-aware registration warning. |
| Supporting file | `case-studies/commercial/librechat-deep-dive-verification-2026-06-06.md` |

---

## Tier 3 — Institutional (per-operator, cohort-responsive)

The cohort analysis showed institutional CISO/IT offices respond at ~12-22%. These are the wins available with reasonable expected response rates.

### Sharpened (cert-pivot refined this session)

#### 7. Arizona State University → CSE 240 course operator — HIGH

| Field | Value |
|---|---|
| Operator (refined) | **CSE 240 course staff** (per cert subject `cse240.com`), not central ASU IT. Cert covers `cse240.com`, `www`, `api`, `git`. |
| Recipient candidates | CSE 240 instructor of record (departmental webpage), ASU School of Computing CISO (`infosec@asu.edu` per ASU IT publication), course teaching staff via department admin. |
| Severity | HIGH (course infrastructure used by undergraduates; credential surface for student work). |
| Recommendation | Disable Langfuse signup; rotate API keys; audit for unauthorized tenant projects. |
| Supporting files | `case-studies/commercial/langfuse-population-survey-2026-06-06.md`, `research-program/mitnick-pivot-2026-06-07.md` |

#### 8. Tunghai University (TW) — aisse.thu.edu.tw — HIGH

| Field | Value |
|---|---|
| Operator (refined) | Tunghai University AI Software Systems Engineering project (`aisse.thu.edu.tw`), not Taiwan MoE Computer Center. Original survey label was the upstream allocation, not the institutional operator. |
| Recipient candidates | Tunghai U CS department / faculty IT (per CN), TWCERT/CC for consolidated bundle. |
| Severity | HIGH |
| Bundle with | The TWCERT/CC consolidated bundle (Langfuse `140.115.59.61:3000` + RAGFlow `163.15.166.54:80` + this Tunghai instance). |
| Supporting files | `case-studies/commercial/ragflow-population-survey-2026-06-06.md`, `research-program/mitnick-pivot-2026-06-07.md` |

#### 9. Santé Pair (FR mental-health nonprofit) — HIGH-SENSITIVE (GDPR Art 9)

| Field | Value |
|---|---|
| Operator (refined) | Santé Pair runs **two chat surfaces** — `santepair.fr` (LibreChat) and `chat.santepair.fr` (separate application, confirmed via cert SAN). Disclosure should bundle both. |
| Recipient candidates | DPO (GDPR-mandated for health nonprofits) — published at `santepair.fr/mentions-legales` or equivalent legal page. CNIL as fallback if DPO unresponsive. |
| Severity | HIGH-SENSITIVE — GDPR Article 9 covers special-category data (health). |
| Recommendation | Disable open registration on LibreChat; audit `chat.` posture separately. |
| Supporting files | `case-studies/commercial/librechat-deep-dive-verification-2026-06-06.md`, `research-program/mitnick-pivot-2026-06-07.md` |

### Existing queue (unsharpened)

| # | Target | Platform | Severity | Recipient candidate |
|---|---|---|---|---|
| 10 | Harvard University | Langfuse | HIGH | `informationsecurity@harvard.edu` (verify on harvard.edu IT page first) |
| 11 | UC Santa Barbara | Langfuse | HIGH | `infosec@ucsb.edu` (verify) |
| 12 | Khajeh Nasir Toosi U (Iran) | Langfuse | HANDLING | **OFAC consultation required before any contact** |
| 13 | Northeastern University | Phoenix | HIGH | `it-security@northeastern.edu`; Essaybot finding has FERPA-class data — escalate to CISO, not faculty |
| 14 | HKUST (Hong Kong) | RAGFlow | HIGH | `cscsec@ust.hk` |
| 15 | Brno University of Technology | RAGFlow | HIGH | `csirt@vutbr.cz` |
| 16 | Indiana University (2 ports) | RAGFlow | HIGH | `it-incident@iu.edu` |
| 17 | Shenzhen Middle School (K-12) | RAGFlow | HIGH | Path: vendor InfiniFlow (school disclosure direct = jurisdictional risk; let upstream pressure the operator). |
| 18 | SENAI Brazil (national vocational ed) | Phoenix | HIGH | CERT.br consolidated; LGPD-class |
| 19 | TruslerLegal / Lexpertcloud | LibreChat | HIGH-PRIVILEGED | Vendor: `security@truslerlegal.*` (verify) |
| 20 | LegalMatch AI | LibreChat | HIGH-PRIVILEGED | `security@legalmatch.com` (verify) |
| 21 | UC Berkeley CEE | LibreChat (USER_KEY mode) | MEDIUM-institutional | `security@berkeley.edu` |
| 22 | Atticus Legal Assistant | LibreChat | MEDIUM | (verify recipient) |
| 23 | Legal-Knowledge-Graph-Chatbot | LibreChat (Azure) | MEDIUM-UNKNOWN | (insufficient providers data; defer until reattribution) |

---

## Tier 4 — Consolidated CERT bundles

### 24. TWCERT/CC — 3 Taiwan institutional findings

| Field | Value |
|---|---|
| Recipient | `twcert@twcert.org.tw` (verify on TWCERT website) |
| Findings | Langfuse `140.115.59.61:3000` + RAGFlow `140.128.122.64:443` (= Tunghai University `aisse.thu.edu.tw`, refined) + RAGFlow `163.15.166.54:80` |
| Severity | CRITICAL (3 institutional findings, same agency footprint, same day) |
| Bundle rationale | TWCERT consolidates routing; saves three separate outreach attempts. |
| Supporting files | `case-studies/commercial/langfuse-population-survey-2026-06-06.md`, `case-studies/commercial/ragflow-population-survey-2026-06-06.md`, `research-program/mitnick-pivot-2026-06-07.md` |

### 25. CERT.br — SENAI national education infrastructure

| Field | Value |
|---|---|
| Recipient | CERT.br (verify) |
| Finding | SENAI Phoenix instance (LGPD-class) |
| Severity | HIGH |
| Supporting file | `case-studies/commercial/phoenix-population-survey-2026-06-06.md` |

---

## Tier 5 — Bulk follow-up (d+30 silent worklist)

82 prior disclosures are SILENT and >30 days old. Bulk soft-followup ("following up on disclosure dated YYYY-MM-DD; please confirm receipt") would convert some of these to ACK/BOUNCED states. See `research-program/disclosure-followup-worklist-2026-06-07.md` for the per-case list.

This isn't a single send; it's a batch action. **Recommended trigger:** allocate one focused hour for the worklist after the Tier 1-4 items are dispatched.

---

## Policy reminders (codified)

- **No autonomous disclosure-body drafting.** Per `feedback_no_disclosure_recommendations`, body drafting is the researcher's call per recipient. This inventory pre-bundles recipient + severity + recommendation; it does not pre-draft text.
- **Verify recipient before send.** Per the `disclosures/SCHEMA.md` and prior feedback, `security@<edu>` bounces ~10% of the time; always confirm the address resolves via the institution's own IT page before sending.
- **OFAC items require legal review.** KNTU Tehran entry is HANDLING; default is DECLINED unless legal pathway exists.
- **FERPA-class findings escalate.** Northeastern Essaybot has student-data class concerns; route through CISO, not faculty.
- **Bug bounty verification.** Verify on the org's own canonical site BEFORE recommending a bounty submission. Listicles fabricate programs.

---

_Generated 2026-06-07 from `research-program/disclosures/INDEX.md` + Mitnick-pivot refinements + cohort response analysis. To regenerate: read `INDEX.md`, apply Mitnick deltas, cross-reference cohort response rates. No tooling automates this yet — it's a researcher decision document._
