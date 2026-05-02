# Vietnam National University Ho Chi Minh City — final-exploit-v1 + gpt-oss Cloud Proxy

_NuClide Research · 2026-05-01_

---

## Summary

Vietnam National University Ho Chi Minh City (Information Technology Park) has an Ollama instance with an unusually named model `final-exploit-v1:latest` and a `gpt-oss:latest` cloud proxy. The `final-exploit-v1` model is 168 bytes — the size of a cloud proxy artifact, not a local model — suggesting a custom-named cloud redirect.

---

## Infrastructure

| Field | Value |
|---|---|
| IP | 103.88.123.165 |
| rDNS | — |
| Org | Information Technology Park — Vietnam National University Ho Chi Minh City |
| Country | Vietnam |
| Open ports | 11434 (Ollama — **public**) |

---

## Models

| Model | Size | Notes |
|---|---|---|
| final-exploit-v1:latest | 0 GB (168 bytes) | **Cloud proxy artifact — custom-named** |
| gpt-oss:latest | 12 GB | ☁️ Cloud proxy |
| llama3.2:3b | 1 GB | Local |
| llama3.2:latest | 1 GB | Local |
| smollm2:135m | 0 GB | Local |
| tinyllama:latest | 0 GB | Local |

---

## Findings

**F1 — Unauthenticated Ollama API (HIGH):** All models accessible without credentials.

**F2 — `final-exploit-v1` Cloud Proxy Artifact (MEDIUM):** The model is 168 bytes — identical size pattern to standard cloud proxy models (deepseek-v4-pro:cloud = 344 bytes, minimax = 384 bytes). Modified January 2026. No system prompt returned. Inference returns empty response. Likely a student-created cloud proxy with custom naming.

**F3 — gpt-oss Cloud Proxy (HIGH):** `gpt-oss:latest` 12GB present. Status (200 OK vs 401) not confirmed on final probe.

**F4 — Model Injection (HIGH):** All models injectable via CVE-2025-63389.

---

## Disclosure

- **Discovered:** 2026-05-01
- **Status:** Pending outreach to VNU-HCM IT Park / VNCERT
