# Insight #82: API-gateway guardrail vendors emit vendor-branded error bodies at HTTP 400 without auth, by design. The error string IS the cheap-fingerprint banner.

**Codified:** 2026-06-07. Cat-33 Phase 3B Lane B survey.
**Source:** `data/platform-intel/cat33-lane-b-vendors-2026-06-07.md` (3 vendors).
**Family:** Insight #16 (status-code-is-identity-not-auth-state), Insight #52 (an-http-200-at-an-api-path-is-not-that-api), Insight #73 (header-versioned APIs evade headerless fingerprinters).
**Falsifiability tier:** medium. n=3 confirmed at population level; a fourth would promote to high.

## The pattern

Three API-gateway guardrail vendors (Lakera Guard, Prompt Security, AegisAI) all return distinctive vendor-branded error bodies when the marker endpoint is called without authentication. The errors are not a security failure: they are deliberate developer-experience choices to make customer integration debugging easier. The side effect is that the error body becomes the cheapest possible vendor banner.

| Vendor | Marker endpoint | Unauthenticated response | Distinctive payload |
|---|---|---|---|
| Lakera Guard | `POST /v1/guard` | HTTP 400 | error body includes `docs.lakera.ai/docs/api` literal |
| Prompt Security | `GET /v1/protect` | HTTP 400 | JSON `{"status":false,"error":"No api key provided"}` |
| AegisAI | branded console SPA marker | HTTP 200 (SPA shell) | branded JS bundle name + console route |

The marker probe is one HTTP call, no auth needed, response distinguishes vendor cleanly from generic 400/401/403 noise.

## Why this matters

For a population-scale survey of API-gateway guardrail vendors, the distinguishing payload at HTTP 400 is structurally more useful than the cert-CN or the favicon-hash. Cert-CN scopes too narrowly (operator deployments often use customer cert, not vendor cert). Favicon-hash misses headless deployments. The error body sits at the API surface itself, is operator-independent, and is fingerprint-stable across versions because it is exposed integration metadata, not internal state.

This generalizes the Insight #16 lesson (status code is identity, not auth state) in a constructive direction: when the vendor has gone out of their way to make error bodies developer-friendly, the friendliness is the dork.

## How to apply

- For any API-gateway vendor, the first marker probe should be unauth-POST against the documented inference endpoint and read the error body, not the status code.
- Build aimap fingerprints anchored on the body marker, not the path. The path is changeable; the developer-friendly error string is stable for years.
- For Shodan: search the error literal in `http.html`, not the path. Limited to vendors whose self-hosted customers expose the surface, but a non-trivial subset will.

## Confirmation pending

Three vendors hit the pattern. A fourth (Pillar Security, Aporia, or Hiddenlayer would be natural candidates) would promote to high-confidence numbered insight. Until then, this is a medium-confidence pattern call.

## DCWF KSAT fit

- 672: K7044 (V&V tooling via fingerprint banner), T5919 (verify with marker probe).
- 733: K7051 (developer experience as an information leak is an ML blind spot at the architecture level).
- Overlap: K7003, K22.
