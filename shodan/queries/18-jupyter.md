# 18. Jupyter Notebook / JupyterHub

_Section created: 2026-05-09_

Port 8888 is heavily shared (Adminer, Chronograf, Spring Boot Config Server). Title-based detection after following 302 redirects is the reliable signal — substring matching on API paths produces high false-positive rates. JupyterHub has mandatory login by default since v1.x and universally enforces auth at `/api/kernels`; the primary survey use-case is inventory and version disclosure rather than unauth access. JupyterLab on developer VPS boxes (direct `jupyter lab --ip 0.0.0.0` invocations without `--no-browser` or a proxy) remains the primary unauth exposure surface.

**Survey result (2026-05-03):** 10,524 port-8888 hits across 28 cloud /16 ranges → 0 unauth Jupyter instances. 18 confirmed JupyterHub at university ranges, 18/18 auth-gated. Auth-on-default thesis holds. Unauth Jupyter at population scale is CVE-era (pre-2019 token-auth default); modern deployments are consistently locked.

**CVE watch:**
- `CVE-2019-10255` — JupyterLab/Notebook < 5.7.8: open redirect; combined with XSRF token bypass enables session-token theft.
- `CVE-2022-24757` — Jupyter Server < 1.15.4: open redirect.
- `CVE-2024-35048` — JupyterHub < 4.1.0: SSRF via hub-login redirect parameter.
- `CVE-2026-33709` — JupyterHub 1.5–4.0.x pre-CVE-2024-35048 patch: auth bypass on `/hub/api/` when using `LocalAuthenticator` + specific PAM config (confirmed in NuClide NCSU + UIC disclosures 2026-05-06).

---

## Jupyter Notebook / JupyterLab (standalone)

| Shodan Query | Notes |
|---|---|
| `http.title:"Jupyter"` | Broadest; Notebook + Lab + Hub |
| `http.title:"Jupyter" port:8888` | Default port |
| `http.title:"JupyterLab"` | Lab-specific title |
| `http.title:"JupyterLab" port:8888` | Lab on default port |
| `http.title:"Jupyter Notebook"` | Notebook classic |
| `http.title:"Jupyter Notebook" port:8888` | Notebook on default port |
| `http.title:"Jupyter Server"` | Server-mode (newer) |
| `http.title:"Jupyter Server" port:8888` | Server on default port |
| `http.html:"jupyter" port:8888` | HTML-scoped lowercase |
| `http.html:"/api/kernels"` | Jupyter-specific API path in page source |
| `http.html:"/api/kernelspecs"` | Kernelspecs path; high-recall with FP risk |
| `http.html:"jupyter-lab" port:8888` | JS bundle identifier |
| `http.html:"jupyter_notebook_config"` | Config reference in error pages |
| `"Jupyter" port:8888` | Bare-string on default port |
| `"JupyterLab" port:8888` | Bare-string Lab |
| `http.favicon.hash:963937823` | Jupyter favicon hash |
| `http.favicon.hash:963937823 port:8888` | Favicon + default port |
| `ssl.cert.subject.cn:"jupyter"` | TLS cert CN |
| `hostname:"jupyter" port:8888` | rDNS pattern |
| `http.title:"Jupyter" -port:443` | Non-HTTPS; higher direct-exposure probability |
| `http.title:"JupyterLab" -port:443` | Lab non-HTTPS |
| `http.title:"Jupyter" org:"university"` | Academic networks |
| `http.title:"Jupyter" org:"amazon"` | AWS-hosted |
| `http.title:"Jupyter" org:"hetzner"` | Hetzner |
| `http.title:"Jupyter" org:"digitalocean"` | DigitalOcean |
| `http.title:"Jupyter" country:US` | US-scoped |
| `http.title:"Jupyter" country:CN` | China |
| `http.title:"Jupyter" country:DE` | Germany |
| `http.title:"Jupyter" country:IN` | India |
| `http.title:"Jupyter" country:TW` | Taiwan (high university density found in survey) |
| `http.title:"Jupyter" country:KR` | Korea |

---

## JupyterHub

| Shodan Query | Notes |
|---|---|
| `http.title:"JupyterHub"` | Hub login page; broadest |
| `http.title:"JupyterHub" port:8000` | Default Hub port (8000, not 8888) |
| `http.title:"JupyterHub" port:80` | Reverse-proxied |
| `http.title:"JupyterHub" port:443` | HTTPS |
| `http.title:"JupyterHub" port:8888` | Alt port |
| `http.html:"jupyterhub"` | HTML-scoped |
| `http.html:"jupyterhub" port:8000` | Hub HTML on default port |
| `http.html:"/hub/login"` | Hub login path in source |
| `http.html:"/hub/api/"` | Hub API path; high precision |
| `http.html:"xsrf_token" port:8000` | XSRF token in Hub page source |
| `"JupyterHub" port:8000` | Bare-string on default port |
| `"JupyterHub"` | Bare-string broadest |
| `ssl.cert.subject.cn:"jupyterhub"` | TLS cert CN |
| `hostname:"jupyterhub"` | rDNS pattern |
| `http.title:"JupyterHub" org:"university"` | Academic (primary deployment context) |
| `http.title:"JupyterHub" org:"amazon"` | AWS-hosted Hub |
| `http.title:"JupyterHub" org:"google"` | GCP-hosted Hub |
| `http.title:"JupyterHub" country:US` | US academic sweep |
| `http.title:"JupyterHub" country:TW` | Taiwan (TANET density) |
| `http.title:"JupyterHub" country:KR` | Korea |
| `http.title:"JupyterHub" country:DE` | Germany |
| `http.title:"JupyterHub" http.html:"version"` | Version disclosure in page source |

---

## Version-specific (CVE targeting)

| Shodan Query | Notes |
|---|---|
| `http.html:"jupyterhub" http.html:"1.5"` | Hub 1.5.x range (CVE-2026-33709 window) |
| `http.html:"jupyterhub" http.html:"2.0"` | Hub 2.0.x range |
| `http.html:"jupyterhub" http.html:"3."` | Hub 3.x range |
| `http.html:"jupyterhub" http.html:"4.0"` | Hub 4.0.x (pre-4.1 CVE-2024-35048) |
| `http.html:"jupyter" http.html:"token"` | Token-auth in page source (Notebook older mode) |

---

## Combined

| Shodan Query | Notes |
|---|---|
| `(http.title:"JupyterHub" OR http.title:"JupyterLab" OR http.title:"Jupyter Notebook")` | Full Jupyter sweep |
| `(http.title:"JupyterHub" OR http.title:"JupyterLab") port:8000` | Hub + Lab on port 8000 |
| `(http.title:"Jupyter" OR http.html:"/api/kernels") -port:443` | Non-HTTPS Jupyter instances |
| `(http.title:"JupyterHub" OR http.title:"JupyterLab") org:"university"` | Academic sweep |
| `(hostname:"jupyter" OR ssl.cert.subject.cn:"jupyter")` | rDNS + TLS sweep |
| `(http.title:"JupyterHub" OR http.title:"JupyterLab" OR http.title:"Jupyter Notebook") org:"hetzner"` | Hetzner sweep |
| `(http.title:"JupyterHub" OR http.title:"JupyterLab") country:TW org:"tanet"` | TANET (Taiwan research network) sweep |
