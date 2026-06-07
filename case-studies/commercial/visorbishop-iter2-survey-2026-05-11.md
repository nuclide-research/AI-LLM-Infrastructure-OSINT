---
type: tool-dev-log
title: "VisorBishop loop-iteration #2: Extended port set, exposure-inventory pivot"
date: 2026-05-11
class: tool
category: cross-platform-tool-validation
status: research-active
methodology: re-running VisorBishop with 21-port IP-shadow set (vs iter-1's 15) across all Phase 1 corpora to test which additional service classes are exposed
---

# VisorBishop loop-iteration #2 · 2026-05-11

NuClide Research · 2026-05-11

## Summary

Second iteration of the Phase 3 loop-back. Iter-1 added 4 ports beyond
the original Phase 2 port list and found 8 new unauth services. Iter-2
adds **6 more ports**, bringing the IP-direct-shadow list from 15 → 21:

<!-- ksat-tag:auto-generated:start -->
## DCWF KSAT coverage

Auto-derived from DCWF AI work-role rule files (`ksat-tag`).

- **672 (AI Test & Evaluation Specialist):** K7003, K7004, S7068, S7070, S7075, T5858, T5904
- **733 (AI Risk & Ethics Specialist):** T5868
- **overlap (Common AI KSATs (all 5 roles)):** K108, K1158, K1159, K22, K6311, K7003

<!-- ksat-tag:auto-generated:end -->

| New in iter-2 | Service |
|---|---|
| 1883 | (reserved for MQTT in a later iter; not added yet) |
| 4222 | NATS (protocol probe: INFO frame `auth_required` field) |
| 5044 | Logstash beats-input |
| 5672 | RabbitMQ AMQP |
| 9000 | MinIO API (`/minio/health/live` + anonymous `ListBuckets` test) |
| 9092 | Kafka |
| 11211 | Memcached (`version` command) |

> **Reproduce with VisorBishop ≥ v0.1.2:** `visorbishop -i hosts.txt -ip-shadow-all`

**Headline finding: 0 NEW unauthenticated services across all five
populations.** None of the 6 added ports surfaced a single unauth
exposure beyond what iter-1 already found.

But the **exposure inventory expanded significantly**: iter-2 revealed
**20 MinIO API instances + 12 ClickHouse instances open** on platform IPs
that iter-1's port list didn't probe. None are anonymously exploitable,
but all 32 are reachable to credential-stuffing against documented
defaults.

The negative result is the result. Iter-2 confirms the AI-observability
population is **not co-located with the message-broker tier** (NATS,
Kafka, RabbitMQ). Those services either aren't deployed on these hosts
or are properly firewalled. The interesting exposure lives in
**state-tier services** (Redis, ClickHouse, Postgres, MinIO) where
operators deliberately publish endpoints and trust per-service auth.

## Per-platform iter-2 deltas vs iter-1

| Platform | Iter-1 unauth | Iter-2 unauth | Δ | New service classes |
|---|--:|--:|--:|---|
| Phoenix | 14 | 14 | 0 | none |
| Langfuse | 2 | 2 | 0 | none |
| LangSmith | 0 | 0 | 0 | none |
| Helicone | 2 | 2 | 0 | none |
| OpenLIT | 1 | 1 | 0 | none |

**Total iter-2 new unauth yield: 0.**

The Phoenix-class operator population is uniformly NOT running
NATS/Kafka/RabbitMQ/Memcached/Logstash unauth on the same hosts. Either
they don't run those services, or they firewall them, or they put them
on different boxes. The class pattern: **observability ops + dev-tooling
co-location, NOT observability ops + message-broker co-location**.

## What iter-2 DID surface: exposure-inventory expansion

While no new ports yielded unauth findings, the 21-port sweep mapped the
broader exposure surface that iter-1 missed:

### 20 MinIO API instances exposed on platform IPs

The bundled-MinIO-with-AI-observability pattern is widespread. Per
[helicone-deep-dive-survey-2026-05-10.md](helicone-deep-dive-survey-2026-05-10.md),
Helicone's `docker-compose.yml` ships MinIO with `S3_ACCESS_KEY=minioadmin`
+ `S3_SECRET_KEY=minioadmin`. Iter-2 shows operators publish port 9000
across all observability platforms:

| Platform | Hosts with MinIO API open |
|---|--:|
| OpenLIT | 7 |
| Phoenix | 5 |
| Helicone | 5 |
| Langfuse | 2 |
| LangSmith | 1 |
| **Total** | **20** |

None are anonymously listing buckets (the `/` endpoint check returns
403 AccessDenied for every probed host). But each represents a
credential-stuffing target for `minioadmin:minioadmin`. We don't
credential-test, so we don't know how many would fall, but the
exposure pattern is documented.

### 12 ClickHouse instances exposed on platform IPs

The OpenLIT operator population leads here:

| Platform | ClickHouse hosts | Unauth | Notes |
|---|--:|--:|---|
| OpenLIT | 7 | 0 | All auth-fronted; 30% of OpenLIT population exposes 8123 |
| Helicone | 2 | **2** | `benchmarkit.solutions` — Phase 2 actualized CRITICAL |
| Langfuse | 1 | 0 | `langfuse.revdot.ai` Phase 2 finding |
| LangSmith | 1 | 0 | new — not in Phase 1+2 |
| Phoenix | 1 | 0 | new — not in Phase 1+2 |

The OpenLIT pattern is striking: **7 of 23 OpenLIT operators publish
ClickHouse 8123 publicly.** All are auth-fronted, but the install
template/docs may not call out port-binding hardening. Worth a follow-on
case study on OpenLIT's deployment-default risk surface.

### Other exposed services (open but auth-fronted)

| Service | Total hosts open | Unauth |
|---|--:|--:|
| Postgres | 19 | 0 (no credential testing) |
| Prometheus | 37 | 4 |
| MongoDB | 5 | 0 (no protocol probe) |
| MySQL | 2 | 0 |
| AlertManager | 2 | 0 |
| Kafka | 1 | 0 |
| Logstash | 0 | — |
| RabbitMQ | 0 | — |
| Memcached | 0 | — |
| NATS | 0 | — |

The complete absence of NATS/Kafka/RabbitMQ/Memcached unauth on these
hosts confirms the AI-observability tier doesn't co-locate with the
message-broker tier in our population.

## Methodology refinement from iter-2

The hypothesis going into iter-2: "more ports = more findings." That's
**false**. The right framing is "more ports = better exposure inventory,
even when 0 are unauth."

The exposure inventory matters because:

1. **Credential-stuffing readiness**: 20 MinIO APIs with documented
   default creds are 20 potential single-curl compromises if the
   operator left the default. We don't test, but the targets are now
   catalogued.
2. **Defense-in-depth audit**: 12 ClickHouse exposures means 12
   operators rely on per-service password rather than network ACLs.
   When the password leaks (env-var dump, container escape, etc.), the
   compromise is one connection away.
3. **CVE-window targeting**: when a future CVE drops against any of
   these services, the exposure list is the targeting roster.

This is the candidate for **Methodology Insight #14**: *The tool's
output is not just "findings". It's a maintained exposure inventory.
Iterations that surface 0 new unauth still surface new exposure surface,
which becomes load-bearing the moment defaults change or CVEs land.*

## What we did NOT find: and what that proves

iter-2 specifically did NOT find:
- A single unauth NATS server (despite our `INFO`-frame probe ready to detect it)
- A single unauth Memcached server (despite our `version` probe ready to detect it)
- A single unauth Kafka, RabbitMQ, Logstash port

This is a **meaningful negative result**. It rules out a hypothesis we'd
been carrying since the ParamWallet NATS finding
on 2026-05-09. That "AI infrastructure operators run NATS unauth
because the deployment templates don't call it out." That's true for
the ledger/agent-pipeline tier (ParamWallet was an AI pipeline), but
**not** for the AI-observability tier (Phoenix/Langfuse/Helicone/
LangSmith/OpenLIT operators). Different operator populations, different
exposure profiles.

Methodologically: the right shape of every iteration is to test a class
hypothesis, not just "scan more ports." The negative results constrain
the threat model as much as the positive ones do.

## Iter-2 plan refinement for iter-3

Given iter-2's empty-yield on message-broker ports, iter-3 should probe
**different classes** rather than more of the same:

- **Web admin UIs**: Portainer (9000 conflict-free, but at 9443 or alt
  ports), Adminer (8080-style), Grafana (3000, already in our list but
  not specifically targeted as Grafana), n8n web UI, RClone Web GUI
- **AI-stack ML pipeline admin**: MLflow UI port (5000), Kubeflow UI
  (8080), Airflow webserver (8080), Streamlit (8501), Gradio (7860),
  Comet UI
- **Vector DBs**: Qdrant (6333), Milvus (19530), Weaviate (8080),
  ChromaDB (8000)
- **Container/k8s admin**: Docker Registry (5000), Kubernetes API (6443),
  kube-state-metrics (8080)

The "AI-stack ML pipeline" set is the most-aligned with the Phoenix-class
operator profile we already understand. Likely to yield non-zero on the
existing population.

## Bug fixes shipped during iter-2

None this round. The iter-1 fixes (URL-parser, port-parallelism) made
iter-2 trivially fast. 24 seconds for the full Phoenix sweep, 1m34s for
the Langfuse 381-host sweep. Both well within iteration-cadence budget.

## Next steps

1. ~~Build VisorBishop v0.1 (Phase 3)~~ ✓
2. ~~Loop iter-1: re-sweep all Phase 1 corpora~~ ✓
3. ~~Loop iter-2: extended port set (message brokers, MinIO, Memcached)~~ ✓ (this document)
4. **Loop iter-3**: AI-stack ML pipeline ports (MLflow UI, Airflow, Streamlit,
   Gradio, vector DBs). Higher likelihood of yield than message brokers.
5. **Methodology Insight #14 writeup**, the "exposure inventory > findings count" reframe
6. **Phase 4 (web UI)** still queued

## Evidence pack

`~/recon/2026-05-10-llm-sweep/visorbishop-results/iter2/`
- `phoenix-shadow.json` / `.csv`. 94-host Phoenix iter-2 sweep
- `langfuse-shadow.json` / `.csv`. 381-host Langfuse iter-2 sweep
- `langsmith-shadow.json` / `.csv`. 96-host LangSmith iter-2 sweep
- `helicone-shadow.json` / `.csv`. 21-host Helicone iter-2 sweep
- `openlit-shadow.json` / `.csv`. 23-host OpenLIT iter-2 sweep

Source: Nicholas-Kloster/VisorBishop. 21-port `ShadowPorts` list at `internal/probe/ipshadow.go`

Cross-references:
- [iter-1 case study](visorbishop-iter1-survey-2026-05-11.md): what we found before adding these 6 ports
- [Phase 3 case study](visorbishop-phase3-survey-2026-05-11.md): original tool ship
- [Helicone deep-dive](helicone-deep-dive-survey-2026-05-10.md): `benchmarkit.solutions` unauth ClickHouse + `minioadmin:minioadmin` doc-default
- [Methodology Insight #12](../../methodology/insight-12-ip-direct-shadow.md): IP-direct-shadow methodology
