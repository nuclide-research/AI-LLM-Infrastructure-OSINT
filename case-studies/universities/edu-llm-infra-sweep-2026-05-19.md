---
type: stage-0-sweep
title: ".edu LLM infrastructure dork-map — 1,584 verified-dork × hostname:.edu sweep (2026-05-19)"
date: 2026-05-19
class: institutional-deployment
category: stage-0-survey
status: stage-0-complete
methodology: shodan-count-sweep + repo-verified-dork-library
session: 24
---

# .edu LLM Infrastructure Dork-Map — Stage 0 Sweep

_NuClide Research, 2026-05-19. Sub-survey of Session 24._

## TL;DR

The repo's 1,629-dork verified Shodan catalog (29 categories, hand-curated and FP-tested across 50+ prior commercial surveys) was scoped to `hostname:.edu` and run through `shodan count` (free per query, no scan credit). After dropping 45 dorks that already had a `hostname:` filter, **1,584 scoped queries** ran in 48 minutes with a 1.2s rate-limit. **382 dorks (24%) returned ≥1 hit**, 1,143 returned 0, 59 errored (~3.7% rate-limit blip). The data-mapping output establishes which platform classes have material `.edu` exposure surface, what populations to expect at Stage 1 verify, and which dork classes are productive vs noise on the academic surface.

The session-5 university survey (2026-05-03) found 252 JupyterHub instances on `.edu` via a single dork. This Stage 0 catches the same population plus 36 other productive JupyterHub-related dork variants and the entire LLM tier (Ollama, Open WebUI, LiteLLM, n8n, Dify, Streamlit, etc.) that session 5 missed because it stopped after Ollama/Open WebUI/JupyterHub.

## Methodology

**Source dorks:** parsed every backtick-wrapped query line from the 29 `shodan/queries/*.md` files in this repo. Each is a hand-verified dork from a prior commercial survey, with hit-count notes and FP-trap documentation already in place.

**Scope filter:** appended ` hostname:.edu` to each dork. Dorks already containing `hostname:` (45 of 1,629) were dropped to avoid filter conflicts.

**Execution:** `shodan count` per scoped dork, 1.2s sleep between queries, 50-min hard deadline. Output captured as `count<TAB>category<TAB>scoped_dork`.

**Rate-limit empirical data:** an earlier per-university burst sweep at 0s delay produced 62% ERRs (~165/264). At 1.2s delay this sweep produced 3.7% ERRs (~59/1,584). Sustained Shodan freelance-tier rate is ~50 queries/min per API key — empirical, useful for sizing future sweeps.

**No subagent parallelization** for the count phase: Shodan's per-key throttle is the bottleneck, not local concurrency.

## Headline numbers

| Metric | Value |
|---|---|
| Total scoped queries fired | 1,584 |
| Non-zero hit count | **382 (24%)** |
| Zero hit count | 1,143 |
| ERR count (rate-limit) | 59 (3.7%) |
| Categories with ≥1 productive dork | 22 of 29 |
| Categories with 0 productive dorks | 7 of 29 |
| Sweep wall-time | 48 min |
| Shodan scan credits consumed | 0 (count queries are free) |

## Productive dorks per category

Sorted by productivity rate (productive ÷ total):

| Category | Productive | Total | Productivity |
|---|---|---|---|
| 18-jupyter | 37 | 62 | **60%** |
| 02-vector-databases | 74 | 160 | 46% |
| 16-bi-dashboard | 69 | 156 | 44% |
| 04-training-experiments | 28 | 67 | 42% |
| 01-llm-orchestration | 18 | 49 | 37% |
| 12-containers | 4 | 13 | 31% |
| 03-model-serving | 16 | 57 | 28% |
| 19-streamlit | 11 | 44 | 25% |
| 25-elasticsearch | 17 | 71 | 24% |
| 21-browser-agents | 14 | 62 | 23% |
| 22-data-labeling | 16 | 71 | 23% |
| 10-mcp-servers | 3 | 14 | 21% |
| 05-gateways-monitoring | 8 | 40 | 20% |
| 27-embedding-services | 11 | 59 | 19% |
| 24-observability | 10 | 61 | 16% |
| 26-mem0-agent-memory | 5 | 33 | 15% |
| 09-code-assistants | 4 | 35 | 11% |
| 24-llm-safety-guardrail-policy | 12 | 115 | 10% |
| 23-ai-safety-eval | 4 | 43 | 9% |
| 17-voice-audio-ai | 8 | 123 | 7% |
| 06-agent-frameworks | 5 | 79 | 6% |
| 20-gradio | 3 | 53 | 6% |
| 26-exfiltrated-credentials-in-html | 3 | 49 | 6% |
| 15-fingerprinting | 2 | 21 | 10% |
| 07-rag-stacks | 0 | 10 | **0%** |
| 08-image-generation | 0 | 11 | **0%** |
| 11-credential-leaks | 0 | 14 | **0%** |
| 13-backup-snapshot | 0 | 7 | **0%** |
| 14-gpu-compute | 0 | 5 | **0%** |

**Observation:** `.edu` is dominated by **notebooks (Jupyter), data substrate (PostgreSQL/MongoDB/Redis/Elasticsearch/OpenSearch), observability (Grafana), and the core LLM frontend tier (Ollama/Open WebUI/n8n/LiteLLM/Streamlit)**. Universities do NOT (publicly) run RAG framework servers, image-generation servers, GPU-compute exporters, or backup/snapshot services at meaningful population on `.edu` hostnames — those categories had 0 productive dorks. Most of those surface on commercial cloud (AWS/Azure) infra instead.

## Top LLM-tier dorks (excluding data-substrate, observability, and noise)

Filtered to platforms that are unambiguously LLM-tier infra:

| Hits | Category | Dork |
|---|---|---|
| **800** | 04-training | `http.html:"jupyter" hostname:.edu` |
| **539** | 18-jupyter | `http.title:"Jupyter" hostname:.edu` |
| **521** | 18-jupyter | `http.title:"Jupyter" -port:443 hostname:.edu` |
| **513** | 18-jupyter | `http.html:"jupyter" http.html:"token" hostname:.edu` |
| **510** | 18-jupyter | `http.title:"Jupyter Server" hostname:.edu` |
| **497** | 18-jupyter | `http.title:"Jupyter" country:US hostname:.edu` |
| **466** | 18-jupyter | `http.title:"Jupyter" org:"university" hostname:.edu` |
| **297** | 18-jupyter | `http.html:"jupyterhub" hostname:.edu` |
| **284** | 04-training | `"Jupyter" hostname:.edu` |
| **275** | 18-jupyter | `"JupyterHub" hostname:.edu` |
| **233** | 18-jupyter | `http.title:"JupyterHub" hostname:.edu` |
| **179** | 18-jupyter | `http.title:"JupyterHub" port:443 hostname:.edu` |
| **171** | 18-jupyter | `http.html:"/hub/login" hostname:.edu` |
| **167** | 19-streamlit | `port:8501 hostname:.edu` |
| **161** | 18-jupyter | `http.title:"JupyterHub" country:US hostname:.edu` |
| **146** | 19-streamlit | `port:8501 country:US hostname:.edu` |
| **133** | 10-mcp-servers | `http.title:"Open WebUI" hostname:.edu` |
| **133** | 01-llm-orchestration | `http.title:"Open WebUI" hostname:.edu` |
| **133** | 01-llm-orchestration | `http.html:"open-webui" hostname:.edu` |
| **95** | 10-mcp-servers | `http.html:"open-webui" "uvicorn" hostname:.edu` |
| **90** | 04-training | `http.html:"streamlit" hostname:.edu` |
| **90** | 01-llm-orchestration | `product:"n8n" hostname:.edu` |
| **87** | 01-llm-orchestration | `http.html:"Ollama is running" -port:443 hostname:.edu` |
| **83** | 01-llm-orchestration | `product:Ollama port:11434 hostname:.edu` |
| **50** | 02-vector-databases | `"MinIO Console" port:9001 hostname:.edu` |
| **44** | 02-vector-databases | `product:"Docker Registry" hostname:.edu` |
| **41** | 02-vector-databases | `"Docker Registry" hostname:.edu` |
| **35** | 01-llm-orchestration | `http.title:"LiteLLM" hostname:.edu` |
| **33** | 02-vector-databases | `"MongoDB" port:27017 "vector" hostname:.edu` |
| **29** | 02-vector-databases | `http.title:"Harbor" hostname:.edu` |
| **16** | 01-llm-orchestration | `http.html:"dify" hostname:.edu` |
| **13** | 24-observability | `http.title:"Phoenix" hostname:.edu` |
| **11** | 01-llm-orchestration | `http.html:"Chainlit" hostname:.edu` |
| **11** | 01-llm-orchestration | `http.title:"Open WebUI" port:8080 hostname:.edu` |
| **5** | 01-llm-orchestration | `title:"Flowise" port:443 hostname:.edu` |
| **3** | 01-llm-orchestration | `"Jan" port:1337 hostname:.edu` |

## Noise observations (Insight-class)

1. **`org:"Airtable, Inc" port:443 hostname:.edu` returned 46,444** — the highest hit count of any single dork in the sweep. This is **NOT 46K Airtable-hosted university apps**; it's Shodan facet-combinatorial: customer `.edu` domains pointing at Airtable's IPs, where the customer's `.edu` ends up in Shodan's hostname index but the actual host is Airtable. Discarded from the LLM-tier table. **Class:** SaaS-customer-CNAME noise; mirrors the `org:"Cloudflare"` problem in commercial surveys.

2. **`port:4444 hostname:.edu` returned 1,672** — Selenium Grid default port, but `.edu` campus networks routinely run port 4444 for many non-Selenium services (krb524 in particular). The cat-21 browser-agents subset of this is a real signal at much smaller population; will need conjunctive verify to extract.

3. **`http.html:".co" hostname:.edu` returned 1,104** under cat-24-llm-safety-guardrail-policy — substring match on the `.co` TLD as a body string. Generic FP class, drop.

4. **PostgreSQL/MongoDB/Redis/OpenSearch returning 1007/170/118/476** — universities run lots of data-tier infra publicly. Not LLM-specific by themselves, but pre-Insight: when colocated with a confirmed Ollama/Open WebUI/Jupyter host, these are the Pharos-class shadow-port findings to look for (per [Insight #11/#12](../../methodology/insight-12-ip-shadow-colocation.md)).

## Dork-class hierarchy on `.edu`

Confirming this session's earlier [Candidate Insight #45](../../methodology/insight-45-niche-dork-class-hierarchy.md) at the academic scope:

| Class | Example | `.edu` population |
|---|---|---|
| **Frontend-bundle-ID body** | `http.html:"jupyter"` | 800 |
| **Bundle-ID body alt** | `http.html:"jupyterhub"` | 297 |
| **Server-header banner** | `http.html:"Ollama is running"` | 87 |
| **Product facet** | `product:Ollama port:11434` | 83 |
| **Title** | `http.title:"Jupyter"` | 539 |
| **Default-port facet** | `port:8501` (Streamlit) | 167 |
| **JSON-config body** | `http.html:"Chainlit"` | 11 |
| **Route-slug body** | `http.html:"/hub/login"` | 171 |

Title and bundle-ID body are the highest-yield on `.edu`. Server-header banners under-represent because the `.edu` Ollama population is dominated by older versions that pre-date the `Server: ollama` header (added v0.5+).

## Carry-forward — Stage 1 (next)

This case study captures **Stage 0 only** — the dork-mapping output. Stages 1–4 are pending:

**Stage 1:** Per high-yield dork (≥3 hits), `shodan download --limit N` to pull sample IPs. ~100 dorks × avg 50 hosts = ~5K sample tuples to verify.

**Stage 2:** Inline-probe verify per platform-class (proven 21s/1000-host asyncio pattern from this session's earlier `.edu` work). Drop substring-FP candidates per Insight #15.

**Stage 3:** Hostname → institution attribution via the local `world_universities_and_domains.json` (2,349 US institutions with `.edu` domains). Suffix-match `gpu.cs.example.edu` → `Example University`.

**Stage 4:** Diff confirmed hosts against the 81 existing case studies (49 cross-validated institutions per `known-from-overview.tsv`). Surface NEW institutions only. Per-institution case study files under `US/` and `international/`.

**Optional Stage 5:** Disclosure routing decisions (Cowboy's call, per `feedback_no_disclosure_recommendations`).

## Toolchain provenance

```
Stage 0 — index ~/AI-LLM-Infrastructure-OSINT/shodan/queries/*.md → 1,629 verified dorks
         → drop dorks with existing hostname: filter → 1,584 scoped dorks
         → shodan count per dork, 1.2s rate-limit, 50-min deadline
         → scoped-counts.tsv (382 non-zero rows of 1,584)
```

## Artifacts

All raw data lives at `~/recon/edu-llm-infra-2026-05-19/`:

- `verified-dorks-master.tsv` — the 1,629 source dorks indexed from the repo's `shodan/queries/`
- `scoped-dorks-edu.tsv` — the 1,584 scoped dorks fed to the sweep
- **`scoped-counts.tsv`** — the canonical Stage-0 output (1,584 rows of `count<TAB>category<TAB>scoped_dork`)
- `scoped-counts.log` — sweep progress + done signal
- `us-universities.tsv` — local Hipo `world_universities_and_domains.json` filtered to 2,349 US institutions (for Stage 3 hostname → institution attribution)
- `known-from-overview.tsv` — 181-row baseline of institutions already documented in `OVERVIEW.md` + `index.md` + `SESSION.md`
- `PLAN.md` — live stage tracker for the multi-stage sub-survey

## Reference

- Session 5 baseline: [`OVERVIEW.md`](OVERVIEW.md) — 77 case studies as of 2026-05-03
- Session 23: [`../commercial/llm-orchestration-rerun-2026-05-19.md`](../commercial/llm-orchestration-rerun-2026-05-19.md) — the dork-remap methodology this sweep applies
- Insight #4 (WHOIS authoritative): [`../../methodology/insight-04-whois-derived-contact.md`](../../methodology/insight-04-whois-derived-contact.md)
- Insight #15 (~50% real-rate on title/body dorks): [`../../methodology/insight-15-dork-real-rate.md`](../../methodology/insight-15-dork-real-rate.md)
