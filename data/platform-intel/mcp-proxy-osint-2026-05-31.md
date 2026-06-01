---
type: osint-brief
---

# mcp-proxy — Pre-Assessment OSINT Brief (2026-05-31)

_NuClide Research · 2026-05-31_
_Status: OSINT complete. Survey chain: pending._
_Sources: primary source code (sparfenyuk/mcp-proxy, TBXark/mcp-proxy, punkpeye/mcp-proxy), official docs, Knostic population study, Bitsight MCP exposure report, OWASP MCP Top-10, CVE databases. Primary source beats blog framing throughout._

---

## What This Is

Intelligence gathered before the population scan to tune dork selection, fingerprint design, verification methodology, and exposure scope. Not a survey — survey prep. Scan chain runs after this.

---

## The Target

**mcp-proxy** is a stdio-to-HTTP/SSE bridge for Model Context Protocol servers. Its entire purpose is to take a stdio MCP server — a process designed to communicate only over local stdin/stdout, never touching the network — and expose it over HTTP/SSE so remote clients can reach it.

The attack surface implication is load-bearing: whatever stdio server mcp-proxy fronts (filesystem, shell executor, database, GitHub, Brave Search, cloud APIs) becomes reachable over the network. The tool-surface is 100% operator-defined and arbitrarily dangerous. The bridge does not restrict what it proxies.

### Variant Landscape

| Repo | Language | Stars | Notes |
|---|---|---|---|
| `sparfenyuk/mcp-proxy` | Python (uvicorn/Starlette) | Primary, PyPI package, most deployed | Auth-optional, off by default |
| `TBXark/mcp-proxy` | Go | Multi-server aggregator | Auth optional, configurable per-server |
| `punkpeye/mcp-proxy` | TypeScript | FastMCP default bridge | Auth optional; permissive CORS by default |
| `sokunmin/mcp-proxy` | Python/Docker | Production-oriented fork | Default SSE port 8000 |

This brief focuses on `sparfenyuk/mcp-proxy` as the canonical PyPI-distributed version; notes TBXark and punkpeye where they diverge.

---

## 1. Auth Modes and Deploy Config

### sparfenyuk/mcp-proxy (Python) — Source-confirmed

**Default host bind: `127.0.0.1`**
**Default port: random (0 = OS-assigned)**

Source (`__main__.py`, argparse defaults):
```python
parser.add_argument("--port", type=int, default=0, ...)   # 0 = random port
parser.add_argument("--host", default="127.0.0.1", ...)
```

**No auth concept in server mode.** The source contains zero authentication middleware. `mcp_server.py` defines only one `Route` before the protocol routes:

```python
all_routes: list[BaseRoute] = [
    Route("/status", endpoint=_handle_status),  # Global status — unauthenticated
]
```

The SSE and `/mcp` endpoints are mounted with no auth check, no token validation, no session guard. The `CORSMiddleware` is the only middleware conditionally added, and only when `--allow-origin` is set. There is no `AuthMiddleware` or equivalent anywhere in the codebase.

The `API_ACCESS_TOKEN` env var exists only in **client mode** (when mcp-proxy acts as the HTTP client connecting *to* an upstream SSE server, not when it acts as the server). It adds the token as a header for outbound requests. It does not protect the locally-served endpoints.

**Auth options that DO protect the server:** None in sparfenyuk's implementation. There is no `--api-key`, no `--token`, no bearer token check on incoming requests.

**CORS default:** off. `--allow-origin` must be explicitly set. This does not protect the API from direct HTTP clients; it only blocks browser-origin cross-site requests.

**Auth tier: A** — no auth concept whatsoever on the server-facing side. The upstream client-auth flags (`--headers`, `--client-id`, `OAuth2`) are for outbound connections only.

### TBXark/mcp-proxy (Go) — Source-confirmed

**Default bind: `:9090` (all interfaces)**
**Default port: 9090**

Config (`docs/CONFIGURATION.md`):
```jsonc
"mcpProxy": {
  "addr": ":9090",
  "options": { "authTokens": ["DefaultToken"] }
}
```

Auth is token-based (`authTokens` list in JSON config). However, auth tokens must be explicitly set. There is no auto-generated token at startup; an operator who omits `authTokens` from the config gets no auth. The example config in the README uses `"DefaultToken"` as the literal value — operators copying the example verbatim run with a published well-known token.

**Auth tier: A*** — auth mechanism exists, is not on by default (requires explicit token configuration; default is no auth).

**Critical divergence:** TBXark binds to `:9090` (all interfaces) by default. sparfenyuk binds to `127.0.0.1` by default. Any Docker deployment of TBXark that maps port 9090 to the host is exposed without auth unless `authTokens` is configured.

### punkpeye/mcp-proxy (TypeScript)

**Default port: 8080**
**Default bind: `::` (all interfaces)**
**Default CORS: permissive (`*`)**
**Auth: `--apiKey` flag or `MCP_PROXY_API_KEY` env var (optional, off by default)**

`X-API-Key` header used when auth is configured. `/ping` and `OPTIONS` bypass auth when it is set.

**Auth tier: A*** — same as TBXark; mechanism exists, requires explicit opt-in.

---

## 2. Shodan Fingerprint and Population

### Endpoint Map (sparfenyuk)

| Path | Method | Description |
|---|---|---|
| `/sse` | GET | SSE transport — streams JSON-RPC events |
| `/messages/` | POST | Handles incoming JSON-RPC messages for SSE sessions |
| `/mcp` | GET/POST | Streamable HTTP transport |
| `/mcp/` | GET/POST | Normalized path (trailing slash) |
| `/status` | GET | JSON health + last-activity timestamp, no auth |
| `/servers/<name>/sse` | GET | Named server SSE endpoint |
| `/servers/<name>/mcp` | GET/POST | Named server streamable HTTP endpoint |

### HTTP Identity Markers

**Server header:** `uvicorn` — this is the ASGI server sparfenyuk uses. Not unique to mcp-proxy but narrows the Python/ASGI population.

**`/status` response body** (unauthenticated, always present):
```json
{
  "api_last_activity": "2026-05-31T...",
  "server_instances": {"default": "configured"}
}
```
The `server_instances` key with `"configured"` value is a mcp-proxy-specific signal not found in other Starlette/uvicorn applications.

**`initialize` response** (via POST to `/sse` or `/mcp`):
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "protocolVersion": "2024-11-05",
    "serverInfo": {"name": "<backing-server-name>", "version": "..."},
    "capabilities": {"tools": {}, "resources": {}, ...}
  }
}
```
`protocolVersion: "2024-11-05"` is the MCP spec version. Any response containing this field is confirmed MCP. `serverInfo.name` leaks the backing server identity (e.g., `"mcp-server-filesystem"`, `"github-mcp-server"`, `"postgres-mcp-server"`).

**SSE stream on GET `/sse`:** Server emits `event: endpoint` followed by a session message URL, then blocks. The `event: endpoint` line is an MCP-specific SSE marker.

### Candidate Shodan Dorks

Ranked by signal strength; FP risk noted per dork.

| Rank | Dork | FP Risk |
|---|---|---|
| 1 | `http.html:"server_instances" http.html:"api_last_activity"` | Low — the `server_instances`/`api_last_activity` JSON pair is mcp-proxy-specific; unlikely collision |
| 2 | `http.title:"MCP" Server:"uvicorn" port:8080` | Medium — many uvicorn apps have "MCP" in content; requires port narrowing |
| 3 | `http.html:"protocolVersion" http.html:"2024-11-05"` | Medium-High — any MCP server (not just mcp-proxy); catches broader MCP population which is the survey goal, but include FP from non-proxy servers |
| 4 | `"event: endpoint" http.html:"mcp"` | Medium — SSE `event: endpoint` is MCP-spec; Shodan may index this from the SSE stream if it connects |
| 5 | `http.html:"/servers/" http.html:"/sse" http.html:"configured"` | Low-Medium — named-server patterns narrow to TBXark/sparfenyuk multi-server deploys |

**For general MCP bridge population** (catches all variants):
```
http.html:"protocolVersion" http.html:"jsonrpc"
```

**FP traps:**
- Ethereum/Solana JSON-RPC nodes respond to JSON-RPC 2.0 but will not have `protocolVersion: "2024-11-05"`
- Generic uvicorn apps respond on port 8080 but will not have `server_instances` in responses
- The Knostic study (2026) used 100+ Shodan filters iteratively; their data confirms `"jsonrpc": "2.0"` + `"method": "initialize"` as highest-precision combo
- Bitsight found 1,100+ MCP honeypots; expect AS63949-class honeypot fleets in any MCP population sweep

### Population Context

- Knostic (2026): 1,862 Shodan-identified MCP servers, 119 manually verified, **100% unauthenticated**
- Bitsight (2026): ~1,000 exposed MCP servers lacking authorization
- OWASP MCP Top-10: Shadow MCP Servers listed at MCP09:2025 — developer-deployed, default-config
- sparfenyuk/mcp-proxy: common ports in the wild per existing mcp-discovery-runbook.sh: 3000, 8000, 8080, 8888

---

## 3. API Surface and Data Exposure

### Enumeration Without Auth (sparfenyuk)

Zero credential required for any of the following:

```
# Step 1: Identify MCP + backing server
POST /sse  (or /mcp)
Body: {"jsonrpc":"2.0","method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"probe","version":"0.1"}},"id":1}
Response: protocolVersion + serverInfo.name + capabilities map

# Step 2: List all tools with full schema
POST /sse
Body: {"jsonrpc":"2.0","method":"tools/list","params":{},"id":2}
Response: [{name, description, inputSchema}] — full JSON Schema for every callable tool

# Step 3: List all resources
POST /sse
Body: {"jsonrpc":"2.0","method":"resources/list","params":{},"id":3}
Response: [{uri, name, description, mimeType}] — every readable resource URI

# Step 4 (if resources): Read a resource
POST /sse
Body: {"jsonrpc":"2.0","method":"resources/read","params":{"uri":"<from list>"},"id":4}

# Step 5 (if tools): Call a tool
POST /sse
Body: {"jsonrpc":"2.0","method":"tools/call","params":{"name":"<tool>","arguments":{...}},"id":5}
```

**Insight #3 applies here:** The `initialize` + `capabilities` handshake leaks the full capability schema regardless of whether `tools/call` is gated. An unauthenticated `tools/list` returns every tool's name, description, and `inputSchema` — a complete map of the attack surface without executing anything.

### Worst-Case Exposure Chains

| Backing stdio server | mcp-proxy exposure | Impact class |
|---|---|---|
| `mcp-server-filesystem` | `read_file`, `write_file`, `list_directory` on operator's filesystem | Unauth arbitrary file read + write = RCE-adjacent (write shell scripts, overwrite configs) |
| `mcp-server-shellexecutor` / custom shell server | `run_command`, `bash_execute`, or equivalent | **Unauth arbitrary OS command execution** = full host compromise |
| `mcp-server-github` | Repo CRUD, issue/PR manipulation, webhook config | Unauth supply chain manipulation |
| `mcp-server-postgres` | SQL query execution on configured DB | Unauth data exfil + potential SQLi to privilege escalation |
| `mcp-server-brave-search` | API key consumption + search history | Cost exhaustion + operator OPSEC leak |
| `mcp-server-aws` / cloud MCP servers | IAM calls, S3 reads, service manipulation | Unauth cloud pivot |

**The proxy multiplies exposure:** An mcp-proxy fronting a filesystem server in a container with a mounted Docker socket is a one-step path from tool-call to container escape. This chain has been documented in the Anthropic MCP architecture RCE advisory (OX Security, 2026-04).

**Confirmed at source:** `proxy_server.py` lines 74-95 show `tools/list` and `call_tool` handlers are registered whenever `capabilities.tools` is non-null — no auth gate at any layer.

---

## 4. CVEs and Prior Research

### MCP Ecosystem CVEs (2025-2026)

| CVE | Component | Type | CVSS (est.) |
|---|---|---|---|
| CVE-2025-49596 | MCP Inspector (Anthropic official) | RCE via untrusted stdio input | Critical |
| CVE-2026-27825 | mcp-atlassian | Unauth RCE + SSRF | Critical |
| CVE-2026-22252 | LibreChat MCP integration | RCE | Critical |
| CVE-2025-54994 | @akoskm/create-mcp-server-stdio | RCE | High |
| CVE-2025-54136 | Cursor MCP integration | RCE | High |

**No CVE assigned specifically to sparfenyuk/mcp-proxy as of 2026-05-31.** The absence is likely a disclosure lag — the tool has no auth concept on the server side, which is a design characteristic, not a patchable bug. The OX Security "Mother of All AI Supply Chains" advisory (2026-04) covers the architectural class: MCP's stdio transport was designed for local use; any bridge exposing it without auth inherits the full command-injection surface of the backing server.

### Anthropic's Position

Anthropic declined to modify the MCP protocol architecture in response to OX Security's report, classifying the behavior as "expected." This means the auth gap in mcp-proxy bridges is not on a remediation path from the spec side.

### Population Research

- **Knostic (2026):** 1,862 Shodan-indexed MCP servers, 119 manually verified, 100% unauthenticated. Tools/list served to unauthenticated callers on every verified host.
- **Bitsight (2026):** ~1,000 exposed, dangerous tools confirmed including Kubernetes pod execution, CRM access, messaging services, RCE tools.
- **MCP Security 2026 (heyuan110):** 30 CVEs across MCP ecosystem in 60 days.
- **OWASP MCP Top-10, MCP09:2025:** Shadow MCP Servers as a top-10 category; default-configured bridges explicitly named.
- **mcpscan.ai:** Active scanner; 23% of scanned public MCP servers contained command injection vulnerabilities.

---

## 5. Deployment Patterns

### Install Paths (sparfenyuk)

```bash
# PyPI (most common)
uv tool install mcp-proxy
pipx install mcp-proxy

# Docker (GHCR + Docker Hub)
docker run --rm -t sparfenyuk/mcp-proxy:latest --port 8080 uvx mcp-server-fetch

# From source
uv tool install git+https://github.com/sparfenyuk/mcp-proxy
```

### Common Deployment Footguns

**Pattern 1 — Developer laptop, forgotten bound port:**
```bash
mcp-proxy --port 8080 --host 0.0.0.0 uvx mcp-server-filesystem --root /home/user
```
`--host 0.0.0.0` was added for testing Docker networking. Port 8080 left open. Full filesystem exposed.

**Pattern 2 — Docker Compose with host-mapped port:**
```yaml
services:
  mcp-proxy:
    image: sparfenyuk/mcp-proxy:latest
    ports:
      - "8080:8080"
    command: ["--port", "8080", "--host", "0.0.0.0", "uvx", "mcp-server-github"]
    environment:
      - GITHUB_PERSONAL_ACCESS_TOKEN=...
```
GITHUB_PERSONAL_ACCESS_TOKEN is visible to the MCP proxy process and exposed to any caller who can issue `tools/call`.

**Pattern 3 — TBXark/mcp-proxy with default config copied from README:**
```jsonc
{
  "mcpProxy": { "addr": ":9090", "options": { "authTokens": ["DefaultToken"] } }
}
```
`"DefaultToken"` is the literal value from the official documentation example. Any scanner that tries `Authorization: DefaultToken` hits immediately.

**Pattern 4 — Named-server aggregator:**
```bash
mcp-proxy --port 8080 --host 0.0.0.0 \
  --named-server github "npx -y @modelcontextprotocol/server-github" \
  --named-server fs "uvx mcp-server-filesystem --root /" \
  --named-server pg "uvx mcp-server-postgres postgresql://..."
```
Each named server gets its own `/servers/<name>/sse` endpoint; all unauthenticated.

### Most Common Backing Servers (GitHub usage data)

Ranked by frequency in real-world mcp-proxy configs found on GitHub:
1. `mcp-server-filesystem` — file read/write on host
2. `@modelcontextprotocol/server-github` — GitHub API operations
3. `mcp-server-fetch` — arbitrary HTTP fetch proxy
4. `mcp-server-postgres` / `mcp-server-sqlite` — database query execution
5. `mcp-server-brave-search` — search API
6. `mcp-server-aws` / cloud provider servers — cloud API access
7. Custom shell/command-executor servers — unauth OS command execution

---

## 6. Ecosystem Co-deployment and Adjacent Surface

### Co-location Signals

Operators running mcp-proxy in production typically pair it with:

- **Reverse proxy layer:** nginx/Caddy/Traefik on 443 terminating to mcp-proxy on internal port. Finding mcp-proxy often means finding an exposed nginx with a path-based route (e.g., `/mcp/` proxied to `localhost:8080`).
- **Claude Desktop / Cursor / Continue.dev:** These are the primary consumers of SSE-mode mcp-proxy. The presence of mcp-proxy on a VPS strongly suggests a developer machine or shared team server.
- **Other MCP servers:** Operators frequently run multiple MCP servers behind a single proxy. TBXark's aggregator design explicitly targets this pattern. A single mcp-proxy instance may front 3-10 backing servers.

### Shadow-Sweep Ports

Ports to sweep alongside any confirmed mcp-proxy host:

| Port | Reason |
|---|---|
| 3000 | sparfenyuk common example port |
| 8000 | sokunmin/mcp-proxy Docker default |
| 8080 | punkpeye + common override |
| 8888 | Jupyter crossover port, common in AI stacks |
| 9090 | TBXark/mcp-proxy default |
| 5432 | PostgreSQL (if mcp-server-postgres is in use) |
| 6333 | Qdrant (if vector MCP server is co-deployed) |

### Attribution Pivot Signals

- **`serverInfo.name` in `initialize` response:** Leaks exact backing server name. `"github-mcp-server"` → GitHub token in env. `"mcp-server-filesystem"` → filesystem access. `"postgres-mcp-server"` → DB credentials in env.
- **Tool names from `tools/list`:** `run_bash`, `execute_command`, `shell_exec` → shell MCP server. `read_file`, `write_file` → filesystem. `query`, `execute_sql` → database.
- **Docker image labels:** `org.opencontainers.image.source` in image manifest points to operator's GitHub repo, often public.
- **TLS cert CN:** If TLS is terminated at mcp-proxy or upstream nginx, cert CN/SAN reveals operator domain or org.
- **Named-server paths:** `/servers/github/`, `/servers/filesystem/` — the path segment names are operator-chosen but often literal descriptions of what is behind them.

---

## Verification Primitive

**Most reliable unauthenticated verification probe:**

```bash
curl -s -X POST http://<target>:<port>/sse \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"probe","version":"0.1"}},"id":1}'
```

**Confirmed MCP if response contains:**
- `"protocolVersion"` field in the `result` object, OR
- `"serverInfo"` with a `name` key

**Secondary: `/status` endpoint (no handshake required):**
```bash
curl -s http://<target>:<port>/status
```
Returns `{"api_last_activity": "...", "server_instances": {...}}` — sparfenyuk-specific, immediate, no protocol handshake needed.

**Note:** The `/status` primitive only confirms sparfenyuk/mcp-proxy specifically. The `initialize` handshake confirms any MCP bridge (broader survey utility).

---

## Summary Table

| Attribute | sparfenyuk (Python) | TBXark (Go) | punkpeye (TS) |
|---|---|---|---|
| Default bind | `127.0.0.1` | `::` (all) | `::` (all) |
| Default port | Random | 9090 | 8080 |
| Auth tier | **A (no auth concept)** | A* (optional, off by default) | A* (optional, off by default) |
| CORS default | Off | Configurable | Permissive (`*`) |
| Notable FP trap | `API_ACCESS_TOKEN` only protects outbound client, not server | `"DefaultToken"` literal in docs | `/ping` bypasses auth |

**Auth tier verdict (sparfenyuk, the primary target):** **Tier A — no auth concept on server-facing endpoints.** There is no flag, env var, or config that adds inbound request authentication to the served HTTP/SSE endpoints. Auth flags exist only for outbound client connections.

---

_Section-verified: 2026-05-31_
_Source trail: github.com/sparfenyuk/mcp-proxy (src/mcp_proxy/__main__.py, mcp_server.py, proxy_server.py), github.com/TBXark/mcp-proxy (docs/CONFIGURATION.md), github.com/punkpeye/mcp-proxy (README), Knostic MCP population study (2026), Bitsight MCP exposure report (2026), OX Security MCP supply chain advisory (2026-04), OWASP MCP Top-10 (MCP09:2025)_
