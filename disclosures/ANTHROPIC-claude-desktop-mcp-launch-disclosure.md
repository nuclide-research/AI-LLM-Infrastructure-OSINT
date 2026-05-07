---
to: security@anthropic.com
cc: abuse@nuclide-research.com
severity: MEDIUM
ip: n/a
institution: "Anthropic, Claude Desktop MCP-launch path harden recommendation: claude_desktop_config.json -> npx -y <package> auto-installs and executes arbitrary npm packages with no operator confirmation, creating a typosquat-by-design surface for tutorial-authored configs"
status: DRAFT
outcome: sent
date: 2026-05-07
---

**To:** security@anthropic.com
**Cc:** abuse@nuclide-research.com
**Subject:** Claude Desktop MCP launcher, harden against tutorial-authored typosquat configs (`npx -y <unclaimed-package>`)

---

Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com

2026-05-07

This is an unsolicited good-faith product-security recommendation under the NuClide Research umbrella (CISA disclosures CVE-2025-4364, ICSA-25-140-11). The finding is design-level, not a working exploit; severity MEDIUM.

---

## Summary

Claude Desktop reads `~/Library/Application Support/Claude/claude_desktop_config.json` (and Windows / Linux equivalents) and launches each entry under `mcpServers[*]` as a child process via the configured `command` + `args`. The most common pattern across community tutorials is:

```json
{
  "mcpServers": {
    "<name>": {
      "command": "npx",
      "args": ["-y", "<some-mcp-server-package>"]
    }
  }
}
```

`npx -y <package>` auto-installs the package from the npm public registry and executes it without any operator confirmation. If the named package is unclaimed at the time the user authors the config, anyone can register the name later and ship code that runs as the operator user the next time Claude Desktop starts.

Concrete current example: `mcp-server-ollama` is referenced by [Ollama Issue #16005](https://github.com/ollama/ollama/issues/16005), multiple awesome-mcp-servers indexes, and tutorial blog posts. The npm registry returns 404 for that name as of 2026-05-07. Two adjacent names (`@ollama/mcp-server`, `@modelcontextprotocol/server-ollama`) are also unclaimed.

This is not specific to Ollama: it is a structural property of Claude Desktop's MCP launcher path that any unclaimed npm name appearing in a sufficiently-trafficked tutorial creates an exploitation surface for the operator who follows the tutorial.

## Suggested mitigations

In rough order of effort vs. value:

### 1. Surface the package source on first execution of any new `mcpServers` entry

Today: Claude Desktop reads the config and silently launches every entry on next start.

Proposed: when Claude Desktop sees an `mcpServers` entry it has not previously launched, prompt the operator with a confirmation that surfaces:

- The entry name (`mcpServers.ollama`)
- The command + args verbatim (`npx -y mcp-server-ollama`)
- For `npx`-based commands specifically: the npm registry that resolves it (`https://registry.npmjs.org/mcp-server-ollama`) and whether the package currently exists
- A "Run once" / "Always run" / "Don't run" tri-state choice

This is the same pattern Claude Code uses for tool permissions today; extending it to MCP commands surfaces parity.

### 2. Treat `npx -y` (and `pip install` + `pipx run` + similar auto-install patterns) as a distinct privilege class

The `-y` flag in `npx` skips the standard "confirm install" prompt. From the operator's perspective, it is equivalent to "execute arbitrary code from npm without asking me." Claude Desktop could:

- Detect `command: "npx"` + args containing `-y` (or `--yes`)
- Surface this specifically as "this entry will download and execute arbitrary code from npm" in the confirmation dialog
- Optionally refuse to auto-launch such entries until the operator explicitly opts in once

This is a one-time per-config-key onboarding flow, not a per-launch friction.

### 3. Maintain an MCP allow-list of known-safe packages

Anthropic could publish a curated list of vetted MCP servers (similar to Claude Code's tool registry) and treat allow-listed packages as auto-launch without prompting, while requiring confirmation for everything else.

This shifts the security model from "warn on every launch" (operator fatigue) to "warn on the unknown" (signal-to-noise wins).

### 4. Sandbox MCP processes by default

A more invasive change: launch each MCP server in a sandbox that limits filesystem access, network access, and privilege escalation. The current model gives MCP processes the operator user's full environment. A sandboxed default reduces the blast radius of a compromised MCP package even when the user has consented to launch it.

This is significantly more engineering than the first three options and may be incompatible with some MCP server use cases that legitimately need broad access.

### 5. Sign and verify MCP packages

Long-term: extend the MCP protocol to include a signature scheme where MCP server packages are signed by their publishers, and Claude Desktop verifies signatures before launch. This requires upstream MCP-protocol coordination (Anthropic + Microsoft + community) and is the most-investment / highest-value option.

## What NuClide is not doing

- Not registering the unclaimed npm names speculatively.
- Not publishing exploitation tooling.
- Not coordinating with bad actors. We are the only party currently aware of these specific unclaimed names in this specific framing, to our knowledge.

We have parallel-disclosed to Ollama (`security@ollama.com`) about the Ollama-namespace-specific surface; this disclosure is the broader Claude-Desktop-side perspective.

## Severity rationale

MEDIUM.

The vulnerability is structural in Claude Desktop's MCP launcher path; operators who follow tutorials with unclaimed package names are vulnerable the moment any party claims the name. There is no current exploitation that we can identify. The fix is fully on the Claude Desktop side and ranges from "single dialog addition" (option 1) to "MCP protocol extension" (option 5).

## Reference

Full case study (with verbatim source-line citations from Ollama's launcher + Methodology Insight #11 on source-as-authority):

https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT/blob/main/case-studies/commercial/vendor-ollama-launch-claude-desktop-2026-05-07.md

Happy to walk through the unclaimed-name corpus, share the npm-registry probe script, or hand off any tooling that would aid Claude Desktop's product-security review.

Regards,

Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT
