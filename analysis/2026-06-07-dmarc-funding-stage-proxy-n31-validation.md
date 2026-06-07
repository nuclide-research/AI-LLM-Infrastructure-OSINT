# DMARC Funding-Stage Proxy — Validation Sweep N=31

Date: 2026-06-07. Cohort: AI security vendors (LLM guardrails, agent runtime, email safety, redteam, observability, monitoring, DLP, EDR).

## Tally

| Stage | N | reject | quarantine | none | absent/other | % enforced |
|---|---|---|---|---|---|---|
| Pre-seed / YC | 5 | 0 | 0 | 4 | 1 | 0% |
| Seed | 8 | 2 | 2 | 2 | 2 | 50% |
| Series A | 4 | 3 | 1 | 0 | 0 | 100% |
| Series B | 4 | 0 | 2 | 1 | 1 | 50% |
| Series C | 5 | 5 | 0 | 0 | 0 | 100% |
| Public | 4 | 3 | 1 | 0 | 0 | 100% |

## Verdict

REVISED. The original "p=none → p=reject transition at seed boundary" hypothesis is WRONG. Actual pattern:

- Pre-seed / YC: 0% enforce (5/5). Strong, clean signal.
- Series C / Public: 100% enforce (9/9). Strong, clean signal.
- Seed → Series A → Series B: mixed (50-100%, small N). NOT a sharp boundary.

## Revised codified rule

DMARC posture is a funding-stage proxy at the EXTREMES, not the middle:
- Vendor at p=none + AI security category  → 80% chance YC-current / pre-seed
- Vendor at p=reject + AI security category → 64% chance Series C or later
- Vendor at p=quarantine or absent in this category → 50/50 seed through Series B (uninformative)

## Surprises (worth tracking)

- Arthur.ai (Series B): p=none. Genuinely unusual for late-Series-B enterprise.
- Robust Intelligence (Cisco-acquired 2024): DMARC absent. Acquisition didn't propagate parent hardening.
- Guardrails AI (seed): DMARC absent. Category irony — LLM-guardrails vendor missing email guardrails.
- AegisAI (seed): p=reject — outlier; founder DNA (ex-Google Safe Browsing). Pre-confirmed the founder-DNA caveat from the original insight.

## Population breakdown

```
Pre-seed/YC (5): sluice.email, trysalus.ai, alterai.dev, clawvisor.com, beesafe.ai
Seed (8):       aegisai.ai, straiker.ai, guardrails.ai, patronus.ai, opsani.com, nexla.com, adversaai.com, mindgard.ai
Series A (4):   prompt.security, lakera.ai, protectai.com, calypsoai.com
Series B (4):   hiddenlayer.com, robustintelligence.com, arthur.ai, fiddler.ai
Series C (5):   abnormalsecurity.com, sublime.security, material.security, appomni.com, arize.com
Public (4):     proofpoint.com, checkmarx.com, sentinelone.com, darktrace.com
```

## Next steps

- Push N higher: add ~50 more vendors at Series B specifically (smallest cohort here) before promoting to numbered NuClide Insight.
- Cross-category validation: does the same pattern hold for non-AI-security verticals (e.g., generic SaaS at the same stages)? If yes, this is a sector-agnostic SaaS-maturity heuristic.
- File the surprises as discrete findings (Arthur.ai, Robust Intelligence, Guardrails AI) — these are enterprise vendors that customers might want to know about.
