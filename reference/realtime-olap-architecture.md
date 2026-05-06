# AI Exposure Survey System: Analytics & OLAP Design

## 1. Purpose and Scope

This document describes the analytics and storage design for the AI exposure survey system.

- SQLite remains the **system of record** for findings and lifecycle state.
- A real-time OLAP layer (ClickHouse) provides **population-scale analytics** and supports new, aggregated tools for both humans and LLM agents.
- DuckDB is used for **embedded, ad-hoc analysis** over exported data.

This design is additive: OLAP augments the existing per-finding pipeline; it does not replace it.

---

## 2. Current Architecture (Baseline)

### 2.1 Canonical Stores

- `nuclide.db` (VisorLog)
  - Lifecycle-tracked findings store (statuses, disclosure state).
- `empire.db` (JAXEN)
  - Shodan harvest staging DB.
- `~/recon/...`
  - Raw per-survey artifacts on disk; evidence packs for disclosures.
- JSON shapes
  - Stable schemas passed between tools; outputs are valid inputs to downstream tools.

### 2.2 Tools and Stages (High Level)

- Discovery and staging:
  - Shodan → JAXEN (`empire.db`)
  - Masscan, CT logs, DNS, WHOIS, JS bundle analysis
- Enrichment and attribution:
  - `VisorGraph` cert-pivot (IP → operator via SANs & WHOIS)
  - `aimap` fingerprinting (service/framework tag)
- Policy and scoring:
  - `VisorScuba` (Rego) → compliance score (0–10) + criticality tier
  - Severity from PII presence, unauth admin surface, version disclosure
- Post-processing:
  - CVE links from Shodan vulns + version inference
  - Honeypot filtering
  - `nuclide-contact` for recipient resolution
  - Country/sector tagging
  - `VisorLog` dedupe by IP

SQLite + files hold **all authoritative state** and evidence.

---

## 3. New Requirements for Population-Scale Analytics

### 3.1 Scale and Retention

- Bursty ingestion: 500–1000 findings/min during survey runs.
- Steady state: <100 findings/day.
- Ledger growth: ~500 findings/month (across active surveys).
- Retention goals:
  - Hot (fast queries): 90 days.
  - Warm (trend analysis): 1 year.
  - Cold (raw artifacts/evidence): indefinite (on disk).

### 3.2 Latency and Cadence

- Active exploitation alerts: 5–15 minutes from probe → alert.
- New high-severity findings: visible in dashboards within 1 hour (no paging).
- Trend and population studies: daily/weekly; focus on **rates**, not per-instance immediacy.
- Drift checks: hourly cron; re-probe stale findings.
- Disclosure status updates: propagate to analytics within 10 minutes of `VisorLog` edits.

### 3.3 Population-Scale Queries (Examples)

Must be "interactive" (sub-second to a few seconds):

- New high-severity findings since last check, grouped by category & framework.
- Auth-off rate per platform class over the last 90 days.
- Per-operator exposure picture for any org/ASN/netblock.
- Disclosure pipeline state: open & undisclosed by severity.
- Cross-platform multi-finding operators (same org leaks ≥2 categories).
- Re-probe staleness queue: findings last verified > N days ago.
- CVE distribution across open findings.

---

## 4. Target Architecture

### 4.1 Storage Roles

- **SQLite (existing)**
  - Source of record for:
    - Findings, lifecycle state, disclosure history.
    - Rego outputs, scoring, tags.
  - Backed by raw evidence under `~/recon`.

- **ClickHouse (new, real-time OLAP layer)**
  - Analytic mirror over findings and enrichment outputs.
  - Supports:
    - Time-windowed aggregation (last 15m, 1h, 90d, 1y).
    - Multi-dimensional group-bys (framework, platform class, sector, country, org, ASN, category, severity, CVE).
  - Feeds dashboards, daily/weekly rate studies, and LLM population-level tools.

- **DuckDB (new, embedded analytics)**
  - Local, ad-hoc analysis engine.
  - Reads:
    - Parquet exports from ClickHouse,
    - or snapshots from SQLite/JSON.
  - Used for:
    - Prototyping metrics,
    - One-off analysis,
    - Testing new policy/taxonomy changes on subsets.

### 4.2 Data Flow

1. Scanners and harvesters populate staging and evidence:
   - JAXEN → `empire.db`, raw JSON artifacts under `~/recon`.

2. Enrichment pipeline:
   - `VisorGraph` → operator mapping.
   - `aimap` → service/framework tagging.
   - `VisorScuba` → Rego-based compliance and criticality scores.
   - CVE mapping, honeypot filtering, recipient resolution.

3. SQLite update:
   - `nuclide.db` (VisorLog) records:
     - Findings, tags, scores, status, disclosure metadata, verification timestamps.

4. OLAP ingestion:
   - A small ETL/sync process:
     - Reads from `nuclide.db` (and/or JSON exports).
     - Writes to ClickHouse fact and dimension tables.
   - Batched updates aligned with:
     - Survey runs,
     - Hourly drift jobs,
     - Disclosure status changes.

5. DuckDB usage:
   - Snapshots or exports from ClickHouse/SQLite for:
     - Local analysis,
     - Testing new Rego policies and metrics on subsets of the data.

---

## 5. OLAP Schema (High-Level)

### 5.1 Fact Table: `findings`

Example columns (non-exhaustive):

- Identity:
  - `finding_id` (PK)
  - `survey_id`
  - `first_seen_at`, `last_verified_at`
- Target:
  - `ip`, `port`, `hostname`, `asn`, `cidr`
  - `org_id` (operator), `country`, `sector`
- Classification:
  - `platform_class` (e.g., LLM gateway, vector DB, MCP, RAG endpoint, data layer)
  - `framework` / `framework_version`
  - `category` (taxonomy category)
- Security:
  - `auth_present` (bool/enum)
  - `severity_tier`
  - `compliance_score` (0–10, VisorScuba)
  - `criticality_tier`
  - `pii_present` (bool/enum)
  - `admin_surface_exposed` (bool)
  - `version_disclosed` (bool)
  - `cve_ids` (array or normalized join table)
  - `exploitation_indicator` (bool/enum)
- Lifecycle:
  - `status` (open, in_progress, closed, etc.)
  - `disclosure_sent` (bool)
  - `disclosure_first_sent_at`
  - `disclosure_last_updated_at`

Dimensions (optional separate tables if needed for normalization/readability):
- `org`, `asn`, `framework`, `category`, `survey`, `country`, `sector`, `cve`.

---

## 6. OLAP-Backed Queries and Tools

### 6.1 Human-Facing and Dashboard Queries

Backed directly by ClickHouse:

- New high-severity findings since last check, grouped by `category`, `framework`.
- Auth-off rate per `platform_class` over last 90 days (per day/week).
- Exposure snapshot for a given `org_id`/`asn`/`cidr`:
  - Counts by `category`, `severity`, status.
  - Time series of new vs. closed.
- Disclosure pipeline state:
  - `status in ('open','in_progress') AND disclosure_sent=false` grouped by `severity`, `framework`, `sector`.
- Multi-category operators:
  - Group by `org_id`, `count_distinct(category) >= 2`.
- Re-probe staleness queue:
  - `status != 'closed' AND last_verified_at < now() - N days`, sorted by risk score.
- CVE distribution:
  - Group by `cve_id`, `framework`, `category` over `status='open'`.

### 6.2 LLM/AI-Backed Tools (Additions)

New tools that call OLAP instead of SQLite directly:

- `get_auth_off_rates(window, group_by)`
- `get_population_trends(framework, window)`
- `get_operator_exposure(org_or_asn_or_cidr)`
- `get_disclosure_backlog(group_by)`
- `get_multi_category_operators(min_categories)`
- `get_reprobe_candidates(N_days)`
- `get_cve_distribution(filter)`

These are additive to existing per-finding tools:

- `get_findings`, `get_finding_history`
- `aimap_fingerprint`, `visorgraph_pivot`
- `nuclide_contact`, `bare_rank`
- `visorscuba_score`, `visorcorpus_generate`
- `draft_disclosure`, `cluster_find`

LLM agents can now perform both:

- **Local reasoning** (per finding), and
- **Population-tier reasoning** (rates, trends, cross-operator patterns).

---

## 7. Decision Logic and Cadences Using OLAP

- Active exploitation alerts:
  - OLAP query over last 5–15 minutes for findings with exploitation indicators; drive pages.
- New high-severity dashboards:
  - Hourly sync from SQLite → ClickHouse; dashboards query "since last check".
- Daily/weekly auth-off-rate and population-thesis jobs:
  - Scheduled OLAP queries → reports and maintainer-facing evidence packs.
- Hourly drift:
  - OLAP-driven `get_reprobe_candidates(N_days)` → scheduler.
- Disclosure status:
  - Changes in `nuclide.db` mirrored into OLAP within ~10 minutes → up-to-date pipeline views.

---

## 8. Migration and Safety Considerations

- ClickHouse is a **mirror**, not a replacement:
  - All authoritative state remains in SQLite + raw artifacts.
  - OLAP ingestion is idempotent and recoverable from SQLite and evidence packs.
- The system already surveys ClickHouse for exposure:
  - Apply same standards internally: no unauthenticated exposure of analytic cluster.
- OLAP failure modes:
  - If ClickHouse is down or lagging:
    - Per-finding tools and disclosures continue from SQLite.
    - Population-level views degrade gracefully (stale/absent analytics).

---

## 9. Companion Documents

- **[`reference/olap-schema-clickhouse.sql`](olap-schema-clickhouse.sql)** — concrete `CREATE TABLE` sketches for ClickHouse fact + dimensions. Partition keys, sort keys, optional CVE / org / framework dimension tables. Future: materialized views for the Section 6.1 query set.
- **[`reference/olap-tools-spec.md`](olap-tools-spec.md)** — spec for each of the 8 OLAP-backed LLM tools: input schema, output schema, SLO, ClickHouse SQL sketch, fallback behavior when the OLAP layer is unavailable.

Pending follow-on (offered as next deliverable):

- **`olap-migration.md`** — bootstrap procedure for ClickHouse from existing `nuclide.db` + `~/recon`, sync mechanics, and operational runbook for the layer.
