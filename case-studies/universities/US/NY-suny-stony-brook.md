# SUNY Stony Brook — Biology Department, OLMo Research Stack + Cloud Proxy

_NuClide Research · 2026-05-01_

---

## Summary

SUNY Stony Brook Biology Department server (`040-218.bio.sunysb.edu`) is running Ollama with the full Allen AI OLMo-3 research stack (olmo-3, olmo-3.1-32b-think, olmo-3.1-32b-instruct) alongside `gpt-oss:latest` cloud proxy and several Gemma 4 models. Unauthenticated, publicly accessible.

---

## Infrastructure

| Field | Value |
|---|---|
| IP | 129.49.40.218 |
| rDNS | `040-218.bio.sunysb.edu` |
| Org | State University of New York at Stony Brook |
| Department | Biology |
| Country | US — New York |
| Open ports | 11434 (Ollama — **public**) |

---

## Models

| Model | Size | Notes |
|---|---|---|
| gpt-oss:latest | ? | ☁️ Cloud proxy |
| olmo-3:latest | ? | Allen AI OLMo-3 |
| olmo-3.1:32b-think | ? | Allen AI OLMo-3.1 reasoning |
| olmo-3.1:32b-instruct | ? | Allen AI OLMo-3.1 instruct |
| mistral-small3.2:latest | ? | — |
| gemma4:26b | ? | — |
| gemma4:latest | ? | — |
| lfm2:latest | ? | Liquid FM-2 |

---

## Findings

**F1 — Biology Research Server (HIGH):** OLMo models (Allen AI's open research language models) suggest active NLP/bioinformatics research. Model injection via CVE-2025-63389 affects research outputs.

**F2 — Cloud Proxy Exposure (HIGH):** `gpt-oss:latest` present. Status (200 OK vs 401) not confirmed in final probe.

**F3 — Model Injection (HIGH):** All models injectable via CVE-2025-63389.

---

## Disclosure

- **Discovered:** 2026-05-01
- **Status:** Pending outreach to SUNY Stony Brook IT Security
