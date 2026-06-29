# Metabase - Cat-16 BI/Dashboard OSINT (Stage -1)

Status: CANDIDATE. Software-default characterization. No live host probed in this squad. Cold greenfield, no local seed dump.

Scope: AI-wired BI. Metabase instances whose backend connects to AI/ML data - pgvector Postgres, LLM-analytics warehouses, embedding result tables.

Vendor: Metabase (Metabase, Inc.). OSS `0.x` line, Enterprise/Pro `1.x` line. Clojure + React. Repo github.com/metabase/metabase.

---

## Auth posture

Metabase ships an unconfigured setup flow on first boot. A fresh, never-initialized instance walks through `/setup`. The setup flow is gated by a single-use `setup-token` minted at boot. That token is the whole problem.

Auth states:
- **Unconfigured** - no admin yet. `setup-token` is live and leaked unauth. Pre-auth RCE surface (CVE-2023-38646).
- **Configured** - admin created, `setup-token` cleared (returns null). Login wall at `/auth/login`. Session cookie `metabase.SESSION`.

The headline issue is not weak passwords. It is that an unconfigured or unpatched instance leaks the setup token to anyone, and the token drives a database-add path that reaches RCE.

auth_default: `setup-flow-token-gated` (token leaks unauth pre-config; CVE-class pre-auth RCE on unpatched).

---

## Default ports

- **3000** - Jetty default (`MB_JETTY_PORT=3000`). The typical exposed port.
- Reverse-proxied behind 80/443 (nginx/Caddy/Traefik) in most production deployments. Expect a fronting proxy more often than bare 3000.
- 8080 occasionally when run behind an app server convention.

---

## Metabase-unique fingerprint - `/api/session/properties`

This single unauth GET is the fingerprint AND the version source AND the AI-backend discriminator AND the pre-auth-RCE token leak. One call does all four jobs.

`GET /api/session/properties` returns a large unauthenticated JSON settings blob. No session required. Key fields:

- `"version"` object - `"version.tag"` (e.g. `"v0.48.1"`), `"version.date"`, `"version.hash"`. This is the authoritative version source. Beats banner guessing.
- `"setup-token"` - a UUID string on an **unconfigured** instance, `null` once an admin exists. Non-null setup-token = pre-auth RCE candidate (the CVE-2023-38646 leak vector, confirmed against Assetnote research and NVD).
- `"has-sample-database"` - boolean. `true` means the bundled H2 sample DB is present. The H2 sample DB (`zip:/app/metabase.jar!/sample-database.db`) is the pivot surface the public exploit uses to avoid corrupting production data during the JDBC-injection RCE. `true` here = the exploit's preferred target DB is available.
- `"engines"` - a map of every database driver the instance can connect to (postgres, mysql, bigquery, snowflake, redshift, h2, mongo, etc.). This is the AI-backend discriminator (see below).
- `"available-locales"`, `"site-name"` (often operator-attributing), `"google-auth-client-id"`, `"saml-enabled"`, `"ldap-enabled"`, `"premium-features"` (1.x Enterprise tell), `"application-name"`/`"application-logo-url"` (custom branding = named tenant).

Why this is gold: it is unauth, it is verbatim-vendor JSON (no other product emits this exact key set), and it self-discloses version, config state, and backend driver universe in one read. A blog mirror or reverse-proxied marketing page 404s this route. A real Metabase answers it.

Liveness/identity null-cost tell: `GET /api/health` returns `{"status":"ok"}` on a live instance.

---

## AI-backend discriminator (the Cat-16 scope filter)

Metabase itself is not AI. The scope is Metabase wired to an AI/ML backend. Discriminators, least-to-most intrusive:

1. **`engines` map in `/api/session/properties`** (unauth) - tells you which driver families are *available*, not which are *configured*. `postgres` present = pgvector is possible (pgvector rides inside a normal Postgres connection; Metabase has no distinct pgvector driver). Weak signal alone.
2. **`/api/database`** (auth-gated; verify lane only) - the configured database list. Each entry's `engine`, `name`, and `details.dbname`. pgvector shows as `engine: "postgres"`. The discriminator is the **dataset/question/table names**, not the driver.
3. **Name-based AI tells** in cards/questions/collections (auth or via a leaked session): table or question names containing `embedding`, `embeddings`, `vector`, `pgvector`, `cosine`, `similarity`, `llm`, `rag`, `chunks`, `inference`, `model_runs`, `completions`. A Postgres connection feeding a Metabase dashboard whose questions query `embeddings` or `vector` columns = in-scope AI-wired BI.
4. **`details.dbname`/host hints** pointing at known vector/warehouse stacks (e.g. a `bigquery`/`snowflake`/`databricks` engine with an `*_embeddings` dataset; a `clickhouse` engine over LLM-analytics).

Key point: pgvector is invisible at the engine layer. The AI-backend confirmation is a **schema/name read**, which is the verify lane's job (auth-gated). Stage -1 flags candidates by Postgres-present + AI-shaped names.

---

## CVEs

**CVE-2023-38646 - pre-auth RCE (the big one).** CVSS 9.8 (AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H). Verified against NVD + Assetnote primary research.

Chain:
1. Unauth `GET /api/session/properties` (or the index/login HTML, which embeds the same JSON) leaks the `"setup-token"` UUID.
2. Unauth `POST /api/setup/validate` with that token. Body carries a nested `"details"` object; the load-bearing field is `details.db` - a JDBC connection string.
3. The H2 driver path is abused: not the blocked `INIT` param, but `TRACE_LEVEL_SYSTEM_OUT=1` plus stacked SQL to dodge keyword filters, then `CREATE TRIGGER ... AS $$//javascript ...$$` to execute JavaScript inside H2's trigger syntax = arbitrary command exec at server privilege. The public exploit targets `zip:/app/metabase.jar!/sample-database.db` (the H2 sample DB) to avoid corrupting production.

Affected (verbatim from NVD):
- OSS: `< 0.43.7.2`; `0.44.0`-`0.44.7.1` (excl); `0.45.0`-`0.45.4.1` (excl); `0.46.0`-`0.46.6.1` (excl).
- Enterprise: `< 1.43.7.2`; `1.44.0`-`1.44.7.1` (excl); `1.45.0`-`1.45.4.1` (excl); `1.46.0`-`1.46.6.1` (excl).

Fixed: **0.46.6.1 / 1.46.6.1** (and back-ports 0.45.4.1/1.45.4.1, 0.44.7.1/1.44.7.1, 0.43.7.2/1.43.7.2).

Version-tier verdict from `/api/session/properties` `version.tag`: any tag below the fixed line = unpatched pre-auth-RCE candidate. A live non-null `setup-token` on any version = the leak vector is already exposed.

**CVE-2023-39752** - pre-auth info disclosure / null-pointer DoS class on the same setup surface (companion to 38646).

**CVE-2021-41277** - local file inclusion via the custom GeoJSON map-URL feature (`/api/geojson`), pre-auth read of local files / SSRF. Fixed 0.40.5 / 1.40.5.

**Session/JWT note:** Metabase uses an opaque `metabase.SESSION` cookie by default (not a JWT). JWT enters via the Enterprise embedding/SSO feature (signed embedding params + JWT SSO). Embedding JWT secret leakage and unsigned/`alg:none` embedding-token mishandling are the JWT-class risks; they live on `1.x` Enterprise with embedding enabled (`enable-embedding` true in properties). Not a default-instance issue.

---

## Dork FP rate

Expected moderate-to-high FP on the basic tier. Reasons:
- `metabase` appears in unrelated product names, GitHub mirrors, doc sites, and as a substring (`metabasic`, metadata tooling).
- `http.title:Metabase` is clean-ish but proxied marketing/embed pages and the public Metabase Cloud login (`*.metabaseapp.com`) inflate counts with non-self-hosted, non-in-scope hosts.
- The `metabase.SESSION` cookie and the `/api/session/properties` JSON signature are near-zero-FP: no other product emits `setup-token` + `has-sample-database` + `version.tag` together.

Strip rule: confirm with the `/api/session/properties` JSON contract at the verify lane. Basic-title hits that 404 the properties route are FPs. Strict/version tiers below are built to cut this at the dork layer.

---

## Sources

- https://nvd.nist.gov/vuln/detail/CVE-2023-38646 (affected/fixed versions, CVSS 9.8)
- https://www.assetnote.io/resources/research/chaining-our-way-to-pre-auth-rce-in-metabase-cve-2023-38646 (setup-token leak via /api/session/properties; details.db JDBC; H2 TRACE_LEVEL trigger RCE)
- https://www.metabase.com/docs/latest/security (setup-token, session model)
- https://github.com/metabase/metabase (engines, /api/session/properties, /api/setup/validate, /api/database)
- https://nvd.nist.gov/vuln/detail/CVE-2021-41277 (GeoJSON LFI/SSRF)
- [CANDIDATE - NuClide Cat-16 BI/Dashboard Stage -1 OSINT, Metabase squad, 2026-06-28; software-default characterization, no live host probed]
