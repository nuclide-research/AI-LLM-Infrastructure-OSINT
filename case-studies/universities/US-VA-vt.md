# Virginia Polytechnic Institute and State University (Virginia Tech) — DHCP Node

_NuClide Research · 2026-05-01_

---

## Summary

Virginia Tech has at least 4 Ollama-running IPs in Shodan; only `h80adf308.dhcp.vt.edu` (128.173.243.8) responds publicly. The DHCP hostname indicates a desktop or workstation on the campus DHCP pool rather than a dedicated server. 5 models, no cloud proxies.

---

## Infrastructure

| Field | Value |
|---|---|
| IP | 128.173.243.8 |
| Hostname | h80adf308.dhcp.vt.edu |
| Organization | Virginia Polytechnic Institute and State Univ. |
| Country | United States (Virginia) |
| Open ports | 11434 (Ollama — public) |

Additional VT IPs in Shodan (198.82.9.219, 198.82.11.101, 198.82.13.6) did not respond — likely firewalled or offline.

---

## Model Inventory

| Model | Size |
|---|---|
| `smollm2:135m` | 0.3GB |
| `qwen3:30b` | 18.6GB |
| `qwen:latest` | 2.3GB |
| `qwen2.5:32b` | 19.9GB |
| `llama3.2:latest` | 2.0GB |

---

## Findings

### F1 — Researcher Workstation Publicly Exposed (LOW)

DHCP hostname pattern (`h80adf308.dhcp.vt.edu`) indicates a laptop or desktop on campus DHCP. No cloud proxies, no credential leak. Standard unauthenticated Ollama exposure on a workstation.

### F2 — CVE-2025-63389 Injectable (HIGH)

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
- **Status:** Pending outreach to VT IT Security (vt.edu)
