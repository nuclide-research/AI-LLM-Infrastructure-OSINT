# Informatics and Telematics Institute (ITI) — Mistral Small 24B, vcl.iti.gr

_NuClide Research · 2026-05-02_

---

## Summary

The Information Technologies Institute (ITI), part of CERTH (Centre for Research and Technology Hellas), Greece's largest national research centre, exposes one Ollama node (`vcl.iti.gr`, 195.251.117.101) running Mistral Small 24B with an exposed system prompt.

---

## Infrastructure

| Field | Value |
|---|---|
| IP | 195.251.117.101 |
| Hostname | vcl.iti.gr |
| Org | Informatics and Telematics Institute |
| Country | Greece |
| Ollama version | 0.16.0 |
| Open port | 11434 (public) |

---

## Models

| Model | System Prompt |
|---|---|
| mistral-small:24b | "You are Mistral Small 3, a Large Language Model (LLM) created by Mistral AI, a French startup headquartered in Paris. Your knowledge base was last updated..." |
| (1 additional model) | — |

The hostname `vcl.iti.gr` suggests a Virtual Compute Lab — likely shared research infrastructure accessible to ITI researchers.

---

## Findings

### F1 — National Research Centre Node Exposed (MEDIUM)

ITI/CERTH is Greece's premier national research centre (equivalent to Fraunhofer in Germany). The `vcl.iti.gr` hostname confirms this is shared lab infrastructure, not a personal workstation — potential for multiple researcher deployments behind the same exposed port.

### F2 — Model Injection (CRITICAL)

CVE-2025-63389 applies.

---

## Remediation

```bash
OLLAMA_HOST=127.0.0.1:11434
systemctl restart ollama
```

---

## Disclosure

- **Discovered:** 2026-05-02
- **Status:** Pending outreach to ITI/CERTH security
