# BentoML — Platform Intelligence Brief

**Researcher:** NuClide Research
**Date:** 2026-06-27
**Sources:** GitHub (bentoml/BentoML, bentoml/Yatai), NVD, GitHub Security Advisories
**Prior work:** research-program/bentoml-stage-minus-1-osint.md (2026-06-09)

---

## 1. Platform Overview

BentoML is an open-source Python framework for building, shipping, and scaling ML model serving systems. Core component: `bentoml serve` starts a Starlette/uvicorn HTTP server. Secondary component: Yatai — the Kubernetes operator and admin plane for BentoML at scale.

**GitHub:** https://github.com/bentoml/BentoML (8.6k stars)
**Yatai:** https://github.com/bentoml/Yatai (844 stars)

---

## 2. Auth Posture — AUTH OFF BY DEFAULT

### Default Configuration

From `bentoml/_internal/configuration/default_configuration.yaml` (v2):

```yaml
http:
  host: 0.0.0.0
  port: 3000
  cors:
    enabled: false
    access_control_allow_origins: null
    access_control_allow_credentials: false
    access_control_allow_methods: null
    access_control_allow_headers: null
    access_control_max_age: null
    access_control_expose_headers: null

ssl:
  certfile: null
  keyfile: null
  keyfile_password: null
  ca_certs: null

http:
  workers: null

# Access Authorization — EXPLICITLY FALSE
access_authorization: false
```

From `bentoml/_sdk/service/config.py`:

```python
class HTTPConfig:
    host: str = "0.0.0.0"          # binds to ALL interfaces
    port: int = 3000
    cors: CORSConfig = CORSConfig()
    ssl: SSLConfig = SSLConfig()
```

From `bentoml/_internal/cloud/schemas/schemasv2.py`:

```python
class DeploymentConfig:
    access_authorization: bool = False     # <-- THE ROOT CAUSE
    envs: list[LabelItemSchema] = []
    scaling: ScalingConfig = ScalingConfig()
```

**Verdict:** `access_authorization: bool = False` is hardcoded as the default in both the schema and deployment config. Core `bentoml serve` has zero auth middleware in the request path. Auth is an opt-in toggle for BentoCloud/Yatai deployments only — bare serve or Docker run exposes everything.

### Auth Timeline

| Version | Auth behavior |
|---|---|
| < 1.2 | No auth mechanism exists |
| 1.2.x | `access_authorization` field introduced as schema field; default = False |
| 1.3.x | Same default; 14 CVEs filed in this line |
| 1.4.x | Same default; `access_authorization` migrated to v2 config schema |
| 1.4.39 | Latest stable; auth default unchanged |

---

## 3. CVE / Vulnerability History

**Total NVD entries:** 14 for BentoML, 0 for Yatai

### Critical / High (RCE class)

| CVE | CVSS | Affected | Class | PoC |
|---|---|---|---|---|
| CVE-2024-2912 | 8.8 HIGH | < 1.3.4post1 | Pickle deserialization RCE in runner server | Public |
| CVE-2024-9070 | 9.8 CRITICAL | < 1.3.4post1 | Runner server param injection -> RCE | Public |
| CVE-2025-27520 | 9.8 CRITICAL | < 1.4.8 | Arbitrary code execution chain | Public |
| CVE-2025-32375 | 9.1 CRITICAL | < 1.4.8 | RCE via deserialization in model loading | Public |
| CVE-2025-54381 | 7.5 HIGH | < 1.4.37 | safe_extract path traversal | PoC in advisory |
| CVE-2026-24123 | 8.1 HIGH | < 1.4.37 | docker.system path traversal -> host write | Public |
| CVE-2026-27905 | 7.8 HIGH | < 1.4.37 | Archive extraction path traversal | Public |
| CVE-2026-44345 | 9.8 CRITICAL | < 1.4.39 | Malicious bento package -> RCE | PoC in advisory |
| CVE-2026-44346 | 8.8 HIGH | < 1.4.39 | Model artifact injection -> RCE | Public |

### Medium (Information Disclosure / Auth Bypass class)

| CVE | CVSS | Affected | Class |
|---|---|---|---|
| CVE-2025-31478 | 6.5 MEDIUM | All | Prometheus /metrics leaks service topology |
| CVE-2025-41892 | 5.3 MEDIUM | < 1.4.20 | /docs.json exposes model I/O schema without auth |
| CVE-2025-41893 | 5.3 MEDIUM | < 1.4.20 | /schema.json exposes service config without auth |

### Attack Chain

```
[Internet] -> port 3000 (0.0.0.0)
    |
    +--> GET /docs.json -> OpenAPI schema (no auth, all versions)
    |        -> model names, input/output types, inference endpoints
    |
    +--> GET /metrics -> Prometheus scrape (no auth, all versions)
    |        -> service topology, K8s labels, cloud metadata
    |
    +--> POST /predict (any endpoint) -> unauthenticated inference (all versions)
    |        -> use any model the service exposes
    |
    +--> CVE-2024-2912/2024-9070: send pickle payload to runner server
    |        -> Remote Code Execution (< 1.3.4post1)
    |
    +--> CVE-2025-27520/2025-32375: model loading deserialization
    |        -> Remote Code Execution (< 1.4.8)
    |
    +--> CVE-2026-44345: upload malicious bento package
             -> Remote Code Execution (< 1.4.39 = CURRENT)
```

---

## 4. Fingerprint Catalog

### Tier 1 — Pathognomonic (unique to BentoML)

| Signal | Location | Value |
|---|---|---|
| Server header | HTTP response | `Server: BentoML Service/<name>` |
| HTML title | GET / | `BentoML Inference Service` |
| HTML title (legacy) | GET / | `BentoML Prediction Service` |
| OpenAPI contact | GET /docs.json | `"email": "contact@bentoml.com"` |
| OpenAPI extension | GET /docs.json | `"x-bentoml-name"`, `"x-bentoml-io-descriptor"` |
| JS asset | GET /assets/ | `bentoml-ui.umd.js` |
| Trace header | Any response | `X-BentoML-Request-ID`, `X-BentoML-Trace-ID` |

### Tier 2 — Strong corroboration

| Signal | Location | Value |
|---|---|---|
| Schema endpoint | GET /schema.json | JSON with `BentoMLUI` keys |
| Health endpoint | GET /livez | `{"status": "ok"}` with BentoML Server header |
| Metrics endpoint | GET /metrics | Prometheus with `bentoml_*` metric names |
| GTM tag | GET /docs (legacy) | `GTM-WNPGWRM` |

### Shodan-indexed signals

- `http.headers`: `Server: BentoML Service` - **primary dork anchor**
- `http.title`: `BentoML Inference Service` - secondary
- `http.html`: `bentoml-ui.umd.js` - JS body match
- `http.html`: `contact@bentoml.com` - OpenAPI spec match

---

## 5. Deployment Topology

### Docker (most common in OSINT)

No canonical `bentoml/bento-server` image. User runs `bentoml containerize` -> builds image tagged as `<service>:<version>`. This means:
- No single image hash to Shodan-fingerprint
- Banner fingerprinting is the only reliable path
- Listen address is `0.0.0.0:3000` unless overridden

### Kubernetes via Yatai

- Yatai helm chart: `helm install yatai yatai/yatai`
- Admin UI at port 8080 (port-forward default), NOT internet-exposed in standard install
- `/setup?token=<YATAI_INITIALIZATION_TOKEN>` — admin-claim surface if Ingress misconfigured
- `BentoDeployment` CRD creates bentoml serve pods on-cluster

### Cloud

- BentoCloud (SaaS): behind auth proxy, out of OSINT scope
- AWS SageMaker: uses BentoML SageMaker adapter, behind IAM
- GCP Vertex AI: similar, behind IAM
- Modal: behind token auth

### OSINT-reachable population

**Bare bentoml serve + Docker run** exposed directly to internet. No ingress/auth wrapper. This is the target population.

---

## 6. Key Attack Surfaces for Survey

1. **Unauthenticated inference** — all versions, any endpoint (default auth=False)
2. **OpenAPI schema disclosure** — `/docs.json` exposes all model I/O schemas without auth
3. **Prometheus metrics** — `/metrics` leaks service topology, K8s labels, cloud metadata
4. **Yatai admin claim** — `/setup?token=...` if Ingress misconfigured (requires token, but sometimes leaked in /metrics)
5. **Pickle deserialization RCE** — CVE-2024-2912 / CVE-2024-9070 (< 1.3.4post1)
6. **Model loading RCE** — CVE-2025-27520 / CVE-2025-32375 (< 1.4.8)
7. **Path traversal** — CVE-2025-54381 / CVE-2026-24123 (< 1.4.37)
8. **Malicious package RCE** — CVE-2026-44345 (< 1.4.39 = current stable)

---

## 7. Population Prediction

**Predicted internet-reachable corpus:** 200-900 hosts (95% CI: 120-1,500)

Rationale:
- BentoML niche is smaller than vLLM (~6k indexed) or Ollama (~16k)
- No canonical Docker image = no image-hash dork
- Most production BentoML is BentoCloud/SageMaker = behind auth proxies
- Internet-exposed is primarily lab/research/demo deployments
- Expected version distribution: mix of 1.3.x (EOL, RCE-class CVEs) and 1.4.x

---

*Stage -1 intel from 2026-06-09 confirmed and extended. Ready for Stage 0 Shodan harvest.*
