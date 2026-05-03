# n8n on Public Cloud — Auth Posture Survey

_NuClide Research · 2026-05-03_

---

## Summary

Sweep of 1.83M IPs across 28 cloud-provider /16 ranges (DigitalOcean, Hetzner, Vultr) on port 5678 → 5,885 live hosts → **1,006 confirmed n8n instances** via `/rest/settings` → `"timezone"` fingerprint. **Zero unauthenticated, exploitable instances.**

This matches the Flowise result: orchestration-layer tools on cloud platforms are uniformly auth-protected. n8n made authentication mandatory in v0.166.0 (September 2022) and operator adoption on the three largest self-hosting clouds appears complete.

---

## Methodology

```
masscan -iL <28 cloud /16 CIDRs> -p 5678 --rate 6000
  → 5,885 unique live hosts on :5678

httpx -p 5678 -path /rest/settings -mc 200 -ms '"timezone"'
  → 1,011 n8n instances confirmed

aiapp-probe.py (deep enumeration)
  → /api/v1/workflows, /api/v1/credentials, /rest/workflows,
    /rest/credentials, /api/v1/executions
```

**Why `/rest/settings` is the definitive fingerprint:**
Returns a JSON object containing n8n-specific fields: `executionMode`, `endpointWebhook`, `endpointMcp`, `databaseType`, `timezone`. No other software in the wild returns this schema on this path. The `/healthz` → `{"status":"ok"}` alternative was rejected — 5,139 matches vs 1,011 for `/rest/settings`, confirming ~80% false-positive rate on the generic healthz filter.

---

## Findings Summary

| Metric | Value |
|---|---|
| Live hosts on :5678 | 5,885 |
| Confirmed n8n (via `/rest/settings`) | 1,006 |
| Unauthenticated `/api/v1/credentials` | **0** |
| Unauthenticated `/api/v1/workflows` | **0** |
| SPA catch-all false positives | 3 |
| Instances with MCP endpoint exposed | ~400 (estimated from settings sample) |

---

## SPA Catch-All Anti-Pattern

Three instances (`167.71.196.43`, `167.71.78.254`, `178.62.181.200`) returned HTTP 200 on `/api/v1/credentials` and `/api/v1/workflows` — but the response body was the n8n Vue SPA HTML, not JSON. These instances serve the frontend on every path, making HTTP status codes useless as auth indicators for these endpoints.

Correct verification: check `Content-Type: application/json` and parse response before concluding a credential endpoint is open.

---

## Notable Observations

**Database types (from `/rest/settings`):**
- SQLite: majority of instances (single-node, personal/dev deployments)
- PostgreSQL (`"databaseType":"postgresdb"`): minority — production multi-tenant setups

**MCP endpoints:**
Newer n8n instances (v1.x) expose `"endpointMcp": "mcp"` in settings. This wires n8n's 400+ integrations as MCP tools accessible to LLMs. The MCP endpoint itself (`/mcp/`) requires the same auth as the rest of the API — but the existence of the endpoint is disclosed unauthenticated via `/rest/settings`.

**Version signal:**
- Instances with `"inE2ETests"`, `"isDocker"`, `"endpointForm"` fields → n8n ≥1.0
- Instances without those fields → legacy n8n <1.0 (pre-2023)
- Both cohorts returned 401/403 on all data endpoints

---

## Why This Matters (Even as a Negative Result)

n8n's credential store, when exposed, returns names and types for every stored integration: OAuth tokens for Google/Slack/GitHub, API keys for OpenAI/Anthropic/Stripe, database connection strings, SSH credentials. The `/api/v1/credentials` endpoint in unauth configurations is a single-request multi-service compromise.

The empirical result — 0 of 1,006 cloud-hosted instances exposed — indicates mandatory auth adoption is near-complete on cloud platforms. The risk surface has moved to:

- **Self-hosted on bare metal / home servers** — different operator population, lower update cadence
- **Internal network deployments** — not reachable from public internet but accessible post-lateral-movement
- **Webhook endpoints** — n8n webhooks (`/webhook/`) execute workflows and are intentionally public; misconfigured webhook triggers are a separate attack surface

---

## Platform Posture Comparison

| Platform | Confirmed | Unauth | Notes |
|----------|-----------|--------|-------|
| Flowise | 43 | 0 (0%) | Post-CVE-2024-36420 hygiene |
| n8n | 1,006 | 0 (0%) | Mandatory auth since v0.166.0 |
| Qdrant | 61 | 61 (100%) | Auth off by default, no change |
| Elasticsearch | 42 | 42 (100%) | 7.x default-no-auth still common |

Pattern: **orchestration tools have hardened; data layer tools haven't.**

---

## Probe Tooling

- `data/aiapp-probe.py` — n8n prober: `/rest/settings` fingerprint, dual-path credential/workflow enumeration (`/api/v1/` and `/rest/`), execution history sampling
- httpx filter: `httpx -p 5678 -path /rest/settings -mc 200 -ms '"timezone"'`

---

## Discoverer

NuClide Research — nicholas@nuclide-research.com

No data was accessed, modified, or exfiltrated. All instances probed only on documented endpoints to determine auth posture.
