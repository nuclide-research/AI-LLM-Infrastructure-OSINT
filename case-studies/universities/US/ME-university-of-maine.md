# University of Maine: 69GB Uncensored 122B Model + 18 Cloud Subscriptions, ECE Server

_NuClide Research · 2026-05-03_

---

## Summary

University of Maine's Electrical and Computer Engineering (ECE) department runs an Ollama server at `ECE-Ubuntu-02.um.maine.edu` (Orono, AS557) with 21 models: 18 cloud proxy subscriptions and 3 local models including a 69GB aggressively uncensored 122B parameter model (`tripolskypetr/qwen3.5-uncensored-aggressive:122b`) and `gpt-oss:120b` (60.8GB). The cloud proxy portfolio includes every major pre-release frontier model (deepseek-v4-pro/flash, devstral-2:123b, gemini-3-flash-preview, kimi-k2 family, qwen3.5:397b). Fully unauthenticated.

---

## Infrastructure

| Field | Value |
|---|---|
| IP | 130.111.219.37 |
| rDNS | `ECE-Ubuntu-02.um.maine.edu` |
| Org | University of Maine System |
| Department | Electrical and Computer Engineering |
| City | Orono, ME |
| Ollama version | 0.18.2 |
| Open port | 11434 (public, no auth) |

---

## Models

**Local (3):**

| Model | Size | Notes |
|---|---|---|
| tripolskypetr/qwen3.5-uncensored-aggressive:122b | **69.1 GB** | Aggressively uncensored 122B, no content filtering |
| gpt-oss:120b | **60.9 GB** | OpenAI open model, 120B |
| llama3.2:3b | 1.9 GB | General |

**Cloud proxies (18):** qwen3.5:cloud, deepseek-v4-pro:cloud, deepseek-v4-flash:cloud, kimi-k2.6:cloud, kimi-k2.5:cloud, kimi-k2-thinking:cloud, deepseek-v3.2:cloud, glm-4.6:cloud, glm-4.7:cloud, glm-5:cloud, glm-5.1:cloud, minimax-m2:cloud, minimax-m2.1:cloud, minimax-m2.5:cloud, minimax-m2.7:cloud, nemotron-3-super:cloud, devstral-2:123b-cloud, gemini-3-flash-preview:cloud, qwen3-coder-next:cloud

---

## Findings

### F1: 69GB Uncensored 122B Model on University Infrastructure (CRITICAL)

`tripolskypetr/qwen3.5-uncensored-aggressive:122b` is explicitly tuned to remove all content filtering. At 69GB it is not a small experiment, this is a substantial frontier-class model deployed on ECE department infrastructure and served publicly without authentication. Any internet actor can use it to generate content that would be blocked by all commercial providers, at the university's electricity and GPU cost.

### F2: 18 Pre-Release Cloud Subscriptions Exposed (CRITICAL)

The cloud proxy portfolio includes `deepseek-v4-flash:cloud`, `devstral-2:123b-cloud`, `gemini-3-flash-preview:cloud`, `kimi-k2-thinking:cloud`, and `qwen3-coder-next:cloud`, models only accessible via Ollama Connect beta subscriptions. Any actor can consume these at the operator's subscription cost.

### F3: CVE-2025-63389 on All 21 Models (CRITICAL)

Unauthenticated `/api/create` allows system prompt injection. The uncensored model has no prompt-level restrictions; injection would allow arbitrary instruction override on both local and cloud models.

---

## Remediation

```bash
OLLAMA_HOST=127.0.0.1:11434
systemctl restart ollama
```

Also: the uncensored model should be reviewed for policy compliance with UMaine AUP.

---

## Disclosure

- **Discovered:** 2026-05-03
- **Status:** Pending outreach to UMaine ECE / it-security@maine.edu

---

## Second host (2026-05-19 .edu sweep): fate2.library.umaine.edu

A second UMaine Ollama instance was observed on the library system during the 2026-05-19 .edu LLM-infra survey wave-2. Distinct host, distinct department, same auth-on-default class.

### Infrastructure

| Field | Value |
|---|---|
| IP | 130.111.64.5 |
| rDNS | `fate2.library.umaine.edu` |
| Org | University of Maine System |
| Department | Library |
| Ollama version | 0.23.2 |
| Open port | 11434 (public, no auth) |

### Observations

`/api/version` returns `{"version":"0.23.2"}`. `/api/tags` returns 5,004 bytes of model inventory (15 models). `/api/ps` shows `qwen2.5vl:7b` (14.2 GB) actively LOADED in resident memory at the time of probe.

**Models present (15)** — vision-language stack with embedded chat models:

- `moondream:1.8b`
- `llava:13b`
- `llava-llama3:8b`
- `gemma3:4b`
- `minicpm-v:8b`
- `qwen2.5vl:7b` — with explicit system prompt `"You are a helpful assistant."`
- `llama3.2-vision:11b`
- `qwen3-vl:8b`
- `glm-ocr:latest`
- `ibm/granite3.3-vision:2b` — with explicit system prompt `"A chat between a curious user and an artificial intelligence assistant. The assistant gives helpful, detailed, and polite…"` (truncated)
- `qwen3-vl:4b`
- `llama3.2:8k`
- `qwen2.5-coder:7b-8k` — with explicit system prompt `"You are Qwen, created by Alibaba Cloud. You are a helpful assistant."`
- `llama3.2:latest`
- `qwen2.5-coder:7b` — same Qwen system prompt as 8k variant

### Observation-class

- **Public unauth Ollama API surface observed**: `/api/version`, `/api/tags`, `/api/ps`, `/api/show` all return 200 from public probe. No authentication required.
- **Vision-language inventory observed**: stack appears purpose-built for OCR / image-to-text workloads (consistent with library digitization / accessibility use cases).
- **Model-specific system prompts present**: `/api/show` returns customized SYSTEM prompts on at least three entries, indicating someone configured them deliberately (not stock pulls).
- **Class membership — quota-leeching surface**: per Insight class (Ollama public unauth), the host's local GPU compute is reachable by any internet caller. Quota-leech via local-model usage; cloud-quota-leech does NOT apply on this host (no `:cloud`-suffix models observed in tag list, unlike the ECE-Ubuntu-02 instance).
- **CVE-2025-63389 applicability — UNVERIFIED**: this version (0.23.2) is in a range that received the unauthenticated `/api/create` patch in later releases. We did NOT POST to `/api/create` (restraint). Class-membership for the CVE class is APPLICABLE per public version mapping; whether THIS host has been patched downstream is not data-verified from this probe.

No tier labels assigned per the survey's verified-tier convention. Observations recorded; data-membership for impact (specific data accessed, models invoked, accounts affected) was not tested per restraint ethic.

### Cross-host pattern within UMaine

Two distinct UMaine Ollama deployments observed:

| Host | Department | Models | Posture |
|---|---|---|---|
| `ECE-Ubuntu-02.um.maine.edu` (130.111.219.37) | Electrical & Computer Engineering | 21 (3 local incl. 69GB uncensored 122B + 18 cloud proxies) | Cloud-proxy class observed; uncensored-frontier-model class observed |
| `fate2.library.umaine.edu` (130.111.64.5) | Library | 15 (vision-language stack, local-only) | Vision-language inventory observed; no cloud proxy class on this host |

Two different departments running Ollama publicly suggests no central institutional policy enforcement for self-hosted LLM services on UMaine's network. Distinct compute environments, distinct model portfolios, same auth-on-default class posture. Worth noting in any disclosure routing to UMaine IT security: this is a pattern, not an isolated host.

### Discovery method

Surfaced via visorgoose `--tld .edu` scan (G8 fix applied) at 2026-05-19 20:56 UTC. Cross-confirmed via direct `aimap -ports-class wide` against the wave-2 corpus (which had the host in via Stage-0 dork). Both tools independently identified the host as live Ollama.

### Source artifacts

- visorgoose state: `~/recon/edu-llm-infra-2026-05-19/stage2-wave2/visorgoose-edu-state.json`
- visorgoose report: `~/recon/edu-llm-infra-2026-05-19/stage2-wave2/visorgoose-edu-report.md`
- aimap wave-2 results: `~/recon/edu-llm-infra-2026-05-19/stage2-wave2/aimap-wave2.json`
- direct probe: `~/recon/edu-llm-infra-2026-05-19/stage2-wave2/vg-priority-direct-probe.json`
