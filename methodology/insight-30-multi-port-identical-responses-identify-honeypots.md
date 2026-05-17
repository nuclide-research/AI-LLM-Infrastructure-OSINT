---
title: "Multi-port identical responses identify honeypot fleets"
insight_number: 30
date: 2026-05-17
tags:
  - methodology
  - honeypot-detection
  - protocol-agnostic
  - aimap
related_research:
  - case-studies/commercial/mcp-server-survey-2026-05-17.md
source: case-studies/commercial/mcp-server-survey-2026-05-17.md
---

# Insight #30. Multi-port identical responses identify honeypot fleets

A real service occupies one port. A honeypot fleet that ships the same canned response on every port it has open is identifiable by that uniformity alone, with no need to decode any specific protocol.

This generalizes [Insight #19](insight-19-protocol-strict-handshakes-honeypot-fleets.md). Insight #19 applies protocol-strict checks per-protocol: send a real handshake, check whether the response is real or canned. Insight #30 is protocol-agnostic: detect honeypots from the response *distribution* across ports, not from the response *content* on any one port.

## The rule

For an IP that fingerprints positive for a service, also probe N ports the service is **not** expected to run on. If the same response signature returns on multiple unrelated ports, the host is a multi-protocol honeypot. Real services occupy a single port. A research/lab MCP server runs on 3000 or 8000. A real Elasticsearch runs on 9200. A real Redis runs on 6379. A real service does not answer MCP `initialize` on `:443`, `:80`, `:5000`, `:5001`, `:8000`, `:8001`, `:3000`, `:3001` *simultaneously*.

## Empirical basis

NuClide MCP server survey 2026-05-17:

- 51 of 51 hosts from yesterday's accidental MCP hits responded identically to MCP `initialize` on 6+ ports with `serverInfo: {name: "mcp-server", version: "1.0.1", protocolVersion: "2025-06-18"}`.
- Their `/version` endpoint returns `1.13.0` (Docker-shaped but wrong format), `/info` returns Docker info JSON with `Containers: 0`, `/networks` returns an Ivanti Connect Secure login page, `/volumes` returns `POC_SUCCESS_Linux dev 5.15.0-134-generic`, `/sse` returns DrayTek VigorConnect admin or Tor exit router HTML.
- The protocol-strict survey on the same date returned 45 real MCP servers, each on a single port (3001 dominantly), each returning a real `406 Not Acceptable` HTTP+SSE handshake error.

The 51 false positives and the 45 true positives ran on the same ASNs. AS63949 (Akamai-Linode) hosted both 21 honeypots and 21 real MCP servers. ASN is not a discriminator. Multi-port response uniformity *is*.

## How to apply

In aimap or any service classifier:

1. When a fingerprint matches, store the response signature (status code + body hash).
2. Probe the same service-detection signature on at least 3 ports the service is not expected to run on.
3. If the signature matches on 3+ ports, classify the host as **honeypot-multiprotocol** and exclude from downstream disclosure pipelines that frame "your host is exposed."
4. The check is one round-trip per extra port. Cheap.

This belongs in aimap v1.9.11 as a second-pass check on every host that matches a fingerprint. Candidate Finding category: `honeypot_multiprotocol`.

## How this protects research

Honeypots are not just decoys for adversaries. For population-scale researchers, they are noise that inflates exposure counts. A 51-host honeypot fleet that gets classified as "MCP Server" inflates yesterday's training-observability MCP exposure count by 17% (51 of 309 host:port hits) and contaminates any disclosure batch built from that classification. Insight #30 prevents that contamination at population scale.
