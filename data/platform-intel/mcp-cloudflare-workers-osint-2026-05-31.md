---
type: operational
category: mcp-cloudflare-workers
date: 2026-05-31
status: pre-assessment (Stage -1) complete; harvest pending
---

# MCP on Cloudflare Workers: Pre-Assessment OSINT

_NuClide Research, 2026-05-31. Stage -1 intelligence for Workers-hosted MCP server survey._
_Sources: Cloudflare Agents docs (primary), GitHub source, CVE databases, MCP registry APIs, security research (Knostic). No live probing._

---

## What This Is

Intelligence gathered before population scanning to answer the one question that blocked the prior MCP survey: Workers-hosted MCP servers are invisible to the cert-pivot and Shodan-banner approaches that surface every other category. This brief maps the enumeration vectors, then covers auth posture, fingerprint, secret-exposure class, and CVE surface.

Two deployment packages are in scope:
- **`workers-mcp`** (cloudflare/workers-mcp) — older adapter layer; transpiles Worker methods to Claude Desktop MCP tools via stdio proxy. Predates the Agents SDK; still in circulation.
- **`@cloudflare/agents` McpAgent** — current canonical SDK. `McpAgent` class extends `Agent`, exposes tools over streamable HTTP (primary) or SSE (legacy). Durable Objects backed. Used for all new deployments as of mid-2025.

---

## THE HARD PROBLEM: Enumeration Vectors

`*.workers.dev` is a Cloudflare-owned wildcard: one shared cert covers all `*.workers.dev` subdomains. crt.sh and Censys CT-log searches return nothing useful for individual worker subdomains. Shodan indexes Cloudflare-fronted hosts as Cloudflare infrastructure, not the origin Worker. Standard NuClide enumeration chains (cert-pivot, banner-grab-Shodan, TLS SAN sweep) do not apply here.

### Ranked Enumeration Vectors

#### 1. MCP Registries as Named-Server Substrate (HIGHEST YIELD, START HERE)

The registries are a pre-enumerated, self-reporting population. They contain both `*.workers.dev` URLs and custom domain URLs, with auth status and tool listings visible per-entry.

| Registry | Scale | API | Query |
|---|---|---|---|
| **Glama** | 21,000+ servers | `https://glama.ai/api/mcp/v1/servers/` (REST, cursor pagination) | Filter `type=remote` or keyword `cloudflare`/`workers` |
| **PulseMCP** | 11,840+ hand-reviewed | `https://www.pulsemcp.com/servers?other[]=remote` | Page through `remote` filter |
| **Smithery** | 7,000+ | REST API, page-based pagination | Filter `cloudflare` / `workers.dev` |
| **MCP.so** | 19,700+ | Structured JSON export | Query for `workers.dev` in endpoint URL field |
| **Official registry** | registry.modelcontextprotocol.io | Community-maintained | Check `remoteUrl` fields |

Glama already indexes labeled entries: "Remote MCP Server (Authless) on Cloudflare," "Remote MCP Server on Cloudflare," etc. Multiple authless forks of the Cloudflare template are listed. The registry data surfaces the deployed URL, transport type (SSE vs streamable-HTTP), tool list, and linked GitHub repo.

**Concrete action:** `curl 'https://glama.ai/api/mcp/v1/servers/?query=cloudflare+workers&limit=100'` then iterate cursor. Extract `remoteUrl` fields containing `workers.dev` or custom domains.

#### 2. GitHub Code Search for Deployed Config Files (HIGH YIELD, PARALLEL WITH #1)

Developers commit MCP client config files containing live `*.workers.dev` endpoints. These are not template placeholders; repos with committed configs have deployed servers.

**Exact GitHub search queries (run these):**

```
"workers.dev/sse" path:.cursor/mcp.json
"workers.dev/mcp" path:.cursor/mcp.json
"workers.dev" "mcpServers" path:claude_desktop_config.json
"workers.dev" "mcpServers" path:.mcp.json
"workers.dev/sse" "mcp-remote"
remote-mcp-server-authless workers.dev path:README.md
wrangler.toml McpAgent site:github.com
```

The pattern `remote-mcp-server-authless.<account>.workers.dev` appears in dozens of README files and config commits. Many repos were forked from `cloudflare/ai/demos/remote-mcp-authless` and deployed without modification. The account subdomain segment leaks the Cloudflare account slug.

**Concrete action:** GitHub code search API: `https://api.github.com/search/code?q="workers.dev/sse"+mcpServers&type=code`

#### 3. Custom Domains via Certificate Transparency (MEDIUM YIELD, VIABLE)

When an operator maps a custom domain (e.g., `mcp.example.com`, `api.tools.io`) to a Cloudflare Worker, Cloudflare issues an individual Advanced Certificate via Let's Encrypt, Google Trust Services, SSL.com, or Sectigo. All four are CT-logging CAs. These certificates appear in crt.sh.

The pivot problem: there is no reliable signal in the cert that identifies it as a Worker-hosted MCP server specifically. The cert just shows the domain. However:
- crt.sh query `%.mcp.%` or `mcp-server.%` returns custom domains with "mcp" in the hostname
- Cross-reference with Shodan HTTP response headers (`cf-ray` present + `/mcp` or `/sse` path in HTML)
- Knostic research (2025) found 1,862 MCP servers via Shodan; their fingerprints work for custom-domain Workers

**CT pivot query:** `https://crt.sh/?q=%25.mcp.%25&output=json` -- then filter for Cloudflare-issued certs (Let's Encrypt/Google Trust Services on domains resolving to Cloudflare ASN 13335).

#### 4. Shodan/Search-Engine Response Signature (LOWER YIELD, CLOUDFLARE FRONTING DEGRADES THIS)

Shodan sees the Cloudflare edge, not the Worker. However:
- `cf-ray` header is present on all Cloudflare responses; not Workers-specific
- MCP-protocol markers in HTTP responses: `"jsonrpc":"2.0"`, `"method":"initialize"`, `Content-Type: text/event-stream` at `/sse`
- Knostic's dork: `http.html:"mcp" content:"text/event-stream"` finds SSE endpoints
- Workers-specific marker: if the `Server:` header is absent or `cloudflare`, and `cf-ray` present, and response body matches MCP JSON-RPC, it is likely a Worker

**Shodan query candidate:** `http.html:"Model Context Protocol" http.headers:"cf-ray"`

Shodan coverage of Cloudflare-fronted hosts is inconsistent. This lane is useful for confirmation, not discovery.

#### 5. Cloudflare's Own Registry of Managed Servers (KNOWN-GOOD LIST, NOT FULL POPULATION)

Cloudflare operates 16 first-party MCP servers at `*.mcp.cloudflare.com/mcp`. All are OAuth-gated. These are not the target population but serve as fingerprint anchors -- their response structure (`serverInfo.name`, tool schemas) shows what a Workers-McpAgent response looks like.

---

## Auth Posture

**Default tier: B/C split — strongly biased toward unauthenticated in tutorials and templates.**

Cloudflare's documented quickstart explicitly starts with no auth: "deploy a public MCP server without authentication, then add user authentication later." The canonical authless template (`cloudflare/ai/demos/remote-mcp-authless`) ships open with no credential requirement. Dozens of forks are indexed on Glama and PulseMCP as explicitly "authless."

| Deployment path | Auth | Effective tier |
|---|---|---|
| `remote-mcp-authless` template (default quickstart) | NONE | C (open) |
| `remote-mcp-server-authless` (older workers-mcp demo) | NONE | C (open) |
| GitHub OAuth template (`remote-mcp-github-oauth`) | OAuth via workers-oauth-provider | A |
| Cloudflare Access integration | SSO/OIDC policy | A |
| Hand-rolled Worker with no auth | NONE | C (open) |

The ecosystem split: tutorial/demo deployments are overwhelmingly open; production deployments that followed the OAuth path are gated. The auth layer is opt-in, not default. This mirrors the Argo `--auth-mode=server` pattern -- secure mode requires affirmative configuration.

`workers-mcp` (the older package) has no auth layer at all. It relies on the Worker being deployed only to the operator's account. Public deployment of a `workers-mcp` server is fully open.

**No `tools/list` auth gate exists by default.** An unauthenticated McpAgent instance returns the full tool schema to any MCP `initialize` + `tools/list` sequence.

---

## Fingerprint

### Endpoint Paths

| Path | Transport | Notes |
|---|---|---|
| `/mcp` | Streamable HTTP (current standard) | `POST` for requests, `GET` for SSE stream. McpAgent default. |
| `/sse` | Server-Sent Events (legacy, still supported) | Used in all pre-2025 workers-mcp deployments; still in many live configs |
| `/mcp/sse` | Variant pattern | Seen in some third-party frameworks |

### Response Markers

- `Content-Type: text/event-stream` at `/sse`
- JSON-RPC 2.0 envelope at `/mcp`: `{"jsonrpc":"2.0","id":1,"result":{"serverInfo":{...}}}`
- `serverInfo.name` field: set by developer. Common values from template repos: `"demo-mcp-server"`, `"my-mcp-server"`, `"cloudflare-worker-mcp"`, `"remote-mcp-server-authless"`
- `cf-ray` header: present on all Cloudflare-proxied responses (edge, not origin)
- `Server: cloudflare` header (when present)
- `x-powered-by` absent (Workers do not inject this)
- McpAgent Durable Object hibernation: connection may drop and reconnect mid-session; fingerprint persists across reconnects

### Verification Probe

```
POST https://<host>/mcp
Content-Type: application/json

{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"probe","version":"0.1"}}}
```

Unauthenticated authless server returns `serverInfo` + `capabilities` immediately with HTTP 200. Authenticated server redirects to OAuth (`302` to `/authorize` or Cloudflare Access login page).

---

## API Surface and Secret-Exposure Class

Workers-based MCP servers wrap one or more Cloudflare bindings or third-party APIs. The binding model is the key exposure surface.

### Cloudflare Bindings (Cloudflare-native resources)

| Binding | Exposure when unauth |
|---|---|
| **KV Namespace** | Worker has full R/W on all keys in the bound namespace; MCP tools wrap KV ops |
| **D1 (SQLite)** | Worker runs arbitrary SQL against the bound database |
| **R2 (object storage)** | Worker reads/writes objects; tools may wrap bucket ops |
| **Durable Objects** | Stateful sessions; hibernated DO holds per-session state accessible to tools |
| **AI binding (Workers AI)** | Worker can invoke Cloudflare AI models with no per-call cost to the attacker |
| **Service bindings** | Worker-to-Worker RPC; expands blast radius to other internal Workers |

Cloudflare's security model embeds the binding permissions into the Worker runtime. The secrets (account credentials, binding tokens) are never in source code or `wrangler.toml`. **However: if the Worker is exposed without auth, the binding-granted capabilities are entirely delegable to any caller that can reach the `/mcp` endpoint.** The caller does not need the underlying credentials; they have Worker-proxy access to everything the binding permits.

### Third-Party API Keys via `wrangler secret put`

Operators bind external API keys (OpenAI, Stripe, database connection strings, GitHub tokens) as Worker secrets accessed via `env.MY_SECRET` at runtime. These never appear in source but are callable via any tool the MCP server exposes. An authless server wrapping an OpenAI key, a Postgres connection string, or a GitHub token provides full delegated API access to any caller.

This is the Insight #36 build-arg secret-baking analog: the secret is not in the artifact, but the artifact grants the capability. Unauth access to the artifact = full access to the capability.

### `tools/list` Data Leakage (Pre-Access Intel)

The MCP `tools/list` response exposes the full tool schema including parameter names, descriptions, and JSON Schema types. In operator-built Workers, tool descriptions frequently contain internal system architecture detail: database table names, internal API routes, service names, data classifications. No authentication required for `tools/list` on authless instances.

---

## CVEs and Prior Security Research

| ID | Package | Type | CVSS | Fixed |
|---|---|---|---|---|
| **CVE-2025-4143** | `@cloudflare/workers-oauth-provider` < 0.0.4 | Open redirect (no redirect_uri validation) | Medium | 0.0.4 |
| **CVE-2025-4144** | `@cloudflare/workers-oauth-provider` < 0.0.5 | PKCE bypass via downgrade attack | 5.3 | 0.0.5 |
| **CVE-2026-1721** | `@cloudflare/agents` < 0.3.10 | Reflected XSS in OAuth callback handler via `JSON.stringify()` escape | 6.2 | 0.3.10 |

**CVE-2025-4143 chain context:** Attacker crafts a malicious link to a known MCP server URL with an injected `url=` parameter. If the victim has previously authorized the client, workers-oauth-provider auto-approves and redirects credentials to the attacker's domain. Practical in phishing scenarios targeting MCP users.

**CVE-2025-4144 context:** PKCE is mandatory under OAuth 2.1 (which the MCP spec follows). Bypass allows authorization code interception without PKCE verifier. Fixed in 0.0.5 — operators running unpatched workers-oauth-provider are vulnerable even with auth enabled.

**CVE-2026-1721 context:** AI Playground OAuth callback rendered error messages unsanitized inside a `<script>` tag. `</script>` injection broke JSON context. Impact: steal LLM chat history, hijack connected MCP server sessions.

**Note on CVE-2026-23744** (MCP server memory corruption): sourced from a secondary aggregator with no primary advisory found. Flag as unverified; treat as unresolvable without primary CVE record.

**Knostic MCP scanner** (`github.com/knostic/MCP-Scanner`): independent research team mapped 1,862 MCP servers via Shodan in 2025 using 100+ filters. Their tooling and published dorks are the most developed prior art for MCP discovery at population scale. The NuClide survey should diff against their population.

---

## Deployment Patterns

### Template Names (Canonical — what operators clone)

```
cloudflare/ai/demos/remote-mcp-authless          # open, no auth
cloudflare/ai/demos/remote-mcp-github-oauth      # OAuth via GitHub
```

Deploy command: `npm create cloudflare@latest -- my-mcp-server --template=cloudflare/ai/demos/remote-mcp-authless`

### Worker Naming Convention

Default name from template: `remote-mcp-server-authless`. Operators frequently rename to describe their tool, e.g.:
- `my-mcp-server`
- `<company>-mcp`
- `<tool-name>-worker`
- `<username>-mcp-server`

Resulting URL: `<worker-name>.<account-slug>.workers.dev/mcp`

The account slug is a stable Cloudflare account identifier (not user-visible name). It appears in all `*.workers.dev` URLs for that account and leaks across all Workers the same operator deploys.

### `wrangler.jsonc` Signals

Authless deployments: minimal config, no bindings, no secrets. High-confidence signal of operator capability.

OAuth deployments require:
```json
{
  "kvNamespaces": [{"binding": "OAUTH_KV", "id": "<id>"}]
}
```
`OAUTH_KV` binding presence = workers-oauth-provider deployed = auth intended (but verify it is actually enforced -- misconfigured route patterns can bypass it).

---

## Ecosystem and Adjacent Surface

- **Cloudflare AI Playground** (`playground.ai.cloudflare.com`) -- web-based MCP client that connects to any remote MCP server via OAuth. Operators use it to test their Workers MCP servers. CVE-2026-1721 was in this component.
- **`mcp-remote`** npm package -- stdio-to-HTTP bridge; allows Claude Desktop (stdio-only) to reach remote MCP servers. Config embeds the `workers.dev` URL. Source of most committed config file leaks.
- **Cloudflare's 16 first-party MCP servers** -- all at `*.mcp.cloudflare.com/mcp`, all OAuth-gated. The Radar server (`https://radar.mcp.cloudflare.com/mcp`) is publicly accessible after OAuth and exposes internet traffic intelligence. The Workers Bindings server (`https://bindings.mcp.cloudflare.com/mcp`) exposes full KV/D1/R2 management to authenticated callers -- a compromise of the OAuth flow would be high-impact.
- **Durable Objects hibernation** -- WebSocket connections to McpAgent instances sleep between messages. An open persistent connection to an authless server costs the operator nothing in compute; it does not timeout or rate-limit passively. Long-lived unauthenticated sessions are operationally viable.

---

## Open Items / Unresolvable

- **CVE-2026-23744** (memory corruption in MCP server): no primary advisory located. Secondary source only. Do not rely on this finding.
- **Smithery hosted remote server** architecture: Smithery hosts some MCP servers itself (not just indexes them). Whether Smithery-hosted servers are Workers-backed or their own infra is not confirmed from primary sources. Treat as unknown.
- **Glama API pagination schema**: `https://glama.ai/api/mcp/v1/servers/` returned 400 on direct fetch (auth or CORS restriction). API schema unconfirmed from primary source. Route access through browser automation (Playwright) or authenticated session.
- **Rate limiting on authless Workers**: Cloudflare applies account-level rate limits. Unverified whether unauthenticated MCP endpoint requests are subject to the same limits as the deploying account or have a separate default. This affects deep-scan viability.
