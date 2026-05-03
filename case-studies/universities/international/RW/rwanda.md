# University of Rwanda — Qwen3.5 + Qwen3.6 27B, College of Education Campus

_NuClide Research · 2026-05-03_

---

## Summary

154.68.72.29 (University of Rwanda, College of Education Campus, Kigali) runs Ollama with `qwen3.5:27b` and `qwen3.6:27b` accessible without authentication. This is the first Sub-Saharan Africa (excluding Kenya) university finding in the sweep.

---

## Infrastructure

| Field | Value |
|---|---|
| IP | 154.68.72.29 |
| Hostname | — (no rDNS) |
| Organization | University of Rwanda — College of Education (CoE) |
| Network | RWED01-UR-KIE-01 (University of Rwanda, Rwanda) |
| Country | Rwanda |
| Ollama version | — |
| Open port | 11434 (public) |

---

## Models

| Model | Size | Notes |
|---|---|---|
| `qwen3.5:27b` | 17GB | Qwen3.5 27B |
| `qwen3.6:27b` | 17GB | Qwen3.6 27B |

---

## Findings

### F1 — Unauthenticated Inference (MEDIUM)

Both 27B models accessible without authentication. The College of Education campus context suggests academic staff or student use for education-related NLP or coursework.

### F2 — CVE-2025-63389 (HIGH)

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
- **Status:** Pending outreach to University of Rwanda IT
