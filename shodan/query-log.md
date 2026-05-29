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

## 2026-05-28 — Auth/Gateway Survey

| Date | Query | Hits | Survey | Notes |
|---|---|---|---|---|
| 2026-05-28 | `port:3567 "Hello" http.status:200` | 455 | auth-gateway | SuperTokens primary dork — confirmed TOTAL RESULTS 455 from rendered Shodan page; top orgs Linode/Aliyun/Alibaba Cloud |
| 2026-05-28 | `port:9000 http.title:"authentik" http.status:200` | 1,000+ | auth-gateway | Authentik — hits Shodan display cap; top orgs Hetzner/Contabo/OVH; EU-dominant |
| 2026-05-28 | `port:9091 http.title:"Authelia" http.status:200` | 33 | auth-gateway | Authelia — confirmed 33 total; 10 IPs harvested |
| 2026-05-28 | `port:8001 "via: kong" http.status:200` | ~4 | auth-gateway | Kong admin API — 4 IPs: 222.77.87.242, 46.224.151.168, 159.203.154.157, 188.245.181.37 |
| 2026-05-28 | `port:4445 http.html:"client_id"` | ~6 | auth-gateway | Hydra/OAuth2 candidate — 6 IPs; requires identity verification (client_id field not unique to Hydra) |
| 2026-05-28 | `http.title:"Keycloak" port:8080` | unknown | auth-gateway | Keycloak — 10 IPs harvested from fetch; TOTAL RESULTS count not confirmed from rendered page |
| 2026-05-28 | `http.title:"Casdoor" port:8000` | unknown | auth-gateway | Casdoor — 10 IPs harvested; total count unconfirmed |
| 2026-05-28 | `http.title:"ZITADEL" port:8080` | unknown | auth-gateway | ZITADEL — 10 IPs harvested; total count unconfirmed |
| 2026-05-28 | `port:8181 http.html:"Open Policy Agent"` | unknown | auth-gateway | OPA — 10 IPs harvested; GCP cluster (34.x/35.x prefixes); total unconfirmed |
| 2026-05-28 | `port:4434 "identities" http.status:200` | 0 | auth-gateway | Kratos admin — dead; port 4434 not in Shodan HTTP index |
| 2026-05-28 | `port:4434 http.html:"admin/identities"` | 0 | auth-gateway | Kratos admin alt — dead |
| 2026-05-28 | `port:4434 "kratos"` | 0 | auth-gateway | Kratos any — dead; port 4434 not indexed |
| 2026-05-28 | `port:4445 "clients" http.status:200` | 0 | auth-gateway | Hydra admin primary — dead; port 4445 not indexed |
| 2026-05-28 | `port:4445 "hydra"` | 0 | auth-gateway | Hydra any — dead |
| 2026-05-28 | `port:8080 "x-tyk-gateway" http.status:200` | 0 | auth-gateway | Tyk gateway header — dead |
| 2026-05-28 | `port:8080 "x-tyk-authorization"` | 0 | auth-gateway | Tyk auth header — dead |
| 2026-05-28 | `port:3000 http.title:"Tyk Dashboard"` | 0 | auth-gateway | Tyk dashboard — dead |
| 2026-05-28 | `port:7002 "opal_updates"` | 0 | auth-gateway | OPAL pub/sub — dead |
| 2026-05-28 | `port:7002 "opal" http.status:200` | 0 | auth-gateway | OPAL broad — dead |
| 2026-05-28 | `port:8181 "v1/data" http.status:200` | 0 | auth-gateway | OPA primary dork — dead; path not in Shodan crawl |
| 2026-05-28 | `port:8181 "/v1/policies"` | 0 | auth-gateway | OPA policy path — dead |
| 2026-05-28 | `port:4433 "csrf_token"` | unknown | auth-gateway | Kratos public API — broad hits; requires per-host identity verification |
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

## 2026-05-28 — K8s FinOps Cost-Allocation (Kubecost/OpenCost) — NEW SLICE

NOTE: "Cost/Billing/Usage Analytics" was already surveyed 2026-05-19 (cost-billing-analytics-survey-2026-05-19.md → Insight #37): Lago/Helicone/OpenMeter/Phoenix/LiteLLM-spend. Lago (349) and Helicone (5) rows below OVERLAP that prior work. The genuine new contribution is Kubecost (116) + OpenCost (~9) = K8s FinOps cost-allocation class, NOT in the 2026-05-19 survey. Distinct surface: cost-model API on :9090. Insight #37 lens applies (UI gated vs cost-model API open).

| Date | Query | Total Hits | Survey | Notes |
|---|---|---|---|---|
| 2026-05-28 | `http.title:"Kubecost"` | 116 | cost-billing | PRIMARY WORKING DORK. US 59/SG 16/ID 11/IE 9/IN 6; ports 80(75)/9090(23)/443(18); orgs Amazon 63/Google 15/MS; all cloud (EKS/GKE). Dashboard root returns HTTP 200 + ACAO:* on sampled hosts (verification target). Versions leaked via ETag (2.7.1-3.1.3); many tagged eol-product. Pivot dork: http.favicon.hash:611531125 |
| 2026-05-28 | `http.html:"openmeter"` | 0 | cost-billing | WRONG-DORK ARTIFACT — bare HTML dork returns 0, but prior survey (cost-billing-analytics-survey-2026-05-19) got 30 via `port:8888 http.html:"openmeter"` confirmed through /api/v1/portal/info. OpenMeter is NOT Shodan-dark; use the port-scoped dork. This category was already surveyed 2026-05-19. |
| 2026-05-28 | `http.html:"lago-front"` | 0 | cost-billing | Lago SPA build marker not indexed (Shodan stores shell only). Dead niche dork. |
| 2026-05-28 | `http.title:"Lago"` | 349 | cost-billing | REFINEMENT — FP-heavy ("Lago" = lake in IT/ES/PT: Synology NAS, IIS sites, lake-named businesses). US 125/DE 46/IT 27/CN 18/IE 16; Hetzner 34/DO 29/Amazon. GENUINE Lago billing telltale: title exactly "Lago" + CL 792/1268 + CSP frame-ancestors *.force.com *.zive.app. Operator cluster: Elestio one-click (lago-*.vm.elestio.app); real deploys e.g. lago.quadient.codes. Use CSP discriminator for intel doc, not bare title. |
| 2026-05-28 | `http.title:"Helicone"` | 5 | cost-billing | All genuine, zero FP. Title "Helicone - Open-Source Generative AI Platform for Developers" + X-Powered-By:Next.js. 4 unique IPs: 54.147.228.203 (helicone.tools.forge.gg/AWS), 137.184.217.47 (benchmarkit.solutions/DO, also :3000), 3.75.2.136 (helicone.glami-ml.com/AWS DE), 188.34.196.197 (Hetzner DE :3000). Ports 443(3)/3000(2). All HTTP 200. |
| 2026-05-28 | `http.html:"opencost"` | 31 | cost-billing | CNCF OpenCost exporter. US 15/DE 5/IN 3/FR 2/IE 2; ports 80(15)/9090(11)/443(4); Amazon 13/Contabo/MS/OVH. TP telltale: ETag 1.96.0 + favicon.hash 2140086526. FP class: opencost.de (132.199.150.68, Uni Regensburg, Apache/GEANT) = German "openCost Registry" construction-cost standard, namesake, unrelated. Auth-gated: encardio (52.66.151.224, SSO login page). ~9 genuine open exporters; verification target = /model/allocation API |

### 2026-05-29 — Lakera GATEWAY pivot (Portkey lead -> LiteLLM/Kong/Portkey)

Hypothesis: Lakera is consumed THROUGH LLM gateways (Portkey/LiteLLM/Kong), which are deployed infra and far more Shodan-visible than a server-side SDK call. Each gateway names Lakera in config with a gateway-unique string: LiteLLM `guardrail: lakera_v2`, Kong plugin `ai-lakera-guard`, Portkey check "Lakera Guard". Result: config-string LIFT vectors are dark (server-side config never reaches the crawled root), but the Kong plugin string resolved to a real misconfig class.

| Date | Query | Hits | Survey | Notes |
|---|---|---|---|---|
| 2026-05-29 | `http.html:"lakera_v2"` | 0 | guardrail | LiteLLM Lakera-v2 provider string. Server-side config.yaml; not in crawled Swagger root. Lift vector dark |
| 2026-05-29 | `"lakera_v2"` | 0 | guardrail | bare-banner variant; same null |
| 2026-05-29 | `http.html:"ai-lakera-guard"` | 6 | guardrail | SAME 6 IPs as `http.html:"Lakera Guard"` (q9). = EXPOSED KONG ENTERPRISE ADMIN API on :8001. VERIFIED 34.57.164.89 (GCP us-central1): :8000 kong/3.13.0.1-enterprise-edition proxy; :8001 admin API HTTP 200 application/json Content-Length 27609 (X-Kong-Admin-Request-ID, X-Kong-Admin-Latency), CORS Access-Control-Allow-Origin http://IP:8002 + Allow-Credentials:true (Kong Manager on :8002). The string comes from the admin-root available-plugins catalog -> Lakera plugin is INSTALLED IN BUILD, NOT confirmed CONFIGURED. Real finding = exposed Kong admin API class (full gateway control per Kong admin API capability), surfaced via the Lakera plugin string. Surface open (Shodan captured 200 + 27KB admin JSON unauth); access not exercised. Other 5 share identical dork+JSON/CORS signature, not individually verified |
| 2026-05-29 | `http.title:"LiteLLM"` | 59,895 | guardrail | LiteLLM gateway BASELINE (2,316 on :4000; orgs Amazon-heavy + A100 ROW 3,572). lakera_v2=0 against this baseline confirms Lakera-via-LiteLLM config is not Shodan-visible. Lift-by-config-string vector dead for LiteLLM |

LESSON (Insight candidate): a gateway plugin-catalog string finds EXPOSED ADMIN APIs reliably, but "plugin available in build" != "plugin configured/enabled." Do not conflate plugin-availability with vendor usage. The high-value byproduct is the misconfig the dork surfaces (Kong :8001 admin exposure), not the guardrail attribution. To confirm enabled-Lakera you must read the /plugins collection (availability lives at admin root); that requires active third-party probing -> out of scope without authorization.

### 2026-05-29 — Lakera "relations in code" pivot (guard-demo-client template) — METHOD CLOSED

Thesis: the Lakera call is server-side and never observable (api.lakera.ai=0, lakera_v2=0 all confirmed). So map WHO uses Lakera via code, extract the deployable's OBSERVABLE ring, and dork the ring instead of the invisible center.
Source: github.com/lakeraai/guard-demo-client ("A demo client application for Lakera Guard"), 44 forks dominated by Check Point SEs (chkp-bryans, *CheckPoint, CloudGuard-Training, mazh-cp, *CP) + NTT Data (thnttdata) + Thai integrators (supachai-j, pakawatw). The fork network IS the deployer map.
Template ring: Vite/React 18 SPA, static <title>Agentic Demo</title>, pkg "agentic-demo-frontend", favicon /vite.svg (default, useless). Backend FastAPI EXPOSE 8000 (start_all.py). Bundled LiteLLM proxy :4000 image litellm/litellm:v1.82.3 with DEFAULT DEMO CREDS master_key sk-demo-master-key / UI admin:demo / DISABLE_ADMIN_UI=False. Lakera via backend/lakera.py -> POST api.lakera.ai/v2/guard {breakdown,payload,dev_info} (server-side; invisible). Also bakes internal endpoint staging-openai.azure-api.net/openai-gw-proxy-app/.

| Date | Query | Hits | Survey | Notes |
|---|---|---|---|---|
| 2026-05-29 | `http.title:"Agentic Demo"` | 4 | guardrail | RING DORK — finds guard-demo-client deployments with ZERO Lakera string in query. 3x Google SE demos (bq-agents / bq-agents-partner / bq-agentic .gricardo.demo.altostrat.com, GCP, altostrat=Google demo domain) + 1x Thai integrator 119.110.254.51 (thtechs.com / Symphony Communication Plc, Bangkok, nginx/1.18.0, LE cert thtechs.com, eol-product). FP CAVEAT: "Agentic Demo" is not Lakera-unique; verify per host. These are demos/POCs not confirmed prod customers |
| 2026-05-29 | `"sk-demo-master-key"` | 0 | guardrail | Demo LiteLLM default master key not echoed in any crawled banner (config secret, never surfaced). Null = no key leak via Shodan |

INSIGHT (candidate): For an invisible server-side dependency, fingerprint the DEPLOYABLE it ships inside, not the dependency. The template's frontend shell title is the cross-deployment fingerprint; deployer attribution comes from the GitHub fork network, not the host. This finds the demo/SE/POC population (who share the template shell), NOT bespoke prod customers (who don't). Bespoke prod needs a different observable relation: the bundled LiteLLM :4000 ring, the user-facing block-message string, or org/ASN cross-ref from the customer list.

### 2026-05-29 — Lakera VERIFICATION pass (corrections + per-host confirmation)

Verification overturned the raw counts. Logged honestly.

| Date | Query | Hits | Survey | Notes |
|---|---|---|---|---|
| 2026-05-29 | `http.title:"Agentic Demo"` | 4 RAW / 1 REAL | guardrail | FP CORRECTION: 3 of 4 are Google's "BigQuery Agentic Demo Engine" (Express/Node on Cloud Run, *.gricardo.demo.altostrat.com = Google demo domain) — Shodan http.title substring-matched "Agentic Demo". NOT Lakera. Verified 34.49.56.93 = Express/Google, no vite/lakera. Only 119.110.254.51 is the real guard-demo-client |
| 2026-05-29 | `http.title:"Agentic Demo" http.html:"vite.svg"` | 1 | guardrail | REFINED / FP-FREE. +vite.svg discriminator drops the 3 Google BigQuery FPs. Sole real guard-demo-client deployment = 119.110.254.51 (thtechs.com / Symphony Communication Plc, Bangkok; nginx/1.18.0; 443-only; 617-byte Vite shell; LE cert; backend/LiteLLM not exposed). Lakera invisible in shell (in JS bundle) as expected |
| 2026-05-29 | `http.html:"Powered by Lakera"` | 2 | guardrail | "Secure AI Chat - Powered by Lakera AI" lineage (DISTINCT from guard-demo-client, which has always titled "Agentic Demo" since first commit). Brand string in <title> = Shodan-visible. Both Azure: 20.57.185.155 (Microsoft, Moses Lake) + 172.203.242.228 (Microsoft Limited, Flint Hill). No public repo matches; custom/hosted Lakera demo |

KONG exposed-admin class — verified 2/6:
- 34.57.164.89 (GCP us-central1): kong/3.13.0.1-enterprise-edition; :8000 proxy, :8001 admin 200 JSON 27609B, :8002 Kong Manager (CORS). 
- 139.196.55.32 (Aliyun Shanghai): kong/3.13.0.3-enterprise-edition; :8000 proxy, :8001 admin 200 JSON 27926B (CORS internal 172.23.56.217:8002), :8443 proxy-TLS; self-signed.
Both: admin API internet-exposed (Shodan captured unauth 200 + 27KB config JSON). ai-lakera-guard present in admin available-plugins catalog (plugin in build, NOT confirmed configured). Finding = exposed Kong Enterprise admin API class. Surface open; access not exercised (out of scope to drive).

GitHub evidence (code-relation map):
- lakeraai/guard-demo-client = canonical Lakera demo. 37 forks, ALL retain <title>Agentic Demo (zero rebrands since first commit 2025-10-17). Fork owners heavy Check Point SE (chkp-*, *CheckPoint, CloudGuard-Training, mazh-cp, *CP) + NTT Data (thnttdata) + Thai integrators (matches the Thai live host). Stack: Vite/React SPA :8000 (FastAPI start_all.py) + bundled LiteLLM :4000 default creds (sk-demo-master-key / admin:demo). All Lakera UI strings live in .tsx (hashed JS bundle) => NOT Shodan-visible. Only static fingerprint = the title.

## 2026-05-29 — Voice/Audio AI cat-17 re-run (Playwright web UI, API keys dead)

| Dork | Total | Note |
|------|-------|------|
| `http.html:"GPT-SoVITS"` | 22 | brand-dork, page1 mostly FP; ports 80/8800/8000 not 9880 |
| `http.html:"GPT-SoVITS" port:9880` | 0 | API JSON-only root, Shodan-dark (Insight #21) |
| `http.html:"rvc-webui"` | 4 | all ByteDance Volcano; 3/4 uvicorn; 11x CVSS-9.8 RCE candidates |
| `port:8880 http.html:"/dev/captioned_speech"` | 0 | Kokoro unique path not indexed |
| `port:8880 http.html:"Kokoro"` | 2 | Hetzner + Chinanet real Kokoro demos |
| `http.html:"/v1/audio/speech" -openai` | 12 | highest-yield; OpenAI-compat TTS; 9 unique IPs uvicorn |
| `http.html:"system_health" http.html:"active_batch_requests"` | 0 | Deepgram /v1/status JSON not crawled, Shodan-dark |
| `http.html:"chatterbox"` | 96 | FP swamp (walls art, entermediadb DAM); single-keyword collision |
| `http.title:"Chatterbox TTS"` | 18 | CLEAN; real Chatterbox; ports 8004/4321; voice-clone surface |
| `port:9090 "WhisperLive"` | 0 | WS JSONL not indexed; 9090=Prometheus; PII surface Shodan-dark |
| `port:8899 http.html:"Orpheus"` | 0 | Orpheus API JSON-only |
| `http.title:"Orpheus TTS"` | 0 | Orpheus variant space exhausted |
| `"whisper.cpp" "/inference"` | 12 | CLEAN conjunctive; real whisper.cpp ASR; compute-theft |
| `http.html:"so-vits-svc"` | 2 | FP; CN music marketing pages; so-vits-svc Shodan-dark |
| `http.html:"xtts"` | 34 | ~50% rule; real XTTS mixed w/ FP; needs title anchor |

**Category finding:** OpenAI-compat voice API servers (GPT-SoVITS, Orpheus, Kokoro API, Deepgram, WhisperLive) return JSON-only roots that Shodan cannot index — the RCE/PII surfaces are Shodan-dark. Only the demo/Swagger HTML UI pages get indexed, in tiny counts. Title-anchored dorks (Chatterbox) beat html-keyword dorks (FP swamp). Confirms Insight #21 (port-first > brand-dork) for the entire voice-AI category.
