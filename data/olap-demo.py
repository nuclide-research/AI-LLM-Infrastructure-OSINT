#!/usr/bin/env python3
"""
olap-demo.py — runnable demo of the OLAP-backed tool query set

Validates the end-to-end pipeline today, no ClickHouse required:

    nuclide.db (SQLite)
        → export-findings.py
        → /tmp/findings.jsonl
        → DuckDB in-memory
        → the query set documented in reference/olap-tools-spec.md

Each section below corresponds to one of the OLAP-backed tools. The same
SQL shape (with parameter substitution) drops into ClickHouse when that
layer is deployed (see reference/olap-migration.md §3.3).

Usage:
    python3 olap-demo.py                           # default db + auto-export
    python3 olap-demo.py --jsonl /path/to.jsonl    # use existing export
    python3 olap-demo.py --window-days 90          # change window for trend queries

Requires:
    - DuckDB python module (`pip install duckdb`)
    - export-findings.py in the same directory (or pre-exported JSONL)
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

try:
    import duckdb  # type: ignore
except ImportError:
    print("ERROR: duckdb not installed. Try: pip install duckdb", file=sys.stderr)
    print("       (or use the security-tools venv if available)", file=sys.stderr)
    sys.exit(1)


HERE = Path(__file__).resolve().parent
DEFAULT_DB = Path.home() / "AI-LLM-Infrastructure-OSINT" / "data" / "nuclide.db"
DEFAULT_EXPORTER = HERE / "export-findings.py"


def section(title: str) -> None:
    print()
    print("=" * 72)
    print(title)
    print("=" * 72)


def print_table(rows: list[tuple], headers: list[str], widths: list[int] | None = None) -> None:
    if not rows:
        print("  (no rows)")
        return
    if widths is None:
        widths = [max(len(h), max(len(str(r[i])) for r in rows)) for i, h in enumerate(headers)]
    fmt = "  " + "  ".join(f"{{:<{w}}}" for w in widths)
    print(fmt.format(*headers))
    print("  " + "  ".join("-" * w for w in widths))
    for r in rows:
        print(fmt.format(*[str(c) for c in r]))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.strip().split("\n\n")[0])
    ap.add_argument("--db", type=Path, default=DEFAULT_DB,
                    help=f"Path to nuclide.db (default: {DEFAULT_DB})")
    ap.add_argument("--jsonl", type=Path, default=None,
                    help="Use this pre-exported JSONL instead of re-running export.")
    ap.add_argument("--window-days", type=int, default=90,
                    help="Window for trend queries (default 90)")
    args = ap.parse_args()

    # Step 1: get JSONL (either reuse or re-export)
    if args.jsonl and args.jsonl.exists():
        jsonl_path = args.jsonl
        print(f"Using existing JSONL: {jsonl_path}")
    else:
        if not DEFAULT_EXPORTER.exists():
            print(f"ERROR: exporter not found: {DEFAULT_EXPORTER}", file=sys.stderr)
            return 1
        tmpdir = Path(tempfile.mkdtemp(prefix="olap-demo-"))
        jsonl_path = tmpdir / "findings.jsonl"
        rc = subprocess.run(
            [sys.executable, str(DEFAULT_EXPORTER),
             "--db", str(args.db), "--output", str(jsonl_path)],
            check=False,
        ).returncode
        if rc != 0:
            print("ERROR: exporter failed", file=sys.stderr)
            return 1

    # Step 2: load into DuckDB
    con = duckdb.connect(":memory:")
    con.execute(
        f"CREATE TABLE findings AS "
        f"SELECT * FROM read_json('{jsonl_path}', format='newline_delimited', auto_detect=true)"
    )
    n = con.execute("SELECT COUNT(*) FROM findings").fetchone()[0]
    print(f"\nLoaded {n} rows into DuckDB.\n")

    # ------------------------------------------------------------------
    # Tool 1: get_auth_off_rates
    section("get_auth_off_rates(group_by=['platform_class'])")
    rows = con.execute("""
        SELECT
            platform_class,
            SUM(CASE WHEN auth_present = 0 THEN 1 ELSE 0 END) AS unauth_count,
            COUNT(*) AS total_count,
            ROUND(SUM(CASE WHEN auth_present = 0 THEN 1 ELSE 0 END) * 1.0 / COUNT(*), 3) AS auth_off_rate
        FROM findings
        WHERE platform_class != ''
        GROUP BY platform_class
        ORDER BY total_count DESC
    """).fetchall()
    print_table(rows, ["platform_class", "unauth", "total", "rate"])

    # ------------------------------------------------------------------
    # Tool 2: get_auth_off_rates by framework
    section("get_auth_off_rates(group_by=['framework'])")
    rows = con.execute("""
        SELECT
            framework,
            SUM(CASE WHEN auth_present = 0 THEN 1 ELSE 0 END) AS unauth_count,
            COUNT(*) AS total_count,
            ROUND(SUM(CASE WHEN auth_present = 0 THEN 1 ELSE 0 END) * 1.0 / COUNT(*), 3) AS auth_off_rate
        FROM findings
        WHERE framework != ''
        GROUP BY framework
        ORDER BY total_count DESC
        LIMIT 15
    """).fetchall()
    print_table(rows, ["framework", "unauth", "total", "rate"])

    # ------------------------------------------------------------------
    # Tool 3: get_disclosure_backlog
    section("get_disclosure_backlog(group_by=['severity_tier'])")
    rows = con.execute("""
        SELECT
            severity_tier,
            COUNT(*) AS backlog_count
        FROM findings
        WHERE disclosure_sent = 0
          AND status = 'open'
          AND severity_tier != ''
        GROUP BY severity_tier
        ORDER BY CASE severity_tier
            WHEN 'critical' THEN 1
            WHEN 'high'     THEN 2
            WHEN 'medium'   THEN 3
            WHEN 'low'      THEN 4
            ELSE 5 END
    """).fetchall()
    print_table(rows, ["severity_tier", "backlog_count"])

    # ------------------------------------------------------------------
    # Tool 4: get_multi_category_operators
    section("get_multi_category_operators(min_categories=2)")
    rows = con.execute("""
        SELECT
            org_name,
            COUNT(DISTINCT platform_class) AS classes_leaked,
            COUNT(*)                       AS findings_count
        FROM findings
        WHERE platform_class != '' AND org_name != ''
        GROUP BY org_name
        HAVING COUNT(DISTINCT platform_class) >= 2
        ORDER BY classes_leaked DESC, findings_count DESC
        LIMIT 10
    """).fetchall()
    print_table(rows, ["org_name", "classes_leaked", "findings_count"])
    if not rows:
        print("  Note: 0 results expected until VisorGraph cert-pivot is wired into")
        print("        ingest. Most current rows lack populated org_name beyond manual")
        print("        entries; the cert-pivot step is what fills this in for survey-ingested rows.")

    # ------------------------------------------------------------------
    # Tool 5: get_cve_distribution
    section("get_cve_distribution()")
    rows = con.execute("""
        SELECT
            cve_id,
            COUNT(*) AS finding_count
        FROM findings, UNNEST(cve_ids) AS t(cve_id)
        WHERE array_length(cve_ids) > 0
        GROUP BY cve_id
        ORDER BY finding_count DESC
        LIMIT 10
    """).fetchall()
    print_table(rows, ["cve_id", "finding_count"])

    # ------------------------------------------------------------------
    # Tool 6: get_reprobe_candidates
    section(f"get_reprobe_candidates(staleness_days={args.window_days})")
    rows = con.execute(f"""
        SELECT
            finding_id,
            ip,
            framework,
            severity_tier,
            last_verified_at
        FROM findings
        WHERE status != 'archived'
          AND DATE_DIFF('day', CAST(last_verified_at AS TIMESTAMP), CURRENT_TIMESTAMP) > {args.window_days}
        ORDER BY severity_tier, last_verified_at
        LIMIT 10
    """).fetchall()
    print_table(rows, ["finding_id", "ip", "framework", "severity", "last_verified"])

    # ------------------------------------------------------------------
    # Tool 7: top sectors by unauth count
    section("get_auth_off_rates(group_by=['sector'])")
    rows = con.execute("""
        SELECT
            sector,
            SUM(CASE WHEN auth_present = 0 THEN 1 ELSE 0 END) AS unauth_count,
            COUNT(*)                                          AS total_count,
            ROUND(SUM(CASE WHEN auth_present = 0 THEN 1 ELSE 0 END) * 1.0 / COUNT(*), 3) AS auth_off_rate
        FROM findings
        WHERE sector != ''
        GROUP BY sector
        ORDER BY total_count DESC
    """).fetchall()
    print_table(rows, ["sector", "unauth", "total", "rate"])

    print()
    print("Done. The same SQL shapes drop into ClickHouse with minor dialect")
    print("adjustments (CAST -> toType, DATE_DIFF -> dateDiff, etc.) per the")
    print("query templates in reference/olap-tools-spec.md.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
