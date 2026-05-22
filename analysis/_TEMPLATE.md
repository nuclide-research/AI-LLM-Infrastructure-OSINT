# Session Analysis: [Brief Title]

**Date:** YYYY-MM-DD  
**Session:** N  
**Classification:** Internal / Research Use Only  
**Toolchain:** [tools + versions used]  
**Repos updated:** [repo (commit)] · [repo (commit)]

---

## 1. Overview

### Objective

State the objective of this run (discovering exposed or misconfigured LLM infrastructure). What thesis question was being tested? What target class or category?

### Scope and Constraints

- **Target domains/IPs:** [IP ranges, domains, platform classes]
- **Allowed techniques:** [passive Shodan, banner grab, safe HTTP GET, Docker-local fingerprinting, etc.]
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

Describe how you operated inside Claude Code. Orchestrator + subagents? Parallel terminals dispatched? Any model-tier switching?

### Tools Used

| Tool | Role | Config notes |
|---|---|---|
| JAXEN | Stage-0 discovery: Shodan harvest → empire.db | Rate-limit, --clean flag |
| aimap | Stage-1 fingerprint + Stage-2 verify | Version, -scan-all-fingerprints if needed |
| VisorBishop | Productized re-prober | -ip-shadow for adjacent-port sweep |
| VisorGraph | Cert-pivot → operator attribution | |
| VisorLog | Ledger ingest → nuclide.db | |
| VisorScuba | Compliance scoring (OPA/Rego) | |
| BARE | Metasploit semantic ranking | |
| VisorCorpus | Adversarial corpus generation | |
| VisorSD | ASN/org dork sweep | |
| VisorGoose | TLD / CT-log sweep | |
| menlohunt | GCP EASM | |
| recongraph | Seed-polymorphic recon graph | |
| nu-recon | Single-host passive deep-read | |
| VisorPlus | Orchestrator (hands-off chain) | |
| cortex | Auth-context analyzer | |
| JS-bundle extract | SPA → hidden API / secret extraction | |
| VisorRAG | RAG adversarial confirmation | Controlled targets only |
| VisorAgent | Active LLM exploitation | Controlled targets only (ethical-stop) |
| VisorHollow | Windows process-injection benchmark | [—] not applicable — Windows-only |
| Docker | Local platform sandbox for fingerprinting | |

*Remove rows for tools not relevant to this session. Document null results — a null result is a result.*

### Notable Configuration

Timeouts, concurrency, rate limits, filters, API key availability, VPN state, anything that constrained or shaped what ran.

---

## 3. Methodology

Explain step by step how you approached the problem.

### Enumeration approach

How did you enumerate potential LLM-related services? (Shodan dorks, port-first masscan, JAXEN harvest, carry-forward from prior session, cert-pivot, etc.)

### Candidate identification

How did you distinguish "LLM infrastructure" from unrelated services? What fingerprint conjuncts, identity markers, or proxy signals did you use?

### Validation checks

What probes confirmed a candidate as a live, real instance? (e.g., safe HTTP GET to `/api/version`, banner grab, `/api/projects` data-layer check, `pg_isready` for Postgres). Cite the relevant Insight # for each validation rule applied.

### Safeguards

Explicitly state: no brute forcing, no privilege escalation, no data exfiltration, no write-tier operations, no credential use. What specific restraint decisions were made during this session?

---

## 4. Execution Trace

Chronological narrative of what happened. For each major step: brief command/output summary → what it told you → what you did next. Focus on decisions and reasoning, not raw log dumps.

| Time | Action | Outcome / Decision |
|---|---|---|
| HH:MM | | |
| HH:MM | | |
| HH:MM | | |

---

## 5. Findings

> **Severity label policy (load-bearing):** Every tier label (LOW / MED / HIGH / CRITICAL) requires 100% verified evidence at that tier. Unverified observations are UNRATED. Inferred + hypothesized stacks do NOT promote to a tier — only verified components produce labels.

For each finding:

### [N.N] [Platform / Host] — [One-line description]

| Field | Value |
|---|---|
| **Name/ID** | host, path, or service name (sanitise sensitive details) |
| **Type** | API endpoint / admin UI / gateway / model orchestration / data tier / etc. |
| **Evidence** | What you directly observed (probe, response body, version, timestamp) |
| **Observed exposure** | Unauthenticated access / weak auth / debug mode / open metrics / open signup / etc. |
| **Severity** | CRITICAL / HIGH / MED / LOW / OBSERVED / UNRATED — with justification |

**Potential impact:** What could a malicious actor achieve? (arbitrary prompt injection, access to logs, extract system prompts, quota drain, PII access, pivot to other systems, etc.)

---

Group findings by severity:

**CRITICAL** — verified data-in-hand, direct impact  
**HIGH** — verified unauth access, significant data class  
**MED** — partial access, limited data class, or requires chaining  
**LOW** — information disclosure, version leak, or low-impact exposure  
**OBSERVED** — confirmed platform behavior, not yet verified at population scale  
**UNRATED** — candidate, pending verification  

---

## 6. Risk Assessment

### Overall Posture

Summarise the risk posture across all findings. Is this a systemic pattern or isolated?

### Confidentiality

What data is at risk of exposure? (User prompts, PII, system prompts, API keys, model weights, evaluation data, etc.)

### Integrity

Can an unauthenticated actor modify, corrupt, or delete data? Can they inject false metrics, tamper with evaluation baselines, or disrupt training?

### Availability

Can an unauthenticated actor degrade or deny service? (Compute exhaustion, quota drain, cache poisoning, model deletion.)

### Systemic Patterns

- Shared root cause across multiple findings?
- Operator-culture patterns (same misconfiguration on multiple platforms from same operator)?
- Platform-default propagation (Insight #13: shipping defaults are load-bearing)?

---

## 7. Recommendations

Concrete, actionable remediation for each issue class.

### R1 — [Issue class]

```bash
# Concrete fix example
```

Explain why this works and what it prevents.

### R2 — [Issue class]

...

### Future automation

How regular tool-based scans could be integrated into CI/CD or periodic security checks to detect similar exposures early:

```bash
# Example: aimap integrated into post-deploy pipeline
aimap -list your-public-ips.txt -ports 8000,3000,5432,6333,11434 -o report.json
```

---

## 8. Limitations and Assumptions

| # | Limitation | Risk Implication |
|---|---|---|
| L1 | | |
| L2 | | |

Common categories:
- Internal-only deployments not visible to Shodan
- API key / env var unavailable (harvest blocked)
- Parallel sessions dispatched but not yet reporting
- Write-tier operations not tested (restraint ethic)
- VPN artifacts affecting local test environment
- Docker fingerprinting = default config, not operator variation
- Auth bypass not attempted — method finds Tier-A only

---

## 9. Proof of Concept (PoC) Illustrations

> PoCs use minimal, read-only, or simulated interactions. No operator data extracted. No credentials used. No exploit payloads. Demonstrate existence and risk conceptually only.

### PoC 1: [Title]

**Scenario:** [One sentence: who, what, against what]

```
REQUEST:
  [method] [path] HTTP/1.1
  Host: <operator-host>:[port]
  [headers if relevant]

RESPONSE:
  HTTP/1.1 [status]
  [relevant headers]

  [sanitised body — replace sensitive values with <placeholder>]
```

**Demonstrated:** [What the actor now knows or can do. What this surface enables. What it does NOT do — be precise about the boundary.]

---

*Prepared by NuClide Research (Nicholas Kloster + Claude Sonnet 4.6) · Session N · YYYY-MM-DD*
