---
type: methodology
insight_number: 53
title: "A hostname label is not a cloud project identifier"
---

# Insight #53 — A hostname label is not a cloud project identifier

**Codified:** 2026-05-21 (global university LLM-exposure map, per-host arsenal triage, Firebase candidate verification)
**Family:** Insight #51 (a port number names a candidate), Insight #52 (an HTTP 200 is not that API), Insight #16 (no status code is identity). This one is the attribution-stage variant. In #51 and #52 the thing is not there. In #53 the thing is there, real and public, and it is not the target's.
**Falsifiability tier:** high. A sweep where hostname-label-guessed cloud names verify as the target's own resource at a material rate breaks it.

---

## The pattern

A scanner that derives a cloud resource name from a target's hostname label, probes that name in a global namespace, and reports the hit as the target's exposure produces confident, reproducible, misattributed findings. A short generic word resolved in a global namespace belongs to whoever registered it first. That is almost never the host the word was lifted from.

Stated empirically, with the source case:

`menlohunt`'s phase-4 `checkFirebase` took the host's reverse-DNS, split it into labels with `extractNames`, and probed `https://<label>.firebaseio.com/.json` for each label. A 200 with a non-empty body became "Firebase Realtime Database — public read confirmed", severity CRITICAL.

On the university survey it produced 4 such CRITICALs. They were 2 distinct Firebase projects, each reported on 2 host:port entries:

| Project probed | Lifted from | Host's real identity | Project's actual content |
|---|---|---|---|
| `earth.firebaseio.com` | label `earth` | `jupyterhub2.earth.ox.ac.uk` — Oxford, Dept of Earth Sciences | a music-gigs app: `{"music":{"gigs":[...]}}` |
| `marine.firebaseio.com` | label `marine` | `manglillo.marine.usf.edu`, `ocgmod1.marine.usf.edu` — USF Marine Science | `{"users","reports","marines","imarines","cats","searchHistory","test"}` |

Both databases are real and genuinely public. A `?shallow=true` marker read confirmed it. Neither belongs to the university whose hostname carried the word. `earth` is a music app. `marine` is some unrelated developer's project. menlohunt attributed both to university hosts because the universities happen to have the words "earth" and "marine" in their DNS.

The exposure is real. The attribution is false. A finding is a host plus an exposure. Getting the exposure right and the host wrong is still a wrong finding.

## Mechanism

`extractNames` splits a reverse-DNS name on `.` and keeps every label longer than three characters. `jupyterhub2.earth.ox.ac.uk` yields `jupyterhub2` and `earth`. Those labels are then fed to three global-namespace probes: `checkFirebase` (`<name>.firebaseio.com`), `checkGCS` (`storage.googleapis.com/<name>`), and `checkCloudRunFunctions` (`<name>-<region>.cloudfunctions.net`).

A global namespace is first-come, first-served and flat. `earth`, `marine`, `data`, `cloud`, `api` were all registered years ago by unrelated developers. A scanner that probes a bare generic word will hit one of those projects, and the hit has nothing to do with the host the word came from.

The label is a real signal. It says something about the host. It does not name a resource the host owns. Ownership is established by a reference the host itself emits: a project ID in a TLS certificate SAN, in a served JavaScript bundle, in a page body. A word in the host's domain name is not that reference.

## What this insight is NOT

- NOT "the firebase check is useless." Firebase exposure is real and worth finding. The error is sourcing the project name from a hostname label instead of from a reference the host emits.
- NOT specific to Firebase. `checkGCS` and `checkCloudRunFunctions` share the same `extractNames`-derived input and the same failure mode. A GCS bucket named `marine` is no more USF's than the Firebase project is.
- NOT "the databases are safe." `earth` and `marine` are genuinely public and exposed. They are findings for whoever owns them. They are not findings for the universities, and not in scope for a university survey.
- NOT specific to menlohunt. Any scanner that guesses cloud resource names from target hostnames has this misattribution mode.

## Falsification conditions

The insight is wrong if:

1. A sweep of hostname-label-guessed cloud names verifies as the target's own resource at a material rate, say above 10%.
2. The collision turns out to be an artifact of generic university DNS labels and specific, non-generic labels guess correctly often enough to be worth the misattribution cost.

## The scanner-design corollary, and the fix

The fix is structural. A scanner must not attribute a global-namespace resource to a host on the strength of a shared word. It must either source the resource name from a reference the host emits, or not claim the host owns it.

Codified into menlohunt, commit pending (2026-05-21):

- `checkFirebase` skips bare labels. `isBareLabel` rejects any name that is a single token with no hyphen, underscore or digit, the shape of a common word rather than an organization-specific resource name. `earth` and `marine` are skipped; compound names that plausibly belong to a target are still probed. Commit `9b99efa`.
- `checkGCS` and `checkCloudRunFunctions` carried the same `extractNames`-derived flaw, `checkGCS` worse for expanding each label with `-dev`, `-prod`, `-data` and `-backup` suffixes. A 12-of-12 sample of the survey's `gcs_public` buckets were all misattributions: `gs://marine` is a car-manuals site, `gs://uconn` a dog-logo page, `gs://hpc1` an image host. Both now apply the same `isBareLabel` skip. Commit `f6234fc`.
- Verified: the Oxford host `163.1.22.119` dropped its CRITICAL `firebase_public` to 0; a host whose GCS candidates derived from the bare label `static` dropped to 0, while `screening-app`, a specific name, still fires.

The lesson also ships as `winnow` signatures, `firebase-name-from-hostname-label` and `gcs-name-from-hostname-label`, which refute any Firebase or GCS finding whose name is a bare generic word. winnow flagged 1,447 such GCS candidates on the survey.

## Methodology impact

- The methodology pipeline has an Attribute stage. #53 is its first codified failure mode. #51 and #52 measure the discovery and verification stages, where the failure is a thing that is not there. #53 measures attribution, where the failure is a real thing bound to the wrong owner.
- A finding has two parts, the host and the exposure. Verification confirms the exposure. Attribution confirms the host. A scanner can pass the first and fail the second, and the result is still a false finding.
- Ownership in a global namespace is proven by a reference the target emits, never by a word the target's hostname contains.

## Cross-references

- **Insight #51, #52** the discovery and verification variants. #53 completes the set across the first three pipeline stages.
- **Insight #16** no status code is identity. Same family: a cheap signal, here a hostname label, is not identification.
- **METHODOLOGY.md** discover, fingerprint, verify, attribute. #53 is the attribute-stage failure measured.

## Source data

- Survey: global university LLM-exposure map, per-host arsenal run, slug `univ-llm-2026-05-hosts`
- Findings: 4 `firebase_public` CRITICAL across `163_1_22_119_{80,443}` and `131_247_{136_183,139_171}_8000` in `results/univ-llm-2026-05-hosts/*/menlohunt.json`
- Marker reads: `earth.firebaseio.com/.json?shallow=true` returned `{"music":true}`; `marine.firebaseio.com/.json?shallow=true` returned 7 unrelated top-level keys
- GCS verification: 12-of-12 sampled `gcs_public` buckets misattributed (`marine`, `uconn`, `euclid`, `registrar`, `mercury`, `auth-dev`, `media-prod`, `dashboard-prod`, `guppy-data`, `mamut-dev`, `hpc1`, `web12`)
- menlohunt fix: `isBareLabel` applied in `checkFirebase`, `checkGCS`, `checkCloudRunFunctions`, github.com/Nicholas-Kloster/menlohunt
- Screening signatures: `firebase-name-from-hostname-label`, `gcs-name-from-hostname-label` in `winnow`, github.com/Nicholas-Kloster/winnow

---

*Codified by Nuclide Research (Nicholas Kloster + Claude) 2026-05-21 from the global university LLM-exposure map per-host arsenal triage. Methodology per `~/.claude/nuclide-internal/METHODOLOGY.md`.*
