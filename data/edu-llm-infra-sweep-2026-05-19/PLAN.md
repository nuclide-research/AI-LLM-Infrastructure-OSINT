# .edu LLM Infrastructure Survey — Plan & Tracker

**Started:** 2026-05-19 ~12:58 CDT
**Workspace:** `~/recon/edu-llm-infra-2026-05-19/`
**Goal:** Find all publicly-exposed LLM infrastructure on US university (`.edu`) networks. Build per-institution case studies. Diff against the 81 universities already documented.

---

## Stage 0 — Dork-map (RUNNING, ~76% complete at write-time)

**Method:** index all 1,629 verified Shodan dorks from `~/AI-LLM-Infrastructure-OSINT/shodan/queries/` (29 categories, hand-curated and FP-tested over 50+ prior commercial surveys). Cross-product each with `hostname:.edu`. Run `shodan count` (free per query, no credit cost) with 1.2s rate-limit + 50-min deadline.

**Files:**
- `verified-dorks-master.tsv` — the 1,629 source dorks from the OSINT repo
- `scoped-dorks-edu.tsv` — 1,584 dorks (after dropping those that already had `hostname:` filter)
- `scoped-counts.tsv` — running output: `count<TAB>category<TAB>scoped_dork`
- `scoped-counts.log` — sweep progress + milestones

**Exit signal:** Monitor task `b21lf2x6t` fires when log contains `[done` or `deadline-hit`.

**Status checkpoint (this write):** 1,206/1,584 (76%), 325 non-zero hits, 54 ERRs (~4.5%).

---

## Stage 0.5 — Log Stage-0 results to OSINT repo (DO IMMEDIATELY ON SWEEP DONE)

Persist Stage 0 so we don't re-do the count sweep next session.

**Actions:**
1. Write `~/AI-LLM-Infrastructure-OSINT/case-studies/universities/edu-llm-infra-sweep-2026-05-19.md` — methodology, top-N table by hit count, dork-class hierarchy (server-header / bundle-ID body / route-slug body / TLS-CN), the Airtable noise observation, ERR rate.
2. Copy `scoped-counts.tsv` → repo as artifact (under `data/edu-llm-infra-sweep-2026-05-19/scoped-counts.tsv` or referenced by absolute path from the case study).
3. Update `case-studies/universities/index.md` — add a row pointing at the new case study.
4. Update `~/AI-LLM-Infrastructure-OSINT/SESSION.md` — Session 24 "Mid-session sub-survey: .edu LLM-infra Stage 0 dork-map."
5. Optionally `git commit` the case study + index + SESSION.md so it's preserved.

**Output:** sweep result is reproducible from the persisted artifact; the per-category dork populations are durable reference data.

---

## Stage 1 — Pull samples per high-yield dork (NEXT)

**Criterion for "high-yield":** scoped dork returned ≥ 3 hits. Skip 0-hit (no data) and skip 1-2 hits (too small to invest sample-pull credit; can manually visit one host).

**Method:** for each high-yield dork, `shodan download --limit N` where N is the dork's count (cap at 500). Files saved to workspace as `sample-<dork-slug>.json.gz`.

**Cost:** Freelance-tier Shodan; each download = 1 scan credit per 100 results. 100 high-yield dorks × avg 50 results = 50 credits. Out of the 6,200+ available.

**Output:** `sample-*.json.gz` files containing `(ip, port, hostname, http_html_body)` per host.

---

## Stage 2 — Inline-verify per category (the "go through each category and look at IPs" step)

**Per category (01 through 27, in order):**

1. **List the high-yield dorks** in that category from `scoped-counts.tsv`.
2. **Pull the samples** if not already pulled in Stage 1.
3. **Inline-probe verify** — fast asyncio HTTP probe (`/api/tags` for Ollama, `/api/config` for Open WebUI, `/hub/api/info` for JupyterHub, etc.) against marker list per platform. Drop substring-FP hits (Insight #15).
4. **Per confirmed IP, inspect manually:**
   - Hostname → institution mapping via local Hipo `world_universities_and_domains.json` (suffix-match on `domain`)
   - Auth state (200 OK unauth / 401-with-cred-leak / signup-open / behind-TLS / etc.)
   - Per-platform deep enum (Ollama models, JupyterHub version, Streamlit app title, n8n workflow count, etc.)
   - Severity class per OVERVIEW.md taxonomy (cloud-proxy-200, auth-disabled, cloud-proxy-cred-leak, abliterated, agentic-tool-exec, large-deployment, outdated-version, transport-downgrade, adjacent-rservices, other)
5. **Capture findings** as we go in `category-<NN>-findings.tsv` with columns: `ip, port, hostname, institution, country, state, platform, severity, finding_class, key_detail`.
6. **Cross-reference against the 81 existing case studies** (`known-from-overview.tsv`) — surface NEW institutions only.

**Output per category:** a findings TSV + per-host case study files for confirmed NEW exposures.

---

## Stage 3 — Per-institution case study writeups

**For each NEW institution surfaced (not in the 81 existing case studies):**

Write a per-host case study under:
- `~/AI-LLM-Infrastructure-OSINT/case-studies/universities/US/<STATE>-<institution-slug>.md` (US)
- `~/AI-LLM-Infrastructure-OSINT/case-studies/universities/international/<CC>/<institution-slug>.md` (non-US)

Follow the existing case-study format (see `NY-columbia.md` as the template):
- TL;DR (one sentence)
- Discovery (dork that surfaced it)
- Verification (probe + response)
- Finding(s) by severity
- Operator attribution (WHOIS, hostname, AS)
- Disclosure routing (per Insight #4 — WHOIS authoritative)
- Notable details (model name, system prompt, exposed creds, etc.)

**Cross-update:** add row to `case-studies/universities/index.md` per new case study. Update `case-studies/universities/OVERVIEW.md` running tally if the new finding fits an existing severity-class table.

---

## Stage 4 — Session wrap-up

1. Update `~/AI-LLM-Infrastructure-OSINT/SESSION.md` Session 24 with:
   - Total new institutions surfaced (count + by-country breakdown)
   - Finding-class distribution (count per severity)
   - New methodology insights if any (candidate Insights queued)
   - Carry-forward items
2. Update auto-memory:
   - `project_university_mapping.md` — bump count from 81 → new total, note Session 24 work
   - New reference memories for any reusable findings (e.g. .edu-specific Jupyter / Open WebUI population numbers)
3. Update MEMORY.md index
4. Optionally `git add` + `git commit` the new case studies + index + OVERVIEW + SESSION.md

---

## Optional Stage 5 — Disclosure backlog

Session 5 ended with 36 queued Gmail drafts (per `project_university_mapping.md` memory). Add to that backlog per Cowboy decision; per `feedback_no_disclosure_recommendations` memory, I don't draft disclosures unsolicited — Cowboy decides routing.

---

## What's deferred / out of scope this session

- Non-`.edu` international academic TLDs (`.ac.uk`, `.edu.au`, `.edu.cn`, etc.). Catalogued in `dorks-matrix.tsv` but not in scope for this Stage 0. The session-5 method (`org:"university"`) catches international via WHOIS; we'd run it as a second pass.
- TLS cert subject CN attribution-class dorks. `ssl.cert.subject:edu` and similar. Skipped per the Stage 0 narrowing.
- aimap deep-enum chain (the full visor-chain-runner). Stage 2 inline-probe replaces it for speed; aimap can run on per-host curiosity later.

---

## Tooling state notes (carry-forward)

- **No zombie shells.** Every background process has a deadline (50-min cap on the count sweep). Monitor cleans itself up on done signal.
- **Rate limit:** 1.2s between Shodan API calls. Earlier 264-query burst Alabama sweep hit 62% ERR; current 1,584-query sweep at 1.2s delay holds ~4% ERR steady.
- **Reference data leverage:** the 1,629-dork master list pulls FROM the OSINT repo's vetted catalog. No more inventing dorks from scratch.

---

## Live status (filled in as we progress)

| Stage | State | Started | Done | Output |
|---|---|---|---|---|
| 0 — Dork-map | RUNNING (76%) | 12:58 | TBD | scoped-counts.tsv |
| 0.5 — Log to repo | pending | — | — | case-studies/universities/edu-llm-infra-sweep-2026-05-19.md |
| 1 — Sample pulls | pending | — | — | sample-*.json.gz |
| 2 — Inline-verify per category | pending | — | — | category-*-findings.tsv |
| 3 — Per-institution case studies | pending | — | — | case-studies/universities/<CC>/*.md |
| 4 — Session wrap-up | pending | — | — | SESSION.md update + memory |
