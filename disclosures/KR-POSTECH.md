---
institution: POSTECH
ip: 141.223.84.47
to: security@postech.ac.kr
severity: CRITICAL
status: DRAFT
date: 2026-05-01
---

**To:** security@postech.ac.kr
**Subject:** Unauthenticated AI inference endpoint — POSTECH (141.223.84.47)

---

Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com

2026-05-01

**Re:** Unauthenticated Ollama AI inference endpoint — POSTECH
**IP / Host:** 141.223.84.47
**Severity:** CRITICAL

---

I'm an independent security researcher. I hold CISA disclosures CVE-2025-4364 and ICSA-25-140-11 and conduct good-faith AI infrastructure research under the NuClide Research umbrella. This is an unsolicited disclosure — no engagement exists with your organization, and I have not accessed, modified, or exfiltrated any data beyond what was necessary to confirm the exposure.

---

## Summary

Pohang University of Science and Technology (POSTECH) has a 5-node BSP (Brain Science Platform) cluster with Ollama exposed on all nodes. The primary server has 18 active cloud proxy subscriptions including `kimi-k2:1t-cloud` (1 trillion parameters). Four satellite nodes each leak separate Ollama Connect SSH keypairs in 401 responses. All nodes publicly accessible, no authentication.

---

## Cluster Topology

| Node | IP | Hostname | Ollama Account | SSH Pubkey (truncated) |
|---|---|---|---|---|
| Main DGX | 141.223.84.47 | astros.postech.ac.kr | (18 cloud subs) | — |
| bsp-server-2 | 141.223.121.58 | siren.postech.ac.kr | `bsp-server-2` | `AAAAID0hdi+...` |
| bsp-server-6 | 141.223.121.73 | dragons.postech.ac.kr | `bsp-server-6` | `AAAAIHcp6+...` |
| bsp-server-10 | 141.223.121.77 | astros2.postech.ac.kr | `bsp-server-10` | `AAAAIIgasJ...` |
| bsp-server-12 | 141.223.121.80 | padres.postech.ac.kr | `bsp-server-12` | `AAAAIPY8Ib...` |

Naming pattern `bsp-server-N` (N = 2, 6, 10, 12) suggests the cluster has at least 12 nodes. Gaps in numbering indicate additional nodes not yet discovered.

---

## Infrastructure

| Field | Value |
|---|---|
| Primary IP | 141.223.84.47 |
| Cluster subnet | 141.223.121.0/24 (multiple nodes) |
| Org | Pohang University of Science and Technology |
| Country | South Korea |
| Open ports | 11434 (Ollama — **public on all nodes**) |

---

## Cloud Proxy Subscriptions (18)

| Model | Provider | Notes |
|---|---|---|
| kimi-k2:1t-cloud | Moonshot AI | **1 trillion parameter model** |
| deepseek-v3.1:671b-cloud | DeepSeek | 671B parameter model |
| qwen3-coder:480b-cloud | Alibaba Qwen | 480B coding model |
| gpt-oss:120b-cloud | OpenAI | 120B GPT-OSS |
| kimi-k2.6:cloud | Moonshot AI | — |
| kimi-k2.5:cloud | Moonshot AI | — |
| kimi-k2-thinking:cloud | Moonshot AI | — |
| glm-5.1:cloud | Zhipu AI | — |
| glm-5:cloud | Zhipu AI | — |
| glm-4.7:cloud | Zhipu AI | — |
| glm-4.6:cloud | Zhipu AI | — |
| deepseek-v4-pro:cloud | DeepSeek | — |
| deepseek-v4-flash:cloud | DeepSeek | — |
| deepseek-v3.2:cloud | DeepSeek | — |
| minimax-m2.7:cloud | MiniMax | — |
| minimax-m2.5:cloud | MiniMax | — |
| minimax-m2.1:cloud | MiniMax | — |
| minimax-m2:cloud | MiniMax | — |
| qwen3.5:cloud | Alibaba | — |
| qwen3-coder-next:cloud | Alibaba | — |
| nemotron-3-super:cloud | NVIDIA | — |
| gemini-3-flash-preview:cloud | Google | — |

---

## Findings

### F1 — 18 Cloud Subscriptions Exposed (CRITICAL)

All 18 cloud proxy subscriptions are accessible on the unauthenticated primary node. Any internet actor can:
- Enumerate all cloud subscriptions via `/api/tags`
- Inject system prompts into cloud proxy models via CVE-2025-63389
- Drain operator API quotas through the exposed port

The subscription portfolio includes frontier models: Kimi K2 (1T), DeepSeek V3.1 (671B), Qwen3-Coder (480B).

### F2 — 4 Credential Leaks Across Cluster Nodes (CRITICAL)

Four satellite nodes each leak a separate Ollama Connect SSH keypair in their 401 response body:

```json
// bsp-server-2 (141.223.121.58)
{"error":"unauthorized","signin_url":"https://ollama.com/connect?name=bsp-server-2&key=..."}
// SSH: ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAID0hdi+zn5fILlZ0zkL0N9J7wgFntb4IweWnfJzCoOtq

// bsp-server-6 (141.223.121.73)
// SSH: ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIHcp6+jJK6HzmVIhHwgMhzsL/t0n5NsbasdZQ4U/DDDj

// bsp-server-10 (141.223.121.77)
// SSH: ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIIgasJHMoumP9WevsQIsU2MCe3MVOotb7ppZT6gyCdJi

// bsp-server-12 (141.223.121.80)
// SSH: ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIPY8IbSqSueyuZ2kfRoffgayA7ErdbnYnVKTvG+0twg4
```

### F3 — Model Injection on Research Infrastructure (CRITICAL)

All models on all nodes injectable. POSTECH researchers using these models receive outputs shaped by injected system prompts.

---

**Why it matters**

Any internet actor can run inference against your cloud API subscription at your expense — this constitutes direct quota/billing theft. The credential leak (username + SSH public key) exposes your service account to enumeration and credential-stuffing against other services. An embedding model indicates an active RAG pipeline — documents loaded into your vector store are reachable via unauthenticated queries.

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
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT/blob/main/case-studies/universities/KR-POSTECH.md

This research is part of a broader sweep of university AI infrastructure exposures documented at:
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT/blob/main/case-studies/universities/OVERVIEW.md

I'm happy to answer questions or assist with verification. No response is required.

Regards,
Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT
