# F2 Lane B -- MLflow Deep Enumeration -- 168.138.146.91
Date: 2026-06-28

## B1 Experiment Count
Total experiments: 14 (IDs 0-1, 11-20, 23-24; gap in IDs 2-10 suggests deleted experiments)
Pwn experiments: 9 (IDs 11-17, 23, 24)
Normal ML experiments: 5 (IDs 0, 1, 18, 19, 20)

## B2 Pwn Experiment IDs
- [11] cve_test_1778457629        -- artifact_location: file:///
- [12] test_scan_1778457775       -- artifact_location: /mlflow/artifacts/12 (safe path, precursor test)
- [13] scan_1778457788            -- artifact_location: file:///
- [14] scan_1778457790            -- artifact_location: file:///tmp
- [15] scan_1778457792            -- artifact_location: file:///home
- [16] scan_1778457795            -- artifact_location: file:///opt
- [17] scan_1778457797            -- artifact_location: file:///app
- [23] pwn_tmp_test_3f86ad        -- artifact_location: file:///tmp
- [24] pwn_cron_root_d74b03       -- artifact_location: file:///etc/cron.d  <-- CRITICAL

## B3 Pwn Run Tags
mlflow.user on pwn runs: ABSENT (user_id field = empty string "")
mlflow.source.name on pwn runs: ABSENT
mlflow.source.git.commit: ABSENT
Other notable tags: only mlflow.runName auto-generated (adjective-animal-number pattern)
Note: start_time = 0 on both pwn runs with actual run objects -- raw API calls, not SDK

## B4 Legitimate Run Tags
mlflow.user on legitimate runs: ABSENT (user_id="" on exp 0 runs; user_id="x" on exp 18-20)
mlflow.source.name on legitimate runs: ABSENT
Same user as pwn runs? Both-absent; exp 18-20 have user_id="x" (single-char placeholder, not a real OS username)
Note: exp 0 (Default) runs have real start_times (~2026-05-13); exp 18-20 runs have start_time=0

## B5 /tmp Artifact Listing
Run ID used: e4a7ed29393e4a6db170aed3140405d6
Files found at /tmp: NULL -- API returned only root_uri (file:///tmp/e4a7ed29393e4a6db170aed3140405d6/artifacts)
Implication: artifact_location=file:///tmp means the server would write artifacts INTO /tmp using the run_id as directory -- no files logged yet in this run

## B6 Registered Models
Total: 100+ (next_page_token present, at least one more page)
Sample source_uri (CRITICAL FINDINGS):
  - ml-JSMzyYvR: "http://d74lnhgnaeps72h9noug7k6ujxcdta5oy.a.dnsg.cc/poc.tar.gz"
    DNS canary subdomain + poc.tar.gz payload delivery -- external attacker callback URL
  - poc_1962: "http://1.2.3.4:4444/api/2.0/mlflow-artifacts/artifacts/"
    1.2.3.4:4444 = classic PoC C2 placeholder / netcat listener address
  - protectai-*: 7 entries with ProtectAI scanner UUIDs -- at least two separate security scanner runs hit this host
Model name pattern: random 26-char base58 strings -- programmatic API creation, no human-authored names
Model tags: none on any model

## B7 ML Legitimacy
Experiments checked: exp 0 (Default, run 9ad76af0), exp 18 (p_3030377b, run a16f9218), exp 19 (p_9a9714c4, run e332e174)
Has logged metrics? NO -- data.metrics absent on all runs
Has logged params? NO -- data.params absent on all runs
Has SDK tags? NO -- only mlflow.runName present; no mlflow.user, mlflow.source.name, mlflow.project.name
Verdict: SHELL MODELS -- all runs are API-created stubs; zero ML work logged on this server

## B8 Timeline
Chronological (*** = pwn/attacker):

  2025-05-05 00:08:36  [0]  Default                    (server initialized)
  2025-05-05 01:42:33  [1]  SSL with PyGlove            (only named-ML experiment; zero runs)
  2026-05-11 00:00:29  [11] cve_test_1778457629         *** WAVE 1 START
  2026-05-11 00:02:56  [12] test_scan_1778457775        ***
  2026-05-11 00:03:09  [13] scan_1778457788             *** artifact=file:///
  2026-05-11 00:03:11  [14] scan_1778457790             *** artifact=file:///tmp
  2026-05-11 00:03:13  [15] scan_1778457792             *** artifact=file:///home
  2026-05-11 00:03:15  [16] scan_1778457795             *** artifact=file:///opt
  2026-05-11 00:03:17  [17] scan_1778457797             *** artifact=file:///app  WAVE 1 END
  2026-05-25 06:53:43  [18] p_3030377b                  (programmatic; user_id="x")
  2026-05-25 08:04:56  [19] p_9a9714c4                  (programmatic; user_id="x")
  2026-05-25 09:20:46  [20] p_368da897                  (programmatic; user_id="x")
  2026-06-11 16:29:53  [23] pwn_tmp_test_3f86ad         *** WAVE 2 -- artifact=file:///tmp
  2026-06-11 16:30:08  [24] pwn_cron_root_d74b03        *** WAVE 2 END -- artifact=file:///etc/cron.d

Earliest experiment: 2025-05-05 00:08:36 UTC (Default)
Latest experiment:   2026-06-11 16:30:08 UTC (pwn_cron_root_d74b03)
First pwn experiment: 2026-05-11 00:00:29 UTC
Last pwn experiment:  2026-06-11 16:30:08 UTC
Pwn cluster 1 duration: 2 minutes 48 seconds (7 experiments, fully automated)
Pwn cluster 2 duration: 15 seconds (2 experiments)
Gap: legitimate base install (2025-05-05) to first attack (2026-05-11) = ~370 days
Gap cluster 1 to cluster 2: 31 days

## Key Discriminating Findings

- EXTERNAL ATTACKER, not owner testing. The mlflow.user tag is ABSENT on all pwn runs (user_id="").
  Owner testing via the MLflow SDK always sets mlflow.user from the OS username automatically.
  Raw HTTP API callers skip this. The empty user_id field is the raw-API signature.

- start_time=0 on pwn runs. SDK-initiated runs always record start_time at run creation.
  Zero timestamps = bare POST /api/2.0/mlflow/runs/create with no SDK context.

- Two distinct attack waves, 31 days apart. Wave 1 (2026-05-11): directory scan via
  artifact_location pointing at /, /tmp, /home, /opt, /app -- mapping writable paths.
  Wave 2 (2026-06-11): escalation -- pwn_tmp_test writes into /tmp; pwn_cron_root targets
  file:///etc/cron.d, which if the MLflow server writes artifacts there is a cron persistence
  primitive (drop executable file to /etc/cron.d = root cron job on most Linux distros).

- poc.tar.gz DNS canary on registered model ml-JSMzyYvR. Domain
  d74lnhgnaeps72h9noug7k6ujxcdta5oy.a.dnsg.cc is a DNS-based out-of-band callback tracker.
  Registering this as a model source tests whether the server fetches remote URIs (SSRF/RCE via
  pickle deserialization in mlflow.pyfunc.load_model). This is a known CVE-class attack vector.

- poc_1962 model with source "http://1.2.3.4:4444/..." = attacker listener address registered
  to test artifact fetch callback. The 4444 port is the netcat/Metasploit default.

- ProtectAI scanner left 7 registered model entries. At least two separate scanner sessions
  ran against this host (UUIDs from 2021-era and 2025-era timestamps). The scanner entries
  confirm this server is publicly known in security research circles.

- Zero legitimate ML work. Exp 1 (SSL with PyGlove) has zero runs. Exp 0 runs have real
  timestamps but no metrics, params, or SDK tags. Exps 18-20 have user_id="x" (placeholder).
  100+ registered models are all random base58 names with no run_id-linked artifact sources.
  This server has never been used for actual machine learning.

- VERDICT: External attacker confirmed. Wave 1 = recon/directory scan. Wave 2 = persistence
  attempt (cron.d). The server is a standing target, unpatched MLflow open to the internet
  with artifact_location write primitive demonstrated. The pwn_cron_root experiment targeting
  /etc/cron.d is the most severe finding -- if the MLflow process has write access to /etc/cron.d,
  any artifact logged to run c51fda5721954759ade3a16694cf28e0 lands in /etc/cron.d as a file
  the cron daemon will execute as root.
