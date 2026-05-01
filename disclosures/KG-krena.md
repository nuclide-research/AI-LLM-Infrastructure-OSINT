---
institution: KRENA
ip: 178.217.174.90
to: noc@krena.kg
severity: CRITICAL
status: DRAFT
date: 2026-05-01
---

**To:** noc@krena.kg
**Subject:** Unauthenticated AI inference endpoint — KRENA (178.217.174.90)

---

Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com

2026-05-01

**Re:** Unauthenticated Ollama AI inference endpoint — KRENA
**IP / Host:** 178.217.174.90
**Severity:** CRITICAL

---

I'm an independent security researcher. I hold CISA disclosures CVE-2025-4364 and ICSA-25-140-11 and conduct good-faith AI infrastructure research under the NuClide Research umbrella. This is an unsolicited disclosure — no engagement exists with your organization, and I have not accessed, modified, or exfiltrated any data beyond what was necessary to confirm the exposure.

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

**Why it matters**

The credential leak (username + SSH public key) exposes your service account to enumeration and credential-stuffing against other services. An embedding model indicates an active RAG pipeline — documents loaded into your vector store are reachable via unauthenticated queries.

**One-line fix**

```
OLLAMA_HOST=127.0.0.1:11434
systemctl restart ollama
```

This rebinds Ollama to loopback only. If running in Docker: `docker run -p 127.0.0.1:11434:11434 ollama/ollama`.

**CVE-2025-63389**

All models on this instance are injectable via the unauthenticated `/api/create` endpoint — an attacker can overwrite any model's system prompt or delete models entirely. No patch exists as of this disclosure.

**Reference**

Full technical details, parameter counts, and remediation notes are in this public research repository:
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT/blob/main/case-studies/universities/KG-krena.md

This research is part of a broader sweep of university AI infrastructure exposures documented at:
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT/blob/main/case-studies/universities/OVERVIEW.md

I'm happy to answer questions or assist with verification. No response is required.

Regards,
Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT
