# Cat-16 BI/Dashboards - Shodan Query Log

Scope: AI-wired BI only. Date: 2026-06-28. Session: authed web-UI in-page fetch.

| dork | total | harvested | note |
|---|---|---|---|
| `http.html:"frame-src redash.io"` | None | 0 | ZERO - http.html: multi-token not web-UI indexed, route to Censys |
| `http.title:"Redash Initial Setup"` | 20 | 20 |  |
| `http.html:"data-bootstrap" "Apache Superset"` | 1,659 | 190 |  |
| `http.title:"Metabase" http.html:"metabase.SESSION"` | None | 0 | ZERO - http.html: multi-token not web-UI indexed, route to Censys |
| `http.favicon.hash:698624197` | 4,304 | 184 | favicon fallback |
| `product:"Metabase"` | 21,710 | 170 |  |

## Step 0b Censys (2026-06-28)

| query | result | note |
|---|---|---|
| `host.services.http.response.html_title="Login to Redash"` | 422 insufficient balance | search-feature bucket exhausted (view shows 100, search separately metered). BLOCKED not skipped. |

CT-log delta unavailable this cycle. Redash-CSP + metabase.SESSION body signals route to Step 0c scanner (live banner reads them direct, no index staleness).
