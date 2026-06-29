# Metabase - Shodan dorks (Cat-16 BI/Dashboard)

Status: CANDIDATE. Derived from vendor-unique fields, no live-host validation yet. Hand-derived (tome had no metabase entry; `tome dorks metabase` returned empty).

Web-UI body-only caveat: `http.html:` and `http.headers:` match HTML/header body on the Shodan web UI. JSON-body signals (`/api/session/properties`) are NOT directly dorkable on Shodan; they are the VERIFY-lane confirmation, not the harvest dork. The strict tier keys on the `metabase.SESSION` cookie (a real HTTP response header Shodan indexes) and the title - both body/header-indexed.

---

## basic (population sweep, moderate FP)

```
http.title:"Metabase"
```
Catches self-hosted instances and Metabase Cloud login pages. FP from mirrors/marketing. Use only as the upper-bound population estimate; strip with strict tier.

Alt basic:
```
http.html:"Metabase"
```
Higher FP (substring). Logged as a population ceiling, not a candidate list.

---

## strict (vendor-unique, low FP)

Key on the Metabase session cookie - emitted in `Set-Cookie` on the login/redirect response, indexed by Shodan, and unique to Metabase:

```
http.title:"Metabase" http.html:"metabase.SESSION"
```

Cookie-only variant (cuts title-spoof mirrors):
```
"Set-Cookie: metabase.SESSION"
```

SPA-asset variant - Metabase serves a hashed app bundle and a known favicon; the login page embeds `window.MetabaseBootstrap` / `MetabaseRoot`:
```
http.title:"Metabase" http.html:"MetabaseBootstrap"
```

Anti-FP rule: a true Metabase answers `GET /api/session/properties` with JSON containing `setup-token`, `has-sample-database`, and `version.tag`. Verify lane confirms; the strict dork just narrows.

---

## version (CVE-2023-38646 scoping, pre-0.46.6.1 / 1.46.6.1)

Shodan does not index the JSON `version.tag`, so version-scoping at the dork layer is coarse. Combine title + port and defer precise version to `/api/session/properties` at verify:

```
http.title:"Metabase" port:3000
```

Reverse-proxied variant (most production):
```
http.title:"Metabase" port:443
```

Self-hosted-only (drop Metabase Cloud SaaS, which is patched and out of scope):
```
http.title:"Metabase" -hostname:metabaseapp.com -ssl.cert.subject.cn:"*.metabaseapp.com"
```

Version verdict is earned at verify: pull `version.tag` from `/api/session/properties`; tag `< 0.46.6.1` (OSS) or `< 1.46.6.1` (Ent), accounting for the back-port lines (0.45.4.1, 0.44.7.1, 0.43.7.2 and 1.x equivalents) = unpatched pre-auth-RCE candidate. A non-null `setup-token` on ANY version = leak vector live.

---

## AI-backend candidate narrowing (Cat-16 scope)

No Shodan dork distinguishes pgvector - it is invisible at the engine layer (rides inside a normal Postgres connection). AI-wired confirmation is a verify-lane schema/name read (`/api/database`, card/question names with `embedding`/`vector`/`llm`/`rag`). Stage -1 hands the verify lane the strict-tier live cohort plus the rule: Postgres engine present + AI-shaped table/question names = in-scope.

---

## Dork count

6 distinct dorks across 3 tiers (basic x2, strict x3, version x3 listed; counting unique non-overlapping forms: basic 1 + alt 1, strict 3, version 3 = 8 dork lines, 3 tiers). Strict tier is the load-bearing low-FP set keyed on `metabase.SESSION`.

Sources: same as osint/metabase.md.
