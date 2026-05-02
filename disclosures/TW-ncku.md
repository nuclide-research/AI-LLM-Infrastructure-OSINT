---
institution: National Cheng Kung University
ip: 140.116.158.98
to: mailservice@ncku.edu.tw
severity: CRITICAL
status: DRAFT
date: 2026-05-01
---

**To:** mailservice@ncku.edu.tw
**Subject:** Unauthenticated AI inference endpoint — National Cheng Kung University (140.116.158.98)

---

Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com

2026-05-01

**Re:** Unauthenticated Ollama AI inference endpoint — National Cheng Kung University
**IP / Host:** 140.116.158.98
**Severity:** CRITICAL

---

I'm an independent security researcher. I hold CISA disclosures CVE-2025-4364 and ICSA-25-140-11 and conduct good-faith AI infrastructure research under the NuClide Research umbrella. This is an unsolicited disclosure — no engagement exists with your organization, and I have not accessed, modified, or exfiltrated any data beyond what was necessary to confirm the exposure.

---

## Summary

National Cheng Kung University (NCKU), one of Taiwan's top engineering universities, has an Ollama instance running on non-standard port 22222. The MiniMax cloud proxy leaks the Ollama Connect account `nckusoc-3090` — indicating NCKU School of Computing (SOC) department server with an NVIDIA RTX 3090 GPU.

---

## Infrastructure

| Field | Value |
|---|---|
| IP | 140.116.158.98 |
| rDNS | — |
| Org | Ministry of Education Computer Center (TANET) |
| Institution | National Cheng Kung University — SOC Department |
| Country | Taiwan |
| Open ports | **22222** (Ollama non-standard port — **public**) |

Note: IP routes through Taiwan's Ministry of Education TANET network, shared by major Taiwanese universities.

---

## Models

| Model | Size | Type | Cred Leak |
|---|---|---|---|
| minimax-m2.7:cloud | 0 GB | ☁️ Cloud proxy | **`nckusoc-3090`** |
| qwen3.6:35b | 22 GB | Local | — |
| gpt-oss:20b | 12 GB | Local | — |
| mistral-small3.2:24b | 14 GB | Local | — |
| gemma3:27b | 16 GB | Local | — |
| gemma3:12b | 7 GB | Local | — |
| gemma3:4b | 3 GB | Local | — |
| llama3.2:3b | 1 GB | Local | — |

---

## Credential Leak

```json
{
  "error": "unauthorized",
  "signin_url": "https://ollama.com/connect?name=nckusoc-3090&key=<base64>"
}
```

- **Username:** `nckusoc-3090`
- **SSH Public Key:** `ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIMwH+iskAm2POkZim1R1+IHud67QvLGpB7DRs19xh/pb`

`nckusoc` = NCKU School of Computing; `3090` = NVIDIA RTX 3090 GPU identifier.

---

## Findings

**F1 — Credential Leak via Non-Standard Port (HIGH):** Ollama running on port 22222 instead of default 11434. MiniMax cloud proxy leaks `nckusoc-3090` account credentials.

**F2 — Model Injection (HIGH):** All 8 models injectable via CVE-2025-63389.

---

## Taiwan MOE TANET Context

Multiple Taiwanese universities share the MOE TANET (Taiwan Academic Network) IP space (140.112.x.x - NTU, 140.114.x.x - NTHU, 140.116.x.x - NCKU, 140.136.x.x - FJU). Ollama instances observed across this network on 2026-05-01:

| IP | Institution | Models | Cloud |
|---|---|---|---|
| 140.112.91.82 | NTU (Electrical Engineering) | 4 | minimax-m2.7 |
| 140.112.18.214 | NTU (PC-214) | 5 | — |
| 140.112.233.108 | NTU (GPU cluster g1) | 11 | — |
| 140.116.82.105 | NCKU / TANET | 8 | deepseek-v4-pro |
| 140.116.158.98 | **NCKU (SOC-3090)** | 8 | minimax-m2.7 |
| 140.136.192.220 | FJU (Medical Public Health) | 8 | — |
| 140.136.239.75 | FJU (net2net) | 5 | — |
| 163.25.105.115 | TANET node | 9 | — |
| 163.13.202.114 | TANET node | 2 | — |
| 140.136.149.212 | TANET node | 2 | — |
| 210.70.138.233 | TANET node | 3 | — |

---

**Why it matters**

The credential leak (username + SSH public key) exposes your service account to enumeration and credential-stuffing against other services. Medical AI models exposed without authentication create compliance risk (potential HIPAA/patient-data adjacent exposure depending on RAG content).

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
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT/blob/main/case-studies/universities/TW/ncku.md

This research is part of a broader sweep of university AI infrastructure exposures documented at:
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT/blob/main/case-studies/universities/OVERVIEW.md

I'm happy to answer questions or assist with verification. No response is required.

Regards,
Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT
