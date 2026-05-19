---
type: methodology
insight: 31
title: App-builder tools brand the OUTPUT, not the AGENT — anchor on agent API contract
---

# Insight #31 — App-builder tools brand the OUTPUT, not the AGENT

_Source: code-assistants survey verification, 2026-05-18. Extends Insight #6
(conjunctive marker-anchored matchers) and Insight #15 (~50% real-rate on
single-token dorks)._

## The rule

For AI **app-builder** tools (bolt.diy, Dyad, gpt-engineer, Vercel v0, Lovable,
and similar "build me an app" agents), the brand string appears in the HTML of
**the apps they generate**, not in the agent's own UI. Shodan dorks targeting
the brand catch a population of **end-user applications that were built using
the tool** — not deployments of the agent itself.

Worse than Insight #15's "single-token dork has ~50% FP rate" — these dorks
can run at **0% true-positive rate at the data-layer** if the agent is an
Electron desktop app or runs locally. The agent has no internet surface at all,
but its OUTPUT (every generated app) is internet-visible and carries its brand.

The corollary: **anchor on the agent's specific API contract, not the brand
string in body**. If the agent has no documented HTTP API, the platform may be
genuinely unmappable from Shodan and require a different discovery surface.

## Empirical basis

The 2026-05-18 code-assistants survey verification:

| Platform | Original "unauth" claim | Verified actually-agent | Verified actually-unauth-at-data-layer |
|---|---|---|---|
| bolt.diy | 14 | 0 (all `og:image=bolt.new/static/og_default.png` = generated apps) | 0 |
| Dyad | 22 | 0 (all `<title>dyad-generated-app</title>` = generated apps) | 0 |
| gpt-engineer | 11 | 0 (all match `storage.googleapis.com/gpt-engineer-file-uploads/og-images/` = GCS CDN for generated-app og:images) | 0 |
| **Subtotal app-builder** | **47** | **0** | **0** |
| OpenHands | 100 | 100 (real OpenHands UI on every host) | 61 |
| Sourcegraph | 19 | 19 (real Sourcegraph login page) | 0 (all "Private mode required") |
| Sourcebot | 14 | 14 (real Sourcebot login page) | 1 |
| Tabnine | 5 | 5 (real Tabnine Context Engine landing page) | 0 data-layer (landing page only) |
| OpenDevin | 2 | 2 (real OpenDevin catalog endpoint) | 0 (agent gated) |
| Sweep AI | 3 | 3 (real Sweep API surface) | 3 (limited routes) |
| CodeGeeX | 2 | 2 (real CodeGeeX admin UI) | 0 (login page only) |
| **TOTAL** | **192** | **145** | **65** |

**47 of 192 (24.5%) were app-builder false positives at the agent layer.**
Another **80 of 145 (55%) had auth-on at the data layer** — they returned 200
on the catalog HTML but 401 on actual data routes. The combined FP rate at
the data-layer is **127 of 192 = 66%**.

## Diagnostic signals — how to tell apart

When a Shodan dork for an AI-tool brand returns hits, check before counting:

1. **Look at og:image and twitter:image META tags** in the response HTML.
   If `og:image` points to the *tool's* CDN
   (`bolt.new/static/`, `gpt-engineer-file-uploads/`,
   `storage.googleapis.com/<tool>-...`), the host is a generated app, not the
   agent.
2. **Look at the HTML title.** If the title is `<tool-name>-generated-app`
   or `Create Next App` (default scaffold), it's an output, not the agent.
3. **Probe the agent's specific API endpoint.** OpenHands has
   `/api/options/agents` returning a JSON array of `[BrowsingAgent,
   CodeActAgent, ...]`. If the response shape does not match, it is not
   OpenHands. Test by JSON shape, not by name appearing in body.
4. **Check for catch-all routing.** If `/openapi.json` returns HTML, the host
   has SPA catch-all routing and most endpoints return the same React shell
   regardless of path. Status 200 on `/openapi.json` is not "the API exists";
   it's "the SPA framework returned its index for any unknown path."

## Procedural rules this insight generates

1. **Stage-2 verify probes for app-builder dorks**: require the anchor
   predicate to test the AGENT's API shape, not the brand string in body.
   For platforms without a documented agent API, **drop the dork** as
   unverifiable.
2. **Add og:image / twitter:image to the FP-trap check** — if a generated-app
   CDN is in the og:image URL, the host is the output, not the agent.
3. **For every "agent" platform in the catalogue**, document: does it run as
   a server (verifiable via API contract) or is it desktop/local-only
   (Shodan-dark for the agent itself)? If desktop-only, the brand-name dork
   is permanently unusable for agent enumeration.
4. **Build BARE-style platform-class fingerprints** that test by API
   contract rather than body text. The aimap convention is the right shape;
   port it to the verify-probe stage.

## Negative form (when this rule does NOT apply)

- Platforms with their own server-mode that exposes the agent on a public
  port: real OpenHands, real Sourcebot, real Tabnine — these can be
  legitimately found via brand dork because the agent IS the running server.
- Tools that don't generate user-facing apps with embedded branding (e.g.
  code-completion engines, code-search backends): no output to confuse with
  the agent. Brand dork is more reliable.

## Related insights

- **Insight #6** — conjunctive marker-anchored matchers. App-builder brand in
  body is a single-token match; this insight tightens that rule to "must
  test API contract, not body text."
- **Insight #15** — ~50% real-rate on single-token dorks. App-builder dorks
  can hit 0% at the data layer; this insight extends the FP ceiling.
- **Insight #21** — port-first beats brand-dork for low-footprint platforms.
  For desktop-only AI tools, port-first probes also fail — the tool has no
  port. They are genuinely Shodan-dark.

## Verification protocol going forward

When a Stage-1 fingerprint identifies a platform, the Stage-2 verify probe
MUST:

1. Hit an agent-specific JSON endpoint with a known response schema
2. Parse the response and confirm at least 2 fields match the expected
   schema
3. If the response is HTML, run the og:image FP-trap check before counting
4. Only call a host `confirmed_platform=true` if both shape-match AND no
   FP-trap signal fired

This is non-negotiable for any platform in the app-builder / generator
category.

## See also

- `case-studies/commercial/code-assistants-population-survey-2026-05-18.md`
  (originally published with the overclaim; corrected in the same file)
- `insight-06-conjunctive-marker-anchored-matchers.md`
- `insight-15-dork-hits-are-not-platform-instances.md`
- `insight-16-200-is-platform-identity-not-auth-state.md`
- `~/.claude/projects/-home-cowboy/memory/feedback_verify_before_claiming_exploitable.md` — the operator-level discipline that this insight implements at the methodology layer
