---
title: "aimap's AI-service classifier needs the ML data tier, not just the inference tier"
insight_number: 20
date: 2026-05-13
tags:
  - methodology
  - tooling
  - aimap
  - self-critical
  - ml-pipeline
related_research:
  - case-studies/commercial/smartshop-ai-pentech-disclosure-2026-05-13.md
source: case-studies/commercial/smartshop-ai-pentech-disclosure-2026-05-13.md
---

# Methodology Insight #20: aimap's AI-service classifier needs the ML data tier, not just the inference tier

## The insight

`aimap` classifies a target by what AI/ML services it can fingerprint on
that target's open ports. The catalog has been built incrementally around
the inference and observability tiers: Ollama, vLLM, llama.cpp, MLflow,
Phoenix, Langfuse, LangSmith, Helicone, Open WebUI, ChromaDB, Qdrant,
Milvus, etc. It does **not** yet treat the standard ML data tier as
AI-relevant: PostgreSQL, Redis, S3-compatible MinIO buckets, MailHog
sinks, Kafka brokers, RabbitMQ.

On the PENTECH host that anchored the SmartShop AI case study, aimap's
55-minute deep-enum across 19 ports returned exactly **one** "AI service
found" (Apache Airflow on port 8080) despite the same host running an
exposed MLflow tracker (port 5000), an exposed Redis (port 6379), an
exposed PostgreSQL (port 5432) that backs the MLflow tracker, and a Postfix
mail server. The visible AI/ML attack surface was understated by 4x.

## Why this matters

The undercount has three downstream effects:

1. **Operator-impact framing**. Disclosure emails generated from aimap's
   classification understate the operator's actual blast radius. A
   recipient reading "1 unauth AI service" responds with different urgency
   than one reading "AI service running on the same host as its backing
   PostgreSQL, Redis cache, and orchestration scheduler."
2. **Risk scoring**. VisorScuba and BARE consume aimap's output. A host
   that exposes the full ML data tier should score worse than a host that
   exposes only the tracker, but the current pipeline treats them
   equivalently.
3. **Operator attribution**. Same-host port adjacency is a high-signal
   attribution feature ("the team that runs the MLflow tracker also runs
   the Postgres on the same VM"). Without the data tier in the catalog,
   this signal is lost.

The aimap-profile companion does catch some of this via Shodan-passive port
enumeration, but the active aimap scan is where the per-port fingerprint
evidence lives. The split classification weakens both stages.

## What the catalog should add

Six ports/services worth treating as ML-data-tier AI signals when adjacent
to an inference- or tracker-tier service on the same host:

| Port | Service | AI-context signal |
|---|---|---|
| 5432 | PostgreSQL | MLflow backend store, Langfuse DB, embeddings tables |
| 6379 | Redis | Inference cache, session store for serving stacks |
| 9000 / 9001 | MinIO / S3-compatible | Local artifact store, RAG document corpus |
| 1025 / 8025 | MailHog | Inference-pipeline notification sink |
| 9092 | Kafka | Streaming inference, event-driven RAG |
| 5672 / 15672 | RabbitMQ | Inference queueing |

Standalone, none of these are "an AI service." Adjacent to a confirmed AI
service on the same host, every one of them is part of the ML pipeline and
should classify accordingly. The conjunctive matcher pattern (Insight #6: status_code + json_field +
body_contains) extends naturally to a
"adjacent-port" predicate: `port:5432 alongside port:5000` becomes an
MLflow-backend-store fingerprint that the standalone Postgres probe cannot
detect.

## How to apply

The rule was implemented in aimap v1.8.3 (2026-05-13). Implementation
shape:

1. Run the standard port enum.
2. After Phase 2 fingerprinting, derive `AdjacencyMatch` records: for
   each open port on a host with at least one confirmed AI/ML service,
   if the port appears in the data-tier catalog, emit an adjacency
   finding scaled to the catalog's per-port severity.
3. Adjacencies appear as a new section in the terminal output
   ("ML-ADJACENT INFRASTRUCTURE") and as a separate `adjacencies` key
   in the JSON report.
4. Severity counts in the report summary include adjacency findings.

Reference implementation: `adjacency.go` in the aimap repository,
covered by `adjacency_test.go` (6 tests). Live-validated 2026-05-13
against `78.135.66.61` (PENTECH BILISIM / SmartShop AI host). The
host's exposed Postgres on `:5432` and Redis on `:6379` now both
emit as ML-adjacent findings tied to the MLflow + Airflow services
on the same host.

Operational shape:

```bash
aimap -list ips.txt -ports "5000,80,443,8080" -o report.json
# Adjacencies present in the report under the "adjacencies" key,
# rendered in the terminal under ML-ADJACENT INFRASTRUCTURE.
```

## Self-critical note

This is a tooling gap our own work surfaced against our own tooling. The
PENTECH chain ran six tools across one host in parallel, and the
discrepancy between aimap's "1 AI service" and the full Shodan host
record's "11 ports / 27 CVEs / full ML pipeline" became visible only
because we cross-checked the outputs.

The lesson generalizes: **single-tool classifications should always be
cross-checked against the broader infrastructure record** when the host
is under deep-dive. Catalog gaps in one tool are invisible from within
that tool's output. They only show up against an external reference.

## When this could break

- **A host running just MLflow with co-located Postgres for a personal
  research project**. The data tier exposure is real but the operator
  impact is genuinely low. The adjacency-based reclassification should
  preserve severity nuance, not flatten everything to HIGH.
- **Honeypots running fake ML stacks**. Adjacent-port fingerprinting will
  flag honeypots that mimic the full stack. Insight #1 (honeypot
  self-filtering) already addresses this; the data-tier classifier should
  inherit the same protocol-strictness check.

## Discovery context

The PENTECH chain in the SmartShop AI case study ran aimap, visorgraph,
aimap-profile, Shodan host pull, JS-bundle extraction, and a controlled
set of anonymous API probes against `78.135.66.61`. The Shodan record
showed ports `[80, 110, 143, 443, 465, 587, 995, 5000, 5432, 6379,
8080]`. aimap's output reported `5000` as MLflow and `8080` as Airflow,
but emitted only Airflow as an "AI service found". MLflow was
fingerprinted but suppressed at the AI-classification stage by a
catalog-version mismatch. The Postgres + Redis + Postfix were never
classified as AI-related at all.

The visible asymmetry between aimap's narrow read and the broader Shodan
record was the prompt for codifying this gap as an insight rather than a
silent bug.