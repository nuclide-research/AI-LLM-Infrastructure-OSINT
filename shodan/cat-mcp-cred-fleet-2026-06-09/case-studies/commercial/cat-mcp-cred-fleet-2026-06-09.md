# Cat-MCP-Cred-Fleet 2026-06-09: 66-host unauthenticated MCP credential-theft surface across AWS multi-region

**Date:** 2026-06-09
**Origin:** Cat-Tabby + Devstral session, Lane B regression-test escape
**Researcher:** Nicholas Kloster, NuClide Research
**Cohort:** 66 AWS EC2 IPs on port 9090
**Disclosure:** routing groundwork only; not sent

## Summary

While hardening aimap's Tabby fingerprint against a 14-byte `<title>Tabby` literal that was overmatching unrelated Next.js SPAs, Lane B's regression test caught an unexpected secondary classification: every Tabby false-positive on port 9090 also passed aimap's MCP-Server fingerprint with `auth_status=none`, `risk_level=critical`. Lane B's 3-host sample showed identical `mcp-server 1.0.1` instances exposing five high-criticality tools (`get_aws_admin_credentials`, `get_aws_session_credentials`, `get_ssh_session_credentials`, `add_cron_job`, `schedule_commands`).

This case study widens the scope from the 3-host sample to the full 66-host cohort, applies protocol-strict identity verification per Insight #1, and resolves whether the surface is a real-but-misconfigured single-operator deployment, an operator-by-operator deployment of a popular template, or coordinated deception infrastructure.

## Verification ladder (DCWF 672)

Protocol-strict probe per Insight #1: HTTP POST a fully-formed JSON-RPC `initialize` envelope to candidate endpoints (`/mcp`, `/sse`, `/`, `/rpc`) under both HTTPS and HTTP. Verify the response carries `jsonrpc=2.0`, `result.protocolVersion`, `result.serverInfo`, and `result.capabilities`. Follow with `tools/list` over the same session. Do not invoke `tools/call` (load-bearing ethical stop).

Results across 66 hosts:

| Field | Value | Count |
|---|---|---|
| init pass | true | 66/66 |
| scheme | https | 66/66 |
| path | /mcp | 66/66 |
| serverInfo.name | mcp-server | 66/66 |
| serverInfo.version | 1.0.1 | 66/66 |
| protocolVersion | 2025-06-18 | 66/66 |
| distinct toolsets | 1 (5 tools) | 66/66 |

Protocol shape is uniform across the cohort. Per the decision rule in the task brief, 100% `initialize` pass with identical tool sets evidences a **coordinated fleet**.

## Tool surface (DCWF 672 + 733 restraint)

All 66 hosts expose the same five tools:

| Tool | Description | Schema |
|---|---|---|
| get_aws_admin_credentials | Retrieve long-lived AWS admin credentials from the configured credential vault | `{}` (no params) |
| get_aws_session_credentials | Retrieve short-lived AWS session credentials | `{}` (no params) |
| get_ssh_session_credentials | Retrieve SSH session credentials | `{}` (no params) |
| add_cron_job | Schedule a cron job | params per inputSchema |
| schedule_commands | Schedule arbitrary commands | params per inputSchema |

Tool **names** alone classify this surface as credential-theft + arbitrary code execution. Per Insight #1 and the framework on metadata maximization, **names ARE the finding**: the MCP server publishes a self-describing surface that any LLM agent connecting via MCP would consume and act on. No `tools/call` was issued; doing so would either return real credentials (theft against the operator if honest), trigger a honeypot capture (red-team trap), or trigger a state change (`add_cron_job`, `schedule_commands` are state-changing by definition).

## Operator attribution (NICE 541)

- **rDNS:** 62/66 `compute.amazonaws.com`, 4/66 `compute-1.amazonaws.com` — 100% AWS EC2.
- **RDAP/WHOIS:** 100% Amazon entities across regional AWS subsidiaries (US, EU, AP, SA, AF, CA). 21 distinct regional org names; all roll up to Amazon.
- **/16 spread:** 58 distinct /16 blocks. Consistent with elastic IP allocation across AWS multi-region.
- **TLS issuer chains:** 54 distinct issuer CNs across 66 hosts. Examples include `Amazon RSA 2048 M01` (5), `HashiCorp Vault Certificate Authority` (3), `Microsoft Azure RSA TLS Issuing CA 08` (2), `Epic Systems Certificate Authority` (1), `DeltaV` (1), `Schneider Electric Certificate` (1), `BACnet-Controller` (1), `Nordex-Issuing-CA-2-2015` (1), `WellsSecure Public Certificate Authority 01 G2` (1), `Mitel MSPSDK Intermediate CA` (1), `Nintendo CA - G3` (1), `SonicWall Firewall Certificate` (1), `Verifone Certificate Authority` (1), `Juniper Device Certificate` (1), `Realtek` (1), `tigera-operator-signer` (1).

The cert-chain heterogeneity is **structurally impossible for a single legitimate operator**: no production deployment would rotate cert issuers across DeltaV (industrial DCS), Schneider Electric, Mitel, Wells Fargo, Nintendo, Epic Systems, BACnet, Verifone, Juniper, and HashiCorp Vault on the same 66-host deployment. These issuers come from harvested cert stores, embedded device defaults, or deliberate impersonation.

## Front-end deception layer (DCWF 672 verify)

GET `/` per host surfaces a different L7 mimicry on each host. Distinct titles surveyed: ComfyUI (4), Ray Dashboard (3), FortiSwitch (3), ServiceNow (3), Mirth Connect Administrator (3), Apache ActiveMQ (2), Remote Support Portal (2), Confluence, Polycom, Cisco Catalyst SD-WAN, CrushFTP, n8n.io, EasyIO-30P Sedona, ngrok, Flowise, AiCloud, plus Server headers including BBC HP OpenView, Sun-ILOM-Web-Server, Roku UPnP, cisco-IOS, 4D_WebSTAR, WebLogic, Jetty, AdSubtract, cPanel, EIG Embedded.

Universe of impersonations is too disjoint to be coincidence: AI/ML stacks (ComfyUI, Ray, Flowise, n8n), enterprise SaaS (ServiceNow, Confluence, Zendesk), healthcare (Mirth Connect — HL7/HIPAA), industrial DCS (DeltaV, EasyIO Sedona, BACnet), routing/firewall (FortiSwitch, Cisco SD-WAN, SonicWall), and consumer devices (Roku, Nintendo).

## Verdict

**Coordinated single-operator deception fleet.** The MCP backend is uniform and real (mcp-server 1.0.1, MCP 2025-06-18, identical 5-tool surface). The L7 layer and TLS cert chain are deliberately heterogeneous, drawn from harvested device fingerprints across unrelated victim categories.

Two plausible operator profiles fit:

1. **Honeypot/research telemetry:** measuring scanner taxonomy distribution. The MCP surface is the bait; `tools/call` would log the attacker and tool-name distribution would reveal scanner sophistication.
2. **Credential-collection trap:** the MCP surface is the bait; agents that auto-discover MCP servers and invoke `get_aws_admin_credentials` would expose their own pipeline. State-changing tools (`add_cron_job`, `schedule_commands`) might run the agent's *own* infrastructure into a callback.

Honeypot infrastructure is the parsimonious explanation. Multi-region AWS spread is consistent with a research or commercial honeynet operator.

## Restraint posture (DCWF 733)

- No `tools/call` against any of the 66 hosts. Hard-refused at code level in `mcp-initialize-probe.py` (`DO_NOT_CALL = True`; tampering aborts the run).
- All reads were schema/metadata only (`initialize`, `tools/list`, GET `/`, TLS cert DER, RDAP, rDNS).
- Cisco MCP scanner used in YARA-only mode against one sample host (3.137.167.45) as a cross-check; LLM-judge and behavioral modes not enabled.

## Sectoral classification + disclosure-channel candidates (DCWF 733)

| Operator class | Candidate routing channel | Notes |
|---|---|---|
| AWS infrastructure abuse | abuse@amazonaws.com (Trust & Safety) | Single channel covers all 66 hosts; AWS handles tenant identification internally. |
| Country CERT — regional | US-CERT, ENISA member CSIRTs (DE/FR/IE/IT/SE/CH), JPCERT, KrCERT, AusCERT, MOCERT, ZA CERT, BR CERT, IN CERT, MX SCT | If AWS abuse is non-responsive, region-by-region CERTs per /16 block ASN regional assignment. |
| Honeypot/research operator (if identified via abuse) | direct researcher contact | Conditional on AWS abuse identifying the customer; not a NuClide-side step. |
| MCP protocol working group | modelcontextprotocol.io editors | Generic concern: tool-name normalization as a sensitive-capability signal in MCP discovery clients. |

**Routing groundwork only. No disclosure decisions are made in this case study.**

## Generalized insight codified

See `methodology/insight-97-cert-heterogeneity-honeypot-discriminator.md` (Candidate). The primary codifiable lesson: for an N-host cohort with identical-backend protocol shape (`B = 1`, `T = 1`), the cert-issuer distribution ratio `I/N` is bounded by the operator's legitimacy. Legitimate single-operator deployments produce narrow cert distributions (`I/N ≤ 0.05`); honeypot/deception operators produce wide disjoint distributions (`I/N ≥ 0.30`). The Cat-MCP-Cred-Fleet measures `I/N = 0.833` across 66 identical-backend hosts (55 distinct issuer CommonNames including Wells Fargo, Salesforce, Snowflake, Epic Systems, Emerson DeltaV, Nordex, BACnet-Controller, AXIS IAM, FortiMail, Cisco AnyConnect, Microsoft Azure, HashiCorp Vault, Verifone, OpenStack, Kubernetes, Tigera). That ratio is the deception extreme.

Secondary lesson (pending #98 candidate): the Tabby-class FP-masking pattern (real-criticality MCP backend hidden behind a Next.js-shaped SPA on the same port) is the methodology gap that surfaced this cohort. Any host where probe-1 returns a SPA shape but does not return a vendor-specific `/v1/health` 200 must be additionally probed for secondary backend identity on the same port. Tracked in the parent Cat-Tabby retrospective (`shodan/cat-tabby-devstral-2026-06-09/SESSION-RETROSPECTIVE.md`).

## Artifacts

- `mcp-initialize-probe.py` - protocol-strict probe with DO_NOT_CALL hard-refusal
- `mcp-initialize-results.jsonl` - 66 records, initialize + tools/list
- `mcp-tools-inventory.json` - deduped tool union (1 distinct toolset, 5 tools)
- `operator-attribution.json` - rDNS + RDAP cluster summary
- `cert-resniff-results.json` - DER-parsed TLS subject/issuer per host (54 distinct issuers)
- `frontend-probe-results.json` - GET / response per host (heterogeneous deception layer)
- `cisco-scanner-3.137.167.45.json` - Cisco YARA scanner cross-check (1 host)
- `findings-breakdown.txt` - per-cohort analytical breakdown (verification ladder, tool surface, cert/frontend distribution, verdict, restraint posture, next-steps)
- `cat-mcp-cred-fleet-findings-breakdown.txt` - per-host data dump (auto-built from the JSONL probe results)
- `methodology/visorcas-signature-mcp-cred-theft-honeypot.yaml` - VisorCAS signature draft (cohort signal, aimap override, ledger action)
- `methodology/insight-9X-mcp-tool-name-is-the-finding.md` - candidate insight on carrier-shape masking the MCP backend on the same port; complements `methodology/insight-97-*` (global)
- `build-breakdown.py`, `build-visorlog-events.py` - cohort artifact builders

## Reference insights applied

- Insight #1 - exact protocol envelope drops honeypot pollution (this cohort PASSES #1; deception lives outside the protocol layer)
- Insight #3 - traverse every nested handshake field; capabilities leak
- Insight #32 - multi-service deception fleets (HTTP-layer companion to the cert-layer signature here)
- Insight #68 - depth/breadth verification grid; cohort-level cert distribution is a Breadth-2 promotion
- Insight #97 (this survey, candidate) - cert-issuer heterogeneity across identical-backend fleet as honeypot discriminator
- ref_ov_cert_attribution - no-SNI cert read for customer OV/EV (yielded 55 distinct issuers, revealing the deception)
- reference_as63949_honeypot_fleet - prior-generation single-issuer fleet, less sophisticated than this one
- feedback_verify_before_claiming_exploitable - blocked-state framing for unverified calls
- feedback_no_disclosure_recommendations - routing channels listed; recommendations not made

## Wardrobe + syllabus stance

- **DCWF 672** Test & Evaluation - protocol conformance discriminator, schema completeness as evidence
- **DCWF 733** Risk Management / AI Ethics - restraint at the `tools/call` boundary, routing-only disclosure
- **NICE 541** Penetration Tester - cert pivot + multi-modal attribution clustering

Threat literature anchors:
- MCP specification, modelcontextprotocol.io 2025-06-18 revision
- Prompt-injection-as-supply-chain analyses (EchoLeak, ShadowLeak, LLMail-Inject)
- Honeypot detection literature - cert reuse + service heterogeneity as canary signature
