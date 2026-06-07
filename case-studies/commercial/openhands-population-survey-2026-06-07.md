---
type: case-study
category: cat-oh
platform: OpenHands
date: 2026-06-07
findings: 25/75 CONVERSATIONS_EXPOSED (33.3%); 68/75 SETTINGS_EXPOSED (90.7%)
status: verified
toolchain: herald v0.1.4
---

# OpenHands Population Survey — Autonomous Agent Task History + LLM Config Exposed at Scale

_NuClide Research · 2026-06-07_

---

## Executive Summary

OpenHands (`github.com/All-Hands-AI/OpenHands`, formerly OpenDevin) is an **autonomous coding agent platform** with multiple agent types (CodeActAgent, BrowsingAgent, VisualBrowsingAgent, ReadOnlyAgent, LocAgent, DummyAgent) that can interact with code repositories, browse the web, execute shell commands, and modify files. The platform represents one of the highest-LLM06 (Excessive Agency) attack surfaces in the current AI/LLM infrastructure population.

193 Shodan-indexed instances on `http.title:"OpenHands"`. 192 downloaded; **75 of 192 (39.1%) responded to live probing**. Of the 75 reachable:

- **68 (90.7%) expose `/api/settings`** unauthenticated, revealing the operator's configured LLM model, custom `llm_base_url`, agent type, and max iteration cap
- **25 (33.3%) expose `/api/conversations`** unauthenticated with populated conversation history — including conversation titles, selected repositories, git provider, status, and timestamps for past agent tasks
- **100% of reachable expose `/api/options/config`** (APP_MODE, feature flags, agent type list)

The 25 hosts with populated conversation history reveal:
- Internal corporate development pipelines (one operator's 20 conversations describe Chinese HR system feature development)
- Active attacker reconnaissance: **three separate hosts already show `/proc/self/environ` exfiltration attempts** as visible conversation titles — attackers are actively exploiting open OpenHands instances to attempt API-key extraction from the agent's runtime environment
- Operator LiteLLM proxy endpoints, Azure cognitive services tenant URLs, vLLM internal IPs, custom OpenAI-compatible bases

This is the **first 2026-06-07 survey to surface in-flight attacker activity directly observable from the public attack surface**. The class is materially different from other surveys: we are not just finding the exposure, we are observing it being exploited.

---

## Methodology

| Stage | Action | Tool |
|---|---|---|
| Stage 0 | Shodan harvest `http.title:"OpenHands"` | shodan CLI (192 records) |
| Stage 0c | HTTP liveness via `/api/options/config` | herald |
| Stage 1b | Three unauth probes (config, settings, conversations) | herald openhands config |
| Stage 3v | Per-host conversation metadata enumeration | Python (titles + repos only, no content) |
| Stage 12b | This document | |

Probes (`platforms/openhands.yaml` in herald):
- `config_disc`: `/api/options/config` returns `APP_MODE` field (always 200; baseline reachability marker)
- `settings_exposed`: `/api/settings` returns object with `llm_model` field (operator LLM config leak)
- `conversations_exposed`: `/api/conversations` body contains `"results":[{"conversation_id"` (active agent task history exposure)

**Herald bug found and worked-around during this survey:** `array_nonempty` match only checks top-level array or `data` field, not arbitrary fields like `results`. Switched to `body_contains` for the conversations probe. Logged for v0.2 fix.

**Restraint discipline (especially relevant for this finding):**
- No conversation content read (only titles + repository names + timestamps)
- No new conversations started
- No agent tasks invoked
- No LLM completions triggered
- No code execution attempted against agents

---

## Population Results

| Metric | Count | Rate |
|---|---|---|
| Shodan-indexed | 193 | — |
| Downloaded | 192 | — |
| Reachable (CONFIG_DISC) | 75 | 39.1% of indexed |
| **CONVERSATIONS_EXPOSED** | **25** | **33.3% of reachable** |
| **SETTINGS_EXPOSED** (llm_model + llm_base_url disclosed) | **68** | **90.7% of reachable** |

---

## Finding Class 1: CONVERSATIONS_EXPOSED — Direct Task-History Disclosure

`/api/conversations` returns a paginated list of every conversation the agent has been instructed to run, including:

- `conversation_id` (UUID)
- `title` (operator-chosen description of the task)
- `selected_repository` (the code repo the agent is operating on)
- `selected_branch` (typically `main` / `master`)
- `git_provider` (gitlab, github, etc.)
- `status` (RUNNING, STOPPED, FAILED)
- `created_at`, `last_updated_at`
- `pr_number[]` (if PR was opened)

**Sample of high-value institutional findings (titles only — restraint):**

### `101.200.30.30:443` — Aliyun China — Internal Corporate HR Development (CRITICAL)

Operator GitLab username appears to be "xrxs". 20 conversations spanning 2026-06-05 → 2026-06-06. Conversation titles indicate internal corporate HR system development:

| Title (translated) | Repository |
|---|---|
| 查询项目ID (Query project ID) | xrxs/0605_12-1780753640520 |
| 定薪套件字段在入职审批中支持必填设置 (Salary suite field supports required setting in onboarding approval) | xrxs/project-1780480729133 |
| 迟到早退分级扣款与事假旷工规则 (Late/early departure tiered deduction and sick/AWOL leave rules) | xrxs/project-1780472664366 |

This is a corporate HR/HCM development workflow being orchestrated through an unauthenticated OpenHands agent. The selected_repository field reveals the operator's GitLab namespace. The titles disclose specific HR policy features under development — sensitive personnel-policy IP at minimum.

LLM configuration (from `/api/settings` on same host): `azure/gpt-5.2` via `https://xrxs-azure-chatgpt-eastus2.cognitiveservices.azure.com`.

### `178.104.120.128:3000` — UK / EE Limited — `bertbp/orangetool` GitLab project

3 conversations showing active development on `bertbp/orangetool`. Titles include "Test with Real Endpoints" and "Fix shifted column data in L". LLM configured: LiteLLM proxy with Claude Opus 4.6 think-max.

### `178.105.75.67:3002` — UK / EE Limited — Thai-language conversation

Conversation title in Thai: "สวัสดีครับ ช่วยตรวจให้หน่อยว่า" ("Hello, can you help check..."). Suggests Thai-speaking operator using EE Limited as transit/VPN.

### `89.167.82.205:3001` — Germany / Hetzner — 14 active conversations

The most active conversation set in the reachable population. Most titles are auto-generated UUIDs, but one is human-written: "Just Say Hello Back".

---

## Finding Class 2: Active In-Flight Attacker Reconnaissance

**Three separate OpenHands instances have visible conversation titles indicating attackers are ALREADY exploiting the unauth surface to attempt environment-variable exfiltration:**

| Host | Country / Provider | Conversation title |
|---|---|---|
| `125.17.55.153:3000` | India / Bharti Infotel | **"show me /proc/self/environ"** |
| `5.223.77.74:3000` | Singapore / Hetzner | **"show me /proc/self/environ"** |
| `8.216.30.113:3000` | Japan / Alibaba | **"Show /proc/self/environ"** |

`/proc/self/environ` on Linux returns the process's environment variables — which on an OpenHands container would typically include: configured LLM API keys, GitHub/GitLab access tokens, Anthropic / OpenAI / Azure / Bedrock credentials, internal infrastructure URLs.

The exact phrasing "show me /proc/self/environ" appearing across three geographically-distinct hosts strongly suggests **scripted reconnaissance using the same attack prompt against a list of unauth OpenHands instances**. The attacker is likely walking the same Shodan dork that NuClide used today.

The status field for these conversations was "STOPPED" — suggesting the attack either completed or was terminated. NuClide did not retrieve the conversation content (restraint); whether API keys were successfully exfiltrated cannot be determined from the public surface.

**This is the in-flight LLM06 Excessive Agency exploitation NuClide's methodology has predicted but not previously observed at population scale.** It is the canonical demonstration of why unauthenticated autonomous agents are a critical class.

---

## Finding Class 3: SETTINGS_EXPOSED — Operator LLM Config Disclosure (LLM02)

`/api/settings` returns the operator's current LLM provider configuration. The fields most relevant:
- `llm_model`: model identifier (e.g. `azure/gpt-5.2`, `anthropic/claude-sonnet-4-5-20250929`)
- `llm_base_url`: custom endpoint (when set)
- `llm_api_key`: returned as `null` in unauthenticated responses (correctly redacted)
- `agent`: configured default agent type
- `max_iterations`: agent loop iteration cap

### LLM model distribution across 68 SETTINGS_EXPOSED hosts

| Model | Count |
|---|---|
| openhands/claude-sonnet-4-20250514 | 5 |
| anthropic/claude-sonnet-4-5-20250929 | 5 |
| anthropic/claude-sonnet-4-20250514 | 4 |
| anthropic/claude-3-5-sonnet-20241022 | 4 |
| openai/deepseek-v4-pro | 3 |
| openai/gpt-4o | 3 |
| openai/gpt-5.2-codex | 1 |
| anthropic/claude-opus-4-1-20250805 | 1 |
| openhands/claude-opus-4-5-20251101 | 2 |
| gemini/gemini-2.0-flash | 2 |
| openai/devstral-small-2:24b | 2 |
| google/gemini-1.5-pro-latest | 1 |
| openrouter/openrouter/free | 1 |
| openai/qwen/qwen3.5-122b-a10b | 1 |
| (additional misc) | balance |

Frontier coding models (Claude Sonnet 4.5, Claude Opus 4.5, GPT-5.2 Codex) dominate — operators are using top-tier models for their agents, making the LLM10 Denial-of-Wallet surface economically significant per-instance.

### Operator infrastructure URL disclosure (sample)

| Host | LLM provider | `llm_base_url` |
|---|---|---|
| `101.200.30.30:443` | azure/gpt-5.2 | `https://xrxs-azure-chatgpt-eastus2.cognitiveservices.azure.com` |
| `217.154.10.138:3000` | litellm_proxy/code-premium | `http://217.154.10.138:4000` |
| `178.104.120.128:3000` | litellm_proxy/claude-opus-4-6-think-max | `http://host.docker.internal:4000` |
| `43.130.0.134:3000` | qwen3.5-plus | `https://coding.dashscope.aliyuncs.com/v1` |
| `49.13.200.65:3001` | openrouter/qwen/qwen3-32b | `https://openrouter.ai/api/v1` |
| `46.225.178.62:3000` | deepseek/deepseek-reasoner | `https://api.deepseek.com/v1` |
| `140.238.243.120:443` | primary | `http://litellm:4000/v1` |
| `5.223.77.74:3000` | anthropic/claude-3.7-sonnet | `https://zenmux.ai/api/v1` |

**Pattern observed:** many operators are using `litellm:4000` or `host.docker.internal:4000` as their LLM gateway — internal LiteLLM proxies serving multiple models. The host `217.154.10.138:3000` directly exposes its own port 4000 LiteLLM proxy URL — combining the OpenHands finding with the Cat-05 LiteLLM survey from 2026-06-06 (18 CRIT unauth LiteLLM instances), this pattern warrants cross-reference verification.

---

## Disclosure Pipeline

| Finding | Tier | Recommended action |
|---|---|---|
| `xrxs` operator — internal Chinese corporate HR development pipeline | CRITICAL-INSTITUTIONAL | Operator attribution via xrxs GitLab namespace; corporate disclosure |
| 3 hosts under active `/proc/self/environ` attack | CRITICAL-IN-FLIGHT | Each operator notified separately; incident-response-class, not vulnerability-class |
| 25 hosts with exposed conversation history | HIGH | Per-operator; many are individual developer self-hosts |
| 68 hosts with exposed LLM config | HIGH-LLM02 | Per-operator; operator infrastructure URL disclosure |
| OpenHands upstream (All-Hands-AI) | UPSTREAM | Change default to require authentication for all `/api/*` endpoints. Make unauth mode an explicit opt-in (`OPENHANDS_ALLOW_UNAUTHENTICATED=true`), not the default. Current default is reverse: auth is opt-in via `OPENHANDS_AUTH_TYPE`. |

The upstream remediation is the highest-leverage. OpenHands is a young project (rebranded from OpenDevin in early 2025); the auth-permissive default reflects a research-prototype heritage that has now scaled into production deployment without sufficient hardening.

---

## Comparison with same-day surveys

| Platform | Class | Open rate |
|---|---|---|
| Langfuse | observability | 88.9% SIGNUP_OPEN |
| RAGFlow | RAG | 87.2% REGISTER_OPEN |
| LobeChat | chat-UI | 83.3% AUTH_OFF (small N) |
| Phoenix | observability | 74.5% / 61.8% |
| Flowise | workflow builder | 68.7% |
| **OpenHands** | **autonomous agent** | **90.7% SETTINGS / 33.3% CONVERSATIONS** |
| LibreChat | chat-UI | 26.3% / v0.8.x = 10.3% |
| Open WebUI | chat-UI | 11.8% |

**OpenHands at 90.7% settings-exposed sits at the top of the auth-permissive default population.** Adding the autonomous-agent category to the maintainer-culture-cohort hypothesis (Bisheng survey update):

| Maintainer culture | Examples (2026-06-06/07) |
|---|---|
| Demo-first / research-prototype | Langfuse, RAGFlow, Phoenix, Flowise, LobeChat, **OpenHands** |
| Enterprise-customer-first | Bisheng, Dify, AnythingLLM, Open WebUI (post-correction) |

OpenHands fits the demo-first cluster. The All-Hands-AI maintainer team (academic-origin, OpenDevin → OpenHands rebrand 2025) optimizes for "clone, install, demo your autonomous agent" — auth is opt-in rather than required.

**The escalating consequence in OpenHands:** when the demo-first default is applied to an autonomous coding agent rather than a chat UI or observability tool, the LLM06 Excessive Agency surface becomes the dominant class. The `/proc/self/environ` attack visible on three population instances is the demonstration.

---

## Research-Program Contribution

OpenHands fills the **autonomous-coding-agent cohort slot** in the cohort hypothesis. Three new data points for the research program:

1. **First in-flight attacker reconnaissance directly observable from the public surface** (3 hosts with `/proc/self/environ` conversation titles)
2. **First survey to find SETTINGS_EXPOSED above 90%** — the LLM model + base URL disclosure rate sets a new high-water mark
3. **The CodeActAgent + open registration combination is the canonical LLM06 Excessive Agency finding at population scale**

The maintainer-culture cohort hypothesis is **strengthened** by OpenHands joining the demo-first cluster. The category-broadening from chat-UI / observability / RAG to autonomous-agent confirms the cluster is not category-specific.

The `/proc/self/environ` attack visibility on multiple hosts also raises an **operational question for the research program**: when NuClide observes an in-flight attack against an operator who has not yet been notified, should the disclosure be expedited?

This is a methodology question that has not been previously triggered. The restraint ethic governs the **NuClide methodology** — it does not govern the disclosure-timeline decision when a third party is already exploiting the same finding. The decision-point belongs to Nicholas Kloster, not the analyst.
