---
type: case-study
title: "Airbnb Tenant Agent — CORS Wildcard and Open Booking Thread State"
date: 2026-05-25
severity: HIGH
sector: commercial
tags: [LangGraph, WhatsApp, CORS, real-estate, PII, Hetzner, booking-agent, property-management]
summary: "A LangGraph-backed Airbnb booking agent on Hetzner Nuremberg exposes thread creation, thread state reads, and agent execution with no authentication. CORS wildcard headers mean any browser origin can invoke the agent. WhatsApp guest communications are the data class at risk."
---

# Airbnb Tenant Agent — CORS Wildcard and Open Booking Thread State

**Date:** 2026-05-25
**Target:** 46.224.86.76
**ASN:** AS24940, Hetzner Online GmbH, Nuremberg, Germany
**Severity:** HIGH

---

## What Was Found

### F1 — CORS Wildcard on an Unauthenticated Agent API (HIGH)

Port 8000 runs `standalone-langgraph-server v1.0.0` with CORS wildcard headers and no credential enforcement. Every response carries:

```
Access-Control-Allow-Origin: *
Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
Access-Control-Allow-Headers: Content-Type, Authorization, x-api-key
Access-Control-Allow-Credentials: true
```

The `x-api-key` header appears in `Allow-Headers` but is not checked by the server. No credential is required. No token is validated. The CORS wildcard is the delivery mechanism for the authentication gap. Any web page a guest visits can make cross-origin requests to this agent and read the responses.

The assistant registry confirms the application:

```
GET /assistants
→ [{"assistant_id":"booking","name":"Airbnb Tenant Agent","updated_at":"2026-05-25T19:50:28","config":{},"metadata":{}}]
```

One assistant. `graph_id: "booking"`. The deployment is an Airbnb property host or property management company running a WhatsApp-based tenant communication bot.

### F2 — Thread State Readable Without Auth (HIGH)

Thread creation is open:

```
POST /threads
→ {"thread_id":"booking-1779738615718-0w77n9","status":"idle","graph_id":"booking","assistant_id":"booking"}
```

Thread IDs follow the pattern `booking-{timestamp}-{random}`. The timestamp component is millisecond epoch. Threads created during known activity windows are enumerable within a bounded time range.

```
GET /threads/{threadId}
→ Returns thread state, message history, and metadata — no auth
```

Thread state holds the booking agent's full conversation history. Real guest threads would contain names, WhatsApp numbers, check-in and check-out dates, property details, and check-in instructions. Content of pre-existing real guest threads has not been read.

### F3 — Agent Execution Open to Any Caller (HIGH)

Two execution endpoints accept unauthenticated requests:

```
POST /threads/:threadId/runs/stream   — streaming agent execution
POST /threads/:threadId/runs/wait     — synchronous agent execution
```

Any caller can invoke the booking agent against any thread ID, including threads created by real guests. This enables injection of content into an active booking conversation.

### F4 — WhatsApp Webhook Service (MEDIUM)

Port 3000 serves the WhatsApp ingestion layer:

```
GET /webhook → "Verification token mismatch"
GET /health  → {"status":"ok","service":"whatsapp-webhook"}
```

The webhook verification token check is active, which blocks direct WhatsApp message spoofing. Incoming guest messages flow port 3000 to port 8000. Port 3000 is how real thread state enters the system. Port 8000 is where that state becomes readable.

---

## Stack Map

| Port | Service | Auth | Severity |
|---|---|---|---|
| 8000 | LangGraph standalone-langgraph-server v1.0.0 | None | HIGH |
| 3000 | WhatsApp webhook service | Verification token (webhook only) | MEDIUM |

---

## Data Class

Real guest threads would contain:

- Guest names and WhatsApp phone numbers
- Booking dates and property details
- Check-in and check-out instructions
- Property access codes (not verified)
- Disputes and special requests

Thread creation is confirmed unauthenticated. Content of pre-existing real guest threads has not been read. The exposure class is guest PII and operational data for an active short-term rental.

---

## CORS Wildcard: Why It Matters Here

A CORS wildcard on an internal tool is a different finding than a CORS wildcard on a booking agent handling paying guest communications.

A guest visits a compromised page. That page makes a cross-origin request to port 8000. The server allows it. No browser warning appears. The page reads the guest's booking thread, or any other thread on the server.

The agent was already open. The wildcard means a browser can reach it from any origin, not just from the operator's own frontend.

---

## Attribution

PTR record is the Hetzner generic reverse: `static.76.86.224.46.clients.your-server.de`. No domain name in any response. No TLS certificate to pivot from. No frontend served on port 80 or 443. Operator identity unknown.

---

## Thesis Placement

This host confirms the pattern across the LangGraph survey: the framework ships with no authentication, and operators ship it to production that way. This is a WhatsApp bot fielding real guest inquiries. Thread state is open.

**See also:** [LangGraph Server Survey (2026-05-25)](langgraph-server-survey-2026-05-25.md) · [LangGraph Deployment Gap — Systematic Pattern](langgraph-deployment-gap-survey-2026-05-25.md)
