# Binh Duong University — Account Takeover, Contabo VPS (`itu.edu.vn`)

_NuClide Research · 2026-05-03_

---

## Summary

A server with hostname `itu.edu.vn` (94.136.191.179) running Ollama on Contabo GmbH VPS infrastructure has a live Ollama Connect account takeover. The hostname references the International University (IU Vietnam) or Binh Duong University domain, indicating a Vietnamese academic operator running cloud-hosted Ollama outside campus infrastructure. The cloud proxy 401 leaks an account claim URL.

---

## Infrastructure

| Field | Value |
|---|---|
| IP | 94.136.191.179 |
| Hostname | itu.edu.vn |
| Hosting | Contabo GmbH (Germany — commercial VPS) |
| Institution | Binh Duong University / IU Vietnam |
| Country | Vietnam (operator) / Germany (hosting) |
| Ollama version | 0.13.1 |
| Open port | 11434 (public, no auth) |

---

## Account Takeover

```json
{
  "error": "unauthorized",
  "signin_url": "https://ollama.com/connect?name=372f4fd0a9dd&key=<base64>"
}
```

- **Username:** `372f4fd0a9dd` (MAC address)
- **SSH pubkey:** `ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIByBAlbkqHJMN9yeNases9WgIyniv2tcW3CLwPQs6VNM`

---

## Models

| Model | Notes |
|---|---|
| `minimax-m2.7:cloud` | ☁️ Cloud proxy — account takeover |
| `llama3.2:3b` | Local 3B model |

---

## Findings

### F1 — Account Takeover via Cloud Proxy 401 (CRITICAL)

MiniMax M2.7 cloud subscription exposed via unauthenticated port. Live claim URL leaks SSH pubkey and account credentials.

### F2 — Off-Campus VPS Deployment (MEDIUM)

The server is hosted on Contabo VPS (Germany), not on university infrastructure. The operator moved the Ollama instance to a commercial VPS — likely to avoid university firewall restrictions — bypassing any network-level controls the institution might have had.

### F3 — CVE-2025-63389 (HIGH)

v0.13.1. Both models injectable.

---

## Remediation

Rotate Ollama Connect account, restrict port 11434 in Contabo firewall settings.

---

## Disclosure

- **Discovered:** 2026-05-03
- **Status:** Pending outreach to IU Vietnam / VN-CERT
