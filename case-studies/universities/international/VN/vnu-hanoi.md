# Vietnam National University Hanoi — Domain-Specific Distilled Models

_NuClide Research · 2026-05-01_

---

## Summary

Vietnam National University Ha Noi has an Ollama instance with domain-specific fine-tuned models for legal (CaseHold), biomedical (PubMedQA), and financial (FinQA) question answering — indicating active NLP research pipelines publicly accessible without authentication.

---

## Infrastructure

| Field | Value |
|---|---|
| IP | 112.137.129.161 |
| rDNS | — |
| Org | VietNam National University Ha Noi |
| Country | Vietnam |
| Open ports | 11434 (Ollama — **public**) |

Note: This is a separate server from Hanoi University (103.185.232.21) documented in VN-hanoi.md.

---

## Models

| Model | Size | Notes |
|---|---|---|
| gemma4:latest | 8 GB | Local |
| gemma3:12b | 7 GB | Local |
| gemma3:4b | 3 GB | Local |
| llama3.2:1b | 1 GB | Local |
| xuananle/distill-CaseHold:latest | 1 GB | **Legal case classification** |
| pubmedqa-distilled:latest | 1 GB | **Biomedical QA** |
| finqa-distilled:latest | 1 GB | **Financial QA** |
| llama2:13b | 6 GB | Local |
| deepseek-r1:1.5b | 1 GB | Local |

---

## Findings

**F1 — Unauthenticated Ollama API (HIGH):** All models accessible. Research-grade domain-specific models (legal, medical, financial) exposed.

**F2 — Domain-Specific Research Models (MEDIUM):** `distill-CaseHold` (legal reasoning), `pubmedqa-distilled` (biomedical Q&A), `finqa-distilled` (financial analysis) — active research pipelines. Injection via CVE-2025-63389 affects domain responses.

---

## Disclosure

- **Discovered:** 2026-05-01
- **Status:** Pending outreach to VNU Hanoi IT / VNCERT
