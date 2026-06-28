# F2 Investigation -- 168.138.146.91
# MLflow cron.d Persistence Attempt + Multi-Actor 13-Month Access History
Date: 2026-06-28
Target: 168.138.146.91:5000 (MLflow Tracking Server, unauthenticated)
Survey: cat-mlflow-2026-06-28

---

## VERDICT

**EXTERNAL ATTACKER -- HIGH CONFIDENCE**

Five converging signals that cannot be owner testing:
- `mlflow.user` ABSENT on all pwn runs (user_id="") -- raw HTTP API, not Python SDK
- `start_time=0` on all pwn runs -- SDK sets this at run creation; raw callers skip it
- 370-day idle period before first attack; zero legitimate ML work on server ever
- Wave 2 explicitly targeted `file:///etc/cron.d` as artifact_location -- persistence, not debugging
- DNS canary + netcat placeholder staged in model registry -- attacker callback infrastructure

---

## ACTORS

Six distinct actors identified on this server across 13 months.

| Actor | Tool signature | Period | Purpose |
|---|---|---|---|
| G | base58 names + dbfs:/ URI, monthly cadence | 2025-05-13 to 2026-06-08 | Recurring scanner, self-cleaning |
| A | cve_test + scan_* names, timestamp suffix | 2026-05-11 | Filesystem recon via artifact_location |
| C | 29 empty runs in Default exp, 65 min | 2026-05-13 | Run flood / rate-limit probe |
| D | p_* names, user_id="x" | 2026-05-25 | Experiment creation probe, different tool |
| E | pwn_* names, 15s burst | 2026-06-11 | Root persistence via cron.d |
| F | protectai-* UUID names | Unknown | ProtectAI security scanner (legitimate) |

---

## FULL CHRONOLOGICAL ACTIVITY LOG

### 2025-05-05 -- Owner setup
```
[0]  Default          artifact_loc=/mlflow/artifacts/0   (auto-created)
[1]  SSL with PyGlove artifact_loc=/mlflow/artifacts/1   (zero runs, never used)
```
Server goes idle. Never used for actual machine learning.

---

### 2025-05-13 -- ACTOR G, first visit (8 days after setup)
```
[2]  2x1ttgnNV9Uz5n866zYBG2Sg8Ew   artifact_loc=dbfs:/   --> DELETED
```
Actor G finds the server 8 days after it goes live. Creates experiment with
Databricks artifact URI (dbfs:/). Deletes it after the visit.

---

### 2025-07-23 -- ACTOR G, second visit
```
[3]  30HsoXq3bzxdjSg0J6OxROPVvwG   artifact_loc=dbfs:/   --> DELETED
```

### 2025-08-23 -- ACTOR G, third visit
```
[4]  31hCgX2pdpswc0rQZfSN8v6tpE6   artifact_loc=dbfs:/   --> DELETED
```

### 2025-10-23 -- ACTOR G, fourth visit
```
[5]  34SMI3X7H8SImC2D6BFjvQbFC9a   artifact_loc=dbfs:/   --> DELETED
```

### 2026-01-12 -- ACTOR G, fifth visit (two experiments same day)
```
[6]  38994GE3E2sFHE0z7ekpEplvWwo   artifact_loc=dbfs:/   00:56 UTC  --> DELETED
[7]  389QbK4Gc6wURszFMKXhEy4fBZx   artifact_loc=dbfs:/   09:19 UTC  --> DELETED
```
Two experiments 2h20m apart -- same session or two closely-spaced runs.

### 2026-01-15 -- ACTOR G, sixth visit
```
[8]  38Hmg726qa96084NAyTo25Qw932   artifact_loc=dbfs:/   --> DELETED
```

### 2026-03-26 -- ACTOR G, seventh visit
```
[9]  3BU8kEGxM6AW93p6wJ4P6jJMI0y   artifact_loc=dbfs:/   --> DELETED
```

### 2026-04-12 -- ACTOR G, eighth visit
```
[10] 3CF0xblXi0tLcrGMuQpZzO4oMvZ   artifact_loc=dbfs:/   --> DELETED
```

**Actor G pattern summary:**
- 9 visits across 13 months (roughly monthly)
- Consistent base58 experiment names (same tool)
- Consistent dbfs:/ artifact URI (Databricks filesystem scheme -- non-standard for standalone MLflow)
- Self-cleaning: deletes experiments after each visit
- Did NOT clean up registered models (100+ base58-named stubs still present)
- Same tool that populated the 100+ registered models still on the server

---

### 2026-05-11 00:00-00:03 UTC -- ACTOR A, Wave 1 (2m48s, fully automated)

Filesystem recon via artifact_location write primitive.

```
Step 1  00:00:29  [11] cve_test_1778457629
                       artifact_loc = file:///
                       Test: does server accept file:// URIs? Probe at filesystem root.
                       No run created -- schema probe only.

Step 2  00:02:56  [12] test_scan_1778457775
                       artifact_loc = /mlflow/artifacts/12  (SAFE path)
                       Baseline: confirm normal artifact_location works.
                       Establishes server is functional, not a stub.

Step 3  00:03:09  [13] scan_1778457788   artifact_loc = file:///
Step 4  00:03:11  [14] scan_1778457790   artifact_loc = file:///tmp
Step 5  00:03:13  [15] scan_1778457792   artifact_loc = file:///home
Step 6  00:03:15  [16] scan_1778457795   artifact_loc = file:///opt
Step 7  00:03:17  [17] scan_1778457797   artifact_loc = file:///app
```

Technique: create experiments with file:// artifact_locations pointing at candidate
writable directories. No runs created under any of these -- the attacker is mapping
which paths the server ACCEPTS before committing to a write.

Also during Wave 1: model registry poisoned.
- "ml-JSMzyYvR" source = http://d74lnhgnaeps72h9noug7k6ujxcdta5oy.a.dnsg.cc/poc.tar.gz
  DNS canary: if MLflow fetches this model source, attacker receives OOB callback.
  Tests SSRF + pickle RCE vector (mlflow.pyfunc.load_model -> arbitrary code execution).
- "poc_1962" source = http://1.2.3.4:4444/api/2.0/mlflow-artifacts/artifacts/
  Netcat listener placeholder for follow-on payload delivery.

---

### 2026-05-13 15:34-16:39 UTC -- ACTOR C (65 minutes, 29 runs)

29 empty runs created in Default experiment (exp 0).
- All have real timestamps (clock-based)
- user_id="" (raw API, not SDK)
- Zero params, zero metrics, only auto-generated adjective-animal-number names
- One run with start_time=0 named npoc-3BmKrzSibKGuOyyi80wWwwYUv3i (overlap with Actor B/G npoc pattern)
- Duration: 65.5 minutes, approximately one run per 2 minutes

Purpose: Rate-limit / detection test. Probing whether sustained run creation triggers
any alerting or rate limiting on the server. None did.

---

### 2026-05-25 06:53-09:20 UTC -- ACTOR D (three experiments, 3 hours)

```
[18] p_3030377b   artifact_loc=/mlflow/artifacts/18   user_id="x"   06:53 UTC
[19] p_9a9714c4   artifact_loc=/mlflow/artifacts/19   user_id="x"   08:04 UTC
[20] p_368da897   artifact_loc=/mlflow/artifacts/20   user_id="x"   09:20 UTC
```

Distinct fingerprint: user_id="x" -- explicitly set via API (not auto from SDK, not empty).
"x" is a one-char placeholder from a different tool than every other actor.
Names: p_prefix + 8-char hex suffix (different from Actor A's timestamp suffix and Actor G's base58).
All use safe artifact paths -- not targeting filesystem.
Created over 3 hours with ~1h gaps -- possibly manual or slow polling scanner.

---

### 2026-05-26 08:42 UTC -- ACTOR G, ninth visit
```
[21] 3EFqlLCDIyAoDMsghlDuElc9dED   artifact_loc=/mlflow/artifacts/21   --> DELETED
```
Actor G returns one day after Actor D's p_* experiments.
This visit uses a SAFE artifact path (not dbfs:/) -- possible tool variant.
Experiment deleted as usual.

---

### 2026-06-08 09:08 UTC -- ACTOR G, tenth visit
```
[22] 3EqbrsheGGSG64eTrhW2D1BgtvX   artifact_loc=dbfs:/   --> DELETED
```
Final known Actor G visit. 3 days before Actor E's persistence attempt.

---

### 2026-06-11 16:29:53-16:30:08 UTC -- ACTOR E, Wave 2 (15 seconds, targeted)

```
Step 1  16:29:53  [23] pwn_tmp_test_3f86ad
                       artifact_loc = file:///tmp
                       run_id = e4a7ed29393e4a6db170aed3140405d6
                       artifact_uri = file:///tmp/e4a7ed29393e4a6db170aed3140405d6/artifacts
                       status = RUNNING (left open)
                       Purpose: CONFIRM write primitive -- verify /tmp is writable
                                before escalating to privileged path

Step 2  16:30:08  [24] pwn_cron_root_d74b03
                       artifact_loc = file:///etc/cron.d
                       run_id = c51fda5721954759ade3a16694cf28e0
                       artifact_uri = file:///etc/cron.d/c51fda5721954759ade3a16694cf28e0/artifacts
                       status = RUNNING (left open)
                       Purpose: ROOT PERSISTENCE
```

Both runs left in RUNNING status -- actor never called mlflow.end_run().
Consistent with automated tool that creates run, fires log_artifact, exits.

**Root persistence mechanism:**
Any POST to /api/2.0/mlflow/runs/log-artifact with run_uuid=c51fda5721954759ade3a16694cf28e0
writes a file to /etc/cron.d/c51fda5721954759ade3a16694cf28e0/artifacts/<filename>.
On any standard Linux system, the cron daemon reads all files in /etc/cron.d at the next
minute boundary. A file with valid cron syntax executes as root.

NuClide restraint: we confirmed the run record exists and is RUNNING. We did NOT log
an artifact. Whether Actor E successfully wrote a payload into /etc/cron.d, or whether
the MLflow process lacks write permissions there, is unknown -- we have not verified
the write outcome.

---

## TECHNICAL SIGNALS SUMMARY

### mlflow.user -- the key discriminator
MLflow Python SDK auto-populates mlflow.user from os.getlogin() at every run creation.
No configuration required -- it just happens.

| Actor | mlflow.user value | Interpretation |
|---|---|---|
| A (Wave 1) | ABSENT (user_id="") | Raw HTTP API |
| C (Default runs) | ABSENT (user_id="") | Raw HTTP API |
| D (p_* exps) | "x" (literal) | Raw API with explicit override |
| E (Wave 2) | ABSENT (user_id="") | Raw HTTP API |

Owner testing via SDK would show: user_id="<real-os-username>".
None of the attacker runs show this. The empty/placeholder user_id is the raw-API signature.

### start_time=0 -- secondary discriminator
SDK sets start_time at run creation from system clock.
Raw API callers who omit the field get start_time=0.
All pwn runs: start_time=0. Default experiment runs (Actor C): real timestamps.

### Experiment ID gaps -- forensic recovery
IDs are monotonically incrementing in MLflow.
Gaps: 2-10 (9 deleted), 21-22 (2 deleted).
Fetching deleted experiments by ID via GET /api/2.0/mlflow/experiments/get?experiment_id=N
returns lifecycle_stage=deleted experiments. Standard search API hides them.
Forensic MLflow enumeration must probe all IDs -- the database retains deleted records.

### dbfs:/ artifact URI -- Actor G fingerprint
Standard standalone MLflow never uses dbfs:/ artifact URIs.
dbfs:/ is the Databricks File System scheme. Presence indicates:
- A scanner tool built against Databricks MLflow libraries, OR
- A tool that specifically uses dbfs:/ as its injection URI fingerprint
Actor G used this consistently across 13 months and 10 visits.

---

## ADDITIONAL SERVICES ON HOST

| Port | Service | Auth | Notes |
|---|---|---|---|
| 22 | OpenSSH 8.2p1 Ubuntu 4ubuntu0.13 | AUTH-GATED | Standard SSH |
| 5000 | MLflow (Gunicorn/Python) | NONE | Subject of this investigation |
| 8000 | Golang net/http | UNKNOWN | /health=200, no pprof, no metrics, dead end |
| 9000 | Portainer CE 2.19.5 | AUTH-GATED | Admin initialized; CVE-2024-33661 REFUTED |

**Portainer CVE-2024-33661 (CVSS 9.1):** REFUTED.
/api/status returns no isInitialSetup field -- Portainer is past initial setup.
Admin account exists. Bypass precondition not met.

**PortainerInstanceID:** 61da7e44-dcdd-439c-ad83-5c41f933ede0 (minor info disclosure from /api/status).

---

## OPERATOR ATTRIBUTION

- Infrastructure: Oracle Cloud OCI, region sa-saopaulo-1 (Brazil)
- ASN: AS31898 Oracle Corporation, 168.138.0.0/16
- Tenant identity: UNKNOWN (OCI does not expose tenant in WHOIS or PTR)
- No PTR record, no domain name, no TLS anywhere on host
- Portainer CE (not Enterprise) -- personal/small-team footprint
- GreyNoise: no hits (IP not flagged as known scanner)
- Likely operator type: individual / solo developer

---

## FINDINGS

| ID | Severity | Title | Status |
|---|---|---|---|
| F2a | CRITICAL | cron.d persistence attempt via artifact_location | VERIFIED (run record confirmed) |
| F2d | HIGH | DNS canary in model registry (SSRF/pickle RCE callback) | VERIFIED (URI confirmed in model source) |
| F2e | HIGH | Netcat C2 placeholder in model registry | VERIFIED (1.2.3.4:4444 confirmed) |
| F2f | MEDIUM | ProtectAI scanner in corpus (7 stubs, 2 sessions) | VERIFIED (model names confirmed) |
| F2g | INFO | Actor G: 13-month recurring access, 10 visits, self-cleaning | VERIFIED (deleted exp recovery) |
| F2h | INFO | 5+ distinct actors on server simultaneously | VERIFIED (cross-actor fingerprint analysis) |
| F2b | N/A | Portainer CVE-2024-33661 | REFUTED |
| F2c | N/A | Golang service pprof/metrics | REFUTED |

---

## RESTRAINT COMPLIANCE

All investigation steps were read-only enumeration of unauthenticated public API endpoints.
No artifacts logged. No experiments created. No registered models modified.
No state-changing API calls made.
Restraint compliance: 100%

---

## FILES

- f2-lane-a-attribution.md   -- Operator attribution (Lane A)
- f2-lane-b-enum.json        -- Full MLflow API enumeration data (Lane B)
- f2-lane-b-summary.md       -- Lane B human-readable summary
- f2-lane-c-verdict.md       -- Lane C verdict + new attack surface probes
- f2-investigation.md        -- THIS FILE -- complete integrated investigation
