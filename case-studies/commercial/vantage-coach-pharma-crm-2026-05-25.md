---
type: case-study
title: "Vantage Coach — Pharmaceutical CRM with Healthcare Client Records and Voice Endpoints Open"
date: 2026-05-25
severity: HIGH
sector: commercial
tags: [LangGraph, Redis, Supabase, healthcare, pharma, CRM, voice, Spanish, DigitalOcean, multi-tenant]
summary: "A pharmaceutical sales representative AI tool on two DigitalOcean nodes exposes a healthcare client database, conversation history, and voice endpoints without authentication. The OpenAPI spec explicitly describes access to doctor names, hospitals, visit dates, and medication discussion records."
---

# Vantage Coach — Pharmaceutical CRM with Healthcare Client Records and Voice Endpoints Open

**Date:** 2026-05-25
**Hosts:** 138.68.228.98 · 167.99.26.114
**Cloud:** DigitalOcean (AS14061), Santa Clara, California, US
**App:** Vantage Coach API v1.0.0 — LangGraph Conversational Agent
**Severity:** HIGH

---

## What Was Found

### F1 — Healthcare Client Database Accessible Without Auth (HIGH)

<!-- ksat-tag:auto-generated:start -->
## DCWF KSAT coverage

Auto-derived from DCWF AI work-role rule files (`ksat-tag`).

- **672 (AI Test & Evaluation Specialist):** S7068, S7075
- **733 (AI Risk & Ethics Specialist):** K7040, K7051
- **overlap (Common AI KSATs (all 5 roles)):** K1158, K22, K6311, K6935, K942

<!-- ksat-tag:auto-generated:end -->

Healthcare client records are accessible on port 8000. No token. No session. The OpenAPI spec describes the agent as "an AI assistant with access to weather data and comprehensive client information." The example response in the spec:

```
"I found 2 clients matching 'Dr. Smith'. Dr. John Smith is a general practitioner
at City Hospital. His last visit was on January 15, 2024, where you discussed
the new medication protocol..."
```

The `POST /chat` endpoint accepts `user_id` and `organization_id` in the request body. No JWT. No session token. No enforced credential check. The endpoint is open. Any caller who supplies a valid `organization_id` can query the client database.

```
POST http://138.68.228.98:8000/chat
Content-Type: application/json
{
  "thread_id": "test-thread",
  "message": "...",
  "user_id": "...",
  "organization_id": "..."
}
```

The spec response model includes `total_cost_usd`. The operator is billed per query regardless of who submits it.

### F2 — Conversation History Readable and Deletable Without Auth (HIGH)

```
GET http://138.68.228.98:8000/chat/history/{thread_id}
```

A valid thread ID returns the full conversation: role, content, and message UUID for every turn. Thread IDs follow the pattern in the spec examples: `user-123-session-456`. A 404 on an unknown ID returns no auth error. The endpoint is live and returns data for valid IDs.

```
DELETE http://138.68.228.98:8000/chat/history/{thread_id}
```

Delete is also open. Any caller can clear a thread without credentials.

### F3 — Voice Endpoints Open (MEDIUM)

```
POST /voicebot      — audio in, PCM audio out (STT + Agent + TTS)
POST /voicebot/text — audio in, streaming text response
```

Default language: Spanish (`"es"`). No authentication. The required fields are `audio`, `thread_id`, `user_id`, and `organization_id`. All are supplied by the caller. Accepted audio formats: wav, m4a, mp3, webm, ogg. Maximum file size: 10MB.

### F4 — Identical Build on Both Nodes (LOW)

Next.js ETag `"uh3ph94ezhie9"` is identical on both nodes. The same compiled frontend artifact runs on both IPs. Both nodes run the same LangGraph backend. Redis is confirmed connected on both.

---

## Stack

Two DigitalOcean nodes in Santa Clara. LangGraph FastAPI on ports 8000 and 8001. Next.js frontend on port 3000. Redis for session state with a 48-hour TTL. Supabase for message persistence (response fields `user_message_id` and `assistant_message_id` are Supabase UUIDs).

Rate limiting is present: 300 requests per minute per IP, 20 per minute per user, 5,000 per minute per organization. These limits do not constitute authentication. Any caller can stay within the per-IP limit and query the client database indefinitely.

---

## Data Classification

The client database holds records for individual doctors and healthcare professionals. Each record includes name, specialty, institution, visit history, and notes from sales interactions including medication discussions. The spec example is explicit on all five fields.

The application targets pharmaceutical sales representatives. The intended users query their client roster by name or specialty and review prior visit notes before calling on a doctor. Those records are accessible to any caller with an organization ID.

The GitHub URL in the spec is a placeholder (`github.com/yourorg/vantage-coach`). The contact email is `support@yourdomain.com`. Operator identity is not confirmed.
