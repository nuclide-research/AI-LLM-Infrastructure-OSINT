---
type: survey
category: cat-tabby
slug: cat-tabby-2026-06-09
date: 2026-06-09
researcher: nuclide
status: in-progress
---

# Cat-Tabby — Code-Assistant Stragglers — 2026-06-09 Survey

_NuClide Research · 2026-06-09 · 4-platform survey: Tabby + Sourcegraph + Continue.dev + Devstral_

## Wardrobe + syllabus stance

- Outfit `ai-infra-hunt` — 13 atoms covering T0028 (authorized pentest), T0188 (remediation analysis), K0342/S0001/S0051 (vuln tools + scan recognition), T0247 (T&E + verification), K0107/K0118 (cross-jurisdiction + evidence preservation), T0064 (R&D research-engineering)
- Syllabus context: Les Dissonances (NDSS — cross-tool harvesting in pool-of-tools LLM agents), ObliInjection (NDSS — multi-source prompt injection). Together they license the restraint posture: code-completion endpoints (`/v1/completions`, `/.api/completions/stream`) ARE the exploit primitive these papers describe; enumeration via model-list endpoints (`/v1beta/models`, `/.api/graphql site.productVersion`) is the legal-equivalent. **All `/v1/completions` calls hard-refused against survey-set hosts (see `stage3v-verify.py` `DO_NOT_CALL` set).**

## DCWF role-agent lane assignment

| Lane | Role | Stage ownership | Atoms exercised |
|---|---|---|---|
| A | NICE 541 Pentester | -1 → 0 → 0b → 0c → 1c | T0028, S0051, K0342, S0001, S0081 |
| B | DCWF 623 AI/ML Specialist | 0d → 1a → 1b → 1cm → 1d | T0064, K0177 — wrote Tabby aimap fingerprint, ran aimap+monitor |
| C | DCWF 672 AI T&E Specialist | 2 → 2b → 3v → 4 → 8 | T0247, T0188 — marker-anchored verify, restraint enforcement |
| D | DCWF 733 AI Risk/Ethics Specialist | 3 → 6 → 7 → 9-13 | K0107, K0118 — jurisdiction + evidence preservation, restraint |

## Summary

Four-platform code-assistant straggler survey. Stage 0 Shodan harvest pulled 165 unique IPs across the four platforms (Continue.dev verified CLI-only and excluded; Devstral reframed as model-fingerprint-via-serving-stack and queued as aimap enhancement). The squad-1 port:8080-constrained Tabby dork set caught 5/94 = 5.3% of the real Shodan-visible Tabby population — corrected via the unconstrained `http.title:"Tabby"` dork at 94 unique IPs, of which port 9090 dominates at 42.6% per the docker-compose quickstart default (binary `--port` flag default is 8080 — codified as Insight #93).

Stage 0c scanner active-banner ran 70.7% live across the 75-IP baseline cohort (2.4× the Insight #77 ~29% baseline — codify candidate for recent-harvest live-rate variance). Stage 0d scaffolded a new Tabby aimap fingerprint with marker discipline (`/v1/health` chat_model+webserver conjunctive + `/auth/signin` <title>Tabby), committed and rebuilt aimap v1.9.53.

Stage 1b aimap on the combined 165-IP cohort identified 60 services / 12 findings / 1 critical + 5 medium. The critical (Metabase setup token at 15.235.214.158:3000, operator Midsuit/avolut.midsuit.com) was a cross-category incidental — not a Cat-Tabby finding but logged for cross-survey-correlation per methodology Stage 6.

Stage 3v Lane C verify ran 1,523 marker-anchored probes across 197 unique hosts with Lane D ethical-stop boundary enforced at code level (10-endpoint DO_NOT_CALL set, 0 violations). 70 unique IPs confirmed as Tabby (59) or Sourcegraph (11) identities. **0 of 70 confirmed identities returned an open compute primitive or public-repository leak.** This is a strong auth-on-default thesis confirmation for the modern Tabby v0.11.0+ docker-compose deployment cohort and the Sourcegraph Tier-C cohort. Per methodology §1, the negative result is publishable evidence for the thesis (auth-on-default strengthens across OSS generations under disclosure pressure — Insight #40).

Three Lane D-discovered squad-1 intel corrections drove the final scope:

1. Squad-1 reported Tabby Shodan-dark (5 host estimate). Reality: 94 Shodan-visible. → Insight #93 (port-assumption-under-counts).
2. Squad-1 reported `/v1/health` always-open on all versions. Reality: confirmed Tabby v0.11.0+ host returns 401 on `/v1/health`, `/v1beta/models`, `/v1beta/server_setting` — the entire operational API surface is gated when admin is configured. → Insight #94 (hybrid Tier-A*/C platforms).
3. Squad-1 reported no nuclei templates. Reality: `s4e-io/tabby-panel.yaml` exists in projectdiscovery/nuclei-templates.

The 3v verify script (`stage3v-verify.py`) implements Lane D restraint at code level: every do-not-call endpoint (admin-create POST, completions endpoints, GraphQL mutations) is hard-refused before any probe runs. The same script is the per-survey verify primitive going forward for code-assistant categories.

## Stage 0 contamination retraction (Devstral cross-section, 2026-06-09 later session)

**RETRACTED:** the Cat-Tabby + Devstral re-validation re-run later on 2026-06-09 produced a Stage 0 cross-section (1,217 code-model-loaded hosts across the 10,895-host confirmed-unauth Ollama corpus, 434 of them Devstral; shadow-sweep surfacing 117 hosts with port 9090 open; direct Tabby identity probe matching 66 as "confirmed Tabby") that is RETRACTED pending Lane A clean-route paired-probe re-validation.

**Cause:** Stage 0 ran while routed through Mullvad WireGuard (`us-phx-wg-206` -> Miami exit). Lane A re-probed 3 of the 66 Tabby hits and 3 of the 1,217 code-model hits moments after the first pass. The Tabby `/auth/signin` re-probes returned EMPTY bodies (no `<title>Tabby`). The Ollama `/api/tags` re-probes returned DIFFERENT model loadouts on the SAME IP (e.g. `qwen2.5:1.5b` substituted where `codellama:13b` had been reported). Same IP, same endpoint, minutes apart, different body. The contamination class is L7 response rewriting — VPN-exit transparent proxy or upstream MITM substituting templated responses on the first pass.

**Verification rung (per Insight #68):** the contaminated cross-section is inner-A / outer-0 — logic-only, no live host actually exercised via a clean route. The numbers are reproducible by re-running through the same contaminated path; they are confident and wrong.

**Critical note:** the contamination was discovered ONLY because Lane A re-probed. Without the paired-probe step, the 1,217 / 434 / 117 / 66 numbers would have been published as findings. The methodology gap is documented at `analysis/2026-06-09-cat-tabby-devstral-vpn-contamination.md`; the candidate codify is at `methodology/insight-96-paired-probe-mandatory-when-vpn-routed.md` (Stage 0 sandbox-MITM check + paired-probe schema as MANDATORY prerequisites under non-local routing).

**Discipline win (Lane D, K0107):** zero disclosures sent on the basis of the contaminated cross-section. Restraint held even with confident-looking internal numbers. **No operator was contacted. No CERT was contacted. No vendor was contacted.**

**Evidence preservation (Lane D, K0118):** `probe-results.jsonl`, `code-loaded-hosts.jsonl`, `tabby-on-shadow-9090.jsonl`, `shadow-sweep.jsonl`, and `sanity-probe.jsonl` are preserved INTACT in `shodan/cat-tabby-devstral-2026-06-09/`. `EVIDENCE-CONTAMINATED.txt` in that directory carries the chain-of-custody note.

**Scope of retraction:** the retraction is bounded to the Devstral cross-section produced by the 2026-06-09 later-session re-run. The earlier same-day 4-platform Cat-Tabby survey (this case study's primary subject) used Stage 3v marker-anchored verification with conjunctive markers (`chat_model` + `webserver`) and TLS-CN cross-reads that are substantially harder for a templated-response layer to forge; the 59 Tabby + 11 Sourcegraph identifications and the 0/62 open-compute-primitive negative result are not retracted, but they are flagged for clean-route re-confirmation when the Stage 0 MITM gate is in place.

---

## Methodology

The Cat-Tabby survey ran the standard NuClide chain on four code-assistant platforms (Tabby + Continue.dev + Sourcegraph/Cody + Devstral). Stage -1 dispatched four parallel research squads via the Agent tool — one per platform — producing pre-assessment intelligence + tome platform JSONs before any active probe.

### Pre-assessment intelligence outcomes (Stage -1, four squads)

| Platform | Scope verdict | Population estimate (squad-1) | Notes |
|---|---|---|---|
| Tabby (TabbyML) | Server platform, in scope | 150-600 live :8080 | Greenfield — no aimap FP, no nuclei templates (squad-1 missed `s4e-io/tabby-panel.yaml`) |
| Continue.dev | **CLI/extension-only, out of scope** | 0 Continue-branded hosts | Realistic finding = `config.yaml` leak from public repos (separate engagement scope) |
| Sourcegraph + Cody | Server platform, in scope | 500-2,000 strict | Tier-C auth-on-default; first-admin-wins race window + `auth.public:true` cohort = hunt focus |
| Devstral | **Model-fingerprint-via-serving-stack** | 150-300 Devstral-loaded hosts | Cat-coherence: Devstral-on-Ollama is natural backend for Tabby/Continue/Cody |

### Stage 0 — Shodan harvest

Population revealed via shodan-fetch in-page `Promise.all` (web-UI SSR, 0 query credits) with chrome-devtools MCP browser. Squad-1's port-:8080-constrained dorks caught only 5/94 Tabby hosts (5.3%). The unconstrained `http.title:"Tabby"` dork pulls 97 (94 deduped). Real Tabby population distribution:

| Port | Count | % of population |
|---|---|---|
| 9090 | 40 | 42.6% |
| 8000 | 11 | 11.7% |
| 443  | 8  | 8.5% |
| 80   | 7  | 7.4% |
| 9000 | 6  | 6.4% |
| 8080 | 5  | 5.3% |
| Long tail (9999, 8010, 12399, 8180, 2048, 9190, 8003, 9443, 9165, 8001, 39001, 8008, 9445, 9099, 3000) | 17 | 18.1% |

**Codify candidate (Insight #21 sharpening):** A pre-assessment squad's port assumption baked into every dork variant produces systematic under-counting at population scale. The fix is mechanical: every dork set must include at least one variant without `port:N` constraint. The Tabby cohort is the canonical example — port 9090 is the operator-default (because Tabby's webserver mode listens there in the docker-quickstart recommendation), but the squad fixated on :8080 because squad-1 read the `--port` flag default (which was 8080 in earlier Tabby releases).

### Stage 0c — scanner active-banner

scanner v1.x ran 75 IPs × 21 ports → 53/75 live (**70.7% live rate**, 2.4× the Insight #77 ~29% population baseline). This is the second methodology codify candidate:

**Codify candidate (Insight #77 sharpening):** the ~29% live-rate floor is the *population average over rolling Shodan crawl staleness*; for survey cohorts harvested within ~7 days of a recent crawl, live rates run 2-3× higher. NuClide Cat-Tabby's 70.7% vs the 29% expected.

### Stage 0d — aimap fingerprint scaffolded for Tabby

aimap v1.9.53 had no Tabby fingerprint. Added in `ai-recon/aimap/fingerprints.go` between Sweep AI and Tabnine (alphabetical order). Two-probe schema per the matcher contract (`(Name, DefaultPorts[], Probes[], Severity)`):

```go
Name:         "Tabby (TabbyML)",
DefaultPorts: []int{9090, 8080, 8000, 443, 80, 9000, 9999, 8443},
Probes: []Probe{
    {Path: "/v1/health", Matches: []MatchCond{
        {Type: "status_code", Value: "200"},
        {Type: "json_field", Field: "chat_model"},
        {Type: "json_field", Field: "webserver"},
    }},
    {Path: "/auth/signin", Matches: []MatchCond{
        {Type: "status_code", Value: "200"},
        {Type: "body_contains", Value: "<title>Tabby"},
    }},
},
Severity: "high",
```

Marker discipline: `chat_model` + `webserver` are Tabby-unique together (no other AI service emits the two together at `/v1/health`). The `/auth/signin` probe handles the v0.11.0+ webserver cohort; pre-v0.11.0 falls back to the API probe.

Sourcegraph fingerprint already existed in aimap (squad-3 missed it). Two-probe schema: `/.api/graphql` body anchor on `"Private mode requires authentication"` (locked-down cohort identification), `/sign-in` on title `"Sign in - Sourcegraph"`. Note: the existing Sourcegraph FP misses the `auth.public:true` cohort by design — the hunt's high-severity target. Lane C's `stage3v-verify.py` adds the missing probe (`POST /.api/graphql { repositories(first:1) { nodes { name } } }`).

### Stage 1b — aimap on 53-IP baseline cohort

Baseline aimap on the live 53 IPs (pre-Tabby-FP) returned:

- **13 Sourcegraph identifications** (auth-on locked-down cohort, all probing correctly)
- 4 false positive identifications (Coqui XTTS + dcm4che + Apollo GraphQL) → VisorCAS signature candidates

The 13 Sourcegraph hits are working-as-designed authenticated deployments. Hunt focus shifts to the `auth.public:true` and unclaimed-admin-state cohorts via Lane C's verify script.

### Stage 1cm — agent-logging-system FP scan

```
FALSE-POSITIVE CANDIDATES (>30% auth_unknown/no-findings rate):
  aimap.dcm4che / dcm4chee-arc DICOM Archive  100% error rate  (4/4)
  aimap.Sourcegraph                           100% error rate  (13/13)   ← by-design, locked-cohort
  aimap.Coqui XTTS                           100% error rate
  aimap.Apollo GraphQL API                    40% error rate  (2/5)
```

The Sourcegraph 100% is by design (locked-cohort = enumerator returns empty). dcm4che + Coqui XTTS + Apollo GraphQL are real VisorCAS signature targets — they cross-fire on Sourcegraph-class hosts (same `/.api/graphql` endpoint, similar TLS/nginx stack).

## Findings (mid-survey, Lane B in progress)

[PENDING aimap-combined on 165 IPs]

### Tabby hosts confirmed (so far)

| IP:port | Operator (TLS CN / rDNS) | Auth State | Notes |
|---|---|---|---|
| 5.78.203.59:8080 | `ide.cohesia.ai` (Hetzner US) | **NONE — /v1/health open, /v1/completions optional-Bearer** | Squad-1 strict dork. Stage 3v verify pending. |
| 43.133.248.37:8080 | (APNIC KR) | Pending Lane C | Real Tabby + gunicorn:3001 |

### Sourcegraph hosts confirmed (so far)

| IP:port | Operator (TLS CN / rDNS) | Notes |
|---|---|---|
| 62.149.163.76:7080 | `*.dkr.srl` (DKR S.r.l., Italy) | Default port pair 7080+7443+8443. Verify pending. |
| 209.145.62.76:7080 | (Contabo US) — **+:9200 Elasticsearch on same /32** | Insight #12 stacked-exposure ready-made |
| 35.195.86.189:7080+:443+:80 | (Google Belgium) | 3-port SG, eol-product tag |
| 51.91.31.20:81 | (OVH FR) | Caddy alt-port self-host |
| 5.161.61.142:81 | (Hetzner) | Caddy alt-port self-host |
| 159.65.244.239:443, 35.161.153.130:443 | (DigitalOcean/AWS) | Standard :443 deployments |
| 35.190.92.144:80, 34.107.119.99:80, 54.201.131.91:80, 34.77.102.18:80 | (Multi-cloud) | :80 deployments |

## Risk assessment

[FILLING IN — Stage 7 VisorScuba scoring pending]

## Limitations and negative space

- **Censys (Stage 0b) deferred** — free-tier search requires org-id (returns 403 from cencli); UI-only path needs the dev-browser hand-off Nick controls. We deliberately did not pursue (chain still runs without it; cross-population delta untapped this run).
- **Stale Tabby host 5.9.83.215** — scanner reports all 21 ports dead. Two interpretations: (a) Shodan cache stale + host firewalled since crawl; (b) host actively blocks Mullvad VPN exits. Cannot distinguish from one survey.
- **Continue.dev verdict** — CLI-only means brand-population is by-design zero. The realistic Continue-related finding pattern is github-code-search of `config.yaml` leaks; that surface is outside the chain scope.
- **Devstral verdict** — model-fingerprint deep-enum over existing Ollama/vLLM enumerators is the proper next step; not exercised this survey, queued as aimap enhancement.

## Codify candidates (Stage 7 → numbered Insights)

1. **Insight candidate A:** "Client-side-only platforms produce server-side findings via upstream-gateway exposure." A brand-name survey of a CLI-only product becomes a *redirection survey* — the brand becomes the lookup key for the upstream gateway population (Continue.dev → Ollama + vLLM + LiteLLM gateways).

2. **Insight candidate B:** "Model-fingerprint deep-enum is a separate axis from server-fingerprint identity." Cat-NIM / Cat-53 / Cat-Tabby (this survey) all share the pattern. The auth-on-default thesis sharpens: failures concentrate at the *serving-stack* layer, but the *loaded-model-family* layer is the operator-attribution + impact-class differentiator.

3. **Insight candidate C:** "A pre-assessment squad's port assumption baked into every dork variant systematically under-counts alt-port deployments." Mandatory fix: include at least one dork variant without `port:N` constraint. Tabby is the canonical example — squad-1 fixated on :8080, missed :9090 (the real dominant port at 42.6% of population).

4. **Insight candidate D:** "Active-banner live-rate floor (Insight #77, ~29%) is the population average over rolling Shodan crawl staleness; survey cohorts harvested within ~7 days of a recent crawl run 2-3× higher." NuClide Cat-Tabby's 70.7% vs the 29% baseline.

5. **Insight candidate E (sharper version of #16):** "An auth-on-default Tier-C platform with explicit auth-off-by-design endpoints (Tabby's `/v1/health`, `/v1beta/models`, `/v1beta/server_setting` are always-open even on webserver-enabled v0.11.0+) creates a hybrid Tier-A*/C surface that escapes the existing tier vocabulary."

## Toolchain provenance

Wardrobe outfit: `ai-infra-hunt` (T0028 / S0051 / K0342 / S0001 / T0188 / T0247 / K0107 / K0118).
Syllabus context: Les Dissonances (NDSS), ObliInjection (NDSS) — informed do-not-call endpoint set.
Stage -1: Agent tool dispatching 4 parallel general-purpose research squads.
Stage 0: shodan-fetch in-page Promise.all via chrome-devtools MCP browser (0 query credits).
Stage 0c: scanner v1.x at 60 threads.
Stage 0d: aimap source edit at `~/ai-recon/aimap/fingerprints.go` between Sweep AI and Tabnine; built and installed v1.9.53.
Stage 1b: aimap two runs (baseline 53 + combined 165).
Stage 1cm: `agent-logging-system/examples/aimap_monitor.py`.
Stage 3v: `stage3v-verify.py` (this survey directory) — Lane D restraint enforcement at code level via DO_NOT_CALL constant.
Tome corpus writes: `~/tome/platforms/{tabby,continue-dev,sourcegraph-cody,devstral}.json` (all CANDIDATE until 3v promotes).

<!-- ksat-tag:auto-generated:start -->
## DCWF KSAT coverage

Wardrobe outfit: `ai-infra-hunt`.

- **672 (AI Test & Evaluation Specialist):** T5919 (adversarial T&E in operational environments — marker probes), K7044 (V&V tools — aimap+monitor+VisorCAS), S7067 (low-prob/high-impact ML risks — restraint ethic), T5904/T5858 (technical risk assessment per host), K7004 (T&E frameworks)
- **733 (AI Risk & Ethics Specialist):** T5893/T5882 (responsible-AI practices — names ARE the finding), K7040 (PHI/PII handling — bag-of-fields schema classification, no record reads), T5868 (risk assessment process per survey)
- **NICE 541:** T0028 (authorized pentest), T0188 (audit findings + remediation), K0342 (pentest principles), S0001 (vuln-scan recognition), S0051 (pentest tooling), T0247 (T&E + verification), K0107 (cross-jurisdiction), K0118 (evidence preservation)

<!-- ksat-tag:auto-generated:end -->
