# Cat-16 Tooling Debt

## tome corpus rebuild (RESOLVED for Cat-16)
- 4 new platform JSONs written: superset, redash, metabase, lightdash (all CANDIDATE).
- `go install` rebuilt the CLI; `tome dorks <platform>` now serves all 4 strict dorks. Verified 2026-06-28.

## tome corpus schema drift (PRE-EXISTING, NOT ours, deferred)
`tome list` errors on these platform JSONs (unmarshal failures, older debt):
- autogen-studio: `vulnerabilities` is object, struct wants string
- clawdbot: `vulnerabilities` object vs string
- continue-dev, dynamoai, enkryptai: `sources` object vs string
Single-platform `dorks`/`probe` lookups still work; only `list` (walks all files) chokes.
ACTION: dedicated tome-maintenance pass to reconcile Platform struct vs richer nested JSONs. Out of Cat-16 scope.

## Step 0d aimap fingerprint coverage (RESOLVED, 3/4)
aimap 1.9.55 already has working fingerprints:
- Superset (7 refs), Redash (4 refs), Metabase (5 refs, probes /api/session/properties = CVE-2023-38646 surface)
- Lightdash: 0 refs = NO fingerprint. DEFERRED: 0 confirmed-live targets in population, so no value building it now.
  Build when a Lightdash population surfaces. tome JSON exists for scaffold.
No FP-build needed this survey. aimap natively version-scopes the 126 Metabase candidates.
