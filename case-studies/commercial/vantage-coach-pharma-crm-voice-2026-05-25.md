---
type: case-study
title: "Vantage Coach — Pharma CRM Agent, Open Voice Endpoints, Healthcare Client Records"
date: 2026-05-25
severity: HIGH
sector: commercial
tags: [LangGraph, FastAPI, Redis, Supabase, pharmaceutical, healthcare-CRM, voice, Spanish, DigitalOcean, agent-framework]
summary: "A Spanish-language pharmaceutical CRM AI agent runs on two DigitalOcean nodes with no authentication. The agent has tool access to a healthcare client database. Voice endpoints accept audio queries against that database without credentials."
---

# Vantage Coach — Pharma CRM Agent, Open Voice Endpoints, Healthcare Client Records

**Date:** 2026-05-25
**Targets:** 138.68.228.98, 167.99.26.114
**ASN:** AS14061, DigitalOcean — Santa Clara, California, US
**Severity:** HIGH

---

## What Was Found

### F1 — Healthcare CRM Agent Accessible Without Auth (HIGH)

<!-- ksat-tag:auto-generated:start -->
## DCWF KSAT coverage

Auto-derived from DCWF AI work-role rule files (`ksat-tag`).

- **672 (AI Test & Evaluation Specialist):** K7003, K7004, S7068, S7075, T5904, T5919
- **733 (AI Risk & Ethics Specialist):** K7040, K7051
- **overlap (Common AI KSATs (all 5 roles)):** K1158, K22, K7003, K942

<!-- ksat-tag:auto-generated:end -->

Two ports respond on each node. No authentication on either:

```
GET http://138.68.228.98:8000/
→ HTTP 200
→ {"title": "Vantage Coach API", "version": "1.0.0"}

GET http://138.68.228.98:8001/
→ HTTP 200
→ (identical response)
```

The OpenAPI spec at `/docs` describes the agent as "Production-ready AI assistant with access to weather data and comprehensive client information."

The spec example makes the data class explicit:

```
"Dr. John Smith is a general practitioner at City Hospital.
His last visit was on January 15, 2024, where you discussed
the new medication protocol."
```

This is a pharmaceutical sales rep assistant. The LangGraph agent has tool access to a database of doctor and healthcare client records. Multi-tenancy is `organization_id` passed in the request body.

`POST /chat` takes `user_id` and `organization_id` as body parameters. No JWT. No session token. No enforced credential check. Any caller with a valid `organization_id` can submit queries and retrieve client records.

The response includes `total_cost_usd` per request. This is production billing infrastructure.

### F2 — Conversation History Readable and Deletable Without Auth (HIGH)

```
GET  /chat/history/{thread_id}  → 404 "Conversation not found" (no auth error)
DELETE /chat/history/{thread_id} → open
```

The 404 on an unknown ID confirms the endpoint exists and is reachable. No auth gate fires. Thread IDs follow the pattern `user-123-session-456`, constructed from `user_id` and session identifier. Guessable.

A thread that exists returns full conversation history and any client records the agent retrieved during that session.

### F3 — Voice Endpoints Query the Same Database Without Auth (HIGH)

```
POST /voicebot       — audio in, PCM audio out (STT + Agent + TTS pipeline)
POST /voicebot/text  — audio in, streaming text out
```

Required fields: `audio`, `thread_id`, `user_id`, `organization_id`. Default language: Spanish. No auth gate.

A caller sends audio and receives spoken synthesis of client records. Same database. Same unauth access. Different interface.

### F4 — Identical Build Across Both Nodes (LOW)

Next.js ETag `"uh3ph94ezhie9"` is identical on 138.68.228.98:3000 and 167.99.26.114:3000. Same compiled frontend artifact. Same operator. Same deployment template deployed twice.

Both nodes run FastAPI/LangGraph on ports 8000 and 8001. Both are confirmed unauth. Redis state backend is connected on both (48-hour TTL). Supabase handles message persistence (UUID message IDs in API responses).

---

## Stack Map

| Host | Port | Service | Auth | Severity |
|---|---|---|---|---|
| 138.68.228.98 | 8000 | LangGraph FastAPI | None | HIGH |
| 138.68.228.98 | 8001 | LangGraph FastAPI | None | HIGH |
| 138.68.228.98 | 3000 | Next.js frontend | Not probed | UNRATED |
| 167.99.26.114 | 8000 | LangGraph FastAPI | None | HIGH |
| 167.99.26.114 | 8001 | LangGraph FastAPI | None | HIGH |
| 167.99.26.114 | 3000 | Next.js frontend | Not probed | UNRATED |

---

## Architecture

Backend: FastAPI + LangGraph. State: Redis (48-hour TTL, confirmed connected on both nodes). Persistence: Supabase. Rate limiting is present: 300 req/min per IP, 20/min per user, 5,000/min per org. Rate limits are not authentication.

`org_id` is passed in the request body with no credential binding. Tenant isolation depends entirely on the caller supplying a correct value.

---

## Attribution

GitHub URL in the spec uses `"yourorg"` placeholder. Contact email uses `"yourdomain.com"`. These are template placeholders, not resolved operator identity. The app title "Vantage Coach" is the only named artifact. Operator is unresolved.

DigitalOcean Santa Clara, AS14061. Two nodes. Same artifact. Both nodes serve production billing responses (`total_cost_usd`).

---

## Thesis Placement

The agent holds doctor names, specializations, hospital affiliations, visit dates, and medication discussion notes. Whether the production deployment holds real client records beyond the OpenAPI example is unverified. The surface is open. The access path is confirmed.

The voice layer adds a second unauth interface to the same database. `/voicebot` returns spoken synthesis of client records with no credential gate.

**See also:** [LangGraph Server Survey (2026-05-25)](langgraph-server-survey-2026-05-25.md) · [LangGraph Deployment Gap — Systematic Pattern](langgraph-deployment-gap-survey-2026-05-25.md)
