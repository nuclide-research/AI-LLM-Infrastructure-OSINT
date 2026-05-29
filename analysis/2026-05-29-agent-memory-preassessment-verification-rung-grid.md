# Session Analysis: Agent-Memory Pre-Assessment and the Verification-Rung Grid

**Date:** 2026-05-29
**Session:** date-only (methodology-formalization arc)
**Classification:** Internal / Research Use Only
**Toolchain:** parallel OSINT research agents (Opus subagents), WebFetch, Go 1.26 (logic-reproduction harness), Docker (present, not used this session)
**Repos updated:** AI-LLM-Infrastructure-OSINT (uncommitted at write time); `~/.claude/nuclide-internal/METHODOLOGY.md` (local canon)

---

## 1. Overview

### Objective

Open the next unmapped niche category, the agent-memory layer (mem0, Letta,
Zep, and adjacent self-hostable memory servers), at the pre-assessment stage. The
thesis question: does the auth-on-default thesis hold on a platform class whose
entire purpose is persisting PII-dense user memory? Secondary objective, which
became the session's main product: formalize the claims-discipline vocabulary
that the program had been applying informally, into a reusable verification-rung
grid.

This session was deliberately held at high depth, low breadth. No public host was
scanned. The survey's harvest and arsenal phases were not run, by choice (NuClide
restraint ethic).

### Scope and Constraints

- **Target class:** agent-memory / LLM long-term-memory self-hosted servers.
- **Allowed techniques this session:** public primary-source OSINT (official docs,
  GitHub source, CVE databases) via research subagents; local Go logic
  reproduction. No live third-party host touched.
- **Ethical limitations:** no data exfiltration, no destructive calls, no
  credential use, no scanning of public deployments. Breadth held at outer 0 by
  design.

---

## 2. Environment and Tooling

### Claude Code Operation

Orchestrator plus subagent delegation. Four Opus research subagents dispatched in
parallel for the pre-assessment OSINT (one per platform: mem0, Letta, Zep, plus an
ecosystem-sweep lane). Synthesis, verification decisions, and all writing kept at
the orchestrator. Opus-direct for the survey-relevant reasoning per standing
preference.

### Tools Used

| Tool | Role | Config notes |
|---|---|---|
| Research subagents (Opus) | Stage -1 pre-assessment OSINT, parallel fan-out | 4 lanes, primary-source-only brief |
| WebFetch | Pull verbatim Zep CE middleware source | raw.githubusercontent.com |
| Go 1.26 | Inner-A logic-reproduction harness | `/tmp/zep-auth-verify/main.go` |
| Docker 29.5.2 | Present and daemon up; not used this session (breadth held at 0) | available for inner-B step |

The 19-tool arsenal was not run. This is not a category-survey session; it is a
pre-assessment plus methodology-formalization session. The harvest (JAXEN /
Playwright Shodan), aimap fingerprinting, and the rest of the chain are queued
for whenever breadth is raised.

### Notable Configuration

Shodan API keys remain dead (carry-forward), so any future harvest is
Playwright-web-UI-only. Mullvad active (us-lax-wg-007). The pre-assessment lanes
need only public web access, so the dead keys did not constrain this session.

---

## 3. Methodology

### Enumeration approach

New-category pre-assessment per methodology Stage -1. Before any dork, four
parallel research agents gathered auth posture, ports, API surface, data-exposure
class, CVEs, and Shodan-fingerprint signals from primary sources. Output committed
to `data/platform-intel/agent-memory-osint-2026-05-29.md` and a query catalog to
`shodan/queries/30-agent-memory.md`.

### Candidate identification

The category's structural hazard: four of five in-scope servers default to port
8000. Fingerprints were designed to anchor on vendor-unique signals (OpenAPI
`info.title`, semantic routes like `/api/v1/cognify`, the `X-Zep-Version` response
header), never the port (Insight #7, Insight #15).

### Validation checks

One finding was driven to its rung this session: the Zep CE empty-`api_secret`
condition. Verbatim source pulled and read (Insight #11, source is authoritative).
The exact branch logic was reproduced in a Go harness and exercised against a
truth table, confirming the empty-token-passes behavior and the load-bearing
trailing-space precondition.

### Safeguards

No brute forcing, no privilege escalation, no data exfiltration, no credential
use, no scanning. The session's defining restraint decision: confirm the Zep
condition at the code level and stop, holding breadth at outer 0 rather than
standing up a container (inner B) or scanning the public CE population (outer
1/2). This is "NuClide mode" exercised on purpose.

---

## 4. Execution Trace

| Time | Action | Outcome / Decision |
|---|---|---|
| 16:13 | Session start, methodology loaded, continuity read | Loop next-category was ML Governance; Nick redirected to niche/smaller platforms |
| 16:20 | Coverage gap map vs FUTURE-SURVEYS roadmap | Identified agent-memory as freshest unmapped niche; Nick selected it |
| 16:30 | 4 parallel Opus OSINT lanes dispatched | mem0/Letta/Zep + ecosystem briefs returned, all primary-sourced |
| 16:45 | Synthesized intel doc + cat-30 query catalog | Committed-to-disk pre-assessment artifact |
| 16:55 | Zep CE middleware source pulled (WebFetch) | Confirmed verbatim `strings.Split` + equality compare |
| 17:00 | Go logic-reproduction harness run | Truth table confirms empty-secret + `Api-Key ` = allow; trailing space load-bearing |
| 17:10 | Iterative methodology dialog with Nick | Linear ladder rejected in favor of 2D Depth x Breadth grid |
| 17:30 | Insight #68 + canon box + template + finding written, then retrofitted to grid | All artifacts consistent on inner(A/B) x outer(0/1/2); restraint ethic named |

---

## 5. Findings

> Severity policy: every tier label requires 100% verified evidence at that tier.

### 5.1 Zep Community Edition — empty default `api_secret` accepts a zero-entropy credential

| Field | Value |
|---|---|
| **Name/ID** | Zep CE secret-key auth middleware |
| **Type** | Authorization control (header check) |
| **Evidence** | Verbatim source (`legacy/src/api/middleware/secret_key_auth_ce.go`): `strings.Split(authHeader," ")`, prefix gate `Api-Key`, `tokenString != config.ApiSecret()`. `legacy/zep.yaml` ships `api_secret` empty. Logic reproduction confirms `Authorization: Api-Key ` (trailing space) passes when secret is empty. |
| **Observed exposure** | Zero-entropy credential satisfies the auth check on default config; no non-empty-secret invariant at config load |
| **Severity** | OBSERVED (code-level). Inner A / outer 0. Not labeled exploitable: no live binary exercised, no host surveyed. |

**Potential impact (code level):** on a populated instance the gated `/api/v2`
surface serves session message history, summaries, and extracted user facts
(PII-dense conversational memory). Impact is stated at code level only because the
finding has not been exercised against a running binary or any real deployment.

**No other findings.** No population survey was run, by design.

---

## 6. Risk Assessment

### Overall Posture

Category-level, the agent-memory tier reads as a strong auth-on-default thesis
confirmation at the source level: of the in-scope platforms, OpenMemory (mem0
legacy), Letta, Zep CE, Cognee, Graphiti, and Motorhead all read as auth-off or
default-cred by default; only mem0's newer `/server` ships auth-on. That single
counter-pressure case is Insight #40 (auth-on-default shifts rightward) playing
out inside one repository, the deprecated component auth-off and its replacement
auth-on. None of this is measured. It is inner A / outer 0: supported by code
reading, not by population data.

### Confidentiality

If exposed and exercised, the data class is high: conversation-derived user facts,
session message history, system prompts, and LLM provider config (potential key
leak via mem0 `/api/v1/config`). The data sensitivity is the reason this category
is worth surveying and the reason verification discipline matters before any
public claim.

### Integrity

mem0 OpenMemory supports unauthenticated writes (POST `/api/v1/memories`), a
memory-poisoning vector at code level. Not exercised.

### Availability

Not assessed.

### Systemic Patterns

Platform-default propagation (Insight #13) is the expected driver, to be tested
when breadth is raised. The port-8000 clustering is an operator-and-ecosystem
pattern that shapes the discovery method, not a risk in itself.

---

## 7. Recommendations

### R1 — Zep CE: reject an empty secret at config load

```yaml
# zep.yaml — operator fix
auth:
  required: true
  secret: "<non-empty-random-value>"   # ZEP_AUTH_SECRET
```

For the project: refuse to boot, or treat the route as deny-all, when the
configured secret is empty. This removes the entire zero-entropy-credential class
rather than depending on each operator to set a value.

### R2 — Category fingerprinting: anchor on protocol features, never port 8000

Fingerprints for this category must key on OpenAPI `info.title`, the unique route
set, or a vendor header (`X-Zep-Version`, the `m0sk_` key prefix). A port-8000
plus generic Swagger match would inherit the substring-FP class (Insight #7).

### Future automation

When breadth is raised, the masscan-seeded path is likely required (these servers
are probably Shodan-dark behind JSON-only roots, like the embedding tier):

```bash
# masscan tier-2 cloud on the agent-memory port set, then aimap by API shape
sudo masscan -iL /tmp/tier2-all-ranges.txt -p8765,8283,8019,8000,9000,6333 --rate 10000 -oG /tmp/agent-memory.txt
aimap -list /tmp/agent-memory-ips.txt -o agent-memory.json
```

---

## 8. Limitations and Assumptions

| # | Limitation | Risk Implication |
|---|---|---|
| L1 | No live host tested (outer 0 by design) | Cannot speak to prevalence; thesis confirmation is source-level only |
| L2 | Zep bypass is inner A (logic reproduction), not inner B (binary) | "Exploitable" not licensed until a CE container is exercised |
| L3 | Auth-default claims for ecosystem platforms are doc-inferred | Each must be exercised before any tier label |
| L4 | No aimap fingerprint exists for any platform yet | Unknown FP rate until fingerprints are built and sample-200 validated |
| L5 | Shodan API keys dead | Any harvest is Playwright-web-UI-only; likely Shodan-dark, masscan-seeded |

---

## 9. Proof of Concept (PoC) Illustrations

> Read-only / simulated. No operator data, no credentials, no live host.

### PoC 1: Zep CE empty-secret logic (inner A, against a local harness, not a host)

**Scenario:** demonstrate, against a reproduction of the released auth logic, that
an empty configured secret accepts an empty-token credential.

```
HARNESS (reproduction of secret_key_auth_ce.go branch logic):
  authOK("Api-Key ", "")          -> true   (BYPASS: empty secret + empty token)
  authOK("Api-Key", "")           -> false  (no trailing space: 1 part, 401)
  authOK("Api-Key ", "s3cr3t")    -> false  (set secret rejects empty token)
  authOK("Api-Key s3cr3t","s3cr3t") -> true (control: correct token)
```

**Demonstrated:** the branch logic accepts a zero-entropy token when the secret is
empty, and the trailing space is load-bearing. It does NOT demonstrate the
released `zepai/zep` binary behaves identically in a full stack (that is inner B),
nor that any real deployment is exposed (that is outer 1+). The boundary is the
point.

---

*Prepared by NuClide Research (Nicholas Kloster + Claude Opus 4.8) · 2026-05-29*
