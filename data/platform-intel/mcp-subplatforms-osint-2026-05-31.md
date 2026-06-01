# MCP Sub-Platforms — Stage -1 Pre-Assessment OSINT (synthesis)

_2026-05-31 · survey workspace `recon/mcp-subplatforms-2026-05-31/`_

## Why this survey exists (not a re-run)

The generic MCP HTTP+SSE cross-cloud survey is **done** (`mcp-cloud-survey-2026-05.md`,
2026-05-04: 95 confirmed, 28 with exposed tools incl. a full Gmail mailbox MCP). This
survey targets the `not-yet` sub-platforms flagged in `FUTURE-SURVEYS.md` and the
**productization gap**: aimap had the MCP *fingerprint* (presence) but no *enumerator*
(auth-state + tool-surface). That gap is now closed — see "Tooling" below.

Detailed per-platform briefs (this directory):
- [`mcp-fastmcp-osint-2026-05-31.md`](mcp-fastmcp-osint-2026-05-31.md)
- [`mcp-proxy-osint-2026-05-31.md`](mcp-proxy-osint-2026-05-31.md)
- [`mcp-cloudflare-workers-osint-2026-05-31.md`](mcp-cloudflare-workers-osint-2026-05-31.md)
- [`mcp-protocol-primitive-2026-05-31.md`](mcp-protocol-primitive-2026-05-31.md) — load-bearing

## The auth-default gradient (the falsifiable test)

MCP sub-platforms sit at different points on the auth-on-default axis, so the survey
is a clean gradient test of the thesis:

| Sub-platform | Default auth | Tier | Thesis prediction |
|---|---|---|---|
| **sparfenyuk/mcp-proxy** | no auth concept at all (server-side) | A | ~100% unauth among HTTP-exposed |
| **FastMCP** | `auth=None` default; OAuth opt-in | A* | high unauth among HTTP/SSE-switched (Knostic: 119/119 sampled) |
| **Cloudflare Workers MCP** | open `remote-mcp-authless` quickstart template | C | mixed: authless-template forks open, OAuth path gated |
| **Official registry remote servers** | published SaaS, mostly Authorization/API-key | (C-tier auth) | mostly auth-gated → **contrapositive confirmation** |

Worst-case exposure (mcp-proxy fronting a shell/filesystem stdio server) = unauthenticated
OS command execution. Per the April-2026 OX Security disclosure, tool execution IS the
protocol; the only thing between a caller and the tool is whether auth wraps it.

## Verification primitive (current, dual-transport)

Spec revisions: 2024-11-05, 2025-03-26, 2025-06-18, 2025-11-25. Servers lag the spec, so
the scan handles **both** transports:
- **Streamable HTTP:** `POST /mcp`, `Accept: application/json, text/event-stream`, JSON-RPC
  `initialize`. Do NOT send `MCP-Protocol-Version` on the initialize POST (400s some servers).
- **Legacy SSE:** `GET /sse` → `endpoint` event → POST initialize.

3-conjunct identity matcher (the honeypot discriminator, Insight #1 + #16):
`endpoint reachable` + `valid JSON-RPC result` + `result.protocolVersion ∈ {closed spec-date
set}` AND `serverInfo.name` non-empty. Auth discrimination: `200 + populated tools/list` =
unauthenticated finding; `401/403 + WWW-Authenticate` (RFC 9728) = OAuth-configured, not a
finding.

## Discovery vectors

- **Self-hosted (Shodan, Playwright):** `http.headers:"mcp-session-id"` (LOW FP — nothing
  outside the MCP SDK emits it), `http.html:"server_instances" http.html:"api_last_activity"`
  (sparfenyuk mcp-proxy, LOW FP), `"FastMCP" "uvicorn" port:8000`. The core unauth population.
- **Registry-published remote (primary source):** `registry.modelcontextprotocol.io/v0/servers`
  (cursor-paginated, `remotes[].url` + `remotes[].type`); Glama/PulseMCP/mcp.so directories.
- **Cloudflare Workers:** `*.workers.dev` is a CT dead-end (shared wildcard); custom-domain
  `crt.sh/?q=%25.mcp.%25` is pivotable; GitHub code search of committed `.mcp.json` configs.
- **Censys delta** + ledger cross-reference.

## Tooling — productization closed (aimap v1.9.45)

`enumMCP` (committed `4fa3e69`): runs the active `initialize` handshake (Streamable HTTP +
SSE fallback, SSE-unwrapping, root/path fallbacks), gates on protocol-shape conformance,
enumerates `tools/list`, classifies auth state, and scores the tool-name set with a
bag-of-fields severity classifier (`execute_command`/`write_file`/`kubectl`/`get_secret` →
critical; fs-read/database → high; network → medium). sparfenyuk/mcp-proxy identified by its
vendor-unique `/status` `server_instances` map. **Restraint (schema-recon):** names,
descriptions, and input schemas only — `tools/call` and `resources/read` are never invoked;
findings carry `data_accessed: false`, with an end-to-end test asserting the no-invocation
guarantee. This makes the survey's verification stage deterministic (the manual→productize→
re-run discipline; the 05-04 survey enumerated tools by hand).

## Negative space (what this method cannot see)

- Cloudflare Workers MCP at `*.workers.dev` is largely Shodan-dark and CT-dark; the registry
  + GitHub-config vectors are partial substitutes, not population coverage.
- stdio-only MCP servers (the design-intended transport) are not network-reachable by
  construction and are out of scope — only HTTP/SSE-exposed servers are measurable.
- The closed protocolVersion gate will miss a spec-non-conformant real server (FN), the
  deliberate trade for honeypot rejection (Insight #1).
