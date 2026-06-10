# Insight #103 — Nash mass-action equilibrium as the mechanism behind auth-on-default

**Status:** candidate
**Source papers:** Nash, "Non-Cooperative Games" (Princeton PhD dissertation, May 1950), §9 Motivation and Interpretation; Ioannou, "Nash Equilibrium: Theory" (lecture notes, slides 1-20).
**Codified:** 2026-06-10.

## The claim

The "auth-on-default shifts rightward" thesis (Insight #40) has, until now, been an empirical pattern with a hand-wavy causal story ("disclosure pressure improves defaults"). Nash's §9 "mass-action" interpretation of equilibrium gives that pattern a precise, falsifiable mathematical mechanism, and it dictates exactly what we should be measuring.

## Nash's mass-action interpretation, transposed

Nash's §9 frames an equilibrium without assuming rational, calculating players. Instead:

1. There is a *population* of participants for each position in the game.
2. The "average playing" of the game involves n participants drawn from these populations.
3. Each population converges, through accumulated empirical experience, to a stable frequency over pure strategies.
4. At convergence, every pure strategy that any population uses with positive frequency yields the maximum payoff against the other populations' frequencies (equation (4), p. 4).

Nash's words, near-verbatim: it is *unnecessary* to assume the participants reason about the game; they only need to "accumulate empirical information on the relative advantages of the various pure strategies at their disposal." That accumulation is the disclosure pipeline.

## The mapping to AI-infra exposure

| Nash construct | AI-infra recon construct |
|---|---|
| Population for position *i* | All operators deploying platform *P* (vLLM, Ollama, LMDeploy, Chroma, MLflow, ...) |
| Pure strategy of operator | Auth posture: `AUTH_OFF`, `AUTH_ON_DEFAULT`, `AUTH_HARDENED`, `NET_ISOLATED` |
| Pay-off P_i | Convenience minus expected-cost-of-disclosure minus expected-cost-of-compromise |
| Mixed strategy S_i | Population frequency over postures |
| Equilibrium point | Stable population frequency where no posture would strictly improve a deviating operator's pay-off |
| Symmetric equilibrium (Theorem 4) | For any single-platform population (all operators face the same game), an equilibrium where everyone plays the same mixed strategy must exist |
| Rightward drift of equilibrium | Insight #40: as disclosure pressure raises the expected cost of `AUTH_OFF`, the equilibrium frequency on `AUTH_OFF` falls monotonically |

## Why this is more than a metaphor

Three falsifiable predictions fall out of the mapping immediately.

**Prediction 1 (off-equilibrium hosts).** At equilibrium, hosts running `AUTH_OFF` on a platform whose population has converged to `AUTH_ON_DEFAULT` are, by definition, off-equilibrium players. Nash's mass-action interpretation says off-equilibrium players exist only because of incomplete learning. So an `AUTH_OFF` host inside an `AUTH_ON` population is, with high prior:
- newly deployed (has not seen disclosure pressure yet), OR
- a honeypot (deliberately deviating; the payoff function is different), OR
- abandoned (no learning, no updating), OR
- an adversary cohort (the payoff function is genuinely different — they *want* `AUTH_OFF`).

This is the existing operator-classification grid, derived now from first principles rather than asserted.

**Prediction 2 (cohort = sub-solution).** Nash's sub-solution (§5) is "the set of all n-tuples of mixed strategies belonging to a maximal interchangeable subset of equilibrium points." Concretely, a sub-solution is a *factorable cohort* of equilibria that hang together. Cert-pivot already discovers these: a set of hosts sharing TLS subject, identical port set, identical banner — i.e., the same factored strategy profile. Nash gives this discovery a mathematical name and lets us reason about it: every cert-pivot cohort is a sub-solution; the population partition into cohorts is the partition into sub-solutions.

Operationally: a *single* operator running 88 MCP credential-theft hosts (Cat-MCP-Cred-Fleet, 2026-06-09; I/N = 0.833) is one player playing a single pure strategy 88 times, not a sub-population of 88 independent players. The cert-distribution discriminator (Insight #97) is, in Nash's vocabulary, a test for whether what looks like a population is actually a single player. I/N → 1 means a single sub-solution with one factor; I/N → 0 means many independent equilibrium strategies.

**Prediction 3 (dominance pruning of probes).** Nash §7 ("Dominance and Contradiction Methods") establishes that no equilibrium point can involve a dominated pure strategy. Read backwards from the verifier's side: any verification probe that is strictly dominated by another probe (same evidentiary value, more invasive) is never used in any restraint-equilibrium. The verify-allowlist is the dominance frontier. This is the formal basis for the per-platform path-class taxonomy of Insight #101: the DO_NOT_CALL list is the set of dominated probes.

## What this changes about how we measure

Up to now, surveys report:
- N hosts found
- K verified unauth
- ratio K/N as "auth-off rate"

Under the mass-action framing, the right reportable is the **deviation vector** of each host from the platform's empirical equilibrium frequency, plus the **equilibrium drift** of the population over time. Concretely:

1. Per platform *P*, maintain an empirical posture distribution `S_P = (p_OFF, p_DEFAULT, p_HARDENED, p_ISOLATED)` reconstructed from the survey corpus.
2. For each host `h`, score `deviation(h, S_P) = -log p_S_P(posture(h))` — surprisal under the population strategy. High deviation = candidate of interest (the off-equilibrium classes from Prediction 1).
3. Track `S_P` over survey cycles. Monotone decrease in `p_OFF` is Insight #40 evidence; non-monotone movement is a falsification flag.
4. Per platform, compute the cert I/N ratio (Insight #97) and label the dominant cohort as a sub-solution factor; report sub-solution count and largest-cohort share alongside the headline number.

## Conjecture (testable)

For any AI-infra platform with a public disclosure pipeline operating for >= 18 months, the population posture distribution `S_P` converges to a stable equilibrium with `p_OFF < 0.10` and `p_HARDENED + p_ISOLATED > 0.60`, and the convergence is monotone in time. Counter-examples (platforms whose `p_OFF` is rising under disclosure pressure) are direct refutations and would force a respecification of the payoff function (most likely: the platform's operator cohort has a payoff function distinct from the disclosure pipeline's assumptions, i.e., they are not the disclosure pipeline's target audience).

## Tool implication

A new tool, `nash-recon`, computes the deviation score per host against the empirical equilibrium reconstructed from the corpus. It is built as a single Go binary; see `~/nash-recon/`. Output is a ranked candidate list for the verification stage, replacing the "probe everything" default with "probe deviations first." This is the Nash-dominance pruning of the verification chain (Prediction 3) realized as a tool.

## Provenance

Both source PDFs are at `~/Downloads/Nash Equilibrium Theory.pdf` (lecture notes) and `~/Downloads/Non-Cooperative_Games_Nash.pdf` (Nash's 1950 dissertation, 32 pp.). The mass-action argument is on pp. 21-23 of the dissertation. The symmetric-equilibrium theorem is Theorem 4, p. 8. Dominance methods are pp. 15-16.

## Crosslinks

- [[insight-40-auth-on-default-shifts-rightward]] — empirical pattern this insight provides the mechanism for
- [[insight-97-cert-heterogeneity-honeypot-discriminator]] — I/N ratio as sub-solution-factor measurement
- [[insight-101-per-platform-path-class-taxonomy-encodes-restraint-at-code]] — DO_NOT_CALL as dominance frontier
- [[insight-100-brown-2018-to-2026-delta-as-insight-40-evidence]] — longitudinal equilibrium drift evidence
