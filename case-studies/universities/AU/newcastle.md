# University of Newcastle, Australia — DeepSeek Cloud Proxy + RAG Pipeline

_NuClide Research · 2026-05-01_

---

## Summary

University of Newcastle (Australia, Callaghan campus) server with `deepseek-v4-pro:cloud` cloud proxy subscription and `mxbai-embed-large:latest` embedding model indicating an active RAG pipeline. Raw Ollama port publicly accessible, no authentication.

---

## Infrastructure

| Field | Value |
|---|---|
| IP | 157.85.107.12 |
| Org | University of Newcastle, Australia — Callaghan campus |
| Country | Australia |
| Open ports | 11434 (Ollama — **public**) |

---

## Models

| Model | Size | Notes |
|---|---|---|
| deepseek-v4-pro:cloud | 0 GB | ☁️ Cloud proxy — DeepSeek API |
| qwen3.5:35b | 22 GB | Local |
| qwen2.5:32b | 18 GB | Local |
| qwen3.5:9b | 6 GB | Local |
| mxbai-embed-large:latest | 0 GB | **Embedding — RAG pipeline** |

`mxbai-embed-large` is a high-performance text embedding model used in RAG (retrieval-augmented generation) pipelines. Its presence alongside large language models confirms this Ollama instance is backing a document retrieval system.

---

## Findings

**F1 — Unauthenticated Ollama API (CRITICAL):** Port 11434 publicly accessible.  
**F2 — DeepSeek Cloud Proxy (HIGH):** `deepseek-v4-pro:cloud` accessible, 401 returned.  
**F3 — RAG Pipeline Injection Surface (HIGH):** Embedding model present — model injection via CVE-2025-63389 affects documents served via RAG.

---

## Disclosure

- **Discovered:** 2026-05-01
- **Status:** Pending outreach to UoN IT Security
