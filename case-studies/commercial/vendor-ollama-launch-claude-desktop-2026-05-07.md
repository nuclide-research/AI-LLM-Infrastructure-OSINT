---
title: "ollama launch claude-desktop — gateway-mode MITM by default + community-tutorial typosquat surface"
date: 2026-05-07
class: vendor-template
category: bridge-architecture
status: open-research
methodology: source-code authority + npm-registry survey + community-corpus search
---

# `ollama launch claude-desktop`: gateway-mode MITM by default + community-tutorial typosquat surface

NuClide Research, 2026-05-07

## TL;DR

Two distinct findings from a primary-source review of Ollama v0.23.1's `ollama launch claude-desktop` command:

1. **Gateway-mode MITM by design.** Running the command rewrites Claude Desktop into a "third-party inference" deployment with `inferenceGatewayBaseUrl: https://ollama.com`. Every prompt and every response from that point forward transits Ollama Cloud as plaintext under the user's bearer key. Consent is implicit in the act of running the command; the privacy implication is not surfaced in the success message ("Claude Desktop profile changed to Ollama Cloud").

2. **Community-tutorial typosquat surface.** The npm package name `mcp-server-ollama` (referenced by GitHub Issue #16005, several "awesome-mcp-servers" indexes, and a number of tutorial blog posts) is not registered on the npm public registry. `npx -y mcp-server-ollama` returns 404. Anyone who registers the package can publish code that gets auto-installed and executed as the operator user the next time Claude Desktop reads a tutorial-poisoned `claude_desktop_config.json`. Several adjacent unclaimed names (`@ollama/mcp-server`, `@modelcontextprotocol/server-ollama`) compound the surface.

A third finding is that **Issue #16005 itself is misframed**: the bug reporter blames Ollama for writing the typosquat-vulnerable config, but the v0.23.1 source does not write `mcpServers` entries at all. The config the reporter saw most likely pre-existed from a tutorial they had previously followed; Ollama's config-writer preserves keys it does not manage, creating a misattribution attack surface where the vendor inherits blame for content the vendor only failed to remove.

## Background: what the command does

Ollama v0.23.0 (released 2026-05-03) introduced a new `cmd/launch/` subcommand framework with 13 first-party launcher targets. v0.23.1 (2026-05-05) ships the launcher set used in the field today. The `claude-desktop` target lives in [`cmd/launch/claude_desktop.go`](https://github.com/ollama/ollama/blob/main/cmd/launch/claude_desktop.go) (single commit, 2026-05-03).

The `Run` flow:

1. `claudeDesktopSupported()` — guards against unsupported OSes.
2. `claudeDesktopTargetPaths()` — resolves Claude Desktop's macOS `~/Library/Application Support/Claude/` and `Claude-3p/` profile directories, plus per-profile `configLibrary/_meta.json` and `configLibrary/<profileID>.json`. Windows and Nest-variant paths handled in `claudeDesktopWindowsPaths` / `Claude Nest-3p`.
3. `claudeDesktopValidatedAPIKey(ctx, profilePaths)` — reads any existing API key from a profile, validates against `https://ollama.com`, prompts the operator if invalid (printed prompt: "Enter your Ollama API key (https://ollama.com/settings/keys):").
4. `writeClaudeDesktopDeploymentMode(path, "3p")` — sets `deploymentMode: "3p"` on the normal config.
5. `writeClaudeDesktopGatewayProfile(path, key, true)` — writes the gateway block to the third-party profile config:

```json
{
  "deploymentMode": "3p",
  "inferenceProvider": "gateway",
  "inferenceGatewayBaseUrl": "https://ollama.com",
  "inferenceGatewayApiKey": "<user's Ollama Cloud API key>",
  "inferenceGatewayAuthScheme": "bearer",
  "disableDeploymentModeChooser": true
}
```

6. `claudeDesktopLaunchOrRestart("Restart Claude Desktop to use Ollama?")` — confirms with the operator and restarts the app.

The `Restore` flow (`ollama launch claude-desktop --restore`) reverses the deployment-mode chooser flag and removes the gateway entries, returning to direct-Anthropic mode.

## Finding 1: gateway-mode MITM by design

### What the gateway path means

After the command runs successfully, Claude Desktop's inference pipeline routes through `https://ollama.com/...` instead of directly to Anthropic. Concretely:

- Every user prompt is sent as plaintext to ollama.com under the user's bearer-auth Ollama Cloud key.
- Every model response is fetched from ollama.com.
- Tool-use payloads, attached files, MCP-server outputs, system prompts, and any other turn content all flow through ollama.com.
- Claude Desktop's transport-layer encryption to ollama.com is TLS-as-usual; Ollama-the-company has plaintext access on the server side.

This is a feature, not a bug. It is how Ollama Cloud is intended to host Claude Desktop traffic for operators who prefer Ollama-managed billing or unified-API access. It is also a complete loss of the direct-to-Anthropic privacy posture that Claude Desktop has by default.

### What the operator is told

The CLI prints exactly two strings on success:

```
Claude Desktop profile changed to Ollama Cloud.
To restore the usual Claude profile, run: ollama launch claude-desktop --restore
```

There is no language about plaintext interception, log retention, telemetry, jurisdiction (Ollama, Inc. is US-based), or training-data implications. An operator who runs `ollama launch claude-desktop --yes` to skip confirmation receives nothing more than "Claude Desktop profile changed to Ollama Cloud."

### Recommendation

Ollama should expand the success message to surface the trust-boundary shift. Suggested copy:

> Claude Desktop profile changed to Ollama Cloud.
>
> All Claude Desktop prompts, responses, attached files, and tool outputs will now route through ollama.com and are visible to Ollama, Inc. Ollama's privacy policy and data-retention terms apply to your Claude Desktop traffic from now until you run `ollama launch claude-desktop --restore`.
>
> To restore the direct-Anthropic profile, run: ollama launch claude-desktop --restore

The change is single-string and ships in the next firmware push. No protocol or schema modification required.

## Finding 2: community-tutorial typosquat surface

### The unclaimed package

The npm package name `mcp-server-ollama` (verbatim, no scope) is referenced across:

- GitHub Issue [ollama/ollama#16005](https://github.com/ollama/ollama/issues/16005) (filed 2026-05-06)
- `ever-works/awesome-mcp-servers` (catalog repo)
- `andysingal/llm-course` (tutorial)
- `metorial/metorial-index` (catalog)
- `TensorBlock/awesome-mcp-servers`
- Multiple PyPI / GitHub catalog crawls that reference the name as if registered

The name is not registered. `https://registry.npmjs.org/mcp-server-ollama` returns HTTP 404 as of 2026-05-07.

Two adjacent names also unclaimed:

- `@ollama/mcp-server` — 404
- `@modelcontextprotocol/server-ollama` — 404

Two adjacent names that ARE registered (and therefore not part of this surface):

- `ollama-mcp-server` — 200
- `mcp-ollama` — 200

### The exploit chain

A user who follows any tutorial directing them to write the following into `~/Library/Application Support/Claude/claude_desktop_config.json`:

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

…sees Claude Desktop attempt to launch the MCP server on next start. Today this fails silently (404 from npm registry). The moment any party publishes a package named `mcp-server-ollama`, Claude Desktop will:

1. `npx -y mcp-server-ollama` (auto-install with no prompt, because of `-y`)
2. Spawn the MCP server process under the operator user
3. Wire its stdio into the Claude Desktop MCP transport
4. Forward tool calls and responses bidirectionally

Whoever owns the package owns the operator's Claude Desktop session: read every prompt, inject responses, exfiltrate clipboard via tool calls, write to disk via Claude's built-in `Filesystem` tool surface, etc.

### Why the surface persists

The npm registry permits anyone to register an unclaimed name. The MCP protocol specifies no signature or trust mechanism for command invocations. Claude Desktop reads `claude_desktop_config.json` and runs the listed commands without prompting the user for consent on each new MCP server. `npx -y` is the path-of-least-resistance install pattern repeated across community tutorials.

These four design choices compose into a typosquat-by-default architecture for any unclaimed package name that appears in a sufficiently-trafficked tutorial.

### Recommendation

Two parties should act:

1. **Ollama** should claim `mcp-server-ollama`, `@ollama/mcp-server`, and similar Ollama-namespaced MCP names with placeholder packages that loudly warn on invocation and direct the user to either the legitimate community bridge of choice (`ollama-mcp-server` or `mcp-ollama`) or to the gateway-mode flow that doesn't require an MCP bridge at all.

2. **Anthropic** should harden Claude Desktop's MCP-launch path:
   - Warn on first execution of any new `mcpServers[*].command` entry, naming the package and the registry it'd resolve from.
   - Surface `npx -y` invocations specifically as "downloading and executing arbitrary code from npm; confirm?".
   - Optionally maintain a `mcpServers` allow-list of known-safe packages that bypass the warning.

The third party (NuClide) will not register the unclaimed names. Speculatively claiming names creates registry pollution and shifts the failure mode from "silent 404" to "third-party-controlled placeholder", neither of which is the right end-state. The right end-state is vendor-side fixes from the two parties above.

## Finding 3: Issue #16005 is misframed

The reporter cites:

> `ollama launch claude-desktop` writes a configuration that references a non-existent npm package, causing the Claude Desktop integration to fail silently.

The v0.23.1 source does not write `mcpServers` entries at all (888 lines of `claude_desktop.go` have zero references to `mcp`, `npx`, `mcpServers`, or `npm` in any form). The config-writer (`writeClaudeDesktopGatewayProfile`) sets `inferenceProvider`, `inferenceGatewayBaseUrl`, `inferenceGatewayApiKey`, `inferenceGatewayAuthScheme`, and `disableDeploymentModeChooser`, then writes back via `writeClaudeDesktopJSON`. That writer reads the existing config (`readClaudeDesktopJSONAllowMissing`), updates the keys it manages, and re-serializes. **Keys it does not manage are preserved as-is.**

The most consistent explanation for what the reporter saw is that they had previously followed a tutorial that wrote an `mcpServers.ollama` entry pointing at `mcp-server-ollama`. When they then ran `ollama launch claude-desktop`, Ollama's writer added the gateway keys and preserved the `mcpServers` entry the user already had. The reporter, on inspecting the post-launch config and finding `mcp-server-ollama` in it, attributed authorship to the most recent writer (Ollama). The actual authorship is whichever tutorial they followed earlier.

This is a **misattribution attack surface**: when a config-mutator preserves keys it doesn't manage, downstream users may credit the mutator with content the mutator only failed to remove. From a security-research perspective the surface is benign (the user authored the bad key themselves), but from a product-trust perspective it is corrosive (the vendor inherits blame for community-tutorial pollution).

### Recommendation

Ollama's launcher should treat unrecognized top-level keys in `claude_desktop_config.json` as out-of-scope and either:

- Leave them alone (current behavior) **and** print a warning during the launch flow listing any such keys it found, so the user is aware that they exist and weren't authored by Ollama.
- Or migrate to a `--profile` style where Ollama writes a separate file (`Claude Desktop-3p/claude_desktop_config.json` is already partially this) and never touches the user's primary config at all.

The first option is one fmt.Println + a json.Decode pass; the second already exists for the third-party profile and could be expanded.

## Methodology Insight #11

> **Source code is authoritative; bug reports are framing.** When a bug report claims that a vendor wrote `X` to a config, verify against the vendor's source repository and current release tag before accepting the framing. Config mutators that preserve keys they don't manage are a misattribution attack surface; the right verification path is `grep` on the actual writer function, not `cat` on the post-mutation config.

This insight applies broadly:

- The Ulm CL1 case (Methodology Insight #10) was originally framed as "operator misconfiguration" by the SOC's first-pass intake; source-of-truth verification of the vendor's default systemd unit promoted the framing to "vendor-template default-no-auth" — different actor, different fix path.
- The 2026-05-04 SUNY Buffalo State misroute (Insight #4) was framed by our own pipeline as "send to UB"; WHOIS source-of-truth verification rerouted to Buffalo State.

The pattern: **always trace a claim back to the actor's own primary record before crediting or blaming.**

## Disclosure plan

Three threads:

1. **Comment on `ollama/ollama#16005`** — clarification post explaining that the v0.23.1 source does not write `mcpServers`; the reporter likely had a pre-existing tutorial-authored config; the real bug is the silent failure of the bridge they configured manually, not an Ollama-side bug. Suggest the maintainer mark the issue as `not-a-bug` with a note for future readers, or rename the issue to the actual problem ("Ollama's launcher preserves unrecognized keys, creating misattribution risk").

2. **Disclose to Ollama** (`security@ollama.com` or via their published security.txt if available) — two recommendations: (a) expand the success message to surface the gateway MITM, (b) claim Ollama-namespaced unclaimed npm names defensively.

3. **Disclose to Anthropic** (`security@anthropic.com`) — recommend Claude Desktop harden its MCP-launch path: warn on first execution of new `mcpServers[*].command` entries, treat `npx -y` specifically, optionally allow-list known-safe packages.

NuClide will not register the unclaimed names speculatively.

## IOCs

| Type | Value |
|---|---|
| Vulnerable command | `ollama launch claude-desktop` (v0.23.0+) |
| Config write path (macOS) | `~/Library/Application Support/Claude/claude_desktop_config.json` |
| Config write path (third-party) | `~/Library/Application Support/Claude-3p/claude_desktop_config.json` |
| Gateway endpoint | `https://ollama.com` |
| Gateway auth | `Authorization: Bearer <user-supplied Ollama Cloud key>` |
| Unclaimed npm names | `mcp-server-ollama`, `@ollama/mcp-server`, `@modelcontextprotocol/server-ollama` |
| Tutorial-poisoned config snippet | `{"mcpServers":{"ollama":{"command":"npx","args":["-y","mcp-server-ollama"]}}}` |
| Issue ref | [github.com/ollama/ollama/issues/16005](https://github.com/ollama/ollama/issues/16005) |

## References

- Ollama v0.23.1 source — [`cmd/launch/claude_desktop.go`](https://github.com/ollama/ollama/blob/v0.23.1/cmd/launch/claude_desktop.go)
- Ollama blog — [`ollama launch`](https://ollama.com/blog/launch) (2026-01-23)
- Claude Desktop integration docs — [docs.ollama.com/integrations/claude-desktop](https://docs.ollama.com/integrations/claude-desktop)
- Methodology Insight #10 — [vendor-template default-no-auth on research instruments](../../methodology/insight-10-vendor-template-default-no-auth.md)
- Methodology Insight #4 — [WHOIS-driven contact resolution](../../methodology/insight-04-whois-driven-contact-resolution.md)
