#!/usr/bin/env python3
import sys, json
try:
    d = json.load(sys.stdin)
    rows = d.get("data", [])
    for p in rows[:15]:
        name = p.get("name", "") or ""
        pid = (p.get("id", "") or "")[:24]
        gid = p.get("gradient_start_color", "")
        tc = p.get("trace_count", "?")
        print(f"  proj: name={name[:40]:40s}  id={pid:24s}  traces={tc}")
    print(f"  TOTAL projects: {len(rows)}")
except Exception as e:
    txt = sys.stdin.read() if False else ""
    print(f"  parse error: {e}")
