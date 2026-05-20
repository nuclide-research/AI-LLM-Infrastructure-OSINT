# University of Chicago: Two-Host Observation — Streamlit on `helabserver0` (auth-on framework) + JupyterHub on `jupyterhub-dev.grid` (502 Bad Gateway / degraded)

_NuClide Research · 2026-05-19_

---

## Summary

The University of Chicago surfaces two distinct hosts in this survey: `helabserver0.uchicago.edu` running a Streamlit application on port 8501, and `jupyterhub-dev.grid.uchicago.edu` running JupyterHub on port 8000. The Streamlit host has framework-confirmed deployment with default title; the JupyterHub host returns HTTP 502 Bad Gateway, indicating the service is degraded / not serving requests.

---

## Hosts

### Host A — `helabserver0.uchicago.edu` (Streamlit)

| Field | Value |
|---|---|
| IP | 128.135.10.23 |
| rDNS | `helabserver0.uchicago.edu` |
| Org | University of Chicago (`128.135.0.0/16` UChicago allocation) |
| Hostname semantics | `helabserver0` — "He Lab" server 0 (possibly a faculty lab named "He" — common surname in academic faculty; or HE = High-Energy / Helium / etc., context-dependent) |
| Open port observed | 8501 (Streamlit default port) |

#### Observations

`GET http://helabserver0.uchicago.edu:8501/_stcore/health` → 200 with body `ok`.
`GET .../` → 200 with 891 bytes — Streamlit React shell (older bundle naming).
HTML `<title>`: `Streamlit` (default).
JS bundle: `/static/js/main.dbbac55a.js` (older `main.*.js` naming).

**Class observed**: Streamlit framework with default title and older bundle. Same observation state as the wave-2 Streamlit cohort (GSU, Stanford, UW).

### Host B — `jupyterhub-dev.grid.uchicago.edu` (JupyterHub, degraded)

| Field | Value |
|---|---|
| IP | 128.135.20.141 |
| rDNS | `jupyterhub-dev.grid.uchicago.edu` |
| Org | University of Chicago |
| Hostname semantics | `jupyterhub-dev` on the `grid.uchicago.edu` subdomain — explicit DEV (non-production) JupyterHub deployment within UChicago's Computing Grid / Open Science Grid affiliated infrastructure |
| Open port observed | 8000 (JupyterHub default port) |
| Service state | **HTTP 502 Bad Gateway** — service is responding but the backend / spawner is failing |

#### Observations

`GET http://jupyterhub-dev.grid.uchicago.edu:8000/hub/api/info` → 502 Bad Gateway
`GET .../hub/login` → 502 Bad Gateway
`GET .../` → 502 Bad Gateway

Response body: minimal HTML error page (`<html><head><title>502 Bad Gateway</title></head><body><center><h1>502 Bad...`).

**Class observed**: degraded service. The JupyterHub frontend is reachable on port 8000 (the proxy is up) but the backend / spawner / hub process is not responding. Either:
1. The JupyterHub backend is down (process not running or crashed)
2. The hub-to-spawner network path is broken
3. The deployment is mid-deployment or maintenance

This host is not in an auth-bypass-able state because there's nothing answering behind the gateway — even an authenticated request would return 502.

---

## Operator attribution (per Insight #4)

- **Org**: University of Chicago (per ARIN registration of `128.135.0.0/16`)
- **Host A subdomain**: `helabserver0.uchicago.edu` — main university domain, suggests a faculty/lab host (no department subdomain)
- **Host B subdomain**: `jupyterhub-dev.grid.uchicago.edu` — Computing Grid subdomain. `grid.uchicago.edu` is associated with UChicago's involvement in the Open Science Grid (OSG) consortium, providing distributed computing for high-energy physics, astronomy, and similar fields.

---

## Cross-tool confirmations

- aimap wave-2 (`-ports-class wide`) — surfaced both hosts on their respective ports
- Direct probes — confirmed Streamlit framework on Host A; confirmed 502 degraded state on Host B
- visorbishop — no platform classification (Bishop doesn't have JupyterHub or Streamlit signatures)

---

## Class-membership summary (no tier labels per survey convention)

- **Host A**: Streamlit framework deployment on UChicago — OBSERVED; default title, auth state unknown (per the wave-2 Streamlit observation discipline)
- **Host B**: JupyterHub-degraded class — OBSERVED; service is in 502 state and not actively serving; no auth-bypass / exposure surface because nothing is functional behind the gateway

Data-membership (specific user accounts on either host, specific notebooks/apps, specific compute resources) not enumerated per restraint ethic.

---

## Discovery method

- **Initial surfacing**: Stage-0 dork-map of 1,629 verified Shodan dorks — both hosts matched their respective framework dorks (Streamlit + JupyterHub).
- **Verification**: direct probes confirmed Host A's Streamlit framework + Host B's 502 degraded state.

---

## Source artifacts

- Workspace: `~/recon/edu-llm-infra-2026-05-19/stage2-wave2/`
- Direct probes: `wave2-stragglers-and-jupyterhub.json` (Chicago-Grid section) + `wave2-streamlit-and-stragglers-deep.json` (UChicago-helab section)
- aimap wave-2: `aimap-wave2.json`

---

## Notable details

- **`grid.uchicago.edu` subdomain** indicates UChicago Computing Grid (OSG) — research-computing infrastructure with national-scale partnerships. The "dev" prefix on `jupyterhub-dev` suggests a non-production environment, consistent with the 502 state being acceptable operational behavior rather than a security incident.
- **Two-host pattern at UChicago** shows the institution has multiple LLM/research-compute services with different operational states. Worth a follow-up `hostname:uchicago.edu` Shodan sweep to enumerate the broader fleet.
