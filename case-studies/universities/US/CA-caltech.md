# California Institute of Technology (Caltech) — GPT-OSS 120B, RAG Pipeline

_NuClide Research · 2026-05-02_

---

## Summary

A Caltech node (`yertle.caltech.edu`, 131.215.141.46) exposes Ollama with 6 models including `gpt-oss:120b` (OpenAI's 120B open model, 65.4GB) and a RAG pipeline stack (two embedding models). The hostname `yertle` references the Dr. Seuss turtle — a common playful server naming convention at research universities.

---

## Infrastructure

| Field | Value |
|---|---|
| IP | 131.215.141.46 |
| Hostname | yertle.caltech.edu |
| Org | California Institute of Technology |
| Country | United States |
| Ollama version | 0.12.10 |
| Open port | 11434 (public) |

---

## Models

| Model | Size | Notes |
|---|---|---|
| gpt-oss:120b | ~65 GB | OpenAI open-weight, 120B params |
| rjmalagon/gte-qwen2-1.5b-instruct-embed-f16:latest | ~3 GB | Embedding model (RAG) |
| mxbai-embed-large:latest | ~670 MB | Embedding model (RAG) |
| syntax:latest | — | Custom model |
| java:latest | — | Custom model |
| smollm2:135m | 270 MB | SmolLM |

System prompt on smollm2: `You are a helpful AI assistant named SmolLM, trained by Hugging Face`

The custom `syntax:latest` and `java:latest` models suggest research tooling — possibly code syntax assistance or Java-specific fine-tunes.

---

## Findings

### F1 — 120B Model Accessible for Free Inference (HIGH)

`gpt-oss:120b` — OpenAI's 120B open-weight model — accessible without authentication. Frontier-class inference at Caltech's compute cost.

### F2 — Active RAG Pipeline (MEDIUM)

Two embedding models (`gte-qwen2-1.5b` and `mxbai-embed-large`) co-deployed with a custom `syntax:latest` model suggests an active RAG pipeline under development, likely for code understanding research.

### F3 — Model Injection (CRITICAL)

CVE-2025-63389 applies. Custom research models (`syntax`, `java`) injectable via `/api/create`.

---

## Remediation

```bash
OLLAMA_HOST=127.0.0.1:11434
systemctl restart ollama
```

---

## Disclosure

- **Discovered:** 2026-05-02
- **Status:** Pending outreach to Caltech IMSS security
