# Data Labeling & Annotation: the registration knob that re-opens the door

_Data Labeling & Annotation survey. 2026-05-31. Label Studio / CVAT / Argilla / doccano / Prodigy._
_Findings: nuclide.db #36217-36254. Insights #72, #73. Breakdown: data/findings-breakdown-data-labeling-2026-05-31.txt._

## Why this category

Data-labeling platforms sit at the input boundary of every supervised-learning and
RLHF pipeline. They hold the raw data being labeled: PII-dense text, scanned
documents, medical and facial imagery, and the human-preference pairs that fine-tune
LLMs. A 2026-05-04 cheap-VPS pass had already shown the category is auth-on by
default (doccano 348/348, 98.9% auth-on). So this survey was not a literal-no-auth
hunt. It asked a sharper question: when a platform ships auth-on, does its own
**default-open knob** (open self-registration, a documented default API key, no-auth
commercial mode) re-create effective-unauth at population scale? And it targeted the
managed-cloud tier the cheap-VPS pass had missed.

<!-- ksat-tag:auto-generated:start -->
## DCWF KSAT coverage

Auto-derived from DCWF AI work-role rule files (`ksat-tag`).

- **672 (AI Test & Evaluation Specialist):** K7003, K7004, K7044, S7068, S7070, S7075, T5858, T5904, T5919
- **733 (AI Risk & Ethics Specialist):** K7040, S7056, T5854, T5893
- **overlap (Common AI KSATs (all 5 roles)):** K1158, K1159, K22, K6311, K6900, K6935, K7003, K942, T5896

<!-- ksat-tag:auto-generated:end -->

## Discovery and the tool fixes it forced

Shodan title-dorks against the managed-cloud tier (no cheap-VPS org filter) harvested
80 candidates: Label Studio 21, CVAT 30, doccano 29. Argilla (`port:6900`) and Prodigy
(`http.html:"prodigy.js"`) returned 0, consistent with the Stage -1 intel: Argilla is
Hugging-Face-Spaces-dominant and not Shodan-indexable, Prodigy is commercial and rarely
exposed. Those two are honest negative space (Argilla needs HF-Hub enumeration).

aimap already shipped fingerprints for all five, built before this survey's intel. The
productize-and-re-run discipline caught three problems, each fixed and unit-tested:

- **CVAT was invisible (0 of 30).** CVAT uses DRF `AcceptHeaderVersioning`: its identity
  endpoint `/api/server/about` returns the product JSON only with
  `Accept: application/vnd.cvat+json`. A generic `application/json` probe (and aimap,
  which sends no vendor media type) gets 404/406. A high-precision title dork returning
  0 confirmations was the alarm; re-probing the same 30 with the vendor header confirmed
  **20**. This is Insight #73, and a real aimap gap: its header-less `Probe` cannot
  express the requirement, so the verification probe carries CVAT for now.
- **doccano false-positived on Label Studio.** A v1.9.43 fix had added `/v1/health`
  (`{"status":...}`) as a doccano identity probe; it matched Label Studio hosts whose
  reverse proxy also serves a `/v1/health` with a `status` field. The verification probe
  (stricter) reclassified them correctly; aimap reverted to the root-page `doccano`
  marker (v1.9.44, regression-tested).
- **Prodigy and CVAT carried FP-prone anchors** (a bare `<title>Prodigy</title>` that
  collides with the band/music, and a bare `cvat` keyword that fired on GCP-IAP catch-all
  200s). Both re-anchored on structured JSON (Insight #6).

The auth-state verification ran through `datalabel-probe.py` (v0.2: HTTPS support,
Label-Studio open-signup detection, project-name capture, `--from-aimap` chaining),
the category's productized verification tool. Two catalog CVE errors were corrected
against NVD: CVE-2023-38686 is Sydent, not Argilla; CVE-2022-25011 is unverified for
Label Studio.

## Verification (the load-bearing stage)

**Label Studio: 16 of 17 confirmed hosts have open self-registration.** Every confirmed
LS host was checked for the `DISABLE_SIGNUP_WITHOUT_LINK=False` default: `/user/signup`
returns 200 with the account-creation form on 16 of 17. Anyone reaches the URL, registers,
gets an API token, and reads `/api/projects` and `/api/tasks`, the raw labeled data and
annotator emails. This is effective-unauth, graded **medium / inner-A**: the signup form
is reachable (observed), but registering and reading would exercise it, and the NuClide
ethic stops at "signup reachable, registration not exercised." One host (192.46.220.113)
had signup closed. One (3.219.249.249) additionally returned `Access-Control-Allow-Origin: *`.

**CVAT: 20 of 20 confirmed hosts auth-on.** With the vendor header, 20 CVAT confirmed
(versions 2.5 through 2.64.1). Every one returned 401/403 on `/api/projects`: the
registration-off, OPA-backed authz model held under the same exposure that opened Label
Studio. Many run outdated versions carrying an applicable-CVE class (CVE-2024-47172 BOLA
< 2.19.1, CVE-2025-23045 Nuclio RCE < 2.26.0), version-confirmed but not exercised
(auth-on). Graded low.

**doccano: confirmed auth-on**, `/v1/projects` gated, consistent with the 2026-05-04 pass.

## The discriminator

Same category, same managed-cloud population, same restraint. Label Studio's
registration knob defaults open and 94% of its hosts are effective-unauth; CVAT's and
doccano's registration defaults closed and they hold. The variable that predicted the
outcome was a single boolean, the **default value of the registration knob**, not
operator skill, cloud, or the correctness of the auth layer (which was correct on all
three). That is Insight #72: a platform can ship real authentication and a real authz
layer and still be effectively unauthenticated because its self-registration default
re-opens the door. Account acquisition is one rung up the funnel from credential bypass,
and the default decides whether that rung is open.

## Bonus critical: the beekeeper's open directory

`<IP-withheld-pending-remediation>:8000`, a Label Studio title-hit, turned out to be an unauthenticated
**open directory listing** exposing `.env` (credentials), `.ssh/` (keys), a backup
directory, a Dockerfile, and requirements.txt, the full tree browsable and downloadable.
aimap's Open Directory enumerator caught it. The host is a rootserver.io VPS in
Switzerland; its `:443` serves the site of a small Swiss beekeeping business (name withheld). The filenames are the finding (the listing was exercised); the `.env` and
`.ssh/` contents were not pulled, which caps it at high rather than confirmed-critical.
A small business one `curl` away from leaking its own credentials and SSH keys.

## Impact

For Label Studio, the exposed data is whatever the operator is labeling: in NLP and
document-AI deployments that is raw PII-bearing text and scanned contracts; in
computer-vision and medical deployments, imagery; in RLHF deployments, the human-preference
pairs that are the operator's proprietary fine-tuning signal. Open registration turns all
of it into a one-account-away read. BARE places all four finding classes below its match
threshold (top 0.38 to 0.53), confirming they are first-party configuration and authz
findings, not commodity-CVE chains.

## Remediation

- **Label Studio**: set `DISABLE_SIGNUP_WITHOUT_LINK=True` (invite-link signup only) on
  any internet-reachable instance; set `SSRF_PROTECTION_ENABLED=True`; do not run with
  `DEBUG=True`. Patch to >=1.18 for the SSRF/XSS chain and >1.22 for CVE-2026-22033.
- **CVAT**: keep registration disabled (default); upgrade off end-of-life 2.x versions
  (>=2.55 clears the privilege-escalation and stored-XSS chain). Do not co-expose the
  docker-compose Grafana (it ships anonymous-admin).
- **<IP-withheld-pending-remediation>**: remove the open directory on :8000; rotate the credentials in `.env`
  and the SSH keys, which must be assumed compromised.
- **Category-wide**: treat self-registration default and default credentials as auth-state,
  not configuration trivia. An auth-on data endpoint behind an open signup is unauth.

## Toolchain provenance

Run by hand, in order, results recorded (null is a result).

- **Stage -1 OSINT**: 4 parallel general-purpose(sonnet) agents -> `data/platform-intel/data-labeling-osint-2026-05-31.md`. Corrected 2 CVE errors.
- **JAXEN / Shodan** (Playwright web UI, authenticated session): title dorks, 80 candidates. Argilla/Prodigy 0 (Shodan-dark).
- **aimap v1.9.42 -> v1.9.44**: fixed 5 fingerprints (CVAT anti-IAP + header-gap noted, Prodigy anti-collision, Argilla v2, doccano FP-revert), unit-tested. Scan: 68 services, found the open-directory critical via the Open Directory enumerator.
- **datalabel-probe.py v0.2**: the auth-state verification tool (HTTPS, LS open-signup, project names, --from-aimap + vendor Accept header for CVAT). LS 16/17 open-signup, CVAT 20/20 auth-on, doccano auth-on.
- **aimap-profile**: <IP-withheld-pending-remediation> -> rootserver.io VPS (CH), :443 beekeeper site, no honeypot signals.
- **VisorLog**: #36217-36254 (1 high, 16 medium, 21 low).
- **BARE**: all 4 classes NO-MATCH (first-party, no MSF coverage).
- **VisorScuba**: 38/38 vacuous pass (no AI-baseline control for annotation platforms / open dirs; tool gap, same class as service-mesh/KubeSphere).
- **VisorGraph / recongraph / nu-recon / VisorBishop / menlohunt / VisorSD / VisorPlus**: attribution/discovery breadth lanes; the LS/CVAT hosts are bare managed-cloud IPs (GCP/AWS/Hetzner/OVH) with thin cert-pivot value, and the population is already enumerated. cert-pivot attribution rests on the namespace/host data already captured; not re-run per-host in this pass.
- **VisorCorpus / VisorRAG / VisorAgent**: LLM-target tools; the survey targets are annotation control planes (the data tier), not LLM inference endpoints, so no in-scope LLM target. VisorAgent ethical-stop (controlled only). Recorded with reason, not silently skipped.
- **cortex**: validates auth-context docs (SKELETON/VIOLATIONS/CONTEXT), a different artifact than this survey produced. N/A with reason.
- **VisorGoose**: gov/edu-CT discovery; this corpus is commercial cloud. N/A with reason.
- **VisorHollow**: not applicable, Windows-only.

Argilla (HF-Spaces) and Prodigy are the documented open lanes: Argilla needs HF-Hub
enumeration (Shodan-dark), and both carry default-open knobs (Argilla `owner.apikey`,
Prodigy no-auth) that this Shodan-tier corpus could not measure.
