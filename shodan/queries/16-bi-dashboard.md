# 16. BI / Dashboard / Visualization

_Section created: 2026-05-08_

Self-hosted analytics frontends co-deployed with AI/ML stacks to surface model performance, training metrics, and inference telemetry. Auth posture: T2 by default, but setup-wizard bypass (Metabase CVE-2023-38646), anonymous-access misconfiguration (Grafana), and default-credential failures (Superset `admin/general`) are common enough that population-scale surveys still yield unauth findings.

**CVE watch:**
- `CVE-2023-38646` — Metabase pre-auth RCE via JDBC injection through active setup wizard. `"has-user-setup": false` in `/api/session/properties` = exploitable.
- `CVE-2023-27524` — Apache Superset predictable `SECRET_KEY` → forged session cookie → auth bypass. Affects < 2.1.0.
- `CVE-2021-43798` — Grafana path-traversal arbitrary file read via `/public/plugins/<id>/../../../`. Affects 8.0.0–8.3.0.

---

## Metabase

| Shodan Query | Notes |
|---|---|
| `http.title:"Metabase"` | Broadest; all instances regardless of port |
| `http.title:"Metabase" port:3000` | Default port scope |
| `http.title:"Metabase" port:80` | HTTP on port 80 (reverse-proxied) |
| `http.title:"Metabase" port:443` | HTTPS instances |
| `http.title:"Metabase" port:8080` | Alt port |
| `http.title:"Metabase" port:8443` | Alt HTTPS |
| `http.title:"Metabase" -port:443` | Non-HTTPS only; higher misconfiguration probability |
| `http.html:"Metabase" port:3000` | HTML-scoped; catches custom titles |
| `http.html:"metabase" port:3000` | Lowercase HTML form |
| `http.html:"/api/session/properties"` | Metabase-specific API path in bundled JS; very high precision |
| `http.html:"/api/session/properties" port:3000` | Above + default port |
| `http.html:"metabase_session"` | Session cookie name appears in JS source |
| `http.html:"metabase/frontend"` | JS bundle path |
| `http.html:"metabase" http.html:"setup"` | Instances with setup flow visible in HTML |
| `"Metabase"` | Bare-string; searches all indexed text |
| `"Metabase" port:3000` | Bare-string on default port |
| `"Metabase" port:80` | Bare-string on port 80 |
| `http.favicon.hash:-1776938843` | Metabase favicon hash; survives title/config changes |
| `http.favicon.hash:-1776938843 port:3000` | Favicon + default port |
| `http.favicon.hash:-1776938843 -port:443` | Favicon, non-HTTPS |
| `ssl.cert.subject.cn:"metabase"` | TLS cert CN contains "metabase"; operator-named instances |
| `ssl.cert.subject.cn:"metabase" port:443` | Above + HTTPS |
| `hostname:"metabase"` | rDNS contains "metabase" |
| `hostname:"metabase" port:3000` | rDNS + default port |
| `http.title:"Metabase" country:US` | US-scoped |
| `http.title:"Metabase" country:DE` | Germany (Hetzner-heavy) |
| `http.title:"Metabase" country:SG` | Singapore (high SE-Asia AI deployment density) |
| `http.title:"Metabase" country:BR` | Brazil |
| `http.title:"Metabase" country:IN` | India |
| `http.title:"Metabase" org:"amazon"` | AWS-hosted |
| `http.title:"Metabase" org:"google"` | GCP-hosted |
| `http.title:"Metabase" org:"microsoft"` | Azure-hosted |
| `http.title:"Metabase" org:"hetzner"` | Hetzner (German budget cloud, high AI-stack density) |
| `http.title:"Metabase" org:"digitalocean"` | DigitalOcean |
| `http.title:"Metabase" org:"ovh"` | OVH |
| `http.title:"Metabase" org:"university"` | Academic networks |
| `http.title:"Metabase" org:"hospital"` | Healthcare operators — highest-impact data class |
| `http.title:"Metabase" http.status:200` | HTTP 200 only; filters login-redirect variants |
| `product:"Metabase"` | Shodan service fingerprint (when detected) |

---

## Apache Superset

| Shodan Query | Notes |
|---|---|
| `http.title:"Superset"` | Broadest |
| `http.title:"Superset" port:8088` | Default port; cleanest signal (8088 near-unique to Superset) |
| `http.title:"Superset" port:80` | Reverse-proxied |
| `http.title:"Superset" port:443` | HTTPS |
| `http.title:"Superset" port:8080` | Alt port |
| `http.title:"Superset" -port:443` | Non-HTTPS |
| `http.title:"Apache Superset"` | Full-name title form |
| `http.title:"Apache Superset" port:8088` | Full-name + default port |
| `http.html:"superset" port:8088` | Lowercase HTML form on default port |
| `http.html:"Apache Superset" port:8088` | Full-name HTML + default port |
| `http.html:"apache_superset"` | Underscore form (Python package/JS var) |
| `http.html:"apache_superset" port:8088` | Above + default port |
| `http.html:"superset_load_chart"` | Superset JS function name; high precision |
| `http.html:"superset-frontend"` | Frontend bundle identifier |
| `http.html:"SUPERSET_WEBSERVER_PORT"` | Env var appears in some deployment HTML pages |
| `"Superset" port:8088` | Bare-string on default port |
| `"Apache Superset"` | Full-name bare-string |
| `"Apache Superset" port:8088` | Full-name bare-string + default port |
| `ssl.cert.subject.cn:"superset"` | TLS cert CN |
| `ssl.cert.subject.cn:"superset" port:443` | Above + HTTPS |
| `hostname:"superset"` | rDNS pattern |
| `hostname:"superset" port:8088` | rDNS + default port |
| `http.title:"Superset" country:US` | US-scoped |
| `http.title:"Superset" country:CN` | China (Alibaba/Tencent deployments) |
| `http.title:"Superset" country:DE` | Germany |
| `http.title:"Superset" country:IN` | India |
| `http.title:"Superset" country:BR` | Brazil |
| `http.title:"Superset" org:"amazon"` | AWS |
| `http.title:"Superset" org:"google"` | GCP |
| `http.title:"Superset" org:"microsoft"` | Azure |
| `http.title:"Superset" org:"alibaba"` | Alibaba Cloud |
| `http.title:"Superset" org:"hetzner"` | Hetzner |
| `http.title:"Superset" org:"university"` | Academic |
| `http.title:"Superset" http.status:200` | 200 OK only |
| `port:8088 http.html:"dashboard"` | Port-scoped BI sweep; higher false-positive rate |
| `port:8088 "Superset"` | Bare-string on unique port; broad |

---

## Redash

| Shodan Query | Notes |
|---|---|
| `http.title:"Redash"` | Broadest |
| `http.title:"Redash" port:5000` | Default port |
| `http.title:"Redash" port:80` | Reverse-proxied |
| `http.title:"Redash" port:443` | HTTPS |
| `http.title:"Redash" port:8080` | Alt port |
| `http.title:"Redash" -port:443` | Non-HTTPS |
| `http.html:"redash" port:5000` | Lowercase HTML on default port |
| `http.html:"Redash" port:5000` | Capitalized HTML on default port |
| `http.html:"/api/data_sources"` | Redash data-source API path in JS; high precision |
| `http.html:"/api/queries"` | Redash queries API path |
| `http.html:"redash-app"` | JS bundle identifier |
| `http.html:"REDASH_" port:5000` | Env var prefix in config/HTML; operator-exposed config |
| `"Redash" port:5000` | Bare-string on default port |
| `"Redash"` | Bare-string broadest |
| `http.favicon.hash:1471491032` | Redash favicon; survives customization |
| `http.favicon.hash:1471491032 port:5000` | Favicon + default port |
| `http.favicon.hash:1471491032 -port:443` | Favicon, non-HTTPS |
| `ssl.cert.subject.cn:"redash"` | TLS cert CN |
| `ssl.cert.subject.cn:"redash" port:443` | Above + HTTPS |
| `hostname:"redash"` | rDNS pattern |
| `hostname:"redash" port:5000` | rDNS + default port |
| `http.title:"Redash" country:US` | US-scoped |
| `http.title:"Redash" country:IL` | Israel (Redash was built at Wix; high Israeli SaaS adoption) |
| `http.title:"Redash" country:DE` | Germany |
| `http.title:"Redash" country:JP` | Japan |
| `http.title:"Redash" country:IN` | India |
| `http.title:"Redash" org:"amazon"` | AWS |
| `http.title:"Redash" org:"google"` | GCP |
| `http.title:"Redash" org:"microsoft"` | Azure |
| `http.title:"Redash" org:"hetzner"` | Hetzner |
| `http.title:"Redash" org:"digitalocean"` | DigitalOcean |
| `http.title:"Redash" http.status:200` | 200 OK only |
| `product:"Redash"` | Shodan service fingerprint (when detected) |

---

## Grafana (unauth-focused)

| Shodan Query | Notes |
|---|---|
| `http.title:"Grafana"` | Broadest; very high volume |
| `http.title:"Grafana" port:3000` | Default port |
| `http.title:"Grafana" port:80` | Reverse-proxied |
| `http.title:"Grafana" port:443` | HTTPS |
| `http.title:"Grafana" port:8080` | Alt port |
| `http.title:"Grafana" -port:443` | Non-HTTPS; higher misconfiguration probability |
| `http.title:"Grafana" port:3000 -port:443` | Default port, non-HTTPS |
| `http.title:"Grafana" http.html:"anonymous"` | Anonymous access enabled; dashboards readable without login |
| `http.title:"Grafana" http.html:"Anonymous"` | Capitalized form of above |
| `http.title:"Grafana" http.html:"viewer"` | Viewer role string in HTML |
| `http.title:"Grafana" http.html:"datasources"` | Data-source routes in HTML; `/api/datasources` may leak creds |
| `http.title:"Grafana" http.html:"data-sources"` | Hyphenated form |
| `http.title:"Grafana" http.html:"alerting"` | Alert-rule routes in HTML |
| `http.html:"grafana" port:3000` | Lowercase HTML on default port |
| `product:"Grafana"` | Shodan service fingerprint |
| `product:"Grafana" port:3000` | Service fingerprint + default port |
| `product:"Grafana" -port:443` | Service fingerprint, non-HTTPS |
| `http.component:"Grafana"` | Shodan component detection |
| `"Grafana" port:3000` | Bare-string on default port |
| `"Grafana"` | Bare-string broadest |
| `http.favicon.hash:1185022786` | Grafana favicon hash |
| `http.favicon.hash:1185022786 port:3000` | Favicon + default port |
| `http.favicon.hash:1185022786 -port:443` | Favicon, non-HTTPS |
| `ssl.cert.subject.cn:"grafana"` | TLS cert CN |
| `hostname:"grafana"` | rDNS pattern |
| `hostname:"grafana" port:3000` | rDNS + default port |
| `http.title:"Grafana" country:US` | US-scoped |
| `http.title:"Grafana" country:DE` | Germany |
| `http.title:"Grafana" country:CN` | China |
| `http.title:"Grafana" country:IN` | India |
| `http.title:"Grafana" country:JP` | Japan |
| `http.title:"Grafana" country:BR` | Brazil |
| `http.title:"Grafana" org:"amazon"` | AWS |
| `http.title:"Grafana" org:"google"` | GCP |
| `http.title:"Grafana" org:"microsoft"` | Azure |
| `http.title:"Grafana" org:"hetzner"` | Hetzner |
| `http.title:"Grafana" org:"digitalocean"` | DigitalOcean |
| `http.title:"Grafana" org:"ovh"` | OVH |
| `http.title:"Grafana" org:"linode"` | Linode/Akamai |
| `http.title:"Grafana" org:"university"` | Academic networks |
| `http.title:"Grafana" org:"hospital"` | Healthcare |
| `http.title:"Grafana" http.status:200` | 200 OK only; filters redirect-to-login |
| `http.title:"Grafana" http.html:"anonymous" country:US` | US anonymous-access instances |
| `http.title:"Grafana" http.html:"anonymous" org:"university"` | Academic anonymous Grafana |

---

## Combined / cross-platform

| Shodan Query | Notes |
|---|---|
| `(http.title:"Metabase" OR http.title:"Superset" OR http.title:"Redash" OR http.title:"Grafana")` | Full BI sweep |
| `(http.title:"Metabase" OR http.title:"Grafana") port:3000` | Port-3000 collision pair |
| `(http.title:"Metabase" OR http.title:"Grafana") port:3000 -port:443` | Above, non-HTTPS |
| `(http.title:"Metabase" OR http.title:"Grafana") port:3000 http.status:200` | Above, 200 only |
| `port:8088 (http.title:"Superset" OR http.html:"Superset")` | Superset unique-port sweep |
| `(http.title:"Metabase" OR http.title:"Superset" OR http.title:"Redash" OR http.title:"Grafana") org:"university"` | Academic BI sweep |
| `(http.title:"Metabase" OR http.title:"Superset" OR http.title:"Redash" OR http.title:"Grafana") org:"hospital"` | Healthcare BI sweep |
| `(http.title:"Metabase" OR http.title:"Superset" OR http.title:"Redash" OR http.title:"Grafana") org:"hetzner"` | Hetzner BI sweep |
| `(http.title:"Metabase" OR http.title:"Superset" OR http.title:"Redash" OR http.title:"Grafana") country:US org:"amazon"` | AWS US BI sweep |
| `(http.title:"Metabase" OR http.title:"Superset" OR http.title:"Redash") -http.title:"Grafana"` | BI without Grafana noise |
| `(http.favicon.hash:-1776938843 OR http.favicon.hash:1471491032 OR http.favicon.hash:1185022786)` | Multi-platform favicon sweep |
| `(ssl.cert.subject.cn:"metabase" OR ssl.cert.subject.cn:"superset" OR ssl.cert.subject.cn:"redash" OR ssl.cert.subject.cn:"grafana")` | TLS cert sweep across all four |
| `(hostname:"metabase" OR hostname:"superset" OR hostname:"redash" OR hostname:"grafana")` | rDNS sweep across all four |
| `(hostname:"metabase" OR hostname:"superset" OR hostname:"redash" OR hostname:"grafana") -port:443` | rDNS sweep, non-HTTPS |
