---
to: hostmaster@vnu.edu.vn
cc: abuse@nuclide-research.com
severity: HIGH
ip: 112.137.129.161
institution: Vietnam National University Hanoi (resend per security@vnu.edu.vn user-unknown bounce)
status: DRAFT
date: 2026-05-04
---

**To:** hostmaster@vnu.edu.vn
**Cc:** abuse@nuclide-research.com
**Subject:** Unauthenticated AI inference endpoint — VNU Hanoi (112.137.129.161) [resend via DNS hostmaster contact]

---

Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com

2026-05-04

**Re:** Unauthenticated Ollama AI inference endpoint — Vietnam National University Hanoi
**IP / Host:** 112.137.129.161
**Severity:** HIGH

---

I'm an independent security researcher conducting good-faith AI infrastructure research under the NuClide Research umbrella (CISA disclosures CVE-2025-4364, ICSA-25-140-11). This is an unsolicited coordinated-disclosure resend.

**Note on previous attempt:** I sent this disclosure on 2026-05-04 to `security@vnu.edu.vn`; the address bounced with `550 5.1.1` user-unknown. Resending to `hostmaster@vnu.edu.vn` per the SOA RNAME record for `vnu.edu.vn`. Please forward to the appropriate IT-security team. Apologies for the noise.

---

## Summary

Vietnam National University Hanoi has an Ollama instance at `112.137.129.161:11434` with domain-specific fine-tuned models for legal (CaseHold), biomedical (PubMedQA), and financial (FinQA) question answering. All models accessible without authentication.

(Distinct from a separate finding at `103.185.232.21` — Hanoi University, `disclosures/VN-hanoi.md`.)

## Models

| Model | Size | Notes |
|---|---|---|
| gemma4:latest | 8 GB | Local |
| gemma3:12b | 7 GB | Local |
| gemma3:4b | 3 GB | Local |
| llama3.2:1b | 1 GB | Local |
| **xuananle/distill-CaseHold:latest** | 1 GB | Legal case classification |
| **pubmedqa-distilled:latest** | 1 GB | Biomedical Q&A |
| **finqa-distilled:latest** | 1 GB | Financial Q&A |
| llama2:13b | 6 GB | Local |
| deepseek-r1:1.5b | 1 GB | Local |

## Findings

- **F1 — Unauth Ollama on research server (HIGH)** — All models accessible, including domain-specific research fine-tunes.
- **F2 — Domain-specific model injection (MEDIUM)** — `distill-CaseHold` (legal), `pubmedqa-distilled` (medical), `finqa-distilled` (finance) — CVE-2025-63389 affects responses for downstream research workflows.

## One-line fix

```
OLLAMA_HOST=127.0.0.1:11434
systemctl restart ollama
```

## Reference

Full case study:
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT/blob/main/case-studies/universities/VN/vnu-hanoi.md

Regards,
Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT
