# Shiv Nadar University — 7-Node Cluster, Chest X-Ray AI + Abliterated Models + 30+ Cloud Subscriptions

_NuClide Research · 2026-05-01 — Updated 2026-05-03 (session 4)_

---

## Summary

Shiv Nadar Institution of Eminence (India, Noida) runs a 7-node shared AI cluster with all nodes exposed on 0.0.0.0:11434. The cluster grew from 3 nodes (2026-05-01) → 5 nodes (2026-05-03 morning) → 7 nodes (2026-05-03 evening), all running Ollama v0.15.2. Node 2 (.37) carries active medical AI research: four lung/chest X-ray models (`lungsvlm`, `lungslm`) trained on VinDr-CXR data. All nodes share 75+ models including abliterated models, image generation, and 30+ cloud proxy subscriptions — all unauthenticated. The cluster added `deepseek-v4-pro:cloud` and `deepseek-v4-flash:cloud` (pre-release DeepSeek V4 models only available via Ollama Connect beta) and `devstral-2:123b-cloud` (Mistral's latest 123B agent model).

---

## Infrastructure

| Node | IP | Hostname | Notes |
|------|-----|----------|-------|
| Node 1 | 103.27.166.36 | 36-166-27-103.noida.snu.in | cloud proxy |
| Node 2 | 103.27.166.37 | 37-166-27-103.noida.snu.in | cloud proxy + **medical AI** |
| Node 3 | 103.27.166.38 | 38-166-27-103.noida.snu.in | cloud proxy |
| Node 4 | 103.27.166.39 | 39-166-27-103.noida.snu.in | cloud proxy + **image gen** *(added session 3)* |
| Node 5 | 103.27.166.40 | 40-166-27-103.noida.snu.in | cloud proxy *(added session 3)* |
| Node 6 | 103.27.166.28 | 28-166-27-103.noida.snu.in | cloud proxy *(added session 4)* |
| Node 7 | 103.27.166.29 | 29-166-27-103.noida.snu.in | cloud proxy *(added session 4)* |

All nodes in `103.27.166.0/24` (`noida.snu.in`). All bind `0.0.0.0:11434`, Ollama v0.15.2.

---

## Model Scale (~75 models per node)

| Model | Size | Notes |
|---|---|---|
| lordoliver/DeepSeek-V3-0324:671b-q4_k_m | **376.7 GB** | 671B parameter local DeepSeek |
| qwen3:235b | 132.4 GB | 235B MoE model |
| Qwen2.5vl:72b | 45.4 GB | Vision-language, 72B |
| llama3.2-vision:90b | 50.9 GB | Vision-language, 90B |
| llama4:latest | 62.8 GB | Meta Llama 4 |
| gpt-oss:120b | 60.8 GB | OpenAI open model, 120B |
| deepseek-r1:70b | 39.6 GB | Reasoning model |
| meditron:70b | 36.2 GB | Medical LLM (EPFL) |
| llama3:70b | 37.2 GB | — |
| Qwen2.5vl:32b | 19.7 GB | Vision-language |
| qwen3-vl:32b | 19.5 GB | Vision-language |
| qwen3:32b | 18.8 GB | — |
| devstral-small-2:24b | 14.1 GB | Mistral agent model |
| glm-4.7-flash:latest | 17.7 GB | — |
| vishalraj/qwen3-30b-abliterated:latest | 17.3 GB | **Abliterated (jailbroken)** |
| dengcao/Qwen3-30B-A3B-Instruct-2507:latest | 17.4 GB | Community fine-tune |
| (local models) | varies | 40+ additional local models |
| **deepseek-v4-pro:cloud** | — | **Pre-release DeepSeek V4** |
| **deepseek-v4-flash:cloud** | — | **Pre-release DeepSeek V4 Flash** |
| **devstral-2:123b-cloud** | — | Mistral Devstral 2 (123B agent) |
| **qwen3.5:397b-cloud** | — | 397B MoE via cloud |
| kimi-k2.6:cloud | — | Kimi K2.6 |
| kimi-k2-thinking:cloud | — | Kimi K2 reasoning |
| kimi-k2.5:cloud | — | Kimi K2.5 |
| qwen3-coder-next:cloud | — | Qwen3 Coder Next (unreleased) |
| deepseek-v3.1:671b-cloud | — | DeepSeek V3.1 |
| deepseek-v3.2:cloud | — | DeepSeek V3.2 |
| minimax-m2.7:cloud | — | MiniMax M2.7 |
| minimax-m2.5:cloud | — | MiniMax M2.5 |
| minimax-m2.1:cloud | — | MiniMax M2.1 |
| minimax-m2:cloud | — | MiniMax M2 |
| glm-5.1:cloud | — | GLM 5.1 |
| glm-5:cloud | — | GLM 5 |
| glm-4.7:cloud | — | GLM 4.7 |
| glm-4.6:cloud | — | GLM 4.6 |
| gemini-3-flash-preview:cloud | — | Google Gemini 3 Flash (preview) |
| nemotron-3-super:cloud | — | NVIDIA Nemotron |
| qwen3.5:cloud | — | Qwen 3.5 |
| **x/flux2-klein:latest** | 5.3 GB | **Image generation (FLUX 2 Klein)** |

---

## Notable Models on Node 2 (103.27.166.37) — Medical AI Research

| Model | Category | System Prompt |
|---|---|---|
| `lungsvlm:latest` | Chest X-ray AI (VinDr-CXR) | "You are LungSVLM, a specialized AI for chest X-ray analysis trained on VinDr-CXR dataset." |
| `siddharthmalu/lungsvlm:latest` | Chest X-ray AI (researcher build) | "You are LungSVLM, a specialized AI for chest X-ray analysis trained on VinDr-CXR dataset." |
| `qwen3vl8blungsvlm:latest` | Chest X-ray AI (Qwen3-VL base) | "You are LungSVLM, a medical AI assistant specialized in analyzing chest X-rays." |
| `lungslm:latest` | Lung health SLM | "You are LungSLM, dedicated EXCLUSIVELY to lung health, chest X-ray analysis, and respiratory medicine." |
| `meditron:70b` / `meditron:7b` | Medical LLM (EPFL) | Standard medical assistant |
| `medllama2:latest` | Medical fine-tune | — |
| `deepseek-ocr:latest` | OCR/document analysis | — |

`siddharthmalu/` is a researcher-published namespace on Ollama Hub — active Shiv Nadar researcher developing lung AI tools. These models represent active research output being served on an unauthenticated public endpoint.

---

## Findings

### F1 — Medical AI Research Infrastructure Publicly Exposed (CRITICAL)

Four specialized chest X-ray / lung imaging models and three medical LLMs are served publicly without authentication. Any actor can query the research models, inject system prompts altering their diagnostic behavior, or enumerate the datasets and configurations driving the research. Research integrity is directly at risk.

### F2 — Pre-Release Cloud Models Accessible via Exposed Subscriptions (CRITICAL)

Nodes 4 and 5 added `deepseek-v4-pro:cloud`, `deepseek-v4-flash:cloud`, `qwen3-coder-next:cloud`, and `devstral-2:123b-cloud` — models only available through Ollama Connect beta subscriptions. Any internet actor can access these pre-release capabilities at the operator's subscription cost.

### F3 — Cluster Expanded Under Active Exposure (HIGH)

The cluster grew 3 → 5 → 7 nodes across three sessions on 2026-05-03 while remaining fully unauthenticated. Infrastructure buildout continues without security posture improvement. The exposure is actively widening.

### F4 — Image Generation via FLUX 2 (MEDIUM)

`x/flux2-klein:latest` (FLUX 2 image generation) is exposed on nodes 4 and 5. Unauthenticated actors can generate images at the operator's GPU cost. No content filtering.

### F5 — Abliterated + Uncensored Models on Shared Research Infrastructure (HIGH)

`vishalraj/qwen3-30b-abliterated:latest` and `uandinotai/dolphin-uncensored:latest` coexist with medical research models across all five nodes. No access control separates research use from unrestricted generation.

### F6 — 5-Node Model Injection Surface (CRITICAL)

CVE-2025-63389 applies to all ~75 models across all 5 nodes. A single unauthenticated `/api/create` POST overwrites any model's system prompt across the cluster. Researchers running lung AI inference receive attacker-controlled output after injection.

---

## Remediation

```bash
# Apply to all nodes (.36–.40)
OLLAMA_HOST=127.0.0.1:11434
systemctl restart ollama
```

---

## Disclosure

- **Discovered:** 2026-05-01
- **Cluster expansion observed:** 2026-05-03 (3 → 5 nodes)
- **Status:** Pending outreach to Shiv Nadar IT Security (security@snu.edu.in)
- **Disclosure email:** `disclosures/IN-shiv-nadar.md` (needs update for 5-node scope)
