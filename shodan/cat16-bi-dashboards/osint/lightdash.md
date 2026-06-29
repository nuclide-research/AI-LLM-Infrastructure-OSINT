# Lightdash — Cat-16 BI/Dashboard OSINT (Stage -1)

Status: CANDIDATE. Newer dbt-native OSS BI. No live host probed. Software-default characterization from primary source (GitHub main + docs).

Lightdash now markets as "Agentic BI." Ships LLM AI agents over the dbt semantic layer plus an MCP server. In scope for AI-wired BI.

## Auth posture

Lightdash is a multi-user, organization-scoped app. There is no single-user "auth off" toggle like AnythingLLM. Access to data, projects, charts, and the AI agents is gated behind a session login by default. There is no documented env flag that turns the whole app unauthenticated.

- `ALLOW_SELF_REGISTRATION` does NOT exist in Lightdash. The task's named flag is not in source or docs. Registration is governed differently (see below). Documented honestly: the flag is a non-finding.
- Registration model: the FIRST user to hit a fresh instance creates the org and becomes admin. Primary source `HealthService.ts`:
  `const requiresOrgRegistration = !(await this.organizationModel.hasOrgs());`
  So `requiresOrgRegistration: true` means the instance has ZERO orgs and the next visitor can claim admin by registering. This is the real misconfig class, not a self-registration flag.
- After an org exists, new users join by invite. `ALLOW_MULTIPLE_ORGS=false` (default) means a stranger registering does NOT silently get into the existing org; they would spin up a separate org only if multi-org is enabled. So a live instance with an org already created is invite-only by default.
- `AUTH_DISABLE_PASSWORD_AUTHENTICATION=false` (default) — password login enabled. SSO/OIDC (Google/Okta/Azure AD/OneLogin/generic OIDC) all default `enabled:false`.
- `LIGHTDASH_SECRET` ships as `'not very secret'` in `.env.development` and has NO default in production docs (marked Required, must be fixed between deployments). An operator who copies the dev env into prod runs a known token-signing secret. CANDIDATE misconfig.
- `SECURE_COOKIES=false`, `TRUST_PROXY=false` are the dev defaults. Behind a proxy without flipping these, the session cookie is not marked secure.

### Insight #40 test (auth-on-default rightward shift)

HYPOTHESIS HOLDS, with a sharper framing. Lightdash has NO unauth-by-default whole-app mode. Unlike Superset (admin/admin default creds, historically exposed) and Redash (setup-page claim + known default-secret issues), Lightdash ships auth-mandatory: every data path is behind a session. The only open door is the pre-setup window (`requiresOrgRegistration:true`) where no admin exists yet, which is a transient race, not a standing unauth posture. Predicted population open rate: near-zero for data exposure, low for claimable-admin (only un-set-up instances). A high Superset/Redash open rate against a near-zero Lightdash rate CONFIRMS #40's rightward shift across the BI category. This is the falsification test the orchestrator wants.

## Default ports

- `PORT=8080` (backend listen + docker-compose publishes `8080:8080`). Primary BI surface.
- Almost always reverse-proxied (nginx/traefik/cloud LB) on 80/443 with a hostname.
- `PGPORT=5432` (Postgres metadata store, not the warehouse), `HEADLESS_BROWSER_PORT=3000` (puppeteer for PDF/CSV export), `LIGHTDASH_PROMETHEUS_PORT=9090` (metrics, off by default).
- Dev `SITE_URL` is `http://localhost:3000`; prod requires SITE_URL set to the public host.

## Lightdash-unique fingerprint

BEST UNAUTH FINGERPRINT: `GET /api/v1/health` — HTTP 200, no auth gate, returns a rich JSON blob. The anonymous case is a first-class response: `isAuthenticated:false`. Exact verified shape (from `healthResponse.mock.ts` + `HealthService.ts`, real instance returns live values not mock 0.0.0):

```
{
  "status": "ok",
  "results": {
    "healthy": true,
    "mode": "default" | "demo" | "pr" | "cloud_beta" | "development",
    "version": "<real instance version, e.g. 0.1729.x>",
    "localDbtEnabled": <bool>,
    "isAuthenticated": false,            // anonymous probe
    "requiresOrgRegistration": <bool>,   // true = no org yet = claimable admin
    "latest": { "version": "<dockerhub latest>" },
    "siteUrl": "https://<operator host>",   // ATTRIBUTION LEAK
    "auth": { "disablePasswordAuthentication": <bool>,
              "google": {"enabled": <bool>}, "okta": {...}, "azuread": {...},
              "oidc": {...}, "snowflake": {...}, "databricks": {...} },
    "hasEmailClient": <bool>, "hasSlack": <bool>, "hasGithub": <bool>,
    "hasGitlab": <bool>, "hasHeadlessBrowser": <bool>, "hasMicrosoftTeams": <bool>,
    "embedding": { "enabled": <bool> },
    "ai": { "analyticsProjectUuid": <uuid|null>,
            "analyticsDashboardUuid": <uuid|null>,
            "isAmbientAiEnabled": <bool> }    // AI-WIRED DISCRIMINATOR
  }
}
```

Confirm Lightdash (vs any other app) by the conjunction: HTTP 200 AND JSON has `results.version` AND `results.requiresOrgRegistration` key AND `results.auth.disablePasswordAuthentication` key. No other product emits that field set. This kills the ~50% title-only FP.

Secondary:
- App bootstrap: `<title>Lightdash</title>`, `<div id="root"></div>` (React SPA), `theme-color #394b59`.
- Favicon: `/favicon.ico` (+ `/apple-touch-icon.png`, `/manifest.json`). Hash → Stage 1c jaxen (CANDIDATE, compute on a live host).
- `/api/v1/org` — 401/403 unauth (good negative control: confirms the session gate is real on data routes while /health stays open).
- Session cookie: `connect.sid` (express-session default; CANDIDATE — not pinned to source, may be overridden).

## AI-backend discriminator

Lightdash is dbt + warehouse (BigQuery/Snowflake/Postgres/Databricks/Redshift). AI-wired = AI agents (LLM) answering over the semantic layer + MCP server for Claude/Cursor write-access. Observable UNAUTH:
- `health.results.ai.isAmbientAiEnabled` and the `analyticsProjectUuid`/`analyticsDashboardUuid` fields — the cleanest pre-auth signal that AI agents are turned on. This is the single best AI-wired discriminator in the category.
- `health.results.auth.snowflake.enabled` / `databricks.enabled` hint the warehouse class (embedding/vector tables typically live in Snowflake/BigQuery for AI BI).
- `health.results.embedding.enabled` — embedded-analytics mode (Lightdash's own embed feature, not vector embeddings; do not conflate).
- `siteUrl` is the operator-attribution leak: the operator's real hostname, pre-auth.

Honest limit: project names, dbt model names, warehouse contents, and the actual embedding/vector tables are all BEHIND auth. Pre-auth you learn AI-on/off + warehouse class + host, not the corpus. Consistent with a newer hardened tool.

## CVEs

Two confirmed, both authenticated-only (need editor/admin), both in v0.1024.6, the only CVE-bearing version found:
- CVE-2024-6585 (GHSA-6529-6jv3-66q2) — stored XSS in markdown dashboards + dashboard comments. High, CVSS 8.7. Fixed 0.1042.2. Auth required (Admin/Editor).
- CVE-2024-6586 (GHSA-4h7x-6vxh-7hjf) — SSRF session-takeover via dashboard export; exporting user leaks session token. High, CVSS 7.3. Fixed 0.1027.2. Auth required.

No pre-auth RCE/authz-bypass CVEs found. Main misconfig class is therefore NOT a CVE: it is the `requiresOrgRegistration:true` claimable-admin pre-setup window, plus copied-dev-secret (`LIGHTDASH_SECRET='not very secret'`) and `SECURE_COOKIES=false` behind a proxy.

## Dork FP rate

LOW expected. `/api/v1/health` JSON conjunction is vendor-unique. Title `Lightdash` is a small niche population; the main FP source is the Lightdash marketing site (www.lightdash.com) and doc mirrors, which 404 the `/api/v1/health` JSON contract. Strip with the active-probe conjunction at Stage 0c. Estimated raw-dork FP < 15%, near-0 after the health-JSON confirm.

## tome JSON

Written to `~/tome/platforms/lightdash.json`, status CANDIDATE. tome is a local read-write platform corpus (CLI over `~/tome/platforms/*.json`), not a remote source-repo; the file is the registry entry. Flagged: `tome dorks lightdash` was empty before this survey; after this write, dorks resolve from the JSON. Schema matched against `anythingllm.json`.

## Sources

- https://github.com/lightdash/lightdash (main; "Agentic BI")
- packages/backend/src/services/HealthService/HealthService.ts (requiresOrgRegistration = !hasOrgs(); version=VERSION; isAuthenticated)
- packages/frontend/src/testing/__mocks__/api/healthResponse.mock.ts (exact health JSON shape incl. `ai` block)
- packages/frontend/index.html (title/favicon/root div/theme-color)
- docker-compose.yml (PORT 8080:8080)
- .env.development (AUTH_DISABLE_PASSWORD_AUTHENTICATION=false; LIGHTDASH_SECRET='not very secret'; SECURE_COOKIES=false; ports)
- https://docs.lightdash.com/self-host/customize-deployment/environment-variables (PORT, LIGHTDASH_SECRET, ALLOW_MULTIPLE_ORGS, AUTH_* )
- https://www.lightdash.com/agentic-bi (AI agents + MCP over dbt semantic layer)
- GHSA-6529-6jv3-66q2 / CVE-2024-6585 (XSS); GHSA-4h7x-6vxh-7hjf / CVE-2024-6586 (SSRF)
- [CANDIDATE — NuClide Cat-16 BI-Dashboards Stage -1 OSINT 2026-06-28; software-default, no live host probed]
