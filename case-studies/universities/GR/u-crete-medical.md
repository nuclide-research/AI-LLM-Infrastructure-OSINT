# University of Crete Medical Center — Dual-Embedding RAG Pipeline

_NuClide Research · 2026-05-01_

---

## Summary

The University of Crete Medical Center (`centaur.med.uoc.gr`) is running Ollama with a sophisticated dual-embedding RAG pipeline — both `mxbai-embed-large` and `nomic-embed-text` are deployed alongside large language models (Llama 3.3, Qwen3-Coder, Mistral). Dual embedding models indicate a production RAG system over medical/research content, unauthenticated and injectable.

---

## Infrastructure

| Field | Value |
|---|---|
| IP | 147.52.71.221 |
| rDNS | `centaur.med.uoc.gr` |
| Org | University of Crete |
| Facility | Medical Center (med.uoc.gr) |
| Country | Greece |
| Open ports | 11434 (Ollama — **public**) |

---

## Models

| Model | Size | Notes |
|---|---|---|
| llama3.3:latest | 39 GB | Large LLM |
| qwen3-coder:30b | 17 GB | Code model |
| qwen2.5-coder:latest | 4 GB | Code model |
| qwen2.5:latest | 4 GB | — |
| mistral:latest | 4 GB | — |
| gemma3:latest | 3 GB | — |
| **mxbai-embed-large:latest** | 0 GB | **Embedding model 1 — RAG pipeline** |
| **nomic-embed-text:latest** | 0 GB | **Embedding model 2 — RAG pipeline** |

---

## Findings

**F1 — Dual-Embedding RAG Pipeline on Medical Server (CRITICAL):** Two embedding models (mxbai-embed-large + nomic-embed-text) running simultaneously indicates a production RAG system. On a medical university server, the document corpus likely includes medical research, clinical workflows, or patient-facing content. Model injection via CVE-2025-63389 affects all documents served through the RAG pipeline.

**F2 — Unauthenticated Medical Research Server (HIGH):** `centaur` suggests an academic/mythological name for a compute node (common at Greek universities). All models accessible without credentials — researchers' document-augmented queries are injectable.

**F3 — Model Injection (HIGH):** All 8 models injectable via CVE-2025-63389.

---

## Context

This is a separate institution from the Technical University of Crete (TUC, 147.27.38.32) documented in GR-tech-crete-ntua.md. University of Crete (UoC) is a public university with a medical school; `centaur.med.uoc.gr` is a named server in the medical faculty.

---

## Disclosure

- **Discovered:** 2026-05-01
- **Status:** Pending outreach to UoC IT / GR-CERT (cert@cert.gr)
