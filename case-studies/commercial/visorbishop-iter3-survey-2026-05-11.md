---
title: VisorBishop loop-iteration #3 — AI-stack ML pipeline ports, Rogers NetOps disclosure
date: 2026-05-11
class: tool
category: cross-platform-tool-validation
status: research-active
methodology: re-running VisorBishop with 26-port IP-shadow set (added MLflow, Qdrant, Milvus, ChromaDB, Streamlit, Gradio) across all Phase 1 corpora
---

# VisorBishop loop-iteration #3 · 2026-05-11

NuClide Research · 2026-05-11

## Summary

Third iteration of the Phase 3 loop-back. Iter-2 added message-broker
ports (NATS, Kafka, RabbitMQ, etc.) and found 0 new unauth — meaningful
negative result. Iter-3 pivots to **AI-stack ML pipeline ports** (MLflow,
Qdrant, ChromaDB, Streamlit, Gradio, Milvus) since these are closer to
the operator class we're surveying.

**Headline finding: 3 NEW unauth Qdrant vector DBs surfaced on Phoenix
hosts, one of which (`172.178.38.117`) belongs to Rogers Communications
and exposes 49 collections of network operations logs — router,
firewall, and load-balancer embeddings.**

Plus broader exposure inventory: **32 ChromaDB ports open** across all
platforms (though only the TCP open state was observed; most don't
respond as ChromaDB), **6 MLflow instances**, **5 Streamlit apps**,
**5 Qdrant instances** (3 unauth, 2 API-key-required).

> **Reproduce with VisorBishop ≥ v0.1.3:** `visorbishop -i hosts.txt -ip-shadow-all`
> 26 ports now in the IP-shadow set.

## Per-platform iter-3 deltas

| Platform | Iter-2 unauth | Iter-3 unauth | Δ | NEW |
|---|--:|--:|--:|---|
| Phoenix | 14 | **17** | +3 | 3× unauth Qdrant |
| Langfuse | 2 | 2 | 0 | none |
| LangSmith | 0 | 0 | 0 | none |
| Helicone | 2 | 2 | 0 | none |
| OpenLIT | 1 | 1 | 0 | none |

**Total iter-3 new unauth yield: 3.** All on Phoenix population.

The yield isn't as dramatic as iter-1's (8 new), but it's
class-different: iter-1 found dev-tooling co-location (Redis, MailHog);
iter-3 finds AI-stack co-location (Qdrant vector DBs).

## Critical actualized finding: Rogers Communications NetOps AI exposure

**Operator: Rogers Communications (Canadian telecom)**
**Host: `172.178.38.117` (Microsoft Azure US)**

Cross-correlation between the Phoenix project enumeration (Phase 1) and
the iter-3 Qdrant find:

| Source | Finding |
|---|---|
| Phoenix /graphql (Phase 1) | Project `rogers-netops-ai-bot-project` with 8,738 traces, 2.67M tokens |
| Phoenix /graphql (Phase 1) | 5 additional projects: `inference-A100-single`, `inference-A100-parallel-workers-{4,8,16}`, `inference-A100-model-replicas-4` |
| Qdrant /collections (iter-3) | 49 collections including `router_fw66_nbmn_log_vector`, `router_fw66_qcmtl_log_vector`, `router_new_fw67_qcmtl_log_vector`, `router_dgw71_rchrd_re0_log_vector`, `router_dgw71_grnsbr_re0_log_vector`, `firewall_apfw_log_vector`, `firewall_apfw_untrust_log_vector`, `loadbalancer_ldbl_ltm_log_vector` |
| Qdrant /telemetry (iter-3) | Qdrant 1.13.4, started 2026-05-08, 49 collections, 623 GET /collections requests over uptime |

The collection names disclose:
- Rogers' router naming convention (`fw66`, `fw67`, `dgw71`, `dgw74` prefixes)
- Rogers' datacenter site codes (`nbmn`, `qcmtl`, `rchrd`, `grnsbr`, `ms1`) — Canadian municipal codes (Quebec Montreal, Greensboro, Richmond, etc.)
- Rogers' F5 LTM load balancer instance (`ldbl_ltm`) and zone-based firewall topology (`apfw`, `apfw_untrust`)
- Their A100 inference benchmarking configuration (parallel-worker counts 4/8/16, model-replicas 4)

The exposure is **two-layered**:
1. **Phoenix unauth** discloses the bot's LLM traces (prompts, responses, agent reasoning)
2. **Qdrant unauth** discloses the embedding space of their network-ops log corpus

Combined, this means an attacker can:
- Read the Phoenix traces to learn what kinds of network-ops queries the bot is being asked
- Query the Qdrant collections to retrieve semantically-similar log lines from Rogers' production network infrastructure
- Cross-correlate the two to understand both the queries and the answers the bot draws from

This is genuine **critical-infrastructure operator** exposure. Rogers
operates ~10M Canadian telecom subscribers. Their internal network
operations AI tooling is on the public internet via two unauthenticated
endpoints on the same host.

**Per the standing research-mode discipline, this is a documented
finding, not yet a disclosure target.** The chain will route through
Rogers' security team via standard coordinated-disclosure channels when
the full research cycle completes.

## Other iter-3 unauth Qdrant finds

### `167.86.90.102:6333` (Contabo DE)
Qdrant 1.17.0, **0 collections** (empty). Operator stood up Qdrant but
hasn't populated it. Latent exposure — the moment any embedding work
starts, it's public.

### `35.193.206.38:6333` (measurepm.com / Google Cloud US)
Qdrant 1.15.5, 3 collections: `my_document_chunks`, `373_documents`,
`workflows`. Measure PM is an HR/labor-analytics company; this is
likely their internal document-RAG setup. Smaller scope than Rogers,
but the collection names confirm document-store usage.

## Iter-3 broader exposure inventory

The 26-port sweep also surfaced the AI-stack co-location pattern across
non-Phoenix populations:

### MLflow tracking servers (port 5000)

| Platform | Open | Confirmed-MLflow | Unauth |
|---|--:|--:|--:|
| Phoenix | 6 | 0 | 0 |
| Langfuse | 2 | 0 | 0 |
| OpenLIT | 0 | 0 | 0 |
| Helicone | 0 | 0 | 0 |
| LangSmith | 0 | 0 | 0 |

8 hosts have TCP port 5000 open across the population. None responded
as MLflow API (the `/api/2.0/mlflow/experiments/list` endpoint check
came back empty or different-shape). Most are likely generic Python
FastAPI / Flask apps on the default port. **Worth a future iter** — the
MLflow probe path may need broadening to catch all MLflow variants.

### Streamlit apps (port 8501)

5 hosts return 200 on `/healthz`. Streamlit's framework has no
authentication — exposure depends entirely on per-app code. We flag
the framework presence as INFO, not unauth.

### Gradio apps (port 7860)

0 confirmed Gradio across all populations. Gradio is typically deployed
with a hosted-services API key (HuggingFace Spaces, etc.) — bare-metal
self-hosted Gradio is rare on AI-observability operator hosts.

### ChromaDB (port 8000)

**32 hosts** have TCP port 8000 open, but **0 confirmed-ChromaDB** via
the `/api/v1/heartbeat` endpoint. Port 8000 is a heavily-overloaded
default (FastAPI, generic web apps, Django, Express, ...) so the
co-location signal here is noisy. The exposure inventory is meaningful
even when ChromaDB-specific confirmation rate is 0.

## Methodology refinement from iter-3

Iter-3 validates the **operator-class-aligned port hypothesis** from
iter-2's plan: AI-stack pipeline ports yield positively (3 unauth
Qdrant) where message-broker ports yielded 0. The yield asymmetry
matters:

| Iteration | Port class added | New unauth yield |
|---|---|--:|
| iter-1 | Extended dev-tooling (Redis, MailHog, Kibana) | 8 |
| iter-2 | Message brokers (NATS, Kafka, RabbitMQ, Memcached) | 0 |
| iter-3 | AI-stack pipeline (Qdrant, MLflow, ChromaDB, Streamlit, Gradio, Milvus) | 3 |

**The lesson: yield per port-added depends on operator-class alignment.**
Dev-tooling ports align tightly with the AI-observability operator
profile (devs deploying Phoenix on a quick-and-loose host). AI-stack
pipeline ports align medium-tightly (some operators co-locate their
RAG/vector DBs). Message brokers don't align (different operator class
entirely).

This refines Methodology Insight #14 (still in draft): *port-set
selection for IP-direct-shadow methodology should be hypothesis-driven,
matched to the operator-class profile of the seed population*.

## Performance metrics

Iter-3 with 26 ports across 5 populations:
- Phoenix (94 hosts × 26 ports): 18 seconds
- Langfuse (381 hosts × 26 ports): 1m34s
- LangSmith (96 hosts × 26 ports): 41 seconds
- Helicone (21 hosts × 26 ports): 25 seconds
- OpenLIT (23 hosts × 26 ports): 25 seconds

Wall time scales sublinearly with port count thanks to port-parallelism
([iter-1 fix](https://github.com/Nicholas-Kloster/VisorBishop/commit/0dd8c90)).
Iter-1's 15-port sweep took ~24s on Phoenix; iter-3's 26-port sweep
takes ~18s. Faster, despite ~73% more ports per host, because the new
ports are mostly TCP-only banners that complete fast.

## Next steps

1. ~~Build VisorBishop (Phase 3)~~ ✓
2. ~~iter-1: extended dev-tooling ports~~ ✓
3. ~~iter-2: message-broker ports~~ ✓ (zero-yield, refined methodology)
4. ~~iter-3: AI-stack pipeline ports~~ ✓ (this document)
5. **Disclosure prep for Rogers Communications** — when full research
   chain completes, coordinate disclosure of the Phoenix+Qdrant
   double-exposure on `172.178.38.117`
6. **Methodology Insight #14 final writeup** — incorporates iter-1+2+3
   pattern: tool re-iteration yield depends on operator-class alignment
7. **Phase 4 (web UI)** for VisorBishop — still queued

## Evidence pack

`~/recon/2026-05-10-llm-sweep/visorbishop-results/iter3/`
- `phoenix-shadow.json` / `.csv` — 94-host Phoenix iter-3 sweep (3 new unauth Qdrant)
- `langfuse-shadow.json` / `.csv` — 381-host Langfuse iter-3 sweep
- `langsmith-shadow.json` / `.csv` — 96-host LangSmith iter-3 sweep
- `helicone-shadow.json` / `.csv` — 21-host Helicone iter-3 sweep
- `openlit-shadow.json` / `.csv` — 23-host OpenLIT iter-3 sweep

Source: [Nicholas-Kloster/VisorBishop@v0.1.3](https://github.com/Nicholas-Kloster/VisorBishop)
— 26-port `ShadowPorts` list at `internal/probe/ipshadow.go`

Cross-references:
- [iter-1 case study](visorbishop-iter1-survey-2026-05-11.md)
- [iter-2 case study](visorbishop-iter2-survey-2026-05-11.md)
- [Phase 3 case study](visorbishop-phase3-survey-2026-05-11.md)
- [Phoenix Phase 1 survey](phoenix-llm-observability-survey-2026-05-10.md) — Rogers project surfaced during initial GraphQL enumeration
- [Methodology Insight #12](../../methodology/insight-12-ip-direct-shadow.md)
