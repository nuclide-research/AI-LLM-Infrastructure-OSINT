# Redash Shodan Dorks (Cat-16 BI/Dashboard)

Vendor-unique JSON/header beats title. Title alone catches a deception fleet (see FP note).

## basic
```
http.title:"Login to Redash"
```
Catches the auth-wall cohort. Also catches catch-all decoy hosts that echo the title. Use only as a seed.

## strict (vendor-unique header, survives catch-all body echo)
```
http.html:"frame-src redash.io"
```
The Redash app CSP carries `frame-src redash.io`. Compiled into the app, not a cookie or title a decoy host replays. Zero hits on the 7 known FP hosts in our dump. This is the recommended primary dork.

Header-form variant (HTML-body-only on web UI, route header/JSON forms to Censys):
```
http.html:"script-src 'self' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; frame-ancestors 'none'; default-src 'self'; frame-src redash.io"
```

## setup-wizard sub-population (finding-rich tier)
```
http.title:"Redash Initial Setup"
```
Pre-auth first-user-admin wizard. 7 hosts in our 1810-IP dump. Each one is a claimable-admin candidate: an exposed `/setup` lets an unauthenticated visitor create the first admin account and own the instance. Highest-value tier. Confirm the title is exact (`Redash Initial Setup`, not `Login to Redash`).

Conjunctive hardening (title + app CSP, kills any title-echo decoy):
```
http.title:"Redash Initial Setup" http.html:"frame-src redash.io"
```

## version / favicon
```
http.favicon.hash:698624197
```
Redash favicon mmh3 hash. 1621/1990 of the real-title cohort. Does not appear on any FP host. Pairs well with the CSP dork for breadth.

```
Server:"gunicorn" http.html:"frame-src redash.io"
```
Redash ships on gunicorn (536/1990 expose the banner). Narrows to the canonical self-host stack, drops reverse-proxied 80/443 hosts that hide the gunicorn banner.

## ports
- 5000 (default gunicorn) — 355 hosts
- 80 / 443 (reverse-proxied, nginx/CDN front) — 586 / 657 hosts
- 8080 and assorted high ports — long tail

## FP note (catch-all deception fleet)
`http.title:"Login to Redash"` caught hosts whose `data` blob is a wall of decoy Set-Cookie headers (Qlik `X-Qlik-Session`, OFBiz `JSESSIONID`, Gitea `i_like_gitea`, webvpn, jeesite) plus unrelated titles surfaced under the same query: a Chinese hotel-admin system (合泰软件酒店后台管理系统), Synology Photos, an iLapse camera, CFMBOX, Prometheus, an AW930-S device. These echo strings to poison title/cookie dorks. Mitigation: anchor on `frame-src redash.io` (app-CSP, source-unique) or the favicon hash. Neither fires on any FP host. FP rate at the title layer is low by count (~1.6 percent of cohort) but the decoy hosts are specifically engineered to waste verify-lane cycles, so strip them at the dork.
