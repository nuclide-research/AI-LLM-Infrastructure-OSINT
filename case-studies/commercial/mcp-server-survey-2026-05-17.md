---
type: synthesis
---

# MCP server population survey, 2026-05-17

_NuClide Research, 2026-05-17 (evening pass)_
_Survey #19 in the AI infrastructure series._

---

## Summary

We surveyed the public Model Context Protocol (MCP) server population. MCP is Anthropic's wire format for letting LLMs call into external tools, prompts, and resources. It has become the standard control plane for agentic LLM deployments. We harvested candidates with protocol-strict Shodan dorks and cross-referenced against the 51 accidental MCP hits in yesterday's training-observability survey.

Three findings.

**One. The training-observability MCP hits were 100% honeypot.** All 51 IPs that aimap classified as "MCP Server" in yesterday's training-obs corpus respond to MCP `initialize` on **every port** (80, 443, 3000, 3001, 5000, 5001, 8000, 8001, 8080, 8081, 8888) with the same canned `serverInfo: {name: "mcp-server", version: "1.0.1", protocolVersion: "2025-06-18"}` response. They also return Docker daemon API shapes, Tor exit router pages, DrayTek VigorConnect admin pages, Ivanti Connect Secure login bait, and the `POC_SUCCESS_` canary string on `/volumes`. They are a multi-protocol honeypot fleet that bait the MCP service classifier.

**Two. The protocol-strict Shodan harvest surfaced 45 real MCP servers.** Queries like `http.html:"mcp"+http.html:"jsonrpc"`, `"@modelcontextprotocol"`, `"x-mcp-session"`, `"streamable+http"+mcp` returned hosts that respond on a single port with `406 Not Acceptable: Client must accept text/event-stream`. The canonical response for HTTP+SSE-transport MCP servers when accessed without the right Accept header. These are real.

**Three. Both populations overlap entirely on the same ASNs.** Linode (AS63949) hosts both 21 of the honeypot IPs and 21 of the real MCP IPs. The honeypot fleet runs on the same infrastructure as the real operators. ASN alone is not a discriminator.

This is **Insight #19 applied at population scale**: protocol-strict handshakes are the only verifier for multi-protocol honeypot fleets.

---

## Honeypot signature

The honeypots respond identically across ports with the same canned `mcp_server 1.0.1` payload:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "protocolVersion": "2025-06-18",
    "capabilities": {"tools": {}},
    "serverInfo": {"name": "mcp-server", "version": "1.0.1"}
  }
}
```

A real MCP server runs on one port (typically 3000 or 8000) and responds to handshakes there only. The honeypot answers on six or more ports with the same payload. Multi-port identical-response is the discriminator.

Adjacent canary surfaces seen on the same hosts:

| Probe path | Honeypot response |
|---|---|
| `/version` | `1.13.0` (looks Docker-shaped but wrong) |
| `/info` | Docker `info` JSON with `Containers: 0` |
| `/containers/json` | `{"version":"11.86.0.41"}` (not Docker format) |
| `/images/json` | `-----BEGIN OPENSSH PRIVATE KEY-----` (fake key) |
| `/networks` | Ivanti Connect Secure login page |
| `/volumes` | `POC_SUCCESS_Linux dev 5.15.0-134-generic` |
| `/system/df` | Random Ivanti admin pages |
| `/sse` | DrayTek VigorConnect HTML, or Tor exit router HTML |

The `POC_SUCCESS_` literal in `/volumes` is the canary. Any researcher who exfils that string and reports it has triggered the honeypot. It is the modern equivalent of the classic "kippo" SSH honeypot canaries.

---

## The real population

45 hosts confirmed running real HTTP+SSE-transport MCP servers:

| Hosting | Hosts | Country pattern |
|---|---:|---|
| AKAMAI-LINODE-AP (AS63949) | 21 | mixed; US-fronted with backend often elsewhere |
| Alibaba Cloud (AS37963) | 18 | China |
| Huawei Cloud (AS55990) | 6 | China |

The 17 Chinese hosts (Alibaba + Huawei) are likely production MCP deployments. Possibly customer-facing agentic LLM products built on local infrastructure. Worth follow-up deep enumeration with the proper SSE-transport protocol handshake.

The 21 Linode hosts return the 406 error pattern uniformly and all live on port 3001. The deployment uniformity (same port, same response shape, same nginx-fronted SSE topology) suggests a single SaaS provider running MCP-as-a-service against many subdomains, rather than 21 independent operators.

---

## Why protocol-strict matters

aimap's existing MCP fingerprint matches on five probe patterns including the `406 + jsonrpc error` shape. That fingerprint is sound. It gets the protocol-level signal right. The problem is upstream: aimap fingerprints HTTP responses, and the honeypot fleet ships canned HTTP responses that match many fingerprints simultaneously.

Two complementary defenses:

1. **Multi-port consistency check**, if the same IP returns the same MCP `initialize` response on 3+ ports, classify as honeypot. Real MCP servers run on one port.
2. **Protocol-strict handshake**, issue an MCP `initialize` POST with proper Accept headers; if the response is a canned `mcp-server 1.0.1 2025-06-18` payload, classify as honeypot (real servers either give a 406 error or return a unique serverInfo).

Both are cheap to add to aimap as a second-pass check on hosts that already match the fingerprint. Candidate v1.9.11.

---

## Candidate Insight #30

**Multi-port identical responses identify multi-protocol honeypot fleets.**

A real service occupies one port. A honeypot fleet running the same canned response on every port it has open is identifiable by that uniformity alone, without needing to decode any specific protocol. This is a generalization of Insight #19 (which applied protocol-strict checks per-protocol). Insight #30 is protocol-agnostic: detect honeypots from the response *distribution*, not the response *content*.

Empirical basis: 51 of 51 training-obs MCP hits classified as honeypot by this rule (multi-port canned), then verified by protocol-strict handshake + canary string match.

---

## Method

1. **Shodan harvest:** nine protocol-strict dorks (`http.title:"MCP"`, `http.html:"mcp"+http.html:"jsonrpc"`, `"@modelcontextprotocol"`, `"x-mcp-session"`, `"streamable+http"+mcp`, `"mcp-proxy"`, `"MCP+Inspector"`, `"mcp"+"initialize"+jsonrpc`, `"prompts":[]+"tools":[]`). Union: 403 candidate IPs.
2. **aimap fingerprint pass:** 403 hosts × 15 ports. 233 service hits across 45 unique IPs.
3. **Training-obs MCP cross-reference:** 51 unique IPs from yesterday's training-observability survey that aimap classified as MCP. Zero overlap with (2).
4. **Multi-port honeypot classifier:** for each of 96 unique IPs, POST `initialize` to `/mcp` on 6 standard ports; count canned-response hits. 3+ canned = honeypot.

Results: 51 honeypot, 45 real, 96 total.

---

## Restraint

We probed only the MCP handshake endpoint and adjacent canary paths. We did not enumerate tools, resources, prompts, or any operator data on the 45 confirmed real MCP servers. The fingerprint plus protocol response is the finding; deep enumeration is held for the v1.9.11 enumerator work and is out of scope for the population-class survey.

The Docker daemon API probes on the honeypot host (`172.105.118.142:3001`) hit `/version`, `/info`, `/containers/json`, `/images/json`, `/networks`, `/volumes`, `/system/df`. Each returned a different canary surface, confirming honeypot. We did not interact further.

---

## Toolchain provenance

```
JAXEN        [x] Shodan harvest across 9 protocol-strict dorks (403 candidates)
aimap v1.9.10[x] 233 service hits, 45 unique IPs (port set 80-9090)
aimap-profile[ ] queued for the 45 real hosts
VisorGraph   [ ] queued for the 17 Chinese cloud hosts (Alibaba + Huawei)
VisorLog     [ ] queued ingest
nu-recon     [—] not needed; multi-host pattern check
classifier   [x] custom multi-port classifier built for this survey
```

---

## See also

- [`adya-ai-vanijmcp-2026-05-17.md`](adya-ai-vanijmcp-2026-05-17.md): adjacent Adya AI custom MCP-proxy (not in survey corpus, but methodologically related)
- [`training-observability-survey-2026-05-17.md`](training-observability-survey-2026-05-17.md): source of the 51-IP false-positive honeypot cohort
- [`../../methodology/insight-19-protocol-strict-handshakes-honeypot-fleets.md`](../../methodology/insight-19-protocol-strict-handshakes-honeypot-fleets.md)
- [`../../reference/as63949-honeypot-fleet.md`](../../reference/as63949-honeypot-fleet.md): prior 393-host Akamai/Linode AI-stack honeypot documentation
