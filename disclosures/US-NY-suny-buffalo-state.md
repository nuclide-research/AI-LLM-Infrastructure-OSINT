---
to: killiatd@buffalostate.edu
cc: abuse@buffalostate.edu
severity: CRITICAL
ip: 136.183.56.88
institution: SUNY Buffalo State University
status: DRAFT
outcome: sent
date: 2026-05-04
---

**To:** killiatd@buffalostate.edu
**Cc:** abuse@buffalostate.edu
**Subject:** Unauthenticated AI inference endpoint — SUNY Buffalo State University (136.183.56.88) [resend, correctly routed]

---

Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com

2026-05-04

**Re:** Unauthenticated Ollama AI inference endpoint — SUNY Buffalo State University
**IP / Host:** 136.183.56.88
**Severity:** CRITICAL

---

I'm an independent security researcher. I hold CISA disclosures CVE-2025-4364 and ICSA-25-140-11 and conduct good-faith AI infrastructure research under the NuClide Research umbrella. This is an unsolicited disclosure — no engagement exists with your organization, and I have not accessed, modified, or exfiltrated any data beyond what was necessary to confirm the exposure.

**Note on prior misroute:** I sent the same finding earlier today routed to University at Buffalo (`buffalo.edu`) — that was a bug in my disclosure pipeline's domain-resolution heuristic. ARIN WHOIS for `136.183.0.0/16` correctly identifies your institution (`NetName SUCBUFFALO`, `OrgName SUNY Buffalo State University`, `OrgAbuseEmail killiatd@buffalostate.edu`). Catherine Ullman at UB IT Security flagged the misroute. Corrected and resent here. Apologies for the noise.

---

## Summary

State University of New York at Buffalo State research compute node running 26 Ollama models including `gemma4:31b-cloud`, a cloud proxy model. **Cloud proxy inference confirmed live — 200 OK response at operator expense.** Also includes RAG pipeline components (embedding model + reranker) and a 74GB Mixtral instance. Raw Ollama port publicly accessible, no authentication.

---

## Infrastructure

| Field | Value |
|---|---|
| IP | 136.183.56.88 |
| Org | SUNY Buffalo State University (per ARIN: `NetName SUCBUFFALO`, `OrgName SUNY Buffalo State University`) |
| Country | US — New York |
| Open ports | 11434 (Ollama — **public**) |

---

## Models (26 total)

| Model | Size | Notes |
|---|---|---|
| **gemma4:31b-cloud** | 0 GB | **☁️ Cloud proxy — CONFIRMED LIVE** |
| mixtral:8x22b-instruct | 74 GB | Local — MoE |
| qwen2.5:72b-instruct | 44 GB | Local |
| llama3.1:70b | 39 GB | Local |
| qwen3.5:35b | 22 GB | Local |
| qwen2.5:32b-instruct | 18 GB | Local |
| gemma4:31b-it-q4_K_M | 18 GB | Local |
| gemma4:31B | 18 GB | Local |
| glm-4.7-flash:latest | 17 GB | Local (Zhipu AI) |
| (16 additional smaller models, full list in case study) | — | — |

---

## Findings

### F1 — Unauthenticated Ollama (CRITICAL)

Port 11434 is publicly accessible without any auth. All 26 models enumerable via `/api/tags`; all injectable via the unauthenticated `/api/create` endpoint (CVE-2025-63389).

### F2 — Cloud Proxy Quota Theft (HIGH — confirmed live)

`gemma4:31b-cloud` is a cloud-proxy model that routes inference through Ollama's commercial cloud at the operator's billing expense. Confirmed live by a non-destructive `/api/generate` call returning HTTP 200 + 2 tokens of completion.

### F3 — RAG Pipeline Components (HIGH)

The deployment includes a BGE-M3 embedding model and a BGE-reranker-v2-M3, indicating an active RAG pipeline. If this Ollama instance backs a document retrieval system with university data, model injection via CVE-2025-63389 would affect all RAG-augmented responses.

---

**Why it matters**

The cloud-proxy model is direct billing-impact on the operator's Ollama Cloud subscription. Attacker scripted abuse can drain quota at scale. The RAG pipeline indicates indexed documents — possibly research data, internal documentation, or course materials — accessible via unauth queries. Model injection (CVE-2025-63389) compromises any downstream use of Aiden Assistant-equivalent services on this instance.

**One-line fix**

```
OLLAMA_HOST=127.0.0.1:11434
systemctl restart ollama
```

This rebinds Ollama to loopback only.

**CVE-2025-63389**

All models on this instance are injectable via the unauthenticated `/api/create` endpoint. No patch exists as of this disclosure.

**Reference**

Full case study: https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT/blob/main/case-studies/universities/US/NY-suny-buffalo.md

I'm happy to answer questions or assist with verification. No response is required.

Regards,
Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT
