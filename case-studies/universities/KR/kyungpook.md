# Kyungpook National University — 3-Node Cluster, Multimodal AI

_NuClide Research · 2026-05-02_

---

## Summary

Kyungpook National University (KNU, Daegu, South Korea) exposes three Ollama nodes on the public internet. Together the nodes span vision-language models (qwen3-vl:32b, llava), a custom community quantization (VladimirGav/gemma4-26b), and lightweight inference models. The strongest node (155.230.92.188) runs 6 models including a 32B vision-language model and a 27B vision model.

---

## Infrastructure

| Node | IP | Version | Models | Tags |
|---|---|---|---|---|
| knu-node-1 | 155.230.15.121 | 0.19.0 | 1 | — |
| knu-node-2 | 155.230.92.188 | 0.15.4 | 6 | multimodal |
| knu-node-3 | 155.230.36.196 | 0.20.7 | 2 | — |

All nodes in `155.230.0.0/16` (Kyungpook National University ASN).

---

## Model Inventory (Node 2 — 155.230.92.188)

| Model | Notes |
|---|---|
| VladimirGav/gemma4-26b-16GB-VRAM:latest | Community quantization, optimized for 16GB VRAM |
| glm-4.7-flash:latest | Zhipu AI GLM multimodal |
| llama3.2:3b | Meta Llama |
| nomic-embed-text:latest | Embedding (RAG pipeline signal) |
| gemma3:27b | Google Gemma3 27B |
| qwen3-vl:32b | Qwen3 vision-language 32B |

---

## Findings

### F1 — 3-Node Cluster Exposed Without Authentication (HIGH)

All three nodes bind to 0.0.0.0:11434. No Ollama Connect credentials found, no cloud proxy subscriptions — this is a pure local compute exposure.

### F2 — 32B Vision-Language Model Accessible (HIGH)

`qwen3-vl:32b` — a frontier vision-language model — accessible for free inference to any internet actor. The co-presence of `nomic-embed-text` suggests active multimodal RAG pipeline development.

### F3 — Model Injection (CRITICAL)

CVE-2025-63389 applies to all three nodes.

---

## Remediation

```bash
OLLAMA_HOST=127.0.0.1:11434
systemctl restart ollama
```

---

## Disclosure

- **Discovered:** 2026-05-02
- **Status:** Pending outreach to KNU IT Security
