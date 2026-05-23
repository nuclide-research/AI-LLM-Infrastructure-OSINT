---
type: host
date: 2026-05-22
country: KE
sector: government
severity: CRITICAL
tags: [rasa, chatbot, conversation-history, postgresql, metabase, dpa-regulator]
---

# Who Watches the Watchmen? How Kenya's Data Protection Authority Leaked 3 Years of Citizen Complaints via an Unauthenticated AI Chatbot

_NuClide Research · 2026-05-22_

---

The primary mandate of any national data protection authority is to enforce privacy laws and ensure that organizations implement the technical measures necessary to safeguard citizen data. But what happens when the regulator itself deploys a vulnerable AI system that violates the very statutes it was created to enforce?

In a staggering demonstration of the risks inherent in hastily deployed AI infrastructure, the Kenyan Office of the Data Protection Commissioner (ODPC) inadvertently exposed over three years of sensitive citizen interactions to the public internet.

The culprit was "Linda Data," an AI chatbot designed to help citizens navigate data privacy laws. Instead, it became a massive, unauthenticated repository of the public's personal information.

---

## The Core Irony: "I will never share your personal information"

Since its deployment in April 2023, the ODPC chatbot was the front line for citizens reporting data breaches, filing regulatory complaints, and seeking assistance with data subject rights. The bot greeted every user with a reassuring prompt: _"I will never share any of your personal information."_

However, a fundamental architectural flaw and a complete lack of API authentication resulted in a catastrophic mass data disclosure. A single, unauthenticated HTTP request was all it took to retrieve the entire history of the chatbot's usage.

Over **30,000 events and 5,041 individual citizen messages** were pooled into a single, publicly readable tracker session. This included highly sensitive NLU (Natural Language Understanding) intents, such as `raise_complaint_hacked`, `data_breach_notification`, and `investigation_process`.

---

## The Anatomy of the Exposure

The vulnerability stemmed from a combination of poor vendor engineering by THiNK Ltd. and a failure to secure the AI shadow stack. The exposure breaks down into two critical failures.

### 1. The Hardcoded Identity Flaw (Mass Disclosure)

In a standard chatbot deployment, each user is assigned a unique session ID to ensure tenant isolation. The frontend JavaScript for the ODPC bot hardcoded a single, static session identity for all visitors:

```javascript
user_id = "bot";
```

Because the backend Rasa inference engine stores all conversational context by sender ID, every citizen who interacted with the bot over three years had their messages appended to the exact same tracker session. One GET request, no credentials:

```bash
$ curl -s http://102.220.23.140:5005/conversations/bot/tracker \
    | jq '{sender_id, total_events: (.events|length), user_messages: [.events[]|select(.event=="user")|.text]|length}'

{
  "sender_id":    "bot",
  "total_events": 30823,
  "user_messages": 5041
}
```

### 2. The Unauthenticated AI API

The chatbot's backend was powered by Rasa 3.5.10. The entire REST API was exposed on three ports — :5005, :5006, and :8443 — with no authentication layer and `Access-Control-Allow-Origin: *` on every response.

| Endpoint | Method | Exposure |
|---|---|---|
| `/version` | GET | Rasa version string |
| `/status` | GET | Model file, model ID, training status |
| `/domain` | GET | Full intent + action schema (150+ intents) |
| `/model/parse` | POST | NLU inference on arbitrary input |
| `/webhooks/rest/webhook` | POST | Message injection into any session |
| `/conversations/<id>/tracker` | GET | Full event stream for any session ID |

The NLU schema exposed the full operational structure of the ODPC's work:

`raise_complaint` · `raise_complaint_hacked` · `raise_complaint_without_consent` · `data_breach_inquiry` · `data_breach_notification` · `investigation_process` · `track_investigation` · `data_subject_request` · `data_subject_erase` · `job_application` · `shortlisting` · `enforcement_notice` · `penalty` · `administrative_fine`

---

## Collateral Infrastructure: The Shadow Stack

The poor security hygiene extended beyond the AI inference engine.

**Exposed PostgreSQL:** The Rasa tracker store database (PostgreSQL 14) was directly reachable from the public internet on port 5432, completely lacking IP restrictions in `pg_hba.conf`. This is the database holding all 30,823 events and all 5,041 citizen messages.

```
PORT     STATE SERVICE    VERSION
5432/tcp open  postgresql PostgreSQL DB 14.7 - 14.9
```

**Leaking Analytics:** A Metabase 0.55.8 analytics dashboard on port 3000 leaked internal setup tokens from an unauthenticated endpoint. The `site-url` field reads `http://localhost:3000` — confirming it was never intended to be internet-facing.

```bash
$ curl -s http://102.220.23.140:3000/api/session/properties \
    | jq '{version: .version.tag, setup_token: .["setup-token"], site_url: .["site-url"]}'

{
  "version":    "v0.55.8",
  "setup_token": "9469ba5d-e13d-4b06-b9d4-fa72b9ee7b95",
  "site_url":   "http://localhost:3000"
}
```

**Full attack surface:**

```
:22   OpenSSH 8.9p1 Ubuntu
:443  nginx → THiNK chatbot frontend (Linda Data) — citizen-facing
:3000 Metabase 0.55.8 — setup token leaks unauthenticated
:5005 Rasa 3.5.10 — HTTP, fully unauth
:5006 Rasa 3.5.10 — HTTPS, fully unauth  ← production endpoint
:5432 PostgreSQL 14.7 — exposed, no IP restriction
:8443 Rasa 3.5.10 — HTTPS, fully unauth
:9999 nginx — 401 auth required (only protected port)
```

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

## Regulatory Hypocrisy and the AI Blindspot

Section 25 of the Kenya Data Protection Act 2019 explicitly requires data controllers to implement appropriate technical measures to protect personal data. In this instance, the ODPC was both the enforcer of this obligation and its primary violator.

This exposure highlights a critical, industry-wide blindspot: the rush to deploy AI and LLM-backed tools is outpacing standard security fundamentals. Organizations are treating AI inference engines like black boxes, failing to apply the same network segmentation, authentication protocols, and rigorous vendor audits they would demand for a standard web application.

The ODPC exposure serves as a stark warning. As government entities and enterprises continue to integrate AI into citizen-facing and customer-support roles, securing the AI shadow stack is no longer optional. If the watchmen aren't auditing their own AI infrastructure, who is?

---

## Remediation

**R1 — Bind Rasa to localhost immediately**
```nginx
location /webhooks/ {
    proxy_pass http://127.0.0.1:5005;
    allow 127.0.0.1;
    deny all;
}
```

**R2 — Generate unique session IDs per user**
```javascript
// Replace: user_id = "bot";
user_id = localStorage.getItem('chat_session_id') || (() => {
    const id = crypto.randomUUID();
    localStorage.setItem('chat_session_id', id);
    return id;
})();
```

**R3 — Restrict PostgreSQL to localhost**
```
# /etc/postgresql/14/main/pg_hba.conf
host    all    all    127.0.0.1/32    scram-sha-256
# Remove all 0.0.0.0/0 entries
```

**R4 — Move Metabase off the public internet.** Restrict to VPN or internal network. Rotate the exposed setup token.

---

## Disclosure

- **Discovered:** 2026-05-22
- **Reported to:** info@odpc.go.ke · complaints@odpc.go.ke · enquiries@odpc.go.ke
- **CERT routing:** KE-CIRT / Communications Authority of Kenya
- **Status:** Disclosure sent 2026-05-22
