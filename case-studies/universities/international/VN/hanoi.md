# Hanoi University — 18 Cloud Proxy Subscriptions + Credential Leak (Containerized Deployment)

_NuClide Research · 2026-05-01_

---

## Summary

Hanoi University (Vietnam) running a 31-model Ollama instance with 18 active cloud proxy subscriptions. Cloud proxy 401 response leaks Ollama Connect credentials — **username `04aa6fb5e0b8` is a Docker container ID**, confirming Ollama runs inside a container with no network isolation. Raw Ollama port publicly accessible.

---

## Infrastructure

| Field | Value |
|---|---|
| IP | 103.185.232.21 |
| Org | Hanoi University |
| Country | Vietnam |
| Open ports | 11434 (Ollama — **public**) |

---

## Credential Leak

```json
{
  "error": "unauthorized",
  "signin_url": "https://ollama.com/connect?name=04aa6fb5e0b8&key=<base64>"
}
```

- **Username:** `04aa6fb5e0b8` — **Docker container ID** (the container's hostname, which Ollama uses as the account name)
- **SSH pubkey:** `ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAILi5RXxQeIXNUjDJJl2W54szLU6Y5IQI4IulfxbWaK14`

The container hostname as Ollama username reveals the operator registered Ollama Connect from inside a Docker container. This means port 11434 was published from the container to the host, then left accessible externally — a common misunderstanding of Docker's default `0.0.0.0` binding behavior.

---

## Cloud Proxies (18)

Same ecosystem as POSTECH and Shiv Nadar: DeepSeek (v4-pro, v4-flash, v3.2), MiniMax (m2.7, m2.5, m2.1, m2), Kimi (k2.6, k2.5, k2-thinking), GLM (5.1, 5, 4.7, 4.6), Qwen (3.5, coder-next), Nemotron, Gemini.

---

## Findings

### F1 — 18 Cloud Proxy Subscriptions Exposed (CRITICAL)

All 18 cloud proxies accessible via unauthenticated port 11434.

### F2 — Credential Leak via Containerized Deployment (HIGH)

Docker container ID exposed as Ollama Connect username. Any actor probing port 11434 receives the container's SSH public key, confirming containerized deployment and extracting credentials.

### F3 — Docker Port Publishing Misunderstanding (HIGH)

Ollama published via Docker `-p 11434:11434` defaults to `0.0.0.0` binding. The operator likely assumed this was internal-only. All 31 models + 18 cloud proxies are exposed as a result.

---

## Remediation

```bash
# Docker: bind to loopback only
docker run -p 127.0.0.1:11434:11434 ollama/ollama

# Or use OLLAMA_HOST inside container
```

---

## Disclosure

- **Discovered:** 2026-05-01
- **Status:** Pending outreach to Hanoi University IT / Vietnam CERT
