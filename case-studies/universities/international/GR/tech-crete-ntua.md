# Technical University of Crete + NTUA — Unauthenticated Ollama, MiniMax Cloud, 235.7B Model

_NuClide Research · 2026-05-01_

---

## Technical University of Crete

**IP:** 147.27.38.32 (`hp2420.telecom.tuc.gr`) — Heraklion, Greece  
**Models:** 14 (1 cloud proxy)

### MiniMax Cloud Proxy + Credential Leak

```json
{
  "error": "unauthorized",
  "signin_url": "https://ollama.com/connect?name=arian&key=<base64>"
}
```

- **Username:** `arian`
- **SSH pubkey:** `ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIASZr/fN5P73o/WF6vT/owMFz3ftTeBlzOpEFpS2QStP`
- **Cloud proxy:** `minimax-m2.7:cloud` (MiniMax API subscription)

14 total models accessible without authentication.

---

## National Technical University of Athens — Node 1

**IP:** 147.102.40.5 (`p620.cn.ece.ntua.gr`) — Athens, Greece  
**Models:** 20 (0 cloud proxy)

### 235.7B-Parameter Model Exposed

| Model | Size | Notes |
|-------|------|-------|
| deepseek-coder-v2:236b | **123 GB** | 235.7B-param MoE coding model (tag is `:236b`, actual params 235.7B) |
| qwen2.5-coder:32b | 18 GB | Coding |
| qwen3-coder:30b | 17 GB | Coding |
| qwen3-embedding:0.6b | 0 GB | Embedding — RAG component |
| qwen3:latest | 4 GB | General |
| (15 more models) | | |

20 models accessible without authentication. The `deepseek-coder-v2:236b` (235.7B params, 123GB on disk) represents significant dedicated GPU compute accessible to any internet actor for free inference.

RAG pipeline present: `qwen3-embedding:0.6b` suggests active document retrieval workflow.

---

## National Technical University of Athens — Node 2

**IP:** 147.102.111.27 — Athens, Greece  
**Models:** 3 (2 cloud proxy)

### Cloud Proxy + Account Takeover

```json
{
  "error": "unauthorized",
  "signin_url": "https://ollama.com/connect?name=1600b8395e7f&key=<base64>"
}
```

- **Username:** `1600b8395e7f`
- **SSH pubkey:** `ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIB5OXHHJjrUQNMZQWSXuZlJz8DG422KMffCpLMst22/5`
- **Cloud proxies:** `deepseek-v4-pro:cloud`, `minimax-m2.7:cloud`

| Model | Notes |
|-------|-------|
| deepseek-v4-pro:cloud | Cloud proxy — account takeover |
| minimax-m2.7:cloud | Cloud proxy — account takeover |
| llama3.2:3b | Local |

Username `1600b8395e7f` is a MAC address or container ID — automated or containerized deployment.

---

## Findings (Both)

Both institutions have unauthenticated Ollama ports (11434 open, no auth). CVE-2025-63389 model injection applies to all models on both hosts.

TechCrete F2 — credential leak on MiniMax cloud proxy.  
NTUA F2 — free inference on 235.7B model, potential RAG pipeline injection.

---

## Remediation

```bash
OLLAMA_HOST=127.0.0.1:11434
systemctl restart ollama
```

---

## Disclosure

- **Discovered:** 2026-05-01
- **Status:** Pending outreach to TUC and NTUA IT Security
