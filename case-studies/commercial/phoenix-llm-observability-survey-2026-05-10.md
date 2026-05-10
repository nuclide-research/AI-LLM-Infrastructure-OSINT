---
title: Arize AI Phoenix unauthenticated LLM-observability exposure (377-host population)
date: 2026-05-10
class: substrate
category: cross-cloud-survey
status: research-active
methodology: shodan-driven + GraphQL enumeration + VisorGraph attribution + BARE exploit-class match
---

# Arize AI Phoenix LLM-observability survey · 2026-05-10

NuClide Research · 2026-05-10

## Summary

[Arize AI](https://arize.com/)'s [Phoenix](https://arize.com/phoenix/) is an open-source LLM
observability platform for agent development and evaluation, typically deployed self-hosted —
every prompt, every model
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

## Two-tier admin model: secure-fail vs insecure-fail

Phoenix's permission system at `src/phoenix/server/api/auth.py` defines two distinct admin-only authorization classes:

```python
class IsAdmin(Authorization):
    def has_permission(self, source, info, **kwargs):
        if not info.context.auth_enabled:
            return False  # secure-fail: deny all when auth is off
        return isinstance(user := info.context.user, PhoenixUser) and user.is_admin

class IsAdminIfAuthEnabled(Authorization):
    def has_permission(self, source, info, **kwargs):
        if not info.context.auth_enabled:
            return True   # insecure-fail: ALLOW all when auth is off
        return isinstance(user := info.context.user, PhoenixUser) and user.is_admin
```

The naming is the tell. `IsAdmin` is the secure-default class — when `auth_enabled=False`, it returns `False` and denies the request; nobody can reach admin-gated functionality on an unauth instance. `IsAdminIfAuthEnabled` is the explicit insecure-default class — when `auth_enabled=False`, it returns `True` and allows the request; **anyone** can reach the field on an unauth instance.

Live confirmation across 5 random unauth hosts: `users` and `systemApiKeys` GraphQL queries (gated by `IsAdmin`) consistently return `"Only admin can perform this action"` even on default-no-auth instances. Properly secure-failed.

Searching the source for `IsAdminIfAuthEnabled` decorators surfaces three paths where the insecure-fail variant is attached:

- `src/phoenix/server/api/types/Secret.py:48` — the **`Secret.value` field** that returns the decrypted plaintext
- `src/phoenix/server/api/mutations/secret_mutations.py:123` — secret mutations
- `src/phoenix/server/api/mutations/generative_model_custom_provider_mutations.py` (5 occurrences) — generative-model provider config
- `src/phoenix/server/api/mutations/project_trace_retention_policy_mutations.py` (3 occurrences) — trace retention

The most consequential is `Secret.value`. Phoenix's `secrets` table (added in ~v15.x per the schema) stores encrypted LLM provider credentials — per the docstring at `src/phoenix/server/api/routers/v1/secrets.py:4`: *"Secrets store encrypted API keys (e.g., OPENAI_API_KEY, ANTHROPIC_API_KEY) in the Phoenix database."*

When auth is off, calling the GraphQL `secrets` query (no permission decorator) returns the keys. Resolving `Secret.value` on each result decrypts the secret server-side and returns the plaintext to the unauth caller via `DecryptedSecret(value=RedactedString(decrypted_value))`. `RedactedString` is a thin client-side toString wrapper, not an access-control mechanism — the plaintext goes back over the wire.

## Latent primitive: stored-secret extraction

Tested across 25 modern (v13.x–v15.x) unauth hosts and the top-15 by token volume: **0 hosts have stored secrets**. The `secrets` query returns empty edges everywhere we sampled.

This means the secret-leak primitive **exists in source and is callable at protocol level on every unauth Phoenix ≥ v15.x**, but our population doesn't currently exercise it because operators haven't moved their LLM provider keys into Phoenix's secret manager yet. Phoenix's secret manager is a recent feature; adoption is still climbing.

Two implications:

1. **Latent exposure** — every operator who migrates their `OPENAI_API_KEY` / `ANTHROPIC_API_KEY` / `GOOGLE_API_KEY` into Phoenix's secret manager *while running auth=off* converts their existing trace-data leak into a credential-leak. The exposure profile of these instances will get worse over time without any new operator misconfiguration, just by adopting a new Phoenix feature.

2. **Code-level finding** — `IsAdminIfAuthEnabled` on `Secret.value` is a defense-in-depth gap. The default authentication state should not turn an admin-only field into a public field. The principled fix is to use `IsAdmin` (secure-fail) on `Secret.value` and require explicit auth setup before the secret manager becomes usable. Documented for upstream-Arize disclosure.

## Cross-version posture: default-no-auth ships in current `main`

`src/phoenix/config.py:1136` — Phoenix's auth-enable default in the current `main` branch:

```python
def get_env_enable_auth() -> bool:
    return _bool_val(ENV_PHOENIX_ENABLE_AUTH, False)
```

The hardcoded fallback is `False`. Every Phoenix instance launched today, including v15.x, ships with `PHOENIX_ENABLE_AUTH=False` unless the operator explicitly sets the environment variable. The 25% population unauth rate is not a legacy-deployment artifact.

Probing the SPA `Config.platformVersion` field across the 94 unauth hosts surfaces this version distribution (excluding 5 hosts where the version field couldn't be parsed):

| Major version | Hosts | Notable subversions |
|--:|--:|---|
| 4.x | 1 | 4.33.1 |
| 7.x | 2 | 7.5.2, 7.9.4 |
| 8.x | 6 | 8.6.0, 8.12.1, 8.19.1, 8.24.2, 8.25.0, 8.32.1 |
| 11.x | 10 | 11.9.0, 11.19.0 (×2), 11.24.1 (×3), 11.32.1 |
| 12.x | 20 | 12.4.0, 12.6.1, 12.10.0 ... 12.35.0 |
| 13.x | 27 | 13.3.0 (×3), 13.5.0 (×2), 13.12.0 (×2), **13.15.0 (×10)**, 13.20.0 (×2) |
| 14.x | 10 | 14.0.0 (×2), 14.5.0 (×2), 14.8.0 (×2), 14.11.0, 14.14.0, 14.15.0 |
| 15.x | 13 | 15.1.0 (×2), **15.2.0 (×6)**, 15.4.0 (×2), 15.5.1 (×3) |

The unauth-state spans every major version Phoenix has shipped. The population is bimodal: 13.15.0 is the most-deployed legacy snapshot (10 hosts), 15.2.0 is the most-deployed recent snapshot (6 hosts). Modern-version operators are running unauth in production at the same rate as legacy operators. Phoenix has not changed the shipping default.

## Bulk-export REST primitive

`POST /v1/spans` (handler `query_spans_handler` at `spans.py:587`) is a bulk-query endpoint with no auth dependency declared:

```python
@router.post("/spans", operation_id="querySpans", ...)
async def query_spans_handler(
    request: Request,
    request_body: QuerySpansRequestBody,
    accept: Optional[str] = Header(None),
    ...
) -> Response:
```

The request body takes a list of `SpanQuery` DSL objects. The response shape is selected by the `Accept` header:

- `Accept: application/json` → multipart streaming JSON
- (default) → `application/x-pandas-arrow` (Apache Arrow IPC)

This is the canonical bulk-export path. An attacker with the right query DSL can stream the entire span dataset for any project on any unauth Phoenix instance in a single POST. Schema validation is the only gate; auth is not.

The Phoenix React SPA on port 6006 *also* answers GET requests for these REST routes with the SPA's HTML, which obscures the API surface from casual browser-based probes. The SPA will route any GET to `/v1/projects/{id}/spans`, `/v1/spans/csv`, etc. through the React Router and return the dashboard HTML, masking the existence of the underlying API endpoints. Only POSTs with proper Content-Type reach the FastAPI handlers.

## Mutation surface (40 mutations)

Full GraphQL mutation introspection across host #1 surfaces 40 mutations. Triaged by threat class:

| Threat class | Mutations | Auth gate observed |
|---|---|---|
| Trace data destructive | `deleteProject`, `clearProject`, `deleteSpanAnnotations`, `deleteTraceAnnotations`, `deleteDataset`, `deleteDatasetExamples`, `deleteExperiments` | mixed — some `IsAdmin`, some unguarded; testable per-host |
| User/account control | `createUser`, `patchUser`, `deleteUsers`, `createSystemApiKey`, `createUserApiKey`, `deleteSystemApiKey`, `deleteUserApiKey` | **`IsAdmin`** — properly secure-failed on unauth instances |
| LLM proxy | `chatCompletion(input)`, `chatCompletionOverDataset(input)` | input schema accepts an `apiKey` param; if the operator has stored an OpenAI/Anthropic key, attacker-supplied prompts can be billed to the operator's quota (LLMjacking primitive) |
| Bulk export | `exportEvents(eventIds, fileName)`, `exportClusters` | confirmed callable unauth on host #1 |
| Prompt management | `createChatPrompt`, `createChatPromptVersion`, `deletePrompt`, `clonePrompt`, `patchPrompt`, `deletePromptVersionTag`, `setPromptVersionTag`, `createPromptLabel`, `patchPromptLabel`, `deletePromptLabel`, `setPromptLabel`, `unsetPromptLabel` | unguarded — anyone can poison a project's stored prompts |
| Annotation injection | `createSpanAnnotations`, `patchSpanAnnotations`, `createTraceAnnotations`, `patchTraceAnnotations` | unguarded |
| Dataset injection | `createDataset`, `patchDataset`, `addSpansToDataset`, `addExamplesToDataset`, `patchDatasetExamples` | unguarded |

The per-mutation auth gate has not been exhaustively confirmed at source — what's mapped above is from live probing on host #1 plus the `IsAdmin`/`IsAdminIfAuthEnabled` decorator audit. The full per-mutation auth posture is a follow-on probe.

## Operator clustering across the 94-host unauth set

Jaccard-similarity (≥0.5) over non-generic project names surfaces **four multi-host operator clusters**, one of which (Kapture CRM) was already attributed via TLS certs and three of which are **new**:

| # | Hosts | Project signature | Cumulative tokens | Operator inference |
|--:|---|---|---:|---|
| 1 | `13.228.68.200`, `3.1.189.83` | brand-content / brand-knowledge / brand-recognize / brand-sentiment / test-debug / test-debug2 | 2.17B | Chinese brand-mention monitoring SaaS, AWS Singapore active-active or blue-green pair |
| 2 | `34.40.51.187` (EU), `34.23.4.130` (US) | Multi-Agent Engine | 587M | **Kapture CRM** (already attributed via TLS) — pair captured by clustering, third Mumbai host (`34.93.215.14`) excluded because its product name `KapEX` differs |
| 3 | `34.23.90.218` (GCP US), `101.37.104.193` (Alibaba China) | playground | 538M | **NEW** — Lillia ([lilliacare.ai](https://www.lilliacare.ai/)), B2B2C chronic-disease management platform (Vertex AI Gemini 2.5 Pro/Flash, CrewAI multi-agent). Per their own marketing: "next-generation population health engine" sold to "providers, pharma, device companies, insurers, governments, and employers"; **40,000+ patients under management** across GCC + India; two ADA-published clinical studies; recognized on TIME / Statista's 2025 World's Top HealthTech list. Cross-cloud deploy on GCP US + Alibaba China is unexplained by their stated geography (Singapore HQ, Qatar, India, Delaware). Their public marketing site has no `/security` or `/trust` page and no HIPAA / SOC 2 / ISO 27001 language. |
| 4 | `172.214.59.229`, `20.253.29.16`, `4.255.37.60` (all Azure US, three regions) | agentic-nlq-api | 24.9M | **NEW** — biodefense / medical-countermeasures (MCM) research agent, GPT-4o + LlamaIndex AgentWorkflow + SQL DB of "viruses, bacteria, their countermeasures" |

Identical port topology on cluster #4 (5000 + 6006 across all three Azure regions) corroborates the same-operator inference from project-name match alone.

## IP-direct-shadow sweep across the unauth population

Building on the reputacion.digital ([single-host case study](AR-reputacion-digital-multi-surface-2026-05-10.md)) finding that one operator's defensive SSO posture was undermined by services bound on the host IP rather than only via the reverse proxy, this sweep applies the same check at population scale.

Method: nmap SYN scan across the 92 unique IPs in the unauth Phoenix set on 11 high-signal ports (NFS, rpcbind, MailCatcher, MailHog, Prometheus, AlertManager, node_exporter, Kibana, Elasticsearch, Grafana). Then per-port auth-posture probing on each open service. Documented in detail in [Methodology Insight #12](../../methodology/insight-12-ip-direct-shadow.md).

Result: **25 of 92 hosts (27%) have at least one secondary attack surface exposed on the same IP.** Five of those have real, exploitable primitives:

| Host | Phoenix project | Secondary surface | Operator |
|---|---|---|---|
| `190.210.105.193` | GPU_REPORTS (1.21B tokens) | NFS exports incl. `/postgres` + Prometheus + MailCatcher | reputacion.digital (Argentina) |
| `173.208.247.17` | `stt-dr-assistant` | Prometheus on GPU compute (`dcgm-exporter`) | wiratek.id / "ai-insight-pln" — Indonesian PLN AI vendor |
| `173.214.172.254` | (Phoenix unauth + Grafana auth-fronted) | Prometheus scraping FastAPI backend | dsb-kairo.de — German School Cairo |
| `47.251.246.12` | `deepagents-monitor-verify` | **Kibana 7.17.20 fully unauthenticated** | Alibaba Cloud US ("deepagents") |
| `51.15.207.110` | `default` (empty) | **MailHog with 139 captured emails** from `@teetsh.com` | Teetsh (French educational tools SaaS) |

Notes:

- The Kibana 7.17.20 on `47.251.246.12` is fully unauthenticated. `/api/spaces/space` returns the default space. `/api/saved_objects/_find` is callable. Anyone can configure dashboards and query the backing Elasticsearch through it. The Elasticsearch instance itself is not directly exposed (port 9200 closed), but the Kibana proxy makes it reachable.
- The MailHog on `51.15.207.110` had **139 captured emails at probe time**, the most recent from `thibault@teetsh.com`. This is the only IP-direct-shadow find in our population with an actively-leaking message store (the other three MailHog instances on the Teetsh operator's IPs were empty).
- The Wiratek/PLN host's Prometheus is small (only 2 scrape targets including `dcgm-exporter`) but the dcgm-exporter is a strong tell — this is a GPU compute node serving AI inference, likely tied to PLN (Indonesia's state electricity company) given the hostname. The Phoenix project `stt-dr-assistant` (speech-to-text doctor's assistant) suggests a healthcare-adjacent application.
- The German School Cairo (dsb-kairo.de) Phoenix is unattributed by name in our project-clustering pass but is unambiguously identified via the TLS cert. Their Prometheus scrapes a FastAPI backend at `:8000/metrics`.

The class pattern: **operators who ship Phoenix with default-no-auth tend to ship other internally-facing services the same way.** A Phoenix unauth instance is a high-value beacon for follow-on enumeration; the IP-direct-shadow check converts a single Phoenix finding into a multi-surface operator-attribution opportunity.

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

- The literal top-3 module match for Phoenix hosts is `exploits_multi_http_phoenix_exec` — but this is a **semantic false positive**. The MSF module by that name is the Phoenix Exploit Kit (browser-exploit framework), not Arize AI's Phoenix.
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
10. ~~Cross-version posture survey~~ ✓ (94-host platformVersion sweep; default-no-auth spans v4.x→v15.x; current `main` still defaults to `False`)
11. ~~GraphQL admin-gate audit~~ ✓ (`IsAdmin` vs `IsAdminIfAuthEnabled` two-tier model identified; `Secret.value` is the latent insecure-fail field on v15.x+)
12. ~~Stored-secret enumeration across modern hosts~~ ✓ (25 v13.x–v15.x hosts + top-15 sampled, 0 stored secrets — primitive is latent, not actualized)
13. ~~Mutation-surface enumeration~~ ✓ (40 mutations triaged into 7 threat classes)
14. **Per-mutation auth-gate confirmation** — exhaustive per-mutation IsAdmin vs unguarded source audit so the disclosure cleanly enumerates which write primitives are unauth-callable on default-no-auth hosts
15. ~~Single-host multi-surface deep-dive on `190.210.105.193` (reputacion.digital)~~ ✓ ([AR-reputacion-digital-multi-surface-2026-05-10.md](AR-reputacion-digital-multi-surface-2026-05-10.md))
16. ~~IP-direct-shadow population sweep~~ ✓ ([Methodology Insight #12](../../methodology/insight-12-ip-direct-shadow.md)) — 25/92 hosts (27%) have secondary surfaces; 4 NEW operator attributions: wiratek.id, dsb-kairo.de, "deepagents" (Alibaba US), Teetsh (FR)
17. Synthesis writeup; coordinated-disclosure planning when research complete

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
- `deep-dive/version-survey.tsv` — Phoenix `platformVersion` for all 94 unauth hosts
- `deep-dive/ip-shadow/` — IP-direct-shadow sweep: nmap output, per-port probes, operator attributions (5 finds across 92 IPs)
- `~/recon/reputacion-digital-2026-05-10/` — single-host multi-surface deep-dive (Phoenix + Prometheus + MailCatcher + MinIO + authentik)
