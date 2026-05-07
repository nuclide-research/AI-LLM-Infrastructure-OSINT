# 10. MCP Servers

_New in v2 · Section verified: April 2026_

Model Context Protocol servers expose tool surfaces, filesystem read, shell, database, internal APIs, for consumption by LLM clients. When operators expose MCP over HTTP/SSE rather than stdio, the tools become available to anyone who connects.

| Shodan Query | Notes |
|---|---|
| `"modelcontextprotocol" port:3000` | MCP SSE transport, no auth default |
| `"mcp" "/sse" "message" port:3000` | MCP server over SSE |
| `"mcp" "tools/list" port:8080` | JSON-RPC MCP transport |
| `"jsonrpc" "2.0" "tools/list"` | Transport-agnostic MCP handshake, catches servers that stripped the "mcp" literal |
| `"server-filesystem" "mcp"` | Filesystem MCP exposed, host file access |
| `"mcp-server-" "sse" port:8000` | |
| `"FastMCP" "uvicorn" port:8000` | Python MCP server framework |
| `"mcp-proxy" port:8080` | stdio-to-HTTP bridge, extends exposure surface |

## Open WebUI: Adjacent MCP Surface

Open WebUI v0.6.0+ ships native MCP server integration. When an operator wires MCP tools into Open WebUI (filesystem, shell, browser, database, cloud APIs), those tools are callable by any connected AI model during inference.

**Shodan queries (7,273 instances as of 2026-05-01):**

| Shodan Query | Notes |
|---|---|
| `http.html:"Open WebUI" port:3000` | **7,273 instances**, default port |
| `http.html:"open-webui" "uvicorn"` | Python ASGI stack fingerprint |
| `http.title:"Open WebUI"` | Title-based, broader |

**Probe for auth bypass (Open WebUI auth + raw Ollama port):**
```bash
# Check Open WebUI version + auth status
curl http://TARGET:3000/api/config | jq '{version, auth: .features.auth}'

# Auth bypass: direct Ollama port regardless of Open WebUI auth setting
curl http://TARGET:11434/api/tags

# Check for cloud proxy models (quota hijack)
curl http://TARGET:11434/api/tags | jq '[.models[].name | select(endswith(":cloud"))]'
```

**33% of Open WebUI instances** have raw Ollama port 11434 also exposed (sampled 42/7,273). Extrapolated: **~2,400 instances** with auth bypass.

**Compound chain (MCP-capable instances, v0.6.0+):**
1. Inject Ollama model via port 11434 (unauthenticated)
2. User interacts with model through authenticated Open WebUI
3. Injected model generates MCP tool calls per attacker instructions
4. Open WebUI executes tool calls, filesystem, shell, cloud APIs, trusting model output

See `tools/open-webui-ollama-bypass.md` and `tools/open-webui-cloud-proxy-hijack.md`.

**Live finding:** `hts.k12.nj.us` (NJ K-12), Open WebUI v0.8.8, Ollama v0.17.5, 5 cloud proxy subs (Gemini, DeepSeek, MiniMax x3). See `case-studies/hts-k12-nj-open-webui.md`.

---

**MCP over HTTP is the 2026 wave.** The protocol was designed for stdio (in-process transport) but the ecosystem pushed toward HTTP/SSE for remote access. Operators wiring internal tools, shell, database, filesystem, into an MCP server and exposing it without auth is the same failure pattern as unauthenticated RPC from the 1990s, with a new label.

## HexStrike AI: Ollama-Backed Offensive MCP Platform

`0x4m4/hexstrike-ai` (8,444★) is a widely-deployed MCP server wiring 150+ security tools to LLM clients. It ships as two components: `hexstrike_server.py` (Flask, default port 8888) and `hexstrike_mcp.py` (47 MCP tool definitions). The companion Ollama model is `hexstrike-ai:latest`, a thin system-prompt wrapper over `huihui_ai/qwen3.5-abliterated:35b-a3b-q4_K`.

**Detection fingerprints:**

| Shodan Query | Notes |
|---|---|
| `http.html:"hexstrike" port:8888` | HexStrike Flask server health endpoint |
| `"HexStrike" port:11434` | Ollama instance with hexstrike model loaded |
| `"hexstrike-ai" port:11434` | Model name fingerprint in Ollama /api/tags |

**Attack surface when found:**
- Flask `/api/command` (POST) = unrestricted shell exec on the host
- Flask `/api/files/*` = filesystem read/write/delete
- Ollama `/api/create` = unauthenticated model injection (see `tools/ollama-model-injection.md`)
- Ollama `/api/pull` = SSRF to internal services (see `tools/ollama-ssrf.md`)

**Note:** The Flask server binds to localhost by default, only Ollama port 11434 is typically externally exposed. When found on Shodan, the Ollama model is accessible but the Flask execution layer is not directly reachable. Model injection + SSRF are the available vectors from outside.
