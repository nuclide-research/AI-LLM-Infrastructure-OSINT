# Monash University — 404.5GB DeepSeek V3.1, Kimi + MiniMax Cloud Proxies

_NuClide Research · 2026-05-01_

---

## Summary

Monash University (Melbourne, Australia) has an Ollama instance at `vm-118-138-233-225.erc.monash.edu.au` with 8 models totalling over 510GB of local inference including a full **DeepSeek V3.1 671B** (404.5GB) — tied with KRENA for largest local deployment in this sweep. Two cloud proxies are present.

---

## Infrastructure

| Field | Value |
|---|---|
| IP | 118.138.233.225 |
| Hostname | vm-118-138-233-225.erc.monash.edu.au |
| Organization | Monash University |
| Network | Monash ERC (Education and Research Cluster — 118.138.0.0/16) |
| Country | Australia |
| Open ports | 11434 (Ollama — public) |

Two additional Monash nodes on the same subnet (118.138.243.239, 118.138.243.34) host smaller stacks (deepseek-r1:latest, qwen2.5, llama3 — 3 models each).

---

## Model Inventory (Primary Node)

| Model | Size | Notes |
|---|---|---|
| `deepseek-v3.1:latest` | **404.5GB** | **671.0B params**, DeepSeek2 family — largest model in sweep |
| `qwen3-coder-next:latest` | 51.7GB | — |
| `nemotron-cascade-2:latest` | 24.3GB | NVIDIA Nemotron Cascade 2 |
| `gpt-oss-safeguard:latest` | 13.8GB | gpt-oss 20.9B — `safeguard` variant, no system prompt set |
| `kimi-k2.5:cloud` | 0GB | Cloud proxy |
| `minimax-m2.7:cloud` | 0GB | Cloud proxy |
| `gemma4:latest` | 9.6GB | — |
| `qwen3.5:latest` | 6.6GB | — |

**Total primary node:** ~510GB local + 2 cloud proxies

---

## Findings

### F1 — 404.5GB DeepSeek V3.1 671B Publicly Accessible (HIGH)

`deepseek-v3.1:latest` is verified as 671.0B params (DeepSeek2 family, family confirmed via `/api/show`). At 404.5GB, this requires multi-GPU infrastructure to serve (typically 8×A100/H100 or equivalent). Any internet actor can run uncapped inference against this model at Monash's compute cost.

This is co-ranked with KRENA's GLM-5.1 as the largest local model accessible in the sweep.

### F2 — Cloud Proxy Portfolio (HIGH)

`kimi-k2.5:cloud` and `minimax-m2.7:cloud` are present. Both return `{"error":"unauthorized"}` with no credential leak in response body. No quota drain confirmed.

### F3 — gpt-oss-safeguard Variant (MEDIUM)

`gpt-oss-safeguard:latest` (13.8GB, 20.9B params) is a named variant of the gpt-oss model with no system prompt set. The `safeguard` tag suggests it was intended to include content filtering, but the system prompt slot is empty — the safeguard was not configured.

### F4 — CVE-2025-63389 Injectable (HIGH)

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
- **Status:** Pending outreach to Monash IT Security (monash.edu.au)
