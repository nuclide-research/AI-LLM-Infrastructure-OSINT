# BentoML — Stage -1 OSINT Brief

Researcher: Nuclide | Date: 2026-06-09 | Source: read-only (gh, NVD)

## 1. Platform Identification

- **Versions.** Stable `v1.4.39` (2026-05-07). Active line `v1.4.x` (~monthly). `v1.3.x` final = `v1.3.4post1` (RCE-CVE'd). v1.2 = auth-policy boundary; Yatai 2.0 proposal in flight.
- **Default ports (from `default_configuration.yaml` v2):** `http.host: 0.0.0.0` / `http.port: 3000` primary; `proxy_port: 8000` internal; gRPC `8001` (deprioritized in 1.4). Yatai admin: `8080` via port-forward.
- **Auth posture — AUTH OFF.** `access_authorization: bool = False` in `schemasv2.py` and `_internal/cloud/deployment.py`. Core `bentoml serve` has NO auth middleware in the request path; auth is a deployment toggle pushed via BentoCloud / Yatai. Bare `bentoml serve` or `docker run` exposes `/`, `/docs`, `/metrics`, `/schema.json`, `/livez`, `/readyz` open to any reacher of 3000.
- **Endpoint shape (`_bentoml_impl/server/app.py`):**
  - `/` -> `main-ui.html` (`BentoML Inference Service`) or `main-openapi.html` (Swagger)
  - `/docs.json` -> OpenAPI 3.0.2, `info.contact.email = contact@bentoml.com`, `info.title = <svc name>`
  - `/schema.json` -> internal BentoML schema feeding the React UI
  - `/livez`, `/readyz`, `/healthz` (alias `/health`), `/metrics` (Prometheus)
  - `/<api_name>` -> service-author-defined inference endpoint (`/summarize`, `/predict`, ...)
  - `/assets/*` -> UI bundle (`bentoml-ui.umd.js`, `favicon.ico`)
- **Yatai admin:** `/setup?token=<YATAI_INITIALIZATION_TOKEN>` is the first-admin-claim surface — if Ingress-exposed and the token leaks, attacker claims root admin. `/api_tokens`, `/api/v1/*`, `/dashboard` follow.

## 2. Deployment Patterns

- **Docker** (most common): `bentoml containerize` then user-built image; no canonical `bentoml/bento-server` registry tag.
- **K8s via Yatai helm chart**: BentoDeployment CRD. 844 stars / 76 forks (low adoption vs core 8.6k).
- **Bare `bentoml serve`** on Python (lab/research): uvicorn direct.
- **Cloud**: BentoCloud (vendor SaaS), Modal, SageMaker — mostly behind auth proxies, out of OSINT scope.

## 3. Fingerprint Research

| Signal | Value | Strength |
|---|---|---|
| **Server header** | `Server: BentoML Service/<service_name>` | **STRONG** — pathognomonic |
| HTML title (UI) | `<title>BentoML Inference Service</title>` | STRONG |
| HTML title (legacy) | `<title>BentoML Prediction Service</title>` | STRONG |
| JS asset | `/assets/bentoml-ui.umd.js`, `BentoMLUI.mount(schema, ...)` | STRONG |
| Response header | `X-BentoML-Request-ID`, `X-BentoML-Trace-ID` | STRONG (any endpoint emits) |
| OpenAPI extension | `x-bentoml-name`, `x-bentoml-io-descriptor` keys in `/docs.json` | STRONG |
| OpenAPI contact | `info.contact.email: "contact@bentoml.com"` | STRONG |
| GTM (legacy UI) | `GTM-WNPGWRM` | MEDIUM (only legacy /docs) |
| Underlying stack | uvicorn + Starlette | NOISE (do not anchor on these alone) |

## 4. Population Estimate

- **Top 3 Shodan dorks for Stage 0 harvest:**
  1. `"Server: BentoML Service"` — direct header match; highest precision
  2. `http.title:"BentoML Inference Service"` — UI match
  3. `http.html:"x-bentoml-name"` OR `http.html:"BentoMLUI.mount"` — JS/spec match
- **Predicted population.** BentoML serves a similar niche to vLLM (~6k Shodan), Triton (~1.5k), Ray Serve (~800). But: Docker deploys are user-built (no canonical image hash), and 3000 is shared with Grafana/Node.js apps. Most BentoML lives behind ingress / BentoCloud SaaS. **Predicted internet-reachable population: 200-900 hosts; 95% CI [120, 1500].**
- **Geographic spread expectation.** US-heavy (BentoML, Inc. is SF-based, OSS adoption skews US/EU); secondary China (heavy MLOps adoption); Korea/JP smaller pockets.

## 5. Known Attack Surfaces

- **14 BentoML CVEs in NVD, 0 Yatai CVEs.** Themes: pickle deserialization RCE, runner-server param injection, archive path traversal, Dockerfile-gen RCE.
  - **CVE-2024-2912 / 2024-9070** — pickle RCE in runner server (1.3.4post1-)
  - **CVE-2025-27520 / 2025-32375** — RCE chain pre-1.4.8
  - **CVE-2025-54381 / 2026-24123 / 2026-27905** — path traversal `safe_extract`, `docker.system` pre-1.4.37
  - **CVE-2026-44345 / 44346** — malicious bento package RCE pre-1.4.39 (current)
- **Misconfigs:** (a) no auth wrapper around `bentoml serve` (default); (b) `/metrics` exposes service names + labels; (c) Yatai `/setup` reachable if Ingress misconfigured -> admin claim; (d) `/docs.json` leaks all method names + I/O schema regardless of auth.

## 6. Sources Read

`bentoml/BentoML` README, `default_configuration.yaml` v2, `_bentoml_impl/server/app.py`, `_bentoml_sdk/service/config.py`, `_internal/service/openapi/`, `cloud/schemas/schemasv2.py`. `bentoml/Yatai` README, install script, helm NOTES, `common/consts/env.go`. NVD bentoml (14) / yatai (0). No dedicated O'Reilly title.

## Top 3 Stage-0c Scanner Signals

1. **`Server: BentoML Service` response header** — strongest single-probe fingerprint
2. **`/docs.json` body containing `x-bentoml-name` or `contact@bentoml.com`** — version + service surface
3. **`/schema.json` returning JSON with `BentoMLUI`-shaped keys** — confirms running UI

## Verdict

**Worth a full cohort survey.** Auth-off-by-default on a `0.0.0.0:3000` listener, a 14-CVE history dominated by RCE/deserialization, a claimable Yatai `/setup?token=` admin surface, and 0 prior NuClide coverage — this maps cleanly onto the auth-on-default thesis and likely yields a small-but-high-severity cohort (target band 200-900, RCE-class CVEs gating most of it). Add BentoML to tome, build aimap fingerprint, run the chain.
