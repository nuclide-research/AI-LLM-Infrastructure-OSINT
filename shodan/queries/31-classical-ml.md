# 31 — Classical ML & Auxiliary Model Services

_Recommenders / ranking / fraud-anomaly. NARROW scope (purpose-built only; excludes generic model-servers). Intel: `data/platform-intel/classical-ml-osint-2026-05-31.md`. Survey: 2026-05-31._

Dork status legend: ⏳ candidate (not yet run) · ✓ run (hit count recorded) · ✗ zero (lesson noted).

## Dork catalog (run via Playwright web UI; log every executed dork to query-log.md)

| # | Platform | Dork | FP-risk | Status | Hits |
|---|---|---|---|:---:|---|
| 1 | Gorse | `http.title:"Gorse Dashboard"` | LOW | ⏳ | |
| 2 | Gorse | `http.html:"Gorse Dashboard" http.html:"fontawesome.com/releases/v7.0.0"` | LOW | ⏳ | |
| 3 | Gorse | `port:8087 http.html:"/api/health/live"` | MED | ⏳ | |
| 4 | Vespa-q | `http.html:"\"coverage\"" http.html:"\"documents\"" http.html:"\"degraded\"" port:8080` | MED | ⏳ | |
| 5 | Vespa-q | `http.html:"/document/v1/" http.html:"pathId"` | LOW-MED | ⏳ | |
| 6 | TF-Serving | `port:8501 http.html:"model_version_status"` | LOW | ⏳ | |
| 7 | TF-Serving | `http.html:"Could not find any versions of model"` | LOW | ⏳ | |
| 8 | django-river-ml | `http.html:"models" port:8000 "django"` | MED | ⏳ | |
| 9 | Solr-LTR | `http.html:"schema/feature-store"` | LOW | ⏳ | |
| 10 | Solr-LTR | `http.html:"ManagedFeatureStore"` | MED | ⏳ | |
| 11 | ES-LTR | `http.html:".ltrstore"` | LOW | ⏳ | |
| 12 | ES-LTR | `http.html:"_ltr" http.html:"featureset" port:9200` | LOW-MED | ⏳ | |
| 13 | Cornac | `port:8080 http.html:"remove_seen"` | MED | ⏳ | |
| 14 | Marble | `"yente" "motiva" port:8080` | LOW-MED | ⏳ | |
| 15 | VW daemon | `port:26542` | HIGH (seed only) | ⏳ | |

## FP traps (do not re-run blind)
- `ssl:`/cert dorks BLIND this category — Gorse/Cornac/TF-Serving default plain-HTTP + loopback; exposed tier is containerized `0.0.0.0`. Use port + body-JSON dorks.
- Metarank: generic `:8080`, no brand body. aimap-primary, Shodan-thin. Seed from Redis-6379 co-location, not a title dork.
- VW daemon: `port:26542` returns empty banner (no connect-time data). Seed only; classify with zgrab2 full-handshake (newline-terminated VW example line), not Shodan.
- Cornac/TF-Serving richest tokens (`remove_seen`, `tensorflow/serving/predict`) live in query-path bodies Shodan won't auto-crawl — expect thin passive counts, confirm with aimap.

## Verification primitives (auth-state, not identity)
- Gorse: `GET /api/dashboard/userinfo` → body `null` = unauth dashboard open.
- Vespa-q: `GET /search/?yql=select * from sources * where true;&hits=1` → `root.coverage.documents>0` = populated readable corpus.
- Metarank: `POST /train/{m}` → JSON w/ `features`,`iterations`,`sizeBytes` = unauth weight read.
- TF-Serving: `GET /v1/models/{m}/metadata` → `model_spec`+`tensorflow/serving/predict`.
- django-river-ml: `GET /api/models` → top-level `models` array.
- Cornac: `GET /recommend?uid=1&k=1` → `recommendations`+nested `query.uid`.
- Solr-LTR: `GET /solr/{c}/schema/feature-store` → `managedList`.
- ES-LTR: `GET /_ltr/_featureset` → feature-set list.
