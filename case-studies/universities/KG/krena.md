# KRENA (Kyrgyz Research and Education Network) — 433GB GLM-5.1, DeepSeek Cloud Proxy

_NuClide Research · 2026-05-01_

---

## Summary

The Kyrgyz Research and Education Network (KRENA) has an Ollama instance exposed on port 11434 running a 433GB quantized GLM-5.1 model — the largest single local model observed in this research. The instance also carries a `deepseek-v4-pro:cloud` proxy.

---

## Infrastructure

| Field | Value |
|---|---|
| IP | 178.217.174.90 |
| Organization | KRENA — Kyrgyz Research and Education Network Association |
| Address | Bishkek, Panfilova 237 / Chui Ave 265a, Bishkek 720071, Kyrgyz Republic |
| Country | Kyrgyzstan |
| Open ports | 11434 (Ollama — public) |

---

## Model Inventory

| Model | Size | Notes |
|---|---|---|
| `frob/glm-5.1:744b-a40b-ud-q4_K_XL` | **433GB** | GLM-5.1 MoE, **753.9B params** (verified via `/api/show`), 40B-active, family `glm-dsa`, Q4_K_M quant. (Tag reads `744b`; actual count is higher.) |
| `deepseek-v4-pro:cloud` | 0 | Cloud proxy |
| `qwen2.5:7b` | 4GB | — |
| `deepseek-r1:7b` | 4GB | — |
| `deepseek-r1:14b` | 8GB | — |

---

## Findings

### F1 — 433GB Local Model Publicly Accessible (HIGH)

`frob/glm-5.1:744b-a40b-ud-q4_K_XL` is the largest single local model discovered in this research sweep. The model is actively loaded (responds to `/api/show`); 433GB on disk requires substantial GPU infrastructure to serve. Any internet actor can run inference at KRENA's compute cost.

**Parameter count cross-reference:**
- Tag: `744b-a40b` — declares 744B total, 40B active MoE
- Epoch AI database (GLM-5, Z.ai/Zhipu, 2026-02-17): **744B total**
- KRENA `/api/show` reports `parameter_size: 753.9B` (likely Q4 quant overhead from tokenizer/embedding tensors)

The `frob/` prefix is a Hugging Face community namespace — community quantization of ZhipuAI's GLM-5.1.

### F2 — DeepSeek Cloud Proxy (HIGH)

`deepseek-v4-pro:cloud` is present. The 401 response does not include a `signin_url` with credentials (returns plain `{"error": "unauthorized"}`), suggesting either Ollama Connect credential storage differs on this instance or the account uses a non-standard auth path.

### F3 — CVE-2025-63389 Injectable (HIGH)

All 5 models injectable via unauthenticated `/api/create`.

---

## Remediation

```bash
OLLAMA_HOST=127.0.0.1:11434
systemctl restart ollama
```

---

## Disclosure

- **Discovered:** 2026-05-01
- **Status:** Pending outreach to KRENA (krena.kg)
