# Bangladesh Research and Education Network (BdREN) — Unauthenticated Inference Node

_NuClide Research · 2026-05-02_

---

## Summary

The Bangladesh Research and Education Network (BdREN), the national research and education network of Bangladesh, exposes one Ollama node on 203.96.189.126. Seven models including Mistral, Llama 3.x, and Gemma2 are accessible without authentication. BdREN serves as the connectivity backbone for Bangladeshi universities and research institutions — this node is on the national education backbone.

---

## Infrastructure

| Field | Value |
|---|---|
| IP | 203.96.189.126 |
| Org | Bangladesh Research and Education Network (BdREN) |
| Country | Bangladesh |
| Ollama version | 0.21.2 |
| Open port | 11434 (public) |

---

## Models

| Model | Notes |
|---|---|
| gemma2:2b | Google Gemma2 |
| qwen2.5:3b | Alibaba Qwen |
| llama3.2:3b | Meta Llama |
| qwen2.5:latest | Alibaba Qwen |
| mistral:latest | Mistral AI |
| llama3.1:latest | Meta Llama |
| llama3:latest | Meta Llama |

System prompts present on qwen2.5:3b and qwen2.5:latest (default Qwen prompt).

---

## Findings

### F1 — National Education Backbone Node Exposed (HIGH)

BdREN is Bangladesh's equivalent of Internet2 (US) or JANET (UK) — the research and education network connecting all major Bangladeshi universities. An Ollama node on this infrastructure exposes compute at the national backbone level, unauthenticated.

### F2 — Free Inference on National Infrastructure (MEDIUM)

Seven general-purpose models accessible without authentication. No cloud proxy, no account takeover surface — but the infrastructure context makes this higher-impact than a typical workstation exposure.

### F3 — Model Injection (CRITICAL)

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
- **Status:** Pending outreach to BdREN NOC
