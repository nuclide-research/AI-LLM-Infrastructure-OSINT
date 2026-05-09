[![Claude Code Friendly](https://img.shields.io/badge/Claude_Code-Friendly-blueviolet?logo=anthropic&logoColor=white)](https://claude.ai/code)

# AI/LLM Infrastructure OSINT

> Open-source intelligence and security research focused on the exposed control plane of modern AI/ML infrastructure.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Research: Authorized Only](https://img.shields.io/badge/Research-Authorized%20Only-red.svg)](DISCLAIMER.md)
[![Maintained by NuClide](https://img.shields.io/badge/Maintained%20by-NuClide-purple.svg)](#about)
[![Reference: v2.1](https://img.shields.io/badge/Reference-v2.1%20%C2%B7%20Apr%202026-teal.svg)](shodan/Shodan_AI_Reference.pdf)
[![Cross-Survey 2026-05](https://img.shields.io/badge/Cross--Survey-2026--05%20%C2%B7%2027%20platforms-blue)](case-studies/commercial/SYNTHESIS-2026-05.md)
[![Findings: 746](https://img.shields.io/badge/Findings%20Ledger-746%20events%20%C2%B7%20741%20hosts%20%C2%B7%2027%20surveys-red)](case-studies/commercial/SYNTHESIS-2026-05.md)
[![Tier-2 Expansion](https://img.shields.io/badge/Tier--2%20Expansion-Scaleway%2FOVH%2FLinode%20%C2%B7%20850%20Ollama%20%2B%20781%20Qdrant-orange)](case-studies/commercial/ollama-tier2-cloud-survey-2026-05.md)
[![Backup Snapshots](https://img.shields.io/badge/Backup%20%26%20Snapshots-269%20GB%20Qdrant%20snapshots%20exposed-darkred)](case-studies/commercial/backup-snapshot-services-survey-2026-05.md)
[![AS63949 Honeypot Fleet](https://img.shields.io/badge/Discovery-AS63949%20honeypot%20fleet%20%C2%B7%20393%20hosts-yellowgreen)](case-studies/commercial/ollama-tier2-cloud-survey-2026-05.md#honeypot-pollution-and-the-as63949-deception-fleet)
[![Compute Orchestration](https://img.shields.io/badge/Compute--Orch-Spark%20%2B%20Airflow%20%2B%20Ray%20%C2%B7%20118%20unauth-darkred)](case-studies/commercial/compute-orchestration-cloud-survey-2026-05.md)
[![Embedding Services](https://img.shields.io/badge/Embedding--Services-818%20IPs%20%C2%B7%20Klinikken.ai%20medical%20AI%20unauth-critical)](case-studies/commercial/embedding-services-cloud-survey-2026-05.md)
[![Vector DBs](https://img.shields.io/badge/Vector--DBs-Weaviate%20435%20open%20%C2%B7%20MyAi%20Corp%20enterprise%20exposure-orange)](case-studies/commercial/weaviate-cloud-survey-2026-05.md)
[![Milvus/Attu](https://img.shields.io/badge/Milvus%2FAttu-303%20Attu%20GUI%20open%20%C2%B7%20RAGFlow%201%2C224%20collections-orange)](case-studies/commercial/milvus-attu-survey-2026-05.md)
[![Elasticsearch](https://img.shields.io/badge/Elasticsearch-920%20unauth%20%C2%B7%20817%20ransomed%20%C2%B7%20active%20campaign-critical)](case-studies/commercial/neo4j-elasticsearch-supabase-redis-survey-2026-05.md)
[![Redis Stack](https://img.shields.io/badge/Redis%20Stack-112%20RedisInsight%20open%20%C2%B7%20100%25%20unauth-red)](case-studies/commercial/neo4j-elasticsearch-supabase-redis-survey-2026-05.md)
[![BI Dashboards](https://img.shields.io/badge/BI%2FDashboards-1%2C881%20unauth%20%C2%B7%20403%20Grafana%20admin%3Aadmin%20%C2%B7%20266%20Superset%20default--creds-critical)](case-studies/commercial/bi-dashboard-cloud-survey-2026-05.md)
[![Future Surveys](https://img.shields.io/badge/Future--Surveys-30%2B%20platforms%20catalogued-lightgrey)](case-studies/commercial/FUTURE-SURVEYS.md)
[![Operator Remediation Guide](https://img.shields.io/badge/Operators-Remediation%20Guide-green)](case-studies/commercial/REMEDIATION-GUIDE.md)
[![Disclosure: Ollama](https://img.shields.io/badge/Disclosure-Ollama%20Unauth%20Injection-critical)](case-studies/ollama-enterprise-exposures.md)
[![Universities: 81 case studies](https://img.shields.io/badge/Universities-81%20case%20studies-orange)](case-studies/universities/index.md)

---

## Featured: 2026-05 Cross-Survey Synthesis

**[Read the synthesis paper →](case-studies/commercial/SYNTHESIS-2026-05.md)**

Over 28 cloud /16 ranges (DigitalOcean + Hetzner + Vultr, ~1.83M IPs), surveyed 15 distinct AI/ML platform classes with ~5,000 confirmed unique deployments. **Tier-2 expansion 2026-05-04** ([`ollama-tier2-cloud-survey-2026-05.md`](case-studies/commercial/ollama-tier2-cloud-survey-2026-05.md)) reproduced the auth-off-default thesis across Scaleway, OVH, and Linode (76 additional /16s, 3.55M IPs, **1,019 more unauth Ollama instances**, operator-culture-independent).

- **Vector DB tier (Qdrant + ChromaDB + Milvus)**, 142 instances, **100% unauthenticated**
- **Inference tier (Triton + vLLM + Ollama)**, 388 instances, **100% unauthenticated**
- **MLOps (MLflow Tracking)**, 11 instances, **100% unauthenticated**, and **18% actively being exploited via CVE-2023-1177**, with attacker-injected experiments doubling overnight between probes
- **Data app (Streamlit)**, 551 instances, 100% unauthenticated (no built-in auth)
- **Object storage (MinIO)**, 852 instances, **0% anonymous-list** (auth-on-default works)
- **Orchestration UI tier (Flowise / n8n / Open WebUI / Langflow)**, 1,170 instances, 0% unauthenticated

The single sharpest finding in the survey: **the same operator population leaks Qdrant/Milvus/MLflow at 100% while protecting MinIO and Dify at ~0%**. Not different operators, same operators on different platforms. **Upstream defaults are the load-bearing variable**, not operator awareness.

Notable per-instance findings worth pulling up in the case-study list:

- **[tweet-optimize.com](case-studies/commercial/multi-tweet-optimize-facial-recognition.md)**, 1.21M facial embeddings (`onlyfans` + `psos` collections) on unauth Milvus; functional doxing primitive against creators. Disclosed 2026-05-03 to OnlyFans/Hetzner/Finnish DPA/operator. Still live ~9h post-disclosure.
- **[Triton chat-platform safety pipeline](case-studies/commercial/triton-cloud-survey-2026-05.md)**, child-safety minor-detection classifier with **127.4 million** lifetime inferences logged, exposed for adversarial probing
- **[MLflow CVE pair](case-studies/commercial/mlflow-cloud-survey-2026-05.md)**, two instances actively exploited by external attacker spraying CVE-2023-1177 path-traversal payloads at `/etc/` and `/root/.ssh/`; attack progressing between probes
- **[sanctionscanner.com](case-studies/commercial/TR-sanctionscanner-aml-kyc.md)**, 79M KYB records + 6.2M sanctions list entries unauth Elasticsearch; active ransomware compromise predates discovery
- **[MCP cross-cloud survey](case-studies/commercial/mcp-cloud-survey-2026-05.md)**, 95 confirmed Model Context Protocol servers across Scaleway / OVH / Linode (~2.18M IPs), 28 with non-empty `tools/list`. **Headline: a fully-exposed Gmail mailbox MCP** (19-tool send/read/delete CRUD on operator's own Gmail), **Alcy CRM MCP** (22-tool French facility-management CRUD), `rmcp` Elasticsearch MCP proxy, **hindsight-mcp v3.1.1 personal-AI-memory CRUD** (29 tools incl. `clear_memories`), 3× Casdoor IAM-CRUD across providers (recurring template-auth-off pattern), Brazilian legal RAG with state-audit data. Protocol-strict JSON-RPC handshake gate filtered AS63949 honeypot pollution to 1.1% (vs 91.6% on the prior Milvus survey).
- **[LLM Gateways cross-cloud survey](case-studies/commercial/llm-gateways-cloud-survey-2026-05.md)**, **1,899 confirmed unauth gateways across the same tier-2 cloud space, of which 1,857 (97.8%) returned functional inference to a single-token unauthenticated `/v1/chat/completions` PoC, operator provider-key quota actively billed.** Provider tags include 1,835 OpenAI / 2 Anthropic-functional / Google / OpenRouter / Mistral / DeepSeek / MiniMax / xAI / Moonshot. **1,829 of 1,857 (98.5%) returned the identical canned response from `gpt-4o-mini`, single open-source reseller-proxy template mass-deployed auth-off across operators**, single root-cause auth failure propagating to the entire population. Aggregate $0.011 of operator quota consumed by the disclosure-PoC across all 1,857 hosts; no key strings extracted. Extends the vLLM survey's 10-reseller-proxy finding by ~180× at the gateway-product tier.
- **[RAG framework survey](case-studies/commercial/rag-framework-cloud-survey-2026-05.md)**, **169 confirmed cross-cloud RAG framework hosts; auth-off-default thesis breaks here** (~100% auth-on at content endpoints), but **51% leak `/openapi.json` publicly**, full FastAPI route maps + Pydantic schemas + securitySchemes exposed. The "PrivateGPT" classification was over-eager: ~98% of those hits are custom FastAPI RAG apps (`Hibrit RAG API v1`, `AI News Publisher API`, `CamV3 Prediction Service`, `Nexus Skill Graph API`, `Docling Ingest API`), operators leak product names + API designs publicly, even when their data is locked.
- **[Browser-agent survey](case-studies/commercial/browser-agent-cloud-survey-2026-05.md)**, **153 confirmed unauth browser-automation backends** (83 Selenium Grid / 36 raw Chromium CDP / 34 Browserless). 100% unauth at the platform endpoint. **36 raw-Chromium CDP hosts = browser-RCE-equivalent** via WebSocket WSCP control. Single Browserless template fleet at HeadlessChrome 121.0.6167.85 mirrors the LLM-Gateway 1,829-host canned-response pattern; 5+ hosts on pre-2023 Chromium versions = chained stale-CVE attack surface on top of the unauth issue.
- **[Datalabel survey](case-studies/commercial/data-labeling-cloud-survey-2026-05.md)**, **348 confirmed cross-cloud, all doccano** (single-platform sweep). ~99% auth-on at `/v1/projects`, auth-off-default thesis breaks at this tier too. Zero Argilla / LabelStudio / Prodigy / CVAT confirmed in 1,017 prefixes, operator hygiene at population scale OR different-tier deployment profile.
- **[AI safety eval survey](case-studies/commercial/ai-safety-eval-cloud-survey-2026-05.md)**, **0 confirmed (corrected 2026-05-05)**. Initial survey reported 6; all were substring-match false positives (e.g. `b"garak"` matched on a Japanese anime filename `Garakuta no Kamisama` in a personal video library). Re-probed with tightened aimap fingerprints (status_code + json_field + anchored keyword, conjunctive): 0/6 confirm. The methodology-correction lesson is the load-bearing finding, captured as Methodology Insight #6 in [`SYNTHESIS-2026-05.md`](case-studies/commercial/SYNTHESIS-2026-05.md).
- **[Compute orchestration / training survey](case-studies/commercial/compute-orchestration-cloud-survey-2026-05.md)**, **118 unauthenticated exposures** across Apache Spark (85), Apache Airflow (29), Ray Dashboard (4), from 203 Shodan-seeded candidates. Highlights: **8 Airflow `/home`-bypass criticals** (anonymous public role enabled, `/login` still serves the login template, but `/home` returns the authenticated DAG dashboard) on GCP/AWS/DO/Timeweb customer hosts; **4 Ray Dashboard hosts with CVE-2023-48022 ShadowRay surface** (unauth job-submission RCE actively exploited since 2023); 71% population exposure on Spark Master / Worker / Application UIs (cluster topology + driver Environment-tab credential leak surface). Spark + Ray reproduce Tier-A "no auth concept"; Airflow's `/home` route surfaces a new methodology lesson, **entry-point-only fingerprints miss auth-bypass-via-misconfiguration findings whose entry-point looks login-gated** (Methodology Insight #8).

**Cross-tier auth-posture is now empirically clear:** infrastructure-for-engineers tier (vector DBs, inference servers, gateways, MCP, browser-agent) reproduces 97-100% unauth at population scale; applications-for-end-users tier (RAG framework, doccano labeling) reproduces ~99% auth-on. Same operators, different defaults; **the framework default is the deployment**.

---

## Mission

The AI/ML stack moved faster than its security model. Vector databases ship without auth by default. LLM gateways log every prompt to disk. Inference servers expose `/v1/models` to the internet. Fine-tuning dashboards proxy GPU compute to anyone who finds the URL. MCP servers wire shell, filesystem, and database tools to LLMs over unauthenticated HTTP.

This repository is a living catalogue of **fingerprints, queries, exposure patterns, and detection logic** for the infrastructure that runs modern AI, built so that defenders can find their own assets before adversaries do.

## Scope

| Category | Examples |
|----------|----------|
| **LLM Orchestration** | Flowise, Langflow, Dify, Open WebUI, LiteLLM, Ollama, n8n, SillyTavern, Clawdbot |
| **Vector Databases** | ChromaDB, Qdrant, Weaviate, Milvus, pgvector, Redis Search, ClickHouse, Cassandra |
| **Object Storage & Artifact Stores** | MinIO, Harbor, Docker Registry v2, where the models and vectors actually live |
| **Model Serving** | vLLM, Triton, TGI, llama.cpp, LM Studio, GPT4All, NVIDIA NIM, text-generation-webui, Kobold.cpp, SGLang |
| **Embedding Services** | HuggingFace TEI, infinity-embedding, SentenceTransformers server, documents → vectors over unauthenticated HTTP |
| **Training & Experiments** | MLflow, Kubeflow, Ray, ClearML, Argilla, Label Studio, Feast |
| **Data Pipeline Orchestration** | Apache Airflow, Prefect, Dagster, Argo Workflows, unauth Airflow = code execution via DAG trigger, secrets in Variables API |
| **AI Gateways & Observability** | LiteLLM Proxy, Portkey, Langfuse, Helicone, Phoenix/Arize |
| **Agent Frameworks** | SuperAGI, OpenDevin, MetaGPT, AutoGen, Clawdbot |
| **RAG Stacks & Self-Hosted AI Apps** | h2oGPT, Danswer/Onyx, Quivr, Khoj, RAGFlow, LibreChat |
| **Image Generation** | ComfyUI, Stable Diffusion, AUTOMATIC1111, InvokeAI, Fooocus |
| **Speech & Audio AI** | Whisper.cpp server, Coqui TTS, AllTalk TTS, LocalAI audio, OpenAI-compat `/v1/audio/transcriptions` |
| **Notebook & Dev Environments** | JupyterHub, VS Code Server (code-server), Jupyter AI, multi-user institutional deployments, full RCE class |
| **AI Code Assistants** | Tabby, Refact, self-hosted Sourcegraph Cody, server-based, expose codebase indexes and completion history |
| **Search & Data Infrastructure** | Elasticsearch, OpenSearch (with ELSER/kNN ML plugins), Typesense, Meilisearch, the corpus layer AI apps query |
| **MCP Servers** | Model Context Protocol exposed over HTTP/SSE, wires shell, filesystem, and database tools to LLMs |
| **Credential & Config Leaks** | `OPENAI_API_KEY` / `ANTHROPIC_API_KEY` / `GROQ_API_KEY` / `HF_TOKEN` exposure, `.env` files |
| **Backup & Snapshot Services** | Velero, restic REST server, Barman, Longhorn, model weights and training data in unprotected snapshots |
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
│   │   ├── US/                     # United States (11 case studies)
│   │   │   ├── IN-purdue-northwest.md # Purdue NW - account takeover, user-ID embedded sales models
│   │   │   └── NC-duke.md          # Duke - agent model + file inspection tools
│   │   └── international/          # All other countries (46 case studies, 28 countries)
│   │       ├── KR/                 # South Korea - POSTECH, SNU, Yonsei, INHA, Kyungpook
│   │       ├── TW/                 # Taiwan - TANet 18-node cluster, NTU, NCKU, FJU, NCU
│   │       ├── VN/                 # Vietnam - Hanoi, VNU HN, VNU HCMC
│   │       └── ...                 # 25 more countries: see index.md
│   ├── critical-infra/             # Critical infrastructure exposures
│   │   ├── US-GA-cartersville-city.md  # City of Cartersville - Windows, cloud proxy
│   │   └── US-TN-meriwether-lewis-ec.md  # Electric cooperative - 235B model
│   ├── k12/                        # K-12 school district exposures
│   │   └── US-NJ-hts-k12-dvrc.md  # NJ school district (DVRC) - 5 cloud proxies
│   ├── hts-k12-nj-open-webui.md   # (legacy path - see k12/)
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
- [Shodan Query Index](shodan/README.md), 15 categories + CVE cross-reference appendix
- [Common AI/LLM Ports Reference](reference/ports.md)
- [AI/ML Terminology Primer](reference/terminology.md)
- [Download the polished PDF reference (v2.1)](shodan/Shodan_AI_Reference.pdf)

**Active research:**
- **[2026-05 Cross-Survey Synthesis](case-studies/commercial/SYNTHESIS-2026-05.md)** ⭐, 15 platform classes, ~5,000 deployments surveyed across DO/Hetzner/Vultr; the auth-off-default thesis with positive controls (MinIO, Dify) and active-attack-progression evidence
- [Commercial AI Infrastructure Exposures Index](case-studies/commercial/index.md), 15 platform-class surveys + per-instance high-impact case studies
- [Ollama Enterprise Exposures, Case Study](case-studies/ollama-enterprise-exposures.md), 11 enterprise/critical-infra targets confirmed vulnerable (2026-05-01)
- [University AI Exposures](case-studies/universities/index.md), **57 case studies** across 29 countries; 10 account takeovers, 20+ cloud proxy nodes, organized by country (`KR/`, `US/`, `VN/`, ...)
  - Notable: **POSTECH synchrotron beamline** (`4gsr-beamline-ws`, PAL 4th-gen light source), 235B Qwen3 model + live account takeover
  - **Shiv Nadar University**, 3-node cluster, chest X-ray AI (`lungsvlm` / VinDr-CXR), abliterated models, 18 cloud subscriptions
  - **TANet Taiwan**, 18-node multi-institution cluster across NTU/NCCU/NTHU/FJU/NCKU, account takeover, 5G security research system prompt
  - **India NIB / BSNL National Backbone**, qwen2.5-coder:32b coding cluster on national telecom backbone infrastructure
  - **Purdue NW**, account takeover + user-ID embedded fine-tuned sales models (multi-tenant platform exposure)
- [K-12 Education, NJ DVRC](case-studies/k12/US-NJ-hts-k12-dvrc.md), Open WebUI bypass, 5 cloud proxy subscriptions, student data at risk
- [Critical Infrastructure, City of Cartersville](case-studies/critical-infra/US-GA-cartersville-city.md), local government, Windows, DeepSeek cloud proxy
- [Critical Infrastructure, Meriwether Lewis Electric](case-studies/critical-infra/US-TN-meriwether-lewis-ec.md), rural electric coop, 235B model, unauthenticated
- [Open WebUI Auth Bypass](tools/open-webui-ollama-bypass.md), UI auth on port 3000 does not protect Ollama port 11434
- [Cloud Proxy Quota Hijacking](tools/open-webui-cloud-proxy-hijack.md), operator API subscriptions drained via unauthenticated inference
- [Ollama Unauthenticated Model Injection](tools/ollama-model-injection.md), all versions, no patch
- [Ollama Connect Account Takeover](tools/ollama-connect-takeover.md), cloud subscription hijacking via leaked signin_url
- [HexStrike AI → RCE Chain](tools/hexstrike-ai-chain.md), model injection → shell execution via trust confusion

## NuClide Toolchain

The 2026-05 cross-survey was produced end-to-end by the NuClide tool stack, discovery → fingerprint → enumeration → findings ledger → compliance scoring → adversarial corpus generation. Each stage is its own focused tool; [VisorPlus](https://github.com/Nicholas-Kloster/VisorPlus) is the orchestrator that chains them.

| Stage | Tool | Repo | What it does |
|---|---|---|---|
| **Orchestrator** | VisorPlus | [Nicholas-Kloster/VisorPlus](https://github.com/Nicholas-Kloster/VisorPlus) | Single CLI that chains JAXEN → VisorSD → VisorCorpus → BARE → aimap into one workflow (`visorplus full <dork>`) |
| **Discovery (Shodan)** | VisorSD | [Nicholas-Kloster/VisorSD](https://github.com/Nicholas-Kloster/VisorSD) | ~20 hardcoded AI/LLM exposure dorks ranked by severity; `visorsd -org "Acme"` returns scored hits |
| **Discovery (Shodan harvest)** | JAXEN | [Nicholas-Kloster/JAXEN](https://github.com/Nicholas-Kloster/JAXEN) | Hunts a Shodan dork and harvests live hosts into `empire.db` |
| **Discovery (gov TLD)** | VisorGoose | [Nicholas-Kloster/VisorGoose](https://github.com/Nicholas-Kloster/VisorGoose) | Government-TLD AI discovery via CT logs + Shodan + DNS |
| **Discovery (graph)** | VisorGraph | [Nicholas-Kloster/VisorGraph](https://github.com/Nicholas-Kloster/VisorGraph) | Seed-polymorphic recon engine; input IP/CIDR/domain/ASN/cert-FP; output typed provenance graph with rule-based exposure classification |
| **Fingerprint + deep enum** | aimap | [Nicholas-Kloster/aimap](https://github.com/Nicholas-Kloster/aimap) | Fingerprints 69 AI/ML services + 36 dedicated deep enumerators (PII, unauth RCE, exposed creds, claimable admin states) |
| **Findings ledger** | VisorLog | [Nicholas-Kloster/VisorLog](https://github.com/Nicholas-Kloster/VisorLog) | ECS-normalized SQLite store with append-only lifecycle (`open → disclosed → acknowledged → remediated → verified`); ingests NDJSON from any of the above. The 746 findings (across 741 unique hosts, as of 2026-05-09) in the cross-survey ledger live in `data/nuclide.db` here |
| **Compliance scoring** | VisorScuba | [Nicholas-Kloster/VisorScuba](https://github.com/Nicholas-Kloster/VisorScuba) | OPA/Rego policies (CISA ScubaGear-inspired) → ScubaGear-style 0–10 compliance score per node against the NuClide AI Security Baseline |
| **Exploit ranking** | BARE | [Nicholas-Kloster/BARE](https://github.com/Nicholas-Kloster/BARE) | Semantic search of scanner findings against an embedded Metasploit corpus (3,904 modules); pipe nuclei/nmap/Shodan adapters in, get ranked exploit modules out, offline, no Python runtime |
| **Adversarial RAG/LLM corpus** | VisorCorpus | [Nicholas-Kloster/VisorCorpus](https://github.com/Nicholas-Kloster/VisorCorpus) | Generates structured adversarial test cases (prompt injection, kb_exfiltration, tenant_cross_leak, system_prompt, jailbreak, config_secrets) for downstream RAG/LLM red-team validation |
| **Agentic LLM benchmark** | VisorAgent | [Nicholas-Kloster/VisorAgent](https://github.com/Nicholas-Kloster/VisorAgent) | Delivers adversarial prompts through real tool-use paths (`web_fetch`, `doc_retrieve`, `code_exec`, `email_send`); pass/fail per signal |
| **Process-injection benchmark** | VisorHollow | [Nicholas-Kloster/VisorHollow](https://github.com/Nicholas-Kloster/VisorHollow) | Detection benchmark for process-injection techniques on Windows x64; 6-tier ladder coverage matrix |
| **Banner / aesthetics** | artisan | [Nicholas-Kloster/artisan](https://github.com/Nicholas-Kloster/artisan) | Go CLI: FIGlet banners + asciiart.eu gallery scraper for tooling output |

### How the tools chained for this survey

For each platform class in the 2026-05 cross-survey:

1. **`masscan`** scoped to the 28 cloud /16 ranges produced raw IP hits (one port per platform)
2. **Custom Python probes** (`/tmp/<platform>-probe.py`, 200-thread) fingerprinted each platform via its distinctive endpoint shape, `/v2/vectordb/collections/list` for Milvus, `/api/version` for Open WebUI / MLflow / Ray, `/v1/models` for vLLM, `/_stcore/host-config` for Streamlit, `/api/tags` for Ollama, etc.
3. **Schema/metadata enumeration** captured per-instance detail (collections, models, registered models, experiments, version, RBAC state), metadata only, no payload exfiltration where avoidable
4. **VisorLog NDJSON ingest** loaded confirmed findings into `data/nuclide.db` with severity tiering driven by content sensitivity
5. **VisorScuba** scored every node against the NuClide AI Security Baseline (Rego policies); HTML report at `data/scuba-report-2026-05-03.html`
6. **VisorCorpus** generated a 137-case adversarial corpus targeting the Class-A reseller-proxy + RAG-exfiltration threat classes; bundled at `data/visorcorpus-chromadb-rag-adversarial-2026-05.json` for affected operators to test their own defenses
7. **Cross-survey synthesis** (`SYNTHESIS-2026-05.md`) pulled all 15 platform writeups into the auth-on-default-vs-off pattern with positive/negative controls

The full `data/nuclide.db` SQLite ledger is committed to the repo. Anyone with the toolchain can run `visorlog --db data/nuclide.db query --severity critical` to triage from the ledger directly, or `visorscuba --db data/nuclide.db assess --json` to re-score against current OPA policies.

**Search across all queries:**
```bash
git clone https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT.git
cd AI-LLM-Infrastructure-OSINT
grep -r "qdrant" shodan/queries/
grep -rn " T1 " shodan/queries/    # all unauth-by-default queries
```

## Tier System

Every query in v2.x is tagged with an exposure tier:

- **T1**, Unauthenticated by default. A positive hit is typically a live, interactive target.
- **T2**, Requires misconfiguration or has known auth-bypass CVEs. One additional probe confirms exposure.
- **T3**, Recon / fingerprint only. Use for inventory and pivoting, not as an immediate finding.

See [shodan/README.md](shodan/README.md#how-to-read-the-tables) for the full legend.

## Active Disclosure

### tweet-optimize.com: 1.21M facial embeddings on unauth Milvus (2026-05-03)

- **Operator brand:** tweet-optimize.com / "Twitter Forecast" (legal entity per ToS), Danish registrant, Hetzner Helsinki origin
- **Exposure:** Milvus on `65.108.107.240:19530` and `:9091`, fully unauth; 897K + 313K facial embeddings (`onlyfans` + `psos` collections) with bbox + MongoDB references; functional doxing primitive against creators via `/v2/vectordb/entities/search`
- **Disclosed to:** Operator (via `/contact` form), Fenix International / OnlyFans (`privacy@onlyfans.com` + EU GDPR rep), Hetzner abuse, Finnish DPA (Tietosuojavaltuutettu), all 2026-05-03
- **Status:** Exposure remains live as of last re-probe; counts unchanged. See [`disclosure log`](case-studies/commercial/disclosure/tweet-optimize-2026-05-03-log.md).
- **Public evidence pack:** [evidence/tweet-optimize-2026-05-03/](evidence/tweet-optimize-2026-05-03/), 8 screenshots + 33 raw probe artifacts + SHA-256 manifest + Internet Archive Wayback snapshots

### MLflow CVE-2023-1177 actively-exploited pair (2026-05-04)

- **Affected:** `138.197.152.103` (MLflow 2.2.1) + `159.203.110.202` (MLflow 2.9.2), both DigitalOcean
- **Active exploitation observable:** attacker-injected experiments with `artifact_location: http:///?/../../../../../etc/` and `/root/.ssh/`; same attacker UUIDs span both hosts (population-scale CVE-2023-1177 sweep)
- **Attack progressing:** 138.197.152.103 grew from 10 → 20 attacker-experiments in ~24h between probes
- **Disclosure:** drafted to DigitalOcean abuse channel; ready to send

### Ollama Unauthenticated Model Injection: coordinated disclosure initiated 2026-05-01

- **Affected:** All Ollama versions (no authentication on `/api/create` in any release)
- **CVE-2025-63389**, filed 2025-12-18, scoped ≤v0.13.5. Scope is incorrect: confirmed live on v0.13.5 → v0.22.0. `first_patched_version: null`.
- **Scale:** 227,715 exposed instances on Shodan as of 2026-05-01
- **Enterprise targets confirmed:** US electric utility co-op [CISA notified, identity withheld], Oracle Corporation infra, Azure IBM Granite RAG pipelines, GCP autonomous agent deployment, OVH cybersecurity product company, AWS managed instances
- **Public disclosure:** 2026-07-30 (90-day window)
- **Contact:** nicholas@nuclide-research.com

Secondary findings in coordinated disclosure:
- SSRF via `/api/pull` (CVE-2026-5530), OOB DNS + internal port detection
- Ollama Connect account takeover, cloud subscription hijacking via leaked `signin_url`
- HexStrike AI RCE chain, model injection → trust confusion → Flask `/api/command` shell exec

---

## Use with Claude Code

This repo is designed to work as a live context source for Claude Code. Drop the following prompt into any Claude Code session to turn it into a guided AI infrastructure OSINT analyst, it'll use the queries, findings, and tooling here as its working reference.

**Copy-paste starter prompt:**

```
You are an AI/LLM infrastructure security analyst. I've cloned the AI-LLM-Infrastructure-OSINT
repository at ~/AI-LLM-Infrastructure-OSINT/. Use it as your primary reference.

Read the following files to orient yourself:
- README.md - repo overview and active disclosure status
- shodan/queries/ - query catalog by category
- tools/ollama-model-injection.md - active vulnerability (all Ollama versions)
- case-studies/ollama-enterprise-exposures.md - confirmed enterprise targets

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

PRs welcome, see [CONTRIBUTING.md](CONTRIBUTING.md). The bar is:
- Queries should be **verifiable** (you've seen them return real results).
- Tag every new query with an exposure tier (T1/T2/T3).
- Add a `Notes` column when the query reveals something specific (auth state, version disclosure, snapshot exposure).
- New categories should map to a real, deployed-in-the-wild AI/ML platform.

## Disclaimer

Read [DISCLAIMER.md](DISCLAIMER.md). Short version: this material is for **authorized security research, defensive asset discovery, and threat hunting only**. Touching infrastructure you don't own or have explicit permission to test is illegal in most jurisdictions. Don't.

## About

Maintained by **[Nicholas Michael Kloster](https://github.com/Nicholas-Kloster)** as part of [**NuClide**](https://nuclide-research.com), independent ICS/OT and AI infrastructure security research.

CISA disclosures: [CVE-2025-4364](https://nvd.nist.gov/vuln/detail/CVE-2025-4364) · [ICSA-25-140-11](https://www.cisa.gov/news-events/ics-advisories/icsa-25-140-11)

Companion tooling: see the **[NuClide Toolchain](#nuclide-toolchain)** section above, VisorPlus orchestrator + 12 focused tools covering discovery, fingerprinting, deep enumeration, findings ledger, compliance scoring, and adversarial corpus generation.
