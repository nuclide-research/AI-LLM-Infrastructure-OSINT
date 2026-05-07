# City of Cartersville, GA: Local Government Ollama + Cloud Proxy Credential Leak

_NuClide Research · 2026-05-01_

---

## Summary

City of Cartersville, Georgia municipal server running Ollama on Windows with one active cloud proxy subscription (DeepSeek v4 Pro). Raw Ollama port publicly accessible, no authentication. Cloud proxy 401 response leaks Ollama Connect username (Windows machine hostname) and SSH public key. Local government AI infrastructure exposed to model injection and quota drain.

---

## Infrastructure

| Field | Value |
|---|---|
| IP | 104.36.136.143 |
| Domain | fizziemail.0054086.xyz (Shodan hostname) |
| Org | City of Cartersville |
| State | Georgia, USA |
| OS | **Windows** (hostname pattern: `WIN-QAHP18EJH8I`) |
| Open ports | 11434 (Ollama, **public**) |

---

## Models

| Model | Size | Type |
|---|---|---|
| deepseek-v4-pro:cloud | 0 GB | ☁️ Cloud proxy, DeepSeek API |
| gemma3:12b | 7 GB | Local |
| gpt-oss:20b | 12 GB | Local |
| smollm2:135m | 0 GB | Local |

---

## Findings

### F1: Unauthenticated Ollama API (CRITICAL)

Port 11434 bound to 0.0.0.0 on a Windows machine at municipal government. No auth, no firewall.

```bash
curl http://104.36.136.143:11434/api/tags
```

### F2: Cloud Proxy + Credential Leak (CRITICAL)

DeepSeek v4 Pro cloud proxy returns 401 with Ollama Connect credentials:

```json
{
  "error": "unauthorized",
  "signin_url": "https://ollama.com/connect?name=WIN-QAHP18EJH8I&key=<base64>"
}
```

Decoded:
- **Ollama username:** `WIN-QAHP18EJH8I` (Windows default machine name = no admin renamed it)
- **SSH pubkey:** `ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIIMKxccqkabWsNBkeqzUuLKzOAhJXKr76IS9Vjfu7eEV`

The default Windows hostname (`WIN-` prefix + random alphanumeric) indicates this machine was never domain-joined or renamed, typical of an unmanaged standalone deployment.

### F3: Model Injection on Government System (CRITICAL)

Any actor can inject system prompts into any model via CVE-2025-63389. If city staff use these models for government workflows, injected prompts affect those sessions.

---

## Impact

Municipal government AI deployment with exposed cloud API credentials. If `deepseek-v4-pro:cloud` is in active use, quota can be drained at city expense. Model injection affects any government workflow using this Ollama instance.

---

## Remediation

**Windows:**
```
OLLAMA_HOST=127.0.0.1
# In Ollama Windows settings, bind to loopback only
# Or: Windows Firewall rule blocking inbound TCP 11434
```

---

## Disclosure

- **Discovered:** 2026-05-01
- **Status:** Pending outreach to City of Cartersville IT
- **Escalation path:** CISA, MS-ISAC (state/local government sector)
