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

_Scaleway preview pass complete (2026-05-04). OVH + Linode passes in flight; cross-cloud synthesis updates when both return._

| Source | Prefixes | IPs scanned | Masscan hits | Confirmed MCP |
|---|---|---|---|---|
| Scaleway (AS12876) | 156 CIDRs | 574,720 (deduped) | 17,115 (8080:7,313 / 8000:4,548 / 3000:2,910 / 8888:2,344) | **9** |
| OVH (AS16276) | TBD | TBD | TBD | TBD |
| Linode (AS63949 + AS48666) | TBD | TBD | TBD | TBD |
| **Total** | TBD | TBD | TBD | TBD |

Scaleway confirmation rate: **9 / 17,115 = 0.05%** of port-open hits resolve to a real MCP server. The remaining 99.95% are HTTP services that fail the JSON-RPC `initialize` handshake — non-MCP web apps, blockchain RPC nodes, generic JSON-RPC services that lack `protocolVersion` / `serverInfo`.

---

## Tool-surface classification (Scaleway preview)

| Class | Hosts | Notable examples |
|---|---|---|
| **Database / query** | 4 | `rmcp` (Elasticsearch — `esql`, `search`, `list_indices`); 3× Netdata (`query_metrics` time-series, sandboxed) |
| **Operational telemetry** | 3 | 3× Netdata (`execute_function` — `processes`, `network-connections`, `mount-points`, `systemd-services`) |
| **Ad / media-buy management** | 1 | teknalab-adcp-server (`create_media_buy`, `log_event`, campaign mgmt — 12 tools) |
| **Domain analytics (LCA)** | 1 | volca v0.6.0 (18-tool Life-Cycle Assessment — ecoinvent/Agribalyse) |
| **Empty `tools/list`** | 3 | TrustGraph, textile-pgvector, "cool" — MCP confirmed via `initialize` but `tools/list` returned empty (resource/prompt-only servers, or partial registration) |
| Filesystem (read/write) | 0 | none observed in Scaleway sample |
| Shell / RCE (`run_command`, `bash`) | 0 | none observed |
| Cloud-API wrapper (AWS / Slack / Gmail) | 0 | none observed |
| Web / scraping (`fetch_url`) | 0 | none observed |

---

## Notable findings (Scaleway preview)

### F1 — Unauthenticated `rmcp` Elasticsearch MCP proxy (HIGHEST RISK)

**`212.47.253.45:8080`** — `rmcp` v0.2.1, exposing `esql`, `search`, `list_indices` as MCP tools.

The MCP layer is unauthenticated, meaning any unauthenticated caller can:

- Issue Elasticsearch ES|QL queries (full ES|QL grammar) against the operator's backing cluster
- Submit Query DSL via the `search` tool
- Enumerate all indices

This is functionally equivalent to an unauthenticated Elasticsearch endpoint — the MCP wrapper provides no auth boundary. Whatever data lives in the backing Elasticsearch cluster is queryable.

### F2 — Three unauthenticated Netdata MCP servers

`163.172.44.20:8000`, `51.159.58.44:8000`, `62.210.217.194:8000` — three distinct Netdata builds (v2.10.0-84, -59, -54 nightlies) exposing 13 tools each:

- `list_metrics`, `query_metrics` (time-series telemetry)
- `execute_function` — Netdata's plugin-function executor; tool documentation enumerates `processes`, `network-connections`, `mount-points`, `systemd-services` as callable targets

Not arbitrary RCE (Netdata's `execute_function` is sandboxed to its plugin subsystem), but **unauthenticated infrastructure introspection**: hostnames, OS details, running process lists, active TCP connections, mounted filesystems, systemd unit state. Operationally useful for an attacker mapping target infrastructure.

### F3 — Ad-tech MCP server with mutation tools

`163.172.134.54:3000` — `teknalab-adcp-server` v1.0.0, 12 tools spanning campaign creation, creative asset sync, budget modification, and conversion-event logging. Tools include `create_media_buy`, `log_event`, and other state-mutating operations. If the backing ad platform accepts MCP-driven calls without secondary auth, this is an ad-fraud / unauthorized-campaign-manipulation primitive.

### F4 — `volca` LCA platform — read-only analytical exposure

`51.159.151.231:8080` — `volca` v0.6.0, 18-tool Life-Cycle Assessment server exposing ecoinvent / Agribalyse environmental databases. Lower risk class (read-only domain analytics), but the protocol-layer MCP negotiation happened on an unprotected port — same auth-failure pattern, lower-impact data class.

### F5 — Three confirmed-MCP zero-tool servers

TrustGraph (195.154.210.102:8000), `textile-pgvector` (51.15.140.118:8000), and `cool` (51.15.53.156:3000) all responded to `initialize` with valid `protocolVersion` + `serverInfo` but returned empty `tools/list` arrays. All three advertised `tools.listChanged` capability. Possible interpretations:

- Tools registered dynamically and not yet announced to the unauthenticated probe
- Servers that expose only `resources/` or `prompts/` rather than tools
- Partially-configured deployments with broken tool-registration paths

These count as MCP exposures (server identity disclosed) but represent no immediate tool-call attack surface.

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
