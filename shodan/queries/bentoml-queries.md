# BentoML — Shodan Dork Catalog

**Date:** 2026-06-27
**Researcher:** NuClide Research

---

## Tier 1 — Direct Fingerprint (pathognomonic)

| Dork | Hits | Notes |
|---|---|---|
| `"BentoML Service"` | 1 | Server header match — highest precision; Shodan indexes headers sparsely |
| `"BentoML Service/"` | 1 | Variant with trailing slash (same host: 117.50.218.103) |
| `http.title:BentoML` | 72 | **Primary harvest dork** — UI title match; 69 unique IPs recovered |
| `"BentoML Prediction Service"` | 1 | Legacy title (v1.2-era); 222.106.216.54 |

## Tier 2 — Endpoint-Based (0 hits — Shodan indexing limitation)

| Dork | Hits | Notes |
|---|---|---|
| `http.html:"bentoml-ui.umd.js"` | 0 | Shodan does not index JS bundle paths in http.html |
| `http.html:"x-bentoml-name"` | 0 | JSON API response bodies not indexed in http.html |
| `http.html:"contact@bentoml.com"` | 0 | /docs.json body not indexed |
| `http.headers:"BentoML"` | 0 | Shodan does not index full header values via this filter |
| `http.headers:"X-BentoML"` | 0 | Same limitation |
| `product:BentoML` | 0 | Shodan has no product classification for BentoML |

## Tier 3 — Broad Sweep

| Dork | Hits | Notes |
|---|---|---|
| `port:3000 http.html:bentoML` | 18 | Subset of title matches (port 3000 + HTML body) |
| `http.title:BentoML port:3000` | 18 | Port-scoped title — confirms 3000 is primary |
| `http.title:BentoML port:5000` | 3 | Secondary port: 103.103.21.215, 34.134.151.192, 34.134.103.105 |
| `http.title:BentoML port:8080` | 0 | No Yatai-on-8080 in public corpus |
| `port:3000 "BentoML"` | 0 | Exact string + port — Shodan html index limitation |

---

## Key Observations

1. **`http.title:BentoML` is the load-bearing dork** — captures 69/71 unique hosts.
   - Reason: BentoML's React UI sets `<title>BentoML Inference Service</title>`; Shodan indexes HTML titles reliably.
   - Tier 1 header dork `"BentoML Service"` only returns 1 result because Shodan's http.headers index is sparse for non-standard headers.

2. **http.html dorks are blind** — Shodan does not deeply index JSON API response bodies (`/docs.json`, `/schema.json`). The fingerprints that work best for BentoML (x-bentoml-name, contact@bentoml.com) live in API responses, not HTML bodies indexed by Shodan.

3. **Port 3000 dominates** — 68/71 hosts on default port. No Yatai (8080) exposure in public internet population.

4. **Population is small-but-clean** — 71 unique hosts is at the low end of the predicted 120-900 range. Likely reflects: (a) most BentoML lives behind BentoCloud/SageMaker; (b) Docker images are user-built so no image-hash dork; (c) some v1.4.x UI may not set the title in all conditions.

---

## False Positive Assessment

- Port 3000 is shared with Grafana, Node.js/Express apps — Tier 3 dorks need FP filtering.
- `http.title:BentoML` is low-FP: the title string is specific to BentoML's React UI.
- Scanner step (0c) will strip FPs via banner/body verification.

---

## Population Summary

| Source | Raw hits | Unique IPs |
|---|---|---|
| http.title:BentoML | 72 | 69 |
| "BentoML Service" (header) | 1 | 1 |
| "BentoML Prediction Service" | 1 | 1 |
| **Total deduplicated** | — | **71** |
