# Apache Superset — Shodan dorks (Cat-16)

Vendor-unique over title. Title-only is FP-polluted (squatters: Udio Superset, Red Digital, MSI Superset, Proxmox/camera hash-collisions). All tiers conjoin a vendor token.

Dump-derived expected counts are from the local 2000-record sample, not live Shodan. Treat as relative magnitude, not a live hit count.

## basic (broad population)

```
http.html:"data-bootstrap"
```
- Coverage: ~80% of real Superset in dump (1594/2000). Vendor-unique FAB bootstrap blob.
- FP class: collides with other Flask-AppBuilder apps that embed `data-bootstrap` (rare; Airflow uses a different bootstrap shape). Low. Strip residue with the `/static/appbuilder/` co-signal if needed.

Alt basic (broadest, accept FP for population estimate):
```
http.title:"Superset"
```
- FP class: brand squatters (~3-5%) + html-hash-collision noise (~18%, anything-llm bucket + cameras/gateways). DO NOT use alone for a finding set; population estimate only.

## strict (Superset-confirmed, vendor-unique)

```
"Apache Superset:" "Version:"
```
- Matches the multi-line `Apache Superset:` response-header version block. 754/2000 in dump. Zero squatter collision — this string is emitted only by the real product header.
- FP class: effectively none. The trade is coverage (~38% of real hosts emit the header; the rest are reverse-proxied and strip it).

Conjunctive strict (best precision+recall balance):
```
http.html:"data-bootstrap" "Apache Superset"
```
- FP class: near-zero. Bootstrap blob AND product header.

## version (CVE-2023-27524 scoping)

```
"Apache Superset:" "Version: 2.0.1"
```
```
"Apache Superset:" "Version: 2.0.0"
```
```
"Apache Superset:" "Version: 1."
```
```
"Apache Superset:" "Version: 0."
```
- Selects the default-SECRET_KEY auth-bypass cohort (<= 2.0.1). Dump cohort: 2.0.1=16, 2.0.0=3, plus all 1.x / 0.x builds.
- FP class: none on the version string itself. Caveat: a host on a newer Version banner can STILL be vulnerable if it overrode the default-key boot refusal — version dork UNDER-counts the true CVE-2023-27524 population. Verify lane confirms by forge+replay, not by version alone.

Favicon-pivot (Stage 1c enrichment, not a primary dork):
```
http.favicon.hash:1582430156
```
- Canonical Superset favicon. 735/2000 in dump. Use to pull reverse-proxied hosts that strip the version header but keep the favicon. FP class: squatters that reuse the real favicon share the hash; rebranded ones drop out.

AI-backend scope note: there is NO passive dork for AI-wiring. `http.html:"embedding"` / `http.html:"llm"` are FALSE POSITIVES (UI copy + anything-llm hash-collision noise). AI-backend is a verify-lane `/api/v1/database/` read, not a Shodan dork.

Dork count written: 7 primary (1 basic + 1 alt-basic + 2 strict + 4 version + 1 favicon-pivot = effectively 9 query forms across tiers).
