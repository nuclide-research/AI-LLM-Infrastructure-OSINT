# Session Analysis: Data Labeling & Annotation Survey

_2026-05-31. Label Studio / CVAT / Argilla / doccano / Prodigy. Findings #36217-36254, Insights #72 + #73._

## 1. Overview

### Objective
Survey the Data Labeling & Annotation category (a roadmap gap with a query file + probe
but no Stage-1 intel doc). Test whether auth-on-default survives each platform's own
default-open knob, against the managed-cloud tier the 2026-05-04 cheap-VPS pass missed.

### Scope and Constraints
Roadmap category. Identification + auth-state only. Restraint: enumerate auth-state,
project counts, and project names (names are the finding); never read labeled records,
never register an account, never use default credentials against a live host.

## 2. Environment and Tooling

### Claude Code Operation
Orchestrator-direct (Opus) + 4 parallel general-purpose(sonnet) Stage-1 OSINT agents.
aimap source edited/rebuilt locally; verification probe enhanced.

### Tools Used
Stage-1 agents, aimap v1.9.42-44, Playwright (authenticated Shodan), datalabel-probe.py
v0.2, aimap-profile, VisorLog, BARE, VisorScuba. Breadth tools recorded with reason.

### Notable Configuration
rooster, no VPN. Shodan via Playwright web UI (API key invalid). Censys not used this run.

## 3. Methodology

### Enumeration approach
Stage-1 OSINT first (no intel doc existed) -> intel doc + 2 CVE corrections. Then Shodan
title-dorks (managed-cloud tier) -> 80 candidates.

### Candidate identification
aimap (5 fingerprints, fixed this session). The CVAT 0/30 result triggered a probe-design
review (Insight #73): CVAT needs Accept: application/vnd.cvat+json.

### Validation checks
datalabel-probe.py v0.2 per platform: Label Studio /user/signup (open-signup); CVAT
/api/projects with the vendor header (auth-state); doccano /v1/projects. Insight #16 throughout.

### Safeguards
Open-signup = inner-A (reachable, registration not exercised). Default creds (Argilla key,
doccano admin/password) = intel only. Open-dir .env/.ssh = listing exercised, contents not pulled.

## 4. Execution Trace

1. Picked Data Labeling from the roadmap (eval/benchmarking already surveyed 2026-05-28).
2. 4 parallel Stage-1 agents -> intel doc; corrected CVE-2023-38686 (Sydent) + CVE-2022-25011 (unverified).
3. Reviewed + fixed 5 aimap data-labeling fingerprints (v1.9.43, v1.9.44); enhanced datalabel-probe.py (v0.2).
4. Shodan harvest (Playwright): 80 candidates; Argilla/Prodigy 0 (Shodan-dark).
5. aimap scan: 68 services + the open-directory critical (<IP-withheld-pending-remediation>).
6. Verification: LS 16/17 open-signup; CVAT 0/30 -> diagnosed vendor-header gap -> 20/20 auth-on; doccano auth-on.
7. VisorLog #36217-36254. BARE (all NO-MATCH). VisorScuba (38/38 vacuous).
8. Wrote intel doc, breakdown, Insights #72/#73, case study, this analysis, query-catalog update.

## 5. Findings

### 5.1 Label Studio open self-registration — 16 of 17 hosts (MEDIUM)
`/user/signup` reachable (DISABLE_SIGNUP_WITHOUT_LINK=False default) -> register -> full
project/task data API. Effective-unauth. inner-A/outer-1 (signup reachable, not exercised).
3.219.249.249 also CORS:*. 192.46.220.113 signup-closed (held).

### 5.2 Open directory .env + .ssh — <IP-withheld-pending-remediation>:8000 (HIGH)
Unauth open directory listing .env (creds), .ssh/ (keys), backup, Dockerfile. Swiss
small-business VPS. inner-B/outer-1 for the listing; contents not pulled.

### 5.3 CVAT exposed, auth-on, outdated — 20 hosts (LOW)
20/20 confirmed auth-on (/api/projects 401/403). Versions 2.5-2.64.1; outdated ones carry
applicable-CVE class (BOLA, Nuclio RCE) by version, not exercised. The Insight #72 discriminator.

### 5.4 doccano exposed, auth-on — 1 host (LOW)
/v1/projects gated; ALLOW_SIGNUP=False holds. Consistent with 2026-05-04 (348/348 auth-on).

## 6. Risk Assessment

### Overall Posture
Auth-on-default holds; the risk is the default-open registration knob (Label Studio) and a
default-credential knob (Argilla, unmeasured this corpus). Confirms #72.

### Confidentiality
High for Label Studio: raw labeled training data (PII, documents, imagery, RLHF pairs) one
account-creation away on 94% of confirmed hosts. Critical for <IP-withheld-pending-remediation> (.env/.ssh).

### Integrity / Availability
Not exercised. Open-signup grants read+write to a registered user; not tested (restraint).

### Systemic Patterns
Registration-default predicts effective-unauth (LS open vs CVAT/doccano closed) on the same
hosts/clouds. Header-versioned APIs evade header-less fingerprinters (CVAT, #73).

## 7. Recommendations

### R1 — Label Studio
DISABLE_SIGNUP_WITHOUT_LINK=True on internet-reachable instances; SSRF_PROTECTION_ENABLED=True; patch >=1.18 / >1.22.

### R2 — CVAT / <IP-withheld-pending-remediation>
CVAT: keep registration off, upgrade off EOL 2.x (>=2.55), do not co-expose the compose Grafana. <IP-withheld-pending-remediation>: remove the open dir, rotate the .env creds + SSH keys (assume compromised).

### Future automation
Add request-header support to aimap's Probe (the CVAT vendor-Accept gap, #73). Add a VisorScuba
control for annotation platforms / open directories (38/38 vacuous here). Build the Argilla
HF-Spaces enumeration lane (Shodan-dark).

## 8. Limitations and Assumptions

- Argilla (HF-Spaces) and Prodigy (commercial) are Shodan-dark; 0 measured. Argilla's default-key
  population needs HF-Hub enumeration. Both carry default-open knobs this corpus could not measure.
- Open-signup is inner-A (not exercised). Default creds documented as intel, not used.
- doccano managed-cloud count is fuzzy (loose-health-endpoint FP overlap with Label Studio,
  fixed in v1.9.44); the auth-state conclusion (auth-on) is robust.
- aimap cannot fingerprint CVAT live (header gap); the verification probe covers it.

## 9. Proof of Concept (PoC) Illustrations

Label Studio open-signup discriminator (reachable, not exercised):
```
$ curl -s http://<host>:8080/api/version        # 200 {"label-studio-os-package":...,"edition":...}  (identity)
$ curl -s http://<host>:8080/api/projects        # 302 -> /user/login   (data endpoint auth-on)
$ curl -s http://<host>:8080/user/signup         # 200 + "Create account" form  = OPEN SIGNUP (the finding)
# Registration is NOT performed: signup-reachable is the finding, account-creation is the line not crossed.
```

CVAT vendor-header discriminator (Insight #73):
```
$ curl -s -H 'Accept: application/json'            http://<host>:8080/api/server/about   # 404/406 (header-less = invisible)
$ curl -s -H 'Accept: application/vnd.cvat+json'   http://<host>:8080/api/server/about   # 200 {"name":"Computer Vision Annotation Tool","version":...}
$ curl -s -H 'Accept: application/vnd.cvat+json'   http://<host>:8080/api/projects        # 401/403  (auth-on holds, 20/20)
```

Open directory (listing exercised, contents not pulled):
```
$ curl -s http://<IP-withheld-pending-remediation>:8000/   # directory listing: .env  .ssh/  backup/  Dockerfile  requirements.txt
# .env and .ssh/ are NOT downloaded — the listing of those names is the finding (restraint).
```
