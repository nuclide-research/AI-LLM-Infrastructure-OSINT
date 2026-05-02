# University of Manitoba — CS Department GPU Server, Deep Research Stack

_NuClide Research · 2026-05-01_

---

## Summary

The Computer Science department at the University of Manitoba (`quail.cs.umanitoba.ca`) is running Ollama with five large local models including DeepSeek-R1:70B, Llama 3.3, and Llama 3:70B — a deep research stack totaling ~156GB of local models, all accessible without authentication.

---

## Infrastructure

| Field | Value |
|---|---|
| IP | 130.179.30.15 |
| rDNS | `quail.cs.umanitoba.ca` |
| Org | University of Manitoba |
| Department | Computer Science |
| Country | Canada — Manitoba |
| Open ports | 11434 (Ollama — **public**) |

---

## Models

| Model | Size |
|---|---|
| llama3.3:latest | 39 GB |
| llama3:70b | 37 GB |
| deepseek-r1:70b | 39 GB |
| qwen2.5-coder:32b | 18 GB |
| smollm2:135m | 0 GB |

Total local compute: ~133 GB across 5 models.

---

## Findings

**F1 — Unauthenticated CS Research Server (HIGH):** Named GPU server in CS department. Research models (DeepSeek-R1, large Llama) and code model (Qwen2.5-Coder) exposed to the public internet.

**F2 — Model Injection (HIGH):** All 5 models injectable via CVE-2025-63389 — attacker can overwrite system prompts, affecting any research workflows using this Ollama instance.

---

## Disclosure

- **Discovered:** 2026-05-01
- **Status:** Pending outreach to UManitoba IT / csirt@canarie.ca (CANARIE)
