# University of Western Ontario — Unauthenticated Ollama + Cloud Proxy Exposed

_NuClide Research · 2026-05-01_

---

## Summary

University of Western Ontario (London, Ontario) research server running 9 Ollama models including `deepseek-v4-pro:cloud`. Cloud proxy request returns 401 (subscription tier limit) without credential leak — cloud subscription authenticated but not drained on this probe. Raw Ollama port publicly accessible, no authentication.

---

## Infrastructure

| Field | Value |
|---|---|
| IP | 129.100.226.217 |
| rDNS | WE-D-ECE-0288.eng.uwo.ca |
| Org | University of Western Ontario |
| Faculty | Engineering (ECE department — hostname) |
| Country | Canada — Ontario |
| Open ports | 11434 (Ollama — **public**) |

---

## Models

| Model | Size | Notes |
|---|---|---|
| deepseek-v4-pro:cloud | 0 GB | ☁️ Cloud proxy — DeepSeek API |
| qwen3.6:35b | 22 GB | Local |
| qwen2.5vl:3b | 2 GB | Local — vision-language |
| qwen2.5vl:7b-q8_0 | 8 GB | Local — vision-language |
| gemma4:e2b | 6 GB | Local |
| gemma4:31b | 18 GB | Local |
| qwen2.5vl:latest | 5 GB | Local — vision-language |
| llava:latest | 4 GB | Local — vision-language |
| qwen3.5:35b | 22 GB | Local |

---

## Findings

### F1 — Unauthenticated Ollama API (CRITICAL)

Port 11434 publicly accessible. All models enumerable and injectable without credentials.

### F2 — Cloud Proxy Accessible (HIGH)

`deepseek-v4-pro:cloud` is accessible on the unauthenticated port. 401 returned (subscription tier limit) without credential disclosure on this probe. Inference may succeed at lower priority times or with different model variants. Model injection via `/api/create` can redirect all cloud proxy traffic.

### F3 — Vision-Language Models Exposed (MEDIUM)

Three vision-language model variants (qwen2.5vl, llava) accessible without auth. If used in document or image workflows, injection would affect all vision-assisted outputs.

---

## Remediation

```bash
OLLAMA_HOST=127.0.0.1:11434
systemctl restart ollama
```

---

## Disclosure

- **Discovered:** 2026-05-01
- **Status:** Pending outreach to UWO IT / ECE department
