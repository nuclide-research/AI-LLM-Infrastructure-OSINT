---
type: host
date: 2026-05-22
country: KE
sector: government
severity: CRITICAL
tags: [rasa, chatbot, conversation-history, postgresql, metabase, dpa-regulator]
---

# Kenya's Data Protection Authority Leaked 3 Years of Citizen Complaints via an Unauthenticated AI Chatbot

_NuClide Research · 2026-05-22_

---

The primary mandate of any national data protection authority is to enforce privacy laws and ensure that organizations implement the technical measures necessary to safeguard citizen data. But what happens when the regulator itself deploys a vulnerable AI system that violates the very statutes it was created to enforce?

The Kenyan Office of the Data Protection Commissioner (ODPC) deployed "Linda Data," an AI chatbot for citizens to report data breaches, file regulatory complaints, and ask questions about data subject rights. The bot greeted every user with a promise: _"I will never share any of your personal information."_

A fundamental architectural flaw and a complete lack of API authentication made that promise impossible to keep.

---

## Infrastructure

| Field | Value |
|---|---|
| IP | 102.220.23.140 |
| Hostname | bot.odpc.go.ke |
| Org | Office of the Data Protection Commissioner, Kenya |
| ASN | AS328847 — Konza Technopolis |
| Vendor | THiNK Ltd (think.ke) |
| Bot name | Linda Data |
| Deployed | 2023-04-19 |
| Stack | Rasa 3.5.10, PostgreSQL 14, Metabase 0.55.8, nginx |

---

## F1 — Unauthenticated Rasa 3.5.10 REST API `CRITICAL`

The chatbot backend runs Rasa 3.5.10. The entire REST API is exposed on three ports — `:5005`, `:5006`, and `:8443` — with no authentication layer and `Access-Control-Allow-Origin: *` on every response.

| Endpoint | Method | Exposure |
|---|---|---|
| `/version` | GET | Rasa version string |
| `/status` | GET | Model file, model ID, training status |
| `/domain` | GET | Full intent + action schema (150+ intents) |
| `/model/parse` | POST | NLU inference on arbitrary input |
| `/webhooks/rest/webhook` | POST | Message injection into any session |
| `/conversations/<id>/tracker` | GET | Full event stream for any session ID |

The `/domain` endpoint exposes the full operational schema of the ODPC's work:

`raise_complaint` · `raise_complaint_hacked` · `raise_complaint_without_consent` · `data_breach_inquiry` · `data_breach_notification` · `investigation_process` · `track_investigation` · `data_subject_request` · `data_subject_erase` · `job_application` · `shortlisting` · `enforcement_notice` · `penalty` · `administrative_fine`

---

## F2 — Mass Citizen Data Disclosure via Hardcoded `sender_id` `CRITICAL`

In a standard chatbot deployment, each user is assigned a unique session ID to ensure isolation. The ODPC frontend (`script-material.js`, line 6) hardcoded a single static identity for all visitors:

```javascript
user_id = "bot";
```

Rasa stores all conversational context by sender ID. Every citizen who interacted with the bot since April 2023 had their messages appended to the same tracker session. One GET request, no credentials:

```bash
$ curl -s http://102.220.23.140:5005/conversations/bot/tracker \
    | jq '{sender_id, total_events: (.events|length), user_messages: [.events[]|select(.event=="user")|.text]|length}'

{
  "sender_id":    "bot",
  "total_events": 30823,
  "user_messages": 5041
}
```

5,041 citizen messages. Three years. One command.

The data class spans complaints filed against organizations, data breach reports, investigation status queries, job application questions, and enforcement notice inquiries. Citizens interacting with the national data protection authority — trusting the bot's assurance of privacy.

---

## F3 — PostgreSQL 14 Exposed on Port 5432 `HIGH`

The Rasa tracker store database is directly reachable from the public internet. No IP restriction.

```
PORT     STATE SERVICE    VERSION
5432/tcp open  postgresql PostgreSQL DB 14.7 - 14.9
```

This is the database backing every conversation in F2.

---

## F4 — Metabase 0.55.8 Setup Token Leak `HIGH`

Metabase runs on port 3000. The `/api/session/properties` endpoint returns an internal setup token without authentication. The `site-url` field reads `http://localhost:3000` — the platform was never intended for external access.

```bash
$ curl -s http://102.220.23.140:3000/api/session/properties \
    | jq '{version: .version.tag, setup_token: .["setup-token"], site_url: .["site-url"]}'

{
  "version":    "v0.55.8",
  "setup_token": "9469ba5d-e13d-4b06-b9d4-fa72b9ee7b95",
  "site_url":   "http://localhost:3000"
}
```

---

## Attack Surface

```
:22   OpenSSH 8.9p1 Ubuntu
:443  nginx — citizen-facing chatbot frontend
:3000 Metabase 0.55.8 — setup token leaks unauthenticated
:5005 Rasa 3.5.10 — HTTP, fully unauth
:5006 Rasa 3.5.10 — HTTPS, fully unauth
:5432 PostgreSQL 14.7 — exposed, no IP restriction
:8443 Rasa 3.5.10 — HTTPS, fully unauth
:9999 nginx — 401 required (only protected port)
```

---

## Regulatory Context

Section 25 of the Kenya Data Protection Act 2019 requires data controllers to implement appropriate technical measures to protect personal data. The ODPC issues fines and enforcement notices for precisely this class of failure. Their own chatbot violated every requirement they enforce on others.

This exposure reflects an industry-wide blindspot: the rush to deploy AI tools is outpacing basic security fundamentals. Organizations are treating AI inference engines as black boxes, failing to apply the network segmentation and authentication controls they would require for any standard web application. If the watchmen aren't auditing their own AI infrastructure, who is?

---

## Disclosure

| Field | Value |
|---|---|
| Discovered | 2026-05-22 |
| Reported to | info@odpc.go.ke · complaints@odpc.go.ke · enquiries@odpc.go.ke |
| CERT routing | KE-CIRT / Communications Authority of Kenya |
| Status | Disclosure sent 2026-05-22 |
