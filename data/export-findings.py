#!/usr/bin/env python3
"""
export-findings.py — VisorLog SQLite → JSONL/CSV exporter for OLAP ingest

Reads from the events table in nuclide.db (VisorLog's ECS-normalized schema)
and emits rows shaped to the OLAP fact-table target documented in
reference/olap-schema-clickhouse.sql + reference/olap-migration.md.

Field mapping (events column → fact-table column):
    id                  → finding_id (stringified)
    source              → survey_id
    timestamp           → first_seen_at / created_at (ISO-8601)
    host_ip             → ip
    host_hostname       → hostname
    org_name            → org_name (org_id is left unset; VisorGraph cert-pivot
                          will populate later)
    org_country         → country
    sector              → sector
    tld                 → tld
    event_category      → category
    event_severity      → severity_tier
    tags                → tags (preserved as array) AND derived classifiers:
                            platform_class, framework, cloud_provider,
                            auth_present (UNAUTH tag → 0)
    vuln_ids            → cve_ids
    lifecycle_status    → status
    notes               → notes
    raw                 → parsed for port + framework_version + match_path
                          when non-empty

Stable across runs given the same input row. Idempotent on the export side;
ClickHouse-side de-duplication uses ReplacingMergeTree(updated_at) — see
reference/olap-migration.md §4.2.

Usage:
    python3 export-findings.py --output findings.jsonl
    python3 export-findings.py --output findings.csv --format csv
    python3 export-findings.py --since-id 500 --output deltas.jsonl
"""

from __future__ import annotations

import argparse
import csv
import json
import sqlite3
import sys
from pathlib import Path

DEFAULT_DB = Path.home() / "AI-LLM-Infrastructure-OSINT" / "data" / "nuclide.db"


# Controlled vocabularies derived from the observed tag distribution
# (most-common 200 tags in nuclide.db). Each tag maps to at most one
# classifier axis. Tags not in any vocabulary stay in the `tags` array
# as-is. Order matters: more-specific frameworks should come before
# generic class tags.

PLATFORM_CLASSES = {
    "OLLAMA":          "inference",
    "VLLM":            "inference",
    "TRITON":          "inference",
    "INFERENCE":       "inference",
    "VECTOR_DB":       "vector_db",
    "RAG":             "rag",
    "MLOPS":           "mlops",
    "DATA_APP":        "data_app",
    "STREAMLIT":       "data_app",
    "AGENT_PLATFORM":  "agent",
    "MCP":             "mcp",
    "LLM_GATEWAY":     "llm_gateway",
    "GATEWAY":         "llm_gateway",
    "AI_SAFETY_EVAL":  "ai_safety_eval",
    "BROWSER_AGENT":   "browser_agent",
    "DATALABEL":       "data_labeling",
    "OBSERVABILITY":   "observability",
    "OBJECT_STORE":    "object_storage",
    "MINIO":           "object_storage",
    "S3_COMPAT":       "object_storage",
    "DUCKDB_API":      "specialty_data_layer",
    "CLICKHOUSE":      "specialty_data_layer",
    "PINOT":           "specialty_data_layer",
    "CASSANDRA":       "specialty_data_layer",
    "SCYLLADB":        "specialty_data_layer",
    "AMULET_SCAN":     "specialty_data_layer",
    "DLT":             "specialty_data_layer",
}

FRAMEWORKS = {
    "OLLAMA":              "Ollama",
    "VLLM":                "vLLM",
    "TRITON":              "NVIDIA Triton",
    "ChromaDB":            "ChromaDB",
    "Qdrant":              "Qdrant",
    "Milvus":              "Milvus",
    "MILVUS":              "Milvus",
    "Weaviate":            "Weaviate",
    "MLFLOW":              "MLflow",
    "MLflow":              "MLflow",
    "STREAMLIT":           "Streamlit",
    "OPENWEBUI":           "Open WebUI",
    "OPEN_WEBUI":          "Open WebUI",
    "FLOWISE":             "Flowise",
    "DIFY":                "Dify",
    "MINIO":               "MinIO",
    "LITELLM":             "LiteLLM",
    "JAN_AI":              "Jan AI",
    "LM_STUDIO":           "LM Studio",
    "GRAFANA":             "Grafana",
    "PROMETHEUS":          "Prometheus",
    "ETCD":                "etcd",
    "AMULET_SCAN":         "Amulet Scan DuckDB API",
    "DEFINITE":            "Definite.app DuckDB",
    "CLICKHOUSE":          "ClickHouse",
    "PINOT":               "Apache Pinot",
    "SCYLLADB":            "ScyllaDB",
    "CASSANDRA":           "Apache Cassandra",
    "JUPYTER":             "Jupyter",
    "RAY":                 "Ray",
    "LANGFUSE":            "Langfuse",
    "PHOENIX":             "Phoenix",
    "DOCCANO":             "doccano",
}

CLOUD_PROVIDERS = {
    "AWS":           "aws",
    "GCP":           "gcp",
    "AZURE":         "azure",
    "DIGITALOCEAN":  "digitalocean",
    "HETZNER":       "hetzner",
    "VULTR":         "vultr",
    "SCALEWAY":      "scaleway",
    "OVH":           "ovh",
    "LINODE":        "linode",
    "CONTABO":       "contabo",
    "ALIBABA":       "alibaba",
    "ORACLE_CLOUD":  "oracle",
}


def _classify_tag_set(tags: list[str], vocabulary: dict[str, str]) -> str | None:
    """Return the first vocabulary value matched by any tag, or None."""
    for tag in tags:
        if tag in vocabulary:
            return vocabulary[tag]
    return None


def _safe_json_load(s: str | None) -> object:
    if not s:
        return None
    try:
        return json.loads(s)
    except (json.JSONDecodeError, TypeError):
        return None


def _transform_row(row: sqlite3.Row) -> dict:
    """Transform one events-table row into the fact-table-shaped dict."""
    tags = _safe_json_load(row["tags"]) or []
    if not isinstance(tags, list):
        tags = []
    cve_ids = _safe_json_load(row["vuln_ids"]) or []
    if not isinstance(cve_ids, list):
        cve_ids = []
    raw = _safe_json_load(row["raw"]) or {}
    if not isinstance(raw, dict):
        raw = {}

    platform_class = _classify_tag_set(tags, PLATFORM_CLASSES)
    framework = _classify_tag_set(tags, FRAMEWORKS)
    cloud_provider = _classify_tag_set(tags, CLOUD_PROVIDERS)

    # Derived flags from tag presence. Both UNAUTH* family (UNAUTH,
    # UNAUTH_ADMIN_POST, UNAUTH_API, etc.) and TAKEOVER (account-takeover
    # finding implies the instance was reachable without auth) directly
    # signal auth_present=0. BILLING_THEFT_RISK and OLLAMA_CLOUD_MODELS
    # are consequence tags, not direct signals — left alone.
    auth_present = 0 if any(t.startswith("UNAUTH") or t == "TAKEOVER" for t in tags) else None
    cve_vuln_flag = 1 if "CVE_VULN" in tags else 0
    version_disclosed = 1 if "VERSION_DISCLOSED" in tags else 0
    is_honeypot = 1 if any(t in {"HONEYPOT", "AS63949", "DECOY"} for t in tags) else 0

    # Pull port + framework_version + match_path from raw if present
    port = raw.get("port")
    framework_version = raw.get("version") or raw.get("framework_version")
    match_path = raw.get("match_path")

    return {
        # identity
        "finding_id":          str(row["id"]),
        "survey_id":           row["source"] or "",
        "first_seen_at":       row["timestamp"],
        "last_verified_at":    row["timestamp"],   # no separate re-probe column yet
        "created_at":          row["timestamp"],
        "updated_at":          (row["updated_at"] if "updated_at" in row.keys() else None) or row["timestamp"],
        # target
        "ip":                  row["host_ip"] or "",
        "port":                int(port) if port else 0,
        "hostname":            row["host_hostname"] or "",
        "asn":                 0,                  # unknown until enrichment
        "cidr":                "",
        "org_id":              "",                 # populated by VisorGraph cert-pivot post-export
        "org_name":            row["org_name"] or "",
        "country":             row["org_country"] or "",
        "sector":              row["sector"] or "",
        "tld":                 row["tld"] or "",
        # classification
        "platform_class":      platform_class or "",
        "framework":           framework or "",
        "framework_version":   framework_version or "",
        "category":            row["event_category"] or "",
        "tags":                tags,
        # security / scoring
        "auth_present":        auth_present if auth_present is not None else 2,
        "severity_tier":       row["event_severity"] or "",
        "compliance_score":    0.0,                # from VisorScuba; not yet persisted in events
        "criticality_tier":    row["event_severity"] or "",
        "pii_present":         2,
        "admin_surface_exposed": 1 if "UNAUTH_ADMIN_POST" in tags else 2,
        "version_disclosed":   version_disclosed,
        "exploitation_indicator": 1 if cve_vuln_flag and version_disclosed else 0,
        # vuln
        "cve_ids":             cve_ids,
        # lifecycle
        "status":              row["lifecycle_status"] or "open",
        "disclosure_sent":     1 if row["lifecycle_status"] in {"disclosed","acknowledged","remediated","verified"} else 0,
        "disclosure_first_sent_at": "",
        "disclosure_last_updated_at": "",
        "last_status_change_at":     row["timestamp"],
        # provenance
        "is_honeypot":         is_honeypot,
        "source_systems":      [row["source"]] if row["source"] else [],
        "survey_version":      "",
        "policy_version":      "",
        # NuClide-only — preserved for evidence-pack tracing; ClickHouse can ignore
        "notes":               row["notes"] or "",
        "match_path":          match_path or "",
    }


def export(db_path: Path, out_path: Path, fmt: str, since_id: int, since_updated_at: str | None) -> int:
    """Read events, transform, write out. Return row count.

    Filters: --since-id picks rows by autoincrement id (good for first-seen
    delta exports); --since-updated-at picks rows by the updated_at watermark
    (good for ongoing sync that catches lifecycle / severity / tag changes).
    """
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    clauses = []
    params: list = []
    if since_id:
        clauses.append("id > ?")
        params.append(since_id)
    if since_updated_at:
        clauses.append("updated_at > ?")
        params.append(since_updated_at)
    where = ("WHERE " + " AND ".join(clauses)) if clauses else ""
    sql = f"SELECT * FROM events {where} ORDER BY id"
    rows = cur.execute(sql, params).fetchall()

    if fmt == "jsonl":
        with out_path.open("w", encoding="utf-8") as fh:
            for row in rows:
                fh.write(json.dumps(_transform_row(row), default=str) + "\n")
    elif fmt == "csv":
        if not rows:
            print("No rows to export (CSV requires at least one row to derive header)", file=sys.stderr)
            return 0
        first = _transform_row(rows[0])
        with out_path.open("w", encoding="utf-8", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=list(first.keys()))
            writer.writeheader()
            for row in rows:
                d = _transform_row(row)
                # CSV can't hold arrays — JSON-encode array columns
                d["tags"] = json.dumps(d["tags"])
                d["cve_ids"] = json.dumps(d["cve_ids"])
                d["source_systems"] = json.dumps(d["source_systems"])
                writer.writerow(d)
    else:
        print(f"Unknown format: {fmt!r} (must be jsonl or csv)", file=sys.stderr)
        return -1

    conn.close()
    return len(rows)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.strip().split("\n\n")[0])
    ap.add_argument("--db", type=Path, default=DEFAULT_DB,
                    help=f"Path to nuclide.db (default: {DEFAULT_DB})")
    ap.add_argument("--output", "-o", type=Path, default=Path("findings.jsonl"),
                    help="Output file path (default: findings.jsonl)")
    ap.add_argument("--format", choices=["jsonl", "csv"], default="jsonl",
                    help="Output format (default: jsonl). Parquet support pending pyarrow dep.")
    ap.add_argument("--since-id", type=int, default=0,
                    help="Only export rows with id > this value (delta by autoincrement). 0 = full export.")
    ap.add_argument("--since-updated-at", type=str, default=None,
                    help="Only export rows with updated_at > this ISO timestamp (delta by sync watermark).")
    args = ap.parse_args()

    if not args.db.exists():
        print(f"ERROR: db not found: {args.db}", file=sys.stderr)
        return 1

    n = export(args.db, args.output, args.format, args.since_id, args.since_updated_at)
    if n < 0:
        return 1
    filters = []
    if args.since_id: filters.append(f"since_id={args.since_id}")
    if args.since_updated_at: filters.append(f"since_updated_at={args.since_updated_at}")
    filter_str = ", " + ", ".join(filters) if filters else ""
    print(f"Exported {n} rows → {args.output} (format={args.format}{filter_str})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
