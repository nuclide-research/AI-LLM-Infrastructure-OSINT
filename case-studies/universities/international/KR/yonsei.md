# Yonsei University — 17 Cloud Subscriptions on Non-Standard Port, Free-Tier 200 OK

_NuClide Research · 2026-05-01_

---

## Summary

Yonsei University (Seoul, South Korea) is running Ollama on non-standard port 5004 with 17 cloud proxy subscriptions matching the pattern seen at POSTECH, Shiv Nadar, Hanoi University, and RIT. `minimax-m2.1:cloud` returns **200 OK** without credentials, confirming free-tier cloud quota drain. Local models include 75GB `qwen3.5:122b` and 65GB `gpt-oss:120b` (MXFP4), indicating a high-VRAM GPU server.

---

## Infrastructure

| Field | Value |
|---|---|
| IP | 1.233.220.117 |
| rDNS | — |
| Org | Yonsei University |
| Country | South Korea |
| Open ports | **5004** (Ollama non-standard port — **public**) |
| Timezone | UTC+9 (Korea) |

---

## Cloud Proxy Subscriptions (17)

| Model | Provider | Notes |
|---|---|---|
| kimi-k2-thinking:cloud | Moonshot AI | 1 trillion parameters |
| kimi-k2.6:cloud | Moonshot AI | — |
| kimi-k2.5:cloud | Moonshot AI | — |
| deepseek-v4-pro:cloud | DeepSeek | — |
| deepseek-v4-flash:cloud | DeepSeek | — |
| deepseek-v3.2:cloud | DeepSeek | 671B |
| minimax-m2.7:cloud | MiniMax | — |
| minimax-m2.5:cloud | MiniMax | — |
| **minimax-m2.1:cloud** | MiniMax | **200 OK confirmed — free-tier** |
| minimax-m2:cloud | MiniMax | 230B |
| glm-5.1:cloud | Zhipu AI | — |
| glm-5:cloud | Zhipu AI | — |
| glm-4.7:cloud | Zhipu AI | — |
| glm-4.6:cloud | Zhipu AI | 355B |
| qwen3.5:cloud | Alibaba | 397B |
| qwen3-coder-next:cloud | Alibaba | 80B |
| nemotron-3-super:cloud | NVIDIA | — |
| gemini-3-flash-preview:cloud | Google | — |

## Local Models

| Model | Size |
|---|---|
| qwen3.5:122b | 75 GB |
| qwen3.5:35b | 22 GB |
| qwen3.5:9b | 6 GB |
| gpt-oss:120b | 65 GB (MXFP4) |

---

## Findings

### F1 — Free-Tier Cloud Proxy 200 OK (CRITICAL)

`minimax-m2.1:cloud` returns full inference without credentials. 40 tokens consumed at operator expense:

```bash
curl -X POST http://1.233.220.117:5004/api/chat \
  -d '{"model":"minimax-m2.1:cloud","messages":[{"role":"user","content":"hi"}],"stream":false}'
# 200 OK — "Hi there! How can I help you today?"
```

### F2 — 17 Cloud Subscriptions on Non-Standard Port (CRITICAL)

Running Ollama on port 5004 instead of 11434. All 17 cloud subscriptions accessible.

### F3 — Same Cloud Bundle as POSTECH/Shiv Nadar/Hanoi/RIT (HIGH)

The 17-subscription cloud portfolio overlaps with the 18-bundle pattern seen at POSTECH (KR), Shiv Nadar (IN), Hanoi University (VN), and RIT (US). This is a distinct subset — shared Ollama Connect demonstration account or institutional bundle.

### F4 — Large Local Models (HIGH)

75GB and 65GB models accessible. Significant compute resources exposed to unauthenticated callers.

---

## Disclosure

- **Discovered:** 2026-05-01
- **Status:** Pending outreach to Yonsei IT Security / KrCERT/CC
