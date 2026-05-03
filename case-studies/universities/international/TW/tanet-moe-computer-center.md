# Taiwan Ministry of Education Computer Center (TANet) — Account Takeover, Default `ollama` Credentials

_NuClide Research · 2026-05-03_

---

## Summary

A TANet-hosted node (AS1659 Taiwan Academic Network Information Center, Taipei) exposes Ollama with two cloud proxy subscriptions and a live account takeover — the Ollama Connect account name is the default `ollama`, indicating the operator never changed it from the installation default. The SSH public key is exposed via the 401 cloud proxy response. No rDNS.

---

## Infrastructure

| Field | Value |
|---|---|
| IP | 140.125.180.91 |
| rDNS | None |
| Org | AS1659 Taiwan Academic Network (TANet) Information Center |
| City | Taipei, Taiwan |
| Ollama version | 0.14.3 |
| Open port | 11434 (public, no auth) |

---

## Account Takeover

```json
{
  "error": "unauthorized",
  "signin_url": "https://ollama.com/connect?name=ollama&key=<base64>"
}
```

- **Account name:** `ollama` — **installation default, never changed**
- **SSH public key:** `ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIGdI/XYFCAqJaH2k+MfvjFRJ2i4GYKPN3rvGAEF8Niey`

The generic account name `ollama` is the default credential issued when Ollama Connect is set up without customization. It is a strong signal that the operator followed a default installation path without reviewing the cloud proxy security configuration.

---

## Models

| Model | Size | Notes |
|---|---|---|
| deepseek-v4-pro:cloud | 0 GB | ☁️ Cloud proxy — **account takeover** |
| minimax-m2.7:cloud | 0 GB | ☁️ Cloud proxy |
| smollm2:135m | 0.3 GB | Local |
| llama3.2:3b | 1.9 GB | Local |
| phi3:latest | 2.0 GB | Local |

---

## Findings

### F1 — Default Account Name Exposes Ollama Connect (CRITICAL)

Account name `ollama` is the default Ollama Connect identifier — the same credential that any operator gets during initial setup. Combined with the exposed SSH public key, this allows an attacker to claim or associate with the TANet operator's Ollama Connect account, taking over both cloud model subscriptions.

### F2 — TANet Infrastructure (HIGH)

TANet is Taiwan's national academic network, operated by the Ministry of Education Computer Center. Exposure on this network means other TANet-connected institutions may have similar misconfigurations. Related: `tanet.md` documents an 18-node TANet multi-institution cluster with separate account takeover.

### F3 — CVE-2025-63389 (CRITICAL)

All 5 models injectable via unauthenticated `/api/create`.

---

## Related

- `tanet.md` — TANet 18-node cluster, separate account takeover (`name=ollama`), multiple institutions

---

## Remediation

```bash
OLLAMA_HOST=127.0.0.1:11434
systemctl restart ollama
```

Additionally: rotate the Ollama Connect account to a non-default name via `ollama.com` settings.

---

## Disclosure

- **Discovered:** 2026-05-03
- **Status:** Pending outreach to TANet / MOE-CC Taiwan (cert@twcert.org.tw)
