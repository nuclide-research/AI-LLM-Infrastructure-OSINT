# University of Alberta — CS Dept GPU Server, gpt-oss:120b, Coding Stack

_NuClide Research · 2026-05-03_

---

## Summary

`lula.cs.ualberta.ca` (129.128.243.184), University of Alberta Computer Science department, runs Ollama v0.21.1 with 5 models including `gpt-oss:120b` (65GB, 116.8B parameters) and `qwen2.5-coder:32b` — indicating an active coding research or development workflow.

---

## Infrastructure

| Field | Value |
|---|---|
| IP | 129.128.243.184 |
| Hostname | lula.cs.ualberta.ca |
| Organization | University of Alberta — Computer Science |
| Network | AS226 University of Alberta (129.128.0.0/16) |
| Country | Canada — Alberta |
| Ollama version | 0.21.1 |
| Open port | 11434 (public) |

---

## Model Inventory

| Model | Size | Notes |
|---|---|---|
| `gpt-oss:120b` | 65GB | 116.8B parameter local inference |
| `qwen3.6:35b` | 23GB | Qwen3.6 35B |
| `qwen3.6:27b` | 17GB | Qwen3.6 27B |
| `qwen2.5-coder:32b` | 19GB | Qwen2.5 Coder 32B |
| `qwen3.5:9b` | 6GB | Qwen3.5 9B |

**Total local storage:** ~130GB

---

## Findings

### F1 — Unauthenticated Inference on CS GPU Server (HIGH)

All 5 models freely accessible. The `qwen2.5-coder:32b` indicates an active coding research or code generation workflow. `gpt-oss:120b` (116.8B params) represents significant compute exposure — unauthenticated callers can run 120B inference at no cost.

### F2 — CVE-2025-63389 (HIGH)

All 5 models injectable via unauthenticated `/api/create`.

---

## Remediation

```bash
OLLAMA_HOST=127.0.0.1:11434
systemctl restart ollama
```

---

## Disclosure

- **Discovered:** 2026-05-03
- **Status:** Pending outreach to UAlberta IT Security (ualberta.ca)
