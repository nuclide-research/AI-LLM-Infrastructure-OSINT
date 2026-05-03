# University of Indonesia — Unauthenticated Ollama Node

_NuClide Research · 2026-05-03_

---

## Summary

The University of Indonesia (Universitas Indonesia, UI) exposes one Ollama node at 152.118.31.61 (Depok, West Java, AS3382). The instance runs an ancient Ollama build (v0.5.4-dirty) and hosts llama3.2:3b. Open WebUI v0.5.4 is deployed on port 3000 with authentication enabled, but the raw Ollama API on port 11434 is fully unprotected — the WebUI auth provides no barrier to direct API access.

CVE-2025-63389 confirmed: `/api/create` successfully accepts unauthenticated system prompt injection across the loaded model.

---

## Infrastructure

| Field | Value |
|---|---|
| IP | 152.118.31.61 |
| ASN / Org | AS3382 University of Indonesia |
| City | Depok, West Java, ID |
| Ollama version | 0.5.4-dirty (very old; pre-0.6.0) |
| Open WebUI version | 0.5.4 |
| Open WebUI auth | Enabled (signup disabled, login form enabled) |
| Open port | 11434/tcp (public, no auth) |
| WebUI port | 3000/tcp (public, auth required) |

---

## Models

| Model | Family | Size | Quantization |
|---|---|---|---|
| llama3.2:3b | llama | 2.0 GB | Q4_K_M |

Model was last modified 2026-03-28 — active and recently used.

---

## Findings

### F1 — Unauthenticated Ollama API on Public Internet (HIGH)

Port 11434 is bound to 0.0.0.0 without authentication. Any actor can enumerate models, run inference, and inject system prompts via the raw Ollama API. Open WebUI auth on port 3000 does not protect the underlying API port — operators likely believe auth on port 3000 is sufficient.

### F2 — Model Injection via CVE-2025-63389 (CRITICAL)

Unauthenticated `/api/create` accepts model creation with arbitrary system prompt overrides. Confirmed: a POST to `/api/create` with a modified modelfile successfully created a new model derived from llama3.2:3b with attacker-supplied system instructions. Any user of this instance receiving inference via llama3.2:3b can be served attacker-controlled output after injection.

**No patch exists as of this disclosure.** All Ollama versions are affected.

### F3 — Outdated Ollama Build (MEDIUM)

Version 0.5.4-dirty is a modified pre-release build from early 2024. The `-dirty` suffix indicates local patches were applied outside the official release pipeline. Any security improvements from the 40+ subsequent Ollama releases are absent.

---

## Remediation

Bind Ollama to loopback only:

```bash
OLLAMA_HOST=127.0.0.1:11434
systemctl restart ollama
```

If using Docker:
```bash
docker run -p 127.0.0.1:11434:11434 ollama/ollama
```

---

## References

- **CVE-2025-63389** — Unauthenticated `/api/create` endpoint allows system prompt injection on any loaded model. No authentication, no patch.
- Full sweep context: [OVERVIEW.md](../../OVERVIEW.md)
