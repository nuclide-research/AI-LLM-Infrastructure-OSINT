# TANet Abliterated Model Cluster — `gemma4-crack-fixed`, Multiple Safety-Bypassed Models

_NuClide Research · 2026-05-03_

---

## Summary

A Taiwan Academic Network node at 120.126.16.144 (AS1659 TANet, Taipei, no rDNS) runs a concentrated cluster of abliterated, uncensored, and jailbreak-labeled models on Ollama v0.20.3. The most notable model is `gemma4-crack-fixed:latest` — a name indicating a modified Gemma 4 with safety restrictions "cracked" and then patched. Two additional abliterated models from HuggingFace, a Dolphin uncensored model, and `Yinr/qwen2.5-agi:32b` (AGI-branded) complete the stack. No cloud proxy, no hostname, no rDNS — the operator may be actively avoiding identification.

---

## Infrastructure

| Field | Value |
|---|---|
| IP | 120.126.16.144 |
| Hostname | — (no rDNS) |
| Org | AS1659 Taiwan Academic Network (TANet) — Taipei |
| Institution | Unknown TANet institution |
| Ollama version | 0.20.3 |
| Open port | 11434 (public) |

---

## Model Inventory

| Model | Notes |
|---|---|
| `gemma4-crack-fixed:latest` | **Custom — "crack-fixed" Gemma 4** (safety bypassed, then modified) |
| `hf.co/paperscarecrow/Gemma-4-31B-it-abliterated:Q4_K_M` | Gemma 4 31B abliterated — safety fine-tuning removed |
| `hf.co/mradermacher/Mistral-Small-24B-Instruct-2501-Abliterated-GGUF:latest` | Mistral Small 24B abliterated |
| `dolphin-llama3:latest` | Dolphin (uncensored Llama 3) |
| `Yinr/qwen2.5-agi:32b` | Qwen2.5 32B branded "AGI" — no published details |
| `gemma4:26b` | Base Gemma 4 26B |
| `llava:latest` | LLaVA vision-language |

---

## Findings

### F1 — `gemma4-crack-fixed`: Custom Safety-Bypassed Model (CRITICAL)

The name `gemma4-crack-fixed` is unique in this sweep. "Crack" suggests the model's safety alignment was deliberately broken; "fixed" may indicate the operator modified it further to prevent detection or re-restriction. This is a non-standard model not published on Ollama Hub, created and named by the operator. On a university network node, it is publicly accessible without authentication.

### F2 — Concentrated Abliterated + Uncensored Cluster (HIGH)

4 of 7 models have safety alignment removed (abliterated × 2, Dolphin, crack-fixed). This is the highest density of safety-bypassed models on a single TANet node in the sweep. The `Yinr/qwen2.5-agi:32b` branding suggests the operator is specifically collecting models positioned as "uncensored" or "AGI-complete."

### F3 — No Hostname / No rDNS (MEDIUM)

Unlike most TANet nodes which carry hostnames identifying their department (ntu.edu.tw, fju.edu.tw, etc.), this node has neither rDNS nor a Shodan hostname. The 120.126.x.x block is in the TANet allocation but the specific institution is unknown from passive data.

### F4 — CVE-2025-63389 (CRITICAL)

All 7 models injectable via unauthenticated `/api/create`.

---

## TANet Context

This node is part of the broader TANet exposure documented in `tanet.md`, `ncku.md`, `ntu-gpu.md`, and `fju-medph.md`. The concentrated abliterated model cluster is an outlier relative to other TANet nodes, which primarily run research and domain-specific models.

---

## Remediation

```bash
OLLAMA_HOST=127.0.0.1:11434
systemctl restart ollama
```

Report to TWCERT/CC (cert@twcert.org.tw) for investigation of the specific TANet tenant.

---

## Disclosure

- **Discovered:** 2026-05-03
- **Status:** Pending outreach to TWCERT (cert@twcert.org.tw) — institution identity unknown
