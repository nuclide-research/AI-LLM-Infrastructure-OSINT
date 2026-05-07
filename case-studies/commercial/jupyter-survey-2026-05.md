# Jupyter Notebook / JupyterHub on Public Cloud & University Networks: Auth Posture Survey

_NuClide Research · 2026-05-03_

---

## Summary

Two-phase sweep targeting port 8888 across cloud-hosting providers and university research networks. **Zero unauthenticated Jupyter instances found** in either population. JupyterHub's mandatory login and Jupyter Notebook's token-auth defaults are universally adopted in both deployment contexts.

---

## Methodology

**Phase 1, Cloud ranges (DO/Hetzner/Vultr):**
```
masscan -iL <28 cloud /16 CIDRs> -p 8888 --rate 6000
  → 10,524 live hosts on :8888

Fingerprint: curl -L /  → title contains "Jupyter"
  → 0 confirmed Jupyter (all hits: Adminer, Chronograf, Spring Boot)
```

**Phase 2, University research networks:**
```
masscan -iL <26 university /16 CIDRs> -p 8888 --rate 3000
  → 1,259 live hosts on :8888

Fingerprint: HTTP 302 redirect + curl -L / → title "Jupyter Server" or "Jupyter Notebook"
  → 18 confirmed Jupyter instances

Auth check: GET /api/kernels (no auth header)
  → 18/18 returned 403 {"message":"Forbidden"}
```

**Fingerprinting lesson:** Port 8888 is heavily shared. `/api/kernelspecs` with substring match `-ms '"kernelspecs"'` produced high false-positive rates (Adminer serves `kernels?file=` in links; Spring Boot Config Server reflects path segments into `"profiles"` array). Title-based detection (`"Jupyter"` in `<title>`) after following 302 redirects is the reliable filter.

---

## Confirmed University Instances (18, all protected)

| IP | Institution | Country | Auth State |
|---|---|---|---|
| 128.32.173.82 | UC Berkeley (AS25) | US | 403 JupyterHub |
| 128.32.246.65 | UC Berkeley (AS25) | US | 403 JupyterHub |
| 129.132.31.137 | ETH Zurich / SWITCH (AS559) | CH | 403 JupyterHub |
| 131.111.88.195 | University of Cambridge, Neurosurgery (AS786) | UK | 403 JupyterHub |
| 140.112.90.79 | National Taiwan University, CSIE (AS17716) | TW | 403 JupyterHub |
| 140.112.21.12 | National Taiwan University, EE (AS17716) | TW | 403 JupyterHub |
| 140.112.156.28 | National Taiwan University (AS17716) | TW | 403 JupyterHub |
| 165.246.43.214 | INHA University (AS9317) | KR | 403 JupyterHub |
| 165.246.43.222 | INHA University (AS9317) | KR | 403 JupyterHub |
| 165.246.149.63 | INHA University (AS9317) | KR | 403 JupyterHub |
| 140.119.81.90 | TANet / NCCU (AS1659) | TW | 403 JupyterHub |
| 140.119.162.16 | TANet / NCCU, chairmtchi.cs.nccu.edu.tw (AS1659) | TW | 403 JupyterHub |
| 140.119.164.19 | TANet / NCCU, cglab.cs.nccu.edu.tw (AS1659) | TW | 403 JupyterHub |
| 140.119.163.219 | TANet / NCCU, v100x4.cs.nccu.edu.tw (AS1659) | TW | 403 JupyterHub |
| 175.45.203.51 | NAVER Business Platform (AS135354) | KR | 403 JupyterHub |
| 210.125.101.156 | Korea Telecom (AS4766) | KR | 403 JupyterHub |
| 210.125.100.224 | Korea Telecom (AS4766) | KR | 403 JupyterHub |
| 210.125.93.241 | Korea Telecom (AS4766) | KR | 403 JupyterHub |

All 18 returned `{"message":"Forbidden","reason":null}`, JupyterHub XSRF protection active on the API layer.

---

## Platform Posture Comparison (Cloud DO/Hetzner/Vultr)

| Platform | Confirmed | Unauth | Notes |
|----------|-----------|--------|-------|
| Flowise | 43 | 0 (0%) | Post-CVE-2024-36420 hygiene |
| n8n | 1,006 | 0 (0%) | Mandatory auth since v0.166.0 |
| Jupyter | 18 (univ) | 0 (0%) | JupyterHub login + token-auth defaults |
| **Qdrant** | **61** | **61 (100%)** | Auth off by default, no change |
| **Elasticsearch** | **42** | **42 (100%)** | 7.x default-no-auth still common |

**Pattern:** Orchestration and compute tools have hardened. Data layer tools (vector DBs, search engines) remain default-open.

---

## Why Jupyter Was High Priority

An unauthenticated Jupyter instance is full remote code execution, POST to `/api/kernels` creates a kernel, then `POST /api/kernels/{id}/channels` over WebSocket executes arbitrary Python in the server's context. In university environments this means:

- Access to GPU compute allocated to the server
- Research data in the working directory (datasets, model outputs, credentials in notebooks)
- Lateral movement onto the research network
- Potential access to HPC cluster submission endpoints (SLURM, PBS) callable from notebook

The 0% unauth finding indicates JupyterHub deployment (with PAM/LDAP auth) has become standard at the universities surveyed.

---

## Discoverer

NuClide Research, nicholas@nuclide-research.com

No data was accessed. Auth check was a single unauthenticated GET to `/api/kernels`; response code only.
