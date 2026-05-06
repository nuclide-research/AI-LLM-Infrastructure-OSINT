#!/usr/bin/env python3
"""
migrate-add-updated-at.py — one-shot SQLite migration for nuclide.db

Adds an `updated_at` column to the events table for use as the OLAP-sync
high-water mark (see reference/olap-migration.md §4.1). Idempotent: safe
to re-run.

Steps:
    1. ALTER TABLE events ADD COLUMN updated_at TEXT (nullable; SQLite
       does not allow DEFAULT changes after add, so we backfill manually).
    2. UPDATE events SET updated_at = timestamp WHERE updated_at IS NULL
       (so historical rows have a meaningful, monotonic-with-creation
       value rather than "now()" at migration time).
    3. CREATE TRIGGER trg_events_updated_at_insert — populates on new
       inserts when the writer didn't set it.
    4. CREATE TRIGGER trg_events_updated_at_update — bumps to NOW() on
       any UPDATE that didn't already set it (lifecycle changes,
       severity reclassification, tag adds, etc.).

After this migration:
    - Sync watermark queries become `WHERE updated_at > :last_synced_at`.
    - VisorLog code does not need to change immediately — the triggers
      handle population of the column transparently.
    - When VisorLog gains explicit updated_at writes, the WHEN clause
      on the UPDATE trigger prevents double-bumping.

Usage:
    python3 migrate-add-updated-at.py                      # default db path
    python3 migrate-add-updated-at.py --db /path/to.db
    python3 migrate-add-updated-at.py --dry-run            # show plan, no changes
"""

from __future__ import annotations

import argparse
import sqlite3
import sys
from pathlib import Path

DEFAULT_DB = Path.home() / "AI-LLM-Infrastructure-OSINT" / "data" / "nuclide.db"


SQL_BACKFILL = "UPDATE events SET updated_at = timestamp WHERE updated_at IS NULL"

SQL_TRIGGER_INSERT = """
CREATE TRIGGER IF NOT EXISTS trg_events_updated_at_insert
AFTER INSERT ON events
WHEN NEW.updated_at IS NULL
BEGIN
    UPDATE events
       SET updated_at = NEW.timestamp
     WHERE id = NEW.id;
END
"""

SQL_TRIGGER_UPDATE = """
CREATE TRIGGER IF NOT EXISTS trg_events_updated_at_update
AFTER UPDATE ON events
WHEN OLD.updated_at = NEW.updated_at
BEGIN
    UPDATE events
       SET updated_at = strftime('%Y-%m-%dT%H:%M:%fZ', 'now')
     WHERE id = NEW.id;
END
"""

SQL_INDEX = "CREATE INDEX IF NOT EXISTS idx_updated_at ON events(updated_at)"


def column_exists(cur: sqlite3.Cursor, table: str, col: str) -> bool:
    rows = cur.execute(f"PRAGMA table_info({table})").fetchall()
    return any(r[1] == col for r in rows)


def trigger_exists(cur: sqlite3.Cursor, name: str) -> bool:
    row = cur.execute(
        "SELECT 1 FROM sqlite_master WHERE type='trigger' AND name=?", (name,)
    ).fetchone()
    return row is not None


def index_exists(cur: sqlite3.Cursor, name: str) -> bool:
    row = cur.execute(
        "SELECT 1 FROM sqlite_master WHERE type='index' AND name=?", (name,)
    ).fetchone()
    return row is not None


def migrate(db_path: Path, dry_run: bool) -> int:
    if not db_path.exists():
        print(f"ERROR: db not found: {db_path}", file=sys.stderr)
        return 1

    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()

    plan = []

    if not column_exists(cur, "events", "updated_at"):
        plan.append(("ADD COLUMN events.updated_at",
                     "ALTER TABLE events ADD COLUMN updated_at TEXT"))
    else:
        print("• events.updated_at already exists — skipping ADD COLUMN")

    null_rows = cur.execute(
        "SELECT COUNT(*) FROM events WHERE updated_at IS NULL"
    ).fetchone()[0] if column_exists(cur, "events", "updated_at") else None
    if null_rows is None:
        plan.append((f"BACKFILL existing rows (count to be determined post-add)",
                     SQL_BACKFILL))
    elif null_rows > 0:
        plan.append((f"BACKFILL {null_rows} rows where updated_at IS NULL",
                     SQL_BACKFILL))
    else:
        print("• no NULL updated_at rows — skipping BACKFILL")

    if not trigger_exists(cur, "trg_events_updated_at_insert"):
        plan.append(("CREATE TRIGGER trg_events_updated_at_insert",
                     SQL_TRIGGER_INSERT))
    else:
        print("• trg_events_updated_at_insert already exists — skipping")

    if not trigger_exists(cur, "trg_events_updated_at_update"):
        plan.append(("CREATE TRIGGER trg_events_updated_at_update",
                     SQL_TRIGGER_UPDATE))
    else:
        print("• trg_events_updated_at_update already exists — skipping")

    if not index_exists(cur, "idx_updated_at"):
        plan.append(("CREATE INDEX idx_updated_at",
                     SQL_INDEX))
    else:
        print("• idx_updated_at already exists — skipping")

    if not plan:
        print("\nMigration is up to date. Nothing to do.")
        conn.close()
        return 0

    print("\n=== migration plan ===")
    for label, _ in plan:
        print(f"  • {label}")

    if dry_run:
        print("\n(dry-run; no changes applied)")
        conn.close()
        return 0

    print("\n=== applying ===")
    for label, sql in plan:
        print(f"  → {label}")
        cur.executescript(sql)
    conn.commit()
    conn.close()
    print("\nDone.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.strip().split("\n\n")[0])
    ap.add_argument("--db", type=Path, default=DEFAULT_DB,
                    help=f"Path to nuclide.db (default: {DEFAULT_DB})")
    ap.add_argument("--dry-run", action="store_true",
                    help="Show migration plan; do not apply changes.")
    args = ap.parse_args()
    return migrate(args.db, args.dry_run)


if __name__ == "__main__":
    sys.exit(main())
