# Vantage Coach Cluster — Complete Investigation Notes

**Hosts:** 138.68.228.98 · 167.99.26.114
**Cloud:** DigitalOcean (AS14061) — Santa Clara, California, US
**App:** Vantage Coach API — LangGraph Conversational Agent (pharmaceutical/healthcare CRM)
**Status:** FULLY MAPPED
**Priority:** 6

---

## Confirmed Services

| Host | Port | Service | Auth |
|---|---|---|---|
| 138.68.228.98 | 8000 | LangGraph FastAPI — "Vantage Coach API" v1.0.0 | NONE |
| 138.68.228.98 | 8001 | LangGraph FastAPI — identical | NONE |
| 138.68.228.98 | 3000 | Next.js frontend | UNKNOWN |
| 167.99.26.114 | 8000 | LangGraph FastAPI — identical | NONE |
| 167.99.26.114 | 8001 | LangGraph FastAPI — identical | NONE |
| 167.99.26.114 | 3000 | Next.js frontend | UNKNOWN |

---

## App Description (from OpenAPI spec)

"Production-ready AI assistant with access to weather data and comprehensive client information."

The OpenAPI spec example explicitly shows healthcare client records: "Dr. John Smith is a general practitioner at City Hospital. His last visit was on January 15, 2024, where you discussed the new medication protocol."

This is a **pharmaceutical sales rep assistant** or **healthcare CRM AI agent**. The agent has direct access to a database of doctor/healthcare client records. `organization_id` isolation is the multi-tenancy model.

Language: Spanish (default `"es"` on voice endpoints).

---

## Confirmed Findings

### F1 — Healthcare Client Database Accessible Without Auth (HIGH)

POST /chat accepts `user_id` + `organization_id` as parameters in the request body — no JWT, no session, no enforced credential check. Any caller can submit queries against the client database by supplying a valid organization_id.

The agent has tool access to "client database" per the OpenAPI description. Successful queries return client records including names, specializations, locations, visit history, and discussion notes.

### F2 — Conversation History Readable Without Auth (HIGH)

```
GET /chat/history/{thread_id}
→ 404 "Conversation not found" for unknown IDs (no auth error)
```

Thread IDs from examples: `user-123-session-456` — guessable pattern from user_id + session. Real thread history contains full conversation turns including any client records retrieved by the agent.

DELETE /chat/history/{thread_id} also open — no auth.

### F3 — Voice Endpoints Open (MEDIUM)

```
POST /voicebot       — audio in, PCM audio out (STT + Agent + TTS)
POST /voicebot/text  — audio in, streaming text out
```

Required fields: audio, thread_id, user_id, organization_id. Default language: Spanish. No auth gate.

### F4 — Identical Build on Both Nodes (LOW)

Next.js ETag `"uh3ph94ezhie9"` identical on both IPs — same compiled frontend artifact, same operator, same deployment template.

---

## Endpoint Map

| Method | Path | Auth |
|---|---|---|
| GET | / | NONE |
| GET | /health | NONE |
| POST | /chat | NONE (user_id+org_id in body, not enforced) |
| GET | /chat/history/{thread_id} | NONE |
| DELETE | /chat/history/{thread_id} | NONE |
| POST | /voicebot | NONE |
| POST | /voicebot/text | NONE |

---

## Architecture

- Backend: FastAPI/LangGraph
- State: Redis (48-hour TTL, confirmed connected on both nodes)
- Persistence: Supabase (UUID message IDs in response)
- Rate limiting: 300 req/min per IP, 20/min per user, 5,000/min per org (rate limits, not auth)
- Multi-tenancy: org_id in request body
- Cost tracking: total_cost_usd returned per response

---

## Pending

- [ ] Operator attribution — GitHub URL uses "yourorg" placeholder, contact email "yourdomain.com" — template placeholders, not real domains
- [ ] What database system holds the client records?
