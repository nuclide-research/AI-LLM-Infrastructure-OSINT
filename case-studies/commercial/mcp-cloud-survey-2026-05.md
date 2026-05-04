# Model Context Protocol (MCP) Servers — Cross-Cloud Survey (2026-05)

_NuClide Research · 2026-05-04 (in progress)_

> **Status:** Methodology + scaffolding complete. Discovery scan in progress. Synthesis section will fill as data lands.

---

## Premise

Model Context Protocol (MCP) was published by Anthropic in late 2024 as a standard for connecting LLMs to tools, filesystems, and databases. The protocol was designed for **stdio (in-process) transport** — but the ecosystem rapidly pushed toward **HTTP+SSE** for remote access. Operators wiring filesystem, shell, database, and cloud-API tools into MCP servers and exposing them without authentication replays the unauthenticated-RPC failure pattern at the protocol layer — a 1990s-era exposure category with a 2025 label.

The auth-on-default thesis (`SYNTHESIS-2026-05.md`) predicts: where the framework defaults to no-auth (which most MCP server templates do — they assume stdio-only), the population-scale deployment will be unauthenticated.

---

## Methodology

### Discovery vectors

MCP discovery is heterogeneous (no canonical port, multiple transports, multiple deployment modes). This survey covers four vectors in parallel:

1. **Tier-2 cloud masscan** — Scaleway (7) + OVH (33) + Linode (36) = 76 prefixes ≈ 3.55M IPs, scanning ports 3000, 8000, 8080, 8888 (the most common MCP-host ports per `shodan/queries/10-mcp-servers.md`).
2. **Shodan dorks** — 8 fingerprints already documented in `shodan/queries/10-mcp-servers.md`. (Limited by current credit availability.)
3. **Cloudflare Workers cert-transparency** — many MCP servers ship as Cloudflare Workers (`*.workers.dev`); CT log enumeration finds candidate hostnames.
4. **GitHub code search** — public repos referencing deployed MCP server URLs; `awesome-mcp-servers` lists; ngrok/tunnel exposures committed in config files.

### Probe

`data/mcp-probe.py` performs a JSON-RPC `initialize` handshake at four candidate paths (`/`, `/sse`, `/mcp`, `/message`) per host. A response is confirmed MCP only if it contains:

- `protocolVersion` in the initialize result, OR
- `serverInfo.name` matching MCP-server patterns, OR
- A subsequent `tools/list` returning an array of `{name, description}` objects

Capabilities, server name/version, and the full tool list (capped at 50 per host) are captured as JSONL.

### Filters

- **AS63949 honeypot fleet** — apply the `~/Tools/honeypot-detector.py` filter (393-host Akamai/Linode honeypot fleet documented in `reference_as63949_honeypot_fleet`).
- **Authentication-required servers** — record presence (auth-on) but exclude from "exposed-tools" classification.
- **Self-hosted vs Cloudflare Workers** — separate buckets, since Workers have per-Worker auth posture and a different operator-population profile.

### Tools-classification taxonomy

For each confirmed exposed MCP server, classify the *kind* of tools exposed:

| Class | Examples | Risk |
|---|---|---|
| **Filesystem** | `read_file`, `write_file`, `list_directory` | Direct host file read/write |
| **Shell / command-exec** | `run_command`, `bash`, `python` | Remote code execution on operator's host |
| **Database** | `query`, `execute_sql` | Data exfil from operator's databases |
| **Cloud-API wrapper** | `aws_*`, `gcp_*`, `slack_send`, `gmail_*` | Operator credentials abuse via service tokens baked into MCP server |
| **Code-search / repo** | `search_code`, `get_file_contents` | Private-repo content access |
| **Web / scraping** | `fetch_url`, `web_search`, `screenshot` | Compute-theft + IP-reputation abuse |
| **Internal API** | Custom operator endpoints | Operator's internal business logic exposed |
| **Memory / context** | `get_memory`, `search_history` | Conversation-history exfil |

---

## Discovery results

_(populated as masscan + probe pipeline completes)_

| Source | Hits | MCP-confirmed | Auth-on | Auth-off |
|---|---|---|---|---|
| Scaleway tier-2 (7 prefixes) | TBD | TBD | TBD | TBD |
| OVH tier-2 (33 prefixes) | TBD | TBD | TBD | TBD |
| Linode tier-2 (36 prefixes) | TBD | TBD | TBD | TBD |
| Shodan fingerprints | TBD | TBD | TBD | TBD |
| Cloudflare Workers CT | TBD | TBD | TBD | TBD |
| GitHub code search | TBD | TBD | TBD | TBD |
| **Total unique** | TBD | TBD | TBD | TBD |

---

## Tool-surface classification

_(populated)_

| Class | Hosts exposed | Notable examples |
|---|---|---|
| Filesystem | TBD | TBD |
| Shell | TBD | TBD |
| Database | TBD | TBD |
| Cloud-API wrapper | TBD | TBD |
| Code-search / repo | TBD | TBD |
| Web / scraping | TBD | TBD |
| Internal API | TBD | TBD |
| Memory / context | TBD | TBD |

---

## Notable findings

_(populated)_

---

## Threat classes

1. **Tool-surface exfil** — `tools/list` enumerates the operator's MCP tool definitions, leaking the structure of their internal automation.
2. **Credential exposure in tool definitions** — many operators bake API tokens into their MCP server configs (Slack tokens, GitHub PATs, AWS keys); these are sometimes visible in tool-call schemas or default-argument fields.
3. **Direct execution** — when filesystem / shell / database tools are exposed, the MCP server is effectively an unauthenticated RPC API onto the host.
4. **Compute-theft / proxy-abuse** — when web-fetch tools are exposed, attackers route scraping or credential-stuffing through the operator's IP.
5. **Memory / context exfil** — agent stacks that persist conversation history through MCP memory tools expose those histories.

---

## Honest negative space

- **Stdio-transport MCP is invisible to network scanning.** The bulk of MCP usage is local-only (Claude Desktop, Cursor, etc.) and never network-exposed. This survey only enumerates the HTTP+SSE deployment subset.
- **Authenticated MCP servers** that require Bearer tokens or other auth on the initialize handshake will appear as "no MCP detected" in our probe. We may underestimate authenticated-MCP population.
- **Cloudflare Workers** can host MCP servers behind Cloudflare Access (zero-trust auth); these will return HTTP-level auth challenges before the JSON-RPC handshake. We classify these as "auth-on" but don't enumerate their tools.

---

## Disclosure plan

For each unauthenticated MCP server with high-risk tool classes (shell, filesystem, database, credential-baked cloud-API), draft a coordinated-disclosure email per the standard NuClide template. Where the server's tool-list reveals operator identity (e.g., `slack_send_to_<workspace>`), pursue direct operator contact via WHOIS / cert-pivot.

---

## See also

- [`shodan/queries/10-mcp-servers.md`](../../shodan/queries/10-mcp-servers.md) — pre-existing MCP fingerprint scaffolding
- [`reference/terminology.md`](../../reference/terminology.md) — MCP definition + LLMjacking context
- [`SYNTHESIS-2026-05.md`](SYNTHESIS-2026-05.md) — companion cross-survey synthesis
- [`FUTURE-SURVEYS.md`](FUTURE-SURVEYS.md) — broader unsurveyed roadmap
- [`data/mcp-probe.py`](../../data/mcp-probe.py) — JSON-RPC handshake probe used for this survey
