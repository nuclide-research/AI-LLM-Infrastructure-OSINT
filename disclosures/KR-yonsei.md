---
institution: Yonsei University
ip: 1.233.220.117
to: security@yonsei.ac.kr
severity: CRITICAL
status: DRAFT
date: 2026-05-01
---

**To:** security@yonsei.ac.kr
**Subject:** Unauthenticated AI inference endpoint — Yonsei University (1.233.220.117)

---

Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com

2026-05-01

**Re:** Unauthenticated Ollama AI inference endpoint — Yonsei University
**IP / Host:** 1.233.220.117
**Severity:** CRITICAL

---

I'm an independent security researcher. I hold CISA disclosures CVE-2025-4364 and ICSA-25-140-11 and conduct good-faith AI infrastructure research under the NuClide Research umbrella. This is an unsolicited disclosure — no engagement exists with your organization, and I have not accessed, modified, or exfiltrated any data beyond what was necessary to confirm the exposure.

---

## Summary

Yonsei University (Seoul, South Korea) is running Ollama on non-standard port 5004 with 17 cloud proxy subscriptions matching the pattern seen at POSTECH, Shiv Nadar, Hanoi University, and RIT. `minimax-m2.1:cloud` returns **200 OK** without credentials, confirming free-tier cloud quota drain. Local models include 75GB `qwen3.5:122b` and 65GB `gpt-oss:120b` (MXFP4), indicating a high-VRAM GPU server.

---

## Infrastructure

| Field | Value |
|---|---|
| IP | 1.233.220.117 |
| rDNS | — |
| Org | Yonsei University |
| Country | South Korea |
| Open ports | **5004** (Ollama non-standard port — **public**) |
| Timezone | UTC+9 (Korea) |

---

## Cloud Proxy Subscriptions (17)

| Model | Provider | Notes |
|---|---|---|
| kimi-k2-thinking:cloud | Moonshot AI | 1 trillion parameters |
| kimi-k2.6:cloud | Moonshot AI | — |
| kimi-k2.5:cloud | Moonshot AI | — |
| deepseek-v4-pro:cloud | DeepSeek | — |
| deepseek-v4-flash:cloud | DeepSeek | — |
| deepseek-v3.2:cloud | DeepSeek | 671B |
| minimax-m2.7:cloud | MiniMax | — |
| minimax-m2.5:cloud | MiniMax | — |
| **minimax-m2.1:cloud** | MiniMax | **200 OK confirmed — free-tier** |
| minimax-m2:cloud | MiniMax | 230B |
| glm-5.1:cloud | Zhipu AI | — |
| glm-5:cloud | Zhipu AI | — |
| glm-4.7:cloud | Zhipu AI | — |
| glm-4.6:cloud | Zhipu AI | 355B |
| qwen3.5:cloud | Alibaba | 397B |
| qwen3-coder-next:cloud | Alibaba | 80B |
| nemotron-3-super:cloud | NVIDIA | — |
| gemini-3-flash-preview:cloud | Google | — |

## Local Models

| Model | Size |
|---|---|
| qwen3.5:122b | 75 GB |
| qwen3.5:35b | 22 GB |
| qwen3.5:9b | 6 GB |
| gpt-oss:120b | 65 GB (MXFP4) |

---

## Findings

### F1 — Free-Tier Cloud Proxy 200 OK (CRITICAL)

`minimax-m2.1:cloud` returns full inference without credentials. 40 tokens consumed at operator expense:

```bash
curl -X POST http://1.233.220.117:5004/api/chat \
  -d '{"model":"minimax-m2.1:cloud","messages":[{"role":"user","content":"hi"}],"stream":false}'
# 200 OK — "Hi there! How can I help you today?"
```

### F2 — 17 Cloud Subscriptions on Non-Standard Port (CRITICAL)

Running Ollama on port 5004 instead of 11434. All 17 cloud subscriptions accessible.

### F3 — Same Cloud Bundle as POSTECH/Shiv Nadar/Hanoi/RIT (HIGH)

The 17-subscription cloud portfolio overlaps with the 18-bundle pattern seen at POSTECH (KR), Shiv Nadar (IN), Hanoi University (VN), and RIT (US). This is a distinct subset — shared Ollama Connect demonstration account or institutional bundle.

### F4 — Large Local Models (HIGH)

75GB and 65GB models accessible. Significant compute resources exposed to unauthenticated callers.

---

**Why it matters**

Any internet actor can run inference against your cloud API subscription at your expense — this constitutes direct quota/billing theft. The credential leak (username + SSH public key) exposes your service account to enumeration and credential-stuffing against other services.

**One-line fix**

```
OLLAMA_HOST=127.0.0.1:11434
systemctl restart ollama
```

This rebinds Ollama to loopback only. If running in Docker: `docker run -p 127.0.0.1:11434:11434 ollama/ollama`.

**Reference**

Full technical details, parameter counts, and remediation notes are in this public research repository:
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT/blob/main/case-studies/universities/KR-yonsei.md

This research is part of a broader sweep of university AI infrastructure exposures documented at:
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT/blob/main/case-studies/universities/OVERVIEW.md

I'm happy to answer questions or assist with verification. No response is required.

Regards,
Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT
