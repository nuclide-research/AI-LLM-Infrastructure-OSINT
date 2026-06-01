---
type: osint-brief
---

# FastMCP (Python MCP Server) — Pre-Assessment OSINT Brief (2026-05-31)

_NuClide Research · 2026-05-31_
_Status: OSINT complete. Survey chain: pending._
_Sources: primary source code (fastmcp-slim 3.3.1 wheel), official docs (gofastmcp.com), CVE databases, prior exposure research (Knostic 2026), nuclei-templates repo._

---

## What This Is

Intelligence gathered before the population scan to fine-tune dork selection, fingerprint design, verification methodology, and scope. Not a survey — a survey prep document. The scan chain runs after this.

---

## The Target

**FastMCP** — the dominant Python framework for building MCP (Model Context Protocol) servers. Originally authored by Jeremiah Lowin (`jlowin/fastmcp`); upstreamed into the official `modelcontextprotocol/python-sdk`; then relaunched under Prefect as `PrefectHQ/fastmcp` (the current active repo, PyPI `fastmcp` ≥ v3). The `fastmcp` PyPI package is now a meta-package wrapping `fastmcp-slim`. The project claims ~1M downloads/day and "70% of all MCP servers across all languages."

This is not a niche library. It is the de facto standard for AI-tool-exposure infrastructure.

---

## Section 1: Auth Modes and Deploy Config

**Auth posture: Tier A\* — auth optional, OFF by default for all transports.**

### Source-verified defaults (fastmcp-slim 3.3.1, `fastmcp/settings.py`)

```
transport  = "stdio"       # default; no network exposure
host       = "127.0.0.1"   # loopback-only; MUST be changed to expose
port       = 8000
sse_path   = "/sse"
streamable_http_path = "/mcp"
message_path = "/messages/"
```

**Critical finding from `server.py` line 397:**

```python
self.auth: AuthProvider | None = auth
```

The `FastMCP()` constructor signature is:

```python
def __init__(self, name=None, ..., auth: AuthProvider | None = None, ...)
```

`auth=None` is the default. No auth is applied to any transport unless the caller explicitly passes an `AuthProvider` instance.

### Transport chain

When `transport=None`, `run()` falls through to `fastmcp.settings.transport` which defaults to `"stdio"`. STDIO has no network exposure. **The risk population is deployments where the operator has explicitly switched to HTTP transport (`"http"`, `"streamable-http"`, or `"sse"`) and left `auth=None`.**

HTTP transport dispatch in `http.py` (`create_streamable_http_app` / `create_sse_app`):

```python
if auth:
    # mount RequireAuthMiddleware on all endpoints
else:
    # No auth required — endpoint is fully open
    server_routes.append(Route(streamable_http_path, endpoint=streamable_http_app, methods=http_methods))
```

This is a hard binary: auth object present = enforced on every request; no auth object = zero protection. There is no concept of "soft" auth or warnings.

### Auth options (when explicitly configured)

| Option | Class | Notes |
|--------|-------|-------|
| Bearer token / JWT | `TokenVerifier` (subclass) | Static or JWKS-backed |
| OAuth 2.1 full flow | `OAuthProvider` / `OIDCProxy` | GitHub, Google, Auth0, Keycloak, WorkOS, Clerk, Descope, AWS, Azure, Supabase, PropelAuth, ScaleKit providers |
| Multi-provider | `MultiAuth` | Chain multiple providers |
| Debug (dev only) | `DebugProvider` | Never production-safe |

Auth is enforced at the Starlette middleware layer via `RequireAuthMiddleware` wrapping every MCP route. No partial protection is possible at the framework layer — you either set `auth=` or you don't.

### Host binding realities in the wild

The `settings.py` default is `127.0.0.1` (safe). But:
- Docker deployments almost universally set `host=0.0.0.0` explicitly
- `FASTMCP_HOST=0.0.0.0` env var overrides the default globally
- PaaS deployments (Render, Railway, Fly.io) require `0.0.0.0` to pass health checks
- Common Docker Compose patterns expose `8000:8000` with `FASTMCP_HOST=0.0.0.0`

Evidence from GitHub issue ecosystem: multiple repos confirm `host="0.0.0.0"` as the standard Docker deployment pattern, with `FASTMCP_SERVER_HOST` / `FASTMCP_SERVER_PORT` as the canonical env var names.

### Server name (`serverInfo.name`)

When `name=None` is passed to `FastMCP()` (the default), the server generates a random name via `generate_name()`:

```python
@classmethod
def generate_name(cls, name: str | None = None) -> str:
    class_name = cls.__name__
    if name is None:
        return f"{class_name}-{secrets.token_hex(2)}"
    # → e.g. "FastMCP-3a7f"
```

So `serverInfo.name` in the initialize response is either:
- A user-provided string (e.g., `"MyWeatherServer"`, `"filesystem"`, `"database"`)
- `"FastMCP-<4hex>"` when no name is provided

The **4-hex suffix is random per instance** and is NOT a reliable fingerprint. The string `"FastMCP"` as a prefix is the fingerprint marker, but many operators name their server something descriptive. More reliable: the framework version string in `serverInfo.version`, which defaults to the `fastmcp.__version__` string (e.g., `"3.3.1"`).

---

## Section 2: Shodan Fingerprint and Population

### Identity markers

**Primary — HTTP response header (most reliable):**

`mcp-session-id` — issued by the server in the HTTP response to a POST on `/mcp` or `/sse` connection. This header is FastMCP/MCP-SDK-specific. Nothing else puts `mcp-session-id` in a response header. Confirmed in mcp-sdk source (issue #1063: "HTTP responses from FastMCP servers include the `mcp-session-id` header").

**Secondary — content-type on SSE path:**

`Content-Type: text/event-stream` + MCP context (e.g., body containing `"jsonrpc"`)

**Tertiary — framework + path combination:**

`Server: uvicorn` + path `/mcp` or `/sse` — FastMCP uses uvicorn as its embedded HTTP server. However, `Server: uvicorn` is generic to all Python ASGI apps.

**Quaternary — JSON-RPC response body:**

A POST to `/mcp` with `{"jsonrpc":"2.0","method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"probe","version":"1.0"}},"id":1}` returns a JSON body containing `"serverInfo"` and `"capabilities"`. The `"serverInfo"` key is MCP-specific.

### Candidate Shodan dorks

| Rank | Dork | FP Risk |
|------|------|---------|
| 1 | `http.headers:"mcp-session-id"` | LOW — this header is MCP-protocol-specific. No known non-MCP service emits it. |
| 2 | `http.html:"\"serverInfo\"" http.html:"\"capabilities\""` | MEDIUM — both keys appear in MCP initialize response, but `capabilities` is generic JSON. Combine with `http.html:jsonrpc` to tighten. |
| 3 | `Server: uvicorn http.title:"" http.html:"/mcp"` | HIGH — uvicorn is used by any FastAPI/Starlette app; needs path qualifier. |

**Additional candidates (lower confidence):**

- `http.html:"\"protocolVersion\""` — in MCP initialize response body; rare string
- `http.html:"tools/list"` — appears in error responses and verbose MCP output
- `http.html:"\"method\":\"initialize\""` — can be cached by Shodan if banner-grabbed

**False positive traps:**

- `uvicorn` alone: any Python ASGI app (FastAPI, Starlette, LangChain server, etc.)
- `text/event-stream`: any SSE server (notification systems, stock tickers, ChatGPT-compatible APIs)
- `"jsonrpc"`: any JSON-RPC 2.0 service (Ethereum node, legacy RPC APIs)
- `"Model Context Protocol"` in HTML: landing pages, documentation mirrors, marketing sites

**Prior population research (Knostic, 2026):**

1,862 internet-exposed MCP servers found via 100+ Shodan filters. 119/119 sampled servers returned tool listings without authentication. This was not specific to FastMCP alone — includes MCP servers on all SDKs — but the Python/FastMCP share is likely dominant given the ecosystem.

560 exposed MCP Inspector instances also found on Shodan at time of research.

---

## Section 3: API Surface and Data Exposure

### Methods reachable without auth on a default HTTP deployment

On a FastMCP server with `auth=None` and HTTP transport, the entire MCP JSON-RPC surface is open. The `RequireAuthMiddleware` is not mounted; Starlette routes are bare.

| Method | What it leaks | Auth required (default) |
|--------|---------------|------------------------|
| `initialize` | `serverInfo` (name, version), full `capabilities` object (tools, resources, prompts, sampling flags) | No |
| `tools/list` | All tool names, descriptions, full input JSON schemas | No |
| `resources/list` | All resource URIs and descriptions | No |
| `prompts/list` | All prompt names and argument schemas | No |
| `tools/call` | Tool execution — RCE if any shell/filesystem/cloud tool registered | No |
| `resources/read` | Resource content — often file or DB content | No |

**What `tools/list` leaks in practice:**

Tool definitions include:
- `name`: e.g., `"execute_shell"`, `"read_file"`, `"write_file"`, `"query_database"`, `"s3_list_buckets"`
- `description`: natural-language description of what the tool does — often reveals internal system topology
- `inputSchema`: full JSON Schema of parameters, revealing internal field names, types, and constraints

A `tools/list` response from a filesystem MCP server will enumerate file operation tools with path parameters. A database MCP server leaks table names and query capabilities. A cloud MCP server leaks cloud account scope.

**The `initialize` capabilities object (Insight #3 applies):**

Even if tool execution were protected (it isn't by default), the `initialize` response's `capabilities` block reveals the surface:
```json
{
  "capabilities": {
    "tools": {},
    "resources": {"subscribe": true},
    "prompts": {}
  }
}
```
This tells the attacker which MCP primitives exist before they call `tools/list`.

**Sensitive data classes commonly exposed:**

- Filesystem tools: arbitrary file read/write on the server running FastMCP
- Shell/subprocess tools: direct OS command execution (highest severity)
- Database connectors: SQL query execution against production databases
- Cloud API tools: AWS/GCP/Azure SDK calls using credentials baked into the environment
- LLM sampling tools: prompt injection surface if the MCP server proxies to another LLM
- Memory/vector DB tools: direct read/write of agent memory stores (Chroma, Qdrant, Weaviate)

Cloud and DB credentials are typically passed as environment variables to the FastMCP process, not stored in tool definitions — but the tool surface reveals their scope.

---

## Section 4: CVEs and Prior Research

### FastMCP CVEs

| CVE | CVSS | Affected Versions | Type | Fix |
|-----|------|-------------------|------|-----|
| CVE-2025-62801 | 7.8 (NVD) | < 2.13.0 | Windows command injection via `server_name` in `fastmcp install cursor` — shell metacharacters unescaped in `subprocess.run` | 2.13.0 |
| CVE-2025-64340 | CVSS:3.1/AV:L/AC:H/PR:L/UI:R C:H/I:H/A:H | < 3.2.0 | Same class — Windows command injection via `server_name` in `fastmcp install gemini-cli` / `fastmcp install claude-code` | 3.2.0 |

Both CVEs are **local** — they require the attacker to influence the `server_name` argument to the install subcommand on a Windows host. Not a remote attack vector against HTTP-deployed servers. IBM watsonx.data issued a security bulletin for these.

GHSA identifiers: `GHSA-rj5c-58rq-j5g5` (CVE-2025-62801), `GHSA-m8x7-r2rg-vh5g` (CVE-2025-64340).

### MCP ecosystem CVEs (relevant to deployed FastMCP instances)

| CVE | Target | Relevance |
|-----|--------|-----------|
| CVE-2025-54136 (MCPoison) | MCP protocol | Tool-poisoning: attacker who controls MCP server embeds instructions in tool descriptions to hijack LLM agent behavior |
| CVE-2025-54135 (CurXecute) | MCP protocol | Tool-poisoning variant targeting Cursor |
| CVE-2025-49596 | MCP Inspector | XSS in Anthropic's MCP Inspector debug UI |

**Tool poisoning is the most relevant remote attack class for deployed FastMCP servers.** If an attacker reaches `tools/call` (trivial with no auth), they can call any registered tool AND they can mutate tool definitions on a compromised FastMCP host to poison downstream LLM clients reading those tools.

### Prior public research

- **Knostic (2026):** 1,862 exposed MCP servers, 119/119 sample unauthenticated. Methodology: Shodan + `mcp_func_checker.py` verification via JSON-RPC handshake. Key finding: "All 119 servers allowed access to internal tool listings without authentication."
- **Wallarm:** Published `mcp-jsonrpc2-ultimate-detect` nuclei template; documented dozens of unintentionally public MCP backends.
- **ProjectDiscovery nuclei-templates:** `http/exposures/apis/exposed-mcp-server.yaml` — POST to `{{BaseURL}}` and `{{BaseURL}}/mcp/` with `tools/list`, `resources/list`, `prompts/list` methods. Matchers look for `"tools": [...]`, `"resources": [...]`, `"prompts": [...]` in response. **FP note:** The template also matches on strings like `"available_tools": [` and `"parameters": {` which are generic JSON — expect false positives from non-MCP JSON-RPC services.
- **Elastic Security Labs:** Published threat model for MCP tool abuse vectors.
- **OWASP MCP Top 10:** Published as of early 2026.

---

## Section 5: Deployment Patterns

### Transports and paths

| Transport | Default path | HTTP methods | Notes |
|-----------|-------------|--------------|-------|
| `streamable-http` / `http` | `/mcp` | GET, POST, DELETE | Recommended for new deployments; bidirectional |
| `sse` | `/sse` (connect) + `/messages/` (POST) | GET + POST | Legacy; still widely deployed |
| `stdio` | N/A | N/A | Default; no network exposure |

### Uvicorn as the embedded server

FastMCP calls `uvicorn.Config(app, host=host, port=port, ...)` directly from `run_http_async()`. It does NOT expose a `--workers` flag in the default `run()` path (stateful sessions require sticky connections). This means:
- Single process, no forking
- `Server: uvicorn` in HTTP responses
- Starlette as the ASGI framework underneath

### Common deployment configurations

**Docker run (most common raw pattern):**
```
docker run -p 8000:8000 -e FASTMCP_HOST=0.0.0.0 my-mcp-server
```

**Docker Compose (standard pattern):**
```yaml
services:
  mcp:
    ports: ["8000:8000"]
    environment:
      FASTMCP_SERVER_HOST: "0.0.0.0"
      FASTMCP_SERVER_PORT: "8000"
```

**PaaS (Render/Railway/Fly.io):**
Startup command typically: `uvicorn app:http_app --host 0.0.0.0 --port $PORT`
These platforms require binding to `0.0.0.0` and use a random external port forwarded from their edge. Some operators expose port 80/443, others a high port.

**ASGI mount (FastAPI integration):**
```python
app = FastAPI()
mcp_app = mcp.http_app()
app.mount("/mcp", mcp_app)
```
In this case the path is `/mcp` under whatever base path FastAPI is hosted at.

**Behind nginx:**
Path variants seen in the wild: `/mcp`, `/api/mcp`, `/v1/mcp`, `/messages`. No standard convention for proxy deployments.

### Port distribution

- **8000**: Default, most common for direct FastMCP deployments
- **8080**: Common alternative, especially in K8s sidecar patterns
- **3000**: Some Docker Compose stacks collide with frontend default
- **80/443**: Nginx-proxied production deployments
- **10000**: Render.com's default port assignment

---

## Section 6: Ecosystem Co-deployment and Adjacent Surface

### What else runs on the same host

FastMCP is a tool-exposure layer. By definition it wraps data sources. Common co-resident services on the same host or Docker network:

| Service | Default Port | Notes |
|---------|-------------|-------|
| Ollama | 11434 | LLM inference engine; often the model backend for the tools |
| Chroma | 8000 | Vector DB — port COLLISION with FastMCP default |
| Qdrant | 6333 (HTTP), 6334 (gRPC) | Vector DB |
| Weaviate | 8080 | Vector DB |
| PostgreSQL | 5432 | Common tool backend |
| Redis | 6379 | Session / memory store |
| FastAPI app | 8001, 8080 | The user app that the MCP wraps |
| n8n | 5678 | Workflow automation platform; increasingly MCP-integrated |
| Open WebUI | 3000, 8080 | LLM chat UI; can run alongside Ollama + MCP |
| LangChain API server | 8080 | Common integration |

**Port collision note:** Chroma defaults to 8000, same as FastMCP. Docker Compose stacks commonly bump one to 8001. This means Shodan results on port 8000 from a given IP may be FastMCP OR Chroma — the `mcp-session-id` header differentiates them.

### Shadow-sweep port priorities

When a host at 8000 is confirmed as FastMCP, probe:
- 11434 — Ollama (unauth LLM inference; frequently co-deployed)
- 8080 — alternate FastMCP or Weaviate
- 6333 — Qdrant
- 5432 — PostgreSQL (rarely directly exposed, but Docker-network-reachable)
- 6379 — Redis
- 9090 — Prometheus (metrics endpoint often exposes tool invocation counters)

### TLS cert patterns for attribution pivot

Many FastMCP deployments run HTTP-only (especially on internal networks or PaaS with TLS termination at edge). For HTTPS deployments:
- Let's Encrypt certs on PaaS — operator subdomain reveals company (e.g., `my-mcp.fly.dev`, `mcp-server.onrender.com`, `*.railway.app`)
- Self-signed certs — typically contain a hostname or IP; direct-IP TLS probe (no SNI) surfaces the cert's CN
- OV/EV certs are rare for MCP servers given the dev-tooling nature

Subdomain patterns seen in the wild: `mcp.`, `api-mcp.`, `mcp-server.`, `tools.`, `ai-tools.`, `agent.` — all common naming conventions for FastMCP deployments behind reverse proxies.

---

## Verification Primitive (Primary)

**Single most reliable unauthenticated identity marker:**

POST to `<target>:8000/mcp` (or `/sse` for legacy):

```
POST /mcp HTTP/1.1
Host: <target>:8000
Content-Type: application/json

{"jsonrpc":"2.0","method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"probe","version":"1.0"}},"id":1}
```

Expected response shape on a FastMCP server:
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "protocolVersion": "2024-11-05",
    "capabilities": { "tools": {}, "resources": {}, "prompts": {} },
    "serverInfo": {
      "name": "<user-provided or FastMCP-XXXX>",
      "version": "<fastmcp version, e.g. 3.3.1>"
    }
  }
}
```

Confirmation signal: HTTP 200 + `Content-Type: application/json` + `"serverInfo"` key in body + `mcp-session-id` response header.

If the server responds with 401 and a `WWW-Authenticate: Bearer ...` header containing `resource_metadata=`, it is a FastMCP server with auth enabled — still confirmable as FastMCP, just gated.

For SSE transport, the initialize is sent differently: GET `/sse` establishes the stream, then POST `/messages/` carries the JSON-RPC payload. The `initialize` response arrives as a server-sent event on the stream.

---

## Auth Posture Verdict

**Tier A\*** — auth-optional, off by default.

- No auth concept at the transport layer in `stdio` mode (the default).
- HTTP mode: `auth=None` is the default constructor argument; no auth middleware is mounted unless explicitly set.
- Source confirmation: `self.auth: AuthProvider | None = auth` with `auth=None` as default.
- The framework has rich auth support (OAuth 2.1, JWT, 15+ identity providers) — but it is entirely opt-in.
- Documentation recommends auth for remote deployments but does not enforce it.
- Population evidence: 119/119 sampled real-world deployments were unauthenticated (Knostic 2026).

The thesis holds: auth-optional-off at population scale means deployed unauthenticated.

---

## Pre-Survey Notes

1. The nuclei template `exposed-mcp-server.yaml` probes only `{{BaseURL}}` and `{{BaseURL}}/mcp/` — misses `/sse`, `/api/mcp`, `/v1/mcp`. Write a supplemental probe.
2. Chroma's default port 8000 is a collision source. Filter on `mcp-session-id` header to separate.
3. STDIO-only deployments have no network exposure — they are Claude Desktop / Cursor / VS Code local installs and are not in the Shodan population.
4. The `serverInfo.version` field leaking the exact fastmcp version is a secondary fingerprint; operators on old versions (pre-2.13.0) are also CVE-2025-62801/64340 candidates on Windows.
5. Proxy deployments (FastMCP behind nginx) may not expose `Server: uvicorn` — rely on `mcp-session-id` header instead.
