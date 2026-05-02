# Shiv Nadar University — 3-Node Cluster, Chest X-Ray AI + Abliterated Models + 18 Cloud Subscriptions

_NuClide Research · 2026-05-01 — Updated 2026-05-02_

---

## Summary

Shiv Nadar Institution of Eminence (India, Noida) is running a 3-node shared AI cluster with all nodes exposed on 0.0.0.0:11434. Node 3 (103.27.166.37) reveals active medical AI research: four lung/chest X-ray analysis models (`lungsvlm`, `lungslm`) trained on VinDr-CXR data, deployed alongside abliterated models, a pentest-named model, and 18 cloud proxy subscriptions — all unauthenticated. Total model count across nodes: 76+.

---

## Infrastructure

| Node | IP | Hostname | Status |
|------|-----|----------|--------|
| Node 1 | 103.27.166.36 | 36-166-27-103.noida.snu.in | cloud proxy |
| Node 2 | 103.27.166.38 | 38-166-27-103.noida.snu.in | cloud proxy |
| Node 3 | 103.27.166.37 | 37-166-27-103.noida.snu.in | cloud proxy + **medical AI** |

All nodes in the 103.27.166.0/24 subnet (`noida.snu.in`). All bind Ollama to 0.0.0.0:11434 without authentication.

---

## Model Scale (per node, 76 models)

| Model | Size | Notes |
|---|---|---|
| lordoliver/DeepSeek-V3-0324:671b-q4_k_m | **376 GB** | 671B parameter DeepSeek |
| qwen3:235b | 132 GB | 235B MoE model |
| llama4:latest | 62 GB | Local |
| gpt-oss:120b | 60 GB | OpenAI open model |
| llama3.2-vision:90b | 50 GB | Vision-language, 90B |
| (53 more local models) | varies | |
| (18 cloud proxy models) | 0 GB each | DeepSeek, MiniMax, Kimi, Qwen, GLM, Gemini, Nemotron, NVIDIA |

---

## Notable Models on Node 3 (103.27.166.37)

| Model | Category | System Prompt |
|---|---|---|
| `lungsvlm:latest` | Chest X-ray AI (VinDr-CXR) | "You are LungSVLM, a specialized AI for chest X-ray analysis trained on VinDr-CXR dataset." |
| `siddharthmalu/lungsvlm:latest` | Chest X-ray AI (researcher build) | "You are LungSVLM, a specialized AI for chest X-ray analysis trained on VinDr-CXR dataset." |
| `qwen3vl8blungsvlm:latest` | Chest X-ray AI (Qwen3-VL base) | "You are LungSVLM, a medical AI assistant specialized in analyzing chest X-rays." |
| `lungslm:latest` | Lung health SLM | "You are LungSLM, dedicated EXCLUSIVELY to lung health, chest X-ray analysis, and respiratory medicine." |
| `meditron:70b` / `:7b` | Medical LLM (EPFL) | Standard medical assistant prompt |
| `vishalraj/qwen3-30b-abliterated:latest` | Abliterated (jailbroken) | — |
| `uandinotai/dolphin-uncensored:latest` | Uncensored | — |
| `pentest-copy:latest` | Security research model | SmolLM default (base model copy, security-named) |
| `lordoliver/DeepSeek-V3-0324:671b-q4_k_m` | 671B local (376 GB) | — |

The `siddharthmalu/` namespace suggests a researcher at Shiv Nadar developed the LungSVLM models. VinDr-CXR is a public Vietnamese chest X-ray dataset. Four distinct lung AI models on the same node suggest active medical imaging research using this cluster as compute infrastructure.

---

## Findings

### F1 — Medical AI Research Infrastructure Publicly Exposed (CRITICAL)

Node 3 serves four specialized chest X-ray / lung imaging models alongside medical LLMs (`meditron:70b`). These models are likely used for active research — any actor can query them, inject system prompts, or enumerate what datasets/configurations the research team is using.

### F2 — Abliterated + Uncensored Models on Shared Research Infrastructure (HIGH)

`vishalraj/qwen3-30b-abliterated:latest` (explicitly jailbroken) and `uandinotai/dolphin-uncensored:latest` coexist with medical research models on the same unauthenticated instance. These models will comply with arbitrary instructions, including generating harmful content, with no access control.

### F3 — Multi-Node Cluster Fully Exposed (CRITICAL)

All three nodes expose port 11434 without authentication. The shared model set is injectable across all nodes simultaneously.

### F4 — 671B Local Model Accessible for Free Inference (HIGH)

`lordoliver/DeepSeek-V3-0324:671b-q4_k_m` (376GB) accessible without authentication. Any actor can run frontier-class inference at the operator's electricity and hardware cost.

### F5 — 18 Cloud Subscriptions Exposed (CRITICAL)

Same cloud proxy portfolio as POSTECH: DeepSeek, MiniMax, Kimi, Qwen, GLM, Gemini, Nemotron/NVIDIA.

### F6 — Model Injection on All Models (CRITICAL)

CVE-2025-63389 applies to all models across all nodes. Researchers using these models — including the lung AI tools — receive outputs under attacker-controlled instructions after a single `/api/create` call.

---

## Remediation

```bash
# All nodes
OLLAMA_HOST=127.0.0.1:11434
systemctl restart ollama
```

---

## Disclosure

- **Discovered:** 2026-05-01
- **Status:** Pending outreach to Shiv Nadar IT Security
