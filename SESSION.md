# University Mapping — Session State

_Last updated: 2026-05-02 (session 3)_

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

### Case Studies Completed: 57 (updated 2026-05-02 session 3)
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
- [ ] **Write new case study stubs** for newly confirmed institutions not yet documented:
  - University of Pittsburgh (130.49.190.86) — plain unauth
  - University of Indonesia (152.118.31.61) — plain unauth
- [ ] **Update Shiv Nadar case study** — 2 new cloud proxy nodes (103.27.166.38, 103.27.166.36)
- [ ] **Second sweep** — run with `--limit 100` again to catch remaining ~125 Shodan results

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
