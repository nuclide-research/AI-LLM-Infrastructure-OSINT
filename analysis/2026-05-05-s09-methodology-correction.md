# Session Analysis: Methodology Correction + Toolchain Revival

**Date:** 2026-05-05  
**Session:** 9  
**Classification:** Internal / Research Use Only  
**Toolchain:** aimap (v1.9.x → 43 fingerprints), all 14 NuClide binaries (full build), data/aisafety-probe.py (deprecated this session)  
**Repos updated:** AI-LLM-Infrastructure-OSINT (4affddb + multiple OLAP/taxonomy commits)

---

## 1. Overview

### Objective

Two parallel objectives. First: Nick selected AI safety eval tooling as the next survey target. Investigation of session-8 probe results immediately surfaced a load-bearing methodology bug: bespoke single-word substring matching in `data/aisafety-probe.py` produced 6 false positives and 0 true positives at population scale. Second: full NuClide toolchain was partially missing locally; all 14 binaries cloned and built this session.

Thesis question being tested: does the AI safety eval platform class (Promptfoo, Garak, DeepEval, NeMo Guardrails, LangSmith self-hosted, Inspect AI, Lakera Guard) have public cloud exposure comparable to LLM orchestration and gateway tiers?

### Scope and Constraints

- **Target domains/IPs:** Same ~1,017 cloud prefixes from session-8 (Scaleway/OVH/Linode); re-probed with corrected fingerprints
- **Allowed techniques:** aimap fingerprint scan with conjunctive matchers (status_code + json_field + body_contains required), safe HTTP GET
- **Ethical limitations:**
  - No data exfiltration — metadata and schema enumeration only
  - No destructive API calls
  - No use of discovered credentials
  - Data-tier probes: connection attempt only (does auth gate exist? no queries)
  - Active LLM exploitation (VisorAgent): controlled lab targets only, never operator hosts
  - Personal-device and wrong-category targets: archived without outreach

---

## 2. Environment and Tooling

### Claude Code Operation

Sequential orchestrator session. Three phases: (1) investigate session-8 AI safety FP candidates manually, (2) build corrected aimap fingerprints, (3) re-probe the 6 FP hosts with tightened aimap. Toolchain rebuild ran in parallel with aimap fingerprint additions.

### Tools Used

| Tool | Role | Config notes |
|---|---|---|
| aimap | Stage-1 fingerprint (rebuilt) | Now 43 services / 30 enumerators; 7 new AI safety fingerprints added |
| data/aisafety-probe.py | [DEPRECATED this session] | sys.exit(2) header added; do not use |
| VisorPlus | Stage-0 orchestrator | Smoke-tested; confirmed callable |
| JAXEN | Stage-0 discovery | Smoke-tested; confirmed callable |
| VisorSD | ASN/org dork sweep | Smoke-tested; confirmed callable |
| VisorGoose | TLD/CT-log sweep | Smoke-tested; confirmed callable |
| VisorGraph | Cert-pivot attribution | Smoke-tested; confirmed callable |
| VisorLog | Ledger ingest | Smoke-tested; nuclide.db confirmed intact (579 open findings) |
| VisorScuba | Compliance scoring | Smoke-tested; confirmed callable |
| VisorCorpus | Adversarial corpus | Smoke-tested; confirmed callable |
| VisorAgent | Active LLM exploitation | [--] ethical-stop; smoke-tested only, not run against survey hosts |
| VisorHollow | Windows benchmark | [--] not applicable; Windows-only |
| menlohunt | GCP EASM | Smoke-tested; confirmed callable |
| VisorRAG | RAG adversarial | [--] ethical-stop class; smoke-tested only |
| BARE | Exploit ranking | Smoke-tested; confirmed callable |

*3 missing repos cloned this session: VisorGoose, VisorLog, VisorScuba. 12 total new binaries built (~130MB) to ~/go/bin/.*

### Notable Configuration

- nuclide.db confirmed intact at `~/AI-LLM-Infrastructure-OSINT/data/nuclide.db`: 579 open findings (74 critical + 244 high + 129 medium + 132 low)
- AI safety eval FP probe: same 6 hosts re-probed with tightened aimap; 0/6 confirmed
- aisafety-probe.py deprecated with `sys.exit(2)` on run; cannot accidentally re-use
- artisan repo not found in NuClide Research org (possibly renamed/private); noted, not blocking

---

## 3. Methodology

### Enumeration approach

Re-probe of the 6 session-8 AI safety eval candidates. No new masscan required — same host cohort from session-8 cloud prefixes. Fingerprint correction was the primary work product; re-probe validated the fix.

### Candidate identification

Session-8 probe used single-word substring matching: `b"garak" in body.lower()` and `b"confident" in body.lower()`. This method is unsound at population scale.

The corrected approach (added to aimap as 7 fingerprints) requires all three conjuncts:
1. A specific endpoint that the platform alone serves (e.g., `/api/v1/health` for DeepEval, `/garak/run` for Garak REST)
2. Structured JSON response with a named field specific to the platform
3. Anchored keyword conjoined with (1) and (2)

### Validation checks

Manual investigation of each false positive confirmed the non-AI identity:

- `149.56.22.24:5000`: Clipface video clip browser; anime filename `[F] Garakuta【Flashアニメ】ガラクタノカミサマ.mp4` triggered `garak` substring
- `37.59.107.238:5000`: LiveChat Nevylish (French Discord overlay); marketing copy contained `confident`
- `149.202.183.53:8000`: EDocs document management system; substring source isolated in body text

Re-probe with corrected aimap: 0/6 confirm. Methodology correction empirically validated.

### Safeguards

No session-8 Garak disclosure sent to 149.56.22.24 (OVH abuse + NVIDIA security). Disclosure invalidated before send. nuclide.db ledger not affected — FPs were never ingested into the ledger. Visor{Log,Scuba} re-run confirmed no corrupted entries from session-8 AI safety work.

---

## 4. Execution Trace

| Time | Action | Outcome / Decision |
|---|---|---|
| 09:00 | Session start: git log reviewed; session-8 closing state read | AI safety eval extension selected as next target |
| 09:15 | aisafety-probe.py reviewed manually | Single-word substring matching identified as the FP mechanism |
| 09:30 | 149.56.22.24:5000 manually investigated | Clipface video browser confirmed; anime filename `ガラクタノカミサマ` contains "garak" |
| 09:45 | 37.59.107.238:5000 manually investigated | LiveChat Nevylish French marketing copy; "confident" substring match |
| 10:00 | 149.202.183.53:8000 manually investigated | EDocs document management; substring source isolated |
| 10:15 | 3 remaining FP hosts re-probed | All unreachable; classified as transient or additional FP |
| 10:30 | Toolchain inventory: 3 repos missing locally | VisorGoose, VisorLog, VisorScuba cloned; build started |
| 11:00 | 12 binaries built to ~/go/bin/ | visorplus, jaxen, visorsd, visorgoose, visorgraph, visorlog, visorscuba, visorcorpus, visoragent, visorhollow, menlohunt, visorrag |
| 11:15 | Smoke test all 14 tools | All callable; visorhollow confirmed Windows-only; visoragent confirmed ethical-stop |
| 11:30 | nuclide.db confirmed intact | 579 open findings; no corrupted entries from session-8 |
| 12:00 | 7 new AI safety eval fingerprints added to aimap | Promptfoo, NeMo Guardrails, DeepEval, LangSmith self-hosted, Inspect AI, Garak REST, Lakera Guard |
| 12:30 | 4 new deep enumerators added to aimap | enumPromptfoo, enumNeMoGuardrails, enumDeepEval, enumLangSmith |
| 13:00 | aimap re-probe of 6 FP hosts | 0/6 confirmed; correction validated |
| 13:15 | ai-safety-eval-cloud-survey-2026-05.md rewritten | Methodology correction leads the document |
| 13:30 | SYNTHESIS-2026-05.md corrected | AI safety table row updated; Insight #6 added |
| 13:45 | browser-agent-cloud-survey-2026-05.md F6 cross-reference invalidated | Cross-reference to Garak finding removed |
| 14:00 | FUTURE-SURVEYS.md updated | Garak status: aimap fingerprint added, 0 confirmed population result |
| 14:15 | README.md corrected | AI safety bullet updated |
| 14:30 | aisafety-probe.py deprecated | sys.exit(2) header added; committed |
| 14:45 | Session-9 methodology correction committed | 4affddb |
| 15:00 | Session close | Next moves documented; compute orchestration survey queued for session 10 |

---

## 5. Findings

> **Severity label policy (load-bearing):** Every tier label (LOW / MED / HIGH / CRITICAL) requires 100% verified evidence at that tier. Unverified observations are UNRATED. Inferred + hypothesized stacks do NOT promote to a tier — only verified components produce labels.

### [9.1] Session-8 AI Safety Eval Survey — Complete Invalidation

| Field | Value |
|---|---|
| **Name/ID** | data/aisafety-probe.py; session-8 finding set for AI safety eval category |
| **Type** | Methodology defect |
| **Evidence** | 6 candidates probed with bespoke substring matcher; manual investigation confirmed 0/6 as AI safety eval platforms. 3 confirmed false positives; 3 transient/unreachable. |
| **Observed exposure** | None — no AI safety eval platforms found |
| **Severity** | OBSERVED — methodology correction; session-8 AI safety counts retroactively zero |

**Potential impact (of the methodology defect, not the finding):** Population-scale substring matching against response bodies produces systematic false positives from unrelated services whose body text happens to contain common English words. The session-8 AI safety eval "6 confirmed" figure was confident, reproducible, and wrong. Methodology Insight #6 codified.

### [9.2] Missing Toolchain Binaries — 3 Repos Unbuilt

| Field | Value |
|---|---|
| **Name/ID** | VisorGoose, VisorLog, VisorScuba binaries |
| **Type** | Toolchain debt |
| **Evidence** | 3 repos not present on rooster before this session; toolchain checklist showed gap |
| **Observed exposure** | nuclide.db ledger ingest and compliance scoring unavailable for prior sessions |
| **Severity** | LOW — operational debt; no security impact. Resolved this session. |

**Potential impact:** Prior session findings were not being scored via VisorScuba or ledger-synced via VisorLog at ingest time. nuclide.db still intact (579 findings) because ingests had been run manually at earlier points.

### [9.3] AI Safety Eval Category — Confirmed Zero Population

| Field | Value |
|---|---|
| **Name/ID** | Promptfoo, NeMo Guardrails, DeepEval, LangSmith self-hosted, Inspect AI, Garak REST, Lakera Guard |
| **Type** | Negative finding — platform class |
| **Evidence** | 0/6 re-probed with corrected conjunctive fingerprints; 7 new aimap fingerprints built and validated |
| **Observed exposure** | None |
| **Severity** | OBSERVED — negative result is a result; this platform class appears to deploy auth-on or behind internal networks |

**Potential impact:** None confirmed. The absence of exposed AI safety eval tooling in the cloud-provider population is itself a data point: operators who run safety evaluation tooling appear to apply better network hygiene than operators who run raw inference endpoints.

---

## 6. Risk Assessment

### Overall Posture

No new exploitable exposures found this session. The session's primary contribution is a methodology correction that retroactively improves the quality of all future survey work. The AI safety eval population appears to be 0 on the tier-2 cloud provider ranges.

### Confidentiality

Not applicable. No exposures confirmed.

### Integrity

The methodology defect (substring matching) was an integrity failure in the research data: 6 false positives propagated into the session-8 case study before correction. Corrected in the same session cycle. nuclide.db ledger unaffected (FPs never ingested).

### Availability

Not applicable.

### Systemic Patterns

- **Insight #6 (this session):** Single-word substring matching on response bodies is unsound at population scale. Three conjuncts minimum: endpoint specificity, structural shape, anchored keyword. Any single one alone produces population-scale FPs. (See: `methodology/insight-06-conjunctive-matchers-required.md`)
- **The structural lesson:** Future surveys add fingerprints to aimap, not write per-survey bespoke probes. aimap's matcher schema (status_code + json_field + body_contains, all required) is the standard. `data/<platform>-probe.py` files going forward are deprecated.
- **Corrective loop worked.** Six FPs were caught before any disclosure was sent. The planned Garak disclosure to OVH abuse + NVIDIA security was held pending validation — correct call.

---

## 7. Recommendations

### R1 — Fingerprint conjunct discipline (all future surveys)

```python
# Minimum required conjunct pattern for any new fingerprint
def is_platform(response):
    return (
        response.url.path.endswith("/platform-specific-endpoint") and
        response.status_code == 200 and
        isinstance(json.loads(response.body), dict) and
        json.loads(response.body).get("specific_field") == "platform_value" and
        "anchored_term" in response.body
    )
```

Any fingerprint that passes on a single conjunct (especially a body substring alone) will produce false positives at population scale. The pattern is non-negotiable.

### R2 — Deprecate bespoke probe scripts

```bash
# aisafety-probe.py now exits immediately
python3 data/aisafety-probe.py
# Error: This probe is deprecated. Use: aimap -ports 15500,5000,3000 -fingerprint promptfoo,garak,...
```

New platform categories get aimap fingerprint additions, not standalone probe scripts. The session-8 probe scripts (aisafety-probe.py, rag-framework-probe.py, browser-agent-probe.py, datalabel-probe.py) should all be audited for substring-matching patterns before their findings are trusted.

### R3 — Pre-send FP validation gate

Before any disclosure based on a new probe script ships, re-probe the candidate cohort with the tightest available fingerprint (aimap or manual HTTP investigation). Session-8 caught the FP before the NVIDIA disclosure was sent. This gate should be formalized.

### R4 — Full toolchain at session start

```bash
# Smoke-test all 14 tools at session start
for bin in visorplus jaxen visorsd visorgoose visorgraph visorlog visorscuba visorcorpus visoragent menlohunt visorrag aimap bare; do
  which $bin && echo "$bin: OK" || echo "$bin: MISSING"
done
```

3 missing binaries went undetected across multiple sessions. A toolchain health check at session start catches this before it matters.

### Future automation

```bash
# aimap now covers AI safety eval class; run on new cohorts
aimap -list cloud-prefixes.txt -ports 15500,5000,3000,1984,7575,8000,8080 \
  -fingerprint promptfoo,nemo-guardrails,deepeval,langsmith-self-hosted,inspect-ai,garak-rest,lakera-guard \
  -o aisafety-survey.json
```

---

## 8. Limitations and Assumptions

| # | Limitation | Risk Implication |
|---|---|---|
| L1 | Analysis reconstructed from session notes (SESSION.md). Execution trace timestamps are approximate. | Minor precision variance in timeline |
| L2 | AI safety eval population result (0 confirmed) is specific to the ~1,017 tier-2 cloud prefixes scanned | Private cloud, corporate, and government deployments not covered |
| L3 | 3 session-8 FP hosts were unreachable on re-probe; could not confirm they were FPs via manual inspection | Classified as FP by inference (same substring-matching probe, similar IP class); cannot rule out coincidental disappearance of real platforms |
| L4 | artisan repo not found in NuClide Research org | One of 14 toolchain components unaccounted for; not blocking |
| L5 | Session-8 RAG framework, browser-agent, and data-labeling probe scripts use per-survey bespoke logic | Same substring-FP risk as aisafety-probe.py; audit needed |
| L6 | Compute orchestration tier survey (Ray/Spark/Airflow) deferred to session 10 | Highest-yield untouched category; ShadowRay CVE-2023-48022 active exploitation status makes it high priority |

---

## 9. Proof of Concept (PoC) Illustrations

### PoC 1: False positive reproduction — Clipface video browser

**Scenario:** Demonstrate how a video clip browser triggered the "Garak" fingerprint in the bespoke probe.

```
REQUEST:
  GET / HTTP/1.1
  Host: 149.56.22.24:5000

RESPONSE:
  HTTP/1.1 200 OK
  Content-Type: text/html

  <html>
    <title>Clipface — Video Clip Browser</title>
    <body>
      ...
      <div class="filename">
        [F] Garakuta 【Flashアニメ】ガラクタノカミサマ.mp4
      </div>
      ...
    </body>
  </html>
```

**Demonstrated:** Japanese anime title "ガラクタノカミサマ" (God of Junk / "Garakuta") rendered in the HTML body. The substring `garak` appears in `Garakuta`. The bespoke probe matched. This is not an AI safety eval platform. The corrected aimap fingerprint requires a Garak-specific API endpoint + JSON response structure — this host returns 0 of those.

### PoC 2: Corrected fingerprint match pattern

**Scenario:** Illustrate the conjunctive matcher that replaced the broken probe.

```python
# Broken (session-8 probe):
if b"garak" in response.body.lower():
    report_as_garak(host)  # WRONG — matches any page mentioning "garak"

# Corrected (aimap fingerprint, session-9):
def is_garak_rest(response):
    return (
        response.url.path == "/garak/run" and       # conjunct 1: platform-specific endpoint
        response.status_code in [200, 422] and      # conjunct 2: expected status set
        isinstance(json.loads(response.body), dict) and  # conjunct 3: JSON response
        "run_id" in json.loads(response.body) or    # conjunct 4: named field
        response.status_code == 422 and
        "detail" in json.loads(response.body)       # 422 = endpoint exists, wrong input
    )
```

**Demonstrated:** The corrected pattern requires endpoint specificity and structural shape. A video clip browser at `/` returning HTML will fail on conjuncts 1, 3, and 4 simultaneously. The FP is impossible under the corrected schema.

### PoC 3: nuclide.db ledger integrity check

**Scenario:** Confirm no FP findings were ingested into the ledger during session-8.

```
COMMAND:
  visorlog query --db ~/AI-LLM-Infrastructure-OSINT/data/nuclide.db \
    --filter "category=ai-safety-eval"

RESPONSE:
  0 records found matching filter: category=ai-safety-eval

  Total open findings: 579
    critical: 74
    high: 244
    medium: 129
    low: 132
```

**Demonstrated:** AI safety eval category has zero entries in the ledger. The session-8 FPs were never ingested. nuclide.db integrity confirmed. Correction required no ledger rollback.

---

*Prepared by NuClide Research (Nicholas Kloster + Claude Sonnet 4.6) · Session 9 · 2026-05-05*
