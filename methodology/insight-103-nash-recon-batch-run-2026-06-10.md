# Insight #103 — first batch nash-recon run across recent surveys (2026-06-10)

Companion to `insight-103-nash-mass-action-foundation-for-auth-on-default.md`. Records what fell out of running `nash-recon` against six recent surveys, with one methodology refinement and three concrete verification leads.

## Run summary

| Survey | N (confirmed) | S_P (equilibrium) | cert I/N | OFF_EQ candidates |
|--------|---------------|-------------------|----------|-------------------|
| cat-mcp-cred-fleet-2026-06-09 (per-cluster) | 66 | by-cluster, every cluster I/N=1.000 | 1.000 | 2 (the two UNKNOWNs in the blank cluster) |
| cat-tabby-2026-06-09 | 70 | AUTH_OFF=0.80, AUTH_ON=0.04, UNKNOWN=0.16 | 0.357 | 3 (the three AUTH_ON hosts) |
| cat-tabby-devstral-2026-06-09 | 66 | AUTH_OFF=0.91, AUTH_ON=0.09 | n/a | 6 (all six AUTH_ON hosts) |
| cat-bentoml-2026-06-10 | 44 | AUTH_OFF=0.82, AUTH_ON=0.05, UNKNOWN=0.14 | n/a | 2 (the two AUTH_ON hosts) |
| cat-lmdeploy-2026-06-10 | 5 | NET_ISOLATED=1.00 | n/a | 0 (degenerate; confirms refuted) |
| cat-syllabus-leads-2026-06-09 (Lane 1 ledger) | 4 | AUTH_OFF=1.00 | n/a | 0 (degenerate; all four unauth registries) |
| cat53-fl-2026-06-09 | 4 | AUTH_OFF=1.00 | 0.250 (small N) | 0 |

## The recurring signal: the rare hardened minority is a worth-probing class

Across Tabby, Tabby-Shadow, and BentoML, the same pattern emerges: 4–9% of confirmed platform hosts present `AUTH_ON_DEFAULT` against an equilibrium frequency of `AUTH_OFF >= 0.80`. Surprisal scores 2.3–2.9 nats. Under the previous reporting convention these hosts would be filed as "good, hardened, ignore"; under Insight #103 they are *off-equilibrium players*, which Nash's mass-action framework predicts are one of:

- early-adopter operators (leading edge of Insight #40's rightward drift),
- commercial-vs-OSS deployments with a different payoff function,
- honeypots (auth-gated to look like a legitimate hardened install rather than the obvious-honeypot AUTH_OFF case), or
- a separately-attributed sub-cohort.

The concrete OFF_EQ candidates worth a re-probe:

- **Tabby**: `5.78.203.59`, `43.133.248.37`, `98.64.233.47`
- **Tabby-Shadow**: `18.188.53.175`, `13.53.139.178`, `3.121.130.230`, `13.208.238.59`, `43.199.29.225`, plus one more
- **BentoML**: `35.168.161.143`, `35.153.226.93`

These are the verification queue ordered by Nash-surprisal rather than "everyone gets the same probe." This is the Nash-dominance pruning of the verification chain (Insight #103 Prediction 3) realized as an artifact.

## Methodology refinement: cert I/N threshold is context-dependent

Insight #97 calibrated `I/N >= 0.30 = honeypot-likely` against a B=1,T=1 cohort already presumed to be one operator (Cat-MCP-Cred-Fleet). Applied to an OSS population whose hosts are independent operators (Tabby, N=70), `I/N = 0.357` is what one expects from per-operator self-signed certs and cloud-platform reuse; not a honeypot signature. The threshold needs a context flag:

- **Within a single suspected operator cohort**: `I/N >= 0.30` = honeypot.
- **Across an OSS population of independent operators**: `I/N` close to 1 is the expected baseline; *low* `I/N` (`<= 0.10`) is the anomaly that flags shared-operator cohorts hiding inside what looks like an organic population.

This inversion is worth its own follow-up insight; tentatively numbered Insight #104.

## Degenerate cases are also data

LMDeploy N=5 all `NET_ISOLATED` is a faithful echo of the original case study: the bootstrap cohort was refuted and the hosts went unreachable. Syllabus-Registry N=4 all `AUTH_OFF` and FATE-FL N=4 all `AUTH_OFF` are degenerate equilibria with zero deviation — Nash gives no extra information here, but the *shape* of the equilibrium (single posture, 100% mass) is itself worth recording: these are populations that have *not yet seen disclosure pressure*, which is exactly the leftmost state of the Insight #40 drift. Re-running these surveys quarterly with the equilibrium recorded each cycle is how we get longitudinal evidence for Insight #40 directly from `S_P` drift.

## Artifacts

- Batch script: `~/nash-recon/scripts/extract-and-run.py`
- Per-survey outputs in each survey directory:
  - `nash-population.csv` — (ip, platform, posture) input
  - `nash-certs.tsv` — (ip, subject_cn) where available
  - `nash-equilibrium.txt` — per-platform `S_P` summary
  - `nash-ranked.tsv` — full surprisal-ranked deviation list

## Operational change going forward

Every new survey, in addition to the existing findings-breakdown, should write `nash-population.csv` and run nash-recon. The equilibrium summary becomes part of the survey's standard output. The top of the ranked deviation list becomes the priority verification queue for the next probe cycle.

## Crosslinks

- [[insight-103-nash-mass-action-foundation-for-auth-on-default]] — the theoretical framework this run exercises
- [[insight-97-cert-heterogeneity-honeypot-discriminator]] — the threshold needing the context refinement above
- [[insight-40-auth-on-default-shifts-rightward]] — the longitudinal claim that `S_P` drift now operationalizes
