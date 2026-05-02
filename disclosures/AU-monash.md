---
institution: Monash University
ip: 118.138.233.225
to: cyberteam@monash.edu
severity: CRITICAL
status: DRAFT
date: 2026-05-01
---

**To:** cyberteam@monash.edu
**Subject:** Unauthenticated AI inference endpoint — Monash University (118.138.233.225)

---

Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com

2026-05-01

**Re:** Unauthenticated Ollama AI inference endpoint — Monash University
**IP / Host:** 118.138.233.225
**Severity:** CRITICAL

---

I'm an independent security researcher. I hold CISA disclosures CVE-2025-4364 and ICSA-25-140-11 and conduct good-faith AI infrastructure research under the NuClide Research umbrella. This is an unsolicited disclosure — no engagement exists with your organization, and I have not accessed, modified, or exfiltrated any data beyond what was necessary to confirm the exposure.

---

## Summary

Monash University (Melbourne, Australia) has an Ollama instance at `vm-118-138-233-225.erc.monash.edu.au` with 8 models totalling over 510GB of local inference including a full **DeepSeek V3.1 671B** (404.5GB) — tied with KRENA for largest local deployment in this sweep. Two cloud proxies are present.

---

## Infrastructure

| Field | Value |
|---|---|
| IP | 118.138.233.225 |
| Hostname | vm-118-138-233-225.erc.monash.edu.au |
| Organization | Monash University |
| Network | Monash ERC (Education and Research Cluster — 118.138.0.0/16) |
| Country | Australia |
| Open ports | 11434 (Ollama — public) |

Two additional Monash nodes on the same subnet (118.138.243.239, 118.138.243.34) host smaller stacks (deepseek-r1:latest, qwen2.5, llama3 — 3 models each).

---

## Model Inventory (Primary Node)

| Model | Size | Notes |
|---|---|---|
| `deepseek-v3.1:latest` | **404.5GB** | **671.0B params**, DeepSeek2 family — largest model in sweep |
| `qwen3-coder-next:latest` | 51.7GB | — |
| `nemotron-cascade-2:latest` | 24.3GB | NVIDIA Nemotron Cascade 2 |
| `gpt-oss-safeguard:latest` | 13.8GB | gpt-oss 20.9B — `safeguard` variant, no system prompt set |
| `kimi-k2.5:cloud` | 0GB | Cloud proxy |
| `minimax-m2.7:cloud` | 0GB | Cloud proxy |
| `gemma4:latest` | 9.6GB | — |
| `qwen3.5:latest` | 6.6GB | — |

**Total primary node:** ~510GB local + 2 cloud proxies

---

## Findings

### F1 — 404.5GB DeepSeek V3.1 671B Publicly Accessible (HIGH)

`deepseek-v3.1:latest` is verified as 671.0B params (DeepSeek2 family, family confirmed via `/api/show`). At 404.5GB, this requires multi-GPU infrastructure to serve (typically 8×A100/H100 or equivalent). Any internet actor can run uncapped inference against this model at Monash's compute cost.

This is co-ranked with KRENA's GLM-5.1 as the largest local model accessible in the sweep.

### F2 — Cloud Proxy Portfolio (HIGH)

`kimi-k2.5:cloud` and `minimax-m2.7:cloud` are present. Both return `{"error":"unauthorized"}` with no credential leak in response body. No quota drain confirmed.

### F3 — gpt-oss-safeguard Variant (MEDIUM)

`gpt-oss-safeguard:latest` (13.8GB, 20.9B params) is a named variant of the gpt-oss model with no system prompt set. The `safeguard` tag suggests it was intended to include content filtering, but the system prompt slot is empty — the safeguard was not configured.

### F4 — CVE-2025-63389 Injectable (HIGH)

All models injectable via unauthenticated `/api/create`.

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
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT/blob/main/case-studies/universities/AU/monash.md

This research is part of a broader sweep of university AI infrastructure exposures documented at:
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT/blob/main/case-studies/universities/OVERVIEW.md

I'm happy to answer questions or assist with verification. No response is required.

Regards,
Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT
