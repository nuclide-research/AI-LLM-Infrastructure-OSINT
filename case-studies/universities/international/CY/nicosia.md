# University of Nicosia — DeepSeek V4 Pro Cloud Proxy, Unauthenticated Inference

_NuClide Research · 2026-05-03_

---

## Summary

82.116.203.130 (University of Nicosia / Intercollege, Cyprus — CYNET) runs Ollama v0.17.0 with `deepseek-v4-pro:cloud` listed in the model inventory. Cloud inference returned `"ollama cloud is disabled: remote model is unavailable"` at probe time, indicating the cloud backend was disconnected but the model record persists. Two local models (llama3.2:3b, smollm2:135m) remain freely accessible.

---

## Infrastructure

| Field | Value |
|---|---|
| IP | 82.116.203.130 |
| Hostname | — (no rDNS) |
| Organization | University of Nicosia / Intercollege (CYNET — Cyprus Academic Network) |
| Country | Cyprus |
| Ollama version | 0.17.0 |
| Open port | 11434 (public) |

---

## Models

| Model | Notes |
|---|---|
| `deepseek-v4-pro:cloud` | ☁️ Cloud proxy — disabled at probe time (model record present) |
| `llama3.2:3b` | Local 3B |
| `smollm2:135m` | SmolLM |

---

## Findings

### F1 — DeepSeek V4 Pro Cloud Proxy (MEDIUM)

`deepseek-v4-pro:cloud` appears in the model list. At probe time the cloud backend returned `"ollama cloud is disabled: remote model is unavailable"` — the subscription may have lapsed, the account may have been rotated, or the cloud proxy was manually disabled. The model record's presence indicates the operator previously had an active cloud subscription. If the cloud backend is re-enabled, the account takeover vector reactivates without configuration changes.

### F2 — Unauthenticated Inference (HIGH)

Local models `llama3.2:3b` and `smollm2:135m` accessible without authentication. CVE-2025-63389 injectable.

### F3 — CVE-2025-63389 (HIGH)

All models injectable via unauthenticated `/api/create`.

---

## Remediation

```bash
OLLAMA_HOST=127.0.0.1:11434
systemctl restart ollama
```

---

## Disclosure

- **Discovered:** 2026-05-03
- **Status:** Pending outreach to University of Nicosia IT / CYNET
