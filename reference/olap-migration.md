# OLAP Migration: Bootstrapping and Maintaining the Analytics Layer

_Companion to: [`reference/realtime-olap-architecture.md`](realtime-olap-architecture.md), [`reference/olap-schema-clickhouse.sql`](olap-schema-clickhouse.sql), [`reference/olap-tools-spec.md`](olap-tools-spec.md)._

This document describes how to:

1. Bootstrap ClickHouse from existing SQLite + `~/recon`.
2. Keep ClickHouse in sync with `nuclide.db` and `empire.db`.
3. Use DuckDB for ad-hoc analysis.
4. Handle failure and correctness concerns.

SQLite remains the **system of record**. ClickHouse is an **analytic mirror** for population-scale reasoning; DuckDB is for local experiments.

---

## 1. Goals

- Populate ClickHouse with historical findings and enrichment outputs.
- Support the OLAP-backed tools described in [`olap-tools-spec.md`](olap-tools-spec.md) (`get_auth_off_rates`, `get_operator_exposure`, etc.).
- Ensure we can **rebuild** ClickHouse at any time from:
  - `nuclide.db` (VisorLog),
  - `empire.db` (JAXEN, as needed),
  - Raw artifacts under `~/recon`.

No canonical data lives *only* in ClickHouse.

---

## 2. Baseline: Existing State

- `nuclide.db` (SQLite):
  - Lifecycle-tracked findings, current classification, disclosure state, timestamps, Rego scores, tags.

- `empire.db` (SQLite):
  - Shodan staging, intermediate harvest metadata.

- `~/recon/...`:
  - Raw per-survey artifacts (HTTP responses, banners, CT dumps, JS bundles, etc.).
  - Evidence packs referenced by findings.

- JSON shapes:
  - Stable contracts between tools (VisorGraph, aimap, VisorScuba, VisorLog, etc.).

These remain unchanged by the migration.

---

## 3. ClickHouse Bootstrap

### 3.1 Create ClickHouse Schema

Apply the schema (or adjusted variant) from [`olap-schema-clickhouse.sql`](olap-schema-clickhouse.sql), including:

- `findings` fact table.
- Optionally `finding_cves`, `org_dim`, `framework_dim` if/when required.

Run this once against the ClickHouse cluster.

### 3.2 Export from SQLite

Write a small CLI (e.g., `export_findings.py`) that:

1. Connects to `nuclide.db`.
2. SELECTs all relevant fields for the `findings` table.
3. Emits either:
   - CSV files, or
   - Parquet files (preferred), or
   - Direct HTTP inserts to ClickHouse.

Recommended: **Parquet** to allow reuse with DuckDB.

Example shape (pseudo-SQL from SQLite):

```sql
SELECT
  finding_id,
  survey_id,
  first_seen_at,
  last_verified_at,
  created_at,
  updated_at,
  ip,
  port,
  hostname,
  asn,
  cidr,
  org_id,
  org_name,
  country,
  sector,
  platform_class,
  framework,
  framework_version,
  category,
  tags_json,              -- JSON array of strings
  auth_present,
  severity_tier,
  compliance_score,
  criticality_tier,
  pii_present,
  admin_surface_exposed,
  version_disclosed,
  exploitation_indicator,
  cve_ids_json,           -- JSON array of strings
  status,
  disclosure_sent,
  disclosure_first_sent_at,
  disclosure_last_updated_at,
  last_status_change_at,
  is_honeypot,
  source_systems_json,
  survey_version,
  policy_version
FROM findings;            -- or the appropriate table name in nuclide.db
```

Then transform JSON fields into arrays during export, or let ClickHouse parse JSON.

### 3.3 Load into ClickHouse

Option A: Use `clickhouse-client` with CSV/TSV.

Option B (recommended): load Parquet via HTTP or `clickhouse-local`.

Example (CSV for illustration):

```bash
clickhouse-client --query="INSERT INTO findings FORMAT CSV" \
  < findings_export.csv
```

Or Parquet:

```sql
INSERT INTO findings
SELECT *
FROM file('findings_export.parquet', Parquet);
```

Bootstrap should be **idempotent** if possible (or run once on a fresh DB).

---

## 4. Ongoing Sync (SQLite → ClickHouse)

### 4.1 Change Detection Strategy

We need to propagate:

- New findings.
- Updates to severity/score/classification.
- Status/disclosure changes.
- Re-verification timestamps.

Approach:

- Add a monotonic column in SQLite (if not already present):
  - `updated_at` or `last_synced_at`.
- Track a **high-water mark** per sync job:
  - e.g., `last_synced_updated_at`.

### 4.2 Sync Process

Implement a periodic job (e.g. `sync_clickhouse.py`) that runs every N minutes (e.g., 5–10 min):

1. Read `last_synced_updated_at` from a local state file/table.
2. Query `nuclide.db` for rows with `updated_at > last_synced_updated_at`.
3. Export deltas to a temp file (CSV/Parquet) or in-memory.
4. Upsert into ClickHouse.

Because ClickHouse doesn't have native row-level UPDATE in MergeTree, use one of:

- **Re-insert pattern**:
  - Use a `ReplacingMergeTree` with a `version` or `updated_at` column.
  - Insert a new row for each update; queries use the latest version.

- **Insert-only with "current" flag** (for now):
  - If the volume is low, simpler: insert new rows and filter by latest `updated_at` per `finding_id` in views.

Example engine tweak:

```sql
ENGINE = ReplacingMergeTree(updated_at)
PARTITION BY toYYYYMM(first_seen_at)
ORDER BY (finding_id);
```

Then sync job simply inserts delta rows; merges resolve to latest state.

5. Update `last_synced_updated_at` after a successful batch.

### 4.3 Failure Handling

- If sync fails:
  - Do not advance high-water mark.
  - Next run reattempts the same range.
- If ClickHouse is down:
  - SQLite + pipeline continue to function; only analytics degrade.
- To rebuild:
  - Drop/empty `findings`.
  - Rerun full bootstrap from SQLite + `~/recon`.

---

## 5. DuckDB Integration

DuckDB is for:

- Local, ad-hoc analysis.
- Prototyping new metrics/reports on subsets of data.
- Testing new Rego policies or taxonomy transformations.

### 5.1 Data Sources for DuckDB

- Parquet exports from ClickHouse (via `SELECT ... INTO OUTFILE`).
- Direct reads from Parquet generated by SQLite export.
- Possibly small snapshots of `~/recon` JSON.

Example workflow:

```sql
-- In DuckDB
CREATE TABLE findings AS
SELECT * FROM read_parquet('findings_export.parquet');

-- Experiment with a new aggregate
SELECT platform_class,
       count(*) AS total,
       avg(compliance_score) AS avg_score
FROM findings
GROUP BY platform_class;
```

Once a new metric/projection looks useful, port it into a ClickHouse view or a Python/Go tool.

---

## 6. Verification and Invariants

After bootstrap and initial sync, verify:

1. **Row counts**
   - `count(*)` in SQLite vs ClickHouse (with latest-version semantics).
   - Allow for minor skew if you ignore closed/old findings in ClickHouse.

2. **Spot-check fields**
   - Sample N `finding_id`s; compare fields between SQLite and ClickHouse.

3. **Key queries**
   - Run a selection of OLAP-backed queries (auth-off rates, backlog, multi-category operators) and sanity-check results against known examples.

Invariants:

- No canonical data exists only in ClickHouse.
- Every ClickHouse row is derivable from:
  - `nuclide.db` + `empire.db` + artifacts under `~/recon`.
- Sync is monotonic: we never delete or mutate SQLite based on ClickHouse.

---

## 7. Security and Exposure

- Treat ClickHouse as **sensitive**:
  - It aggregates cross-operator, cross-sector exposure data.
- Apply the same survey standards to your own cluster:
  - No unauthenticated exposure,
  - TLS + auth,
  - Network restrictions.

The system already knows how to detect exposed ClickHouse instances; apply those checks locally (self-dogfooding).

---

## 8. Implementation Checklist

- [ ] Finalize ClickHouse schema ([`olap-schema-clickhouse.sql`](olap-schema-clickhouse.sql)).
- [ ] Implement `export_findings` from `nuclide.db` to Parquet.
- [ ] Implement bootstrap loader into ClickHouse.
- [ ] Implement periodic `sync_clickhouse` job (delta export + insert).
- [ ] Add a high-water mark store for `updated_at`.
- [ ] Add basic verification script (row counts + spot-checks).
- [ ] Add DuckDB example notebook/script for local analysis.
- [ ] Add monitoring/alerting on sync failures and ClickHouse health.

---

This is a living migration plan: adjust schema fields, sync cadence, and engine options as the system evolves, but the core pattern, SQLite as system of record, ClickHouse as analytic mirror, DuckDB as scratchpad, stays stable.

---

## 9. Reference Install: rooster (2026-05-06, decommissioned same day)

> **Status: DECOMMISSIONED 2026-05-06.** Container, cron, credentials, data, and log directories were removed several hours after install. Rationale: at the current ledger scale (~600 findings, ~500 added per month), DuckDB embedded against `nuclide.db` answers every population-tier query the OLAP-tools-spec describes in milliseconds. The ClickHouse mirror was running but no read path was actually using it, `data/olap-demo.py` reads SQLite directly via DuckDB's `sqlite_scanner`, not ClickHouse. The infrastructure (schema, exporter, sync, bootstrap, cron wrapper) is preserved in the repo and is ready to redeploy when scale or use case warrants, e.g., crossing 100k findings, public-facing dashboards, or sub-second materialized-view alerting.
>
> The notes below remain canonical for the next install. Re-deploy effort is ~5 minutes given the gotchas are now documented.

First production install was on rooster (Linux 6.17, Docker 29.4.2, IPv6 disabled). 581 rows bootstrapped end-to-end. Notes for future installs:

### Container

ClickHouse 26.3.9.8 official image (`clickhouse/clickhouse-server:latest`). Run with `--network host` so the listener binds directly to rooster's network stack, then lock to localhost via the listen-host config override below. Bridge networking failed on this host because docker-proxy and the IPv6-disabled config interact badly, direct curl to the container's bridge IP got `Connection refused` even when the listener was visibly up inside the container.

```bash
docker run -d \
  --name nuclide-clickhouse \
  --restart unless-stopped \
  --network host \
  -v ~/clickhouse-data:/var/lib/clickhouse \
  -v ~/clickhouse-logs:/var/log/clickhouse-server \
  -v ~/clickhouse-config/listen.xml:/etc/clickhouse-server/config.d/listen.xml:ro \
  --env-file ~/.config/nuclide/clickhouse-credentials.env \
  -e CLICKHOUSE_DEFAULT_ACCESS_MANAGEMENT=1 \
  --ulimit nofile=262144:262144 \
  clickhouse/clickhouse-server:latest
```

### `listen.xml` config override

```xml
<clickhouse>
    <!-- Container runs with host networking; bind listener to localhost only.
         Dogfoods the survey rule against exposing ClickHouse on a public IP. -->
    <listen_host replace="replace">127.0.0.1</listen_host>
</clickhouse>
```

Two gotchas resolved during this install:

1. **IPv6 dual-stack default fails on IPv6-disabled hosts.** ClickHouse's default config uses `<listen_host>::</listen_host>` (IPv6 wildcard with IPv4-mapped fallback). On a host with IPv6 disabled the bind returns `EAI: Address family for hostname not supported`. The `listen_try=1` fallback to `0.0.0.0` did not work cleanly here; an explicit `replace="replace"` override was required.

2. **XML comments cannot contain `--`.** The XML parser rejects `--network host` inside a `<!-- ... -->` comment because `-->` ends the comment. SAXParseException at parse time put the container into a restart loop. Avoid hyphen-pairs inside comments.

### Credentials

```
~/.config/nuclide/clickhouse-credentials.env  (mode 600)

CLICKHOUSE_HOST=127.0.0.1
CLICKHOUSE_PORT=8123
CLICKHOUSE_USER=default
CLICKHOUSE_PASSWORD=<generated>
CLICKHOUSE_DATABASE=nuclide
```

Generate password with `openssl rand -base64 24 | tr -d '/+=' | head -c 32`.

### Schema notes (reflected in olap-schema-clickhouse.sql)

Two schema corrections shipped during bootstrap:

- `finding_cves` originally had `PARTITION BY toYYYYMM(now())`. ClickHouse rejects this, partition keys must be deterministic functions of row data, not of system clock. Removed PARTITION BY (single partition is fine for this small join table).
- `ip` and `disclosure_first_sent_at` / `disclosure_last_updated_at` are now `Nullable(IPv4)` / `Nullable(DateTime)`. Empty string `""` is not parseable as either type; rows without resolved IP or pending-disclosure findings need actual `NULL`.

### Insert path

Both `bootstrap-clickhouse.py` and `sync-clickhouse.py` use ClickHouse's native `JSONEachRow` format via `clickhouse_connect.client.raw_insert()`. Two reasons:

1. The exporter emits ISO-8601 timestamp strings (e.g. `"2026-05-02T23:53:51Z"`); `client.insert()` expects Python `datetime` objects and crashes with `'str' object has no attribute 'timestamp'`. ClickHouse server-side parses these via `parseDateTimeBestEffort` natively.
2. The exporter emits a superset of columns (carries `notes`, `match_path`, `tld` for evidence-pack tracing). The insert-side projects each row dict to the table's declared column set before serialization; extras are silently dropped.

### Self-dogfood

After install, verify the listener is actually localhost-only:

```bash
ROOSTER_IP=$(hostname -I | awk '{print $1}')
curl -s -m 3 "http://$ROOSTER_IP:8123/ping"           # should fail (connection refused)
curl -s -m 3 "http://127.0.0.1:8123/ping"             # should return "Ok."
```

Confirms the survey rule "no unauthenticated ClickHouse exposure on a public interface" is being applied to our own analytics layer.

### Cron-driven delta sync

`data/cron-sync-clickhouse.sh` is the documented entrypoint. It sources the credentials env, runs `sync-clickhouse.py --execute`, and appends UTC-bracketed output to `~/.config/nuclide/clickhouse-sync.log`. Suggested crontab entry (every 10 minutes):

```
*/10 * * * * /home/cowboy/AI-LLM-Infrastructure-OSINT/data/cron-sync-clickhouse.sh
```

A typical run on no-delta is logged as:

```
[2026-05-06T03:21:05Z] sync starting
Delta rows:       0
Nothing to sync. State unchanged.
[2026-05-06T03:21:05Z] sync finished (exit 0)
```

When new findings land in `nuclide.db`, the next cron tick advances the watermark and inserts only the deltas. Watermark state at `~/.config/nuclide/clickhouse-sync-state.json` (mode 600). To force a full re-sync (e.g., after a schema change): `python3 data/sync-clickhouse.py --reset` then re-run.
