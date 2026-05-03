# National Chengchi University — Taiwan National AI Models (TAIDE) Exposed on V100×4 Server

_NuClide Research · 2026-05-03_

---

## Summary

National Chengchi University (政治大學) Computer Science department has a 4× NVIDIA V100 GPU server (`V100x4.cs.nccu.edu.tw`, 140.119.163.219) with Ollama exposed on port 11434 without authentication. The server hosts Taiwan's national AI models — **TAIDE (Taiwan AI Dialogue Engine)**, a government-funded bilingual LLM initiative operated by NCHC (National Center for High-performance Computing) — alongside 60GB+ commercial models including `gpt-oss:120b`. This is the most nationally significant Taiwan finding in the sweep: publicly funded national AI infrastructure exposed on a university research node.

---

## Infrastructure

| Field | Value |
|---|---|
| IP | 140.119.163.219 |
| Hostname | V100x4.cs.nccu.edu.tw |
| Org | National Chengchi University — Computer Science Dept |
| Network | TANet (Taiwan Academic Network, 140.119.0.0/16) |
| City | Taipei, Taiwan |
| GPU | 4× NVIDIA V100 (hostname indicates) |
| Ollama version | 0.11.6 |
| Open port | 11434 (public, no auth) |

---

## Model Inventory

| Model | Size | Notes |
|---|---|---|
| `llama-3-taiwan:70b` | 69.8 GB | **Taiwan national LLM — Llama-3 fine-tuned on Traditional Chinese** |
| `llama-3-taiwan:70b` (2nd) | 69.8 GB | Duplicate instance or second quantization |
| `gpt-oss:120b` | 60.8 GB | OpenAI open model, 116B params |
| `Gemma-3-TAIDE-12b-Chat` | 23.1 GB | **TAIDE national model — Gemma-3 12B, Traditional Chinese dialogue** |
| `qwq:32b-q8_0` | 34.8 GB | QwQ-32B reasoning (Q8 quantization) |
| `qwen3:32b-q8_0` | 34.8 GB | Qwen3 32B (Q8) |
| `Llama-3.1-TAIDE-LX-8B-Chat` | 15.9 GB | **TAIDE national model — Llama-3.1 8B, Traditional Chinese** |
| `gemma3:27b-it-fp16` | 54.5 GB | Gemma3 27B instruction-tuned, full precision |
| *(7 more models)* | | |

---

## TAIDE — Taiwan National AI Initiative

**TAIDE (Trustworthy AI Dialogue Engine)** is Taiwan's government-funded national LLM project, developed by NCHC and partnered institutions with backing from the National Science and Technology Council (NSTC). The models are optimized for Traditional Chinese (zh-tw) and Taiwan-specific domain knowledge — bilingual education, government services, legal text.

Three TAIDE-series models are present:

| Model | Base | Focus |
|---|---|---|
| `llama-3-taiwan:70b` | Llama-3 70B | Large-scale Traditional Chinese bilingual |
| `Gemma-3-TAIDE-12b-Chat` | Gemma-3 12B | Dialogue-optimized, chat interface |
| `Llama-3.1-TAIDE-LX-8B-Chat` | Llama-3.1 8B | Lightweight deployment variant |

These are not commodity models — they are products of a multi-institution national AI project and represent significant public investment. Their presence on an externally accessible port with no auth is a disclosure vector for any data submitted to them.

---

## Findings

### F1 — Taiwan National AI Models Exposed (CRITICAL)

Three TAIDE models (Llama-3-Taiwan:70b, Gemma-3-TAIDE-12b-Chat, Llama-3.1-TAIDE-LX-8B-Chat) are accessible to any internet actor without authentication. Any researcher, student, or external application submitting queries to these models has no visibility into the exposure. The `llama-3-taiwan:70b` appears twice, suggesting either two quantization variants or active dual-deployment for load distribution.

### F2 — gpt-oss:120b Accessible at NCCU's Compute Cost (HIGH)

OpenAI's 116B open-source model (60.8GB) is running on NCCU's V100×4 cluster, accessible to unauthenticated callers. Sustained inference against this model drains significant GPU compute and electricity from NCCU's research allocation.

### F3 — CVE-2025-63389 Injects Into National AI Models (CRITICAL)

All models (including all three TAIDE variants) are injectable via unauthenticated `/api/create`. An attacker can overwrite the system prompt of `Gemma-3-TAIDE-12b-Chat` or `Llama-3.1-TAIDE-LX-8B-Chat` to make Taiwan's national AI produce arbitrary output for any subsequent caller using those endpoints.

### F4 — High-Value GPU Compute (HIGH)

The hostname `V100x4` signals four NVIDIA V100 GPUs — each ~32GB HBM2. Inference on `qwen3:32b-q8_0` or `qwq:32b-q8_0` at full Q8 quality is available to any internet actor against NCCU's research allocation without cost or accountability.

---

## Taiwan National Context

This is the second TANet node in the sweep running TAIDE models (see also `tanet.md` for the 18-node TANet cluster). NCCU houses Taiwan's premier social science and governance research programs — the CS department's TAIDE deployment suggests cross-institutional national AI research integration. The exposure affects both the compute infrastructure and the integrity of Taiwan's national AI systems.

---

## Remediation

```bash
OLLAMA_HOST=127.0.0.1:11434
systemctl restart ollama
```

Report to: NCCU CS Dept IT + TANet security (cert@twcert.org.tw)

---

## Disclosure

- **Discovered:** 2026-05-03
- **Status:** Pending outreach to NCCU / TWCERT (cert@twcert.org.tw)
