# LLM Tools Spec: OLAP-Backed (Population-Tier) Tools

_Companion to: [`reference/realtime-olap-architecture.md`](realtime-olap-architecture.md) and [`reference/olap-schema-clickhouse.sql`](olap-schema-clickhouse.sql)._

These tools are **additive** to the existing per-finding tools (`get_findings`, `aimap_fingerprint`, `nuclide_contact`, `bare_rank`, `visorscuba_score`, `visorcorpus_generate`, `draft_disclosure`, `cluster_find`). They sit on top of ClickHouse and let humans and LLM agents reason over **populations**: rates over time, cross-operator patterns, framework-level harm rankings.

The agent now picks tool by question shape:
- *"What about IP X?"* → per-finding tools (existing).
- *"Which framework should we pressure this week?"* → OLAP-backed tools (below).

Each tool below specifies inputs, behavior (with a ClickHouse SQL sketch), output, and an SLO. All queries assume `is_honeypot = 0` is applied unless otherwise noted, and that the SQLite → ClickHouse sync window is at most 10 minutes for lifecycle changes.

---

## 1. `get_auth_off_rates`

**Purpose**
Return auth-off rates over a time window, grouped by dimensions (e.g., platform_class, framework). The headline thesis-tracking tool.

**Inputs**

- `window`: string
  - Examples: `"7d"`, `"30d"`, `"90d"`.
- `group_by`: array of strings
  - Allowed: `"platform_class"`, `"framework"`, `"framework_version"`, `"sector"`, `"country"`.

**Behavior (ClickHouse sketch)**

```sql
SELECT
    {{ group_by_columns }},
    countIf(auth_present = 0) AS auth_off_count,
    count() AS total_count,
    auth_off_count / total_count AS auth_off_rate
FROM findings
WHERE first_seen_at >= now() - INTERVAL {{window}}
  AND is_honeypot = 0
GROUP BY {{ group_by_columns }};
```

**Output**

List of objects with:
- `group`: dict of group-by fields
- `auth_off_count`
- `total_count`
- `auth_off_rate` (float 0–1)

**SLO**

Latency: < 1s on hot data (≤ 90 days).

---

## 2. `get_population_trends`

**Purpose**
Time-series of exposure counts and/or auth-off rate for a given dimension (e.g., framework) over time. The "before vs after" curve when a maintainer ships a default change.

**Inputs**

- `dimension`: string (`"framework"`, `"platform_class"`, `"category"`).
- `value`: string (e.g., `"LangChain"`, `"llm_gateway"`).
- `window`: string (e.g., `"90d"`).
- `bucket`: string (`"day"` or `"week"`).

**Behavior**

```sql
SELECT
    toStartOf{{bucket}}(first_seen_at) AS bucket_ts,
    count() AS total_count,
    countIf(auth_present = 0) AS auth_off_count,
    auth_off_count / total_count AS auth_off_rate
FROM findings
WHERE first_seen_at >= now() - INTERVAL {{window}}
  AND {{dimension}} = {{value}}
  AND is_honeypot = 0
GROUP BY bucket_ts
ORDER BY bucket_ts;
```

**Output**

Array of `{bucket_ts, total_count, auth_off_count, auth_off_rate}`.

**SLO**

Latency: < 2s on 1-year window.

---

## 3. `get_operator_exposure`

**Purpose**
Per-operator exposure snapshot given an org/ASN/CIDR selector. The "everything we have on this org" view.

**Inputs**

- `selector_type`: `"org_id" | "asn" | "cidr"`.
- `selector_value`: string.
- `status_filter` (optional): e.g., `["open","in_progress"]`.

**Behavior**

1. Filter `findings` by the selector and (optional) status.
2. Return:
   - Counts by severity tier and category,
   - Counts by platform_class,
   - List of top-N open findings (IDs + key attributes).

**SQL sketches**

By severity:

```sql
SELECT severity_tier, count() AS cnt
FROM findings
WHERE {{selector_type}} = {{selector_value}}
  AND status IN {{status_filter}}
GROUP BY severity_tier;
```

By category/platform:

```sql
SELECT category, platform_class, count() AS cnt
FROM findings
WHERE {{selector_type}} = {{selector_value}}
  AND status IN {{status_filter}}
GROUP BY category, platform_class;
```

Top-N findings:

```sql
SELECT finding_id, ip, port, platform_class, framework, category,
       severity_tier, compliance_score, status
FROM findings
WHERE {{selector_type}} = {{selector_value}}
  AND status IN {{status_filter}}
ORDER BY severity_tier DESC, compliance_score DESC
LIMIT 100;
```

**Output**

- `severity_counts`: list of `{severity_tier, count}`
- `category_platform_counts`: list of `{category, platform_class, count}`
- `top_findings`: list of summarized findings

**SLO**

Latency: < 1s typical.

---

## 4. `get_disclosure_backlog`

**Purpose**
Summarize undisclosed findings by severity and optionally framework/sector. Drives "what should we work on today" agent decisions.

**Inputs**

- `group_by`: array of strings
  - e.g., `["severity_tier"]`, `["severity_tier","framework"]`, `["severity_tier","sector"]`.
- Optional `min_severity`: filter (e.g., `"med"` and above).

**Behavior**

```sql
SELECT
    {{group_by_columns}},
    count() AS backlog_count
FROM findings
WHERE disclosure_sent = 0
  AND status IN ('open','in_progress')
  AND severity_tier >= {{min_severity_optional}}
GROUP BY {{group_by_columns}};
```

**Output**

List of `{group: {...}, backlog_count}`.

**SLO**

Latency: < 1s.

---

## 5. `get_multi_category_operators`

**Purpose**
Find operators leaking multiple categories (e.g., vector DB + gateway + MCP). Input to escalation logic and CSIRT/DPA evidence packs.

**Inputs**

- `min_categories`: integer (default 2).
- Optional `window`: string (e.g., `"90d"`; defaults to `null` = all time).

**Behavior**

```sql
SELECT
    org_id,
    org_name,
    countDistinct(category) AS categories_leaked,
    count() AS findings_count
FROM findings
WHERE is_honeypot = 0
  {{ AND first_seen_at >= now() - INTERVAL {{window}} }}
GROUP BY org_id, org_name
HAVING categories_leaked >= {{min_categories}}
ORDER BY categories_leaked DESC, findings_count DESC
LIMIT 500;
```

**Output**

List of `{org_id, org_name, categories_leaked, findings_count}`.

**SLO**

Latency: < 2s on 1-year window.

---

## 6. `get_reprobe_candidates`

**Purpose**
Build the staleness queue: findings due for re-verification. Hourly-cron call to drive the drift checker.

**Inputs**

- `stale_days`: integer (`N`).
- Optional `limit`: integer (e.g., 1000).

**Behavior**

```sql
SELECT
    finding_id,
    ip, port, hostname,
    org_id, org_name,
    category, platform_class, framework,
    severity_tier, compliance_score,
    last_verified_at
FROM findings
WHERE status != 'closed'
  AND last_verified_at < now() - INTERVAL {{stale_days}} DAY
ORDER BY severity_tier DESC, compliance_score DESC, last_verified_at ASC
LIMIT {{limit}};
```

**Output**

List of findings with enough fields to re-probe and prioritize.

**SLO**

Latency: < 1s.

---

## 7. `get_cve_distribution`

**Purpose**
Summarize which CVEs are live across open findings, sliced by framework/category. Drives "these three CVEs are most prevalent in AI infra right now."

**Inputs**

- Optional `status_filter`: default `["open","in_progress"]`.
- Optional `window`: string (e.g., `"90d"`).
- Optional `group_by`: array (`["framework"]`, `["framework","category"]`, etc.).

**Behavior** (denormalized array version):

```sql
SELECT
    arrayJoin(cve_ids) AS cve_id,
    {{ group_by_columns }},
    count() AS cnt
FROM findings
WHERE status IN {{status_filter}}
  {{ AND first_seen_at >= now() - INTERVAL {{window}} }}
  AND length(cve_ids) > 0
GROUP BY cve_id, {{ group_by_columns }}
ORDER BY cnt DESC
LIMIT 1000;
```

**Output**

List of `{cve_id, group: {...}, count}`.

**SLO**

Latency: < 2s on 1-year window.

---

## 8. `get_new_high_severity_since`

**Purpose**
Incremental "what's new" feed for dashboards and LLM. The `since_ts` cursor lets the caller pull only deltas.

**Inputs**

- `since_ts`: ISO timestamp (last time caller checked).
- Optional `group_by`: array (`["category","framework"]`).

**Behavior**

```sql
SELECT
    {{group_by_columns}},
    count() AS new_high_count
FROM findings
WHERE created_at > {{since_ts}}
  AND severity_tier IN ('high','critical')
  AND is_honeypot = 0
GROUP BY {{group_by_columns}};
```

Optionally also returns top-N new high findings with brief details.

**Output**

Aggregated counts plus list of new high/critical finding IDs + key fields.

**SLO**

Latency: < 1s.

---

## Fallback behavior when OLAP layer is unavailable

If ClickHouse is down or lagging beyond the sync SLO:

- Per-finding tools and disclosures continue from SQLite without degradation.
- These OLAP-backed tools return a structured `{"unavailable": true, "reason": "...", "fallback": "..."}` rather than stale data, so the LLM agent can route around them rather than reason on stale aggregates.
- The fallback for hot queries is to run the same SQL shape against `nuclide.db` directly via DuckDB's `sqlite_scanner` extension. Slower but correct.

The orchestrator's first job after a fallback is recorded in the run log so the operator can see when OLAP was bypassed and re-warm the cache.

---

## What this enables (composed examples)

The agent chains the new tools the same way it chains the per-finding tools.

```
agent: "Today's focus?"
  → get_disclosure_backlog(group_by=["severity_tier","framework"])
  → get_auth_off_rates(window="30d", group_by=["framework"])
  → returns: "Frameworks A, B, C have the highest critical-undisclosed
    backlog. Framework D shows unusual auth-off rate growth - pull the
    drift curve next."
  → get_population_trends(dimension="framework", value="D", window="90d")
  → bare_rank(finding_text=...)  # per-finding tool, ranks MSF modules
```

vs the per-finding-only equivalent which can only answer "what about IP X."
