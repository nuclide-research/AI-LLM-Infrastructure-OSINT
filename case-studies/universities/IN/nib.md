# India NIB (National Internet Backbone / BSNL) — 2-Node Cluster, 32B Coder

_NuClide Research · 2026-05-02_

---

## Summary

Two Ollama nodes on India's National Internet Backbone (NIB), operated by BSNL (Bharat Sanchar Nigam Limited), India's state-owned telecom. Node 2 (`static.ill.117.251.22.196.bsnl.co.in`) runs a 32B coding model alongside DeepSeek-Coder 6.7B, suggesting an active software development or research deployment on national backbone infrastructure.

---

## Infrastructure

| Node | IP | Hostname | Version | Models |
|---|---|---|---|---|
| nib-node-1 | 117.203.246.108 | — | 0.9.2 | 3 |
| nib-node-2 | 117.251.22.196 | static.ill.117.251.22.196.bsnl.co.in | 0.17.7 | 7 |

Both in BSNL NIB ASN (India national backbone).

---

## Node 2 Models (117.251.22.196)

| Model | System Prompt |
|---|---|
| qwen2.5-coder:32b | "You are Qwen, created by Alibaba Cloud. You are a helpful assistant." |
| deepseek-coder:6.7b | "You are an AI programming assistant, utilizing the Deepseek Coder model..." |
| smollm2:135m | "You are a helpful AI assistant named SmolLM, trained by Hugging Face" |
| (4 additional models) | — |

---

## Findings

### F1 — National Backbone Infrastructure Exposed (HIGH)

These nodes sit on BSNL's National Internet Backbone — India's government-owned national IP transit network. AI inference running on national telecom backbone infrastructure, exposed without authentication.

### F2 — 32B Coding Model for Free Inference (HIGH)

`qwen2.5-coder:32b` accessible without authentication. The co-deployment with `deepseek-coder:6.7b` and system prompts indicates active coding assistance use — production tooling on public-facing backbone IP.

### F3 — Model Injection (CRITICAL)

CVE-2025-63389 applies to both nodes.

---

## Remediation

```bash
OLLAMA_HOST=127.0.0.1:11434
systemctl restart ollama
```

---

## Disclosure

- **Discovered:** 2026-05-02
- **Status:** Pending outreach to BSNL NIB NOC
