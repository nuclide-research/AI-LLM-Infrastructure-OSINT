---
institution: National Taiwan University
ip: 140.112.233.108
to: security@ntu.edu.tw
severity: HIGH
status: DRAFT
date: 2026-05-01
---

**To:** security@ntu.edu.tw
**Subject:** Unauthenticated AI inference endpoint — National Taiwan University (140.112.233.108)

---

Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com

2026-05-01

**Re:** Unauthenticated Ollama AI inference endpoint — National Taiwan University
**IP / Host:** 140.112.233.108
**Severity:** HIGH

---

I'm an independent security researcher. I hold CISA disclosures CVE-2025-4364 and ICSA-25-140-11 and conduct good-faith AI infrastructure research under the NuClide Research umbrella. This is an unsolicited disclosure — no engagement exists with your organization, and I have not accessed, modified, or exfiltrated any data beyond what was necessary to confirm the exposure.

---

## Summary

NTU's GPU cluster node `g1pc2n108.g1.ntu.edu.tw` (140.112.233.108) has Ollama exposed on port 11434 with 11 models skewed heavily toward vision and multimodal tasks — including GLM-OCR, GLM-4.7-Flash, MiniCPM-V, LLaVA, and llama3.2-vision.

---

## Infrastructure

| Field | Value |
|---|---|
| IP | 140.112.233.108 |
| Hostname | g1pc2n108.g1.ntu.edu.tw |
| Organization | National Taiwan University — GPU Cluster 1, Node 108 |
| Network | Taiwan MOE TANet (140.112.0.0/16) |
| Country | Taiwan |
| Open ports | 11434 (Ollama — public) |

---

## Model Inventory

| Model | Size | Category |
|---|---|---|
| `glm-4.7-flash:latest` | 17GB | ZhipuAI GLM-4.7 vision-language |
| `glm-ocr:latest` | 2GB | ZhipuAI OCR model (1.1B params) |
| `llama3.2-vision:latest` | 7GB | Meta vision-language |
| `minicpm-v:latest` | 5GB | MiniCPM-V multimodal |
| `llava:7b` | 4GB | LLaVA vision-language |
| `moondream:latest` | 1GB | Lightweight vision model |
| `qwen3.5:latest` | 6GB | Text LLM |
| `llama3.2:3b` | 1GB | Small LLM |
| `llama3.2:latest` | 1GB | — |
| `llama3:latest` | 4GB | — |
| `qwen:latest` | 2GB | — |

---

## Findings

### F1 — Unauthenticated Inference on University GPU Cluster (HIGH)

All 11 models are publicly accessible without authentication. The heavy multimodal/vision focus — GLM-4.7-Flash, GLM-OCR, LLaVA, MiniCPM-V, moondream, llama3.2-vision — indicates this node serves active vision research or document processing workflows.

**GLM-OCR** (glm-ocr:latest) is a specialized optical character recognition model. Any documents being processed through this pipeline are accessible to unauthenticated callers.

### F2 — CVE-2025-63389 Injectable (HIGH)

All 11 models injectable via unauthenticated `/api/create`.

---

## NTU Footprint

Multiple NTU nodes have been identified across different departments:

| Node | IP | Hostname | Notes |
|---|---|---|---|
| EE Dept | 140.112.91.82 | — | Engineering department node |
| PC-214 | 140.112.18.214 | — | Workstation/lab |
| GPU Cluster 1 Node 108 | 140.112.233.108 | g1pc2n108.g1.ntu.edu.tw | Vision stack |

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
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT/blob/main/case-studies/universities/TW/ntu-gpu.md

This research is part of a broader sweep of university AI infrastructure exposures documented at:
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT/blob/main/case-studies/universities/OVERVIEW.md

I'm happy to answer questions or assist with verification. No response is required.

Regards,
Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT
