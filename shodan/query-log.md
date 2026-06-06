# Shodan Query Results Log

Every executed dork is logged here — zero hits are results, not skips.

| Date | Query | Total Hits | Survey | Notes |
| 2026-06-05 | `"SillyTavern"` | 8,900 | cat-03-model-serving | Banner match; 19 IPs sampled (5 pages) |
| 2026-06-05 | `http.html:"/v1/chat/completions"` | 7,263 | cat-03-model-serving | OpenAI-compat catch-all; 19 IPs |
| 2026-06-05 | `http.html:"/v1/models"` | 7,390 | cat-03-model-serving | OpenAI-compat models endpoint; 20 IPs |
| 2026-06-05 | `"llama.cpp"` | 1,466 | cat-03-model-serving | Banner match; 20 IPs |
| 2026-06-05 | `"llama.cpp" port:8080` | 363 | cat-03-model-serving | Port-narrowed default port; 20 IPs |
| 2026-06-05 | `"vLLM"` | 336 | cat-03-model-serving | Banner match; 16 IPs |
| 2026-06-05 | `http.html:"TEI"` | 263 | cat-03-model-serving | HuggingFace TEI; 19 IPs |
| 2026-06-05 | `http.html:"faster-whisper"` | 228 | cat-03-model-serving | faster-whisper ASR; 20 IPs |
| 2026-06-05 | `http.html:"sentence-transformers"` | 211 | cat-03-model-serving | sentence-transformers serving; 20 IPs |
| 2026-06-05 | `http.title:"Whisper"` | 479 | cat-03-model-serving | Whisper ASR web UIs; 20 IPs |
| 2026-06-05 | `http.html:"sglang"` | 143 | cat-03-model-serving | SGLang in HTML; 20 IPs |
| 2026-06-05 | `http.html:"lm studio"` | 126 | cat-03-model-serving | LM Studio desktop app; 20 IPs |
| 2026-06-05 | `http.html:"coqui"` | 47 | cat-03-model-serving | Coqui TTS; 20 IPs |
| 2026-06-05 | `"koboldcpp"` | 43 | cat-03-model-serving | KoboldCpp banner; 20 IPs |
| 2026-06-05 | `"sglang"` | 37 | cat-03-model-serving | SGLang banner; 20 IPs |
| 2026-06-05 | `"koboldai"` | 21 | cat-03-model-serving | KoboldAI banner; 20 IPs |
| 2026-06-05 | `"lmdeploy"` | 3 | cat-03-model-serving | LMDeploy; ALL 3 IPs sampled |
| 2026-06-05 | `"Aphrodite Engine"` | 0 | cat-03-model-serving | Zero. Exact phrase; low deployment. |
| 2026-06-05 | `http.html:"GPT4All"` | 0 | cat-03-model-serving | Zero. localhost-default; not internet-exposed. |
| 2026-06-05 | `http.html:"nvidia nim"` | 0 | cat-03-model-serving | Zero. NIM mostly cloud-hosted/internal. |
| 2026-06-05 | `port:1234 "model"` | 0 | cat-03-model-serving | Zero. LM Studio port; HTML not indexed at depth. |
| 2026-06-05 | `http.html:"/v1/embeddings"` | 0 | cat-03-model-serving | Zero. Path in JSON body not HTML-embedded. |
| 2026-06-05 | `http.html:"jina"` | 0 | cat-03-model-serving | Zero. Jina self-hosted rare on public internet. |
| 2026-06-05 | `http.title:"Bark"` | 0 | cat-03-model-serving | Zero. No canonical Bark HTTP server title. |
| 2026-06-05 | `http.title:"Piper"` | 0 | cat-03-model-serving | Zero. Piper TTS — no standard HTTP title. |
| 2026-06-01 | `"AI Gateway says hey"` | 0 | ai-gateways | Portkey health endpoint not publicly indexed; pure API proxy, no web UI |
| 2026-06-01 | `"Welcome to kong" port:8001` | 0 | ai-gateways | Kong Admin API body string not matching; try `product:kong port:8001` |
| 2026-06-01 | `http.html:"available_on_server" http.html:"ai-proxy" port:8001` | 277 | ai-gateways | Kong AI plugin confirmed active; 100 IPs harvested (page 1 of 3) |
| 2026-06-01 | `http.title:"Bifrost AI Gateway"` | 0 | ai-gateways | Title differs in deployed instances; body+favicon dorks cover population |
| 2026-06-01 | `http.html:"getbifrost.ai" port:8080` | 82 | ai-gateways | Bifrost footer link; 82 IPs harvested |
| 2026-06-01 | `http.favicon.hash:1651823509` | 237 | ai-gateways | Bifrost favicon; 97 IPs harvested |
| 2026-06-01 | `http.title:"One API" port:3000` | 2,449 | ai-gateways | one-api; 100 IPs harvested (page 1 of 25) |
| 2026-06-01 | `http.title:"New API" port:3000` | 13,456 | ai-gateways | new-api; 114 IPs harvested (page 1 of 135) -- LARGEST EXPOSED GATEWAY POPULATION |
| 2026-06-01 | `http.favicon.hash:1318451613` | 274 | ai-gateways | one-api favicon; 95 IPs harvested |
| 2026-06-01 | `http.favicon.hash:-1643864359` | 251 | ai-gateways | new-api favicon; 99 IPs harvested |
| 2026-06-01 | `port:8585 http.html:"helicone"` | 0 | ai-gateways | Helicone worker port not indexed; tool in maintenance mode |
| 2026-06-01 | `http.favicon.hash:-794809853` | 2 | ai-gateways | Helicone self-hosted favicon; 2 IPs harvested |
| 2026-06-01 | `port:9901 http.html:"config_dump"` | 89 | ai-gateways | Envoy admin config_dump; 87 IPs harvested; HIGH PRIORITY |
| 2026-06-01 | `http.title:"TensorZero"` | 1 | ai-gateways | TensorZero; 1 IP harvested |
| 2026-06-01 | `http.favicon.hash:-112038367` | 268 | ai-gateways | Kong Manager UI (:8002); 97 IPs harvested |
| 2026-06-01 | `"Server: kong"` | 70,924 | ai-gateways | Full Kong install base (all deployments, not just AI plugin); most durable Kong signal |
| 2026-06-01 | `port:8001 http.html:"Welcome to Kong"` | 600 | ai-gateways | FIXED from dork 2 (lowercase k bug); Kong Admin API root JSON -- capital K required |
| 2026-06-01 | `http.title:"LiteLLM"` | 65,976 | ai-gateways | LiteLLM -- MISSED PLATFORM; second largest gateway population after new-api |
| 2026-06-01 | `port:4000 http.html:"litellm"` | 2,290 | ai-gateways | LiteLLM port-specific; subset of title dork |
| 2026-06-01 | `http.html:"healthy_endpoints"` | 1 | ai-gateways | LiteLLM /health body leaked; too narrow |
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

## 2026-05-29 — ML Governance / Data Catalog (Playwright, API keys dead)

| Dork | Total | Note |
|------|-------|------|
| `http.title:"OpenMetadata" port:8585` | 56 | clean; auth-on; 10/10 sampled v1.10-1.12 (CVE-2024-28255 needs <1.3.1, all patched); catalog 401-gated |
| `http.title:"DataHub" port:9002` | 27 | clean frontends; GMS :8080 NOT exposed on 10/10 (secure); 3.30.235.161=AWS us-gov-west-1 |
| `port:21000 http.title:"Atlas"` | 0 | Atlas Shodan-dark (Cloudera/HDP internal) |
| `http.html:"api/atlas/v2"` | 0 | Atlas API path not in HTML |
| `port:21000 "Apache Atlas"` | 0 | Atlas variant space exhausted |
| `http.html:"ckan_version"` | 0 | JSON field not in crawled HTML |
| `http.html:"ckan" port:5000` | 53 | gov open-data portals; reads open by design |
| `http.html:"marquezproject"` | 0 | string not in crawled HTML |
| `http.title:"Marquez"` | 50 | ~50% real Marquez (auth-off); surname FP (Xorcom/Ortigosa/Juan Marquez); 1 confirmed unauth (demo) |

**Category verdict:** well-secured at population scale. Auth-on (OpenMetadata) patched; auth-off (DataHub GMS, Marquez) dark/not-public/demo. Thesis confirmed by SECURE branch. 1 unauth Marquez (demo, no prod data). 0 exploitable CVE-2024-28255. Verification = version-bucketing (extends Insight #16: a 200 from /api/v1/system/version is identity+version, not auth state).

## 2026-05-29 — LLM Safety/Guardrail (Playwright, paced)

| Dork | Total | Note |
|------|-------|------|
| `http.html:"LLM Guard API"` | 9 | CLEAN; 1 unauth (5.78.101.230) / 2 auth / 4 aged-out. Only guardrail marker that indexes |
| `http.html:"/v1/rails/configs"` | 0 | NeMo JSON-dark |
| `port:5000 http.html:"vigil"` | 20 | FP swamp: Pro-Vigil cameras + Synology NAS, NOT vigil-llm |
| `http.html:"guardrails-ai" port:8000` | 0 | Swagger-dark |
| `http.html:"rebuff" port:3000` | 0 | archived, Next.js, string not in HTML |

**Finding:** 5.78.101.230 (Hetzner) unauth LLM Guard :8000 + STACKED unauth data tier (MongoDB/Redis 7.2.10/MySQL/Postgres/Docker-registry). The safety tool was the least-guarded thing (Insight #12). Thesis: AUTH_TOKEN opt-in -> 1/3 open. aimap has no guardrail fingerprint (gap).

## 2026-05-29 — Experiment Tracking (registry/RCE half; compute-orch half done 2026-05-26)

| Dork | Total | Note |
|------|-------|------|
| `http.title:"MLflow" port:5000` | 370 | BIG unauth pop; 8/8 sampled unauth (counts 4-379); 34.139.85.153=379+GCS bucket aircheck-mlflow-tracking |
| `http.title:"Determined" port:8080` | 6 | 4 real all auth-ON (401), incl 2 AWS us-gov-west-1; admin:blank NOT present; +2 FP "could not be determined" |
| `port:8265 http.title:"Ray"` | 1 | stale (2026-05-03); ShadowRay pop React-SPA Shodan-dark |
| `http.html:"ray dashboard" port:8265` | 0 | React SPA string not in HTML |
| `port:43800 http.html:"aim"` | 0 | Aim React SPA, JSON-dark |

**Finding:** MLflow unauth-by-default confirmed (8/8 sampled). Headline 34.139.85.153 = 379 unauth experiments + leaked GCS bucket. Determined auth-on (intel admin:blank absent). Ray/Aim Shodan-dark (Insight #67). aimap enumMLflow CVE-2024-37052+ = applicable-class (hardcoded, version-unverified) -> tier HIGH not CRITICAL. 4th thesis data point: shipping default predicts open rate (MLflow off=open, Determined on=closed, same category).

## 2026-05-29 — Model Serving (mgmt-plane/registry; inference pop done 2026-05-04)

| Dork | Total | Note |
|------|-------|------|
| `http.title:"triton" port:8000` | 1 | FP (Triton Content Engine CMS); Triton inference=JSON /v2 dark |
| `http.html:"model_sha" http.html:"tokenization_workers"` | 0 | TGI /info JSON-dark |
| `http.html:"owned_by" http.html:"vllm"` | 0 | vLLM /v1/models JSON-dark |
| `"vllm" port:8000` | 1 | 1 real (144.76.75.252 Hetzner, vLLM 0.19.0 unauth, GPT-OSS 20B) |

**Category finding:** model-serving is Shodan-dark (Insight #67 purest case). vLLM/Triton/TGI/TorchServe serve JSON; dominant server (vLLM) = 1 hit on banner. Mgmt-bypass RCE surfaces (/update_weights, ShellTorch) invisible to passive discovery -> needs masscan on 8000/8080/8081. 1 confirmed unauth vLLM (compute theft + mgmt-bypass present, not exercised). aimap has no vLLM mgmt fingerprint (gap).

## 2026-05-29 — RAG framework stragglers (Playwright)

| Dork | Total | Note |
|------|-------|------|
| `http.title:"AnythingLLM" port:3001` | 152 | CLEAN; CN/DE/US; 2/5 sampled RequiresAuth:false (browser-UI-unauth; dev API still key-gated) |
| `http.html:"ragflow"` | 1705 | BIG; Alibaba/Tencent/Linode; CVE-2024-12433 pre-auth RCE class (<0.14.0); version not externally confirmable |
| `port:9621 http.html:"LightRAG"` | 0 | LightRAG FastAPI JSON-dark (Insight #67) |
| `http.favicon.hash:-1467534538` | 0 | RAGFlow favicon hash stale |

**Finding:** AnythingLLM 2/5 browser-UI-unauth (single-user-no-auth default; dev REST API key-gated -> verification-refined MEDIUM). 213.239.218.83 also MySQL :3306 open. RAGFlow 1,705 identity-confirmed, RCE applicable-class (internal-RPC, not probed). 3 tool FPs killed: menlohunt GCS=global-namespace guess, aimap MCP=404, aimap dcm4che=RuoYi admin. aimap no RAG fingerprint (gap). Off-VPN for later arsenal (Mullvad dropped, authorized).

## 2026-05-29 — Auth / Identity / Gateway (Playwright, off-VPN)

| Dork | Total | Note |
|------|-------|------|
| `http.html:"Open Policy Agent" port:8181` | 27 | CLEAN; 5/6 sampled UNAUTH policy leak (HIGH); IN/US/DE |
| `http.html:"casdoor"` | 1375 | BIG identity platform; Alibaba/ByteDance; admin/123 default (cred-submit restraint-gated, not tested) |
| `port:8181 "v1/data" "result"` | 0 | OPA JSON-dark |
| `port:8001 "Welcome to kong"` | 0 | Kong admin API JSON-dark |

**Finding:** OPA no-auth-default CONFIRMED, 5/6 sampled leak full Rego policy list unauth via /v1/policies (HIGH; authz model + infra topology; 35.202.178.170=13 policies, operator markers stillum/strvctvra). Restraint: policy IDs/names only, NOT /v1/data secret dump or policy bodies. Casdoor 1,375 identity platforms with admin/123 default (not cred-tested). Kong/OPA admin APIs JSON-dark (Insight #67). aimap no OPA/Casdoor fingerprint (gap). 7th category; off-VPN (Mullvad down, authorized).

## 2026-05-30 — Specialty Data Layers (Playwright, off-VPN)

| Dork | Total | Note |
|------|-------|------|
| `http.title:"ClickHouse" port:8123` | 5208 | HUGE; empty-password default; auth-state SQL-GATED (not exercised; population live via /ping, NOT claimed unauth per Insight #16) |
| `http.title:"History Server" port:18080` | 33 | Spark History; 3/5 sampled UNAUTH ML-pipeline job inventories (34.145.73.130=47 apps gen-traintable/predtable/trainingjob); AWS-key env surface present, not pulled |
| `port:6566 "feature_names"` | 0 | Feast JSON-dark (Insight #67) |

**Finding:** Spark History 3/5 unauth ML-pipeline job inventories (HIGH; GCP; AWS-key environment surface present, restraint=not pulled). ClickHouse 5,208 population live but auth-state SQL-gated -> declined to execute SQL on self-selected prod DBs under generic directive (scope/restraint line held; classifier enforced). Honest non-claim > inflated number (Insight #16). aimap v1.9.40 Apache Spark UI fingerprint works (6/6). 8th category; off-VPN authorized.

## Service Mesh / Network Perimeter survey — 2026-05-31
_Shodan web UI (Playwright), logged-in. Censys attempted first but free-tier search credit-gated (2 cr balance); deferred._

| Dork | Hits | Notes |
|------|-----:|-------|
| `http.title:"Hubble UI"` | 22 | Cilium Hubble UI. Ports 80(18)/30120(2 NodePort)/8080/9002. Orgs: AWS 9, GCP 3, OVH 2. favicon.hash:-1850133310 = refined pivot. 1 host server:envoy. |
| `http.title:"Kiali"` | 140 | Istio mesh UI. Ports 443(86)/80(24)/20001(24 default)/32001+30001(NodePort). AWS 87, GCP 9. favicon.hash:533727566. Default=token now; anon-strategy subset = full cluster read (verify split). |
| `http.html:"data-controller-namespace"` | 5 | Linkerd viz dashboard. Small/niche (ClusterIP-default; rarely exposed). |
| `http.html:"pomerium"` | 1,009 | Pomerium FOOTPRINT, not findings (med-FP: matches the correct login-redirect page). Finding = behavioral public_access subset, no dork isolates it. |
| `"cilium_drop_count_total"` | 0 | **Shodan-dark.** Cilium metrics plane (9962/9965) body not indexed. Censys-only tier. |
| `port:4191 proxy_build_info` | 0 | **Shodan-dark.** Linkerd proxy-admin plane not indexed. Censys-only tier. |
| `port:15000 "config_dump"` | 0 | **Shodan-dark.** Envoy sidecar admin not indexed. Censys-only tier. |
| `ssl:"hubble-grpc.cilium.io"` | 47 | ~50% FP (Insight #15/#7: loose ssl substring → ASUS/FTP/NextChat). Genuine signal = ~10 Cilium K8s clusters via 6443 kube-apiserver (403, X-Kubernetes-Pf headers). Reaches cluster, NOT Hubble plane. |

**Shodan pass conclusion:** Shodan sees the HTTP-UI tier (Hubble UI 22, Kiali 140, Linkerd viz 5) + cert-leaked cluster tier (~10 K8s apiservers). It is BLIND to every introspection plane on high ports (Envoy admin 15000, Linkerd 4191, Cilium metrics 9962/9965 all = 0). That dark tier is the Censys/tiptoe-naabu+grpcurl target and is where the crown-jewel unauth surfaces (Hubble Relay GetFlows, Envoy config_dump) live. Category materially needs Censys.

### Expanded variants (forwarded-set triage, 2026-05-31) — kept after FP/error filtering
| Dork | Hits | Notes |
|------|-----:|-------|
| `http.title:"Consul by HashiCorp"` | 1,111 | Adjacent (Secrets-Mgmt overlap). Consul ACL=allow-all default → catalog+KV often unauth. Cleaner than 1,830 noisy `consul` ledger hits. |
| `http.title:"Jaeger UI"` | 434 | No-auth-default tracing; internal call graph + span metadata. Mesh co-deploy. |
| `ssl:"istiod.istio-system.svc"` | 14 | Istio control-plane CA cert. Clean small set (istiod rarely public; forwarded note's 'high FP' wrong). |
| `port:15021 "envoy"` | 68 | Envoy INGRESS-gateway status port. Reachable (public ingress) UNLIKE sidecar admin 15000 (=0). |
| `port:8081 http.title:"Cilium"` | 0 | CUT: no Cilium-titled UI on 8081 (it's Hubble-UI backend). Forwarded note wrong. |
| `port:6443 ssl.cert.subject.cn:"cilium.io"` | 3 | Precise Cilium cluster cert pivot (broader hubble-grpc SAN reached ~10). |

**Forwarded-set triage result:** ran 6 of ~25; cut istiod-15010 http.html (gRPC), regex http.html (unsupported), Falco/Tetragon (no default UI), Prometheus 9090 (own category/too broad), and footprint/FP rows. Best forwarded catch = 15021 (ingress status reachable where admin is dark).

## Service Mesh data-plane tier (pivot 1, 2026-05-31, authenticated Shodan UI via Playwright)

| Query | Hits | Note |
|-------|------|------|
| `port:15000 "config_dump"` | 0 | Envoy sidecar admin. Shodan-dark: crawler never GETs /config_dump. |
| `port:15014 "pilot_xds"` | 0 | istiod debug metrics. Shodan-dark. |
| `port:15010 "cluster.local"` | 0 | istiod plaintext xDS. Shodan-dark. |
| `port:4191 "proxy_build_info"` | 0 | Linkerd proxy-admin /metrics. Shodan-dark. |
| `port:4191 "linkerd"` | 0 | Linkerd proxy-admin. Shodan-dark. |
| `"hubble_flows_processed_total"` | 0 | Cilium Hubble metric. Shodan-dark. |
| `"cilium_drop_count_total"` | 0 | Cilium metric. Shodan-dark. |
| `ssl:"identity.linkerd.cluster.local"` | 0 | Linkerd identity issuer cert (self-signed, not in CT/Shodan). |
| `port:4245` | 30 | Hubble Relay port BUT shared + gRPC-opaque to Shodan. grpcurl: 0 reflection-enabled relays (1 reflection-off candidate 103.86.177.103, residual blind spot). |
| `http.title:"Kiali"` | hits | Console tier (Shodan-visible). 10 harvested prior, 4 anon-confirmed. |
| `http.title:"Hubble UI"` | hits | Console tier (Shodan-visible). 9 confirmed exposed. |

**Result:** every DATA-PLANE marker dork = 0 (Shodan-dark); console TITLE dorks return populations. Empirical proof of Insight #71 corollary (Shodan indexes the console tier, blind to the data-plane tier). Data-plane tier needs Censys full-range / tiptoe/naabu.


## 2026-05-31 — Classical ML & Auxiliary Model Services (Cat-31)

Intel: data/platform-intel/classical-ml-osint-2026-05-31.md · Catalog: shodan/queries/31-classical-ml.md

| Query | Hits | Note |
|-------|------|------|
| `http.title:"Gorse Dashboard"` | 34 | Recommender dashboard at `/`. Vendor-unique, ~0 FP. US 11/CN 9/DE 3/SG 3. Ports 443,80,18088,8087,7088. The ONLY Shodan-visible population in the category. |
| `port:8087 http.html:"/api/health/live"` | 0 | Gorse server REST tier. Path not in default-crawl banner -> aimap active-probe on the 34 dashboard hosts. |
| `http.html:"coverage" http.html:"documents" http.html:"degraded" port:8080` | 0 | Vespa query-node. coverage JSON lives on /search/?yql=, Shodan crawls /. -> aimap active-probe. |
| `http.html:"Could not find any versions of model"` | 0 | TF-Serving 404 body. Not served on /. -> aimap active-probe on :8501. |
| `port:8000 http.html:"models" "django"` | 0 | django-river-ml DRF. Rare RSE pkg; near-0 expected. -> aimap. |
| `http.html:"schema/feature-store"` | 0 | Solr-LTR managed resource. Not on Solr admin root. -> aimap extension on existing Solr fp. |
| `http.html:".ltrstore"` | 0 | ES-LTR hidden index. Appears in _cat/indices, not /. -> aimap extension on ES. |
| `"yente" "motiva" port:8080` | 0 | Marble co-deploy signature. Young commercial product, low public pop; auth-on by default anyway (positive control). |

Dorks NOT run (reason): #2 Gorse title+FA-pin (subset of the 34); #5 Vespa /document/v1+pathId, #6 TF model_version_status, #10 Solr ManagedFeatureStore, #12 ES _ltr+featureset, #13 Cornac remove_seen (all query-path JSON signals, same /-crawl mechanism as the 0s above); #15 VW port:26542 (Shodan-dark by design, seed-only generic port).

**Result:** 1/8 dorks productive (Gorse 34). The category is **port-first / active-probe, not brand-dork** — every API-body/JSON-key signal returned 0 because Shodan crawls `/` and these platforms emit their vendor-unique strings only on API query paths (/search, /v1/models, /_ltr, /schema/feature-store). Empirical re-confirmation of Insight #21 for the classical-ML class. Only Gorse (dashboard rendered at `/`) is passively visible; the other 8 fingerprintable platforms are productized as aimap fingerprints for a port-first sweep.

## Cat-31 Data Labeling (Extended) — 2026-06-01 (Shodan API, Freelance tier)

| Dork | Hits | Note |
|---|---|---|
| `port:9200 http.html:"argilla"` | 1 | Argilla ES backend leaked — CRITICAL (unauth ES = corpus R/W + training-data poisoning) |
| `http.title:"Argilla"` | 46 | Argilla front-ends |
| `http.title:"CVAT"` | 7 | CVAT (title-confirmed) |
| `http.html:"cvat"` | 494 | broad substring — FP-prone (see reference_aimap_cvat_iap_fp); sampled 100 |
| `port:8080 http.html:"prodigy"` | 2 | Prodigy — no built-in auth |
| `http.html:"diffgram"` | 3 | Diffgram |
| `http.title:"Label Studio"` | 1642 | highest-CVE-density product; sampled 100 |

Lessons (0-hit / tooling):
- `port:8075 http.html:"nuclio"` = 0 and `port:8070 http.html:"nuclio"` = 0 — no CVAT Nuclio mgmt API internet-mapped with that marker (either good hygiene or not crawled on that signal). The Nuclio RCE plane is the brief's top concern; absence here is a result, not a miss — verify per-host via aimap on CVAT instances.
- `http.html:"labelbox"` — jaxen hunt parse bug: `math/big: cannot unmarshal "3.73e+28" into *big.Int` (go-shodan field in scientific notation). Population unharvested pending a jaxen fix.

Harvest: 237 unique IPs -> /tmp/shodan-cat31-hits.txt; empire.db 256 assets / 243 with index favicon.

## 2026-06-01 | manager360.pro deep dive

| Query | Hits | Notes |
|-------|------|-------|
| `ip:158.160.80.95` | 1 | Neurofit360 host, Lunary health endpoint |
| CT log: manager360.pro | 44 domains | VisorGraph pivot |
| cert CN: manager360.sport.vpa.group | confirms VPA Group operator |

## 2026-06-03 — Vector Databases category survey (dogfood VisorCAS Stage 1d)
_count endpoint (free), vendor-unique-JSON dorks. 0 = result._

| vendor | dork | total |
|---|---|---|
| qdrant | `"qdrant - vector search engine"` | 13 |
| chromadb | `"nanosecond heartbeat"` | 0 |
| weaviate | `"x-weaviate"` | 897 |
| meilisearch | `"X-Meilisearch"` | 25 |
| milvus | `port:19530 "milvus"` | 0 |
| typesense | `"x-typesense"` | 194 |
| qdrant6333 | `port:6333 "qdrant"` | 0 |
| qdrant-prod | `product:Qdrant` | 0 |
| qdrant-bare | `"qdrant"` | 162 |
| qdrant-coll | `"result":{"collections"` | 3 |
| chroma-bare | `"chromadb"` | 36 |
| chroma-v2 | `"/api/v2/heartbeat"` | 0 |
| chroma-tenant | `"default_tenant"` | 169 |
| milvus-bare | `"milvus"` | 1460 |
| milvus-attu | `http.title:"Attu"` | 1243 |
| milvus-9091 | `port:9091 "milvus"` | 136 |

## 2026-06-04 — Specialty Data Layers (scanner-in-chain methodology test)
| vendor | dork | total |
|---|---|---|
| elastic | `"You Know, for Search"` | 5426 |
| elastic9200 | `port:9200 "cluster_uuid"` | 5 |
| clickhouse | `"X-ClickHouse-Summary"` | 115200 |
| clickhouse2 | `port:8123 "Ok."` | 120879 |
| pinot | `http.title:"Pinot Controller"` | 0 |
| druid | `"druid/coordinator-overlord"` | 0 |
| scylla | `port:10000 "scylla"` | 0 |
| starrocks | `http.title:"StarRocks"` | 76 |

## 2026-06-04 — Data Labeling / Annotation (dogfood run 3)
| vendor | dork | total |
|---|---|---|
| doccano | `http.title:"doccano"` | 163 |
| labelstudio | `http.title:"Label Studio"` | 1640 |
| labelstudio2 | `"X-Label-Studio"` | 0 |
| cvat | `http.title:"CVAT"` | 6 |
| cvat2 | `"/api/server/about"` | 0 |
| argilla | `http.title:"Argilla"` | 49 |
| prodigy | `http.title:"Prodigy"` | 131 |

## 2026-06-04 Cat-01 LLM Orchestration niche slice (VisorCAS dogfood run #4)
| Dork | Shodan available | Harvested (post --clean) | Note |
|---|---|---|---|
| `product:"Flowise"` | 502 | 70 | 30 CDN dropped |
| `http.title:"Langflow"` | 96070 (!) | 16 | title tokenized, 100x vs catalog 844; 64/80 CDN |
| `"AnythingLLM" port:3001` | 240 | 58 | clean |
| `"LocalAI" port:8080` | 80 | 49 | clean |

## 2026-06-04 Cat-03 Model Serving niche slice (VisorCAS dogfood run #5)
| Dork | Harvested | Note |
|---|---|---|
| "sglang" | 35 | clean |
| "lmdeploy" | 3 | clean |
| "Triton Inference Server" | 8 | of 47 avail |
| "koboldcpp" port:5001 | 38 | clean |
| "vLLM" | 80 | JAXEN big.Int bug -> python shodan fallback |
| "Seldon" | 40 | JAXEN big.Int bug -> python shodan fallback |

**Cat-03 honeypot domination (2026-06-04):** full-corpus Shodan-tag enrichment of
180 model-serving IPs = 21 honeypot-tagged. Honeypot share of aimap findings:
MCP 10/10, SGLang 15/17, Ollama 14/16, Docker Registry 0/39. 30/34 "critical"
were bait. Real population = 28 anonymous Docker registries (/v2/_catalog + AI/ML
images). vLLM/Seldon dorks honeypot/Docker-collision polluted (~0 real). JAXEN
big.Int bug on vLLM/Seldon -> python-shodan fallback.

## 2026-06-04 Cat-04 Training/Experiments niche slice (VisorCAS dogfood run #6)
MLflow(title) 9, mlflow(html) +N, clearml 28, Determined 30, ray dashboard 6, wandb 19, Kubeflow +N.
JAXEN big.Int fix worked - no crashes. MLflow title 38695 / ray 87331 available = tokenized.

**Cat-04 honeypot domination (2026-06-04):** 116 IPs, 43 honeypot-tagged (37%, densest yet). 42/42 critical = bait. MCP 132/132, Ray Dashboard 28/28 (ShadowRay bait), ClickHouse 7/7 honeypot. ClearML 0/24 = real population (auth-unverified, aimap has no ClearML auth-probe). Honeypot tarpitting -> 49min scan (4x clean). JAXEN big.Int fix held (no crashes). 3rd category confirming honeypot-dominated inference/famous-CVE tier.

## Cat-01 LLM Orchestration — virgin re-birth harvest (2026-06-04)

Tier: Freelance (9,878 query credits). Harvest = shodan download (full pop) + API facet triage.

| Dork | total avail | pulled (uniq IP) | http.status note |
|---|---|---|---|
| `product:"Flowise"` | 505 | 439 | 503/505 = 200 (auth-off) |
| `http.html:"langflow"` | 96,080 | 152 (sample) | TITLE-FARM: title:"Langflow"=96,005, 0/16 real (FP) |
| `port:7860 http.html:"langflow"` | 4 | 4 | real Langflow tail |
| `http.title:"LibreChat"` | 3,142 | 2,379 | 3140=200; port 3080=566; org V tal(BR)=413 |
| `http.title:"LobeChat"` | 682 | 496 | 660=200, 19=401 (Mode-A open) |
| `http.title:"big-AGI"` | 18 | 15 | full pop |
| `http.title:"FastGPT"` | 21 | 16 | full pop |
| `http.title:"Coze Studio"` | 267 | 246 | all 200; port 8888=177; Alibaba cluster |
| `http.html:"dataelement"` (BISHENG) | 33 | 29 | full pop |
| `http.html:"chainlit-cloud.s3.eu-west-3.amazonaws.com"` | 1,004 | 855 | og:image marker, low-FP |
| `port:1865` (Cheshire Cat) | 297 | 292 | NOISY: only 7/297=200, needs marker |
| `port:42110` (Khoj) | 505 | 490 | NOISY: only 14/505=200, needs marker |
| `port:1337 "/v1/models"` (Jan) | 2 | 2 | UNMAPPABLE: port owned by Strapi/OpenSSH |
| `http.html:"h2oGPT"` | 1 | 1 | full pop |
| `http.html:"/rest/login"` (n8n) | 210 | 192 | 206=200; tight vs 173k title-token bleed |
| `http.title:"Clawdbot Control"` (OpenClaw) | 1,113 | 576 | all 200; port 18789=745; Alibaba/DO |

Corpus: 6,064 unique IPs / 7,319 ip:port → ~/recon/01-llm-orchestration-2026-06-04/
Zero-result corrections: `port:18789 "Clawdbot Control"`=0 (use http.title); `"langflow_version"`=0 (API body unindexed); `port:42110 "khoj"`=0 (use port alone + marker).

## 2026-06-04 Cat-02 Vector DB virgin re-birth (MCP Playwright web-UI harvest, 0 credits)
| dork | hits | note |
|---|---|---|
| `http.html:"qdrant - vector search engine"` | 685 | VERY LOW FP, primary Qdrant |
| `http.html:"You Know, for Search" port:9200` | 7947 | ES (kNN substrate; v7 unauth tail) |
| `http.html:"opensearch.org" port:9200` | 924 | OpenSearch |
| `http.html:"RedisInsight" port:8001` | 179 | RedisInsight UI |
| `"com.yahoo.vespa"` (bare, NOT http.html) | 38 | http.html variant = 0; bare works |
| `http.html:"Welcome to Marqo"` | 7 | niche |
| `http.html:"weaviate" http.html:"modules"` | 6 | conjunctive may under-count; widen next |
| `http.html:"nanosecond heartbeat"` (Chroma) | 0 | + bare + port:8000 variants all 0 = SHODAN-WEB-DARK on Freelancer; route Censys |
| `"X-Meilisearch-Version"` / header | 0 | header dorks 0 on web UI; route Censys |
| `Server:"Typesense"` | 0 | header dork 0; route Censys |
| `"milvus_" port:9091` | 0 | gRPC/metrics Shodan-dark; route Censys/active 9091 |
| `"Manticore Search" port:9308` | 0 | route Censys/active |
| `product:"Qdrant"` | 0 | product: filter empty on Freelancer; use http.html title |

## 2026-06-05 Cat-02 wave-2 wide dork sweep (MCP Playwright, 0 credits)
| dork | hits | note |
|---|---|---|
| `port:23820` | 441 | Infinity/InfiniFlow vector DB |
| `"surrealdb" port:8000` | 232 | SurrealDB |
| `http.title:"Neo4j Browser" port:7474` | 6475 | Neo4j |
| `port:8123 "Ok."` | 120016 | ClickHouse+MyScale (MyScale = subset, needs MSTG discriminator) |
| `port:27017 "MongoDB"` | 78482 | MongoDB |
| `http.title:"Supabase"` | 912 | Supabase self-hosted |
| `port:8091 "couchbase"` | 292 | Couchbase |
| `http.title:"YugabyteDB"` | 237 | YugabyteDB |
| `port:8081 "jina"` | 27 | Jina |
| `port:8000 "databend"` | 21 | Databend |
| `http.title:"Greenplum Command Center"` | 7 | Greenplum CC |
| `port:8888 "statusCode"` | 1 | Epsilla (anchor weak, variant needed) |
| `port:9042 "Cassandra"` | 1 | anchor weak; CQL banner lacks string; variant needed |
| `port:8817 "vearch"` | 0 | variant needed (banner lacks "vearch") |
| `port:8081 "vectorVamana"` | 0 | SemaDB variant needed |
| `port:4000 "greptime"` | 0 | GreptimeDB variant needed |
| `port:2881 "OceanBase"` | 0 | variant needed |
| `port:8983 "Apache Solr"` | 0 | SUSPICIOUS (Solr large); variant needed |
| `port:9042 "SCYLLA_SHARD_AWARE"` | 0 | variant needed |
| `port:3000 "Aerospike"` | 0 | variant needed |
| `port:10080 "git_hash"` | 0 | TiDB variant needed |
| `product:"Hasura GraphQL Engine"` | 0 | product: filter empty; variant needed |
| `port:5000 "kdb"` | CF | Cloudflare tripped; not measured |
| `product:"SingleStore"` | - | not run (after CF) |

### 2026-06-05 variant pass on the zeros
| variant dork | hits | resolves |
|---|---|---|
| `"kdb+"` | 846 | KDB.ai/kdb+ CONFIRMED (was 0 on `port:5000 "kdb"`) |
| `"Solr Admin"` | 64 | Solr web UI (was 0 on `"Apache Solr"`; `port:8983` total=360) |
| `"x-hasura"` | 15 | Hasura (was 0 on `product:`) |
| `"GreptimeDB"` | 2 | GreptimeDB tiny-but-real (was 0 on `"greptime"`) |
| `port:8817` | 61379 | NOT Vearch — port noise; `"vearch"` bare=0 (port count != platform count) |
| `"vearch"` `"oceanbase" port:2881` `"Scylla" port:9042` `"aerospike" port:3000` | 0 | still dark → Censys/API filter |
| `port:10080 "tidb"` `"SingleStore" port:3306` `port:8081 "SemaDB"` `port:9042 product:Cassandra` | 0 | still dark → Censys/API filter |

NOTE: web-UI  filter returns 0 on Freelancer (Cassandra/Scylla undercount); CQL-binary
services need the API product: filter or Censys. Cassandra/Scylla NOT absent (prior Scylla host confirmed).
NOTE: web-UI product: filter returns 0 on Freelancer (Cassandra/Scylla undercount). CQL-binary services need the API product: filter or Censys. Cassandra/Scylla NOT absent (prior Scylla host confirmed in wave-2 Lane B / nyovenn case).

### 2026-06-05 API harvest (Freelance key) — move1 paginate + move2/3 FREE count+facet
MOVE 1 dedicated tier harvested (13 query credits): 1594 unique IPs -> recon/.../ips-dedicated.txt
  qdrant 644 (of 678) | infinity 441 | surrealdb 232 | redisinsight 177 | vespa 39 | jina 27 | databend 21 | marqo 7 | weaviate 6

MOVE 3 giant-population facets (FREE /shodan/host/count) — FP CAUGHT:
  ClickHouse: port:8123 "Ok." = 120028 BUT product facet = Home Assistant 83569 / ClickHouse only 11070.
    => the "Ok." dork is ~90% Home Assistant FP. REAL ClickHouse ~= 11070, NOT 120k. (Insight #15 lesson, automated.)
  MongoDB: 163601 (product:MongoDB clean) | Neo4j: 6475 raw, 4882 real (Neo4j Browser product).

MOVE 2 dark-vendor port queries REFUTED via product facet (port != platform):
  port:9042 (Cassandra) 394082 = nginx/Socks4A/OpenSSH (no Cassandra in top products)
  port:3000 (Aerospike) 1365442 = nginx/Grafana/webOS | port:4000 (TiDB) 767465 = nginx/printers
  port:8817 (Vearch) 61380 = OpenSSH/Socks4A (confirms NOT-Vearch) | product:Scylla=0 | SingleStore=0 | SemaDB=0
  => dark vendors NOT Shodan-findable; route to Censys. The facet=product count is a FREE 1-call FP detector.

## 2026-06-05 — aimap functional test targets

| Query | Hits | Notes |
|-------|------|-------|
| `port:6333 http.html:"qdrant"` | 16 | basic tier |
| `product:Ollama port:11434` | 17,513 | basic tier |
| `product:Weaviate port:8080` | 286 | basic tier |

## 2026-06-05 — Cat-03 Model Serving harvest (API key active)

| Query | Hits | Harvested |
|-------|------|-----------|
| `"SillyTavern"` | 8,904 | 991 |
| `"llama.cpp"` | 1,467 | 928 |
| `http.html:"/v1/chat/completions"` | 7,271 | 890 |
| `http.title:"Whisper"` | 479 | 448 |
| `http.html:"TEI"` | 263 | 240 |
| `http.html:"faster-whisper"` | 228 | 217 |
| `"vLLM"` | 337 | 309 |
| `http.html:"lm studio"` | 125 | 117 |
| `port:1234 "model"` | 69 | 66 |
| `"koboldcpp"` | 43 | 40 |
| `"Triton Inference Server"` | 53 | 34 |
| `"sglang"` | 37 | 28 |
| `"koboldai"` | 21 | 21 |
| `http.html:"nvidia nim"` | 18 | 17 |
| `"lmdeploy"` | 3 | 3 |
| `"Aphrodite Engine"` | 0 | 0 |
| `"GPT4All"` | 0 | 0 |

**Total deduplicated IPs: 4,284**
**Notes:** Aphrodite Engine and GPT4All Shodan-dark (0 results). Confirmed still valid: use aimap/direct probing on known ports 2242/4891.

## 2026-06-05 — Cat-03 Censys harvest (org key, 351 credits)

| Query | IPs harvested |
|-------|--------------|
| `host.services.banner: "SillyTavern"` | 500 |
| `host.services.banner: "llama.cpp"` | 500 |
| `host.services.banner: "vLLM"` | 23 |
| `host.services.banner: "sglang"` | 2 |

**Credits used: ~348/351** (charges per host returned, not per page)
**3 credits remaining** (expires 2027-06-04) -- save for verification probes
**Combined Shodan+Censys corpus: 5,018 unique IPs**
| 2026-06-05 | `http.title:"Unsloth Studio"` | 54 | cat-04-training | Unsloth Studio daemon; Python/Uvicorn :8888 |
| 2026-06-05 | `http.html:"unsloth"` | 71 | cat-04-training | broader; FP tail = H2O LLM Studio (llmstudio.h2o.dev) |
| 2026-06-05 | `http.html:"Determined Deep Learning Training Platform"` | 5 | cat-04-training | real Determined (title dork=56 FP-prone); 2x AWS GovCloud |
| 2026-06-05 | `http.title:"Determined"` | 56 | cat-04-training | FP-prone generic word; tightened by meta-string variant |
| 2026-06-05 | `http.html:"openllm"` | 7 | cat-04-training | OpenLLM :3000; openllm-france.chat, aitokenhub.io |
| 2026-06-05 | `http.html:"llama-factory"` | 9 | cat-04-training | VARIANT REVIVED IT: title:"LLaMA Factory"=0; China/Aliyun training UIs |
| 2026-06-05 | `http.title:"LLaMA Factory"` | 0 | cat-04-training | title dork dead; html variant found 9 (verify-before-stop) |
| 2026-06-05 | `http.html:"lightning.ai"` | 2 | cat-04-training | both = lightning.ai vendor infra, NOT self-hosted -> logged-negative |
| 2026-06-05 | `port:6566` | 288 | cat-04-training | Feast Shodan-dark: cards are noise (Win/PHP/Fly.io); needs aimap active-probe |
| 2026-06-05 | `"feast" "feature"` | 1 | cat-04-training | noise-collapsed (brand word useless) |

## 2026-06-06 — Cat-05 AI Gateways / Observability

| Date | Dork | Hits | Category | Notes |
|------|------|------|----------|-------|
| 2026-06-06 | `http.title:"LiteLLM" port:4000` | 2219 | cat-05-gateways | Primary LiteLLM dork; 500+500 IPs downloaded; ~40% live; ~5-10 CRIT open-key instances in sampled population |
| 2026-06-06 | `port:8001 http.title:"Kong"` | 178 | cat-05-gateways | Kong Admin API; content-based dork `"tagline" "Welcome to kong"` = 0; title variant works |
| 2026-06-06 | `"Langfuse" port:3000` | 1141 | cat-05-gateways | 25/25 checked = signUpDisabled:false; ASU + GCP + Safespring notable |
| 2026-06-06 | `port:6006 "phoenix"` | 91 | cat-05-gateways | Arize Phoenix; 5/5 live; Northeastern Essaybot project |
| 2026-06-06 | `"AI Gateway says hey" port:8787` | 0 | cat-05-gateways | Portkey Shodan-dark |
| 2026-06-06 | `port:9998 "Apache Tika"` | 0 | cat-05-gateways | Tika Shodan-dark (both variants) |
| 2026-06-06 | `"tagline" "Welcome to kong" port:8001` | 0 | cat-05-gateways | Kong content-body dork dark; use title variant |

## 2026-06-06 — LiteLLM Favicon Hash Sweep
- **Query:** `http.favicon.hash:-1875761561`
- **Total hits:** 4,008
- **Sample:** 988 unique IPs (10 pages)
- **Trigger:** Insight #78 — shared deployment kit population selector
- **Notes:** Standard LiteLLM Swagger UI favicon; full global LiteLLM proxy population. US 42%, DE 13%, CN 10%. 17 universities. YipitLLM (5), Cloudeka (1) branded. Kit-specific subset requires version+callback+no-Prisma-DB overlay.
