# Model Context Protocol (MCP) Servers: Cross-Cloud Survey (2026-05)

_NuClide Research · 2026-05-04 (in progress)_

> **Status:** Cross-cloud discovery complete (Scaleway + OVH + Linode tier-2 = 1,017 prefixes / ~6.33M IPs). 95 confirmed MCP servers, 28 with non-empty `tools/list`. Synthesis below.

---

## Premise

Model Context Protocol (MCP) was published by Anthropic in late 2024 as a standard for connecting LLMs to tools, filesystems, and databases. The protocol was designed for **stdio (in-process) transport**, but the ecosystem rapidly pushed toward **HTTP+SSE** for remote access. Operators wiring filesystem, shell, database, and cloud-API tools into MCP servers and exposing them without authentication replays the unauthenticated-RPC failure pattern at the protocol layer, a 1990s-era exposure category with a 2025 label.

The auth-on-default thesis (`SYNTHESIS-2026-05.md`) predicts: where the framework defaults to no-auth (which most MCP server templates do, they assume stdio-only), the population-scale deployment will be unauthenticated.

---

## Methodology

### Discovery vectors

MCP discovery is heterogeneous (no canonical port, multiple transports, multiple deployment modes). This survey covers four vectors in parallel:

1. **Tier-2 cloud masscan**, Scaleway (7) + OVH (33) + Linode (36) = 76 prefixes ≈ 3.55M IPs, scanning ports 3000, 8000, 8080, 8888 (the most common MCP-host ports per `shodan/queries/10-mcp-servers.md`).
2. **Shodan dorks**, 8 fingerprints already documented in `shodan/queries/10-mcp-servers.md`. (Limited by current credit availability.)
3. **Cloudflare Workers cert-transparency**, many MCP servers ship as Cloudflare Workers (`*.workers.dev`); CT log enumeration finds candidate hostnames.
4. **GitHub code search**, public repos referencing deployed MCP server URLs; `awesome-mcp-servers` lists; ngrok/tunnel exposures committed in config files.

### Probe

`data/mcp-probe.py` performs a JSON-RPC `initialize` handshake at four candidate paths (`/`, `/sse`, `/mcp`, `/message`) per host. A response is confirmed MCP only if it contains:

- `protocolVersion` in the initialize result, OR
- `serverInfo.name` matching MCP-server patterns, OR
- A subsequent `tools/list` returning an array of `{name, description}` objects

Capabilities, server name/version, and the full tool list (capped at 50 per host) are captured as JSONL.

### Filters

- **AS63949 honeypot fleet**, apply the `~/Tools/honeypot-detector.py` filter (393-host Akamai/Linode honeypot fleet documented in `reference_as63949_honeypot_fleet`).
- **Authentication-required servers**, record presence (auth-on) but exclude from "exposed-tools" classification.
- **Self-hosted vs Cloudflare Workers**, separate buckets, since Workers have per-Worker auth posture and a different operator-population profile.

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

_Cross-cloud final as of 2026-05-04 19:30 UTC. All three providers complete._

| Source | Prefixes | IPs scanned | Masscan hits | Confirmed MCP | Confirmation rate |
|---|---|---|---|---|---|
| Scaleway (AS12876) | 156 CIDRs | 574,720 (deduped) | 17,115 | **9** | 0.05% |
| OVH (AS16276) | 766 CIDRs | 4,387,072 | 209,397 | **82** | 0.04% |
| Linode (AS63949 + AS48666) | 95 CIDRs | ~1.37M | 5,706 | **4** | 0.07% |
| **Total** | **1,017 CIDRs** | **~6.33M** | **232,218** | **95** | **0.04%** |

Confirmation rate is consistently low (0.04–0.07%) across providers. The remaining 99.96% of port-open hits are HTTP services that fail the JSON-RPC `initialize` handshake, non-MCP web apps, blockchain RPC nodes, generic JSON-RPC services lacking `protocolVersion` / `serverInfo`. **Linode-specific finding:** the AS63949 honeypot pollution rate that hit other surveys at 91.6% (Milvus tier-2) was only 1.1% on this MCP survey, because the strict JSON-RPC handshake gate is itself a stronger filter than the IP-based honeypot list. The protocol-shape check IS the filter for protocol-strict surveys.

### MCP-server population statistics (95-host snapshot)

| Metric | Value |
|---|---|
| Total confirmed MCP servers | 95 |
| Hosts with **non-empty** `tools/list` (real attack surface) | **28** (29.5%) |
| Hosts with empty `tools/list` (auth-gated, stub, or resource/prompt-only) | 67 (70.5%) |
| Hosts advertising `tools` capability | 95 (100%) |
| Hosts advertising `resources` capability | 45 (47%) |
| Hosts advertising `prompts` capability | 42 (44%) |
| Hosts advertising `experimental` capability | 38 (40%) |
| Hosts advertising `logging` capability | 26 (27%) |

---

## Tool-surface classification (cross-cloud, 95-host snapshot)

Across the 28 servers with non-empty `tools/list`:

| Class | Hosts | Notable examples |
|---|---|---|
| **Email / mailbox access** | 1 | **`51.75.128.16:3000` `gmail` v1.0.0, full Gmail mailbox CRUD (read/send/delete/batch_delete/download_attachment)** |
| **Operational telemetry** | 6 | 6× Netdata across providers (`execute_function`, `query_metrics`, sandboxed but unauth) |
| **Database / query** | 1 | `rmcp` v0.2.1 (Elasticsearch MCP proxy, `esql`, `search`, `list_indices`) |
| **AI memory / cognition** | 1 (+17 auth-gated) | hindsight-mcp-server v3.1.1, 29 tools (`retain`, `recall`, `mental_models` CRUD, `clear_memories`); 17 sibling instances auth-gated |
| **Identity / OAuth admin** | 3 | 3× Casdoor MCP, application-CRUD (`add_application`, `update_application`, `delete_application`) |
| **CRM / facility management** | 1 | **`188.165.203.72:8000` Alcy MCP Simple v3.2.0, 22-tool French CRM exposing client/work-order/intervention CRUD** |
| **Legal / regulatory RAG** | 1 | `15.235.43.173:8000` locus-juridico-rag v1.26.0, 31.2M-chunk Brazilian legal RAG with TCE-ES state-audit data |
| **Ad / media-buy management** | 1 | teknalab-adcp-server (`create_media_buy`, `log_event`, 12 tools) |
| **Domain analytics (LCA)** | 1 | volca v0.6.0 (18-tool Life-Cycle Assessment, ecoinvent/Agribalyse) |
| **Generic monitoring / utility** | 6 | brightwavess-monitor (×2, identical 10-tool clones), pointed-noize, koolfood-mcp, Simplicité Platform Assistant, brave-search-mcp-server |
| **News / web wrapper** | 2 | bytecode.news-mcp, brave-search-mcp-server |
| **Misc small surfaces** | 6 | tokenforges-tools (4 tools), mcp-typescript on vercel (2 tools), CobradorAPI (2 tools), mcp-web-tools-working, start-server, others |
| Filesystem (read/write) | 0 | none observed in cross-cloud sample |
| Shell / RCE (`run_command`, `bash`) | 0 | none observed |
| AWS/Slack-tagged cloud-API tools | 0 | none observed |

---

## Notable findings (cross-cloud)

### F0: Unauthenticated full Gmail mailbox MCP (CRITICAL: OVH)

**`51.75.128.16:3000`**, `gmail` v1.0.0, **19 tools**, all of them mutating mailbox state on the operator's own Gmail account:

```
send_email, draft_email, read_email, search_emails, modify_email, delete_email,
list_email_labels, batch_modify_emails, batch_delete_emails,
create_label, update_label, delete_label, get_or_create_label,
create_filter, list_filters, get_filter, delete_filter, create_filter_from_template,
download_attachment
```

This is functionally a backdoor into someone's Gmail mailbox. Any unauthenticated caller can read every email, search the mailbox, send messages as the operator, batch-delete entire conversations, download attachments, and configure filters that forward incoming mail elsewhere. The operator is presumably running this MCP server for their own AI client to drive, but exposed it on a public IP without any auth on the MCP transport. **Highest-impact finding in the survey to date.**

Disclosure: WHOIS the IP, identify the operator, contact directly. Likely a developer or solo operator running their own Claude/Cursor/IDE-MCP integration.

### F0a: Alcy MCP Simple: CRM/facility-management CRUD (CRITICAL: OVH)

**`188.165.203.72:8000`**, `Alcy MCP Simple` v3.2.0, **22 tools** wrapping what appears to be a French CRM/facility-management platform (alcy.fr, service-provider field-operations SaaS). Read tools include `search_clients`, `search_installations`, `search_ordre_mission` (work orders), `search_intervention`, `search_contact`, `search_user`, `get_entity_history`. **Mutate tools include `create_ticket`, `create_ordre_mission`, `create_intervention`, `patch_ticket`, `patch_ordre_mission`, `patch_intervention`.**

Effective unauth read+write access to customer-facing operational records: client list, installation database, work-order history, technician interventions, contracts. An attacker can also create fake work orders, modify existing tickets, or pull entire customer rolodex.

### F1: Unauthenticated `rmcp` Elasticsearch MCP proxy (HIGH: Scaleway)

**`212.47.253.45:8080`**, `rmcp` v0.2.1, exposing `esql`, `search`, `list_indices` as MCP tools.

The MCP layer is unauthenticated, meaning any unauthenticated caller can:

- Issue Elasticsearch ES|QL queries (full ES|QL grammar) against the operator's backing cluster
- Submit Query DSL via the `search` tool
- Enumerate all indices

This is functionally equivalent to an unauthenticated Elasticsearch endpoint, the MCP wrapper provides no auth boundary. Whatever data lives in the backing Elasticsearch cluster is queryable.

### F2: Three unauthenticated Netdata MCP servers

`163.172.44.20:8000`, `51.159.58.44:8000`, `62.210.217.194:8000`, three distinct Netdata builds (v2.10.0-84, -59, -54 nightlies) exposing 13 tools each:

- `list_metrics`, `query_metrics` (time-series telemetry)
- `execute_function`, Netdata's plugin-function executor; tool documentation enumerates `processes`, `network-connections`, `mount-points`, `systemd-services` as callable targets

Not arbitrary RCE (Netdata's `execute_function` is sandboxed to its plugin subsystem), but **unauthenticated infrastructure introspection**: hostnames, OS details, running process lists, active TCP connections, mounted filesystems, systemd unit state. Operationally useful for an attacker mapping target infrastructure.

### F3: Ad-tech MCP server with mutation tools

`163.172.134.54:3000`, `teknalab-adcp-server` v1.0.0, 12 tools spanning campaign creation, creative asset sync, budget modification, and conversion-event logging. Tools include `create_media_buy`, `log_event`, and other state-mutating operations. If the backing ad platform accepts MCP-driven calls without secondary auth, this is an ad-fraud / unauthorized-campaign-manipulation primitive.

### F4: `volca` LCA platform: read-only analytical exposure

`51.159.151.231:8080`, `volca` v0.6.0, 18-tool Life-Cycle Assessment server exposing ecoinvent / Agribalyse environmental databases. Lower risk class (read-only domain analytics), but the protocol-layer MCP negotiation happened on an unprotected port, same auth-failure pattern, lower-impact data class.

### F5: Three confirmed-MCP zero-tool servers (Scaleway-specific)

TrustGraph (195.154.210.102:8000), `textile-pgvector` (51.15.140.118:8000), and `cool` (51.15.53.156:3000) all responded to `initialize` with valid `protocolVersion` + `serverInfo` but returned empty `tools/list` arrays. All three advertised `tools.listChanged` capability. Possible interpretations: tools registered dynamically and not yet announced to the unauthenticated probe; servers that expose only `resources/` or `prompts/` rather than tools; partially-configured deployments with broken tool-registration paths.

These count as MCP exposures (server identity disclosed) but represent no immediate tool-call attack surface. **At cross-cloud scale, this pattern is the majority: 67 of 95 confirmed servers (70.5%) returned empty `tools/list`**, most likely the auth-gated case (the server initializes anonymously per spec but gates tool listing on credentials).

### F6: `hindsight-mcp-server` cluster: fleet adoption + 1 fully-exposed instance (HIGH: OVH)

**18 instances** of `hindsight-mcp-server` (mostly v3.2.4, some v3.2.0) on port 8888 across OVH. 17 returned empty `tools/list` (auth-gated). **One instance, `92.222.230.219:8888` v3.1.1, returned a 29-tool list** covering full personal-AI-memory CRUD:

```
retain, recall, reflect, list_banks, create_bank, get_bank, get_bank_stats,
update_bank, delete_bank, clear_memories,
list_mental_models, get_mental_model, create_mental_model, update_mental_model,
delete_mental_model, refresh_mental_model,
list_directives, create_directive, delete_directive,
list_memories, get_memory, delete_memory,
list_documents, get_document, delete_document,
list_operations, get_operation, cancel_operation, list_tags
```

The operator's entire AI-cognition state, memories, mental models, directives, documents, readable and destructible (`clear_memories`, `delete_bank`) by any unauthenticated caller. The 17 sibling instances suggest hindsight-mcp-server is a popular open-source project with viral self-host adoption; the version-3.1.1 outlier is likely an older deployment that pre-dates an auth-gating fix in v3.2.x.

### F7: `Casdoor MCP Server`: recurring IAM/OAuth-CRUD pattern across providers (HIGH)

Three confirmed instances across Linode + OVH:

- `139.162.50.110:8888` (Linode)
- `141.95.127.178:8000` (OVH)
- `51.195.82.158:8000` (OVH)

All three identical: **`Casdoor MCP Server` v1.0.0, 5 tools**, `get_applications`, `get_application`, `add_application`, `update_application`, `delete_application`. Casdoor is an OAuth 2.0 / SSO identity platform; the MCP wrapper exposes full application-registration CRUD. An attacker can enumerate registered OAuth applications, modify their redirect URIs (account-takeover vector if attacker controls the redirect), or delete them.

This is the survey's clearest cross-provider pattern, same MCP server template, same auth failure, three independent operators. Disclosure to Casdoor maintainers about the upstream template's auth-off-default would mitigate future deployments.

### F8: `locus-juridico-rag`: Brazilian legal RAG with state-audit data (HIGH: OVH)

**`15.235.43.173:8000`**, `locus-juridico-rag` v1.26.0, 8 tools fronting a 31.2M-chunk Brazilian legal corpus. Description: "Busca híbrida semântica (Dense Voyage + BM25 sparse com RRF fusion + Voyage rerank) em 31.2M+ chunks jurídicos brasileiros."

Tools: `search_juridico`, `buscar_precedentes` (precedents), `analisar_caso` (case analysis), `comparar_entendimentos` (compare interpretations), `buscar_norma` (find legal norms), `search_tcees` (TCE-ES = Tribunal de Contas do Estado do Espírito Santo, the State Audit Court of Espírito Santo), `get_document`, `rag_stats`.

The TCE-ES indexing implies the operator has access to (or a license for) state-audit-court records, government accountability data. If this is a commercial legal-AI product, exposed unauth means competitor legal-research firms can free-ride on the operator's indexed corpus + Voyage embedding compute.

### F9: `Simplicité Platform Assistant` (HIGH: OVH)

**`213.32.74.24:8000`**, Simplicité is a French low-code platform (simplicite.io). The MCP server v1.26.0 exposes 7 tools wrapping the operator's internal Simplicité business-application API. Attack surface depends on which entities the operator has registered as Simplicité objects.

### F0b: Second Gmail-MCP server (auth-gated stub): OVH

**`51.222.84.103:3000`**, `Gmail-MCP` v1.7.4. `initialize` returns valid `serverInfo`, but `tools/list` returns empty. Likely the same template as the F0 finding (`51.75.128.16:3000`), but this operator either has auth gating enabled or hasn't loaded credentials. Confirms that "Gmail MCP server" is a recognizable open-source project pattern with multiple deployments, F0 is not an isolated incident, just the only one in this sample where the operator failed to gate `tools/list`.

### F11: MySQL MCP capabilities-object schema leak (HIGH: OVH; novel methodology insight)

**`51.91.31.191:8000`**, `@benborla29/mcp-server-mysql` v2.0.1. `tools/list` returned empty, but the `capabilities` field of the `initialize` response carried the **full `mysql_query` tool schema embedded as a structural element**, marked READ-ONLY. The probe could see:

- A live MySQL backend is wired into the MCP server
- `mysql_query` is the available tool (read-only mode)
- The schema's parameter shape (query string + connection identifier)

Even with `tools/list` returning empty (auth-gated for tool *invocation*), the **handshake itself leaks the existence + shape of the tools the operator has registered**. This is a methodology insight worth flagging across the survey: the probe should capture not just `tools/list` but also `serverInfo.capabilities` deeply, server identity, registered-tool count, and sometimes tool schemas leak at the unauthenticated handshake layer regardless of `tools/list` gating.

### F12: `brightwavess-monitor`: Cloudflare DNS CRUD with operator API key baked in (HIGH: OVH)

**Two instances**, identical 10-tool surfaces:

- `15.235.109.186:3000`
- `158.69.194.62:3000`

Both expose:

- `check_uptime`, `check_db_health` (monitoring tools)
- `cloudflare_list_dns_records`, `cloudflare_create_dns_record`, `cloudflare_update_dns_record`, `cloudflare_delete_dns_record`, **full DNS CRUD**
- Slack alerting tools

The operator's **Cloudflare API key is baked into the MCP server config**. Any unauthenticated caller can list, create, update, or delete DNS records on whatever Cloudflare zone(s) the operator's key authorizes, a domain-takeover primitive (point A records or NS records to attacker-controlled infrastructure, then catch all traffic to the operator's domains). Two instances suggest either one operator running a fleet or a popular monitoring template adopted by multiple operators with shared deployment pattern.

### F10: Recurring telemetry-server pattern: 6× Netdata (MEDIUM)

Six Netdata MCP server instances across Scaleway (3) and OVH (3), all identical 13-tool surfaces (`list_metrics`, `query_metrics`, `execute_function`). Different Netdata builds (v2.10.0-54-nightly, -59, -84, -90; one v2.10.3 release). The fleet pattern matches the hindsight pattern, a popular open-source MCP that operators self-deploy with default-no-auth.

`execute_function` is sandboxed to Netdata's plugin subsystem (not arbitrary RCE), but enumerates running processes, network connections, mount points, and systemd services without authentication. Operational reconnaissance primitive.

---

## Cross-provider pattern synthesis

Five distinct patterns emerge across the 95-host snapshot:

1. **Single-operator catastrophic exposures.** The Gmail MCP (F0) and Alcy CRM (F0a) findings show that individual developers running their own MCP servers for personal AI-tool integration are exposing them on public IPs with no auth. The operator's intent, "this is a private tool for my Claude Desktop", collides with the deployment reality of binding to `0.0.0.0`. The blast radius for these exposures is bounded by the single operator's data, but the data itself is intimate (a personal mailbox, a customer rolodex, a state legal corpus).

2. **Fleet-deployed open-source MCP with auth-off-default templates.** The 18× hindsight, 6× Netdata, 3× Casdoor, 13× supabase, 4× dual-graph-mcp clusters all show the same pattern: a popular open-source MCP server template that ships without auth on its `tools/list` endpoint by default, adopted by multiple independent operators, all of whom inherit the auth failure. The fix here is upstream, the template authors enabling auth by default, rather than per-operator disclosure.

3. **The 70/30 auth split.** 67 of 95 confirmed servers (70.5%) returned empty `tools/list` despite advertising the `tools` capability. The most parsimonious explanation: many MCP server frameworks gate `tools/list` behind authentication while still allowing the unauth `initialize` handshake (consistent with the protocol spec's separation of capability negotiation from authorized operations). The 28 (29.5%) with non-empty lists are the genuine attack surface; the 67 are confirmed MCP exposures with server identity disclosed but no immediate tool-call vector.

4. **Identity / IAM-platform MCP wrappers as a recurring high-risk class.** Casdoor (3 instances) is the explicit example, but the broader pattern is "MCP wrapping an admin-CRUD API." `Alcy MCP Simple` (F0a) is the same shape applied to a CRM platform. The pattern: an internal admin API with reasonable auth at the application layer gets re-fronted by an MCP server with no auth, and the operator forgets the MCP transport is now the weakest link.

5. **The protocol-shape filter is the strongest filter.** Linode's AS63949 honeypot fleet polluted the Milvus tier-2 survey at 91.6% but contributed only 1.1% noise to this MCP survey, because the strict JSON-RPC `initialize` handshake (with required `protocolVersion` + `serverInfo` markers) cannot be satisfied by the honeypot's generic-JSON mimicry. **For protocol-strict surveys, the protocol gate is itself the honeypot filter.**

---

## Threat classes

1. **Tool-surface exfil**, `tools/list` enumerates the operator's MCP tool definitions, leaking the structure of their internal automation.
2. **Credential exposure in tool definitions**, many operators bake API tokens into their MCP server configs (Slack tokens, GitHub PATs, AWS keys); these are sometimes visible in tool-call schemas or default-argument fields.
3. **Direct execution**, when filesystem / shell / database tools are exposed, the MCP server is effectively an unauthenticated RPC API onto the host.
4. **Compute-theft / proxy-abuse**, when web-fetch tools are exposed, attackers route scraping or credential-stuffing through the operator's IP.
5. **Memory / context exfil**, agent stacks that persist conversation history through MCP memory tools expose those histories.

---

## Honest negative space

- **Stdio-transport MCP is invisible to network scanning.** The bulk of MCP usage is local-only (Claude Desktop, Cursor, etc.) and never network-exposed. This survey only enumerates the HTTP+SSE deployment subset.
- **Authenticated MCP servers** that require Bearer tokens or other auth on the initialize handshake will appear as "no MCP detected" in our probe. We may underestimate authenticated-MCP population.
- **Cloudflare Workers** can host MCP servers behind Cloudflare Access (zero-trust auth); these will return HTTP-level auth challenges before the JSON-RPC handshake. We classify these as "auth-on" but don't enumerate their tools.
- **MCP-targeted honeypot in the wild**: `158.69.205.58:8000` self-identifies as `MCP Honeypot` v1.0.0, a deliberate-deception MCP server returning valid `initialize` + empty `tools/list`. Confirms that MCP scanning has reached the awareness threshold where defenders are deploying decoys against it. Excluded from confirmed-finding counts; noted as a research artifact.
- **Tool-schema leakage via the `capabilities` field** (see F11), at least one MCP server template (the MySQL connector) carries tool schemas in the `initialize` response's `capabilities` object even when `tools/list` is gated. Other server templates may have similar handshake-time disclosures we did not capture in this survey's snapshot. A future deeper-probe pass should fully traverse the `capabilities` JSON-tree, not just enumerate `tools/list`.

---

## Disclosure plan

For each unauthenticated MCP server with high-risk tool classes (shell, filesystem, database, credential-baked cloud-API), draft a coordinated-disclosure email per the standard NuClide template. Where the server's tool-list reveals operator identity (e.g., `slack_send_to_<workspace>`), pursue direct operator contact via WHOIS / cert-pivot.

---

## See also

- [`shodan/queries/10-mcp-servers.md`](../../shodan/queries/10-mcp-servers.md), pre-existing MCP fingerprint scaffolding
- [`reference/terminology.md`](../../reference/terminology.md), MCP definition + LLMjacking context
- [`SYNTHESIS-2026-05.md`](SYNTHESIS-2026-05.md), companion cross-survey synthesis
- [`FUTURE-SURVEYS.md`](FUTURE-SURVEYS.md), broader unsurveyed roadmap
- [`data/mcp-probe.py`](../../data/mcp-probe.py), JSON-RPC handshake probe used for this survey
