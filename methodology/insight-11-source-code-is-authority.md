---
title: "Source code is authoritative; bug reports are framing"
insight_number: 11
date: 2026-05-07
featured: true
tags:
  - methodology
  - source-verification
  - misattribution
  - config-mutators
related_research:
  - case-studies/commercial/vendor-ollama-launch-claude-desktop-2026-05-07.md
source: case-studies/commercial/vendor-ollama-launch-claude-desktop-2026-05-07.md
---

# Methodology Insight #11, Source code is authoritative; bug reports are framing

**When a bug report claims that a vendor wrote `X` to a config, verify against the vendor's source repository and current release tag before accepting the framing. Config mutators that preserve keys they don't manage are a misattribution attack surface; the right verification path is `grep` on the actual writer function, not `cat` on the post-mutation config.**

## Evidence

GitHub Issue [`ollama/ollama#16005`](https://github.com/ollama/ollama/issues/16005) (filed 2026-05-06) claimed:

> `ollama launch claude-desktop` writes a configuration that references a non-existent npm package, causing the Claude Desktop integration to fail silently.

A primary-source review of the v0.23.1 source found:

- `cmd/launch/claude_desktop.go` is 888 lines, single commit on 2026-05-03
- Zero references to `mcp`, `mcpServers`, `npx`, or `npm` anywhere in the file
- The config-writer (`writeClaudeDesktopGatewayProfile`) writes only `inferenceProvider`, `inferenceGatewayBaseUrl`, `inferenceGatewayApiKey`, `inferenceGatewayAuthScheme`, and `disableDeploymentModeChooser`
- The reader (`readClaudeDesktopJSONAllowMissing`) loads existing config; the writer (`writeClaudeDesktopJSON`) re-serializes including unrecognized keys

The most consistent explanation: the bug reporter had previously followed a tutorial that wrote an `mcpServers.ollama` entry referencing `mcp-server-ollama`. Ollama's launcher preserved the entry. The reporter inspected the post-launch config and credited authorship to the most recent writer (Ollama). The actual author is whichever tutorial they had followed.

## How to apply

Three steps:

1. **Find the writer function.** When a bug report says "tool X wrote field Y to file Z", grep tool X's source repository for either field Y's name or the path Z. If the writer doesn't reference Y, the writer is not authoring Y.
2. **Trace key-preservation behavior.** When the writer reads-modifies-writes (vs. truncates and rewrites), unrecognized keys persist. The post-write file's content is the union of (writer output) + (preserved input). Misattribution is structural in this design.
3. **Look for the upstream author.** If the writer didn't author the suspect key, search community tutorials, GitHub gists, blog posts, and indexer / awesome-list catalogs for the exact key/value pattern. The actual author is typically two or three referrers upstream from the bug reporter.

## How to apply (broader)

This is a verification discipline, not just a triage rule:

- The Ulm CL1 case (Methodology Insight #10) was first framed by the SOC's intake as "operator misconfiguration"; primary-source verification of Cortical Labs' default systemd unit promoted the framing to "vendor-template default-no-auth", different actor, different fix path.
- The 2026-05-04 SUNY Buffalo State misroute (Insight #4) was framed by our own pipeline as "send to UB"; WHOIS source-of-truth verification rerouted to Buffalo State.

The pattern across all three: **always trace a claim back to the actor's own primary record before crediting or blaming.** Bug reports, intake notes, and slug-string heuristics are framing layers. Source code, WHOIS records, and vendor systemd units are primary records.

## When the framing is correct (and when it isn't)

A bug report's framing is reliable when:

- The bug reporter quotes a specific source-line or commit
- The bug is reproducible in isolation (no pre-existing state)
- The reporter has the authority to inspect the writer (developer, package maintainer)

A bug report's framing is unreliable when:

- The bug is observed only in the post-mutation state, not in the writer's act
- The reporter is a downstream consumer who doesn't read the writer's source
- The mutator preserves keys it doesn't manage (misattribution structural risk)

The discipline: distrust framing by default; trust source. If primary-source verification confirms the framing, the bug is real. If it refutes the framing, the bug is somewhere else.

## Source

Captured in [`case-studies/commercial/vendor-ollama-launch-claude-desktop-2026-05-07.md`](../case-studies/commercial/vendor-ollama-launch-claude-desktop-2026-05-07.md). Connected to:

- Insight [#4 (WHOIS-driven contact resolution)](insight-04-whois-driven-contact-resolution.md), same shape at the disclosure-routing layer
- Insight [#10 (vendor-template default-no-auth)](insight-10-vendor-template-default-no-auth.md), same shape at the deployment-classification layer
