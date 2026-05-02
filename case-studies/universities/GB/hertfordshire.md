# University of Hertfordshire — RobotHouse Dev Server, gpt-oss Cloud Proxy 200 OK

_NuClide Research · 2026-05-01_

---

## Summary

A development server at the University of Hertfordshire's RobotHouse facility (`robothouse-dev.herts.ac.uk`) is running Ollama with `gpt-oss:latest` cloud proxy returning **200 OK** without credentials — free-tier cloud quota consumed at operator expense by any internet caller. 103 tokens consumed during research confirmation.

---

## Infrastructure

| Field | Value |
|---|---|
| IP | 147.197.191.230 |
| rDNS | `robothouse-dev.herts.ac.uk` |
| Org | University of Hertfordshire |
| Facility | RobotHouse (robotics research lab) |
| Country | United Kingdom |
| Open ports | 11434 (Ollama — **public**) |

---

## Models

| Model | Size | Type | 200 OK? |
|---|---|---|---|
| gpt-oss:latest | 12 GB | ☁️ Cloud proxy | **YES — 34 tokens** |
| gemma4:latest | 8 GB | Local | — |

---

## Findings

### F1 — Free-Tier Cloud Proxy 200 OK (CRITICAL)

`gpt-oss:latest` returns full inference without authentication. 103 tokens total consumed (69 prompt + 34 output) during research confirmation:

```bash
curl -X POST http://147.197.191.230:11434/api/chat \
  -d '{"model":"gpt-oss:latest","messages":[{"role":"user","content":"say hi"}],"stream":false}'
# 200 OK - "Hi! 👋" — operator quota consumed
```

### F2 — Research Lab Dev Server (HIGH)

The `robothouse-dev.herts.ac.uk` hostname indicates this is a development/staging server in the RobotHouse robotics research facility. LLM API abuse or injection could affect robot-planning pipelines or research workflows connected to this Ollama instance.

### F3 — Model Injection (HIGH)

Both models injectable via CVE-2025-63389.

---

## Disclosure

- **Discovered:** 2026-05-01
- **Status:** Pending outreach to UH IT Security / JISC CSIRT
