# OLAP Migration — Bootstrapping and Maintaining the Analytics Layer

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

This is a living migration plan: adjust schema fields, sync cadence, and engine options as the system evolves, but the core pattern — SQLite as system of record, ClickHouse as analytic mirror, DuckDB as scratchpad — stays stable.
