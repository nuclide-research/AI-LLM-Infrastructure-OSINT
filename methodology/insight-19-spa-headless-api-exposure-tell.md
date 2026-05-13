---
title: "SPA + headless API is a high-severity exposure tell"
insight_number: 19
date: 2026-05-13
tags:
  - methodology
  - operator-attribution
  - cdn-frontend
  - headless-api
  - vercel
  - cloudflare-pages
  - detection-heuristic
related_research:
  - case-studies/commercial/smartshop-ai-pentech-disclosure-2026-05-13.md
  - case-studies/commercial/promptlayer-disclosure.md
source: case-studies/commercial/smartshop-ai-pentech-disclosure-2026-05-13.md
---

# Methodology Insight #19: SPA + headless API is a high-severity exposure tell

## The insight

When a single-page application is hosted on a CDN platform (Vercel,
Cloudflare Pages, Netlify, GitHub Pages, etc.) and its bundled JavaScript
calls a same-brand API host of the form `https://api.<brand>.<tld>/...`, the
API host is *almost always* on infrastructure the operator manages directly,
and very often that infrastructure is unhardened.

The CDN provides TLS, edge caching, and DDoS protection for the static
frontend. The API surface that does the actual work lands wherever the
developer chose, and that choice is often a single cloud VM with no
authentication wall, no WAF, and the operator's data tier exposed on
adjacent ports of the same host.

The CDN-hosted SPA gives the operator (and any casual observer) a false
sense of security: the visible state is professional, the actual posture
is unhardened.

## Field-validated cases

| Operator | SPA host | API host | Backing infra | Severity |
|---|---|---|---|---|
| PromptLayer (April 2026) | Vercel | call to Make.com webhook from the bundle | hardcoded webhook secrets | LLMjacking / quota drain |
| Multiple Phase 5 MLflow operators | Vercel / Netlify | tracker on raw cloud VM | unauth MLflow + open data ports | CRITICAL |
| SmartShop AI / amazonrec.space (May 2026) | Vercel | `api.amazonrec.space` → single Turkish VM | unauth FastAPI + MLflow + Redis + Postgres + Airflow on one host | CRITICAL |

Three independent instances of the same pattern across the same six-week
window. The pattern is consistent enough to codify as a detection heuristic.

## Detection heuristic

For any operator under investigation whose primary web presence is on a CDN
edge:

1. Identify the CDN by HTTP response headers: `server: Vercel`, `cf-ray:`,
   `x-vercel-id:`, `x-served-by:` (Fastly), `via: 1.1 vegur` (Heroku
   stragglers), `server: Netlify`.
2. Fetch the index HTML and extract any `<script src="/assets/...">` or
   similar bundled-JS URLs.
3. Fetch the bundle. For typical SPA builds (Vite/Webpack/Turbopack) this
   is one 200KB–500KB file at a hashed path.
4. Grep for absolute URLs matching `https?://api\.[^"]+` or
   `https?://[^"]*\.<operator-domain>/api`.
5. Resolve the extracted API hostname. If it lands on a different ASN than
   the CDN edge, that resolved host is the soft target. Probe it directly.

The heuristic surfaces the headless API in under 30 seconds per operator
once automated.

## Why it works

CDN platforms market themselves as "deploy your frontend, we handle the
hard parts." They deliberately do *not* host long-lived stateful backends.
That separation of concerns is operationally correct, but it pushes the
backend onto whatever infrastructure the developer is comfortable with,
which for a small team is often the cheapest available cloud VM.

The same developer who pushes their frontend through a polished
Vercel/Cloudflare workflow may have stood up the API on a Turkish or
Indonesian or DigitalOcean shared-hosting VM in 20 minutes using a tutorial.
The resulting asymmetry (professional frontend, unhardened backend) is the
exposure-tell.

A second contributor: the CDN-hosted SPA usually pre-resolves the API
hostname in the bundle as a constant. The hostname *must* be a stable
public DNS name (so the SPA can call it from end-user browsers), which
means it's findable via passive DNS the moment the SPA ships. There is no
network hardening shortcut available; the API has to be reachable from
the open Internet by design.

## How to apply at population scale

For a platform-class survey, after extracting per-host operator domains:

1. Filter for hosts where the operator domain is on a CDN edge (cheap test:
   does the operator domain resolve to a known CDN ASN, while a `api.`
   subdomain resolves elsewhere?)
2. Pull the SPA bundle and apply the heuristic.
3. Probe the resolved API host directly.
4. Bucket findings: SPA+API on same ASN (less interesting, may be
   self-hosted edge) vs. SPA on CDN + API elsewhere (high-priority
   probe).

## What this is not

The heuristic does not catch:

- **Server-rendered apps** without a separate API hostname (the backend is
  on the same edge or behind it).
- **API gateways with proper authentication**. The heuristic surfaces the
  host, not the exposure level. The host still needs probing to confirm.
- **APIs accessed via the CDN's own proxy** (e.g. Vercel Edge Functions,
  Cloudflare Workers). These don't reveal a separate backend hostname in
  the bundle; the API call goes to the same edge.

It does catch the most common small-team deployment topology where a
solo dev or contractor splits frontend hosting from backend hosting along
"easy" lines and leaves the backend half exposed.

## Tooling

This heuristic becomes a VisorBishop stage in iter-9.
`discoverHeadlessAPI(target)`: given a CDN-fronted operator domain,
extract its largest JS bundle, parse for `api.*` URLs, resolve them, and
return the soft-target host record. Costs one HTTP fetch per operator;
returns either a high-priority probe target or nothing.

## When this could break

- **CDN platforms expanding backend hosting**. Vercel's Functions,
  Cloudflare Workers, and Netlify Functions all eat into the
  edge/backend split. Adoption is uneven across operator skill levels;
  expect this heuristic to remain effective for 2–3 more years before
  the topology shifts.
- **Backend-on-edge by default**. If framework defaults (Next.js,
  Remix, SvelteKit) push more developers to deploy the API alongside
  the frontend on the CDN, the soft-target host stops existing.
- **API gateway adoption**. Managed gateways (AWS API Gateway,
  Cloudflare API Gateway, Azure APIM) decouple the API hostname from
  the backend host, so DNS resolution stops pointing at the vulnerable
  VM. Operators who use a gateway are a different population.

For now, the pattern holds. Watch the cumulative case-count over the
next two quarters; if the rate of confirmed instances drops below 1 per
month while the platform-class survey volume holds steady, the topology
is shifting and the heuristic needs revisiting.