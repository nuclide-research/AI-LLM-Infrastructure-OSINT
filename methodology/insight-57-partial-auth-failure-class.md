---
title: "Partial-auth failure: auth on collection endpoints, none on individual resource endpoints"
insight_number: 57
date: 2026-05-25
tags:
  - methodology
  - authentication
  - partial-auth
  - langgraph
  - fastapi
---

# Insight #57: Partial-Auth Failure Class

**Date codified**: 2026-05-25
**Survey anchor**: Survey-38 LangGraph — Stock.ai / EMOR AI (20.193.252.230)
**File**: `case-studies/commercial/stock-ai-emor-partial-auth-2026-05-25.md`

---

## The Finding

A developer implements authentication on collection/list endpoints and leaves individual resource endpoints open. The Swagger UI shows padlock icons on list endpoints. The individual resource endpoints carry no security definition.

Confirmed pattern (Stock.ai / EMOR AI):

```
GET  /conversations        → 401 (JWT enforced)
GET  /conversations/{id}   → 200 (no auth)
GET  /portfolio            → 401 (JWT enforced)  
GET  /portfolio/{user_id}  → 200 (no auth)
GET  /pdf                  → 401 (JWT enforced)
GET  /pdf/{filename}       → 200 (no auth)
DELETE /conversations/{id} → 200 (no auth)
```

62 proprietary Arihant Capital research PDFs were accessible at `/pdf/{filename}` without credentials.

---

## Why This Happens

FastAPI and similar frameworks implement auth as a dependency injected at the route level. A developer securing endpoints one-by-one will apply the dependency to the first endpoint they write (typically the list/collection route) and omit it from the individual resource routes added later. Swagger UI renders the lock icon per-route from the `security` definition — its presence on some routes creates a false impression of comprehensive coverage.

This is distinct from the pure no-auth case (LangGraph dev mode, Ollama default). The operator invested effort in authentication. The partial result is worse than no auth in one sense: it creates a false sense of coverage that delays remediation.

---

## Detection Heuristic

1. Swagger UI shows padlock icons on list endpoints → flag as candidate
2. Probe individual resource endpoints without credentials
3. If collection endpoint returns 401 but `/collection/{id}` returns 200 → confirmed partial-auth failure

The presence of a Swagger UI is itself a signal: operators who expose API docs are more likely to have implemented auth in layers (docs → auth → resources) than in one pass.

---

## Verification Anchor

`GET /pdf/{filename}` returned HTTP 200 with 448KB PDF content (Arihant Capital analyst reports) without credentials. `GET /pdf` returned 401. Both probed against the same host within the same session.

---

## Relation to Other Insights

- **Insight #55** (auth-gated API, signup open): auth at the API layer coexists with open signup. Partial-auth is a different failure: auth on some routes, none on adjacent routes in the same service.
- **Insight #51** (port is not identity): the auth-on-list, none-on-resource pattern can appear even when the port is correctly identified as a protected service.

---

## Remediation Class

Apply the auth dependency uniformly across all routes via a router-level dependency, not route-by-route. In FastAPI: `router = APIRouter(dependencies=[Depends(get_current_user)])`. Route-level dependency injection is the failure vector.
