---
title: "Capabilities-object tool-schema leak"
insight_number: 3
date: 2026-05-04
tags:
  - methodology
  - mcp
  - protocol-handshake-leak
related_research:
  - case-studies/commercial/mcp-cloud-survey-2026-05.md
source: case-studies/commercial/SYNTHESIS-2026-05.md
---

# Methodology Insight #3: Capabilities-object tool-schema leak

**Auth-gated invocation surfaces still leak structural information at the unauthenticated handshake layer.**

## Evidence

`@benborla29/mcp-server-mysql` v2.0.1 returned an empty `tools/list` (auth-gated for invocation) but **leaked the `mysql_query` tool schema via the `capabilities` object of the `initialize` response**.

A protocol probe that only enumerates the top-level `tools` array will miss this. The capabilities object is part of the unauth handshake and must be traversed deeply.

## How to apply

For any protocol with a multi-stage handshake (MCP, JSON-RPC variants, gRPC reflection, GraphQL introspection):

1. After the `initialize`/connect step, fully traverse every nested capabilities/metadata field, `serverInfo`, `capabilities`, `meta`, `extensions`.
2. Treat the absence of `tools/list` content as a "look elsewhere in the handshake" signal, not a "fully gated" signal.
3. Auth-gated *invocation* and unauthenticated *introspection* are independent attack surfaces.

## Source

Captured in [`case-studies/commercial/SYNTHESIS-2026-05.md`](../case-studies/commercial/SYNTHESIS-2026-05.md). Survey: [`mcp-cloud-survey-2026-05`](../case-studies/commercial/mcp-cloud-survey-2026-05.md).
