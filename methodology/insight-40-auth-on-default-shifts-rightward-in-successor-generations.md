---
type: methodology
insight_number: 40
title: "Auth-on-default thesis shifts rightward in successor OSS generations"
---

# Insight #40 — Auth-on-default thesis shifts rightward in successor OSS generations

**Codified:** 2026-05-19 (sub2api population survey)
**Family:** Insight #25 (auth-on-default thesis), Insight #36 (PaaS build-arg secret baking), Insight #39 (pooled-account attribution laundering)
**Falsifiability tier:** medium — pattern needs at least one more successor-generation pair to confirm or break

---

## The pattern

When a security disclosure is made against an OSS LLM-infrastructure project, the next-generation release (successor project by the same author or fork) hardens the specific surface that drove the disclosure. The auth-on-default thesis (Insight #25) does not just hold at a given point in time — it strengthens over successor generations within the same project family.

Stated empirically, with the source case:

- **v1: `claude-relay-service`** (Wei-Shaw, Node.js, 2024-2025)
  - Public `/` endpoint exposed pooled-account stats: `{"accounts": N, "availableAccounts": M, "stats": {"totalTokens": ...}, "thirdPartyMaxConcurrent": K}`
  - 6 hosts surveyed; 32 pooled Anthropic accounts; 13.92B Claude tokens served
  - Disclosed to Anthropic 2026-05-19

- **v2: `sub2api`** (Wei-Shaw, Go, 2026)
  - `/health` returns only `{"status":"ok"}` — pool counts removed
  - `/api/v1/admin/*` returns 401 with `{"code":"UNAUTHORIZED","message":"Authorization required"}` — admin surface auth-gated
  - `/v1/models` returns 401 with verbatim API_KEY_REQUIRED envelope
  - 7,720 hosts surveyed; **zero** pool-leak hosts (0/7,720 = 0.00%)
  - 5,848/6,083 verified hosts = 96.1% confirmed auth-on-default

The successor generation closed the specific gap. The architectural pattern (pooled-account upstream proxy, Insight #39) persisted; the externally-observable finding pattern did not.

## Mechanism (hypothesis)

OSS authors observe disclosure outcomes and respond. Specifically:
1. Tier-1 vendor (Anthropic, OpenAI) enforces pool-detection bans → operators lose accounts
2. OSS author observes ban patterns via user issue reports (claude-relay-service GitHub: issues #587, #861, #673, #1000)
3. Next generation hardens the surface that made the bans easy (public metrics counters were the load-bearing evidence)
4. Authority of disclosure: when the disclosure target (vendor) has direct enforcement power and the OSS author depends on the vendor's continued tolerance, the feedback loop closes fast

This is distinct from:
- Patches in the same project (a CVE fix in v1 that ships in v1.2.x). This insight is about whole-project rewrites/successors.
- Author-led security hardening absent pressure (some authors harden by inclination). This insight asserts pressure as the mechanism.

## What this insight is NOT

- NOT a claim that v2 has zero security gaps. Sub2api shipped with SETUP_OPEN as a 1.31% finding class (101/7,720 hosts have install wizards accessible). New finding shapes emerge as old ones close.
- NOT a claim that all OSS-author response cycles work this way. Closed-source vendors, abandoned projects, and authors who ignore disclosures are counterexamples.
- NOT a substitute for actually surveying v2. The directional confirmation requires the empirical pass.

## Falsification conditions

The pattern is wrong if:
1. The next-published OSS pooled-account proxy after sub2api reverts to publicly-readable pool stats.
2. A v3 successor by the same author re-opens the v1-disclosed gap.
3. A different OSS-author project in this ecosystem with similar disclosure exposure does NOT harden the equivalent surface.

## Test conditions

Apply this insight to:
- The next sub2api-class project (Go-rewrite, OpenAI-compat, Vertex-compat). Expect auth-on-default on metrics.
- A different OSS pooled-relay project (e.g., one targeting Gemini or Mistral). Expect the same v2-style hardening if the maintainer has been on the receiving end of vendor pressure.
- The reverse: a project whose disclosed gap was NOT pool-stats but something else (e.g., model-impersonation per Insight #38). Expect the next generation to fix that specific gap, not the metrics gap.

## Operator impact

For Tier-1 vendors (Anthropic, OpenAI, Google):
- Disclosure to the vendor against the v1 surface drove the v2 architecture. This is a **disclosure-efficacy measurement** that's externally observable.
- Re-probe at 14/30/60 days post-disclosure on the v1 cohort: measure decline in `accounts`, `totalTokens` rate, `uptime` per host. (This is the same scheduled re-probe protocol from the v1 disclosure, now extended to "and verify v2 still has zero POOL_LEAK at re-probe windows.")

For research methodology:
- A negative result (zero pool-leak in v2) is publishable evidence that disclosures work in this ecosystem. Quantitative measurement of disclosure efficacy is rare.
- The same `verify_probe.py` schema can be re-run periodically. Drift toward POOL_LEAK > 0 would be evidence of regression OR new operator behavior outpacing OSS hardening.

For the auth-on-default thesis:
- Insight #25 was previously stated as "platform-default auth is the dominant pattern in this ecosystem." Insight #40 extends: "...and the pattern strengthens over successor generations under disclosure pressure."

## Cross-references

- **Insight #25:** auth-on-default thesis (the parent)
- **Insight #36:** PaaS build-arg secret baking (the v2 sub2api result of "zero baked secrets" confirms #36 doesn't generalize to this install class)
- **Insight #37:** asymmetric auth gating (sub2api gates dashboard AND API symmetrically; #37 doesn't apply)
- **Insight #38:** model-impersonation fraud (orthogonal — covers a different vendor-deception class)
- **Insight #39:** pooled-account attribution laundering (the architecture; #40 is about the *finding-shape evolution* within this architecture)

## Source data

- v1 cohort: `case-studies/commercial/claude-relay-chinese-reseller-2026-05-19.md`
- v2 population: `case-studies/commercial/sub2api-population-2026-05-19.md`
- Disclosure: sent to Anthropic Trust & Safety 2026-05-19 ~11:00 UTC re: v1 cohort
- Re-probe schedule: 14/30/60-day on the six v1 hosts; first re-probe due 2026-06-02

---

*Codified by Nuclide Research (Nicholas Kloster + Claude) 2026-05-19 from the sub2api population survey. Methodology per `~/.claude/nuclide-internal/METHODOLOGY.md`.*
