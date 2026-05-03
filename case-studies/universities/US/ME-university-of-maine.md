# University of Maine — 69GB Uncensored 122B Model + 18 Cloud Subscriptions, ECE Server

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
| tripolskypetr/qwen3.5-uncensored-aggressive:122b | **69.1 GB** | Aggressively uncensored 122B — no content filtering |
| gpt-oss:120b | **60.9 GB** | OpenAI open model, 120B |
| llama3.2:3b | 1.9 GB | General |

**Cloud proxies (18):** qwen3.5:cloud, deepseek-v4-pro:cloud, deepseek-v4-flash:cloud, kimi-k2.6:cloud, kimi-k2.5:cloud, kimi-k2-thinking:cloud, deepseek-v3.2:cloud, glm-4.6:cloud, glm-4.7:cloud, glm-5:cloud, glm-5.1:cloud, minimax-m2:cloud, minimax-m2.1:cloud, minimax-m2.5:cloud, minimax-m2.7:cloud, nemotron-3-super:cloud, devstral-2:123b-cloud, gemini-3-flash-preview:cloud, qwen3-coder-next:cloud

---

## Findings

### F1 — 69GB Uncensored 122B Model on University Infrastructure (CRITICAL)

`tripolskypetr/qwen3.5-uncensored-aggressive:122b` is explicitly tuned to remove all content filtering. At 69GB it is not a small experiment — this is a substantial frontier-class model deployed on ECE department infrastructure and served publicly without authentication. Any internet actor can use it to generate content that would be blocked by all commercial providers, at the university's electricity and GPU cost.

### F2 — 18 Pre-Release Cloud Subscriptions Exposed (CRITICAL)

The cloud proxy portfolio includes `deepseek-v4-flash:cloud`, `devstral-2:123b-cloud`, `gemini-3-flash-preview:cloud`, `kimi-k2-thinking:cloud`, and `qwen3-coder-next:cloud` — models only accessible via Ollama Connect beta subscriptions. Any actor can consume these at the operator's subscription cost.

### F3 — CVE-2025-63389 on All 21 Models (CRITICAL)

Unauthenticated `/api/create` allows system prompt injection. The uncensored model has no prompt-level restrictions; injection would allow arbitrary instruction override on both local and cloud models.

---

## Remediation

```bash
OLLAMA_HOST=127.0.0.1:11434
systemctl restart ollama
```

Additionally: the uncensored model should be reviewed for policy compliance with UMaine AUP.

---

## Disclosure

- **Discovered:** 2026-05-03
- **Status:** Pending outreach to UMaine ECE / it-security@maine.edu
