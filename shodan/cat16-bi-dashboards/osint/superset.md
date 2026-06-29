# Apache Superset — Cat-16 BI/Dashboard OSINT (Stage -1)

Squad: Apache Superset. Scope: AI-wired BI only (Superset backed by AI/ML data — vector-DB result tables, LLM-analytics, embedding stores). Intel + fingerprints only. No live host probed in this task.

Local dump basis: `~/AI-LLM-Infrastructure-OSINT/superset.json.gz` (NDJSON, 2000 records sampled, 1178 unique IPs). Numbers below are from that dump, not live probes.

## Auth posture

Superset ships a login wall. Flask-AppBuilder (FAB) renders `/login/` and gates the app by default. Auth is ON by default in a clean install. The exposure is not "no login form," it is the default `SECRET_KEY`.

- **Default state (4.x / 5.x):** login wall present. `AUTH_TYPE = AUTH_DB`. A first-run admin is created by `superset fab create-admin` (operator picks the password; the docker-compose quickstart hardcodes `admin/admin`).
- **The real hole — CVE-2023-27524.** Superset <= 2.0.1 shipped a documented default `SECRET_KEY = '\2\1thisismyscretkey\1\2\\e\\y\\y\\h'`. Flask signs the session cookie with that key. An attacker who knows the key forges a session for `user_id=1` (the bootstrap admin) and walks straight past the login wall. Auth "on by default," defeated by a known signing key. Later versions refuse to boot on the default key, but operators override that check and many never rotate.
- **Dump evidence of the footprint:** 847 banners carry `Set-Cookie: session=...` whose decoded payload is exactly `{"_user_id":1,"user_id":1}`. That is the server handing out a user_id=1 session in the unauthenticated landing response. On a default-`SECRET_KEY` host that cookie is forgeable; on a rotated host it is an opaque anon token. The cookie alone is not proof of compromise — it is the surface. Verify lane earns the finding by forging+replaying against a version-pinned host.
- **default_creds:** `admin/admin` from the canonical `docker-compose` / Helm quickstart (`ADMIN_PASSWORD`, `SUPERSET_ADMIN_PASSWORD`). Opt-in to change; frequently shipped as-is on "internal" boxes that are internet-reachable.

auth_default classification: **login-wall-default-on**, but **default-SECRET_KEY-forgeable** on the <=2.0.1 / override cohort.

## Default ports

- 8088 — canonical Superset / gunicorn dev+compose default.
- 80 / 443 — reverse-proxied production (dominant in the dump: 443=475, 80=217 of the sample). 8088 itself rare in Shodan because most real deploys sit behind nginx.
- 8080, 8090, 5000 — secondary observed binds.

## Superset-unique fingerprint signals (ranked)

Title is FP-prone (see FP section). Rank by unauth-distinguishability:

1. **`data-bootstrap` HTML attribute — BEST unauth fingerprint.** The unauth landing/login page embeds `<... data-bootstrap="{&#34;common&#34;: {&#34;conf&#34;: {&#34;SUPERSET_WEBSERVER_TIMEOUT&#34;...`. Present in 1594/2000 dump records (~80%). This is the FAB+Superset bootstrap blob; the JSON keys `SUPERSET_WEBSERVER_TIMEOUT`, `SUPERSET_DASHBOARD_POSITION_DATA_LIMIT` are vendor-unique and do not collide with the title-squatters. CONFIRMED in dump.
2. **`Apache Superset:` response-header version block — BEST for version/CVE scoping.** 754 records emit a multi-line header:
   ```
   Apache Superset:
     Node Version Range: ^20.16.0
     NPM Version Range: ^10.8.1
     Version: 5.0.0
     Name: superset
   ```
   Exact `Version:` string. Drives CVE-2023-27524 cohort selection (Version <= 2.0.1). CONFIRMED in dump. Note Shodan indexes this as a flattened header key `apache superset` (754 hits) — that is the dork hook.
3. **`/static/appbuilder/` asset path** — 1958/2000 records reference it (FAB static mount). Very high coverage, slightly lower specificity (any FAB app emits `/static/appbuilder/`, e.g. Airflow, but combined with `data-bootstrap` it is Superset-pinned). CONFIRMED in dump.
4. **`session` cookie with `{"_user_id":1,"user_id":1}` payload** — 847 records. Specific to FAB's anon/bootstrap session. Strong tell, but it is the CVE-2023-27524 surface marker, not a clean liveness fingerprint (rotated hosts emit an opaque token).
5. **Canonical favicon hash `1582430156`** — 735/2000 records. Stable Stage 1c enrichment hook. Title-squatters that reuse the real Superset favicon will share it; squatters that rebrand will not.
6. `/health` returns `OK` (200, text). Generic, not Superset-unique. Useful for liveness only.

**Most reliable single unauth discriminator:** `data-bootstrap` HTML attribute. Highest coverage of a vendor-unique token, present pre-auth, no title collision. Use the `Apache Superset:` version header as the conjunctive second signal when you also need the version.

## AI-backend discriminator (AI-wired BI)

This is the scope filter. A Superset is "AI-wired" when its backend database connection points at AI/ML data: a pgvector-enabled Postgres, a Qdrant/Weaviate/Milvus result table, an embedding store, or LLM-analytics datasets.

What is observable, and at what auth depth:

- **NOT observable passively.** Caution: the dump shows `llm` (361) and `embedding` (263) substring hits in `http.html`, but inspection proves these are NOISE — `llm` comes from `Mintplex-Labs/anything-llm/master` strings injected by Shodan html-hash collisions (353 records), and `embedding` comes from Superset's own dashboard UI copy ("allow embedding from any domain"). Neither indicates an AI backend. Do not dork on `http.html:"embedding"` for this scope — it is a pure FP.
- **The real discriminator lives at `/api/v1/database/`.** If RBAC is misconfigured (or the session is forged via CVE-2023-27524), the database list leaks connection **display names** and SQLAlchemy URIs. Connection names containing `pgvector`, `qdrant`, `weaviate`, `milvus`, `pinecone`, or a `postgresql+psycopg2://...` URI against a vector-enabled DB = AI-wired. `/api/v1/dataset/` leaks dataset names; names with `embedding`, `vector`, `_emb`, `llm_`, `chunks` = vector tables.
- **Chart-type tell:** charts over vector tables show up as similarity/distance scatter or table viz over `*_embedding` datasets in `/api/v1/chart/`.
- **Auth depth required:** AI-backend confirmation is a VERIFY-lane action behind `/api/v1/database/` (needs a 200-with-data read, which on the survey set means RBAC-misconfig or a forged session). Passive Stage -1 CANNOT confirm AI-wiring. This squad hands the verify lane the discriminator query, not a finding.

## Known CVEs

- **CVE-2023-27524 (HEADLINE, CVSS 8.9).** Default `SECRET_KEY` -> Flask session forgery -> auth bypass as admin. Chains to RCE: an authenticated admin can run SQL via SQLLab and, on permissive DB drivers, reach OS command exec. Affects <= 2.0.1 and any host that overrode the default-key boot refusal. Dump cohort: 16 records at 2.0.1, plus all sub-2.0 versions, plus override hosts on newer builds.
- **CVE-2023-27526** — improper SSRF/metadata via Superset (related disclosure window).
- **CVE-2021-37798** — Mako-template SSTI in chart/SQLLab params (RCE on older builds).
- **CVE-2024-39887** — SQLLab `/api/v1/sqllab/` SQL-injection-class on specific drivers.
- **CVE-2023-37941** — pickle-based metastore RCE (import of crafted artifacts by an authenticated user).
- General class: any post-auth SQLLab access on a Superset wired to a sensitive backend is a data-exfil primitive, which is exactly why the AI-backend discriminator matters.

## Dork false-positive rate + mitigation

`title:"Superset"` is heavily polluted. Dump title census (2000 records):

- 1940 bare `Superset` (mostly real, but the title is the product word).
- Brand squatters: `Udio Superset` (3), `Red Digital - Superset` (2), `MSI Superset` (1), `Home - Superset Solutions, Inc.` (1), `KSM-Stoker`, `Traccar`, `Network Camera VB-H610`, `中国联通家庭网关`, `Proxmox`, `FreedomBox` — these ride the same html-hash bucket or literally use the word "Superset" as a product name. Non-Superset devices (cameras, gateways, Proxmox) appear because the dump was hash-clustered, not because they self-identify.
- 353 records are `anything-llm` html-hash-collision noise.

**Mitigation:** never scope on `title:"Superset"` alone. Conjoin with a vendor-unique token:
- `http.html:"data-bootstrap"` (FAB bootstrap blob) strips the camera/gateway/Proxmox squatters.
- `"Apache Superset:"` header presence strips everything that is not the real product.
- The FP rate on bare `title:"Superset"` is ~3-5% hard squatters plus the ~18% hash-collision noise; conjoining with `data-bootstrap` or the version header drops it toward zero.

## tome JSON

Written to `~/tome/platforms/superset.json` (schema matched against `anythingllm.json` / `agentgpt.json`). Status **CONFIRMED** for the platform fingerprint (data-bootstrap, version header, favicon, ports, CVE-2023-27524 all evidenced in the local dump). Status of the **AI-backend wiring** per host stays CANDIDATE — not confirmable passively, requires `/api/v1/database/` verify-lane read.

tome is a Go source repo (`tome dorks superset` currently empty); adding the JSON requires a `go generate` / embed rebuild for the CLI to serve it. Flagged to orchestrator: tome needs a rebuild after this commit, not just a file drop.
