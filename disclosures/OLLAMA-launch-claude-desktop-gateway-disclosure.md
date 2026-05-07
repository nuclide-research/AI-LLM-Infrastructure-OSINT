---
to: security@ollama.com
cc: abuse@nuclide-research.com
severity: MEDIUM
ip: n/a
institution: "Ollama, Inc., vendor advisory: 'ollama launch claude-desktop' silently rewrites Claude Desktop into Ollama-Cloud gateway mode without surfacing the privacy implication; recommend success-message expansion and defensive npm-name claims"
status: DRAFT
outcome: sent
date: 2026-05-07
---

**To:** security@ollama.com (or `abuse@`, `support@`, or via security.txt if published)
**Cc:** abuse@nuclide-research.com
**Subject:** Vendor advisory, `ollama launch claude-desktop` (v0.23.x) — gateway-mode trust boundary not surfaced + adjacent npm typosquat surface

---

Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com

2026-05-07

This is an unsolicited good-faith vendor advisory under the NuClide Research umbrella (CISA disclosures CVE-2025-4364, ICSA-25-140-11). No active exploitation observed; this is a design / UX advisory plus a defensive npm-namespace recommendation.

---

## Summary

Two items, both arising from a primary-source review of [`cmd/launch/claude_desktop.go`](https://github.com/ollama/ollama/blob/v0.23.1/cmd/launch/claude_desktop.go) on the v0.23.1 tag:

### 1. Gateway-mode MITM is not surfaced to the operator

Running `ollama launch claude-desktop` rewrites Claude Desktop's deployment to "third-party gateway" mode with `inferenceGatewayBaseUrl: https://ollama.com`. From that moment, every Claude Desktop prompt, response, attached file, and tool-use payload transits ollama.com as plaintext under the operator's bearer-auth Ollama Cloud key.

The success message printed by the launcher is:

```
Claude Desktop profile changed to Ollama Cloud.
To restore the usual Claude profile, run: ollama launch claude-desktop --restore
```

This does not surface to the operator that:

- ollama.com now sees plaintext prompts and responses on the server side (TLS-as-usual to the gateway, plaintext access by Ollama-the-company)
- Direct-to-Anthropic privacy posture is replaced
- Ollama's data retention, jurisdiction, and ToS apply to traffic that previously bypassed Ollama entirely
- The `--yes` / `--config` flags allow scripted invocation that completely skips operator awareness of the mode shift

The trust-boundary shift is the design intent of gateway mode and is correct for many Ollama Cloud customers. The advisory is about consent visibility, not about the design itself.

#### Recommended fix

Expand the success message to surface the trust-boundary shift. Suggested copy:

```
Claude Desktop profile changed to Ollama Cloud.

All Claude Desktop prompts, responses, attached files, and tool outputs
will now route through ollama.com and are visible to Ollama, Inc. The
Ollama privacy policy and data-retention terms apply to your Claude
Desktop traffic until you run: ollama launch claude-desktop --restore

To restore the direct-Anthropic profile, run: ollama launch claude-desktop --restore
```

A single-string firmware push. No protocol or schema changes required.

### 2. Adjacent npm typosquat surface (Ollama-namespaced unclaimed names)

Three npm package names that appear in community tutorials, awesome-mcp-servers indexes, and PyPI/GitHub catalog crawls under an Ollama-implied origin are not registered:

| Name | npm registry status |
|---|---|
| `mcp-server-ollama` | 404 |
| `@ollama/mcp-server` | 404 |
| `@modelcontextprotocol/server-ollama` | 404 |

[Ollama Issue #16005](https://github.com/ollama/ollama/issues/16005) (filed 2026-05-06, still open) is the most public reference; multiple awesome-mcp-servers list-of-lists also surface these names as if registered. None are registered. `npx -y mcp-server-ollama` returns 404.

A user who follows a tutorial directing them to write the following into `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "ollama": {
      "command": "npx",
      "args": ["-y", "mcp-server-ollama"]
    }
  }
}
```

…sees Claude Desktop attempt to launch the MCP server on next start. Today the launch fails silently (404 on the npm registry). The moment a malicious actor registers a package named `mcp-server-ollama`, every Claude Desktop instance with such a config will `npx -y` the package on next start and execute its code as the operator user, with full MCP-bridge access to the Claude Desktop session.

The vulnerability is community-tutorial-driven and not currently in any Ollama official binary. However, the Ollama brand is implicated by the names: a malicious package at `mcp-server-ollama` would be widely assumed to be Ollama-published.

#### Recommended fix

Defensively claim the three Ollama-namespaced names with placeholder packages. Each placeholder should:

- Print a clear warning when invoked: "This is a NuClide-coordinated defensive placeholder. The package name `<name>` is not the Ollama-published Claude Desktop bridge. If you reached this from a tutorial, refer to docs.ollama.com/integrations/claude-desktop for the supported integration path."
- Exit cleanly without spawning a long-lived process (so Claude Desktop reports a missing-bridge error rather than hanging on a dead transport).
- Optionally include npm download statistics so Ollama can measure how widespread the tutorial-poisoned configs are in the wild.

The minimum viable placeholder is a single `index.js` that `console.error`s the warning and `process.exit(1)`s. Total package size: ~500 bytes.

If Ollama prefers not to register names you don't operate, NuClide can claim them as community defensive placeholders, but the Ollama brand association argues for vendor-side ownership.

### 3. Unrecognized-key preservation in `claude_desktop_config.json`

A secondary recommendation, related to Issue #16005's framing:

The launcher's config-writer (`writeClaudeDesktopGatewayProfile`) reads the existing `claude_desktop_config.json`, sets the keys it manages, and re-serializes. Keys it does not manage are preserved as-is. This is correct behavior for not stomping on operator-authored config, but it creates a misattribution surface: a user who had previously written `mcpServers.ollama` into the config from a tutorial sees Ollama's writer "preserve" that key, and credits Ollama with authorship.

Option A: leave preservation as-is and add a one-time warning during the launch flow:

```
Note: existing config keys not managed by this launcher were preserved:
  - mcpServers (1 entry: ollama -> npx -y mcp-server-ollama)

If these were authored by a previous tool or tutorial and you want them
removed, edit ~/Library/Application Support/Claude/claude_desktop_config.json
or run: ollama launch claude-desktop --reset-foreign-keys
```

Option B: migrate fully to the third-party-profile path (`Claude-3p/`) and stop touching the user's primary config at all. The third-party-profile path already exists in the launcher; expanding it to be the sole write target eliminates the misattribution surface entirely.

## Severity rationale

Severity: MEDIUM.

The gateway-mode item is a UX/consent issue, not a vulnerability per se. Operators who deliberately want gateway-mode are unaffected. Operators who don't realize they enabled it are exposed to a meaningful privacy degradation but no immediate security loss; the privacy degradation is reversible via `--restore`.

The npm typosquat item is currently inert (the names are unclaimed). Claiming the names defensively closes a future-exploitation surface; if they remain unclaimed, the surface waits to be exploited.

The misattribution item is a product-trust risk for Ollama, not a security risk; severity is informational.

## NuClide will not

- Register the unclaimed names speculatively without explicit vendor approval. Defensive squatting becomes ongoing maintenance burden and registry pollution if not vendor-owned.
- Publish exploitation tooling. The disclosure path here is vendor-side fixes, not a working exploit.

## Reference

Full case study (with the verbatim source-line citations + the Methodology Insight #11 framing on source-as-authority over bug-report-claims):

https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT/blob/main/case-studies/commercial/vendor-ollama-launch-claude-desktop-2026-05-07.md

Issue #16005 reference:

https://github.com/ollama/ollama/issues/16005

Happy to coordinate disclosure timeline, walk the launcher source line-by-line, or hand off the npm-name placeholder package implementations if you'd find that useful.

Regards,

Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT
