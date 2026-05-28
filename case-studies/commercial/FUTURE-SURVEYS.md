---
type: operational
---

# Future Surveys: AI/ML Infrastructure Categories Not Yet Covered

_NuClide Research · 2026-05-04_
_Companion to: [`SYNTHESIS-2026-05.md`](SYNTHESIS-2026-05.md)_

---

The 2026-05 survey series covers 19+ platform classes. Several adjacent categories remain unsurveyed and are catalogued here as a roadmap. Each entry includes:

- **Port(s)** to masscan
- **Fingerprint** (the canonical signature for the probe to use)
- **Auth posture in framework default** (Tier-A no-auth-concept, Tier-A* auth-optional-off, Tier-B setup-wizard, Tier-C auth-on-default)
- **Risk class** if exposed
- **Status** (planned / partial / not-yet)

Anyone running NuClide's tier-2 cloud range list (`/tmp/tier2-all-ranges.txt`, Scaleway 7, OVH 33, Linode 36 = 3.55M IPs) can pick a category and run the survey using the same masscan-then-probe pattern documented in the existing case studies.

---

## Priority gaps: still open as of 2026-05-14

Cross-referenced against the 27-category `shodan/queries/` index and the completed case-study set. These are the categories with the most untouched surface. Pick from here for a fresh survey:

| Gap | Category | Why it's the gap | Tooling state |
|---|---|---|---|
| **K8s-native workflow orchestration** (NEW — category 29) | **Argo Workflows** (port 2746) | **IN PROGRESS 2026-05-27** — 6-agent parallel OSINT complete. ~3,000 unauth instances confirmed (E.V.A 2024). CRITICAL surface: unauth container exec via `POST /api/v1/workflows/`. CVE-2026-28229 (`Bearer nothing` template exfil) live on most deployed versions. Cluster-takeover chain when etcd co-deployed. aimap fingerprint: not yet built. Dorks, verification primitive, shadow sweep, and full intelligence brief in: `case-studies/commercial/argo-workflows-osint-pre-assessment-2026-05-27.md` + `shodan/queries/29-workflow-orchestration.md`. | **No aimap fingerprint yet** — build before JAXEN run |
| **Experiment tracking** (category 04, registry half) | W&B self-hosted, ClearML, Comet ML | **DONE 2026-05-26** (cat-04 stragglers) — ClearML auth-on-default confirmed (81/81); ransomed Elasticsearch at 37.230.233.135; 26/81 version disclosure via server.info. BentoML: narrative.io AWS infra leak. Insight #63 codified. | aimap fingerprints exist; enumPrefect deep enumerator still missing |
| **Code assistants** (category 09) | Tabby, Sourcegraph/Cody, OpenDevin/Devon, Continue.dev | **DONE 2026-05-26** — 52 unauth OpenHands, 26-host WhatsApp bot template, Fluid Attacks home-dir leak, HKUST/HKGAI. Case study: `openhands-code-assistant-survey-cat09-2026-05-26.md`. Tabby ML still Shodan-dark (needs masscan). | aimap fingerprints: OpenHands/Sourcegraph/Sourcebot/Sweep/Tabnine/Dyad/bolt.diy all exist |
| **Specialty data layers** (no query file) | ClickHouse, Cassandra/ScyllaDB, Apache Pinot, DuckDB-HTTP | Runbook built (`data/specialty-data-layers-discovery-runbook.sh`) and waiting; never executed | runbook ready, aimap ≥ v1.5.0 |
| **Vector-DB stragglers** (category 02) | pgvector, Redis Stack (vector), Vespa, Apache Solr, LanceDB | Qdrant/Chroma/Milvus/Weaviate done; these four never run | partial aimap coverage |
| **Agent-framework stragglers** (category 06) | CrewAI Studio, BabyAGI/SuperAGI, Goose, Agno, GPT Researcher, AgentGPT, Devika | **DONE 2026-05-26** — Agno auth-off-default (3 confirmed: AIRIAD Risk Advisor, Collision AgentOS+Walmart Temporal, agno-playground); GPT Researcher 14/21 unauth; AgentGPT 3 broken-localhost-OAuth; CrewAI Shodan-dark; SuperAGI all-SaaS; Devika defunct; BabyAGI/Goose CLI-only. Insight #64 codified. aimap v1.9.32-33 shipped. | aimap v1.9.32 fingerprints shipped |
| **Specialty domains** (medical leg) | NVIDIA Clara, MONAI, Orthanc/DICOM, dcm4che, NIM | **DONE 2026-05-15** (Survey 28) — 39 Orthanc unauth DICOM SCPs found; Clara/MONAI/NIM negative results on tier-2 cloud. | aimap v1.9.4 fingerprints shipped |
| **Specialty domains** (robotics leg) | ROS robotics (11311/9090), Jetson edge | Genuinely unmapped — highest-novelty, physical-impact tier for ROS | none |
| **Compute-orch leftovers** (category 04) | Dask (8787), Prefect (4200), Temporal (7233/8080), BentoML (3000) | **DONE 2026-05-26** — Prefect auth-off-default (9/15 unauth; Italian LLM procurement + energy grid + MLS pipelines exposed); Dask 6 unauth university/cloud dashboards (Cambridge, UCB, UCSB, DigitalOcean active). Temporal not scanned (Shodan-dark at 7233). Case study: `prefect-dask-clearml-cat04-stragglers-2026-05-26.md`. | aimap fingerprints: all exist; enumPrefect deep enumerator gap |
| **Embeddings — masscan re-run** (category 27) | TEI, infinity-embedding (7997), llama.cpp `--embedding` | Survey ran but Shodan-dark: TEI/infinity return JSON-only roots Shodan can't index, Shodan pool gave ~1% live rate. Needs a **masscan-seeded** pass on 7997/8080 instead of Shodan-seeded | survey done Shodan-blind; aimap fingerprints exist |

Detailed port/fingerprint/risk for each is in the per-category sections below.

---

## Compute orchestration / training tier

Most are Tier-A "no auth concept" on the dashboard endpoint. Auth is bolted on by surrounding infra (K8s ingress + auth proxy), not the framework itself.

| Platform | Port | Fingerprint | Tier | Risk | Status |
|---|---|---|---|---|---|
| **Ray Dashboard** | 8265 | GET `/` returns Ray UI HTML; GET `/api/jobs` lists jobs | A | CVE-2023-48022 ShadowRay actively exploited (job-submission RCE); job logs leak | **DONE 2026-05-06**, see [`compute-orchestration-cloud-survey-2026-05.md`](compute-orchestration-cloud-survey-2026-05.md) (4 confirmed unauth on Shodan-seeded sample of 26; 16 ports-open-no-match likely Ray Serve, deferred) |
| **Dask Dashboard** | 8787 | GET `/status` returns Bokeh-rendered Dask page | A | Cluster topology + worker info disclosure; expensive ops triggerable | not-yet |
| **Apache Spark UI** | 4040, 8080 | GET `/` returns Spark Master / Application UI | A | Job logs + driver state + sometimes credentials in env | **DONE 2026-05-06**, see [`compute-orchestration-cloud-survey-2026-05.md`](compute-orchestration-cloud-survey-2026-05.md) (85 confirmed unauth on Shodan-seeded sample of 120 across US/CN/DE/FR; ~71% exposure rate) |
| **Apache Airflow** | 8080 | GET `/login` returns Airflow login page; **`/home` discloses dashboard if AnonymousUser public role enabled** | A* (auth optional, off-by-default in older versions) | DAG-run history, sometimes plaintext credentials in connections | **DONE 2026-05-06**, see [`compute-orchestration-cloud-survey-2026-05.md`](compute-orchestration-cloud-survey-2026-05.md) (8 confirmed unauth-via-/home + ~30 login-gated of 36 confirmed Airflow on Shodan-seeded sample of 57) |
| **Prefect** | 4200 | GET `/api/health` returns `{"status":"healthy"}` | A* | Flow runs + state | not-yet |
| **Temporal** | 7233 (gRPC), 8080 (web UI) | GET `/api/v1/cluster-info` | A* | Workflow history | not-yet |
| **Kubeflow / KServe** | varies (K8s ingress) | `/v1/models` OpenAPI | varies | Model serving + pipeline metadata | not-yet, K8s ingress profile, separate from cheap-VPS surface |
| **BentoML** | 3000 | GET `/` returns BentoML service page; `/docs` Swagger | A* | Model serving + sometimes file upload | not-yet |

---

## Embeddings infrastructure

| Platform | Port | Fingerprint | Tier | Risk | Status |
|---|---|---|---|---|---|
| **TEI (HuggingFace Text Embeddings Inference)** | 80, 3000, 8080 | GET `/info` returns `{"model_id":"...","max_concurrent_requests":..., "model_pipeline_tag":"feature-extraction"}` | A | Compute theft; model fingerprinting | **PARTIAL 2026-05**, see [`embedding-services-cloud-survey-2026-05.md`](embedding-services-cloud-survey-2026-05.md) — confirmed **Shodan-dark** (JSON-only root, not crawler-indexed); 0 live on Shodan-seeded pool. Needs masscan-seeded re-run |
| **infinity-embedding** (michaelfeil) | 7997 | GET `/openapi.json` body contains `Infinity Emb` | A | Compute theft | **PARTIAL 2026-05**, embedding survey — port 7997 confirmed deployed at ~100-host signal, but Shodan-dark; masscan-seeded probe found 0 (hosts moved off default port / non-HTTP). Re-run candidate |
| **llama.cpp HTTP server** | 8080 | GET `/health` returns `{"status":"ok"}`; GET `/props` returns model props | A | Compute theft, prompt injection | **PARTIAL 2026-05**, embedding survey covered `--embedding` mode; `/props` deep-enum on full LLM-server mode still open |

---

## Specialty vector DBs

| Platform | Port | Fingerprint | Tier | Risk | Status |
|---|---|---|---|---|---|
| **Weaviate** | 8080 | GET `/v1/meta` returns Weaviate version JSON; GET `/v1/schema` lists classes | A* (anonymous-access on by default in `auth.anonymous_access.enabled=true`) | Same as Qdrant, vector data + schema disclosure | not-yet, port 8080 conflicts heavily |
| **pgvector** (PostgreSQL extension) | 5432 | TCP banner + `SELECT pgvector_version();` | A* (Postgres auth, depends on operator) | Vector data via SQL injection / weak creds | not-yet, needs auth-bypass enumeration |
| **Redis Stack** (with vector search) | 6379 | TCP `*1\r\n$4\r\nINFO\r\n` returns Redis info | A* (default ALLOW-ANY in dev configs) | Vector + cache + sometimes sessions | not-yet |
| **LanceDB** | various | GET `/api/v1/database/list` | A | RAG store | not-yet |
| **Vespa** | 8080 | GET `/state/v1` returns Vespa health JSON | A | Search + vector | not-yet |
| **Typesense** | 8108 | GET `/health` returns `{"ok":true}`; X-TYPESENSE-API-KEY header for auth | A* | Document index + facets | not-yet |
| **Meilisearch** | 7700 | GET `/health` returns `{"status":"available"}` | A* (master-key auth optional) | Document index | not-yet |
| **Apache Solr** | 8983 | GET `/solr/admin/info/system` | A* | Document index + sometimes RCE via velocity templates | not-yet |

---

## LLM observability / tracing

| Platform | Port | Fingerprint | Tier | Risk | Status |
|---|---|---|---|---|---|
| **Langfuse** | 3000 | GET `/api/public/health` returns Langfuse health JSON | C (auth-on-default) | LLM trace history if signup-open | **PARTIAL 2026-05-06**, single-host case study via cross-survey-correlation methodology ([`langfuse-cross-survey-2026-05-06.md`](langfuse-cross-survey-2026-05-06.md)). 1 confirmed hit (operator shifted to port 3001; 4-platform AI-stack catastrophe at `pharos.unistarthubs.gr`). Full population survey (Shodan dork `"Langfuse" port:3000` ≈ 1,131 hits) **deferred until Shodan API restored** |
| **Phoenix (Arize)** | 6006 | GET `/v1/traces` OTLP JSON | A | LLM call traces, sometimes PII in prompts | **DONE 2026-05-04**, see [`observability-cloud-survey-2026-05.md`](observability-cloud-survey-2026-05.md) (6 confirmed Phoenix + 3 TensorBoard, all unauth, active SDXL distillation training visible) |
| **Helicone** | varies | gateway pattern, proxy logs | A* | LLM call history | not-yet |
| **TruLens self-hosted** | varies | dashboard fingerprint | A* | Eval traces | not-yet |

---

## Image generation / vision (beyond port 7860 surveyed)

| Platform | Port | Fingerprint | Tier | Risk | Status |
|---|---|---|---|---|---|
| **ComfyUI** | 8188 | GET `/system_stats` returns GPU info; GET `/queue` lists running jobs | A | Compute theft + workflow exfil + GPU info | **DONE 2026-05-04**, see [`comfyui-cloud-survey-2026-05.md`](comfyui-cloud-survey-2026-05.md) (6 confirmed, 100% unauth, 385 GB VRAM exposed including RTX PRO 6000 Blackwell) |
| **Roboflow self-hosted** | varies | API key required | C | Custom model serving | not-yet |
| **YOLOv8 / MMDetection inference servers** | varies (often 8000) | Custom HTTP API | A* | Compute theft, prompt injection (multimodal) | partial, some seen via Triton survey |

---

## Speech & Audio AI (survey 17: IN PROGRESS 2026-05-08)

Survey-17 query catalog: [`shodan/queries/17-voice-audio-ai.md`](../../shodan/queries/17-voice-audio-ai.md)
Discovery runbook: [`data/voice-audio-ai-discovery-runbook.sh`](../../data/voice-audio-ai-discovery-runbook.sh)
aimap fingerprints added (10 new, count went 56 → 66): Whisper ASR, Coqui XTTS, Piper TTS, RVC Voice Cloning WebUI, OpenVoice, ChatTTS, F5-TTS, Pipecat Voice Agent, Vocode Voice Agent, LiveKit Agents.

| Platform | Port | Fingerprint | Tier | Risk | Status |
|---|---|---|---|---|---|
| **Whisper ASR** family | 9000, 8080, 7860, 8000 | `/asr` or `/inference` or `/v1/audio/transcriptions` | A | Free transcription compute theft; PHI/PII in audio captured by hospital deployments | aimap fingerprint added; population survey **pending Shodan IP harvest** |
| **Coqui XTTS server** | 8020, 5002 | GET `/api/tts/speakers` returns speaker list | A | Compute theft (voice cloning), trademark/voice misuse | aimap fingerprint added; survey pending |
| **Piper TTS** HTTP wrapper | 5000, 8080, 10200 | GET `/` body contains `piper` + `tts` | A | Edge-deployed; compute theft | aimap fingerprint added; survey pending |
| **RVC / GPT-SoVITS / Applio** voice cloning | 7865, 7860, 7897 | GET `/` body contains `Retrieval-based-Voice-Conversion` / `GPT-SoVITS` / `Applio` | A | **Fraud-relevant — voice cloning Gradio UIs**; trademark abuse + deepfake-call enablement | aimap fingerprint added (high); survey pending |
| **OpenVoice (MyShell.ai)** | 7860, 8000 | GET `/` body contains `OpenVoice` + `myshell` | A | Multi-language voice cloning compute theft | aimap fingerprint added (high); survey pending |
| **ChatTTS (2noise)** | 7860, 8000, 9966 | GET `/` body contains `ChatTTS` + `2noise` | A | Conversational TTS compute theft | aimap fingerprint added; survey pending |
| **F5-TTS / E2-TTS** | 7860, 8000 | GET `/` body contains `F5-TTS` or `swivid/f5-tts` | A | Voice-cloning compute theft | aimap fingerprint added; survey pending |
| **Pipecat (Daily.co)** | 7860, 8000, 8080 | GET `/` body contains `pipecat` | A* | **Real-time voice-agent abuse** — outbound call automation if integrated with Twilio/Daily | aimap fingerprint added (high); survey pending |
| **Vocode** | 8000, 3000, 7860 | GET `/` body contains `vocode` + `transcriber` | A* | Same as Pipecat | aimap fingerprint added (high); survey pending |
| **LiveKit Agents** | 7880, 8080, 3000 | GET `/` body contains `livekit-agents` or `livekit-server` | A* | Same | aimap fingerprint added; survey pending |
| **Mozilla TTS / Coqui TTS legacy** | 5002 | GET `/api/tts` | A | Same | covered under Coqui XTTS fingerprint (alt port) |
| **Bark / MusicGen Gradio UIs** | 7860 | GET `/` returns Gradio UI | A | Compute theft | covered by Gradio + body_contains discriminator queries in 17-voice-audio-ai.md |
| **pyAnnote diarization** | varies | Custom HTTP API | A | Speaker-ID compute theft | not-yet (no canonical HTTP server pattern) |

---

## ML lifecycle / model registries

| Platform | Port | Fingerprint | Tier | Risk | Status |
|---|---|---|---|---|---|
| **W&B self-hosted** | 8080, 443 | GET `/api/health` returns `{"version":"..."}` | C (auth-on-default) | Experiment data if signup-open | not-yet |
| **ClearML server** | 8080, 8081, 8008 | GET `/version` returns ClearML version | A* | Experiment data | not-yet |
| **Comet ML self-hosted** | varies | API token required | C | Experiment data | not-yet |
| **Neptune.ai** | varies | API token required | C | Experiment data | not-yet, managed-mostly |
| **DVC remote storage** | S3-compat | bucket-policy depends on operator | varies | Model artifacts, training data | partial, covered by MinIO survey |

---

## Agent platforms (newer / autonomy)

| Platform | Port | Fingerprint | Tier | Risk | Status |
|---|---|---|---|---|---|
| **AutoGen Studio** | 8081 | GET `/` returns AutoGen Studio UI; GET `/api/agents` | A* | Agent definitions + sometimes credentials in tools | **DONE 2026-05-14**, see [`autogen-studio-survey-2026-05-14.md`](autogen-studio-survey-2026-05-14.md) (9 confirmed, 100% unauth; `/api/teams` leaking agent defs + tool creds on 7/9; produced Insight #21 port-first discovery) |
| **CrewAI Studio** | varies | dashboard fingerprint | A* | Agent definitions | not-yet |
| **LangGraph servers** | 8000 (uvicorn) | `server: uvicorn` + JSON body contains "langgraph" | A* | Financial workflows, PII scraper, conversation history (user_conversations Qdrant) | **DONE 2026-05-25**, see [`langgraph-server-survey-2026-05-25.md`](langgraph-server-survey-2026-05-25.md) (16 confirmed, 100% unauth; 7 stacked-exposure hosts; 4 templates; Insight #56) |
| **BabyAGI / SuperAGI** | varies | dashboard fingerprint | A* | Agent state, sometimes API keys | not-yet |
| **Goose** (Block) | varies | Custom config endpoint; `goose-` HTTP signatures | A* | Agent definitions, sometimes embedded credentials in extensions | not-yet |
| **AutoGPT-derivative server modes** | varies | Dashboard or `/api/agent/*` routes | A* | Agent state, embedded keys | not-yet |

---

## Specialty data layers (often AI-adjacent)

| Platform | Port | Fingerprint | Tier | Risk | Status |
|---|---|---|---|---|---|
| **ClickHouse** | 8123 (HTTP), 9000 (TCP) | GET `/?query=SELECT+1` returns `1`; HTTP banner `ClickHouse-` | A* | OLAP query access, sometimes including AI training datasets | not-yet, partial signal during chroma probe (port 9000 collision) |
| **DuckDB HTTP server** | varies | Custom HTTP API | A* | Embedded analytics queries | not-yet |
| **Cassandra / ScyllaDB** | 9042 (CQL native), 7000 (gossip) | TCP banner + `SELECT release_version FROM system.local` | A* | NoSQL data + sometimes AI feature stores | not-yet |
| **Apache Pinot** | 9000 (controller), 8000 | GET `/cluster/info` | A* | Real-time analytics | not-yet, port 9000 collision with whisper |

---

## Dev-tooling AI / coding agents

| Platform | Port | Fingerprint | Tier | Risk | Status |
|---|---|---|---|---|---|
| **Continue.dev servers** | varies | Custom config endpoint | A* | LLM proxy abuse | not-yet |
| **Tabby self-hosted** | 8080 | GET `/` returns Tabby UI; GET `/v1beta/health` | A* | Code-completion compute theft | not-yet |
| **Sourcegraph self-hosted (Cody backend)** | 7080, 3080 | GET `/.api/graphql` returns Sourcegraph schema; Cody integration via HTTP+SSE | C | Code-context exfil, sometimes private-repo access via Cody session tokens | not-yet, passing mentions in repo |
| **OpenDevin / Devon agent backends** | 3000, 8000 | GET `/` returns OpenDevin UI; `/api/options/models` | A* | Autonomous-agent control, sandbox escape if Docker-on-host | not-yet |
| **Devstral self-hosted** | varies | Custom HTTP API | A* | Code-completion compute theft | not-yet |
| **Aider** | typically not server-mode | n/a | n/a | n/a | not-applicable (CLI-only) |

---

## Specialty domains

| Platform | Port | Fingerprint | Tier | Risk | Status |
|---|---|---|---|---|---|
| **NVIDIA Clara** (medical AI) | varies | Triton-class APIs | A* | Medical-data compute theft | **DONE-NEGATIVE 2026-05-15**, see [`medical-edge-ai-survey-2026-05-15.md`](medical-edge-ai-survey-2026-05-15.md). No Clara on tier-2 cloud; Clara is K8s-bound, on-prem, or in HIPAA-specialized hosting. Negative result confirms category-class tenancy. |
| **MONAI Deploy** / Label | 8000 | `/info/` JSON with `trainers`+`strategies`+`scoring`+`datastore` | A* | Medical-imaging label/model data | **DONE-NEGATIVE 2026-05-15** — aimap fingerprint added (v1.9.4); zero confirmed on tier-2 cloud. Same on-prem tenancy as Clara. |
| **Orthanc DICOM** | 4242/8042/8043/11112 | DICOM A-ASSOCIATE-AC PDU with "ORTHANC" AE | A* (DICOM TCP unauth, HTTP REST auth-on) | PHI via C-FIND/C-MOVE/C-STORE | **DONE 2026-05-15** — 39 confirmed unauth DICOM SCPs (post 2-pass honeypot filter), 11 named operators. Produced [Insight #22](../../methodology/insight-22-protocol-strict-handshakes-against-multi-protocol-honeypots.md). |
| **dcm4che / dcm4chee-arc** | 8080/8443 | `/dcm4chee-arc/aets` array | C (Keycloak-fronted) | Same as Orthanc | aimap fingerprint added; zero confirmed on tier-2 (Keycloak-fronted = real deployments behind enterprise IAM). |
| **DICOMweb (QIDO-RS)** | 8080/8042/443 | `/studies` array + DICOM tag `0020000D` | A* | PHI | aimap fingerprint added; zero confirmed on tier-2. |
| **NVIDIA NIM** | 8000 | `/v1/metadata` with `modelInfo` array | A* | Paid quota theft + model gating bypass | aimap fingerprint added; zero confirmed on tier-2 (NIM is GPU-bound — runs on H100/A100 hosting, not commodity cloud). |
| **ROS interfaces** | 11311 (master), 9090 (rosbridge) | XML-RPC banner | A | Robot fleet control | not-yet |
| **TensorRT inference servers** | varies | Custom HTTP API | A* | Compute theft | not-yet, partial via Triton |
| **Jetson endpoints** | varies | Custom edge-AI protocols | A | Compute / sensor theft | not-yet |

---

## MCP (Model Context Protocol) servers

The newest exposure surface in the AI stack. MCP was designed for stdio (in-process) transport but the ecosystem pushed HTTP/SSE for remote access. Operators wiring filesystem, shell, database, and cloud-API tools into MCP servers and exposing them without auth replays the unauthenticated-RPC failure pattern at the protocol layer.

Existing scaffolding: [`shodan/queries/10-mcp-servers.md`](../../shodan/queries/10-mcp-servers.md), 8 fingerprint queries already documented. n8n cross-reference (`n8n-cloud-survey-2026-05.md`) counted ~400 instances exposing MCP endpoints, but no dedicated population-level survey yet.

| Platform | Port | Fingerprint | Tier | Risk | Status |
|---|---|---|---|---|---|
| **MCP HTTP+SSE servers** (generic) | 3000, 8000, 8080, 8888 | JSON-RPC `initialize` handshake; `tools/list` enumerates exposed tools | A* (auth-optional, off-by-default in most templates) | Tool-surface exfil, credential leak in tool definitions, sometimes shell/filesystem/db/cloud-API access | **DONE 2026-05-04**, see [`mcp-cloud-survey-2026-05.md`](mcp-cloud-survey-2026-05.md) (95 confirmed cross-cloud, 28 with exposed tools incl. full Gmail mailbox MCP, Alcy CRM CRUD, hindsight-mcp v3.1.1 with 29 memory tools, 3× Casdoor IAM CRUD, rmcp Elasticsearch proxy) |
| **FastMCP** (Python framework) | 8000 | `"FastMCP" "uvicorn"` Shodan | A* | Same | not-yet |
| **mcp-proxy** (stdio-to-HTTP bridge) | 8080 | `"mcp-proxy"` | A | Bridges local stdio MCP to HTTP, expanding exposure | not-yet |
| **HexStrike AI** (offensive MCP) | 8888 (Flask), 11434 (Ollama) | `"hexstrike"` HTML / model name | A | 47 MCP tools wiring 150+ security tools to LLMs | partial, see [`shodan/queries/10-mcp-servers.md`](../../shodan/queries/10-mcp-servers.md) |
| **Cloudflare Workers MCP** | 443 | `*.workers.dev` SSE endpoints | varies | Per-Worker auth posture | not-yet, cert-transparency enumeration vector |

---

## LLM gateways / OpenAI-compat proxies

Mirror the vLLM-survey reseller-proxy finding ([`vllm-cloud-survey-2026-05.md`](vllm-cloud-survey-2026-05.md) documented 10 commercial-API reseller proxies burning operator credit). Different operator tier, gateway products run alongside or in front of upstream LLM providers, exposing provider keys + quota.

| Platform | Port | Fingerprint | Tier | Risk | Status |
|---|---|---|---|---|---|
| **LiteLLM Proxy** | 4000 | GET `/health/liveliness`; `litellm:` Prometheus prefix | A* | Provider key leak, quota theft, OpenAI-compat reseller pattern | **DONE 2026-05-04**, see [`llm-gateways-cloud-survey-2026-05.md`](llm-gateways-cloud-survey-2026-05.md) (1,899 cross-cloud confirmed, 1,857 burnable unauth, including 2 Anthropic-key-functional hosts) |
| **LocalAI** | 8080 | GET `/readyz` returns `OK`; `/v1/models` OpenAI-compat | A* | Self-host LLM gateway, model-list enumeration | **DONE 2026-05-04**, folded into LLM Gateways survey above |
| **Text Generation WebUI / oobabooga** | 5000, 7860 | GET `/api/v1/model` returns model name; Gradio/FastAPI dual-stack | A* | Self-host inference, gradio surface | **DONE 2026-05-04**, folded into LLM Gateways survey |
| **LM Studio server mode** | 1234 (default), varies | GET `/v1/models` OpenAI-compat | A | Compute theft + model-list | **DONE 2026-05-04**, 318 confirmed (LM Studio survey leg of LLM Gateways) |
| **Jan AI server mode** | 1337 (default) | GET `/v1/models` OpenAI-compat; Jan-specific model paths | A | Same | **DONE 2026-05-04**, 126 confirmed (Jan AI / Cortex leg of LLM Gateways) |
| **OneAPI / NewAPI** | 3000 | OpenAI-compat gateway with admin UI | A* | Provider keys, quota theft | **DONE 2026-05-04**, folded into LLM Gateways survey |

---

## RAG framework servers

The pipeline above the vector DBs. RAG framework servers store embedded prompts, retrieval logic, and the bridge between document corpora and LLM calls. Exposing the framework, even with the underlying vector DB locked down, leaks prompt structure, system prompts, and operator data-flow.

| Platform | Port | Fingerprint | Tier | Risk | Status |
|---|---|---|---|---|---|
| **LlamaIndex servers** | 8000, 80 | GET `/api/health`; `llama_index` in OpenAPI | A* | Prompt + retrieval logic exfil | partial, passing references in repo, no survey |
| **Haystack** (deepset) | 8000 | GET `/initialized` returns `{"initialized":true}`; FastAPI surface | A* | Pipeline definitions, embedded prompts | partial, passing references |
| **LightRAG** | 9621 (default), varies | GET `/health`; LightRAG-specific endpoints | A | RAG store + retrieval surface | not-yet, **secondary priority after MCP** |
| **Microsoft GraphRAG** | varies | Custom HTTP API | A* | Knowledge graph + embedded prompts | not-yet |
| **AnythingLLM** | 3001 | GET `/api/ping` returns `pong` | A* | RAG admin + sometimes embedded creds | not-yet, supported in `aiapp-probe.py` |
| **RAGFlow** | 9380 | GET `/v1/health`; FastAPI | A* | Document pipeline | not-yet, supported in `aiapp-probe.py` |
| **PrivateGPT / LocalGPT** | 8001, 8000 | GET `/health` | A* | Self-host RAG | not-yet |

---

## AI safety evaluation / red-team self-hosted

Their finding-corpus may itself be sensitive when exposed. Adversarial prompt libraries, evaluator outputs, and red-team test results often contain proprietary attack vectors that operators don't want public.

| Platform | Port | Fingerprint | Tier | Risk | Status |
|---|---|---|---|---|---|
| **Garak** (NVIDIA adversarial harness) | varies | CLI-mode primary; some web UIs | A* | Adversarial probe library, eval results | **fingerprint added to aimap 2026-05-05** (`/api/v1/garak/version` + `json_field: garak_version`); **0 confirmed at population scale on tier-2 cloud sample**; CLI deployment dominates |
| **Promptfoo evaluators** | 15500 (default) | GET `/api/health`; promptfoo-specific endpoints | A* | Eval-run history, model-comparison data | not-yet |
| **Patronus AI** (managed-mostly) | varies | API token required | C | Eval artifacts | not-yet |
| **AILuminate** (MLCommons) | varies | Custom | varies | Benchmark data | not-yet, limited self-host |
| **DeepEval / Confident AI** | varies | Custom HTTP API | A* | Eval runs | not-yet |

---

## Browser automation / agent backends

Headless-Chrome endpoints used by agent stacks. Misconfigured ones offer remote browser control as a service, attackers can drive scraping, credential harvesting, or cloud-resource abuse using the operator's compute and IP reputation.

| Platform | Port | Fingerprint | Tier | Risk | Status |
|---|---|---|---|---|---|
| **Browserless** | 3000, 8000 | GET `/json/version` returns Chrome DevTools Protocol info | A | Remote browser control, session/cookie exfil if shared, scraping abuse | **DONE 2026-05-14**, see [`browser-automation-backend-survey-2026-05-14.md`](browser-automation-backend-survey-2026-05-14.md) (374 confirmed, v1 Docker monoculture) |
| **Playwright server** | 3000, 8931 (MCP) | GET `/json/protocol` returns CDP | A | Same | **DONE 2026-05-14**, folded into browser-automation backend survey |
| **Skyvern** | 8000 | GET `/api/v1/health`; Skyvern-specific endpoints | A* | Browser-AI agent control, sometimes credentials in workflow definitions | not-yet |
| **Puppeteer / CDP endpoints** | 9222 (CDP default) | GET `/json/version` | A | Direct CDP access, authenticated-session exfil | **DONE 2026-05-14**, see [`cdp-browser-control-survey-2026-05-14.md`](cdp-browser-control-survey-2026-05-14.md) (6 real of 1.5k candidates; 3 critical incl. live OnlyFans + Ticketmaster sessions; aimap v1.9.2 anti-detect CDP enumerator added) |
| **Selenium Grid** | 4444 | GET `/wd/hub/status` returns Selenium status | A | Browser fleet abuse | **DONE 2026-05-14**, folded into browser-automation backend survey (1.6k grids, H4Y operator) |
| **Splash** | 8050 | GET `/_debug` returns Splash debug page | A | Render-service abuse, SSRF | **DONE 2026-05-14**, folded into browser-automation backend survey (139 instances, 97% leaking `/_debug`) |

---

## Data labeling / annotation servers

Often exposed in ML team workflows; PII frequently in their datasets. Operators stand up labeling tools quickly to crowd-source annotation, then forget to lock them down before walking away.

Population survey **DONE 2026-05**, see [`data-labeling-cloud-survey-2026-05.md`](data-labeling-cloud-survey-2026-05.md). Per-platform table below retained for fingerprint reference.

| Platform | Port | Fingerprint | Tier | Risk | Status |
|---|---|---|---|---|---|
| **Argilla** | 6900 (default) | GET `/api/_info` returns Argilla version | A* | Dataset content (often PII), labeled examples, sometimes embedded model outputs | **DONE 2026-05**, data-labeling survey |
| **LabelStudio** | 8080 | GET `/version` returns LabelStudio version | A* | Dataset content + project structure | **DONE 2026-05**, data-labeling survey |
| **Prodigy** (Explosion AI) | 8080 | GET `/` returns Prodigy UI | A* | Dataset + annotator credentials | covered by data-labeling survey scope |
| **doccano** | 8000 | GET `/v1/health` returns OK | A* | NLP annotation projects | covered by data-labeling survey scope |
| **CVAT** (Computer Vision Annotation Tool) | 8080 | GET `/api/server/about` | A* | Image/video annotation projects, sometimes facial PII | covered by data-labeling survey scope |

---

## Methodology template

For any platform above, the probe pattern is:

```bash
# 1. Masscan the canonical port across the tier-2 cloud /16 ranges
sudo masscan -iL /tmp/tier2-all-ranges.txt -p<port> --rate 10000 --wait 5 -oG /tmp/<platform>-masscan.txt

# 2. Filter to unique IPs
awk '/Host:/ {print $4}' /tmp/<platform>-masscan.txt | sort -u > /tmp/<platform>-ips.txt

# 3. Run the framework-specific fingerprint probe (200-thread Python)
/home/cowboy/security-tools/bin/python3 /tmp/<platform>-probe.py < /tmp/<platform>-ips.txt > /tmp/<platform>-confirmed.jsonl

# 4. Filter AS63949 honeypot fleet pollution if probe is permissive
/home/cowboy/security-tools/bin/python3 /tmp/honeypot-detector.py < /tmp/<platform>-ips.txt | comm -23 /tmp/<platform>-ips.txt -

# 5. Cert-pivot identified hosts on port 443 for operator attribution
while read ip; do
  cn=$(timeout 4 bash -c "echo | openssl s_client -connect $ip:443 -servername $ip 2>/dev/null" | openssl x509 -noout -ext subjectAltName 2>/dev/null | tail -1)
  echo "$ip → $cn"
done < /tmp/<platform>-confirmed-ips.txt
```

The existing case studies serve as templates, the [`speech-audio-cloud-survey-2026-05.md`](speech-audio-cloud-survey-2026-05.md) is the most recent example following this pattern.

---

## Why this list exists

The auth-on-default thesis predicts: **for any framework that ships without authentication enabled by default, the population-scale deployment will be unauthenticated.** Each unsurveyed platform above is an opportunity to either:

1. **Confirm the thesis** on a new platform class (extends the evidence base)
2. **Falsify the thesis** if a platform with auth-off-default ships ~0% unauth at population scale (would be a meaningful counter-example, none observed yet)

The list also acts as a roadmap for any contributor who wants to add coverage. NuClide's tooling (`aimap`, `recongraph`, `BARE`) already covers many of the fingerprints above; running them at population scale on tier-2 cloud ranges is the work product.

---

## See also

- [`SYNTHESIS-2026-05.md`](SYNTHESIS-2026-05.md), completed-survey synthesis
- [`REMEDIATION-GUIDE.md`](REMEDIATION-GUIDE.md), operator fix-it guide for the platforms covered
- [`index.md`](index.md), index of all completed case studies
