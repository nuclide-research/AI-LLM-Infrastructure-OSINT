#!/usr/bin/env python3
"""Triage Phoenix unauth hosts: rank by data volume and recency."""
import sys, json, datetime

rows = []
for line in sys.stdin:
    line = line.rstrip("\n")
    if "\t" not in line: continue
    url, body = line.split("\t", 1)
    if not body or not body.startswith("{"): continue
    try:
        d = json.loads(body)
    except Exception:
        continue
    edges = d.get("data", {}).get("projects", {}).get("edges", [])
    if not edges: continue
    total_records = 0
    total_traces = 0
    total_tokens = 0
    project_names = []
    latest_end = None
    for e in edges:
        n = e.get("node", {})
        rc = n.get("recordCount") or 0
        tc = n.get("traceCount") or 0
        tk = n.get("tokenCountTotal") or 0
        nm = n.get("name") or ""
        et = n.get("endTime")
        total_records += rc
        total_traces += tc
        total_tokens += tk
        project_names.append(nm)
        if et:
            try:
                d2 = datetime.datetime.fromisoformat(et.replace("Z","+00:00"))
                if latest_end is None or d2 > latest_end:
                    latest_end = d2
            except Exception:
                pass
    rows.append({
        "url": url,
        "projects": len(edges),
        "names": project_names,
        "records": total_records,
        "traces": total_traces,
        "tokens": total_tokens,
        "latest": latest_end.isoformat() if latest_end else "",
    })

# Sort by tokens desc, then traces, then records
rows.sort(key=lambda r: (r["tokens"], r["traces"], r["records"]), reverse=True)

print(f"{'#':>3}  {'URL':<35} {'projs':>5} {'records':>9} {'traces':>8} {'tokens':>12}  {'latest':<25}  names")
print("-" * 140)
for i, r in enumerate(rows, 1):
    names = ",".join(r["names"][:4])
    if len(r["names"]) > 4:
        names += f" (+{len(r['names'])-4})"
    print(f"{i:>3}  {r['url']:<35} {r['projects']:>5} {r['records']:>9} {r['traces']:>8} {r['tokens']:>12}  {r['latest']:<25}  {names}")
print()
print(f"TOTAL: {len(rows)} hosts | non-empty: {sum(1 for r in rows if r['records']>0)} | with-tokens: {sum(1 for r in rows if r['tokens']>0)}")
