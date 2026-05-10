#!/usr/bin/env python3
"""
Sample ONE span from a Phoenix project to characterize data class.

Usage: sample_one_span.py <base_url> <project_global_id>

Outputs span attributes (truncated) for data-class assessment.
"""
import sys, json, urllib.request, urllib.parse

if len(sys.argv) != 3:
    print("usage: sample_one_span.py <base_url> <project_global_id>", file=sys.stderr)
    sys.exit(2)

base, pid = sys.argv[1], sys.argv[2]

q = """
query($id: GlobalID!) {
  project: node(id: $id) {
    ... on Project {
      name
      spans(first: 1) {
        edges {
          node {
            name
            spanKind
            startTime
            endTime
            statusCode
            statusMessage
            attributes
          }
        }
      }
    }
  }
}
"""

body = json.dumps({"query": q, "variables": {"id": pid}}).encode()
req = urllib.request.Request(
    base.rstrip("/") + "/graphql",
    data=body,
    headers={"Content-Type": "application/json"},
    method="POST",
)
try:
    with urllib.request.urlopen(req, timeout=10) as r:
        d = json.loads(r.read())
except Exception as e:
    print(f"ERROR: {e}", file=sys.stderr)
    sys.exit(1)

p = d.get("data", {}).get("project") or {}
print(f"project: {p.get('name')}")
edges = p.get("spans", {}).get("edges", [])
if not edges:
    print("(no spans)")
    sys.exit(0)
n = edges[0]["node"]
print(f"span name: {n.get('name')}")
print(f"kind: {n.get('spanKind')}  status: {n.get('statusCode')}")
print(f"time: {n.get('startTime')} -> {n.get('endTime')}")
print()
attrs_raw = n.get("attributes")
if isinstance(attrs_raw, str):
    try:
        attrs = json.loads(attrs_raw)
    except Exception:
        attrs = {"_raw": attrs_raw}
else:
    attrs = attrs_raw or {}

# Print top-level keys + truncated values
def trunc(v, n=400):
    s = json.dumps(v) if not isinstance(v, str) else v
    return (s[:n] + f"...[{len(s)} chars]") if len(s) > n else s

print("=== attributes ===")
for k, v in attrs.items():
    print(f"  {k}: {trunc(v)}")
