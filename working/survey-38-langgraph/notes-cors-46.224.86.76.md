# Airbnb Tenant Agent — CORS Wildcard — Working Notes

**Host:** 46.224.86.76
**Cloud:** Hetzner Online GmbH (AS24940) — Nuremberg, Germany
**PTR:** static.76.86.224.46.clients.your-server.de
**App:** Airbnb Tenant Agent (booking assistant via WhatsApp)
**Status:** FULLY MAPPED — case study candidate
**Priority:** 3

---

## Confirmed Services

| Port | Service | Auth |
|---|---|---|
| 3000 | Express — WhatsApp webhook service | NONE (webhook verification enforced) |
| 8000 | Node.js/Express "standalone-langgraph-server" v1.0.0 — Airbnb booking agent | NONE |

---

## App Identification

```
GET /assistants
→ [{"assistant_id":"booking","name":"Airbnb Tenant Agent","updated_at":"2026-05-25T19:50:28","config":{},"metadata":{}}]
```

One assistant: "Airbnb Tenant Agent" with `graph_id: "booking"`. This is an Airbnb property host (or property management company) using a WhatsApp bot backed by LangGraph to handle tenant inquiries and bookings.

Operator geography: Hetzner Nuremberg. Operator identity unknown — Hetzner generic PTR.

---

## Confirmed Findings

### F1 — CORS Wildcard + No Auth (HIGH)

Response headers on every endpoint:

```
Access-Control-Allow-Origin: *
Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
Access-Control-Allow-Headers: Content-Type, Authorization, x-api-key
Access-Control-Allow-Credentials: true
```

The `x-api-key` header is listed in Allow-Headers but not enforced. No auth on any endpoint. Any webpage's JavaScript can create threads and read thread state without credentials.

### F2 — Thread State Open Without Auth (HIGH)

```
POST /threads
→ {"thread_id":"booking-1779738615718-0w77n9","status":"idle","graph_id":"booking","assistant_id":"booking"}
```

Thread IDs: `booking-{timestamp}-{random}`. Timestamp-based format means thread history is approximate-enumerable within a known time range.

```
GET /threads/{threadId}
→ Returns thread state, message history, and metadata — no auth
```

Thread state contains the booking agent's conversation history. Real threads (pre-existing, created by WhatsApp users) would contain Airbnb guest communications: names, dates, property access requests, check-in instructions.

### F3 — WhatsApp Webhook Exposed (MEDIUM)

Port 3000 serves a WhatsApp webhook service:

```
GET /webhook → "Verification token mismatch" (verification token check active)
GET /health → {"status":"ok","service":"whatsapp-webhook"}
```

The webhook verification token check prevents replay/spoofing of incoming messages. Incoming WhatsApp messages from guests flow through port 3000 → processed by LangGraph agent on port 8000.

### F4 — Agent Execution Open (HIGH)

```
POST /threads/:threadId/runs/stream   — stream agent execution
POST /threads/:threadId/runs/wait     — synchronous agent execution
```

No auth. Any caller can invoke the Airbnb booking agent against any thread, including existing threads with real guest conversations.

---

## Endpoint Map

| Method | Path | Service | Auth |
|---|---|---|---|
| GET | /health | :8000 | NONE |
| POST | /threads | :8000 | NONE |
| GET | /threads/:id | :8000 | NONE |
| POST | /threads/:id/runs/stream | :8000 | NONE |
| POST | /threads/:id/runs/wait | :8000 | NONE |
| GET | /assistants | :8000 | NONE |
| GET | /health | :3000 | NONE |
| GET | /webhook | :3000 | VERIFICATION TOKEN (webhook only) |

---

## Data Class Assessment

Threads from real WhatsApp interactions would contain:
- Guest names and WhatsApp phone numbers
- Booking dates and property details
- Check-in/check-out instructions
- Property access codes (potentially)
- Any inquiry or issue the guest raised

This is PII + operational security data for an Airbnb property. The exposure tier depends on what the existing threads contain — the thread creation endpoint is confirmed open; content of pre-existing threads is not verified.

---

## Pending

- [ ] Thread enumeration: try timestamps around known creation time to find real threads
- [ ] Operator attribution: no domain in any response, no frontend on any port
- [ ] Port scan broader: check 80, 443, 5432, 6333
