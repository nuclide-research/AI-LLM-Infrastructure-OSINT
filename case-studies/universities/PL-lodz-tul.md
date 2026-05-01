# Technical University of Łódź (TUL) — DeepSeek-R1:32B, Cross-Network Custom Model

_NuClide Research · 2026-05-01_

---

## Summary

Technical University of Łódź (Politechnika Łódzka) has an Ollama instance on `xray02.p.lodz.pl` with 3 models including a 20GB DeepSeek-R1 and `lukashabtoch/plutotext-r3-emotional:latest` — the same custom emotional-roleplay model observed independently at CEFET/RJ in Brazil and other nodes, indicating cross-institutional propagation of an obscure community fine-tune.

---

## Infrastructure

| Field | Value |
|---|---|
| IP | 212.51.215.102 |
| Hostname | xray02.p.lodz.pl |
| Organization | Technical University of Łódź (Politechnika Łódzka) |
| Country | Poland |
| Open ports | 11434 (Ollama — public) |

---

## Model Inventory

| Model | Size | Notes |
|---|---|---|
| `deepseek-r1:32b` | 19.9GB | 32.8B params, Qwen2 family |
| `lukashabtoch/plutotext-r3-emotional:latest` | 4.9GB | 8.0B params, emotional roleplay fine-tune |
| `llama3.2:3b` | 2.0GB | — |

---

## Findings

### F1 — Cross-Network Model Propagation (MEDIUM)

`lukashabtoch/plutotext-r3-emotional:latest` is a low-citation community fine-tune for emotional roleplay. This exact model appears on at least two geographically unrelated institutions (Łódź, Poland and CEFET/RJ, Brazil) suggesting it propagates through shared Hugging Face download patterns or operator-to-operator social sharing. Uncommon model identifiers like this can serve as Shodan/HTTP banner search correlators for cross-network attribution.

### F2 — Unauthenticated Inference on Research Server (HIGH)

`deepseek-r1:32b` (19.9GB, 32.8B params) is accessible without authentication. The hostname `xray02` suggests an X-ray / radiological research compute node, making the exposure pattern consistent with a research GPU being repurposed for LLM workloads without access controls.

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
- **Status:** Pending outreach to TUL IT (lodz.pl)
