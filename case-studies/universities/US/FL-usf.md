# University of South Florida: Marine Lab JupyterHubs (auth-enforced) + Adjacent Prometheus `/metrics` Public

_NuClide Research · 2026-05-19_

---

## Summary

USF College of Marine Science operates two JupyterHub instances on the `marine.usf.edu` subdomain: `ocgmod1.marine.usf.edu` (131.247.139.171:8000) and `manglillo.marine.usf.edu` (131.247.136.183:8000). Both correctly enforce authentication (`/hub/api/info` returns 403 "Missing or invalid credentials"). However, the `manglillo` host has a separate Prometheus instance on port 9090 with `/metrics` returning ~90 KB of unauthenticated metric data — a co-located observability service exposed without auth alongside the auth-enforced JupyterHub.

The JupyterHubs are properly configured. The Prometheus exposure is the material finding.

---

## Infrastructure

| Field | `ocgmod1` | `manglillo` |
|---|---|---|
| IP | 131.247.139.171 | 131.247.136.183 |
| Hostname | `ocgmod1.marine.usf.edu` | `manglillo.marine.usf.edu` |
| Org (WHOIS) | University of South Florida | University of South Florida |
| Department | College of Marine Science | College of Marine Science |
| JupyterHub port | 8000 | 8000 |
| Prometheus port | — | **9090 (public unauth)** |

Both hosts on USF's marine science research-compute network. Naming pattern (`ocgmod1` likely "ocean general circulation model 1"; `manglillo` is a Cuban/Spanish word for "small mangrove") consistent with academic marine modeling and biology compute.

---

## Observations

### Service 1 — `ocgmod1.marine.usf.edu:8000` JupyterHub

`GET http://ocgmod1.marine.usf.edu:8000/hub/api/info` → 403, `{"status":403,"message":"Missing or invalid credentials."}`
`GET .../hub/login` → 200, JupyterHub login page rendered

**Class observed**: JupyterHub auth-enforced (no anonymous access to `/hub/api/*`). The login form is publicly reachable but credentials are required. No exposed `/hub/api/users` or `/hub/api/services` without auth. Properly configured.

### Service 2 — `manglillo.marine.usf.edu:8000` JupyterHub

`GET http://manglillo.marine.usf.edu:8000/hub/api/info` → 403, `{"status":403,"message":"Action is not authorized with current scopes; requir..."}` (response truncated — scope-aware error message; auth backend differs slightly from `ocgmod1`)

**Class observed**: JupyterHub auth-enforced with scope-aware authorization. Same posture as `ocgmod1` — login required, no anonymous API access.

### Service 3 — `manglillo.marine.usf.edu:9090` Prometheus `/metrics` PUBLIC (but empty — default install)

`GET http://manglillo.marine.usf.edu:9090/metrics` → 200, ~90,303 bytes of Prometheus exposition format.
`GET .../` → 200, 714 bytes (Prometheus UI landing page)
`GET .../healthz` → 404
`GET .../api/v1/...` → 404 (Prometheus query API unconfigured or blocked)

**Initial observation downgraded after content analysis:**

After enumerating the 90 KB `/metrics` content:
- Only `job="prometheus"` label observed (Prometheus is only scraping itself, not any external targets)
- No `instance=` labels for external scrape targets
- Metric prefixes observed: `go`, `net`, `process`, `prometheus`, `promhttp` — exclusively Prometheus's own internal metrics (Go runtime, HTTP server, scrape engine, build info)
- 173 distinct metric families, all Prometheus self-reporting

**Refined class observation**: this is a **default Prometheus install with no production scrape targets configured**. The `/metrics` endpoint is public-unauth (confirmed), but the metric data exposes only Prometheus's own internal state — no environmental observability data, no internal hostnames, no application-level metrics from the JupyterHub or any other USF service.

The deployment appears to be a **placeholder or never-configured Prometheus** — possibly stood up as a "we should have monitoring" first step that never got past initial install. The Prometheus query API (`/api/v1/query`) returning 404 is consistent with this — the API is reachable only when scrape configs are loaded; with no config, no data, no API.

**This DOWNGRADES the earlier "info-disclosure / scrape targets enumerable" finding**: there are no scrape targets to enumerate. The exposure is "Prometheus is installed here" and "Prometheus version + build info are visible" — both class observations but not material exposure.

**What was NOT done per restraint ethic:**
- Did not attempt to invoke `/api/v1/query` (returned 404 anyway).
- Did not attempt write-API endpoints (e.g., `/api/v1/admin/tsdb/*` — admin API would allow data deletion if exposed; not probed).

---

## Operator attribution (per Insight #4)

- **WHOIS OrgName** for both IPs: University of South Florida
- **Hostname suffix**: `marine.usf.edu` — College of Marine Science subdomain
- **Distinct hosts on adjacent /24 ranges**: 131.247.139.x and 131.247.136.x — typical institutional VLAN slicing

---

## Cross-tool confirmations

| Tool | Output | Notes |
|---|---|---|
| `aimap -ports-class wide` | Surfaced both JupyterHubs + Prometheus on `manglillo` | The wide port profile caught :9090 which `llm-gateway` wouldn't have |
| `visorbishop` | No platform classification (Bishop doesn't have a JupyterHub signature yet) | Gap noted (would need separate Bishop signature work, smaller priority than G5 OW/LiteLLM since JupyterHub already has its own canonical auth model) |
| Direct probes | Both JupyterHubs return 403 on `/hub/api/info`; `manglillo` :9090 `/metrics` returns 200 unauth | |

---

## Notable details

- **Prometheus auth model is "don't expose `/metrics` publicly"** — the standard Prometheus deployment guide explicitly recommends `/metrics` either be reverse-proxied with authentication or bound to a private network. Public `/metrics` is a known info-disclosure class; what's NOT in the metrics is whatever data Prometheus's `/api/v1/query` endpoint could serve (which here returns 404, so the disclosure is limited to `/metrics`'s self-reported state).
- **Co-location pattern**: the same host runs an auth-enforced JupyterHub AND an unauth Prometheus. This suggests the operator considered "JupyterHub is the user-facing service" and forgot or didn't realize Prometheus's `/metrics` endpoint requires the same treatment.
- **Discovery via aimap wave-2**: the Stage-0 dork list had `manglillo` tagged as JupyterHub only; aimap's wide port profile in wave-2 caught the second open port and probed it as Prometheus.
- **No LLM service observed on either host** — these are research-computing JupyterHubs serving the marine science department, not LLM-stack deployments. Included in this survey because the IP ranges hit the Stage-0 `.edu` JupyterHub dorks; observations recorded for completeness of the .edu academic-computing posture picture.

---

## Class-membership summary (no tier labels per survey convention)

- JupyterHub auth-enforced class — OBSERVED on both hosts (data: 403 on `/hub/api/info`)
- Prometheus public-but-empty class — OBSERVED on `manglillo` :9090 (data: 200 + 90 KB body, all metrics are Prometheus self-monitoring; no external scrape targets)
- Prometheus query-API closed class — OBSERVED (data: `/api/v1/*` returns 404)
- Default-install / never-configured-Prometheus class — OBSERVED (no production observability data being collected or exposed)

The earlier characterization of "info-disclosure on adjacent Prometheus" was DOWNGRADED after `/metrics` content analysis — the disclosure surface is Prometheus's own internal state (Go runtime, scrape engine self-metrics, build info), not environmental data about USF's compute fleet.

Data-membership (specific JupyterHub user list — not extracted per restraint) was not enumerated. Prometheus content was enumerated since `/metrics` is the public design-intent endpoint and the data turned out to be uninteresting (Prometheus monitoring itself only).

---

## Discovery method

- **Initial surfacing**: Stage-0 dork-map flagged both marine.usf.edu JupyterHubs (port 8000 + JupyterHub dorks).
- **Verification**: direct `/hub/api/info` probe on both hosts (auth-enforced confirmation); aimap wave-2 with `-ports-class wide` caught the secondary Prometheus exposure on `manglillo`.
- **Probe-time discovery**: `manglillo` :9090 was not in the Stage-0 dork hits — it surfaced because aimap's wide port profile scans all common observability/AI ports and confirmed Prometheus's `/metrics` exposition format.

---

## Source artifacts

- Workspace: `~/recon/edu-llm-infra-2026-05-19/stage2-wave2/`
- aimap wave-2 report: `aimap-wave2.json` (manglillo :9090 entry)
- Direct probe: `wave2-stragglers-and-jupyterhub.json` (USF section)
- Wave-2 findings document: `WAVE2-FINDINGS.md`

---

## Pattern observation — JupyterHub-adjacent observability exposure

USF `manglillo` matches a broader pattern: institutions correctly configure their user-facing JupyterHub with auth, but adjacent services on the same host (Prometheus, Grafana, node-exporter, cAdvisor, etc.) get deployed with default-public posture. Worth a survey lane: enumerate all JupyterHub-confirmed hosts and probe their :9090, :3000, :9100, :8081 etc. for adjacent observability services.
