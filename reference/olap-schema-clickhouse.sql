-- =============================================================================
-- OLAP Schema — ClickHouse fact + dimensions for the AI Exposure Survey System
-- =============================================================================
--
-- Companion to: reference/realtime-olap-architecture.md
--
-- ClickHouse acts as the population-scale analytical mirror over findings
-- persisted authoritatively in nuclide.db (SQLite). All authoritative state
-- lives in SQLite + raw evidence under ~/recon. This schema is read-mostly,
-- backfillable from SQLite, and idempotent on re-ingest.
--
-- Conventions:
--   - All UInt8 boolean-ish columns use 0/1/2 (unknown/false/true) unless noted.
--   - `is_honeypot = 0` filter is applied to almost every analytical query.
--   - first_seen_at + org_id + framework + category is the primary co-locate
--     order because the most common queries scope by time × operator × stack.
--
-- Notes for future hardening (not in v1):
--   - Materialized views for the Section 6.1 hot queries (auth-off rate daily,
--     disclosure backlog, multi-category operators, CVE distribution).
--   - Retention TTLs once volume justifies tiering hot/warm.
--   - ReplicatedMergeTree if/when the layer outgrows a single node.
-- =============================================================================


-- -----------------------------------------------------------------------------
-- Core fact table: one row per (finding_id, survey, current classification)
-- -----------------------------------------------------------------------------
CREATE TABLE findings
(
    -- Identity
    finding_id         String,          -- UUID or stable ID from nuclide.db
    survey_id          String,          -- which survey run produced/confirmed it
    first_seen_at      DateTime,
    last_verified_at   DateTime,
    created_at         DateTime,        -- ingestion into findings
    updated_at         DateTime,

    -- Target / addressing
    ip                 IPv4,            -- or String if IPv6 is common
    port               UInt16,
    hostname           String,
    asn                UInt32,
    cidr               String,
    org_id             String,          -- canonical operator ID (from VisorGraph)
    org_name           String,
    country            FixedString(2),  -- ISO-3166
    sector             String,          -- taxonomy value

    -- Classification
    platform_class     String,          -- e.g. "llm_gateway", "vector_db", "mcp_server"
    framework          String,          -- e.g. "LangChain", "LlamaIndex", "VendorX"
    framework_version  String,
    category           String,          -- exposure taxonomy category
    tags               Array(String),   -- misc tags, fingerprints, etc.

    -- Security / scoring
    auth_present       UInt8,           -- 0/1/2 (unknown/false/true) or small enum
    severity_tier      String,          -- e.g. "low","med","high","critical"
    compliance_score   Float32,         -- 0.0-10.0 from VisorScuba
    criticality_tier   String,          -- e.g. "low","med","high"
    pii_present        UInt8,           -- 0/1/2
    admin_surface_exposed UInt8,        -- 0/1/2
    version_disclosed  UInt8,           -- 0/1/2
    exploitation_indicator UInt8,       -- 0/1/2 (none/suspected/confirmed)

    -- Vuln / CVE (simplest form; can normalize via finding_cves below)
    cve_ids            Array(String),   -- derived from Shodan + version inference

    -- Lifecycle / disclosure
    status             String,          -- "open","in_progress","closed",...
    disclosure_sent    UInt8,           -- 0/1
    disclosure_first_sent_at DateTime,
    disclosure_last_updated_at DateTime,
    last_status_change_at    DateTime,

    -- Survey / pipeline metadata
    is_honeypot        UInt8,           -- 0/1 flag (honeypot fleet filtered = 0)
    source_systems     Array(String),   -- e.g. ["shodan","masscan","ct","jsbundle"]
    survey_version     String,          -- survey methodology version
    policy_version     String           -- Rego policy version used
)
ENGINE = MergeTree
PARTITION BY toYYYYMM(first_seen_at)
ORDER BY (first_seen_at, org_id, framework, category);


-- -----------------------------------------------------------------------------
-- Optional: normalized CVE dimension
-- Use when finding-to-CVE cardinality grows or when joining against external
-- CVE metadata (CVSS, EPSS, KEV) is needed.
-- -----------------------------------------------------------------------------
CREATE TABLE finding_cves
(
    finding_id String,
    cve_id     String
)
ENGINE = MergeTree
PARTITION BY toYYYYMM(now())
ORDER BY (cve_id, finding_id);


-- -----------------------------------------------------------------------------
-- Optional: org dimension
-- Most org/framework details can be denormalized in the fact table at this
-- scale. Promote to a dimension once enrichment data outgrows the row.
-- -----------------------------------------------------------------------------
CREATE TABLE org_dim
(
    org_id     String,
    org_name   String,
    asn        UInt32,
    country    FixedString(2),
    sector     String
)
ENGINE = MergeTree
ORDER BY org_id;


-- -----------------------------------------------------------------------------
-- Optional: framework dimension
-- The auth_default_noted column is load-bearing for the auth-off-default thesis.
-- Once we have shipped a framework's default-config audit, flip it to 1.
-- -----------------------------------------------------------------------------
CREATE TABLE framework_dim
(
    framework          String,
    vendor             String,
    homepage           String,
    auth_default_noted UInt8  -- 0/1 flag once you've documented the default
)
ENGINE = MergeTree
ORDER BY framework;
