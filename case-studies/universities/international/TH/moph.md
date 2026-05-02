# Thailand Ministry of Public Health — Unauthenticated Inference, Vision Models

_NuClide Research · 2026-05-01_

---

## Summary

Thailand's Ministry of Public Health (MoPH) has an Ollama instance at 203.157.41.151 with 5 models publicly accessible, including `granite3.2-vision:2b` (IBM's vision-language model) and `qwen3.6:35b` (22GB). No authentication, no Open WebUI fronting the API.

---

## Infrastructure

| Field | Value |
|---|---|
| IP | 203.157.41.151 |
| Organization | Ministry of Public Health, Thailand |
| Country | Thailand |
| Open ports | 11434 (Ollama — public) |

---

## Model Inventory

| Model | Size | Notes |
|---|---|---|
| `qwen3.6:35b` | 22GB | Large general LLM |
| `granite3.2-vision:2b` | 2GB | IBM Granite vision-language model |
| `gemma3:4b` | 3GB | Google Gemma3 |
| `llama3.2:3b` | 1GB | — |
| `smollm2:135m` | — | Tiny LLM |

---

## Findings

### F1 — Government Health Ministry Inference Exposed (HIGH)

All 5 models are accessible without authentication on a Thai government Ministry of Public Health IP. Any internet actor can:
- Run inference against `qwen3.6:35b` (22GB, large model) at MoPH compute cost
- Submit images to `granite3.2-vision:2b` for analysis
- Enumerate all configured models via `/api/tags`

The `granite3.2-vision:2b` model carries IBM's default system prompt (not customized), indicating likely development/testing rather than a custom healthcare application.

No Open WebUI was detected on port 3000. The Ollama API is directly exposed with no frontend authentication layer.

### F2 — CVE-2025-63389 Injectable (HIGH)

All 5 models injectable via unauthenticated `/api/create`. If any of these models are being used for internal MoPH workflows, injected prompts affect those users.

---

## Remediation

```bash
OLLAMA_HOST=127.0.0.1:11434
systemctl restart ollama
```

---

## Disclosure

- **Discovered:** 2026-05-01
- **Status:** Pending outreach to Thailand MoPH CSIRT / ETDA (Electronic Transactions Development Agency)
