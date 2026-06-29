# Cat-16 BI/Dashboards — Stage 3v Verified Findings

Date: 2026-06-29. All entries below = 200-with-data confirmed. Restraint observed throughout.

## CRITICAL: Metabase CVE-2023-38646 Pre-Auth RCE Surface

CVSS 9.8. Pre-auth RCE via H2 JDBC injection through exposed setup token.
Fixed in 0.46.6.1 / 1.46.6.1. Restraint: setup-token presence = surface confirmed. JDBC payload NOT fired.

### Confirmed (token present + vulnerable version):
| host | port | version | setup_token |
|---|---|---|---|
| 198.58.115.254 | 3000 | v0.45.3 | [REDACTED] |

### Version-vulnerable (token consumed, setup complete, auth required):
| host | version | note |
|---|---|---|
| 139.59.228.73 | v0.37.8 | configured, login-wall; RCE surface closed |
| 167.99.126.142 | v0.41.6 | configured |
| 184.34.52.134 | v0.40.2 | configured |
| 3.17.106.43 | v0.41.5 | configured |
| 34.101.41.222 | v0.38.0 | configured |
| 34.232.170.175 | v0.41.5 | configured |
| 35.236.204.120 | v0.37.6 | configured |
| 44.215.56.71 | v0.39.4 | configured |
| 5.161.77.244 | v0.44.5 | configured |
| 52.200.138.124 | v0.38.6 | configured |
| 54.164.138.2 | v0.46.2 | configured |
| 54.81.106.137 | v0.41.0 | configured |
| 91.121.39.95 | v0.41.4 | configured |

Note: 13 version-vulnerable instances with login-wall = not in CVE-2023-38646 RCE scope
(token required; however these remain on EOL versions with other vuln exposure).

## HIGH: Redash Claimable Admin (unauthenticated first-admin setup)

All 14 confirm: HTTP 200 redirect terminates at /setup, CSP frame-src=redash.io.
Finding: unauthenticated visitor can create the first admin account = full instance takeover.
Restraint: GET /setup only. No POST. Form render = finding.

| host | port | proto | final_url |
|---|---|---|---|
| 13.114.94.90 | 80 | http | http://13.114.94.90/setup |
| 141.98.199.66 | 5000 | http | http://141.98.199.66:5000/setup |
| 147.139.174.41 | 5000 | http | http://147.139.174.41:5000/setup |
| 151.106.41.4 | 5000 | http | http://151.106.41.4:5000/setup |
| 18.169.167.31 | 80 | http | http://18.169.167.31/setup |
| 34.146.65.22 | 5000 | http | http://34.146.65.22:5000/setup |
| 34.34.217.74 | 5000 | http | http://34.34.217.74:5000/setup |
| 35.76.81.200 | 80 | http | http://35.76.81.200/setup |
| 35.78.223.69 | 80 | http | http://35.78.223.69/setup |
| 54.175.242.57 | 80 | http | http://54.175.242.57/setup |
| 13.159.122.214 | 443 | https | https://13.159.122.214:443/setup |
| 18.176.25.64 | 443 | https | https://18.176.25.64/setup |
| 35.74.226.223 | 443 | https | https://35.74.226.223:443/setup |
| 54.210.52.34 | 443 | https | https://54.210.52.34/setup |

## HIGH: Metabase Claimable Admin (setup wizard, patched version)

From aimap priority run. v0.58.6.1 = post-CVE-2023-38646-fix, but setup wizard active = claimable admin.

| host | port | version | note |
|---|---|---|---|
| 3.136.52.120 | 80 | v0.58.6.1 | setup wizard active; NOT RCE path (patched); admin account creatable |

## Measurement notes

- 15 CVE candidates -> 1 confirmed CRITICAL (token present + vulnerable) + 13 configured (setup complete) + 1 unreachable
- 14 Redash setup candidates -> 14/14 confirmed HIGH (100% rate on CSP-gated dork population)
- Lightdash = 0 hosts confirmed in population (negative thesis result, codified)
- Full Superset auth-state (612 hosts) pending aimap full run
