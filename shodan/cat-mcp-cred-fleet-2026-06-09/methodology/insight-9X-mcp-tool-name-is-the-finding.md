# Candidate Insight #9X - MCP tool names are the finding; the carrier shape can mask the backend

**Status:** candidate (awaits canon assignment in `~/.claude/nuclide-internal/METHODOLOGY.md` insight ledger)
**Surfaced by:** Cat-Tabby + Devstral 2026-06-09 / Cat-MCP-Cred-Fleet 2026-06-09
**Sample:** 66 hosts (AWS multi-region, port 9090)

## The pattern

The Cat-Tabby aimap fingerprint matched a 14-byte `<title>Tabby` literal that ALSO appeared as a transient Next.js SPA chrome on 66 unrelated hosts. Hardening the FP by tightening the title-window match removed Tabby FPs but did NOT remove the underlying surface: those 66 hosts run `mcp-server 1.0.1` on the same port (9090, /mcp), exposing five tools whose **names alone** classify the surface as credential-theft + arbitrary-code-execution risk:

- `get_aws_admin_credentials`
- `get_aws_session_credentials`
- `get_ssh_session_credentials`
- `add_cron_job`
- `schedule_commands`

The L7 layer in front of /mcp is a **deception fleet wearing harvested service masks**: ComfyUI, FortiSwitch, ServiceNow, Mirth Connect, Cisco SD-WAN, Roku UPnP, Sun-ILOM, Apache ActiveMQ, n8n, Flowise, EasyIO Sedona DCS, BBC HP OpenView, 50+ distinct cert issuers. A scanner that matches on /v1/health, /, Server header, title, or cert CN gets routed to a different "false" classification on every host. The MCP backend is uniform; only the front is heterogeneous.

## The lesson

When the carrier-shape fingerprint fires but the vendor-specific health check does not return 200, the carrier shape may be **deception chrome covering a different, more critical backend on the same port**. The single-port assumption (one service per port) is wrong by default on AI/agent infrastructure, where multiple protocol layers commonly cohabit.

## The rule (candidate codification)

> For any host where the carrier-shape fingerprint matches on probe-1 (HTML/SPA title or Server header) but the vendor-specific endpoint (`/v1/health`, `/version`, `/info`, `/_status`) does NOT return a vendor-confirming 200, **also issue a protocol-strict MCP `initialize` probe to the same port at `/mcp`, `/sse`, `/`, `/rpc`**. If the initialize handshake succeeds, the host carries an MCP backend regardless of what the front-end purports to be; tools/list is the load-bearing schema read; tool **names** are the finding.

## Why this matters

1. **MCP tool names are self-describing capability declarations.** The MCP spec REQUIRES servers to publish tool name + description + inputSchema on `tools/list`. Names like `get_aws_admin_credentials` are the operator's own classification of risk; no `tools/call` is needed to know what the surface is.
2. **The Tabby-class FP is a discovery affordance, not a noise source to silence.** The shadow-port sweep that lands on port 9090 surfaces the MCP backend only because the Tabby fingerprint overmatches first. Hardening to suppress the carrier-shape match without also probing the MCP shape on the same port WOULD HAVE DROPPED these 66 critical hosts from disclosure entirely.
3. **Schema is restraint-clean.** The full critical classification is achievable with `initialize` + `tools/list` (read-only metadata). `tools/call` crosses the ethical-stop boundary. This is the high-depth / low-breadth posture (Insight #68).

## Generalization

This is the AI-infra analog of the OT lesson: **port labels lie; protocols don't**. On Modbus or DNP3, you fingerprint the protocol envelope, not the service banner. On MCP, you fingerprint the JSON-RPC envelope and the tools schema, not the SPA chrome or the Server header.

## Action items for aimap

1. Add MCP `initialize` probe as a **secondary fingerprint** triggered on any port where the primary fingerprint matches but the vendor-confirming endpoint does not (i.e., suspected mask). Candidate ports: 9090, 8000, 8080, 3000, 5000, 8443.
2. Track `(carrier_shape, mcp_backend_present)` pairs in the corpus. Repeated co-occurrence is a coordinated-fleet signal.
3. Treat MCP `tools/list` tool-name strings as a classifier feature: train a lightweight critical/non-critical scorer on the name string + description, using the bag-of-fields sensitivity classifier discipline from the schema-recon skill.

## Audit trail

- 3-host sample on 2026-06-09 17:35 PT showed identical 5-tool exposure (Lane B regression test)
- 66-host cohort confirmed 100% identical exposure (this case study)
- Cisco MCP scanner YARA mode used as cross-check on one host

## Insight number

Assignment deferred to canon merge. Suggested wording for the canon entry:

> **Insight #9X. MCP backend can hide behind L7 deception chrome on the same port. When a carrier-shape fingerprint matches but the vendor-confirming health endpoint does not, probe the same port for MCP `initialize` shape at `/mcp`, `/sse`, `/`, `/rpc`. Tool names from `tools/list` ARE the finding; `tools/call` is the ethical-stop boundary.**
