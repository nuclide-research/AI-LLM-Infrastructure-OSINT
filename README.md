[![Claude Code Friendly](https://img.shields.io/badge/Claude_Code-Friendly-blueviolet?logo=anthropic&logoColor=white)](https://claude.ai/code)

# AI/LLM Infrastructure OSINT

> Open-source intelligence and security research focused on the exposed control plane of modern AI/ML infrastructure.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Research: Authorized Only](https://img.shields.io/badge/Research-Authorized%20Only-red.svg)](DISCLAIMER.md)
[![Maintained by NuClide](https://img.shields.io/badge/Maintained%20by-NuClide-purple.svg)](#about)
[![Reference: v2.1](https://img.shields.io/badge/Reference-v2.1%20%C2%B7%20Apr%202026-teal.svg)](shodan/Shodan_AI_Reference.pdf)
[![Disclosure: Ollama](https://img.shields.io/badge/Disclosure-Ollama%20Unauth%20Injection-critical)](case-studies/ollama-enterprise-exposures.md)
[![Universities: 57 case studies](https://img.shields.io/badge/Universities-57%20case%20studies-orange)](case-studies/universities/index.md)
[![Account Takeovers: 10](https://img.shields.io/badge/Account%20Takeovers-10%20confirmed-red)](case-studies/universities/index.md)

---

## Mission

The AI/ML stack moved faster than its security model. Vector databases ship without auth by default. LLM gateways log every prompt to disk. Inference servers expose `/v1/models` to the internet. Fine-tuning dashboards proxy GPU compute to anyone who finds the URL. MCP servers wire shell, filesystem, and database tools to LLMs over unauthenticated HTTP.

This repository is a living catalogue of **fingerprints, queries, exposure patterns, and detection logic** for the infrastructure that runs modern AI — built so that defenders can find their own assets before adversaries do.

## Scope

| Category | Examples |
|----------|----------|
| **LLM Orchestration** | Flowise, Langflow, Dify, Open WebUI, LiteLLM, Ollama, Clawdbot |
| **Vector Databases** | ChromaDB, Qdrant, Weaviate, Milvus, pgvector, Redis Search, ClickHouse, Cassandra |
| **Object Storage & Artifact Stores** | MinIO, Harbor, Docker Registry v2 — where the models and vectors actually live |
| **Model Serving** | vLLM, Triton, TGI, llama.cpp, LM Studio, GPT4All, NVIDIA NIM |
| **Training & Experiments** | MLflow, Kubeflow, Ray, ClearML, Argilla, Label Studio, Feast |
| **AI Gateways & Observability** | LiteLLM Proxy, Portkey, Langfuse, Helicone, Phoenix/Arize |
| **Agent Frameworks** | SuperAGI, OpenDevin, MetaGPT, Clawdbot, AutoGen |
| **RAG Stacks & Self-Hosted AI Apps** | h2oGPT, Danswer/Onyx, Quivr, Khoj, RAGFlow, LibreChat |
| **Image Generation** | ComfyUI, Stable Diffusion, AUTOMATIC1111, InvokeAI, Fooocus |
| **AI Code Assistants** | Tabby, self-hosted Cody, Continue, Refact |
| **MCP Servers** | Model Context Protocol exposed over HTTP/SSE |
| **Credential & Config Leaks** | `OPENAI_API_KEY` / `ANTHROPIC_API_KEY` / `GROQ_API_KEY` / `HF_TOKEN` exposure, `.env` files |
| **Container & Orchestration** | Docker daemon, Kubernetes, kubelet, etcd, Consul, Vault |
| **GPU & Compute Dashboards** | NVIDIA DCGM, Ray dashboard, RunPod, Vast.ai, GPUStack |

## Repository Structure

```
.
├── reference/                      # Tool-agnostic reference material
│   ├── ports.md                    # Common AI/LLM infrastructure ports
│   └── terminology.md              # AI/ML stack terminology primer
├── shodan/                         # Shodan query reference
│   ├── Shodan_AI_Reference.pdf     # Polished PDF (v2.1, April 2026)
│   └── queries/                    # Per-category markdown sources
│       ├── 01-llm-orchestration.md
│       ├── 02-vector-databases.md  # incl. Object Storage & Artifact Stores
│       ├── 03-model-serving.md
│       ├── 04-training-experiments.md
│       ├── 05-gateways-monitoring.md
│       ├── 06-agent-frameworks.md
│       ├── 07-rag-stacks.md
│       ├── 08-image-generation.md
│       ├── 09-code-assistants.md
│       ├── 10-mcp-servers.md
│       ├── 11-credential-leaks.md
│       ├── 12-containers.md
│       ├── 13-backup-snapshot.md
│       ├── 14-gpu-compute.md
│       ├── 15-fingerprinting.md
│       └── appendix-cve.md
├── tools/                          # Attack surface research & PoC tooling
│   ├── ollama-model-injection.md   # Unauthenticated /api/create injection (all versions)
│   ├── ollama-ssrf.md              # SSRF via /api/pull private registry URLs
│   ├── ollama-connect-takeover.md  # Cloud account takeover via leaked signin_url
│   ├── hexstrike-ai-chain.md       # Model injection → RCE chain (HexStrike AI)
│   ├── ollama-recon-findings.md    # Recon methodology & scan findings
│   ├── ollama-recon.py             # Scanner: enumerate, inject-test, cloud hunt
│   └── bypass-prompts.json         # System prompt bypass corpus
├── data/                           # Scan outputs (gitignored sensitive fields)
│   └── ollama-findings.md          # Human-readable scan findings
├── case-studies/                   # Real-world exposure writeups
│   ├── universities/               # University AI infrastructure exposures (57 case studies)
│   │   ├── index.md                # Index + discovery methodology
│   │   ├── KR/                     # South Korea (5 case studies)
│   │   │   └── POSTECH.md          # 7-node cluster, 3 account takeovers, synchrotron beamline
│   │   ├── US/                     # United States (11 case studies)
│   │   │   ├── IN-purdue-northwest.md # Purdue NW — account takeover, user-ID embedded sales models
│   │   │   └── NC-duke.md          # Duke — agent model + file inspection tools
│   │   ├── TW/                     # Taiwan (5 case studies)
│   │   │   └── tanet.md            # TANet 18-node cluster, multi-institution, account takeover
│   │   ├── VN/                     # Vietnam (3 case studies)
│   │   │   └── hanoi.md            # 18 cloud proxy subscriptions, Docker container ID leak
│   │   └── ...                     # 29 countries total: see index.md
│   ├── critical-infra/             # Critical infrastructure exposures
│   │   ├── US-GA-cartersville-city.md  # City of Cartersville — Windows, cloud proxy
│   │   └── US-TN-meriwether-lewis-ec.md  # Electric cooperative — 235B model
│   ├── k12/                        # K-12 school district exposures
│   │   └── US-NJ-hts-k12-dvrc.md  # NJ school district (DVRC) — 5 cloud proxies
│   ├── hts-k12-nj-open-webui.md   # (legacy path — see k12/)
│   └── ollama-enterprise-exposures.md  # Enterprise/critical-infra targets (2026-05-01)
├── censys/                         # Censys equivalents (planned)
├── fofa/                           # FOFA queries (planned)
├── zoomeye/                        # ZoomEye queries (planned)
├── dorks/                          # Google / GitHub dorks (planned)
├── nuclei-templates/               # Detection templates (planned)
├── DISCLAIMER.md
├── CONTRIBUTING.md
└── LICENSE
```

## Quick Start

**Browse by category:**
- [Shodan Query Index](shodan/README.md) — 15 categories + CVE cross-reference appendix
- [Common AI/LLM Ports Reference](reference/ports.md)
- [AI/ML Terminology Primer](reference/terminology.md)
- [Download the polished PDF reference (v2.1)](shodan/Shodan_AI_Reference.pdf)

**Active research:**
- [Ollama Enterprise Exposures — Case Study](case-studies/ollama-enterprise-exposures.md) — 11 enterprise/critical-infra targets confirmed vulnerable (2026-05-01)
- [University AI Exposures](case-studies/universities/index.md) — **57 case studies** across 29 countries; 10 account takeovers, 20+ cloud proxy nodes — organized by country (`KR/`, `US/`, `VN/`, ...)
  - Notable: **POSTECH synchrotron beamline** (`4gsr-beamline-ws`, PAL 4th-gen light source) — 235B Qwen3 model + live account takeover
  - **Shiv Nadar University** — 3-node cluster, chest X-ray AI (`lungsvlm` / VinDr-CXR), abliterated models, 18 cloud subscriptions
  - **TANet Taiwan** — 18-node multi-institution cluster across NTU/NCCU/NTHU/FJU/NCKU, account takeover, 5G security research system prompt
  - **India NIB / BSNL National Backbone** — qwen2.5-coder:32b coding cluster on national telecom backbone infrastructure
  - **Purdue NW** — account takeover + user-ID embedded fine-tuned sales models (multi-tenant platform exposure)
- [K-12 Education — NJ DVRC](case-studies/k12/US-NJ-hts-k12-dvrc.md) — Open WebUI bypass, 5 cloud proxy subscriptions, student data at risk
- [Critical Infrastructure — City of Cartersville](case-studies/critical-infra/US-GA-cartersville-city.md) — local government, Windows, DeepSeek cloud proxy
- [Critical Infrastructure — Meriwether Lewis Electric](case-studies/critical-infra/US-TN-meriwether-lewis-ec.md) — rural electric coop, 235B model, unauthenticated
- [Open WebUI Auth Bypass](tools/open-webui-ollama-bypass.md) — UI auth on port 3000 does not protect Ollama port 11434
- [Cloud Proxy Quota Hijacking](tools/open-webui-cloud-proxy-hijack.md) — operator API subscriptions drained via unauthenticated inference
- [Ollama Unauthenticated Model Injection](tools/ollama-model-injection.md) — all versions, no patch
- [Ollama Connect Account Takeover](tools/ollama-connect-takeover.md) — cloud subscription hijacking via leaked signin_url
- [HexStrike AI → RCE Chain](tools/hexstrike-ai-chain.md) — model injection → shell execution via trust confusion

**Search across all queries:**
```bash
git clone https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT.git
cd AI-LLM-Infrastructure-OSINT
grep -r "qdrant" shodan/queries/
grep -rn " T1 " shodan/queries/    # all unauth-by-default queries
```

## Tier System

Every query in v2.x is tagged with an exposure tier:

- **T1** — Unauthenticated by default. A positive hit is typically a live, interactive target.
- **T2** — Requires misconfiguration or has known auth-bypass CVEs. One additional probe confirms exposure.
- **T3** — Recon / fingerprint only. Use for inventory and pivoting, not as an immediate finding.

See [shodan/README.md](shodan/README.md#how-to-read-the-tables) for the full legend.

## Active Disclosure

**Ollama Unauthenticated Model Injection** — coordinated disclosure initiated 2026-05-01.

- **Affected:** All Ollama versions (no authentication on `/api/create` in any release)
- **CVE-2025-63389** — filed 2025-12-18, scoped ≤v0.13.5. Scope is incorrect: confirmed live on v0.13.5 → v0.22.0. `first_patched_version: null`.
- **Scale:** 227,715 exposed instances on Shodan as of 2026-05-01
- **Enterprise targets confirmed:** US electric utility co-op [CISA notified — identity withheld], Oracle Corporation infra, Azure IBM Granite RAG pipelines, GCP autonomous agent deployment, OVH cybersecurity product company, AWS managed instances
- **Public disclosure:** 2026-07-30 (90-day window)
- **Contact:** nicholas@nuclide-research.com

Secondary findings in coordinated disclosure:
- SSRF via `/api/pull` (CVE-2026-5530) — OOB DNS + internal port detection
- Ollama Connect account takeover — cloud subscription hijacking via leaked `signin_url`
- HexStrike AI RCE chain — model injection → trust confusion → Flask `/api/command` shell exec

---

## Use with Claude Code

This repo is designed to work as a live context source for Claude Code. Drop the following prompt into any Claude Code session to turn it into a guided AI infrastructure OSINT analyst — it'll use the queries, findings, and tooling here as its working reference.

**Copy-paste starter prompt:**

```
You are an AI/LLM infrastructure security analyst. I've cloned the AI-LLM-Infrastructure-OSINT
repository at ~/AI-LLM-Infrastructure-OSINT/. Use it as your primary reference.

Read the following files to orient yourself:
- README.md — repo overview and active disclosure status
- shodan/queries/ — query catalog by category
- tools/ollama-model-injection.md — active vulnerability (all Ollama versions)
- case-studies/ollama-enterprise-exposures.md — confirmed enterprise targets

My objective: [describe your target or task here]

Start by reading the relevant reference files, then help me build a query or probe strategy.
Use the tier system (T1/T2/T3) from the Shodan reference to prioritize.
```

**For Ollama-specific recon:**

```
I'm investigating an exposed Ollama instance at [IP]:11434.
Read tools/ollama-model-injection.md and tools/ollama-connect-takeover.md in my
AI-LLM-Infrastructure-OSINT repo, then help me:
1. Enumerate loaded models and detect cloud proxy access
2. Check for injectable system prompts
3. Test for the SSRF primitive via /api/pull
4. Assess if this matches any enterprise profiles in case-studies/
Tell me what you find and what to do next.
```

**For defender asset discovery:**

```
I need to find our org's exposed AI infrastructure before someone else does.
Read README.md in AI-LLM-Infrastructure-OSINT to understand the scope, then:
1. Help me build Shodan queries targeting our ASN or IP range
2. Identify which T1 (unauth-by-default) services I should prioritize checking
3. Generate a checklist of exposure patterns to verify internally
Focus on services that require no authentication by default.
```

---

## Contributing

PRs welcome — see [CONTRIBUTING.md](CONTRIBUTING.md). The bar is:
- Queries should be **verifiable** (you've seen them return real results).
- Tag every new query with an exposure tier (T1/T2/T3).
- Add a `Notes` column when the query reveals something specific (auth state, version disclosure, snapshot exposure).
- New categories should map to a real, deployed-in-the-wild AI/ML platform.

## Disclaimer

Read [DISCLAIMER.md](DISCLAIMER.md). Short version: this material is for **authorized security research, defensive asset discovery, and threat hunting only**. Touching infrastructure you don't own or have explicit permission to test is illegal in most jurisdictions. Don't.

## About

Maintained by **NuClide** — independent ICS/OT and AI infrastructure security research.

CISA disclosures: [CVE-2025-4364](https://nvd.nist.gov/vuln/detail/CVE-2025-4364), [ICSA-25-140-11](https://www.cisa.gov/news-events/ics-advisories/icsa-25-140-11).

Companion tooling: [aimap](https://github.com/Nicholas-Kloster/aimap) — AI/ML infrastructure scanner that defenders can run against their own networks.

Contact: nicholas@nuclide-research.com · [@Nicholas-Kloster](https://github.com/Nicholas-Kloster)
