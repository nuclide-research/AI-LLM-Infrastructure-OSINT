# University Mapping — Session State

_Last updated: 2026-05-03 (session 5)_

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

- [ ] **Third sweep** — run with --government, --hospital, or new Shodan dork vectors
- [ ] **Build disclosure emails for new batch** — nccu-taide (TWCERT), forskningsnettet, Monash update, Kyungpook update, tanet-abliterated (TWCERT)

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
