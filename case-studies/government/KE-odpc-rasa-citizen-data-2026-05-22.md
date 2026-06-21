---
type: case-study
severity: CRITICAL
date: 2026-05-22
title: "Kenya's Data Protection Regulator: Three Years of Citizen Conversations Behind a Single Unauthenticated Request"
summary: "The Office of the Data Protection Commissioner of Kenya, the body that enforces the Data Protection Act, ran its citizen chatbot on a Rasa server with no authentication. A hardcoded session ID in the vendor's frontend collapsed every citizen's conversation into one tracker. A single unauthenticated GET returned 30,823 events and 5,041 citizen messages spanning three years. The exposed stack also left PostgreSQL and Metabase on the public internet. The enforcer failed the standard it enforces."
tags:
  - rasa
  - unauth
  - cwe-306
  - government
  - citizen-data
  - kenya
  - vendor-template
sidenotes:
  - kind: host
    label: Target
    kv:
      - k: Operator
        v: "Office of the Data Protection Commissioner (odpc.go.ke)"
      - k: Sector
        v: "Government / Data Protection Regulator"
      - k: Country
        v: "Kenya"
      - k: Platform
        v: "Rasa Open Source 3.5.10"
      - k: Severity
        v: CRITICAL
  - kind: see-also
    label: Classification
    kv:
      - k: Primary
        v: "CWE-306 Missing Authentication for Critical Function"
      - k: Secondary
        v: "CWE-284 Improper Access Control"
      - k: Root cause
        v: "Hardcoded shared session identifier (vendor template)"
      - k: Law
        v: "Kenya Data Protection Act 2019, Section 41"
---

# Kenya's Data Protection Regulator: Three Years of Citizen Conversations Behind a Single Unauthenticated Request

_NuClide Research -- Nicholas Kloster -- 2026-05-22_

---

## Summary

The Office of the Data Protection Commissioner of Kenya runs the national data protection regime. It investigates breaches, issues enforcement notices, and fines organizations that fail to protect personal data under the Kenya Data Protection Act 2019.

Its own citizen chatbot ran on a Rasa server with no authentication on any endpoint. The vendor's web frontend hardcoded one session identifier, `user_id = "bot"`, for every visitor. Three years of citizen conversations did not land in per-user sessions. They all landed in one. A single unauthenticated GET to the conversation tracker returned 30,823 events and 5,041 citizen messages, dating to April 2023.

We confirmed the exposure and counted it. We did not read or store a single citizen message.

The institution that enforces data protection failed the standard it enforces.

---

## Attack Surface

One host. Four exposed services. No network segmentation.

| Port | Software | Role | Auth |
|------|----------|------|------|
| 5005 | Rasa Open Source 3.5.10 | Citizen chatbot REST API (also on 5006, 8443) | None |
| 5432 | PostgreSQL 14 | Rasa tracker store backend | Open to internet, login not tested |
| 3000 | Metabase 0.55.8 | BI analytics, bound to localhost by config but internet-reachable | Setup token leaked |
| 8000 | Python WSGI | THiNK chatbot frontend ("Linda Data") serving the hardcoded session ID | None |

The host is 102.220.23.140, `bot.odpc.go.ke`. Rasa, PostgreSQL, and Metabase all bind on 0.0.0.0. Identity is solid: the TLS certificate carries `*.odpc.go.ke`, issued by Sectigo, and `.go.ke` is Kenya's government second-level domain, issued only to Kenyan government entities by KENIC. WHOIS attributes the network to Konza Technopolis (AS328847).

---

## The Root Cause: One Session ID for Everyone

Rasa stores each conversation under a sender ID. A correct frontend generates a unique ID per visitor. The THiNK frontend did not. Line 6 of its `script-material.js` reads:

```javascript
user_id = "bot";
```

Every citizen who used the chatbot since deployment was written to the same tracker, the one named `bot`. The design intended privacy. The implementation merged every citizen into a single record. That record sat behind no authentication.

This is a vendor-template failure, not a one-off. If other THiNK deployments ship the same script, each one collapses all of its users into one readable session.

---

## What We Confirmed

**Unauthenticated API:** GET /domain returned 150-plus intents and actions over plain HTTP, no token. POST /model/parse returned the full NLU pipeline. Every response carried `Access-Control-Allow-Origin: *`.

**Mass citizen data read:** GET /conversations/bot/tracker returned HTTP 200 with `sender_id: "bot"`, 30,823 total events, and 5,041 user messages, deployed 2023-04-19. The complete conversation history was reachable in one request.

**PostgreSQL reachable:** nmap confirmed PostgreSQL 14 open on 5432 from an external IP, no IP restriction. We confirmed TCP reachability only. No login was attempted.

**Metabase setup token:** GET /api/session/properties on 3000 returned Metabase 0.55.8 with a setup token in the body and `site-url: http://localhost:3000`, a service never meant to face the internet.

We read counts and schema. We did not retrieve, read, or store any citizen message content. The PostgreSQL probe stopped at reachability.

---

## Data Exposed

The chatbot's intent schema names what citizens bring to it: complaints filed against organizations, data breach inquiries and notifications, investigation tracking, job applications, and penalty and enforcement queries. The 5,041 messages in the tracker are citizens corresponding with their national privacy regulator on exactly these topics.

The data class is citizen personal data held by a government regulator. We classify it from the intent schema and message counts, not from message content, which we did not read.

---

## Impact

**Confidentiality:** Any internet client could read three years of citizen interactions with the national data protection authority in a single unauthenticated request. People who contacted the regulator to report that their data was mishandled had that very correspondence left open.

**Integrity:** The webhook accepts POST from any caller with any sender ID. An unauthenticated actor can inject messages into conversation sessions and exercise the NLU pipeline at will.

**Escalation:** PostgreSQL on 5432 is the tracker's backend and is internet-reachable. The Metabase setup token leak is a second path toward the same data. The four findings share one root cause: the stack shipped with no network segmentation.

**Institutional:** ODPC issues enforcement notices to private organizations under Section 41 of the Kenya Data Protection Act for failing to implement appropriate technical measures. An unauthenticated production endpoint exposing citizen data is a failure of that same standard, by the body that defines it.

---

## Remediation

**Immediate (no code change):** Firewall ports 5005, 5006, 8443, 5432, and 3000 to the application network. Only the reverse proxy should reach Rasa.

**Root cause (frontend change, no backend work):** Replace the hardcoded `user_id = "bot"` with a per-session UUID generated client-side. This stops new citizen conversations from merging into one tracker.

**Short-term:** Set a Rasa REST channel token in `credentials.yml`. Restrict CORS from `*` to the canonical ODPC web origin. Restrict PostgreSQL to the application network in `pg_hba.conf`. Move Metabase behind authentication and rotate the leaked setup token.

---

## Restraint

The data-tier read confirmed exposure by status code and event counts. No citizen message content was retrieved, read, or stored. The PostgreSQL probe confirmed TCP reachability and attempted no login. No credentials were used. No write operations were performed. The adversarial prompt-injection step was stopped at the ethical gate because this is a government host.

---

## Disclosure

Finding documented 2026-05-22 under NuClide Research responsible-disclosure practice. Prior coordinated disclosures from this researcher include CVE-2025-4364 and ICSA-25-140-11, both through CISA.
