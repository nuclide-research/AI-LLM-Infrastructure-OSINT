---
institution: Shiv Nadar University
ip: 103.27.166.36 (+4 nodes, 5 total)
to: security@snu.edu.in
severity: CRITICAL
status: DRAFT
date: 2026-05-03
---

**To:** security@snu.edu.in
**Subject:** Unauthenticated AI inference endpoint — Shiv Nadar University (5-node cluster, 103.27.166.36–.40)

---

Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com

2026-05-01

**Re:** Unauthenticated Ollama AI inference endpoint — Shiv Nadar University
**IP / Host:** 103.27.166.36–103.27.166.40 (5-node cluster)
**Severity:** CRITICAL

---

I'm an independent security researcher. I hold CISA disclosures CVE-2025-4364 and ICSA-25-140-11 and conduct good-faith AI infrastructure research under the NuClide Research umbrella. This is an unsolicited disclosure — no engagement exists with your organization, and I have not accessed, modified, or exfiltrated any data beyond what was necessary to confirm the exposure.

---

## Summary

Shiv Nadar Institution of Eminence (India, Noida) is running a 5-node shared AI cluster with all nodes exposed on 0.0.0.0:11434, collectively serving 75+ models per node. These include a 376GB local DeepSeek-V3-0324 (671B parameters), `qwen3:235b` (132GB), chest X-ray / lung AI research models, and 30+ cloud proxy subscriptions including pre-release `deepseek-v4-pro:cloud`, `devstral-2:123b-cloud`, and `qwen3.5:397b-cloud`. The cluster grew from 3 to 5 nodes between initial discovery (2026-05-01) and this disclosure update (2026-05-03), indicating active infrastructure buildout under continued exposure.

---

## Infrastructure

| Node | IP | Hostname | Notes |
|------|-----|----------|-------|
| Node 1 | 103.27.166.36 | 36-166-27-103.noida.snu.in | cloud proxy |
| Node 2 | 103.27.166.37 | 37-166-27-103.noida.snu.in | cloud proxy + **medical AI** |
| Node 3 | 103.27.166.38 | 38-166-27-103.noida.snu.in | cloud proxy |
| Node 4 | 103.27.166.39 | 39-166-27-103.noida.snu.in | cloud proxy + image gen |
| Node 5 | 103.27.166.40 | 40-166-27-103.noida.snu.in | cloud proxy |

All nodes in the 103.27.166.0/24 subnet (`noida.snu.in`). All bind Ollama to 0.0.0.0:11434 without authentication. All running v0.15.2. The cluster expanded from 3 to 5 nodes between 2026-05-01 and 2026-05-03.

---

## Model Scale (~75 models per node)

| Model | Size | Notes |
|---|---|---|
| lordoliver/DeepSeek-V3-0324:671b-q4_k_m | **376 GB** | 671B parameter local DeepSeek |
| qwen3:235b | 132 GB | 235B MoE model |
| llama3.2-vision:90b | 50 GB | Vision-language, 90B |
| llama4:latest | 62 GB | Meta Llama 4 |
| gpt-oss:120b | 60 GB | OpenAI open model |
| (40+ more local models) | varies | Vision, coding, reasoning, medical |
| x/flux2-klein:latest | 5.3 GB | **Image generation (FLUX 2)** |
| deepseek-v4-pro:cloud | — | **Pre-release DeepSeek V4** |
| deepseek-v4-flash:cloud | — | **Pre-release DeepSeek V4 Flash** |
| devstral-2:123b-cloud | — | Mistral Devstral 2 (123B agent model) |
| qwen3.5:397b-cloud | — | 397B MoE via cloud |
| (26 more cloud models) | — | Kimi, GLM, MiniMax, Gemini, NVIDIA, Qwen |

---

## Findings

### F1 — 5-Node Cluster Fully Exposed and Growing (CRITICAL)

All five nodes on the `noida.snu.in` subnet expose port 11434 without authentication. The cluster grew from 3 to 5 nodes between 2026-05-01 and 2026-05-03 while remaining fully exposed — the infrastructure is actively expanding without security improvements. The shared model set is injectable across all nodes simultaneously.

### F2 — 671B Local Model Accessible for Free Inference (HIGH)

`lordoliver/DeepSeek-V3-0324:671b-q4_k_m` (376GB) is accessible without authentication. Any internet actor can run frontier-class inference at the operator's electricity and hardware cost.

### F3 — 30+ Cloud Subscriptions Exposed, Including Pre-Release Models (CRITICAL)

30+ cloud proxy models are exposed across all nodes, including `deepseek-v4-pro:cloud` and `deepseek-v4-flash:cloud` (pre-release DeepSeek V4 only available via Ollama Connect beta), `devstral-2:123b-cloud` (Mistral's 123B agent model), and `qwen3.5:397b-cloud` (397B MoE). Any actor can consume these premium/beta subscriptions at the operator's cost.

### F4 — Model Injection on All ~75 Models per Node (CRITICAL)

CVE-2025-63389 applies to all models across all five nodes. Any researcher using these models — including the lung AI tools and medical LLMs — receives outputs under attacker-controlled instructions after a single unauthenticated `/api/create` POST.

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
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT/blob/main/case-studies/universities/international/IN/shiv-nadar.md

This research is part of a broader sweep of university AI infrastructure exposures documented at:
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT/blob/main/case-studies/universities/OVERVIEW.md

I'm happy to answer questions or assist with verification. No response is required.

Regards,
Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT
