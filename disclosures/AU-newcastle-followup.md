---
to: cap-d-core-technology@newcastle.edu.au
cc: abuse@newcastle.edu.au
severity: CRITICAL
ip: 157.85.107.12
institution: University of Newcastle, Australia (resend per dts-cybersecurity@ deprecated-address auto-response)
status: DRAFT
outcome: acknowledged
date: 2026-05-04
---

**To:** cap-d-core-technology@newcastle.edu.au
**Cc:** abuse@newcastle.edu.au
**Subject:** Unauthenticated AI inference endpoint, University of Newcastle, Australia (157.85.107.12) [resend per deprecated-address auto-response]

---

Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com

2026-05-04

**Re:** Unauthenticated Ollama AI inference endpoint, University of Newcastle, Australia
**IP / Host:** 157.85.107.12
**Severity:** CRITICAL

---

I'm an independent security researcher conducting good-faith AI infrastructure research under the NuClide Research umbrella (CISA disclosures CVE-2025-4364, ICSA-25-140-11). This is an unsolicited coordinated-disclosure resend.

**Note:** I originally routed this disclosure to `dts-cybersecurity@newcastle.edu.au` earlier today; that address auto-replied indicating it is no longer monitored and pointed me at this address. Resending here per the auto-response.

---

## Summary

University of Newcastle Australia has an Ollama instance at `157.85.107.12:11434` exposed without authentication. Cloud proxy models present; CVE-2025-63389 model injection vector reachable.

---

## Infrastructure

| Field | Value |
|---|---|
| IP | 157.85.107.12 |
| Org | University of Newcastle, Australia |
| Country | AU, New South Wales |
| Open ports | 11434 (Ollama, **public**) |

(Full model inventory and per-model risk classification in the case study link below.)

---

## Findings

### F1: Unauthenticated Ollama (CRITICAL)

Port 11434 is publicly accessible without any auth. Models enumerable via `/api/tags`; all injectable via `/api/create` (CVE-2025-63389).

### F2: Cloud Proxy Quota Theft (HIGH)

Cloud-proxy models present route inference through Ollama's commercial cloud at the operator's billing expense.

---

**Why it matters**

Same as the original disclosure: the cloud-proxy model is direct billing-impact, the unauth `/api/create` endpoint allows model-system-prompt injection, and any RAG pipeline backed by this instance is affected.

**One-line fix**

```
OLLAMA_HOST=127.0.0.1:11434
systemctl restart ollama
```

**CVE-2025-63389**

All models injectable via the unauthenticated `/api/create` endpoint. No patch exists as of this disclosure.

**Reference**

Full case study + cross-cloud Ollama survey context:
AI-LLM-Infrastructure-OSINT/blob/main/case-studies/universities/AU-newcastle.md

I'm happy to answer questions or assist with verification.

Regards,
Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com
AI-LLM-Infrastructure-OSINT
