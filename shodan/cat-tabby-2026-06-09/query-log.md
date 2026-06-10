# Cat-Tabby Shodan query log — 2026-06-09

Per feedback-shodan-query-log: every executed dork logged with hit count. Zero = result.

| # | Tier | Dork | Count | Notes |
|---|---|---|---|---|
| 1 | Tabby basic | `port:8080 "Tabby"` | 2 | |
| 2 | Tabby strict | `port:8080 http.html:"Tabby" http.html:"AI coding"` | 3 | |
| 3 | Tabby version | `port:8080 http.html:"Tabby" http.html:"swagger-ui"` | 0 | |
| 4 | Sourcegraph basic | `http.title:"Sourcegraph"` | 32 | |
| 5 | Sourcegraph strict | `http.html:"/.api/graphql" http.title:"Sourcegraph"` | 0 | |
| 6 | Sourcegraph version | `http.html:"productVersion" http.html:"/.assets/scripts/"` | 0 | |
| variant | Tabby-alt | `port:8081 "Tabby"` | 0 | |
| variant | Tabby-server-hdr | `product:"tabby-server"` | 0 | |
| variant | Tabby-uvicorn | `http.html:"Tabby" http.html:"uvicorn"` | 0 | |
| variant | Tabby-tabby-server | `http.html:"tabby-server"` | 0 | |
| variant | Tabby-bare | `"tabby-server"` | 0 | |
| variant | Tabby-favicon | `http.favicon.hash:0 "Tabby"` | 0 | |
| variant | Tabby-v1-health | `http.html:"/v1/health" http.html:"webserver"` | 0 | |
| variant | Tabby-HealthState | `"HealthState"` | 0 | |
| variant | Tabby-tabbyml | `"tabbyml"` | 0 | |
| variant | SG-graphql | `"/.api/graphql"` | 278 | |
| variant | SG-port-7080 | `port:7080 "Sourcegraph"` | 0 | |
| variant | SG-port-3080 | `port:3080 "Sourcegraph"` | 0 | |
| variant | SG-source-text | `http.html:"sourcegraph" -http.title:"Sourcegraph"` | 248 | |
| variant | SG-Cody | `"Cody" "Sourcegraph"` | 0 | |
| variant | SG-Caddy | `"sourcegraph" "Caddy"` | 4 | |
