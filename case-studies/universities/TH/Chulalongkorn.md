# Chulalongkorn University — Three Cloud Proxies + Credential Leak (Kimi K2.6, DeepSeek, Qwen)

_NuClide Research · 2026-05-01_

---

## Summary

Chulalongkorn University (Thailand, ranked ~1 in Southeast Asia) server with 12 Ollama models including three cloud proxy subscriptions: DeepSeek v4 Pro, Kimi K2.6 (Moonshot AI), and Qwen3-Coder-Next. All three 401 responses leak the same Ollama Connect credentials. Raw Ollama port publicly accessible, no authentication.

---

## Infrastructure

| Field | Value |
|---|---|
| IP | 161.200.94.244 |
| Org | Chulalongkorn University |
| Country | Thailand |
| Open ports | 11434 (Ollama — **public**) |

---

## Cloud Proxies + Credential Leak

All three cloud proxy models return 401 with the same credentials:

```json
{
  "error": "unauthorized",
  "signin_url": "https://ollama.com/connect?name=llm&key=<base64>"
}
```

- **Username:** `llm` (generic service account)
- **SSH pubkey:** `ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIF62M2w3KpDWb90LH8DRhehBjI8Up5i3scd349g6OUdH`

| Cloud Proxy | Provider | Status |
|-------------|----------|--------|
| deepseek-v4-pro:cloud | DeepSeek API | 401 + cred leak |
| kimi-k2.6:cloud | Moonshot AI (Kimi) | 401 + cred leak |
| qwen3-coder-next:cloud | Alibaba Qwen | 401 + cred leak |

`kimi-k2.6` is Moonshot AI's frontier model. All three subscriptions share one Ollama Connect account (`llm`).

---

## Findings

### F1 — Unauthenticated Ollama API (CRITICAL)

Port 11434 publicly accessible. 12 models enumerable and injectable without credentials.

### F2 — Credential Leak via Cloud Proxy (HIGH)

Same Ollama Connect credentials leaked on all three cloud proxy 401 responses. Any actor probing port 11434 receives the operator's SSH public key and username.

### F3 — Model Injection (CRITICAL)

CVE-2025-63389 applies. All 12 models injectable. If used for student/research workflows, injection redirects outputs under attacker-controlled system prompts.

---

## Remediation

```bash
OLLAMA_HOST=127.0.0.1:11434
systemctl restart ollama
```

---

## Disclosure

- **Discovered:** 2026-05-01
- **Status:** Pending outreach to Chulalongkorn IT Security
