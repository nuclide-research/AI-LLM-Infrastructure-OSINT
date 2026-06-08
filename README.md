<h1 align="center">AI-LLM-Infrastructure-OSINT</h1>

<h4 align="center">Population-scale survey program of exposed AI and ML infrastructure on the public internet.</h4>

<p align="center">
  <a href="https://github.com/nuclide-research/AI-LLM-Infrastructure-OSINT/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue?style=flat-square" alt="license"></a>
  <a href="https://nuclide-research.com"><img src="https://img.shields.io/badge/by-NuClide-blue?style=flat-square" alt="NuClide"></a>
</p>

<p align="center">
  <a href="#snapshot-2026-06-08">Snapshot</a> •
  <a href="#the-thesis-under-test">Thesis</a> •
  <a href="#repository-structure">Structure</a> •
  <a href="#numbered-category-catalogue">Categories</a> •
  <a href="#methodology">Methodology</a> •
  <a href="#articles">Articles</a> •
  <a href="#nuclide-toolchain">Toolchain</a> •
  <a href="#restraint-discipline">Restraint</a>
</p>

---

This repository is the NuClide Research catalogue of how the modern AI and ML stack exposes itself to the public internet by default. A living archive of Shodan queries, population-scale surveys, per-instance case studies, methodology insights, IR hand-off packages, and disclosure outcomes.

It is the primary published record of the NuClide survey program. The work is done. The surveys are published. The methodology is open. The toolchain that produced this work lives in its own repos and is linked under [NuClide Toolchain](#nuclide-toolchain).

---

## Snapshot (2026-06-08)

| | |
|---|---:|
| Numbered platform categories | 33 |
| Shodan query files | 54 |
| Methodology insights | 88 (numbered 01-89, one gap) |
| Case studies, total | 376 |
| Case studies, commercial | 254 |
| Case studies, universities | 101 |
| Case studies, critical-infra + government + K12 + AI-chatbot | 13 |
| Published articles | 3 |
| IR hand-off packages | 3 (Censys ARC, Oligo Security + Anyscale, Cat-04 research bundle) |
| Disclosure documents | 134 |
| Session analyses | 71 |
| Per-survey evidence packs | 33 |

The program runs continuously and ships fresh measurements monthly. The most recent published headline finds are in `articles/` and the corresponding case studies in `case-studies/commercial/`.

---

## The thesis under test

NuClide is a research program, not a one-shot scan. The work has a falsifiable thesis, and every survey either strengthens or breaks it.

**Insight #76, auth-permissive cohort default.** A new generation of OSS AI/ML infrastructure platforms (vector databases, RAG knowledge-base engines, agent orchestrators, observability platforms, model gateways, LLM workflow builders) ships with auth-permissive defaults. Registration is open, the data layer requires no authentication, and configuration disclosure on public endpoints is the norm. Operators deploy these into production, including at universities, hospitals, national research institutes, and Fortune 500 enterprises, without re-configuring the defaults.

The thesis is platform-cohort dependent. Same-day measurements across the cohort:

| Platform | Class | Unauth rate |
|---|---|---:|
| Langfuse | observability | 88.9 % SIGNUP_OPEN |
| RAGFlow | RAG engine | 87.2 % REGISTER_OPEN |
| Arize Phoenix | observability | 74.5 % PROJECTS_UNAUTH |
| Flowise | workflow builder | 68.7 % CHATFLOWS_OPEN |
| ComfyUI | image-gen UI | 77.5 % (no auth concept at all) |
| Meilisearch | vector + search | 9.6 % (env var, doc-foregrounded) |
| Open WebUI | chat UI | 11.8 % |
| Dify | LLM app platform | 0.9 % |
| AnythingLLM | doc chat | 0 % (hardened-by-default) |
| Langfuse cloud-tier auth | observability | 0 % (forced) |

The cohort split is real. The same-day spread from 0 % to 88.9 % is the corollary that **shipping defaults are load-bearing**: operators inherit whatever the framework ships with, at population scale, regardless of operator skill.

Each new platform we survey either reproduces the cohort pattern or breaks it. Negative results (AnythingLLM at 0 %) are published as confirmation by contrapositive. The thesis can be falsified by finding a same-cohort platform that ships auth-closed and at population scale stays auth-closed.

The full program brief is at `research-program/PROGRAM.md`. The synthesis paper-in-progress is `case-studies/commercial/SYNTHESIS-2026-05.md`.

---

## Repository structure

```
.
├── shodan/
│   ├── queries/                    33 numbered category files + supplementary sets (54 files total)
│   ├── ct-log-catalog.md
│   ├── favicon-hashes.md
│   ├── query-log.md                Every executed dork with hit counts
│   ├── Shodan_AI_Reference.pdf     Polished v2.1 PDF reference (April 2026)
│   └── README.md
├── methodology/                    88 numbered insight files (01-89, gap at 48)
│   ├── README.md                   Insight index with first-capture dates
│   ├── tool-stage-mapping.md       Which arsenal tool runs at which pipeline stage
│   ├── gov-critinfra-playbook.md
│   └── embedding-services-survey-runbook.md
├── case-studies/
│   ├── commercial/                 254 per-survey writeups, cross-survey syntheses, deep-dive subdirs
│   ├── universities/               101 university AI infrastructure exposures
│   │   ├── US/                     31 files organized by state prefix
│   │   └── international/          32 country-code subdirectories
│   ├── critical-infra/             3
│   ├── government/                 5
│   ├── k12/                        3
│   └── ai-chatbot/                 2
├── articles/                       Published-grade write-ups (Medium / defender advisories / X-posts)
├── assessments/                    IR hand-off packages, restraint-bounded, draft form
├── disclosures/                    134 published disclosure documents + templates + _rendered/
├── analysis/                       71 session-analysis reports (one per closing session)
├── evidence/                       33 per-survey evidence packs (screenshot bundles + raw probe artifacts)
├── research-program/               Three-layer index of the entire program
│   ├── PROGRAM.md                  Thesis statement + empirical baseline
│   ├── ROADMAP.md                  Append-only decision log + survey queue
│   ├── surveys/                    Date-indexed survey log
│   ├── roles/                      NICE / DCWF role-to-research mapping
│   ├── insights/                   Per-insight cross-references
│   ├── disclosures/                Pipeline-state index
│   ├── literature/                 Academic citation index
│   └── papers/                     Drafts of synthesis papers
├── reference/                      Port catalog, terminology, category taxonomy, OLAP architecture notes
├── tools/                          Attack-surface research docs, PoC scripts, survey utilities
├── assurance/                      Blue-team OPA/Rego policies + NuClide task bindings (v1, v2, v3)
├── categories/                     Per-category deep briefs (currently: Cat-33 AI Email Guardrails)
├── data/                           Scan outputs (sensitive fields gitignored; .db files not tracked)
├── docs/                           Superpowers skill files
├── CLAUDE.md                       Toolchain context for Claude Code sessions
├── SESSION.md                      Last session state, updated every close
├── CONTRIBUTING.md
├── DISCLAIMER.md
└── LICENSE
```

---

## Numbered category catalogue

Each numbered category has a primary query file in `shodan/queries/` and one or more case studies in `case-studies/commercial/`.

```
01 LLM Orchestration             18 Jupyter / JupyterHub
02 Vector Databases              19 Streamlit Data Apps
03 Model Serving                 20 Gradio + Specialty Data Layers
04 Training & Experiments        21 Browser Agents
05 Gateways & Monitoring         22 Data Labeling
06 Agent Frameworks              23 AI Safety Eval
07 RAG Stacks                    24 LLM Safety Guardrail + Observability
08 Image Generation              25 Elasticsearch
09 Code Assistants               26 Exfiltrated Credentials + Agent Memory
10 MCP Servers                   27 Embedding Services
11 Credential Leaks              28 Medical Edge AI + ML Governance
12 Container Infrastructure      29 Workflow Orchestration
13 Backup + Snapshot             30 Agent Memory
14 GPU + Compute Dashboards      31 Classical ML
15 Fingerprinting Canaries       32 AI Gateways
16 BI + Dashboards               33 AI Email Guardrails
17 Voice + Audio AI
```

Survey extensions tracked as case studies (no dedicated query file): **Cat-34** (FastGPT), **Cat-46** (ComfyUI default-port population), **Cat-46b** (Meilisearch), **Cat-47** (Ray Dashboard).

Every query is tagged with an exposure tier:

| Tier | Meaning |
|---|---|
| T1 | Unauthenticated by default. A hit is typically a live, interactive target. |
| T2 | Requires misconfiguration or has known auth-bypass CVEs. One extra probe confirms exposure. |
| T3 | Recon and fingerprint only. Use for inventory and pivoting. |

Supplementary query sets cover AI-eval / red-team, auth gateways, experiment tracking, model-serving registry, RAG frameworks, safety guardrail, service mesh, specialty data layers, voice / audio AI, workflow orchestration, Texas universities, and a Google-dorks supplement (`ghdb-google-dorks.md`).

---

## Methodology

The pipeline is documented and executable. Eight stages, in order:

```
Platform Intel -> Discover -> Active Banner -> Fingerprint -> Verify -> Attribute -> Classify -> Ledger -> Score -> Codify
```

The middle stage, Verify, is where the discipline lives. 18 of the first 21 codified insights are verification-stage failures or the rules that prevent them. The scan is the easy part; verification is what separates a candidate from a finding. At population scale, skipped verification fails in systematic, not random, ways, producing confident, reproducible, wrong numbers.

The restraint ethic governs every survey. Enumerate metadata, do not exfiltrate. Names ARE the finding. Sample payloads minimally only to confirm severity. The ratio of "what we did not do" to "what we did" is the methodology.

### Numbered insights (88 files, 01 through 89, gap at #48)

Each insight is a standalone markdown file derived from a specific survey or incident, citable independently. The index is at `methodology/README.md`.

Recent insights include:

- **#76** Auth-permissive cohort default (the central thesis above)
- **#77** Active-banner prefilter via the `scanner` stage (Shodan cache decay around 70 %)
- **#78** Shared deployment kit, operator-class exposure
- **#79** Aspirational name-field attribution hierarchy
- **#80** DMARC enforcement rate as funding-stage proxy
- **#81** Compose EHLO leak generalizes to a class of three MTAs
- **#82** Branded error bodies are the banner
- **#83** Lane-C per-operator OAuth, not marketplace
- **#84** Cloud wrapper blast-radius expansion
- **#85** Stub vs real-vendor discriminator in LiteLLM catalog
- **#86** The disclosure pipeline is itself attack surface
- **#87** Canary persistence as monitoring proxy
- **#88** Scrape topology as operator org chart
- **#89** Framework-level auth bypass on pprof

---

## Articles

`articles/` holds published-grade write-ups of headline findings:

| File | Topic |
|---|---|
| `medium-2026-06-08-changsha-deepfake-rig.md` | A complete turnkey deepfake-production pipeline running unauthenticated on a Chinese 8x A100 cluster |
| `shadowray-2-self-detect-2026-06-08.md` | Defender advisory: 5-signal IoC pattern for ShadowRay 2.0 attacker fleet on Ray Dashboard |
| `x-post-2026-06-08-hk-meilisearch-botnet.md` | X (Twitter) headline thread: 66-host Hong Kong SEO content-spam botnet, attributed entirely from Meilisearch index naming |

---

## Assessment hand-off packages

`assessments/` holds IR-grade hand-off packages, draft form, restraint-bounded, never sent without researcher review. One bundle per active campaign cross-reference.

| Bundle | Recipient | Subject |
|---|---|---|
| `comfyui-ghost-2026-06-08-handoff/` | Censys ARC | 3 likely-GHOST hosts extending the April 2026 cryptomining-botnet disclosure |
| `ray-shadowray-2026-06-08-handoff/` | Oligo Security + Anyscale | 463 likely-ShadowRay-2.0 attacker IPs + 5-signal metadata IoC pattern |
| `cat04/` | (research bundle) | Training-frameworks survey artifacts |

---

## Disclosures

`disclosures/` contains 134 published disclosure documents covering universities, vendors, healthcare organizations, defense contractors, government CERTs, and AI-platform maintainers. The portfolio is an intentional public record; individual disclosures are not enumerated in this README. The directory includes the disclosure schema (`SCHEMA.md`), templates, and `_rendered/` outputs.

A meta-finding about this portfolio is captured as Insight #86: the disclosure pipeline is itself attack surface, and the choices made in the disclosure-routing flow are themselves findings.

---

## Tools

`tools/` holds attack-surface research documents and Python scripts used in survey work. Notable entries:

| File | What it is |
|---|---|
| `ollama-recon.py` | Enumerate, inject-test, cloud hunt across the Ollama population |
| `ollama-model-injection.md` | Unauthenticated `/api/create` injection (all Ollama versions) |
| `ollama-ssrf.md` | SSRF via `/api/pull` private registry URLs |
| `ollama-connect-takeover.md` | Cloud account takeover via leaked `signin_url` |
| `hexstrike-ai-chain.md` | Model injection to RCE chain (HexStrike AI) |
| `open-webui-ollama-bypass.md` | UI auth on port 3000 does not protect Ollama port 11434 |
| `open-webui-cloud-proxy-hijack.md` | Operator API subscriptions drained via unauthenticated inference |
| `chroma_probe.py`, `verify_chroma_campaign.py`, `verify_chroma_version.py` | ChromaDB campaign verifiers |
| `clickhouse_probe.py`, `flowise_probe.py`, `n8n_probe.py` | Per-platform survey probes |
| `verify_vm_unauth.py` | VictoriaMetrics unauth verifier |
| `glance.py` | Schema-only sensitivity analyzer |
| `aimap-to-findings.py`, `binding-runner.py`, `ns-attribution.py` | Survey utility pipeline |
| `staleness_check.py` | Detect stale survey data |
| `version_sweep.py` | Population-level version-distribution sweep |
| `visor-report.py` | HTML report generator |
| `bypass-prompts.json` | System-prompt bypass corpus |
| `epoch_lookup.py` | Epoch AI timestamp lookup |

These are point-in-time research artifacts, not maintained attack tooling. The continuously-developed tools live in the NuClide toolchain repos.

---

## NuClide toolchain

The surveys run end-to-end through the NuClide tool stack. Each stage is its own repo under `github.com/nuclide-research`.

| Stage | Tool | What it does |
|---|---|---|
| Orchestrator | VisorPlus | Chains JAXEN -> VisorSD -> VisorCorpus -> BARE -> aimap, writes to VisorLog |
| Platform corpus | tome | Canonical per-platform JSON (50 platforms): dorks, fingerprints, probe configs |
| Active sweep | tiptoe, scanner | Quiet single-host assessment; standing post-harvest banner sweep |
| Shodan harvest | JAXEN | Shodan-dork harvester, accumulates into `empire.db` |
| Shodan dorks | VisorSD | Dork curation tool |
| Gov-TLD discovery | VisorGoose | `.gov`/`.mil` AI-infra discovery |
| Censys + recon graph | VisorGraph, recongraph, nu-recon | Cert pivot, multi-source recon graph |
| Managed-tier discovery | menlohunt | GCP-EASM-class discovery |
| Fingerprint + deep enum | aimap | 120 fingerprints, 50 deep enumerators, single Go binary |
| Target classification | aimap-profile | HIPAA / clinical / personal / commercial / research / honeypot classification |
| FP refutation ledger | VisorCAS | False-positive signature store, the inverse of VisorLog |
| Agent-monitoring | agent-logging-system | Per-enumerator FP detection across multi-corpus runs |
| HTTP auth-prober | herald | Declarative YAML-configured HTTP auth probes |
| Internal sensor | VisorRoam | Continuous AI-infra sensor for owned networks |
| Findings ledger | VisorLog | Append-only ECS-normalized ledger with lifecycle tracking |
| Compliance scoring | VisorScuba | OPA / Rego, ScubaGear-style, NIST AI RMF + OWASP LLM Top 10 + MITRE ATLAS |
| Exploit ranking | BARE | Semantic search across 3,904 Metasploit modules, offline binary |
| Adversarial corpus | VisorCorpus | 6-class adversarial corpus for any LLM-adjacent surface |
| Prior-findings recall | VisorRAG | RAG over the cumulative ledger |
| Agentic LLM benchmark | VisorAgent | Controlled-target LLM exploitation benchmark (ethical-stop tool) |
| Process-injection benchmark | VisorHollow | Windows-only Cobalt-Strike-class process injection bench |
| Auth-context analyzer | cortex | Per-request authentication-context derivation |
| Wardrobe (NICE/DCWF) | wardrobe | 1,281 atoms across 39 NICE roles, outfit-based session stance |
| Research syllabus | syllabus | 981-PDF corpus (NICE 541 + aisec courses + USENIX/NDSS papers) |
| Live safety dashboard | safety-stream | SSE stream of self-reported safety reasoning |
| Book-grounded skill | warrant | Citation-grounded coding agent |
| Operator doctrine | operator-doctrine | 5-role DCWF DoD framework |

The active arsenal chain runs through `bash data/visor-chain-runner.sh <slug>` against an IP list and produces case studies plus ledger entries plus a numbered insight per survey.

---

## Restraint discipline

Every survey and deep dive in this repository was conducted under the same explicit rules. They are not soft preferences; they are how the work is admissible at all.

- GET-only metadata reads. Never POST to job-submission, prompt-execution, or write endpoints.
- Names + counts + version strings + file names. Never read job bodies, model checkpoints, or operator content.
- No authentication attempts on any service. No credential testing. No CVE exploitation.
- Honeypot pre-filter on every survey (AS63949 Linode salt, protocol-strict probe shape, GreyNoise scanner classification).
- WHOIS-driven contact resolution for disclosure routing. Never slug-heuristic.
- Hard-disclosure floor: even when "stopping the malicious activity" is the obvious want, intervention on third-party hosts is unauthorized computer access regardless of intent. Hand-off to substrate providers, national CERTs, and tracker authors (Censys ARC, Oligo Security, others) is the legitimate channel.

The 463 likely-ShadowRay attacker IPs and the 2,423-hour-of-output Changsha deepfake rig were observed, not engaged.

---

## Quick start

```bash
git clone https://github.com/nuclide-research/AI-LLM-Infrastructure-OSINT
cd AI-LLM-Infrastructure-OSINT

# Browse Shodan queries by category
ls shodan/queries/

# Search queries for a specific platform
grep -rn "qdrant" shodan/queries/

# Read the methodology index
less methodology/README.md

# Browse recent case studies
ls -t case-studies/commercial/*.md | head -20

# Read the headline articles
ls articles/

# Read the research-program three-layer index
less research-program/README.md
```

---

## What this repo is not

This is not a scanner. It does not run queries, probe hosts, or maintain attack tooling. It is a published reference and data repository: query catalog, methodology insights, case studies, survey artifacts, IR hand-offs, and disclosure record.

The active scanning, fingerprinting, and verification is done by the toolchain repos linked above. The `tools/` PoC scripts are point-in-time research artifacts; the live tools live in their own repos.

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). The bar:

- Queries must be verifiable. You have to have seen them return real results.
- Queries are tagged with an exposure tier (T1 / T2 / T3) and a Notes column where the query reveals something specific.
- New categories must map to a real, deployed AI/ML platform with a population worth tracking.
- New insights are numbered, derived from a specific survey or incident, and citable independently.
- Case studies follow the methodology pipeline and end with a toolchain-provenance block.

---

## License

MIT. Part of the NuClide toolchain. Contact: [nuclide-research.com](https://nuclide-research.com), `nicholas@nuclide-research.com`.

Prior published research includes CISA-coordinated disclosures CVE-2025-4364 and ICSA-25-140-11.
