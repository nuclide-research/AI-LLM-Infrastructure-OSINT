# Lanka Education and Research Network (LEARN) — Credential Leak (user: modelserver)

_NuClide Research · 2026-05-01_

---

## Summary

Sri Lanka's academic network (LEARN — Lanka Education and Research Network) has an Ollama instance at 192.248.70.139 with a `deepseek-v4-pro:cloud` subscription and `llama3.2-vision`. The cloud proxy 401 response leaks the Ollama Connect account username `modelserver` and corresponding SSH public key.

---

## Infrastructure

| Field | Value |
|---|---|
| IP | 192.248.70.139 |
| Organization | Lanka Education and Research Network (LEARN) — Information Technology Center |
| Country | Sri Lanka |
| ASN | APNIC assigned, LEARN-LK |
| Open ports | 11434 (Ollama — public) |

---

## Model Inventory

| Model | Size | Notes |
|---|---|---|
| `deepseek-v4-pro:cloud` | 0 | Cloud proxy — credential leak |
| `llama3.2-vision:latest` | 7GB | Multimodal vision-language |

---

## Findings

### F1 — Credential Leak (user: modelserver) (HIGH)

Querying the `deepseek-v4-pro:cloud` model triggers a 401 response containing the Ollama Connect account credentials:

```json
{
  "error": "unauthorized",
  "signin_url": "https://ollama.com/connect?name=modelserver&key=AAAAC3NzaC1lZDI1NTE5AAAAIBefRlkywyAvwYWiTapAKIiPnTAKLic1GNxEZeJfwG6l"
}
```

- **Username:** `modelserver`
- **SSH Public Key:** `ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIBefRlkywyAvwYWiTapAKIiPnTAKLic1GNxEZeJfwG6l`

The username `modelserver` is a service account pattern, suggesting institutional deployment rather than a personal workstation.

### F2 — Unauthenticated Inference (HIGH)

Both models accessible without authentication. `llama3.2-vision` enables multimodal inference (image + text) at LEARN's expense.

### F3 — CVE-2025-63389 Injectable (HIGH)

Both models injectable via unauthenticated `/api/create`.

---

## Remediation

```bash
OLLAMA_HOST=127.0.0.1:11434
systemctl restart ollama
```

---

## Disclosure

- **Discovered:** 2026-05-01
- **Status:** Pending outreach to LEARN-LK IT
