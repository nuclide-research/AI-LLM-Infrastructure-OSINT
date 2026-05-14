---
title: "Port-first discovery beats brand-dork discovery for low-footprint platforms"
insight_number: 21
date: 2026-05-14
tags:
  - methodology
  - discovery
  - shodan
  - agent-platforms
  - aimap
related_research:
  - case-studies/commercial/autogen-studio-survey-2026-05-14.md
source: case-studies/commercial/autogen-studio-survey-2026-05-14.md
---

# Methodology Insight #21: Port-first discovery beats brand-dork discovery for low-footprint platforms

## The insight

The standard population survey is dork-then-confirm: write a Shodan dork
that matches the platform's brand string, harvest the hits, confirm each
one. That works when the platform's web frontend carries
Shodan-indexable distinctive text.

It fails for a whole class of platforms: newer agent platforms,
locally-run developer tools, and any SPA whose shell carries no indexed
brand text. For these, the productive strategy inverts: **port-first
discovery**. Identify the platform's default server signature, harvest
that superset, and let a structure-anchored fingerprint do the
classification.

## Why brand dorks fail for these platforms

Two compounding reasons, both observed in the AutoGen Studio survey
(2026-05-14):

1. **The SPA shell has no indexed brand text.** AutoGen Studio is a
   Gatsby React app. Its `/` HTML carries the brand only in `<meta>` tags
   that Shodan does not reliably capture. Every brand dork returned
   near-zero:

   | Dork | Hits |
   |---|--:|
   | `http.title:"AutoGen Studio"` | 0 |
   | `http.html:"AutoGen Studio"` | 1 |
   | `http.html:"Build Multi-Agent Apps"` | 0 |

2. **Shodan crawls `/`, not `/api/*`.** The brand signature lives in the
   API responses (`/api/version`, `/api/health`), but Shodan does not
   crawl those routes. The only brand-ish dork that returned anything
   (`"Service is healthy" port:8081`, 5 hits) caught the handful of
   operators who happened to proxy `/api/health` at `/`.

A third structural reason: low-footprint platforms are often run locally
by design. AutoGen Studio's `autogenstudio ui` binds to localhost. The
public population is small to begin with, so even a working brand dork
would surface a thin set.

## The port-first method

1. **Identify the default server signature.** Not the brand, the
   *substrate*. AutoGen Studio runs on `uvicorn` at `:8081`. The Shodan
   query `port:8081 "uvicorn"` returns 6,403 hosts: a tractable superset
   containing the real instances plus every other FastAPI app on that
   port.
2. **Harvest the superset.** Sample it (2,000 hosts in the AutoGen
   survey), import to the intel DB.
3. **Classify with a structure-anchored fingerprint that probes `/api/*`,
   not `/`.** aimap's AutoGen Studio fingerprint probes `/api/version`
   and `/api/health` for unique-to-the-platform message strings. The
   classification fingerprint does the work the dork could not.

The yield is low but precise. In the AutoGen survey: 9 of 2,000 (0.45%)
classified as AutoGen Studio, and every one of the 9 was a real,
critical, unauthenticated finding. A brand dork would have surfaced 1
host. Port-first surfaced 9.

## When to reach for port-first

Reach for port-first discovery when:

- The platform's brand dork returns implausibly few hits relative to its
  GitHub stars / known adoption
- The platform is a SPA (React/Gatsby/Vue/Svelte) whose shell has no
  distinctive indexed text
- The platform's distinctive signature is in an `/api/*` route Shodan
  does not crawl
- The platform is commonly run locally by default (developer tools,
  agent IDEs, eval frameworks)

Stay with brand-dork discovery when the platform has a distinctive
`http.title` or `http.html` signature, a large public population, and a
server-rendered or otherwise-indexed frontend.

## What port-first requires from the fingerprint

The classification fingerprint has to be tighter than usual, because the
superset it runs against is dominated by *unrelated* services on the same
port. ~1,900 of the 2,000 `uvicorn:8081` hosts were not AutoGen Studio.
The fingerprint must:

- Probe an `/api/*` route, not the SPA shell
- Use a conjunctive match anchored on a unique-to-the-platform string
  (AutoGen Studio: the `/api/version` body message "Version retrieved
  successfully" plus the `data` JSON field)
- Carry an over-match guard against generic responses (a generic FastAPI
  health endpoint returning `{"status":true,"message":"OK"}` must not
  match)

This is more fingerprint engineering than a brand dork needs. The
trade is worth it: the fingerprint is reusable, the dork is not.

## Substrate-signature catalogue

Default server signatures worth knowing for port-first discovery of
common AI-platform substrates:

| Substrate | Default port(s) | Server signature | Platforms that use it |
|---|---|---|---|
| uvicorn | 8000, 8081, 8001 | `Server: uvicorn` or body `"uvicorn"` | FastAPI apps: AutoGen Studio, Mem0, many agent platforms |
| gunicorn | 5000, 8000 | `Server: gunicorn` | Flask apps: MLflow, many ML services |
| Gradio | 7860 | `Server` varies; body `gradio` | RVC, ComfyUI-adjacent, voice-cloning UIs |
| Next.js | 3000 | `_next/static` asset paths | Langfuse, Helicone, many dashboards |
| Gatsby | varies | `page-data.json`, `webpack-runtime` chunks | AutoGen Studio frontend |

The substrate is the harvest key; the fingerprint is the classifier.

## Discovery context

The AutoGen Studio survey was the first survey of the agent-platform
tier. The brand dork returned 1 host. Port-first discovery against
`uvicorn:8081` surfaced 2,000 candidates, of which aimap classified 9 as
real AutoGen Studio, all unauthenticated. The insight was forced by the
brand dork's failure: there was no other way to find the population.
