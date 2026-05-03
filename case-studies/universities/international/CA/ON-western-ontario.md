# University of Western Ontario — 2-Node Cluster, Account Takeover on Node 2

_NuClide Research · 2026-05-01 — Updated 2026-05-03_

---

## Summary

University of Western Ontario (London, Ontario) Engineering faculty runs two Ollama nodes on its `eng.uwo.ca` subnet. Node 1 (WE-D-ECE-0288) has 9 models with cloud proxy (no credential exposure). Node 2 (ebithp-c1v17) exposes an Ollama Connect account via 401 credential leak — **account takeover available**. Both nodes run Ollama without authentication.

---

## Infrastructure

| Node | IP | Hostname | Ollama | Cloud | Takeover |
|------|-----|----------|--------|-------|---------|
| Node 1 | 129.100.226.217 | WE-D-ECE-0288.eng.uwo.ca | v0.x | deepseek-v4-pro | No |
| Node 2 | 129.100.174.232 | ebithp-c1v17.eng.uwo.ca | v0.13.5 | deepseek-v4-pro | **YES** |

Both nodes: Engineering faculty, `eng.uwo.ca` subnet, port 11434 public.

---

## Account Takeover — Node 2 (CRITICAL)

```json
{
  "error": "unauthorized",
  "signin_url": "https://ollama.com/connect?name=0732205c469d&key=<base64>"
}
```

- **Account name:** `0732205c469d`
- **SSH public key:** `ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIOqftorYOI//59fSD15j0BFaxUFniYm6Z1cVqE9pp3Jx`

The base64-encoded key is the Ed25519 public key for the Ollama Connect account. The corresponding private key is held on the UWO server; the public key, once known, can be used to claim or identify the account at `ollama.com/connect`.

---

## Node 1 Models (129.100.226.217)

---

## Models

| Model | Size | Notes |
|---|---|---|
| deepseek-v4-pro:cloud | 0 GB | ☁️ Cloud proxy — DeepSeek API |
| qwen3.6:35b | 22 GB | Local |
| qwen2.5vl:3b | 2 GB | Local — vision-language |
| qwen2.5vl:7b-q8_0 | 8 GB | Local — vision-language |
| gemma4:e2b | 6 GB | Local |
| gemma4:31b | 18 GB | Local |
| qwen2.5vl:latest | 5 GB | Local — vision-language |
| llava:latest | 4 GB | Local — vision-language |
| qwen3.5:35b | 22 GB | Local |

---

## Node 2 Models (129.100.174.232)

| Model | Size | Notes |
|---|---|---|
| deepseek-v4-pro:cloud | 0 GB | ☁️ Cloud proxy — **account takeover** |
| llama3.2:3b | 1.9 GB | Local |
| llama3.2:latest | 1.9 GB | Local |
| smollm:135m | 0.1 GB | Local |
| smollm2:135m | 0.3 GB | Local |

---

## Findings

### F1 — Account Takeover on Node 2 (CRITICAL)

`ebithp-c1v17.eng.uwo.ca` returns Ollama Connect credentials on 401 response from `deepseek-v4-pro:cloud`. The exposed public key allows an attacker to claim the Ollama Connect account, taking over the cloud subscription and redirecting all cloud model traffic to attacker-controlled endpoints.

### F2 — Two-Node Engineering Faculty Cluster Exposed (HIGH)

Both `WE-D-ECE-0288` and `ebithp-c1v17` on the Engineering faculty subnet expose Ollama without authentication. Any researcher in UWO Engineering using these nodes is subject to model injection, inference enumeration, and cloud subscription abuse.

### F3 — Vision-Language Models Exposed on Node 1 (MEDIUM)

Three vision-language model variants on Node 1 (qwen2.5vl, llava) accessible without auth.

---

## Remediation

```bash
OLLAMA_HOST=127.0.0.1:11434
systemctl restart ollama
```

---

## Disclosure

- **Discovered:** 2026-05-01
- **Status:** Pending outreach to UWO IT / ECE department
