---
type: case-study
category: cat-fw
platform: Flowise
date: 2026-06-06
findings: 578 open (68.7%), including CVE-2024-36420 PoC lab, multi-tenant B2B exposure
status: verified
---

# Flowise Population Survey — 578/841 Open, CVE-2024-36420 PoC Lab Exposed

_NuClide Research · 2026-06-06_

---

## Discovery

Flowise is a drag-and-drop LLM workflow builder. Default deployment: no authentication on `/api/v1/chatflows` — the endpoint returns the full list of all configured chatflows, their nodes, deployment status, and embedded credentials in flow configurations.

Shodan: 841 instances on `http.title:"Flowise" port:3000`.
Sweep: `GET /api/v1/chatflows` on all 841.
Result: **578 responded with array data (68.7%)** — the auth check endpoint is open.

---

## Population Results

| Category | Count | Rate |
|---|---|---|
| Chatflows API accessible (no auth) | 578 | 68.7% |
| Instances with deployed chatflows | 14 | 1.7% |
| Empty (accessible but no flows configured) | 564 | 67.0% |

The 68.7% open rate reflects Flowise's default no-auth posture — auth is added only by installing an explicit auth plugin or deploying behind a proxy.

---

## Notable Finding: CVE-2024-36420 Research Lab (146.190.128.73)

`146.190.128.73:3000` — DigitalOcean, LLC

**43 chatflows, no authentication.** The chatflow inventory is a CVE-2024-36420 PoC development environment — 15+ deployed RCE test chatflows all using the `Custom Tool` + `Tool Agent` node combination that constitutes the Flowise pre-auth code execution attack surface:

**Deployed RCE flows:**
- `rce_exploit` — Tool Agent + Custom Tool + Calculator + ChatOpenAI
- `rce_tool_agent` — Tool Agent + Custom Tool + Buffer Memory
- `agent_rce_test` — Tool Agent + Custom Tool
- `openai_function_rce` — OpenAI Function Agent + Custom Tool
- `test_rce` — Custom Tool only
- `rce_poc_final` — Conversational Agent + Custom Tool
- `mrkl_rce_v2` — ReAct Agent + Custom Tool
- `rce_poc_working` — Tool Agent + Custom Tool
- `rce_exact_clone` — Tool Agent + Custom Tool
- `rce_conversational_agent` — Conversational Agent + Custom Tool
- `rce_mrkl_agent` — ReAct Agent + Custom Tool
- `rce_mrkl_working` — ReAct Agent + Custom Tool
- `rce_conversational_working` — Conversational Agent + Custom Tool
- `cmd_exec_flow` — Tool Agent (deployed)
- `path_traversal_test` — (deployed)
- `sql_test` — (deployed)

Also deployed: `deepseek_admin` (administrative flow using DeepSeek).

Legitimate flows mixed in: `FDAPineconeIndexing` (FDA document corpus indexed in Pinecone), `ItechTranslator`, `ItechDocsQnA` — operator name "Itech."

**Reading:** This is a security researcher reproducing CVE-2024-36420 against a self-hosted Flowise. The Flowise instance itself has no auth — the chatflow API is public. The `Custom Tool` node in Flowise allows arbitrary JavaScript execution server-side; in older versions this was pre-auth exploitable. All deployed PoC flows remain callable via the public API (any client can POST to `/api/v1/prediction/<chatflowId>`).

**Verification:** Read chatflow metadata (names, node types, deployment status). No chatflow invocation.

---

## Brazilian CNPJ Multi-Tenant Exposure (5.161.107.189)

`5.161.107.189:3000` — Hetzner.

23 chatflows named with 14-digit Brazilian CNPJ numbers (`06285918000100`, `07473654000181`, etc.). CNPJ is Brazil's company registration number. A B2B SaaS platform built on Flowise where each client company's chatflow is named by their corporate tax ID. All workflows accessible without authentication.

**Impact:** Any attacker can enumerate all 23 client company identifiers, access their chatflow configurations (including which LLM providers and embeddings they use), and potentially invoke their deployed chatflows directly.

---

## Chinese Pharmaceutical Compliance (106.52.236.135)

`106.52.236.135:3000` — TencentCloud, China.

7 chatflows including `GSP整改报告撰写` ("GSP improvement report writing") — GSP = Good Supply Practice, the Chinese pharmaceutical regulatory compliance framework. Also: `dp善于编程` ("good at programming") and multiple Ollama conversation flows. Pharmaceutical compliance AI workflow configuration accessible without auth.

---

## CVE-2024-36420 Context

The Custom Tool node in Flowise accepts JavaScript code that executes server-side during chatflow inference. Pre-patch, this was exploitable without any authentication — an unauthenticated POST to a prediction endpoint with a crafted input could trigger arbitrary code execution.

The PoC lab at `146.190.128.73` demonstrates systematic testing of this attack surface across multiple agent frameworks (Tool Agent, MRKL Agent, Conversational Agent, OpenAI Function Agent) — each deployed and callable via the public prediction API.

**The Flowise instance with the RCE PoC is itself unprotected.** Anyone can enumerate the chatflows, read the node configurations, and call the prediction endpoints.

---

## Auth Bypass Pattern

Flowise's default deployment has no authentication layer on the API. The `/api/v1/chatflows` endpoint is intentionally public in the default config — the assumption is that operators will deploy Flowise behind a reverse proxy with their own auth.

Result: 68.7% of Shodan-indexed Flowise instances expose their full chatflow catalog to the public internet.

---

## Toolchain Provenance

```
Stage 0:  shodan download 'http.title:"Flowise" port:3000' (841 IPs)
Stage 0c: /tmp/check_flowise_v2.sh — GET /api/v1/chatflows per IP (35 workers)
Stage 3v: Chatflow metadata read: names, nodes, deployment status
          No prediction endpoint invocation (restraint)
Stage 12b: This document
```

---

## Remediation

```bash
# Add to Flowise environment:
FLOWISE_USERNAME=admin
FLOWISE_PASSWORD=<strong-random-password>
# Or deploy behind nginx with http_auth
```

Upstream: Flowise added an auth plugin in v1.3.0. Operators on older versions or who don't configure the plugin remain open.
