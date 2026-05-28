#!/usr/bin/env python3
"""Flag stale findings in Ollama state files.
A host is stale if last_probed is > STALE_DAYS days ago or missing.
Prints a report; does not modify files.
"""
import json, sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

STALE_DAYS = 30
DATA_DIR = Path(__file__).parent.parent / "data"

STATE_FILES = [
    "ollama-state.json",
    "ollama-state-fresh.json",
    "ollama-univ-state.json",
    "ollama-gov-state.json",
    "ollama-health-state.json",
    "ollama-inst-state.json",
]

NOW = datetime.now(timezone.utc)
CUTOFF = NOW - timedelta(days=STALE_DAYS)


def parse_date(s):
    if not s:
        return None
    for fmt in ("%Y-%m-%dT%H:%M:%S.%f", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"):
        try:
            dt = datetime.strptime(s[:19], fmt[:len(fmt)])
            return dt.replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    return None


def main():
    total = stale = fresh = no_date = 0
    stale_hosts = []

    for fname in STATE_FILES:
        path = DATA_DIR / fname
        if not path.exists():
            continue
        with open(path) as f:
            data = json.load(f)
        hosts = data if isinstance(data, dict) else {h.get('ip', str(i)): h for i, h in enumerate(data)}

        for ip, host in hosts.items():
            total += 1
            lp = host.get("last_probed") or host.get("last_seen") or host.get("first_seen")
            dt = parse_date(lp)
            if dt is None:
                no_date += 1
                stale_hosts.append({"ip": ip, "file": fname, "last_probed": None, "age_days": None})
            elif dt < CUTOFF:
                age = (NOW - dt).days
                stale += 1
                stale_hosts.append({"ip": ip, "file": fname, "last_probed": lp[:10], "age_days": age})
            else:
                fresh += 1

    print(f"Staleness report — threshold: {STALE_DAYS} days")
    print(f"  Total hosts:    {total}")
    print(f"  Fresh (<{STALE_DAYS}d):  {fresh}")
    print(f"  Stale (>{STALE_DAYS}d):  {stale}")
    print(f"  No date:        {no_date}")

    if stale_hosts:
        print(f"\nStale hosts (top 20):")
        for h in sorted(stale_hosts, key=lambda x: x["age_days"] or 9999, reverse=True)[:20]:
            age = f"{h['age_days']}d" if h['age_days'] else "no-date"
            print(f"  {h['ip']:<20}  {age:<8}  {h['file']}")

    if "--json" in sys.argv:
        print(json.dumps(stale_hosts, indent=2))


if __name__ == "__main__":
    main()
