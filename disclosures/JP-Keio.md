---
institution: Keio University
ip: 131.113.41.213
to: security@keio.ac.jp
severity: CRITICAL
status: DRAFT
date: 2026-05-01
---

**To:** security@keio.ac.jp
**Subject:** Unauthenticated AI inference endpoint — Keio University (131.113.41.213)

---

Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com

2026-05-01

**Re:** Unauthenticated Ollama AI inference endpoint — Keio University
**IP / Host:** 131.113.41.213
**Severity:** CRITICAL

---

I'm an independent security researcher. I hold CISA disclosures CVE-2025-4364 and ICSA-25-140-11 and conduct good-faith AI infrastructure research under the NuClide Research umbrella. This is an unsolicited disclosure — no engagement exists with your organization, and I have not accessed, modified, or exfiltrated any data beyond what was necessary to confirm the exposure.

---

## Summary

Keio University (Japan) server with 8 Ollama models including two DeepSeek cloud proxy subscriptions and a 122-billion-parameter Qwen3.5 MoE model. Raw Ollama port publicly accessible without authentication. Cloud proxies require a higher-tier subscription (returned upgrade prompt, no credential leak). Full model injection surface via CVE-2025-63389.

---

## Infrastructure

| Field | Value |
|---|---|
| IP | 131.113.41.213 |
| Org | Keio University |
| Country | Japan |
| Open WebUI | 131.113.37.67:3000 — v0.3.32, auth=True (different IP) |
| Open ports | 11434 (Ollama — **public**) |

---

## Models

| Model | Size | Notes |
|---|---|---|
| **deepseek-v4-pro:cloud** | 0 GB | ☁️ Cloud proxy — DeepSeek Pro API |
| **deepseek-v4-flash:cloud** | 0 GB | ☁️ Cloud proxy — DeepSeek Flash API |
| qwen3.5:122b | 75 GB | Local — 122B MoE |
| qwen3-coder-next:latest | 48 GB | Local — coding model |
| qwen3.6:35b | 22 GB | Local |
| qwen3.6:latest | 22 GB | Local |
| gemma4:31b | 18 GB | Local |
| gemma4:31b-nvfp4 | 18 GB | Local (NV FP4 quantization) |

---

## Findings

### F1 — Unauthenticated Ollama API (CRITICAL)

Port 11434 publicly accessible. All 8 models enumerable without credentials.

### F2 — Dual DeepSeek Cloud Proxy Subscriptions (HIGH)

Two DeepSeek cloud proxy models registered. Subscription tier check returned:

```json
{
  "error": "this model requires a subscription, upgrade for access: https://ollama.com/upgrade",
  "ref": "684df060-4e09-4e03-a76d-c07d04eb77c9"
}
```

Cloud proxy models exist and are registered — quota drain is gated behind subscription tier, not external access control. A subscription-bearing Ollama account could call these directly.

### F3 — 122B-Parameter Free Inference (HIGH)

Any actor can run inference on `qwen3.5:122b` (75GB) without authentication:

```bash
curl http://131.113.41.213:11434/api/generate \
  -d '{"model":"qwen3.5:122b","prompt":"...","stream":false}'
```

Free compute at operator's hardware expense.

### F4 — Model Injection (CRITICAL)

All models injectable via CVE-2025-63389. Affects students/staff using the Open WebUI frontend at 131.113.37.67:3000.

---

**Why it matters**

Any internet actor can run inference against your cloud API subscription at your expense — this constitutes direct quota/billing theft. The credential leak (username + SSH public key) exposes your service account to enumeration and credential-stuffing against other services.

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
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT/blob/main/case-studies/universities/JP-Keio.md

This research is part of a broader sweep of university AI infrastructure exposures documented at:
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT/blob/main/case-studies/universities/OVERVIEW.md

I'm happy to answer questions or assist with verification. No response is required.

Regards,
Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT
