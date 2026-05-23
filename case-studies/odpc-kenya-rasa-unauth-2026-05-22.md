# Kenya ODPC Rasa Chatbot — Unauthenticated API + Citizen Data Exposure

**Date:** 2026-05-22  
**Target:** 102.220.23.140 / bot.odpc.go.ke  
**Org:** Kenya Office of the Data Protection Commissioner  
**ASN:** AS328847 — KONZA (Konza Technopolis, Kenya)  
**Vendor:** THiNK (think.ke) — "Linda Data" bot  
**Bot deployed:** 2023-04-19 (assistant_id: `20230419-124032-ivory-bag`)  
**Severity:** CRITICAL  
**Ledger:** #7  

---

## Context

The Kenya Office of the Data Protection Commissioner enforces the Kenya Data Protection Act 2019 — the country's GDPR-equivalent. Citizens use the ODPC website to file complaints, track investigations, and ask questions about data rights. The ODPC bot ("Linda Data") is the front door to this service.

The bot runs Rasa 3.5.10. The entire API stack is exposed without authentication.

---

## What Was Found

### F1 — Rasa 3.5.10 Unauthenticated REST API (CRITICAL)

Port 5005 serves the full Rasa REST API with no auth layer.

```
GET /version → {"version":"3.5.10","minimum_compatible_version":"3.5.0"}
GET /status  → {"model_file":"core-model-agnostic-v3.tar.gz","model_id":"70be4...","num_active_training_jobs":0}
GET /domain  → 150+ intents and actions (full operational schema)
POST /model/parse + {"text":"..."} → NLU classification, intent confidence, entity extraction
POST /webhooks/rest/webhook + {"sender":"<any>","message":"..."} → bot responds
GET /conversations/<id>/tracker → full conversation event stream for any session ID
```

No token. No JWT. No IP restriction. `Access-Control-Allow-Origin: *` on every response.

### F2 — Mass Citizen Data Disclosure via Hardcoded `sender_id` (CRITICAL)

`/static/js/script-material.js`, line 6:

```javascript
user_id = "bot";
```

Every visitor to the chatbot sends their messages with `sender: "bot"`. Rasa stores all conversations by sender ID. The result: 3+ years of citizen queries are merged into a single conversation thread, readable via a single unauthenticated GET.

```
GET http://102.220.23.140:5005/conversations/bot/tracker
→ HTTP 200
→ {"sender_id":"bot","events":[...30823 events...],"latest_event_time":1779441388}
→ 5041 user messages spanning 2023-04-19 to 2026-05-21
```

The bot's own welcome message states: *"I will never share any of your personal information."*

The /conversations endpoint disagrees.

### F3 — PostgreSQL 14 Exposed on :5432 (HIGH)

```
PORT     STATE SERVICE    VERSION
5432/tcp open  postgresql PostgreSQL DB 14.7 - 14.9
```

Exposed to the public internet, no IP restriction. This is the Rasa tracker store backend — the same database that backs the /conversations endpoint. Direct credential access is out of scope for passive research but the attack surface is clear.

### F4 — Metabase 0.55.8 Analytics Dashboard Exposed (HIGH)

```
GET http://102.220.23.140:3000/api/session/properties
→ {
    "version": {"tag":"v0.55.8","date":"2025-07-15"},
    "setup-token": "9469ba5d-e13d-4b06-b9d4-fa72b9ee7b95",
    "site-url": "http://localhost:3000",
    ...
  }
```

`site-url: localhost:3000` confirms this was never intended to be internet-facing. Setup token leaks in unauthenticated response. Metabase at this level of exposure is likely connected to the same PostgreSQL instance.

---

## Stack

```
:22   OpenSSH 8.9p1 Ubuntu 3ubuntu0.15
:80   nginx 1.18.0 → redirect to :443
:88   nginx (unconfigured default page)
:443  nginx → THiNK chatbot frontend (Linda Data)
:3000 Metabase 0.55.8 (Jetty 12.0.21)
:3001 nginx SSL
:5005 Rasa 3.5.10 (HTTP, unauth)
:5006 Rasa 3.5.10 (HTTPS, unauth) ← canonical production endpoint
:5432 PostgreSQL 14.7-14.9 (exposed)
:6001 Rasa (additional instance)
:8000 Python WSGIServer 0.2 — THiNK chatbot dev frontend
:8443 Rasa 3.5.10 (HTTPS)
:9999 nginx (auth required — only protected port)
```

All Rasa instances share the same wildcard cert (`*.odpc.go.ke`, Sectigo, valid until 2026-07-17) and return the same model.

---

## NLU Schema (Selected Intents)

The domain endpoint exposes the full operational schema. Selected intents that indicate data sensitivity:

- `raise_complaint`, `raise_complaint_hacked`, `raise_complaint_without_consent`
- `data_breach_inquiry`, `data_breach_status`, `data_breach_notification`
- `investigation_process`, `track_investigation`
- `data_subject_request`, `data_subject_erase`, `data_subject_rectification`
- `job_application`, `shortlisting`, `job_appointment`
- `penalty`, `enforcement_notice`, `administrative_fine`
- `email` (email collection intent — PII ingest confirmed in design)

---

## Operator Attribution

- **Registrant:** KONZA Technopolis, Kenya (AS328847)
- **Admin contacts (AfriNIC):** Lucas Omollo, Richard Gachoki, Timothy Kosgei — 7th floor, Konza Complex
- **Vendor:** THiNK Ltd (think.ke) — chatbot platform, "Linda Data" bot name
- **TLS:** Sectigo wildcard `*.odpc.go.ke`, issued 2025-06-17
- **Passive DNS:** `bot.odpc.go.ke` → 102.220.23.140
- **CT log subdomains:** e-payments, helpdesk, hackathon, recruitment, webmail (full ODPC infrastructure visible)

---

## Chain

```
Shodan/passive DNS → bot.odpc.go.ke : 5005
GET /version → Rasa 3.5.10 confirmed, no auth
GET /domain → 150+ intents leaked
JS analysis (script-material.js) → sender_id = "bot" hardcoded
GET /conversations/bot/tracker → 30,823 events, 5,041 citizen messages, unauth
nmap → PostgreSQL :5432 exposed
Port 3000 → Metabase 0.55.8, setup-token leaks
```

No active exploitation. All findings established via read-only probes.

---

## BARE Output

All four findings fell below the 0.55 corpus coverage threshold (top score: Metabase at 0.518). No Metasploit module maps cleanly to Rasa-native attack surface — consistent with prior AI/ML infrastructure surveys. The finding class is novel relative to the MSF corpus.

---

## Regulatory Note

The Kenya Data Protection Act 2019 §25 requires data controllers to implement appropriate technical measures to protect personal data. The ODPC is both the enforcer of this obligation and its violator here. Citizens filing complaints about data breaches with the data protection authority have their messages stored without adequate controls and exposed to any internet-connected client.

---

## Remediation

1. Bind Rasa API to localhost or internal network — never expose :5005/:5006/:8443 directly
2. Generate unique session IDs per user — do not hardcode `sender_id = "bot"`
3. Add PostgreSQL pg_hba.conf to reject external connections
4. Move Metabase behind auth proxy or VPN
5. Rotate the exposed Metabase setup token

---

*NuClide Research | 2026-05-22*
