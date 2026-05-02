# Brno University of Technology — Abliterated Gemma + Bulgarian GPT + RAG Pipeline

_NuClide Research · 2026-05-01_

---

## Summary

Brno University of Technology (VUT Brno), Czech Republic, is running Ollama on a Faculty of Mechanical Engineering server with an abliterated Gemma 3 model (safety fine-tuning removed), two variants of a Bulgarian-language GPT model, and an embedding model indicating an active RAG pipeline. All models are unauthenticated and injectable.

---

## Infrastructure

| Field | Value |
|---|---|
| IP | 147.229.83.12 |
| rDNS | `pelton.ofivk.fme.vutbr.cz` |
| Org | Brno University of Technology |
| Faculty | Mechanical Engineering (fme.vutbr.cz) |
| Country | Czech Republic |
| Open ports | 11434 (Ollama — **public**) |

---

## Models

| Model | Size | Notes |
|---|---|---|
| seamon67/Gemma3-Abliterated:27b-q4_K_M | 16 GB | **Abliterated — safety removed** |
| ukjin/Qwen3-30B-A3B-Thinking-2507-Deepseek-v3.1-Distill:latest | 17 GB | Distilled reasoning |
| qwen3:30b | 17 GB | Local |
| todorov/bggpt:v0.2 | 4 GB | **Bulgarian language GPT** |
| todorov/bggpt:Gemma-3-4B-IT-Q4_K_M | 2 GB | **Bulgarian language GPT (Gemma base)** |
| nomic-embed-text:latest | 0 GB | **Embedding — RAG pipeline** |
| smollm2:1.7b | 1 GB | Local |
| smollm2:135m | 0 GB | Local |

---

## Findings

**F1 — Abliterated Gemma 3 27B (HIGH):** `seamon67/Gemma3-Abliterated` has safety fine-tuning removed. Accessible to any unauthenticated internet caller on a university research server.

**F2 — RAG Pipeline Injection Surface (HIGH):** `nomic-embed-text` embedding model confirms an active RAG pipeline. CVE-2025-63389 injection affects document-augmented responses.

**F3 — Bulgarian Language Models (MEDIUM):** `todorov/bggpt` is a Bulgarian-language GPT — suggests international research collaboration or researcher with Bulgarian connections. Both variants are publicly accessible.

**F4 — Unauthenticated Ollama API (HIGH):** All 8 models injectable via CVE-2025-63389.

---

## Disclosure

- **Discovered:** 2026-05-01
- **Status:** Pending outreach to VUT Brno IT / CESNET-CERTS (CZ-CERT)
