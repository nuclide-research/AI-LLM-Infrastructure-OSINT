# LLM06:2025 — Excessive Agency

**OWASP rank 2025:** #6 (**MERGED**: combines LLM07:2023 Insecure Plugin Design + LLM08:2023 Excessive Agency)
**OWASP rank 2023:** LLM07 + LLM08

The 2025 merge unifies the two related concepts: a plugin/tool grants the LLM functionality, and the question of how much authority the LLM has when invoking that functionality. Both reduce to "the LLM has more power than it should." The 2025 revision adds explicit treatment of **autonomous agent risks** — agents that orchestrate multiple tool calls without human-in-the-loop.

## Description

An LLM-integrated system grants the model:

1. **Permission to execute code** (sandbox-free or with insufficient sandbox)
2. **Permission to make stateful changes** (file system, database, API calls that mutate)
3. **Permission to invoke tools whose effects compound** (sending email, posting to social media, transferring funds)
4. **Multi-step autonomous chains** (agent decides which tool to invoke next, no human review)
5. **Permission to invoke other agents** (multi-agent systems where authority propagates)

The vulnerability is that the LLM's authority is decoupled from any guarantee of correctness. Combined with LLM01 prompt injection, this becomes catastrophic — an attacker who injects a prompt into the LLM gets to invoke whatever tools the agent has access to.

## Academic citations

The threat model is new (no canonical pre-2023 paper covers autonomous agent risk), but conceptually related:

- **Reinforcement Learning safety** literature in cs598-fall2020/2021 — including Constrained Policy Optimization, safe RL with shielding. The conceptual framework for "agent with bounded authority" is here.
- **Backdoor + agency** intersection — when an autonomous agent is backdoored (LLM04), excessive agency becomes the exploitation vector. Bo Li's group has covered this in Trojaning + DBA papers.

## Current survey instances

- **Flowise Custom Tool + Tool Agent + ReAct Agent + Conversational Agent** (CVE-2024-36420 PoC lab at `146.190.128.73:3000`) — 16+ deployed chatflows specifically demonstrate the LLM06 class:
  - `rce_exploit`, `agent_rce_test`, `rce_tool_agent`, `mrkl_rce_v2`, `rce_poc_working`, `rce_exact_clone`, `rce_conversational_agent`, `rce_mrkl_agent`, `rce_mrkl_working`, `rce_conversational_working`, `cmd_exec_flow`, `openai_function_rce`, `path_traversal_test`, `sql_test`
  - Plus the secondary `deepseek_admin` prototype-pollution RCE vector identified in the case study.
- **Flowise population at large** — 578 of 841 Flowise instances expose `/api/v1/chatflows` unauthenticated. **Each chatflow with a Custom Tool node is a potential LLM06 endpoint.** The class is enabled at population scale; only a small subset has been verified to deploy the exploit configuration.
- **Dify SSO + register conflict** (`47.117.33.199:80`) — registration creates a local account before SSO enforcement applies. A partial-LLM06 scenario where the agent's permissions (registered Dify account → app creation) are decoupled from the auth path (SSO).

## CVE-2024-36420 — the canonical Flowise LLM06 CVE

Pre-patch Flowise allowed unauthenticated POST to `/api/v1/prediction/<chatflowId>` to trigger Custom Tool execution. The Custom Tool node runs JavaScript server-side without sandbox. The combination of (a) public prediction endpoint + (b) Custom Tool's authority + (c) no auth = direct LLM06 exploitation.

The PoC lab operator deployed RCE chatflows specifically to test the class. NuClide's contribution is documenting that the operator left the test bed exposed publicly, including a **second RCE vector** (Axios `baseOptions.__proto__` pollution) not part of the original CVE.

## Defensive controls

- **Tool capability bounds** — every tool's effect is enumerated and bounded (no "shell exec" tool; replace with narrowly-scoped tools)
- **Human-in-the-loop confirmation** for any mutating tool invocation
- **Sandboxed execution** (gVisor, Firecracker, V8 isolates) for any code-execution tool
- **Audit logging** of every tool invocation with full context (agent decisions are auditable post-hoc)
- **Authority decoupling** — agent's identity is not the same as the user's identity (least privilege)

## Related NICE roles

- **541 Vulnerability Assessment Analyst** — discovers public exploit configurations
- **631 Information Systems Security Developer** — implements the sandbox + capability bounds
- **661 R&D Specialist** — tracks the emerging agent-safety literature
- **K0202 KSA: Knowledge of application firewall concepts and functions** — relevant to agent-tool boundary enforcement
