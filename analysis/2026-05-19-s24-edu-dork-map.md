# Session Analysis: .edu LLM Infrastructure Dork-Map (Stage 0)

**Date:** 2026-05-19
**Session:** 24
**Classification:** Internal / Research Use Only
**Toolchain:** JAXEN (count mode) · Shodan CLI · repo dork library (1,629 entries)
**Repos updated:** AI-LLM-Infrastructure-OSINT (65cab05)

---

## 1. Overview

### Objective

Map LLM/AI-related Shodan dork coverage across the `.edu` hostname surface. The thesis question: which platform classes from the commercial OSINT survey catalog produce non-zero populations at academic institutions, and what are the relative population sizes? Target class: all `.edu`-namespaced hosts visible to Shodan.

Prior approach (per-university burst sweep at 0s delay) failed at 62% ERR rate. This session reset to the verified dork library approach: cross-product of the repo's 1,629 curated Shodan queries with `hostname:.edu`, run as count-only queries (free tier, zero scan credit consumption).

### Scope and Constraints

- **Target domains:** `*.edu` hostname space (Shodan-indexed)
- **Allowed techniques:** `shodan count` queries only — read-only, no scan credit, no host probing
- **Ethical limitations:**
  - No data exfiltration — metadata and schema enumeration only
  - No destructive API calls
  - No use of discovered credentials
  - Data-tier probes: connection attempt only
  - VisorAgent: controlled lab targets only, never operator hosts
  - Personal-device and wrong-category targets: archived without outreach

---

## 2. Environment and Tooling

### Claude Code Operation

Single-session orchestrator. Subagent parallelization explicitly ruled out for the count phase: Shodan's per-key throttle (~50 queries/min) is the bottleneck, not local CPU. Parallel lanes would hit the same rate ceiling.

### Tools Used

| Tool | Role | Config notes |
|---|---|---|
| JAXEN | Shodan count sweep against dork library | `shodan count` mode; 1.2s sleep between queries; 50-min hard deadline |
| Shodan CLI | Underlying query engine | Freelance-tier API key; count queries free |

*All other arsenal tools deferred to Stage 1 (host probing) and Stage 2 (deep enum). Stage 0 is count-only.*

### Notable Configuration

- Rate: 1.2s delay between queries. Empirical basis: 0s delay → 62% ERR; 1.2s → 3.7% ERR. Sustained Shodan freelance tier is ~50 queries/min per key.
- Dork source: `shodan/queries/*.md` in the OSINT repo — 29 category files, each query hand-vetted across 50+ prior commercial surveys.
- 45 dorks already containing a `hostname:` filter were dropped to avoid filter conflicts. 1,584 queries ran.
- Zero Shodan scan credits consumed.

---

## 3. Methodology

### Enumeration Approach

Parsed every backtick-wrapped query from the 29 repo query-category files. Appended `hostname:.edu` to each. Ran `shodan count <scoped_dork>` per query with a 1.2s sleep. Captured `count<TAB>category<TAB>dork` tuples.

### Candidate Identification

A dork returning count ≥ 1 is "productive." No per-host probing at this stage — counts only. The productive/total ratio per category measures dork-library coverage of the academic surface, not platform exposure directly.

### Validation Checks

Count queries produce candidate populations only. No validation at Stage 0. All validation deferred to Stages 1+2.

The SaaS-customer-CNAME noise class surfaced: `org:"Airtable, Inc" port:443 hostname:.edu` returned 46,444 — `.edu` institutions CNAME to Airtable, inflating the org-based dorks. Discarded. Same mechanism as the `org:"Cloudflare"` false-positive class documented in prior surveys.

Port-4444 returned 1,672 hits: Selenium Grid default, but also Kerberos krb524 on campus networks. Requires conjunctive verify at Stage 1 per Insight #6.

### Safeguards

Stage 0 is count-only. No host contacts, no service probes, no credential interaction. The 48-minute sweep left zero traces on any `.edu` host.

---

## 4. Execution Trace

| Time | Action | Outcome / Decision |
|---|---|---|
| ~14:00 | Reset from burst approach after 62% ERR rate | Switched to dork-library × hostname cross-product strategy |
| ~14:05 | Parsed 1,629 dorks from 29 repo category files | Dropped 45 with existing `hostname:` filter → 1,584 scoped queries |
| ~14:10 | Started `shodan count` sweep at 1.2s/query | Monitoring loop confirmed sustained ~3.7% ERR vs prior 62% |
| ~14:58 | Sweep completed: 1,584/1,584 | 382 productive dorks (24%), 1,143 zero, 59 ERR |
| ~15:05 | Headline analysis by category | Jupyter 60% productive rate tops; 7 categories zero across all dorks |
| ~15:10 | Flagged noise patterns | Airtable org-dork and port-4444 logged as false-positive classes |
| ~15:15 | LLM-tier count table extracted | 800 Jupyter, 167 Streamlit, 133 Open WebUI, 90 n8n, 87 Ollama top entries |
| ~15:20 | Carry-forward plan written | Stage 1: per-dork download for ≥3-hit dorks; Stage 2: inline verify |
| ~15:25 | Case study + raw data committed | 65cab05; workspace preserved at ~/recon/edu-llm-infra-2026-05-19/ |

---

## 5. Findings

> **Severity label policy:** Every tier label requires 100% verified evidence at that tier. Stage 0 produces population counts only — no per-host verification occurred. All results at this stage are UNRATED pending Stage 1.

### 5.1 Category Coverage Map (OBSERVED)

| Category | Productive dorks | Total dorks | Rate |
|---|---|---|---|
| 18-jupyter | 37 | 62 | 60% |
| 02-vector-databases | 74 | 160 | 46% |
| 16-bi-dashboard | 69 | 156 | 44% |
| 04-training-experiments | 28 | 67 | 42% |
| 01-llm-orchestration | 18 | 49 | 37% |
| 03-model-serving | 16 | 57 | 28% |
| 19-streamlit | 11 | 44 | 25% |
| 27-embedding-services | ~19% | — | — |
| 07-rag-stacks | 0 | — | 0% |
| 08-image-generation | 0 | — | 0% |

**Observed:** Jupyter dominates the academic surface at 60% dork productivity. RAG stacks and image generation show zero `.edu` presence in the Shodan-indexed surface. LLM-serving tier (Ollama, Open WebUI, LiteLLM) shows 24–37% productivity — material population for Stage 1.

### 5.2 LLM-Tier Population Estimates (UNRATED)

Population counts from Shodan — not yet probe-verified:

- 800 Jupyter (html body); 275 JupyterHub specifically
- 167 Streamlit on default port 8501
- 133 Open WebUI (95 with uvicorn signature)
- 90 n8n; 87 Ollama; 35 LiteLLM; 16 Dify

---

## 6. Risk Assessment

### Overall Posture

Stage 0 establishes surface area only. Material `.edu` populations exist across 22 of 29 platform categories. Jupyter is the dominant class. LLM-serving (Ollama, Open WebUI) and gateway (n8n, LiteLLM) classes are present at non-trivial population. Risk assessment deferred to Stage 1 verification.

### Confidentiality

Not assessed at Stage 0.

### Integrity

Not assessed at Stage 0.

### Availability

Not assessed at Stage 0.

### Systemic Patterns

Shodan-dark problem partially visible even at count stage: RAG stack and image-generation categories returning zero productive dorks on `.edu` does not mean those platforms are absent. It means their signatures don't survive Shodan's crawler. Confirmed by prior survey experience.

The SaaS-CNAME noise class (Airtable, Cloudflare) is structurally the same as the CDN-proxy problem documented for commercial surveys. Academic institutions proxy through SaaS providers; org-based dorks over-count by orders of magnitude.

---

## 7. Recommendations

### R1 — Stage 1 Prioritization

High-yield categories for Stage 1 download+verify: 18-jupyter (37 productive dorks), 01-llm-orchestration (37% rate, includes Ollama/Open WebUI), 03-model-serving (Ollama 87 count). Use `shodan download --limit N` per dork for the ≥3-hit productive set.

### R2 — Noise Filter Codification

Add the SaaS-CNAME class to the dork-library FP-trap documentation. Dorks using `org:"<SaaS vendor>"` with `hostname:.edu` will over-count via customer CNAMEs. Conjunctive filtering required.

### R3 — Rate-Limit Parameterization

1.2s delay is the empirical minimum for sustained freelance-tier Shodan API without ERR cascade. Codify as the default for future count sweeps.

### Future Automation

```bash
# Stage 0 count sweep — reusable pattern
while IFS=$'\t' read -r dork category; do
  count=$(shodan count "${dork} hostname:.edu" 2>/dev/null || echo "ERR")
  echo -e "${count}\t${category}\t${dork}"
  sleep 1.2
done < scoped-dorks-edu.tsv > scoped-counts.tsv
```

---

## 8. Limitations and Assumptions

| # | Limitation | Risk Implication |
|---|---|---|
| L1 | Stage 0 produces counts, not verified hosts | All population numbers are Shodan estimates; actual live platform count unknown until Stage 1 |
| L2 | `.edu` hostname filter relies on Shodan's rDNS data | Hosts with missing or incorrect rDNS on Shodan may be missed |
| L3 | Shodan freelance tier rate cap (~50 queries/min) | 1.2s delay introduced; 59 ERR queries represent ~3.7% of the dork library not counted |
| L4 | SaaS-CNAME noise class not fully characterized | Some productive-dork counts inflate the true platform-on-edu estimate |
| L5 | Analysis reconstructed from session notes (SESSION.md). Execution trace timestamps are approximate. | |

---

## 9. Proof of Concept (PoC) Illustrations

### PoC 1: Scoped Shodan Count Query Pattern

**Scenario:** Researcher maps LLM infrastructure presence on the `.edu` hostname surface using the repo's vetted dork library.

```
REQUEST (Shodan CLI):
  shodan count 'http.title:"Open WebUI" hostname:.edu'

RESPONSE:
  133

REQUEST:
  shodan count 'port:11434 hostname:.edu'

RESPONSE:
  83
```

**Demonstrated:** 133 hosts matching Open WebUI title signature and 83 hosts on Ollama's default port exist in the Shodan `.edu` hostname index. No hosts contacted. No credentials involved. Population size established for Stage 1 prioritization. What this does NOT do: confirm those hosts are live, unauth, or running the named platform — that is Stage 1's job.

---

*Prepared by NuClide Research (Nicholas Kloster + Claude Sonnet 4.6) · Session 24 · 2026-05-19*
