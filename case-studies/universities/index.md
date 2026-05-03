# University AI Infrastructure Exposures

_NuClide Research — ongoing · Updated 2026-05-02_

Unauthenticated Ollama and Open WebUI instances discovered on university networks. Organized by country / state.

## Structure

- `US/` — United States, organized by state prefix (e.g. `NY-columbia.md`)
- `international/CC/` — all other countries, grouped by ISO country code

---

## Confirmed Findings

| File | Institution | Country/State | Severity | Key Finding |
|------|-------------|---------------|----------|-------------|
| [NY-columbia.md](US/NY-columbia.md) | Columbia University | US · NY | CRITICAL | Cloud proxy (deepseek-v4-pro) + cred leak (username: seascvn066) |
| [CA-ucsb.md](US/CA-ucsb.md) | UC Santa Barbara | US · CA | CRITICAL | Auth **disabled**, open inference, "AI Lab", macOS user `marcos` leaked |
| [NY-suny-buffalo.md](US/NY-suny-buffalo.md) | SUNY Buffalo | US · NY | CRITICAL | Cloud proxy **200 OK** confirmed, 26 models, RAG pipeline components |
| [NC-duke.md](US/NC-duke.md) | Duke University | US · NC | HIGH | Agent model with file inspection tools, function-calling, injection surface |
| [IN-purdue-northwest.md](US/IN-purdue-northwest.md) | Purdue University Northwest | US · IN | CRITICAL | **3 cloud proxies live (200 OK)**: qwen3-coder-next, gemma4:31b, gpt-oss:20b |
| [Keio.md](international/JP/Keio.md) | Keio University | Japan | HIGH | Dual DeepSeek cloud proxy, qwen3.5:122b (75GB) accessible without auth |
| [Chulalongkorn.md](international/TH/Chulalongkorn.md) | Chulalongkorn University | Thailand | HIGH | 3 cloud proxies (DeepSeek, Kimi K2.6, Qwen), cred leak (user: llm) |
| [POSTECH.md](international/KR/POSTECH.md) | POSTECH | South Korea | CRITICAL | **18 cloud subscriptions** incl. Kimi 1T-param, DeepSeek 671B, Qwen 480B |
| [shiv-nadar.md](international/IN/shiv-nadar.md) | Shiv Nadar University | India | CRITICAL | 3-node cluster, 376GB local DeepSeek, 18 cloud subscriptions |
| [hanoi.md](international/VN/hanoi.md) | Hanoi University | Vietnam | HIGH | 18 cloud proxies, cred leak — Docker container ID leaked as username |
| [KTH.md](international/SE/KTH.md) | KTH Royal Institute of Technology | Sweden | HIGH | Dual-node DeepSeek cloud, abliterated Gemma running as root |
| [tech-crete-ntua.md](international/GR/tech-crete-ntua.md) | Tech Univ. Crete + NTUA | Greece | HIGH | TechCrete: MiniMax cred leak (user: arian); NTUA: 235.7B model open |
| [ON-western-ontario.md](international/CA/ON-western-ontario.md) | University of Western Ontario | Canada · ON | HIGH | Cloud proxy (deepseek-v4-pro), 9 models including vision-language |
| [NY-rit.md](US/NY-rit.md) | Rochester Institute of Technology | US · NY | CRITICAL | 4 nodes: DGX w/ 18 cloud subs, student machine w/ 2 abliterated QwQ-32B |
| [newcastle.md](international/AU/newcastle.md) | University of Newcastle | Australia | HIGH | DeepSeek cloud proxy, RAG pipeline (mxbai-embed) |
| [armenian-academy.md](international/AM/armenian-academy.md) | IIAP NAS Armenia | Armenia | HIGH | Dual cloud proxy, Docker container ID cred leak |
| [JKUAT.md](international/KE/JKUAT.md) | Jomo Kenyatta University | Kenya | HIGH | Cloud proxy (minimax-m2.7), unauthenticated inference |
| [zilina.md](international/SK/zilina.md) | University of Žilina | Slovakia | CRITICAL | Student laptop, **3 free-tier cloud proxies 200 OK**: devstral-2:123b, deepseek-v3.1:671b, qwen3-coder:480b |
| [brno-vutbr.md](international/CZ/brno-vutbr.md) | Brno University of Technology | Czech Republic | HIGH | Abliterated Gemma3-27B, Bulgarian GPT, RAG pipeline |
| [hertfordshire.md](international/GB/hertfordshire.md) | University of Hertfordshire | UK | CRITICAL | RobotHouse dev server, gpt-oss:latest **200 OK confirmed** |
| [itmo.md](international/RU/itmo.md) | ITMO University | Russia | HIGH | 24 models incl. Kimi-Dev-72B, Llama4, gpt-oss:20b/120b |
| [vnu-hanoi.md](international/VN/vnu-hanoi.md) | VNU Ha Noi | Vietnam | HIGH | Domain-specific models: legal, biomedical, financial QA |
| [vnu-hcmc.md](international/VN/vnu-hcmc.md) | VNU Ho Chi Minh City | Vietnam | HIGH | final-exploit-v1 cloud proxy, gpt-oss |
| [MB-u-manitoba.md](international/CA/MB-u-manitoba.md) | University of Manitoba | Canada · MB | HIGH | CS GPU server, DeepSeek-R1:70B, Llama 3.3 |
| [umea.md](international/SE/umea.md) | Umeå University | Sweden | HIGH | gpuhost02 CS cluster, qwen3.6:35b |
| [CA-ucdavis.md](US/CA-ucdavis.md) | UC Davis | US · CA | HIGH | 75GB MoE model, Claude 4.6 Opus-distilled model |
| [yonsei.md](international/KR/yonsei.md) | Yonsei University | South Korea | CRITICAL | 17 cloud subs on port 5004, minimax-m2.1 **200 OK**, 75GB + 65GB local models |
| [NY-syracuse.md](US/NY-syracuse.md) | Syracuse University | US · NY | CRITICAL | IST R640 server, gemma4:31b-cloud **200 OK** on port 12345 |
| [NY-suny-stony-brook.md](US/NY-suny-stony-brook.md) | SUNY Stony Brook | US · NY | HIGH | Biology dept, OLMo-3 research stack, gpt-oss cloud proxy |
| [u-crete-medical.md](international/GR/u-crete-medical.md) | University of Crete Medical Center | Greece | HIGH | Dual-embedding RAG pipeline (mxbai + nomic-embed) on medical server |
| [shandong-med.md](international/CN/shandong-med.md) | Shandong Medical Graduate School | China | CRITICAL | 376GB local DeepSeek, abliterated R1-Distill, cred leak (user: bowee) |
| [ncku.md](international/TW/ncku.md) | National Cheng Kung University | Taiwan | HIGH | nckusoc-3090 cred leak, non-standard port 22222, 8 models |
| [ncu-aiden.md](international/TW/ncu-aiden.md) | NCU / Oplentia (Chang Gung Univ.) | Taiwan | CRITICAL | Production medical scheduling SaaS (Aiden Assistant) system prompt fully exposed, support contacts, HIS integration |
| [fju-medph.md](international/TW/fju-medph.md) | Fu Jen Catholic University | Taiwan | HIGH | Medical Public Health dept, 75GB MoE + 60GB gpt-oss:120b, RAG pipeline |
| [ntu-gpu.md](international/TW/ntu-gpu.md) | National Taiwan University | Taiwan | HIGH | GPU cluster g1pc2n108, 11 vision/multimodal models (GLM-OCR, GLM-4.7, LLaVA, MiniCPM-V) |
| [krena.md](international/KG/krena.md) | Kyrgyz Research and Education Network (KRENA) | Kyrgyzstan | HIGH | **433GB GLM-5.1 (744B-a40b) — largest local model in sweep**, deepseek-v4-pro cloud |
| [learn.md](international/LK/learn.md) | Lanka Education and Research Network | Sri Lanka | HIGH | Cred leak (user: modelserver), deepseek-v4-pro cloud, llama3.2-vision |
| [moph.md](international/TH/moph.md) | Thailand Ministry of Public Health | Thailand | HIGH | Government health ministry, qwen3.6:35b + IBM granite vision |
| [cefet-rj.md](international/BR/cefet-rj.md) | CEFET/RJ (Federal Tech Education Center) | Brazil | HIGH | 17 models incl. DeepSeek-R1:70B, custom Brazilian Portuguese fine-tunes (chatbode, mistral-pt) |
| [enstinet-nren.md](international/EG/enstinet-nren.md) | ENSTINET Egypt NREN | Egypt | HIGH | **Port 3005** (non-standard), 3 custom Arabic uncensored HauhauCS-35B models, RAG pipeline, CVE-2025-63389 **injection + deletion confirmed** |
| [lodz-tul.md](international/PL/lodz-tul.md) | Technical University of Łódź | Poland | HIGH | xray02 research node, DeepSeek-R1:32B, `lukashabtoch/plutotext-r3-emotional` cross-network propagation with CEFET/RJ Brazil |
| [comsats.md](international/PK/comsats.md) | COMSATS University | Pakistan | HIGH | MedGemma 27B medical AI + 4B medical AI exposed, Kimi cloud proxy |
| [VA-vt.md](US/VA-vt.md) | Virginia Tech | US · VA | LOW | DHCP workstation (h80adf308), 5 models, no cloud proxy |
| [snu.md](international/KR/snu.md) | Seoul National University | South Korea | CRITICAL | Cloud proxies (devstral-2:123b, deepseek-v3.1:671b) + **cred leak** (user: node1, SSH pubkey) |
| [inha.md](international/KR/inha.md) | INHA University | South Korea | HIGH | gpt-oss:20b local, dual Nemotron-Cascade 30B, 132GB total |
| [monash.md](international/AU/monash.md) | Monash University | Australia | HIGH | **3-node cluster**; 376.7GB DeepSeek V3.1 671B (OOM on current allocation); Kimi + MiniMax cloud proxies; v0.20.2/0.18.3/0.19.0 |
| CA-AB-u-alberta | University of Alberta | Canada · AB | HIGH | `lula.cs.ualberta.ca`, gpt-oss:120b (65.4GB, 116.8B params), Qwen3.6 35B/27B |
| [tanet.md](international/TW/tanet.md) | Taiwan Academic Network (TANet) | Taiwan | CRITICAL | 18-node multi-institution cluster, **account takeover** (name=ollama), 5G security system prompt, 4 cloud proxy nodes |
| [jingdong.md](international/CN/jingdong.md) | China Unicom / Jingdong Cluster | China | HIGH | 26-node uniform cluster v0.5.10, deepseek-r1:1.5b dominant, RAG pipeline |
| [kyungpook.md](international/KR/kyungpook.md) | Kyungpook National University | South Korea | HIGH | 3-node cluster 155.230.x, qwen3-vl:32b vision-language model |
| [ici-bucharest.md](international/RO/ici-bucharest.md) | ICI Bucharest (National IT Research Institute) | Romania | CRITICAL | 2 nodes: cloud proxy (DeepSeek + MiniMax), abliterated Qwen2.5-Coder, rdv-bot system prompt exposed, 72B model |
| [bdren.md](international/BD/bdren.md) | Bangladesh Research and Education Network (BDREN) | Bangladesh | HIGH | National NREN node, 7 models, unauthenticated inference |
| [CA-caltech.md](US/CA-caltech.md) | California Institute of Technology (Caltech) | US · CA | HIGH | `yertle.caltech.edu`, gpt-oss:120b (116B), dual-embedding RAG pipeline, custom syntax + java models |
| [arn.md](international/DZ/arn.md) | Algerian Academic Research Network (ARN) | Algeria | MEDIUM | National research network, v0.9.6 (unpatched), SmolLM2 with live system prompt |
| [onpt.md](international/MA/onpt.md) | Office National des Postes et Télécommunications (ONPT) | Morocco | MEDIUM | National PTT/telecom infrastructure node, v0.9.6, 1 model |
| [nib.md](international/IN/nib.md) | India NIB / BSNL National Backbone | India | HIGH | 2 nodes on national backbone (BSNL NIB), qwen2.5-coder:32b + deepseek-coder:6.7b coding cluster |
| [iti.md](international/GR/iti.md) | Informatics and Telematics Institute (ITI/CERTH) | Greece | HIGH | `vcl.iti.gr` Virtual Compute Lab, Mistral Small 24B, system prompt exposed |
| [moec.md](international/MY/moec.md) | Malaysia Ministry of Education EMISC | Malaysia | HIGH | Government education IT ministry, v0.9.6, unauthenticated inference |
| [university-of-indonesia.md](international/ID/university-of-indonesia.md) | University of Indonesia | Indonesia | CRITICAL | AS3382, Depok; llama3.2:3b; v0.5.4-dirty (pre-0.6.0 ancient build); Open WebUI v0.5.4 auth-on/3000 + raw API open/11434; CVE-2025-63389 confirmed |
| [tianjin-cloud-park.md](international/CN/tianjin-cloud-park.md) | China Telecom Tianjin Big Data Park | China | HIGH | AS141679; 46-node multi-tenant cluster; v0.5.10 uniform; RAG pipelines (nomic-embed + deepseek-r1:1.5b); aliafshar/gemma3-it-qat-tools:27b; no rDNS; research institute tenants |
| [IN-purdue.md](US/IN-purdue.md) | Purdue University (main campus) | US · IN | CRITICAL | `n8n.tap.purdue.edu` — n8n workflow automation server; v0.12.3; account takeover `d3af393f8e4e`; deepseek-v4-pro + minimax-m2.7 cloud; AI workflow hijack surface |
| [university-of-dhaka.md](international/BD/university-of-dhaka.md) | University of Dhaka | Bangladesh | CRITICAL | AS137359; coding cluster (codellama×2, qwen2.5-coder×2, deepseek-coder); bge-m3 embedding (RAG); 3 cloud proxies incl. qwen3-coder-next (unreleased); v0.20.5 |
| [ME-university-of-maine.md](US/ME-university-of-maine.md) | University of Maine (ECE-Ubuntu-02) | US · ME | CRITICAL | AS557 Orono; v0.18.2; **tripolskypetr/qwen3.5-uncensored-aggressive:122b (69GB)**; gpt-oss:120b; 18 cloud proxies incl. devstral-2:123b, deepseek-v4-flash, gemini-3-flash-preview |
| [CA-ucsd.md](US/CA-ucsd.md) | University of California, San Diego | US · CA | HIGH | AS26397; v0.20.7; qwen3.5:35b, gpt-oss:120b/20b; devstral-2:123b-cloud + deepseek-v3.1:671b-cloud; 67.58.51.111 |
| [nccu-taide.md](international/TW/nccu-taide.md) | National Chengchi University | Taiwan | CRITICAL | V100×4 GPU server; v0.11.6; **3× Taiwan national TAIDE models** (llama-3-taiwan:70b, Gemma-3-TAIDE-12b-Chat, Llama-3.1-TAIDE-LX-8B-Chat); gpt-oss:120b; CVE-2025-63389 |
| [forskningsnettet.md](international/DK/forskningsnettet.md) | Forskningsnettet (Danish NREN) | Denmark | HIGH | AS1835 Aalborg; **Node B v0.3.0** (2023-era ancient build, 2.5yr unpatched); Node A v0.22.0; gemma3:27b + nemotron3:33b |
| [waseda.md](international/JP/waseda.md) | Waseda University | Japan | CRITICAL | `tokoko.human.waseda.ac.jp`; account takeover **name=tokoko** (human-chosen); custom `deepseek-r1-70b-academic` + `deepseek-r1-70b-jp` research models; qwen3-vl:235b |
| [itb.md](international/ID/itb.md) | Institut Teknologi Bandung | Indonesia | HIGH | LSKK AI Lab; v0.9.2; 22 models incl. 7 custom Indonesian-education fine-tunes (indoedu-e5-base, llama-3.1-8b-indoedu, gemma-3-12b-indoedu) + UAT models; BGE-M3 RAG |
| [nthu.md](international/TW/nthu.md) | National Tsing Hua University | Taiwan | HIGH | sd197130.shin34.ab.nthu.edu.tw; v0.22.0; **taide-npc:latest** (Taiwan national AI as NPC/agent model); qwen3.6:35b |
| [binh-duong.md](international/VN/binh-duong.md) | Binh Duong University / IU Vietnam | Vietnam | CRITICAL | Contabo GmbH VPS (Germany); v0.13.1; account takeover name=372f4fd0a9dd; itu.edu.vn hostname |

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
