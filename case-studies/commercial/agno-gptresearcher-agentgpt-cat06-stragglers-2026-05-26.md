# Cat-06 Stragglers: Agno Auth-Off-Default, GPT Researcher 14 Unauth, Walmart Temporal Exposure

**Survey:** Category 06 — Agent Frameworks (stragglers)  
**Date:** 2026-05-26  
**Platforms:** CrewAI Studio, SuperAGI, Agno (formerly Phidata), GPT Researcher, AgentGPT, Devika  
**Method:** Shodan harvest (Playwright) + aimap v1.9.32 + manual verification

---

## Summary

Agno ships with no authentication. The playground server (`uvicorn`, port 7777) returns full agent manifests and run histories to any caller. Three confirmed Agno deployments expose AI agents with live database, email, call-transcript, and document access.

GPT Researcher has no auth concept. 14 of 21 Shodan-seeded instances confirmed on port 8000. The platform accepts research task submissions and exposes output files without credentials.

CrewAI Studio is Shodan-dark. No direct HTML or title fingerprint is indexed; the SSL cert CN dork returns only vendor infrastructure (crewai.com AWS fleet). Zero self-hosted confirmed.

SuperAGI: all 14 Shodan hits are the commercial SaaS platform. Auth enforced at `/auth_users/login`. No self-hosted exposures found.

---

## F1: Agno auth-off-default — 3 confirmed unauth instances (HIGH)

Agno (formerly Phidata) ships with no authentication on the playground server. `/openapi.json` is world-readable. `/agents` returns the full agent manifest including each agent's name, description, and implicitly its data-source access. No token, no session, no prompt.

**Unauthenticated endpoints confirmed:**
- `GET /` — `{"name":"...", "id":"...", "version":"1.0.0"}` — service identity
- `GET /openapi.json` — full API spec with all paths
- `GET /agents` — agent manifest (name, description, data sources)
- `GET /teams` — team definitions
- `GET /workflows` — workflow definitions
- `POST /agents/{id}/runs` — invoke agent (ethical-stop; not exercised)

---

## F1a: Collision Analysis AgentOS — Hetzner/DE (CRITICAL)

Host: `5.78.111.11`  
Provider: Hetzner Online GmbH, Germany  
PTR: `static.11.111.78.5.clients.your-server.de`  
API title: `Collision Analysis AgentOS`  
Agno: port 7777 (uvicorn) + Agent UI port 3000 (Next.js)

Three agents, all enumerable without authentication:

| Agent | Data access |
|---|---|
| Router Agent | Routes queries to specialist agents |
| PDF Knowledge Agent | Reads PDF document knowledge base |
| **PostgreSQL Data Agent** | **Direct database queries** |

The PostgreSQL Data Agent gives any unauthenticated caller natural-language access to the backend database. The `/api/summary` endpoint on port 8001 (Collision Analytics API, co-located) returns the dataset scope: 1,532 road collision records (2014–2025), 56 killed, 314 unique corridors, 1,155 intersections. An LLM-powered countermeasures endpoint (`/api/llm-sitrep`) and countermeasure recommendation chain are accessible without credentials.

The agent manifest, the collision statistics, and the LLM endpoints are all open. The database connection behind the PostgreSQL Data Agent is not confirmed without invoking a run (ethical-stop).

**Compound exposure on same host:**

Temporal Web on port 8080 — fully unauthenticated. Active workflows:

| Workflow ID | Type | Status |
|---|---|---|
| `temporal-sys-scheduler:walmart_va_flow` | temporal-sys-scheduler-workflow | Running |
| `temporal-sys-scheduler:walmart_postprocessing_flow` | temporal-sys-scheduler-workflow | Running |
| `temporal-sys-scheduler:walmart_matching_flow` | temporal-sys-scheduler-workflow | Running |
| `walmart_va_flow-workflow-2026-05-26T15:00:00Z` | WalmartVAWorkflow | Completed |
| `walmart_postprocessing_flow-workflow-2026-05-26T13:00:00Z` | WalmartPostfilterWorkflow | Completed |
| `walmart_matching_flow-workflow-2026-05-26T12:00:00Z` | WalmartMainWorkflow | Completed |

Three active Walmart data pipelines running on a public Hetzner VPS. The Temporal API at `/api/v1/namespaces/default/workflows` returns all execution history, schedules, and run IDs without credentials.

Two separate systems — road safety analytics and Walmart retail data pipelines — share a single host with no authentication on either.

---

## F1b: AIRIAD Risk Advisor — GCP/US (CRITICAL)

Host: `34.57.75.173`  
Provider: Google Cloud Platform, US  
API title: `AIRIAD Risk Advisor`  
Agno: port 7777

Five agents, all enumerable without authentication:

| Agent | Description |
|---|---|
| ContractAgent | Parse project contract documents (SOW, Change Requests, BRD) |
| EmailsAgent | Analyze client email threads for risk signals (RED/YELLOW/GREEN) |
| CallsAgent | Analyze Fireflies call transcripts for project risk signals |
| DeliveryAgent | Analyze Asana task snapshots and Smartsheet timeline data |
| AdvisorAgent | Synthesize sub-agent reports into project risk assessment |

The agent descriptions confirm the data sources each agent accesses: SOW documents, client email threads, Fireflies call transcripts, Asana project data, Smartsheet timelines. Any caller can enumerate this manifest and invoke agent runs against client project data without credentials.

The `/agents` endpoint returns descriptions sufficient to establish that live client engagement data is in scope for this system.

---

## F1c: agno-playground — Alibaba Cloud/CN (MED)

Host: `212.0.123.62:3000`  
Provider: Alibaba Cloud, China  
API title: `agno-playground`  
Agno: port 7777 (uvicorn)

Generic Agno playground deployment. No named agents returned from `/agents` at enumeration time. No client data established. Default install pattern, no auth.

---

## F2: GPT Researcher — 14 confirmed unauth instances (HIGH)

**Population:** `http.html:"gpt-researcher" port:8000` = 21 Shodan results. 14/21 confirmed.

GPT Researcher (assafelovic/gpt-researcher) has no authentication. The platform accepts a research query, dispatches web searches, synthesizes a report, and returns a markdown document. No token required to submit or retrieve research.

**Confirmed port:** 8000 (FastAPI). HTML title `<title>GPT Researcher</title>` confirmed on all 14.

**Impact:** Any caller can submit a research task, consuming operator LLM quota and web-search API credits. Output files, if served, disclose prior research topics.

`gpt_researcher` (Python module name, underscore) returns 0 Shodan hits — the underscore form is not indexed as a token boundary. `gpt-researcher` (hyphen) on port 8000 is the canonical dork.

**Sample confirmed hosts:** `64.188.23.206`, `124.222.235.35`, `49.13.4.239`, `47.94.103.159`, `91.98.193.213`, `5.78.113.154` (6 of 14 listed).

---

## F3: AgentGPT — 3 confirmed, OAuth misconfigured (LOW)

**Hosts:** `129.146.84.38:3000`, `132.145.106.176:3000`, `158.247.192.218:3000`  
**Provider distribution:** Oracle Cloud (2), diverse (1)

All three run NextAuth with Google and GitHub OAuth providers. All three have OAuth callback URLs pointing to `localhost:3000`:

```json
{
  "google": {
    "signinUrl": "http://localhost:3000/api/auth/signin/google",
    "callbackUrl": "http://localhost:3000/api/auth/callback/google"
  }
}
```

The OAuth callback URLs confirm these were configured for local development and exposed on cloud VMs without reconfiguring the callback host. Authentication is broken for any external user — OAuth flows redirect back to localhost, completing only on the server itself.

The agent creation surface is reachable. No agent run history confirmed — auth-gating on agent state may still hold at the application layer. Tier: LOW, not CRITICAL — the auth mechanism is present even if misconfigured.

---

## Negative results

**CrewAI Studio:** Shodan-dark. `http.title:"CrewAI Studio"` = 0, `http.html:"CrewAI Studio"` = 0, `http.html:"crewai-studio"` = 0. Seven hosts from `port:3000 http.html:"crewai"` returned Coolify, Open WebUI, and other services — none confirmed as CrewAI Studio. The SSL cert CN pivot (`ssl.cert.subject.cn:"crewai"`) returns 19 AWS hosts that are crewai.com vendor infrastructure, not operator deployments.

**SuperAGI:** 14 Shodan hits, all commercial SaaS. Direct access returns HTTP redirect to `/auth_users/login`. No self-hosted instances found. Auth-on-default confirmed.

**Devika:** 2 Shodan hits. Platform effectively defunct — no active community deployment found. Not confirmed as actual Devika instances (title match only, not verified against API shape).

**BabyAGI / Goose:** CLI tools with no HTTP server. Zero Shodan surface. Confirmed absent.

---

## FP classes documented

| FP | Root cause | Fix |
|---|---|---|
| aimap "RedisInsight" at `5.78.111.11:8001` | `/api/info` returns `{name, version, status}` — RedisInsight fingerprint triggers on JSON shape alone | Add `body_contains "RedisInsight"` conjunct |
| aimap "Tabnine" at `48.209.17.55:443` | cite.videmak.net returns `{"error":"API key required"}` matching Tabnine probe | Anchor Tabnine probe to Tabnine-specific response fields |
| VisorScuba "Unauthenticated Ollama" on GPT Researcher hosts | Port 8000 is shared; Ollama also defaults to 8000 | VisorScuba classification reads port, not service identity from aimap |
| SuperAGI Shodan hits | `http.html:"superagi"` matches the commercial SaaS marketing content | Title dork `http.title:"SuperAGI"` is slightly tighter; still catches vendor fleet |

---

## Insight candidate: Agno auth-off-default

Agno follows the same install-experience pattern as Prefect and Dask (Insight #63). The playground server is a `pip install + run` local-first design. It binds to `0.0.0.0:7777` with no authentication.

The novel finding here is what the agent manifest exposes before any run is invoked. The `/agents` endpoint returns each agent's name and description. The descriptions confirm the data-source class: "PostgreSQL Data Agent," "analyzes client email threads," "analyzes Fireflies call transcripts." The names ARE the finding. Invoking a run is not required to establish severity — the manifest proves what data the system can reach.

**Candidate Insight #64:** AI agent manifests are pre-run disclosure. The agent description tells you what data sources are in scope before any run is invoked. An unauth `/agents` endpoint on a system that accesses contracts, databases, or communications is a CRITICAL finding regardless of whether a run is triggered — because the manifest proves the attack surface.

---

## Recon artifacts

```
~/AI-LLM-Infrastructure-OSINT/recon/cat06-stragglers-2026-05-26/
  shodan-crewai-superagi-agno.txt     93 IP:PORT (all platforms)
  shodan-harvest-log.md               per-dork breakdown with counts
  ips-all.txt                         93 unique IPs
  aimap-cat06.json                    93 targets, 14 services, 5 findings
```

**aimap gaps noted:**
- RedisInsight FP: `/api/info` JSON shape match — needs `body_contains "RedisInsight"` conjunct
- Tabnine FP: API-key-required response shape — needs Tabnine-specific field anchor
- CrewAI Studio: fingerprint added (v1.9.32) but platform is Shodan-dark — masscan on port 3000 needed for direct discovery
