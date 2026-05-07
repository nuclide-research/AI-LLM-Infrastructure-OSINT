# Shodan Queries: AI/ML Infrastructure

Living catalogue of Shodan dorks for fingerprinting exposed AI/ML control-plane infrastructure.

**Polished PDF reference:** [Shodan_AI_Reference.pdf](Shodan_AI_Reference.pdf), _v2.1, April 2026 (markdown ahead at v2.2)_
**Living markdown source:** see [`queries/`](queries/), these are the files to PR against.

## How to Read the Tables

Every query is tagged with an exposure tier. Tiers let you triage Shodan result sets without re-deriving risk for every entry.

| Tier | Meaning | How to use |
|---|---|---|
| **T1** | Unauthenticated by default | Service ships with no auth, or trivially-bypassed auth. A positive hit is typically a live, interactive target. Treat as immediately actionable. |
| **T2** | Requires misconfiguration | Service has auth by default but is commonly deployed without it, or has known auth-bypass CVEs. Positive hits need one additional probe to confirm exposure. |
| **T3** | Recon / fingerprint only | Identifies the presence of the service. Does not indicate auth status. Use for inventory, trend analysis, and pivoting. |

## Index

| # | Category | Examples |
|---|---|---|
| 1 | [LLM Orchestration Platforms](queries/01-llm-orchestration.md) | Flowise, Langflow, Dify, Open WebUI, Ollama, n8n, Clawdbot |
| 2 | [Vector Databases](queries/02-vector-databases.md) | ChromaDB, Qdrant, Weaviate, Milvus, pgvector, **MinIO/Harbor (artifact stores)** |
| 3 | [Model Serving & Inference](queries/03-model-serving.md) | vLLM, Triton, TGI, llama.cpp, LM Studio, GPT4All, NVIDIA NIM |
| 4 | [Training, Fine-Tuning & Experiments](queries/04-training-experiments.md) | MLflow, Kubeflow, Ray, ClearML, Argilla, Feast |
| 5 | [AI Gateways, Proxies & Monitoring](queries/05-gateways-monitoring.md) | LiteLLM, Portkey, Langfuse, Helicone |
| 6 | [Agent Frameworks](queries/06-agent-frameworks.md) | SuperAGI, OpenDevin, MetaGPT, Clawdbot, AutoGen |
| 7 | [RAG Stacks & Self-Hosted AI Apps](queries/07-rag-stacks.md) _(new)_ | h2oGPT, Danswer/Onyx, Quivr, Khoj, RAGFlow, LibreChat |
| 8 | [Image Generation & Diffusion](queries/08-image-generation.md) _(new)_ | ComfyUI, Stable Diffusion, AUTOMATIC1111, InvokeAI, Fooocus |
| 9 | [AI Code Assistants](queries/09-code-assistants.md) _(new)_ | Tabby, self-hosted Cody, Continue, Refact, FauxPilot |
| 10 | [MCP Servers](queries/10-mcp-servers.md) _(new)_ | Model Context Protocol over HTTP/SSE, filesystem, shell, DB tool surfaces |
| 11 | [Credential Leaks & Misconfigs](queries/11-credential-leaks.md) | OpenAI/Anthropic/Groq/Gemini keys, `.env` exposure, HF tokens |
| 12 | [Container & Orchestration Infrastructure](queries/12-containers.md) _(expanded)_ | Docker daemon, Kubernetes, kubelet, etcd, Consul, Vault |
| 13 | [Backup / Snapshot Exposure](queries/13-backup-snapshot.md) _(new)_ | Qdrant snapshots, Weaviate backups, ES snapshots, HTTP-served dumps |
| 14 | [GPU & Compute Dashboards](queries/14-gpu-compute.md) | NVIDIA DCGM, RunPod, Vast.ai, GPUStack |
| 15 | [Fingerprinting Canaries](queries/15-fingerprinting.md) | Favicon hashes, generic FastAPI/OpenAI-style detection |
| A | [Appendix, High-Severity CVE Cross-Reference](queries/appendix-cve.md) _(new)_ | Ray, MLflow, Flowise, Ollama, ComfyUI, kubelet, etc. |

## Search across all queries

```bash
grep -rn "qdrant"   queries/
grep -rn "port:8000" queries/
grep -rn "API_KEY"  queries/
grep -rn " T1 "     queries/    # all T1 (unauth-by-default) queries
```

## Adding a new query

1. Find the category file it belongs in (or open an issue to propose a new category).
2. Add a row to the appropriate Markdown table, include a tier (T1/T2/T3).
3. Add a `Notes` cell when the query reveals something specific, auth state, version, snapshot exposure, default credentials.
4. Open a PR. See [CONTRIBUTING.md](../CONTRIBUTING.md).

## Versioning

The PDF reference is regenerated periodically from the markdown sources. Check the date on the cover page; the markdown is always more current.

**Current PDF:** v2.1 · April 2026
- v2.0 added four new sections (RAG Stacks, Image Generation, AI Code Assistants, MCP Servers), expanded Container/Orchestration to cover k8s/kubelet/etcd/Docker Registry v2, tagged every query with an exposure tier, and added Appendix A.
- v2.1 folds in a new Object Storage & Artifact Stores subsection under Vector Databases (MinIO, Harbor, image registries where AI models, vectors, and snapshots live), adds ClickHouse / Cassandra / txtai / Feast / Tecton entries, introduces GPT4All / NVIDIA NIM / AutoGen coverage, and ships a [terminology primer](../reference/terminology.md) for readers newer to the stack.
- v2.2 adds Audio/Speech/Vision inference (whisper.cpp, faster-whisper, Coqui, Piper, Bark, Vocode, PaddleOCR) + SGLang / LMDeploy / Aphrodite / Seldon under §3; Dagster, Weights & Biases self-hosted, wandb-local, CVAT, Doccano, Humanloop, Kubeflow Pipelines under §4; PromptLayer, Kong/Tyk AI plugins, Unify router under §5; OpenHands and AutoGPT-Next-Web under §6; a transport-agnostic MCP `jsonrpc`/`tools/list` fingerprint under §10; and Mistral / DeepSeek / raw `sk-ant-` key leaks plus `.claude/settings.json` exposure under §11.
