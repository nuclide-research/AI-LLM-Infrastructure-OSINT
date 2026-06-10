# Session Retrospective — Cat-Tabby + Devstral re-validation
_NuClide Research · 2026-06-09 · Lane-A/B/C/D parallel-agent run_

## TL;DR

The 4-DCWF-lane parallel agent dispatch is the most productive pattern this session produced. The corrected truth after agent reconciliation:

- 884 paired-probe-stable code-loaded Ollama hosts (validated subset of 1,217 suspect)
- 66 unauthenticated MCP servers exposing `get_aws_admin_credentials`, `get_ssh_session_credentials`, `schedule_commands` — credential-theft tool fleet (Lane B finding while hardening Tabby FP)
- Wire is CLEAN per Lane C 5-control shape check; VPN-MITM hypothesis was wrong
- Tabby aimap FP hardened with `/_next/static/chunks/webpack-` + `app/auth/signin/page-` conjunctive markers — defeats both the spoof class AND surfaces the MCP fleet that was being masked

## What worked

- **Custom DCWF wardrobe outfits per lane.** `cat-tabby-lane-{a,b,c,d}-*` saved at `~/wardrobe/outfits/`. 6-7 atoms each, lane-scoped, not the 13-piece kitchen-sink `ai-infra-hunt`. The minimal-atom framing pushed each agent to embody the role rather than reach for unrelated tools.
- **Parallel agent dispatch with explicit role identity in the prompt.** Each agent got the role number (NICE 541 / DCWF 623 / 672 / 733), the outfit slug, the atom list, and an unambiguous mission. Reconciliation of their findings produced more truth than any single-agent serial run would have.
- **Lane A's paired-probe approach (stability signature via sha256 of sorted model-list).** Caught the divergence class cleanly: 99.34% stable on the suspect cohort, 54% stable on the broader 10,895 corpus — sharply distinguishes the trustworthy subset.
- **Lane B's marker hardening pattern.** A 14-byte `<title>Tabby` literal was spoofable; a 50-byte Next.js webpack chunk path is a build artifact the mimicry doesn't produce. Insight #6 conjunctive discipline applied at the *marker level inside a probe*, not just at the probe level. Generalizes to every other identity FP that relies on a short HTML token.
- **Lane C's methodology §3 sandbox-MITM formalization.** Took standing advice and turned it into an executable script with a decision rule. Stage 0 prerequisite from now on.
- **Lane D's chain-of-custody discipline.** Preserved evidence files intact rather than deleting, marked the contamination as evidence not garbage. K0118 working as designed.
- **shodan-fetch in-page Promise.all via chrome-devtools MCP browser.** Continues to deliver 0-credit population sweeps. 165 IPs across 6 queries in ~60s. The README-derived four-step architecture (persistent profile, asset-strip, parallel fetch, SSR parse) holds up.
- **Restraint discipline at code level.** `stage3v-verify.py` `DO_NOT_CALL` constant — 0 violations across 1,523 probes. Nick should never have to police completions / admin-creates manually.

## What needs improvement

- **Stage -1 squad outputs need ground-truth validation before Stage 0.** Four squad-1/3 errors landed on this Cat-Tabby survey: Tabby Shodan-dark (wrong), `/v1/health` always-open (wrong), no nuclei templates (wrong), no Sourcegraph aimap FP (wrong). The squads' confidence outpaced their groundedness. Mitigation: a 5-minute Stage -0.5 "squad cross-check" task that runs three trivial validations (does the dork return 0 or N?, does the binary actually emit the reported endpoint shape?, does a `find` for the FP source file return anything?) before the squad output is allowed into Stage 0 dork design.
- **My initial category choice was strategically wrong.** Nick asked for exposed AI/LLM infrastructure; I picked Cat-Tabby (a hardened category). 2 hours of methodology execution against a category that yielded a thesis-confirmation negative result instead of the live exposures Nick wanted. Mitigation: at category-pick time, run a 30-second "is this category in the auth-on-default or auth-off-default cohort" check via the existing tier vocabulary; pivot if the wrong one.
- **VPN/MITM hypothesis jumped too far without Lane C's formal verification.** I retracted findings based on a hunch about VPN-exit response rewriting. Lane C subsequently disproved the hunch. The right order: run the sandbox-MITM check FIRST (free, 5 controls, takes ~10 seconds), then decide whether to retract. Mitigation: same as Stage 0 MITM gate — bake the check into the chain runner so it always runs.
- **The original Tabby aimap fingerprint shipped without the build-artifact anchor.** A 14-byte title literal is spoofable. Lane B's hardening is the model going forward: every identity probe should have at least one MATCHER that anchors on a build artifact (webpack chunk path, semver in a /version endpoint, framework-specific HTML class) rather than a marketing string. Codify as a fingerprint-engineering rule.
- **Lane D's retraction was authored against the VPN-contamination hypothesis BEFORE Lane C disproved it.** Cross-lane reconciliation should happen at the orchestrator level (here, me) before any retraction goes into the case study. Parallel agents are not independent observers; one of them being wrong upstream poisons the downstream documentation. Mitigation: orchestrator waits for ALL lanes to land before writing the retraction; if any lane materially changes the picture, re-draft.
- **Censys deferred to UI-only.** Free-tier search needs org-id (403 from cencli); chrome-devtools MCP browser hits Cloudflare on Censys UI. Need to find another passive avenue (see the "Censys alternatives" section below).

## What wasted time

- **Cat-Tabby category choice** itself (~2 hours net). Hardened-by-design category, methodology produced thesis-confirmation negative result instead of headline exposure findings. Lesson: pick the high-yield categories when "find exposed infrastructure" is the user's goal.
- **The VPN MITM hypothesis** (~30 minutes drafting retraction docs that Lane C immediately falsified). The hunch came before the verification; reversing the order saves both the bad docs and the cognitive thrash.
- **Squad-1 strict-tier dorks** (~15 minutes harvesting 5 hosts that were 5.3% of the real population). Codified as Insight #93 going forward.
- **aimap baseline run on 53 hosts BEFORE adding the Tabby FP** (~9 minutes for a run that couldn't identify Tabby because the FP didn't exist). Reorder: scaffold the FP first if the baseline FP catalog doesn't cover the survey target.
- **Repeated `wc -l` / `tail` / `ps -p` progress checks while waiting for backgrounds.** Should use Monitor or the Bash run_in_background until-loop pattern more aggressively.

## What we still don't know

- Identity / operator behind the 66 MCP credential-theft fleet. Heterogeneous front-end emulation (BBC IoT, FortiSwitch login, Sun-ILOM, Bomgar Remote Support, TVersity Media Server, boa server, Linux/UPnP) on different AWS regions suggests either (a) a sophisticated honeypot operator emulating diverse devices to capture attacker probes, OR (b) a real attacker C2 fleet using the same MCP server template across multiple hijacked hosts. Lane C-style verify on `tools/list` would distinguish (the tool surface is the operator signature), but firing it crosses the Lane D ethical-stop boundary against any non-controlled MCP endpoint.
- True scope of the 884 trustworthy code-loaded hosts. Need the 10,895 full-corpus paired-probe to finish (in progress). Expected outcome: 4,000-6,000 trustworthy live Ollama, some subset code-loaded, narrower than the 884 from the 1,217 suspect.
- Devstral-specific exposed-compute count. The 434-host Devstral figure is from the suspect (contaminated-by-hypothesis) cohort. Lane A's three recommended targets (`149.56.241.75`, `87.139.165.66`, `130.61.103.37`) are paired-probe-stable Devstral-loaded hosts — verify those first to ground the count.

## Custom DCWF wardrobe outfits saved (for future re-use)

| Outfit slug | Atoms | Lane / role |
|---|---|---|
| `cat-tabby-lane-a-recon` | T0028, S0051, K0342, S0001, S0081, T0188, K0177 | Lane A — NICE 541 Pentester |
| `cat-tabby-lane-b-engineering` | T0064, K0177, K0001, K0009, A0123, S0001 | Lane B — DCWF 623 AI/ML Specialist |
| `cat-tabby-lane-c-te` | T0247, T0188, S0081, K0009, K0005, K0006 | Lane C — DCWF 672 AI T&E Specialist |
| `cat-tabby-lane-d-risk-ethics` | K0107, K0118, K0003, K0002, A0123, K0004 | Lane D — DCWF 733 AI Risk/Ethics Specialist |

All persisted at `~/wardrobe/outfits/cat-tabby-lane-*.json`. Load via `wardrobe load <slug>`.

## Generalized DCWF role-outfit template for future Cat-X surveys

Use these as the starting outfit set for any Cat-X parallel-lane survey; rename per category:

```
wardrobe load cat-tabby-lane-a-recon          # Lane A: recon + harvest + active banner
wardrobe load cat-tabby-lane-b-engineering    # Lane B: fingerprint engineering + monitor
wardrobe load cat-tabby-lane-c-te             # Lane C: marker-anchored verify
wardrobe load cat-tabby-lane-d-risk-ethics    # Lane D: classify + ledger + jurisdiction + restraint
```

Build new lane variants by `wardrobe try-on <atom-id>` then `wardrobe save cat-<slug>-lane-<x>-<role>`.

## Censys alternatives (per Nick's directive — "if Censys does not work, find another avenue")

Free / passive engines that overlap with the Censys role at Stage 0b cross-population delta:

| Engine | Free-tier ceiling | Strength | Weakness |
|---|---|---|---|
| **FOFA** | 100 results / search free | strong CN coverage, distinct cert+banner index | reg-required, monthly cap |
| **Quake (Qihoo 360)** | 100 results / day free | CN-strong, IoT depth | reg + WeChat verify |
| **ZoomEye** | 100 results / day free | global, distinct from Shodan crawl | reg-required |
| **Hunter.io** | for email enumeration only | not Censys-class | scope-narrow |
| **BinaryEdge** | 250 queries / month free | EU-strong, similar to Shodan | reg-required |
| **Onyphe** | 1,500 queries / month free | banner + DNS + URL cross-product | distinct API style |
| **GreyNoise Community** | 10,000 queries / day | passive bot/scanner classification | doesn't replace Censys for service discovery |
| **CT logs direct** (`crt.sh`, `Censys CT`) | unlimited | cert-pivot equivalent | only the cert layer, no service banner |
| **alienvault OTX / Pulsedive** | free | threat intel + IP enrichment | not service-discovery primary |

NuClide's existing toolchain choice: route Stage 0b through **FOFA web UI via chrome-devtools MCP browser** (same Cloudflare workaround as Shodan), or **crt.sh CT-log direct for the cert-pivot delta**.

## External tool ecosystems (per directive)

### SANS tools (https://www.sans.org/tools)
Surveyed list to integrate. Curated below by use-case mapping to NuClide chain stages.

- **DShield** — IP attack-data feed. Stage 3 attribution (operator-attack-history cross-ref) and Stage 7 (honeypot signature classification). Free + API.
- **Internet Storm Center handlers' diary** — daily incident-response reports. Stage 2 (cert-pivot context) and Stage 4 (classify by observed-malware-family).
- **REMnux** — Linux toolkit for malware analysis. Bundles ~140 tools incl. yara, ssdeep, bulk_extractor. For Stage 8 module ranking on dropped-payload findings.
- **SOF-ELK** — security ELK stack. For Stage 6 ledger + dashboarding.
- **SIFT Workstation** — DFIR forensics toolkit. Stage 12 (visor-report extension) for IR-handoff format.

### GitHub-sourced tools to integrate (proposed)

| Tool | GitHub | NuClide chain stage | Use |
|---|---|---|---|
| **nuclei** | projectdiscovery/nuclei | Stage 1d / 3v | template-driven verify; complements aimap |
| **httpx** | projectdiscovery/httpx | Stage 0c | active banner alternative to scanner for HTTP-only sweeps |
| **subfinder** | projectdiscovery/subfinder | Stage 2 | subdomain enumeration for cert-pivot follow-through |
| **katana** | projectdiscovery/katana | Stage 4 | JS-bundle deep crawl |
| **gowitness** | sensepost/gowitness | Stage 12 | screenshot dashboard for visor-report |
| **trufflehog** | trufflesecurity/trufflehog | Stage 4 | secret-scanning JS bundles |
| **interactsh** | projectdiscovery/interactsh | Stage 3v | OOB callback for verify primitives (when authorized) |
| **JaeleS** | jaeles-project/jaeles | Stage 1d | signature-based scanner, complements VisorCAS |
| **assetfinder** | tomnomnom/assetfinder | Stage 2 | quick subdomain enumeration |
| **dnsx** | projectdiscovery/dnsx | Stage 2 | DNS bulk resolution |
| **sshprank** | itsmkz/sshprank | Stage 0c | SSH banner sweep |
| **rustscan** | RustScan/RustScan | Stage 0c | fast port scanner, naabu alternative |
| **mcp-scan** (search needed) | various | Cat-MCP follow-up | MCP-specific fingerprint scanner (relevant to the 66 MCP fleet finding) |

(Some of these may already be installed; rustscan and rustscan-alike were retired in favor of naabu/tiptoe per memory `feedback-no-masscan`. Pull what fills genuine gaps; do not replace what works.)

### O'Reilly Learning (per directive)
The colophon CLI + warrant book-grounded skill pattern apply here. For specific gaps:

- **MCP protocol deep-dive** (relevant to the 66 MCP fleet finding) — search O'Reilly for "Model Context Protocol", "MCP server", "JSON-RPC AI" via `syllabus search` or via colophon.
- **OAuth bearer flows for Ollama / vLLM** (relevant to auth-on-default thesis evidence base) — search for "OAuth 2.1", "PKCE", "DPoP" implementation patterns.
- **Next.js SSR build artifacts** (relevant to Lane B's webpack chunk anchor) — confirm the chunk path pattern across Next.js 13 vs 14 vs App Router; Lane B's marker may need version-tolerance.

## What to do next session

1. Finish the 10,895 paired-probe corpus run (in progress; ~6 more minutes at current rate).
2. Lane C verify on Lane A's 3 recommended Devstral targets (`149.56.241.75`, `87.139.165.66`, `130.61.103.37`) using the existing `stage3v-verify.py` extended for Ollama-specific marker probes (`/api/show`, `/api/tags`).
3. The 66-host MCP fleet — separate case study. Survey them via aimap (already classifies as MCP Server). Authorize Lane C to read `tools/list` on the protocol layer (Lane D restraint: read-only, no `tools/call`). The `get_aws_admin_credentials` finding alone, if confirmed against the JSON-RPC `tools/list` shape, is a CRITICAL exposed-tool fleet warranting CISA / CERT routing.
4. Implement the Stage 0 sandbox-MITM gate as a chain runner prerequisite.
5. Rewrite Lane D's retraction in the case study to reflect the corrected Lane C verdict (wire clean, MCP fleet is real, 884 hosts are trustworthy).
6. Push the work to GitHub.
