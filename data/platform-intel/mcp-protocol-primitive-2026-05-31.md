# MCP Protocol Verification Primitive
**Date:** 2026-05-31  
**Spec sources:** modelcontextprotocol/modelcontextprotocol (GitHub), schema/2025-11-25/schema.ts  
**Purpose:** aimap fingerprint + honeypot-discrimination primitive for MCP survey

---

## 1. Transport Evolution

### Spec Revision Timeline

| Version | Date | Transport Change |
|---------|------|-----------------|
| v1 | 2024-11-05 | HTTP+SSE (two endpoints: `/sse` GET + `/messages` POST) |
| v2 | 2025-03-26 | **Streamable HTTP replaces HTTP+SSE** (PR #206); OAuth 2.1 auth added |
| v2.1 | 2025-06-18 | `MCP-Protocol-Version` header made **MUST** on subsequent requests (PR #548) |
| v2.2 | 2025-11-25 | OIDC Discovery support; polling SSE; `WWW-Authenticate` optional with well-known fallback |

### Legacy HTTP+SSE Transport (2024-11-05 — still in wild)

Two separate endpoints, no canonical path mandated:
- `GET /sse` — client opens SSE stream; server sends `event: endpoint` with `data: <post-url>` as first event
- `POST <post-url>` — client sends JSON-RPC messages to the URL received in the `endpoint` event

Common real-world paths: `/sse`, `/events`, `/stream`  
Common POST paths: `/messages`, `/message`, `/rpc`

Detection flow: `GET <base>/sse` → look for `event: endpoint` SSE frame in response body.

### Streamable HTTP Transport (2025-03-26 — spec current)

**Single endpoint** supporting both POST and GET. Canonical example: `https://example.com/mcp`

- `POST /mcp` — send JSON-RPC (requests, notifications, responses); response is either `application/json` (direct) or `text/event-stream` (streaming)
- `GET /mcp` — open SSE stream for server-initiated messages (optional; server may return 405)
- `DELETE /mcp` — explicit session termination (server may return 405)

**In-the-wild reality (2026-05-31):** The majority of deployed servers still use the legacy SSE shape (most frameworks/tutorials predate 2025-03-26). The registry `server.json` format explicitly supports both `"type": "streamable-http"` and `"type": "sse"` as co-equal options. **Scan MUST handle both shapes.**

---

## 2. Canonical Unauthenticated `initialize` Request

### Streamable HTTP Transport

**Headers:**
```
POST /mcp HTTP/1.1
Content-Type: application/json
Accept: application/json, text/event-stream
MCP-Protocol-Version: 2025-11-25
```
Note: `MCP-Protocol-Version` header is NOT sent on the initialize request itself — it is MUST on all *subsequent* requests after negotiation. Omit it on the first `initialize` POST. If missing on subsequent requests, server SHOULD assume `2025-03-26`.

**Body (current spec — 2025-11-25):**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "initialize",
  "params": {
    "protocolVersion": "2025-11-25",
    "capabilities": {},
    "clientInfo": {
      "name": "nuclide-scanner",
      "version": "1.0.0"
    }
  }
}
```

**Multi-version probe strategy:** Try `"protocolVersion": "2025-11-25"` first. If error code `-32602` ("Unsupported protocol version"), retry with `"2025-03-26"`, then `"2024-11-05"`. Server echoes back its highest supported version; that value is the fingerprint anchor.

**Session ID lifecycle (Streamable HTTP):**
- Server MAY return `MCP-Session-Id: <uuid>` header in the `InitializeResult` response
- If returned, ALL subsequent requests MUST include `MCP-Session-Id: <value>` header
- Requests without session ID (after init) → server SHOULD return 400
- Server-terminated session → 404 → client re-initializes without session ID

### Legacy SSE Transport

```
Step 1: GET <base>/sse HTTP/1.1
        Accept: text/event-stream

Step 2: Parse SSE stream for first event:
        event: endpoint
        data: /messages?sessionId=abc123

Step 3: POST /messages?sessionId=abc123 HTTP/1.1
        Content-Type: application/json

        {"jsonrpc":"2.0","id":1,"method":"initialize","params":{
          "protocolVersion":"2024-11-05",
          "capabilities":{},
          "clientInfo":{"name":"nuclide-scanner","version":"1.0.0"}
        }}

Step 4: Response arrives as SSE message event on the GET /sse stream:
        event: message
        data: {"jsonrpc":"2.0","id":1,"result":{...}}
```

---

## 3. Expected Response Shape — Identity Markers

**Nominal `InitializeResult`:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "protocolVersion": "2025-11-25",
    "serverInfo": {
      "name": "example-server",
      "version": "1.0.0"
    },
    "capabilities": {
      "tools": {},
      "resources": {},
      "prompts": {},
      "logging": {}
    },
    "instructions": "..."
  }
}
```

**Required fields as of 2025-11-25:** `protocolVersion` and `serverInfo` are MUST. `capabilities` is MUST (can be empty `{}`). `instructions` is optional.

**`serverInfo.name` values in 2025-11-25:** The `name` field is a programmatic identifier; `title` is the display name (added 2025-06-18, PR #663). Fingerprint on `name`, not `title`.

### 3-Conjunct Verification Matcher

A real MCP server satisfies ALL THREE:

```
CONJUNCT-1 (endpoint):
  Streamable: POST /mcp returns HTTP 200 with Content-Type application/json OR text/event-stream
  Legacy SSE: GET /sse returns HTTP 200 with Content-Type text/event-stream AND first event is "endpoint"

CONJUNCT-2 (response structure):
  Response body is valid JSON with keys: jsonrpc="2.0", id=<matches request id>, result.protocolVersion

CONJUNCT-3 (anchored field):
  result.protocolVersion is one of: "2024-11-05" | "2025-03-26" | "2025-06-18" | "2025-11-25"
  AND result.serverInfo.name is a non-empty string
```

**Why this discriminates:** A permissive honeypot typically:
- Returns 200 to any POST (fails C1 on method/path specificity)
- Returns generic JSON without `result.protocolVersion` (fails C2)
- Cannot produce a valid version-date string in `result.protocolVersion` (fails C3)

C3 is the hard filter: the version string set is small, closed, and semantically specific. A generic HTTP echo/tarpit cannot produce it correctly. This is the same discriminant used in the 2026-05-04 survey (protocol-shape conformance dropped honeypot pollution from 91.6% to 1.1%).

---

## 4. Auth Discrimination

### Spec Compliance (2025-03-26, refined 2025-06-18, 2025-11-25)

A spec-compliant **authenticated** server returns:
```http
HTTP/1.1 401 Unauthorized
WWW-Authenticate: Bearer resource_metadata="https://mcp.example.com/.well-known/oauth-protected-resource",
                         scope="tools:read"
```

The `resource_metadata` URL points to a Protected Resource Metadata document (RFC 9728) containing `authorization_servers`. As of 2025-11-25, the `WWW-Authenticate` header is OPTIONAL — server MAY omit it and rely solely on the `/.well-known/oauth-protected-resource` endpoint (align with RFC 9728; spec change PR #985).

Fallback discovery chain:
1. Parse `resource_metadata` from `WWW-Authenticate` if present
2. Else probe `/.well-known/oauth-protected-resource/<mcp-path>`
3. Else probe `/.well-known/oauth-protected-resource`

### On/Off Discrimination Rule

| Response | Classification |
|----------|---------------|
| `initialize` → `200` + valid `result.protocolVersion` + `result.capabilities.tools` | **UNAUTH FINDING** — no token required, full tool listing accessible |
| `initialize` → `401` + `WWW-Authenticate` with `resource_metadata` | **AUTH CONFIGURED** — not a finding, surface open, access not exercised |
| `initialize` → `401` without `WWW-Authenticate` | **AUTH CONFIGURED (non-compliant)** — auth present but RFC 9728 discovery missing |
| `initialize` → `200` but no `result.protocolVersion` | **NOT MCP** — filter out (honeypot/generic HTTP) |
| `GET /sse` → `200` + `text/event-stream` but no `event: endpoint` | **NOT MCP** — SSE but wrong protocol |

**Critical distinction:** Auth-on-default means `initialize` returns 401 BEFORE any capability exposure. Auth-off means `initialize` succeeds AND `tools/list` is callable. The finding requires both: successful `initialize` AND successful `tools/list` with populated tool array.

---

## 5. Discovery Substrate

### Official Registry (`registry.modelcontextprotocol.io`)

- **API:** `GET https://registry.modelcontextprotocol.io/v0/servers?limit=N&query=<term>` — returns server metadata including `remotes[].url` and `remotes[].type` (`streamable-http` or `sse`)
- Registry in preview as of 2026-05-31; ~29,000+ servers indexed in glama.ai aggregator
- `server.json` schema: `name` field is `<reverse-domain>/<slug>` (e.g., `io.github.username/server-name`)
- Registry aggregators also include: Smithery (`smithery.ai`), glama.ai (`glama.ai/mcp/servers`), PulseMCP (`pulsemcp.com`)

### Reference Server `serverInfo.name` Values

These are the canonical Anthropic reference implementations — high-value identity markers for aimap:

| Package | `serverInfo.name` | Language | Notes |
|---------|------------------|----------|-------|
| `@modelcontextprotocol/server-filesystem` | `"secure-filesystem-server"` | TypeScript | Most widely deployed |
| `@modelcontextprotocol/server-memory` | `"memory-server"` | TypeScript | |
| `@modelcontextprotocol/server-sequential-thinking` | `"sequential-thinking-server"` | TypeScript | |
| `@modelcontextprotocol/server-everything` | `"mcp-servers/everything"` | TypeScript | Test/demo server |
| `mcp-server-fetch` | `"mcp-fetch"` | Python | |
| `mcp-server-git` | `"mcp-git"` | Python | |
| `mcp-server-time` | `"mcp-time"` | Python | |

**Note:** The `name` field in `serverInfo` is a runtime string set by the server's `Server()` constructor call. Third-party servers vary widely. `"secure-filesystem-server"` and `"mcp-fetch"` are the two most likely to appear in real deployments because they are the most commonly linked reference implementations.

**Ambiguity flag:** Third-party frameworks (FastMCP, MCP-Framework, etc.) may set `serverInfo.name` to generic values like `"fastmcp"` or the npm package name. The `serverInfo.name` field alone is not sufficient for taxonomy — it must be combined with the `capabilities` shape and `protocolVersion` for reliable fingerprinting.

---

## Scan Implementation Notes

### Port Enumeration

Spec does not mandate a port. Common observed ports in wild: 3000, 8000, 8080, 8443, 443. Shodan dork surface: `http.title:"MCP"` or banner-match on `"jsonrpc":"2.0"` + `"protocolVersion"`.

### Probe Sequence for aimap Integration

```
1. Try POST <host>/mcp (Streamable HTTP probe)
   Headers: Content-Type: application/json, Accept: application/json, text/event-stream
   Body: initialize request with protocolVersion: "2025-11-25"
   
2. If 404/405: Try GET <host>/sse (Legacy SSE probe)
   Parse for event: endpoint frame
   Then POST to endpoint URL with initialize

3. If 400/401: Record auth state, probe /.well-known/oauth-protected-resource

4. On valid result: Send notifications/initialized, then tools/list
   POST /mcp with: {"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}
   Include MCP-Session-Id if returned during initialize
   Include MCP-Protocol-Version: <negotiated-version>

5. Verify 3-conjunct match; classify as UNAUTH or AUTH_CONFIGURED
```

### Common Non-Standard Endpoint Paths (wild observation)

In addition to `/mcp` and `/sse`, operators deploy at: `/api/mcp`, `/v1/mcp`, `/mcp/sse`, `/chat/mcp`, `/`, `/api`. The backward-compatibility probe (POST first, fallback to GET for SSE) per spec section "Backwards Compatibility" handles this automatically.
