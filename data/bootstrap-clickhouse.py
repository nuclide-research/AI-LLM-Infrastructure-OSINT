#!/usr/bin/env python3
"""
bootstrap-clickhouse.py — one-shot ClickHouse setup + initial load

Implements reference/olap-migration.md §3:
    1. Apply the schema from reference/olap-schema-clickhouse.sql.
    2. Load the full historical export from nuclide.db (via export-findings.py
       or a pre-existing JSONL) into the findings table.
    3. Run a sanity-check row-count comparison against SQLite.

Idempotent on the schema side (CREATE TABLE IF NOT EXISTS).
The data load is full-table by default. For ongoing sync use sync-clickhouse.py.

Usage:
    # Dry-run (default): describe what would happen, no ClickHouse calls.
    python3 bootstrap-clickhouse.py

    # Real bootstrap. Requires clickhouse-connect package + reachable host.
    python3 bootstrap-clickhouse.py --execute --host clickhouse.local --port 8443

    # Skip schema apply (assume already applied), only load data:
    python3 bootstrap-clickhouse.py --execute --skip-schema

    # Use a pre-exported JSONL instead of re-running the exporter:
    python3 bootstrap-clickhouse.py --execute --jsonl /tmp/findings.jsonl
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sqlite3
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent
DEFAULT_DB = REPO_ROOT / "data" / "nuclide.db"
DEFAULT_SCHEMA = REPO_ROOT / "reference" / "olap-schema-clickhouse.sql"
DEFAULT_EXPORTER = HERE / "export-findings.py"
DEFAULT_DATABASE = "nuclide"


def split_sql_statements(sql: str) -> list[str]:
    """Strip SQL comments + split on `;` boundaries."""
    no_comments = re.sub(r"--.*?$", "", sql, flags=re.MULTILINE)
    return [s.strip() for s in no_comments.split(";") if s.strip()]


def get_sqlite_count(db: Path) -> int:
    conn = sqlite3.connect(str(db))
    try:
        return conn.execute("SELECT COUNT(*) FROM events").fetchone()[0]
    finally:
        conn.close()


def export_full(db: Path) -> Path:
    tmpdir = Path(tempfile.mkdtemp(prefix="bootstrap-clickhouse-"))
    out = tmpdir / "findings.jsonl"
    rc = subprocess.run(
        [sys.executable, str(DEFAULT_EXPORTER), "--db", str(db), "--output", str(out)],
        check=False,
    ).returncode
    if rc != 0:
        raise RuntimeError(f"exporter failed (rc={rc})")
    return out


def count_rows(jsonl: Path) -> int:
    return sum(1 for _ in jsonl.open())


def apply_schema(client, sql_text: str) -> int:
    """Execute each statement; return count of statements applied."""
    statements = split_sql_statements(sql_text)
    for stmt in statements:
        if "CREATE TABLE" in stmt.upper():
            stmt = re.sub(r"CREATE\s+TABLE\s+", "CREATE TABLE IF NOT EXISTS ", stmt, count=1, flags=re.IGNORECASE)
        client.command(stmt)
    return len(statements)


def insert_full(client, jsonl: Path, table: str) -> int:
    n = 0
    batch: list[dict] = []
    BATCH_SIZE = 500
    with jsonl.open() as fh:
        for line in fh:
            try:
                batch.append(json.loads(line))
            except json.JSONDecodeError:
                continue
            if len(batch) >= BATCH_SIZE:
                client.insert(table, batch)
                n += len(batch)
                batch = []
    if batch:
        client.insert(table, batch)
        n += len(batch)
    return n


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.strip().split("\n\n")[0])
    ap.add_argument("--db", type=Path, default=DEFAULT_DB)
    ap.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA)
    ap.add_argument("--jsonl", type=Path, default=None,
                    help="Use existing JSONL instead of re-running export.")
    ap.add_argument("--execute", action="store_true",
                    help="Actually apply schema + load data. Default is dry-run.")
    ap.add_argument("--skip-schema", action="store_true",
                    help="Skip schema apply step (assume already done).")
    ap.add_argument("--skip-load",   action="store_true",
                    help="Skip data load step (schema-only bootstrap).")
    ap.add_argument("--host", default=os.environ.get("CLICKHOUSE_HOST", "localhost"))
    ap.add_argument("--port", type=int, default=int(os.environ.get("CLICKHOUSE_PORT", "8443")))
    ap.add_argument("--secure", action="store_true", default=True)
    ap.add_argument("--no-secure", dest="secure", action="store_false")
    ap.add_argument("--database", default=os.environ.get("CLICKHOUSE_DATABASE", DEFAULT_DATABASE))
    ap.add_argument("--table", default="findings")
    ap.add_argument("--username", default=os.environ.get("CLICKHOUSE_USER", "default"))
    ap.add_argument("--password", default=os.environ.get("CLICKHOUSE_PASSWORD", ""))
    args = ap.parse_args()

    print("=== bootstrap-clickhouse ===")
    print(f"  SQLite source:  {args.db}")
    print(f"  Schema file:    {args.schema}")
    print(f"  ClickHouse:     {args.host}:{args.port}/{args.database}.{args.table}")
    print(f"  Mode:           {'EXECUTE' if args.execute else 'DRY-RUN'}")

    sqlite_n = get_sqlite_count(args.db) if args.db.exists() else 0
    print(f"\n  SQLite events:  {sqlite_n} rows")

    if args.jsonl and args.jsonl.exists():
        jsonl = args.jsonl
        print(f"  Using JSONL:    {jsonl}")
    elif args.skip_load:
        jsonl = None
    else:
        print(f"\nExporting full table from SQLite ...")
        jsonl = export_full(args.db)
    if jsonl:
        print(f"  Export rows:    {count_rows(jsonl)}")

    if not args.execute:
        print("\n=== DRY-RUN ===")
        if not args.skip_schema:
            n = len(split_sql_statements(args.schema.read_text()))
            print(f"  Would apply {n} SQL statements from {args.schema.name}")
        if jsonl and not args.skip_load:
            print(f"  Would INSERT {count_rows(jsonl)} rows into {args.database}.{args.table}")
        print(f"  Would create database {args.database!r} if missing.")
        print("\nRe-run with --execute to apply.")
        return 0

    print("\n=== EXECUTING ===")
    try:
        import clickhouse_connect  # type: ignore
    except ImportError:
        print("ERROR: clickhouse-connect not installed. Try:\n"
              "    pip install clickhouse-connect", file=sys.stderr)
        return 1

    client = clickhouse_connect.get_client(
        host=args.host, port=args.port, secure=args.secure,
        username=args.username, password=args.password,
    )
    client.command(f"CREATE DATABASE IF NOT EXISTS {args.database}")
    client = clickhouse_connect.get_client(
        host=args.host, port=args.port, secure=args.secure,
        database=args.database, username=args.username, password=args.password,
    )

    if not args.skip_schema:
        print(f"Applying schema from {args.schema} ...")
        n_stmts = apply_schema(client, args.schema.read_text())
        print(f"  applied {n_stmts} statements")

    if not args.skip_load and jsonl:
        print(f"Loading {count_rows(jsonl)} rows into {args.database}.{args.table} ...")
        n_inserted = insert_full(client, jsonl, args.table)
        print(f"  inserted {n_inserted} rows")
        n_clickhouse = client.command(f"SELECT COUNT(*) FROM {args.table}")
        print(f"\nVerification:")
        print(f"  SQLite      = {sqlite_n}")
        print(f"  ClickHouse  = {n_clickhouse}")
        if n_clickhouse != sqlite_n:
            print(f"  WARNING: row counts do not match", file=sys.stderr)
            return 2

    print("\nBootstrap complete.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
