# UC Berkeley — Residential Hall Machine, qwen2.5:32b Public

_NuClide Research · 2026-05-03_

---

## Summary

`lal-99-178.reshall.berkeley.edu` (169.229.99.178), a machine on UC Berkeley's residential hall network, runs Ollama v0.11.10 with `qwen2.5:32b` (19GB) exposed on port 11434. The `reshall.berkeley.edu` subdomain indicates student on-campus housing infrastructure. A student machine in a residential dorm running a 19GB model publicly accessible from the internet.

---

## Infrastructure

| Field | Value |
|---|---|
| IP | 169.229.99.178 |
| Hostname | lal-99-178.reshall.berkeley.edu |
| Organization | University of California at Berkeley |
| Network | AS25 UC Berkeley |
| Location | Residential Hall, UC Berkeley campus |
| Ollama version | 0.11.10 |
| Open port | 11434 (public) |

---

## Models

| Model | Size | Notes |
|---|---|---|
| `qwen2.5:32b` | 19GB | Qwen2.5 32B |

---

## Findings

### F1 — Residential Hall Machine with Internet-Exposed Inference (HIGH)

The `reshall.berkeley.edu` subdomain places this machine in student-facing residential hall infrastructure — likely a personal workstation or lab machine belonging to a graduate student or researcher. Running `qwen2.5:32b` (19GB weights) indicates significant local hardware (high-VRAM GPU).

Berkeley's residential network should not expose port 11434 to the public internet. This represents a misconfiguration at either the network layer (no egress/ingress filtering on student housing ports) or the host level (Ollama bound to 0.0.0.0 instead of loopback). The `lal` prefix is unresolved — could be a lab allocation within the residential network.

### F2 — v0.11.10: ~1.5-Year-Old Ollama (HIGH)

v0.11.10 dates to approximately late 2024. CVE-2025-63389 injectable.

### F3 — CVE-2025-63389 (HIGH)

`qwen2.5:32b` injectable via unauthenticated `/api/create`.

---

## Remediation

```bash
OLLAMA_HOST=127.0.0.1:11434
systemctl restart ollama
```

Berkeley network team should audit residential hall egress for port 11434 exposure.

---

## Disclosure

- **Discovered:** 2026-05-03
- **Status:** Pending outreach to Berkeley IT Security (security@berkeley.edu)
