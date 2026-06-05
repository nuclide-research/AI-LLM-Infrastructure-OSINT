# Insight #77 — Passive Shodan is an MCP crypto-sieve; the lifecycle handshake is the depth-gate

**Survey:** MCP server population survey, 2026-06-02.

## Statement

Two coupled facts govern any MCP population survey:

1. **Discovery: MCP is Shodan-dark on passive banners.** The protocol's identifying
   content (`result.protocolVersion` + `serverInfo` + `capabilities`) appears only in
   the *response to a POSTed `initialize` request*. A spec-compliant Streamable-HTTP
   server returns `405`/`400` with no MCP-identifying body to the unsolicited GET that
   Shodan/Censys crawlers send. So passive dorks that target the `initialize` *response*
   return ~0, while the only dork with real recall, `"jsonrpc":"2.0","error"`, returns a
   **crypto-mining-dominated false-positive superset** (Bitcoin/Ethereum RPC, IPFS, stratum
   pools all emit the same JSON-RPC error banner).

2. **Verification depth is gated by protocol completeness.** A one-shot `initialize` POST
   confirms *identity* but cannot enumerate *capability* on stateful servers: Streamable-HTTP
   requires the full lifecycle, `initialize` → capture `Mcp-Session-Id` →
   `notifications/initialized` → `tools/list`, carrying the session header. Skip it and the
   most dangerous servers report an empty tool list.

## Evidence

- Harvest: 4 productive dorks → 455 candidates. Free `count` sizing showed the precise
  conjunction (`"jsonrpc":"2.0" "serverInfo" "protocolVersion"`) = **1**, `"method":"initialize"`
  = **0**, while `"jsonrpc":"2.0","error"` = **376** and `Mcp-Session-Id` (bare) = **113,038**
  (FP-saturated, discarded).
- The 376-host lead dork was crypto by inspection: `miningrigrentals.com`, `coinomi.net`,
  IPFS port 5001, SMTP port 25.
- `mcp_verify.py` (conjunctive `initialize` probe) on 349 filtered candidates →
  **17 unauth MCP, 46 auth-gated (8 with MCP-style `WWW-Authenticate`), 286 not-MCP**. The
  286 are the crypto/IPFS/generic-JSON-RPC noise the dork dragged in. The verifier *is* the
  sieve that the dork is not.
- Depth-gate: the one-shot `tools/list` left 6 high-value servers reporting empty catalogs.
  The session-aware `mcp_enum.py` resolved them, including **Azure MCP Server** (declaring
  `keyvault`/`sql`/`role`/`subscription_list`) and **Salesforce MCP** (`query_soql`), both
  invisible to the one-shot probe.
- **Ledger-as-substrate corollary (same day):** re-running the verifier over a prior
  2026-05-15 MCP harvest (2,576 hosts, no new Shodan/Censys spend) yielded **83 unauth /
  72 net-new**, lifting the combined confirmed-unauth population to **89** (28 critical).
  The exposure class persisted across the 18-day gap. The data we already owned was
  under-extracted; the better verifier is what converted it into findings.

## Why this happens

MCP inverts the usual passive-fingerprint assumption. HTTP apps volunteer their identity
in the GET banner (titles, headers, HTML); MCP volunteers nothing until you speak its
JSON-RPC handshake, because the handshake *is* the protocol. And the handshake is a
multi-step lifecycle with server-side session state, so a single request is the wrong unit
of work, identity needs one POST, capability needs the full sequence. The `"jsonrpc","error"`
banner is the only thing that leaks passively, and it is shared by the entire JSON-RPC
universe (crypto being the largest exposed slice), so recall and precision pull apart.

## Methodological consequence

- **Do not size an MCP survey on Shodan passive counts.** They under-report real MCP
  (the precise dorks read ~0) and over-report via the crypto-laden error banner. Treat
  every dork hit as a candidate; the `initialize` conjunction is the only gate.
- **Censys leads the population.** Its `endpoint_type=MCP` label is an active-probe result
  (12–21k); Shodan only catches the chatty-banner tail. A Shodan-only MCP survey is a known
  floor, not the population.
- **Build the verifier with the full lifecycle from the start.** A one-shot `tools/list`
  silently under-enumerates the most severe servers. Enumeration that stops at
  `initialize` confirms existence; enumeration that completes the session confirms blast
  radius, and both stay on the correct side of restraint (`tools/list` is disclosure;
  `tools/call` is invocation and out of scope).

## Cross-references

- Insight #16 (a 200/identity is not auth state) — a 401 on `/mcp` is likewise not MCP
  identity; only the handshake conjunction and a MCP-style `WWW-Authenticate` confirm.
- Insight #15 (~50% dork-FP rule) — MCP is the extreme case: the lead dork is majority
  non-MCP.
- Insight #3 (the handshake leaks structure even when invocation is gated) — here the
  `initialize`/`tools/list` handshake leaks the full capability surface pre-auth.
- Case study / report: `recon/mcp-survey-2026-06-02/MCP-SURVEY-REPORT.md` (local; live IPs).
- Tools: `mcp_verify.py` (conjunctive probe), `mcp_enum.py` (session-aware enumerator).
