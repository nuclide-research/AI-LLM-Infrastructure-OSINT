# ODPC Kenya — Unauthenticated Rasa Chatbot

**Date:** 2026-05-22
**Target:** Office of the Data Protection Commissioner of Kenya (ODPC)
**Host:** `102.220.23.140` / `odpc.go.ke`
**Platform:** Rasa Open Source 3.5.10
**Sector:** Government — data protection enforcement authority
**Country:** Kenya (KE)
**Hosting:** Dialog Telekom Plc (AS37061, LK/KE), CIDR 102.220.23.0/24

---

## 1. Summary

Kenya's data protection enforcement body runs an unauthenticated Rasa chatbot on
a public IP. The `/webhooks/rest/webhook` POST endpoint accepts messages from any
caller and returns bot responses with no token, session cookie, or API key. The
bot identifies itself as "ODPC Virtual Assistant" and was built to handle
data-subject queries on behalf of the Commissioner.

ODPC administers and enforces the Kenya Data Protection Act 2019. The same
institution charged with sanctioning organizations for inadequate data security
misconfigures its own public-facing AI chatbot.

---

## 2. Technical Detail

### Host identification

TLS certificate on port 443 carries SANs `*.odpc.go.ke` and `odpc.go.ke`.
Issuer: Sectigo Public Server Authentication CA DV R36. The `.go.ke` TLD is
Kenya's second-level government domain — issued exclusively to Kenyan government
entities by the Kenya Network Information Centre (KENIC).

```
cert CN:   *.odpc.go.ke
cert SANs: *.odpc.go.ke, odpc.go.ke
issuer:    Sectigo Public Server Authentication CA DV R36
not_after: 2025-05-17 (expiry → 2026-05-17, renewed)
```

### Platform confirmation

GET / on port 5005 returns the Rasa version banner:

```
Hello from Rasa: 3.5.10
```

GET /status returns model metadata without auth:

```json
{"model_file": "core-model-agnostic-v3.tar.gz", "num_active_training_jobs": 0}
```

### Unauthenticated access

POST `/webhooks/rest/webhook` with a minimal probe body returns a full bot
response with no authentication required:

```
POST /webhooks/rest/webhook HTTP/1.1
Host: 102.220.23.140:5005
Content-Type: application/json

{"sender": "probe", "message": "hello"}
```

Response:

```json
[{
  "recipient_id": "probe",
  "text": "Hi, am ODPC Virtual Assistant.\nI was created just to answer your questions..."
}]
```

HTTP 200. No `WWW-Authenticate` header. No token check. No session requirement.

### CORS posture

Response headers include:

```
Access-Control-Allow-Origin: *
Access-Control-Allow-Credentials: true
```

Wildcard CORS on a government chatbot endpoint allows any web origin to POST
messages and read responses via browser-side fetch.

---

## 3. Finding

| Field | Value |
|---|---|
| ID | ODPC-KE-001 |
| Type | Unauthenticated AI chatbot webhook (Rasa no-auth default) |
| Host | 102.220.23.140:5005 |
| Domain | odpc.go.ke |
| Platform | Rasa Open Source 3.5.10 |
| Evidence | POST /webhooks/rest/webhook → HTTP 200 + "ODPC Virtual Assistant" response body; no auth header required |
| Observed exposure | Direct unauthenticated invocation of ODPC's production chatbot |
| Severity | HIGH |

**Potential impact:**

Any caller can inject arbitrary messages into the ODPC Virtual Assistant, observe
its response logic, and map the flows it uses to handle data-subject requests. An
adversary can enumerate the bot's knowledge base, trigger edge-case paths, and read
all bot output without authentication.

This does not require compromising any ODPC system. The bot responds by design;
only the absence of a token makes it available to all callers rather than just
ODPC's own web frontend.

The irony is institutional: ODPC issues enforcement notices to private-sector
organizations for failing to implement adequate technical measures under Section
41 of the Kenya Data Protection Act. An unauthenticated production AI endpoint
on the ODPC's own infrastructure is a failure of the same standard.

---

## 4. Remediation

Rasa's REST channel requires explicit token configuration. Without it, all callers
are accepted.

```yaml
# credentials.yml
rest:
  token: "<strong-random-token-min-32-chars>"
```

Restart Rasa after adding the token. The frontend widget or integration that calls
`/webhooks/rest/webhook` must include the token as a query parameter:

```
POST /webhooks/rest/webhook?token=<token>
```

Additionally: restrict the CORS policy. `Access-Control-Allow-Origin: *` with
`Allow-Credentials: true` is a misconfiguration on a government endpoint. Lock
`Access-Control-Allow-Origin` to the canonical ODPC web origin only.

---

## 5. Restraint

The probe sent one message ("hello") and read the response. No further messages
were sent. No conversation flows were mapped. No attempt was made to extract
information from the bot's knowledge base. The finding rests on the 200-status
response and bot self-identification string.

---

## 6. Toolchain

```
[x] visorgraph     cert CN *.odpc.go.ke → odpc.go.ke confirmed
[x] aimap v1.9.26  service: Rasa, severity: high, auth_status: none
[x] webhook probe  POST /webhooks/rest/webhook → 200, recipient_id confirmed
[x] visorlog       finding #1, HIGH, tags: RASA UNAUTH GOVERNMENT DATA-PROTECTION KE
```

*Prepared by NuClide Research (Nicholas Kloster + Claude Sonnet 4.6) · 2026-05-22*
