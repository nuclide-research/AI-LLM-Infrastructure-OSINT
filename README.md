# AI-LLM-Infrastructure-OSINT

Verified Shodan queries, fingerprints, survey data, and detection logic for exposed AI/ML infrastructure.

This is the NuClide survey program: a living record of what the AI/ML stack exposes to the
internet by default. It covers model servers, vector databases, orchestration UIs, MCP servers,
inference gateways, notebook environments, and adjacent data infrastructure. Each category
produces Shodan queries (tagged T1/T2/T3), per-instance case studies, and numbered methodology
insights extracted from the survey runs. The `tools/` directory contains attack-surface research
documents and PoC scripts tied to specific findings.

A companion toolchain (VisorPlus, aimap, JAXEN, VisorLog, and others) produced and processes the
survey data. The toolchain repos are linked under [NuClide Toolchain](#nuclide-toolchain).

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

---

## Repo structure

```
.
├── shodan/
│   ├── queries/              # Shodan query files: 36 files across categories 01-32, plus supplementary
│   ├── Shodan_AI_Reference.pdf  # Polished PDF reference (v2.1, April 2026)
│   ├── ct-log-catalog.md
│   ├── favicon-hashes.md
│   ├── query-log.md
│   └── README.md
├── methodology/              # 75 numbered insights (insight-01 through insight-76, one gap)
│   ├── README.md             # Insight index with first-capture dates
│   └── tool-stage-mapping.md
├── case-studies/
│   ├── commercial/           # Per-survey writeups and a cross-survey synthesis
│   ├── universities/         # University AI infrastructure exposures
│   │   ├── US/               # 31 files, organized by state prefix
│   │   └── international/    # 32 country-code subdirectories
│   ├── critical-infra/
│   ├── k12/
│   ├── ai-chatbot/
│   └── government/
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
├── disclosures/              # 140 disclosure documents
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
31 Classical ML - 32 AI Gateways

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

75 numbered insights reside in `methodology/` (insight-01 through insight-76; gap after 47).
Each is a standalone markdown file derived from a specific survey or incident, citable
independently. The index is at `methodology/README.md`.

Recent examples: Insight #68 (verification rungs and claim ladders), #71 (network placement
as auth), #74 (gateway as master-key multiplier), #76 (app auth-on with operator debris auth-off).

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
| Fingerprint + deep enum | aimap | nuclide-research/aimap |
| Findings ledger | VisorLog | nuclide-research/VisorLog |
| Compliance scoring | VisorScuba | nuclide-research/VisorScuba |
| Exploit ranking | BARE | nuclide-research/BARE |
| Adversarial corpus | VisorCorpus | nuclide-research/VisorCorpus |
| Agentic LLM benchmark | VisorAgent | nuclide-research/VisorAgent |
| Process-injection benchmark | VisorHollow | nuclide-research/VisorHollow |
| Quiet single-host assessment | tiptoe | nuclide-research/tiptoe |

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

The `disclosures/` directory contains 140 published disclosure documents. They are an
intentional published portfolio and are not enumerated here.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). The bar: queries must be verifiable (you have seen
them return real results), tagged with an exposure tier, with a Notes column when the query
reveals something specific. New categories must map to a real, deployed AI/ML platform.

## License

MIT. Part of the NuClide toolchain. Contact: [nuclide-research.com](https://nuclide-research.com)
