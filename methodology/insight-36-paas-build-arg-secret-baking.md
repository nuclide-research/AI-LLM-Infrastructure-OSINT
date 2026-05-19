---
type: methodology
insight: 36
title: PaaS deployment automation bakes build-time env-vars into client JS bundles; secrets prefixed with NEXT_PUBLIC_ / VITE_ leak to every visitor
---

# Insight #36. PaaS deployment automation bakes build-time env-vars into client JS bundles

_Source: AI cost / billing / usage analytics survey, 2026-05-19. Hetzner host `5.161.75.164:8888` running Dokploy (Coolify-class self-hosted PaaS) leaked `LANGFUSE_SECRET_KEY` to every visitor via webpack-baked client JS. The leak mechanism is PaaS-pattern, not operator-specific; it generalizes across Dokploy, Coolify, Caprover, Easypanel, Railway-style deployments, and any platform that exposes "build-time env vars" as a first-class configuration field._

## The rule

When an operator deploys a Next.js or Vite app via a self-hosted PaaS (Dokploy, Coolify, Caprover, Easypanel) and declares a secret like `LANGFUSE_SECRET_KEY` with one of:

- A `NEXT_PUBLIC_*` prefix (Next.js)
- A `VITE_*` prefix (Vite)
- Direct access via `process.env.SECRET_NAME` in client code

The build system hardcodes the secret into the client JS bundle at build time, and the secret ships to every browser that loads the page. The operator's intent ("set this env var so the build picks it up") is satisfied, but the deployment mechanism turns a "runtime secret" into a "public client constant."

**The framework does not warn the operator.** Next.js documents the `NEXT_PUBLIC_` behavior clearly, but the PaaS UI presents env-vars as a single bucket — no separation between "runtime-only" and "build-time-baked." Operators check the box, the build succeeds, the dashboard says "deployed," and the secret is on every visitor's machine.

## Empirical basis (Cost / billing survey, 2026-05-19)

Host `5.161.75.164:8888` returned `LANGFUSE_SECRET_KEY` via the Shodan body dork. WHOIS = Hetzner US. Port 3000 ran Dokploy (PaaS UI). Port 8080 ran a Next.js / Vite frontend. The leak path was reconstructed from Dokploy's documented build-arg behavior + the Next.js + Vite framework default behaviors:

1. Operator added `LANGFUSE_SECRET_KEY=sk-lf-XXXX` to Dokploy's env-var configuration (or to a `.env` file Dokploy reads).
2. The frontend code referenced `process.env.LANGFUSE_SECRET_KEY` directly, OR the operator prefixed the var as `NEXT_PUBLIC_LANGFUSE_SECRET_KEY=...` and referenced it as `process.env.NEXT_PUBLIC_LANGFUSE_SECRET_KEY` to make the build pick it up.
3. webpack/Vite saw the reference at build time and embedded the string literal into the chunked JS bundle.
4. Shodan crawled the deployed page, indexed the chunked JS, and the `LANGFUSE_SECRET_KEY` substring became searchable.

The leak is not a Dokploy bug. It is a Dokploy + Next.js / Vite + operator-misuse combination that ships the secret without anyone in the chain warning the operator.

## Diagnostic signals

A host is suspected of this leak class if **any** of the following fire:

1. **Dokploy / Coolify / Caprover / Easypanel UI exposed** alongside a Next.js or Vite frontend on adjacent ports
2. **`NEXT_PUBLIC_*` or `VITE_*` substring** present in the host's indexed HTML referencing a known sensitive variable name (e.g. `_SECRET_`, `_KEY`, `_TOKEN`, `_PASSWORD`)
3. **Known SaaS secret-key prefix** (`sk-lf-` for Langfuse, `sk-helicone-` for Helicone, `pk_live_`/`sk_live_` for Stripe, `xoxb-`/`xoxp-` for Slack, `ghp_` for GitHub) **inside the served HTML or JS bundle**
4. **`process.env.SECRET_NAME`** substring inside a chunked JS bundle (rare in compiled JS, but appears occasionally if the operator's code embeds it via template literals)

## Procedural rules this insight generates

1. **Dork the SaaS secret-key prefix directly.** This survey used `http.html:"sk-lf-"` and `http.html:"LANGFUSE_SECRET_KEY"` to find the Dokploy-leak host. The same dork pattern catches Stripe (`pk_live_`/`sk_live_`), Helicone (`sk-helicone-`), Slack (`xoxb-`/`xoxp-`), AWS (`AKIA`), GitHub (`ghp_`/`gho_`/`ghu_`), etc. when those secrets are baked into client bundles.

2. **Combine PaaS-UI dork + adjacent-port frontend dork** to identify high-risk PaaS deployments. E.g., a host serving Dokploy on port 3000 AND a Next.js frontend on adjacent port is a leak-class candidate; further dorks should check for the literal SaaS-secret-key prefix.

3. **Population-scale disclosure framing**: operators using PaaS-style deployment automation are typically small teams or single developers (not enterprise IT). The disclosure should be educational + actionable, not just "your key is leaked": explain the build-time-baking mechanism, the `NEXT_PUBLIC_*` / `VITE_*` distinction, and the correct pattern (server-side API routes that proxy the upstream API using the secret held only at runtime).

4. **PaaS-vendor education**: Dokploy, Coolify, Caprover, Easypanel could add a UI hint when an env-var is prefixed `NEXT_PUBLIC_*` / `VITE_*` AND its value matches a known SaaS-secret-key prefix pattern. The simplest fix in the PaaS UI is a literal warning: "This env-var starts with `NEXT_PUBLIC_` and will be embedded in the client bundle. Do not use this prefix for secrets."

5. **Cross-survey re-check**: past surveys (LLM Gateways, MCP, RAG framework) found many self-hosted AI products. Each is a candidate for the same leak class if the operator deployed via PaaS automation. Re-running the secret-prefix dorks against those harvests could surface additional findings.

## Relationship to prior insights

- **Insight #2 (single-template auth-off propagates at population scale)**: the same root pattern at a different layer. Insight #2 documents how a single misconfigured framework default leaks at population scale. Insight #36 documents how a single PaaS build-pattern leaks at population scale. The operator does not write the bug; the deployment system encodes it.
- **Insight #10 (vendor-template default-no-auth on research instruments)**: same family. The vendor template (here: the PaaS env-var-bucket UI) is the load-bearing variable; operator awareness cannot fix it because the awareness is exactly the gap the vendor design creates.
- **Insight #13 (shipping defaults are load-bearing)**: a corollary at the deployment-tool layer. PaaS shipping defaults (treating all env-vars as one bucket) are load-bearing because they propagate uniformly across the PaaS's customer fleet.
- **Insight #11 (source code is authoritative)**: the leak is in the source-built bundle, not in the operator's intent. Reading the bundle is the authoritative check; trusting the operator's "I configured it as a secret" claim is framing.

## Open questions

- **How many PaaS deployments are affected at population scale?** The Dokploy host was found via the `LANGFUSE_SECRET_KEY` env-var dork (1 hit). A cross-secret-prefix survey across all known SaaS secret patterns would establish the population.
- **Which PaaS is the highest-leak source?** Dokploy, Coolify, Caprover, Easypanel each have different UIs and different env-var-bucket designs. Empirical comparison would identify the worst offender.
- **Do PaaS vendors warn about the `NEXT_PUBLIC_*` / `VITE_*` pattern in their docs?** Most don't. A documentation-review pass per PaaS vendor would identify which ones are silent on this issue.

## See also

- `case-studies/commercial/cost-billing-analytics-survey-2026-05-19.md`: source survey
- `insight-02-single-template-auth-off-propagates.md`: parent class (single-template propagation at scale)
- `insight-13-shipping-defaults-load-bearing.md`: same load-bearing-default rule at a different layer
- Next.js docs on environment variables: https://nextjs.org/docs/pages/guides/environment-variables
- Vite docs on env-and-mode: https://vite.dev/guide/env-and-mode
- Dokploy docs on Next.js deployments: https://docs.dokploy.com/docs/core/nextjs
