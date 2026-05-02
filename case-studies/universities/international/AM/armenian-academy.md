# Institute for Informatics and Automation Problems, Armenia — Dual Cloud Proxy + Docker Credential Leak

_NuClide Research · 2026-05-01_

---

## Summary

The Institute for Informatics and Automation Problems of the National Academy of Sciences of Armenia (Yerevan) is running Ollama inside a Docker container with two cloud proxy subscriptions. The 401 response leaks Docker container credentials — consistent with the Docker port-binding misconfig pattern also found at Hanoi University.

---

## Infrastructure

| Field | Value |
|---|---|
| IP | 37.26.168.19 |
| rDNS | h168.019.yerphi.am |
| Org | Institute for Informatics and Automation Problems, NAS Armenia |
| Country | Armenia |
| Open ports | 11434 (Ollama — **public**) |

---

## Credential Leak

```json
{
  "error": "unauthorized",
  "signin_url": "https://ollama.com/connect?name=c2a68a9aa573&key=<base64>"
}
```

- **Username:** `c2a68a9aa573` — Docker container ID
- **SSH pubkey:** `ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIBqWiNKYbTt7XQxVG0OdY/61UHxsXkuGVtuS0UShBD7V`

Both cloud proxy models return 401 with the same credentials — single Ollama Connect account inside one Docker container.

---

## Models

| Model | Size | Type |
|---|---|---|
| deepseek-v4-pro:cloud | 0 GB | ☁️ Cloud proxy |
| minimax-m2.7:cloud | 0 GB | ☁️ Cloud proxy |
| llama3.2:3b | 1 GB | Local |

---

## Findings

**F1 — Docker Credential Leak (HIGH):** Container ID in Ollama Connect username.  
**F2 — Dual Cloud Proxy on Academic Research Server (HIGH):** DeepSeek and MiniMax subscriptions exposed.  
**F3 — Model Injection (CRITICAL):** All 3 models injectable via CVE-2025-63389.

---

## Pattern

Docker container hostname as Ollama username also seen at: Hanoi University (Vietnam, `04aa6fb5e0b8`), Purdue NW (US-IN, `c0ddfaef7764`). All three expose port 11434 via `docker run -p 11434:11434` which binds to 0.0.0.0.

---

## Disclosure

- **Discovered:** 2026-05-01
- **Status:** Pending outreach to IIAP NAS Armenia / AM-CERT
