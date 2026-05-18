---
type: tool-dev-log
title: "VisorBishop iter-4: Adjacent platforms (Opik, AgentOps, Phospho)"
date: 2026-05-11
class: tool
category: cross-platform-tool-validation
status: research-active
methodology: extending VisorBishop fingerprint coverage to 3 adjacent AI-observability platforms
---

# VisorBishop iter-4 · 2026-05-11

NuClide Research · 2026-05-11

## Summary

Fourth iteration of the Phase 3 loop. iter-1/2/3 expanded the
IP-direct-shadow port set; iter-4 expands **platform coverage**, adding
fingerprints for three platforms not in Phase 1's original sweep:

- **Comet ML Opik**: Dropwizard-based observability + experiment tracking
- **AgentOps**: agent-monitoring with Langfuse-as-trace-store pattern
- **Phospho**: open-source LLM analytics

VisorBishop v0.1.4 adds `opik.go`
and `agentops.go`
probers. Phospho's self-hosted population was too small to merit a
dedicated prober (see negative-result section below).

> **Reproduce with VisorBishop ≥ v0.1.4:** `visorbishop -i hosts.txt -ip-shadow`

**Headline findings:**

1. **`agenticorc.com` runs AgentOps + Langfuse on linked AWS hosts**, surfaced via a single AgentOps `/api/health` probe that discloses the backing Langfuse host (`https://107-21-194-219.sslip.io`, Langfuse v3.160.0).
2. **Opik self-hosted population is tiny** (1 of 21 cert-CN-matched hosts is real Opik). The 20 others are unrelated `.opik.net` domains (public-domain name collision).
3. **Phospho has 0 confirmed self-hosted instances**, the 16 Shodan-derived candidates are all biotech/biochem sites (`affbiotech`, `sabbiotech`, `kendallscientific`, etc.) where "phospho" appears as a chemistry term, not a platform identifier.

## Population summary

| Platform | Shodan dork | Total | Confirmed | Confirmation rate |
|---|---|--:|--:|--:|
| Opik | `ssl.cert.subject.cn:"opik"` | 21 | **1** | 5% |
| Phospho | `http.html:"phospho"` | 16 | **0** | 0% |
| AgentOps | `http.html:"agentops"` | 18 | **2** | 11% |

Total iter-4 new confirmed-platform yield: **3 instances** (1 Opik + 2 AgentOps).

The low confirmation rates reflect the **name-collision noise** problem
already documented in Phase 1 ("Phoenix AZ businesses" pattern). Generic
terms in HTML or TLS certs saturate dorks; only API-shape probing
disambiguates real platform instances from name-collision noise.

## Critical finding: AgentOps `/api/health` discloses backing Langfuse

**Host:** `54.197.255.244` (`controlplane.agenticorc.com`, AWS US-East-1)
**Platform:** AgentOps self-hosted
**Disclosure:** Backing Langfuse host URL via unauthenticated `/api/health`

```
$ curl -sk https://54.197.255.244/api/health
{"status":"ok","langfuse_host":"https://107-21-194-219.sslip.io"}

$ curl -sk https://107-21-194-219.sslip.io/api/public/health
{"status":"OK","version":"3.160.0"}
```

The AgentOps health endpoint **discloses the Langfuse instance that
AgentOps uses as its backing trace store**. The Langfuse instance is
itself properly auth-fronted on protected endpoints (Phase 1 pattern:
0% unauth across the Langfuse population), so direct exploitation
requires credentials. But the **discovery** is gratis: any external
party can map the AgentOps→Langfuse architecture without authentication.

This is the AgentOps analogue of [LangSmith's `/api/v1/info` customer
disclosure](langsmith-deep-dive-survey-2026-05-10.md) finding. Both are
"unauthenticated info-disclosure endpoints reveal more than just
version strings. They reveal architectural/customer context that
becomes load-bearing for targeted attacks."

The operator (`agenticorc.com`) appears to be an AI agent orchestration
SaaS. `controlplane.agenticorc.com` for AgentOps control plane,
`lf.agenticorc.com` and `107-21-194-219.sslip.io` for their Langfuse
backing store. Cross-platform attribution comes free with the
disclosure.

Phase 2 deep-dive on AgentOps would extend this. The source-level
audit for the `/api/health` shape, the population-level probe of
whether other AgentOps operators also disclose their backing
infrastructure. Queued for iter-5.

## Opik: tiny self-host population, well-defended where it exists

`ssl.cert.subject.cn:"opik"` returns 21 hits. After probing each:

| Host | Status |
|---|---|
| `opik.tilla.ai` (35.186.230.189, GCP US) | **Confirmed Opik** — `/api/is-alive/ping` returns healthy. Cloudflare-WAF blocks all other paths with 403. |
| `opik.tmb.kit.edu` (Karlsruhe Institute of Technology) | Returns nginx 404 on Opik API paths; not Opik (DNS-only branding). |
| 18 × `*.opik.net` subdomains | Unrelated. `.opik.net` is a public-suffix-style domain owned by an unrelated operator; subdomains include `xavier8888.opik.net`, `boomy.opik.net`, etc. — names collide with the Comet ML product. |
| 3 × 401-Authorization-Required | Possibly real Opik behind nginx basic auth (could not verify without credentials). |

**`opik.tilla.ai` posture:**
- `/api/is-alive/ping` → 200, healthy response (intentionally public per Opik docs)
- `/api/is-alive/ver`, `/api/openapi.json`, `/swagger`, `/api/v1/private/*` → 403 Forbidden (Cloudflare WAF blocks)
- All sensitive surfaces are behind both auth AND a WAF layer

This is the **inverse-Phoenix** pattern: Opik self-hosters are highly
defensive operators. The product has a small self-hosted population
(SaaS-first, similar to Helicone), but the operators that do self-host
tend to invest in proper WAF + auth fronting.

## Phospho: 0 confirmed self-hosted instances

All 16 Shodan hits on `http.html:"phospho"` are biotech/biochemistry
domain sites. `affbiotech.cn`, `sabbiotech.com`, `kendallscientific.com`,
`bioworlde.com.cn`, `antibodydirectory.com`, and similar. Where
"phospho" appears as a chemistry term (phosphorylation, phospho-signaling,
etc.).

One borderline case: `43.156.0.132:3000` returns a NextAuth.js-style
`307 → /en/auth/login` on `/health`, suggesting a real AI/observability
SaaS, but the `/api/v2/health` route doesn't return a Phospho-shaped
response. Could be a different LLM-related product using the same
NextAuth.js patterns. Not Phospho.

Phospho's GitHub population is small (mostly hosted at `phospho.ai`
SaaS); self-hosting isn't a primary deployment mode. **Negative result
ruled in**, no public-internet Phospho self-host population at
population scale on 2026-05-11.

## Methodological refinement: probe at multiple confidence layers

iter-4 reinforces a pattern from earlier iters: **Shodan dorks surface
candidates; API-shape probing confirms.** The confidence layers are:

| Layer | What it tells you |
|---|---|
| Shodan TLS-cert / HTML hit | Candidate; name-collision-noisy |
| Root HTML `<title>` match | Higher-confidence candidate; still noisy |
| Platform-specific health endpoint | True confirmation |
| Auth-protected endpoint behavior | Auth state confirmed |
| Co-located service (IP-shadow) | Operator hygiene profile |

The dork-only confidence is consistently 5-30% real-platform rate at
population scale. Real iteration needs the API-shape probe to be useful.

VisorBishop bakes this in: every `Prober.Probe` implementation requires
the platform-specific endpoint to respond with the correct shape before
flagging `Confirmed: true`. The Shodan hit is just the seed. The
prober is the disambiguator.

This is candidate for **Methodology Insight #15**: *Dork hits ≠
platform instances. Always probe the platform-specific API shape before
treating a host as a real instance. Confirmation rate < 30% at
population scale is typical for generic dorks.*

## Cross-platform attribution emerging

After iter-3 (Rogers' Phoenix + Qdrant on same host) and iter-4
(agenticorc's AgentOps + Langfuse on linked hosts), a pattern is
visible:

| Operator | Platforms co-located | Disclosure vector |
|---|---|---|
| Rogers (Canadian telecom) | Phoenix + Qdrant | Same IP, both unauth |
| agenticorc.com | AgentOps + Langfuse | AgentOps `/api/health` discloses Langfuse URL |
| reputacion.digital (Phase 2) | Phoenix + Prometheus + NFS + MailCatcher | Same IP, multiple unauth |
| Helicone benchmarkit.solutions (Phase 2) | Helicone + ClickHouse + Postgres | Same IP |
| Teetsh (Phase 2 / iter-1) | Phoenix + 4× MailHog | Per-region template |

The class pattern: **AI infrastructure operators co-locate multiple
platforms either on the same host or on linked hosts where one
discloses the others.** VisorBishop's value here isn't just per-platform
fingerprinting. It's the multi-platform cross-correlation that emerges
from running all probers on all hosts and surfacing the linkage.

Phase 4 (web UI) should visualize this. Operators-running-multiple-
platforms is the threat-graph natural unit.

## Performance

iter-4 sweeps:
- Opik: 21 hosts × 3 probe round trips (`/api/is-alive/ping`, optional `/api/is-alive/ver`, `/api/v1/private/projects`) → 22.5s
- Phospho: 16 hosts × 1 probe → 33.5s (slower due to many slow biotech sites)
- AgentOps: 18 hosts × 2 probes → 45.6s (some slow hosts)

All within iteration-cadence budget. VisorBishop v0.1.4 builds clean and runs against the existing iter-3 corpora without regression (verified via local smoke tests).

## Next steps

1. ~~iter-1: extended dev-tooling ports~~ ✓
2. ~~iter-2: message-broker ports (zero-yield, refined methodology)~~ ✓
3. ~~iter-3: AI-stack pipeline ports + Rogers find~~ ✓
4. ~~iter-4: adjacent platforms (Opik, AgentOps, Phospho)~~ ✓ (this document)
5. **Methodology Insight #15 writeup**. "Dork hits ≠ platform instances" + the confirmation-rate-at-population-scale pattern
6. **iter-5 candidates**: Argilla, Promptfoo, LiteLLM Proxy (different category, gateway not observability, but adjacent), Trulens, Inspekt-ML, LangChain Hub self-host
7. **Phase 4 (web UI)** for VisorBishop with multi-platform cross-attribution visualization

## Evidence pack

`~/recon/2026-05-10-llm-sweep/visorbishop-results/iter4/`
- `opik-noshadow.json` / `.csv`. Opik 21-host iter-4 sweep
- `agentops-noshadow.json` / `.csv`. AgentOps 18-host iter-4 sweep
- `phospho-noshadow.json` / `.csv`. Phospho 16-host iter-4 sweep
- `opik-shadow.json`, `agentops-shadow.json`. IP-shadow on confirmed instances
- `agenticorc-lf-shadow.json`: IP-shadow on the agenticorc-disclosed Langfuse host

Source: Nicholas-Kloster/VisorBishop@v0.1.4

Cross-references:
- [iter-3 case study](visorbishop-iter3-survey-2026-05-11.md)
- [LangSmith deep-dive (similar info-disclosure pattern)](langsmith-deep-dive-survey-2026-05-10.md)
- [Phase 3 case study](visorbishop-phase3-survey-2026-05-11.md)
- [Methodology Insight #12](../../methodology/insight-12-ip-direct-shadow.md)
