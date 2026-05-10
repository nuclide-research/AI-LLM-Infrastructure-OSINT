---
title: Arize Phoenix unauthenticated LLM-observability exposure (377-host population)
date: 2026-05-10
class: substrate
category: cross-cloud-survey
status: research-active
methodology: shodan-driven + GraphQL enumeration + VisorGraph attribution + BARE exploit-class match
---

# Arize Phoenix LLM-observability survey · 2026-05-10

NuClide Research · 2026-05-10

## Summary

Arize Phoenix is a self-hosted LLM observability platform — every prompt, every model
response, every token, every chain step from production AI agents flows through it.
Shodan inventories **377 internet-exposed Phoenix instances**. Of those, **94 (25%)
have unauthenticated GraphQL endpoints**, and **57 hosts contain real customer trace
data** with cumulative volume in the **billions of LLM tokens**.

This survey enumerates the population, classifies auth posture, attributes the top
operators via VisorGraph, and ranks exploit class via BARE.

## Discovery dork

```
http.html:"arize-phoenix"
```

The naive title-based dork (`http.title:"Phoenix"`) returns 4,685 hits but is
~92% noise (Phoenix, AZ businesses). The HTML-body fingerprint is precise.

## Population

| Metric | Value |
|---|---|
| Total hosts | 377 |
| Reachable from research VPN | 357 |
| Auth-protected (`401` to GraphQL) | 113 |
| **Unauthenticated GraphQL** | **94** |
| With real project data | **57** |
| Actively logging tokens | **49** |

**Geographic distribution:** US 201, DE 24, IE 21, FR 21, IN 17, CN 14, SG 13, AU 10
**Hosting:** AWS dominates (~165 hosts), Google 45, Microsoft 27, DigitalOcean 13, Hetzner 10, Alibaba 9
**Ports:** 443 (143), 80 (122), 6006 default Phoenix port (94), 6007 (7), plus 8000/30002/16006/9006 long tail

## Auth-posture finding

Phoenix's *web UI* (port 6006 SPA) returns HTTP 200 to anyone — that's the React
app loading. Naive auth-posture surveys based on HTTP code on `/` are misleading.
The *actual* auth boundary is the GraphQL endpoint (`POST /graphql`), where:

- Unauth instances return JSON: `{"data": {"projects": {"edges": [...]}}}`
- Auth-on instances return JSON error: `{"errors": [{"message": "Unexpected error... 1009001"}]}` or string `Invalid token`

This means default-no-auth Phoenix deployments are **silently** leaking trace data
to anyone who knows to query `/graphql` with the right shape — a non-trivial dork
of normal security scanners that don't speak GraphQL.

## Top-15 unauth hosts by token volume

| # | URL | Projects | Records | Traces | Tokens | Last Active |
|--:|---|--:|--:|--:|--:|---|
| 1 | http://190.210.105.193:6006 | 5 | 878,986 | 3,353 | **1.21B** | 2025-07-10 |
| 2 | http://13.228.68.200:80 | 7 | 514,645 | 50,087 | **1.09B** | 2026-05-09 |
| 3 | http://3.1.189.83:80 | 7 | 514,645 | 50,087 | 1.09B | 2026-05-09 |
| 4 | https://34.40.51.187:443 | 2 | 475,048 | 44,363 | 563M | 2026-05-10 |
| 5 | http://34.23.90.218:6006 | 2 | 116,823 | 47,533 | 538M | 2026-05-10 |
| 6 | https://34.93.215.14:443 | 2 | 438,071 | 438,065 | 473M | 2026-05-08 |
| 7 | http://24.144.113.134:6006 | 1 | 88,163 | 27,932 | 117M | 2026-05-09 |
| 8 | http://185.216.21.164:6006 | 41 | 22,899 | 2,183 | 115M | 2026-04-18 |
| 9 | http://47.92.197.149:6006 | 2 | 11,147 | 1,118 | 43M | 2025-12-16 |
| 10 | http://74.241.249.68:6006 | 1 | 57,379 | 4,280 | 32M | 2026-05-09 |
| 11 | https://34.23.4.130:443 | 2 | 16,061 | 1,292 | 23M | 2026-05-08 |
| 12 | http://100.55.164.90:80 | 2 | 7,152 | 907 | 23M | 2026-05-07 |
| 13 | http://4.255.37.60:6006 | 2 | 635,178 | 2,068 | 19M | 2026-01-20 |
| 14 | http://3.6.143.1:80 | 10 | 18,622 | 1,006 | 16M | 2025-07-18 |
| 15 | http://34.133.205.22:6006 | 6 | 19,480 | 1,668 | 10M | 2026-05-07 |

**Cumulative top-15: ~5.5 billion tokens of customer LLM trace data publicly readable.**

## Operator attribution (via VisorGraph TLS-cert + project-name correlation)

| # | IP | TLS-cert domain | Phoenix project name(s) | Operator |
|--:|---|---|---|---|
| 1 | 190.210.105.193 | (Argentina BB-link IP) | default, GPU_REPORTS, TEST_GPU_REPORTS, evaluators | **`reputacion.digital`** — Argentinian online-reputation SaaS. Multi-GPU vLLM inference farm; full Prometheus topology of 39 internal `192.168.40.x` endpoints leaked alongside Phoenix |
| 2/3 | 13.228.68.200 / 3.1.189.83 | (AWS Singapore EC2 + duplicate) | brand-content, brand-recognize, brand-sentiment, brand-knowledge | **Chinese brand-mention monitoring SaaS** — tracks brand presence in Gemini/Qwen responses; reasoning text in Chinese; uses `gemini-3.1-pro-preview` (Google preview tier) and `qwen-plus-latest` |
| 4 | 34.40.51.187 | `multi-agent-eu.infra.kapturecrm.com` | default, "Multi-Agent Engine" | **Kapture CRM (India)** — Multi-Agent Engine SKU, EU region |
| 6 | 34.93.215.14 | `kapai.infra.kapturecrm.com` | default, "KapEX" | **Kapture CRM** — KapEX/Kapai product, Mumbai |
| 11 | 34.23.4.130 | `multi-agent-us.infra.kapturecrm.com` | default, "Multi-Agent Engine" | **Kapture CRM** — Multi-Agent Engine, US region |
| 7 | 24.144.113.134 | `server.autom8.pro` | default | **autom8.pro** — workflow-automation SaaS |
| 10 | 74.241.249.68 | `extenda-buddy.swedencentral.cloudapp.azure.com` | default | **Extenda Retail** — Nordic POS/retail SaaS, "Buddy" agent product |

**Three of the top 11 hosts (#4, #6, #11) belong to a single operator (Kapture CRM).** That's one Indian CRM-AI vendor's full customer LLM trace data publicly readable across three regions, totaling ~1.06B cumulative tokens.

## What's actually in the trace data

Sampled span from `13.228.68.200` (`brand-recognize`, 28K traces, gemini-3.1-pro-preview):
The user query was `"What is the best laptop?"`. The model answer (MacBook Pro / Dell XPS / ThinkPad) was processed by a LangGraph multi-step agent that extracted brand mentions (Dreame, Juyafio, BaBylissPRO, Conair from a hair-care category citation chain), assigned confidence scores, and emitted reasoning in Chinese.

Per-span data exposed:
- Full user prompt
- Full model response
- Intermediate chain-of-thought reasoning
- Operator-internal logic (brand catalogs, classification rules, confidence thresholds)
- Model identity (proves Gemini 3.1 Pro Preview tier access)
- LangGraph agent topology (`langgraph_node`, `langgraph_path`, `langgraph_step`, `langgraph_checkpoint_ns`)

This is competitive intelligence on the operator's product *and* a sample of their customer queries. The same vendor's competitors could pull operator IP without ever touching the operator's primary infrastructure.

## VisorGraph: top-host secondary exposure

Host #1 (`190.210.105.193`, `reputacion.digital`) carries a **separate exposure** that VisorGraph surfaced: unauthenticated **Prometheus** monitoring on port 9090 with:
- 58 scrape targets covering CoreDNS, Elasticsearch (logs/prod/dev clusters), Flower (Celery), MinIO, Postgres, Traefik, vLLM (multi-GPU inference)
- 39 internal endpoints across `192.168.40.x` private space leaked
- `/-/quit` and `/-/reload` DoS endpoints active

Combined finding: the Phoenix exposure (LLM data plane) and the Prometheus exposure (infrastructure monitoring plane) at the same operator give an attacker the full operational picture — what AI models are deployed, which GPUs serve them, what data flows through, and a one-request DoS primitive on the monitoring layer.

## Write primitive: unauthenticated span ingestion

Source-level confirmation, no live writes against third-party hosts.

`POST /v1/projects/{project_identifier}/spans` (handler `create_spans` at `src/phoenix/server/api/routers/v1/spans.py:1289`) carries a single FastAPI dependency: `Depends(is_not_locked)` — a storage-quota guard, not an auth guard. The auth-aware sibling dependency `restrict_access_by_viewers` is **not** attached to this route, and it explicitly short-circuits when `app.state.authentication_enabled` is false (the default in v0.x).

Read-confirming probe against the live Chinese brand-monitor host (`13.228.68.200`) returned **HTTP 422** with `{"detail":[{"type":"missing","loc":["body","queries"],"msg":"Field required"...}]}` — schema validation, not auth rejection. The server is processing unauthenticated POSTs, only failing on payload shape. The `data` array of `Span` objects (schema documented at `spans.py:528`, requires `name`, `context.trace_id`, `context.span_id`, `span_kind`, `start_time`, `end_time`, `status_code`) is the canonical write shape.

**Threat shift:** the exposure isn't read-only. Default-no-auth Phoenix = unauthenticated *read* + unauthenticated *write* on the trace store. Attacker can:

- Inject fabricated spans into a project to poison evaluation/training data downstream
- Overwrite or shadow real spans (collisions enumerated as duplicates and rejected, but high-rate write floods can still cost the operator on storage and quota)
- Insert malicious payloads into `attributes` that downstream RAG / dashboards / eval pipelines may render or execute (XSS-class on the Phoenix UI, prompt-injection-class if Phoenix data is later piped back into an LLM eval loop)

## Pickle-deserialization probe (ruled out)

`grep -rn "pickle\|cloudpickle\|dill\|marshal\.loads" src/phoenix/` against `Arize-ai/phoenix@main` returns zero hits in server code. The BARE clustering against `graphite_pickle_exec` / `calibre_exec` / `phoenix_exec` was a banner-similarity false positive; no actual unsafe-deserialization sink exists in Phoenix's ingest path. **Hypothesis disproven.**

## Operator clustering across the 94-host unauth set

Jaccard-similarity (≥0.5) over non-generic project names surfaces **four multi-host operator clusters**, one of which (Kapture CRM) was already attributed via TLS certs and three of which are **new**:

| # | Hosts | Project signature | Cumulative tokens | Operator inference |
|--:|---|---|---:|---|
| 1 | `13.228.68.200`, `3.1.189.83` | brand-content / brand-knowledge / brand-recognize / brand-sentiment / test-debug / test-debug2 | 2.17B | Chinese brand-mention monitoring SaaS, AWS Singapore active-active or blue-green pair |
| 2 | `34.40.51.187` (EU), `34.23.4.130` (US) | Multi-Agent Engine | 587M | **Kapture CRM** (already attributed via TLS) — pair captured by clustering, third Mumbai host (`34.93.215.14`) excluded because its product name `KapEX` differs |
| 3 | `34.23.90.218` (GCP US), `101.37.104.193` (Alibaba China) | playground | 538M | **NEW** — "Lillia" personal-health-coach AI (Vertex AI Gemini 2.5 Pro/Flash, CrewAI multi-agent), cross-cloud deploy or licensee pair |
| 4 | `172.214.59.229`, `20.253.29.16`, `4.255.37.60` (all Azure US, three regions) | agentic-nlq-api | 24.9M | **NEW** — biodefense / medical-countermeasures (MCM) research agent, GPT-4o + LlamaIndex AgentWorkflow + SQL DB of "viruses, bacteria, their countermeasures" |

Identical port topology on cluster #4 (5000 + 6006 across all three Azure regions) corroborates the same-operator inference from project-name match alone.

## Data-class characterization across clusters

| Cluster | Data class observed in sampled spans | Identifiers present? |
|---|---|---|
| #1 brand-monitor | Customer brand queries; LangGraph reasoning chains; Gemini 3.1 Pro Preview model identity | session UUIDs only |
| #2 Kapture CRM | LangGraph customer-service routing; full primary-assistant system prompt; proprietary `##KAP_CHAT_INIT_MESSAGE##` template | session UUIDs (per customer chat) |
| #3 "Lillia" health coach | Personal health metrics: weight updates, sleep logs, blood-pressure logs (tool schema includes `SleepLog`, `BloodPressureLog`, `WeightLog`); user health queries; agent-coaching responses | **persistent `user_id` (`DRB_110008755478` format) tied to clinical-adjacent telemetry** — quantified-self with stable identifiers, HIPAA-relevant if any US-resident users |
| #4 MCM agent | Scientific questions about pathogens / countermeasures; agent reasoning over a SQL pathogen DB; full system prompts revealing tool inventory (`SQLQuery`, `FormatResults`) and database scope | session-scoped only in sampled spans |

Cluster #3 is the highest-sensitivity tier observed: identified individual health-data telemetry routed through default-no-auth Phoenix.

Cluster #4 is the highest-context-sensitivity tier: a biodefense-domain agent's scaffolding (system prompts, tool schema, target-DB description) is exposed to anyone who knows the GraphQL shape, even though the per-span text in our sample didn't contain operator IP beyond the MCM framing.

## BARE semantic exploit-class match (logged for completeness)

Running BARE's MiniLM encoder over the 376 host banners against the Metasploit corpus:

- The literal top-3 module match for Phoenix hosts is `exploits_multi_http_phoenix_exec` — but this is a **semantic false positive**. The MSF module by that name is the Phoenix Exploit Kit (browser-exploit framework), not Arize Phoenix.
- BARE also clustered Phoenix hosts with `calibre_exec`, `graphite_pickle_exec`, and `phoenix_exec` — Python-pickle deserialization roots.
- Source review (above) **disproved** the pickle hypothesis. BARE's banner-text clustering surfaced a class match that didn't survive code-level confirmation. Documented as a tool-humility note: semantic banner clustering is a hypothesis generator, not a primitive confirmer.

## Vendor-template implications

Phoenix's threat profile maps cleanly to NuClide's [Methodology Insight #10](../../methodology/insight-10-vendor-template-default-no-auth.md):

> Default-no-auth on embedded web management is a vendor-choice, not an operator misconfiguration. Population-scale exposure tracks the shipping default.

Phoenix v0.x ships with `PHOENIX_ENABLE_AUTH=false` by default. Operators following the quickstart get an unauthenticated public endpoint. The 25% unauth-rate at population scale (94 of 377) is an *improvement* on the typical AI-infra unauth-rate (typically 70-100% per the 2026-05 cross-survey), suggesting Phoenix has been pushing operators toward auth defaults more recently — but the long tail of legacy deployments remains.

## Next steps (research, not disclosure-yet)

1. ~~Shodan harvest 377 hosts~~ ✓
2. ~~GraphQL auth-posture probe~~ ✓
3. ~~VisorGraph top-15 attribution~~ ✓
4. aimap fingerprint top-15 (deferred — Phase 2 enumerator hung repeatedly on slow hosts; non-blocking for the rest of the chain)
5. ~~BARE semantic exploit match~~ ✓
6. ~~Sample more spans from top-15 to characterize data-class diversity~~ ✓ (4 clusters profiled; clinical-adjacent + biodefense surfaces identified)
7. ~~Phoenix `/v1/spans` POST permissions test~~ ✓ (source-confirmed: no auth dependency on `create_spans`; live HTTP 422 schema-only rejection corroborates)
8. ~~Pickle-deserialization probe on `/v1/spans` ingest~~ ✓ (ruled out — zero pickle/cloudpickle/dill/marshal usage in server source)
9. ~~Cluster project names across the full 94-host unauth dataset~~ ✓ (4 multi-host operator clusters surfaced, 3 new)
10. Synthesis writeup; coordinated-disclosure planning when research complete

## Evidence pack

`~/recon/2026-05-10-llm-sweep/phoenix/`
- `phoenix-hosts.tsv` — 377-host Shodan export
- `phoenix-shodan.json` — 376-record JSONL (BARE input)
- `probes/phoenix-graphql.tsv` — 377 GraphQL probe responses
- `probes/phoenix-real-unauth.txt` — 94 confirmed unauth hosts
- `probes/phoenix-projects-deep.tsv` — 83 successful project enumerations
- `triage-report.txt` — ranked by token volume
- `visorgraph-output/*.json` — 14 VisorGraph traces of top-15 hosts
- `bare-phoenix.txt` — BARE semantic-match output for 376 hosts
- `top15-ips.txt` — top-15 IP list
- `probes/cluster_project_names.py` — Jaccard clustering over 94-host project-name signatures (4 clusters output)
- `probes/sample_one_span.py` — single-span sampler for data-class characterization
- `probes/agentic-nlq-spans.json` — 8 sampled MCM-agent spans (cluster #4)
- `probes/kapture-spans.json` — 5 sampled Kapture Multi-Agent Engine spans (cluster #2 EU)
- `probes/playground-spans.json` — 5 sampled "Lillia" health-coach spans (cluster #3)
