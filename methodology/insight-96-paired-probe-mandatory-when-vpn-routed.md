# Insight #96 — Paired-Probe + Sandbox-MITM Check Are Stage 0 PREREQUISITES Under Non-Local Routing (Candidate)

_NuClide Research · 2026-06-09 · Origin: Cat-Tabby + Devstral re-validation, Stage 0 VPN-exit response-rewriting contamination._

---

## Statement

When a survey is conducted via any non-local routing layer (VPN exit, corporate proxy, cloud-NAT egress, transit through any intermediary that can rewrite L7), the sandbox-MITM consistency check AND paired-probe validation are MANDATORY Stage 0 prerequisites — not §3 standing advice. Skipping them at Stage 0 produces L7 conclusions that look confident and reproducible while being silently rewritten by the intermediary. The contaminated cross-section is inner-A / outer-0 per Insight #68: logic-only, no live host actually exercised via a clean route. Without the check, the survey produces confident, reproducible, wrong numbers.

## The incident

2026-06-09 Cat-Tabby + Devstral re-validation. Stage 0 ran across the 10,895-host confirmed-unauth Ollama corpus while egressing through Mullvad WireGuard (`us-phx-wg-206` -> Miami exit). First pass produced:

- 1,217 "code-model-loaded" hosts (434 Devstral) from `/api/tags`
- 117 self-hosted hosts with `:9090` open from shadow-sweep
- 66 "confirmed Tabby" hosts via `/auth/signin` title match on the 117

Lane A then re-probed three of the 66 and three of the 1,217:

- 3/3 Tabby `/auth/signin` re-probes returned EMPTY bodies (no `<title>Tabby`) — the first-pass match was a templated injection
- 3/3 Ollama `/api/tags` re-probes returned DIFFERENT model loadouts on the SAME IP (e.g. `qwen2.5:1.5b` substituted where `codellama:13b` had been reported)

Same IP, same endpoint, minutes apart, different body. The variable was somewhere between us and the host, on our side. The 1,217 / 434 / 117 / 66 cross-section was retracted.

## Verification-rung characterization (per Insight #68)

The contaminated result is **inner-A / outer-0**: the matcher logic is reproducible (Depth-A: rerun via the same contaminated path returns the same numbers), but no live host was actually exercised through a clean route (Breadth-0: zero independent confirmation that the response originated from the target rather than the routing layer). Contaminated results MUST carry this rung label. Without that vocabulary, they look like Depth-B / Breadth-2 findings (verified, multi-source) — confident, reproducible, wrong.

## Why standing §3 advice is insufficient

Methodology §3 ("Distrust your observation position") is correct but does not carry execution force. It tells you to be suspicious, not to run a specific check. The recongraph and VisorGraph tools BOTH implement a formal sandbox-MITM consistency check at startup — they downgrade L7 conclusions automatically when an intercepting environment is detected. That check was never lifted into a Stage 0 prerequisite gate for bespoke survey tooling (shodan-fetch + Python aiohttp probers). The 2026-06-09 incident is the proof that "standing advice" gets skipped at Stage 0 because Stage 0 has too much momentum: harvest is fast, probes are fast, the result table fills in, and the verification consciousness arrives at Stage 3v — already past the point where a contaminated Stage 0 has shaped the cross-section.

## Recommendation — specific tooling

1. **Lane C sandbox-MITM check as Stage 0 prerequisite.** Lift the recongraph / VisorGraph implementation into a standalone script (`stage0-mitm-check.sh`) that runs BEFORE shodan-fetch / aimap / scanner against any non-local-routed corpus. The check emits a single line: `MITM-RISK: clean | suspect | confirmed`. `suspect` or `confirmed` downgrades all subsequent L7 conclusions to inner-A / outer-0 until a clean route is established.
2. **Lane A paired-probe methodology in output schemas.** Every L7 probe record in shodan-fetch, aimap, and scanner output gains a `paired_match: true | false | skipped` field. The probe is re-issued at T+N seconds (default 60-120s) over the same routing layer; the response hash MUST match. `paired_match != true` blocks tier-label promotion. The 3-sample probe used in the 2026-06-09 incident is the minimum viable instrument; the production version pair-probes every record.
3. **Route diversity at Stage 0 under non-local routing.** Where egress is non-local, require at least two distinct exits (or one VPN + one direct) and require both to agree on the identity probe before promoting from candidate to confirmed. If only one exit is available, all results are inner-A / outer-0.
4. **Output schema gating.** Until `paired_match: true` AND `MITM-RISK: clean`, the record carries an explicit `verification_rung: A/0` label. No case study, finding, or disclosure can cite a record without `B/1` or higher.

## Cross-references

- **Insight #68** — Verification-rung grid (Depth A/B x Breadth 0/1/2). This Insight is the routing-layer application of #68's vocabulary.
- **Insight #11** — Source-vs-framing. The routed observation point IS framing; the host's real response IS the primary source. Same class of error, different layer.
- **Insight #77** — Live-rate floor. Contamination class is different from staleness; both must be excluded before population claims are made.
- **Methodology §3** — "Distrust your observation position." This Insight converts the §3 standing advice into an execution gate at Stage 0.

## Restraint discipline note (Lane D, K0107)

The discipline win documented in the parent analysis: zero disclosures sent based on the contaminated 1,217 / 66 numbers. Restraint held the artifact in place until Lane A's paired-probe surfaced the divergence. Without that step, the cross-section would have been published as findings. The methodology produced the right outcome because the restraint discipline outlasted the harvest momentum. The codified fix (this Insight) brings the gate forward to Stage 0 so the next survey does not have to depend on Lane A catching it at the back end.

---

_Status: CANDIDATE. Promotion to numbered Insight pending one additional cross-survey confirmation (a second VPN-routed survey running the new Stage 0 gate and either passing it clean OR catching a second contamination instance). Cite this incident as the founding evidence._
