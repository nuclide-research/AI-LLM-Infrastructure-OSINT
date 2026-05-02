# Seoul National University — 3-Node Cluster, Cloud Proxy + Credential Leak (user: node1)

_NuClide Research · 2026-05-01_

---

## Summary

Seoul National University (SNU — 서울대학교) has three Ollama instances on the 147.47.0.0/16 campus block. Node 1 (147.47.200.153) carries cloud proxy subscriptions and leaks Ollama Connect credentials. Nodes 2 and 3 (147.47.209.39, 147.46.112.49) are additional unauthenticated inference nodes on adjacent SNU subnets.

---

## Infrastructure

| IP | Version | Models | Cloud | Notes |
|---|---|---|---|---|
| 147.47.200.153 | — | 5 | 2 | Credential leak (user: node1) |
| 147.47.209.39 | 0.11.10 | 4 | 0 | — |
| 147.46.112.49 | 0.20.2 | 2 | 0 | — |

---

## Node 1 — 147.47.200.153 (Cloud Proxy + Credential Leak)

| Model | Size | Notes |
|---|---|---|
| `devstral-2:123b-cloud` | 0GB | Cloud proxy |
| `deepseek-v3.1:671b-cloud` | 0GB | Cloud proxy |
| `codellama:13b` | 7.4GB | Local |
| `mistral:7b` | 4.4GB | Local |
| `smollm2:135m` | 0.3GB | Local |

### Credential Leak via 401 Response

```
{"error":"unauthorized","signin_url":"https://ollama.com/connect?name=node1&key=c3NoLWVkMjU1MT..."}
```

- **Username:** `node1`
- **SSH pubkey:** `ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIEc/PPDVTM/k5JSpGzWGbwkpMAMWFyOj57QhQAL7hYDC`

The `node1` username pattern indicates a service account — likely shared institutional infrastructure.

---

## Node 2 — 147.47.209.39 (v0.11.10, 4 models)

4 models, no cloud proxies. Ollama v0.11.10. All injectable via CVE-2025-63389.

---

## Node 3 — 147.46.112.49 (v0.20.2, 2 models)

2 models, no cloud proxies. Ollama v0.20.2 (recent). All injectable via CVE-2025-63389.

---

## Findings

### F1 — Credential Leak via 401 Response (CRITICAL)

Cloud proxy inference on node 1 returns Ollama Connect signin URL with base64-encoded SSH public key. Account claimable by any actor who visits the URL.

### F2 — Cloud Proxy Portfolio (HIGH)

`devstral-2:123b-cloud` (123B) and `deepseek-v3.1:671b-cloud` (671B) on node 1. Both return `{"error":"unauthorized"}`.

### F3 — Additional Unauthenticated Nodes (HIGH)

Nodes 2 and 3 on SNU subnets 147.47.0.0/16 and 147.46.0.0/16 expand the unauth inference surface across the campus.

### F4 — CVE-2025-63389 Injectable (HIGH)

All three nodes injectable via unauthenticated `/api/create`.

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
