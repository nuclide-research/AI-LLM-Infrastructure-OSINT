# AI-LLM-Infrastructure-OSINT

Verified Shodan queries, fingerprints, survey data, and detection logic for exposed AI/ML infrastructure.

This is the NuClide survey program: a living record of what the AI/ML stack exposes to the
internet by default. It covers model servers, vector databases, orchestration UIs, MCP servers,
inference gateways, agent platforms, notebook environments, and adjacent data infrastructure.
Each category produces Shodan queries (tagged T1/T2/T3), per-instance case studies, and numbered
methodology insights extracted from the survey runs.

**Snapshot (2026-06-08):** 33 numbered platform categories, 247 commercial case studies, 88
methodology insights, 134 disclosures, 3 published articles, 3 IR hand-off packages staged. The
program has run continuously since early 2026 and ships fresh measurements monthly. Recent
headline finds include the auth-friction-gradient cross-platform thesis (Insight #88), the
ShadowRay 2.0 attacker-fleet identification (463 IPs via a 5-signal metadata IoC pattern), the
Hong Kong Meilisearch content-spam botnet attributed entirely from index naming, and the
Changsha 8x A100 turnkey deepfake-production rig deep dive.

A companion toolchain (VisorPlus, aimap, JAXEN, VisorLog, and others) produced and processes the
survey data. The toolchain repos are linked under [NuClide Toolchain](#nuclide-toolchain).

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

---

## Repo structure

```
.
├── shodan/
│   ├── queries/              # 54 Shodan query files across categories 01-33, plus supplementary sets
│   ├── Shodan_AI_Reference.pdf  # Polished PDF reference (v2.1, April 2026)
│   ├── ct-log-catalog.md
│   ├── favicon-hashes.md
│   ├── query-log.md
│   └── README.md
├── methodology/              # 88 numbered insights (insight-01 through insight-88)
│   ├── README.md             # Insight index with first-capture dates
│   └── tool-stage-mapping.md
├── case-studies/
│   ├── commercial/           # 247 per-survey writeups + cross-survey synthesis + 3 deep-dive subdirs
│   ├── universities/         # University AI infrastructure exposures
│   │   ├── US/               # 31 files, organized by state prefix
│   │   └── international/    # 32 country-code subdirectories
│   ├── critical-infra/
│   ├── k12/
│   ├── ai-chatbot/
│   └── government/
├── articles/                 # Published-grade write-ups (Medium / blog / X-post drafts)
├── assessments/              # IR hand-off packages (Censys ARC, Oligo Security, Anyscale, etc.)
├── tools/                    # Attack-surface research docs, PoC scripts, survey utilities
│   ├── ollama-model-injection.md
│   ├── ollama-ssrf.md
│   ├── ollama-connect-takeover.md
│   ├── hexstrike-ai-chain.md
│   ├── open-webui-ollama-bypass.md
│   ├── open-webui-cloud-proxy-hijack.md
│   ├── bypass-prompts.json
│   ├── ollama-recon.py
│   └── [survey probe scripts and utilities]
├── analysis/                 # Session analysis documents
├── evidence/                 # Screenshot packs and raw probe artifacts
├── disclosures/              # 134 disclosure documents
├── reference/
│   ├── ports.md
│   └── terminology.md
├── data/                     # Scan outputs (sensitive fields gitignored; .db not tracked)
├── CLAUDE.md                 # Committed; toolchain context for Claude Code sessions
├── SESSION.md                # Committed; last session state
├── DISCLAIMER.md
├── CONTRIBUTING.md
└── LICENSE
```

## Shodan query catalog

Queries are organized under `shodan/queries/` as numbered category files plus supplementary
query sets. The numbered files cover:

01 LLM Orchestration - 02 Vector Databases - 03 Model Serving - 04 Training & Experiments -
05 Gateways & Monitoring - 06 Agent Frameworks - 07 RAG Stacks - 08 Image Generation -
09 Code Assistants - 10 MCP Servers - 11 Credential Leaks - 12 Containers -
13 Backup & Snapshot - 14 GPU Compute - 15 Fingerprinting - 16 BI Dashboards -
17 Voice & Audio AI - 18 Jupyter - 19 Streamlit - 20 Gradio / Specialty Data Layers -
21 Browser Agents - 22 Data Labeling - 23 AI Safety Eval - 24 LLM Safety Guardrail & Observability -
25 Elasticsearch - 26 Exfiltrated Credentials & Agent Memory - 27 Embedding Services -
28 Medical Edge AI & ML Governance - 29 Workflow Orchestration - 30 Agent Memory -
31 Classical ML - 32 AI Gateways - 33 AI Email Guardrails

Survey extensions tracked as case studies rather than dedicated query files: Cat-34 (FastGPT),
Cat-46 (ComfyUI default-port population), Cat-46b (Meilisearch), Cat-47 (Ray Dashboard).

Plus supplementary files: `ai-eval-redteam-queries.md`, `auth-gateway-queries.md`,
`experiment-tracking-queries.md`, `model-serving-registry-queries.md`, `rag-frameworks-queries.md`,
`safety-guardrail-queries.md`, `service-mesh-queries.md`, `specialty-data-layers-queries.md`,
`voice-audio-ai-queries.md`, `workflow-orchestration-queries.md`, and a Google-dork supplement
(`ghdb-google-dorks.md`).

Every query is tagged:

| Tier | Meaning |
|------|---------|
| T1 | Unauthenticated by default. A hit is typically a live, interactive target. |
| T2 | Requires misconfiguration or has known auth-bypass CVEs. One additional probe confirms exposure. |
| T3 | Recon / fingerprint only. Use for inventory and pivoting. |

## Methodology insights

88 numbered insights reside in `methodology/` (insight-01 through insight-88). Each is a
standalone markdown file derived from a specific survey or incident, citable independently.
The index is at `methodology/README.md`.

Recent examples: #76 (auth-permissive cohort by default), #77 (active-banner prefilter via the
scanner stage), #80 (DMARC enforcement as funding-stage proxy), #81 (Compose EHLO leak as a
class-of-three operator-attribution signal), #82 (branded error bodies as the banner), #86
(disclosure pipeline is itself attack surface), #87 (canary persistence as monitoring proxy),
**#88 (the auth-friction gradient — operator unauth rate tracks deploy-time auth friction
across Langfuse / Meilisearch / Phoenix / ComfyUI on a single empirical curve).**

## Articles

`articles/` holds published-grade write-ups of headline findings:

| File | Topic |
|------|-------|
| `medium-2026-06-08-changsha-deepfake-rig.md` | The 8x A100 Changsha deepfake-production rig deep dive (Medium-format) |
| `shadowray-2-self-detect-2026-06-08.md` | Defender advisory: 5-signal IoC pattern for ShadowRay 2.0 attacker fleet on Ray Dashboard |
| `x-post-2026-06-08-hk-meilisearch-botnet.md` | X (Twitter) headline: 66-host HK SEO content-spam botnet via index-name attribution |

## Assessment hand-offs

`assessments/` holds IR-grade hand-off packages (draft form, restraint-bounded — never sent without
researcher review). One bundle per active campaign cross-reference:

| Bundle | Recipient | Subject |
|--------|-----------|---------|
| `comfyui-ghost-2026-06-08-handoff/` | Censys ARC | 3 likely-GHOST hosts extending their April disclosure |
| `ray-shadowray-2026-06-08-handoff/` | Oligo Security + Anyscale | 463 likely-ShadowRay-2.0 attacker IPs + 5-signal IoC pattern |
| `cat04/` | (research bundle) | Training-frameworks survey artifacts |

## Tools

`tools/` holds attack-surface research documents and Python scripts used in survey work:

| File | What it is |
|------|-----------|
| `ollama-model-injection.md` | Unauthenticated `/api/create` injection (all Ollama versions) |
| `ollama-ssrf.md` | SSRF via `/api/pull` private registry URLs |
| `ollama-connect-takeover.md` | Cloud account takeover via leaked `signin_url` |
| `hexstrike-ai-chain.md` | Model injection to RCE chain (HexStrike AI) |
| `open-webui-ollama-bypass.md` | UI auth on port 3000 does not protect Ollama port 11434 |
| `open-webui-cloud-proxy-hijack.md` | Operator API subscriptions drained via unauthenticated inference |
| `bypass-prompts.json` | System prompt bypass corpus |
| `ollama-recon.py` | Enumerate, inject-test, cloud hunt |
| `visor-report.py` | HTML report generator for survey data |
| `run-survey.sh` | Survey pipeline runner |
| `aimap-to-findings.py`, `binding-runner.py`, `ns-attribute.py`, and others | Survey utilities |

## NuClide toolchain

The surveys run end-to-end through the NuClide tool stack. Each stage is its own repo.

| Stage | Tool | Repo |
|-------|------|------|
| Orchestrator | VisorPlus | nuclide-research/VisorPlus |
| Discovery (Shodan harvest) | JAXEN | nuclide-research/JAXEN |
| Discovery (Shodan dorks) | VisorSD | nuclide-research/VisorSD |
| Discovery (gov TLD) | VisorGoose | nuclide-research/VisorGoose |
| Discovery (provenance graph) | VisorGraph | nuclide-research/VisorGraph |
| Discovery (provenance/recon) | recongraph | nuclide-research/recongraph |
| Discovery (multi-source recon) | nu-recon | nuclide-research/nu-recon |
| Discovery (managed-tier surface) | menlohunt | nuclide-research/menlohunt |
| Discovery (corpus + dorks + probes) | tome | nuclide-research/tome |
| Active banner / liveness | scanner | nuclide-research/scanner |
| Fingerprint + deep enum | aimap | nuclide-research/aimap |
| Target classification | aimap-profile | nuclide-research/aimap-profile |
| HTTP auth-prober | herald | nuclide-research/herald |
| FP refutation ledger | VisorCAS | nuclide-research/VisorCAS |
| Agent-monitoring (FP detection) | agent-logging-system | nuclide-research/agent-logging-system |
| Internal continuous sensor | VisorRoam | nuclide-research/VisorRoam |
| Findings ledger | VisorLog | nuclide-research/VisorLog |
| Compliance scoring | VisorScuba | nuclide-research/VisorScuba |
| Exploit ranking | BARE | nuclide-research/BARE |
| Adversarial corpus | VisorCorpus | nuclide-research/VisorCorpus |
| Prior-findings recall | VisorRAG | nuclide-research/VisorRAG |
| Agentic LLM benchmark | VisorAgent | nuclide-research/VisorAgent |
| Process-injection benchmark | VisorHollow | nuclide-research/VisorHollow |
| Auth-context analyzer | cortex | nuclide-research/cortex-framework |
| NICE/DCWF role wardrobe | wardrobe | nuclide-research/wardrobe |
| Research-program syllabus | syllabus | nuclide-research/syllabus |
| Quiet single-host assessment | tiptoe | nuclide-research/tiptoe |
| Live SSE safety dashboard | safety-stream | nuclide-research/safety-stream |
| Book-grounded coding skill | warrant | nuclide-research/warrant |
| Operator-doctrine framework | operator-doctrine | nuclide-research/operator-doctrine |

## Quick start

```bash
git clone https://github.com/nuclide-research/AI-LLM-Infrastructure-OSINT
cd AI-LLM-Infrastructure-OSINT

# Browse Shodan queries by category
ls shodan/queries/

# Search across all queries
grep -r "qdrant" shodan/queries/
grep -rn " T1 " shodan/queries/

# Read the methodology index
cat methodology/README.md

# Browse case studies
ls case-studies/commercial/
ls case-studies/universities/
```

## What this repo is not

This is not a scanner. It does not run queries or probe hosts. It is a reference and data
repository: query catalog, methodology documentation, case studies, and survey artifacts.
Scanning is done by the toolchain repos listed above. The `tools/` PoC scripts are
point-in-time research artifacts, not maintained attack tools.

The `disclosures/` directory contains 134 published disclosure documents. They are an
intentional published portfolio and are not enumerated here.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). The bar: queries must be verifiable (you have seen
them return real results), tagged with an exposure tier, with a Notes column when the query
reveals something specific. New categories must map to a real, deployed AI/ML platform.

## License

MIT. Part of the NuClide toolchain. Contact: [nuclide-research.com](https://nuclide-research.com)
