# Kumamoto University — Account Takeover, MiniMax Cloud Proxy (CS Architecture Lab)

_NuClide Research · 2026-05-03_

---

## Summary

`scorpio.arch.cs.kumamoto-u.ac.jp` (133.95.140.141), Kumamoto University Computer Science department (Architecture lab, `arch.cs`), runs Ollama v0.12.7 with a live Ollama Connect account takeover. The MiniMax M2.7 cloud proxy returns a 401 that leaks the account claim URL and SSH public key.

---

## Infrastructure

| Field | Value |
|---|---|
| IP | 133.95.140.141 |
| Hostname | scorpio.arch.cs.kumamoto-u.ac.jp |
| Organization | Kumamoto University — Computer Science, Architecture Lab |
| Network | AS2907 NII/SINET (Japan national academic backbone) |
| Country | Japan |
| Ollama version | 0.12.7 |
| Open port | 11434 (public) |

---

## Account Takeover

```json
{
  "error": "unauthorized",
  "signin_url": "https://ollama.com/connect?name=d4659cbf55b2&key=c3NoLWVkMjU1MTkgQUFBQUMzTnphQzFsWkRJMU5URTVBQUFBSU1vU09TdE53SkdVTWE2RVJ3MUN6M0I2bWFkUk1jSlp5UnBrWlAzNEx0N2Q"
}
```

- **Username:** `d4659cbf55b2` (MAC address format)
- **SSH pubkey:** `ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIMoSOStNwJGUMa6ERw1Cz3B6madRMcJZyRpkZP34Lt7d`

---

## Models

| Model | Notes |
|---|---|
| `minimax-m2.7:cloud` | ☁️ Cloud proxy — account takeover |
| `qwen3.6:35b` | Local 35B model |
| `gemma3:27b` | Local 27B model |
| `smollm:135m` | SmolLM |

---

## Findings

### F1 — Account Takeover via MiniMax M2.7 Cloud Proxy (CRITICAL)

Live claim URL exposed. SSH pubkey `ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIMoSOStNwJGUMa6ERw1Cz3B6madRMcJZyRpkZP34Lt7d` leaked. Visiting the signin URL with an attacker-controlled account transfers the Ollama Connect association to the attacker, giving full control over the operator's cloud model quota and subscription.

The `scorpio.arch.cs.kumamoto-u.ac.jp` hostname pattern (`scorpio` + `arch.cs`) identifies this as the Architecture research lab in the CS department — likely a workstation or lab server used for computer architecture research.

### F2 — v0.12.7: ~1.5-Year-Old Version (HIGH)

Ollama v0.12.7 dates to approximately mid-2024. CVE-2025-63389 applies. All 4 models are injectable via unauthenticated `/api/create`.

### F3 — CVE-2025-63389 (CRITICAL)

All 4 models injectable via unauthenticated `/api/create`.

---

## Remediation

Rotate Ollama Connect account immediately. Restrict port 11434:

```bash
OLLAMA_HOST=127.0.0.1:11434
systemctl restart ollama
```

---

## Disclosure

- **Discovered:** 2026-05-03
- **Status:** Pending outreach to Kumamoto University IT / JPCERT (cert@jpcert.or.jp)
