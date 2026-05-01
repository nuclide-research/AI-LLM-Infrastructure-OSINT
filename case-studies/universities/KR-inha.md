# INHA University — gpt-oss:20b Local + Nemotron Cascade Stack

_NuClide Research · 2026-05-01_

---

## Summary

INHA University (인하대학교) in Incheon has an Ollama instance with 7 models totalling ~133GB including a local `gpt-oss:20b` (20.9B params) and two NVIDIA Nemotron-Cascade 30B models.

---

## Infrastructure

| Field | Value |
|---|---|
| IP | 165.246.39.51 |
| Organization | INHA UNIVERSITY |
| Country | South Korea |
| Open ports | 11434 (Ollama — public) |

---

## Model Inventory

| Model | Size | Notes |
|---|---|---|
| `gpt-oss:20b` | 12.1GB | Local inference, 20.9B params, `gpt-oss` family |
| `hf.co/unsloth/gpt-oss-20b-GGUF:Q8_0` | 12.1GB | Same weights, direct HF GGUF pull |
| `nemotron-cascade-2:30b` | 24.3GB | NVIDIA Nemotron Cascade 2 30B |
| `gemma4:26b-a4b-it-q8_0` | 28.1GB | Gemma 4 Q8 |
| `nemotron-3-nano:30b` | 24.3GB | NVIDIA Nemotron-3 Nano 30B |
| `qwen3.5:27b` | 22.5GB | — |
| `deepseek-r1:14b` | 9.0GB | — |

**Total local storage:** ~132GB

---

## Findings

### F1 — Local gpt-oss:20b and Dual Nemotron Stack (HIGH)

`gpt-oss:20b` is running locally (12.1GB, 20.9B params). The model family `gpt-oss` is the OpenAI open-source weights release. Both the standard Ollama-tagged version and the direct HuggingFace GGUF pull are present — suggesting the operator downloaded via `hf.co/unsloth/gpt-oss-20b-GGUF:Q8_0` first, then aliased it.

The dual `nemotron-cascade-2:30b` and `nemotron-3-nano:30b` stack (both 24.3GB) suggests NVIDIA model evaluation or research use.

### F2 — CVE-2025-63389 Injectable (HIGH)

All models injectable via unauthenticated `/api/create`. The Nemotron and gpt-oss models have no system prompts — post-injection inference is unobstructed.

---

## Remediation

```bash
OLLAMA_HOST=127.0.0.1:11434
systemctl restart ollama
```

---

## Disclosure

- **Discovered:** 2026-05-01
- **Status:** Pending outreach to INHA IT (inha.ac.kr)
