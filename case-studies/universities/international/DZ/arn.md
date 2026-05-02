# Algerian Academic Research Network (ARN) — Unauthenticated Inference Node

_NuClide Research · 2026-05-02_

---

## Summary

Algeria's national academic research network exposes one Ollama node (193.194.91.182) with two models including SmolLM2 with a live system prompt.

---

## Infrastructure

| Field | Value |
|---|---|
| IP | 193.194.91.182 |
| Org | Algerian Academic Research Network |
| Country | Algeria |
| Ollama version | 0.9.6 |
| Open port | 11434 (public) |

---

## Models

| Model | System Prompt |
|---|---|
| smollm2:135m | "You are a helpful AI assistant named SmolLM, trained by Hugging Face" |
| (1 additional model) | — |

---

## Findings

### F1 — National Research Network Node Exposed (MEDIUM)

ARN is Algeria's national research and education network. An exposed Ollama node on this infrastructure indicates individual researcher or institutional deployment without network-level access control.

### F2 — Model Injection (CRITICAL)

CVE-2025-63389 applies. Old version (0.9.6) confirms this node has not been updated since early 2024.

---

## Remediation

```bash
OLLAMA_HOST=127.0.0.1:11434
systemctl restart ollama
```

---

## Disclosure

- **Discovered:** 2026-05-02
- **Status:** Pending outreach to ARN NOC
