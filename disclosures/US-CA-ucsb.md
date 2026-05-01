---
institution: UC Santa Barbara
ip: 169.231.124.164
to: security@ucsb.edu
severity: CRITICAL
status: DRAFT
date: 2026-05-01
---

**To:** security@ucsb.edu
**Subject:** Unauthenticated AI inference endpoint — UC Santa Barbara (169.231.124.164)

---

Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com

2026-05-01

**Re:** Unauthenticated Ollama AI inference endpoint — UC Santa Barbara
**IP / Host:** 169.231.124.164
**Severity:** CRITICAL

---

I'm an independent security researcher. I hold CISA disclosures CVE-2025-4364 and ICSA-25-140-11 and conduct good-faith AI infrastructure research under the NuClide Research umbrella. This is an unsolicited disclosure — no engagement exists with your organization, and I have not accessed, modified, or exfiltrated any data beyond what was necessary to confirm the exposure.

---

## Summary

University of California, Santa Barbara "AI Lab" instance running Open WebUI v0.8.12 with authentication **completely disabled**. Any internet actor can enumerate models, read model configurations, and execute inference — no credentials required. Includes `functiongemma:latest`, a native function-calling model. Modelfile path leaks the macOS local username.

---

## Infrastructure

| Field | Value |
|---|---|
| IP | 169.231.124.164 |
| rDNS | 169-231-124-164.wireless.ucsb.edu |
| Org | University of California, Santa Barbara |
| Country | US — California |
| Instance name | **"AI Lab (Open WebUI)"** |
| Open ports | 3000 (Open WebUI — **auth disabled**), 11434 (Ollama — **public**) |

---

## Configuration

```json
{
  "name": "AI Lab (Open WebUI)",
  "version": "0.8.12",
  "features": {
    "auth": false,
    "enable_signup": false
  }
}
```

---

## Models

| Model | Size | Notes |
|---|---|---|
| gemma4:31b | 18 GB | Local |
| functiongemma:latest | 0 GB | Native tool/function-calling |
| gemma3:27b | 16 GB | Local |

---

## Findings

### F1 — Authentication Disabled (CRITICAL)

Open WebUI auth is explicitly set to `false`. No login required. All models accessible via both port 3000 and port 11434.

```bash
# No auth — direct inference
curl -s http://169.231.124.164:3000/api/chat  # full WebUI API
curl -s http://169.231.124.164:11434/api/generate \
  -d '{"model":"gemma3:27b","prompt":"...","stream":false}'
```

Confirmed: inference on `gemma3:27b` executes without any credential.

### F2 — Local Username + OS Leak (MEDIUM)

`functiongemma:latest` modelfile exposes the local model path:

```
FROM /Users/marcos/.ollama/models/blobs/sha256-415f8f...
```

- **OS:** macOS (`/Users/` path)
- **Username:** `marcos`

### F3 — Function-Calling Model Exposed (MEDIUM)

`functiongemma:latest` uses Ollama's native function-calling (`RENDERER functiongemma`, `PARSER functiongemma`). If this model is integrated with any tool-execution framework, unauthenticated callers can invoke tool calls.

---

**Why it matters**

The credential leak (username + SSH public key) exposes your service account to enumeration and credential-stuffing against other services.

**One-line fix**

```
OLLAMA_HOST=127.0.0.1:11434
systemctl restart ollama
```

This rebinds Ollama to loopback only. If running in Docker: `docker run -p 127.0.0.1:11434:11434 ollama/ollama`.

**Reference**

Full technical details, parameter counts, and remediation notes are in this public research repository:
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT/blob/main/case-studies/universities/US-CA-ucsb.md

This research is part of a broader sweep of university AI infrastructure exposures documented at:
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT/blob/main/case-studies/universities/OVERVIEW.md

I'm happy to answer questions or assist with verification. No response is required.

Regards,
Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT
