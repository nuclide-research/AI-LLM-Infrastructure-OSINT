---
institution: Syracuse University
ip: 128.230.38.78
to: itsecurity@listserv.syr.edu
severity: CRITICAL
status: DRAFT
date: 2026-05-01
---

**To:** itsecurity@listserv.syr.edu
**Subject:** Unauthenticated AI inference endpoint — Syracuse University (128.230.38.78)

---

Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com

2026-05-01

**Re:** Unauthenticated Ollama AI inference endpoint — Syracuse University
**IP / Host:** 128.230.38.78
**Severity:** CRITICAL

---

I'm an independent security researcher. I hold CISA disclosures CVE-2025-4364 and ICSA-25-140-11 and conduct good-faith AI infrastructure research under the NuClide Research umbrella. This is an unsolicited disclosure — no engagement exists with your organization, and I have not accessed, modified, or exfiltrated any data beyond what was necessary to confirm the exposure.

---

## Summary

A Dell PowerEdge R640 server in Syracuse University's School of Information Studies (`ist-r640-mafudge.syr.edu`) is running Ollama on non-standard port 12345 with `gemma4:31b-cloud` returning **200 OK** without credentials. Five cloud proxy subscriptions total.

---

## Infrastructure

| Field | Value |
|---|---|
| IP | 128.230.38.78 |
| rDNS | `ist-r640-mafudge.syr.edu` |
| Org | Syracuse University |
| Department | Information Studies & Technology |
| Country | US — New York |
| Open ports | **12345** (Ollama non-standard port — **public**) |

---

## Models

| Model | Size | Type | 200 OK? |
|---|---|---|---|
| gemma4:31b-cloud | 0 GB | ☁️ Cloud proxy | **YES — 10 tokens** |
| minimax-m2.7:cloud | 0 GB | ☁️ Cloud proxy | — |
| glm-4.7:cloud | 0 GB | ☁️ Cloud proxy | — |
| glm-5.1:cloud | 0 GB | ☁️ Cloud proxy | — |
| kimi-k2.6:cloud | 0 GB | ☁️ Cloud proxy | — |
| gemma4:31b | 19 GB | Local | — |
| smollm2:latest | 0 GB | Local | — |

---

## Findings

### F1 — Free-Tier Cloud Proxy 200 OK on Non-Standard Port (CRITICAL)

`gemma4:31b-cloud` returns full inference without credentials on port 12345:

```bash
curl -X POST http://128.230.38.78:12345/api/chat \
  -d '{"model":"gemma4:31b-cloud","messages":[{"role":"user","content":"hi"}],"stream":false}'
# 200 OK — "Hello! How can I help you today?"
```

### F2 — Non-Standard Port Exposes Intentional or Misconfigured Deployment (HIGH)

Ollama running on port 12345 (not default 11434) may indicate intentional non-standard deployment or a misconfigured service that bypasses default port-filtering rules.

### F3 — Model Injection (HIGH)

All models injectable via CVE-2025-63389.

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
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT/blob/main/case-studies/universities/US/NY-syracuse.md

This research is part of a broader sweep of university AI infrastructure exposures documented at:
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT/blob/main/case-studies/universities/OVERVIEW.md

I'm happy to answer questions or assist with verification. No response is required.

Regards,
Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT
