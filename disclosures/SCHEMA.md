# Disclosure-File Schema (Controlled Vocabulary)

**Status:** Active as of 2026-06-07.
**Driver:** Disclosure-cohort response analysis (`research-program/disclosure-cohort-response-analysis-2026-06-07.md`) revealed the existing free-text `outcome:` vocabulary makes cross-cohort analysis a Python script rather than a query. This schema fixes that.

---

## Required frontmatter

Every disclosure file in this directory must begin with:

```yaml
---
to: recipient@example.com           # required, single email or comma-list
cc: abuse@nuclide-research.com      # optional
ip: 1.2.3.4                          # if applicable
institution: "Org Name — finding gist"  # required for context
severity: CRITICAL | HIGH | MEDIUM | LOW   # required, one of these four
status: DRAFT | SENT | REMEDIATED          # required, see lifecycle below
outcome: pending | sent | acknowledged | fixed | declined | bounced | no-response   # required if status != DRAFT
date: YYYY-MM-DD                    # required, the date `status` was last updated
date_sent: YYYY-MM-DD               # required when status >= SENT
note: "optional free-text"
---
```

---

## Status lifecycle

```
DRAFT ──(send)──► SENT ──(ack)──► (still SENT, outcome:acknowledged)
                   │                       │
                   │                       ▼
                   │              (fix)──► REMEDIATED (outcome:fixed)
                   │
                   ├──(bounce)─► SENT, outcome:bounced
                   └──(silent for 60+d)─► SENT, outcome:no-response
```

- `status: DRAFT` — disclosure exists but has not been sent.
- `status: SENT` — disclosure was sent. The `outcome:` field carries the response state.
- `status: REMEDIATED` — verified-fixed by re-probe.

---

## Outcome controlled vocabulary

| Value | Meaning | Applies when |
|---|---|---|
| `pending` | Draft not yet sent | `status: DRAFT` |
| `sent` | Sent, no further information | Default after send |
| `acknowledged` | Recipient confirmed receipt | After ACK email |
| `fixed` | Re-probe confirms remediation | After verified fix |
| `declined` | Recipient declined to engage | Explicit refusal |
| `bounced` | Mail did not deliver | Bounce notification |
| `no-response` | 60+ days silent, escalation declined | Researcher closes the case |

No other values are valid. Do not invent ad-hoc states (e.g. `misrouted`, `drafted`, `pending-followup`); use the closest defined value and explain in `note:`.

**Convention:** Once you set `outcome: bounced`, also add a `bounce_date:` and a `bounce_followup:` (link to the next-attempt file if you re-send via a different recipient).

---

## Why this vocabulary

The 2026-06-07 cohort analysis ran into the following issues with the prior free-text vocabulary:

- `outcome: sent` (n=82) was ambiguous — silent vs. ack-not-recorded.
- `outcome: drafted` (n=3) collided with `status: DRAFT`.
- `outcome: misrouted` (n=1) was a one-off variant of `bounced`.
- Three files had empty `outcome:` and could not be classified.

After this schema is enforced and a follow-up day is run on the 82-deep `sent` cohort, the silent-vs-acked distinction becomes legible.

---

## One-time migration (2026-06-07)

The migration script `migrate-outcome-vocab.py` (in this directory) maps the pre-2026-06-07 free-text values to the controlled vocab:

| Old value | New value |
|---|---|
| `sent` | `sent` (unchanged — explicit silent vs ack-not-recorded resolution still requires d+30 follow-up) |
| `pending` | `pending` |
| `drafted` | `pending` |
| `acknowledged` | `acknowledged` |
| `fixed` | `fixed` |
| `bounced` | `bounced` |
| `misrouted` | `bounced` |
| (empty) | `pending` if `status: DRAFT`, else `sent` |

Once migrated, all files conform to the schema above. The 29 pre-2026-05 files without any frontmatter are out of scope for this schema; they remain bare-body documents.

---

## Cross-references

- [[insight-86-disclosure-pipeline-is-attack-surface]] — the meta-insight that flagged free-text vocab as a transparency/analysis problem.
- [[disclosure-cohort-response-analysis-2026-06-07]] — the analysis that prompted this schema.
- [[disclosure-followup-worklist-2026-06-07]] — the d+30 followup worklist that operates over this schema.
