---
type: case-study
title: "Airbnb Tenant Agent — CORS Wildcard and No Auth on a Live WhatsApp Booking Bot"
date: 2026-05-25
severity: HIGH
sector: commercial
tags: [LangGraph, CORS, WhatsApp, Airbnb, booking, Node.js, Hetzner, Germany]
summary: "An Airbnb property manager's WhatsApp booking bot runs on LangGraph with no authentication and a wildcard CORS policy. Thread state from real guest conversations is readable without credentials. The agent is named 'Airbnb Tenant Agent' and is active."
---

# Airbnb Tenant Agent — CORS Wildcard and No Auth on a Live WhatsApp Booking Bot

**Date:** 2026-05-25
**Target:** 46.224.86.76
**Cloud:** Hetzner Online GmbH (AS24940), Nuremberg, Germany
**PTR:** static.76.86.224.46.clients.your-server.de
**App:** standalone-langgraph-server v1.0.0 / Airbnb Tenant Agent
**Severity:** HIGH

---

## What Was Found

### F1 — Airbnb Booking Agent Open Without Authentication (HIGH)

```
GET http://46.224.86.76:8000/assistants
→ [{"assistant_id": "booking", "name": "Airbnb Tenant Agent", "updated_at": "2026-05-25T19:50:28"}]
```

One assistant. Name: "Airbnb Tenant Agent." The agent handles guest booking interactions for an Airbnb property. No authentication on any endpoint.

We created a thread and read it back without a token:

```
POST http://46.224.86.76:8000/threads
→ {"thread_id": "booking-1779738615718-0w77n9", "status": "idle", "graph_id": "booking", "assistant_id": "booking"}

GET http://46.224.86.76:8000/threads/booking-1779738615718-0w77n9
→ {"thread_id": "booking-1779738615718-0w77n9", "status": "idle"}
```

Thread IDs use the format `booking-{timestamp}-{random}`. The timestamp is milliseconds since epoch. Real threads created within a known time range are enumerable by timestamp.

### F2 — CORS Wildcard on All Endpoints (HIGH)

Every response carries:

```
Access-Control-Allow-Origin: *
Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
Access-Control-Allow-Headers: Content-Type, Authorization, x-api-key
Access-Control-Allow-Credentials: true
```

The `x-api-key` header appears in Allow-Headers but is not enforced. Auth was planned and not built. Any page on any domain can make requests to the thread endpoints and read the response.

### F3 — Agent Execution Endpoints Open (HIGH)

```
POST /threads/:threadId/runs/stream   — stream agent execution
POST /threads/:threadId/runs/wait     — synchronous agent execution
```

No authentication. Any caller can run the booking agent against any existing thread. Threads from real WhatsApp conversations hold guest names, booking dates, and check-in requests. They hold property questions and follow-up messages from guests.

### F4 — WhatsApp Webhook Live on Port 3000 (MEDIUM)

```
GET http://46.224.86.76:3000/health
→ {"status": "ok", "service": "whatsapp-webhook"}

GET http://46.224.86.76:3000/webhook?hub.mode=subscribe&hub.verify_token=test&hub.challenge=12345
→ "Verification token mismatch"
```

Port 3000 receives incoming WhatsApp messages. The webhook verification token check is active. Incoming messages from Airbnb guests flow through port 3000 and into the LangGraph agent on port 8000. The checkpointer on port 8000 is confirmed connected and holds durable thread state.

---

## Endpoint Map

| Port | Method | Path | Auth |
|---|---|---|---|
| 8000 | GET | /assistants | NONE |
| 8000 | GET | /health | NONE |
| 8000 | POST | /threads | NONE |
| 8000 | GET | /threads/:id | NONE |
| 8000 | POST | /threads/:id/runs/stream | NONE |
| 8000 | POST | /threads/:id/runs/wait | NONE |
| 3000 | GET | /health | NONE |
| 3000 | GET/POST | /webhook | VERIFICATION TOKEN (webhook only) |

---

## Context

A property host or property manager built this to handle Airbnb guest communication via WhatsApp. The agent is active. The checkpointer holds thread state and the WhatsApp webhook is live.

Existing threads carry check-in times, access codes, property addresses, guest names, and dates. Thread state is accessible to any caller with a valid thread ID. Thread IDs are timestamp-prefixed and approximate-enumerable.

The operator identity is not in any endpoint response. PTR resolves to a Hetzner generic address.
