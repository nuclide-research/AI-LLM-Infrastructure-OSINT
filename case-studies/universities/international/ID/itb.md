# Institut Teknologi Bandung (ITB) — 22 Models, Custom Indonesian Education AI

_NuClide Research · 2026-05-03_

---

## Summary

Institut Teknologi Bandung's LSKK (Laboratorium Sistem Komputer dan Kecerdasan Buatan — Computer Systems and AI Lab, Electrical Engineering) exposes Ollama at `lskk-20.ee.itb.ac.id` (167.205.66.20) with 22 models. The stack includes 7 custom Indonesian-education fine-tuned models and 2 UAT (User Acceptance Testing) performance models — indicating active AI research development for Indonesian educational applications. BGE-M3 embedding signals an active RAG pipeline.

---

## Infrastructure

| Field | Value |
|---|---|
| IP | 167.205.66.20 |
| Hostname | lskk-20.ee.itb.ac.id |
| Organization | Institut Teknologi Bandung |
| Department | LSKK — EE Dept AI Lab |
| Country | Indonesia |
| Ollama version | 0.9.2 |
| Open port | 11434 (public, no auth) |

LSKK = `lskk` in hostname: Laboratorium Sistem Komputer dan Kecerdasan Buatan (Computer Systems and Artificial Intelligence Laboratory).

---

## Model Inventory

| Model | Notes |
|---|---|
| `qwen3.6:35b` | 35B general model |
| `llama3:latest` | Meta Llama 3 |
| **`bge-m3:latest`** | **BGE-M3 multilingual embedding — RAG pipeline** |
| `qwen3:14b` | Qwen3 14B |
| `llama3.2:3b` | Meta Llama 3.2 3B |
| `qwen3:8b` | Qwen3 8B |
| `smollm2:135m` | SmolLM2 — default system prompt |
| `gemma3:12b` | Gemma 3 12B |
| **`indoedu-e5-base:latest`** | **Indonesian educational E5 embedding (custom)** |
| `Llama-3.2-3B-Instruct:q8_0` | — |
| `Llama-3.2-3B-Instruct:q4_k_m` | — |
| **`uat-performance-base:q8_0`** | **UAT baseline model — Q8** |
| **`uat-performance-base:q4_k_m`** | **UAT baseline model — Q4** |
| **`uat-performance-base:latest`** | **UAT baseline (default quant)** |
| **`uat-performance:q8_0`** | **UAT performance model — Q8** |
| **`uat-performance:q4_k_m`** | **UAT performance model — Q4** |
| **`uat-performance:latest`** | **UAT performance (default quant)** |
| `Llama-3.2-3B-Instruct:latest` | — |
| **`llama-3.1-8b-instruct-indoedu-q4ks`** | **Llama 3.1 8B fine-tuned for Indonesian education** |
| **`llama-3.1-8b-instruct-indoedu`** | **Llama 3.1 8B fine-tuned for Indonesian education (full)** |
| **`gemma-3-12b-it-indoedu:latest`** | **Gemma 3 12B fine-tuned for Indonesian education** |
| **`hf.co/ewideplus/indoedu-e5-base-gguf`** | **HF-hosted Indonesian educational E5 embedding** |

---

## Findings

### F1 — Custom Indonesian Education AI Models Exposed (HIGH)

Seven custom models in the Indonesian education domain:
- `indoedu-e5-base`: a multilingual E5-based embedding model specialized for Indonesian educational content
- `llama-3.1-8b-instruct-indoedu`: Llama 3.1 8B instruction-tuned on Indonesian educational data
- `gemma-3-12b-it-indoedu`: Gemma 3 12B fine-tuned for Indonesian education
- `hf.co/ewideplus/indoedu-e5-base-gguf`: HuggingFace-hosted variant of the same embedding

These represent active research artifacts. All are publicly accessible and injectable via CVE-2025-63389, allowing prompt injection into educational AI systems under development.

### F2 — UAT Models: Testing Infrastructure Exposed (HIGH)

`uat-performance-base` and `uat-performance` (both available in q8_0, q4_k_m, and latest quantizations) are labeled "UAT" — User Acceptance Testing. Pre-release models under active quality testing are exposed to public inference and injection. Comparison of quantization quality across multiple variants from the test set is accessible to any attacker.

### F3 — RAG Pipeline (HIGH)

`bge-m3:latest` + `qwen3:14b` (or `qwen3.6:35b`) signals an active Retrieval-Augmented Generation pipeline. With the Indonesian education context, this likely processes educational documents. Injecting the retrieval model's system prompt via CVE-2025-63389 poisons all subsequent RAG queries.

### F4 — v0.9.2 Ancient Build (HIGH)

Ollama v0.9.2 — significantly outdated. No API authentication (which wasn't introduced until later versions), no rate limiting. One of the oldest surviving Ollama deployments in the sweep.

### F5 — CVE-2025-63389 (CRITICAL)

All 22 models injectable via unauthenticated `/api/create`. Impact: custom Indonesian education research models can be poisoned.

---

## ITB Context

ITB (Institut Teknologi Bandung) is Indonesia's premier technical university — the MIT equivalent of the Indonesian higher education system. The LSKK AI Lab is one of the oldest and most cited AI research groups in Southeast Asia. The `indoedu` fine-tune series suggests ongoing work on AI for Indonesian national education, possibly related to the Ministry of Education's AI curriculum initiatives.

---

## Remediation

```bash
OLLAMA_HOST=127.0.0.1:11434
systemctl restart ollama
```

---

## Disclosure

- **Discovered:** 2026-05-03
- **Status:** Pending outreach to ITB IT Security / id-cert.id
- **Contact:** security@itb.ac.id or lskk@ee.itb.ac.id
