# ICI Bucharest — 2-Node Cluster, Cloud Proxy + Abliterated Models

_NuClide Research · 2026-05-02_

---

## Summary

Institutul National de Cercetare-Dezvoltare în Informatică (ICI Bucharest), Romania's national IT research institute, exposes two Ollama nodes. Node 1 (85.122.129.92) runs cloud proxy subscriptions (DeepSeek, MiniMax). Node 2 (85.122.129.248) is a large-model compute node with 11 models including abliterated Qwen2.5-Coder, two Dolphin uncensored models, and a custom `rdv-bot` with exposed system prompt — and a 72B Qwen2.5 model.

---

## Infrastructure

| Node | IP | Version | Models | Tags |
|---|---|---|---|---|
| ici-node-1 | 85.122.129.92 | 0.19.0 | 4 | CLOUD |
| ici-node-2 | 85.122.129.248 | 0.18.3 | 11 | abliterated models |

Subnet: `85.122.129.0/24` (ICI Bucharest ASN, Romania).

---

## Node 1 — Cloud Proxy (85.122.129.92)

| Model | Notes |
|---|---|
| deepseek-v4-pro:cloud | DeepSeek V4 Pro via cloud proxy |
| minimax-m2.7:cloud | MiniMax M2.7 via cloud proxy |
| llama3.2:3b | Local |
| llama3:latest | Local |

---

## Node 2 — Large Compute (85.122.129.248)

| Model | Category | System Prompt |
|---|---|---|
| qwen2.5:72b | 72B model | "You are Qwen, created by Alibaba Cloud." |
| qwen2.5:14b | 14B model | "You are Qwen, created by Alibaba Cloud." |
| qwen2.5:7b-instruct-q4_K_M | 7B model | "You are Qwen, created by Alibaba Cloud." |
| huihui_ai/qwen2.5-coder-abliterate:14b | **Abliterated** | "You are a helpful assistant." |
| llama3.1-8b-abliterated:latest | **Abliterated** | — |
| dolphin-llama3:latest | Uncensored | "You are Dolphin, a helpful AI assistant." |
| dolphin-mistral:latest | Uncensored | "You are Dolphin, a helpful AI assistant." |
| rdv-bot:latest | Custom | (see F2) |
| gemma2:9b-instruct-q4_K_M | Local | — |
| llama3.1:8b | Local | — |

---

## Findings

### F1 — Cloud Proxy Quota Exposure (CRITICAL)

Node 1 exposes DeepSeek V4 Pro and MiniMax M2.7 cloud proxy subscriptions without authentication. Any actor can drain ICI Bucharest's API quotas at no cost to themselves.

### F2 — rdv-bot System Prompt Leaked (HIGH)

Node 2 hosts a custom `rdv-bot:latest` model. The `rdv-bot` name (Romanian: "rdv" = "rendezvous" / appointment scheduling) suggests a production chatbot — a Romanian scheduling or appointment assistant. Full system prompt accessible via `/api/show`.

### F3 — Abliterated + Uncensored Models on Research Infrastructure (HIGH)

`huihui_ai/qwen2.5-coder-abliterate:14b` (safety-removed) and `llama3.1-8b-abliterated` coexist with legitimate research models. Both `dolphin-llama3` and `dolphin-mistral` are uncensored variants. On a national research institute's public-facing IP, these will comply with arbitrary instructions without access control.

### F4 — 72B Model for Free Inference (HIGH)

`qwen2.5:72b` accessible without authentication. Frontier-class inference at ICI Bucharest's compute cost.

### F5 — Model Injection on Both Nodes (CRITICAL)

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
- **Status:** Pending outreach to ICI Bucharest security team
