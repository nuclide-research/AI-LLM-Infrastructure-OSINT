# Morocco ONPT — National Telecom Operator Ollama Node

_NuClide Research · 2026-05-02_

---

## Summary

Office National des Postes et Télécommunications (ONPT), Morocco's national postal and telecommunications operator, exposes one Ollama node (160.174.129.120) with a single model. ONPT operates Morocco's national communications infrastructure — the presence of Ollama on this network is unexpected.

---

## Infrastructure

| Field | Value |
|---|---|
| IP | 160.174.129.120 |
| Org | Office National des Postes et Telecommunications ONPT |
| Country | Morocco |
| Ollama version | 0.9.6 |
| Open port | 11434 (public) |

---

## Models

| Model | Notes |
|---|---|
| (1 model) | No system prompt |

---

## Findings

### F1 — National Telecom Infrastructure Exposure (MEDIUM)

ONPT is Morocco's national PTT — public telecommunications infrastructure. An Ollama node on this network suggests either a staff workstation or a pilot AI deployment without perimeter controls.

### F2 — Model Injection (CRITICAL)

CVE-2025-63389 applies.

---

## Remediation

```bash
OLLAMA_HOST=127.0.0.1:11434
systemctl restart ollama
```

---

## Disclosure

- **Discovered:** 2026-05-02
- **Status:** Pending outreach
