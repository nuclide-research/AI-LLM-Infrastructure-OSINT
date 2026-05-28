# Shodan Query Results Log

Every executed dork is logged here — zero hits are results, not skips.

| Date | Query | Total Hits | Survey | Notes |
| 2026-05-28 | `http.title:"LangSmith"` | 77 | ai-eval-redteam | 3 pages scraped; LangChain official infra dominates; self-hosted at qvine.com + swoop.com; all auth-enforced (401) |
| 2026-05-28 | `http.title:"LangSmith" port:1980` | 0 | ai-eval-redteam | LangSmith nginx frontend port not indexed separately |
| 2026-05-28 | `http.title:"LangSmith" port:1984` | 0 | ai-eval-redteam | Backend API port not indexed with title filter |
| 2026-05-28 | `http.title:"LangSmith" port:443` | 30 | ai-eval-redteam | Subset of main 77; all auth-enforced |
| 2026-05-28 | `ssl.cert.subject.cn:langsmith` | 67 | ai-eval-redteam | TLS CN sweep; mix of langchain.com and third-party operators; all auth-enforced on sampled hosts |
| 2026-05-28 | `http.title:"promptfoo"` | 17 | ai-eval-redteam | 2 pages scraped; 4 confirmed unauth via /api/user/email probe |
| 2026-05-28 | `http.title:promptfoo port:3000` | 6 | ai-eval-redteam | Port-scoped variant; overlapping with main 17 |
| 2026-05-28 | `ssl.cert.subject.cn:promptfoo` | 25 | ai-eval-redteam | TLS CN sweep; additional operator candidates |
| 2026-05-28 | `http.title:"TruLens"` | 1 | ai-eval-redteam | Single hit: trulens.asia = Cambodian news bias site (FP); 0 genuine TruLens |
| 2026-05-28 | `ssl.cert.subject.cn:trulens` | 1 | ai-eval-redteam | vits-simple-api TTS tool (FP); 0 genuine TruLens |
| 2026-05-28 | `http.title:"Inspect" port:7575` | 0 | ai-eval-redteam | 0 Inspect AI instances on default port |
| 2026-05-28 | `http.title:"inspect ai"` | 6 | ai-eval-redteam | All hits: SPIP CMS honeypots on Alibaba cloud (FPs) |
| 2026-05-28 | `http.title:"HELM" port:8000` | 2 | ai-eval-redteam | Both hits: Coolify container platform (Kubernetes Helm) — FPs |
| 2026-05-28 | `http.title:"deepeval"` | 0 | ai-eval-redteam | 0 results |
| 2026-05-28 | `http.title:"PyRIT"` | 0 | ai-eval-redteam | 0 results |
| 2026-05-28 | `http.title:"RAGAS"` | 4 | ai-eval-redteam | All hits: ragas.app SaaS cloud (auth-gated); 0 self-hosted |
| 2026-05-28 | `http.title:"garak"` | 4 | ai-eval-redteam | All hits: Chatterbox TTS and unrelated apps (FPs); 0 genuine Garak |
| 2026-05-28 | `http.title:"Patronus"` | 3 | ai-eval-redteam | Polish hospital login and AWS LBs (FPs); 0 Patronus AI |
| 2026-05-28 | `http.title:"Arthur Shield"` | 13 | ai-eval-redteam | Cloudflare challenge blocked scrape; FP rate expected high given "arthur" ambiguity |
| 2026-05-28 | `port:7851 http.json:"engines_available"` | 0 | voice-audio-ai | AllTalk API port not indexed; Shodan-dark |
| 2026-05-28 | `"openai-whisper-asr-webservice" port:9000` | 0 | voice-audio-ai | Docker banner not indexed at this specificity |
| 2026-05-28 | `port:7865 http.html:"Retrieval-based-Voice-Conversion"` | 0 | voice-audio-ai | RVC WebUI Shodan-dark on canonical port |
| 2026-05-28 | `port:8880 http.html:"Kokoro"` | 3 | voice-audio-ai | 3 confirmed Kokoro-FastAPI: Hetzner US/FI, CHINANET-JS CN |
| 2026-05-28 | `port:5002 http.html:"api/tts"` | 6 | voice-audio-ai | 6 Coqui TTS: CN/BR/UAE/CA/FR/FI; Werkzeug/3.x stack |
| 2026-05-28 | `port:9090 "WhisperLive"` | 0 | voice-audio-ai | WhisperLive WebSocket not indexed |
| 2026-05-28 | `port:8020 http.html:"tts_to_audio"` | 0 | voice-audio-ai | XTTS-api-server Shodan-dark |
| 2026-05-28 | `http.headers:"X-LiveKit-Server" port:7880` | 0 | voice-audio-ai | LiveKit header not indexed |
| 2026-05-28 | `port:7880 "livekit"` | 0 | voice-audio-ai | LiveKit port not crawled |
| 2026-05-28 | `port:8080 http.html:"system_health" http.html:"active_batch_requests"` | 0 | voice-audio-ai | Deepgram on-prem not found |
| 2026-05-28 | `port:8899 http.html:"Orpheus"` | 0 | voice-audio-ai | Orpheus-FastAPI Shodan-dark |
| 2026-05-28 | `http.html:"/v1/audio/speech" -openai` | 12 | voice-audio-ai | OpenAI-compat TTS sweep: 12 uvicorn servers |
| 2026-05-28 | `http.html:"vits-simple-api"` | 4 | voice-audio-ai | 4 vits-simple-api CHINANET-ZJ cluster; same as GPT-SoVITS harvest |
| 2026-05-28 | `port:8800 "GPT-SoVITS"` | 0 | voice-audio-ai | GPT-SoVITS :8800 Shodan-dark |
| 2026-05-28 | `"whisper.cpp" port:8080` | 16 | voice-audio-ai | 16 whisper.cpp: Server header; US/DE/RU/BR/CN/CY/NL; Internet Archive host |
| 2026-05-28 | `port:8000 http.html:"chatterbox"` | 4 | voice-audio-ai | 1 confirmed Chatterbox TTS (DE/Hetzner), 1 WPVoicer FP, 2 generic uvicorn |
| 2026-05-28 | `http.title:"Fish Speech"` | 0 | voice-audio-ai | Fish Speech Shodan-dark |
| 2026-05-28 | `port:5000 http.json:"bark-inference"` | 0 | voice-audio-ai | Bark FastAPI not indexed |
| 2026-05-28 | `http.html:"tortoise-tts" port:7860` | 0 | voice-audio-ai | 4 results all FP (Spanish music sites "ragas") |
| 2026-05-28 | `http.html:"pipecat-ai"` | 3 | voice-audio-ai | 1 confirmed Pipecat (voice.rinqly.ai FI/Hetzner), 2 FP |
| 2026-05-28 | `port:9880 http.html:"GPT-SoVITS"` | 0 | voice-audio-ai | GPT-SoVITS API port Shodan-dark |
| 2026-05-28 | `port:9872 http.html:"GPT-SoVITS"` | 2 | voice-audio-ai | 2 hits TW/CN — both offline at probe |
| 2026-05-28 | `http.html:"GPT-SoVITS"` | 23 | voice-audio-ai | Broad harvest: 23 total; CVE ports offline |
| 2026-05-28 | `http.html:"LLM Guard API"` | 8 | safety-guardrail | Primary LLM Guard signal; 2 live confirmed |
| 2026-05-28 | `port:8000 http.html:"llm-guard"` | 3 | safety-guardrail | Secondary LLM Guard; same 2 instances (overlap) |
| 2026-05-28 | `port:5000 http.html:"/settings" http.html:"scanner"` | 36 | safety-guardrail | Vigil probe — all FP (NAS/betting panels) |
| 2026-05-28 | `http.html:"vigil-llm"` | 0 | safety-guardrail | Vigil product name — not indexed |
| 2026-05-28 | `port:5000 http.html:"/analyze/prompt"` | 0 | safety-guardrail | Vigil scan endpoint path — not indexed |
| 2026-05-28 | `port:5000 http.html:"prompt_entropy"` | 0 | safety-guardrail | Vigil response field — not indexed |
| 2026-05-28 | `http.html:"/v1/rails/configs"` | 0 | safety-guardrail | NeMo Guardrails unique endpoint — not indexed |
| 2026-05-28 | `http.html:"nemoguardrails" port:8000` | 0 | safety-guardrail | NeMo package name — not indexed |
| 2026-05-28 | `http.html:"/v1/rails/generate"` | 0 | safety-guardrail | NeMo rails generate endpoint — not indexed |
| 2026-05-28 | `http.html:"laiyer/llm-guard"` | 0 | safety-guardrail | LLM Guard Docker image name — not indexed |
| 2026-05-28 | `port:3000 http.html:"rebuff.ai"` | 0 | safety-guardrail | Rebuff vendor domain — not indexed |
| 2026-05-28 | `port:3000 http.html:"/api/detect" http.html:"rebuff"` | 0 | safety-guardrail | Rebuff API endpoint — not indexed |
| 2026-05-28 | `port:8000 http.html:"guardrailsai.com"` | 0 | safety-guardrail | Guardrails AI vendor domain — not indexed |
| 2026-05-28 | `http.html:"hub.guardrailsai.com"` | 0 | safety-guardrail | Guardrails AI hub URL — not indexed |
| 2026-05-28 | `http.html:"Llama-Guard-3"` | 0 | safety-guardrail | LlamaGuard 3 model name — not indexed |
| 2026-05-28 | `http.html:"meta-llama/Llama-Guard" port:8000` | 0 | safety-guardrail | LlamaGuard HF path — not indexed |
| 2026-05-28 | `http.html:"ShieldLM" port:8000` | 0 | safety-guardrail | ShieldLM model name — not indexed |
| 2026-05-28 | `http.html:"Llama-Prompt-Guard" port:8000` | 0 | safety-guardrail | PromptGuard model name — not indexed |
| 2026-05-28 | `http.html:"LlamaFirewall"` | 0 | safety-guardrail | LlamaFirewall suite name — not indexed |
| 2026-05-28 | `port:8000 "owned_by":"vllm"` | 0 | model-serving | String too specific for Shodan body index |
| 2026-05-28 | `port:8000 "max_model_len" "vllm"` | 10 | model-serving | Primary vLLM harvest — all offline at probe time |
| 2026-05-28 | `port:8081 "nextPageToken" "models"` | 0 | model-serving | TorchServe mgmt port not crawled |
| 2026-05-28 | `port:8081 "modelName" "modelUrl" "minWorkers"` | 0 | model-serving | TorchServe mgmt port not crawled |
| 2026-05-28 | `port:8082 "ts_"` | 0 | model-serving | TorchServe metrics port not crawled |
| 2026-05-28 | `port:8501 "model_version_status" "AVAILABLE"` | 0 | model-serving | TF Serving response not indexed at this specificity |
| 2026-05-28 | `port:8265 "ray_version"` | 0 | model-serving | Ray /api/version not in Shodan body |
| 2026-05-28 | `port:8265 http.title:"Ray Dashboard"` | 1 | model-serving | 1 Ray Dashboard hit — offline at probe |
| 2026-05-28 | `port:5000 "registered_models" "mlflow"` | 0 | model-serving | Body field too specific |
| 2026-05-28 | `port:5000 http.title:"MLflow"` | 10 | model-serving | 10 MLflow confirmed live; experiments API open |
| 2026-05-28 | `port:8080 "model_id" "model_dtype"` | 0 | model-serving | TGI /info fields not in Shodan index |
| 2026-05-28 | `port:8080 "tokenization_workers" "max_total_tokens"` | 0 | model-serving | TGI secondary fields not indexed |
| 2026-05-28 | `port:8000 "/v2/health/ready"` | 0 | model-serving | Triton V2 health path not indexed |
| 2026-05-28 | `port:8002 "nv_inference_request_success"` | 0 | model-serving | Triton metrics port not crawled |
| 2026-05-28 | `port:3000 "Bento-Name"` | 0 | model-serving | BentoML header not in Shodan index |
| 2026-05-28 | `port:9000 "/api/v1.0/predictions"` | 20 | model-serving | Seldon path — all offline; 1 MinIO FP (94.72.112.137) |
| 2026-05-28 | `http.html:"ragflow" port:80` | 540 | rag-frameworks | Subset of title dork population |
| 2026-05-28 | `http.title:"RAGFlow"` | 1,902 | rag-frameworks | Primary RAGFlow population signal |
| 2026-05-28 | `port:9380 http.html:"ragflow"` | 0 | rag-frameworks | Internal port, not crawled by Shodan |
| 2026-05-28 | `http.html:"/api/v1/user/login" http.html:"ragflow"` | 0 | rag-frameworks | String not in Shodan index |
| 2026-05-28 | `http.title:"DocsGPT"` | 8 | rag-frameworks | Full global DocsGPT population |
| 2026-05-28 | `port:5001 http.html:"DocsGPT"` | 0 | rag-frameworks | Dead dork — port 5001 not crawled |
| 2026-05-28 | `port:5001 http.html:"docsgpt" http.html:"conversation"` | 0 | rag-frameworks | Dead dork |
| 2026-05-28 | `http.html:"DocsGPT" http.html:"uvicorn"` | 0 | rag-frameworks | Dead dork |
| 2026-05-28 | `port:5173 http.html:"docsgpt"` | 0 | rag-frameworks | Dead dork |
| 2026-05-28 | `port:8000 http.html:"ragapp" http.html:"/admin"` | 0 | rag-frameworks | Ragapp not indexed |
| 2026-05-28 | `port:8000 http.html:"RAGapp" http.html:"llamaindex"` | 0 | rag-frameworks | Ragapp not indexed |
| 2026-05-28 | `http.html:"/api/management/config"` | 0 | rag-frameworks | Ragapp config path not indexed |
| 2026-05-28 | `http.title:"Ragapp"` | 0 | rag-frameworks | Ragapp not indexed |
| 2026-05-28 | `port:9621 http.html:"LightRAG"` | 0 | rag-frameworks | Default LightRAG port not crawled |
| 2026-05-28 | `port:9621 http.html:"/query"` | 0 | rag-frameworks | Port 9621 not crawled |
| 2026-05-28 | `http.html:"LightRAG" port:8020` | 0 | rag-frameworks | Dead dork |
| 2026-05-28 | `http.html:"LightRAG" http.html:"/query"` | ~1 | rag-frameworks | Narrow but valid signal |
| 2026-05-28 | `http.html:"LightRAG" http.html:"swagger"` | 5 | rag-frameworks | Best LightRAG dork — Swagger UI indexed |
|------|-------|-----------|--------|-------|
| 2026-05-27 | `ssl.cert.subject.cn:"temporal"` | 961 | workflow-orchestration | Temporal Cloud customers, NOT self-hosted — wrong population |
| 2026-05-27 | `http.title:"Temporal" port:8233` | 0 | workflow-orchestration | dead dork |
| 2026-05-27 | `http.title:"Temporal" port:8080` | 4 | workflow-orchestration | all FP (email demo, TARDIS log, bot dashboard) |
| 2026-05-27 | `port:8233 http.html:"temporal"` | 0 | workflow-orchestration | dead dork |
| 2026-05-27 | `http.html:"supportedClients" "clusterName"` | 0 | workflow-orchestration | dead dork |
| 2026-05-27 | `http.html:"/api/v1/namespaces" "temporal"` | 0 | workflow-orchestration | dead dork |
| 2026-05-27 | `port:7233` | 425 | workflow-orchestration | broad gRPC port, unverified |
| 2026-05-27 | `http.title:"Cadence" port:8088` | 210 | workflow-orchestration | all FP — SaaS products named Cadence (AI social, EDA tools) |
| 2026-05-27 | `http.html:"cadence-web" port:8088` | 0 | workflow-orchestration | dead dork |
| 2026-05-27 | `port:7933 http.html:"cadence"` | 0 | workflow-orchestration | dead dork |
| 2026-05-27 | `http.html:"uber/cadence"` | 0 | workflow-orchestration | dead dork |
| 2026-05-27 | `port:8080 http.html:"netflix/conductor"` | 4 | workflow-orchestration | 4 confirmed: Aliyun CN, GCP US, Contabo DE, Beijing Volcano CN |
| 2026-05-27 | `http.title:"Argo Workflows" port:2746` | 0 | workflow-orchestration | dead dork — Shodan not indexing port 2746 titles |
| 2026-05-27 | `port:2746 http.title:"Argo"` | 0 | workflow-orchestration | dead dork — same reason |
| 2026-05-27 | `ssl.cert.issuer.cn:"Argo Workflows"` | 0 | workflow-orchestration | dead dork — Argo cert has no CN field, only Organization=ArgoProj |
| 2026-05-27 | `port:2746` | 418 | workflow-orchestration | broad port harvest — mostly banner-less; needs content filter |
| 2026-05-27 | `http.html:"assets/favicon/favicon-32x32.png" "noindex"` | 160 | workflow-orchestration | too broad — matches other SPAs; not Argo-specific |
| 2026-05-27 | `ssl:"ArgoProj" port:2746` | 0 | workflow-orchestration | dead — Shodan indexes cert but port 2746 HTTPS content not stored |
| 2026-05-27 | `http.html:"gitTreeState" port:2746` | 0 | workflow-orchestration | dead — API JSON not indexed by Shodan crawler on port 2746 |
| 2026-05-27 | `http.html:"gitTreeState" "gitCommit"` | 0 | workflow-orchestration | dead — API JSON not indexed on any port |
| 2026-05-27 | `ssl:"ArgoProj"` | **233** | workflow-orchestration | WORKING DORK — cert org field; US 81 / JP 50 / DE 33 / IE 26 / CN 20; AWS-heavy; 156 unique IPs harvested. FP class: ACM certs where domain contains "argoproj" as subdomain (e.g. webhook.events.dxsx-argoproj.inside.ai). True positives have self-signed cert Issuer O=ArgoProj; verify via /api/v1/userinfo. |
| 2026-05-27 | `port:2746 http.status:200` | 12 | workflow-orchestration | too broad — Hikvision cameras, Home Assistant, Ollama; not Argo-specific |
| 2026-05-27 | `ssl.cert.subject.org:"ArgoProj"` | 0 | workflow-orchestration | dead — field-specific query not indexed the same way as ssl:"ArgoProj" |
| 2026-05-27 | `ssl:"ArgoProj" port:8080` | 0 | workflow-orchestration | dead — ArgoProj cert instances are on port 443, not 8080 |
| 2026-05-27 | `http.html:"fa82dae05c4e68e1ec09"` | 0 | workflow-orchestration | dead — Shodan does not index Argo SPA HTML body content |
| 2026-05-27 | `port:2746 "X-Ratelimit-Limit"` | 0 | workflow-orchestration | dead — Shodan does not crawl port 2746 HTTP banners. Argo unauth instances (plain HTTP port 2746) are Shodan-dark. Requires direct scan. |
| 2026-05-27 | `http.title:"OpenMetadata" port:8585` | 55 | ml-governance | 30 IPs p1-p3; primary dork confirmed working |
| 2026-05-27 | `http.html:"open-metadata" port:8585` | 0 | ml-governance | dead dork |
| 2026-05-27 | `http.html:"openmetadata" port:8080` | 1 | ml-governance | k8s ingress variant; 1 extra IP |
| 2026-05-27 | `http.title:"DataHub" port:9002` | 25 | ml-governance | 25 IPs confirmed |
| 2026-05-27 | `http.html:"datahubproject" port:9002` | 0 | ml-governance | dead dork — title is the anchor |
| 2026-05-27 | `port:21000 http.title:"Atlas"` | 0 | ml-governance | Apache Atlas not internet-exposed at scale on :21000 |
| 2026-05-27 | `port:21000 http.html:"Apache Atlas"` | 0 | ml-governance | dead dork |
| 2026-05-27 | `http.html:"marquezproject" port:5000` | 0 | ml-governance | Marquez not internet-exposed at scale |
| 2026-05-27 | `http.html:"amundsen" port:5001` | 0 | ml-governance | Amundsen not internet-exposed at scale |
| 2026-05-27 | `http.html:"registered-models" port:5000` | 0 | ml-governance | MLflow registry string not distinctive enough |
| 2026-05-27 | `http.html:"/api/3/action" http.html:"ckan"` | 4 | ml-governance | 2 IPs (129.13.32.206/207), same /29 — likely one operator |
| 2026-05-27 | `port:8585 http.html:"openmetadata"` | 56 | ml-governance | 1 additional IP vs title dork (34.56.227.179); total 57 unique |
| 2026-05-28 | `ssl:"Argo Workflows"` | 214 | argo-workflows | NEW: hits cert CN "Argo Workflows" on commercial certs (Let's Encrypt/ACM) — separate population from ssl:"ArgoProj". 90 IPs harvested (pagination partial). Top operators: Home Depot, Apex Clearing, freed.ai, Waabi AI, BrightInsight, ZOZO Inc, AccelerateLearning (4 envs), INSHUR. Google LLC 93 hosts, AWS ~94. |
| 2026-05-28 | `ssl:"Argo Workflows" -ssl:"ArgoProj"` | 214 | argo-workflows | Zero overlap with ArgoProj cert-org population — entirely distinct deployment class (operator-domain certs vs self-signed) |
| 2026-05-28 | `port:2746` | 403 | argo-workflows | All "No data returned" — confirms port 2746 HTTP body not crawled by Shodan. TCP open detected only. Aliyun 169, Internet Rimon/IL 49, ACEVILLE 38, Fly.io 26. Port 2746 passive discovery is definitively dead in Shodan. |
| 2026-05-28 | `http.html:"assets/favicon/favicon-32x32.png" noindex` | 157 | argo-workflows | HIGH FP — iptel.ua VoIP fleet + Auvious video, not Argo. Path too generic. |
| 2026-05-28 | `port:9880 http.html:"GPT-SoVITS"` | 0 | voice-audio-ai | API port not crawled by Shodan |
| 2026-05-28 | `port:9872 http.html:"GPT-SoVITS"` | 2 | voice-audio-ai | Taiwan MoE + Shanghai UCloud; both offline at probe time (indexed 2026-05-02) |
| 2026-05-28 | `port:9874 http.html:"GPT-SoVITS"` | 0 | voice-audio-ai | Training WebUI port not indexed |
| 2026-05-28 | `port:9871 http.html:"GPT-SoVITS"` | 0 | voice-audio-ai | Proofreading tool port not indexed |
| 2026-05-28 | `http.html:"GPT-SoVITS"` | 23 | voice-audio-ai | Broad: 22 unique IPs; CN 9/US 6/JP 4/UAE 1/KR 1/SG 1; top ports 80(5)/8800(4)/8000(3)/443(2)/9872(2); operators: Aliyun(3)/CHINANET-ZJ(4)/GMO(2)/Lambda(2) |
| 2026-05-28 | `port:9880 http.html:"/set_gpt_weights"` | 0 | voice-audio-ai | API endpoint string not indexed by Shodan |
| 2026-05-28 | `port:7865 http.html:"RVC-Boss"` | 0 | voice-audio-ai | RVC-Boss variant not present |
| 2026-05-28 | `http.html:"vigil-llm"` | 0 | safety-guardrail | dead — Shodan doesn't index Flask response body content for Vigil |
| 2026-05-28 | `port:5000 http.html:"/analyze/prompt"` | 0 | safety-guardrail | dead — endpoint path not indexed on port 5000 |
| 2026-05-28 | `port:5000 http.html:"/settings" http.html:"scanner"` | 36 | safety-guardrail | all FP — Synology NAS / Ukrainian betting bot admin panels. "scanner" is common word on port 5000. |
| 2026-05-28 | `port:5000 http.html:"prompt_entropy"` | 0 | safety-guardrail | dead — Vigil JSON field names not indexed |
| 2026-05-28 | `http.html:"/v1/rails/configs"` | 0 | safety-guardrail | dead — NeMo Guardrails endpoint paths not indexed by Shodan |
| 2026-05-28 | `http.html:"nemoguardrails" port:8000` | 0 | safety-guardrail | dead — package name not in indexed responses |
| 2026-05-28 | `http.html:"/v1/rails/generate"` | 0 | safety-guardrail | dead — NeMo path not indexed |
| 2026-05-28 | `http.html:"LLM Guard API"` | 8 | safety-guardrail | PRIMARY WORKING DORK — exact OpenAPI title string. 2 live confirmed (15.204.46.173, 57.128.58.103). 6 offline/unreachable. |
| 2026-05-28 | `http.html:"laiyer/llm-guard"` | 0 | safety-guardrail | dead — Docker image name not indexed |
| 2026-05-28 | `port:8000 http.html:"llm-guard"` | 3 | safety-guardrail | 3 hits; all overlap with exact-title dork. Secondary dork confirmed working. |
| 2026-05-28 | `port:3000 http.html:"rebuff.ai"` | 0 | safety-guardrail | dead — Rebuff archived, no live self-hosted deployments visible |
| 2026-05-28 | `port:3000 http.html:"/api/detect" http.html:"rebuff"` | 0 | safety-guardrail | dead |
| 2026-05-28 | `port:8000 http.html:"guardrailsai.com"` | 0 | safety-guardrail | dead — Guardrails AI Hub URL not indexed on :8000 |
| 2026-05-28 | `http.html:"hub.guardrailsai.com"` | 0 | safety-guardrail | dead |
| 2026-05-28 | `http.html:"Llama-Guard-3"` | 0 | safety-guardrail | dead — model name not in indexed responses |
| 2026-05-28 | `http.html:"meta-llama/Llama-Guard" port:8000` | 0 | safety-guardrail | dead |
| 2026-05-28 | `http.html:"ShieldLM" port:8000` | 0 | safety-guardrail | dead |
| 2026-05-28 | `http.html:"Llama-Prompt-Guard" port:8000` | 0 | safety-guardrail | dead |
| 2026-05-28 | `http.html:"LlamaFirewall"` | 0 | safety-guardrail | dead |

## 2026-05-28 — Cat-30: Specialty Data Layers

| Date | Query | Hits | Survey | Notes |
|---|---|---|---|---|
| 2026-05-28 | `"X-ClickHouse-Server-Display-Name"` | 270 | cat-30-clickhouse | Header-confirmed HTTP-responding instances; 120 unique IPs harvested |
| 2026-05-28 | `port:8123 product:"ClickHouse"` | 11,772 | cat-30-clickhouse | Full population baseline |
| 2026-05-28 | `port:8123 "ClickHouse"` | 12,001 | cat-30-clickhouse | Broad banner match |
| 2026-05-28 | `port:8123 "Ok." country:US` | 14,330 | cat-30-clickhouse | FP-heavy — "Ok." matches many HTTP servers, not usable |
| 2026-05-28 | `"X-ClickHouse-Exception-Code"` | 219 | cat-30-clickhouse | Auth-error header — servers responding to unauth probes |
| 2026-05-28 | `port:9000 "ClickHouse"` | 8,792 | cat-30-clickhouse | Native TCP port; port:9000 collides with MinIO/Hadoop |
| 2026-05-28 | `port:9042 "Cassandra"` | 1 | cat-30-cassandra | Single honeypot; CQL binary protocol not Shodan-indexable by text |
| 2026-05-28 | `product:"Cassandra"` | 89 | cat-30-cassandra | Shodan Thrift fingerprint; leaks cluster topology; 70 IPs harvested |
| 2026-05-28 | `port:9042 "ScyllaDB"` | 0 | cat-30-scylla | CQL binary — no text banner |
| 2026-05-28 | `product:"ScyllaDB"` | 0 | cat-30-scylla | No Shodan product fingerprint for ScyllaDB |
| 2026-05-28 | `port:10000 "scylla"` | 0 | cat-30-scylla | REST API not indexed this way |
| 2026-05-28 | `port:9042` | 455,506 | cat-30-cassandra | Raw port count — masscan target, not Shodan filter |
| 2026-05-28 | `port:9000 "Apache Pinot"` | 31 | cat-30-pinot | Precision dork; 31 IPs harvested |
| 2026-05-28 | `http.title:"Apache Pinot"` | 29 | cat-30-pinot | Slight subset of above |
| 2026-05-28 | `port:8000 "pinot"` | 0 | cat-30-pinot | No Pinot on port 8000 |
| 2026-05-28 | `port:9999 "duckdb"` | 888 | cat-30-duckdb | All FP — Dozzle Docker log viewer CSP header |
| 2026-05-28 | `"duckdb" port:8000` | 12 | cat-30-duckdb | Same FP class; no actual DuckDB HTTP servers found |
| 2026-05-28 | `port:9180 "scylladb"` | 0 | cat-30-scylla | No hits |
| 2026-05-28 | `port:9042 "SCYLLA_SHARD_AWARE_PORT"` | 0 | cat-30-scylla | Protocol field not Shodan-indexed |
| 2026-05-28 | `port:10000 "Seastar"` | 58 | cat-30-scylla | ScyllaDB REST API; 10 IPs harvested |
| 2026-05-28 | `port:9180 "seastar"` | 99 | cat-30-scylla | ScyllaDB Prometheus; 99 IPs harvested |

## 2026-05-28 — RAG Stragglers Survey

| Date | Query | Total Hits | Survey | Notes |
|---|---|---|---|---|
| 2026-05-28 | `http.title:"RAGFlow"` | 1,902 | rag-stragglers | Primary RAGFlow population; 50 IPs sampled; 7 confirmed auth-enforced |
| 2026-05-28 | `http.html:"ragflow" port:80` | 540 | rag-stragglers | Subset of title dork |
| 2026-05-28 | `port:9380 http.html:"ragflow"` | 0 | rag-stragglers | Internal port not crawled |
| 2026-05-28 | `http.html:"/api/v1/user/login" http.html:"ragflow"` | 0 | rag-stragglers | String not in Shodan index |
| 2026-05-28 | `http.title:"DocsGPT"` | 8 | rag-stragglers | Full DocsGPT population; 8 IPs sampled; 0 confirmed |
| 2026-05-28 | `port:5001 http.html:"DocsGPT"` | 0 | rag-stragglers | Dead dork |
| 2026-05-28 | `http.html:"DocsGPT" http.html:"uvicorn"` | 0 | rag-stragglers | Dead dork |
| 2026-05-28 | `port:8000 http.html:"ragapp" http.html:"/admin"` | 0 | rag-stragglers | Ragapp not indexed |
| 2026-05-28 | `http.title:"Ragapp"` | 0 | rag-stragglers | Ragapp not indexed |
| 2026-05-28 | `port:9621 http.html:"LightRAG"` | 0 | rag-stragglers | Default port not crawled by Shodan |
| 2026-05-28 | `http.html:"LightRAG" http.html:"swagger"` | 5 | rag-stragglers | Best LightRAG dork; 5 IPs collected; 2 confirmed unauth |
| 2026-05-28 | `http.html:"LightRAG" http.html:"/query"` | 1 | rag-stragglers | Narrow LightRAG signal; subset of swagger dork |
| 2026-05-28 | `http.title:"LiteLLM"` | 57,130 | LiteLLM Cat-30 | 100 scraped (10 pages); top ports 4000/443/80; 20,599 tagged LiteLLM product |
| 2026-05-28 | `"healthy_endpoints" "healthy_count"` | 0 | LiteLLM Cat-30 | Zero results |
| 2026-05-28 | `http.html:"litellm_params"` | 0 | LiteLLM Cat-30 | Zero results |
| 2026-05-28 | `http.headers:"x-litellm-version"` | 0 | LiteLLM Cat-30 | Zero results |
| 2026-05-28 | `http.html:"litellm" port:4000` | 2,367 | LiteLLM Cat-30 | 100 scraped (10 pages); Hetzner/DO/Contabo dominant; 170 unique IPs total (dedup across all dorks) |
