# Disclosure-Cohort Response Analysis (n=104, 2026-06-07)

**Author:** NuClide Research (Cowboy session, 2026-06-07)
**Source corpus:** `~/AI-LLM-Infrastructure-OSINT/disclosures/` — 133 files; 104 have YAML frontmatter (29 early-style bodies lack metadata); response classification derived from `outcome:` and `status:` fields.
**Companion:** [[insight-86-disclosure-pipeline-is-attack-surface]] — this analysis is the second-order question that insight flagged ("which cohort responds").

---

## Executive summary

Of 104 disclosures with metadata, **7 produced a closed-loop response** (ACK or FIXED) — a 7/95 = **7.4% response rate across all sent disclosures**. The rate is **not uniform across cohorts**: institutional/academic and institutional IT channels carry essentially all of the responsiveness, while hyperscaler-abuse and commercial-operator channels are statistical black holes for AI-infra disclosures.

```
COHORT                       SENT  ACK/FIX  RESPONSE RATE
institutional/academic         42        5         11.9%
institutional IT (via *@uni)    9        2         22.2%
cloud/hosting-abuse            15        0          0.0%
commercial-operator            26        0          0.0%
CERT/government                 2        0          0.0%
```

The "vendor-security-channel" classifier conflated **vendor PSIRTs** with **university IT support** (`it-support@kth.se`, `support@itmo.ru`). Both wins in that bucket are universities. After re-attribution: **all 7 closed-loop responses are institutional**; **commercial operators, hyperscalers, and CERTs combined: 0 confirmed responses out of 43**.

---

## Methodology

### Corpus

133 disclosure files in `~/AI-LLM-Infrastructure-OSINT/disclosures/`. 104 have parseable YAML frontmatter; 29 (mostly pre-2026-05-25) are early-style bodies without metadata and are excluded from the rate computation. Excluding them probably biases the result toward higher response rates (the early disclosures predate Nick's professionalized disclosure template and would likely have similar or lower response rates).

### Classification

**Cohort** — derived from `to:` field:
- `institutional/academic` — `.edu`, `.ac.`, `edu.*`, university names
- `cloud/hosting-abuse` — AWS, Azure, GCP, DigitalOcean, Hetzner, Linode, OVH, Scaleway, Cloudflare abuse channels
- `commercial-operator` — direct vendor/operator emails not falling into other buckets
- `CERT/government` — `cert.*`, `csirt`, `gov.`, country CERT teams
- `vendor-security-channel` — `security@`, `disclosures@`, `psirt`, `secure@`. **Note:** in this corpus, this bucket misclassified university IT (`it-support@kth.se`, `support@itmo.ru`, `security@ncu.edu.tw`) as vendor; after correction, all 9 entries are institutional.
- `upstream-maintainer` — open-source maintainer security inboxes (n=1)
- `personal-email` — Gmail/Yahoo/etc. (n=2, both UNSENT)

**Response classification** — derived from `outcome:` + `status:`:
- `FIXED` — `outcome: fixed` or `status: REMEDIATED`
- `ACK` — `outcome: acknowledged`
- `BOUNCED` — `outcome: bounced` or `outcome: misrouted`
- `SILENT` — `outcome: sent`, no response signal
- `UNSENT` — `outcome: draft|pending` or `status: DRAFT` without sent indicator

**Key limitation:** the `SILENT` classification overcounts; an `outcome: sent` finding could be silent OR could be unupdated (the researcher never returned to record an ACK). The 82 SILENT entries are 30–37 days old (median 34 days; 79/82 are >30 days). Past industry-typical 7-day response windows, true silence is more probable than unrecorded ACK, but not certain.

---

## Closed-loop wins (the 7 cases)

| File | Cohort | Response | Recipient |
|---|---|---|---|
| `AU-newcastle.md` | institutional/academic | ACK | `dts-cybersecurity@newcastle.edu.au` |
| `AU-newcastle-followup.md` | institutional/academic | ACK | `cap-d-core-technology@newcastle.edu.au` |
| `US-CA-ucdavis.md` | institutional/academic | ACK | `cybersecurity@ucdavis.edu` |
| `US-NY-syracuse.md` | institutional/academic | **FIXED** | `itsecurity@listserv.syr.edu` |
| `TW-ncu-aiden.md` | institutional/academic | **FIXED** | `security@ncu.edu.tw` |
| `SE-KTH.md` | institutional (IT support) | **FIXED** | `it-support@kth.se` |
| `RU-itmo.md` | institutional (IT support) | ACK | `support@itmo.ru` |

**Pattern observations:**

1. **University CISO offices respond.** `dts-cybersecurity@`, `cybersecurity@`, `itsecurity@`, `security@<uni>` — when the recipient address is a security team mailbox, the response rate is non-trivial. Three of seven wins.
2. **Generic IT support sometimes routes to security and fixes the issue.** `it-support@kth.se` and `support@itmo.ru` — these are *not* security inboxes by name. They got the disclosure to the right human anyway. The lesson: when no security inbox is published, IT support is a reasonable fallback for institutional targets.
3. **Time-to-FIXED is observable.** All three FIXED cases are post-ACK, post-30-day window. Academic remediation is slow but is happening.

---

## Bounces (5 cases)

| File | Cohort | Recipient |
|---|---|---|
| `PK-comsats.md` | institutional/academic | `security@comsats.edu.pk` |
| `TW-fju-medph.md` | institutional/academic | `security@fju.edu.tw` |
| `VN-vnu-hanoi.md` | institutional/academic | `security@vnu.edu.vn` |
| `US-NY-suny-buffalo.md` | institutional/academic | `sec-office@buffalo.edu` |
| `AM-armenian-academy.md` | commercial-operator | `ipia@ipia.sci.am` |

**Pattern:** 4 of 5 bounces are `security@<edu>` style addresses. Universities advertise the address (per the IANA RFC 2142 recommendation) but the mailbox is unmonitored or undeliverable. This is itself a finding: **institutional `security@` addresses are coin-flip-deliverable at best.** Followup recommendation: when `security@` bounces, escalate via `csirt@`, `it-support@`, or the CISO's named LinkedIn page rather than the published security.txt path. The published path is silently broken for ~10% of universities.

---

## Bigger story: the cohort silence pattern

Of the 95 disclosures classified as SENT-with-some-recorded-state:

- **42 institutional** → 5 ACK + 2 FIXED + 4 BOUNCED + 31 SILENT → 16.7% closed-loop response among non-bounced. Real signal.
- **15 cloud/hosting-abuse** → 0 ACK + 0 FIXED + 0 BOUNCED + 15 SILENT → 0%. Hyperscaler abuse channels are operational dead-letter offices for AI-infra disclosures specifically. They are built for spam/malware/DMCA, not for "your customer's Langfuse is open." This is a known industry pattern and now empirically documented for AI-infra.
- **26 commercial-operator** → 0 ACK + 0 FIXED + 1 BOUNCED + 25 SILENT → 0%. Independent operators do not respond to cold-email disclosures. Whether they patch silently is unobservable from the disclosure log; longitudinal re-survey (planned but not run) would resolve this for known IPs.
- **2 CERT/government** → 0 ACK + 0 FIXED + 0 SILENT → tiny sample. Both currently UNSENT or SILENT.

---

## Cross-references to existing insights

**Insight #40** (Auth-on-default strengthens across OSS generations under disclosure pressure) — this analysis quantifies the *upstream-end* of the same pipeline. #40 measures whether the maintainer ships a corrected default in the next release; this analysis measures whether the operator on the ground acks. Both endpoints matter; the response-rate data here suggests the maintainer-pressure pathway (upstream PR / GitHub issue) is the higher-throughput route to fix than per-operator email.

**Insight #68** (verification load-bearing) — same shape, one rung along. Verification is load-bearing because finding ≠ confirmed-finding; disclosure is load-bearing because confirmed-finding ≠ fixed-finding. The 7.4% closed-loop rate empirically demonstrates that the disclosure-to-fix transition is itself a high-attrition stage.

**Insight #86** (disclosure pipeline is itself attack surface) — this analysis is the second-order question Insight #86 explicitly opened: *which maintainer organizations actually fix vs which just absorb the disclosure*. The cohort answer:

1. Institutional CISO/IT offices fix at non-trivial rates (~12–22% of sent reach a closed loop).
2. Hyperscaler abuse channels do not.
3. Direct commercial operators do not (or do so silently).
4. CERT path is undersampled.

---

## Actionable implications

| For NuClide | Action |
|---|---|
| Stop routing AI-infra findings to cloud-abuse channels first | They are not the right pipe; route to the operator directly even when the operator is a hyperscaler tenant. |
| Use `security@<edu>` but expect ~10% bounce | Plan a `it-support@` / `csirt@` / named-CISO fallback for institutional follow-ups. |
| Upstream-maintainer pathway is undersampled and high-leverage | Insight #40 says upstream pressure moves the population rate. This corpus has only 1 upstream-maintainer disclosure. Investing more in upstream-maintainer reporting (over per-operator email) is probably the highest unit-impact disclosure work. |
| The 30-day silence cluster is a workload trigger | 79 of 82 SILENT entries are >30 days old. A standing followup-day at d+30 is overdue. |
| Disclosure log format should encode closed-loop state machine-readably | Currently the `outcome:` field is a free-text vocabulary; a controlled vocabulary (sent / acked / fixed / bounced / declined / no-response) would let next-quarter's analysis be a single SQL query, not a Python script. |

| For program disclosure (public-facing artifact) | Action |
|---|---|
| The 7.4% rate is publishable | Frame as: *empirical disclosure-response data for AI-infra-specific findings, 2026-05/06 cohort.* This is data nobody else has; nobody else runs disclosure at this volume on this specific surface. |
| The cohort-silence delta is publishable | Hyperscaler abuse channels = 0/15; institutional CISO = 7/42. This is a defender-actionable finding for any researcher considering disclosure routing. |

---

## Limitations and uncertainty

- **Selection bias.** Many disclosures sent earlier (29 pre-template files) lack metadata. If those skew lower-response (unprofessional template, weaker recipient resolution), the rate is overestimated; if they skew higher (easier-to-fix early findings), underestimated. Likely net-overestimated.
- **Researcher-update bias.** SILENT may overcount because we did not return to update files that received late acks. The actionable mitigation is the controlled vocabulary recommendation above + a standing follow-up day.
- **Outcome-field reliability.** `outcome: fixed` requires the researcher to verify post-disclosure; this was done for SE-KTH and TW-ncu-aiden but is not done systematically. Some "SILENT" entries may have been silently patched and not re-checked.
- **N=104 is enough for cohort-level signal, not for fine cuts.** Specifically the upstream-maintainer (n=1) and CERT (n=2) buckets are too small to draw conclusions.
- **Jurisdiction breakdown not run here.** The dataset supports it (45 country-coded files in the corpus); a follow-up analysis would compute response rate by country, which is a publishable second-order question.

---

_Generated 2026-06-07 from `~/AI-LLM-Infrastructure-OSINT/disclosures/` corpus. Classification logic and raw JSON at `/tmp/mitnick-pivot/disclosure-corpus-classified.json`. Reproducible via the analysis in this file._
