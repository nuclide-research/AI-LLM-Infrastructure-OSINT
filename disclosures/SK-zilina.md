---
institution: University of Žilina
ip: 158.193.144.224
to: security@uniza.sk
severity: CRITICAL
status: DRAFT
date: 2026-05-01
---

**To:** security@uniza.sk
**Subject:** Unauthenticated AI inference endpoint — University of Žilina (158.193.144.224)

---

Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com

2026-05-01

**Re:** Unauthenticated Ollama AI inference endpoint — University of Žilina
**IP / Host:** 158.193.144.224
**Severity:** CRITICAL

---

I'm an independent security researcher. I hold CISA disclosures CVE-2025-4364 and ICSA-25-140-11 and conduct good-faith AI infrastructure research under the NuClide Research umbrella. This is an unsolicited disclosure — no engagement exists with your organization, and I have not accessed, modified, or exfiltrated any data beyond what was necessary to confirm the exposure.

---

## Summary

A student laptop at the University of Žilina (Slovakia, Faculty of Mechanical Engineering) has Ollama bound to 0.0.0.0 with three Ollama Connect cloud proxy models all returning **200 OK** without credentials. The cloud proxies give any internet caller unauthenticated inference access to Devstral-2 (123B), DeepSeek V3.1 (671B), and Qwen3 Coder (480B) at the operator's expense.

---

## Infrastructure

| Field | Value |
|---|---|
| IP | 158.193.144.224 |
| rDNS | `LAPTOP-N7ADDUK8.kst.fri.uniza.sk` |
| Org | University of Žilina |
| Faculty | Mechanical Engineering (kst.fri.uniza.sk) |
| Country | Slovakia |
| Open ports | 11434 (Ollama — **public**) |

---

## Models

| Model | Size | Type | 200 OK? |
|---|---|---|---|
| devstral-2:123b-cloud | 0 GB | ☁️ Cloud proxy | **YES — 48 tokens** |
| deepseek-v3.1:671b-cloud | 0 GB | ☁️ Cloud proxy | **YES — streaming** |
| qwen3-coder:480b-cloud | 0 GB | ☁️ Cloud proxy | **YES — 10 tokens** |
| deepseek-r1:7b | 4 GB | Local | — |
| phi3:latest | 2 GB | Local | — |
| glm-4.7-flash:latest | 17 GB | Local | — |
| llama3.2:3b | 1 GB | Local | — |
| smollm2:135m | 0 GB | Local | — |
| llama3:latest | 4 GB | Local | — |
| codellama:latest | 3 GB | Local | — |

**Devstral** is Mistral's code-specialized frontier model. **DeepSeek V3.1 671B** and **Qwen3 Coder 480B** are among the largest models available via cloud proxy. All three are **free-tier** Ollama cloud models that do not require credentials — any caller can run unlimited inference.

---

## Findings

### F1 — Three Free-Tier Cloud Proxies, 200 OK (CRITICAL)

All three cloud proxy models return full inference responses without authentication. Confirmed token consumption during research:

```bash
curl -X POST http://158.193.144.224:11434/api/chat \
  -d '{"model":"devstral-2:123b-cloud","messages":[{"role":"user","content":"hi"}],"stream":false}'
# 200 OK, 48 tokens returned at operator expense

curl -X POST http://158.193.144.224:11434/api/chat \
  -d '{"model":"qwen3-coder:480b-cloud","messages":[{"role":"user","content":"hi"}],"stream":false}'
# 200 OK, 10 tokens returned at operator expense
```

### F2 — Laptop Exposed via Docker / 0.0.0.0 Binding (HIGH)

Hostname `LAPTOP-N7ADDUK8.kst.fri.uniza.sk` confirms this is a student or researcher's personal laptop connected to the campus network. Ollama bound to `0.0.0.0` routes the port to the internet when the machine is on a campus-facing IP.

### F3 — Model Injection (HIGH)

All 10 models injectable via CVE-2025-63389 — no patch available.

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
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT/blob/main/case-studies/universities/SK-zilina.md

This research is part of a broader sweep of university AI infrastructure exposures documented at:
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT/blob/main/case-studies/universities/OVERVIEW.md

I'm happy to answer questions or assist with verification. No response is required.

Regards,
Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT
