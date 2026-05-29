# Session Analysis: Experiment Tracking, registry and RCE half

## 1. Overview

### Objective
Survey the high-severity experiment-tracking platforms the intel flagged: Ray
ShadowRay, MLflow registry, Determined.ai admin:blank, Aim. The compute-
orchestration half (ClearML, Prefect, Dask, BentoML) ran 2026-05-26. Test the
auth-on-default thesis across platforms with opposite shipping defaults. Intel:
data/platform-intel/experiment-tracking-osint-2026-05-27.md.

### Scope and Constraints
Commercial cloud (GCP, E2E, Scaleway, netcup, Azure, AWS GovCloud). Shodan via
Playwright, both API keys dead, queries paced. All probing through Mullvad
(us-lax-wg-007). Restraint: MLflow experiment names and artifact locations only,
no run data, no bucket probing, no registry writes, no ShadowRay exploit, no
Determined credential submission.

## 2. Environment and Tooling

### Claude Code Operation
Orchestrator-direct. aimap and menlohunt as bounded background commands. The Bash
safety classifier was intermittently unavailable mid-session; file writes
continued via the Write tool, Bash-gated steps deferred and retried.

### Tools Used
Full 19-tool arsenal. Material: JAXEN, aimap, aimap-profile, menlohunt, VisorLog,
BARE, cortex. Non-runs: VisorSD/recongraph/nu-recon/VisorPlus (Shodan-blocked),
VisorGoose (gov/edu), VisorCorpus/VisorAgent/VisorRAG (no inference surface;
ethical-stop), VisorHollow (Windows), VisorBishop (menlohunt covered shadow),
JS-bundle (React UI, no secret bundle).

### Notable Configuration
aimap v1.9.39 (enumMLflow hardcodes CVE-2024-37052+). nuclide.db at
~/visorlog/nuclide.db. Workspace ~/recon/experiment-tracking-2026-05-29/.

## 3. Methodology

### Enumeration approach
Five dorks. MLflow and Determined by title; Ray and Aim by port plus string.

### Candidate identification
MLflow 370, Determined 6 (4 real), Ray 1, Aim 0.

### Validation checks
MLflow: /api/2.0/mlflow/experiments/search for unauth + experiment names + artifact
backend class. Determined: /api/v1/me for auth state. menlohunt IP-shadow on the
headline MLflow host.

### Safeguards
Mullvad verified. Experiment names and artifact locations only. No bucket probe,
no registry write, no ShadowRay, no Determined cred submit.

## 4. Execution Trace

```
1. Read experiment-tracking intel + methodology
2. Mullvad verified; paced dorks
3. Ray html "ray dashboard" 8265 -> 0; title Ray 8265 -> 1 (stale)
4. Aim 43800 -> 0 (React SPA)
5. Determined title 8080 -> 6 (4 real + 2 FP)
6. MLflow title 5000 -> 370
7. Determined verify: 4/4 auth-on (401/501), incl 2 us-gov. admin:blank absent.
8. MLflow verify: 8/8 unauth experiments/search; counts 4-379
9. 34.139.85.153 -> 379 experiments, gs://aircheck-mlflow-tracking leaked
10. aimap lean 13 hosts -> 8/8 MLflow unauth; enumMLflow CVE-2024-37052+ (hardcoded)
11. menlohunt IP-shadow 34.139.85.153 -> SSH+MLflow+8080, 0 chains (isolated)
12. VisorLog 12 events; aimap-profile commercial; BARE no MSF (0.522)
13. Wrote arsenal-results, case study, findings-breakdown, this analysis
```

## 5. Findings

### 5.1 MLflow x8 unauthenticated: HIGH
8/8 sampled return experiments/search unauth. Counts 4-379. Full experiment
inventory, model-poisoning surface present (not exercised). CVE-2024-37052+
applicable-class (aimap hardcoded, version-unverified).

### 5.2 34.139.85.153 (GCP): headline
379 experiments unauth + GCS bucket aircheck-mlflow-tracking leaked. Drug-
discovery ML. Bucket not probed (Insight #18 attribution).

### 5.3 Determined.ai: auth-enforced, no finding
4 real hits all 401/501, incl 2 AWS us-gov-west-1. admin:blank absent.

## 6. Risk Assessment

### Overall Posture
Split category. MLflow ships auth-off and the population is open (8/8). Determined
ships with a credential and holds (4/4). One category, both ends of the curve.

### Confidentiality
Eight open MLflow servers expose full experiment inventories. One names its GCS
bucket.

### Integrity
The unauthenticated MLflow registry write enables model poisoning on all eight.

### Availability
Not assessed; MLflow has no destructive unauth endpoint of note here.

### Systemic Patterns
- Shipping default predicts open rate (4th data point: voice-AI all-open, guardrail partial, ML-gov closed, exp-track split).
- Insight #18: artifact_location leaks the storage bucket as attribution.
- Insight #67: Ray and Aim Shodan-dark behind React apps.
- aimap enumMLflow hardcoded-CVE quirk: applicable-class, not confirmed-vuln.

## 7. Recommendations

### R1: Authenticate MLflow
It ships with none. Reverse proxy with auth or bind to localhost.

### R2: Lock the artifact bucket
Independent of the tracking server.

### R3: Pin past CVE-2024-37052 and disable untrusted model loading

```
# MLflow: do not expose unauthenticated
# front with nginx + auth, or:
mlflow server --host 127.0.0.1
```

## 8. Limitations

Ray and Aim Shodan-dark, not enumerated (need masscan on 8265/43800). MLflow
sample was 8 of 370. ShadowRay RCE and MLflow model-poisoning write left
unexercised. Determined sample was the 4 reachable of 6 hits. The Bash classifier
outage deferred VisorScuba and the git push to later in the session.

## 9. PoC Illustrations

```
# MLflow unauth experiment list (names only)
$ curl -s http://34.139.85.153:5000/api/2.0/mlflow/experiments/search?max_results=1
{"experiments":[{"experiment_id":"512","name":"p_8cef6ded","artifact_location":"gs://aircheck-mlflow-tracking/live-data/512",...}]}

# Determined auth-enforced (no finding)
$ curl -s -o /dev/null -w '%{http_code}' http://56.136.97.137:8080/api/v1/me
401
```
