# Seoul National University — Cloud Proxy + Credential Leak (user: node1)

_NuClide Research · 2026-05-01_

---

## Summary

Seoul National University (SNU — 서울대학교) has an Ollama instance at 147.47.200.153 with two large cloud proxy models. The 401 response on cloud proxy inference reveals the Ollama Connect service account username and SSH public key.

---

## Infrastructure

| Field | Value |
|---|---|
| IP | 147.47.200.153 |
| Organization | Seoul National University |
| Network | SNU Campus (147.47.0.0/16) |
| Country | South Korea |
| Open ports | 11434 (Ollama — public) |

---

## Model Inventory

| Model | Size | Notes |
|---|---|---|
| `devstral-2:123b-cloud` | 0GB | Cloud proxy |
| `deepseek-v3.1:671b-cloud` | 0GB | Cloud proxy |
| `codellama:13b` | 7.4GB | Local |
| `mistral:7b` | 4.4GB | Local |
| `smollm2:135m` | 0.3GB | Local |

---

## Findings

### F1 — Credential Leak via 401 Response (CRITICAL)

Cloud proxy inference returns Ollama Connect signin URL containing base64-encoded SSH public key:

```
{"error":"unauthorized","signin_url":"https://ollama.com/connect?name=node1&key=c3NoLWVkMjU1MT..."}
```

Decoded:
- **Username:** `node1`
- **SSH pubkey:** `ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIEc/PPDVTM/k5JSpGzWGbwkpMAMWFyOj57QhQAL7hYDC`

The `node1` username pattern indicates a service account or generic node account.

### F2 — Cloud Proxy Portfolio (HIGH)

`devstral-2:123b-cloud` and `deepseek-v3.1:671b-cloud` are present. No 200 OK confirmed (both return `{"error":"unauthorized"}`).

### F3 — CVE-2025-63389 Injectable (HIGH)

All models injectable via unauthenticated `/api/create`.

---

## Remediation

```bash
OLLAMA_HOST=127.0.0.1:11434
systemctl restart ollama
```

---

## Disclosure

- **Discovered:** 2026-05-01
- **Status:** Pending outreach to SNU IT Security (snu.ac.kr)
