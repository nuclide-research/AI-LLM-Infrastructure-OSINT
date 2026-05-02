---
institution: Shandong Medical Graduate School
ip: 60.208.108.50
to: security@sdum.edu.cn
severity: CRITICAL
status: DRAFT
date: 2026-05-01
---

**To:** security@sdum.edu.cn
**Subject:** Unauthenticated AI inference endpoint — Shandong Medical Graduate School (60.208.108.50)

---

Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com

2026-05-01

**Re:** Unauthenticated Ollama AI inference endpoint — Shandong Medical Graduate School
**IP / Host:** 60.208.108.50
**Severity:** CRITICAL

---

I'm an independent security researcher. I hold CISA disclosures CVE-2025-4364 and ICSA-25-140-11 and conduct good-faith AI infrastructure research under the NuClide Research umbrella. This is an unsolicited disclosure — no engagement exists with your organization, and I have not accessed, modified, or exfiltrated any data beyond what was necessary to confirm the exposure.

---

## Summary

A Shandong Province medicine video graduate school (China) is running Ollama with the 376GB local DeepSeek V3 model (identical stack to Shiv Nadar University, India), an abliterated DeepSeek-R1-Distill-Qwen-32B reasoning model, and a MiniMax cloud proxy. The cloud proxy leaks credentials for account `bowee`. Unauthenticated, publicly accessible.

---

## Infrastructure

| Field | Value |
|---|---|
| IP | 60.208.108.50 |
| rDNS | — (NXDOMAIN) |
| Org | Shandong Province medicine video graduate school |
| Country | China |
| Open ports | 11434 (Ollama — **public**) |

---

## Models

| Model | Size | Notes |
|---|---|---|
| lordoliver/DeepSeek-V3-0324:671b-q4_k_m | 376 GB | **Same 376GB model as Shiv Nadar (IN)** |
| hf.co/bartowski/DeepSeek-R1-Distill-Qwen-32B-abliterated-GGUF:Q3_K_M | 14 GB | **Abliterated DeepSeek-R1-Distill** |
| minimax-m2.7:cloud | 0 GB | ☁️ Cloud proxy |
| llama3.2:3b | 1 GB | Local |

---

## Credential Leak

```json
{
  "error": "unauthorized",
  "signin_url": "https://ollama.com/connect?name=bowee&key=<base64>"
}
```

- **Username:** `bowee`
- **SSH Public Key:** `ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIL1tODW/n9caizUJ42IUq8cTYdYlN4z1eVjhOAWfk1Dz`

---

## Findings

**F1 — 376GB DeepSeek V3 Local Model Exposed (CRITICAL):** `lordoliver/DeepSeek-V3-0324:671b-q4_k_m` is a 376GB q4 quantized local deployment of DeepSeek-V3. Identical model seen at Shiv Nadar University (India). Accessible without authentication.

**F2 — Abliterated DeepSeek-R1-Distill (HIGH):** `DeepSeek-R1-Distill-Qwen-32B-abliterated` has safety fine-tuning removed. A reasoning model with abliterated safety guardrails on a Chinese medical graduate school server.

**F3 — Cloud Proxy Credential Leak (HIGH):** `minimax-m2.7:cloud` leaks Ollama Connect username `bowee` and SSH public key.

**F4 — Model Injection (HIGH):** All 4 models injectable via CVE-2025-63389.

---

## Pattern Note

The `lordoliver/DeepSeek-V3-0324:671b-q4_k_m` model at 376GB is an unusual deployment for a graduate school — possibly the same model distribution channel as seen at Shiv Nadar University (India, 103.27.166.x). The username `bowee` is likely a Chinese Pinyin or abbreviated personal name.

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
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT/blob/main/case-studies/universities/CN/shandong-med.md

This research is part of a broader sweep of university AI infrastructure exposures documented at:
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT/blob/main/case-studies/universities/OVERVIEW.md

I'm happy to answer questions or assist with verification. No response is required.

Regards,
Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT
