---
title: "Recon yield aligns with port-class operator intent, not port number"
insight_number: 14
date: 2026-05-11
tags:
  - methodology
  - port-selection
  - recon-strategy
  - ip-direct-shadow
  - hypothesis-driven
  - visorbishop
related_research:
  - case-studies/commercial/visorbishop-iter1-survey-2026-05-11.md
  - case-studies/commercial/visorbishop-iter2-survey-2026-05-11.md
  - case-studies/commercial/visorbishop-iter3-survey-2026-05-11.md
  - case-studies/commercial/visorbishop-phase3-survey-2026-05-11.md
source: case-studies/commercial/visorbishop-phase3-survey-2026-05-11.md
---

# Methodology Insight #14: Recon yield aligns with port-class operator intent, not port number

## Statement

When sweeping IP-direct-shadow ports for hidden surfaces on hosts already
fronted by an SSO reverse proxy (see Insight #12), the productive selector
is **what class of service the operator was deploying** — not the port's
formal IANA assignment, popularity rank, or even whether the port number is
"well-known."

Six iterations of the VisorBishop Phase 3 loop empirically confirmed this:
the ports that yielded findings tracked the operator's intent class
(application-tier dev tooling, message-broker tier, AI-stack pipeline,
adjacent observability), not the ports' position on any commodity scanner's
top-N list.

The class signal at corpus scale: **the iter-1 → iter-6 progression's
yield-per-iteration tracked the alignment between the port set and the
operator population's deployment intent**, not the number of new ports
added per iteration.

| Iteration | Port class | New ports | New unauth surfaces |
|---|---|--:|--:|
| iter-1 | Dev-tooling adjacent (Redis, MailHog, node_exporter) | 6 | 8 |
| iter-2 | Message-broker tier (NATS, Kafka admin, RabbitMQ mgmt) | 4 | **0** |
| iter-3 | AI-stack pipeline (Qdrant REST, Triton, model-serving) | 5 | 4 (incl. Rogers NetOps) |
| iter-4 | Adjacent observability (Opik, AgentOps, Phospho) | (platform expansion) | 4 |
| iter-5 | Adjacent tier (gateway/annotation/eval) | (platform expansion) | 35 |
| iter-6 | Full-population validation (LiteLLM 5,391 hosts) | (depth, not breadth) | **283** |

iter-2 yielded zero. The ports were chosen because they were "common
high-value targets" in the abstract — message brokers are sensitive
infrastructure. But Phoenix/Langfuse/Helicone operators don't co-deploy
message brokers on the same host. Their stack is observability + ML
pipeline, not microservices messaging. The port selection was operator-
class-misaligned.

iter-3 corrected this by hypothesizing **what an operator running Phoenix
would also have on the same host**. Answer: vector DB (Qdrant on `:6333`),
inference server, model-serving infrastructure. iter-3 hit Rogers
Communications' co-located Phoenix + Qdrant with 49 router/firewall/LB log
embedding collections — the single highest-impact finding of the chain
came from explicitly choosing ports along the operator-intent axis.

## How the failure mode arises

The default port-selection heuristic in most recon work is one of:

1. **Top-N popular ports** — masscan's top-100, nmap's top-1000. Ranked by
   internet-wide frequency, NOT by relevance to the operator class under
   study.
2. **"Well-known" ports** — IANA assignments. Same problem, plus stale —
   AI infrastructure didn't exist when most IANA assignments were made.
3. **CVE-driven** — ports associated with known CVEs. Yields when the
   CVE is recent; ignores zero-CVE misconfigurations that dominate
   AI infrastructure exposure.

All three default heuristics are operator-class-blind. They produce a
port set that's optimal for *some* recon work, but is rarely optimal
for *this specific population's* shadow surface.

The yield-vs-port-class observation: every recon iteration that added
ports on the operator-intent axis produced findings; every iteration
that added ports off-axis produced zero.

## How to apply

For any new platform-class survey, the port-selection prompt is not "what
are common ports" but "**what would an operator running this platform put
on the same host?**"

Concrete prompt template (the one used in iter-3):

> Operator just installed and exposed `<platform>`. They are running a
> `<platform-category>` stack. What other services do they likely run on
> the same host? Enumerate by:
> 1. Direct dependency (this platform requires service X)
> 2. Co-deployed pipeline component (operators usually deploy this platform
>    alongside service Y)
> 3. Adjacent observability/debugging (a `<platform-category>` developer
>    typically also has Z running locally)

Worked example for Phoenix:

| Hypothesis | Port to probe | iter-3 actual yield |
|---|---|---|
| Vector DB co-deploy | Qdrant `:6333`, Milvus `:19530` | 3 unauth Qdrant including Rogers (49 collections) |
| Inference server | Triton `:8000`, vLLM `:8000` | 1 confirmed (no critical) |
| Object storage | MinIO `:9000` | 20 hits (iter-2) |
| LLM cache | Redis `:6379` | covered in iter-1 (4 unauth) |

The yield-vs-port-class principle generalizes beyond AI infrastructure.
Any recon problem where the population has a non-uniform deployment
class should use intent-axis port selection — same operator → same
co-deployment patterns → same shadow surface.

## Why this matters at population scale

The default port-selection heuristics produce a fixed false-negative rate
that grows with population size. If 27% of operators expose IP-direct
shadow (Insight #12), and 60% of those operators run ports outside the
top-100, then sweeping only the top-100 misses ~16% of the population's
exposures. The fix is not "add more ports" — that produces noise — but
"pick the ports the operators actually use."

VisorBishop's iter-3 port set (15 hand-picked AI-stack ports) outyielded
iter-2's port set (15 message-broker ports) by a factor of infinity
(4 vs 0). Same probe budget, opposite outcomes, only the operator-intent
alignment differed.

## Relation to other insights

- **Insight #12 (IP-direct shadow)** establishes that shadow surfaces
  exist. Insight #14 is *how* to find them efficiently at the corpus
  scale that #12 implies.
- **Insight #13 (shipping defaults are load-bearing)** explains the
  population-scale clustering: when defaults are load-bearing, operator
  populations cluster around the same deployment shapes, which means
  intent-axis port selection has high signal-to-noise.
- **Insight #6 (conjunctive matchers required)** is about how to verify
  a fingerprint once a port is reached. Insight #14 is about which ports
  to reach in the first place.

## Concrete checklist for port-class alignment

When adding ports to a sweep, ask before each port:

1. **Operator intent**: would an operator running the primary platform also
   run this service on the same host?
2. **Auth posture**: does this service default to auth-off, or does it
   require a deliberate exposure mistake?
3. **Co-deployment evidence**: have we observed the co-deployment pattern
   in any prior recon, or is this a theoretical hypothesis?
4. **Yield bar**: if this port produces zero findings on the first 100
   hosts, do we remove it from the next iteration?

Ports that fail #1 or #3 should not enter the sweep at all. Ports that
fail #4 should exit the sweep at the next iteration boundary.

This is the discipline that turned VisorBishop's iter-2 zero-yield into
iter-3's Rogers-finding non-zero yield in one iteration.
