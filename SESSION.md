# University Mapping — Session State

_Last updated: 2026-05-03 (session 6 — in progress)_

---

## What This Is

Active mapping of exposed Ollama / Open WebUI instances on university networks globally.
Feeding into: case studies in `case-studies/universities/`, disclosure queue in `disclosures/`.

---

## Toolchain

| Step | Tool | Location | Purpose |
|------|------|----------|---------|
| Shodan hunt | VisorPlus → JAXEN | `~/Tools/VisorPlus/`, `~/Tools/JAXEN/` | Pull university-tagged IPs from Shodan |
| Deep probe | ollama-recon.py | `data/ollama-recon.py` | Models, cloud proxies, system prompts, creds |
| Institution ID | university-domains-go | `~/university-domains-go/` | Resolve hostname → institution name + country |
| Case study | manual / AI-assisted | `case-studies/universities/<CC>/<slug>.md` | Write findings doc |
| Disclosure | gen_emails.py + build_gmail_drafts.py | `disclosures/` | Generate and queue disclosure emails |

**Key Shodan dorks for university sweep:**
```
http.html:"Ollama is running" org:"university"   → ~225 results (2026-05-01)
http.html:"Open WebUI" port:3000 org:"university" → ~84 results (2026-05-01)
```
Cross-referencing same-IP hits → confirmed auth-bypass (Open WebUI auth doesn't protect raw Ollama port).

**Typical invocation:**
```bash
cd ~/Tools/VisorPlus
./visorplus hunt 'http.html:"Ollama is running" org:"university"'
# Output: recon_dump.json + summary.csv → empire.db
# Then: python3 ~/AI-LLM-Infrastructure-OSINT/data/ollama-recon.py --reprobe
```

**Institution identification:**
```bash
~/university-domains-go/bin/unidomains -domain-search buffalo.edu
~/university-domains-go/bin/unidomains -name "virginia tech"
```

---

## Current State (2026-05-02)

### Case Studies Completed: 77 (updated 2026-05-03 session 5)
See `case-studies/universities/index.md` for full table.

**Updated 2026-05-02 (session 2):**
- `KR-POSTECH.md` — expanded to 7 nodes, 3 account takeovers, synchrotron beamline node (4gsr-beamline-ws, tpd.postech.ac.kr)
- `US-IN-purdue-northwest.md` — added account takeover (163.245.212.67, container ID c0ddfaef7764), user-ID embedded model names (163.245.213.131)
- Files reorganized into country subdirectories (CC/slug.md)

**Institute sweep results (2026-05-02, `--institute`):**
- 73 live nodes found across `org:"institute"`, `org:"national"`, `org:"research"`, `org:"ministry"`, `org:government`
- 5 new account takeovers confirmed
- 10+ new institutions documented

**New case studies (session 2 + 3):**
- `TW/tanet.md` — TANet 18-node cluster, account takeover (name=ollama), multi-institution
- `CN/jingdong.md` — China Unicom 26-node cluster v0.5.10
- `KR/kyungpook.md` — Kyungpook National University 3-node cluster, qwen3-vl:32b
- `RO/ici-bucharest.md` — ICI Bucharest 2-node, cloud proxy + abliterated models
- `BD/bdren.md` — Bangladesh BDREN national NREN
- `US/CA-caltech.md` — Caltech yertle.caltech.edu, gpt-oss:120b + dual RAG
- `DZ/arn.md` — Algeria ARN national research network
- `MA/onpt.md` — Morocco ONPT national telecom
- `IN/nib.md` — India NIB/BSNL national backbone 2 nodes
- `GR/iti.md` — ITI/CERTH Greece vcl.iti.gr, Mistral Small 24B
- `MY/moec.md` — Malaysia MoE EMISC, government education

**New case studies (session 4):**
- `ID/university-of-indonesia.md` — AS3382 Depok, llama3.2:3b, v0.5.4-dirty, Open WebUI v0.5.4 auth-on/3000 + raw API open/11434, CVE-2025-63389 confirmed
- `CN/tianjin-cloud-park.md` — AS141679 China Telecom Tianjin; 46-node multi-tenant cluster; v0.5.10; RAG pipelines; research institute tenants
- `US/IN-purdue.md` — Purdue main campus `n8n.tap.purdue.edu`; account takeover `d3af393f8e4e`; v0.12.3; n8n workflow automation attack surface
- `BD/university-of-dhaka.md` — coding cluster; bge-m3 RAG; 3 cloud proxies; v0.20.5
- `US/ME-university-of-maine.md` — ECE-Ubuntu-02; 69GB uncensored 122B model; 18 cloud proxies; v0.18.2
- `IN/shiv-nadar.md` — expanded to 7 nodes (.28–.29 added session 4); disclosure email updated

**Updated existing (session 4):**
- `CA/ON-western-ontario.md` — added Node 2 (ebithp-c1v17.eng.uwo.ca, account takeover `0732205c469d`)

**Second sweep results (--limit 250, 2026-05-03):**
- 25 new live nodes, 6 new takeovers (cumulative: 11 takeovers, 76 live, 290 total)
- New takeovers: Purdue NW 2nd node (163.245.207.105), Purdue main (128.210.38.15), UWO Node 2 (129.100.174.232), POSTECH bsp-server-3 (.121.59), POSTECH bsp-server-9 (.121.76), NTUA (147.102.111.27)
- Other notable new live: U of Maine (21 models), U of Dhaka (11 models), UCSD (67.58.51.111), Hankyong NW KR (155.230.92.188), Monash x3 new nodes

**Note:** 130.49.190.86 misattributed as "University of Pittsburgh" in state — actually AS215540 GCS LLP Stockholm/Moscow commercial hosting

**Updated existing (session 3):**
- `GR/tech-crete-ntua.md` — added NTUA Node 2 (147.102.111.27), account takeover (name=1600b8395e7f)
- `US/NY-rit.md` — added account takeover for 129.21.220.95 (name=72e95ec7e5f4, AD-joined workstation)
- `SE/KTH.md` — added Node 3 (130.237.218.65, v0.9.3)
- `LK/learn.md` — added minimax-m2.7:cloud to model inventory
- `KR/snu.md` — expanded to 3-node cluster (added 147.47.209.39 v0.11.10, 147.46.112.49 v0.20.2)

State file: `data/ollama-univ-state.json` (145 IPs)
Export: `data/ollama-univ-findings.md`

### Disclosures
- **Sent:** 11 institutions (Duke confirmed reply from Anthony Miracle)
  - Duke, POSTECH, Shiv Nadar, Columbia, UCSB, Chulalongkorn, RIT, Hanoi, MOPH
  - Shandong (no valid contact), KRENA (no contact path)
- **Queued in `_gmail_drafts.json`:** 36 drafts (25 CRITICAL + 11 HIGH), all DRAFT status
- **Script:** `disclosures/build_gmail_drafts.py` regenerates `_gmail_drafts.json` from `disclosures/*.md`
- **Note:** POSTECH disclosure (KR-POSTECH.md) updated with 3 account takeover nodes — needs resend or update email

### JAXEN Run State
- General Ollama cohort: `~/Tools/JAXEN/runs/ollama/state.md` (47 hosts, 2026-04-30)
- Deep dive: `~/Tools/JAXEN/runs/93_123_109_107/` (abliterated models + hexstrike-ai brand)
- No dedicated university JAXEN run exists yet

---

## Next Steps (Priority Order)

- [x] **Finish `--university` mode in `ollama-recon.py`** — DONE 2026-05-02
- [x] **Run university sweep** — DONE: `python3 data/ollama-recon.py --university --limit 100`
- [x] **Update POSTECH case study** — DONE: 7 nodes, 3 account takeovers, synchrotron node
- [x] **Update Purdue NW case study** — DONE: account takeover + user-ID models
- [ ] **Send disclosure queue** — 36 emails in `_gmail_drafts.json` DRAFT
  - POSTECH disclosure also updated, needs resend or follow-up
  - Use Gmail MCP: `mcp__claude_ai_Gmail__list_drafts` or `build_gmail_drafts.py`
- [x] **Write new case study stubs** — DONE 2026-05-03
  - University of Indonesia (152.118.31.61) — AS3382 confirmed, case study written
  - 130.49.190.86 — **NOT university**: AS215540 GCS LLP (Moscow/Stockholm commercial hosting), misattributed in sweep; cloud proxy model deepseek-v3.1:671b-cloud + Open WebUI on 3000; worth filing separately
- [x] **Update Shiv Nadar case study** — DONE 2026-05-03: expanded to 5 nodes, 30+ cloud proxies, pre-release DeepSeek V4, disclosure email updated
- [x] **Second sweep** — DONE 2026-05-03: --limit 250, 25 new live, 6 new takeovers, 11 total

- [x] **Update POSTECH case study** — DONE: 9 nodes, 5 takeovers, bsp-server-3 (rnj-1:8b Essential AI model), bsp-server-9 (rangers.postech.ac.kr)
- [x] **Update Purdue NW case study** — DONE: 3 nodes, Node 2 takeover `5a9d376f9c56`, Node 3 gemma3:12b
- [x] **Update Western Ontario case study** — DONE: Node 2 takeover `0732205c469d`
- [x] **Write UCSD case study** — DONE: CA-ucsd.md, 67.58.51.111
- [x] **Write NCCU TAIDE case study** — DONE: nccu-taide.md, 140.119.163.219; 3× Taiwan national TAIDE models + gpt-oss:120b on V100×4
- [x] **Update POSTECH case study** — DONE: bsp-server-3 (.121.59) + bsp-server-9 (.121.76) added, 9 nodes total, 5 takeovers
- [x] **Update Purdue NW case study** — DONE: 163.245.207.105 + 163.245.208.96, 3 nodes total
- [x] **Write VNU Hanoi domain-specific models** — DONE: vnu-hanoi.md, 112.137.129.161
- [x] **Write NTU GPU case study** — DONE: ntu-gpu.md, 140.112.233.108, vision cluster
- [x] **Update NTUA case study** — DONE: p620 (147.102.40.5) + takeover node (111.27) both in tech-crete-ntua.md
- [x] **RIT DGX Spark** — DONE: NY-rit.md already included disco-dgx-spark (129.21.25.95), 25 models, 18 cloud proxies
- [x] **"Hankyong NW" 155.230.92.188** — confirmed as senlab.knu.ac.kr = Kyungpook NW; already in kyungpook.md as Node 2
- [x] **Write Monash 3-node update** — DONE: updated monash.md; added Nodes 2+3 (118.138.243.239/243.34); OOM note on 671B; v0.20.2/0.18.3/0.19.0
- [x] **Write Denmark/Forskningsnettet** — DONE: forskningsnettet.md; AS1835 Aalborg; Node B v0.3.0 (2.5yr ancient); Node A v0.22.0
- [x] **Write NCCU TAIDE case study** — DONE: nccu-taide.md; 140.119.163.219; V100×4; 3× Taiwan national TAIDE models
**New case studies (session 5):**
- `TW/tanet-abliterated-cluster.md` — 120.126.16.144 TANet Taipei no-rDNS; v0.20.3; gemma4-crack-fixed + 2× abliterated HF + dolphin + qwen2.5-agi:32b
- `TW/nthu.md` — NTHU sd197130.shin34.ab.nthu.edu.tw; v0.22.0; taide-npc:latest (Taiwan national AI as NPC model)
- `VN/binh-duong.md` — itu.edu.vn Contabo VPS; v0.13.1; account takeover name=372f4fd0a9dd; minimax-m2.7:cloud
- `JP/waseda.md` — tokoko.human.waseda.ac.jp; account takeover name=tokoko; custom deepseek-r1-70b-academic/jp; qwen3-vl:235b
- `ID/itb.md` — LSKK AI Lab; v0.9.2; 22 models; 7 custom Indonesian-education fine-tunes; BGE-M3 RAG
- `TW/nccu-taide.md` — V100×4; v0.11.6; 3× Taiwan national TAIDE models; gpt-oss:120b
- `DK/forskningsnettet.md` — AS1835 Aalborg; Node B v0.3.0 (2.5yr ancient); Node A v0.22.0
- `US/CA-ucsd.md` — AS26397; v0.20.7; qwen3.5:35b + gpt-oss + devstral-2:123b-cloud + deepseek-v3.1:671b-cloud

**Updated existing (session 5):**
- `TW/ntu-gpu.md` — added 140.112.183.119 (mdq100/qwen3.5-coder:35b + minimax cloud) and 140.112.91.82 (qwen3-assistant:latest + minimax cloud); NTU footprint now 4 nodes
- `TW/ncu-aiden.md` — added note on second Aiden/TianXing deployment observed on TANet (offline before documentation)
- `TW/fju-medph.md` — added full FJU 4-node footprint table (medph, phy, net2net, ee)
- `AU/monash.md` — corrected 3-node cluster; OOM note on 671B DeepSeek
- `TW/tanet.md` — added 5G security system prompt (pc214 qwen3.5-nothinker) + TANet MoE CC takeover (name=ollama)

**Late session 5 additions:**
- `SK/tuke.md` — prometheus.fei.tuke.sk TUKE FEI Slovakia; 24 models; MedGemma 27B×2 (54GB+29GB); huihui_ai/Qwen3.6-abliterated:35b; Turkish erurollm-9b; v0.11.11
- `GR/aua.md` — afa4pc19.aua.gr AUA Greece; qwen3:235b-a22b (142GB, 235.1B params); dual RAG (BGE-M3 + nomic-embed); v0.18.2
- `JP/kumamoto.md` — scorpio.arch.cs.kumamoto-u.ac.jp; account takeover name=d4659cbf55b2; minimax-m2.7:cloud; v0.12.7
- `CY/nicosia.md` — University of Nicosia/Intercollege Cyprus; deepseek-v4-pro cloud disabled; v0.17.0; first CY finding
- `RW/rwanda.md` — University of Rwanda CoE; qwen3.5:27b + qwen3.6:27b; first RW finding
- `US/CA-berkeley.md` — lal-99-178.reshall.berkeley.edu; v0.11.10; qwen2.5:32b; first Berkeley finding (residential hall!)
- `US/CA-ucsb.md updated` — MCDB node spark-4de1.mcdb.ucsb.edu (128.111.208.95) added
- `KR/POSTECH.md updated` — bionlinux2 (6th takeover) + indians node; 11 nodes total
- `international/CA/AB-u-alberta.md` — lula.cs.ualberta.ca; v0.21.1; gpt-oss:120b + qwen2.5-coder:32b
- `US/NY-columbia.md updated` — Lamont-Doherty EO node (129.236.163.69, RAG pipeline) added
- `TW/ntu-gpu.md updated` — 5 nodes total; added 407-2.m7.ntu.edu.tw (embeddinggemma:300m)
- `DK/forskningsnettet.md updated` — AAU-cloud 3rd node note (130.225.37.103)

**Session 5 totals (end of session):**
- Case studies: **77 total** (was 66 start of session)
- Shodan credits: **exhausted** for May cycle
- Reprobe: 4 of 226 dead nodes came back (POSTECH indians, Berkeley, Covenant, NTU m7)
- Account takeovers: **14 total** (+1 Kumamoto, +1 POSTECH bionlinux2)

---

## Session 6 — vLLM/TGI Pivot (2026-05-03, in progress)

**Pivot rationale:** Shodan credits exhausted; pivoting from Ollama to vLLM/TGI (OpenAI-compatible LLM serving frameworks). Discovery via masscan on known university /16 ranges, port 8000/8080.

**Toolchain for vLLM:**
- `data/vllm-probe.py` — deep probe script (parser, /v1/models, /metrics, inference test, /pause check)
- `~/go/bin/httpx` — fast filter: match `"owned_by"` or `"object"` in /v1/models response
- masscan → httpx filter → vllm-probe.py → case study

**Key vLLM fingerprint:** `/v1/models` returns JSON with `"owned_by": "vllm"` field.

**Scans run:**
- scan1: 23 university /16 ranges → 2548 hits → httpx filtered
- scan2: 20 more ranges (incl. DigitalOcean noise 143.198.x.x — skip)
- scan3: European research networks (FUNET 195.148, 131.108 Brazil) → no vLLM
- scan4: Top CS universities (MIT 18.0/16, Stanford 171.64, CMU 128.2, Princeton 128.112, UW 128.95, UIUC 130.126, Michigan 141.211, Georgia Tech 130.207, UT Austin 128.83, UMass 128.119) — in progress

**New case studies (session 6):**
- `US/CA-berkeley-vllm.md` — **5 vLLM nodes on UC Berkeley research network**
  - 128.32.112.120: vLLM 0.14.0, Meta-SecAlign-8B + Llama-3.1-8B-Instruct, 78.5M prompt tokens, `/pause` unauth admin endpoint
  - 128.32.43.204: Qwen3.5-9B, short context research config
  - 128.32.48.211: Qwen2.5-3B-Instruct, username `akshat` in path, 103K+ requests, live traffic
  - 128.32.48.200: NVIDIA Nemotron-3-Nano-30B-A3B-BF16, reasoning model
  - 169.229.48.109 (brewster.millennium.berkeley.edu): vLLM 0.1.dev15967, Qwen2.5-1.5B, Millennium cluster, dev build
  - Berkeley total: **7 unprotected AI nodes** across residential, research, and course infrastructure
- `US/CA-berkeley-course-ai.md` — `roar-art.EECS.Berkeley.EDU` (128.32.43.210)
  - FastAPI "Course AI Assistant API" v0.1.0, Swagger UI public
  - **Unauthenticated `/api/chat/memory-synopsis`** — no security field in OpenAPI spec, not a bypass
  - All other endpoints (chat, files, courses, RAG) correctly require HTTPBearer
  - Memory injection confirmed: `POST /api/chat/memory-synopsis?sid=<any>` → `{"status":"success"}`
  - Serves multiple EECS courses; worst case: injected memory surfaces in student AI tutor responses
- `TW/ntu-csie-vllm.md` — `mvnl-nas.csie.ntu.edu.tw` (140.112.91.209)
  - CSIE MVNL Lab, vLLM 0.18.2rc1.dev73, `nvidia/Llama-3.3-70B-Instruct-FP8`
  - 2-engine tensor parallel, 237 requests, 450K prompt tokens, 25K gen tokens
  - Port 8080 public, no auth
- `US/CA-ucsb.md updated` — added umang wireless node (169.231.203.223)
  - llama.cpp server, Qwen3-8B GGUF, username `umang` in path, Linux `/home/umang/Desktop/`
  - Wireless network (personal laptop on campus WiFi)

**Scan results (session 6):**
- scan1: 2548 hits → **7 confirmed vLLM** (4 Berkeley, UCLA brew., UCSB wireless, NTU CSIE) + 10 RuoYi false positives (111.228.x.x China)
- scan4 (MIT/Stanford/CMU/Princeton/UW/UIUC/GT/UTX/UMass): 332 hits → **0 confirmed** — top CS universities all firewall ports externally
- sglang-scan (UC campuses port 30000): **0 confirmed** — no SGLang nodes found
- sglang-scan port 8080 (UC campuses): ~300 hits, all infrastructure (UCR DHCP nodes "404 page not found", UCSD empty responses)
- **euro-asia-scan** (in progress): ETH/EPFL/TUM/Cambridge/Oxford/Imperial/Tokyo/Kyoto/NUS × ports 8000,8080,8001,7860,3000

**Session 6 false positive analysis:**
- `111.228.x.x:8080` — **RuoYi admin framework** (Chinese open-source Java admin UI); returns 401 JSON `{"msg":"请求访问：/v1/models，认证失败...","code":401}` — not AI services
- UCR 138.23.186.x/24 — DHCP workstations (d01aq*.dyn.ucr.edu) running Go service; not AI
- UCSD 132.239.x.x port 8080 — empty responses, infrastructure only

**Euro-Asia scan result:** 0 confirmed vLLM/TGI across ETH Zurich (129.132), EPFL (128.178), TUM (131.159), Cambridge (131.111), Oxford (163.1), Imperial (155.198), Tokyo (130.69), Kyoto (157.82) — 1601 filtered hits probed, none were AI inference nodes. European and Japanese elite universities have significantly better outbound firewall hygiene than UC/Asian Pacific peers.
- NUS Singapore (137.132) SYN-ACKed ~73K ports — firewall false positive, entire range excluded.
- Cambridge port 8080 hits were wireless infrastructure controllers (coa.uws-mc-b6.controller.wireless.cam.ac.uk).

**asia-au-scan in progress:** KAIST (143.248), Hanyang (165.132), SKKU (163.152), HKU (147.8), CUHK (137.189), HKUST (143.89), Melbourne (128.250), Sydney (129.78), ANU (150.203) on ports 8000, 8080, 11434.

**Korean university scan (kr-vllm-scan):**
- POSTECH (141.223), Inha (165.246), Kyungpook (155.230), SNU (147.46/47 — SYN-ACK false positives)
- **1 confirmed: 165.246.170.53:8000** — INHA vLLM 0.8.4, `local-qwen` (container mount), 311 requests, 90% prefix cache hit rate
- POSTECH, Kyungpook, all SNU: 0 confirmed vLLM (all Ollama on 11434, not vLLM on 8000)

**asia-au scan (KAIST/HKU/CUHK/HKUST/Melbourne/Sydney/ANU):**
- 86 total hits, 0 confirmed vLLM/TGI
- 1 port 11434 hit (150.203.15.131 / cadre-vip-02.ada.edu.au, ANU) — connection reset, not accessible
- Melbourne (128.250.43.x/24): Barracuda email gateway cluster (port 8080 false positives)
- CUHK (137.189.x.x): web services (MediaWiki, finance, 整数智能数据工程平台)
- SKKU, Hanyang, KAIST, HKU, Sydney, ANU: 0 AI inference

**Session 6 totals:**
- Case studies: **81 total** (+5: CA-berkeley-vllm, CA-berkeley-course-ai, TW/ntu-csie-vllm, CA-ucsb update, KR/inha updated)
- vLLM confirmed this session: 8 nodes across 5 institutions (Berkeley ×5, NTU CSIE ×1, UCSB wireless ×1, INHA ×1)
- Negative space: MIT/Stanford/CMU/Princeton/UW/UIUC/GT/UTX/UMass → 0; ETH/EPFL/TUM/Cambridge/Oxford/Imperial/Tokyo/Kyoto → 0; KAIST/SKKU/Hanyang/HKU/CUHK/HKUST/Melbourne/Sydney/ANU → 0

**Next in session 6:**
- [ ] Probe euro-asia-scan results when masscan completes
- [ ] **Send disclosure queue** — 36 emails still in `_gmail_drafts.json` DRAFT + add Berkeley vLLM + Berkeley Course AI + NTU CSIE
- [ ] **Third Ollama sweep** — Shodan credits reset; run with new dork vectors or non-university ASNs
- [ ] **Build disclosure emails for new batch** — nccu-taide (TWCERT), forskningsnettet, Monash update, Kyungpook update, tanet-abliterated (TWCERT), TUKE, AUA, Kumamoto, Berkeley (Ollama), Berkeley (vLLM), Berkeley (Course AI), NTU CSIE, UCSB (umang)
- [ ] **JAXEN general cohort next-moves** (from `runs/ollama/state.md`):
  - §15 canary fingerprint subagent landing
  - Disclosure path for honeypot-canary net
  - Decision on `93.123.109.107` (abliterated + hexstrike-ai)

---

## Vulnerability Reference

**CVE-2025-63389** — Unauthenticated `/api/create` in Ollama (all versions, no patch).
One request injects attacker-controlled system prompt into any loaded model.

**Cloud proxy takeover** — 401 response to `/api/chat` on a `:cloud` model leaks Ollama Connect signin URL + SSH pubkey. Full account hijack possible.

**Auth bypass pattern** — Open WebUI on port 3000 has auth enabled; Ollama on port 11434 on same host is unprotected. Auth provides false sense of security to operators.
