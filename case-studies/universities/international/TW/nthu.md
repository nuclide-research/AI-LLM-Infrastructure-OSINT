# National Tsing Hua University — TAIDE-NPC Model, Qwen3.6:35b

_NuClide Research · 2026-05-03_

---

## Summary

National Tsing Hua University (清華大學, NTHU) node `sd197130.shin34.ab.nthu.edu.tw` (140.114.197.130) runs Ollama v0.22.0 (current release) with two models — `qwen3.6:35b` and `taide-npc:latest`. The `taide-npc` model is a notable finding: a variant of Taiwan's national TAIDE AI model designated for NPC (Non-Player Character) applications, suggesting AI character/agent research using the national language model as a base.

---

## Infrastructure

| Field | Value |
|---|---|
| IP | 140.114.197.130 |
| Hostname | sd197130.shin34.ab.nthu.edu.tw |
| Organization | National Tsing Hua University |
| Network | Taiwan MOE TANet (140.114.0.0/16) |
| Ollama version | 0.22.0 |
| Open port | 11434 (public, no auth) |

---

## Models

| Model | Notes |
|---|---|
| `qwen3.6:35b` | Qwen3.6 35B general model |
| `taide-npc:latest` | **TAIDE NPC variant** — Taiwan national AI for character/agent applications |

---

## Findings

### F1 — TAIDE-NPC: National AI as Character Model (HIGH)

`taide-npc:latest` is a TAIDE-family model (Taiwan AI Dialogue Engine, NCHC-funded national project) configured or fine-tuned for NPC (Non-Player Character) scenarios. This indicates NTHU research applying Taiwan's national bilingual LLM to interactive agent/character AI — likely game AI, educational simulation, or dialogue system research.

The model's system prompt or fine-tune is publicly accessible and injectable via CVE-2025-63389. An attacker can overwrite the NPC persona configuration.

### F2 — v0.22.0 Current Release (MEDIUM)

NTHU runs the current Ollama release — but CVE-2025-63389 applies to all versions (no patch exists).

### F3 — CVE-2025-63389 (CRITICAL)

Both models injectable via unauthenticated `/api/create`.

---

## Remediation

```bash
OLLAMA_HOST=127.0.0.1:11434
systemctl restart ollama
```

---

## Disclosure

- **Discovered:** 2026-05-03
- **Status:** Pending outreach to NTHU IT / TWCERT (cert@twcert.org.tw)
