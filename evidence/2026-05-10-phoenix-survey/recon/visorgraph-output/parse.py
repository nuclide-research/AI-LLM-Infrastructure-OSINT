#!/usr/bin/env python3
import json, sys
d = json.load(sys.stdin)
print("=== Nodes ===")
for nid, n in d["nodes"].items():
    val = n.get("value", "")
    typ = n.get("type", "")
    print(f"  [{nid}] type={typ} value={val}")
    attrs = n.get("attrs", {})
    if "exposure_reason" in attrs:
        print(f"      exposure: {attrs['exposure_reason'][:300]}")
    if "scrape_targets_count" in attrs:
        print(f"      scrape targets: {attrs['scrape_targets_count']}")
    if "scrape_topology" in attrs:
        try:
            topo = json.loads(attrs["scrape_topology"])
            for job, targets in topo.items():
                print(f"      job={job} targets={len(targets)}")
                for t in targets[:3]:
                    print(f"        - {t.get('url','?')}  ({t.get('health','?')})")
        except Exception as e:
            print(f"      topology parse error: {e}")
print()
print("=== Edges ===")
for eid, e in d.get("edges", {}).items():
    print(f"  [{eid}] {e}")
