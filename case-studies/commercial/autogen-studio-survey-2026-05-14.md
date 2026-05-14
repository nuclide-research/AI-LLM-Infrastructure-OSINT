---
title: AutoGen Studio, agent-platform tier cloud survey 2026-05-14
date: 2026-05-14
class: substrate
category: agent-platforms
status: surveyed
methodology: port-first discovery (uvicorn:8081) then aimap fingerprint classification
---

# AutoGen Studio: agent-platform tier cloud survey 2026-05-14

NuClide Research

## Summary

First survey of the **agent-platform / autonomy tier**, the category the
[FUTURE-SURVEYS roadmap](FUTURE-SURVEYS.md) listed as entirely `not-yet`.

AutoGen Studio is Microsoft's agent IDE (the `autogenstudio` package, part
of `microsoft/autogen`). It is a FastAPI + Gatsby React application that
lets a user build, configure, and run multi-agent teams from a browser.

A port-first survey of 2,000 `uvicorn`-on-`:8081` hosts confirmed
**9 AutoGen Studio instances, and all 9 were fully unauthenticated**, 
a 100% unauth rate. Every one exposes the agent IDE's API surface to any
Internet client with no credential at all.

| Severity | Count | Finding |
|---|--:|---|
| CRITICAL | 9 | AutoGen Studio reachable, API readable without authentication |
| — of which `/api/teams` readable | 7 | Agent team definitions + embedded tool configs world-readable |
| — of which `/api/settings` readable | 5 | Model-client config world-readable (may carry provider API keys) |
| — `/api/sessions` readable | 9 | Agent conversation history (prompts, reasoning, outputs) world-readable |

## Why the agent-platform tier is the highest impact-per-host class

An exposed Whisper server is compute theft. An exposed vector DB is data
disclosure. An exposed **agent platform** is categorically worse: the
attacker inherits

1. **the agent definitions**, what the agents are, what they're for;
2. **the tool configs**, and AutoGen tool definitions routinely embed
   inline API keys and provider credentials;
3. **the conversation history**, every prompt, every reasoning step,
   every output the agents have produced;
4. **the autonomy itself**, if the instance can execute agent runs, the
   attacker can drive the agents, which means inheriting their outbound
   capability (whatever the agents' tools can reach, the attacker can now
   reach through them).

This is why all 9 findings are rated CRITICAL even before any
credential is confirmed in a tool config: the *class* of exposure is
agent-platform-takeover, not data-disclosure.

## Methodology

### The discovery problem

AutoGen Studio has almost no Shodan brand footprint. The standard dorks
return near-zero:

| Dork | Hits |
|---|--:|
| `http.title:"AutoGen Studio"` | 0 |
| `http.html:"AutoGen Studio"` | 1 |
| `http.html:"Build Multi-Agent Apps"` (the Gatsby site description) | 0 |
| `"Service is healthy" port:8081` (the `/api/health` body) | 5 |

The Gatsby SPA shell at `/` carries no Shodan-indexed distinctive text,
and Shodan only crawls `/`, not the `/api/*` routes where the brand
signature lives. AutoGen Studio is also overwhelmingly run locally
(`autogenstudio ui` binds to localhost by default), so the public
population is small to begin with.

### Port-first discovery

Rather than a brand dork, the survey used **port-first discovery**:
AutoGen Studio runs on `uvicorn` at `:8081` by default. The Shodan query
`port:8081 "uvicorn"` returns **6,403 hosts**, a tractable superset that
contains the real AutoGen Studio instances plus every other FastAPI app
on that port.

A 2,000-host sample was harvested, imported into the JAXEN intel database
(`empire.db`), and swept with `aimap`. aimap's AutoGen Studio fingerprint
(added in v1.9.0 for this survey) sorts the real instances out via two
source-verified probes:

- `GET /api/version` → `{"status":true,"message":"Version retrieved
  successfully","data":{"version":"..."}}`
- `GET /api/health` → `{"status":true,"message":"Service is healthy"}`

Both messages are unique-to-AutoGen-Studio strings; the version probe is
a conjunctive 3-condition match.

### Classification yield

Of 2,000 `uvicorn:8081` hosts, **9 classified as AutoGen Studio** (0.45%).
The other ~1,900 are unrelated FastAPI apps on the same port. The aimap
enumerator then probed each confirmed instance's data routes
(`/api/teams`, `/api/settings`, `/api/sessions`, `/api/gallery`) with an
arbitrary `user_id` query parameter, AutoGen Studio's data routes take a
`user_id` param, and with the optional `AuthMiddleware` disabled (the
default) that param is just an arbitrary string, so a `200` with a data
array confirms there is no authentication.

## The 9 confirmed instances

| IP | Port | Country | Hosting | Operator (VisorGraph cert-pivot) |
|---|--:|---|---|---|
| `120.92.209.128` | 8081 | CN | Beijing Kingsoft Cloud | (HTTP-only, no cert pivot) |
| `149.28.78.116` | 8081 | US | Vultr (Los Angeles) | `green-amazon.us`, `tiktok.green-amazon.us` — Chinese-commercial-operator naming pattern |
| `13.68.236.35` | 8081 | US | Microsoft Azure (Ashburn) | `be-admin.dev-vison.infiniticube.in` — Infiniticube, software-dev consultancy; this is a "Vison" product dev environment |
| `172.235.51.32` | 8081 | US | Linode (Los Angeles) | (HTTP-only, no cert pivot) |
| `156.67.28.177` | 8081 | DE | Contabo (Düsseldorf) | (HTTP-only) |
| `207.181.189.110` | 8081 | US | Southern Die Casters (Dallas) | (HTTP-only) |
| `45.190.20.91` | 8081 | BR | Veloso Net (Tabatinga) | `eta.vbarco.com.br` — VBarco, Brazilian company |
| `8.130.142.13` | 8081 | CN | Aliyun (Ulanqab) | (HTTP-only) |
| `50.116.8.185` | 8081 | US | Linode (Fremont) | `neurogen.cc` — NeuroGen; 44-node graph, full cPanel/WHM hosting stack co-resident with `mautic.neurogen.cc` (marketing automation), `crm.neurogen.cc`, `matrix.neurogen.cc` |

### Operator-attribution notes

The cert-pivot attributed 4 of the 9 hosts to identifiable operators:

- **Infiniticube** (`13.68.236.35`), an exposed AutoGen Studio in a
  *dev environment* for a client product called "Vison". The host also
  exposes a service on port 9090. Dev environments routinely carry the
  same credentials as production.
- **`green-amazon.us` operator** (`149.28.78.116`), the `.us` domain
  with `amazon`/`tiktok` subdomains matches the Chinese-commercial-
  operator non-tell documented in prior NuClide work (a `.us` TLD forces
  WHOIS exposure that the operator's home-jurisdiction TLD would not).
- **VBarco** (`45.190.20.91`), Brazilian company, `eta.` subdomain.
- **NeuroGen** (`50.116.8.185`), the highest-impact host. The cert
  graph shows AutoGen Studio is one component of a full marketing/CRM
  stack on shared cPanel hosting: Mautic, a CRM, a Matrix chat server,
  and an "automation" subdomain all co-resident. An attacker who reaches
  the AutoGen Studio instance is one host away from the operator's entire
  marketing-data and customer-relationship surface.

## What aimap's enumerator confirmed

All 9 instances returned `auth_status: none`. The enumerator's
per-endpoint findings:

| Endpoint | Hosts readable | What it exposes |
|---|--:|---|
| `/api/sessions` | 9 / 9 | Agent conversation history — prompts, intermediate reasoning, tool-call traces, final outputs |
| `/api/teams` | 7 / 9 | Agent team definitions; AutoGen team configs embed tool definitions that frequently carry inline API keys |
| `/api/settings` | 5 / 9 | Model-client configuration; may carry OpenAI / Anthropic / Azure OpenAI provider keys depending on operator setup |

The survey stopped at *readability* confirmation. Pulling actual team
data requires a valid `user_id`; that line was not crossed. The finding
is that the endpoints answer `200` to an unauthenticated client at all.

## Versions

The instances probed during the survey were running AutoGen Studio
`0.4.x` (e.g. `0.4.1.1` confirmed live on `120.92.209.128`), current
releases. These are live, modern deployments, not abandoned demos.

## BARE corpus analysis

Running the findings through BARE (semantic match against the 3,904-module
Metasploit corpus) returned only weak neighbors, the top match for the
`/api/teams` finding was a JetBrains TeamCity RCE (matched on the literal
word "team", score 0.51). **No Metasploit module is a real fit.** This is
the BARE signal that confirms AutoGen Studio exposure is a *first-party
authorization bug*, not a commodity-CVE chain. There is no module to run;
the finding is a novel exposure class.

## Methodology insight surfaced

### Insight #21: Port-first discovery beats brand-dork discovery for low-footprint platforms

Some platform classes: particularly newer agent platforms and locally-run
developer tools: have almost no Shodan brand footprint because their SPA
shells carry no indexed distinctive text and Shodan crawls only `/`. For
these, the productive discovery strategy is **port-first**: identify the
platform's default server signature (here, `uvicorn` on `:8081`), harvest
that superset, and let a structure-anchored fingerprint do the
classification.

This inverts the usual order. The standard survey is dork-then-confirm.
For low-footprint platforms it must be **port-harvest-then-classify**, and
the classification fingerprint has to probe an `/api/*` route rather than
the SPA shell. aimap's AutoGen Studio fingerprint was built specifically
to probe `/api/version` and `/api/health` for exactly this reason.

The yield was 0.45% (9 of 2,000), low, but every one of the 9 was a
real, critical, unauthenticated finding. A brand dork would have surfaced
1 host. Port-first surfaced 9.

## Class behavior: agent platforms ship without auth-as-default

AutoGen Studio's `AuthMiddleware` is **optional and off by default**. The
documented assumption is that the operator runs it locally or bolts auth
on via surrounding infrastructure (a reverse proxy with auth, a VPN, K8s
ingress). The survey result: **0 of 9 operators bolted it on.** Every
publicly-reachable AutoGen Studio in the sample was wide open.

This matches the Tier-A* pattern (auth-optional, off-by-default) and the
load-bearing lesson from [Methodology Insight #13](../../methodology/insight-13-shipping-defaults-load-bearing.md):
when a platform ships without authentication enabled by default, the
population-scale exposure rate tracks the shipping default, not operator
intent. AutoGen Studio is a new data point on the same curve.

## Remediation

For AutoGen Studio operators:

1. **Enable `AuthMiddleware`.** AutoGen Studio supports authentication;
   it is off by default. Set it up before exposing the instance.
2. **Do not expose `:8081` to the public Internet.** AutoGen Studio is
   designed to be run locally or behind a private network boundary. If
   remote access is needed, put it behind an authenticating reverse
   proxy or a VPN.
3. **Audit tool configs for inline credentials.** AutoGen team
   definitions can carry API keys inline; rotate any that have been
   exposed and move secrets to environment variables or a secret store.
4. **Treat dev environments as production.** The Infiniticube finding is
   a dev environment: dev instances routinely carry production-grade
   credentials and are exposed more casually.

## Evidence pack

`~/recon/2026-05-14-autogen-studio/`

- `jaxen/uvicorn-8081-corpus.json.gz`, the 2,000-host Shodan corpus
- `jaxen/uvicorn-8081-ips.txt`, extracted IP list (imported to empire.db)
- `aimap/autogen-sweep.json`, full aimap report
- `aimap/autogen-sweep.autogen.tsv`, the 9 confirmed instances + findings
- `visorgraph/*.json`, per-host cert-pivot graphs
- `artifacts/host-geo.json`, Shodan geo/ASN enrichment
- `artifacts/bare-output.json`, BARE module ranking

VisorLog ledger: findings #874–#882.

## Cross-references

- [FUTURE-SURVEYS, Agent platforms section](FUTURE-SURVEYS.md), this
  survey opens that section
- [Methodology Insight #13: shipping defaults are load-bearing](../../methodology/insight-13-shipping-defaults-load-bearing.md)
- aimap v1.9.0, AutoGen Studio fingerprint + enumerator
