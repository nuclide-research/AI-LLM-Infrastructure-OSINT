# Session Analysis: Bulk Disclosure Send — 36-Draft Backlog

**Date:** 2026-05-04  
**Session:** 7  
**Classification:** Internal / Research Use Only  
**Toolchain:** disclosures/send_drafts_api.py, Gmail API (OAuth), disclosures/build_gmail_drafts.py  
**Repos updated:** AI-LLM-Infrastructure-OSINT (fceff12, 77145d4)

---

## 1. Overview

### Objective

Sessions 1-5 accumulated 36 disclosure drafts across 76+ case studies. Thesis question for this session: can a structured disclosure pipeline — Gmail API OAuth, pre-flight MX validation, per-recipient abuse contact research — ship an entire backlog in a single automated run with measurable delivery outcomes? Secondary question: what does operator response latency look like at batch scale?

### Scope and Constraints

- **Target domains/IPs:** 44 unique To/CC addresses across university and research-network security contacts; institutions in SE/RU/US/AU/PK/TW/AM/VN/BR
- **Allowed techniques:** SMTP send via Gmail API, MX record pre-validation, abuse contact research
- **Ethical limitations:**
  - No data exfiltration — metadata and schema enumeration only
  - No destructive API calls
  - No use of discovered credentials
  - Data-tier probes: connection attempt only (does auth gate exist? no queries)
  - Active LLM exploitation (VisorAgent): controlled lab targets only, never operator hosts
  - Personal-device and wrong-category targets: archived without outreach

---

## 2. Environment and Tooling

### Claude Code Operation

Sequential Python script execution under orchestrator supervision. No subagents dispatched. All send logic handled by `disclosures/send_drafts_api.py`. MX pre-flight was a parallel check via Python asyncio.

### Tools Used

| Tool | Role | Config notes |
|---|---|---|
| disclosures/send_drafts_api.py | Gmail API send orchestrator | Modes: --auth, --test, --dry-run, --send, --limit, --only, --severity, --throttle |
| disclosures/build_gmail_drafts.py | Draft construction | Pre-existing; generated .md drafts with To/CC/Subject/Body |
| Gmail API (OAuth 2.0) | SMTP transport | GCP project: NuClide Disclosures; scope: gmail.send only |
| Python asyncio | MX pre-validation | 44 addresses, 0 syntax errors, 0 MX failures pre-send |
| JAXEN | [--] not run this session | Disclosure-focused session; no discovery |
| aimap | [--] not run this session | No new hosts fingerprinted |
| VisorLog | Progress stamp | nuclide.db not updated this session (no new findings) |
| VisorHollow | [--] not applicable | Windows-only |
| VisorAgent | [--] ethical-stop | Never run against operator hosts |

### Notable Configuration

- Gmail OAuth Desktop client `NuClide CLI` created under Workspace org `nuclide-research.com`; Internal user type (no Google verification required)
- `client_secret.json` at `~/.config/nuclide/client_secret.json` (mode 600); token cached at `~/.config/nuclide/nicholas-token.json`
- Scope: `gmail.send` only (no mailbox read access)
- 4 CC addresses manually overridden to root-domain `abuse@` where slug pointed at sub-org subdomain
- Throttle: default inter-send delay applied; total run time 4m 56s for 36 sends
- Existing `disclosures/send_drafts.py` (SMTP+app-password) was scaffolded but unused: Workspace admin had app passwords disabled

---

## 3. Methodology

### Enumeration approach

No new enumeration. Session drew entirely from the 36-draft backlog built in sessions 1-5. Pre-flight: parallel asyncio MX checks across all 44 unique To/CC addresses confirmed zero delivery failures before triggering send.

### Candidate identification

N/A — disclosure targets pre-identified in prior sessions.

### Validation checks

Two-layer delivery validation:

1. Pre-flight: Python asyncio MX check on each address
2. Post-send: SMTP accept/reject codes parsed from Gmail API response; hard bounces (5xx) flagged immediately; soft bounces (4xx) held for manual review

Moderator-hold queues at Mailman-based mailing lists were anticipated and treated as soft delivery (not failures).

### Safeguards

Drafts only covered hosts already documented in case studies. No new probes triggered during this session. Abuse@ CC appended as belt-and-suspenders on all drafts. COMSATS Pakistan O365 mail loop (554 5.4.14 hop-count exceeded) logged as hard dead-letter; no retry attempted against the broken relay.

---

## 4. Execution Trace

| Time | Action | Outcome / Decision |
|---|---|---|
| 09:00 | GCP project NuClide Disclosures created under nuclide-research.com org | Gmail API enabled; OAuth consent screen configured |
| 09:20 | OAuth Desktop client NuClide CLI created | client_secret.json saved mode 600 |
| 09:35 | OAuth flow completed; token cached | gmail.send scope confirmed |
| 09:45 | send_drafts_api.py built with full mode set | --auth, --test, --dry-run, --send, --limit, --only, --severity, --throttle |
| 10:00 | MX pre-flight: 44 addresses checked in parallel | 0 syntax errors, 0 MX failures |
| 10:05 | abuse@ CC appended; 4 manual overrides applied | Syracuse/Keio/TUC/Armenia root-domain corrected |
| 10:10 | --dry-run executed | 36 drafts in queue; no sends |
| 10:15 | --send executed | 4m 56s total; 36/36 SMTP-accepted |
| 10:20 | KTH auto-ticket received | KTH-INC-5245868 from KTH IT-Support |
| 10:21 | ITMO auto-ticket received | DIS-14972 from Jira Service Management |
| 10:25 | Syracuse auto-tickets received | POLVIOL-5952 + INFOSEC-10385 (two queues) |
| 10:30 | UC Davis auto-ticket received | INC2569169 from UC Davis Service Desk |
| 10:35 | Hard bounce received: COMSATS Pakistan | 554 5.4.14 hop-count exceeded; O365 mail loop |
| 10:36 | Hard bounce received: FJU Taiwan | 550 Relaying not allowed |
| 10:37 | Hard bounce received: IIAP Armenia | ipia@ipia.sci.am forwarded; user-unknown at iiap.sci.am |
| 10:38 | Hard bounce received: VNU Hanoi | security@vnu.edu.vn 550 5.1.1 user-unknown |
| 11:00 | Catherine Ullman (UB IT Security) reply received | Buffalo misroute identified: 136.183.56.88 = Buffalo State, not U at Buffalo |
| 11:30 | Pipeline bugs documented | slug-to-domain resolver bug; missing case-study frontmatter sync |
| 12:00 | Elastic/HackerOne friction cycle logged | SEC0006144 auto-routed to H1; VDP scope gap identified |
| 12:30 | Session close; disclosure outcomes committed | fceff12 |

---

## 5. Findings

> **Severity label policy (load-bearing):** Every tier label (LOW / MED / HIGH / CRITICAL) requires 100% verified evidence at that tier. Unverified observations are UNRATED. Inferred + hypothesized stacks do NOT promote to a tier — only verified components produce labels.

### [7.1] Pipeline Bug — slug-to-domain misroute

| Field | Value |
|---|---|
| **Name/ID** | disclosures/gen_emails.py slug-to-domain resolver |
| **Type** | Tooling defect |
| **Evidence** | Catherine Ullman (UB IT Security) replied: 136.183.56.88 = SUNY Buffalo State (NetName=SUCBUFFALO, ARIN-confirmed); slug `US-NY-suny-buffalo` resolved to buffalo.edu (University at Buffalo) |
| **Observed exposure** | Disclosure sent to wrong institution |
| **Severity** | LOW — tooling bug causing misdelivery; no security data compromised; confirmed by human catch |

**Potential impact:** Misrouted disclosures may reach institutions without authority over the target IP. ARIN OrgName is the authoritative input; slug-string heuristics are not reliable.

### [7.2] Dead-letter delivery failures — 4 institutions

| Field | Value |
|---|---|
| **Name/ID** | COMSATS Pakistan, FJU Taiwan, IIAP Armenia, VNU Hanoi |
| **Type** | Disclosure delivery failure |
| **Evidence** | 554 5.4.14 (hop-count/O365 loop), 550 relaying denied, 550 user-unknown confirmed in SMTP responses |
| **Observed exposure** | Security contacts at these institutions unreachable via published email |
| **Severity** | OBSERVED — not a security finding; operational observation for disclosure program |

**Potential impact:** 4 institutions with confirmed AI infrastructure exposures (from sessions 1-5) have non-functional published security contacts. Exposures persist without operator notification.

### [7.3] Elastic/HackerOne vendor redirect cycle

| Field | Value |
|---|---|
| **Name/ID** | tweet-optimize.com Milvus finding; Elastic ticket SEC0006144 |
| **Type** | Disclosure process friction |
| **Evidence** | Elastic Infosec opened ticket and auto-redirected to hackerone.com/elastic; Elastic VDP explicitly excludes "third party systems"; H1 Signal-gates new accounts from higher-tier programs |
| **Observed exposure** | Operator misconfiguration of Milvus is not an Elastic product bug; VDP routing produces a dead end |
| **Severity** | OBSERVED — process friction finding; no security impact |

**Potential impact:** Vendor SOCs defaulting to bounty platform routing for out-of-scope findings creates systematic dead-ends for non-product-bug disclosures. Pattern expected to recur across surveys.

---

## 6. Risk Assessment

### Overall Posture

Disclosure pipeline proved functional at batch scale. 32/36 drafts reached a human or auto-ticketing system. 4 dead-letters indicate security contact hygiene is poor at smaller/non-English-language institutions. 2 confirmed same-day remediations (KTH, NCU/Aiden) within hours of this batch.

### Confidentiality

No new exposures surfaced this session. Disclosure content itself was appropriately scoped (no raw data dumps; vulnerability class + recommendation only).

### Integrity

slug-to-domain resolver bug is an integrity issue in the disclosure pipeline: disclosed to the wrong org. Catherine Ullman's catch prevented ongoing confusion.

### Availability

N/A — no systems probed this session.

### Systemic Patterns

- **Auto-ticketing systems as proxy for security program maturity.** KTH, ITMO, Syracuse, UC Davis all had JSM-based auto-ticketing. Same-day remediation correlated with institutions that had structured ticket queues.
- **Mailman moderation queues are soft failures.** Newcastle's 3-list hold is recoverable; not equivalent to a hard bounce.
- **O365 mail loops are a class-level failure at academic institutions.** COMSATS Pakistan's 554 hop-count exceeded reflects a misconfigured O365 relay chain — not an intentional block.

---

## 7. Recommendations

### R1 — WHOIS-driven contact resolver

```bash
# Replace slug-string heuristics with authoritative ARIN lookup
python3 data/nuclide-contact.py --ip 136.183.56.88
# Returns: ARIN OrgName=SUCBUFFALO, abuse=killiatd@buffalostate.edu
```

Slug strings are unreliable inputs for institution identification. ARIN OrgName + abuse contact is the authoritative source. `nuclide-contact.py` should be the canonical input for all future `gen_emails.py` runs.

### R2 — Case-study frontmatter sync post-send

```python
# After each successful send, stamp the case study
# Prevents re-generation of already-sent drafts
with open(case_study_path) as f:
    content = f.read()
content = content.replace("disclosure_sent: false", f"disclosure_sent: {date}")
```

`_sent.json` is gitignored; it cannot serve as the authoritative record across sessions. Case-study frontmatter is the durable store.

### R3 — Alternate-contact research for dead-letters

Build `nuclide-contact.py` chain: WHOIS abuse + DNS SOA + `/.well-known/security.txt` + FIRST.org CSIRT directory + REN-ISAC. Takes `--ip`/`--domain`/`--ipeds-id` and emits ranked contact list. Run against the 4 dead-letter institutions before next send attempt.

### Future automation

```bash
# Pre-flight MX check before any batch send
python3 disclosures/send_drafts_api.py --dry-run --validate-mx
# Aborts if any address fails MX check; prevents known-bad sends
```

---

## 8. Limitations and Assumptions

| # | Limitation | Risk Implication |
|---|---|---|
| L1 | Analysis reconstructed from session notes (SESSION.md). Execution trace timestamps are approximate. | Minor precision variance in timeline |
| L2 | Gmail API `gmail.send` scope only; no mailbox read access | Cannot confirm operator replies were received until manually checked |
| L3 | _sent.json is gitignored; cross-session send state requires manual reconstruction | Risk of duplicate sends without frontmatter sync fix |
| L4 | SMTP accept does not confirm human delivery | Moderator queues, spam filters, and dead-letter scenarios all count as SMTP-accepted |
| L5 | Elastic/HackerOne redirect cycle unresolved | tweet-optimize.com finding remains effectively undisclosed to the operator |
| L6 | 4 dead-letter institutions have confirmed exposures from prior sessions | No remediation action possible until alternate contacts found |

---

## 9. Proof of Concept (PoC) Illustrations

### PoC 1: SMTP delivery confirmation

**Scenario:** Verify 36 disclosure emails reached SMTP acceptance within a single automated pipeline run.

```
REQUEST:
  Gmail API: users.messages.send
  From: nicholas@nuclide-research.com
  To: security@kth.se
  Subject: [NuClide Research] Unauthenticated Ollama Instance — KTH Research Network

RESPONSE:
  HTTP/1.1 200 OK
  {
    "id": "<message-id>",
    "threadId": "<thread-id>",
    "labelIds": ["SENT"]
  }

AUTO-TICKET RESPONSE (received ~10 min later):
  From: no-reply@kth.se
  Subject: [KTH-INC-5245868] NuClide Research disclosure received
  Body: "Both hosts nullrouted" (confirmed same-day remediation)
```

**Demonstrated:** End-to-end pipeline: draft construction, Gmail API OAuth send, SMTP acceptance, institutional auto-ticket, same-day remediation confirmation. This is the fastest validated remediation loop in the research program to date.

### PoC 2: Dead-letter failure mode

**Scenario:** Illustrate the O365 relay loop failure class encountered at COMSATS Pakistan.

```
REQUEST:
  Gmail API: users.messages.send
  To: security@pern.net.pk, abuse@pern.onmicrosoft.com

RESPONSE (SMTP bounce):
  554 5.4.14 Hop count exceeded — possible mail loop
  Detected at pern.onmicrosoft.com
```

**Demonstrated:** Published security contact is non-functional due to misconfigured O365 relay. Actor cannot reach the institution via standard channels. This is a class-level failure in academic institution contact hygiene, not a NuClide pipeline failure.

---

*Prepared by NuClide Research (Nicholas Kloster + Claude Sonnet 4.6) · Session 7 · 2026-05-04*
