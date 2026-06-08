# Insight #86 — The disclosure pipeline is an attack surface

**Status:** Candidate (1 program-wide data point: NuClide 2026-05 through 2026-06-07)
**First evidence:** 2026-06-07 audit of `~/AI-LLM-Infrastructure-OSINT/disclosures/` (142 sent) and `research-program/disclosures/INDEX.md` (~30 QUEUED, 0 in any post-send state).
**Author:** Mitnick-lens re-frame during Cowboy session 2026-06-07.

---

## Claim

A public disclosure pipeline that publishes per-finding state (`QUEUED` / `SENT` / `ACK` / `RESOLVED`) creates two adversary-readable signals that operate independently of the underlying technical findings:

1. **The state field labels live wires for an opportunistic actor.** Any finding in `QUEUED` or `SENT-not-yet-ACK` is, by definition, "operator has not finished remediation." Reading the public pipeline tells an attacker which targets are still vulnerable without the attacker re-running discovery. The researcher did the recon work and published the labels.
2. **The unsent queue itself is a self-disclosed researcher bottleneck.** When the queue is large and old, the structural failure is researcher-side intake bandwidth, not operator unresponsiveness. From the operator's perspective, a finding sitting `QUEUED` is functionally indistinguishable from a finding nobody discovered. The pipeline state document quantifies that gap publicly.

The combined signal is a researcher-built enrichment for any actor watching the OSINT repo.

---

## Evidence (NuClide program, 2026-06-07)

| Bin | Count | Note |
|---|---|---|
| Sent (in `disclosures/`) | 142 | Some have body content describing recipient response; most do not encode state machine in the file itself. |
| Queued (in `research-program/disclosures/INDEX.md`) | ~30 | Institutional + upstream-maintainer + 1 CRITICAL-ENTERPRISE (Capitol.ai). All currently `QUEUED`. |
| Acked / Resolved / Expired (any bin) | **0 published** | The state machine defined in `INDEX.md` exists; no finding has been promoted past `QUEUED` in the post-2026-06-06 generation. |

Of the 142 sent files, the response-tracking format varies per-file — there is no machine-readable response state. The aggregate-level "which maintainers respond" cohort question is unanswered in the repo, but the per-finding "this one is QUEUED right now" question is fully answered.

---

## Why this is structurally similar to verification-as-load-bearing (Insight #68)

Insight #68 observes that scanning out-paces verification, and the verification stage is where the program's epistemic load actually sits. The disclosure pipeline rhymes with that pattern one stage further:

```
SCAN → VERIFY → CODIFY → DISCLOSE → ACK → RESOLVE
 ↑       ↑                  ↑
 cheap   load-bearing        load-bearing again, and bottlenecked
         (Insight #68)       (this insight)
```

Both bottlenecks share a failure mode: producing more upstream output (scans / findings) makes the downstream gap *visible* without closing it. The pipeline-state publication makes the visibility maximal.

---

## Adversary use case (read-only, no probing required)

An opportunistic actor wanting AI/LLM infrastructure targets, given the public OSINT repo:

1. Pull `research-program/disclosures/INDEX.md`.
2. Filter to `QUEUED` and `SENT` (not `RESOLVED`).
3. Cross-reference against the per-platform surveys for IP/hostname.
4. Target list ready, severity pre-graded, jurisdiction labeled.

The attacker spends no recon budget. The reconnaissance work the researcher did to produce the pipeline IS the recon work the attacker would otherwise have to do.

---

## Why this generalizes

Any disclosure program with these three properties produces this surface:

| Property | NuClide today | Common in industry |
|---|---|---|
| Per-finding state machine published | yes | Increasing — many bounty programs do |
| State machine has a `QUEUED`/pre-send state | yes | Less common; usually private until SENT |
| State machine and per-finding artifact (IP, recommendation) co-located | yes | Less common |

The risk-multiplier is the *combination*. Per-finding state is fine if findings are private; finding artifacts are fine if state isn't published; both together is the inversion.

---

## NuClide-specific remediation options

1. **Pre-send privacy.** Strip target identity from `QUEUED` entries — list category + severity + queue position, not IP or operator name. Publish identity only after `SENT` (operator is on notice).
2. **Post-resolution publication only.** Mirror the public bug-bounty convention: only publish the case study once the operator has had reasonable time to remediate.
3. **Embargo window.** Each queued entry carries a date after which it is published in full regardless of operator action.

The Mitnick-lens framing is option 3 + option 1: an embargo enforces honesty (the researcher cannot indefinitely hold findings), and `QUEUED` redaction denies the attacker the meta-enrichment without losing the program's transparency commitment.

The trade-off is real: NuClide's transparency posture and academic-grade auditability arguably depend on publishing pipeline state. The point of the insight is to be honest about what the transparency posture costs.

---

## Codification-stage hypothesis (the second-order question)

The 142 sent files contain implicit response patterns (which maintainers ack quickly, which never respond, which patch silently). Surfacing those patterns is itself a follow-on research move:

- **Maintainer-response cohort segmentation.** Which open-source vendors respond to direct disclosure within 7/30/90 days? Which CERTs route? Which jurisdictions accept disclosure but never confirm fix?
- **Operator-class response delta.** Is institutional intake (universities, government) systematically slower than commercial intake? Is the inverse true?

This is fertile ground because the *response* (or non-response) data is information the researcher has uniquely accumulated through running the program. It is not derivable from any public source other than NuClide's own log. It is also probably more interesting to defenders than any one platform survey.

---

## Action items implied by this insight

1. **Decide the transparency posture.** Either publish queue identity (current) or redact (proposed). The choice is a researcher-policy question, not a technical one. Default-current is fine if explicitly chosen rather than inherited.
2. **Schedule the maintainer-response cohort analysis** as a research-program work item. Tag the 142 sent files with response-bucket metadata.
3. **Add `QUEUED → SENT` automation** so the researcher-side bottleneck is visible to the researcher as well as to readers. The bottleneck is currently invisible to NuClide internally because there is no aging visualization.

---

## Cross-references

- [[insight-68]] — Verification as the load-bearing stage. Same structural pattern at a different pipeline rung.
- [[reference_research_program_directory]] — The directory layout that makes this insight observable.
- [[project_capitol_ai_enterprise_saas_finding]] — The most-blast-radius finding currently sitting in `QUEUED`; the case that motivates the embargo-window proposal.
- [[reference-insight-40-auth-on-default-shifts-rightward]] — Insight #40 measures the upstream-maintainer end of the same pipeline. This insight measures the researcher's end.

---

_Codified 2026-06-07 from the Mitnick-lens reframe: "the disclosure surface itself is a finding."_
