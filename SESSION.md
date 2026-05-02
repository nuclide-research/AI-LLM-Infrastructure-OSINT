# University Mapping — Session State

_Last updated: 2026-05-02_

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
| Case study | manual / AI-assisted | `case-studies/universities/<CC>-<slug>.md` | Write findings doc |
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

### Case Studies Completed: 44
See `case-studies/universities/index.md` for full table.

Notable gaps (Shodan hits not yet written up):
- ~181 remaining university Ollama instances from the 225-result query not yet documented
- Open WebUI cross-ref (84 results) not fully processed

### Disclosures
- **Sent:** 11 institutions (Duke confirmed reply from Anthony Miracle)
  - Duke, POSTECH, Shiv Nadar, Columbia, UCSB, Chulalongkorn, RIT, Hanoi, MOPH
  - Shandong (no valid contact), KRENA (no contact path)
- **Queued in `_gmail_drafts.json`:** 36 drafts (25 CRITICAL + 11 HIGH), all DRAFT status
- **Script:** `disclosures/build_gmail_drafts.py` regenerates `_gmail_drafts.json` from `disclosures/*.md`

### In-Progress Work
- `data/ollama-recon.py` — `--university` mode partially added (header + constants only, 2026-05-02)
  - Added: `UNIV_STATE_FILE`, `UNIV_EXPORT_FILE`, `UNIDOMAINS_BIN` constants
  - TODO: add `shodan_university_ips()`, `identify_university()`, `probe_webui()`, `--university` argparse flag, university main loop

### JAXEN Run State
- General Ollama cohort: `~/Tools/JAXEN/runs/ollama/state.md` (47 hosts, 2026-04-30)
- Deep dive: `~/Tools/JAXEN/runs/93_123_109_107/` (abliterated models + hexstrike-ai brand)
- No dedicated university JAXEN run exists yet

---

## Next Steps (Priority Order)

- [ ] **Finish `--university` mode in `ollama-recon.py`**
  - `shodan_university_ips(limit)` — query `http.html:"Ollama is running" org:"university"`
  - Also pull `port:3000 org:"university"` for Open WebUI instances
  - `identify_university(ip, hostnames)` — subprocess call to `unidomains` binary
  - Separate state file: `ollama-univ-state.json`
  - Run it: `python3 data/ollama-recon.py --university --limit 250`

- [ ] **Process new findings** into case study stubs
  - Any live hit with cloud proxy → CRITICAL case study
  - Any live hit with cred leak → CRITICAL
  - Auth-disabled Open WebUI → CRITICAL

- [ ] **Send disclosure queue** — 36 emails sitting as DRAFT in `_gmail_drafts.json`
  - Use Gmail MCP tools or `build_gmail_drafts.py` → Gmail API

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
