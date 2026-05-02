# UC Davis — Large Local Models + Claude 4.6 Opus-Distilled

_NuClide Research · 2026-05-01_

---

## Summary

University of California, Davis has an Ollama instance with `Qwen3-Coder-Next` (48GB), `qwen3.5:122b-a10b` (75GB), and — notably — `moophlo/Qwen3.5-27B-Claude-4.6-Opus-Reasoning-Distilled-GGUF:latest`, a model distilled from Claude 4.6 Opus, all accessible without authentication.

---

## Infrastructure

| Field | Value |
|---|---|
| IP | 128.120.246.177 |
| rDNS | — |
| Org | University of California, Davis |
| Country | US — California |
| Open ports | 11434 (Ollama — **public**) |

---

## Models

| Model | Size | Notes |
|---|---|---|
| Qwen3-Coder-Next:latest | 48 GB | Large code model |
| qwen3.5:122b-a10b | 75 GB | 122B MoE reasoning |
| moophlo/Qwen3.5-27B-Claude-4.6-Opus-Reasoning-Distilled-GGUF:latest | 15 GB | **Claude 4.6 Opus knowledge distillation** |
| qwen3.5:latest | 6 GB | Local |

---

## Findings

**F1 — Claude-Distilled Model Exposed (HIGH):** `Qwen3.5-27B-Claude-4.6-Opus-Reasoning-Distilled` is a model trained on Claude 4.6 Opus outputs. Accessible to any internet caller — this represents a research artifact with embedded Anthropic model behaviors.

**F2 — 75GB MoE Model Accessible (HIGH):** `qwen3.5:122b-a10b` (75GB) is a large mixture-of-experts reasoning model. Significant compute resource exposed.

**F3 — Model Injection (HIGH):** All 4 models injectable via CVE-2025-63389.

---

## Disclosure

- **Discovered:** 2026-05-01
- **Status:** Pending outreach to UC Davis IT Security
