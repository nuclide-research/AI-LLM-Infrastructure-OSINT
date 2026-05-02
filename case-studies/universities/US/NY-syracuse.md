# Syracuse University — IST R640 Server, Free-Tier Cloud Proxy on Port 12345

_NuClide Research · 2026-05-01_

---

## Summary

A Dell PowerEdge R640 server in Syracuse University's School of Information Studies (`ist-r640-mafudge.syr.edu`) is running Ollama on non-standard port 12345 with `gemma4:31b-cloud` returning **200 OK** without credentials. Five cloud proxy subscriptions total.

---

## Infrastructure

| Field | Value |
|---|---|
| IP | 128.230.38.78 |
| rDNS | `ist-r640-mafudge.syr.edu` |
| Org | Syracuse University |
| Department | Information Studies & Technology |
| Country | US — New York |
| Open ports | **12345** (Ollama non-standard port — **public**) |

---

## Models

| Model | Size | Type | 200 OK? |
|---|---|---|---|
| gemma4:31b-cloud | 0 GB | ☁️ Cloud proxy | **YES — 10 tokens** |
| minimax-m2.7:cloud | 0 GB | ☁️ Cloud proxy | — |
| glm-4.7:cloud | 0 GB | ☁️ Cloud proxy | — |
| glm-5.1:cloud | 0 GB | ☁️ Cloud proxy | — |
| kimi-k2.6:cloud | 0 GB | ☁️ Cloud proxy | — |
| gemma4:31b | 19 GB | Local | — |
| smollm2:latest | 0 GB | Local | — |

---

## Findings

### F1 — Free-Tier Cloud Proxy 200 OK on Non-Standard Port (CRITICAL)

`gemma4:31b-cloud` returns full inference without credentials on port 12345:

```bash
curl -X POST http://128.230.38.78:12345/api/chat \
  -d '{"model":"gemma4:31b-cloud","messages":[{"role":"user","content":"hi"}],"stream":false}'
# 200 OK — "Hello! How can I help you today?"
```

### F2 — Non-Standard Port Exposes Intentional or Misconfigured Deployment (HIGH)

Ollama running on port 12345 (not default 11434) may indicate intentional non-standard deployment or a misconfigured service that bypasses default port-filtering rules.

### F3 — Model Injection (HIGH)

All models injectable via CVE-2025-63389.

---

## Disclosure

- **Discovered:** 2026-05-01
- **Status:** Pending outreach to Syracuse University IT Security: security@syr.edu
