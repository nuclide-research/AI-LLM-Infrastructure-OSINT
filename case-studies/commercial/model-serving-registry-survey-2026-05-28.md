---
type: survey
---

# Model Serving and Registry Infrastructure Survey

_NuClide Research · 2026-05-28_

---

## Summary

Shodan sweep across 11 model-serving and registry platforms. MLflow is the only platform with a live, indexable population -- 10 confirmed unauthenticated instances spanning 6 cloud providers and 6 countries. Every other platform surveyed (vLLM, TorchServe, TensorFlow Serving, Ray Serve, BentoML, Seldon Core, KServe, ONNX Runtime Server, TGI, Triton) returned zero live hosts.

The zero-hit platforms are not zero-exposure -- they are Shodan-dark. Ports 8081 (TorchServe management), 8082 (TorchServe metrics), 8501 (TF Serving), 8080 (TGI), 8002 (Triton metrics) are not crawled at indexable density. The correct path for those populations is masscan sweep against cloud ranges, not Shodan.

Among the 10 confirmed MLflow hosts: one shows an active exploitation chain in progress, readable without authentication from the public internet.

---

## Dork Execution Log

| Query | Hits | Platform | Result |
|-------|------|----------|--------|
| `port:8000 "max_model_len" "vllm"` | 10 | vLLM | All offline at probe -- stale population |
| `port:8081 "nextPageToken" "models"` | 0 | TorchServe | Port not crawled |
| `port:8081 "modelName" "modelUrl" "minWorkers"` | 0 | TorchServe | Port not crawled |
| `port:8082 "ts_"` | 0 | TorchServe | Port not crawled |
| `port:8501 "model_version_status" "AVAILABLE"` | 0 | TF Serving | Response not indexed |
| `port:8265 "ray_version"` | 0 | Ray | /api/version not indexed |
| `port:8265 http.title:"Ray Dashboard"` | 1 | Ray | Offline at probe |
| `port:5000 "registered_models" "mlflow"` | 0 | MLflow | Body field too specific |
| `port:5000 http.title:"MLflow"` | 10 | MLflow | 10 live, all unauth |
| `port:8080 "model_id" "model_dtype"` | 0 | TGI | /info fields not indexed |
| `port:8080 "tokenization_workers" "max_total_tokens"` | 0 | TGI | Not indexed |
| `port:8000 "/v2/health/ready"` | 0 | Triton | Not indexed |
| `port:8002 "nv_inference_request_success"` | 0 | Triton | Port not crawled |
| `port:3000 "Bento-Name"` | 0 | BentoML | Header not indexed |
| `port:9000 "/api/v1.0/predictions"` | 20 | Seldon | All offline; 1 MinIO FP |

---

## vLLM -- 10 Harvested, 0 Live

10 IPs from `port:8000 "max_model_len" "vllm"`. All returned HTTP 000 at probe. Population exists in Shodan's index but is transient -- vLLM deployments appear short-lived or firewalled after initial exposure.

The security-relevant finding does not require a live population: vLLM's `--api-key` flag does not protect management endpoints. `/metrics`, `/tokenize`, `/health`, `/pause`, `/resume`, and `/update_weights` bypass `--api-key` enforcement. Any instance reachable without authentication leaks the serving model's identity and allows inference against an "secured" deployment. This is a class finding, not population-dependent.

**Stale IPs (for record):** 108.58.51.82, 67.78.191.77, 162.251.247.13, 108.252.249.145, 82.130.248.249, 113.30.160.211, 74.108.66.82, 24.139.33.243, 98.189.181.108, 173.92.133.57

---

## TorchServe -- Shodan-Dark

Port 8081 (management API, the ShellTorch surface) is not in Shodan's crawl. Neither `nextPageToken` nor the `modelName/modelUrl/minWorkers` JSON field set returned any results. Port 8082 (Prometheus `ts_` metrics) is also not crawled.

TorchServe CVE-2023-43654 (SSRF on model registration URL handler) is the relevant chain: any internet-exposed management port accepts an arbitrary model URL, the server fetches and loads it, and the loading process executes Python code in the model archive. Pre-patch this is direct RCE; post-patch it is SSRF. The management port is documented as localhost-only but ships bound to `0.0.0.0` in the default configuration.

**Correct approach:** masscan port 8081 against Hetzner/Scaleway/OVH /16 ranges, httpx filter for `nextPageToken`, aimap for identity confirmation.

---

## Seldon Core -- 20 Harvested, 0 Live

`port:9000 "/api/v1.0/predictions"` returned 20 hits. All 19 genuine candidates returned HTTP 000. Seldon Core pods run inside Kubernetes clusters; they expose port 9000 to the cluster network but not to the internet in any production deployment in this population.

**FP identified:** 94.72.112.137 returns HTTP 400 from `Server: MinIO`. MinIO catches all POST requests and returns a method-not-allowed body that contains the requested path -- it looks like a 400 from Seldon until the Server header is read. Same FP class documented in Insight #22 (aimap dcm4chee-arc FP broadened to any ASP.NET/MinIO catchall).

---

## MLflow -- 10 Confirmed Unauthenticated

Dork: `port:5000 http.title:"MLflow"`

Verification method: `POST /api/2.0/mlflow/experiments/search {"max_results":10}` returns full JSON experiment arrays without credentials on all 10.

### Population Table

| IP | Cloud | Country | Server | Artifact Backend | Notable |
|----|-------|---------|--------|-----------------|---------|
| 104.154.156.34 | GCP | US | gunicorn | local `/home` | Username `wonjungy` leaked |
| 162.55.232.59 | Hetzner | DE | gunicorn | `mlflow-artifacts:/` | 200M+ experiment IDs |
| 20.13.144.13 | Azure | US | gunicorn | `/mlruns/` local | 40 experiments, sequential |
| 210.131.221.109 | Linode/Akamai | JP | gunicorn | `mlflow-artifacts:/` | 900M+ experiment IDs |
| 51.159.148.91 | Scaleway | FR | gunicorn | `file:///root/.venv/...` | Active exploitation confirmed |
| 51.158.107.81 | Scaleway | FR | uvicorn | `mlflow-artifacts:/` | 196 experiments |
| 168.119.201.8 | Hetzner | DE | gunicorn | `s3://mlflow/` | S3 backend, public bucket possible |
| 172.203.208.10 | Azure | US | uvicorn | local `/home/elkmachine/...` | Username `elkmachine` leaked, 841 experiments |
| 79.110.227.36 | Hetzner | FI | uvicorn | `mlflow-artifacts:/` | X-Frame-Options header, no API auth |
| 101.202.128.3 | CN cloud | CN | gunicorn | `s3://mlflow/` | S3 backend, 61+ experiments |

### Exposure Class

Unauthenticated `POST /api/2.0/mlflow/experiments/search` exposes: all experiment IDs, names, artifact storage locations, creation timestamps, and lifecycle state. With an experiment ID, `POST /api/2.0/mlflow/runs/search {"experiment_ids":["N"],"max_results":50}` returns all run metadata: metrics, hyperparameters, tags, artifact URIs, system metrics logged during training.

The registered-models endpoint (`GET /api/2.0/mlflow/registered-models/list`) returned 404 on all 10 -- these instances run MLflow Tracking Server without the Model Registry component, or the registry is on a separate port. The artifact download surface remains open via `/api/2.0/mlflow/artifacts/list` and `/get-artifact`.

### Username Leakage

Two instances expose operator home directory paths directly in the `artifact_location` field:

- `104.154.156.34`: `/home/wonjungy/mlflow-data/artifacts/` -- GCP, operator handle `wonjungy`
- `172.203.208.10`: `/home/elkmachine/mlflow-env/mlruns/` -- Azure, operator handle `elkmachine`

Cross-reference pivot: GitHub, HuggingFace, Docker Hub for these handles may surface model artifacts, training code, and additional infrastructure.

### S3 Backend Exposure

Two instances use `s3://mlflow/{experiment_id}` artifact locations:

- `168.119.201.8` (Hetzner DE)
- `101.202.128.3` (CN cloud)

If the S3 bucket "mlflow" has a public ACL or permissive bucket policy, every artifact in every experiment -- model weights, training data, evaluation outputs, pickle files -- is downloadable without credentials. Verification: `aws s3 ls s3://mlflow/ --no-sign-request`. Not executed; surface open at probe time.

### Active Exploitation: 51.159.148.91

This instance carries the attack record of an ongoing exploitation campaign, fully readable without authentication.

**Operator profile:** Legitimate HuggingFace AutoTrain text classification workload. Models: `autotrain-xlm-roberta-tonality`, `autotrain-modernbert-test`. Runs as `root`. Disk was 100% full at last legitimate run (120GB used).

**Attack timeline (reconstructed from experiment timestamps):**

| Period | Experiment IDs | Activity |
|--------|---------------|----------|
| ~2026-04-27 | 1 | `cve_test_1778457616` -- initial CVE probe |
| ~2026-04-27 | 4-6 | `scan_1778457759` through `scan_1778457767` -- scan phase |
| ~2026-05-28 | 47-58 | `poc_autodiscover_probe_177976...` -- multi-Python PoC |

**Phase 1 -- Recon (experiments 47-58):** 12 experiments targeting 3 Python versions (3.7, 3.13, 3.15) across 4 LLM evaluation scorer packages (phoenix, deepeval, ragas, trulens). Each experiment sets its `artifact_location` to a `file://` URI inside `/root/.venv/lib/pythonX.Y/site-packages/mlflow/genai/scorers/{scorer}/`. The attacker is probing which Python environments and scorer packages exist by seeing which artifact writes succeed.

**Phase 2 -- Exploitation (experiments 57-58):** Two runs named `rce-import-artifact-writer` (run IDs `48b637...` and `c42467...`), status `RUNNING`. The attacker uploaded a `.py` file -- a Python import canary -- into the scorer package directory tree via CVE-2026-2651 (unauthorized artifact upload in `--serve-artifacts` mode). When MLflow's scorer discovery walks the package tree and imports the module, the `Trigger` class writes a marker file containing `os.getuid()`, `os.getgid()`, `os.getpid()`, and an attacker-controlled token to verify execution.

The operator runs MLflow as root. If import-time execution succeeds, the attacker has root code execution on the Scaleway instance.

**CVE context:** CVE-2026-2651 (MLflow artifact write without auth, `--serve-artifacts` mode). Also consistent with the LFI class CVE-2024-2928. The `file://` artifact location scheme is the write primitive.

---

## Shodan Coverage Gap -- Model Serving Platforms

The zero results across 9 of 11 platforms reflect Shodan's port coverage, not platform absence. Concrete alternatives:

| Platform | Primary Port | Shodan Status | Alternative |
|----------|-------------|---------------|-------------|
| TorchServe management | 8081 | Not crawled | masscan Hetzner/Scaleway/OVH |
| TorchServe metrics | 8082 | Not crawled | masscan + httpx `ts_` prefix filter |
| TF Serving REST | 8501 | Not indexed at field depth | masscan + httpx path probe |
| TGI | 8080 | Fields not indexed | masscan + httpx `/info` |
| Triton HTTP | 8000 | Path not indexed | masscan + httpx `/v2` path probe |
| Triton metrics | 8002 | Not crawled | masscan |
| BentoML | 3000 | Header not indexed | masscan + httpx `Bento-Name` header |
| Ray Dashboard | 8265 | API path not indexed | masscan |

Port 5000 is indexed (Flask default, heavy Shodan crawl) -- this is why MLflow is uniquely visible. Every other platform defaults to non-crawled ports.

---

## Attack Classes Documented (not executed)

**MLflow supply chain via model injection:** Unauth artifact upload (`/api/2.0/mlflow/artifacts/upload` or `PUT /upload`) on `--serve-artifacts` deployments writes to the artifact store. If the artifact store path is within the Python package tree (as on 51.159.148.91), the next MLflow scorer import executes attacker code. If the S3 bucket is writable (two instances use `s3://mlflow/`), model pickle files can be replaced with malicious weights. Malicious pickle executes on `mlflow.pyfunc.load_model()`.

**vLLM management endpoint bypass:** `--api-key` on vLLM only gates `/v1/*` inference paths. Control endpoints respond to unauthenticated callers regardless: `GET /metrics` (Prometheus inference telemetry), `GET /tokenize` (tokenize any string), `POST /update_weights` (hot-swap model weights from URL), `POST /pause` / `POST /resume` (stop serving). The update_weights endpoint is the highest-severity primitive: an attacker with network access can point the serving process at a malicious model URL without credentials.

**TorchServe ShellTorch (CVE-2023-43654):** Management API at port 8081 accepts `POST /models?url={arbitrary_url}`. Pre-patch: the URL is fetched and loaded, executing code in the `.mar` archive. Post-patch: the fetch still occurs (SSRF) even with the RCE chain partially blocked. The management port ships bound to `0.0.0.0` despite documentation saying `127.0.0.1`.

---

## aimap Deepdive Results

aimap v1.9.36, `-scan-all-fingerprints`, 420 ports probed across 10 hosts, 46m56s. Summary: 24 open ports, 13 services, 17 findings (9 critical / 5 high / 1 medium / 2 low), 10 unauthenticated.

All 8 directly-confirmed MLflow instances found on port 5000. aimap classifies all as `critical` risk_level, citing CVE-2024-37052...37060 (RCE via malicious pickle model upload to unauth registry, code execution on `pyfunc.load_model()`).

**New services beyond the MLflow surface:**

**172.203.208.10 -- Elasticsearch 8.19.13, port 9200, unauthenticated, MEOW-COMPROMISED:**
- Cluster: `my-cluster`, node name: `ELK-machine` (same operator as MLflow finding #159, username `elkmachine`)
- 7 indices: `centific`, `centific-runtimelogs-dev-2026`, `centific-runtimelogs-development-2026`, `centific-runtimelogs-qa-2026`, `datafactory_logs`, `keycloak`, `read_me`
- 82,701 documents alive. `read_me` is the Meow-Actor-A extortion marker.
- Attribution: BTC `bc1q38rjul6gdamfflf6p4ukz0ymtvfgfv2j9saf6r`, contact wendy.etabw@gmx.com, paste tli.sh/73x1k
- State: compromised-marked, data not yet wiped. `centific` in 4 index names -- probable operator/project name.
- MLflow (#159) and Elasticsearch both unauthenticated on the same Azure host. The attacker already owns the Elasticsearch tier.

**210.131.221.109 -- Open Directory, port 80, CRITICAL:**
- `Server: SimpleHTTP/0.6 Python/3.13.3` -- Python's built-in HTTP server serving from the working directory
- Exposed: `.claude/`, `CLAUDE.md`, `.claudeignore`, `.git/`, `.github/`, `.gitignore`, `.mypy_cache/`, `.pytest_cache/`, approximately 54 entries total
- `.claude/` may contain Claude Code session state, hooks, or credentials
- `.git/` exposes full source commit history
- Same host runs MLflow unauth on port 5000
- The operator is running `python3 -m http.server 80` (or equivalent) from their project root alongside their MLflow instance

**101.202.128.3 -- Harbor + MinIO, AUTH-REQUIRED (LOW/MEDIUM):**
- Ports 443 and 8888: Harbor container registry (`Bearer realm=harbor-registry`) -- catalog access denied. Not a finding; auth enforced.
- Port 9000: MinIO S3 API -- returns `AccessDenied`. Auth is enabled on this MinIO instance.
- Correction to earlier assessment: the `s3://mlflow/` artifact backend on this host uses a local MinIO instance with auth enforced, not AWS S3. Public bucket access is not possible here.
- Port 5000: MLflow confirmed unauth (separate auth state from MinIO/Harbor).

VisorLog updated: findings #166 (Elasticsearch Meow) and #167 (Open Directory) ingested.

---

## Arsenal Coverage

| Tool | Run | Result |
|------|-----|--------|
| JAXEN (Shodan harvest) | Yes | 16 dorks executed; MLflow 10 hits, others 0 or stale |
| aimap | Done | v1.9.36, `-scan-all-fingerprints`, 46m56s. 13 services, 17 findings. 2 critical co-located discoveries. `recon/model-serving-2026-05-28/aimap-mlflow.json` |
| VisorGraph / recongraph | Attempted | crt.sh 502; no cert pivots returned |
| aimap-profile | Not run | Network access denied |
| JS-bundle analysis | Not run | MLflow 5000 is Python server; no SPA bundle secrets surface |
| VisorLog | Done | 12 findings ingested (#152-#161, #166-#167); 9 HIGH, 3 CRITICAL |
| VisorScuba | Done | All 10 primary hosts score 0/10, AI.C1 violation |
| BARE | Not run | Permission denied |
| VisorBishop | Not run | Network access denied |
| menlohunt | Not applicable | |
| nu-recon | Attempted | Network access denied |
| VisorPlus | Partially run | visorplus assess denied |
| VisorHollow | SKIP | Binary cannot execute |
| VisorAgent | ETHICAL STOP | Controlled targets only |

---

## Pivot Avenues

1. **elkmachine Elasticsearch** -- 172.203.208.10:9200 is open and Meow-marked. Pull `/_cat/indices?v` for full index list; read `centific` index for data class identification. The MLflow instance on the same host may have experiment data referencing the Elasticsearch pipeline.
2. **210.131.221.109 open directory** -- `GET http://210.131.221.109/.claude/` to enumerate Claude Code session state. `GET http://210.131.221.109/CLAUDE.md` for project instructions. `git clone http://210.131.221.109/.git` for full source history. Not executed.
3. **Exploitation run artifact read** -- `GET /api/2.0/mlflow/artifacts/list?run_uuid=48b6377316c441e3b71505a45dd94b18` on 51.159.148.91. Confirms whether the `.py` canary landed on an importable path.
4. **Username cross-reference** -- `wonjungy` (GCP), `elkmachine` (Azure), `centific` (ES index name) across GitHub, HuggingFace, Docker Hub, LinkedIn.
5. **S3 bucket check** -- 168.119.201.8 still uses `s3://mlflow/` with gunicorn (not MinIO as on 101.202.128.3). `aws s3 ls s3://mlflow/ --no-sign-request` against this host's backend. 101.202.128.3 S3 bucket is MinIO with auth enabled -- strike that pivot.
6. **TorchServe masscan lane** -- masscan 8081 against Hetzner 95.216.0.0/14, Scaleway 51.158.0.0/16, OVH 135.125.0.0/16. httpx filter for `nextPageToken`.
7. **vLLM re-harvest** -- `port:8000 "vllm" http.status:200` when Shodan index refreshes; also masscan Vast.ai and RunPod ranges.

---

## Candidate Insight

**Candidate Insight #50:** MLflow's default-no-auth posture is uniquely Shodan-visible because port 5000 is heavily crawled (Flask default). No other model-serving platform has equivalent Shodan coverage. This makes MLflow an outlier: its population is surveyable entirely via passive means while every other ML serving platform (TorchServe, TF Serving, vLLM, Triton, TGI) requires active masscan sweeps to find. Port 5000 as a survey anchor is specific to MLflow/Flask-family deployments.

---

## Query Catalog

```
# MLflow (productive)
port:5000 http.title:"MLflow"                               → 10 hits, confirmed live, all unauth

# MLflow (dead — too specific for Shodan body index)
port:5000 "registered_models" "mlflow"                      → 0 hits

# vLLM (stale population -- indexing lag)
port:8000 "max_model_len" "vllm"                            → 10 hits, all offline at probe
port:8000 "owned_by":"vllm"                                 → 0 hits (JSON field depth not indexed)

# Not Shodan-indexable -- use masscan instead
port:8081 "nextPageToken" "models"                          → 0 hits (TorchServe)
port:8082 "ts_"                                             → 0 hits (TorchServe metrics)
port:8501 "model_version_status" "AVAILABLE"                → 0 hits (TF Serving)
port:8265 "ray_version"                                     → 0 hits (Ray)
port:8080 "model_id" "model_dtype"                          → 0 hits (TGI)
port:8000 "/v2/health/ready"                                → 0 hits (Triton)
port:8002 "nv_inference_request_success"                    → 0 hits (Triton metrics)
port:3000 "Bento-Name"                                      → 0 hits (BentoML)
```
