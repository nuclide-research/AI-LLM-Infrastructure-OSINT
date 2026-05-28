---
type: case-study
title: "Airbnb Tenant Agent — CORS Wildcard on a WhatsApp Booking Assistant"
date: 2026-05-25
severity: HIGH
sector: commercial
tags: [LangGraph, CORS, WhatsApp, webhook, booking, PII, Hetzner, Germany, agent-framework]
summary: "An Airbnb property host's WhatsApp booking assistant runs LangGraph with CORS Access-Control-Allow-Origin: * and no authentication on any endpoint. Any webpage can create threads and read guest booking conversations. The WhatsApp webhook service runs on the same host."
---

# Airbnb Tenant Agent — CORS Wildcard on a WhatsApp Booking Assistant

**Date:** 2026-05-25
**Target:** 46.224.86.76
**ASN:** AS24940 Hetzner Online GmbH — Nuremberg, Germany
**Severity:** HIGH

---

## What Was Found

### F1 — CORS Wildcard With No Auth (HIGH)

Port 8000 serves a Node.js/Express LangGraph server identified by its own assistant list:

```
GET http://46.224.86.76:8000/assistants
→ [{"assistant_id":"booking","name":"Airbnb Tenant Agent","updated_at":"2026-05-25T19:50:28"}]
```

One assistant: "Airbnb Tenant Agent." Every response carries:

```
Access-Control-Allow-Origin: *
Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
Access-Control-Allow-Headers: Content-Type, Authorization, x-api-key
Access-Control-Allow-Credentials: true
```

`x-api-key` appears in `Allow-Headers` but is not enforced on any route. `Access-Control-Allow-Credentials: true` combined with `Allow-Origin: *` is the CORS misconfiguration class that enables cross-origin reads from any webpage. The wildcard origin lets browser-based JavaScript from any domain issue credentialed requests and read the response.

No authentication gate exists on any endpoint.

### F2 — Thread State Readable Without Auth (HIGH)

The thread model is the Airbnb guest conversation record:

```
POST http://46.224.86.76:8000/threads
→ {"thread_id":"booking-1779738615718-0w77n9","status":"idle","graph_id":"booking","assistant_id":"booking"}
```

Thread IDs follow the pattern `booking-{timestamp}-{random}`. Threads created by real WhatsApp users follow the same scheme. The timestamp component makes thread history approximately enumerable within a known time range.

```
GET http://46.224.86.76:8000/threads/{threadId}
→ Thread state, full message history, and metadata — no auth
```

A thread from a real guest would contain: WhatsApp phone number, name, booking inquiry, check-in and check-out dates, property access discussion, and any support issue the guest raised. Property access codes delivered through the agent would also be in thread state.

### F3 — Agent Execution Open (HIGH)

```
POST http://46.224.86.76:8000/threads/:threadId/runs/stream
POST http://46.224.86.76:8000/threads/:threadId/runs/wait
```

Both endpoints execute the Airbnb booking agent against any thread without auth. A caller can attach execution to an existing guest thread and read the agent's response, including any data the agent retrieves. Agent state is mutable. A caller can drive the conversation in any direction.

### F4 — WhatsApp Webhook Service (MEDIUM)

Port 3000 serves the companion webhook service that receives incoming WhatsApp messages from guests:

```
GET http://46.224.86.76:3000/health
→ {"status":"ok","service":"whatsapp-webhook"}
```

The webhook endpoint at port 3000 enforces a verification token check against incoming GET requests (Meta's standard webhook handshake). This prevents external webhook spoofing. Incoming WhatsApp messages are legitimately gated. The auth failure is entirely on the LangGraph side at port 8000, where the agent state those messages produce is left open.

---

## Service Map

| Port | Service | Auth |
|---|---|---|
| 8000 | Node.js/Express LangGraph — "standalone-langgraph-server" v1.0.0 | None + CORS * |
| 3000 | WhatsApp webhook service | Verification token (webhook only) |

---

## Data Class

Threads from real Airbnb guest interactions contain: guest names, WhatsApp phone numbers, booking dates, property details, check-in instructions, access codes if delivered through the assistant, and any issue the guest raised. Operational PII for a hospitality business. Exposure class includes personal contact information and potentially physical access data.

The thread exposure is confirmed in structure; content of existing production threads was not read. The data class assessment is derived from the assistant's purpose (Airbnb booking) and the API's confirmed openness, not from extracting real records.

---

## Attribution

Hetzner Nuremberg (AS24940). Generic PTR: `static.76.86.224.46.clients.your-server.de`. No domain in any response. No frontend on any scanned port. Operator identity unknown from passive sources. The "standalone-langgraph-server" package name and the Airbnb context point to an individual host operator, not a SaaS platform.

---

## The Standalone Deployment Pattern

`standalone-langgraph-server` is a self-hosted LangGraph package. It ships as a Node.js Express server with no authentication in the default configuration. The CORS `*` setting is either a copy-paste from a tutorial or a local-testing decision left in place for production. Either way: a guest-facing communication system with no credential gate.

The WhatsApp verification token at port 3000 creates a misleading appearance of security. Incoming messages are verified. The conversation state they produce is not.

---

## Thesis Placement

LangGraph Server's default configuration does not enforce authentication. This host is a direct instance of the auth-on-default failure: the framework ships without auth enabled, the developer did not add it, and the deployment is on the public internet processing real guest communications. The CORS wildcard is an amplifier. Not just server-to-server accessible, but browser-accessible from any origin.

**See also:** [LangGraph Server Survey (2026-05-25)](langgraph-server-survey-2026-05-25.md) · [LangGraph Deployment Gap](langgraph-deployment-gap-survey-2026-05-25.md)
