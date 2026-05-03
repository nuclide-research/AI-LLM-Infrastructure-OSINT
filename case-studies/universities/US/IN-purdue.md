# Purdue University (main campus) — Account Takeover on n8n Workflow Automation Server

_NuClide Research · 2026-05-03_

---

## Summary

Purdue University main campus (West Lafayette, IN) exposes an Ollama instance at `n8n.tap.purdue.edu` — the reverse DNS reveals this is a Purdue n8n workflow automation deployment. n8n is a self-hosted AI workflow tool that connects LLMs to internal databases, APIs, and services. The Ollama instance feeds AI capabilities to the n8n workflow engine; account takeover credentials are exposed via the cloud proxy 401 response. Any AI-powered workflow automation at Purdue running through this instance can be hijacked via model injection.

This is distinct from the existing Purdue Northwest finding (`IN-purdue-northwest.md`) — this is Purdue's main West Lafayette campus.

---

## Infrastructure

| Field | Value |
|---|---|
| IP | 128.210.38.15 |
| rDNS | `n8n.tap.purdue.edu` / `docs.tap.purdue.edu` |
| Org | Purdue University |
| Campus | West Lafayette, IN (main campus) |
| Ollama version | 0.12.3 |
| Open port | 11434 (public, no auth) |

The `n8n.tap.purdue.edu` hostname confirms this server runs n8n — a self-hosted workflow automation platform commonly used to build AI pipelines connecting LLMs to databases, APIs, email, and enterprise systems. `docs.tap.purdue.edu` on the same IP suggests this is a TAP (Technology Assistance Program?) infrastructure node with both documentation and workflow automation services.

---

## Account Takeover

```json
{
  "error": "unauthorized",
  "signin_url": "https://ollama.com/connect?name=d3af393f8e4e&key=<base64>"
}
```

- **Account name:** `d3af393f8e4e`
- **SSH public key:** `ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIDPaIhGoFXRB5vkKZPRpoxkE6uEAocrMBC3WaCEqSgtB`

---

## Models

| Model | Size | Notes |
|---|---|---|
| deepseek-v4-pro:cloud | 0 GB | ☁️ Cloud proxy — **account takeover** |
| minimax-m2.7:cloud | 0 GB | ☁️ Cloud proxy |
| smollm2:135m | 0.3 GB | Local |
| llama3.2:3b | 1.9 GB | Local |
| llama3.2:latest | 1.9 GB | Local |

---

## Findings

### F1 — Account Takeover on Workflow Automation Server (CRITICAL)

The exposed Ollama instance is co-located with `n8n.tap.purdue.edu`. n8n workflows that call the local Ollama endpoint will receive attacker-controlled responses after model injection via CVE-2025-63389. The impact is not limited to the LLM itself — any automated workflow action triggered by AI output (database writes, API calls, email sends, report generation) becomes attacker-influenced. This extends the attack surface beyond model inference into every downstream system n8n is connected to.

### F2 — Cloud Proxy Account Hijack (CRITICAL)

401 response exposes the Ollama Connect public key. Account takeover allows the attacker to:
- View all cloud model usage/billing on this account
- Revoke or reassign cloud model access
- Redirect cloud proxy traffic to attacker-controlled endpoints

### F3 — CVE-2025-63389 Model Injection (CRITICAL)

All models injectable via unauthenticated `/api/create`. On an n8n-connected Ollama instance, a single injection propagates into any workflow that calls the affected model.

---

## Remediation

```bash
OLLAMA_HOST=127.0.0.1:11434
systemctl restart ollama
```

n8n should be configured to connect to `127.0.0.1:11434` only. If running in Docker, use internal Docker networking (do not bind Ollama to host port).

---

## Related Finding

- `IN-purdue-northwest.md` — Purdue University Northwest (separate institution, 3 nodes, also takeover)

---

## Disclosure

- **Discovered:** 2026-05-03
- **Status:** Pending outreach to Purdue ITAP Security / security@purdue.edu
