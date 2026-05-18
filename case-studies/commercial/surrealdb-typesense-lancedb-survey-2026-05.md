---
type: survey
---

# SurrealDB, Typesense, and LanceDB: Exposure Survey

_NuClide Research · 2026-05-09_

---

## Summary

Three additional vector-capable databases surveyed as part of the 2026-05-09 vector DB series. Combined Shodan pull → asyncio probe across 995 IPs (431 SurrealDB + 354 Typesense + 210 LanceDB).

**SurrealDB** is the notable finding: 262 reachable, **34 unauthenticated** (13% open rate). Auth-off instances heavily skewed toward older 1.x versions, consistent with SurrealDB's auth posture tightening across versions. **Typesense** (60 reachable) enforces API key auth universally. 0 unauth. **LanceDB** Shodan hits are almost entirely web applications embedding the library, not standalone REST servers. 7 web app surfaces found, 0 LanceDB REST API endpoints confirmed.

---

## SurrealDB

### Methodology

```
shodan download '"surrealdb"' → 431 unique IPs
asyncio probe: GET /health → 200 confirms reachable
               GET /version → version string
               POST /sql (no auth header) → 200 = unauth, 401 = auth required
```

### Results

| Metric | Value |
|---|---|
| IPs probed | 431 |
| Reachable (/health 200) | **262** |
| **Unauthenticated (SQL executes)** | **34** |
| Auth-gated (401) | 228 |

### Version distribution (top 8)

| Version | Count |
|---|---|
| 2.6.5 | 31 |
| 3.0.5 | 29 |
| 2.3.10 | 19 |
| 2.4.0 | 17 |
| 3.0.4 | 13 |
| 2.6.0 | 11 |
| 2.6.3 | 9 |
| unknown | 11 |

### Auth posture by version era

The 34 unauth instances cluster heavily in the 1.x era (betas through 1.5.x). SurrealDB tightened auth defaults significantly between v1.0 (beta) and v2.x:

- **v1.0 betas / v1.x (pre-2023):** Auth optional, many ship with `--user root --pass root` defaults or no auth at all
- **v2.x+:** Auth required by default; `--unauthenticated` flag needed to disable
- **v3.x:** Auth enforced, no bypass flag

Unauth instances confirmed (selection):
```
142.44.211.206:8000  v=surrealdb-3.0.4   ← anomalous: v3 unauth
106.15.196.17:8000   v=surrealdb-2.6.5   ← v2.6 unauth (misconfigured)
168.119.239.48:8000  v=surrealdb-2.3.10
146.190.50.35:8000   v=surrealdb-1.0.0+20230913
116.202.33.62:8000   v=surrealdb-1.0.0-beta.9
173.230.150.151:8000 v=surreal-1.0.0-beta.8
```

The `surrealdb-3.0.4` unauth instance (`142.44.211.206`) is the most anomalous. V3 shipped with strict auth defaults. Likely deployed with explicit `--unauthenticated` flag or a custom `surreal.toml` disabling auth.

### Impact

SurrealDB is a multi-model database (document + graph + relational + vector) with a SQL-like query language. An unauthenticated `POST /sql` endpoint means:

- `SELECT * FROM <table>`: full table dump
- `SELECT * FROM <table> WHERE vector::similarity::cosine($embedding, vector_field) > 0.8`. Vector search
- `CREATE <table> SET ...`: data injection
- `DELETE <table>`: data destruction
- `DEFINE USER ...`: privilege escalation if `DEFINE` is permitted without auth

---

## Typesense

### Results

| Metric | Value |
|---|---|
| IPs probed | 354 |
| Reachable (/health 200) | **60** |
| Unauthenticated | **0** |
| Auth-gated (API key required) | 60 |

Typesense requires an `X-TYPESENSE-API-KEY` header for all collection operations. The `/health` endpoint returns `{"ok":true}` without a key (confirming reachability) but `/collections` returns 401 without the key. **Typesense has the best auth posture of any vector DB surveyed to date: 0% unauthenticated.**

**Auth posture note:** Typesense's API key is set at startup and baked into application code. The key itself may be discoverable via other means (JS source, exposed env files, public repos) but the Typesense server layer is consistently gated.

---

## LanceDB

### Results

| Metric | Value |
|---|---|
| IPs probed | 210 |
| Web apps with "lancedb" in HTML | **7** |
| Standalone LanceDB REST servers | **0** |
| Tables accessible | **0** |

The `http.html:"lancedb"` Shodan signal captures web applications that embed the `lancedb` Python library (appear in page source, dependency lists, or error messages) rather than standalone LanceDB REST API servers. The 7 confirmed apps are generic web applications (Jupyter, Streamlit, Flask, FastAPI frontends) that reference lancedb in their HTML. None expose the LanceDB REST API directly.

**LanceDB REST server note:** LanceDB's standalone REST server (`lancedb-server`) is a newer addition and less commonly deployed publicly. The library is most often used embedded within Python applications, not as a standalone HTTP service. Shodan cannot distinguish "this app uses lancedb" from "this is a lancedb REST server". Live probing of `/v1/table/` is required. None of the 7 confirmed apps returned valid LanceDB REST responses.

**Assessment:** LanceDB as a standalone database does not appear in meaningful numbers on the public internet at this time. It is primarily an embedded/local library. The Shodan signal for it is noise from web apps that import the package.

---

## Comparative Auth Posture Summary

| Database | Reachable | Unauth | Unauth % | Default auth posture |
|---|---|---|---|---|
| ChromaDB (prior survey) | 92 | 92 | 100% | Off by default (< v0.6) |
| Weaviate (this series) | 694 | 435 | 63% | Off by default |
| Milvus/Attu (this series) | 763 | 593 | 78% | RBAC opt-in |
| SurrealDB (this survey) | 262 | 34 | 13% | On by default (v2+), off in 1.x |
| Typesense (this survey) | 60 | 0 | 0% | **Required, no bypass** |
| LanceDB (this survey) | 7 | 0 | 0% | Embedded library, N/A |

Typesense is the clear outlier: mandatory API key auth with no opt-out path. SurrealDB's improvement from 1.x to 2.x/3.x is visible in the data. The unauth instances are disproportionately old versions.

---

## Discovery Context

Survey conducted 2026-05-09. Shodan pulls: `"surrealdb"` (454 hits), `"typesense"` (416 hits), `http.html:"lancedb"` (420 hits). Asyncio probe with 2s connect / 4s read / 80 concurrent.

Companion surveys: `weaviate-cloud-survey-2026-05.md`, `milvus-attu-survey-2026-05.md`.
