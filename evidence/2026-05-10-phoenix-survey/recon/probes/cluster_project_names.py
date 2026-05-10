#!/usr/bin/env python3
"""
Cluster Phoenix hosts by project-name fingerprint to find shared operators.

Two hosts owned by the same operator typically have identical or near-identical
project-name sets (e.g., Kapture CRM has 'Multi-Agent Engine' across 3 regions).
This script:
  1. Parses phoenix-projects-deep.tsv -> {host: sorted(project_names)}
  2. Drops hosts with only 'default' (too generic to cluster)
  3. Computes Jaccard similarity over name-sets
  4. Reports clusters where Jaccard >= 0.5 between any two hosts
"""
import json, sys
from itertools import combinations

PATH = "/home/cowboy/recon/2026-05-10-llm-sweep/phoenix/probes/phoenix-projects-deep.tsv"
GENERIC = {"default", "test", "demo", "evaluators"}

host_to_names = {}
host_to_meta = {}  # host -> total tokens, latest endTime

for line in open(PATH):
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
    names = []
    tokens = 0
    latest = ""
    for e in edges:
        n = e.get("node", {})
        names.append(n.get("name", ""))
        tokens += n.get("tokenCountTotal") or 0
        et = n.get("endTime") or ""
        if et > latest: latest = et
    host_to_names[url] = sorted(set(names))
    host_to_meta[url] = (tokens, latest, len(edges))

def signal_set(names):
    """Drop generic names; lowercase for matching."""
    return {n.lower() for n in names if n.lower() not in GENERIC and n.strip()}

def jaccard(a, b):
    if not a or not b: return 0.0
    return len(a & b) / len(a | b)

# Build clusters via union-find over edges with Jaccard >= 0.5
parent = {h: h for h in host_to_names}
def find(x):
    while parent[x] != x:
        parent[x] = parent[parent[x]]
        x = parent[x]
    return x
def union(a, b):
    ra, rb = find(a), find(b)
    if ra != rb: parent[ra] = rb

THRESHOLD = 0.5
edges_built = []
hosts = list(host_to_names.keys())
for h1, h2 in combinations(hosts, 2):
    s1 = signal_set(host_to_names[h1])
    s2 = signal_set(host_to_names[h2])
    if not s1 or not s2: continue
    j = jaccard(s1, s2)
    if j >= THRESHOLD:
        union(h1, h2)
        edges_built.append((h1, h2, j, sorted(s1 & s2)))

# Group by cluster root
clusters = {}
for h in hosts:
    r = find(h)
    clusters.setdefault(r, []).append(h)

# Report multi-host clusters
multi = [c for c in clusters.values() if len(c) >= 2]
multi.sort(key=lambda c: -sum(host_to_meta[h][0] for h in c))

print(f"=== Multi-host clusters (Jaccard >= {THRESHOLD} on non-generic project names) ===\n")
for i, cluster in enumerate(multi, 1):
    total_tokens = sum(host_to_meta[h][0] for h in cluster)
    print(f"Cluster #{i}: {len(cluster)} hosts | cumulative tokens: {total_tokens:,.0f}")
    for h in cluster:
        tk, lat, np_ = host_to_meta[h]
        names = host_to_names[h]
        print(f"  {h:<35} projs={np_:<3} tokens={tk:>14,.0f}  latest={lat[:10]}")
        print(f"      names: {names}")
    print()

# Hosts with project names not matching any cluster but are non-generic (singletons of interest)
print(f"\n=== Total hosts with non-generic names: {sum(1 for h in hosts if signal_set(host_to_names[h]))}")
print(f"=== Hosts with ONLY generic names ('default' etc): {sum(1 for h in hosts if not signal_set(host_to_names[h]))}")
print(f"=== Multi-host clusters found: {len(multi)}")
