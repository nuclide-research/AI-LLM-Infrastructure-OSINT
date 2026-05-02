# KTH Royal Institute of Technology — Dual-Node Unauthenticated Ollama, Abliterated Model Running as Root

_NuClide Research · 2026-05-01_

---

## Summary

KTH Royal Institute of Technology (Stockholm) has two separate servers running unauthenticated Ollama with DeepSeek v4 Pro cloud proxy subscriptions. One node hosts an "abliterated" (safety-fine-tuning-removed) Gemma model and runs Ollama as root. Both nodes injectable via CVE-2025-63389.

---

## Infrastructure

| Host | IP | Models | Cloud | Notes |
|------|-----|--------|-------|-------|
| 130.237.67.161 | KTH net | 12 | deepseek-v4-pro | — |
| 130.237.3.105 | KTH net | 8 | deepseek-v4-pro | **Abliterated model, running as root** |
| 130.237.218.65 | KTH net | 2 | 0 | v0.9.3 — older node |

---

## Node 1 — 130.237.67.161 (12 models)

Includes: qwen3.6:35b, deepseek-r1:32b, qwen3.5:35b-a3b, deepseek-v4-pro:cloud

## Node 2 — 130.237.3.105 (8 models)

Includes: qwen3.6:35b, qwen3.5:9b, deepseek-v4-pro:cloud, **`hf.co/OBLITERATUS/gemma-4-E4B-it-OBLITERATED:latest`**

Abliterated model details:
- Modelfile path: `/root/.ollama/models/...` — **Ollama running as root**
- No system prompt — safety fine-tuning removed by design
- OBLITERATUS is a well-known HuggingFace model series that removes safety RLHF from base models

---

## Node 3 — 130.237.218.65 (2 models, v0.9.3)

Running Ollama v0.9.3 (older, unpatched). 2 models with at least 1 system prompt exposed. No cloud proxies.

---

## Findings

### F1 — Unauthenticated Ollama on All Three Nodes (CRITICAL)

Both servers publicly expose port 11434. All models enumerable and injectable without credentials.

### F2 — DeepSeek Cloud Proxy on Both Nodes (HIGH)

`deepseek-v4-pro:cloud` present on both. 401 returned without credential disclosure. Model injection via CVE-2025-63389 can redirect all cloud proxy traffic.

### F3 — Abliterated Model Running as Root (HIGH)

Node 130.237.3.105 runs Ollama as `root` (`/root/.ollama/`). An abliterated model (safety fine-tuning removed) is deployed and accessible to unauthenticated callers. Any actor can inject this model's system prompt or run uncensored inference via the unauthenticated port.

---

## Remediation

```bash
# Both nodes
OLLAMA_HOST=127.0.0.1:11434
systemctl restart ollama

# Node 2: additionally, run Ollama as dedicated non-root user
```

---

## Disclosure

- **Discovered:** 2026-05-01
- **Status:** Pending outreach to KTH IT Security
