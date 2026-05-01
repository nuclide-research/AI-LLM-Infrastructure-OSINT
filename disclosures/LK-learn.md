---
institution: Lanka Education and Research Network
ip: 192.248.70.139
to: security@learn.ac.lk
severity: CRITICAL
status: DRAFT
date: 2026-05-01
---

**To:** security@learn.ac.lk
**Subject:** Unauthenticated AI inference endpoint — Lanka Education and Research Network (192.248.70.139)

---

Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com

2026-05-01

**Re:** Unauthenticated Ollama AI inference endpoint — Lanka Education and Research Network
**IP / Host:** 192.248.70.139
**Severity:** CRITICAL

---

I'm an independent security researcher. I hold CISA disclosures CVE-2025-4364 and ICSA-25-140-11 and conduct good-faith AI infrastructure research under the NuClide Research umbrella. This is an unsolicited disclosure — no engagement exists with your organization, and I have not accessed, modified, or exfiltrated any data beyond what was necessary to confirm the exposure.

---

## Summary

Sri Lanka's academic network (LEARN — Lanka Education and Research Network) has an Ollama instance at 192.248.70.139 with a `deepseek-v4-pro:cloud` subscription and `llama3.2-vision`. The cloud proxy 401 response leaks the Ollama Connect account username `modelserver` and corresponding SSH public key.

---

## Infrastructure

| Field | Value |
|---|---|
| IP | 192.248.70.139 |
| Organization | Lanka Education and Research Network (LEARN) — Information Technology Center |
| Country | Sri Lanka |
| ASN | APNIC assigned, LEARN-LK |
| Open ports | 11434 (Ollama — public) |

---

## Model Inventory

| Model | Size | Notes |
|---|---|---|
| `deepseek-v4-pro:cloud` | 0 | Cloud proxy — credential leak |
| `llama3.2-vision:latest` | 7GB | Multimodal vision-language |

---

## Findings

### F1 — Credential Leak (user: modelserver) (HIGH)

Querying the `deepseek-v4-pro:cloud` model triggers a 401 response containing the Ollama Connect account credentials:

```json
{
  "error": "unauthorized",
  "signin_url": "https://ollama.com/connect?name=modelserver&key=AAAAC3NzaC1lZDI1NTE5AAAAIBefRlkywyAvwYWiTapAKIiPnTAKLic1GNxEZeJfwG6l"
}
```

- **Username:** `modelserver`
- **SSH Public Key:** `ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIBefRlkywyAvwYWiTapAKIiPnTAKLic1GNxEZeJfwG6l`

The username `modelserver` is a service account pattern, suggesting institutional deployment rather than a personal workstation.

### F2 — Unauthenticated Inference (HIGH)

Both models accessible without authentication. `llama3.2-vision` enables multimodal inference (image + text) at LEARN's expense.

### F3 — CVE-2025-63389 Injectable (HIGH)

Both models injectable via unauthenticated `/api/create`.

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
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT/blob/main/case-studies/universities/LK-learn.md

This research is part of a broader sweep of university AI infrastructure exposures documented at:
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT/blob/main/case-studies/universities/OVERVIEW.md

I'm happy to answer questions or assist with verification. No response is required.

Regards,
Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT
