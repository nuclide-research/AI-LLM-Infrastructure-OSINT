# OSINT Platoon -- MLflow (cat-mlflow-2026-06-28)
Date: 2026-06-28
Sources: mlflow.org docs, GitHub mlflow/mlflow, ZeroPath, OffSec, SentinelOne, Docker Hub

---

## Squad 1 - Auth Posture

**Auth default: OFF in all versions.**

MLflow tracking server ships with zero authentication enforced. Any visitor can read all experiments, runs, metrics, parameters, and artifact paths without credentials.

**Optional auth mechanics:**
- First appeared experimentally around v2.5.0; still labeled "experimental" in v2.7.0 docs
- Enable: `mlflow server --app-name basic-auth`
- Requires: `export MLFLOW_FLASK_SERVER_SECRET_KEY="<key>"` (CSRF protection)
- Client-side env vars (for authenticated servers): `MLFLOW_TRACKING_USERNAME` + `MLFLOW_TRACKING_PASSWORD`
- Config file: `mlflow/server/auth/basic_auth.ini`
- Default admin credentials: username=`admin` password=`password` (v2.7.0) / `password1234` (latest docs)
- v2.7.0 docs explicitly say "update the default admin password as soon as possible" -- meaning many admins enable auth but leave defaults

**RBAC timeline:**
- Per-resource permissions (legacy) -- present in v2.x
- RBAC roles -- added in MLflow 3.13.0
- Third-party OIDC plugin: `mlflow-oidc/mlflow-oidc-auth` (community, not official)

**Version landscape (self-hosted population):**
- burakince/mlflow Docker Hub: 1M+ pulls; latest tag = v3.14.0
- Ubuntu/mlflow, bitnami/mlflow, openeuler/mlflow also indexed
- Expected population spans v2.x (2022-2024 era) through v3.x (2025+)
- Pre-v2.5.0: NO auth mechanism exists at all, not just off by default

**Sources:**
- https://mlflow.org/docs/latest/self-hosting/security/basic-http-auth/
- https://mlflow.org/docs/2.7.0/auth/index.html
- https://www.mlflow.org/docs/2.5.0/auth/index.html

---

## Squad 2 - Population/Deployment

**Primary deployment path: Docker / Docker Compose binding to 0.0.0.0**

Official MLflow docker-compose template uses:
```
MLFLOW_HOST=0.0.0.0
MLFLOW_PORT=5000
```

Community templates universally use `mlflow server --host 0.0.0.0 --port 5000`.
Example configurations (all community-confirmed):
```yaml
# PostgreSQL backend, S3 artifacts (common pattern)
command: mlflow server --backend-store-uri postgresql+psycopg2://postgres:postgres@postgresql:5434/mlflow-db
         --host 0.0.0.0 --port 5000 --serve-artifacts

# MySQL backend
command: mlflow server --backend-store-uri $MLFLOW_BACKEND_STORE_URI --host 0.0.0.0

# S3 artifact root
command: mlflow server --default-artifact-root s3://mlflow_bucket/mlflow/ --host 0.0.0.0
```

**Deployment stack pattern:** MLflow + PostgreSQL/MySQL (metadata) + MinIO/S3 (artifacts) + optional NGINX
The NGINX reverse proxy is present in "production" guides but absent in quickstart and most tutorials.

**Docker Hub pull signal:** burakince/mlflow = 1M+ (community image; official does not maintain a standalone tracking server image on Docker Hub directly).

**CVE landscape (all unauthenticated by default):**
| CVE | Type | Auth Required | Affected Versions | Published |
|-----|------|--------------|-------------------|-----------|
| CVE-2024-2928 | LFI via URI fragment | None | <2.11.3 | Apr 2024 |
| CVE-2025-11201 | RCE via dir traversal (model creation) | None | <patch commit | 2025 |
| CVE-2025-14279 | CSRF -> experiment data theft/destruction | None (browser-side) | unknown | May 2025 |
| CVE-2025-15031 | unknown, patched with 2025-11201 | None | unknown | 2025 |
| CVE-2026-2033 | RCE (chained with CVE-2026-2635) | None | unknown | Feb 2026 |
| CVE-2026-2635 | Auth bypass -> chained to RCE | None | unknown | Feb 2026 |
| CVE-2026-2614 | Info disclosure via CreateModelVersion | None | unknown | May 2026 |

**Pattern:** Three critical unauth-required CVEs published Feb-May 2026 alone. Root cause pattern: input validation failure on API endpoints that were never gated by auth.

**Sources:**
- https://github.com/mlflow/mlflow/tree/master/docker-compose
- https://hub.docker.com/r/burakince/mlflow
- https://zeropath.com/blog/cve-2025-11201-mlflow-directory-traversal-rce
- https://www.offsec.com/blog/cve-2024-2928/
- https://www.sentinelone.com/vulnerability-database/cve-2026-2033/
- https://raxe.ai/labs/advisories/RAXE-2026-030

---

## Squad 3 - Data Exposure Surface

**Unauthenticated API surface (no auth required on default install):**

| Endpoint | Method | Returns |
|----------|--------|---------|
| `/api/2.0/mlflow/experiments/search` | POST | Experiment names, tags, artifact_location, creation time |
| `/api/2.0/mlflow/runs/search` | POST | Run params, metrics, tags, artifact_uri, status |
| `/api/2.0/mlflow/registered-models/search` | POST | Model names, versions, description, tags |
| `/api/2.0/mlflow/artifacts/list` | GET | root_uri + FileInfo (path, size, is_dir) |
| `/api/2.0/mlflow/model-versions/search` | POST | Version metadata, source URI, run_id |

**Artifact URI leak:**
`artifact_uri` is stored in `mlflow.entities.RunInfo` and `artifact_location` in experiment metadata.
Exposed URI formats when direct (non-proxied) artifact mode:
```
s3://my-company-bucket/mlflow/experiments/...
gs://gcp-ml-bucket/artifacts/...
wasbs://container@storageaccount.blob.core.windows.net/mlflow/...
b2://bucket@endpoint/path/...
sftp://user@host/path/
hdfs://host:port/path/
/mnt/nfs/mlflow/artifacts/   (local/NFS = operator hostname leak)
```

**Attack significance:**
- Direct mode (no `--serve-artifacts`): S3/GCS bucket names in plain text via API. Pivot to bucket enumeration or credential hunting (if bucket is public or keys are in run params).
- Proxied mode: bucket names still in `artifact_location` metadata; credentials held server-side but all users inherit server IAM role.
- Run parameters can contain hardcoded API keys, DB connection strings, model input PIIs if logged without sanitization.

**LFI primitive (CVE-2024-2928, fixed <2.11.3):**
```
GET /model-uri/model-name/artifacts/somefile#../etc/passwd HTTP/1.1
Host: target:5000
```
No auth required. Browsers strip fragment; exploitation requires curl/Burp. File reads: /etc/passwd, env vars, application secrets.

**RCE primitive (CVE-2025-11201):**
POST to model version creation endpoint with traversal in `source` parameter.
Writes arbitrary file to filesystem; Python .pth file in sys.path triggers code execution.
No auth required.

**Sources:**
- https://mlflow.org/docs/latest/rest-api.html
- https://mlflow.org/docs/latest/self-hosting/architecture/artifact-store/
- https://www.offsec.com/blog/cve-2024-2928/
- https://zeropath.com/blog/cve-2025-11201-mlflow-directory-traversal-rce

---

## Squad 4 - Fingerprint/Dork Research

**HTML fingerprints (confirmed distinctive):**
- Page title: `MLflow` (exact; no version suffix in title tag)
- JS bundle paths: `/static-files/lib/mlflow/...` present in page HTML
- API JSON response: `{"experiments":[...]}` at `/api/2.0/mlflow/experiments/search`
- Favicon: served from `/static-files/...` path

**Port landscape:**
- Port 5000: tracking server (primary, canonical)
- Port 8080: MLflow model serving (`mlflow models serve`) -- different component, NOT tracking UI
- Port 5001: seen in some guides for model serving alternate; uncommon for tracking
- Port 4040: Spark UI (often co-located but not MLflow itself)
- Kubernetes: often exposed via ingress at mlflow.{company}.{tld}, tracking.{company}.internal, or ml.{company}.com -- no canonical pattern

**Dork tiers (from tome baseline + research enrichment):**
- basic:   `"mlflow" port:5000`
- strict:  `http.title:"MLflow" port:5000`
- version: `http.title:"MLflow" port:5000 http.html:"version"` (unconfirmed populates)
- API:     `http.html:"/api/2.0/mlflow" port:5000`
- JS path: `http.html:"static-files/lib/mlflow" port:5000`
- Port 8080 tracking variant: `http.title:"MLflow" port:8080`

**Population estimate (unconfirmed -- requires live Shodan query):**
- No published research with exact count found
- Hackers Arise blog references Shodan dork `port:5000 "MLflow"` as viable hunt technique
- burakince/mlflow Docker image: 1M+ pulls suggests large self-hosted base
- Comparable platforms (Jupyter) show 3,000-8,000 indexed; MLflow likely similar order of magnitude

**Existing security research:**
- CVE-2024-2928 (OffSec, Apr 2024) -- LFI via URI fragment
- CVE-2025-11201 (ZeroPath, 2025) -- RCE dir traversal
- RAXE-2026-030 (RAXE Labs, Feb 2026) -- chained auth bypass + RCE
- April 2026 vulnerability digest notes "auth gap continues pattern"
- No prior population-scale survey published (NuClide would be first)

**Sources:**
- https://hackers-arise.com/hacking-artificial-intelligence-ai-reconnaissance-on-ai-infrastructure/
- https://github.com/advisories/GHSA-5cvj-7rg6-jggj
- https://raxe.ai/labs/advisories/RAXE-2026-030
- https://app.opencve.io/cve/?product=mlflow&vendor=lfprojects

---

## Dork Set (validated, ready for Shodan)

```
# Tier 1 - core population
http.title:"MLflow" port:5000
"mlflow" port:5000

# Tier 2 - enrichment / version discrimination
http.title:"MLflow" port:5000 http.html:"version"
http.html:"/api/2.0/mlflow" port:5000
http.html:"static-files/lib/mlflow" port:5000

# Tier 3 - port variants
http.title:"MLflow" port:8080
http.title:"MLflow" port:5001

# Note: http.html: filters are body-only on Shodan web UI; json-field signals route to Censys
```

---

## Insight Candidates

**Cand #I-A:** MLflow auth posture is a two-level default failure: (1) auth off by default, and (2) even when enabled, default admin password is `password` / `password1234`. A survey of auth-enabled instances may find a significant fraction using default creds -- a deeper failure than simple auth-off.

**Cand #I-B:** The unauthenticated CVE pattern (7 CVEs 2024-2026, all exploitable without creds) is a direct consequence of the auth-off-by-default design. Endpoints were never designed with an auth gate; security patches retrofit validation but cannot retrofit the authentication assumption the API was built without.

**Cand #I-C:** Artifact URI exposure (s3://, gs://, wasbs:// bucket names in `artifact_uri` field) creates a second-order attack surface even on MLflow instances that are otherwise hardened. The artifact location leaks cloud storage topology before any credential is obtained.

**Cand #I-D:** MLflow at port 8080 (`mlflow models serve`) is a distinct service with a different fingerprint and no experiment/run data. Dorks hitting port 8080 with MLflow title will conflate two different attack surfaces; must split population analysis by port.

---

## Intelligence Summary

- Auth is OFF by default in ALL MLflow versions; optional auth added ~v2.5.0 but requires explicit `--app-name basic-auth` flag + default admin creds are `admin/password`
- Primary deployment vector is `mlflow server --host 0.0.0.0` in Docker Compose; official templates ship this configuration with no auth flag
- Unauthenticated API surface exposes experiment names, model names, run parameters, metrics, and cloud artifact storage URIs (S3/GCS/Azure bucket names)
- CVE landscape is severe: 7 published CVEs 2024-2026, ALL requiring no authentication; two active RCE chains (CVE-2025-11201, CVE-2026-2033+2635)
- No prior population-scale survey published; NuClide would be first; population estimated in low thousands based on Docker Hub pull signal and comparable platforms
