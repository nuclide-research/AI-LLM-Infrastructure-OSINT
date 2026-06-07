---
title: "Sanio AI — Collision AgentOS / Walmart Pipeline Exposure"
date: 2026-05-28
operator: Sanio AI (sanio.ai)
host: 5.78.111.11
cloud: Hetzner DE, AS24940
attribution: collision.sanio.ai TLS CN (Let's Encrypt E8, issued 2026-05-13)
severity_max: CRITICAL
findings: 5
tags: [llmjacking, credential-leak, temporal, agno, elasticsearch, walmart, collision-data, unauth-agent-invocation]
---

# Sanio AI — Collision AgentOS / Walmart Pipeline Exposure

**Date:** 2026-05-28  
**Host:** 5.78.111.11 (Hetzner DE, AS24940)  
**Operator:** Sanio AI (sanio.ai) — AI services contractor  
**Attribution:** `collision.sanio.ai` TLS cert CN resolves to this IP. Let's Encrypt E8, issued 2026-05-13, valid through 2026-08-11.  
**Connected host:** 34.57.75.173 (GCP) — same Agno framework, different client stack ("AIRIAD Risk Advisor")

---

## Discovery

Surface identified in session 43 (cat-06 stragglers survey) via Shodan dork `port:7777 http.html:"agno"`. Prior session confirmed the host as unauth Agno on port 7777 with road collision data in scope. This session ran five parallel agents for full stack enumeration.

<!-- ksat-tag:auto-generated:start -->
## DCWF KSAT coverage

Auto-derived from DCWF AI work-role rule files (`ksat-tag`).

- **672 (AI Test & Evaluation Specialist):** K7003, K7004, S7068, S7070, S7075, T5904, T5919
- **733 (AI Risk & Ethics Specialist):** S7067, T5854, T5868
- **overlap (Common AI KSATs (all 5 roles)):** K108, K1158, K22, K6311, K6935, K7003

<!-- ksat-tag:auto-generated:end -->

---

## Surface Map

| Port | Service | Auth | Severity |
|------|---------|------|----------|
| 7777 | Agno AgentOS (uvicorn/FastAPI) | None enforced | CRITICAL |
| 8000 | Collision Analytics API (uvicorn/FastAPI) | None | HIGH |
| 8080 | Temporal Web UI + REST API | None | CRITICAL |
| 7233 | Temporal gRPC frontend | None | MEDIUM |
| 3000 | Agent UI (Next.js) | None | LOW |
| 5432 | PostgreSQL | Auth required | INFO |
| 22 | SSH | Auth required | INFO |
| 80 | Caddy (default page, no routes) | N/A | INFO |

---

## Finding 1 — Elasticsearch Credentials in Temporal Workflow Inputs

**Severity: CRITICAL**  
**Verified: credentials extracted from unauth endpoint; ES cluster access not exercised**

Temporal's web UI (port 8080) requires no authentication. The REST API at `/api/v1/namespaces/default/schedules` returns all three Walmart workflow schedules in full, including the base64-encoded JSON startup parameters. Decoded:

```json
{
  "es_host": "https://5.78.67.23:9200",
  "es_user": "elastic",
  "es_password": "[REDACTED]",
  "es_source_index": "sn-normalized-products-voomi-test-catalog",
  "es_target_index": "sn-normalized-products-voomi-walmart-catalog"
}
```

Same credentials appear in all three schedule configs. The `elastic` user is Elasticsearch's built-in superuser. The target host (5.78.67.23) is a separate Hetzner IP in the same /16 block.

Index names confirm the data class: `voomi-test-catalog` and `voomi-walmart-catalog`. The "voomi" brand and "sn-normalized-products" prefix indicate a product search normalization pipeline feeding a Walmart supplier/catalog integration. "VA" in `WalmartVAWorkflow` is consistent with Vendor Analytics.

**Three-stage daily pipeline** (all ran successfully 2026-05-27):

| Workflow | Type | Schedule (IST) | Run count |
|----------|------|---------------|-----------|
| walmart_matching_flow | WalmartMainWorkflow | 5:30 PM | 57 actions (22 skipped) |
| walmart_postprocessing_flow | WalmartPostfilterWorkflow | 6:30 PM | 80 actions |
| walmart_va_flow | WalmartVAWorkflow | 8:30 PM | 80 actions |

All three running since 2026-03-10 (~78 days). IST scheduling confirms an India-based team. The operator is a third-party contractor, not Walmart internal — Walmart does not use Hetzner DE for production workloads.

---

## Finding 2 — Unauthenticated Agent Invocation (LLMjacking)

**Severity: HIGH**  
**Verified: POST confirmed 200, GPT-4-turbo response received via OpenRouter**

The Agno server declares `HTTPBearer` security in its OpenAPI spec. The check is not enforced. Any caller can invoke any of three agents with no token:

```
POST http://5.78.111.11:7777/agents/postgresql-data-agent/runs
Content-Type: multipart/form-data
(field: message, no Authorization header)

→ HTTP 200, GPT-4-turbo response via OpenRouter
  input_tokens: 519, output_tokens: 17
  run_id, session_id, OpenRouter generation ID in body
```

Model: `openai/gpt-4-turbo` via OpenRouter. Token consumption per call: 2,800-3,600 tokens. No rate limiting. No quota gate. Sustained abuse drains the operator's OpenRouter account at GPT-4-turbo pricing.

Every run response includes the full system prompt verbatim in the `messages[]` array, leaking database schema context, filter logic (`inside_concord=True`, `STATE_HWY_IND='City Road'`, `COLLISION_SEVERITY IN ('Fatal','Severe Injury','Visible Injury')`), and record count (~1,457 collisions).

**Three agents, all invocable without auth:**
- `router-agent` — routes queries to PDF or PostgreSQL agents
- `pdf-knowledge-agent` — RAG over PDFs (knowledge base currently empty)
- `postgresql-data-agent` — natural-language queries into the collision PostgreSQL DB

---

## Finding 3 — Collision Database Exposed via REST API

**Severity: HIGH**  
**Verified: GET /api/map-collisions returned full 1,456-record dataset**

A second API server on port 8000 exposes the full Concord CA road collision dataset without authentication:

```
GET http://5.78.111.11:8000/api/map-collisions
→ HTTP 200, 1,456 records

Sample:
{
  "case_id": "8298886",
  "lat": 37.94841293,
  "lon": -121.9563502,
  "collision_severity": "Visible Injury",
  "type_of_collision": "Vehicle/Pedestrian",
  "primary_rd": "ARIZONA DR",
  "secondary_rd": "WASHINGTON BLVD",
  "collision_date": "2017-02-03",
  "pedestrian": "Yes",
  "bicycle": "No",
  "motorcycle": "No",
  "alcohol_involved": "No"
}
```

191 road names, GPS coordinates, California CASE_ID identifiers, severity classes, collision dates (2014-2025). Countermeasure recommendations per road segment also unauth-accessible via `/api/road-recommendations/{road}`.

Top corridors: Clayton Rd (219 collisions), Willow Pass Rd (131), Concord Blvd (107), Monument Blvd (87), Treat Blvd (64).

The data derives from California's SWITRS database (public record), but this is the operator's processed analysis product — including AI-generated countermeasures — not raw public data.

---

## Finding 4 — Temporal gRPC Open Without Auth

**Severity: MEDIUM**  
**Verified: gRPC health check SERVING, AdminService listed via reflection**

Port 7233 (Temporal gRPC frontend) is open to the internet with no authentication. Services exposed include `WorkflowService`, `OperatorService`, and `AdminService`. The Temporal CLI pointed at this endpoint can retrieve full workflow execution history for all 57-80+ pipeline runs, including input/output payloads per activity.

Temporal 1.22.0 is 9 minor versions behind current (1.31.0, released 2026-04-29).

---

## Finding 5 — System Prompt Exfiltration on Every Run

**Severity: MEDIUM**  
**Verified: system prompt confirmed verbatim in messages[] array**

Every agent run response returns the full internal system prompt. The prompt discloses the database schema context, SQL filter conditions, record count, and routing logic configured by the operator. Combined with unauth invocation (Finding 2), the full internal blueprint of the system is readable on the first unauthenticated request.

---

## Operator Attribution

**Sanio AI** (`sanio.ai`) — training data platform and AI services contractor. Site fronts on Framer CDN. Registrant behind DomainsByProxy privacy shield.

**Client work confirmed:**
- City of Concord, CA road safety analysis — collision data, GPS, countermeasures
- Walmart data pipeline — product catalog normalization, vendor analytics (IST scheduling, "Voomi" index brand)

**Connected host:** 34.57.75.173 (GCP, US) — runs "AIRIAD Risk Advisor" on the same Agno framework. Internal PM risk dashboard for a software delivery company. Both hosts use the same Agno v2.6.1 deployment pattern. Attribution confidence: HIGH for Sanio AI operating both.

**Voomi brand:** appears in ES index names (`voomi-test-catalog`, `voomi-walmart-catalog`). Either a Sanio AI product line name or a third company whose catalog data Sanio processes for Walmart. Not independently confirmed.

---

## Agent Chain

```
Unauth Temporal REST API (port 8080)
  → GET /schedules → base64-decode workflow inputs
  → ES credentials (elastic / [redacted]) for 5.78.67.23:9200
  → Walmart catalog data (test + prod indexes)

Unauth Agno API (port 7777)
  → POST /agents/*/runs → GPT-4-turbo via OpenRouter
  → System prompt + collision data via postgresql-data-agent
  → LLMjacking + data access + schema disclosure

Unauth Temporal gRPC (port 7233)
  → temporal CLI → full workflow history (57-80 runs)
  → input/output payloads of Walmart pipeline runs
```

---

## Pivot Avenues

1. **5.78.67.23:9200** — ES host in same /16. Credentials in hand. Verify index existence + record count via `GET /_cat/indices` (access not exercised).
2. **Temporal CLI on port 7233** — `temporal --address 5.78.111.11:7233 workflow show --workflow-id walmart_va_flow-workflow-2026-05-27T15:00:00Z` pulls 17-event history with activity payloads.
3. **Cert transparency on 5.78.67.23** — TLS cert CN will surface the Voomi/Sanio domain footprint. `crt.sh/?q=5.78.67.23` or Shodan cert pivot.
4. **AIRIAD cert pivot** — 34.57.75.173:7777 runs same framework. TLS on 443 timed out; try Shodan cert lookup for the GCP IP to surface the AIRIAD domain.
5. **`crt.sh/?q=%.sanio.ai`** — map full Sanio subdomain infrastructure. Any staging/dev instances?
6. **`walmart_matching_flow` overlap anomaly** — 22 of 57 runs (39%) skipped due to overlap. Either the workflow runs fast and re-triggers, or workers were down for stretches. Temporal history would confirm which.

---

## Artifacts

- `recon/sanio-5.78.111.11-2026-05-28/findings-breakdown.txt` — plain-English findings (5 findings)
- Agent outputs: Agno manifest, Temporal schedule decodes, port sweep, JS bundle, attribution
