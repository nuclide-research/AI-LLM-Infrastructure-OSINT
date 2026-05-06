# Category Taxonomy

_Conceptual framing for every platform class this repo tracks. Each entry defines the category, distinguishes it from adjacent classes, and explains why it matters for OSINT._

This is the "what does this category MEAN" reference. For Shodan dorks per category, see [`shodan/queries/`](../shodan/queries/). For survey results per category, see [`case-studies/commercial/`](../case-studies/commercial/).

---

## Table of contents

**Substrate tier (the layers everything else sits on):**
- [Object Storage & Artifact Stores](#object-storage--artifact-stores)
- [Specialty Data Layers](#specialty-data-layers)
- [Time-Series Databases](#time-series-databases)
- [Search-as-Analytics](#search-as-analytics)
- [Distributed Coordination Services](#distributed-coordination-services)
- [Container & Orchestration](#container--orchestration)
- [GPU & Compute Dashboards](#gpu--compute-dashboards)
- [Compute Orchestration / Training](#compute-orchestration--training)

**Model tier:**
- [Model Serving / Inference](#model-serving--inference)
- [Embedding Services](#embedding-services)
- [Image Generation](#image-generation)
- [Speech & Audio AI](#speech--audio-ai)

**Data tier:**
- [Vector Databases](#vector-databases)
- [Training & Experiments / ML Lifecycle](#training--experiments--ml-lifecycle)
- [Data Labeling / Annotation](#data-labeling--annotation)
- [Search & Data Infrastructure](#search--data-infrastructure)

**Application tier:**
- [LLM Orchestration](#llm-orchestration)
- [RAG Stacks / RAG Framework](#rag-stacks--rag-framework)
- [Agent Platforms](#agent-platforms)
- [Browser Automation / Agent Backends](#browser-automation--agent-backends)

**Adjunct tier:**
- [LLM Gateways / OpenAI-Compat Proxies](#llm-gateways--openai-compat-proxies)
- [LLM Observability / Tracing](#llm-observability--tracing)
- [MCP Servers](#mcp-servers)
- [AI Safety Evaluation / Red-Team Self-Hosted](#ai-safety-evaluation--red-team-self-hosted)

**Operational tier:**
- [Notebook & Dev Environments](#notebook--dev-environments)
- [Dev-Tooling AI / Coding Agents](#dev-tooling-ai--coding-agents)
- [Backup & Snapshot Services](#backup--snapshot-services)
- [Credential & Config Leaks](#credential--config-leaks)
- [Specialty Domains](#specialty-domains)

---

## Object Storage & Artifact Stores

**What it is:** S3-compatible blob storage that holds the actual model weights, training data, embedding caches, and pipeline artifacts. The substrate beneath every other tier. Includes MinIO, Harbor (container artifact registry), Docker Registry v2, and direct cloud-bucket exposure (S3, GCS, Azure Blob with public ACLs).

**Why it matters for OSINT:** Compromise here exfiltrates the model itself, not just the inference endpoint. Per the 2026-05 cross-survey, MinIO actually performs *better* than the AI tiers on auth posture (852 instances surveyed, 0% anonymous-list — auth-on-default works). Docker Registry v2 leaks operator stack composition (image catalog) even when image pulls require auth. The headline failure mode is the artifact in the bucket — exposed `.env`, model checkpoint, training-data snapshot — rather than the bucket service itself.

**Members:** MinIO · Harbor · Docker Registry v2 · S3/GCS/Azure Blob (public ACLs) · DVC remote storage

**Status:** Surveyed — see [`minio-dify-cloud-survey-2026-05.md`](../case-studies/commercial/minio-dify-cloud-survey-2026-05.md) and [`backup-snapshot-services-survey-2026-05.md`](../case-studies/commercial/backup-snapshot-services-survey-2026-05.md).

---

## Specialty Data Layers

**What it is:** General-purpose analytic/storage platforms that the AI/ML ecosystem co-opts for AI-adjacent work, but that weren't built specifically for AI. Predate the modern AI stack — ClickHouse (2008, Yandex), Cassandra (2008, Facebook), Pinot (2014, LinkedIn), DuckDB (2018, CWI) — and get wired into AI workflows because they're the right tool for analytical / columnar / wide-column / embedded-analytical workloads the purpose-built AI tier handles badly.

**Distinguishing axis:** Specialty data layers don't fit any of the AI-purpose-built tier slots (vector DB, inference, MLOps, gateway, MCP, RAG framework). They're the substrate beneath them. ClickHouse is what your MLflow tracking server runs on top of when scale gets serious. ScyllaDB is what your feature store actually IS. DuckDB is what's inside the analytics dashboard for your governance ML classifier. Cassandra holds the session state for your agent platform.

**Why it matters for OSINT:**

1. **Different default ports** — 8123 (ClickHouse HTTP), 9000 (Pinot Controller / ClickHouse native), 9042 (CQL), 10000 (Scylla REST), 8081 (Druid Coordinator), 8030 (StarRocks FE). None of these collide with the AI-tier surveys.
2. **Mixed auth posture by default** — the AI tier reproduces "framework default = no auth" (Qdrant 100% unauth, Ollama 100% unauth, vLLM 100% unauth). Specialty data layers ship with more variable defaults — ClickHouse `default` user is passwordless but bound to `localhost`; operators must actively make it public. Cassandra ships auth-off but most cloud images flip it on. The expected confirmed-unauth rate is lower than the AI tier's 100%, but **per-host data sensitivity is dramatically higher** — billion-row tables of training data, feature vectors, governance-classifier state, transaction ledgers.
3. **Different attack-surface shape** — vector DBs leak embeddings; inference servers leak prompts and burn quota. Specialty data layers leak **structured operational data** at OLAP / CQL / SQL query-language scale. A confirmed-unauth ClickHouse is `SELECT * FROM training_dataset` accessible to anyone. A confirmed-unauth Pinot Controller is the entire real-time analytics fabric of a company. An unauth Cassandra Reaper UI is repair-job orchestration over the production NoSQL state.

**Members:**

| Platform | Origin | What it does | Why AI-adjacent |
|---|---|---|---|
| **ClickHouse** | Yandex / ClickHouse Inc. | Columnar OLAP DB | Cloudflare/Spotify/Uber observability backends; vector extensions in v23+ |
| **DuckDB** | CWI Amsterdam / DuckDB Foundation | Embedded analytical DB | Increasingly the query engine *inside* AI products (Amulet Scan, Definite.app) |
| **Apache Pinot** | LinkedIn → Apache → StarTree commercial | Real-time OLAP | Uber/Stripe/Slack analytics; Kafka-fed real-time AI feature pipelines |
| **Apache Druid** | Imply.io / Apache | Real-time OLAP (Pinot competitor) | Ad-tech, observability, similar AI-adjacency |
| **StarRocks / Apache Doris** | StarRocks Inc. / Baidu Palo | MPP analytical DB | Chinese-origin commercial; AI-stack analytics tier |
| **Apache Cassandra** | Apache Foundation | Wide-column NoSQL | Feature stores, vector extensions in 5.x+ |
| **ScyllaDB** | ScyllaDB Inc. | Cassandra-compatible C++ rewrite | Same use cases, faster |

**Adjacent (defined in their own categories below):** [Time-Series Databases](#time-series-databases) · [Search-as-Analytics](#search-as-analytics) · [Distributed Coordination Services](#distributed-coordination-services).

**Worked example:** the Canton Foundation case (`dashboard.canton.foundation` Amulet Scan API, 2026-05-05) — a custom Node.js/Express API on port 3001 wraps a DuckDB engine to serve a real-time blockchain analytics dashboard with an embedded ML governance classifier. None of the prior surveys (vector DB, inference, MLOps, MCP, RAG, browser-agent, datalabel) would have caught it; the specialty-data-layers category is what makes findings like that legible.

**Status:** In progress — see [`FUTURE-SURVEYS.md`](../case-studies/commercial/FUTURE-SURVEYS.md#specialty-data-layers-often-ai-adjacent). aimap fingerprints shipped in v1.4.0 (Amulet Scan DuckDB API, Definite.app DuckDB) and v1.5.0 (ClickHouse, Apache Pinot Controller, ScyllaDB REST).

---

## Time-Series Databases

**What it is:** Storage engines optimized for ordered measurements over time — metrics, telemetry, sensor data, financial ticks, application traces. InfluxDB (8086), TimescaleDB (Postgres extension on 5432), VictoriaMetrics (8428), QuestDB (9000 + Postgres-wire on 8812), M3DB (7201), Prometheus TSDB (9090, also see Observability tier).

**Distinguishing axis:** Time-series stores are *append-mostly* with retention/downsampling policies; ClickHouse and other OLAP engines from [Specialty Data Layers](#specialty-data-layers) can do time-series workloads but the time-series-native engines win on ingestion throughput, automatic downsampling, and PromQL/InfluxQL/Flux/SQL-with-time-extensions query languages purpose-built for windowed aggregation.

**Why it matters for OSINT:**

1. **Inference-latency telemetry is what's stored.** Operators monitor model-serving infrastructure here — request latencies, error rates, GPU utilization, queue depth. Exposed time-series DBs leak the operator's traffic shape, customer count, and SLO posture.
2. **Training-loss curves and hyperparameter sweeps land here.** ML teams pipe training metrics to InfluxDB / Prometheus. Exposed instances disclose which experiments succeeded or failed and reveal model-development cadence.
3. **AI agents in production write structured events to these.** Tool-call logs, retrieval scores, eval-set performance over time — everything an agentic system does at scale generates a time-series stream that someone has to put somewhere.
4. **Auth posture varies sharply by product.** InfluxDB v1 shipped auth-off-default (still common in legacy deploys); v2 ships token-required by default. TimescaleDB inherits whatever Postgres auth policy the operator set. VictoriaMetrics ships fully open by default — `vmauth` is a separate bolted-on layer most operators skip. QuestDB has `enable.http.auth=false` as the documented default.

**Members:** InfluxDB · TimescaleDB · VictoriaMetrics · QuestDB · M3DB · Prometheus TSDB

**Status:** Not yet surveyed standalone. Prometheus appears partially in the observability survey. VictoriaMetrics specifically is high-yield given its open-by-default posture and rapid adoption replacing Prometheus at scale.

---

## Search-as-Analytics

**What it is:** Search engines used as the analytical query tier rather than purely as document indexes. Apache Solr (8983) and Vespa (8080) are the primary members; Elasticsearch with the analytical/aggregation pipeline overlaps. Distinct from [Search & Data Infrastructure](#search--data-infrastructure) where the framing is "corpus layer AI apps query" — here the framing is "the platform doing the analytical work."

**Distinguishing axis:** A document index returns ranked results; a search-as-analytics engine returns aggregations, faceted breakdowns, vector-similarity scores, and OLAP-shaped responses over indexed data. Vespa specifically is a tri-purpose engine — search + vector + analytics — that doesn't fit cleanly anywhere else. Solr exposes velocity-template RCE (CVE-2019-17558) and config-file-on-disk write surfaces in older versions, making it more dangerous than its document-index sibling positioning suggests.

**Why it matters for OSINT:**

1. **Vespa's tri-mode design** means a single exposed instance leaks all three workload types at once: search corpus + embedding vectors + analytical aggregates.
2. **Solr's velocity templates** turn a "documentation-leak" finding into RCE — CVE-2019-17558 is straightforward to exploit on auth-off Solr deploys.
3. **Aggregation queries are expensive.** Both platforms support resource-heavy faceted queries; unauth instances enable compute-burn DoS.
4. **Auth-off rate is moderate.** Solr ships with `BasicAuthPlugin` available but disabled by default. Vespa relies on TLS client-cert auth that operators frequently misconfigure. Population-scale unauth rate expected to be 30-50% based on adjacent-class data.

**Members:** Apache Solr · Vespa · Elasticsearch (when used aggregation-heavy)

**Status:** Not yet surveyed standalone. Some Elasticsearch coverage in [`elasticsearch-cloud-survey-2026-05.md`](../case-studies/commercial/elasticsearch-cloud-survey-2026-05.md) but framed as document-index tier, not analytics tier.

---

## Distributed Coordination Services

**What it is:** Behind-the-scenes coordination + consensus + metadata infrastructure that distributed AI/data tiers rely on. ClickHouse Keeper (Raft, 9181), Apache ZooKeeper (2181 — used by Pinot, Solr, Kafka, Druid, HBase), etcd in standalone mode (2379 — also used by Kubernetes), HashiCorp Consul (8500), Apache Helix (used by Pinot for cluster management), Pinot deep-store backends (typically S3/HDFS/GCS), Redis-as-coordination (6379 — distinct from Redis Stack vector usage).

**Distinguishing axis:** These services don't "do work" the operator interacts with directly — they hold the cluster topology, leader election state, configuration metadata, and inter-node communication state for the platform that sits above them. They show up in OSINT scans because operators forget they're network-exposed (the assumption "this is internal-only" is the dominant failure mode).

**Why it matters for OSINT:**

1. **Coordination = secrets in plaintext, often.** ZooKeeper holds connection strings between Solr nodes; etcd holds Kubernetes secrets; Consul holds service-mesh configuration; ClickHouse Keeper holds replication credentials.
2. **Cluster topology is operationally sensitive.** Discovering the full cluster shape (number of replicas, leader/follower roles, current sequence/log positions) tells an attacker exactly where to pivot for highest-impact follow-on.
3. **Pinot deep-store and similar backing stores** are often S3/HDFS buckets. The Pinot Controller leaks the deep-store URI; an unauth bucket means full table-data exfiltration regardless of Pinot Controller's own auth posture.
4. **Redis-as-coordination is distinct from Redis-as-vector-store.** A Redis instance might serve dual purposes — vector search for the AI tier, plus session state for the application tier. An unauth Redis exposes both classes at once.
5. **Auth-off-default is the norm.** ZooKeeper's `4lw` four-letter commands (`mntr`, `srvr`, `cons`) work without authentication on default configs and enumerate cluster state. etcd's v2 and v3 APIs default to no client-cert requirement. ClickHouse Keeper ships open by default and assumes operators put it behind a firewall.

**Members:** ClickHouse Keeper · Apache ZooKeeper · etcd (standalone) · Consul · Apache Helix · Pinot deep-store backends · Redis (coordination role)

**Status:** Not yet surveyed standalone. etcd partial coverage exists in the Container & Orchestration tier (where etcd's role is K8s-cluster-secrets). ZooKeeper is high-yield because of how many of the platforms above (Pinot, Solr, Druid, Kafka, HBase) cluster-manage through it.

---

## Container & Orchestration

**What it is:** The runtime substrate AI workloads ship on. Docker daemon, Kubernetes API + kubelet, etcd, Consul, HashiCorp Vault. Not AI-specific, but every AI deployment runs on top of this layer; exposure here means the entire stack.

**Why it matters for OSINT:** Unauth Docker daemon = arbitrary container execution on the host. Unauth Kubernetes API = full cluster admin. Unauth etcd = cluster secrets in plaintext, including AI-stack credentials. The blast radius is the entire AI deployment; everything above this tier becomes irrelevant if this tier is open.

**Members:** Docker daemon · Kubernetes API · kubelet · etcd · Consul · Vault

**Status:** Documented in [`shodan/queries/12-containers.md`](../shodan/queries/12-containers.md). Tier-2 cross-survey not yet run.

---

## GPU & Compute Dashboards

**What it is:** Operator-facing dashboards for GPU clusters, compute marketplaces, and AI training/inference resource management. NVIDIA DCGM (Datacenter GPU Manager), Ray Dashboard, RunPod, Vast.ai, GPUStack.

**Why it matters for OSINT:** GPU cost is the constraint operators feel most. Exposed dashboards leak which models are being trained/served + cluster topology + sometimes credentials wired into job submissions. Ray Dashboard specifically has CVE-2023-48022 (ShadowRay, actively exploited) — job submission RCE on auth-off-default deployments.

**Members:** NVIDIA DCGM · Ray Dashboard · RunPod · Vast.ai · GPUStack

**Status:** Documented in [`shodan/queries/14-gpu-compute.md`](../shodan/queries/14-gpu-compute.md). Ray Dashboard fingerprint in aimap v1.3.0.

---

## Compute Orchestration / Training

**What it is:** Distributed-compute orchestrators that run model training, batch inference, and ML pipelines at scale. Apache Spark (UI 4040/8080), Apache Airflow (8080), Ray (Dashboard 8265, Serve 3000), Dask (8787), Prefect (4200), Temporal (7233/8080), Kubeflow / KServe (varies), BentoML (3000).

**Distinguishing axis:** This tier orchestrates *what runs and when*. Specialty data layers hold the *data*; this tier holds the *jobs* that operate on it. Most ship Tier-A "no auth concept" on the dashboard endpoint — auth is bolted on by surrounding infrastructure (K8s ingress + auth proxy), not the framework itself.

**Why it matters for OSINT:** Unauth Airflow = code execution via DAG trigger + plaintext credentials in Variables/Connections API. Unauth Ray Dashboard = ShadowRay job-submission RCE (CVE-2023-48022). Unauth Spark UI = job logs + driver state + sometimes credentials in env. This is where the "auth-off-default thesis" breaks operators worst, because the dashboards are designed for trusted-network deployment but routinely end up internet-facing.

**Members:** Apache Spark · Apache Airflow · Ray (Dashboard + Serve) · Dask · Prefect · Temporal · Kubeflow / KServe · BentoML

**Status:** In progress — see [`FUTURE-SURVEYS.md`](../case-studies/commercial/FUTURE-SURVEYS.md#compute-orchestration--training-tier). Discovery runbook at [`data/compute-orch-discovery-runbook.sh`](../data/compute-orch-discovery-runbook.sh).

---

## Model Serving / Inference

**What it is:** The runtime that takes a model + a prompt and returns a generation. vLLM, NVIDIA Triton, llama.cpp HTTP, Ollama, LM Studio, GPT4All, Text Generation WebUI (oobabooga), Kobold.cpp, SGLang, Jan AI, NVIDIA NIM. Most expose `/v1/models` (OpenAI-compat) or platform-specific endpoints.

**Why it matters for OSINT:** Compute theft (operator pays GPU cost for attacker inference), model fingerprinting (which weights are loaded), prompt injection at scale, and quota burn against upstream providers when the inference server is wired to a paid API key. Surveyed at 100% unauth across the Class-A tier (Triton + vLLM + Ollama; 388 instances in the 2026-05 cross-survey).

**Members:** vLLM · NVIDIA Triton · Ollama · llama.cpp · LM Studio · text-generation-webui · Kobold.cpp · SGLang · Jan AI · NVIDIA NIM

**Status:** Surveyed — see [`vllm-cloud-survey-2026-05.md`](../case-studies/commercial/vllm-cloud-survey-2026-05.md), [`triton-cloud-survey-2026-05.md`](../case-studies/commercial/triton-cloud-survey-2026-05.md), [`ollama-cloud-survey-2026-05.md`](../case-studies/commercial/ollama-cloud-survey-2026-05.md), [`ollama-tier2-cloud-survey-2026-05.md`](../case-studies/commercial/ollama-tier2-cloud-survey-2026-05.md).

---

## Embedding Services

**What it is:** Specialized inference servers whose job is to turn documents and queries into vectors. HuggingFace Text Embeddings Inference (TEI), Infinity-Embedding, SentenceTransformers servers, llama.cpp running embedding models. Distinct from full LLM inference because the workload is read-heavy + latency-sensitive + outputs fixed-dim float vectors.

**Why it matters for OSINT:** Compute theft (embedding workloads are GPU-bound), model fingerprinting (which embedding model = which retrieval space), and adversarial-corpus testing (operator's RAG retrieval surface is reachable via the embedder). Also a **forensic anchor**: identifying the embedding model often pins down which RAG framework + which vector DB the operator runs.

**Members:** HuggingFace TEI · Infinity-Embedding · SentenceTransformers server · llama.cpp embedding mode

**Status:** Not yet surveyed standalone. Often surfaces inside RAG framework / inference surveys.

---

## Image Generation

**What it is:** GPU-bound diffusion inference servers. ComfyUI (8188), Stable Diffusion + AUTOMATIC1111 (7860), InvokeAI, Fooocus, Roboflow self-hosted, YOLOv8/MMDetection inference. Heavy GPU workloads, often on Gradio (port 7860) or custom HTTP APIs.

**Why it matters for OSINT:** Compute theft at very high cost (GPU-hours per image). Workflow exfiltration (ComfyUI graphs are operator-specific IP — custom LoRA/embedding/sampler chains). Workflow injection (compromised graphs can persist trojan steps). VRAM exposure proves capacity (RTX PRO 6000 Blackwell etc. — 385 GB VRAM exposed in the ComfyUI survey).

**Members:** ComfyUI · AUTOMATIC1111 · InvokeAI · Fooocus · Roboflow self-hosted · YOLOv8/MMDetection servers

**Status:** Surveyed — see [`comfyui-cloud-survey-2026-05.md`](../case-studies/commercial/comfyui-cloud-survey-2026-05.md), [`gradio-port-7860-survey-2026-05.md`](../case-studies/commercial/gradio-port-7860-survey-2026-05.md).

---

## Speech & Audio AI

**What it is:** Voice synthesis, voice cloning, speech-to-text, and audio-AI agent backends. Whisper.cpp servers (port 9000), Coqui XTTS, Mozilla TTS, AllTalk TTS, LocalAI audio (OpenAI-compat `/v1/audio/transcriptions`), Bark, MusicGen, F5-TTS / E2-TTS / OpenVoice / ChatTTS, Pipecat / LiveKit voice agents (WebRTC + signaling), pyAnnote diarization.

**Why it matters for OSINT:** Voice cloning = deepfake/impersonation primitive at scale; trademark/voice misuse for personalities exposed. Real-time conversation manipulation on Pipecat/LiveKit deployments. Speaker-ID compute theft on pyAnnote.

**Members:** Whisper.cpp · Coqui XTTS · Mozilla TTS · LocalAI audio · Bark · MusicGen · F5-TTS · E2-TTS · OpenVoice · ChatTTS · Pipecat · LiveKit · pyAnnote

**Status:** Surveyed (port 9000 Whisper) — see [`speech-audio-cloud-survey-2026-05.md`](../case-studies/commercial/speech-audio-cloud-survey-2026-05.md). Extended (Coqui/F5/Pipecat) not yet.

---

## Vector Databases

**What it is:** Purpose-built stores for embedding similarity search. Qdrant, Milvus, ChromaDB, Weaviate, pgvector (Postgres extension), Redis Stack vector search, LanceDB, Vespa, Typesense, Meilisearch, Apache Solr.

**Distinguishing axis:** Built around the approximate-nearest-neighbor (ANN) primitive over high-dimensional float vectors. Specialty data layers (ClickHouse 23+, Cassandra 5.x+) have *added* vector capabilities but their primary identity is OLAP/NoSQL — vector DBs are vector-first.

**Why it matters for OSINT:** Embeddings are training-data fingerprints — leaked vectors enable inversion attacks (some vector models leak training-set membership), facial-recognition primitives (the OnlyFans Milvus exposure: 1.21M facial embeddings, functional doxing), and semantic-search over operator-private corpora. Surveyed at 100% unauth in the Class-A tier (142 instances across Qdrant + ChromaDB + Milvus).

**Members:** Qdrant · Milvus · ChromaDB · Weaviate · pgvector · Redis Stack · LanceDB · Vespa · Typesense · Meilisearch · Solr

**Status:** Surveyed — see [`chromadb-cloud-survey-2026-05.md`](../case-studies/commercial/chromadb-cloud-survey-2026-05.md), [`qdrant-cloud-survey-2026-05.md`](../case-studies/commercial/qdrant-cloud-survey-2026-05.md), [`milvus-cloud-survey-2026-05.md`](../case-studies/commercial/milvus-cloud-survey-2026-05.md), tier-2 expansions of each. Specialty-tier (Weaviate, Vespa, etc.) not yet.

---

## Training & Experiments / ML Lifecycle

**What it is:** Experiment tracking, hyperparameter management, model registries, dataset versioning. MLflow (Tracking + Model Registry), Kubeflow, ClearML, Weights & Biases self-hosted, Comet ML, Neptune.ai, Argilla, Label Studio, Feast (feature store), DVC.

**Why it matters for OSINT:** MLflow specifically is actively exploited via CVE-2023-1177 (path-traversal arbitrary file read) — 18% of surveyed instances had attacker-injected experiments with `artifact_location: http:///?/../../../etc/`. Beyond that, the metadata leak is severe: every experiment captures hyperparameters, dataset references, sometimes raw data samples, and operator team structure.

**Members:** MLflow · Kubeflow · ClearML · W&B self-hosted · Comet ML · Neptune.ai · DVC

**Status:** Surveyed — see [`mlflow-cloud-survey-2026-05.md`](../case-studies/commercial/mlflow-cloud-survey-2026-05.md). ML-lifecycle-extended (W&B, ClearML, Comet, Neptune) not yet.

---

## Data Labeling / Annotation

**What it is:** Tools for crowd-sourcing or team-based annotation of datasets. doccano, Label Studio, Argilla, Prodigy (Explosion AI), CVAT (Computer Vision Annotation Tool).

**Why it matters for OSINT:** Datasets in labeling tools frequently contain PII (faces in CVAT, names/emails in doccano text annotations, voice samples in audio labeling). Operators stand up labeling tools quickly to crowd-source annotation, then forget to lock them down before walking away.

**Members:** doccano · Label Studio · Argilla · Prodigy · CVAT

**Status:** Surveyed — see [`data-labeling-cloud-survey-2026-05.md`](../case-studies/commercial/data-labeling-cloud-survey-2026-05.md). The 2026-05 sweep found 348 confirmed cross-cloud, all doccano, ~99% auth-on at `/v1/projects` — auth-off-default thesis breaks at this tier (applications-for-end-users vs infrastructure-for-engineers).

---

## Search & Data Infrastructure

**What it is:** Search engines and document indexes that AI applications query. Elasticsearch (with ELSER + kNN ML plugins), OpenSearch, Typesense, Meilisearch. Elasticsearch in particular runs the corpus layer of many enterprise AI deployments.

**Why it matters for OSINT:** Sanctionscanner.com 79M KYB records + 6.2M sanctions list entries on unauth Elasticsearch (active ransomware compromise predates discovery). The classic Elasticsearch-exposed-corpus pattern combined with ELSER/kNN means even auth-on instances may leak if the ML plugin endpoints aren't separately protected.

**Members:** Elasticsearch · OpenSearch · Typesense · Meilisearch · Apache Solr

**Status:** Surveyed — see [`elasticsearch-cloud-survey-2026-05.md`](../case-studies/commercial/elasticsearch-cloud-survey-2026-05.md). Typesense / Meilisearch / Solr extended sweep folds into [Specialty Data Layers](#specialty-data-layers).

---

## LLM Orchestration

**What it is:** Workflow / chaining UIs that wire LLM calls + tools + retrieval into multi-step pipelines. Flowise, Langflow, Dify, Open WebUI, LiteLLM, n8n (with AI nodes), SillyTavern, Clawdbot.

**Why it matters for OSINT:** Orchestration UIs aggregate operator credentials (provider API keys for OpenAI/Anthropic/etc., database connections, MCP tool credentials). Exposure here often equals all-of-the-above — the orchestrator is the central trust nexus.

**Members:** Flowise · Langflow · Dify · Open WebUI · LiteLLM · n8n · SillyTavern · Clawdbot

**Status:** Surveyed — see [`flowise-cloud-survey-2026-05.md`](../case-studies/commercial/flowise-cloud-survey-2026-05.md), [`openwebui-cloud-survey-2026-05.md`](../case-studies/commercial/openwebui-cloud-survey-2026-05.md), [`n8n-cloud-survey-2026-05.md`](../case-studies/commercial/n8n-cloud-survey-2026-05.md), and others. Auth-off-default thesis: 1,170 instances surveyed, 0% unauthenticated (these have built-in auth that operators leave on).

---

## RAG Stacks / RAG Framework

**What it is:** Two related sub-tiers. **RAG stacks** (h2oGPT, Danswer/Onyx, Quivr, Khoj, RAGFlow, LibreChat) are full self-hosted apps; users interact via chat UI. **RAG framework servers** (LlamaIndex servers, Haystack, LightRAG, GraphRAG, AnythingLLM, RAGFlow API, PrivateGPT/LocalGPT) are framework-level deployments — pipelines + retrieval logic + embedded prompts exposed as APIs.

**Why it matters for OSINT:** Document-corpus exfiltration (enterprise documents in unauth RAG indexes), prompt structure leak (system prompts visible in pipeline definitions), embedded credentials (LLM provider keys, vector DB keys baked in). The RAG framework survey caught the "PrivateGPT" misclassification: ~98% of port-9380 hits were custom FastAPI RAG apps, not PrivateGPT, with 51% leaking `/openapi.json` publicly — full route maps + Pydantic schemas + securitySchemes exposed.

**Members:** h2oGPT · Danswer/Onyx · Quivr · Khoj · RAGFlow · LibreChat · LlamaIndex servers · Haystack · LightRAG · GraphRAG · AnythingLLM · PrivateGPT/LocalGPT

**Status:** Surveyed — see [`rag-framework-cloud-survey-2026-05.md`](../case-studies/commercial/rag-framework-cloud-survey-2026-05.md).

---

## Agent Platforms

**What it is:** Autonomous-agent frameworks where an LLM drives tool calls, memory, and multi-step task execution. AutoGen Studio, CrewAI Studio, LangGraph servers, BabyAGI/SuperAGI, OpenDevin/Devon, Goose (Block), MetaGPT, Clawdbot, AutoGPT-derivative server modes.

**Why it matters for OSINT:** Agent definitions often contain embedded credentials wired into tools (cloud-API keys, database connection strings, MCP-tool authentication). Sandbox escape is common when Docker-on-host is wired in for code execution. Agent state (memory, golden-set evaluation history, classifier learning mode) becomes a manipulation target — see the Canton Foundation Amulet Scan finding: governance-lifecycle ML classifier toggleable via unauth POST.

**Members:** AutoGen Studio · CrewAI Studio · LangGraph · SuperAGI · OpenDevin · Goose · MetaGPT · BabyAGI

**Status:** Not yet surveyed standalone. AutoGPT-derivative + LangGraph appearances in MCP and RAG surveys.

---

## Browser Automation / Agent Backends

**What it is:** Headless-Chrome endpoints used by agent stacks for web tool execution. Browserless, Playwright server, Skyvern, Puppeteer remote (port 9222 CDP), Selenium Grid (4444), raw Chromium DevTools Protocol over WebSocket.

**Why it matters for OSINT:** Misconfigured browser-agent endpoints offer remote browser control as a service — attackers drive scraping, credential harvesting, or cloud-resource abuse using the operator's compute and IP reputation. Raw Chromium CDP is browser-RCE-equivalent via WSCP control. Pre-2023 Chromium versions = chained stale-CVE attack surface.

**Members:** Browserless · Playwright server · Skyvern · Puppeteer remote · Selenium Grid · raw Chromium CDP

**Status:** Surveyed — see [`browser-agent-cloud-survey-2026-05.md`](../case-studies/commercial/browser-agent-cloud-survey-2026-05.md). 153 confirmed unauth, 100% at platform endpoint.

---

## LLM Gateways / OpenAI-Compat Proxies

**What it is:** Reseller proxies that present an OpenAI-compatible API in front of upstream providers (OpenAI, Anthropic, Google, OpenRouter, Mistral, etc.). LiteLLM Proxy, LocalAI, Text Generation WebUI, LM Studio server mode, Jan AI, OneAPI/NewAPI, custom Express/FastAPI shims.

**Why it matters for OSINT:** This is where provider-key quota theft happens. The 2026-05 LLM Gateway survey found 1,899 confirmed cross-cloud unauth gateways, 1,857 (97.8%) returning functional inference to a single-token unauth `/v1/chat/completions` — including 2 Anthropic-functional hosts billing the operator's Anthropic quota for attacker prompts. Single-template propagation: 1,829 of 1,857 returned the *identical canned response* — one open-source proxy template auth-off-deployed at population scale.

**Members:** LiteLLM Proxy · LocalAI · text-generation-webui · LM Studio · Jan AI · OneAPI · NewAPI

**Status:** Surveyed — see [`llm-gateways-cloud-survey-2026-05.md`](../case-studies/commercial/llm-gateways-cloud-survey-2026-05.md).

---

## LLM Observability / Tracing

**What it is:** Trace-and-eval-storage platforms where every LLM call is logged with prompts, completions, latencies, costs, and metadata. Langfuse (3000), Phoenix/Arize (6006), Helicone (gateway pattern), TruLens self-hosted, Portkey.

**Why it matters for OSINT:** Trace data is unredacted prompt + response history — frequently includes PII, internal documents, operator credentials echoed back from system prompts. Phoenix specifically surveyed: 6 confirmed Phoenix instances + 3 TensorBoard, all unauth, including active SDXL distillation training visible.

**Members:** Langfuse · Phoenix/Arize · Helicone · TruLens · Portkey

**Status:** Surveyed (Phoenix subset) — see [`observability-cloud-survey-2026-05.md`](../case-studies/commercial/observability-cloud-survey-2026-05.md). Langfuse/Helicone/TruLens not yet.

---

## MCP Servers

**What it is:** Model Context Protocol servers exposing tool surfaces to LLMs over HTTP / SSE. Generic MCP HTTP+SSE, FastMCP (Python framework), mcp-proxy (stdio→HTTP bridge), HexStrike AI (offensive-MCP), Cloudflare Workers MCP. Designed for stdio (in-process) but the ecosystem pushed HTTP for remote use.

**Why it matters for OSINT:** When operators wire filesystem, shell, database, and cloud-API tools into MCP servers and expose them without auth, the unauthenticated-RPC failure pattern replays at the protocol layer. The 2026-05 MCP survey found 95 confirmed cross-cloud, 28 with non-empty `tools/list` — including a fully-exposed Gmail mailbox MCP (19-tool send/read/delete CRUD on operator's own Gmail), Alcy CRM MCP (22-tool French facility-management CRUD), hindsight-mcp v3.1.1 personal-AI-memory CRUD with `clear_memories` tool, 3× Casdoor IAM-CRUD across providers. Methodology insight: protocol-strict JSON-RPC handshake gate dropped AS63949 honeypot pollution from 91.6% (Milvus) to 1.1% (MCP) — the protocol is itself a stronger filter than IP-list.

**Members:** Generic MCP HTTP+SSE · FastMCP · mcp-proxy · HexStrike AI · Cloudflare Workers MCP

**Status:** Surveyed — see [`mcp-cloud-survey-2026-05.md`](../case-studies/commercial/mcp-cloud-survey-2026-05.md), [`shodan/queries/10-mcp-servers.md`](../shodan/queries/10-mcp-servers.md).

---

## AI Safety Evaluation / Red-Team Self-Hosted

**What it is:** Tools that test AI systems for adversarial robustness, safety violations, prompt-injection susceptibility. Garak (NVIDIA), Promptfoo, Patronus AI, AILuminate (MLCommons), DeepEval / Confident AI, NeMo Guardrails, Lakera Guard, LangSmith, Inspect AI.

**Why it matters for OSINT:** The finding-corpus is sensitive — adversarial prompt libraries, evaluator outputs, red-team test results frequently contain proprietary attack vectors operators don't want public. Methodology lesson from this category (2026-05-05): single-word substring matching produced 6 false positives and 0 true positives at population scale (anime filename matched as Garak, French marketing copy matched as DeepEval). **The methodology correction is the load-bearing finding** — see Methodology Insight #6 in [`SYNTHESIS-2026-05.md`](../case-studies/commercial/SYNTHESIS-2026-05.md).

**Members:** Garak · Promptfoo · Patronus AI · AILuminate · DeepEval · NeMo Guardrails · Lakera Guard · LangSmith · Inspect AI

**Status:** Surveyed (with methodology correction) — see [`ai-safety-eval-cloud-survey-2026-05.md`](../case-studies/commercial/ai-safety-eval-cloud-survey-2026-05.md). 0 confirmed at population scale on tier-2 cloud sample after fingerprint tightening.

---

## Notebook & Dev Environments

**What it is:** Multi-user institutional notebook deployments. JupyterHub, JupyterLab, VS Code Server (code-server), Jupyter AI. Often deployed as the data-science team's shared compute substrate.

**Why it matters for OSINT:** Full RCE class — anyone who reaches an unauth Jupyter has Python execution on the host. Token-based auth often configured but operators mis-share tokens or run with `--allow-root`. Multi-user institutional deployments (universities, research labs) are particularly common targets.

**Members:** JupyterHub · JupyterLab · VS Code Server · Jupyter AI

**Status:** Surveyed — see [`jupyter-survey-2026-05.md`](../case-studies/commercial/jupyter-survey-2026-05.md).

---

## Dev-Tooling AI / Coding Agents

**What it is:** Server-side code-completion + AI-augmented IDE backends. Tabby self-hosted, Refact, self-hosted Sourcegraph Cody backend, Continue.dev servers, OpenDevin / Devon agent backends, Devstral self-hosted.

**Why it matters for OSINT:** Codebase indexes and completion history exposure. Sourcegraph Cody specifically: code-context exfil + sometimes private-repo access via Cody session tokens. OpenDevin / Devon: autonomous-agent control + sandbox escape if Docker-on-host wired in.

**Members:** Tabby · Refact · Sourcegraph Cody · Continue.dev · OpenDevin · Devon · Devstral

**Status:** Not yet surveyed standalone.

---

## Backup & Snapshot Services

**What it is:** Backup orchestrators, snapshot-restore tools, and persistent-volume managers — Velero, restic REST server, Barman (Postgres), Longhorn. Adjacent to Object Storage but distinct: these manage *recovery state*, not just bulk blobs.

**Why it matters for OSINT:** Model weights and training data in unprotected snapshots — the 2026-05 backup survey found 269 GB of Qdrant snapshots exposed across the surveyed range. Snapshots also leak operational state at point-in-time: stale credentials, deprecated API keys still live in older snapshot generations, internal hostnames captured at backup time.

**Members:** Velero · restic REST · Barman · Longhorn

**Status:** Surveyed — see [`backup-snapshot-services-survey-2026-05.md`](../case-studies/commercial/backup-snapshot-services-survey-2026-05.md).

---

## Credential & Config Leaks

**What it is:** Provider API keys, service account tokens, and config files left publicly accessible. `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GROQ_API_KEY`, `HF_TOKEN`, AWS access keys, GCS service-account JSON. Found in `.env` files, public S3 buckets, exposed `/api/config` endpoints, GitHub-public commits, Pastebin paste history.

**Why it matters for OSINT:** This is the bridge tier between AI-stack OSINT and classic credential-discovery work. A leaked Anthropic key is functionally identical in impact to an unauth LLM gateway pointing at that key — both result in burnable provider quota. Search via Shodan dorks for the key prefix, GitHub via TruffleHog/git-secrets, paste-site monitoring.

**Members:** Provider API key prefixes (`sk-`, `sk-ant-`, `gsk_`, `hf_`, etc.) · `.env` files · service account JSON

**Status:** Documented in [`shodan/queries/11-credential-leaks.md`](../shodan/queries/11-credential-leaks.md).

---

## Specialty Domains

**What it is:** Vertical-specific AI deployments outside the cloud-VPS substrate. NVIDIA Clara (medical AI), MONAI Deploy (medical imaging), ROS interfaces (robot fleet control — port 11311 master, 9090 rosbridge), TensorRT inference servers, Jetson edge endpoints.

**Why it matters for OSINT:** Higher disclosure stakes per finding. Medical AI exposure is HIPAA territory. ROS exposure is actuator-control over physical robots (factory floor / autonomous vehicle / warehouse). Jetson endpoints are sensor-fusion edge devices, often deployed in physical-security contexts.

**Members:** NVIDIA Clara · MONAI Deploy · ROS · TensorRT · Jetson edge endpoints

**Status:** Not yet surveyed; documented in [`FUTURE-SURVEYS.md`](../case-studies/commercial/FUTURE-SURVEYS.md#specialty-domains). Approach with elevated ethics-flag handling — `aimap-profile --mode full` first.

---

## How to use this taxonomy

When investigating a new exposed service, ask: **which category does this fit into?** That answers downstream questions:

- **What's the auth-off-default base rate?** (Class-A infrastructure-tier ≈ 100%, applications-for-end-users tier ≈ 0%, specialty data layers ≈ mixed.)
- **What's the per-host data sensitivity?** (Vector DB = embeddings, OLAP = structured rows, agent platform = embedded credentials, etc.)
- **What aimap fingerprint does it match?** (Cross-reference [`aimap`](https://github.com/Nicholas-Kloster/aimap) fingerprints by category.)
- **Where do similar instances live?** (Cross-reference the relevant [`shodan/queries/`](../shodan/queries/) file.)
- **What's the disclosure shape?** (Surveyed-category disclosures follow the templates in [`case-studies/commercial/disclosure/`](../case-studies/commercial/disclosure/); first-of-category disclosures benefit from the methodology lessons in [`SYNTHESIS-2026-05.md`](../case-studies/commercial/SYNTHESIS-2026-05.md).)

When a target *doesn't* fit any category cleanly, that's worth flagging — either the taxonomy needs a new entry, or the target is operationally unusual. The Canton Foundation case (custom Node.js API wrapping DuckDB to serve a blockchain-explorer ML classifier) initially didn't fit; it's now the canonical example for [Specialty Data Layers](#specialty-data-layers) and the inflection point that motivated this taxonomy doc.

---

## See also

- [`reference/terminology.md`](terminology.md) — glossary of cross-cutting terms
- [`reference/ports.md`](ports.md) — port-based quick reference
- [`shodan/queries/`](../shodan/queries/) — Shodan dorks per category
- [`case-studies/commercial/`](../case-studies/commercial/) — survey results per category
- [`case-studies/commercial/SYNTHESIS-2026-05.md`](../case-studies/commercial/SYNTHESIS-2026-05.md) — cross-survey synthesis with methodology insights
- [`case-studies/commercial/FUTURE-SURVEYS.md`](../case-studies/commercial/FUTURE-SURVEYS.md) — not-yet-surveyed roadmap by category
