---
institution: Vietnam National University Hanoi
ip: 112.137.129.161
to: security@vnu.edu.vn
severity: HIGH
status: DRAFT
date: 2026-05-01
---

**To:** security@vnu.edu.vn
**Subject:** Unauthenticated AI inference endpoint — Vietnam National University Hanoi (112.137.129.161)

---

Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com

2026-05-01

**Re:** Unauthenticated Ollama AI inference endpoint — Vietnam National University Hanoi
**IP / Host:** 112.137.129.161
**Severity:** HIGH

---

I'm an independent security researcher. I hold CISA disclosures CVE-2025-4364 and ICSA-25-140-11 and conduct good-faith AI infrastructure research under the NuClide Research umbrella. This is an unsolicited disclosure — no engagement exists with your organization, and I have not accessed, modified, or exfiltrated any data beyond what was necessary to confirm the exposure.

---

## Summary

Vietnam National University Ha Noi has an Ollama instance with domain-specific fine-tuned models for legal (CaseHold), biomedical (PubMedQA), and financial (FinQA) question answering — indicating active NLP research pipelines publicly accessible without authentication.

---

## Infrastructure

| Field | Value |
|---|---|
| IP | 112.137.129.161 |
| rDNS | — |
| Org | VietNam National University Ha Noi |
| Country | Vietnam |
| Open ports | 11434 (Ollama — **public**) |

Note: This is a separate server from Hanoi University (103.185.232.21) documented in VN-hanoi.md.

---

## Models

| Model | Size | Notes |
|---|---|---|
| gemma4:latest | 8 GB | Local |
| gemma3:12b | 7 GB | Local |
| gemma3:4b | 3 GB | Local |
| llama3.2:1b | 1 GB | Local |
| xuananle/distill-CaseHold:latest | 1 GB | **Legal case classification** |
| pubmedqa-distilled:latest | 1 GB | **Biomedical QA** |
| finqa-distilled:latest | 1 GB | **Financial QA** |
| llama2:13b | 6 GB | Local |
| deepseek-r1:1.5b | 1 GB | Local |

---

## Findings

**F1 — Unauthenticated Ollama API (HIGH):** All models accessible. Research-grade domain-specific models (legal, medical, financial) exposed.

**F2 — Domain-Specific Research Models (MEDIUM):** `distill-CaseHold` (legal reasoning), `pubmedqa-distilled` (biomedical Q&A), `finqa-distilled` (financial analysis) — active research pipelines. Injection via CVE-2025-63389 affects domain responses.

---

**Why it matters**

Medical AI models exposed without authentication create compliance risk (potential HIPAA/patient-data adjacent exposure depending on RAG content).

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
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT/blob/main/case-studies/universities/VN-vnu-hanoi.md

This research is part of a broader sweep of university AI infrastructure exposures documented at:
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT/blob/main/case-studies/universities/OVERVIEW.md

I'm happy to answer questions or assist with verification. No response is required.

Regards,
Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT
