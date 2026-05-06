#!/bin/bash
# cron-sync-clickhouse.sh — cron entrypoint for the nuclide.db -> ClickHouse
# delta sync (see reference/olap-migration.md §4.2).
#
# Sources the credentials env, invokes sync-clickhouse.py --execute, appends
# stdout/stderr to ~/.config/nuclide/clickhouse-sync.log with a UTC timestamp
# bracketing each run.
#
# Suggested crontab entry (every 10 min):
#   */10 * * * * /home/cowboy/AI-LLM-Infrastructure-OSINT/data/cron-sync-clickhouse.sh
#
# Manual invocation (same effect, immediate):
#   bash data/cron-sync-clickhouse.sh

set -euo pipefail

CREDS=$HOME/.config/nuclide/clickhouse-credentials.env
LOG=$HOME/.config/nuclide/clickhouse-sync.log
PYTHON=$HOME/security-tools/bin/python3
SCRIPT=$HOME/AI-LLM-Infrastructure-OSINT/data/sync-clickhouse.py

mkdir -p "$(dirname "$LOG")"

if [[ ! -f "$CREDS" ]]; then
  echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] ERROR: credentials file not found: $CREDS" >> "$LOG"
  exit 1
fi

if [[ ! -x "$PYTHON" ]]; then
  echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] ERROR: python interpreter not found: $PYTHON" >> "$LOG"
  exit 1
fi

set -a
# shellcheck disable=SC1090
. "$CREDS"
set +a

{
  echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] sync starting"
  "$PYTHON" "$SCRIPT" \
    --execute \
    --no-secure \
    --port  "$CLICKHOUSE_PORT" \
    --host  "$CLICKHOUSE_HOST" \
    --username "$CLICKHOUSE_USER" \
    --password "$CLICKHOUSE_PASSWORD" \
    --database "$CLICKHOUSE_DATABASE"
  rc=$?
  echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] sync finished (exit $rc)"
} >> "$LOG" 2>&1
