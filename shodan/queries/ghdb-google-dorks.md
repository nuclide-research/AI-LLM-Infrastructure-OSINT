# AI/LLM Infrastructure — Google Dork Catalog (GHDB Format)

_Generated 2026-05-31. 1003 dorks across 11 GHDB categories._
_Method: GHDB operator grammar (7,943-entry corpus) × verified service fingerprints from this repo's surveys._

**Tiers:** 🟡 gold 493 (low-FP, ready) · ⚪ silver 313 (useful, review) · 🟤 bronze 197 (broad/noisy). **CVE-mapped:** 186.

> Hit counts referenced in notes are candidate population from Shodan surveys, not verified findings. Verification is still required per repo methodology. Interactive clickable version: [`ghdb-ai-dorks.html`](ghdb-ai-dorks.html). Raw data: [`data/ghdb-ai-dorks.json`](data/ghdb-ai-dorks.json).

---

## Footholds
_309 dorks_

| T | Dork | Service | CVE | Notes |
|---|------|---------|-----|-------|
| 🟡 | `allintitle:"AgentGPT"` | AgentGPT |  | AgentGPT strict title match (low FP). |
| 🟡 | `allintitle:"Amundsen"` | Amundsen |  | Amundsen strict title match (low FP). |
| 🟡 | `allintitle:"Anduril Lattice - Login"` | Anduril Lattice |  | Anduril Lattice strict title match (low FP). |
| 🟡 | `allintitle:"AnythingLLM"` | AnythingLLM |  | AnythingLLM strict title match (low FP). |
| 🟡 | `intitle:"Airflow"` | Apache Airflow | CVE-2020-13927 | Apache Airflow (workflow_orchestration). auth on with 8 documented bypass patterns |
| 🟡 | `allintitle:"Airflow"` | Apache Airflow | CVE-2020-13927 | Apache Airflow strict title match (low FP). |
| 🟡 | `intitle:"Airflow" -site:airflow.apache.org -site:github.com` | Apache Airflow | CVE-2020-13927 | Self-hosted Apache Airflow only; vendor + source excluded. auth on with 8 documented bypass patterns |
| 🟡 | `allintitle:"DolphinScheduler"` | Apache DolphinScheduler |  | Apache DolphinScheduler strict title match (low FP). |
| 🟡 | `intitle:"Apache Flink Web Dashboard"` | Apache Flink | CVE-2020-17518 | Apache Flink (workflow_orchestration). no auth by default |
| 🟡 | `allintitle:"Apache Flink Web Dashboard"` | Apache Flink | CVE-2020-17518 | Apache Flink strict title match (low FP). |
| 🟡 | `intitle:"Apache Flink Web Dashboard" -site:flink.apache.org -site:github.com` | Apache Flink | CVE-2020-17518 | Self-hosted Apache Flink only; vendor + source excluded. no auth by default |
| 🟡 | `intitle:"Apache Superset"` | Apache Superset | CVE-2023-27524 | Apache Superset (bi_dashboard). default SECRET_KEY leads to auth bypass |
| 🟡 | `allintitle:"Apache Superset"` | Apache Superset | CVE-2023-27524 | Apache Superset strict title match (low FP). |
| 🟡 | `intitle:"Apache Superset" -site:superset.apache.org -site:github.com` | Apache Superset | CVE-2023-27524 | Self-hosted Apache Superset only; vendor + source excluded. default SECRET_KEY leads to auth bypass |
| 🟡 | `allintitle:"Apache Tika"` | Apache Tika |  | Apache Tika strict title match (low FP). |
| 🟡 | `allintitle:"ArangoDB Web Interface"` | ArangoDB |  | ArangoDB strict title match (low FP). |
| 🟡 | `intitle:"Argilla"` | Argilla | CVE-2023-38686 | Argilla (data_labeling). auth on since v1.x; default-public workspace misconfiguration seen |
| 🟡 | `allintitle:"Argilla"` | Argilla | CVE-2023-38686 | Argilla strict title match (low FP). |
| 🟡 | `intitle:"Argilla" -site:argilla.io -site:github.com` | Argilla | CVE-2023-38686 | Self-hosted Argilla only; vendor + source excluded. auth on since v1.x; default-public workspace misconfiguration seen |
| 🟡 | `intitle:"Argo"` | Argo Workflows | CVE-2026-28229 | Argo Workflows (workflow_orchestration). --auth-mode=server disables all credential requirements |
| 🟡 | `intitle:"Argo" -site:argoproj.github.io -site:github.com` | Argo Workflows | CVE-2026-28229 | Self-hosted Argo Workflows only; vendor + source excluded. --auth-mode=server disables all credential requirements |
| 🟡 | `allintitle:"Arize Phoenix"` | Arize Phoenix |  | Arize Phoenix strict title match (low FP). |
| 🟡 | `allintitle:"Authelia"` | Authelia |  | Authelia strict title match (low FP). |
| 🟡 | `intitle:"authentik"` | Authentik | CVE-2024-47070 | Authentik (gateway_observability). login required; /api/v3/root/config/ pre-auth accessible |
| 🟡 | `allintitle:"authentik"` | Authentik | CVE-2024-47070 | Authentik strict title match (low FP). |
| 🟡 | `intitle:"authentik" -site:goauthentik.io -site:github.com` | Authentik | CVE-2024-47070 | Self-hosted Authentik only; vendor + source excluded. login required; /api/v3/root/config/ pre-auth accessible |
| 🟡 | `allintitle:"AutoGPT"` | AutoGPT |  | AutoGPT strict title match (low FP). |
| 🟡 | `allintitle:"Axolotl"` | Axolotl |  | Axolotl strict title match (low FP). |
| 🟡 | `allintitle:"browserless"` | Browserless |  | Browserless strict title match (low FP). |
| 🟡 | `intitle:"CKAN"` | CKAN | CVE-2023-32321 | CKAN (specialty_data). reads open by design |
| 🟡 | `allintitle:"Cadence"` | Cadence Workflow |  | Cadence Workflow strict title match (low FP). |
| 🟡 | `intitle:"Casdoor"` | Casdoor | CVE-2024-41657 | Casdoor (gateway_observability). default-creds built-in/admin/123 |
| 🟡 | `allintitle:"Casdoor"` | Casdoor | CVE-2024-41657 | Casdoor strict title match (low FP). |
| 🟡 | `allintitle:"ChatTTS"` | ChatTTS |  | ChatTTS strict title match (low FP). |
| 🟡 | `allintitle:"Chatterbox TTS"` | Chatterbox TTS |  | Chatterbox TTS strict title match (low FP). |
| 🟡 | `allintitle:"Chroma"` | ChromaDB |  | ChromaDB strict title match (low FP). |
| 🟡 | `allintitle:"ClearML"` | ClearML |  | ClearML strict title match (low FP). |
| 🟡 | `allintitle:"ClickHouse"` | ClickHouse |  | ClickHouse strict title match (low FP). |
| 🟡 | `allintitle:"Collibra"` | Collibra |  | Collibra strict title match (low FP). |
| 🟡 | `allintitle:"ComfyUI"` | ComfyUI |  | ComfyUI strict title match (low FP). |
| 🟡 | `allintitle:"Dagster"` | Dagster |  | Dagster strict title match (low FP). |
| 🟡 | `allintitle:"DataHub"` | DataHub |  | DataHub strict title match (low FP). |
| 🟡 | `allintitle:"Determined"` | Determined AI |  | Determined AI strict title match (low FP). |
| 🟡 | `allintitle:"Devika"` | Devika |  | Devika strict title match (low FP). |
| 🟡 | `allintitle:"doccano"` | Doccano |  | Doccano strict title match (low FP). |
| 🟡 | `allintitle:"Docling"` | Docling |  | Docling strict title match (low FP). |
| 🟡 | `allintitle:"Evidently - ML Monitoring"` | Evidently ML Monitoring |  | Evidently ML Monitoring strict title match (low FP). |
| 🟡 | `intitle:"Flowise"` | Flowise | CVE-2024-36420 | Flowise (orchestration). mixed auth; pre-1.8.2 auth bypass via path traversal |
| 🟡 | `allintitle:"Flowise"` | Flowise | CVE-2024-36420 | Flowise strict title match (low FP). |
| 🟡 | `intitle:"Flowise" -site:flowiseai.com -site:github.com` | Flowise | CVE-2024-36420 | Self-hosted Flowise only; vendor + source excluded. mixed auth; pre-1.8.2 auth bypass via path traversal |
| 🟡 | `allintitle:"Flyte Console"` | Flyte |  | Flyte strict title match (low FP). |
| 🟡 | `allintitle:"GPT Researcher"` | GPT Researcher |  | GPT Researcher strict title match (low FP). |
| 🟡 | `intitle:"GPT-SoVITS"` | GPT-SoVITS | CVE-2025-49833 | GPT-SoVITS (voice_audio). no auth by default; command injection RCE |
| 🟡 | `allintitle:"GPT-SoVITS"` | GPT-SoVITS | CVE-2025-49833 | GPT-SoVITS strict title match (low FP). |
| 🟡 | `intitle:"GitHub Enterprise"` | GitHub Enterprise Server (GHES) | CVE-2024-9487 | GitHub Enterprise Server (GHES) (code_assistant). OAuth enforced; SAML bypass on affected versions |
| 🟡 | `allintitle:"GitHub Enterprise"` | GitHub Enterprise Server (GHES) | CVE-2024-9487 | GitHub Enterprise Server (GHES) strict title match (low FP). |
| 🟡 | `allintitle:"Gradio"` | Gradio |  | Gradio strict title match (low FP). |
| 🟡 | `intitle:"Grafana"` | Grafana | CVE-2021-43798 | Grafana (bi_dashboard). anonymous access misconfiguration common |
| 🟡 | `allintitle:"Grafana"` | Grafana | CVE-2021-43798 | Grafana strict title match (low FP). |
| 🟡 | `intitle:"Grafana" -site:grafana.com -site:github.com` | Grafana | CVE-2021-43798 | Self-hosted Grafana only; vendor + source excluded. anonymous access misconfiguration common |
| 🟡 | `allintitle:"Data Docs"` | Great Expectations |  | Great Expectations strict title match (low FP). |
| 🟡 | `allintitle:"Harbor"` | Harbor |  | Harbor strict title match (low FP). |
| 🟡 | `allintitle:"Helicone"` | Helicone |  | Helicone strict title match (low FP). |
| 🟡 | `allintitle:"Hopsworks"` | Hopsworks |  | Hopsworks strict title match (low FP). |
| 🟡 | `intitle:"Jupyter"` | Jupyter Notebook / JupyterLab | CVE-2019-10255 | Jupyter Notebook / JupyterLab (notebook). modern deployments consistently locked; older --NotebookApp.token= blank is unauth RCE |
| 🟡 | `allintitle:"Jupyter"` | Jupyter Notebook / JupyterLab | CVE-2019-10255 | Jupyter Notebook / JupyterLab strict title match (low FP). |
| 🟡 | `intitle:"Jupyter" -site:jupyter.org -site:github.com` | Jupyter Notebook / JupyterLab | CVE-2019-10255 | Self-hosted Jupyter Notebook / JupyterLab only; vendor + source excluded. modern deployments consistently locked; older --NotebookApp.token= blank is unauth RCE |
| 🟡 | `intitle:"JupyterHub"` | JupyterHub | CVE-2026-33709 | JupyterHub (notebook). auth on by default since v1.x |
| 🟡 | `allintitle:"JupyterHub"` | JupyterHub | CVE-2026-33709 | JupyterHub strict title match (low FP). |
| 🟡 | `intitle:"JupyterHub" -site:jupyter.org -site:github.com` | JupyterHub | CVE-2026-33709 | Self-hosted JupyterHub only; vendor + source excluded. auth on by default since v1.x |
| 🟡 | `allintitle:"Kestra"` | Kestra |  | Kestra strict title match (low FP). |
| 🟡 | `intitle:"Keycloak"` | Keycloak | CVE-2024-3656 | Keycloak (gateway_observability). login required for admin; OIDC discovery endpoints unauthenticated |
| 🟡 | `allintitle:"Keycloak"` | Keycloak | CVE-2024-3656 | Keycloak strict title match (low FP). |
| 🟡 | `intitle:"Keycloak" -site:keycloak.org -site:github.com` | Keycloak | CVE-2024-3656 | Self-hosted Keycloak only; vendor + source excluded. login required for admin; OIDC discovery endpoints unauthenticated |
| 🟡 | `allintitle:"Kibana"` | Kibana |  | Kibana strict title match (low FP). |
| 🟡 | `allintitle:"Kokoro"` | Kokoro TTS / Kokoro-FastAPI |  | Kokoro TTS / Kokoro-FastAPI strict title match (low FP). |
| 🟡 | `allintitle:"Kong Manager"` | Kong AI Gateway |  | Kong AI Gateway strict title match (low FP). |
| 🟡 | `allintitle:"Kubeflow Central Dashboard"` | Kubeflow |  | Kubeflow strict title match (low FP). |
| 🟡 | `allintitle:"LLaMA Factory"` | LLaMA Factory |  | LLaMA Factory strict title match (low FP). |
| 🟡 | `intitle:"Label Studio"` | Label Studio | CVE-2022-25011 | Label Studio (data_labeling). mandatory auth; /api/projects sometimes misconfigured readable |
| 🟡 | `allintitle:"Label Studio"` | Label Studio | CVE-2022-25011 | Label Studio strict title match (low FP). |
| 🟡 | `intitle:"Label Studio" -site:labelstud.io -site:github.com` | Label Studio | CVE-2022-25011 | Self-hosted Label Studio only; vendor + source excluded. mandatory auth; /api/projects sometimes misconfigured readable |
| 🟡 | `allintitle:"LangGraph"` | LangGraph Server |  | LangGraph Server strict title match (low FP). |
| 🟡 | `allintitle:"LangSmith"` | LangSmith |  | LangSmith strict title match (low FP). |
| 🟡 | `intitle:"Langflow"` | Langflow | CVE-2026-33017 | Langflow (orchestration). LANGFLOW_AUTO_LOGIN gating in v1.5+, often left open |
| 🟡 | `allintitle:"Langflow"` | Langflow | CVE-2026-33017 | Langflow strict title match (low FP). |
| 🟡 | `intitle:"Langflow" -site:langflow.org -site:datastax.com -site:github.com` | Langflow | CVE-2026-33017 | Self-hosted Langflow only; vendor + source excluded. LANGFLOW_AUTO_LOGIN gating in v1.5+, often left open |
| 🟡 | `allintitle:"LibreChat"` | LibreChat |  | LibreChat strict title match (low FP). |
| 🟡 | `allintitle:"LiteLLM"` | LiteLLM |  | LiteLLM strict title match (low FP). |
| 🟡 | `allintitle:"LiveKit"` | LiveKit Agents |  | LiveKit Agents strict title match (low FP). |
| 🟡 | `allintitle:"Create Llama App"` | LlamaIndex / Create Llama App |  | LlamaIndex / Create Llama App strict title match (low FP). |
| 🟡 | `intitle:"MLflow"` | MLflow | CVE-2024-37052 | MLflow (training_experiment). no auth by default |
| 🟡 | `allintitle:"MLflow"` | MLflow | CVE-2024-37052 | MLflow strict title match (low FP). |
| 🟡 | `intitle:"MLflow" -site:mlflow.org -site:databricks.com -site:github.com` | MLflow | CVE-2024-37052 | Self-hosted MLflow only; vendor + source excluded. no auth by default |
| 🟡 | `intitle:"Mage"` | Mage.ai | CVE-2025-2129 | Mage.ai (workflow_orchestration). no auth pre-v0.9.78; ~1,045 confirmed unauth at disclosure |
| 🟡 | `intitle:"Mage" -site:mage.ai -site:github.com` | Mage.ai | CVE-2025-2129 | Self-hosted Mage.ai only; vendor + source excluded. no auth pre-v0.9.78; ~1,045 confirmed unauth at disclosure |
| 🟡 | `allintitle:"Marquez"` | Marquez (OpenLineage) |  | Marquez (OpenLineage) strict title match (low FP). |
| 🟡 | `allintitle:"Memgraph Lab"` | Memgraph |  | Memgraph strict title match (low FP). |
| 🟡 | `allintitle:"MetaGPT"` | MetaGPT |  | MetaGPT strict title match (low FP). |
| 🟡 | `intitle:"Metabase"` | Metabase | CVE-2023-38646 | Metabase (bi_dashboard). setup-wizard bypass; has-user-setup: false = exploitable |
| 🟡 | `allintitle:"Metabase"` | Metabase | CVE-2023-38646 | Metabase strict title match (low FP). |
| 🟡 | `intitle:"Metabase" -site:metabase.com -site:github.com` | Metabase | CVE-2023-38646 | Self-hosted Metabase only; vendor + source excluded. setup-wizard bypass; has-user-setup: false = exploitable |
| 🟡 | `intitle:"MinIO Browser"` | MinIO | CVE-2023-28432 | MinIO (container). default-creds minioadmin:minioadmin |
| 🟡 | `allintitle:"MinIO Browser"` | MinIO | CVE-2023-28432 | MinIO strict title match (low FP). |
| 🟡 | `intitle:"MinIO Browser" -site:min.io -site:github.com` | MinIO | CVE-2023-28432 | Self-hosted MinIO only; vendor + source excluded. default-creds minioadmin:minioadmin |
| 🟡 | `intitle:"Conductor UI"` | Netflix Conductor | CVE-2020-9296 | Netflix Conductor (workflow_orchestration). no auth by default |
| 🟡 | `allintitle:"Conductor UI"` | Netflix Conductor | CVE-2020-9296 | Netflix Conductor strict title match (low FP). |
| 🟡 | `allintitle:"Open WebUI"` | Open WebUI |  | Open WebUI strict title match (low FP). |
| 🟡 | `allintitle:"Clawdbot Control"` | OpenClaw / Clawdbot |  | OpenClaw / Clawdbot strict title match (low FP). |
| 🟡 | `allintitle:"OpenHands"` | OpenHands (formerly OpenDevin) |  | OpenHands (formerly OpenDevin) strict title match (low FP). |
| 🟡 | `allintitle:"OpenMemory"` | OpenMemory UI (mem0) |  | OpenMemory UI (mem0) strict title match (low FP). |
| 🟡 | `intitle:"OpenMetadata"` | OpenMetadata | CVE-2024-28255 | OpenMetadata (specialty_data). auth on but CVE-2024-28255 bypass on <1.3.1; actively exploited |
| 🟡 | `allintitle:"OpenMetadata"` | OpenMetadata | CVE-2024-28255 | OpenMetadata strict title match (low FP). |
| 🟡 | `allintitle:"OpenSearch Dashboards"` | OpenSearch |  | OpenSearch strict title match (low FP). |
| 🟡 | `allintitle:"OpenVoice"` | OpenVoice |  | OpenVoice strict title match (low FP). |
| 🟡 | `allintitle:"Optuna Dashboard"` | Optuna Dashboard |  | Optuna Dashboard strict title match (low FP). |
| 🟡 | `allintitle:"Orpheus TTS"` | Orpheus-FastAPI TTS |  | Orpheus-FastAPI TTS strict title match (low FP). |
| 🟡 | `allintitle:"Orthanc Explorer"` | Orthanc DICOM Server |  | Orthanc DICOM Server strict title match (low FP). |
| 🟡 | `allintitle:"Perplexica"` | Perplexica |  | Perplexica strict title match (low FP). |
| 🟡 | `allintitle:"Pipecat"` | Pipecat |  | Pipecat strict title match (low FP). |
| 🟡 | `allintitle:"Playwright"` | Playwright MCP Server |  | Playwright MCP Server strict title match (low FP). |
| 🟡 | `allintitle:"Portkey"` | Portkey |  | Portkey strict title match (low FP). |
| 🟡 | `allintitle:"Prefect Server"` | Prefect Server |  | Prefect Server strict title match (low FP). |
| 🟡 | `allintitle:"PromptLayer"` | PromptLayer |  | PromptLayer strict title match (low FP). |
| 🟡 | `allintitle:"promptfoo"` | Promptfoo |  | Promptfoo strict title match (low FP). |
| 🟡 | `allintitle:"Qdrant"` | Qdrant |  | Qdrant strict title match (low FP). |
| 🟡 | `intitle:"RVC"` | RVC (Retrieval-based Voice Conversion) | CVE-2025-43842 | RVC (Retrieval-based Voice Conversion) (voice_audio). no auth by default; RCE via pickle deserialization |
| 🟡 | `intitle:"Ray Dashboard"` | Ray Dashboard | CVE-2023-48022 | Ray Dashboard (training_experiment). no auth; ShadowRay actively exploited |
| 🟡 | `allintitle:"Ray Dashboard"` | Ray Dashboard | CVE-2023-48022 | Ray Dashboard strict title match (low FP). |
| 🟡 | `intitle:"Ray Dashboard" -site:ray.io -site:anyscale.com -site:github.com` | Ray Dashboard | CVE-2023-48022 | Self-hosted Ray Dashboard only; vendor + source excluded. no auth; ShadowRay actively exploited |
| 🟡 | `allintitle:"Redash"` | Redash |  | Redash strict title match (low FP). |
| 🟡 | `intitle:"RedisInsight"` | Redis | CVE-2025-49844 | Redis (vector_db). no password by default on ~68k of 245k instances |
| 🟡 | `allintitle:"RedisInsight"` | Redis | CVE-2025-49844 | Redis strict title match (low FP). |
| 🟡 | `intitle:"RedisInsight" -site:redis.io -site:github.com` | Redis | CVE-2025-49844 | Self-hosted Redis only; vendor + source excluded. no password by default on ~68k of 245k instances |
| 🟡 | `allintitle:"Refact"` | Refact.ai (self-hosted) |  | Refact.ai (self-hosted) strict title match (low FP). |
| 🟡 | `allintitle:"Omniboard"` | Sacred / Omniboard |  | Sacred / Omniboard strict title match (low FP). |
| 🟡 | `allintitle:"Seldon"` | Seldon Core |  | Seldon Core strict title match (low FP). |
| 🟡 | `allintitle:"Selenium Grid"` | Selenium Grid |  | Selenium Grid strict title match (low FP). |
| 🟡 | `allintitle:"Selenoid"` | Selenoid |  | Selenoid strict title match (low FP). |
| 🟡 | `allintitle:"Sourcebot"` | Sourcebot |  | Sourcebot strict title match (low FP). |
| 🟡 | `allintitle:"Sourcegraph"` | Sourcegraph / Cody |  | Sourcegraph / Cody strict title match (low FP). |
| 🟡 | `allintitle:"History Server"` | Spark History Server |  | Spark History Server strict title match (low FP). |
| 🟡 | `allintitle:"SpeechBrain"` | SpeechBrain |  | SpeechBrain strict title match (low FP). |
| 🟡 | `allintitle:"Stable Diffusion"` | Stable Diffusion WebUI (AUTOMATIC1111) |  | Stable Diffusion WebUI (AUTOMATIC1111) strict title match (low FP). |
| 🟡 | `allintitle:"Streamlit"` | Streamlit |  | Streamlit strict title match (low FP). |
| 🟡 | `allintitle:"Supabase Studio"` | Supabase |  | Supabase strict title match (low FP). |
| 🟡 | `allintitle:"SuperAGI"` | SuperAGI |  | SuperAGI strict title match (low FP). |
| 🟡 | `allintitle:"Temporal"` | Temporal Workflow |  | Temporal Workflow strict title match (low FP). |
| 🟡 | `allintitle:"TensorBoard"` | TensorBoard |  | TensorBoard strict title match (low FP). |
| 🟡 | `allintitle:"Tortoise"` | Tortoise TTS |  | Tortoise TTS strict title match (low FP). |
| 🟡 | `allintitle:"TruLens"` | TruLens |  | TruLens strict title match (low FP). |
| 🟡 | `allintitle:"Unstructured"` | Unstructured API |  | Unstructured API strict title match (low FP). |
| 🟡 | `allintitle:"Weaviate"` | Weaviate |  | Weaviate strict title match (low FP). |
| 🟡 | `allintitle:"Weights & Biases"` | Weights & Biases (W&B) |  | Weights & Biases (W&B) strict title match (low FP). |
| 🟡 | `allintitle:"Whisper"` | Whisper ASR |  | Whisper ASR strict title match (low FP). |
| 🟡 | `allintitle:"Windmill"` | Windmill |  | Windmill strict title match (low FP). |
| 🟡 | `allintitle:"Xinference"` | Xinference |  | Xinference strict title match (low FP). |
| 🟡 | `allintitle:"ZITADEL"` | Zitadel |  | Zitadel strict title match (low FP). |
| 🟡 | `allintitle:"dcm4chee Archive UI"` | dcm4chee Archive |  | dcm4chee Archive strict title match (low FP). |
| 🟡 | `intitle:"n8n"` | n8n | CVE-2024-25289 | n8n (workflow_orchestration). basicauth optional and frequently skipped |
| 🟡 | `intitle:"n8n" -site:n8n.io -site:n8n.cloud -site:github.com` | n8n | CVE-2024-25289 | Self-hosted n8n only; vendor + source excluded. basicauth optional and frequently skipped |
| 🟡 | `allintitle:"pgAdmin"` | pgAdmin |  | pgAdmin strict title match (low FP). |
| 🟡 | `allintitle:"SoftVC"` | so-vits-svc |  | so-vits-svc strict title match (low FP). |
| ⚪ | `intitle:"AgentGPT"` | AgentGPT |  | AgentGPT (agent_framework). full population open-access; 0 auth-gated |
| ⚪ | `intitle:"Amundsen"` | Amundsen |  | Amundsen (specialty_data). auth absent unless flaskoidc manually configured |
| ⚪ | `intitle:"Anduril Lattice - Login"` | Anduril Lattice |  | Anduril Lattice (agent_framework). Envoy + SAML auth |
| ⚪ | `intitle:"AnythingLLM"` | AnythingLLM |  | AnythingLLM (rag_stack). known auth bypass history; single-user mode ships with password protect disabled |
| ⚪ | `intitle:"DolphinScheduler"` | Apache DolphinScheduler |  | Apache DolphinScheduler (workflow_orchestration). default-creds admin/dolphinscheduler123 |
| ⚪ | `intitle:"Apache Tika"` | Apache Tika |  | Apache Tika (gateway_observability). SSRF history; arbitrary file read |
| ⚪ | `intitle:"ArangoDB Web Interface"` | ArangoDB |  | ArangoDB (vector_db). auth defaults to false |
| ⚪ | `intitle:"Arize Phoenix"` | Arize Phoenix |  | Arize Phoenix (gateway_observability). no auth, --host 0.0.0.0 default |
| ⚪ | `intitle:"Arize Phoenix" -site:arize.com -site:github.com` | Arize Phoenix |  | Self-hosted Arize Phoenix only; vendor + source excluded. no auth, --host 0.0.0.0 default |
| ⚪ | `intitle:"Authelia"` | Authelia |  | Authelia (gateway_observability). login portal to all downstream services |
| ⚪ | `intitle:"browserless"` | Browserless |  | Browserless (agent_framework). no auth concept |
| ⚪ | `intitle:"CVAT" -site:cvat.ai -site:github.com` | CVAT |  | Self-hosted CVAT only; vendor + source excluded. auth on by default |
| ⚪ | `intitle:"Chatterbox TTS"` | Chatterbox TTS |  | Chatterbox TTS (voice_audio). no auth; /upload_reference unauth on both variants |
| ⚪ | `intitle:"Chroma" -site:trychroma.com -site:github.com` | ChromaDB |  | Self-hosted ChromaDB only; vendor + source excluded. no auth by default |
| ⚪ | `intitle:"ClearML" -site:clear.ml -site:github.com` | ClearML |  | Self-hosted ClearML only; vendor + source excluded. ships with free access login; explicit opt-in required for real auth |
| ⚪ | `intitle:"ClickHouse"` | ClickHouse |  | ClickHouse (specialty_data). default user ships with empty password |
| ⚪ | `intitle:"ClickHouse" -site:clickhouse.com -site:github.com` | ClickHouse |  | Self-hosted ClickHouse only; vendor + source excluded. default user ships with empty password |
| ⚪ | `intitle:"Collibra"` | Collibra |  | Collibra (specialty_data). default-creds Admin/Admin |
| ⚪ | `intitle:"Dagster" -site:dagster.io -site:github.com` | Dagster |  | Self-hosted Dagster only; vendor + source excluded. no auth since 2020; runConfigYaml exposes all credentials |
| ⚪ | `intitle:"Determined"` | Determined AI |  | Determined AI (training_experiment). default-creds admin with blank password |
| ⚪ | `intitle:"Dify" -site:dify.ai -site:github.com` | Dify |  | Self-hosted Dify only; vendor + source excluded. login-gated but version leaks in headers |
| ⚪ | `intitle:"Evidently - ML Monitoring"` | Evidently ML Monitoring |  | Evidently ML Monitoring (gateway_observability). no auth concept in default deploy |
| ⚪ | `intitle:"Flyte Console"` | Flyte |  | Flyte (workflow_orchestration). useAuth:false in defaults; MinIO default creds |
| ⚪ | `intitle:"GPT Researcher"` | GPT Researcher |  | GPT Researcher (agent_framework). all direct-deployment population openly accessible |
| ⚪ | `intitle:"Data Docs"` | Great Expectations |  | Great Expectations (specialty_data). no auth when Data Docs served externally |
| ⚪ | `intitle:"Harbor" -site:goharbor.io -site:github.com` | Harbor |  | Self-hosted Harbor only; vendor + source excluded. auth on by default |
| ⚪ | `intitle:"Helicone"` | Helicone |  | Helicone (gateway_observability). None |
| ⚪ | `intitle:"Helicone" -site:helicone.ai -site:github.com` | Helicone |  | Self-hosted Helicone only; vendor + source excluded. None |
| ⚪ | `intitle:"Hopsworks"` | Hopsworks |  | Hopsworks (specialty_data). default-creds admin@kth.se/admin |
| ⚪ | `intitle:"Kestra" -site:kestra.io -site:github.com` | Kestra |  | Self-hosted Kestra only; vendor + source excluded. auth off pre-v0.24.0 |
| ⚪ | `intitle:"Kibana" -site:elastic.co -site:github.com` | Kibana |  | Self-hosted Kibana only; vendor + source excluded. None |
| ⚪ | `intitle:"Kong Manager"` | Kong AI Gateway |  | Kong AI Gateway (gateway_observability). admin API no auth when bound to 0.0.0.0 |
| ⚪ | `intitle:"Kong Manager" -site:konghq.com -site:github.com` | Kong AI Gateway |  | Self-hosted Kong AI Gateway only; vendor + source excluded. admin API no auth when bound to 0.0.0.0 |
| ⚪ | `intitle:"Kubeflow Central Dashboard"` | Kubeflow |  | Kubeflow (training_experiment). single-user mode no auth |
| ⚪ | `intitle:"Kubeflow Central Dashboard" -site:kubeflow.org -site:github.com` | Kubeflow |  | Self-hosted Kubeflow only; vendor + source excluded. single-user mode no auth |
| ⚪ | `intitle:"LLaMA Factory"` | LLaMA Factory |  | LLaMA Factory (training_experiment). None |
| ⚪ | `intitle:"LangGraph"` | LangGraph Server |  | LangGraph Server (agent_framework). no authentication in default configuration |
| ⚪ | `intitle:"LangGraph" -site:langchain.com -site:github.com` | LangGraph Server |  | Self-hosted LangGraph Server only; vendor + source excluded. no authentication in default configuration |
| ⚪ | `intitle:"LangSmith"` | LangSmith |  | LangSmith (gateway_observability). auth-off on pre-v0.10 deployments |
| ⚪ | `intitle:"LangSmith" -site:langchain.com -site:github.com` | LangSmith |  | Self-hosted LangSmith only; vendor + source excluded. auth-off on pre-v0.10 deployments |
| ⚪ | `intitle:"LibreChat"` | LibreChat |  | LibreChat (rag_stack). multi-provider chat UI, often unauth |
| ⚪ | `intitle:"LibreChat" -site:librechat.ai -site:github.com` | LibreChat |  | Self-hosted LibreChat only; vendor + source excluded. multi-provider chat UI, often unauth |
| ⚪ | `intitle:"LiteLLM" -site:litellm.ai -site:berri.ai -site:github.com` | LiteLLM |  | Self-hosted LiteLLM only; vendor + source excluded. master key often leaked in env |
| ⚪ | `intitle:"Create Llama App"` | LlamaIndex / Create Llama App |  | LlamaIndex / Create Llama App (rag_stack). None |
| ⚪ | `intitle:"Memgraph Lab"` | Memgraph |  | Memgraph (vector_db). None |
| ⚪ | `intitle:"Attu" -site:milvus.io -site:zilliz.com -site:github.com` | Milvus |  | Self-hosted Milvus only; vendor + source excluded. no auth on Attu admin UI |
| ⚪ | `intitle:"Open WebUI"` | Open WebUI |  | Open WebUI (orchestration). first-user-admin, effectively unauth on fresh deploys |
| ⚪ | `intitle:"Open WebUI" -site:openwebui.com -site:github.com` | Open WebUI |  | Self-hosted Open WebUI only; vendor + source excluded. first-user-admin, effectively unauth on fresh deploys |
| ⚪ | `intitle:"Clawdbot Control"` | OpenClaw / Clawdbot |  | OpenClaw / Clawdbot (agent_framework). no auth; shell execution, browser automation, email send, calendar write |
| ⚪ | `intitle:"OpenHands"` | OpenHands (formerly OpenDevin) |  | OpenHands (formerly OpenDevin) (agent_framework). 0% auth-gated; entire population openly accessible |
| ⚪ | `intitle:"OpenHands" -site:all-hands.dev -site:github.com` | OpenHands (formerly OpenDevin) |  | Self-hosted OpenHands (formerly OpenDevin) only; vendor + source excluded. 0% auth-gated; entire population openly accessible |
| ⚪ | `intitle:"OpenMemory"` | OpenMemory UI (mem0) |  | OpenMemory UI (mem0) (rag_stack). no auth by default |
| ⚪ | `intitle:"OpenSearch Dashboards"` | OpenSearch |  | OpenSearch (search_data). None |
| ⚪ | `intitle:"OpenSearch Dashboards" -site:opensearch.org -site:github.com` | OpenSearch |  | Self-hosted OpenSearch only; vendor + source excluded. None |
| ⚪ | `intitle:"OpenVoice"` | OpenVoice |  | OpenVoice (voice_audio). no auth by default |
| ⚪ | `intitle:"Optuna Dashboard"` | Optuna Dashboard |  | Optuna Dashboard (training_experiment). no auth when containerized |
| ⚪ | `intitle:"Orpheus TTS"` | Orpheus-FastAPI TTS |  | Orpheus-FastAPI TTS (voice_audio). no auth by default |
| ⚪ | `intitle:"Orthanc Explorer"` | Orthanc DICOM Server |  | Orthanc DICOM Server (medical_edge). no auth by default; PHI exposure |
| ⚪ | `intitle:"Perplexica"` | Perplexica |  | Perplexica (rag_stack). no auth; developer advisory against public exposure |
| ⚪ | `intitle:"Playwright"` | Playwright MCP Server |  | Playwright MCP Server (mcp). no auth by default |
| ⚪ | `intitle:"Portkey" -site:portkey.ai -site:github.com` | Portkey |  | Self-hosted Portkey only; vendor + source excluded. provider API keys in config |
| ⚪ | `intitle:"Prefect Server"` | Prefect Server |  | Prefect Server (workflow_orchestration). PREFECT_SERVER_API_AUTH_STRING not set by default |
| ⚪ | `intitle:"Prefect Server" -site:prefect.io -site:github.com` | Prefect Server |  | Self-hosted Prefect Server only; vendor + source excluded. PREFECT_SERVER_API_AUTH_STRING not set by default |
| ⚪ | `intitle:"PromptLayer"` | PromptLayer |  | PromptLayer (gateway_observability). logs every prompt/response with keys |
| ⚪ | `intitle:"promptfoo"` | Promptfoo |  | Promptfoo (safety_guardrail). no auth gate on API routes |
| ⚪ | `intitle:"promptfoo" -site:promptfoo.dev -site:github.com` | Promptfoo |  | Self-hosted Promptfoo only; vendor + source excluded. no auth gate on API routes |
| ⚪ | `intitle:"Qdrant" -site:qdrant.tech -site:github.com` | Qdrant |  | Self-hosted Qdrant only; vendor + source excluded. no auth by default |
| ⚪ | `intitle:"Omniboard"` | Sacred / Omniboard |  | Sacred / Omniboard (training_experiment). no auth; source code with hardcoded creds exposed |
| ⚪ | `intitle:"Selenium Grid"` | Selenium Grid |  | Selenium Grid (agent_framework). no auth in default deploy |
| ⚪ | `intitle:"Selenoid"` | Selenoid |  | Selenoid (agent_framework). no auth in default deploy |
| ⚪ | `intitle:"Sourcebot"` | Sourcebot |  | Sourcebot (code_assistant). None |
| ⚪ | `intitle:"Sourcegraph"` | Sourcegraph / Cody |  | Sourcegraph / Cody (code_assistant). built-in auth; free-license instances promote all users to site-admin |
| ⚪ | `intitle:"Sourcegraph" -site:sourcegraph.com -site:github.com` | Sourcegraph / Cody |  | Self-hosted Sourcegraph / Cody only; vendor + source excluded. built-in auth; free-license instances promote all users to site-admin |
| ⚪ | `intitle:"History Server"` | Spark History Server |  | Spark History Server (workflow_orchestration). no auth by default; job env vars include AWS/GCS credentials |
| ⚪ | `intitle:"SpeechBrain"` | SpeechBrain |  | SpeechBrain (voice_audio). no auth on self-hosted wrappers |
| ⚪ | `intitle:"Stable Diffusion"` | Stable Diffusion WebUI (AUTOMATIC1111) |  | Stable Diffusion WebUI (AUTOMATIC1111) (image_gen). no auth by default |
| ⚪ | `intitle:"Streamlit"` | Streamlit |  | Streamlit (notebook). no auth concept in framework; T1 |
| ⚪ | `intitle:"Streamlit" -site:streamlit.io -site:github.com` | Streamlit |  | Self-hosted Streamlit only; vendor + source excluded. no auth concept in framework; T1 |
| ⚪ | `intitle:"Supabase Studio"` | Supabase |  | Supabase (vector_db). ships with pgvector by default; anon key misconfiguration risk |
| ⚪ | `intitle:"Supabase Studio" -site:supabase.com -site:github.com` | Supabase |  | Self-hosted Supabase only; vendor + source excluded. ships with pgvector by default; anon key misconfiguration risk |
| ⚪ | `intitle:"SuperAGI"` | SuperAGI |  | SuperAGI (agent_framework). some auth friction but mostly open |
| ⚪ | `intitle:"Temporal"` | Temporal Workflow |  | Temporal Workflow (workflow_orchestration). noopAuthorizer compiled in; OIDC requires custom plugin |
| ⚪ | `intitle:"Temporal" -site:temporal.io -site:github.com` | Temporal Workflow |  | Self-hosted Temporal Workflow only; vendor + source excluded. noopAuthorizer compiled in; OIDC requires custom plugin |
| ⚪ | `intitle:"TensorBoard"` | TensorBoard |  | TensorBoard (training_experiment). no auth concept in standalone mode |
| ⚪ | `intitle:"Tortoise"` | Tortoise TTS |  | Tortoise TTS (voice_audio). no auth by default |
| ⚪ | `intitle:"Unstructured"` | Unstructured API |  | Unstructured API (gateway_observability). None |
| ⚪ | `intitle:"Weaviate"` | Weaviate |  | Weaviate (vector_db). anonymous access enabled unless explicitly set to false |
| ⚪ | `intitle:"Weaviate" -site:weaviate.io -site:github.com` | Weaviate |  | Self-hosted Weaviate only; vendor + source excluded. anonymous access enabled unless explicitly set to false |
| ⚪ | `intitle:"Weights & Biases"` | Weights & Biases (W&B) |  | Weights & Biases (W&B) (training_experiment). auth on by default |
| ⚪ | `intitle:"Weights & Biases" -site:wandb.ai -site:github.com` | Weights & Biases (W&B) |  | Self-hosted Weights & Biases (W&B) only; vendor + source excluded. auth on by default |
| ⚪ | `intitle:"Windmill"` | Windmill |  | Windmill (workflow_orchestration). default-creds admin@windmill.dev/changeme |
| ⚪ | `intitle:"Xinference"` | Xinference |  | Xinference (model_serving). no auth by default |
| ⚪ | `intitle:"ZenML" -site:zenml.io -site:github.com` | ZenML Server |  | Self-hosted ZenML Server only; vendor + source excluded. default password empty string |
| ⚪ | `intitle:"dcm4chee Archive UI"` | dcm4chee Archive |  | dcm4chee Archive (medical_edge). Keycloak-fronted; auth state may be misconfigured |
| 🟤 | `intitle:"Agno"` | Agno (formerly Phidata) |  | Agno (formerly Phidata) (agent_framework). thin deployment surface |
| 🟤 | `intitle:"Aim"` | Aim Experiment Tracker |  | Aim Experiment Tracker (training_experiment). no auth mechanism |
| 🟤 | `intitle:"Atlas"` | Apache Atlas |  | Apache Atlas (specialty_data). default-creds admin/admin |
| 🟤 | `intitle:"Applio"` | Applio |  | Applio (voice_audio). no auth by default |
| 🟤 | `intitle:"AutoGPT"` | AutoGPT |  | AutoGPT (agent_framework). moribund project |
| 🟤 | `intitle:"Axolotl"` | Axolotl |  | Axolotl (training_experiment). None |
| 🟤 | `intitle:"Bark"` | Bark TTS |  | Bark TTS (voice_audio). no auth by default |
| 🟤 | `intitle:"CVAT"` | CVAT |  | CVAT (data_labeling). auth on by default |
| 🟤 | `intitle:"Cadence"` | Cadence Workflow |  | Cadence Workflow (workflow_orchestration). CADENCE_WEB_AUTH_STRATEGY=disabled default |
| 🟤 | `intitle:"ChatTTS"` | ChatTTS |  | ChatTTS (voice_audio). no auth by default |
| 🟤 | `intitle:"Chroma"` | ChromaDB |  | ChromaDB (vector_db). no auth by default |
| 🟤 | `intitle:"ClearML"` | ClearML |  | ClearML (training_experiment). ships with free access login; explicit opt-in required for real auth |
| 🟤 | `intitle:"Comet"` | Comet ML |  | Comet ML (training_experiment). default-creds admin:admin on versions <24.9.8 |
| 🟤 | `intitle:"Opik"` | Comet Opik |  | Comet Opik (gateway_observability). auth was feature request as of 2025; likely open |
| 🟤 | `intitle:"ComfyUI"` | ComfyUI |  | ComfyUI (image_gen). no auth by default; ComfyUI-Manager = RCE by design |
| 🟤 | `intitle:"Coqui"` | Coqui TTS |  | Coqui TTS (voice_audio). no auth by default |
| 🟤 | `intitle:"Dagster"` | Dagster |  | Dagster (workflow_orchestration). no auth since 2020; runConfigYaml exposes all credentials |
| 🟤 | `intitle:"Onyx"` | Danswer / Onyx |  | Danswer / Onyx (rag_stack). AUTH_TYPE=disabled option; first-run signup required |
| 🟤 | `intitle:"DataHub"` | DataHub |  | DataHub (specialty_data). GMS backend auth-off by default; JWT not cryptographically verified |
| 🟤 | `intitle:"Devika"` | Devika |  | Devika (agent_framework). None |
| 🟤 | `intitle:"Ratel"` | Dgraph |  | Dgraph (vector_db). None |
| 🟤 | `intitle:"Dify"` | Dify |  | Dify (orchestration). login-gated but version leaks in headers |
| 🟤 | `intitle:"doccano"` | Doccano |  | Doccano (data_labeling). auth on by default; /v1/health open for fingerprinting |
| 🟤 | `intitle:"Docling"` | Docling |  | Docling (gateway_observability). None |
| 🟤 | `intitle:"Dyad"` | Dyad |  | Dyad (code_assistant). None |
| 🟤 | `intitle:"Gradio"` | Gradio |  | Gradio (orchestration). no auth by default |
| 🟤 | `intitle:"Harbor"` | Harbor |  | Harbor (container). auth on by default |
| 🟤 | `intitle:"Hatchet"` | Hatchet |  | Hatchet (workflow_orchestration). default-creds admin@example.com/Admin123!! |
| 🟤 | `intitle:"Kestra"` | Kestra |  | Kestra (workflow_orchestration). auth off pre-v0.24.0 |
| 🟤 | `intitle:"Kibana"` | Kibana |  | Kibana (search_data). None |
| 🟤 | `intitle:"Kokoro"` | Kokoro TTS / Kokoro-FastAPI |  | Kokoro TTS / Kokoro-FastAPI (voice_audio). no auth by default |
| 🟤 | `intitle:"LiteLLM"` | LiteLLM |  | LiteLLM (gateway_observability). master key often leaked in env |
| 🟤 | `intitle:"LiveKit"` | LiveKit Agents |  | LiveKit Agents (voice_audio). JWT required for room ops; health endpoint open |
| 🟤 | `intitle:"Marquez"` | Marquez (OpenLineage) |  | Marquez (OpenLineage) (specialty_data). no auth by default |
| 🟤 | `intitle:"MetaGPT"` | MetaGPT |  | MetaGPT (agent_framework). no persistent HTTP service |
| 🟤 | `intitle:"Attu"` | Milvus |  | Milvus (vector_db). no auth on Attu admin UI |
| 🟤 | `intitle:"Pipecat"` | Pipecat |  | Pipecat (voice_audio). no auth by default |
| 🟤 | `intitle:"Piper"` | Piper TTS |  | Piper TTS (voice_audio). no auth by default |
| 🟤 | `intitle:"Portkey"` | Portkey |  | Portkey (gateway_observability). provider API keys in config |
| 🟤 | `intitle:"Qdrant"` | Qdrant |  | Qdrant (vector_db). no auth by default |
| 🟤 | `intitle:"Redash"` | Redash |  | Redash (bi_dashboard). None |
| 🟤 | `intitle:"Refact"` | Refact.ai (self-hosted) |  | Refact.ai (self-hosted) (code_assistant). auth off initially; community edition accepts any API key value |
| 🟤 | `intitle:"Seldon"` | Seldon Core |  | Seldon Core (model_serving). no auth by default; Istio auth opt-in |
| 🟤 | `intitle:"Splash"` | Splash (Scrapinghub) |  | Splash (Scrapinghub) (agent_framework). no auth by default |
| 🟤 | `intitle:"Trino"` | Trino / Presto |  | Trino / Presto (workflow_orchestration). no auth by default |
| 🟤 | `intitle:"TruLens"` | TruLens |  | TruLens (safety_guardrail). no auth (Streamlit); T1 |
| 🟤 | `intitle:"Tyk"` | Tyk Gateway |  | Tyk Gateway (gateway_observability). default-creds shipped in tyk.conf.example |
| 🟤 | `intitle:"Whisper"` | Whisper ASR |  | Whisper ASR (voice_audio). no auth by default |
| 🟤 | `intitle:"ZenML"` | ZenML Server |  | ZenML Server (workflow_orchestration). default password empty string |
| 🟤 | `intitle:"ZITADEL"` | Zitadel |  | Zitadel (gateway_observability). System API requires JWT; OIDC discovery unauthenticated |
| 🟤 | `intitle:"pgAdmin"` | pgAdmin |  | pgAdmin (search_data). default creds historically common |
| 🟤 | `intitle:"SoftVC"` | so-vits-svc |  | so-vits-svc (voice_audio). no auth by default |

## Pages Containing Login Portals
_96 dorks_

| T | Dork | Service | CVE | Notes |
|---|------|---------|-----|-------|
| 🟡 | `intitle:"Airflow" inurl:login` | Apache Airflow | CVE-2020-13927 | Apache Airflow login portal. auth on with 8 documented bypass patterns |
| 🟡 | `intitle:"Apache Flink Web Dashboard" inurl:login` | Apache Flink | CVE-2020-17518 | Apache Flink login portal. no auth by default |
| 🟡 | `intitle:"Apache Superset" inurl:login` | Apache Superset | CVE-2023-27524 | Apache Superset login portal. default SECRET_KEY leads to auth bypass |
| 🟡 | `intitle:"Argilla" inurl:login` | Argilla | CVE-2023-38686 | Argilla login portal. auth on since v1.x; default-public workspace misconfiguration seen |
| 🟡 | `intitle:"Argo" inurl:login` | Argo Workflows | CVE-2026-28229 | Argo Workflows login portal. --auth-mode=server disables all credential requirements |
| 🟡 | `intitle:"authentik" inurl:login` | Authentik | CVE-2024-47070 | Authentik login portal. login required; /api/v3/root/config/ pre-auth accessible |
| 🟡 | `intitle:"Casdoor" inurl:login` | Casdoor | CVE-2024-41657 | Casdoor login portal. default-creds built-in/admin/123 |
| 🟡 | `intitle:"Flowise" inurl:login` | Flowise | CVE-2024-36420 | Flowise login portal. mixed auth; pre-1.8.2 auth bypass via path traversal |
| 🟡 | `intitle:"GitHub Enterprise" inurl:login` | GitHub Enterprise Server (GHES) | CVE-2024-9487 | GitHub Enterprise Server (GHES) login portal. OAuth enforced; SAML bypass on affected versions |
| 🟡 | `intitle:"Grafana" inurl:login` | Grafana | CVE-2021-43798 | Grafana login portal. anonymous access misconfiguration common |
| 🟡 | `intitle:"Log in to Grafana"` | Grafana |  | Grafana login. CVE-2021-43798 path traversal needs no login. |
| 🟡 | `intitle:"Jupyter" intext:"Password or token" inurl:login` | Jupyter |  | Jupyter token login. Token-in-URL or blank-token instances = notebook RCE. |
| 🟡 | `intitle:"Jupyter" inurl:login` | Jupyter Notebook / JupyterLab | CVE-2019-10255 | Jupyter Notebook / JupyterLab login portal. modern deployments consistently locked; older --NotebookApp.token= blank is unauth RCE |
| 🟡 | `intitle:"JupyterHub" inurl:login` | JupyterHub | CVE-2026-33709 | JupyterHub login portal. auth on by default since v1.x |
| 🟡 | `intitle:"Keycloak" inurl:login` | Keycloak | CVE-2024-3656 | Keycloak login portal. login required for admin; OIDC discovery endpoints unauthenticated |
| 🟡 | `intitle:"Label Studio" inurl:login` | Label Studio | CVE-2022-25011 | Label Studio login portal. mandatory auth; /api/projects sometimes misconfigured readable |
| 🟡 | `intitle:"Langflow" inurl:login` | Langflow | CVE-2026-33017 | Langflow login portal. LANGFLOW_AUTO_LOGIN gating in v1.5+, often left open |
| 🟡 | `intitle:"Sign in to Langfuse" -site:langfuse.com` | Langfuse |  | Langfuse sign-in. Open-signup (signUpDisabled:false) gives authenticated API access. |
| 🟡 | `intitle:"MLflow" inurl:login` | MLflow | CVE-2024-37052 | MLflow login portal. no auth by default |
| 🟡 | `intitle:"Mage" inurl:login` | Mage.ai | CVE-2025-2129 | Mage.ai login portal. no auth pre-v0.9.78; ~1,045 confirmed unauth at disclosure |
| 🟡 | `intitle:"Metabase" inurl:login` | Metabase | CVE-2023-38646 | Metabase login portal. setup-wizard bypass; has-user-setup: false = exploitable |
| 🟡 | `intitle:"Login - Metabase"` | Metabase |  | Metabase login. /api/session/properties setup-token = claimable admin (CVE-2023-38646). |
| 🟡 | `intitle:"Conductor UI" inurl:login` | Netflix Conductor | CVE-2020-9296 | Netflix Conductor login portal. no auth by default |
| 🟡 | `intitle:"Sign in" intext:"Open WebUI" -site:openwebui.com` | Open WebUI |  | Open WebUI sign-in. First account = admin; effectively unauth on fresh installs. |
| 🟡 | `intitle:"Ray Dashboard" inurl:login` | Ray Dashboard | CVE-2023-48022 | Ray Dashboard login portal. no auth; ShadowRay actively exploited |
| 🟡 | `intitle:"authentik" inurl:"/if/flow/"` | authentik |  | authentik flow executor. initial-setup flow claimable on fresh deploys (CVE-2024-47070). |
| 🟡 | `intitle:"n8n" inurl:login` | n8n | CVE-2024-25289 | n8n login portal. basicauth optional and frequently skipped |
| ⚪ | `intitle:"Aim" inurl:login` | Aim Experiment Tracker |  | Aim Experiment Tracker login portal. no auth mechanism |
| ⚪ | `intitle:"AnythingLLM" intext:"sign in"` | AnythingLLM |  | AnythingLLM login. Known auth-bypass history; multi-user workspace data. |
| ⚪ | `intitle:"DolphinScheduler" inurl:login` | Apache DolphinScheduler |  | Apache DolphinScheduler login portal. default-creds admin/dolphinscheduler123 |
| ⚪ | `intitle:"Sign In - Superset"` | Apache Superset |  | Superset login. Default SECRET_KEY = session forge (CVE-2023-27524). |
| ⚪ | `intitle:"Apache Tika" inurl:login` | Apache Tika |  | Apache Tika login portal. SSRF history; arbitrary file read |
| ⚪ | `intitle:"Argo CD" intext:"Log in via"` | Argo CD |  | Argo CD login. /api/v1/settings (public) leaks OIDC issuer = operator attribution. |
| ⚪ | `intitle:"Arize Phoenix" inurl:login` | Arize Phoenix |  | Arize Phoenix login portal. no auth, --host 0.0.0.0 default |
| ⚪ | `intitle:"Authelia" inurl:login` | Authelia |  | Authelia login portal. login portal to all downstream services |
| ⚪ | `intitle:"Authelia" intext:"Login"` | Authelia |  | Authelia auth portal (often fronts other AI services). |
| ⚪ | `intitle:"Axolotl" inurl:login` | Axolotl |  | Axolotl login portal. None |
| ⚪ | `intitle:"CVAT" inurl:login` | CVAT |  | CVAT login portal. auth on by default |
| ⚪ | `intitle:"Cadence" inurl:login` | Cadence Workflow |  | Cadence Workflow login portal. CADENCE_WEB_AUTH_STRATEGY=disabled default |
| ⚪ | `intitle:"Sign in to continue" intext:"Casdoor" -site:casdoor.org` | Casdoor |  | Casdoor-fronted app login. IAM CRUD when default-admin unchanged. |
| ⚪ | `intitle:"ClearML" inurl:login` | ClearML |  | ClearML login portal. ships with free access login; explicit opt-in required for real auth |
| ⚪ | `intitle:"Comet" inurl:login` | Comet ML |  | Comet ML login portal. default-creds admin:admin on versions <24.9.8 |
| ⚪ | `intitle:"Opik" inurl:login` | Comet Opik |  | Comet Opik login portal. auth was feature request as of 2025; likely open |
| ⚪ | `intitle:"Dagster" inurl:login` | Dagster |  | Dagster login portal. no auth since 2020; runConfigYaml exposes all credentials |
| ⚪ | `intitle:"Determined" inurl:login` | Determined AI |  | Determined AI login portal. default-creds admin with blank password |
| ⚪ | `intitle:"Dify" inurl:login` | Dify |  | Dify login portal. login-gated but version leaks in headers |
| ⚪ | `intitle:"Dify" intext:"Sign in" -site:dify.ai` | Dify |  | Dify sign-in. Self-hosted app-builder; stack version leaks in headers. |
| ⚪ | `intitle:"doccano" inurl:login` | Doccano |  | Doccano login portal. auth on by default; /v1/health open for fingerprinting |
| ⚪ | `intitle:"Docling" inurl:login` | Docling |  | Docling login portal. None |
| ⚪ | `intitle:"Dyad" inurl:login` | Dyad |  | Dyad login portal. None |
| ⚪ | `intitle:"Evidently - ML Monitoring" inurl:login` | Evidently ML Monitoring |  | Evidently ML Monitoring login portal. no auth concept in default deploy |
| ⚪ | `intitle:"Sign in" intext:"Flowise" -site:flowiseai.com` | Flowise |  | Flowise login. Pre-1.8.2 auth bypass (CVE-2024-36420). |
| ⚪ | `intitle:"Flyte Console" inurl:login` | Flyte |  | Flyte login portal. useAuth:false in defaults; MinIO default creds |
| ⚪ | `intitle:"Gradio" inurl:login` | Gradio |  | Gradio login portal. no auth by default |
| ⚪ | `intitle:"Hatchet" inurl:login` | Hatchet |  | Hatchet login portal. default-creds admin@example.com/Admin123!! |
| ⚪ | `intitle:"Helicone" inurl:login` | Helicone |  | Helicone login portal. None |
| ⚪ | `intitle:"JupyterHub" inurl:"hub/login"` | JupyterHub |  | JupyterHub login. Misconfig = notebook exec as server user. |
| ⚪ | `intitle:"Kestra" inurl:login` | Kestra |  | Kestra login portal. auth off pre-v0.24.0 |
| ⚪ | `intitle:"Welcome to Keycloak"` | Keycloak |  | Keycloak welcome/admin. CVE-2024-3656 admin API class. |
| ⚪ | `inurl:"/auth/realms/" intext:"account"` | Keycloak |  | Keycloak realm endpoint. Enumerates realms + clients. |
| ⚪ | `intitle:"Kong Manager" inurl:login` | Kong AI Gateway |  | Kong AI Gateway login portal. admin API no auth when bound to 0.0.0.0 |
| ⚪ | `intitle:"Kubeflow Central Dashboard" inurl:login` | Kubeflow |  | Kubeflow login portal. single-user mode no auth |
| ⚪ | `allintitle:"Sign In Kubeflow"` | Kubeflow |  | Kubeflow Central Dashboard login. Pipelines + notebooks + model registry. |
| ⚪ | `intitle:"LLaMA Factory" inurl:login` | LLaMA Factory |  | LLaMA Factory login portal. None |
| ⚪ | `intitle:"Label Studio" intext:"Log In"` | Label Studio |  | Label Studio login (CVE-2022-25011 class). Annotation projects + data. |
| ⚪ | `intitle:"LangSmith" inurl:login` | LangSmith |  | LangSmith login portal. auth-off on pre-v0.10 deployments |
| ⚪ | `intitle:"Sign in" intext:"LibreChat"` | LibreChat |  | LibreChat login. Registration-open instances grant chat + configured provider keys. |
| ⚪ | `intitle:"LiteLLM" inurl:login` | LiteLLM |  | LiteLLM login portal. master key often leaked in env |
| ⚪ | `intitle:"Sign In" intext:"MLflow" -site:databricks.com` | MLflow |  | MLflow auth page. Default config has no auth behind it. |
| ⚪ | `intitle:"Open WebUI" inurl:login` | Open WebUI |  | Open WebUI login portal. first-user-admin, effectively unauth on fresh deploys |
| ⚪ | `intitle:"Optuna Dashboard" inurl:login` | Optuna Dashboard |  | Optuna Dashboard login portal. no auth when containerized |
| ⚪ | `intitle:"Orthanc Explorer" inurl:login` | Orthanc DICOM Server |  | Orthanc DICOM Server login portal. no auth by default; PHI exposure |
| ⚪ | `intitle:"Portainer" intext:"login"` | Portainer |  | Portainer (Docker UI). Often fronts AI container stacks; container takeover. |
| ⚪ | `intitle:"Portkey" inurl:login` | Portkey |  | Portkey login portal. provider API keys in config |
| ⚪ | `intitle:"Prefect Server" inurl:login` | Prefect Server |  | Prefect Server login portal. PREFECT_SERVER_API_AUTH_STRING not set by default |
| ⚪ | `intitle:"PromptLayer" inurl:login` | PromptLayer |  | PromptLayer login portal. logs every prompt/response with keys |
| ⚪ | `intitle:"RagFlow" intext:"Sign in"` | RAGFlow |  | RAGFlow login (CVE-2024-12880). Knowledge bases + ingestion. |
| ⚪ | `intitle:"Ray" intext:"Dashboard" inurl:8265` | Ray Dashboard |  | Ray Dashboard (CVE-2023-48022 ShadowRay unauth RCE). |
| ⚪ | `intitle:"Redash" inurl:login` | Redash |  | Redash login portal. None |
| ⚪ | `intitle:"Refact" inurl:login` | Refact.ai (self-hosted) |  | Refact.ai (self-hosted) login portal. auth off initially; community edition accepts any API key value |
| ⚪ | `intitle:"Omniboard" inurl:login` | Sacred / Omniboard |  | Sacred / Omniboard login portal. no auth; source code with hardcoded creds exposed |
| ⚪ | `intitle:"Sourcebot" inurl:login` | Sourcebot |  | Sourcebot login portal. None |
| ⚪ | `intitle:"Sourcegraph" inurl:login` | Sourcegraph / Cody |  | Sourcegraph / Cody login portal. built-in auth; free-license instances promote all users to site-admin |
| ⚪ | `intitle:"History Server" inurl:login` | Spark History Server |  | Spark History Server login portal. no auth by default; job env vars include AWS/GCS credentials |
| ⚪ | `intitle:"Streamlit" inurl:login` | Streamlit |  | Streamlit login portal. no auth concept in framework; T1 |
| ⚪ | `intitle:"Temporal" inurl:login` | Temporal Workflow |  | Temporal Workflow login portal. noopAuthorizer compiled in; OIDC requires custom plugin |
| ⚪ | `intitle:"TensorBoard" inurl:login` | TensorBoard |  | TensorBoard login portal. no auth concept in standalone mode |
| ⚪ | `intitle:"Trino" inurl:login` | Trino / Presto |  | Trino / Presto login portal. no auth by default |
| ⚪ | `intitle:"Tyk" inurl:login` | Tyk Gateway |  | Tyk Gateway login portal. default-creds shipped in tyk.conf.example |
| ⚪ | `intitle:"Unstructured" inurl:login` | Unstructured API |  | Unstructured API login portal. None |
| ⚪ | `intitle:"Weights & Biases" inurl:login` | Weights & Biases (W&B) |  | Weights & Biases (W&B) login portal. auth on by default |
| ⚪ | `intitle:"Windmill" inurl:login` | Windmill |  | Windmill login portal. default-creds admin@windmill.dev/changeme |
| ⚪ | `intitle:"ZenML" inurl:login` | ZenML Server |  | ZenML Server login portal. default password empty string |
| ⚪ | `intitle:"ZITADEL" inurl:login` | Zitadel |  | Zitadel login portal. System API requires JWT; OIDC discovery unauthenticated |
| ⚪ | `intitle:"dcm4chee Archive UI" inurl:login` | dcm4chee Archive |  | dcm4chee Archive login portal. Keycloak-fronted; auth state may be misconfigured |
| ⚪ | `intitle:"n8n" intext:"Sign in" -site:n8n.io` | n8n |  | n8n sign-in. owner setup sometimes skipped; /rest/ legacy API may be ungated. |

## Sensitive Directories
_65 dorks_

| T | Dork | Service | CVE | Notes |
|---|------|---------|-----|-------|
| 🟡 | `intitle:"index of" intext:"chroma.sqlite3"` | ChromaDB |  | ChromaDB artifact directory (chroma.sqlite3) exposed. |
| 🟡 | `intitle:"index of" "chroma.sqlite3"` | ChromaDB |  | ChromaDB persistent store. Embeddings + source document text + metadata. |
| 🟡 | `intitle:"index of" intext:".safetensors"` | ComfyUI |  | ComfyUI artifact directory (.safetensors) exposed. |
| 🟡 | `intitle:"index of" intext:"checkpoints"` | ComfyUI |  | ComfyUI artifact directory (checkpoints) exposed. |
| 🟡 | `intitle:"index of" "index.faiss"` | FAISS |  | FAISS index (LangChain/LlamaIndex default). Paired index.pkl holds the docs. |
| 🟡 | `intitle:"index of" "index.pkl" intext:"faiss"` | FAISS |  | FAISS docstore pickle. Deserialization-sensitive + leaks indexed corpus. |
| 🟡 | `intitle:"index of" "service_account.json"` | GCP |  | GCP service-account key. Vertex AI / GCS access in one file. |
| 🟡 | `intitle:"index of" intext:"model.safetensors"` | Hugging Face TGI |  | Hugging Face TGI artifact directory (model.safetensors) exposed. |
| 🟡 | `intitle:"index of" ".huggingface" intext:"token"` | HuggingFace |  | HuggingFace cached token dir. hf_ token = model/dataset/Space access. |
| 🟡 | `intitle:"index of" intext:".ckpt"` | InvokeAI |  | InvokeAI artifact directory (.ckpt) exposed. |
| 🟡 | `intitle:"index of" intext:".ipynb" intext:"OPENAI"` | Jupyter |  | Notebooks in an open dir containing OpenAI key references. |
| 🟡 | `intitle:"index of" "kaggle.json"` | Kaggle |  | Kaggle API token. Dataset + competition access. |
| 🟡 | `intitle:"index of" intext:".lance"` | LanceDB |  | LanceDB artifact directory (.lance) exposed. |
| 🟡 | `intitle:"index of" ".lance"` | LanceDB |  | LanceDB columnar vector store files. |
| 🟡 | `intitle:"index of" "litellm_config.yaml"` | LiteLLM |  | LiteLLM proxy config. model_list with provider api_key values inline. |
| 🟡 | `intitle:"index of" "docstore.json"` | LlamaIndex |  | LlamaIndex storage dir. Full ingested document store + node graph. |
| 🟡 | `intitle:"index of" intext:".gguf"` | LocalAI |  | LocalAI artifact directory (.gguf) exposed. |
| 🟡 | `intitle:"index of" intext:"mlruns"` | MLflow | CVE-2024-37052 | MLflow artifact directory (mlruns) exposed. |
| 🟡 | `intitle:"index of" "mlruns"` | MLflow |  | MLflow mlruns tree. Params, metrics, artifacts, model registry per run. |
| 🟡 | `intitle:"index of" intext:"qdrant_storage"` | Qdrant |  | Qdrant artifact directory (qdrant_storage) exposed. |
| 🟡 | `intitle:"index of" "qdrant_storage"` | Qdrant |  | Qdrant on-disk storage dir. Raw vectors + payloads. |
| 🟡 | `intitle:"index of" intext:"models/Stable-diffusion"` | Stable Diffusion WebUI (AUTOMATIC1111) |  | Stable Diffusion WebUI (AUTOMATIC1111) artifact directory (models/Stable-diffusion) exposed. |
| 🟡 | `intitle:"index of" ".streamlit"` | Streamlit |  | Streamlit config dir. secrets.toml holds API keys + DB creds in plaintext. |
| 🟡 | `intitle:"index of" "secrets.toml"` | Streamlit |  | Streamlit secrets file directly. Provider keys, DB strings. |
| 🟡 | `intitle:"index of" intext:"events.out.tfevents"` | TensorBoard |  | TensorBoard artifact directory (events.out.tfevents) exposed. |
| 🟡 | `intitle:"index of" "events.out.tfevents"` | TensorBoard |  | TensorBoard event files. Loss/metric curves, graph, sometimes sample data. |
| 🟡 | `intitle:"index of" intext:"ggml-base.bin"` | Whisper ASR |  | Whisper ASR artifact directory (ggml-base.bin) exposed. |
| 🟡 | `intitle:"index of" "train.jsonl"` | dataset |  | Training corpus in JSONL. The actual fine-tune data, often proprietary or PII. |
| 🟡 | `intitle:"index of" "adapter_model.safetensors"` | fine-tune |  | LoRA/QLoRA fine-tune adapter. Reveals what a base model was specialized on. |
| 🟡 | `intitle:"index of" "trainer_state.json"` | fine-tune |  | HF Trainer state: loss curve, LR schedule, checkpoint steps. Training-run disclosure. |
| 🟡 | `intitle:index.of "models/Stable-diffusion"` | image_gen |  | AUTOMATIC1111/ComfyUI checkpoint dir. SD/SDXL/LoRA model store. |
| 🟡 | `intitle:"index of" ".safetensors"` | model weights |  | Open dir of SafeTensors model weights. Fine-tuned model IP + training-compute cost. |
| 🟡 | `intitle:"index of" ".gguf"` | model weights |  | Open dir of GGUF quantized weights (llama.cpp/Ollama). Full model exfil. |
| 🟡 | `intitle:"index of" "consolidated.00.pth"` | model weights |  | Llama/Mistral raw checkpoint shard. Original weights, pre-quant. |
| 🟡 | `intitle:"index of" "pytorch_model.bin"` | model weights |  | HuggingFace PyTorch weight file in an open listing. |
| 🟡 | `intitle:"index of" "embeddings.pkl"` | rag |  | Pickled embedding store. Deserialization risk + corpus leak. |
| 🟡 | `intitle:"index of" intext:"config.json"` | vLLM |  | vLLM artifact directory (config.json) exposed. |
| 🟡 | `intitle:"index of" intext:"tokenizer.json"` | vLLM |  | vLLM artifact directory (tokenizer.json) exposed. |
| ⚪ | `intitle:"index of" "docker-compose.yml" intext:"flowise"` | Flowise |  | Flowise compose file. Often embeds FLOWISE_USERNAME/PASSWORD. |
| ⚪ | `intitle:"index of" ".ipynb_checkpoints"` | Jupyter |  | Jupyter checkpoint dir. Autosaved notebooks, frequently with inline keys. |
| ⚪ | `intitle:index.of ".jupyter"` | Jupyter |  | Jupyter config dir. jupyter_server_config may hold a hashed/again token. |
| ⚪ | `intitle:"index of" "litellm" intext:".yaml"` | LiteLLM |  | LiteLLM yaml config in an open listing. |
| ⚪ | `intitle:"index of" "index_store.json"` | LlamaIndex |  | LlamaIndex index metadata. Confirms a persisted RAG index. |
| ⚪ | `index.of.mlruns` | MLflow |  | Dotted-form sweep for MLflow run trees. |
| ⚪ | `intitle:"index of" "docker-compose.yml" intext:"ollama"` | Ollama |  | Ollama compose file. Port maps, volumes, env vars. |
| ⚪ | `intitle:index.of "raft_state.json"` | Qdrant |  | Qdrant cluster raft state in an open listing. |
| ⚪ | `intitle:index.of "wandb" intext:"run-"` | W&B |  | Weights & Biases local run dir. Configs, logs, possibly API key in settings. |
| ⚪ | `"Index of" "/weaviate_data"` | Weaviate |  | Weaviate persistence volume in an open listing. |
| ⚪ | `intitle:"index of" "agent_memory"` | agent |  | Persisted agent memory dir. Conversation history + tool state. |
| ⚪ | `intitle:"index of" "chat_history" intext:".json"` | agent |  | Stored chat transcripts. Prompt + PII exposure. |
| ⚪ | `intitle:"index of" "dataset.jsonl"` | dataset |  | Generic dataset JSONL in an open listing. |
| ⚪ | `intitle:"index of" "embeddings.parquet"` | dataset |  | Parquet embedding export. Bulk vector + metadata dump. |
| ⚪ | `intitle:index.of "finetune" intext:".jsonl"` | dataset |  | Fine-tune data directory. |
| ⚪ | `intitle:"index of" ".dvc" intext:"config"` | dataset |  | DVC data-version config. Remote storage URLs + sometimes creds. |
| ⚪ | `intitle:index.of "checkpoint-" intext:"trainer_state"` | fine-tune |  | HF Trainer checkpoint dir series. |
| ⚪ | `intitle:"index of" "loras" intext:".safetensors"` | image_gen |  | LoRA directory for diffusion models. Custom-trained styles/subjects. |
| ⚪ | `intitle:"index of" "system_prompt" intext:".txt"` | prompts |  | Stored system prompts. Reveals agent instructions + guardrail logic. |
| ⚪ | `intitle:"index of" "prompts" intext:".jinja"` | prompts |  | Jinja prompt template dir. Prompt-injection surface mapping. |
| ⚪ | `intitle:"index of" "vectorstore"` | rag |  | Generic RAG vector store dir. Embeddings + chunked source docs. |
| ⚪ | `intitle:index.of.embeddings` | rag |  | Dotted-form sweep for embedding directories. |
| ⚪ | `intitle:"index of" "lightning_logs"` | training |  | PyTorch Lightning log tree. Checkpoints + hparams.yaml. |
| ⚪ | `intitle:"index of" "optuna.db"` | training |  | Optuna study SQLite. Hyperparameter search trials. |
| ⚪ | `intitle:"index of" "deepspeed_config.json"` | training |  | DeepSpeed training config. Cluster + optimizer setup disclosure. |
| ⚪ | `intitle:"index of" "params.yaml" intext:"model"` | training |  | DVC/ML pipeline params. Model + training hyperparameters. |
| ⚪ | `intitle:index.of "checkpoints" intext:".pt"` | training |  | PyTorch checkpoint dir (.pt). Resumable training weights. |

## Web Server Detection
_247 dorks_

| T | Dork | Service | CVE | Notes |
|---|------|---------|-----|-------|
| 🟡 | `intext:"apache airflow" -site:github.com` | Apache Airflow | CVE-2020-13927 | Apache Airflow body fingerprint. |
| 🟡 | `intext:"dag-runs" -site:github.com` | Apache Airflow | CVE-2020-13927 | Apache Airflow body fingerprint. |
| 🟡 | `intext:"Apache Atlas" -site:github.com` | Apache Atlas |  | Apache Atlas body fingerprint. |
| 🟡 | `intext:"/api/atlas/v2" -site:github.com` | Apache Atlas |  | Apache Atlas body fingerprint. |
| 🟡 | `intext:"/dolphinscheduler/ui" -site:github.com` | Apache DolphinScheduler |  | Apache DolphinScheduler body fingerprint. |
| 🟡 | `intext:"flink-version" -site:github.com` | Apache Flink | CVE-2020-17518 | Apache Flink body fingerprint. |
| 🟡 | `intext:"apache_superset" -site:github.com` | Apache Superset | CVE-2023-27524 | Apache Superset body fingerprint. |
| 🟡 | `intext:"superset_load_chart" -site:github.com` | Apache Superset | CVE-2023-27524 | Apache Superset body fingerprint. |
| 🟡 | `intext:"argoproj" -site:github.com` | Argo Workflows | CVE-2026-28229 | Argo Workflows body fingerprint. |
| 🟡 | `intext:"goauthentik.io" -site:github.com` | Authentik | CVE-2024-47070 | Authentik body fingerprint. |
| 🟡 | `intext:"AutoGen Studio" -site:github.com` | AutoGen / AutoGen Studio |  | AutoGen / AutoGen Studio body fingerprint. |
| 🟡 | `intext:"suno-ai/bark" -site:github.com` | Bark TTS |  | Bark TTS body fingerprint. |
| 🟡 | `intext:"/api/3/action" -site:github.com` | CKAN | CVE-2023-32321 | CKAN body fingerprint. |
| 🟡 | `intext:"Computer Vision Annotation Tool" -site:github.com` | CVAT |  | CVAT body fingerprint. |
| 🟡 | `intext:"built-in" -site:github.com` | Casdoor | CVE-2024-41657 | Casdoor body fingerprint. |
| 🟡 | `intext:"/api/v1/heartbeat" -site:github.com` | ChromaDB |  | ChromaDB body fingerprint. |
| 🟡 | `intext:"nanosecond heartbeat" -site:github.com` | ChromaDB |  | ChromaDB: Unique body match for /api/v*/heartbeat. 48/48 surveyed unauth. |
| 🟡 | `intext:"availableAccounts" -site:github.com` | Claude Relay |  | Claude Relay: Pooled-Anthropic-account relay schema. Co-anchor thirdPartyMaxConcurrent for zero-FP. |
| 🟡 | `intext:"/api/v1/cognify" -site:github.com` | Cognee |  | Cognee body fingerprint. |
| 🟡 | `intext:"/api/test-cases" -site:github.com` | DeepEval |  | DeepEval body fingerprint. |
| 🟡 | `intext:"/v1/projects" -site:github.com` | Doccano |  | Doccano body fingerprint. |
| 🟡 | `intext:"/v2/_catalog" -site:github.com` | Docker Registry |  | Docker Registry body fingerprint. |
| 🟡 | `intext:"DocsGPT" -site:github.com` | DocsGPT | CVE-2025-0868 | DocsGPT body fingerprint. |
| 🟡 | `intext:"elasticsearch" -site:github.com` | Elasticsearch | CVE-2024-23445 | Elasticsearch body fingerprint. |
| 🟡 | `intext:"lucene_version" -site:github.com` | Elasticsearch | CVE-2024-23445 | Elasticsearch body fingerprint. |
| 🟡 | `intext:"Low-code LLM apps builder" -site:github.com` | Flowise | CVE-2024-36420 | Flowise body fingerprint. |
| 🟡 | `intext:"/set_gpt_weights" -site:github.com` | GPT-SoVITS | CVE-2025-49833 | GPT-SoVITS body fingerprint. |
| 🟡 | `intext:"/api/kernels" -site:github.com` | Jupyter Notebook / JupyterLab | CVE-2019-10255 | Jupyter Notebook / JupyterLab body fingerprint. |
| 🟡 | `intext:"/hub/login" -site:github.com` | JupyterHub | CVE-2026-33709 | JupyterHub body fingerprint. |
| 🟡 | `intext:"kestra/kestra" -site:github.com` | Kestra |  | Kestra body fingerprint. |
| 🟡 | `intext:"/realms/master" -site:github.com` | Keycloak | CVE-2024-3656 | Keycloak body fingerprint. |
| 🟡 | `intext:"public_key" -site:github.com` | Keycloak | CVE-2024-3656 | Keycloak body fingerprint. |
| 🟡 | `intext:"/dev/captioned_speech" -site:github.com` | Kokoro TTS / Kokoro-FastAPI |  | Kokoro TTS / Kokoro-FastAPI body fingerprint. |
| 🟡 | `intext:"LLM Guard API" -site:github.com` | LLM Guard (Protect AI) |  | LLM Guard (Protect AI) body fingerprint. |
| 🟡 | `intext:"laiyer/llm-guard" -site:github.com` | LLM Guard (Protect AI) |  | LLM Guard (Protect AI) body fingerprint. |
| 🟡 | `intext:"label-studio" -site:github.com` | Label Studio | CVE-2022-25011 | Label Studio body fingerprint. |
| 🟡 | `intext:"/api/v1/auto_login" -site:github.com` | Langflow | CVE-2026-33017 | Langflow body fingerprint. |
| 🟡 | `intext:"signUpDisabled:false" -site:github.com` | Langfuse |  | Langfuse: Open-signup: anyone can register and gain authenticated API access. In __NEXT_DATA__ on /auth/sign-in. |
| 🟡 | `intext:"litellm_global_spend" -site:github.com` | LiteLLM |  | LiteLLM: Exposes operator cumulative LLM spend without auth. |
| 🟡 | `intext:"meta-llama/Llama-Guard" -site:github.com` | LlamaGuard |  | LlamaGuard body fingerprint. |
| 🟡 | `intext:"protocolVersion" -site:github.com` | MCP |  | MCP: JSON-RPC initialize response field. Strongest honeypot filter (1.1% pollution). |
| 🟡 | `intext:"/api/2.0/mlflow" -site:github.com` | MLflow | CVE-2024-37052 | MLflow body fingerprint. |
| 🟡 | `intext:"MONAI Label" -site:github.com` | MONAI Label Server |  | MONAI Label Server body fingerprint. |
| 🟡 | `intext:"MONAI Inference" -site:github.com` | MONAI Label Server |  | MONAI Label Server body fingerprint. |
| 🟡 | `intext:"mage-ai" -site:github.com` | Mage.ai | CVE-2025-2129 | Mage.ai body fingerprint. |
| 🟡 | `intext:"/api/session/properties" -site:github.com` | Metabase | CVE-2023-38646 | Metabase body fingerprint. |
| 🟡 | `intext:"metabase_session" -site:github.com` | Metabase | CVE-2023-38646 | Metabase body fingerprint. |
| 🟡 | `intext:"setup-token" -site:github.com` | Metabase | CVE-2023-38646 | Metabase: Non-null in /api/session/properties = admin registration claimable via POST /api/setup. Two-request takeover. |
| 🟡 | `intext:"MinIO Console" -site:github.com` | MinIO | CVE-2023-28432 | MinIO body fingerprint. |
| 🟡 | `intext:"nvidia nim" -site:github.com` | NVIDIA NIM | CVE-2025-23242 | NVIDIA NIM body fingerprint. |
| 🟡 | `intext:"nemo-toolkit" -site:github.com` | NVIDIA NeMo (ASR) | CVE-2025-23242 | NVIDIA NeMo (ASR) body fingerprint. |
| 🟡 | `intext:"NVIDIA NeMo" -site:github.com` | NVIDIA NeMo (ASR) | CVE-2025-23242 | NVIDIA NeMo (ASR) body fingerprint. |
| 🟡 | `intext:"ownerApp" -site:github.com` | Netflix Conductor | CVE-2020-9296 | Netflix Conductor body fingerprint. |
| 🟡 | `intext:"/api/metadata/workflow" -site:github.com` | Netflix Conductor | CVE-2020-9296 | Netflix Conductor body fingerprint. |
| 🟡 | `intext:"Ollama is running" -site:github.com` | Ollama | CVE-2024-37032 | Ollama body fingerprint. |
| 🟡 | `intext:"/v1/policies" -site:github.com` | Open Policy Agent (OPA) |  | Open Policy Agent (OPA) body fingerprint. |
| 🟡 | `intext:"/v1/data" -site:github.com` | Open Policy Agent (OPA) |  | Open Policy Agent (OPA) body fingerprint. |
| 🟡 | `intext:"/api/options/config" -site:github.com` | OpenHands |  | OpenHands: Returns {"APP_MODE":"oss"}. OPENHANDS_AUTH_TOKEN unset by default. Filesystem access. |
| 🟡 | `intext:"open-metadata" -site:github.com` | OpenMetadata | CVE-2024-28255 | OpenMetadata body fingerprint. |
| 🟡 | `intext:"/v1/audio/speech" -site:github.com` | Orpheus-FastAPI TTS |  | Orpheus-FastAPI TTS body fingerprint. |
| 🟡 | `intext:"/admin/clients" -site:github.com` | Ory Hydra |  | Ory Hydra body fingerprint. |
| 🟡 | `intext:"/admin/identities" -site:github.com` | Ory Kratos |  | Ory Kratos body fingerprint. |
| 🟡 | `intext:"csrf_protection_enabled:false" -site:github.com` | Prefect |  | Prefect: Default config; CSRF disabled + cors '*'. 9/15 sampled unauth. |
| 🟡 | `intext:"/api/evals" -site:github.com` | Promptfoo |  | Promptfoo body fingerprint. |
| 🟡 | `intext:"pyannote/audio" -site:github.com` | Pyannote |  | Pyannote body fingerprint. |
| 🟡 | `intext:"Qdrant Web UI" -site:github.com` | Qdrant |  | Qdrant body fingerprint. |
| 🟡 | `intext:"second brain" -site:github.com` | Quivr |  | Quivr body fingerprint. |
| 🟡 | `intext:"ragflow" -site:github.com` | RAGFlow | CVE-2024-12880 | RAGFlow body fingerprint. |
| 🟡 | `intext:"rvc-webui" -site:github.com` | RVC (Retrieval-based Voice Conversion) | CVE-2025-43842 | RVC (Retrieval-based Voice Conversion) body fingerprint. |
| 🟡 | `intext:"Retrieval-based-Voice-Conversion" -site:github.com` | RVC (Retrieval-based Voice Conversion) | CVE-2025-43842 | RVC (Retrieval-based Voice Conversion) body fingerprint. |
| 🟡 | `intext:"ray serve" -site:github.com` | Ray Dashboard | CVE-2023-48022 | Ray Dashboard body fingerprint. |
| 🟡 | `intext:"/api/data_sources" -site:github.com` | Redash |  | Redash body fingerprint. |
| 🟡 | `intext:"Redis Stack" -site:github.com` | Redis | CVE-2025-49844 | Redis body fingerprint. |
| 🟡 | `intext:"Grid Console" -site:github.com` | Selenium Grid |  | Selenium Grid body fingerprint. |
| 🟡 | `intext:"Spark History Server" -site:github.com` | Spark History Server |  | Spark History Server body fingerprint. |
| 🟡 | `intext:"/v1/completions" -site:github.com` | Tabby (TabbyML) |  | Tabby (TabbyML) body fingerprint. |
| 🟡 | `intext:"/data/runs" -site:github.com` | TensorBoard |  | TensorBoard body fingerprint. |
| 🟡 | `intext:"nextPageToken" -site:github.com` | TorchServe | CVE-2023-43654 | TorchServe body fingerprint. |
| 🟡 | `intext:"/analyze/prompt" -site:github.com` | Vigil LLM |  | Vigil LLM body fingerprint. |
| 🟡 | `intext:"Weaviate Console" -site:github.com` | Weaviate |  | Weaviate body fingerprint. |
| 🟡 | `intext:"nearly-live implementation" -site:github.com` | WhisperLive |  | WhisperLive body fingerprint. |
| 🟡 | `intext:"/ui/console" -site:github.com` | Zitadel |  | Zitadel body fingerprint. |
| 🟡 | `intext:"Infinity Emb" -site:github.com` | infinity-embedding |  | infinity-embedding body fingerprint. |
| 🟡 | `intext:"/v1/chat/completions" -site:github.com` | llama.cpp |  | llama.cpp body fingerprint. |
| 🟡 | `intext:"/rest/login" -site:github.com` | n8n | CVE-2024-25289 | n8n body fingerprint. |
| 🟡 | `intext:"n8n - Workflow Automation" -site:github.com` | n8n | CVE-2024-25289 | n8n body fingerprint. |
| ⚪ | `intext:"Agent UI" -site:github.com` | Agno (formerly Phidata) |  | Agno (formerly Phidata) body fingerprint. |
| ⚪ | `intext:"KafkaTopicList" -site:github.com` | Apache Kafka REST Proxy |  | Apache Kafka REST Proxy body fingerprint. |
| ⚪ | `intext:"MusicGen" -site:github.com` | AudioCraft / MusicGen |  | AudioCraft / MusicGen body fingerprint. |
| ⚪ | `intext:"cadenceClusters" -site:github.com` | Cadence Workflow |  | Cadence Workflow body fingerprint. |
| ⚪ | `intext:"Evidently.AI" -site:github.com` | Evidently ML Monitoring |  | Evidently ML Monitoring body fingerprint. |
| ⚪ | `intext:"InvokeAI" -site:github.com` | InvokeAI |  | InvokeAI body fingerprint. |
| ⚪ | `intext:"taskRunList" -site:github.com` | Kestra |  | Kestra body fingerprint. |
| ⚪ | `intext:"LightRAG" -site:github.com` | LightRAG |  | LightRAG body fingerprint. |
| ⚪ | `intext:"Llama-Guard-3" -site:github.com` | LlamaGuard |  | LlamaGuard body fingerprint. |
| ⚪ | `intext:"focusMode" -site:github.com` | Perplexica |  | Perplexica body fingerprint. |
| ⚪ | `intext:"AUTOMATIC1111" -site:github.com` | Stable Diffusion WebUI (AUTOMATIC1111) |  | Stable Diffusion WebUI (AUTOMATIC1111) body fingerprint. |
| ⚪ | `intext:"StyleTTS" -site:github.com` | StyleTTS2 |  | StyleTTS2 body fingerprint. |
| ⚪ | `intext:"buildIdBasedVersioning" -site:github.com` | Temporal Workflow |  | Temporal Workflow body fingerprint. |
| ⚪ | `intext:"nodeVersion" -site:github.com` | Trino / Presto |  | Trino / Presto body fingerprint. |
| ⚪ | `intext:"WhisperX" -site:github.com` | Whisper ASR |  | Whisper ASR body fingerprint. |
| ⚪ | `intext:"WhisperLive" -site:github.com` | WhisperLive |  | WhisperLive body fingerprint. |
| 🟤 | `intext:"abliterated" -site:github.com` | Abliterated/refusal-stripped Ollama models |  | Abliterated/refusal-stripped Ollama models body fingerprint. |
| 🟤 | `intext:"qwen3.5-abliterated" -site:github.com` | Abliterated/refusal-stripped Ollama models |  | Abliterated/refusal-stripped Ollama models body fingerprint. |
| 🟤 | `intext:"reworkd" -site:github.com` | AgentGPT |  | AgentGPT body fingerprint. |
| 🟤 | `intext:"agno-agents" -site:github.com` | Agno (formerly Phidata) |  | Agno (formerly Phidata) body fingerprint. |
| 🟤 | `intext:"AllTalk" -site:github.com` | AllTalk TTS |  | AllTalk TTS body fingerprint. |
| 🟤 | `intext:"andurilapis" -site:github.com` | Anduril Lattice |  | Anduril Lattice body fingerprint. |
| 🟤 | `intext:"arangodb" -site:github.com` | ArangoDB |  | ArangoDB body fingerprint. |
| 🟤 | `intext:"arize-phoenix" -site:github.com` | Arize Phoenix |  | Arize Phoenix body fingerprint. |
| 🟤 | `intext:"audiocraft" -site:github.com` | AudioCraft / MusicGen |  | AudioCraft / MusicGen body fingerprint. |
| 🟤 | `intext:"autogen" -site:github.com` | AutoGen / AutoGen Studio |  | AutoGen / AutoGen Studio body fingerprint. |
| 🟤 | `intext:"suno-ai" -site:github.com` | Bark TTS |  | Bark TTS body fingerprint. |
| 🟤 | `intext:"bentoml" -site:github.com` | BentoML |  | BentoML body fingerprint. |
| 🟤 | `intext:"cadence-web" -site:github.com` | Cadence Workflow |  | Cadence Workflow body fingerprint. |
| 🟤 | `intext:"Chainlit" -site:github.com` | Chainlit |  | Chainlit body fingerprint. |
| 🟤 | `intext:"chatterbox" -site:github.com` | Chatterbox TTS |  | Chatterbox TTS body fingerprint. |
| 🟤 | `intext:"chromadb" -site:github.com` | ChromaDB |  | ChromaDB body fingerprint. |
| 🟤 | `intext:"cognita" -site:github.com` | Cognita |  | Cognita body fingerprint. |
| 🟤 | `intext:"truefoundry" -site:github.com` | Cognita |  | Cognita body fingerprint. |
| 🟤 | `intext:"comet-ml" -site:github.com` | Comet ML |  | Comet ML body fingerprint. |
| 🟤 | `intext:"comet" -site:github.com` | Comet Opik |  | Comet Opik body fingerprint. |
| 🟤 | `intext:"dagster_webserver_version" -site:github.com` | Dagster |  | Dagster body fingerprint. |
| 🟤 | `intext:"danswer" -site:github.com` | Danswer / Onyx |  | Danswer / Onyx body fingerprint. |
| 🟤 | `intext:"connector" -site:github.com` | Danswer / Onyx |  | Danswer / Onyx body fingerprint. |
| 🟤 | `intext:"datahubproject" -site:github.com` | DataHub |  | DataHub body fingerprint. |
| 🟤 | `intext:"deepeval" -site:github.com` | DeepEval |  | DeepEval body fingerprint. |
| 🟤 | `intext:"system_health" -site:github.com` | Deepgram Self-Hosted |  | Deepgram Self-Hosted body fingerprint. |
| 🟤 | `intext:"active_batch_requests" -site:github.com` | Deepgram Self-Hosted |  | Deepgram Self-Hosted body fingerprint. |
| 🟤 | `intext:"_catalog" -site:github.com` | Docker Registry |  | Docker Registry body fingerprint. |
| 🟤 | `intext:"dyad-generated-app" -site:github.com` | Dyad |  | Dyad body fingerprint. |
| 🟤 | `intext:"f5-tts" -site:github.com` | F5-TTS / E2-TTS |  | F5-TTS / E2-TTS body fingerprint. |
| 🟤 | `intext:"F5_TTS" -site:github.com` | F5-TTS / E2-TTS |  | F5-TTS / E2-TTS body fingerprint. |
| 🟤 | `intext:"FastMCP" -site:github.com` | FastMCP |  | FastMCP body fingerprint. |
| 🟤 | `intext:"fauxpilot" -site:github.com` | FauxPilot |  | FauxPilot body fingerprint. |
| 🟤 | `intext:"codegen" -site:github.com` | FauxPilot |  | FauxPilot body fingerprint. |
| 🟤 | `intext:"feast" -site:github.com` | Feast Feature Store |  | Feast Feature Store body fingerprint. |
| 🟤 | `intext:"feature_names" -site:github.com` | Feast Feature Store |  | Feast Feature Store body fingerprint. |
| 🟤 | `intext:"flyteadmin" -site:github.com` | Flyte |  | Flyte body fingerprint. |
| 🟤 | `intext:"gpt_researcher" -site:github.com` | GPT Researcher |  | GPT Researcher body fingerprint. |
| 🟤 | `intext:"gpt-researcher" -site:github.com` | GPT Researcher |  | GPT Researcher body fingerprint. |
| 🟤 | `intext:"GPT4All" -site:github.com` | GPT4All |  | GPT4All body fingerprint. |
| 🟤 | `intext:"gr-app" -site:github.com` | Gradio |  | Gradio body fingerprint. |
| 🟤 | `intext:"great_expectations" -site:github.com` | Great Expectations |  | Great Expectations body fingerprint. |
| 🟤 | `intext:"guardrails-ai" -site:github.com` | Guardrails AI |  | Guardrails AI body fingerprint. |
| 🟤 | `intext:"guardrailsai.com" -site:github.com` | Guardrails AI |  | Guardrails AI body fingerprint. |
| 🟤 | `intext:"hexstrike-ai" -site:github.com` | HexStrike AI |  | HexStrike AI body fingerprint. |
| 🟤 | `intext:"hexstrike" -site:github.com` | HexStrike AI |  | HexStrike AI body fingerprint. |
| 🟤 | `intext:"deepseek-v4-pro" -site:github.com` | Honeypot / Canary (fabricated model names) |  | Honeypot / Canary (fabricated model names) body fingerprint. |
| 🟤 | `intext:"glm-4.7-flash" -site:github.com` | Honeypot / Canary (fabricated model names) |  | Honeypot / Canary (fabricated model names) body fingerprint. |
| 🟤 | `intext:"tokenization_workers" -site:github.com` | Hugging Face TGI |  | Hugging Face TGI body fingerprint. |
| 🟤 | `intext:"text-generation-inference" -site:github.com` | Hugging Face TGI |  | Hugging Face TGI body fingerprint. |
| 🟤 | `intext:"inspect-ai" -site:github.com` | Inspect AI (UK AISI) |  | Inspect AI (UK AISI) body fingerprint. |
| 🟤 | `intext:"ai-proxy" -site:github.com` | Kong AI Gateway |  | Kong AI Gateway body fingerprint. |
| 🟤 | `intext:"kotaemon" -site:github.com` | Kotaemon |  | Kotaemon body fingerprint. |
| 🟤 | `intext:"kubeflow" -site:github.com` | Kubeflow |  | Kubeflow body fingerprint. |
| 🟤 | `intext:"ml-pipeline" -site:github.com` | Kubeflow |  | Kubeflow body fingerprint. |
| 🟤 | `intext:"llama-factory" -site:github.com` | LLaMA Factory |  | LLaMA Factory body fingerprint. |
| 🟤 | `intext:"lm studio" -site:github.com` | LM Studio |  | LM Studio body fingerprint. |
| 🟤 | `intext:"lakera-guard" -site:github.com` | Lakera Guard |  | Lakera Guard body fingerprint. |
| 🟤 | `intext:"lakera" -site:github.com` | Lakera Guard |  | Lakera Guard body fingerprint. |
| 🟤 | `intext:"lancedb" -site:github.com` | LanceDB |  | LanceDB body fingerprint. |
| 🟤 | `intext:"livekit-agents" -site:github.com` | LiveKit Agents |  | LiveKit Agents body fingerprint. |
| 🟤 | `intext:"localai" -site:github.com` | LocalAI |  | LocalAI body fingerprint. |
| 🟤 | `intext:"modelcontextprotocol" -site:github.com` | MCP Server (generic) |  | MCP Server (generic) body fingerprint. |
| 🟤 | `intext:"mcp.json" -site:github.com` | MCP Server (generic) |  | MCP Server (generic) body fingerprint. |
| 🟤 | `intext:"marquezproject" -site:github.com` | Marquez (OpenLineage) |  | Marquez (OpenLineage) body fingerprint. |
| 🟤 | `intext:"mem0migrations" -site:github.com` | Mem0 |  | Mem0 body fingerprint. |
| 🟤 | `intext:"memgraph" -site:github.com` | Memgraph |  | Memgraph body fingerprint. |
| 🟤 | `intext:"milvus" -site:github.com` | Milvus |  | Milvus body fingerprint. |
| 🟤 | `intext:"mozilla-tts" -site:github.com` | Mozilla TTS |  | Mozilla TTS body fingerprint. |
| 🟤 | `intext:"nemo-guardrails" -site:github.com` | NeMo Guardrails |  | NeMo Guardrails body fingerprint. |
| 🟤 | `intext:"nemoguardrails" -site:github.com` | NeMo Guardrails |  | NeMo Guardrails body fingerprint. |
| 🟤 | `intext:"neo4j_version" -site:github.com` | Neo4j |  | Neo4j body fingerprint. |
| 🟤 | `intext:"neon.tech" -site:github.com` | Neon Postgres |  | Neon Postgres body fingerprint. |
| 🟤 | `intext:"open-webui" -site:github.com` | Open WebUI |  | Open WebUI body fingerprint. |
| 🟤 | `intext:"clawdbot" -site:github.com` | OpenClaw / Clawdbot |  | OpenClaw / Clawdbot body fingerprint. |
| 🟤 | `intext:"opendevin" -site:github.com` | OpenHands (formerly OpenDevin) |  | OpenHands (formerly OpenDevin) body fingerprint. |
| 🟤 | `intext:"opensearch" -site:github.com` | OpenSearch |  | OpenSearch body fingerprint. |
| 🟤 | `intext:"opensearch-dashboards" -site:github.com` | OpenSearch |  | OpenSearch body fingerprint. |
| 🟤 | `intext:"se_extractor" -site:github.com` | OpenVoice |  | OpenVoice body fingerprint. |
| 🟤 | `intext:"optuna" -site:github.com` | Optuna Dashboard |  | Optuna Dashboard body fingerprint. |
| 🟤 | `intext:"Orpheus" -site:github.com` | Orpheus-FastAPI TTS |  | Orpheus-FastAPI TTS body fingerprint. |
| 🟤 | `intext:"pipecat-ai" -site:github.com` | Pipecat |  | Pipecat body fingerprint. |
| 🟤 | `intext:"piper-tts" -site:github.com` | Piper TTS |  | Piper TTS body fingerprint. |
| 🟤 | `intext:"piper-http" -site:github.com` | Piper TTS |  | Piper TTS body fingerprint. |
| 🟤 | `intext:"playwright-mcp" -site:github.com` | Playwright MCP Server |  | Playwright MCP Server body fingerprint. |
| 🟤 | `intext:"prefect" -site:github.com` | Prefect Server |  | Prefect Server body fingerprint. |
| 🟤 | `intext:"privategpt" -site:github.com` | PrivateGPT |  | PrivateGPT body fingerprint. |
| 🟤 | `intext:"prodigy" -site:github.com` | Prodigy |  | Prodigy body fingerprint. |
| 🟤 | `intext:"pyannote" -site:github.com` | Pyannote |  | Pyannote body fingerprint. |
| 🟤 | `intext:"quivr" -site:github.com` | Quivr |  | Quivr body fingerprint. |
| 🟤 | `intext:"ragapp" -site:github.com` | Ragapp |  | Ragapp body fingerprint. |
| 🟤 | `intext:"/admin" -site:github.com` | Ragapp |  | Ragapp body fingerprint. |
| 🟤 | `intext:"coding_assistant_caps" -site:github.com` | Refact.ai (self-hosted) |  | Refact.ai (self-hosted) body fingerprint. |
| 🟤 | `intext:"refact-caps" -site:github.com` | Refact.ai (self-hosted) |  | Refact.ai (self-hosted) body fingerprint. |
| 🟤 | `intext:"Restate" -site:github.com` | Restate |  | Restate body fingerprint. |
| 🟤 | `intext:"restatedev" -site:github.com` | Restate |  | Restate body fingerprint. |
| 🟤 | `intext:"retell-ai" -site:github.com` | Retell AI |  | Retell AI body fingerprint. |
| 🟤 | `intext:"retell-sdk" -site:github.com` | Retell AI |  | Retell AI body fingerprint. |
| 🟤 | `intext:"sglang" -site:github.com` | SGLang |  | SGLang body fingerprint. |
| 🟤 | `intext:"swe-agent" -site:github.com` | SWE-agent |  | SWE-agent body fingerprint. |
| 🟤 | `intext:"swe-bench" -site:github.com` | SWE-agent |  | SWE-agent body fingerprint. |
| 🟤 | `intext:"selenium" -site:github.com` | Selenium Grid |  | Selenium Grid body fingerprint. |
| 🟤 | `intext:"skyvern" -site:github.com` | Skyvern |  | Skyvern body fingerprint. |
| 🟤 | `intext:"sourcegraph-frontend" -site:github.com` | Sourcegraph / Cody |  | Sourcegraph / Cody body fingerprint. |
| 🟤 | `intext:"speechbrain.pretrained" -site:github.com` | SpeechBrain |  | SpeechBrain body fingerprint. |
| 🟤 | `intext:"txt2img" -site:github.com` | Stable Diffusion WebUI (AUTOMATIC1111) |  | Stable Diffusion WebUI (AUTOMATIC1111) body fingerprint. |
| 🟤 | `intext:"streamlit-app" -site:github.com` | Streamlit |  | Streamlit body fingerprint. |
| 🟤 | `intext:"styletts2" -site:github.com` | StyleTTS2 |  | StyleTTS2 body fingerprint. |
| 🟤 | `intext:"supabase" -site:github.com` | Supabase |  | Supabase body fingerprint. |
| 🟤 | `intext:"surrealdb" -site:github.com` | SurrealDB |  | SurrealDB body fingerprint. |
| 🟤 | `intext:"sweepai" -site:github.com` | Sweep AI |  | Sweep AI body fingerprint. |
| 🟤 | `intext:"tabbyml" -site:github.com` | Tabby (TabbyML) |  | Tabby (TabbyML) body fingerprint. |
| 🟤 | `intext:"model_version_status" -site:github.com` | TensorFlow Serving |  | TensorFlow Serving body fingerprint. |
| 🟤 | `intext:"serving_default" -site:github.com` | TensorFlow Serving |  | TensorFlow Serving body fingerprint. |
| 🟤 | `intext:"text-embeddings-inference" -site:github.com` | Text Embeddings Inference (TEI) |  | Text Embeddings Inference (TEI) body fingerprint. |
| 🟤 | `intext:"feature-extraction" -site:github.com` | Text Embeddings Inference (TEI) |  | Text Embeddings Inference (TEI) body fingerprint. |
| 🟤 | `intext:"timescaledb" -site:github.com` | Timescale / TimescaleDB |  | Timescale / TimescaleDB body fingerprint. |
| 🟤 | `intext:"tortoise-tts" -site:github.com` | Tortoise TTS |  | Tortoise TTS body fingerprint. |
| 🟤 | `intext:"voice_samples" -site:github.com` | Tortoise TTS |  | Tortoise TTS body fingerprint. |
| 🟤 | `intext:"trulens_feedback" -site:github.com` | TruLens |  | TruLens body fingerprint. |
| 🟤 | `intext:"typesense" -site:github.com` | Typesense |  | Typesense body fingerprint. |
| 🟤 | `intext:"unsloth" -site:github.com` | Unsloth |  | Unsloth body fingerprint. |
| 🟤 | `intext:"unstructured-api" -site:github.com` | Unstructured API |  | Unstructured API body fingerprint. |
| 🟤 | `intext:"Verba" -site:github.com` | Verba |  | Verba body fingerprint. |
| 🟤 | `intext:"goldenverba" -site:github.com` | Verba |  | Verba body fingerprint. |
| 🟤 | `intext:"vespa" -site:github.com` | Vespa |  | Vespa body fingerprint. |
| 🟤 | `intext:"vigil" -site:github.com` | Vigil LLM |  | Vigil LLM body fingerprint. |
| 🟤 | `intext:"vocode" -site:github.com` | Vocode |  | Vocode body fingerprint. |
| 🟤 | `intext:"vocode-python" -site:github.com` | Vocode |  | Vocode body fingerprint. |
| 🟤 | `intext:"wandb" -site:github.com` | Weights & Biases (W&B) |  | Weights & Biases (W&B) body fingerprint. |
| 🟤 | `intext:"wandb-local" -site:github.com` | Weights & Biases (W&B) |  | Weights & Biases (W&B) body fingerprint. |
| 🟤 | `intext:"faster-whisper" -site:github.com` | Whisper ASR |  | Whisper ASR body fingerprint. |
| 🟤 | `intext:"windmill.dev" -site:github.com` | Windmill |  | Windmill body fingerprint. |
| 🟤 | `intext:"worker_count" -site:github.com` | Windmill |  | Windmill body fingerprint. |
| 🟤 | `intext:"bolt.diy" -site:github.com` | bolt.diy / bolt.new |  | bolt.diy / bolt.new body fingerprint. |
| 🟤 | `intext:"bolt.new" -site:github.com` | bolt.diy / bolt.new |  | bolt.diy / bolt.new body fingerprint. |
| 🟤 | `intext:"code-server" -site:github.com` | code-server (Coder) |  | code-server (Coder) body fingerprint. |
| 🟤 | `intext:"coder-options" -site:github.com` | code-server (Coder) |  | code-server (Coder) body fingerprint. |
| 🟤 | `intext:"dcm4che" -site:github.com` | dcm4chee Archive |  | dcm4chee Archive body fingerprint. |
| 🟤 | `intext:"dcm4chee-arc" -site:github.com` | dcm4chee Archive |  | dcm4chee Archive body fingerprint. |
| 🟤 | `intext:"h2oGPT" -site:github.com` | h2oGPT |  | h2oGPT body fingerprint. |
| 🟤 | `intext:"infinity_emb" -site:github.com` | infinity-embedding |  | infinity-embedding body fingerprint. |
| 🟤 | `intext:"llama.cpp" -site:github.com` | llama.cpp |  | llama.cpp body fingerprint. |
| 🟤 | `intext:"pgvector" -site:github.com` | pgvector |  | pgvector body fingerprint. |
| 🟤 | `intext:"so-vits-svc" -site:github.com` | so-vits-svc |  | so-vits-svc body fingerprint. |

## Vulnerable Files
_60 dorks_

| T | Dork | Service | CVE | Notes |
|---|------|---------|-----|-------|
| 🟡 | `inurl:"/agents" intext:"Agno"` | Agno |  | Agno endpoint co-anchored on 'Agno'. Pre-run disclosure: agent descriptions name data sources (PostgreSQL, email, Asana). Manifest = CRITICAL. |
| 🟡 | `inurl:"/api/v1/settings" intext:"Argo"` | Argo CD |  | Argo CD endpoint co-anchored on 'Argo'. Public-by-design; OIDC issuer URL discloses Azure AD tenant UUID / Okta hostname = operator attribution. |
| 🟡 | `inurl:"/v1/traces" intext:"Arize"` | Arize Phoenix |  | Arize Phoenix endpoint co-anchored on 'Arize'. Returns 200 to unauthenticated POST on 100% of surveyed instances. OTLP data-poisoning of cost analytics + eval scores. |
| 🟡 | `inurl:"/api/version" intext:"AutoGen"` | AutoGen Studio |  | AutoGen Studio endpoint co-anchored on 'AutoGen'. Returns Microsoft AutoGen version JSON. Auth disabled by default; /api/teams leaks inline API keys. |
| 🟡 | `inurl:"/api/v2/tenants/default_tenant/databases/default_database/collections" -site:github.com` | ChromaDB |  | ChromaDB: v2 collection path, no auth on default. RAG knowledge bases + agent memory + PII docs. |
| 🟡 | `inurl:"/api/v2/tenants/default_tenant/databases/default_database/collections" intext:"ChromaDB"` | ChromaDB |  | ChromaDB endpoint co-anchored on 'ChromaDB'. v2 collection path, no auth on default. RAG knowledge bases + agent memory + PII docs. |
| 🟡 | `inurl:"/api/v1/cognify" -site:github.com` | Cognee |  | Cognee: Knowledge-graph ingestion endpoint. Memory pipeline surface. |
| 🟡 | `inurl:"/api/v1/cognify" intext:"Cognee"` | Cognee |  | Cognee endpoint co-anchored on 'Cognee'. Knowledge-graph ingestion endpoint. Memory pipeline surface. |
| 🟡 | `inurl:"/v1/catalog/services" intext:"Consul"` | Consul |  | Consul endpoint co-anchored on 'Consul'. Service catalog. Internal topology. |
| 🟡 | `inurl:"/v2/_catalog" intext:"Registry"` | Docker Registry |  | Docker Registry endpoint co-anchored on 'Registry'. Image catalog. Operator attribution via image names (Jetson, PACS, finance). |
| 🟡 | `inurl:"/config_dump" intext:"Envoy"` | Envoy Admin |  | Envoy Admin endpoint co-anchored on 'Envoy'. Full Envoy config JSON. downstream_auth_password.inline_string = plaintext Redis-AUTH. |
| 🟡 | `inurl:"/v1/sys/health" intext:"HashiCorp"` | HashiCorp Vault |  | HashiCorp Vault endpoint co-anchored on 'HashiCorp'. Vault health + sealed state. Initialization status. |
| 🟡 | `inurl:"/v2/models/" intext:"KServe"` | KServe |  | KServe endpoint co-anchored on 'KServe'. V2 inference protocol model list. |
| 🟡 | `inurl:"/services" intext:"Kong"` | Kong Admin |  | Kong Admin endpoint co-anchored on 'Kong'. Kong admin API (port 8001) no auth by default. Full gateway reconfiguration. |
| 🟡 | `inurl:"/api/v1/runs" intext:"Kubeflow"` | Kubeflow |  | Kubeflow endpoint co-anchored on 'Kubeflow'. Pipeline runs. ML workflow + artifact paths. |
| 🟡 | `inurl:"/v1/agents/" intext:"Letta"` | Letta/MemGPT |  | Letta/MemGPT endpoint co-anchored on 'Letta'. Agent memory store. Lists agents + persisted memory blocks. |
| 🟡 | `inurl:"/v1/model/info" intext:"LiteLLM"` | LiteLLM |  | LiteLLM endpoint co-anchored on 'LiteLLM'. Reveals litellm_params incl. real api_base behind advertised model IDs. Model-impersonation discriminator. |
| 🟡 | `inurl:"/api/v1/collections" -site:github.com` | Milvus |  | Milvus: Collection list. Attu GUI on :3000 loads without auth. |
| 🟡 | `inurl:"/api/v1/collections" intext:"Milvus"` | Milvus |  | Milvus endpoint co-anchored on 'Milvus'. Collection list. Attu GUI on :3000 loads without auth. |
| 🟡 | `inurl:"/metrics" intext:"DCGM"` | NVIDIA DCGM |  | NVIDIA DCGM endpoint co-anchored on 'DCGM'. GPU telemetry. Utilization + process names. |
| 🟡 | `inurl:"/v1/policies" intext:"Policy"` | Open Policy Agent |  | Open Policy Agent endpoint co-anchored on 'Policy'. OPA policy list. Exposes authz logic when admin API unauth. |
| 🟡 | `inurl:"/api/config" intext:"WebUI"` | Open WebUI |  | Open WebUI endpoint co-anchored on 'WebUI'. Config endpoint. signup-enabled flag. First-user-admin. |
| 🟡 | `inurl:"/api/v1/private/projects" -site:github.com` | Opik |  | Opik: Project list + operator name without auth. Full API write (experiments, prompts, datasets). |
| 🟡 | `inurl:"/api/v1/private/projects" intext:"Opik"` | Opik |  | Opik endpoint co-anchored on 'Opik'. Project list + operator name without auth. Full API write (experiments, prompts, datasets). |
| 🟡 | `inurl:"/api/user/email" -site:github.com` | Promptfoo |  | Promptfoo: Returns {"email":null} unauth. Best single-probe auth detector. Provider configs + eval datasets readable. |
| 🟡 | `inurl:"/api/user/email" intext:"Promptfoo"` | Promptfoo |  | Promptfoo endpoint co-anchored on 'Promptfoo'. Returns {"email":null} unauth. Best single-probe auth detector. Provider configs + eval datasets readable. |
| 🟡 | `inurl:"/collections" intext:"Qdrant"` | Qdrant |  | Qdrant endpoint co-anchored on 'Qdrant'. Collection list. No auth by default. Raw embeddings + payloads. |
| 🟡 | `inurl:"FT._LIST" intext:"Redis"` | Redis Stack |  | Redis Stack endpoint co-anchored on 'Redis'. RESP command listing all RediSearch index names. 78/78 surveyed unauth. Vector index inventory. |
| 🟡 | `inurl:"/hello" intext:"SuperTokens"` | SuperTokens |  | SuperTokens endpoint co-anchored on 'SuperTokens'. Returns exactly 'Hello' on port 3567. No API key by default. Full user identity store open. |
| 🟡 | `inurl:"/__vite_ping" intext:"Vite"` | Vite Dev Server |  | Vite Dev Server endpoint co-anchored on 'Vite'. Returns 'pong'. Vite dev server in production exposes all src/ TypeScript at /src/<file>. |
| 🟡 | `inurl:"/v1/objects" intext:"Weaviate"` | Weaviate |  | Weaviate endpoint co-anchored on 'Weaviate'. Object store. 100% unauth at population scale. |
| 🟡 | `inurl:"/api/v2/sessions-ordered" -site:github.com` | Zep CE |  | Zep CE: Agent memory sessions. Empty api_secret default = bypass via 'Api-Key ' trailing space. |
| 🟡 | `inurl:"/api/v2/sessions-ordered" intext:"Zep"` | Zep CE |  | Zep CE endpoint co-anchored on 'Zep'. Agent memory sessions. Empty api_secret default = bypass via 'Api-Key ' trailing space. |
| 🟡 | `inurl:"/v3/kv/range" intext:"etcd"` | etcd |  | etcd endpoint co-anchored on 'etcd'. Key-value range read. Cluster secrets when unauth. |
| 🟡 | `inurl:"/rest/settings" intext:"n8n"` | n8n |  | n8n endpoint co-anchored on 'n8n'. Returns n8n config incl. publicApi.enabled. Confirms presence; ungated-legacy pattern. |
| 🟡 | `inurl:"/v1/metrics" intext:"vLLM"` | vLLM |  | vLLM endpoint co-anchored on 'vLLM'. Prometheus vllm: metrics incl. model path + token counts unauth. ClimateGPT: 92M prompt tokens exposed. |
| ⚪ | `inurl:"/agents" -site:github.com` | Agno |  | Agno: Pre-run disclosure: agent descriptions name data sources (PostgreSQL, email, Asana). Manifest = CRITICAL. |
| ⚪ | `inurl:"/api/v1/settings" -site:github.com` | Argo CD |  | Argo CD: Public-by-design; OIDC issuer URL discloses Azure AD tenant UUID / Okta hostname = operator attribution. |
| ⚪ | `inurl:"/v1/traces" -site:github.com` | Arize Phoenix |  | Arize Phoenix: Returns 200 to unauthenticated POST on 100% of surveyed instances. OTLP data-poisoning of cost analytics + eval scores. |
| ⚪ | `inurl:"/api/version" -site:github.com` | AutoGen Studio |  | AutoGen Studio: Returns Microsoft AutoGen version JSON. Auth disabled by default; /api/teams leaks inline API keys. |
| ⚪ | `inurl:"/v1/catalog/services" -site:github.com` | Consul |  | Consul: Service catalog. Internal topology. |
| ⚪ | `inurl:"/v2/_catalog" -site:github.com` | Docker Registry |  | Docker Registry: Image catalog. Operator attribution via image names (Jetson, PACS, finance). |
| ⚪ | `inurl:"/config_dump" -site:github.com` | Envoy Admin |  | Envoy Admin: Full Envoy config JSON. downstream_auth_password.inline_string = plaintext Redis-AUTH. |
| ⚪ | `inurl:"/v1/sys/health" -site:github.com` | HashiCorp Vault |  | HashiCorp Vault: Vault health + sealed state. Initialization status. |
| ⚪ | `inurl:"/v2/models/" -site:github.com` | KServe |  | KServe: V2 inference protocol model list. |
| ⚪ | `inurl:"/services" -site:github.com` | Kong Admin |  | Kong Admin: Kong admin API (port 8001) no auth by default. Full gateway reconfiguration. |
| ⚪ | `inurl:"/api/v1/runs" -site:github.com` | Kubeflow |  | Kubeflow: Pipeline runs. ML workflow + artifact paths. |
| ⚪ | `inurl:"/v1/agents/" -site:github.com` | Letta/MemGPT |  | Letta/MemGPT: Agent memory store. Lists agents + persisted memory blocks. |
| ⚪ | `inurl:"/v1/model/info" -site:github.com` | LiteLLM |  | LiteLLM: Reveals litellm_params incl. real api_base behind advertised model IDs. Model-impersonation discriminator. |
| ⚪ | `inurl:"/metrics" -site:github.com` | NVIDIA DCGM |  | NVIDIA DCGM: GPU telemetry. Utilization + process names. |
| ⚪ | `inurl:"/v1/policies" -site:github.com` | Open Policy Agent |  | Open Policy Agent: OPA policy list. Exposes authz logic when admin API unauth. |
| ⚪ | `inurl:"/api/config" -site:github.com` | Open WebUI |  | Open WebUI: Config endpoint. signup-enabled flag. First-user-admin. |
| ⚪ | `inurl:"/collections" -site:github.com` | Qdrant |  | Qdrant: Collection list. No auth by default. Raw embeddings + payloads. |
| ⚪ | `inurl:"FT._LIST" -site:github.com` | Redis Stack |  | Redis Stack: RESP command listing all RediSearch index names. 78/78 surveyed unauth. Vector index inventory. |
| ⚪ | `inurl:"/hello" -site:github.com` | SuperTokens |  | SuperTokens: Returns exactly 'Hello' on port 3567. No API key by default. Full user identity store open. |
| ⚪ | `inurl:"/__vite_ping" -site:github.com` | Vite Dev Server |  | Vite Dev Server: Returns 'pong'. Vite dev server in production exposes all src/ TypeScript at /src/<file>. |
| ⚪ | `inurl:"/v1/objects" -site:github.com` | Weaviate |  | Weaviate: Object store. 100% unauth at population scale. |
| ⚪ | `inurl:"/v3/kv/range" -site:github.com` | etcd |  | etcd: Key-value range read. Cluster secrets when unauth. |
| ⚪ | `inurl:"/rest/settings" -site:github.com` | n8n |  | n8n: Returns n8n config incl. publicApi.enabled. Confirms presence; ungated-legacy pattern. |
| ⚪ | `inurl:"/v1/metrics" -site:github.com` | vLLM |  | vLLM: Prometheus vllm: metrics incl. model path + token counts unauth. ClimateGPT: 92M prompt tokens exposed. |

## Vulnerable Servers
_27 dorks_

| T | Dork | Service | CVE | Notes |
|---|------|---------|-----|-------|
| 🟡 | `intitle:"Airflow" intext:"version" -site:github.com` | Apache Airflow | CVE-2020-13927 | Apache Airflow version disclosure. CVE-2020-13927. auth on with 8 documented bypass patterns |
| 🟡 | `intitle:"Apache Flink Web Dashboard" intext:"version" -site:github.com` | Apache Flink | CVE-2020-17518 | Apache Flink version disclosure. CVE-2020-17518. no auth by default |
| 🟡 | `intitle:"Apache Superset" intext:"version" -site:github.com` | Apache Superset | CVE-2023-27524 | Apache Superset version disclosure. CVE-2023-27524. default SECRET_KEY leads to auth bypass |
| 🟡 | `intitle:"Argilla" intext:"version" -site:github.com` | Argilla | CVE-2023-38686 | Argilla version disclosure. CVE-2023-38686. auth on since v1.x; default-public workspace misconfiguration seen |
| 🟡 | `intitle:"Argo" intext:"version" -site:github.com` | Argo Workflows | CVE-2026-28229 | Argo Workflows version disclosure. CVE-2026-28229. --auth-mode=server disables all credential requirements |
| 🟡 | `intitle:"authentik" intext:"version" -site:github.com` | Authentik | CVE-2024-47070 | Authentik version disclosure. CVE-2024-47070. login required; /api/v3/root/config/ pre-auth accessible |
| 🟡 | `intitle:"CKAN" intext:"version" -site:github.com` | CKAN | CVE-2023-32321 | CKAN version disclosure. CVE-2023-32321. reads open by design |
| 🟡 | `intitle:"Casdoor" intext:"version" -site:github.com` | Casdoor | CVE-2024-41657 | Casdoor version disclosure. CVE-2024-41657. default-creds built-in/admin/123 |
| 🟡 | `intitle:"Flowise" intext:"version" -site:github.com` | Flowise | CVE-2024-36420 | Flowise version disclosure. CVE-2024-36420. mixed auth; pre-1.8.2 auth bypass via path traversal |
| 🟡 | `intitle:"GPT-SoVITS" intext:"version" -site:github.com` | GPT-SoVITS | CVE-2025-49833 | GPT-SoVITS version disclosure. CVE-2025-49833. no auth by default; command injection RCE |
| 🟡 | `intitle:"GitHub Enterprise" intext:"version" -site:github.com` | GitHub Enterprise Server (GHES) | CVE-2024-9487 | GitHub Enterprise Server (GHES) version disclosure. CVE-2024-9487. OAuth enforced; SAML bypass on affected versions |
| 🟡 | `intitle:"Grafana" intext:"version" -site:github.com` | Grafana | CVE-2021-43798 | Grafana version disclosure. CVE-2021-43798. anonymous access misconfiguration common |
| 🟡 | `intitle:"Jupyter" intext:"version" -site:github.com` | Jupyter Notebook / JupyterLab | CVE-2019-10255 | Jupyter Notebook / JupyterLab version disclosure. CVE-2019-10255. modern deployments consistently locked; older --NotebookApp.token= blank is unauth RCE |
| 🟡 | `intitle:"JupyterHub" intext:"version" -site:github.com` | JupyterHub | CVE-2026-33709 | JupyterHub version disclosure. CVE-2026-33709. auth on by default since v1.x |
| 🟡 | `intitle:"Keycloak" intext:"version" -site:github.com` | Keycloak | CVE-2024-3656 | Keycloak version disclosure. CVE-2024-3656. login required for admin; OIDC discovery endpoints unauthenticated |
| 🟡 | `intitle:"Label Studio" intext:"version" -site:github.com` | Label Studio | CVE-2022-25011 | Label Studio version disclosure. CVE-2022-25011. mandatory auth; /api/projects sometimes misconfigured readable |
| 🟡 | `intitle:"Langflow" intext:"version" -site:github.com` | Langflow | CVE-2026-33017 | Langflow version disclosure. CVE-2026-33017. LANGFLOW_AUTO_LOGIN gating in v1.5+, often left open |
| 🟡 | `intitle:"MLflow" intext:"version" -site:github.com` | MLflow | CVE-2024-37052 | MLflow version disclosure. CVE-2024-37052. no auth by default |
| 🟡 | `intitle:"Mage" intext:"version" -site:github.com` | Mage.ai | CVE-2025-2129 | Mage.ai version disclosure. CVE-2025-2129. no auth pre-v0.9.78; ~1,045 confirmed unauth at disclosure |
| 🟡 | `intitle:"Metabase" intext:"version" -site:github.com` | Metabase | CVE-2023-38646 | Metabase version disclosure. CVE-2023-38646. setup-wizard bypass; has-user-setup: false = exploitable |
| 🟡 | `intitle:"MinIO Browser" intext:"version" -site:github.com` | MinIO | CVE-2023-28432 | MinIO version disclosure. CVE-2023-28432. default-creds minioadmin:minioadmin |
| 🟡 | `intitle:"Conductor UI" intext:"version" -site:github.com` | Netflix Conductor | CVE-2020-9296 | Netflix Conductor version disclosure. CVE-2020-9296. no auth by default |
| 🟡 | `intitle:"OpenMetadata" intext:"version" -site:github.com` | OpenMetadata | CVE-2024-28255 | OpenMetadata version disclosure. CVE-2024-28255. auth on but CVE-2024-28255 bypass on <1.3.1; actively exploited |
| 🟡 | `intitle:"RVC" intext:"version" -site:github.com` | RVC (Retrieval-based Voice Conversion) | CVE-2025-43842 | RVC (Retrieval-based Voice Conversion) version disclosure. CVE-2025-43842. no auth by default; RCE via pickle deserialization |
| 🟡 | `intitle:"Ray Dashboard" intext:"version" -site:github.com` | Ray Dashboard | CVE-2023-48022 | Ray Dashboard version disclosure. CVE-2023-48022. no auth; ShadowRay actively exploited |
| 🟡 | `intitle:"RedisInsight" intext:"version" -site:github.com` | Redis | CVE-2025-49844 | Redis version disclosure. CVE-2025-49844. no password by default on ~68k of 245k instances |
| 🟡 | `intitle:"n8n" intext:"version" -site:github.com` | n8n | CVE-2024-25289 | n8n version disclosure. CVE-2024-25289. basicauth optional and frequently skipped |

## Error Messages
_27 dorks_

| T | Dork | Service | CVE | Notes |
|---|------|---------|-----|-------|
| 🟡 | `"anthropic.AuthenticationError" -site:github.com -site:stackoverflow.com` | Anthropic SDK |  | Anthropic SDK auth error in production traceback. |
| 🟡 | `"Traceback (most recent call last)" intext:"uvicorn" intext:"openai" -site:github.com -site:stackoverflow.com` | FastAPI |  | FastAPI/uvicorn traceback in an LLM app. Full call stack + file paths. |
| 🟡 | `"litellm.exceptions.AuthenticationError" -site:github.com -site:stackoverflow.com` | LiteLLM |  | LiteLLM auth exception. Reveals proxy config + provider. |
| 🟡 | `"mlflow.exceptions.MlflowException" -site:github.com -site:stackoverflow.com` | MLflow |  | MLflow exception. Experiment names, artifact paths, tracking URI. |
| 🟡 | `"openai.AuthenticationError" -site:github.com -site:stackoverflow.com` | OpenAI SDK |  | OpenAI SDK auth-error traceback in a DEBUG-mode app. Leaks call site + sometimes key tail. |
| 🟡 | `"openai.RateLimitError" "Traceback" -site:github.com -site:stackoverflow.com` | OpenAI SDK |  | OpenAI rate-limit traceback. Confirms live key + the calling code path. |
| 🟡 | `"qdrant_client.http.exceptions.UnexpectedResponse" -site:github.com -site:stackoverflow.com` | Qdrant |  | Qdrant client exception. Leaks collection names + endpoint. |
| 🟡 | `"streamlit" "KeyError" intext:"st.secrets" -site:github.com -site:stackoverflow.com` | Streamlit |  | Streamlit secrets KeyError. Confirms a secrets.toml exists and names its keys. |
| 🟡 | `"weaviate.exceptions.UnexpectedStatusCodeException" -site:github.com -site:stackoverflow.com` | Weaviate |  | Weaviate client exception. Leaks schema/class names + host. |
| 🟡 | `"transformers" "is not a local folder and is not a valid model identifier" -site:github.com -site:stackoverflow.com` | transformers |  | Transformers model-load error leaking the local filesystem path attempted. |
| ⚪ | `"anthropic.APIStatusError" -site:github.com -site:stackoverflow.com` | Anthropic SDK |  | Anthropic API status error leaked in app output. |
| ⚪ | `"chromadb.errors" "Traceback" -site:github.com -site:stackoverflow.com` | ChromaDB |  | ChromaDB error traceback. Collection + tenant disclosure. |
| ⚪ | `"pydantic_core._pydantic_core.ValidationError" intext:"openai" -site:github.com -site:stackoverflow.com` | FastAPI |  | Pydantic validation traceback in an OpenAI-using FastAPI app. |
| ⚪ | `"torch.cuda.OutOfMemoryError" -site:github.com -site:stackoverflow.com` | GPU inference |  | CUDA OOM traceback. Confirms a live GPU inference box, leaks model + device. |
| ⚪ | `"CUDA out of memory. Tried to allocate" -site:github.com -site:stackoverflow.com` | GPU inference |  | Verbatim CUDA OOM string. GPU model-serving box in DEBUG. |
| ⚪ | `"gradio" "Traceback (most recent call last)" -site:github.com -site:stackoverflow.com` | Gradio |  | Gradio app traceback. Reveals handler code + file paths. |
| ⚪ | `"huggingface_hub.utils._errors.RepositoryNotFoundError" -site:github.com -site:stackoverflow.com` | HuggingFace |  | HF hub repo-not-found traceback. Leaks attempted model id + token state. |
| ⚪ | `"huggingface_hub" "GatedRepoError" -site:github.com -site:stackoverflow.com` | HuggingFace |  | HF gated-repo error. Reveals model id + that a token was used. |
| ⚪ | `"Internal Server Error" intext:"langchain" -site:github.com -site:stackoverflow.com` | LangChain |  | LangChain app 500 leaking framework in body. |
| ⚪ | `"langchain_core.exceptions.OutputParserException" -site:github.com -site:stackoverflow.com` | LangChain |  | LangChain output-parser exception. Leaks prompt/chain structure. |
| ⚪ | `"mlflow.exceptions.RestException" -site:github.com -site:stackoverflow.com` | MLflow |  | MLflow REST exception in production. |
| ⚪ | `"ollama._types.ResponseError" -site:github.com -site:stackoverflow.com` | Ollama |  | Ollama python client error traceback. |
| ⚪ | `"llama runner process has terminated" -site:github.com -site:stackoverflow.com` | Ollama |  | Ollama runner crash string. Confirms live Ollama + model load failure. |
| ⚪ | `"pinecone" "ApiException" "Traceback" -site:github.com -site:stackoverflow.com` | Pinecone |  | Pinecone client exception. Index name + environment leak. |
| ⚪ | `"redis.exceptions.ConnectionError" "Traceback" -site:github.com -site:stackoverflow.com` | Redis |  | Redis connection error. Host + port of the cache/vector layer. |
| ⚪ | `"sqlalchemy.exc.OperationalError" intext:"pgvector" -site:github.com -site:stackoverflow.com` | pgvector |  | SQLAlchemy error referencing pgvector. DB host + sometimes DSN. |
| ⚪ | `"vllm.engine" "RayActorError" -site:github.com -site:stackoverflow.com` | vLLM |  | vLLM+Ray engine error. Cluster topology disclosure. |

## Files Containing Juicy Info
_24 dorks_

| T | Dork | Service | CVE | Notes |
|---|------|---------|-----|-------|
| ⚪ | `intext:"AKIA" "AWS_SECRET_ACCESS_KEY" -site:github.com` | AWS |  | AWS AKIA co-anchored with AWS_SECRET_ACCESS_KEY (prefix too broad alone). |
| ⚪ | `intext:"AWS_ACCESS_KEY_ID" filetype:env` | AWS |  | AWS AWS_ACCESS_KEY_ID env-var in .env file. |
| ⚪ | `intext:"AGENTA_AUTH_KEY" "agenta" -site:github.com` | Agenta |  | Agenta AGENTA_AUTH_KEY co-anchored with agenta (prefix too broad alone). |
| ⚪ | `intext:"ANTHROPIC_API_KEY" filetype:env` | Anthropic |  | Anthropic ANTHROPIC_API_KEY env-var in .env file. |
| ⚪ | `intext:"GITHUB_TOKEN" filetype:env` | GitHub |  | GitHub GITHUB_TOKEN env-var in .env file. |
| ⚪ | `intext:"GITLAB_TOKEN" filetype:env` | GitLab |  | GitLab GITLAB_TOKEN env-var in .env file. |
| ⚪ | `intext:"AIzaSy" "generativelanguage" -site:github.com` | Google/Gemini |  | Google/Gemini AIzaSy co-anchored with generativelanguage (prefix too broad alone). |
| ⚪ | `intext:"GOOGLE_API_KEY" filetype:env` | Google/Gemini |  | Google/Gemini GOOGLE_API_KEY env-var in .env file. |
| ⚪ | `intext:"gsk_" "GROQ_API_KEY" -site:github.com` | Groq |  | Groq gsk_ co-anchored with GROQ_API_KEY (prefix too broad alone). |
| ⚪ | `intext:"GROQ_API_KEY" filetype:env` | Groq |  | Groq GROQ_API_KEY env-var in .env file. |
| ⚪ | `intext:"hf_" "HF_TOKEN" -site:github.com` | HuggingFace |  | HuggingFace hf_ co-anchored with HF_TOKEN (prefix too broad alone). |
| ⚪ | `intext:"HF_TOKEN" filetype:env` | HuggingFace |  | HuggingFace HF_TOKEN env-var in .env file. |
| ⚪ | `intext:"LANGSMITH_API_KEY" filetype:env` | LangSmith |  | LangSmith LANGSMITH_API_KEY env-var in .env file. |
| ⚪ | `intext:"LANGFUSE_SECRET_KEY" filetype:env` | Langfuse |  | Langfuse LANGFUSE_SECRET_KEY env-var in .env file. |
| ⚪ | `intext:"LANGFUSE_PUBLIC_KEY" filetype:env` | Langfuse |  | Langfuse LANGFUSE_PUBLIC_KEY env-var in .env file. |
| ⚪ | `intext:"NEXTAUTH_SECRET" "langfuse" -site:github.com` | Langfuse |  | Langfuse NEXTAUTH_SECRET co-anchored with langfuse (prefix too broad alone). |
| ⚪ | `intext:"ENCRYPTION_KEY" "langfuse" -site:github.com` | Langfuse |  | Langfuse ENCRYPTION_KEY co-anchored with langfuse (prefix too broad alone). |
| ⚪ | `intext:"sk-proj-" "openai" -site:github.com` | OpenAI |  | OpenAI sk-proj- co-anchored with openai (prefix too broad alone). |
| ⚪ | `intext:"OPENAI_API_KEY" filetype:env` | OpenAI |  | OpenAI OPENAI_API_KEY env-var in .env file. |
| ⚪ | `intext:"sk-svcacct-" "openai" -site:github.com` | OpenAI |  | OpenAI sk-svcacct- co-anchored with openai (prefix too broad alone). |
| ⚪ | `intext:"phc_" "posthog" -site:github.com` | PostHog |  | PostHog phc_ co-anchored with posthog (prefix too broad alone). |
| ⚪ | `intext:"POSTHOG_API_KEY" filetype:env` | PostHog |  | PostHog POSTHOG_API_KEY env-var in .env file. |
| ⚪ | `intext:"SG." "SENDGRID_API_KEY" -site:github.com` | SendGrid |  | SendGrid SG. co-anchored with SENDGRID_API_KEY (prefix too broad alone). |
| ⚪ | `intext:"SENDGRID_API_KEY" filetype:env` | SendGrid |  | SendGrid SENDGRID_API_KEY env-var in .env file. |

## Files Containing Passwords
_75 dorks_

| T | Dork | Service | CVE | Notes |
|---|------|---------|-----|-------|
| 🟡 | `intitle:"index of" ".aws" intext:"credentials"` | AWS |  | AWS credentials file (Bedrock/SageMaker access) in open dir. |
| 🟡 | `intext:"sk-ant-api03-" -site:github.com` | Anthropic |  | Anthropic ANTHROPIC_API_KEY (sk-ant-api03-) in page body. Vendor-unique prefix. |
| 🟡 | `intext:"sk-ant-api03-" filetype:env` | Anthropic |  | Anthropic sk-ant-api03- in .env file. |
| 🟡 | `filetype:json intext:"ANTHROPIC_API_KEY" -site:github.com` | Anthropic config |  | JSON config leaking Anthropic key (Next.js manifest, deploy config). |
| 🟡 | `inurl:"airflow.cfg" intext:"sql_alchemy_conn"` | Apache Airflow |  | Airflow config: sql_alchemy_conn embeds DB password; fernet_key nearby. |
| 🟡 | `filetype:cfg intext:"fernet_key" intext:"airflow"` | Apache Airflow |  | Airflow Fernet key. Decrypts all stored connection passwords + Variables. |
| 🟡 | `inurl:"superset_config.py" intext:"SECRET_KEY"` | Apache Superset |  | Superset SECRET_KEY (CVE-2023-27524 class). Session forge to admin. |
| 🟡 | `intext:"bt_v1_" -site:github.com` | Braintrust |  | Braintrust key/token (bt_v1_) in page body. Vendor-unique prefix. |
| 🟡 | `intext:"bt_v1_" filetype:env` | Braintrust |  | Braintrust bt_v1_ in .env file. |
| 🟡 | `intext:".claude/settings.json" -site:github.com` | Claude Code |  | Claude Code key/token (.claude/settings.json) in page body. Vendor-unique prefix. |
| 🟡 | `intext:".claude/settings.json" filetype:env` | Claude Code |  | Claude Code .claude/settings.json in .env file. |
| 🟡 | `intext:"COHERE_API_KEY" -site:github.com` | Cohere |  | Cohere COHERE_API_KEY (COHERE_API_KEY) in page body. Vendor-unique prefix. |
| 🟡 | `intext:"COHERE_API_KEY" filetype:env` | Cohere |  | Cohere COHERE_API_KEY in .env file. |
| 🟡 | `intext:"DEEPSEEK_API_KEY" -site:github.com` | DeepSeek |  | DeepSeek DEEPSEEK_API_KEY (DEEPSEEK_API_KEY) in page body. Vendor-unique prefix. |
| 🟡 | `intext:"DEEPSEEK_API_KEY" filetype:env` | DeepSeek |  | DeepSeek DEEPSEEK_API_KEY in .env file. |
| 🟡 | `filetype:json intext:"service_account" intext:"private_key" intext:"vertex"` | GCP Vertex |  | GCP service-account JSON for Vertex AI. |
| 🟡 | `intext:"ghp_" -site:github.com` | GitHub |  | GitHub GITHUB_TOKEN (ghp_) in page body. Vendor-unique prefix. |
| 🟡 | `intext:"ghp_" filetype:env` | GitHub |  | GitHub ghp_ in .env file. |
| 🟡 | `intext:"gho_" -site:github.com` | GitHub |  | GitHub key/token (gho_) in page body. Vendor-unique prefix. |
| 🟡 | `intext:"gho_" filetype:env` | GitHub |  | GitHub gho_ in .env file. |
| 🟡 | `intext:"ghs_" -site:github.com` | GitHub |  | GitHub key/token (ghs_) in page body. Vendor-unique prefix. |
| 🟡 | `intext:"ghs_" filetype:env` | GitHub |  | GitHub ghs_ in .env file. |
| 🟡 | `intext:"glpat-" -site:github.com` | GitLab |  | GitLab GITLAB_TOKEN (glpat-) in page body. Vendor-unique prefix. |
| 🟡 | `intext:"glpat-" filetype:env` | GitLab |  | GitLab glpat- in .env file. |
| 🟡 | `intext:"sk-helicone-" -site:github.com` | Helicone |  | Helicone key/token (sk-helicone-) in page body. Vendor-unique prefix. |
| 🟡 | `intext:"sk-helicone-" filetype:env` | Helicone |  | Helicone sk-helicone- in .env file. |
| 🟡 | `filetype:env intext:"HF_TOKEN" -site:github.com -intext:"hf_xxxx"` | HuggingFace |  | HuggingFace token in .env. Model/dataset/Space write. |
| 🟡 | `intext:"hl_pk_" -site:github.com` | Humanloop |  | Humanloop key/token (hl_pk_) in page body. Vendor-unique prefix. |
| 🟡 | `intext:"hl_pk_" filetype:env` | Humanloop |  | Humanloop hl_pk_ in .env file. |
| 🟡 | `inurl:"jupyter_server_config.json" intext:"password"` | Jupyter |  | Jupyter server config with hashed/plain password or token. |
| 🟡 | `intext:"LAGO_RSA_PRIVATE_KEY" -site:github.com` | Lago |  | Lago LAGO_RSA_PRIVATE_KEY (LAGO_RSA_PRIVATE_KEY) in page body. Vendor-unique prefix. |
| 🟡 | `intext:"LAGO_RSA_PRIVATE_KEY" filetype:env` | Lago |  | Lago LAGO_RSA_PRIVATE_KEY in .env file. |
| 🟡 | `intext:"lsv2_pt_" -site:github.com` | LangSmith |  | LangSmith LANGSMITH_API_KEY (lsv2_pt_) in page body. Vendor-unique prefix. |
| 🟡 | `intext:"lsv2_pt_" filetype:env` | LangSmith |  | LangSmith lsv2_pt_ in .env file. |
| 🟡 | `intext:"lsv2_sk_" -site:github.com` | LangSmith |  | LangSmith LANGSMITH_API_KEY (lsv2_sk_) in page body. Vendor-unique prefix. |
| 🟡 | `intext:"lsv2_sk_" filetype:env` | LangSmith |  | LangSmith lsv2_sk_ in .env file. |
| 🟡 | `intext:"sk-lf-" -site:github.com` | Langfuse |  | Langfuse LANGFUSE_SECRET_KEY (sk-lf-) in page body. Vendor-unique prefix. |
| 🟡 | `intext:"sk-lf-" filetype:env` | Langfuse |  | Langfuse sk-lf- in .env file. |
| 🟡 | `intext:"pk-lf-" -site:github.com` | Langfuse |  | Langfuse LANGFUSE_PUBLIC_KEY (pk-lf-) in page body. Vendor-unique prefix. |
| 🟡 | `intext:"pk-lf-" filetype:env` | Langfuse |  | Langfuse pk-lf- in .env file. |
| 🟡 | `filetype:env intext:"LANGFUSE_SECRET_KEY" intext:"sk-lf-"` | Langfuse |  | Langfuse secret key in .env, prefix-confirmed. |
| 🟡 | `intitle:"index of" "litellm_config.yaml" intext:"api_key"` | LiteLLM |  | LiteLLM proxy config in open dir, provider keys in model_list. |
| 🟡 | `filetype:yaml intext:"api_key" intext:"openai" -sample -example` | LiteLLM/app yaml |  | YAML config (LiteLLM/app) with inline OpenAI api_key. |
| 🟡 | `intext:"MISTRAL_API_KEY" -site:github.com` | Mistral |  | Mistral MISTRAL_API_KEY (MISTRAL_API_KEY) in page body. Vendor-unique prefix. |
| 🟡 | `intext:"MISTRAL_API_KEY" filetype:env` | Mistral |  | Mistral MISTRAL_API_KEY in .env file. |
| 🟡 | `intext:"OPENAI_API_KEY=sk-" -site:github.com` | OpenAI |  | OpenAI OPENAI_API_KEY (OPENAI_API_KEY=sk-) in page body. Vendor-unique prefix. |
| 🟡 | `intext:"OPENAI_API_KEY=sk-" filetype:env` | OpenAI |  | OpenAI OPENAI_API_KEY=sk- in .env file. |
| 🟡 | `filetype:env intext:"OPENAI_API_KEY" -site:github.com -intext:"your-key"` | OpenAI .env |  | Live .env leaking OpenAI key. Strip placeholder values. |
| 🟡 | `filetype:sh intext:"export OPENAI_API_KEY=sk-"` | OpenAI shell |  | Shell script exporting a live OpenAI key. |
| 🟡 | `intext:"sk-or-v1-" -site:github.com` | OpenRouter |  | OpenRouter key/token (sk-or-v1-) in page body. Vendor-unique prefix. |
| 🟡 | `intext:"sk-or-v1-" filetype:env` | OpenRouter |  | OpenRouter sk-or-v1- in .env file. |
| 🟡 | `intext:"xoxb-" -site:github.com` | Slack |  | Slack key/token (xoxb-) in page body. Vendor-unique prefix. |
| 🟡 | `intext:"xoxb-" filetype:env` | Slack |  | Slack xoxb- in .env file. |
| 🟡 | `intext:"xapp-" -site:github.com` | Slack |  | Slack key/token (xapp-) in page body. Vendor-unique prefix. |
| 🟡 | `intext:"xapp-" filetype:env` | Slack |  | Slack xapp- in .env file. |
| 🟡 | `filetype:toml intext:"openai" intext:"api_key" -example -template` | Streamlit secrets |  | Streamlit secrets.toml or pyproject with inline OpenAI key. |
| 🟡 | `intext:"pk_live_" -site:github.com` | Stripe |  | Stripe key/token (pk_live_) in page body. Vendor-unique prefix. |
| 🟡 | `intext:"pk_live_" filetype:env` | Stripe |  | Stripe pk_live_ in .env file. |
| 🟡 | `intext:"sk_live_" -site:github.com` | Stripe |  | Stripe key/token (sk_live_) in page body. Vendor-unique prefix. |
| 🟡 | `intext:"sk_live_" filetype:env` | Stripe |  | Stripe sk_live_ in .env file. |
| 🟡 | `filetype:log intext:"Bearer sk-" -site:github.com` | key-in-logs |  | Log file capturing Authorization: Bearer sk- key. |
| 🟡 | `filetype:env "OPENAI_API_KEY" "ANTHROPIC_API_KEY" "GROQ_API_KEY"` | multi-provider |  | Multi-provider .env dump. Three keys, one file. |
| 🟡 | `inurl:".n8n" intext:"encryptionKey"` | n8n |  | n8n encryptionKey. Decrypts all stored workflow credentials. |
| 🟡 | `intitle:"index of" ".env.production" intext:"KEY"` | prod .env |  | Production .env in an open dir. |
| ⚪ | `filetype:py intext:"SQLALCHEMY_DATABASE_URI" intext:"superset"` | Apache Superset |  | Superset DB URI with embedded credentials. |
| ⚪ | `filetype:env intext:"DEEPSEEK_API_KEY"` | DeepSeek |  | DeepSeek API key in .env. |
| ⚪ | `filetype:env intext:"GROQ_API_KEY"` | Groq |  | Groq API key in .env. |
| ⚪ | `inurl:"config.yaml" intext:"huggingfacehub_api_token"` | LangChain |  | LangChain/LlamaIndex config with HF hub token. |
| ⚪ | `intitle:"index of" "basic_auth.ini" intext:"mlflow"` | MLflow |  | MLflow basic-auth store. Username:bcrypt pairs for the tracking server. |
| ⚪ | `filetype:env intext:"PINECONE_API_KEY"` | Pinecone |  | Pinecone API key in .env. |
| ⚪ | `filetype:env intext:"QDRANT_API_KEY" -site:github.com` | Qdrant |  | Qdrant API key in .env. |
| ⚪ | `inurl:"redis.conf" intext:"requirepass"` | Redis |  | Redis (vector/cache layer) password in config. |
| ⚪ | `filetype:env intext:"WEAVIATE_API_KEY"` | Weaviate |  | Weaviate API key in .env. |
| ⚪ | `filetype:log intext:"api_key" intext:"openai" -site:github.com` | key-in-logs |  | App log leaking openai api_key value. |
| ⚪ | `filetype:env intext:"DATABASE_URL" intext:"postgres" intext:"vector"` | pgvector |  | pgvector Postgres URL with embedded password. |

## Various Online Devices
_38 dorks_

| T | Dork | Service | CVE | Notes |
|---|------|---------|-----|-------|
| 🟡 | `intitle:"CodeProject.AI Server"` | CodeProject.AI |  | CodeProject.AI edge inference server (port 32168). Repo: 39 confirmed. Open detection API. |
| 🟡 | `intitle:"Frigate" inurl:cameras` | Frigate NVR |  | Frigate NVR (AI object detection). Repo: 205 found, 15 leak RTSP camera creds in plaintext via /api/config. |
| 🟡 | `intext:"frigate" "rtsp://" inurl:config` | Frigate NVR |  | Frigate config exposing rtsp:// URLs with embedded camera credentials. |
| 🟡 | `intext:"GPT-SoVITS" inurl:api -site:github.com` | GPT-SoVITS | CVE-2025-49833 | GPT-SoVITS open inference/device endpoint. no auth by default; command injection RCE |
| 🟡 | `intext:"DCGM_FI_DEV_GPU_TEMP"` | NVIDIA DCGM |  | NVIDIA DCGM exporter /metrics. GPU temp/util/process names, no auth. |
| 🟡 | `intitle:"index of" "dustynv" intext:"l4t"` | NVIDIA Jetson |  | NVIDIA Jetson container catalog (dustynv/l4t images). Edge-AI operator attribution. |
| 🟡 | `intext:"RVC" inurl:api -site:github.com` | RVC (Retrieval-based Voice Conversion) | CVE-2025-43842 | RVC (Retrieval-based Voice Conversion) open inference/device endpoint. no auth by default; RCE via pickle deserialization |
| ⚪ | `intext:"Applio" inurl:api -site:github.com` | Applio |  | Applio open inference/device endpoint. no auth by default |
| ⚪ | `intext:"Bark" inurl:api -site:github.com` | Bark TTS |  | Bark TTS open inference/device endpoint. no auth by default |
| ⚪ | `intext:"ChatTTS" inurl:api -site:github.com` | ChatTTS |  | ChatTTS open inference/device endpoint. no auth by default |
| ⚪ | `intext:"Chatterbox TTS" inurl:api -site:github.com` | Chatterbox TTS |  | Chatterbox TTS open inference/device endpoint. no auth; /upload_reference unauth on both variants |
| ⚪ | `inurl:"vision/detection" intext:"CodeProject"` | CodeProject.AI |  | CodeProject.AI detection endpoint. |
| ⚪ | `intext:"Coqui" inurl:api -site:github.com` | Coqui TTS |  | Coqui TTS open inference/device endpoint. no auth by default |
| ⚪ | `intext:"Coral" intext:"edgetpu" inurl:detect` | Coral EdgeTPU |  | Google Coral EdgeTPU detection endpoint. |
| ⚪ | `intitle:"DeepStack" inurl:admin` | DeepStack |  | DeepStack AI server admin (port 5000). Repo: 24 confirmed. |
| ⚪ | `intitle:"ESP32-CAM" -com -net` | ESP32-CAM |  | ESP32-CAM (often paired with edge AI detection). |
| ⚪ | `intitle:"GPUStack"` | GPUStack |  | GPUStack cluster dashboard. GPU inventory + model scheduling. |
| ⚪ | `intitle:"Home Assistant" intext:"Ollama"` | Home Assistant |  | Home Assistant with Ollama integration. Local LLM wired to home automation. |
| ⚪ | `intext:"Kokoro" inurl:api -site:github.com` | Kokoro TTS / Kokoro-FastAPI |  | Kokoro TTS / Kokoro-FastAPI open inference/device endpoint. no auth by default |
| ⚪ | `intitle:"LM Studio" intext:"server" inurl:1234` | LM Studio |  | LM Studio local server mode on a workstation. |
| ⚪ | `intext:"LiveKit" inurl:api -site:github.com` | LiveKit Agents |  | LiveKit Agents open inference/device endpoint. JWT required for room ops; health endpoint open |
| ⚪ | `intext:"jetson" intext:"nvpmodel" -com -net` | NVIDIA Jetson |  | Jetson board management surface (power-model config). |
| ⚪ | `intitle:"NVIDIA Triton" inurl:"v2/health"` | NVIDIA Triton |  | Triton inference server on an edge/appliance box. |
| ⚪ | `intext:"OpenVINO Model Server" inurl:"v1/config"` | OpenVINO |  | Intel OpenVINO model server config endpoint. Edge inference. |
| ⚪ | `intext:"OpenVoice" inurl:api -site:github.com` | OpenVoice |  | OpenVoice open inference/device endpoint. no auth by default |
| ⚪ | `intext:"Orpheus TTS" inurl:api -site:github.com` | Orpheus-FastAPI TTS |  | Orpheus-FastAPI TTS open inference/device endpoint. no auth by default |
| ⚪ | `intext:"Orthanc Explorer" inurl:api -site:github.com` | Orthanc DICOM Server |  | Orthanc DICOM Server open inference/device endpoint. no auth by default; PHI exposure |
| ⚪ | `intext:"Pipecat" inurl:api -site:github.com` | Pipecat |  | Pipecat open inference/device endpoint. no auth by default |
| ⚪ | `intext:"Piper" inurl:api -site:github.com` | Piper TTS |  | Piper TTS open inference/device endpoint. no auth by default |
| ⚪ | `intitle:"Rhasspy"` | Rhasspy |  | Rhasspy offline voice assistant. Intent config + audio device control. |
| ⚪ | `intext:"SpeechBrain" inurl:api -site:github.com` | SpeechBrain |  | SpeechBrain open inference/device endpoint. no auth on self-hosted wrappers |
| ⚪ | `intext:"Tortoise" inurl:api -site:github.com` | Tortoise TTS |  | Tortoise TTS open inference/device endpoint. no auth by default |
| ⚪ | `intitle:"Viam" inurl:robot` | Viam |  | Viam robotics control surface. |
| ⚪ | `intext:"Whisper" inurl:api -site:github.com` | Whisper ASR |  | Whisper ASR open inference/device endpoint. no auth by default |
| ⚪ | `intext:"wyoming" intext:"piper" -com -net` | Wyoming/Piper |  | Wyoming-protocol voice satellite (Piper TTS). Home voice device. |
| ⚪ | `intext:"dcm4chee Archive UI" inurl:api -site:github.com` | dcm4chee Archive |  | dcm4chee Archive open inference/device endpoint. Keycloak-fronted; auth state may be misconfigured |
| ⚪ | `intitle:"motionEye"` | motionEye |  | motionEye surveillance (AI motion). Repo: 18 confirmed. Camera feeds + config. |
| ⚪ | `intext:"SoftVC" inurl:api -site:github.com` | so-vits-svc |  | so-vits-svc open inference/device endpoint. no auth by default |

## Advisories and Vulnerabilities
_35 dorks_

| T | Dork | Service | CVE | Notes |
|---|------|---------|-----|-------|
| 🟡 | `inurl:"/api/auth/signup" -site:github.com` | Agenta |  | Agenta auth-bypass route: HTTP 200 + FIELD_ERROR = signup live. No disable toggle in OSS. Any party registers. |
| 🟡 | `inurl:"/api/v1/dags" -site:github.com` | Airflow | CVE-2020-13927 | Airflow: DAG list. /home bypass: anon role returns authenticated dashboard. |
| 🟡 | `inurl:"/api/v1/dags" intext:"Airflow"` | Airflow | CVE-2020-13927 | Airflow endpoint co-anchored on 'Airflow'. DAG list. /home bypass: anon role returns authenticated dashboard. |
| 🟡 | `inurl:"/if/flow/initial-setup/" -site:github.com` | Authentik | CVE-2024-47070 | Authentik auth-bypass route: Setup-flow-open on fresh instances. Claimable admin. |
| 🟡 | `inurl:"/api/answer" -site:github.com` | DocsGPT | CVE-2025-0868 | DocsGPT: RAG answer endpoint. CVE-2025-0868. |
| 🟡 | `inurl:"/api/answer" intext:"DocsGPT"` | DocsGPT | CVE-2025-0868 | DocsGPT endpoint co-anchored on 'DocsGPT'. RAG answer endpoint. CVE-2025-0868. |
| 🟡 | `inurl:"/api/v1/chatflows" -site:github.com` | Flowise | CVE-2024-36420 | Flowise: Chatflow list. Pre-1.8.2 auth bypass via path traversal. |
| 🟡 | `inurl:"/api/v1/chatflows" intext:"Flowise"` | Flowise | CVE-2024-36420 | Flowise endpoint co-anchored on 'Flowise'. Chatflow list. Pre-1.8.2 auth bypass via path traversal. |
| 🟡 | `inurl:"/public/plugins/" -site:github.com` | Grafana | CVE-2021-43798 | Grafana: CVE-2021-43798 path traversal reads arbitrary files via plugin path. |
| 🟡 | `inurl:"/public/plugins/" intext:"Grafana"` | Grafana | CVE-2021-43798 | Grafana endpoint co-anchored on 'Grafana'. CVE-2021-43798 path traversal reads arbitrary files via plugin path. |
| 🟡 | `intext:"deepseek-v4-pro" intext:"ollama" -site:github.com` | Honeypot Canary |  | Fabricated model name (deepseek-v4-pro does not exist). Hits = deception fleet / proxy-shim, not real deployments. |
| 🟡 | `intext:"gemini-3-flash" intext:"ollama" -site:github.com` | Honeypot Canary |  | Fabricated model name (gemini-3-flash does not exist). Hits = deception fleet / proxy-shim, not real deployments. |
| 🟡 | `intext:"minimax-m2.7" intext:"ollama" -site:github.com` | Honeypot Canary |  | Fabricated model name (minimax-m2.7 does not exist). Hits = deception fleet / proxy-shim, not real deployments. |
| 🟡 | `intext:"kimi-k2.6" intext:"ollama" -site:github.com` | Honeypot Canary |  | Fabricated model name (kimi-k2.6 does not exist). Hits = deception fleet / proxy-shim, not real deployments. |
| 🟡 | `intext:"gemma4" intext:"ollama" -site:github.com` | Honeypot Canary |  | Fabricated model name (gemma4 does not exist). Hits = deception fleet / proxy-shim, not real deployments. |
| 🟡 | `intext:"qwen3-coder-next" intext:"ollama" -site:github.com` | Honeypot Canary |  | Fabricated model name (qwen3-coder-next does not exist). Hits = deception fleet / proxy-shim, not real deployments. |
| 🟡 | `intext:"glm-4.7-flash" intext:"ollama" -site:github.com` | Honeypot Canary |  | Fabricated model name (glm-4.7-flash does not exist). Hits = deception fleet / proxy-shim, not real deployments. |
| 🟡 | `inurl:"/api/2.0/mlflow/experiments/list" -site:github.com` | MLflow | CVE-2023-1177 | MLflow: Experiment list. CVE-2023-1177 path traversal via artifact download. |
| 🟡 | `inurl:"/api/2.0/mlflow/experiments/list" intext:"MLflow"` | MLflow | CVE-2023-1177 | MLflow endpoint co-anchored on 'MLflow'. Experiment list. CVE-2023-1177 path traversal via artifact download. |
| 🟡 | `inurl:"/api/session/properties" -site:github.com` | Metabase | CVE-2023-38646 | Metabase: Returns setup-token. GET then POST /api/setup = full admin. |
| 🟡 | `inurl:"/api/session/properties" intext:"Metabase"` | Metabase | CVE-2023-38646 | Metabase endpoint co-anchored on 'Metabase'. Returns setup-token. GET then POST /api/setup = full admin. |
| 🟡 | `inurl:"/api/tags" -site:github.com` | Ollama | CVE-2024-37032 | Ollama: Model list. No auth. Reveals abliterated/jailbroken variants. |
| 🟡 | `inurl:"/api/tags" intext:"Ollama"` | Ollama | CVE-2024-37032 | Ollama endpoint co-anchored on 'Ollama'. Model list. No auth. Reveals abliterated/jailbroken variants. |
| 🟡 | `inurl:"/api/v1/datasets" -site:github.com` | RAGFlow | CVE-2024-12880 | RAGFlow: Knowledge base list. CVE-2024-12880. |
| 🟡 | `inurl:"/api/v1/datasets" intext:"RAGFlow"` | RAGFlow | CVE-2024-12880 | RAGFlow endpoint co-anchored on 'RAGFlow'. Knowledge base list. CVE-2024-12880. |
| 🟡 | `inurl:"/api/jobs" -site:github.com` | Ray | CVE-2023-48022 | Ray: Job submission API. CVE-2023-48022 ShadowRay unauth RCE. |
| 🟡 | `inurl:"/api/jobs" intext:"Ray"` | Ray | CVE-2023-48022 | Ray endpoint co-anchored on 'Ray'. Job submission API. CVE-2023-48022 ShadowRay unauth RCE. |
| 🟡 | `inurl:"/api/databases" -site:github.com` | RedisInsight |  | RedisInsight auth-bypass route: Returns Redis connection configs with password field in plaintext. 26% leak AUTH creds. |
| 🟡 | `inurl:"/api/v1/database" -site:github.com` | Superset | CVE-2023-27524 | Superset: DB connection list. CVE-2023-27524 default SECRET_KEY = session forge. |
| 🟡 | `inurl:"/api/v1/database" intext:"Superset"` | Superset | CVE-2023-27524 | Superset endpoint co-anchored on 'Superset'. DB connection list. CVE-2023-27524 default SECRET_KEY = session forge. |
| 🟡 | `inurl:"/models" -site:github.com` | TorchServe | CVE-2023-43654 | TorchServe: Management API (port 8081). Model registration + nextPageToken. |
| 🟡 | `inurl:"/models" intext:"TorchServe"` | TorchServe | CVE-2023-43654 | TorchServe endpoint co-anchored on 'TorchServe'. Management API (port 8081). Model registration + nextPageToken. |
| 🟡 | `inurl:"/v2/health/ready" -site:github.com` | Triton | CVE-2024-0087 | Triton: Triton health. /v2/models for model inventory. |
| 🟡 | `inurl:"/v2/health/ready" intext:"Triton"` | Triton | CVE-2024-0087 | Triton endpoint co-anchored on 'Triton'. Triton health. /v2/models for model inventory. |
| 🟡 | `inurl:"/rest/workflows" -site:github.com` | n8n |  | n8n auth-bypass route: Legacy internal API returns workflow data without creds even when public API disabled. |
