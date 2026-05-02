# ITMO University, Russia — 24 Models, gpt-oss:20b + gpt-oss:120b Cloud Proxies

_NuClide Research · 2026-05-01_

---

## Summary

ITMO University (Saint Petersburg, Russia) has an Ollama instance with 24 models including frontier models (Llama 4, Qwen 2.5 VL 72B, Kimi-Dev-72B) and `gpt-oss:20b` / `gpt-oss:120b` cloud proxies. No credential leak detected on active probe — likely paid-tier. Unauthenticated inference against all 24 models.

---

## Infrastructure

| Field | Value |
|---|---|
| IP | 77.234.216.105 |
| rDNS | — (NXDOMAIN) |
| Org | ITMO University (verified via Shodan ASN) |
| Country | Russia |
| Open ports | 11434 (Ollama — **public**) |

---

## Models (24 total)

| Model | Size | Notes |
|---|---|---|
| gpt-oss:20b | 12 GB | ☁️ Cloud proxy candidate |
| gpt-oss:120b | 60 GB | ☁️ Cloud proxy candidate |
| volker-mauel/Kimi-Dev-72B-GGUF:q8_0 | 71 GB | Kimi Dev coding model |
| llama4:16x17b | 62 GB | Llama 4 MoE |
| llama4:latest | 62 GB | Llama 4 |
| qwen2.5vl:72b | 65 GB | Vision-language |
| qwen3.6:35b | 22 GB | |
| qwen3.5:27b | 16 GB | |
| qwen3:32b | 18 GB | |
| qwen3:8b | 4 GB | |
| mistral-small3.2:24b | 14 GB | |
| mistral-small3.1:latest | 14 GB | |
| mistral-small3.1:24b | 14 GB | |
| mistral-small3.1-24b-128k:latest | 14 GB | |
| mistral-small:24b | 13 GB | |
| mixtral:8x7b | 24 GB | |
| gemma3:27b | 16 GB | |
| granite3.2-vision:2b | 2 GB | |
| llama3:70b | 37 GB | |
| deepseek-r1:70b | 39 GB | |
| qwen3-vl:8b | 5 GB | |
| qwen3-vl:4b | 3 GB | |
| llama3.2:3b | 1 GB | |
| smollm2:135m | 0 GB | |

---

## Findings

**F1 — Unauthenticated Ollama API (CRITICAL):** 24 models including 71GB Kimi-Dev, 65GB VL, and multiple 60GB+ frontier models accessible without credentials.

**F2 — Cloud Proxy Presence (HIGH):** `gpt-oss:20b` and `gpt-oss:120b` present. Probe timed out — status (free-tier 200 OK vs paid 401) unconfirmed.

**F3 — Model Injection (HIGH):** All 24 models injectable via CVE-2025-63389.

---

## Disclosure

- **Discovered:** 2026-05-01
- **Status:** Pending outreach to ITMO CERT
