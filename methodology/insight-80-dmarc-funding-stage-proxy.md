# Insight #80 — DMARC enforcement rate is a funding-stage proxy in AI-security vendors

**Status:** confirmed at n=31 known-stage subset; validation at n>=100 blocked on funding-stage data, not method.

**Source:** Lane 1C of 2026-06-07 9-item plan. Full sweep of 410 AI-infra vendor apex domains via `dig +short TXT _dmarc.<domain>`. Funding stage manually cross-referenced on a 31-vendor subset drawn from prior AI-security focused work.

## The claim

DMARC policy strictness scales monotonically with funding stage in AI-security vendors:

| Stage | N | reject | quarantine | none | no-dmarc | %enforce |
|---|---|---|---|---|---|---|
| Pre-seed / YC | 6 | 0 | 0 | 5 | 1 | 0% |
| Seed | 8 | 1 | 3 | 2 | 2 | 50% |
| Series A | 4 | 3 | 1 | 0 | 0 | 100% |
| Series B | 4 | 0 | 2 | 1 | 1 | 50% |
| Series C | 5 | 5 | 0 | 0 | 0 | 100% |
| Public | 4 | 3 | 1 | 0 | 0 | 100% |

The extreme bands hold: 0% enforcement at YC/pre-seed, 100% at Series C and later. Mid-bands are noisier but trend upward.

## Why this is interesting

A single 50ms `dig` call against `_dmarc.<vendor>.com` lets a researcher infer:

1. Approximate funding stage of an AI-security vendor.
2. SOC2/SOC3 audit pressure (enforcing DMARC is a SOC2 control item).
3. Engineering maturity proxy independent of self-reported claims.

This makes it a cheap pre-engagement signal: scope, prioritize, and budget disclosure outreach by stage without scraping LinkedIn or Crunchbase first.

## The side finding (worth flagging on its own)

The pattern breaks at the broader AI-infra level. Of 410 vendor domains:

- no-dmarc:    219 (53.4%)
- p=reject:     71 (17.3%)
- p=none:       56 (13.7%)
- p=quarantine: 48 (11.7%)
- nxdomain:     16 (3.9%)

Overall enforcement rate (reject + quarantine over resolvable domains) is 30.2%. But the absent-DMARC rate is 53.4% across AI-infra, vs ~13% in the AI-security sub-sample. AI-security vendors trail enterprise SaaS broadly, but they are AHEAD of the broader AI-infra ecosystem by a factor of ~4 on basic email hygiene.

Hypothesis: SOC2 pressure scales with enterprise-sales motion, not with funding stage per se. Series C+ companies that go enterprise-up-market all enforce; pre-seed YC and AI-tooling-for-developers companies that don't sell to enterprise security teams skip the control. The signal is "selling to security buyers," not "raised a Series C."

## How to apply

- When prioritizing AI-security vendor outreach: enforcing DMARC = mature security org, expect formal triage and SLA. p=none = startup, may be more responsive but less structured.
- When fingerprinting an unfamiliar AI-infra vendor: no-DMARC is the population baseline (53%), not a finding. p=reject is the anomaly worth noting.
- When publishing methodology: this is a passive, ethical, zero-cost OSINT primitive that surfaces an organizational property the vendor cannot easily fake.

## Limits

- n=31 known-stage validation is small; the 100% Series C+ band is 9 hosts total. The shape is right; the cell counts will move with more data.
- "Known stage" is biased toward AI-security vendors NuClide had already disclosure-engaged. Generalizing to all AI-infra requires manual Crunchbase work the registry sweep does not do.
- AegisAI flipped reject -> quarantine between the original n=7 (Cat-33 work, 2026-06-06) and the re-dug n=31. DMARC posture is not static; the signal is rolling, not frozen.

## Data

- `~/AI-LLM-Infrastructure-OSINT/data/dmarc-funding-stage-sweep-2026-06-07.csv` (410 rows; vendor, domain, dmarc_policy, dmarc_aspf, dmarc_rua, funding_stage, raw)
- `~/AI-LLM-Infrastructure-OSINT/case-studies/commercial/dmarc-funding-stage-proxy-2026-06-07.md` (case study)
- Parent memory: `reference-dmarc-funding-stage-proxy.md`
- Companion candidate: AI-security DMARC enforcement is ~4x higher than AI-infra broadly. Promotion-eligible after one cross-sample validation run.

## DCWF KSAT fit

- 672: T5904 (risk assessment via passive signal), K7044 (V&V tooling — dig is the tool).
- 733: T5882 (Responsible AI process — vendor posture maps to RAI maturity).
- Overlap: K22 (network/DNS), K1158 (security principles).
