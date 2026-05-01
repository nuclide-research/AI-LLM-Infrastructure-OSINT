# University AI Infrastructure Exposures

_NuClide Research — ongoing · Updated 2026-05-01_

Unauthenticated Ollama and Open WebUI instances discovered on university networks. Organized by country / state.

## Naming Convention

Files: `<CC>-<STATE>-<org-slug>.md`  
Example: `US-CA-ucsb.md` = United States, California, UC Santa Barbara

---

## Confirmed Findings

| File | Institution | Country/State | Severity | Key Finding |
|------|-------------|---------------|----------|-------------|
| [US-NY-columbia.md](US-NY-columbia.md) | Columbia University | US · NY | CRITICAL | Cloud proxy (deepseek-v4-pro) + cred leak (username: seascvn066) |
| [US-CA-ucsb.md](US-CA-ucsb.md) | UC Santa Barbara | US · CA | CRITICAL | Auth **disabled**, open inference, "AI Lab", macOS user `marcos` leaked |
| [US-NY-suny-buffalo.md](US-NY-suny-buffalo.md) | SUNY Buffalo | US · NY | CRITICAL | Cloud proxy **200 OK** confirmed, 26 models, RAG pipeline components |
| [US-NC-duke.md](US-NC-duke.md) | Duke University | US · NC | HIGH | Agent model with file inspection tools, function-calling, injection surface |
| [US-IN-purdue-northwest.md](US-IN-purdue-northwest.md) | Purdue University Northwest | US · IN | CRITICAL | **3 cloud proxies live (200 OK)**: qwen3-coder-next, gemma4:31b, gpt-oss:20b |
| [JP-Keio.md](JP-Keio.md) | Keio University | Japan | HIGH | Dual DeepSeek cloud proxy, qwen3.5:122b (75GB) accessible without auth |
| [TH-Chulalongkorn.md](TH-Chulalongkorn.md) | Chulalongkorn University | Thailand | HIGH | 3 cloud proxies (DeepSeek, Kimi K2.6, Qwen), cred leak (user: llm) |
| [KR-POSTECH.md](KR-POSTECH.md) | POSTECH | South Korea | CRITICAL | **18 cloud subscriptions** incl. Kimi 1T-param, DeepSeek 671B, Qwen 480B |
| [IN-shiv-nadar.md](IN-shiv-nadar.md) | Shiv Nadar University | India | CRITICAL | 3-node cluster, 376GB local DeepSeek, 18 cloud subscriptions |
| [VN-hanoi.md](VN-hanoi.md) | Hanoi University | Vietnam | HIGH | 18 cloud proxies, cred leak — Docker container ID leaked as username |
| [SE-KTH.md](SE-KTH.md) | KTH Royal Institute of Technology | Sweden | HIGH | Dual-node DeepSeek cloud, abliterated Gemma running as root |
| [GR-tech-crete-ntua.md](GR-tech-crete-ntua.md) | Tech Univ. Crete + NTUA | Greece | HIGH | TechCrete: MiniMax cred leak (user: arian); NTUA: 235.7B model open |
| [CA-ON-western-ontario.md](CA-ON-western-ontario.md) | University of Western Ontario | Canada · ON | HIGH | Cloud proxy (deepseek-v4-pro), 9 models including vision-language |
| [US-NY-rit.md](US-NY-rit.md) | Rochester Institute of Technology | US · NY | CRITICAL | 4 nodes: DGX w/ 18 cloud subs, student machine w/ 2 abliterated QwQ-32B |
| [AU-newcastle.md](AU-newcastle.md) | University of Newcastle | Australia | HIGH | DeepSeek cloud proxy, RAG pipeline (mxbai-embed) |
| [AM-armenian-academy.md](AM-armenian-academy.md) | IIAP NAS Armenia | Armenia | HIGH | Dual cloud proxy, Docker container ID cred leak |
| [KE-JKUAT.md](KE-JKUAT.md) | Jomo Kenyatta University | Kenya | HIGH | Cloud proxy (minimax-m2.7), unauthenticated inference |
| [SK-zilina.md](SK-zilina.md) | University of Žilina | Slovakia | CRITICAL | Student laptop, **3 free-tier cloud proxies 200 OK**: devstral-2:123b, deepseek-v3.1:671b, qwen3-coder:480b |
| [CZ-brno-vutbr.md](CZ-brno-vutbr.md) | Brno University of Technology | Czech Republic | HIGH | Abliterated Gemma3-27B, Bulgarian GPT, RAG pipeline |
| [GB-hertfordshire.md](GB-hertfordshire.md) | University of Hertfordshire | UK | CRITICAL | RobotHouse dev server, gpt-oss:latest **200 OK confirmed** |
| [RU-itmo.md](RU-itmo.md) | ITMO University | Russia | HIGH | 24 models incl. Kimi-Dev-72B, Llama4, gpt-oss:20b/120b |
| [VN-vnu-hanoi.md](VN-vnu-hanoi.md) | VNU Ha Noi | Vietnam | HIGH | Domain-specific models: legal, biomedical, financial QA |
| [VN-vnu-hcmc.md](VN-vnu-hcmc.md) | VNU Ho Chi Minh City | Vietnam | HIGH | final-exploit-v1 cloud proxy, gpt-oss |
| [CA-MB-u-manitoba.md](CA-MB-u-manitoba.md) | University of Manitoba | Canada · MB | HIGH | CS GPU server, DeepSeek-R1:70B, Llama 3.3 |
| [SE-umea.md](SE-umea.md) | Umeå University | Sweden | HIGH | gpuhost02 CS cluster, qwen3.6:35b |
| [US-CA-ucdavis.md](US-CA-ucdavis.md) | UC Davis | US · CA | HIGH | 75GB MoE model, Claude 4.6 Opus-distilled model |
| [KR-yonsei.md](KR-yonsei.md) | Yonsei University | South Korea | CRITICAL | 17 cloud subs on port 5004, minimax-m2.1 **200 OK**, 75GB + 65GB local models |
| [US-NY-syracuse.md](US-NY-syracuse.md) | Syracuse University | US · NY | CRITICAL | IST R640 server, gemma4:31b-cloud **200 OK** on port 12345 |
| [US-NY-suny-stony-brook.md](US-NY-suny-stony-brook.md) | SUNY Stony Brook | US · NY | HIGH | Biology dept, OLMo-3 research stack, gpt-oss cloud proxy |
| [GR-u-crete-medical.md](GR-u-crete-medical.md) | University of Crete Medical Center | Greece | HIGH | Dual-embedding RAG pipeline (mxbai + nomic-embed) on medical server |
| [CN-shandong-med.md](CN-shandong-med.md) | Shandong Medical Graduate School | China | CRITICAL | 376GB local DeepSeek, abliterated R1-Distill, cred leak (user: bowee) |
| [TW-ncku.md](TW-ncku.md) | National Cheng Kung University | Taiwan | HIGH | nckusoc-3090 cred leak, non-standard port 22222, 8 models |
| [TW-ncu-aiden.md](TW-ncu-aiden.md) | NCU / Oplentia (Chang Gung Univ.) | Taiwan | CRITICAL | Production medical scheduling SaaS (Aiden Assistant) system prompt fully exposed, support contacts, HIS integration |
| [TW-fju-medph.md](TW-fju-medph.md) | Fu Jen Catholic University | Taiwan | HIGH | Medical Public Health dept, 75GB MoE + 60GB gpt-oss:120b, RAG pipeline |
| [TW-ntu-gpu.md](TW-ntu-gpu.md) | National Taiwan University | Taiwan | HIGH | GPU cluster g1pc2n108, 11 vision/multimodal models (GLM-OCR, GLM-4.7, LLaVA, MiniCPM-V) |
| [KG-krena.md](KG-krena.md) | Kyrgyz Research and Education Network (KRENA) | Kyrgyzstan | HIGH | **433GB GLM-5.1 (744B-a40b) — largest local model in sweep**, deepseek-v4-pro cloud |
| [LK-learn.md](LK-learn.md) | Lanka Education and Research Network | Sri Lanka | HIGH | Cred leak (user: modelserver), deepseek-v4-pro cloud, llama3.2-vision |
| [TH-moph.md](TH-moph.md) | Thailand Ministry of Public Health | Thailand | HIGH | Government health ministry, qwen3.6:35b + IBM granite vision |
| [BR-cefet-rj.md](BR-cefet-rj.md) | CEFET/RJ (Federal Tech Education Center) | Brazil | HIGH | 17 models incl. DeepSeek-R1:70B, custom Brazilian Portuguese fine-tunes (chatbode, mistral-pt) |
| [EG-enstinet-nren.md](EG-enstinet-nren.md) | ENSTINET Egypt NREN | Egypt | HIGH | **Port 3005** (non-standard), 3 custom Arabic uncensored HauhauCS-35B models, RAG pipeline, CVE-2025-63389 **injection + deletion confirmed** |
| [PL-lodz-tul.md](PL-lodz-tul.md) | Technical University of Łódź | Poland | HIGH | xray02 research node, DeepSeek-R1:32B, `lukashabtoch/plutotext-r3-emotional` cross-network propagation with CEFET/RJ Brazil |
| [PK-comsats.md](PK-comsats.md) | COMSATS University | Pakistan | HIGH | MedGemma 27B medical AI + 4B medical AI exposed, Kimi cloud proxy |
| [US-VA-vt.md](US-VA-vt.md) | Virginia Tech | US · VA | LOW | DHCP workstation (h80adf308), 5 models, no cloud proxy |
| [KR-snu.md](KR-snu.md) | Seoul National University | South Korea | CRITICAL | Cloud proxies (devstral-2:123b, deepseek-v3.1:671b) + **cred leak** (user: node1, SSH pubkey) |
| [KR-inha.md](KR-inha.md) | INHA University | South Korea | HIGH | gpt-oss:20b local, dual Nemotron-Cascade 30B, 132GB total |
| [AU-monash.md](AU-monash.md) | Monash University | Australia | HIGH | **404.5GB DeepSeek V3.1 671B** (tied largest in sweep), 51.7GB coder, Kimi + MiniMax cloud proxies |
| CA-AB-u-alberta | University of Alberta | Canada · AB | HIGH | `lula.cs.ualberta.ca`, gpt-oss:120b (65.4GB, 116.8B params), Qwen3.6 35B/27B |

---

## Discovery Queries (Shodan)

```
# University Ollama instances
http.html:"Ollama is running" org:"university"   → 225 results (2026-05-01)

# University Open WebUI instances  
http.html:"Open WebUI" port:3000 org:"university" → 84 results (2026-05-01)
```

Cross-referencing same-IP hits across both queries identifies confirmed auth-bypass hosts (Open WebUI auth + raw Ollama port on same machine).

---

## Methodology

1. Pull Shodan hits for university-attributed IPs
2. Cross-reference Ollama (11434) and Open WebUI (3000) on same IP
3. Probe `/api/config` for `auth: false`
4. Probe `/api/tags` on port 11434 for model inventory + cloud proxy models
5. Check `/api/show` for system prompts on all models
6. Cloud proxy: attempt inference → 401 response exposes Ollama Connect creds

---

## Scale (sampled 2026-05-01)

| Query | Count |
|-------|-------|
| University Ollama (port 11434) | 225 |
| University Open WebUI (port 3000) | 84 |
| Auth disabled (Open WebUI) | ~5–10% of Open WebUI set |
| Raw Ollama open (no Open WebUI auth) | ~30–40% of co-deployed |
| Cloud proxy models in university set | ~10–15% of open Ollama |
