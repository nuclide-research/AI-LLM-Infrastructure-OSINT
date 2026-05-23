---
type: host
date: 2026-05-22
country: KE
sector: government
severity: CRITICAL
tags: [rasa, chatbot, conversation-history, postgresql, metabase, dpa-regulator]
---

# Kenya's Data Protection Regulator Exposes Citizen Complaints to the Open Internet

_NuClide Research · 2026-05-22_

---

## Summary

Kenya's Office of the Data Protection Commissioner runs a public chatbot at `bot.odpc.go.ke`. The chatbot's entire API backend is unauthenticated. A single HTTP request returns 3 years of citizen conversations — complaints about data breaches, regulatory inquiries, job applications — merged into one session readable by anyone.

The bot tells every user: *"I will never share any of your personal information."*

---

## Infrastructure

| Field | Value |
|---|---|
| IP | 102.220.23.140 |
| Hostname | bot.odpc.go.ke |
| Org | Office of the Data Protection Commissioner, Kenya |
| ASN | AS328847 — Konza Technopolis |
| Country | Kenya |
| Vendor | THiNK Ltd (think.ke) |
| Bot deployed | 2023-04-19 (assistant\_id: `20230419-124032-ivory-bag`) |
| Stack | Rasa 3.5.10, PostgreSQL 14, Metabase 0.55.8, nginx |

---

## Findings

### F1: Rasa 3.5.10 Fully Unauthenticated REST API (CRITICAL)

Ports 5005, 5006, and 8443 all serve the Rasa REST API without any authentication layer. `Access-Control-Allow-Origin: *` on every response.

Accessible without credentials:

- `GET /domain` — full intent and action schema (150+ intents)
- `POST /model/parse` — NLU classification on arbitrary input
- `POST /webhooks/rest/webhook` — message injection into any conversation session
- `GET /conversations/<id>/tracker` — full conversation event stream for any session ID

### F2: Mass Citizen Data Disclosure via Hardcoded `sender_id` (CRITICAL)

The chatbot frontend (`script-material.js`, line 6) hardcodes a single session identity for all visitors:

```javascript
user_id = "bot";
```

Rasa stores conversations by sender ID. Every citizen who has used the bot since April 2023 has their messages stored under this same key. One GET request, no credentials:

```
GET http://102.220.23.140:5005/conversations/bot/tracker
→ HTTP 200
→ sender_id: "bot"
→ total_events: 30,823
→ user_messages: 5,041
```

The data class includes complaints filed against organizations, data breach reports, investigation status queries, and job application questions — 3 years of citizens interacting with the national data protection authority.

### F3: PostgreSQL 14 Exposed on Port 5432 (HIGH)

The Rasa tracker store database is directly reachable from the public internet. No IP restriction. This is the backend that holds all conversation history.

### F4: Metabase 0.55.8 Analytics Dashboard Exposed (HIGH)

Metabase runs on port 3000. The `/api/session/properties` endpoint returns an internal setup token without authentication. The `site-url` field reads `http://localhost:3000`, confirming the platform was never intended for external access.

---

## Attack Surface Map

```
:22   OpenSSH 8.9p1
:443  nginx → THiNK chatbot frontend (Linda Data)
:3000 Metabase 0.55.8 — setup token leaks unauthenticated
:5005 Rasa 3.5.10 — HTTP, fully unauth
:5006 Rasa 3.5.10 — HTTPS, fully unauth
:5432 PostgreSQL 14.7 — exposed, no IP restriction
:8443 Rasa 3.5.10 — HTTPS, fully unauth
:9999 nginx — 401 auth required (only protected port)
```

---

## NLU Schema (selected intents)

The `/domain` endpoint exposes the full operational schema. Sensitive flows include:

`raise_complaint` · `raise_complaint_hacked` · `raise_complaint_without_consent` · `data_breach_inquiry` · `data_breach_notification` · `investigation_process` · `track_investigation` · `data_subject_request` · `data_subject_erase` · `job_application` · `shortlisting` · `enforcement_notice` · `penalty`

---

## Regulatory Context

The Kenya Data Protection Act 2019 §25 requires data controllers to implement appropriate technical measures to protect personal data. The ODPC issues fines and enforcement notices for precisely this class of failure. Their own chatbot violates every requirement they enforce on others.

---

## Remediation

1. Bind Rasa API to `127.0.0.1` — never expose :5005/:5006/:8443 directly
2. Replace `user_id = "bot"` with a per-session UUID generated client-side
3. Add `pg_hba.conf` rules to reject all external PostgreSQL connections
4. Move Metabase behind an authenticated proxy or restrict to VPN access

---

## Disclosure

- **Discovered:** 2026-05-22
- **Status:** Disclosure sent to info@odpc.go.ke + complaints@odpc.go.ke (2026-05-22)
- **CERT routing:** KE-CIRT / Communications Authority of Kenya
