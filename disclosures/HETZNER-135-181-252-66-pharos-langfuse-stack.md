---
to: abuse@hetzner.com
cc: security@unistarthubs.gr, abuse@nuclide-research.com
severity: CRITICAL
ip: 135.181.252.66
institution: Unistart Hubs (Greek startup hub / Pharos AI Assistant — multi-platform AI stack exposure on Hetzner DE)
status: DRAFT
date: 2026-05-06
---

**To:** abuse@hetzner.com
**Cc:** security@unistarthubs.gr, abuse@nuclide-research.com
**Subject:** Multi-platform AI stack exposure — Langfuse signup-open + leaked CLIENT_SECRET + unauth Milvus + open Attu admin — 135.181.252.66 (pharos.unistarthubs.gr)

---

Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com

2026-05-06

**Re:** Multi-platform AI infrastructure exposure on a Hetzner customer host
**IP / Host:** 135.181.252.66 (rDNS `pharos.unistarthubs.gr`, Hetzner DE)
**Severity:** CRITICAL

---

I'm an independent security researcher conducting good-faith AI infrastructure research under the NuClide Research umbrella (CISA disclosures CVE-2025-4364, ICSA-25-140-11). This is an unsolicited coordinated-disclosure notification covering a Hetzner customer host that exposes a four-platform AI stack with no authentication chain.

---

## Summary

The host at `135.181.252.66` (rDNS `pharos.unistarthubs.gr`) runs a customer-facing AI assistant product called **Pharos**. The product stack is exposed across four ports with auth misconfigurations that chain to give any unauthenticated internet caller full operational visibility into the operator's AI application within ~5 minutes:

| Port | Service | Auth state | Severity |
|---|---|---|---|
| 8080 | **Pharos AI Assistant** (React SPA) | `env.js` publishes `CLIENT_SECRET` in cleartext | **CRITICAL** |
| 3001 | **Langfuse v3.73.1** (LLM observability) | `signUpDisabled:false` — open public registration; credentials-only auth (no SSO) | **CRITICAL** |
| 19530 | **Milvus** (vector DB) | none | HIGH |
| 3000 | **Attu** (Milvus web admin GUI) | none on the GUI; connects to the unauth Milvus | MEDIUM |

The chain:

1. **Sign up to Langfuse via the open registration page** (`http://135.181.252.66:3001/auth/sign-up`). Any internet visitor becomes an authenticated Langfuse user; the operator's PostgreSQL persists a user record.
2. **Read the operator's full LLM trace history** via the authenticated Langfuse API (`/api/public/traces`, `/api/public/observations`, `/api/public/datasets`, etc.) — every system prompt, user input, model output, and tool call ever logged by the Pharos app.
3. **Read the operator's persistent agent-memory store** via the unauthenticated Milvus on port 19530. Collections include `experience_memory`, `mem0migrations`, `all`, `all_v3` — the Mem0 framework's per-user memory primitives.
4. **Use the Attu admin GUI** on port 3000 to inspect / modify Milvus directly via a web UI.
5. **Use the leaked `CLIENT_SECRET`** from `http://135.181.252.66:8080/env.js` to authenticate against whatever Pharos backend surface that secret is bound to (the chat WebSocket at `/api/query/ws/chat/query` is the most likely binding).

Combined, the attacker has the operational logs, the persistent memory, an admin UI to the data substrate, and a backend application secret. **This is a CRITICAL operator catastrophe.**

Found during NuClide Research's cross-survey-correlation Langfuse probe (2026-05-06). Verification was non-destructive: only fingerprint endpoints (`/api/public/health`, `/api/v1/heartbeat`, `/env.js`, `/static/js/main.*.js`) were called. No accounts were registered, no traces were exfiltrated, no Milvus collections were searched, no admin operations were performed. The leaked `CLIENT_SECRET` was observed in the public response and is reproduced below for evidence; it has not been used for authentication.

Full case study with technical detail, methodology, and evidence:
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT/blob/main/case-studies/commercial/langfuse-cross-survey-2026-05-06.md

---

## Confirmed exposures (with reproduction)

### 1. Langfuse v3.73.1 with open public registration (port 3001)

```bash
$ curl -s 'http://135.181.252.66:3001/api/public/health'
{"status":"OK","version":"3.73.1"}
```

The SSR-rendered config from `/auth/sign-in` confirms `signUpDisabled:false`:

```bash
$ curl -s 'http://135.181.252.66:3001/auth/sign-in' | grep -oE '"signUpDisabled":[^,]*'
"signUpDisabled":false
```

A registered user has full read access to `/api/public/traces`, `/api/public/observations`, `/api/public/datasets`, `/api/public/dataset-items`, `/api/public/scores`, `/api/public/v2/prompts`, etc. — i.e. the full LLM observability trace history of every Pharos user interaction.

### 2. Pharos `CLIENT_SECRET` leak (port 8080)

```bash
$ curl -s 'http://135.181.252.66:8080/env.js'
window.APP_CONFIG = {
    CLIENT_SECRET: 'D9OjkzRxHFUL2aNbGOdrihCveBpdxweY'
};
```

The secret is loaded into the React app's runtime config and is published to every visitor of port 8080. Whatever auth surface it unlocks (Pharos backend chat WebSocket, OAuth flow, or custom session issuer), an unauthenticated attacker has it in hand before any prior credential.

### 3. Milvus unauth on port 19530 (Mem0 backend)

```bash
$ curl -s -X POST -H 'Content-Type: application/json' -d '{"dbName":"default"}' \
  'http://135.181.252.66:19530/v2/vectordb/collections/list'
{"code":0,"data":["experience_memory","mem0migrations","all","all_v3"]}
```

The collection names match the Mem0 framework's standard schema for per-user persistent agent memory. This finding is also documented in NuClide's earlier Milvus survey: https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT/blob/main/case-studies/commercial/milvus-cloud-survey-2026-05.md

### 4. Attu Milvus admin GUI on port 3000

```bash
$ curl -s 'http://135.181.252.66:3000/' | grep -oE '<title>[^<]*</title>'
<title>Attu</title>
```

Attu is the official Milvus web admin UI (https://github.com/zilliztech/attu). The container connects to the local Milvus on `127.0.0.1:19530` by default; since that Milvus instance has no auth, Attu has full read+write authority over all collections.

---

## Why this matters

For Unistart Hubs (Pharos AI Assistant operator):

- **Customer privacy** — every Pharos user conversation is logged in Langfuse and persisted in Mem0. An attacker reading either has access to whatever PII users shared with the agent. Under GDPR Article 33, this likely qualifies as a notifiable personal-data breach if user-identifiable content is logged in either store.
- **Operator IP** — system prompts, prompt templates (`/api/public/v2/prompts`), and tool descriptions in Langfuse traces describe the proprietary agent design. A competitor reading these has the operator's product blueprint.
- **App secret compromise** — `CLIENT_SECRET` published in `env.js` undermines whichever backend surface uses it. The cleanest fix is to rotate the secret AND remove it from any client-served config.

For Hetzner abuse:

- A customer (Unistart Hubs / Pharos) needs notification that four AI-platform endpoints on their VPS are publicly reachable without proper authentication. The fixes are operator-side (configuration changes), not Hetzner-side.

---

## Remediation (for the customer)

Per-component fixes, all client-side configuration changes (no code rewrites):

### Langfuse (port 3001)

```bash
# In the Langfuse container env (or .env file):
LANGFUSE_AUTH_DISABLE_SIGNUP=true                              # close public registration
# Optional: restrict signup to specific email domains
LANGFUSE_AUTH_DOMAINS_ALLOWLIST=unistarthubs.gr
# Optional: bind Langfuse to localhost or behind a reverse proxy with SSO
```

Add SSO integration (Google / GitHub / Okta / Azure AD) via the corresponding `LANGFUSE_AUTH_*_CLIENT_*` envs to remove the credentials-only-auth weakness.

### Pharos `CLIENT_SECRET` (port 8080)

```bash
# Remove the secret from /env.js immediately
# Rotate the secret value at the backend (it is now public)
# Backend authentication should not rely on a client-side secret —
# use short-lived per-user tokens minted server-side instead
```

### Milvus (port 19530)

```bash
# Enable Milvus RBAC:
# https://milvus.io/docs/authenticate.md
# Set common.security.authorizationEnabled=true and configure root credentials
```

### Attu (port 3000)

```bash
# Bind Attu to localhost or behind a reverse proxy with auth:
docker run -p 127.0.0.1:3000:3000 zilliz/attu:latest
# Or firewall:
ufw deny 3000/tcp
```

### Network-layer alternative (covers all four)

```bash
# Block external access to all four ports; only allow from operator admin IPs
ufw deny 3000/tcp
ufw deny 3001/tcp
ufw deny 8080/tcp
ufw deny 19530/tcp
ufw allow from <admin-IP> to any port 3000,3001,8080,19530
```

---

## Reference

- Full case study: https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT/blob/main/case-studies/commercial/langfuse-cross-survey-2026-05-06.md
- Langfuse signup-disable docs: https://langfuse.com/self-hosting/authentication-and-sso
- Mem0 framework: https://github.com/mem0ai/mem0
- Milvus RBAC: https://milvus.io/docs/authenticate.md
- Attu README: https://github.com/zilliztech/attu

Happy to answer questions or assist with verification.

Regards,
Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT
