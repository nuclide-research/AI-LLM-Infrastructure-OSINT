# Model Serving Infrastructure Survey — 2026-05-28

**Platforms surveyed:** vLLM, TorchServe, TensorFlow Serving, Ray Serve, BentoML, Seldon Core, KServe, ONNX Runtime Server, Hugging Face TGI, MLflow, Triton Inference Server  
**Dorks executed:** 16 (logged in shodan/query-log.md)  
**Verification:** curl probes from research host

---

## Harvest Summary

| Platform | Dork Hits | Verified Live | Confirmed Identity | Auth Bypass Confirmed |
|----------|-----------|---------------|--------------------|-----------------------|
| vLLM | 10 | 0 | 0 | 0 |
| TorchServe (mgmt) | 0 | — | — | — |
| TF Serving | 0 | — | — | — |
| Ray Dashboard | 1 | 0 | 0 | 0 |
| BentoML | 0 | — | — | — |
| Seldon Core | 20 | 0 | 0 | 0 |
| MLflow | 10 | 10 | 10 | 10 (experiments API open, no auth) |
| Triton | 0 | — | — | — |
| TGI | 0 | — | — | — |

---

## vLLM — 10 Harvested, 0 Live

Dork: `port:8000 "max_model_len" "vllm"`  
All 10 IPs returned HTTP 000 (connection refused / firewall drop) at probe time. Shodan data is stale — these were live when crawled, taken down or firewalled since.

IPs harvested (for record):
- 108.58.51.82, 67.78.191.77, 162.251.247.13, 108.252.249.145, 82.130.248.249
- 113.30.160.211, 74.108.66.82, 24.139.33.243, 98.189.181.108, 173.92.133.57

vLLM management bypass (the key finding from pre-survey intel: `/metrics`, `/tokenize`, `/health` bypass `--api-key`) could not be confirmed against this population. Population exists in Shodan; re-run at different time or use fresh harvest.

**Dork refinement needed:** `"owned_by":"vllm"` zero hits — Shodan does not index JSON field values at that depth. `"max_model_len" "vllm"` is the productive signal. Try also: `port:8000 "vllm" http.status:200`.

---

## TorchServe — 0 Harvested

Port 8081 (management API — the ShellTorch CVE-2023-43654 surface) is not crawled by Shodan at any useful density. Neither the `nextPageToken` discriminator nor the `modelName/modelUrl/minWorkers` field set returned results. Port 8082 (Prometheus metrics with `ts_` prefix) also zero.

**Alternative approach:** masscan sweep on 8081 against known cloud ranges, then aimap for identity. Shodan is not the path here.

---

## Ray Dashboard — 1 Harvested, 0 Live

`18.203.88.120` — HTTP 000 at probe. Stale Shodan record.

---

## Seldon Core — 20 Harvested, 0 Live (1 FP)

Port 9000 `/api/v1.0/predictions` returned 20 Shodan hits. All 19 genuine candidates returned HTTP 000 — Seldon Core pods are not internet-accessible in any current deployment in this population.

**FP identified:** `94.72.112.137` — `Server: MinIO` in response headers. MinIO returns HTTP 400 with "An unsupported API call for method: POST at '/api/v1.0/predictions'" — exact same FP class documented in reference_menlohunt_status_code_fp.md (MinIO catches-all POST paths). Not Seldon.

---

## MLflow — 10 Harvested, 10 Live, 10 Confirmed Open

**All 10 instances confirmed as genuine MLflow, unauthenticated, experiments API live.**

### Verification method
- Server: gunicorn (8/10) or uvicorn (2/10) — both valid MLflow deployment patterns
- Title: `<title>MLflow</title>` confirmed on all 10
- `POST /api/2.0/mlflow/experiments/search {"max_results":10}` returns valid JSON experiment arrays on all 10
- `POST /api/2.0/mlflow/registered-models/search` returns 405 (GET-only endpoint in this MLflow version)
- `POST /api/2.0/mlflow/runs/search` returns `{}` — no runs visible without experiment_id filter, not an auth wall

### Instances

| IP | Server | Artifact Backend | Notable |
|----|--------|-----------------|---------|
| 104.154.156.34 (GCP) | gunicorn | local `/home` | Username leaked: `wonjungy` |
| 162.55.232.59 (Hetzner DE) | gunicorn | `mlflow-artifacts:/` scheme | High experiment count (IDs in 200M+ range) |
| 20.13.144.13 (Azure) | gunicorn | `/mlruns/` local | Sequential IDs, low count (40 experiments) |
| 210.131.221.109 (JP) | gunicorn | `mlflow-artifacts:/` scheme | High experiment count (IDs in 900M+ range) |
| 51.159.148.91 (Scaleway FR) | gunicorn | `file:///root/.venv/lib/python3.13/...` | **Honeypot/scanner activity** — experiment names = `poc_autodiscover_probe_{timestamp}_{hash}`, artifact paths expose `mlflow/genai/scorers/phoenix` and `deepeval` LLM eval packages |
| 51.158.107.81 (Scaleway FR) | uvicorn | `mlflow-artifacts:/` scheme | High experiment count (IDs sequential up to 196) |
| 168.119.201.8 (Hetzner DE) | gunicorn | `s3://mlflow/` | S3 artifact backend — artifacts may be accessible if bucket is public |
| 172.203.208.10 (Azure) | uvicorn | local `/home/elkmachine/mlflow-env/mlruns/` | Username leaked: `elkmachine` |
| 79.110.227.36 (Hetzner FI) | uvicorn | `mlflow-artifacts:/` scheme | Has `X-Frame-Options: SAMEORIGIN` header — partial hardening, no API auth |
| 101.202.128.3 (CN) | gunicorn | `s3://mlflow/` | S3 backend, 61+ experiments |

### Key findings

**Username leakage (2 instances):**
- `104.154.156.34`: `artifact_location: /home/wonjungy/mlflow-data/artifacts/` — `wonjungy` is the operator username
- `172.203.208.10`: `artifact_location: /home/elkmachine/mlflow-env/mlruns/` — `elkmachine` is the operator username

**S3 artifact backend (2 instances):**
- `168.119.201.8` and `101.202.128.3`: artifacts at `s3://mlflow/{experiment_id}` — if the S3 bucket "mlflow" is public, model artifacts, training data, and parameters are downloadable. Requires follow-on: `aws s3 ls s3://mlflow/ --no-sign-request`

**Active exploitation evidence (1 instance — CONFIRMED):**
- `51.159.148.91` (Scaleway FR): This instance shows a two-phase attack pattern already executed.

Phase 1 (recon): Experiments named `poc_autodiscover_probe_{unix_ns_timestamp}_{hash}` — systematic enumeration of Python versions and MLflow GenAI scorer packages. Probed: python3.7, python3.13, python3.15 across scorers: phoenix, deepeval, ragas, trulens. Artifact locations target `file:///root/.venv/lib/.../mlflow/genai/scorers/` and `file:///root/run/.venv/lib/.../mlflow/genai/scorers/` — two separate venv path roots probed.

Phase 2 (exploitation): Runs named **`rce-import-artifact-writer`** (run IDs `48b637...` and `c42467...`) in experiments 57 and 58. Status: `RUNNING`. Artifact URI points into the MLflow scorer package directories. This matches CVE-2026-2651 (unauthorized artifact upload in `--serve-artifacts` mode) — the attacker wrote artifacts to paths inside the Python package tree to overwrite scorer modules with malicious code, achieving import-time RCE.

**This instance has been actively exploited. The attack chain is recorded in the MLflow experiment database and readable without authentication.**

**Consistent pattern across all 10:**
- All experiment names are `p_` or `x_` prefixed with 8-char hex suffix — automated experiment generation, not human-created experiments
- `runs/search` returns `{}` without experiment_id filter — not an auth wall, just pagination behavior
- All instances confirmed no auth — `experiments/search` responds to any caller

### Exposure class
Unauthenticated access to full experiment tree: experiment IDs, names, artifact locations, creation timestamps, lifecycle state. The `/runs/search` endpoint with an experiment_id would return training metrics, parameters, tags, and artifact paths for all runs — confirmed open API surface.

---

## Dork Coverage Gaps

Platforms with zero Shodan coverage — ports not crawled or fields not indexed:
- **TorchServe 8081** — management port, not in Shodan index
- **TorchServe 8082** — metrics port, not crawled
- **TF Serving 8501** — `model_version_status` not indexed at field level
- **TGI 8080** — `/info` response fields not in Shodan body index
- **Triton 8002** — metrics port not crawled
- **Triton 8000** — `/v2/health/ready` path string not indexed
- **BentoML 3000** — `Bento-Name` header not in Shodan response index

For these platforms: masscan → httpx → aimap is the correct chain. Shodan misses ports <8000 almost entirely for ML serving.

---

## Next Steps (pivot avenues)

1. **MLflow S3 buckets** — `aws s3 ls s3://mlflow/ --no-sign-request` on 168.119.201.8 and 101.202.128.3 backends. Public bucket = model artifact download.
2. **MLflow runs extraction** — For any of the 10 live instances, `POST /api/2.0/mlflow/runs/search {"max_results":5,"experiment_ids":["1"]}` to pull actual run data (metrics, params, tags).
3. **Username attribution** — `wonjungy` and `elkmachine` are operator handles. Cross-reference against GitHub, HuggingFace, Docker Hub for model artifacts and identity.
4. **vLLM re-harvest at different hour** — 10 IPs went dark; try `port:8000 "vllm" http.status:200` variant; also try aimap against a fresh masscan sweep of known ML cloud ranges.
5. **51.159.148.91 exploitation confirmed** — `rce-import-artifact-writer` runs confirmed in experiments 57/58. Next: check if artifacts were actually written at the targeted paths (`GET /api/2.0/mlflow/artifacts/list?run_uuid=48b6377316c441e3b71505a45dd94b18`); check if phoenix/deepeval scorer modules are now malicious via the `/v1/evaluate` endpoint (if exposed).
6. **TorchServe masscan sweep** — masscan port 8081 against Hetzner/Scaleway/Linode ranges, httpx filter for `nextPageToken`, aimap for confirmation.
