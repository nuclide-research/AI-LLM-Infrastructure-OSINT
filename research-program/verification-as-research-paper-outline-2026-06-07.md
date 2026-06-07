# Verification Is The Load-Bearing Stage — Paper Outline

_Phase 4 of the 2026-06-07 9-item plan. Scaffolds, not the paper. Body sections that depend on Phase 1 results are marked **[BLOCKED]**._

**Working title:** "The Verification Bottleneck: Why Scanning Is Easy And Method Correctness Lives in the Last Stage" (or similar; better titles in the candidate bin at the end).

**Target length:** 6,000 to 8,000 words.

**Audience:** mixed. Primary: defenders (CISO, blue team, SOC lead) who get population-scale scanner reports and need a framework for filtering them. Secondary: AI-infra vendors who get disclosure reports and need to understand how the researcher arrived at the finding. Tertiary: DoD-adjacent readers who recognize the DCWF vocabulary (added late so it does not dominate).

**Thesis (one sentence):** At population scale, the verification stage is where method correctness is decided; the scan only produces candidates, and 18 of 21 codified insights from a yearlong AI-infra research program are verification-stage failures, not scanning-stage failures.

---

## Section map

### 1. The premise (~400 words)

Open with the AI-infra surface and why population-scale matters now. Establish that auth-on-default is the macro thesis (Insight #40 — auth strengthens across OSS generations under disclosure pressure). Establish that a scan is cheap and a candidate set is large. Establish that the load-bearing decision is what we do with that candidate set.

No data here yet. Set up the rest of the paper.

### 2. The discipline (~600 words)

Define the pipeline: Discover → Fingerprint → **Verify** → Attribute → Classify → Ledger → Score → Codify. Emphasis on verify. Explain "200-with-data" as the verification gate: a finding requires reading something. Explain restraint: names ARE the finding; do not exfiltrate.

Cite NuClide methodology canon by section number (Sections 2 and 3). Quote the one-sentence version from Section 0 of the methodology.

### 3. The evidence — 21 codified insights, 18 verification-stage (~1,200 words)

Walk through the breakdown of Insights #1 through #80 (currently). Bucket each into one of three categories:

- **scanning-stage** (which dork to use, what port to ask, what banner string to match)
- **verification-stage** (whether the candidate is real, whether the 200 is meaningful, whether the framing holds at scale, whether the FP catalog applies)
- **codification-stage** (how to summarize the survey, what the candidate insight should say, what the disclosure should look like)

Count the buckets. The claim is 18/21 verification. Walk through 5 representative insights as worked examples (one per failure mode):

- Insight #40 (auth-on-default) as the macro thesis — the verification result
- Insight #68 (depth × breadth rung grid) — the verification rubric
- Insight #73 (header-versioned APIs evade headerless fingerprinters) — verification-stage method failure
- Insight #77 (active-banner-prefilter) — verification-stage data shape failure
- Insight #80 (DMARC funding-stage proxy) — verification-stage byproduct insight (it pays dividends only once you re-probe at scale)

This section is the spine. Do not rush it.

### 4. The case — Cat-03 Model Serving, 39 candidates to 6 verified (~1,500 words)

The full worked example. Walk through it stage by stage.

- Stage 0: 5,018 IPs harvested via Shodan + Censys.
- Stage 0c (scanner): 158 live.
- Stage 1b (aimap): 72 services classified, 20 CRITICAL / 19 HIGH (39 candidates).
- Stage 3v (verification): 6 verified-unauth, 9-class FP catalog.
- Candidate Insight #78 (One API root/123456 class-level default): **REFUTED** at population (0/9). Single-host outlier promoted to class-level claim. Verification caught it.
- Candidate Insight #79 (Ollama Connect subscription hijack): **CONFIRMED** with hard proof.
- Candidate Insight #80 (provincial Indonesian gov): **RETRACTED** — VisorScuba assessed ledger-wide, not survey-scoped.
- Candidate Insight #81 (framework catch-all FP class): proposed from FP catalog.
- Candidate Insight #82 (front-end-secured / backend-exposed asymmetry): proposed from F5+F6 chain.

The headline number: 39 / 6 = 6.5x correction factor. The pre-verification framing was wrong on most of the candidate set.

Use the exact wording from `case-studies/commercial/cat03-model-serving-survey-2026-06-05.md` where possible. Cite by section.

### 5. The vocabulary — DCWF KSAT coverage matrix (~800 words)

The DCWF AI work-role overlay (Roles 672, 733, overlap). Walk through the auto-tagger build, the 240-case-study retro-tag, the matrix.

Headline numbers:
- K1158 (cybersecurity principles): 100%
- K22 (networking): 98%
- K7003 (AI security risks): 97%
- S7068 (org/project AI risks): 96%
- K7020 (DoD AI Ethical Principles): **0%** ← we don't speak DoD vocabulary natively
- K7045 (AI lifecycle): 3%
- S7076 (dataset bias): 5%

Frame this as honest gaps. The program produces DoD-relevant evidence without using DoD vocabulary. The retro-tagger fixes the vocabulary; the underlying coverage gaps (K7045 lifecycle, S7076 bias) are genuine and worth publishing as such.

### 6. The byproducts (~600 words)

Two methodology byproducts from the same week that illustrate the verify-at-scale principle:

- **Insight #80 (DMARC funding-stage proxy)** — the n=7 pattern from Cat-33 looked clean, but only the n=31 re-probe (and the n=410 sweep) revealed the pattern's actual bounds and the AI-infra side finding (53.4% absent DMARC vs ~13% in AI-security).
- **[BLOCKED on Lane 1A] Cat-29 Argo :2746** — ssl:"Argo Workflows" dork found 0/33 unauth, but :2746 was Shodan-dark. The active scan either confirms or refutes the dork-population-substitution candidate. Write this section once the lane returns. **If confirmed: this is a clean worked example of how a dork can blind you to the unauth tier. If refuted: this is a clean worked example of how a hypothesis dies under verification — and that is the point.**

### 7. The implications (~600 words)

So what?

For defenders: a scanner report at population scale is a candidate set, not a finding set. The 6.5x correction in the Cat-03 worked example is not unusual. Bake verification into the workflow or the headline number lies.

For vendors: when a NuClide disclosure arrives, the framing has already been re-probed. The candidate-to-finding ratio is small by design. This is not a bug-bounty firehose; it is a curated set.

For the field: 18-of-21 verification-stage failure rate is the methodology meta-finding. The interesting research lives at the verify step, not the scan step. Publishing scanners is easy; publishing verification rubrics is rare.

### 8. Limits and caveats (~400 words)

Honest caveats:

- 21 insights is a small denominator. The 18/21 ratio will move with more data.
- "Verification-stage" vs "scanning-stage" is sometimes a judgment call; we coded it deliberately, but a second coder would disagree on edge cases. Methodology section in appendix lists the disputed ones.
- The DCWF overlay is post-hoc; the program was not designed against the framework. Re-running the framework against a program designed for it would surface different gaps.
- The Cat-29 worked example (if it lands) is one host class out of many; the dork-population-substitution pattern might be specific to ssl: dorks and not generalize.

### 9. Conclusion (~200 words)

One paragraph. The closing claim: verification is the load-bearing stage; the scan is the easy part; if you only invest in scanning, your population-scale finding rate is confident and wrong. NuClide invests in verification; that is why the candidate-to-finding ratio looks the way it does; that is why the insights bucket the way they do; that is the program.

---

## Pre-blocked sections to write now (not blocking on Phase 1)

- Section 1 (premise) — fully writeable now.
- Section 2 (discipline) — fully writeable; cites methodology canon.
- Section 3 (21 insights bucketing) — needs the bucketing exercise done first; that is the actual work of this section. Spend the next focused block on this.
- Section 4 (Cat-03) — fully writeable from existing case study.
- Section 5 (DCWF) — fully writeable from today's matrix.
- Section 6 (DMARC byproduct) — fully writeable. Cat-29 byproduct is **[BLOCKED]**.
- Section 7 (implications) — writeable.
- Section 8 (caveats) — writeable.
- Section 9 (conclusion) — write last.

## Pre-bucketing exercise (Section 3 prep)

Open every insight file 1-80, code each one as scanning / verification / codification. Tally. This is the table that anchors Section 3. Half a day of focused work; can do this incrementally between agent returns.

## Candidate alternative titles

- "The Verification Bottleneck"
- "Population-Scale Finds Are Candidate Sets, Not Findings"
- "Why 18 of Our Last 21 Lessons Were About the Last Stage"
- "Scanning Is Easy; Method Lives at the Verify Step"
- "200-With-Data: A Discipline for Population-Scale Security Research"

## Output destinations

- Draft: `~/AI-LLM-Infrastructure-OSINT/research-program/papers/verification-bottleneck-DRAFT.md`
- Final: nuclide-research.com `/papers/` (once polished) + research-program/papers/ archive
- Citations: per-insight `methodology/insight-NN-*.md`, per-case `case-studies/commercial/*.md`, per-matrix `data/dcwf-ksat-coverage-matrix-2026-06-07.csv`
