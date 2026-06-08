#!/usr/bin/env python3
"""Tally verify_results.jsonl into verdict buckets + version table."""

import json
from collections import Counter
from pathlib import Path

RES = Path(__file__).parent / "verify_results.jsonl"

verdicts = Counter()
versions = Counter()
khoj_rows = []

for line in RES.read_text().splitlines():
    r = json.loads(line)
    verdicts[r.get("verdict", "unknown")] += 1
    if r.get("khoj"):
        khoj_rows.append(r)
        v = r.get("version", "?")
        versions[v] += 1

print("=== VERDICT BUCKETS ===")
for v, n in verdicts.most_common():
    print(f"  {v}: {n}")

print(f"\n=== KHOJ CONFIRMED: {sum(1 for v in verdicts if v != 'dead' and v != 'fp_not_khoj') and len(khoj_rows)} ===")

for r in sorted(khoj_rows, key=lambda x: (x.get("verdict", ""), x["ip"])):
    ip = r["ip"]
    port = r["port"]
    verdict = r.get("verdict", "?")
    ver = r.get("version", "?")
    ac = r.get("agents_count", "-")
    au = r.get("automations_count", "-")
    us = r.get("user_status", "-")
    hs = r.get("health_status", "-")
    print(f"  {ip}:{port}  v={verdict}  ver={ver}  user={us}  health={hs}  agents={ac}  automations={au}")

print("\n=== VERSION DISTRIBUTION ===")
for v, n in versions.most_common():
    print(f"  {v}: {n}")

# Dump anon-marker rows with detail
print("\n=== DETAIL: high-interest rows ===")
for r in khoj_rows:
    if r.get("verdict") in ("unauth_khoj_confirmed", "single_user_mode"):
        ip = r["ip"]
        port = r["port"]
        v = r.get("verdict")
        print(f"\n  >>> {ip}:{port} [{v}]")
        print(f"      scheme={r.get('scheme')}  root_status={r.get('root_status')}  root_len={r.get('root_len')}")
        print(f"      health: {r.get('health')}")
        print(f"      user_keys: {r.get('user_keys')}")
        print(f"      anon_marker: {r.get('anon_marker')}")
        print(f"      agents_count: {r.get('agents_count')}  automations_count: {r.get('automations_count')}")
        print(f"      errors: {r.get('errors')}")
