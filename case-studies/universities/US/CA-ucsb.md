# UC Santa Barbara — Open WebUI Auth Disabled + Local Username Leak

_NuClide Research · 2026-05-01_

---

## Summary

University of California, Santa Barbara "AI Lab" instance running Open WebUI v0.8.12 with authentication **completely disabled**. Any internet actor can enumerate models, read model configurations, and execute inference — no credentials required. Includes `functiongemma:latest`, a native function-calling model. Modelfile path leaks the macOS local username.

---

## Infrastructure

| Field | Value |
|---|---|
| IP | 169.231.124.164 |
| rDNS | 169-231-124-164.wireless.ucsb.edu |
| Org | University of California, Santa Barbara |
| Country | US — California |
| Instance name | **"AI Lab (Open WebUI)"** |
| Open ports | 3000 (Open WebUI — **auth disabled**), 11434 (Ollama — **public**) |

---

## Configuration

```json
{
  "name": "AI Lab (Open WebUI)",
  "version": "0.8.12",
  "features": {
    "auth": false,
    "enable_signup": false
  }
}
```

---

## Models

| Model | Size | Notes |
|---|---|---|
| gemma4:31b | 18 GB | Local |
| functiongemma:latest | 0 GB | Native tool/function-calling |
| gemma3:27b | 16 GB | Local |

---

## Findings

### F1 — Authentication Disabled (CRITICAL)

Open WebUI auth is explicitly set to `false`. No login required. All models accessible via both port 3000 and port 11434.

```bash
# No auth — direct inference
curl -s http://169.231.124.164:3000/api/chat  # full WebUI API
curl -s http://169.231.124.164:11434/api/generate \
  -d '{"model":"gemma3:27b","prompt":"...","stream":false}'
```

Confirmed: inference on `gemma3:27b` executes without any credential.

### F2 — Local Username + OS Leak (MEDIUM)

`functiongemma:latest` modelfile exposes the local model path:

```
FROM /Users/marcos/.ollama/models/blobs/sha256-415f8f...
```

- **OS:** macOS (`/Users/` path)
- **Username:** `marcos`

### F3 — Function-Calling Model Exposed (MEDIUM)

`functiongemma:latest` uses Ollama's native function-calling (`RENDERER functiongemma`, `PARSER functiongemma`). If this model is integrated with any tool-execution framework, unauthenticated callers can invoke tool calls.

---

## Remediation

```bash
# Enable authentication in Open WebUI settings
# (Admin Panel → Settings → Auth → Enable authentication)

# Also bind Ollama to loopback
OLLAMA_HOST=127.0.0.1:11434
```

---

## Node: spark-4de1.mcdb.ucsb.edu (128.111.208.95) — Biology Dept, DeepSeek Cloud

`spark-4de1.mcdb.ucsb.edu` — Molecular, Cellular, and Developmental Biology (MCDB) department, `spark-4de1` hostname. v0.13.2.

| Model | Size | Notes |
|---|---|---|
| `qwen3.6:35b` | 23GB | Local |
| `deepseek-v4-pro:cloud` | — | ☁️ Cloud proxy (no takeover URL at probe time) |
| `smollm2:135m` | — | — |
| `llama3.1:8b` | 4GB | — |

DeepSeek V4 Pro cloud proxy present but the 401 response did not include a `signin_url` — indicating the cloud proxy may not be actively linked to an Ollama Connect account, or the account has been rotated. Unauthenticated inference on local models confirmed. CVE-2025-63389 applicable.

| Node | IP | Hostname | Notes |
|---|---|---|---|
| AI Lab | 169.231.124.164 | 169-231-124-164.wireless.ucsb.edu | Open WebUI auth disabled, macOS marcos |
| MCDB Dept | 128.111.208.95 | spark-4de1.mcdb.ucsb.edu | DeepSeek cloud proxy, qwen3.6:35b |

---

## Disclosure

- **Discovered:** 2026-05-01 (AI Lab) / 2026-05-03 (MCDB node)
- **Status:** Pending outreach to UCSB IT / AI Lab operator
