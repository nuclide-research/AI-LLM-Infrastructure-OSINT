# Malaysia Ministry of Education (EMISC) — Unauthenticated Ollama Node

_NuClide Research · 2026-05-02_

---

## Summary

Malaysia's Ministry of Education Education Management Information System Centre (EMISC) exposes one Ollama node (203.172.144.85) with two models. EMISC manages the national school and education data infrastructure for Malaysia.

---

## Infrastructure

| Field | Value |
|---|---|
| IP | 203.172.144.85 |
| Org | Ministry of Education - EMISC |
| Country | Malaysia |
| Ollama version | 0.9.6 |
| Open port | 11434 (public) |

---

## Models

| Model | Notes |
|---|---|
| (2 models) | No system prompts recovered |

---

## Findings

### F1 — Government Education IT Infrastructure Exposed (HIGH)

EMISC is the IT arm of Malaysia's Ministry of Education, responsible for national school data systems. An Ollama node on this network — accessible from the public internet without authentication — represents a misconfigured deployment on government education infrastructure.

### F2 — Model Injection (CRITICAL)

CVE-2025-63389 applies. Version 0.9.6 confirms no updates since early 2024.

---

## Remediation

```bash
OLLAMA_HOST=127.0.0.1:11434
systemctl restart ollama
```

---

## Disclosure

- **Discovered:** 2026-05-02
- **Status:** Pending outreach to Malaysia MoE EMISC
