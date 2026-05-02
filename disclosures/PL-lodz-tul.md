---
institution: Technical University of Łódź
ip: 212.51.215.102
to: bok@p.lodz.pl
cc: cert@pionier.gov.pl
severity: HIGH
status: DRAFT
date: 2026-05-01
---

**To:** bok@p.lodz.pl
**Cc:** cert@pionier.gov.pl
**Subject:** Unauthenticated AI inference endpoint — Technical University of Łódź (212.51.215.102)

---

Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com

2026-05-01

**Re:** Unauthenticated Ollama AI inference endpoint — Technical University of Łódź
**IP / Host:** 212.51.215.102
**Severity:** HIGH

---

I'm an independent security researcher. I hold CISA disclosures CVE-2025-4364 and ICSA-25-140-11 and conduct good-faith AI infrastructure research under the NuClide Research umbrella. This is an unsolicited disclosure — no engagement exists with your organization, and I have not accessed, modified, or exfiltrated any data beyond what was necessary to confirm the exposure.

---

## Summary

Technical University of Łódź (Politechnika Łódzka) has an Ollama instance on `xray02.p.lodz.pl` with 3 models including a 20GB DeepSeek-R1 and `lukashabtoch/plutotext-r3-emotional:latest` — the same custom emotional-roleplay model observed independently at CEFET/RJ in Brazil and other nodes, indicating cross-institutional propagation of an obscure community fine-tune.

---

## Infrastructure

| Field | Value |
|---|---|
| IP | 212.51.215.102 |
| Hostname | xray02.p.lodz.pl |
| Organization | Technical University of Łódź (Politechnika Łódzka) |
| Country | Poland |
| Open ports | 11434 (Ollama — public) |

---

## Model Inventory

| Model | Size | Notes |
|---|---|---|
| `deepseek-r1:32b` | 19.9GB | 32.8B params, Qwen2 family |
| `lukashabtoch/plutotext-r3-emotional:latest` | 4.9GB | 8.0B params, emotional roleplay fine-tune |
| `llama3.2:3b` | 2.0GB | — |

---

## Findings

### F1 — Cross-Network Model Propagation (MEDIUM)

`lukashabtoch/plutotext-r3-emotional:latest` is a low-citation community fine-tune for emotional roleplay. This exact model appears on at least two geographically unrelated institutions (Łódź, Poland and CEFET/RJ, Brazil) suggesting it propagates through shared Hugging Face download patterns or operator-to-operator social sharing. Uncommon model identifiers like this can serve as Shodan/HTTP banner search correlators for cross-network attribution.

### F2 — Unauthenticated Inference on Research Server (HIGH)

`deepseek-r1:32b` (19.9GB, 32.8B params) is accessible without authentication. The hostname `xray02` suggests an X-ray / radiological research compute node, making the exposure pattern consistent with a research GPU being repurposed for LLM workloads without access controls.

### F3 — CVE-2025-63389 Injectable (HIGH)

All models injectable via unauthenticated `/api/create`.

---

**Why it matters**

Any internet actor can run uncapped inference against your GPU at your compute cost, and inject malicious system prompts into any loaded model via CVE-2025-63389.

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
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT/blob/main/case-studies/universities/PL/lodz-tul.md

This research is part of a broader sweep of university AI infrastructure exposures documented at:
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT/blob/main/case-studies/universities/OVERVIEW.md

I'm happy to answer questions or assist with verification. No response is required.

Regards,
Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT
