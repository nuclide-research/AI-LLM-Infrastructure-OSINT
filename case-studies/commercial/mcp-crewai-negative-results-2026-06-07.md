---
type: case-study-methodology
category: cat-meta
platforms: [MCP, CrewAI]
date: 2026-06-07
findings: 2 negative results — methodology refinement
status: verified
---

# MCP Servers and CrewAI — Negative Results with Methodology Value

_NuClide Research · 2026-06-07_

Two attempted same-day surveys produced no actionable findings — but the failure modes are themselves research-program-relevant. Both reveal **classes of AI/LLM infrastructure that are not surveyable with the population-Shodan methodology** that worked for the chat-UI / RAG / observability / autonomous-agent platform surveys.

---

## Attempt 1: MCP Servers

### Dork investigation

<!-- ksat-tag:auto-generated:start -->
## DCWF KSAT coverage

Auto-derived from DCWF AI work-role rule files (`ksat-tag`).

- **672 (AI Test & Evaluation Specialist):** K7003, K7004, K7054, S7068, S7070, S7075, T5858, T5919
- **733 (AI Risk & Ethics Specialist):** K7051, T5868, T5882
- **overlap (Common AI KSATs (all 5 roles)):** K1158, K22, K6311

<!-- ksat-tag:auto-generated:end -->

Tried multiple candidate dorks for Model Context Protocol servers:

| Dork | Hits |
|---|---|
| `http.title:"MCP"` | 2,811 |
| `"mcp-session-id"` | 109,844 |
| `"text/event-stream" "mcp"` | 628 |
| `http.title:"MCP Inspector"` | 121 |
| `"mcp" port:3000` | 426 |
| `"jsonrpc" "tools"` | 4 |
| `"x-mcp-version"` | 0 |
| `"server-name" "mcp"` | 5 |

### Failure mode: dork noise

The largest population (`"mcp-session-id"` at 109,844) is **highly noisy**. Sample of the first 10 hits by title:
- `LOGIN TCF CMMS` (commercial maintenance management system)
- `data_service_platform`
- `Ivanti Policy Secure` (network security gateway)
- `MarsRouter (build 36527)` (router admin UI)
- `Zipline – Login`
- `WebCam`
- `GitLab`

The `Mcp-Session-Id` HTTP header is used by **many non-MCP services** as a generic session-correlation header. The MCP protocol specification has not yet established uniquely-identifiable header signatures that distinguish from common HTTP session header naming conventions.

Even the `http.title:"MCP Inspector"` dork (121 hits, supposed to find the canonical Anthropic MCP debugging UI) returned a **GitLab instance** as its top result — the page title contained "MCP Inspector" only because the GitLab project's name happened to include it.

### Failure mode: protocol architecture

MCP servers are predominantly **localhost-deployed dev tools** orchestrated by client applications (Claude Desktop, Cline, Continue, et al.). Public-IP MCP servers are rare because:
- The MCP transport model is stdio-by-default; HTTP/SSE transport is a less-common opt-in
- Server-side MCP requires authentication via OAuth or API keys (the MCP spec has matured to require this)
- The Shodan visibility model doesn't capture the stdio + websocket transport modes that dominate actual MCP deployments

### Research-program insight

MCP surveys at this stage require:
1. **Port-scan-first methodology** (not dork-first) — known MCP server ports + protocol-level identification via JSON-RPC initialize handshake
2. **Active protocol probe** with the canonical MCP `initialize` method to filter false positives
3. **CT log enumeration** of `*.mcp-server.*` subdomain patterns

The current NuClide methodology (Shodan title + content dorks → herald HTTP probe) is **not the right tool for the MCP ecosystem yet**. The ecosystem will likely become surveyable as it matures and converges on standardized HTTP transport conventions — estimated 2026 H2 based on the current MCP spec roadmap.

---

## Attempt 2: CrewAI

### Population

`http.title:"CrewAI"` → 24 hits. Downloaded 23 unique endpoints.

### Failure mode: framework vs platform

Sample of titles from the 23 hits:

| Host | Title |
|---|---|
| `118.25.27.85:80` | CrewAI 多Agent服务平台 |
| `139.162.52.158:443` | CrewAI Studio - 多智能体管理平台 |
| `143.198.169.179:2222` | CrewAI |
| `165.140.69.189:443` | CrewAI — My Crew |
| `178.105.34.49:3000` | CrewAI Studio |
| `185.2.103.72:443` | CrewAI Control · Monitoring Dashboard |
| `34.110.151.9:443` | Defang CrewAI Demo |
| (16 more) | (similarly diverse) |

**Every deployment is a custom UI built by a different operator on top of the CrewAI Python library.** There is no canonical "CrewAI server" because CrewAI is a Python library (`pip install crewai`), not a deployable service. The deployments reflect 23 operators independently building their own web UI around CrewAI.

API endpoint enumeration across 5 sampled hosts found:
- No shared URL path conventions
- No uniform `/api/*` structure
- No common auth signal

### Research-program insight

The autonomous-agent ecosystem splits into two distinct deployment classes:

| Class | Examples | Survey methodology |
|---|---|---|
| **Platform** (canonical deployment, uniform API) | OpenHands, LangGraph Studio, Flowise, AnythingLLM | Shodan dork + herald HTTP probe — **WORKS** |
| **Framework** (library + custom UI per operator) | CrewAI, LangChain, LlamaIndex, AutoGen | Shodan dork → diverse per-operator UIs — **DOES NOT WORK** |

The "framework class" is more architecturally significant than its small Shodan population suggests: a single CrewAI deployment is built by an operator who decides their own auth model. The exposure pattern is per-deployment-arbitrary rather than maintainer-default.

The right methodology for framework-class agent platforms is **operator-attribution-first** (find who is running CrewAI in production via CT logs, npm package downloads, GitHub corporate-org analysis) rather than **dork-first**.

---

## Comparison with Cohort Surveys

Insight #76 maintainer-culture hypothesis applies to **platform-class** projects:

| Class | Examples | Auth-permissive cohort default? |
|---|---|---|
| Platform — demo-first | Langfuse, RAGFlow, Phoenix, Flowise, LobeChat, OpenHands | YES |
| Platform — enterprise-first | Bisheng, Dify, AnythingLLM | NO |
| Platform — operator-misdeployment | LangGraph Studio | (n/a; correct default abused) |
| Framework — library | CrewAI, AutoGen, LangChain, LlamaIndex | (n/a; no shared deployment) |
| Protocol — emerging | MCP servers | (n/a; not yet population-surveyable) |

**The maintainer-culture hypothesis is bounded to the platform class.** Framework and protocol classes require different research methodologies.

---

## What This Means For Today's Tally

After Bisheng (CN auth-required counter-example), LangGraph Studio (operator-misdeployment new class), MCP (dork-noise negative), and CrewAI (framework-class negative), the research-program scope for Insight #76 is now precisely bounded:

> **Insight #76 (refined, as of 2026-06-07):** Auth-permissive defaults are the cohort norm for **platform-class** new-generation OSS AI/LLM infrastructure where the upstream maintainer optimizes for "demo-first" deployment ergonomics. The rate is platform-maintainer-culture-specific, not jurisdiction-specific. The hypothesis does **not apply** to framework-class libraries (no shared deployment) or to maturing protocol-class ecosystems (no canonical population yet).

The 11 surveys conducted 2026-06-06/07 are **all platform-class**. The hypothesis is now defined within its scope.

---

## Toolchain Provenance

```
Step 0:   shodan count + sample probe for MCP/CrewAI
Step 0c:  Direct curl probe — no actionable population
Step FP:  Confirmed dork-noise (MCP) and framework-architecture
          (CrewAI) failure modes
Step 12b: This methodology document
```

**No herald configs added.** Future MCP survey methodology will require a new tool class (port-scan + protocol-handshake identification). Future CrewAI / AutoGen / framework-class work will require operator-attribution rather than population enumeration.

---

## Disclosure Pipeline State

No disclosure-worthy findings from these attempts. Both negative results have research-program value but no operator-side actionable exposure.
