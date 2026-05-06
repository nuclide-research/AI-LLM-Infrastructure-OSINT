#!/usr/bin/env python3
"""
sync-clickhouse.py — delta-sync nuclide.db -> ClickHouse

Implements reference/olap-migration.md §4.2: read the high-water mark from
state, export rows from nuclide.db where updated_at > watermark, INSERT
into ClickHouse, advance the watermark on success.

Requires the migrate-add-updated-at.py migration applied first; the
exporter uses --since-updated-at to filter.

Usage:
    # Default: dry-run. Shows what WOULD be synced; no ClickHouse calls.
    python3 sync-clickhouse.py

    # Real sync. Requires `clickhouse-connect` package + reachable host.
    python3 sync-clickhouse.py --execute --host clickhouse.local --port 8443

    # Reset watermark (force full re-sync next run).
    python3 sync-clickhouse.py --reset

State file:
    ~/.config/nuclide/clickhouse-sync-state.json
    {
      "last_synced_updated_at": "2026-05-06T01:23:45Z",
      "last_sync_attempt_at":   "2026-05-06T01:25:00Z",
      "last_sync_rows":         42,
      "last_sync_status":       "ok" | "failed:<reason>"
    }
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_DB = Path.home() / "AI-LLM-Infrastructure-OSINT" / "data" / "nuclide.db"
DEFAULT_EXPORTER = HERE / "export-findings.py"
STATE_DIR = Path.home() / ".config" / "nuclide"
STATE_FILE = STATE_DIR / "clickhouse-sync-state.json"
TABLE_NAME = "findings"

INITIAL_WATERMARK = "1970-01-01T00:00:00Z"


def utcnow_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def read_state() -> dict:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except json.JSONDecodeError:
            return {}
    return {}


def write_state(state: dict) -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2))
    os.chmod(STATE_FILE, 0o600)


def export_delta(db: Path, since: str) -> Path:
    """Run export-findings.py with the watermark; return path to JSONL."""
    tmpdir = Path(tempfile.mkdtemp(prefix="sync-clickhouse-"))
    out = tmpdir / "delta.jsonl"
    cmd = [
        sys.executable, str(DEFAULT_EXPORTER),
        "--db", str(db),
        "--output", str(out),
        "--since-updated-at", since,
    ]
    rc = subprocess.run(cmd, check=False).returncode
    if rc != 0:
        raise RuntimeError(f"exporter failed (rc={rc})")
    return out


def count_rows(jsonl: Path) -> int:
    return sum(1 for _ in jsonl.open()) if jsonl.exists() else 0


def latest_updated_at(jsonl: Path) -> str | None:
    """Return the max updated_at value across the delta rows, or None if empty."""
    latest: str | None = None
    if not jsonl.exists():
        return None
    with jsonl.open() as fh:
        for line in fh:
            try:
                d = json.loads(line)
                u = d.get("updated_at")
                if u and (latest is None or u > latest):
                    latest = u
            except json.JSONDecodeError:
                pass
    return latest


def insert_to_clickhouse(jsonl: Path, host: str, port: int, secure: bool,
                         database: str, table: str, username: str, password: str) -> int:
    """Real INSERT path. Requires clickhouse-connect package."""
    try:
        import clickhouse_connect  # type: ignore
    except ImportError:
        raise RuntimeError(
            "clickhouse-connect not installed. Try:\n"
            "    pip install clickhouse-connect\n"
            "(or install via the security-tools venv)."
        )

    client = clickhouse_connect.get_client(
        host=host, port=port, secure=secure,
        database=database, username=username, password=password,
    )

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
    ap.add_argument("--db", type=Path, default=DEFAULT_DB,
                    help=f"Path to nuclide.db (default: {DEFAULT_DB})")
    ap.add_argument("--execute", action="store_true",
                    help="Actually INSERT to ClickHouse. Default is dry-run.")
    ap.add_argument("--reset", action="store_true",
                    help="Reset the watermark to epoch (force full re-sync next run).")
    ap.add_argument("--host", default=os.environ.get("CLICKHOUSE_HOST", "localhost"))
    ap.add_argument("--port", type=int, default=int(os.environ.get("CLICKHOUSE_PORT", "8443")))
    ap.add_argument("--secure", action="store_true", default=True,
                    help="Use HTTPS (default true)")
    ap.add_argument("--no-secure", dest="secure", action="store_false",
                    help="Use plain HTTP (override --secure)")
    ap.add_argument("--database", default=os.environ.get("CLICKHOUSE_DATABASE", "nuclide"))
    ap.add_argument("--table", default=TABLE_NAME)
    ap.add_argument("--username", default=os.environ.get("CLICKHOUSE_USER", "default"))
    ap.add_argument("--password", default=os.environ.get("CLICKHOUSE_PASSWORD", ""))
    args = ap.parse_args()

    if args.reset:
        write_state({
            "last_synced_updated_at": INITIAL_WATERMARK,
            "last_sync_attempt_at":   utcnow_iso(),
            "last_sync_rows":         0,
            "last_sync_status":       "reset",
        })
        print(f"Watermark reset to {INITIAL_WATERMARK}.")
        return 0

    state = read_state()
    last = state.get("last_synced_updated_at", INITIAL_WATERMARK)
    print(f"State file:       {STATE_FILE}")
    print(f"Last synced:      {last}")

    print(f"\nExporting delta with --since-updated-at {last} ...")
    delta = export_delta(args.db, last)
    n = count_rows(delta)
    print(f"Delta rows:       {n}")

    if n == 0:
        print("Nothing to sync. State unchanged.")
        return 0

    new_watermark = latest_updated_at(delta) or last

    if not args.execute:
        print(f"\n=== DRY-RUN ===")
        print(f"Would INSERT {n} rows into ClickHouse table {args.database}.{args.table}")
        print(f"  host:      {args.host}:{args.port} (secure={args.secure})")
        print(f"  username:  {args.username}")
        print(f"  watermark: {last} -> {new_watermark}")
        print(f"  source:    {delta}")
        print("\nRe-run with --execute to apply.")
        return 0

    print(f"\n=== SYNCING ===")
    print(f"Target: {args.host}:{args.port}/{args.database}.{args.table}")
    try:
        inserted = insert_to_clickhouse(
            delta, args.host, args.port, args.secure,
            args.database, args.table, args.username, args.password,
        )
    except Exception as e:
        write_state({
            **state,
            "last_sync_attempt_at": utcnow_iso(),
            "last_sync_status":     f"failed:{type(e).__name__}:{str(e)[:120]}",
        })
        print(f"FAILED: {e}", file=sys.stderr)
        return 1

    write_state({
        **state,
        "last_synced_updated_at": new_watermark,
        "last_sync_attempt_at":   utcnow_iso(),
        "last_sync_rows":         inserted,
        "last_sync_status":       "ok",
    })
    print(f"Inserted {inserted} rows. Watermark advanced to {new_watermark}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
