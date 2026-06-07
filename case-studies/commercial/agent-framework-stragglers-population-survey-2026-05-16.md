---
type: survey
---

# Agent-Framework Stragglers Population Survey (2026-05-16)

_NuClide Research · 2026-05-16 (Survey 8 of the day's 10-category batch)_
_Closes: category 06 (agent-frameworks) stragglers. CrewAI, LangGraph, SuperAGI, Goose, Letta_

---

## Summary

Population survey of the agent-framework stragglers. Platforms that emerged in 2024-2025 alongside the AutoGen / Open WebUI / Flowise generation. Closes the gap left by the AutoGen Studio survey (2026-05-14) which only covered one platform in category 06.

<!-- ksat-tag:auto-generated:start -->
## DCWF KSAT coverage

Auto-derived from DCWF AI work-role rule files (`ksat-tag`).

- **672 (AI Test & Evaluation Specialist):** K7003, K7004, K7044, S7068, S7070, S7075, T5858, T5904
- **733 (AI Risk & Ethics Specialist):** K7051, T5868, T5893
- **overlap (Common AI KSATs (all 5 roles)):** K1158, K22, K6311, K7003

<!-- ksat-tag:auto-generated:end -->

- 302 unique candidates harvested across CrewAI (126), LangGraph (44), SuperAGI (10), Goose (293 title-matches, mostly FP), Letta (35)
- Probed via `fast_enum_agent_fw.py` (threads=60, ~3 min)
- **0 confirmed unauth at the data layer** across all 5 platforms
- 11 partial-open (root or /openapi.json accessible, data endpoints gated)
- 54 shell-only (brand string in HTML but no API behind it)
- 126 dead, 8 unrelated, 101 unknown
- 2 auth-gated

**Result:** category 06 stragglers are mostly Shodan-dark or shell-only. The real population needs port-first masscan on the platform-specific default ports (Letta :8283, LangGraph default :8080, CrewAI :8000, SuperAGI :3000).

---

## Per-platform observations

### CrewAI

126 body-string Shodan hits, 21 title-string hits. CrewAI ships as a Python library; the "CrewAI" string in HTML mostly comes from Streamlit / FastAPI scaffolds that import CrewAI as a backend library. The actual platform doesn't expose a canonical web port. It's invoked from Python apps that may or may not have their own auth layer. Effectively Shodan-dark at the platform-fingerprint level; the population is "Python apps that mention CrewAI", not "CrewAI servers."

### LangGraph

42 title + 44 body. LangGraph (LangChain's stateful-agent framework) has a "LangGraph Server" deployment mode that serves the agent at `/v1/threads`. None confirmed unauth. Hosts found mostly had shell-only or partial-open states. `/openapi.json` accessible (FastAPI default) but data endpoints gated.

### SuperAGI

10 body + 12 title. Niche population. None confirmed unauth in this survey.

### Goose (Block's open-source AI assistant)

293 title-matches + 389 body-matches. Looks large but is mostly FP. "Goose" is a common word/name (companies, products, projects, brand collisions). Block's Goose is a desktop-first tool with no canonical server-mode brand string; the population we'd want to map is near-zero on the server tier.

### Letta (formerly MemGPT)

35 title + 15 body. Letta is Shodan-dark per default-port :8283 shared with many services; the brand string is in JS bundles. None confirmed in this Shodan-seeded slice. Port-first masscan on :8283 is the right discovery channel (also flagged in the prior agent-memory survey).

---

## Methodology placement

All 5 platforms confirm the Insight #21 pattern at the agent-framework tier: brand-dork-seeded Shodan surveys mostly fail for these newer Python-library-based frameworks because:

1. **Library, not server**, most are imported into operator-built apps; no canonical default port
2. **JS-bundle brand-string burial**, when there is a UI, it's a Gradio/React SPA where the brand string is bundled
3. **Niche operator populations**, these are 2024-2025 emergence-tier platforms; the deployed-at-scale population is small (10s to low-100s globally per platform)

Adds 5 platforms to the [[insight-21-port-first-discovery-for-low-footprint-platforms]] catalog.

---

## What an exposed CrewAI / LangGraph server would disclose

For methodology roadmap (when port-first masscan is run):

- **LangGraph Server** at `/v1/threads` returns thread list. Each thread is an agent conversation with state. Unauth = full conversation history disclosure + ability to add to threads (POST). LangGraph's "studio" mode also exposes `/graphs` listing all registered agent graphs (operator-attribution rich, shows what the operator's agent does).
- **CrewAI Server** (when used) exposes `/openapi.json` with crew/agent/task endpoints. The crew + agent + task definitions are operator-IP. They reveal the application's full agentic workflow.
- **SuperAGI** exposes `/api/v1/agents` with the agent list. Each agent has goals + tools assigned. Full agentic workflow disclosure.
- **Letta** exposes `/v1/agents` with agent registry, each with memory blocks (the agent's persona + facts learned).

These are all **agentic-workflow disclosure**, discloses what the operator is building, not just what platform they're using. High-novelty information class for the auth-on-default thesis.

---

## Honest negative space

- **0 confirmed at this survey's reach does not mean zero exposed.** Shodan-dark category. Port-first masscan tier-2 is the next step.
- **CrewAI's "library not server" pattern is interesting.** It's a deployment-architecture insight: the auth-on-default thesis applies to FRAMEWORKS that ship a server tier; libraries imported into operator-built apps inherit whatever auth the operator's app has (no framework default to anchor against).
- **Goose's brand-string overload** is a Shodan-dork pathology. 293 title matches but ~0 are actually Block's Goose. The word is too common.
- **No port-first masscan attempted** in this survey. The fingerprint code is built; the discovery channel is the bottleneck.

---

## Toolchain Provenance

```
0. shodan search × 6 dorks → 302 unique candidates
1. fast_enum_agent_fw.py (threads=60) → 0 unauth across all 5 platforms
2. (deferred) port-first masscan tier-2 on :8283 + :8000 + :3000 → expected hundreds of real instances
3. (queued) aimap v1.9.7 already includes Letta + LangGraph + CrewAI markers; field-validation pending
```

---

## See also

- [[insight-21-port-first-discovery-for-low-footprint-platforms]]. Exactly the pattern these 5 platforms exhibit
- [[insight-25-falsification-confirmation-tier-c-platforms]]. Null result confirms thesis on platforms with no canonical server tier
- [`ros-robotics-population-survey-2026-05-16.md`](ros-robotics-population-survey-2026-05-16.md): same day's Shodan-dark companion
- [`agent-memory-population-survey-2026-05-16.md`](agent-memory-population-survey-2026-05-16.md): same day's agent-memory survey (which had similar Letta result)
