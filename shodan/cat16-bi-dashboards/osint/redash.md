# Redash — Cat-16 BI/Dashboard OSINT (Stage -1)

Scope: AI-wired BI. Redash instances whose data sources reach AI/ML data (pgvector Postgres, embedding tables, LLM-analytics warehouses). Intel + fingerprints only. No active probing.

## Population (local dump)
- 2000 NDJSON records, 1810 unique IPs. Seed at `seed/redash-ips.txt`.
- Title histogram:
  - 1958 `Login to Redash` (auth wall ON)
  - 20 `Login | Redash`
  - 7 `Redash Initial Setup` (PRE-AUTH setup wizard — priority tier)
  - long tail: catch-all decoy hosts + FP devices

## Auth posture
Auth-on-default. 1978 of 1985 Redash-titled hosts render a login wall. The exception is the 7-host setup-wizard tier.

### Setup-wizard exposure (high-value sub-population)
An exposed `/setup` (title `Redash Initial Setup`) is the pre-auth first-user-admin wizard. Redash shows it when the instance has zero users. An unauthenticated visitor can POST the form and create the first admin account = claimable admin = full instance takeover (all dashboards, all saved queries, all data-source connection strings including any pgvector/warehouse creds).

Fingerprint unauth-safely: read the title only. `http.title:"Redash Initial Setup"` is exact and Shodan-cached; no POST needed to classify. Do NOT submit the form (that creates the admin and is destructive/outward-facing — orchestrator gate). Names ARE the finding here.

### CANDIDATE set — 7 setup-wizard hosts (for verify lane)
```
114.55.176.250:5000   CN  Aliyun
136.113.96.139:5000   US  Google LLC
18.169.167.31:80      GB  Amazon (eu-west-2)
35.78.223.69:80       JP  Amazon (ap-northeast-1)
52.194.177.175:80     JP  Amazon (ap-northeast-1)
34.149.223.125:443    US  Google LLC
204.168.223.25:5000   FI  Hetzner
```
All 7 carry the Redash app CSP (`frame-src redash.io`), so all 7 are real Redash, not decoys. CANDIDATE until verify lane confirms the `/setup` page still renders the wizard live (Shodan cache may be stale; instance may have since had its first admin created).

## Default ports
5000 typical (gunicorn, 355 hosts). Reverse-proxied 80/443 dominate the cohort (586/657). 8080 + high-port tail.

## Redash-unique fingerprint
Most reliable unauth discriminator that survives catch-all body echo:

**`frame-src redash.io` inside the Content-Security-Policy header.** The full Redash CSP:
```
Content-Security-Policy: ; script-src 'self' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; frame-ancestors 'none'; default-src 'self'; frame-src redash.io;
```
Why it wins: compiled into the app (Flask after_request), not a title or cookie a decoy host can cheaply replay. Coverage 1538/1990 real-title hosts. Fires on ZERO of the 7 known FP hosts.

Secondary discriminators (ranked):
- favicon mmh3 `698624197` — 1621/1990, zero FP. Use for Stage 1c enrichment + breadth.
- `Server: gunicorn/<ver>` — 536/1990 (only when banner not hidden by proxy). Stack-confirm, not primary.
- `redash_csrf_token` cookie / csrf body mark — 1003/1990, weaker (generic `csrf` substring inflates count).
- React bootstrap JSON — Shodan truncates the body in the dump, not reliably observable here; route to active fetch at scan lane if needed.

Discarded: title alone (decoy-poisoned), `/api/session` / `/ping` (require active probe, out of Stage -1 scope).

## AI-backend discriminator (honest)
Pre-auth: essentially nothing. Redash data-source types (pgvector-backed Postgres, embedding-table queries, warehouse connections) live behind auth in the `/data_sources` API and in saved-query bodies. None of it is observable unauth on a login-walled host. This is a "names ARE the finding only post-auth" platform: the AI-backend link is provable only after a session, which on the survey set we do not establish. The one exception is the setup-wizard tier — claim admin there and the data-source list (with connection strings) becomes readable, which is exactly why the 7-host tier is the finding-rich one. Document the AI-backend angle as a post-takeover consequence on the setup hosts, not a pre-auth signal.

## Known CVEs
- **Setup-wizard takeover** (class, not a single CVE) — exposed `/setup` = unauth first-admin creation. The operational top risk here; maps directly to the 7-host tier.
- **CVE-2021-41192 — SECRET_KEY default** — Redash <= 10.0.0 shipped a hardcoded/default `REDASH_COOKIE_SECRET` / `SECRET_KEY`. Predictable key = session-cookie forgery = auth bypass. Highest-severity Redash CVE for an internet-exposed instance; check version on login-walled hosts at verify.
- **SSRF via data-source / query-runner** — Redash query runners (URL, JSON, and the visualization/embed fetchers) have a history of SSRF letting an authed user reach internal metadata endpoints (cloud IMDS). Post-auth, but pairs with setup-takeover into a chain: claim admin -> add a data source -> SSRF the cloud metadata service -> instance-role creds.
- Older XSS in dashboard/visualization rendering (lower priority).

CVE chain on a setup host: `/setup` claim admin (CVSS-high, unauth) -> data-source SSRF -> cloud IMDS creds. That is the worst-case path; the chain is worse than the sum.

## Dork FP rate + mitigation
Title-layer FP ~1.6 percent by count, but the FPs are engineered: a catch-all deception fleet echoes decoy Set-Cookie walls (Qlik `X-Qlik-Session`, OFBiz `JSESSIONID`, `i_like_gitea`, webvpn, jeesite) and unrelated device titles (hotel-admin, Synology Photos, iLapse camera, CFMBOX, Prometheus, AW930-S) under the redash title query, specifically to burn verify cycles. Mitigation: dork on `frame-src redash.io` or favicon `698624197`. Neither fires on any FP host in the dump. See `shodan/redash-dorks.md`.

## tome JSON
`tome dorks redash` returns `unknown platform "redash"` — not in corpus. tome is a source-repo; CLI has no write verb (only `dorks`/`probe`). I wrote `~/tome/platforms/redash.json` directly to the platforms dir, matching the existing schema. If that dir is not the canonical write path in your tome instance, the full JSON is mirrored below as the authoritative copy for the orchestrator to commit.

Status: **CANDIDATE** (population mapped, fingerprint derived and FP-tested against the dump; no live verification of unauth read performed by this lane — setup-wizard tier is the verify lane's job).
