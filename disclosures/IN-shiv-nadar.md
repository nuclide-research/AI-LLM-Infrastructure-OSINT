---
institution: Shiv Nadar University
ip: 103.27.166.36 (+3 nodes)
to: security@snu.edu.in
severity: CRITICAL
status: DRAFT
date: 2026-05-01
---

**To:** security@snu.edu.in
**Subject:** Unauthenticated AI inference endpoint — Shiv Nadar University (103.27.166.36 (+3 nodes))

---

Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com

2026-05-01

**Re:** Unauthenticated Ollama AI inference endpoint — Shiv Nadar University
**IP / Host:** 103.27.166.36 (+3 nodes)
**Severity:** CRITICAL

---

I'm an independent security researcher. I hold CISA disclosures CVE-2025-4364 and ICSA-25-140-11 and conduct good-faith AI infrastructure research under the NuClide Research umbrella. This is an unsolicited disclosure — no engagement exists with your organization, and I have not accessed, modified, or exfiltrated any data beyond what was necessary to confirm the exposure.

---

## Summary

Shiv Nadar Institution of Eminence (India, Noida) is running a shared AI infrastructure cluster with multiple exposed nodes, collectively serving 76 models including a 376GB local DeepSeek-V3-0324 (671B parameters), `qwen3:235b` (132GB), and 18 cloud proxy subscriptions. Raw Ollama port publicly accessible on multiple nodes.

---

## Infrastructure

| Node | IP | Hostname |
|------|-----|----------|
| Node 1 | 103.27.166.36 | 36-166-27-103.noida.snu.in |
| Node 2 | 103.27.166.38 | 38-166-27-103.noida.snu.in |
| Node 3 | 103.27.166.39 | 39-166-27-103.noida.snu.in |

All nodes in the 103.27.166.0/24 subnet (`noida.snu.in`). All bind Ollama to 0.0.0.0:11434 without authentication.

---

## Model Scale (per node, 76 models)

| Model | Size | Notes |
|---|---|---|
| lordoliver/DeepSeek-V3-0324:671b-q4_k_m | **376 GB** | 671B parameter DeepSeek |
| qwen3:235b | 132 GB | 235B MoE model |
| llama4:latest | 62 GB | Local |
| gpt-oss:120b | 60 GB | OpenAI open model |
| llama3.2-vision:90b | 50 GB | Vision-language, 90B |
| (53 more local models) | varies | |
| (18 cloud proxy models) | 0 GB each | DeepSeek, MiniMax, Kimi, Qwen, GLM, Gemini, Nemotron, NVIDIA |

---

## Findings

### F1 — Multi-Node Cluster Fully Exposed (CRITICAL)

Three nodes on the `noida.snu.in` subnet all expose port 11434 without authentication. The shared model set is injectable across all nodes simultaneously.

### F2 — 671B Local Model Accessible for Free Inference (HIGH)

`lordoliver/DeepSeek-V3-0324:671b-q4_k_m` (376GB) is accessible without authentication. Any internet actor can run inference against one of the most capable open-weight models on dedicated university GPU infrastructure at the operator's cost.

### F3 — 18 Cloud Subscriptions Exposed (CRITICAL)

Same cloud proxy portfolio as POSTECH (shared Ollama Connect account or same ecosystem): DeepSeek, MiniMax, Kimi, Qwen, GLM, Gemini, Nemotron/NVIDIA.

### F4 — Model Injection on All 76 Models (CRITICAL)

CVE-2025-63389 applies to all 76 models across all three nodes. Any researcher on this shared cluster using these models receives outputs under attacker-controlled instructions after injection.

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
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT/blob/main/case-studies/universities/IN-shiv-nadar.md

This research is part of a broader sweep of university AI infrastructure exposures documented at:
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT/blob/main/case-studies/universities/OVERVIEW.md

I'm happy to answer questions or assist with verification. No response is required.

Regards,
Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT
