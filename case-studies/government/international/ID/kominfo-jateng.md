# DINAS KOMINFO PROV. JAWA TENGAH — Account Takeover, RAG Pipeline

_NuClide Research · 2026-05-02_

---

## Summary

The Central Java Province Communications and Information Technology Department (Dinas Kominfo Prov. Jawa Tengah) exposes an Ollama node at `sijoli-11-245-107.jatengprov.go.id` (103.107.245.11) on the Indonesian government network (`.go.id`). The node runs cloud proxy subscriptions including MiniMax M2.7 and an embedding model indicating a RAG pipeline. The cloud proxy 401 response leaks a live Ollama Connect claim URL — full account takeover available.

---

## Infrastructure

| Field | Value |
|---|---|
| IP | 103.107.245.11 |
| Hostname | sijoli-11-245-107.jatengprov.go.id |
| Organization | Dinas Kominfo Prov. Jawa Tengah |
| Network | `.jatengprov.go.id` (Central Java Province Government) |
| Country | Indonesia |
| Ollama version | 0.13.2 |
| Open port | 11434 (public) |

---

## Model Inventory

| Model | Notes |
|---|---|
| `minimax-m2.7:cloud` | Cloud proxy — **account takeover** |
| `bge-m3:latest` | BGE-M3 multilingual embedding — RAG pipeline |
| `qwen3:14b` | Local 14B model |
| `llama3.2:3b` | Local 3B model |
| `smollm2:135m` | SmolLM — system prompt: "You are a helpful AI assistant named SmolLM, trained by Hugging Face" |

---

## Findings

### F1 — Account Takeover via Live Claim URL (CRITICAL)

Querying `minimax-m2.7:cloud` returns a live Ollama Connect claim URL:

```json
{
  "error": "unauthorized",
  "signin_url": "https://ollama.com/connect?name=da298cd9ca86&key=<base64>"
}
```

- **Username:** `da298cd9ca86` (MAC address / container ID)
- **SSH pubkey:** `ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIEd19vXJ586h1nPgxSuRVifj6XAtuBnfdKO6H7fN2V7c`

Visiting the URL claims the account, granting full model management and cloud subscription control over MiniMax M2.7 API quota.

### F2 — RAG Pipeline on Government Infrastructure (HIGH)

`bge-m3:latest` (BGE-M3 multilingual embedder) alongside `qwen3:14b` indicates an active Retrieval-Augmented Generation pipeline. The hostname `sijoli` may correspond to an internal government information system (SIJOLI — Sistem Informasi). Government document retrieval via an unauthenticated, injectable Ollama endpoint.

### F3 — CVE-2025-63389 Injectable (CRITICAL)

v0.13.2 — old, unpatched. All five models injectable via unauthenticated `/api/create`.

---

## Remediation

```bash
OLLAMA_HOST=127.0.0.1:11434
systemctl restart ollama
```

---

## Disclosure

- **Discovered:** 2026-05-02
- **Status:** Pending outreach to Dinas Kominfo Jawa Tengah
- **Contact:** kominfo@jatengprov.go.id
