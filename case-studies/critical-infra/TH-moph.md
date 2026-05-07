# Thailand Ministry of Public Health: Unauthenticated Ollama with Vision Model

_NuClide Research · 2026-05-01_

---

## Summary

Thailand Ministry of Public Health server running Ollama with 5 models including IBM Granite Vision 2B. Raw Ollama port publicly accessible, no authentication. No cloud proxy. Sector: **healthcare / government critical infrastructure**.

---

## Infrastructure

| Field | Value |
|---|---|
| IP | 203.157.41.151 |
| Org | Ministry of Public Health, Thailand |
| Sector | **Healthcare, National Government** |
| Country | Thailand |
| Open ports | 11434 (Ollama, **public**) |

---

## Models

| Model | Size | Notes |
|---|---|---|
| qwen3.6:35b | 22 GB | General |
| llama3.2:3b | 1 GB | General |
| smollm2:135m | 0 GB | Lightweight |
| granite3.2-vision:2b | 2 GB | **IBM vision model** |
| gemma3:4b | 3 GB | General |

`granite3.2-vision:2b` system prompt: generic assistant configuration (not domain-specific). If this model processes medical images or documents in any ministerial workflow, model injection could affect those outputs.

---

## Findings

### F1: Unauthenticated Ollama on Government Healthcare Infrastructure (CRITICAL)

Port 11434 on Ministry of Public Health infrastructure is publicly accessible. All models injectable via CVE-2025-63389.

### F2: Vision Model Injection Surface (HIGH)

`granite3.2-vision:2b` can process images. If connected to any document or imaging workflow within the ministry, injected system prompts redirect the model's behavior on visual inputs.

---

## Remediation

```bash
OLLAMA_HOST=127.0.0.1:11434
systemctl restart ollama
```

---

## Disclosure

- **Discovered:** 2026-05-01
- **Status:** Pending, outreach to Thai NCSB (National Cyber Security Agency of Thailand) / MOPH IT
