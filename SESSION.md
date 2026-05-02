# University Mapping — Session State

_Last updated: 2026-05-02 (session 2)_

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

### Case Studies Completed: 46 (updated 2026-05-02)
See `case-studies/universities/index.md` for full table.

**Updated 2026-05-02:**
- `KR-POSTECH.md` — expanded to 7 nodes, 3 account takeovers, synchrotron beamline node (4gsr-beamline-ws, tpd.postech.ac.kr)
- `US-IN-purdue-northwest.md` — added account takeover (163.245.212.67, container ID c0ddfaef7764), user-ID embedded model names (163.245.213.131)

**University sweep results (2026-05-02, `--university --limit 100`):**
- 145 IPs scanned (48 live, 97 dead)
- 5 account takeovers: Purdue NW (1), POSTECH (3), Hanoi (1)
- 15 cloud proxy nodes (no takeover): Purdue NW, Western Ontario, JKUAT, Newcastle AU, Tech U Crete, UCSB, Keio, Chulalongkorn, Shiv Nadar (2)
- 28 plain unauth Ollama instances

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
