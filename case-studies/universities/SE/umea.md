# Umeå University — GPU Research Server (gpuhost02)

_NuClide Research · 2026-05-01_

---

## Summary

Umeå University (Sweden) has a named GPU compute server (`gpuhost02.cs.umu.se`) running Ollama with a large reasoning model (qwen3.6:35b) publicly accessible without authentication. Part of the Computer Science department compute cluster.

---

## Infrastructure

| Field | Value |
|---|---|
| IP | 130.239.40.121 |
| rDNS | `gpuhost02.cs.umu.se` |
| Org | Umeå University |
| Department | Computer Science |
| Country | Sweden |
| Open ports | 11434 (Ollama — **public**) |

---

## Models

| Model | Size |
|---|---|
| qwen3.6:35b | 22 GB |
| smollm2:135m | 0 GB |
| llama3.2:3b | 1 GB |

---

## Findings

**F1 — Unauthenticated GPU Research Server (HIGH):** Named GPU host #2 in CS compute cluster. All models injectable via CVE-2025-63389.

---

## Disclosure

- **Discovered:** 2026-05-01
- **Status:** Pending outreach to Umeå University IT
