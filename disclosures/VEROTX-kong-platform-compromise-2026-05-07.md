---
to: info@verotx.com
cc: abuse@nuclide-research.com
severity: CRITICAL
ip: 34.60.153.0
institution: "VeroTX, Inc., AI-powered enterprise procurement platform — Kong Enterprise Admin API publicly exposed without authentication on 34.60.153.0:8001, FastAPI ai-agent-server backend bypasses gateway auth on :8050, MCP server tool surface enumerable on :8051, PostgreSQL on :5432, ~11-month exposure window per Kong /license/report request counters"
status: SENT
outcome: sent
date: 2026-05-07
---

**To:** info@verotx.com
**Cc:** abuse@nuclide-research.com
**Subject:** VeroTX (34.60.153.0 / auth.verotx.com) — CRITICAL: Kong Admin API publicly exposed + AI-agent backend bypass + MCP server exposure — recommend immediate action

---

Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com

2026-05-07

This is an unsolicited good-faith coordinated-disclosure notification under the NuClide Research umbrella (CISA disclosures CVE-2025-4364, ICSA-25-140-11). Severity: **CRITICAL**. Recommend immediate-action remediation timeline rather than the standard 90-day window — see below.

I'm reaching `info@verotx.com` because I could not find a published `security@verotx.com`, `security.txt`, or VDP. Please forward to your security/engineering lead immediately. Happy to coordinate with whoever owns the gateway and platform infrastructure.

---

## Executive summary

Three separate CRITICAL exposures on `34.60.153.0` (the GCP host serving `auth.verotx.com` and `platform.verotx.com`). Combined, they constitute a **full platform compromise** vector against the VeroTX Cosmos / VeroCortex agent stack:

1. **Kong Enterprise Admin API on port 8001 is publicly reachable without authentication.** Full read/write access on `/services` (16 backend services), `/routes` (21 routes), `/plugins` (26 plugins). 11 OIDC plugin instances expose their `client_secret` and `session_secret` fields in plaintext when read via `/plugins`. With those, an attacker can mint valid Keycloak JWTs for `client_id=verotx-demo` and `client_id=kong`, or forge OIDC session cookies signed with the leaked session_secret.

2. **The FastAPI `ai-agent-server` (port 8050) does not re-validate JWTs at the backend.** The Kong gateway is supposed to enforce auth, but port 8050 is exposed directly to the internet — bypassing the gateway entirely. `GET /api/agent/agents` returns `200 OK` with `{"total_agents":0,"agents":[]}` to unauthenticated requests. The OpenAPI spec at `/openapi.json` enumerates 54 endpoints, none of which carry a `security` marker. Backend trusts Kong as the only auth layer; Kong is bypassable.

3. **The `verotx-platform` MCP server (port 8051, FastMCP 2.14.5) accepts unauthenticated `initialize` and `tools/list` JSON-RPC calls.** The full surface of 24 procurement-platform tools (`query_table`, `insert_record`, `update_record`, `delete_record`, `trigger_workflow`, `approve_task`, `invoke_agent`, `get_table_schema`, `query_analytics`, etc.) is enumerable without any bearer. Per-tool calls require `bearer_token + organization_id`, but those are obtainable via path 1.

Plus two HIGH and one MEDIUM additional issues (postgres on :5432, Keycloak admin console on :3000, GCP project number leakage via internal Cloud Run URL).

A published Metasploit module — `exploits/multi/http/kong_gateway_admin_api_rce` — directly aligns with finding 1. NuClide BARE semantic-corpus search ranks it as the top match (score 0.673).

---

## Why "immediate action" rather than 90-day

Kong's own `/license/report` endpoint reports request counters per month going back to 2025-06. The gateway has been receiving traffic since at least mid-2025, with a major customer ramp in 2026-03 (254,597 requests that month vs ~23K the prior month). The exposure window covering real customer-data traffic is approximately the last two months; the exposure window covering this gateway being internet-reachable at all is approximately eleven months. The longer this stays open, the higher the likelihood that a threat actor with less benign goals than NuClide has already pulled the same data we did.

Customer-data-handling B2B platforms (procurement / vendor / contract data) carry distinct contractual obligations to customers around exposure, so I expect your team will want to triage faster than the standard window.

---

## Findings (technical)

### CRITICAL #1 — Kong Enterprise 3.10.0.0 Admin API publicly exposed

```
$ curl -s http://34.60.153.0:8001/license/report | jq '.kong_version, .system_info.hostname'
"3.10.0.0"
"docker-kong-oidc-v10"

$ curl -s http://34.60.153.0:8001/services | jq '.data | length'
16

$ curl -s http://34.60.153.0:8001/plugins | jq '[.data[] | select(.name=="oidc") | .config.client_secret] | length'
11
```

Each OIDC plugin's `client_secret` and `session_secret` is returned in plaintext. Plugins reuse two `client_secret` values (one per Keycloak client `kong` / `verotx-demo`) and three `session_secret` values (with five plugins additionally having empty `session_secret` — separate bug class: cookie validation bypassed for those plugin instances).

### CRITICAL #2 — FastAPI ai-agent-server backend bypass

```
$ curl -sI http://34.60.153.0:8050/api/agent/agents
HTTP/1.1 200 OK
server: uvicorn
content-type: application/json
x-request-id: 88ff087f-8214-417a-9aae-7af0bbf460e6

$ curl -s http://34.60.153.0:8050/health/llm | jq .providers
[
  {"name":"anthropic","status":"healthy","details":{"configured":true}},
  {"name":"openai","status":"healthy","details":{"configured":true}},
  {"name":"google","status":"degraded","message":"API key not configured"}
]
```

The `x-request-id` value is preserved in our evidence bundle and exists in your own request logs.

### CRITICAL #3 — MCP server unauth tool enumeration

```
POST /mcp HTTP/1.1
Content-Type: application/json
Accept: application/json, text/event-stream
{"jsonrpc":"2.0","id":1,"method":"initialize",...}

→ event: message
  data: {"protocolVersion":"2024-11-05","serverInfo":{"name":"verotx-platform","version":"2.14.5"},
         "instructions":"VeroTX Platform MCP Server. ... All tools require app_slug and bearer_token..."}

→ tools/list: 24 tools exposed including query_table, insert_record, update_record, delete_record,
  trigger_workflow, approve_task, invoke_agent, get_table_schema, query_analytics
```

### HIGH — PostgreSQL 13.20 publicly exposed on port 5432
Server returns `received unencrypted data after SSL request` when SSL requested, and `server does not support SSL, but SSL was required` when sslmode=require. Password auth required, but credentials transmit in cleartext over the public internet.

### HIGH — Keycloak admin console exposed at port 3000
`http://34.60.153.0:3000/` redirects to `https://auth.verotx.com/admin/`. Identity-provider admin UIs should be VPN-restricted per Keycloak best practices.

### MEDIUM — GCP project number disclosure
Kong `/services` includes `https://rag-copilot-614313863024.us-central1.run.app/`. The numeric project ID `614313863024` identifies the operator's GCP organization for further reconnaissance.

---

## Recommendations

Immediate (within hours):

1. **Bind Kong Admin API to localhost or a private network only.** This is documented as Kong's primary security recommendation: <https://docs.konghq.com/gateway/latest/production/networking/secure-admin-api/>. Bind `admin_listen` to `127.0.0.1:8001` and proxy via Kong Manager with RBAC, or place Kong Admin behind a VPN-only firewall rule.
2. **Rotate every OIDC client_secret and session_secret on the Kong /plugins config.** Treat all 11 plugin instances as compromised.
3. **Firewall ports 8050, 8051, 8081, 8090, 8091 from public internet.** Only Kong (after step 1) should reach the upstream backends.
4. **Remove PostgreSQL :5432 and Keycloak admin :3000 from public IP exposure.**

Within a few days:

5. **Add upstream JWT validation in the FastAPI `ai-agent-server`.** Don't rely solely on Kong as the auth boundary — defense-in-depth pattern. Validate JWTs against the same Keycloak realm in middleware before any business logic.
6. **Add an MCP-protocol-level auth check before `tools/list` returns tool surface.** Even if individual tool calls require bearer_token, leaking the tool surface is a useful targeting signal for attackers.

Within a week:

7. **Audit Kong workspace history for unauthorized config changes** during the exposure window.
8. **Review LiteLLM / Anthropic / OpenAI API quota usage** for anomalous consumption that could indicate abuse during the open window.
9. **Audit application-level data access logs** for the same period for unexpected reads/writes against customer VeroTables.

Optional / posture upgrades:

10. Publish a `security.txt` and a `security@verotx.com` mailbox so future researchers can reach you without having to use `info@`.
11. Consider a coordinated-disclosure / bug bounty surface (HackerOne, Bugcrowd, or a self-hosted VDP page).

---

## Evidence preservation

A complete evidence bundle is preserved locally with a five-witness cryptographic chain:

- SHA-256 manifest (38 files)
- OpenTimestamps receipt anchored to the Bitcoin blockchain via four calendar servers
- Wayback Machine snapshots of the public-facing URLs
- Server-asserted `Date:` headers on every HTTP capture (your own server signed the timestamps)
- `X-Kong-Request-Id` and `X-Trace-Id` values that exist in your own logs (sample IDs preserved in the bundle for cross-reference)
- TLS handshake transcripts + Certificate Transparency log records (verifiable via crt.sh)

The bundle is held privately pending your remediation; we are not publishing it. Available on request via secure channel — happy to use whatever transport works for your security team (PGP-encrypted email, Signal, encrypted ZIP via password channel, etc.).

---

## IOCs

| Type | Value |
|---|---|
| Affected host | `34.60.153.0` (Google Cloud, GCP project number `614313863024`) |
| Hostnames | `auth.verotx.com`, `platform.verotx.com` |
| Adjacent exposed services | `34.60.153.0:{3000,3002,5432,8001,8050,8051,8081,8090}` |
| Service stack | Kong Enterprise `3.10.0.0` (`docker-kong-oidc-v10`), FastAPI `ai-agent-server 2.0.0`, FastMCP `verotx-platform 2.14.5`, PostgreSQL `13.20` |
| Sample request IDs preserved | `88ff087f-8214-417a-9aae-7af0bbf460e6`, `454cb45a-a5b2-47b5-901e-d68c846d1177`, `0a792ecc-cb1d-4daf-9658-4f22809fd74d`, etc. |
| Kong node ID | `54465d61-9618-4357-acfe-1fed38621aa0` |
| OIDC realm | `VeroTX` (`https://auth.verotx.com/realms/VeroTX/.well-known/openid-configuration`) |
| Certificate authorities | Let's Encrypt E7/E8, Google Trust Services WE1 |

---

## Reference

- BARE semantic-corpus match: `exploits/multi/http/kong_gateway_admin_api_rce` (Metasploit), score 0.673
- Kong Admin API hardening guide: <https://docs.konghq.com/gateway/latest/production/networking/secure-admin-api/>
- Keycloak admin endpoints best practice (VPN-restricted): <https://www.keycloak.org/server/reverseproxy>
- FastAPI dependency-based auth pattern: <https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/>
- MCP Authorization spec (2024-11-05+): <https://modelcontextprotocol.io/specification/server/authorization>

---

P.S. — I noticed Rick Bradley wears one of Jerry Garcia's silk neckties (the Grateful Dead-licensed line). Good taste. If your team prefers an out-of-band channel for the evidence handoff, that's the visual recognition cue we can use; otherwise plain email at `nicholas@nuclide-research.com` is fine.

Regards,
Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com
https://nuclide-research.com
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT
