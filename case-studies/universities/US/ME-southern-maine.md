# University of Southern Maine: 8-Host JupyterHub Fleet on `cs.usm.maine.edu` — Entomology-Themed Research Cluster, All Auth-Enforced

_NuClide Research · 2026-05-19_

---

## Summary

University of Southern Maine's CS department runs an 8-host JupyterHub fleet on the `cs.usm.maine.edu` subdomain, with hostnames following an entomology theme (wasp, earwig, locust, mosquito, ant, beetle) plus two computing-pioneer-named hosts (turing, pascal). All 8 hosts respond to `/hub/api/info` with HTTP 403 "Missing or invalid credentials" — JupyterHub authentication is correctly enforced fleet-wide. Documented here as an institutional-fleet entry: same operator, same configuration template, properly secured across the deployment.

---

## Infrastructure

| # | Hostname | IP | Theme |
|---|---|---|---|
| 1 | `wasp.cs.usm.maine.edu` | 130.111.131.120 | entomology |
| 2 | `earwig.cs.usm.maine.edu` | 130.111.131.49 | entomology |
| 3 | `locust.cs.usm.maine.edu` | 130.111.131.118 | entomology |
| 4 | `mosquito.cs.usm.maine.edu` | 130.111.131.123 | entomology |
| 5 | `ant.cs.usm.maine.edu` | 130.111.131.124 | entomology |
| 6 | `beetle.cs.usm.maine.edu` | 130.111.131.119 | entomology |
| 7 | `turing.cs.usm.maine.edu` | 130.111.126.97 | computing pioneer |
| 8 | `pascal.cs.usm.maine.edu` | 130.111.126.105 | computing pioneer |

| Field | Value |
|---|---|
| Org | University of Southern Maine (`130.111.0.0/16` UMaine System allocation) |
| Department | Computer Science |
| Network slicing | 6 hosts on `130.111.131.x` (entomology cluster) + 2 hosts on `130.111.126.x` (turing + pascal — possibly a separate older deployment) |
| Service | JupyterHub on port 8000 (all 8 hosts) |
| Auth state | All 8 return 403 on `/hub/api/info` — auth-enforced fleet-wide |

---

## Observations

For each of the 8 hosts, `GET http://<host>:8000/hub/api/info` returned identical HTTP 403 with body `{"status": 403, "message": "Missing or invalid credentials."}`.

The 8-fold uniformity in response indicates a common deployment template and identical auth posture across the fleet. Likely: a single courseware / instruction sysadmin deployed all 8 hosts from the same Ansible/Terraform/Puppet template with consistent JupyterHub configuration.

`GET .../hub/login` returns 200 with the JupyterHub login form rendered (presumably routes to local accounts or an institutional auth backend; not enumerated without authentication).

**What was NOT tested per restraint ethic:**
- No login attempts made.
- No spawner-related endpoints probed (those typically require a valid user session).
- No enumeration of available kernels / Jupyter notebook content (requires auth).

---

## Operator attribution (per Insight #4)

- **WHOIS OrgName**: University of Maine System (UMaine system allocation `130.111.0.0/16` covers both UMaine main campus and Southern Maine)
- **Hostname pattern**: `*.cs.usm.maine.edu` — Computer Science department subdomain at the University of Southern Maine
- **Cross-host pattern**: 6 entomology + 2 computing-pioneer hostnames is a small enough naming convention that it was likely done by a single sysadmin / instructor team

---

## Cross-tool confirmations

- aimap wave-2 (`-ports-class wide`) — surfaced all 8 hosts on port 8000
- Direct `/hub/api/info` probe — verified auth-enforced posture on each host
- aimap-profile — classified all 8 as `education` with CFAA-CSIRT routing flag
- visorbishop — no platform classification (Bishop doesn't have a JupyterHub signature; this is the same gap noted in the USF case study)

---

## Notable details

- **Entomology-themed cluster**: 6 of 8 hosts use insect names (wasp, earwig, locust, mosquito, ant, beetle). The remaining 2 (turing, pascal) follow a computing-pioneer convention. Whether the two naming conventions represent two separate deployment phases or just operator preference variation is not determinable from external probe. The IP range split (131.x vs 126.x) corresponds to this naming split, hinting at two separate VLAN slices.
- **8-host scale** is substantial for a CS department's JupyterHub deployment. Likely backs an institutional courseware experience where each host hosts a different course / lab / project. Or load-balanced multi-host fleet for a single intro-to-data-science class with high concurrency.
- **All auth-enforced**: this is the correct posture and worth noting as a deployment-discipline exemplar. Many of the institutions in this survey have inconsistent posture across hosts (Duke VCM, RIT, UCSB); USM CS appears to have institutional discipline across the 8-host fleet.
- **Same auth backend across the fleet**: identical 403 response shape suggests a centralized auth config — possibly a USM CS LDAP / SSO that all 8 hosts trust.

---

## Class-membership summary (no tier labels per survey convention)

- JupyterHub auth-enforced class — OBSERVED on all 8 hosts (data: 403 on `/hub/api/info` × 8)
- Fleet-wide consistent-deployment-template class — OBSERVED
- Entomology-themed naming convention — OBSERVED
- 2-tier VLAN slicing (.131 vs .126) — OBSERVED

Data-membership (specific user accounts, specific notebooks, specific compute resources) not enumerated per restraint ethic.

---

## Discovery method

- **Initial surfacing**: Stage-0 dork-map of 1,629 verified Shodan dorks scoped to `hostname:.edu` — all 8 hosts hit the JupyterHub port + login-marker dorks.
- **Verification**: direct `/hub/api/info` probe on each host confirmed identical auth-enforced response.

---

## Source artifacts

- Workspace: `~/recon/edu-llm-infra-2026-05-19/stage2-wave2/`
- Direct probes (all 8 hosts): `wave2-stragglers-and-jupyterhub.json` (USM-* entries)
- aimap wave-2: `aimap-wave2.json`

---

## Pattern observation — institutional deployment discipline

USM's 8-host fleet is an exemplar of consistent institutional-deployment discipline. Each host has identical posture (auth-enforced JupyterHub on the same port). Contrast with multi-host deployments at other institutions in this survey:

- **Duke**: VCM-managed VMs with inconsistent per-VM posture (some signup-open, some auth-on, depending on individual VM owner)
- **RIT**: 4 prior + 2 new hosts across multiple departments with different postures per host
- **DePaul**: 20+ port-3000 hosts on residential/wireless networks with mixed exposure (most are student dev work, not Open WebUI)

USM CS appears to have institutional control over the cluster, suggesting it's a department-managed instructional resource rather than user-spawned. Worth tracking as a positive-example pattern for fleet-management discipline.
