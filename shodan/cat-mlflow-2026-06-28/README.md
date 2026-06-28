# Cat-MLflow: MLflow Tracking Server Survey
**Date:** 2026-06-28
**Slug:** cat-mlflow-2026-06-28
**Thesis test:** auth-on-default (auth_default: none)

## Platform
MLflow Tracking Server. ML experiment lifecycle management. Default port 5000.
Auth shipped as opt-in only (MLFLOW_TRACKING_SERVER_AUTH_TYPE); not enforced on default install.
v2.7.0 (2023-09) added optional auth plugin; prior versions = no auth path at all.

## Survey Dorks (from tome)
- basic:   `"mlflow" port:5000`
- strict:  `http.title:"MLflow" port:5000`
- version: `http.title:"MLflow" port:5000 http.html:"version"`
- variant: `http.title:"MLflow" port:8080`
- api:     `http.html:"/api/2.0/mlflow" port:5000`

## Verification Gate
`GET /api/2.0/mlflow/experiments/search` HTTP 200 + JSON with `"experiments"` array = UNAUTH
`GET /api/2.0/mlflow/registered-models/list` HTTP 200 + JSON = UNAUTH (model registry exposed)

## Status
[ ] Stage -1 OSINT Platoon
[ ] Stage 0  Shodan harvest
[ ] Stage 0b Censys
[ ] Stage 0c scanner
[ ] Stage 1a-1d fingerprint chain
[ ] Stage 3v VERIFY
[ ] Stage 12b findings-breakdown.txt
