---
to: tanetadm@moe.edu.tw
cc: abuse@nuclide-research.com
severity: HIGH
ip: 140.136.192.220
institution: Fu Jen Catholic University (resend via TANet/Ministry of Education admin per FJU mail-relay misconfig)
status: DRAFT
outcome: sent
date: 2026-05-04
---

**To:** tanetadm@moe.edu.tw
**Cc:** abuse@nuclide-research.com
**Subject:** Unauthenticated AI inference endpoint — Fu Jen Catholic University (140.136.192.220) [resend via TANet admin]

---

Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com

2026-05-04

**Re:** Unauthenticated Ollama AI inference endpoint — Fu Jen Catholic University Medical & Public Health
**IP / Host:** 140.136.192.220 (`user220.medph.fju.edu.tw`)
**Network:** Taiwan MOE TANet (140.136.0.0/16)
**Severity:** HIGH

---

I'm an independent security researcher conducting good-faith AI infrastructure research under the NuClide Research umbrella (CISA disclosures CVE-2025-4364, ICSA-25-140-11). This is an unsolicited coordinated-disclosure resend routed through TANet administration.

**Note on previous attempts:** I sent this disclosure on 2026-05-04 to `security@fju.edu.tw` and `abuse@fju.edu.tw`; both addresses rejected with `550 Relaying mail to ... is not allowed` — a per-recipient mail-server misconfiguration at FJU. The hosts are on Taiwan MOE TANet (`140.136.0.0/16`); routing through TANet administration so that the institution can be notified via the network operator. Apologies for the noise if this reaches the wrong inbox.

If TANet has an FJU IT-security contact mapping, please forward.

---

## Summary

Fu Jen Catholic University's Medical and Public Health department server (`user220.medph.fju.edu.tw`, 140.136.192.220) is running an Ollama instance with 8 models including a 75 GB MoE (`qwen3.5:122b-a10b-q4_K_M`) and a 60 GB local 120B model (`gpt-oss:120b`). All models are accessible without authentication.

## Models

| Model | Size | Notes |
|---|---|---|
| `qwen3.5:122b-a10b-q4_K_M` | 75 GB | MoE, ~125B params, 10B active |
| `gpt-oss:120b` | 60 GB | Local 120B inference |
| `gemma4:31b-it-q8_0` | 31 GB | High-quality quant |
| `mistral-small3.2:24b-instruct-2506-q8_0` | 24 GB | — |
| `qwen3.5:27b-q8_0` | 27 GB | — |
| `translategemma:27b-it-q4_K_M` | 16 GB | Translation-specialized |
| `qwen3.5:9b-q8_0` | 9 GB | — |
| `qwen3-embedding:8b-q4_K_M` | 4 GB | RAG embedding pipeline |

Total local model storage: ~246 GB.

## Findings

- **F1 — Unauth inference on medical-domain research server (HIGH)** — RAG embedding signals indexed documents; medical/public-health context creates compliance risk.
- **F2 — CVE-2025-63389 injectable (HIGH)** — All 8 models injectable via unauthenticated `/api/create`.
- **F3 — Compute exposure (HIGH)** — 75GB MoE + 60GB local 120B = significant GPU hardware exposed; unauthenticated inference = compute theft at scale.

## One-line fix

```
OLLAMA_HOST=127.0.0.1:11434
systemctl restart ollama
```

## Reference

Full case study:
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT/blob/main/case-studies/universities/TW/fju-medph.md

I'm happy to answer questions or assist with verification.

Regards,
Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT
