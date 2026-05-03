# Technical University of Košice — MedGemma 54GB, Abliterated Qwen3.6-35B, Turkish LLM, RAG Stack

_NuClide Research · 2026-05-03_

---

## Summary

`prometheus.fei.tuke.sk` (147.232.40.80), Faculty of Electrical Engineering and Informatics at the Technical University of Košice (TUKE), Slovakia, runs Ollama v0.11.11 with 24 models including two quantizations of Google MedGemma 27B (29GB + 54GB), an abliterated Qwen3.6-35B, a Turkish-language model (`alibayram/erurollm-9b-instruct`), and a full coding stack with RAG infrastructure. The version (0.11.11) is approximately 1.5 years old.

---

## Infrastructure

| Field | Value |
|---|---|
| IP | 147.232.40.80 |
| Hostname | prometheus.fei.tuke.sk |
| Organization | Faculty of Electrical Engineering and Informatics (FEI), Technical University of Košice (TUKE) |
| Network | TUKE Slovakia (AS2607) |
| Country | Slovakia |
| Ollama version | 0.11.11 |
| Open port | 11434 (public) |

---

## Model Inventory

| Model | Size | Category |
|---|---|---|
| `google/medgemma-27b-it:latest` | 54GB | **Medical AI (Q4)** — full precision |
| `google/medgemma-27b-it:q8_0` | 29GB | **Medical AI (Q8)** — high quality quant |
| `huihui_ai/Qwen3.6-abliterated:35b` | 23GB | **Abliterated** — safety RLHF removed |
| `qwen3.6:35b` | 23GB | Base Qwen3.6 35B |
| `qwen3.6:27b` | 17GB | Base Qwen3.6 27B |
| `qwen3:30b` | 18GB | Qwen3 30B |
| `qwen3:32b` | 20GB | Qwen3 32B |
| `qwen2.5:14b` | 8GB | Qwen2.5 14B |
| `alibayram/erurollm-9b-instruct:latest` | 5GB | **Turkish language model** — 9.2B params (Llama) |
| `alibayram/medgemma:27b` | 16GB | MedGemma 27B (alternative distrib) |
| `gpt-oss:20b` | 13GB | 20B local inference |
| `llama3.3:latest` | 42GB | Llama 3.3 70B |
| `llama3.1:latest` | 4GB | Llama 3.1 8B |
| `gemma3:27b` | 17GB | Gemma 3 27B |
| `gemma2:9b` | 5GB | Gemma 2 9B |
| `gemma2:27b` | 15GB | Gemma 2 27B |
| `phi3:14b` | 7GB | Phi-3 14B |
| `deepseek-coder-v2:latest` | 8GB | DeepSeek Coder V2 |
| `codegemma:latest` | 5GB | CodeGemma |
| `codeqwen:7b` | 4GB | CodeQwen 7B |
| `starcoder2:latest` | 1GB | StarCoder 2 3B |
| `starcoder2:3b` | 1GB | StarCoder 2 3B |
| `nomic-embed-text:latest` | — | **RAG embedding** |
| `smollm2:135m` | — | SmolLM2 135M |

**Total local storage:** ~420GB+

---

## Findings

### F1 — MedGemma 27B: Medical AI with Exposed System Prompt (HIGH)

Both `google/medgemma-27b-it:latest` (54GB) and `google/medgemma-27b-it:q8_0` (29GB) are running simultaneously — the operator deployed two quantizations of Google's medical AI model. Both carry the extracted system prompt:

```
You are a helpful medical AI assistant trained on medical data. Provide accurate,
evidence-based information while being clear that you are an AI and not a substitute
for professional medical advice.
```

The medical system prompt is injectable via CVE-2025-63389. An attacker can replace it with instructions that remove safety disclaimers, redirect users, or provide deliberately incorrect medical guidance.

The presence of `alibayram/medgemma:27b` (a third-party MedGemma distribution) alongside the official Google variants suggests active medical AI research — potentially clinical NLP, diagnostic decision support, or medical text processing research in the EE/CS faculty.

### F2 — `huihui_ai/Qwen3.6-abliterated:35b`: Safety-Removed Model on University Server (HIGH)

`huihui_ai/Qwen3.6-abliterated:35b` has had its RLHF safety alignment removed. No system prompt present. Running alongside medical AI models on the same server — the coexistence of MedGemma and an abliterated LLM on the same unprotected endpoint is an unusual research stack.

### F3 — `alibayram/erurollm-9b-instruct`: Turkish Language Model (MEDIUM)

`erurollm` (9.2B params, Llama family) is a Turkish-language instruction-tuned model. The `alibayram` namespace is Turkish. Its presence on a Slovak university server suggests either collaborative research with Turkish partners (Atatürk University uses "ERÜ" as its abbreviation for Erzurum) or a researcher with Turkish-language NLP research interests. Not a security finding by itself — notable as a cross-institutional research signal.

### F4 — Active RAG Pipeline (HIGH)

`nomic-embed-text` is the embedding backbone for an active RAG pipeline. Documents indexed into the vector store (research papers, student submissions, course materials) are queryable via the unauthenticated endpoint. Combined with the medical AI stack, this likely represents a medical/clinical document retrieval system.

### F5 — v0.11.11: ~1.5-Year-Old Ollama Release (HIGH)

Ollama v0.11.11 dates to approximately late 2024 — around 1.5 years old. CVE-2025-63389 (no patch exists) applies. The entire 24-model stack is injectable via unauthenticated `/api/create`.

### F6 — CVE-2025-63389 (CRITICAL)

All 24 models injectable via unauthenticated `/api/create`. The medical AI system prompt on both MedGemma variants is overwritable without authentication.

---

## Remediation

```bash
OLLAMA_HOST=127.0.0.1:11434
systemctl restart ollama
```

Upgrade Ollama from v0.11.11 (current: v0.22.0+).

---

## Disclosure

- **Discovered:** 2026-05-03
- **Status:** Pending outreach to TUKE FEI IT Security (tuke.sk)
