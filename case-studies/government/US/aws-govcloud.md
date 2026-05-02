# AWS GovCloud — Unauthenticated Ollama, Custom JOSIE AI, DeepSeek + MiniMax Cloud Proxy

_NuClide Research · 2026-05-02_

---

## Summary

An Ollama node at `ec2-16-64-116-67.us-gov-east-1.compute.amazonaws.com` (16.64.116.67) runs in AWS GovCloud (us-gov-east-1) — the AWS region reserved for US government agencies and their contractors. The node runs 10 models including DeepSeek V4 Pro and MiniMax M2.7 cloud proxies, a custom AI persona named JOSIE, and Gemma3 27B. Port 11434 is publicly accessible without authentication.

---

## Infrastructure

| Field | Value |
|---|---|
| IP | 16.64.116.67 |
| Hostname | ec2-16-64-116-67.us-gov-east-1.compute.amazonaws.com |
| AWS Region | us-gov-east-1 (AWS GovCloud East) |
| Organization | Amazon.com, Inc. |
| Country | United States |
| Ollama version | 0.21.2 |
| Open port | 11434 (public) |

---

## Model Inventory

| Model | System Prompt | Notes |
|---|---|---|
| `deepseek-v4-pro:cloud` | — | Cloud proxy |
| `minimax-m2.7:cloud` | — | Cloud proxy |
| `qwen3.6:35b` | — | Local 35B |
| `gemma3:27b` | — | Local 27B |
| `gemma3:4b` | — | Local 4B |
| `llama3.1:8b` | — | Local |
| `llama3:latest` | — | Local |
| `llama3.2:3b` | — | Local |
| `smollm2:135m` | "You are a helpful AI assistant named SmolLM, trained by Hugging Face" | Default |
| `goekdenizguelmez/JOSIE:latest` | "You are **J.O.S.I.E.** (**Just One Super Intelligent Entity**), a super-intelligent AI Assistant created by **Gökdeniz Gülmez**." | Custom persona |

---

## Findings

### F1 — US Government-Contracted AWS Infrastructure Exposed (CRITICAL)

AWS GovCloud is used exclusively by US federal agencies, state governments with federal contracts, and their contractors. FedRAMP-authorized. Port 11434 (Ollama) publicly accessible without authentication from the open internet means any actor can query, enumerate, and inject models on what is contractually government infrastructure.

### F2 — Custom AI Persona: JOSIE (HIGH)

`JOSIE` (Just One Super Intelligent Entity) is a custom Ollama model by HuggingFace user `goekdenizguelmez` running on a US GovCloud EC2 instance. System prompt fully exposed. The presence of a community-sourced custom persona model on government infrastructure suggests either a developer's personal deployment in a government-contracted AWS account, or a test environment without network controls.

### F3 — Cloud Proxy Quota Exposure (HIGH)

`deepseek-v4-pro:cloud` and `minimax-m2.7:cloud` expose paid API subscriptions over an unauthenticated port. Cloud proxy 401 responses were returned without leaking signin URLs — no account takeover, but quota drain is possible.

### F4 — CVE-2025-63389 Injectable (CRITICAL)

v0.21.2. All 10 models injectable via unauthenticated `/api/create`. A single request can overwrite the system prompt of any model on this GovCloud EC2 instance.

---

## Remediation

```bash
OLLAMA_HOST=127.0.0.1:11434
systemctl restart ollama
```

AWS Security Group: remove inbound rule allowing 0.0.0.0/0 on TCP 11434. Restrict to known IP ranges only.

---

## Disclosure

- **Discovered:** 2026-05-02
- **Status:** Pending — report to AWS GovCloud security + CISA
- **CISA contact:** report@cisa.dhs.gov
- **AWS:** security@amazon.com
