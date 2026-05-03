# University of California, San Diego (UCSD) — Large Local Models + Cloud Proxies

_NuClide Research · 2026-05-03_

---

## Summary

University of California San Diego (AS26397 — The Regents of the University of California) exposes an Ollama instance with 7 models including `qwen3.5:35b` (22GB), `gpt-oss:120b` (61GB), and two cloud proxy subscriptions (`devstral-2:123b-cloud`, `deepseek-v3.1:671b-cloud`). No rDNS — bare IP, no hostname. No account takeover on this node (cloud proxies return non-leaking 401).

---

## Infrastructure

| Field | Value |
|---|---|
| IP | 67.58.51.111 |
| rDNS | None |
| Org | AS26397 The Regents of the University of California — UCSD |
| City | San Diego, CA |
| Ollama version | 0.20.7 |
| Open port | 11434 (public, no auth) |

---

## Models

| Model | Size | Notes |
|---|---|---|
| gpt-oss:120b | 60.8 GB | OpenAI open model, 120B |
| qwen3.5:35b | 22.2 GB | Alibaba Qwen 3.5, 35B |
| gpt-oss:20b | 12.8 GB | OpenAI open model, 20B |
| devstral-2:123b-cloud | 0 GB | ☁️ Mistral Devstral 2, 123B agent model |
| deepseek-v3.1:671b-cloud | 0 GB | ☁️ DeepSeek V3.1, 671B |
| qwen3.5:latest | 6.1 GB | Qwen 3.5 (default) |
| smollm2:135m | 0.3 GB | Local — default SmolLM prompt |

---

## Findings

### F1 — Frontier Models Accessible Without Authentication (HIGH)

`gpt-oss:120b` (60.8GB, OpenAI open model) and `qwen3.5:35b` (22.2GB) are available for uncapped inference by any internet actor at UCSD's GPU and electricity cost.

### F2 — Cloud Proxy Subscriptions Exposed (HIGH)

`devstral-2:123b-cloud` (Mistral's latest 123B agent model) and `deepseek-v3.1:671b-cloud` are accessible. Cloud proxies return 401 without credential disclosure on this probe — no takeover available, but inference quota is drainable.

### F3 — CVE-2025-63389 (CRITICAL)

All 7 models injectable via unauthenticated `/api/create`.

---

## Remediation

```bash
OLLAMA_HOST=127.0.0.1:11434
systemctl restart ollama
```

---

## Disclosure

- **Discovered:** 2026-05-03
- **Status:** Pending outreach to UCSD IT Security (security@ucsd.edu)
