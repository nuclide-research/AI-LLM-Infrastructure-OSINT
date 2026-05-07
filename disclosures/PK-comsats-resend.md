---
to: arsaeed@comsats.net.pk
cc: abuse@nuclide-research.com
severity: CRITICAL
ip: 203.124.40.57
institution: COMSATS University (resend per session-7 dead-letter; using RIPE-registered abuse contact)
status: DRAFT
outcome: sent
date: 2026-05-04
---

**To:** arsaeed@comsats.net.pk
**Cc:** abuse@nuclide-research.com
**Subject:** Unauthenticated AI inference endpoint — COMSATS University (203.124.40.57) [resend, contact via RIPE abuse-mailbox]

---

Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com

2026-05-04

**Re:** Unauthenticated Ollama AI inference endpoint — COMSATS University
**IP / Host:** 203.124.40.57
**Severity:** CRITICAL

---

I'm an independent security researcher conducting good-faith AI infrastructure research under the NuClide Research umbrella (CISA disclosures CVE-2025-4364, ICSA-25-140-11). This is an unsolicited coordinated-disclosure resend.

**Note on previous attempts:** I sent this disclosure on 2026-05-04 to `security@comsats.edu.pk` and `abuse@comsats.edu.pk`; both addresses bounced with `554 5.4.14 hop-count exceeded` (Microsoft 365 mail-loop misconfiguration at `pern.onmicrosoft.com`). RIPE WHOIS for the IP block lists `arsaeed@comsats.net.pk` as the registered abuse-mailbox — resending here. Apologies for the noise if this reaches the wrong inbox.

---

## Summary

COMSATS University has an Ollama instance at `203.124.40.57:11434` with two MedGemma medical AI models (27B + 4B) alongside a Kimi K2.6 cloud proxy. The server is publicly reachable without authentication.

## Models

| Model | Size | Notes |
|---|---|---|
| `kimi-k2.6:cloud` | 0 GB | Cloud proxy (returns 401, no credential leak) |
| `puyangwang/medgemma-27b-it:q8` | 29.6 GB | Google MedGemma 27B medical AI |
| `thiagomoraes/medgemma-1.5-4b-it:F16` | 8.6 GB | MedGemma 1.5B instruct |
| `gemma4:26b` | 18.0 GB | — |
| `qwen3.6:latest` | 23.9 GB | — |
| `gemma3:12b` | 8.1 GB | — |
| `llama3.2:3b` | 2.0 GB | — |

## Findings

- **F1 — Medical AI exposed unauth (HIGH)** — MedGemma 27B + 4B accessible to any internet caller; CVE-2025-63389 model injection allows altering the medical AI's system prompt.
- **F2 — Cloud proxy present (MEDIUM)** — Kimi K2.6 cloud proxy reachable; no credential leak in the 401 response, but the operator's billing is at risk if config changes.
- **F3 — CVE-2025-63389 injectable (HIGH)** — All models on the instance are injectable.

## One-line fix

```
OLLAMA_HOST=127.0.0.1:11434
systemctl restart ollama
```

Rebinds Ollama to loopback only. If in Docker: `docker run -p 127.0.0.1:11434:11434 ollama/ollama`.

## Reference

Full case study:
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT/blob/main/case-studies/universities/PK/comsats.md

Disclosure-outcome tracker (this batch):
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT/blob/main/disclosures/outcomes-2026-05-04.md

I'm happy to answer questions or assist with verification.

Regards,
Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT
