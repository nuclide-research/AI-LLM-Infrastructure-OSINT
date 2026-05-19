---
title: "<Finding or survey title — short, news-headline style>"
date: 2026-MM-DD
type: case-study  # or survey, disclosure, methodology
sector: commercial  # or government, education, healthcare
tags: [...]
---

# <Title>

_NuClide Research · <date> · <one-line sub-header — what the case study covers>._

## Summary

<2–4 sentences. What was found, why it matters, who it affects. No buildup,
no rhetorical "we discovered" framing. Lead with the conclusion.>

## Thesis fit (when applicable)

<If the case study confirms / extends / falsifies the auth-on-default thesis or
a specific numbered Insight, state which and how. Otherwise omit this section.>

---

## Per-finding entries

**One block per finding.** A "finding" = one operator or one host where a
specific exposure was verified. A survey case study may have many of these;
a single-host case study has one.

Each finding follows the four-section + tool-attribution structure below.

### F<N>. `<URL or target identifier>`

#### What was found

<Plain description of the observed state. What the probe returned. What was
visible. No inference, only what was directly observed. Cite the specific
response (status code, JSON key, body string) that established the claim.>

#### Why it is bad

<The operational impact. Distinguish between (a) what is directly verified by
the probe and (b) what would be reachable via further chain steps not exercised
per the restraint ethic. Use the Verified / Inferred / Hypothesized tier
markers where the distinction matters.>

#### Who it affects

<Operator identity if attributed, hosting provider, jurisdiction,
regulatory context. Affected parties downstream of the operator if any
(customers, users, data subjects).>

#### How it got exposed

<Root cause. What shipping default, operator action, or architectural
choice produced this exposure. Tie to the relevant numbered Insight where
applicable (Insight #13 for shipping-defaults-load-bearing, Insight #12 for
IP-direct-shadow, etc.). One or two short paragraphs. This is the section
readers learn from — it should let another operator running the same
software audit their own deployment.>

#### Which tools contributed to the finding

| Stage | Tool | Contribution |
|---|---|---|
| 0 — Discover | <tool> | <what it found, with the specific dork / signal> |
| 1 — Fingerprint | <tool> | <how the platform was confirmed> |
| 2 — Verify | <tool> | <the primary-source probe + the response that proved the claim> |
| 3 — Attribute | <tool or "n/a — bare cloud IP"> | <attribution mechanism if any> |
| 4 — Classify | <tool> | <classification category> |
| 5 — Ledger | VisorLog | <finding ID, severity, lifecycle status> |
| 6 — Score | VisorScuba | <score + violation code> |
| 6 — Exploit-rank | BARE | <top match + score + tier verdict> |
| ... | ... | ... |

**Tools that ran but did not contribute unique signal**: <list with one-line
why each null result is recorded; per the methodology's "no silent skips"
rule>.

**The load-bearing chain for this finding**: <comma-separated sequence of
tools whose output was each strictly necessary to reach the finding>.

---

## Cross-survey / cross-finding analysis

<For survey case studies. Patterns observed across findings; persistence
ratios; provider distributions; population deltas vs prior surveys. Cite
relevant Insights by number.>

## Methodology — what this case study adds

<If the work generated a new Insight or extended an existing one, write it
here and cross-link to the `methodology/insight-NN-*.md` file.>

## Honest negative space

<What this method cannot see. Where confidence is lossy. Tools that have
coverage gaps. Carry-forward queries.>

## Disclosure queue (verified scope)

<List findings ready for disclosure with the routing per finding. Include
verification tier — what is verified vs inferred vs not exercised.>

## Toolchain provenance

```
<linear or tree representation of the chain that produced the case study —
already a NuClide convention, retained as the survey-level summary even when
per-finding tables are present>
```

## See also

<links to related case studies, baseline surveys, Insight files, contributor
docs>

---

## Conventions

### Verified / Inferred / Hypothesized tier markers

Per [`feedback_verify_before_claiming_exploitable`](../.claude/projects/-home-cowboy/memory/feedback_verify_before_claiming_exploitable.md):

- **Verified** — the probe ran and the response established the claim. Cite
  the specific endpoint and response.
- **Inferred** — the chain to claim X requires an additional probe Y that
  was not run (often because Y crosses the restraint-ethic line). State
  explicitly what was not exercised.
- **Hypothesized** — possible based on the surface but no direct evidence.
  Mark as such or do not state at all.

### Tool-attribution table

Adopted 2026-05-18 from the code-assistants survey per-finding review.
Every finding entry includes the tool-attribution table. Stages match the
canonical pipeline: 0 Discover, 1 Fingerprint, 2 Verify, 3 Attribute, 4
Classify, 5 Ledger, 6 Score / Rank / Corpus, 7 Codify.

Tools that ran and produced null results are recorded with their null —
"no silent skips" per the methodology. Tools that are not applicable
(VisorHollow on Linux, VisorAgent against operator hosts) are recorded
with the reason.

### Voice

Hemingway prose. No em dashes. No two-beat reveals. No "we discovered" /
"interestingly" framing. State the finding; explain the consequence; cite
the source. The reader is a peer practitioner — they do not need narrative
buildup.
