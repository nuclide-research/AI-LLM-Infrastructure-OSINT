#!/usr/bin/env python3
import sys, json
d = json.load(sys.stdin)
edges = d["data"]["project"]["spans"]["edges"]
for e in edges:
    n = e["node"]
    kind = n.get("spanKind") or "?"
    name = n.get("name") or ""
    sid = n.get("spanId") or ""
    print(f"{kind:10s} {name:40s} {sid}")
