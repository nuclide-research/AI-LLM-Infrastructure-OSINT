#!/usr/bin/env python3
"""ns-attribute -- namespace-taxonomy -> operator attribution clusterer.

A Kubecost/OpenCost cost API will happily hand an unauthenticated caller the
full namespace list of the cluster it is watching. Standard platform namespaces
(kube-system, cert-manager, the argo* family, ...) are noise -- every cluster
has them, so they carry zero attribution signal. What is left after you strip
that noise is the operator's *own* taxonomy: product names, business units,
internal service shorthand. Two clusters that share a distinctive slice of that
taxonomy are very likely run by the same operator, even when their cluster_id,
region, and provider differ (one operator, many clusters / many LBs).

Pipeline:
  1. Strip standard k8s/platform namespaces (overridable stoplist) and any
     '__'-prefixed pseudo-namespace (kubecost's __idle__ / __unmounted__).
  2. Build each host's DISTINCTIVE namespace set, compute pairwise Jaccard
     similarity, cluster hosts above --threshold into same-operator candidates
     (single-link / connected-components: an operator's clusters can drift, so
     transitive linkage is intended).
  3. Flag exact-duplicate signals across DIFFERENT IPs:
       - identical helmvalues_bytes  -> often the same cluster behind >1 LB
       - identical cluster_id        -> same-operator-multiple-clusters (weak
         on its own: 'cluster-one' is a Kubecost default, so it is reported
         but never treated as distinctive).
  4. Emit operator-candidate groups: shared distinctive tokens, member IPs,
     member cluster_ids, and a confidence score. Confidence is HIGH when the
     shared tokens are many AND rare across the corpus (rarity = inverse
     document frequency), LOW when few and/or common.

STDLIB ONLY. JSON for machines (--json), a human table by default.

Input: cost-API NDJSON. Each row needs at least 'ip' and 'namespaces' (list).
Optional and used when present: cluster_id, provider, region, helmvalues_bytes.
"""
import argparse
import json
import sys
from collections import defaultdict
from itertools import combinations

# --- Stoplist ---------------------------------------------------------------
# Standard k8s control-plane + ubiquitous platform/operator namespaces. These
# appear on clusters run by completely unrelated operators, so they are pure
# noise for attribution. Kept as an overridable set (--stoplist-add /
# --stoplist-file) because "common" varies by shop. Entries ending in '*' are
# prefix-globs (argo, argocd, argo-rollouts all collapse under 'argo*').
DEFAULT_STOPLIST = {
    # control plane / cluster defaults
    "kube-system", "kube-public", "kube-node-lease", "default",
    # cost tooling (the very thing exposing this data)
    "kubecost", "kubecost-ce", "kubecost2", "opencost",
    # observability
    "monitoring", "prometheus*", "loki", "grafana", "tempo", "thanos",
    "datadog", "elastic-system", "elk", "fluent*", "fluentbit", "fluentd",
    "logging", "victoria-metrics", "vmware-system*",
    # ingress / service mesh / cert
    "ingress-nginx", "ingress*", "nginx-ingress", "cert-manager",
    "istio*", "linkerd*", "kong", "traefik", "contour", "emissary*",
    "external-dns", "external-secrets", "metallb-system", "calico-system",
    "tigera-operator", "cilium*",
    # gitops / policy / lifecycle operators
    "argo*", "flux*", "kyverno", "gatekeeper*", "opa*", "olm",
    "operators", "operator-lifecycle-manager", "reloader", "keda",
    "karpenter", "cluster-autoscaler", "descheduler", "px-operator",
    "vault", "sealed-secrets", "spire*",
    # cloud-managed addon namespaces (provider noise, not operator signal)
    "amazon-cloudwatch", "amazon-guardduty", "amazon-network-flow-monitor",
    "aws-observability", "aws-for-fluent-bit", "gke-managed*",
    "gke-gmp-system", "azure-*", "calico-apiserver", "gmp-system",
    "gmp-public", "gke-connect", "config-management-system",
    "kube-prometheus-stack",
    # generic/scratch namespaces that carry no operator identity
    "default-cluster", "test", "testing", "uat", "staging", "dev", "develop",
    "guest", "workspace", "demo", "sandbox", "tmp", "temp",
}

# cluster_id values that are vendor defaults / placeholders -- present across
# many unrelated operators, so an identical cluster_id here means nothing.
GENERIC_CLUSTER_IDS = {
    "cluster-one", "default-cluster", "eks-workshop", "ovh-mks-test",
    "opencost-demo", "aks-containerhub",
}


def load_rows(path):
    """Read NDJSON; tolerate blank lines and trailing junk. One dict per host."""
    rows = []
    fh = sys.stdin if path == "-" else open(path, "r", encoding="utf-8")
    try:
        for ln, line in enumerate(fh, 1):
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError as e:
                print(f"  [warn] skipping malformed line {ln}: {e}", file=sys.stderr)
                continue
            if "ip" not in obj:
                continue
            rows.append(obj)
    finally:
        if fh is not sys.stdin:
            fh.close()
    return rows


def build_stoplist(extra=None, file_path=None):
    sl = set(DEFAULT_STOPLIST)
    if file_path:
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                t = line.strip()
                if t and not t.startswith("#"):
                    sl.add(t.lower())
    if extra:
        for t in extra:
            sl.add(t.strip().lower())
    return sl


def _stopped(token, exact, prefixes):
    """True if token is platform noise: exact match or matches a '*' prefix."""
    if token in exact:
        return True
    for p in prefixes:
        if token.startswith(p):
            return True
    return False


def distinctive_set(namespaces, stoplist):
    """Operator-identifying namespaces only.

    Drops '__'-prefixed pseudo-namespaces (kubecost __idle__/__unmounted__) and
    anything in the stoplist (exact or prefix-glob). Lowercased + deduped.
    """
    exact = {s for s in stoplist if not s.endswith("*")}
    prefixes = tuple(s[:-1] for s in stoplist if s.endswith("*"))
    out = set()
    for ns in namespaces or []:
        if not isinstance(ns, str):
            continue
        tok = ns.strip().lower()
        if not tok or tok.startswith("__"):
            continue
        if _stopped(tok, exact, prefixes):
            continue
        out.add(tok)
    return out


def jaccard(a, b):
    if not a and not b:
        return 0.0
    inter = len(a & b)
    union = len(a | b)
    return inter / union if union else 0.0


def connected_components(n, edges):
    """Union-find over edge list -> list of index groups (size>=1 collapsed)."""
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(x, y):
        rx, ry = find(x), find(y)
        if rx != ry:
            parent[rx] = ry

    for i, j in edges:
        union(i, j)
    comp = defaultdict(list)
    for i in range(n):
        comp[find(i)].append(i)
    return list(comp.values())


def token_rarity(hosts):
    """Document-frequency per distinctive token across all hosts.

    rarity(token) = 1 - df(token)/N. A token on 1 of 40 hosts is rare (~0.975);
    one on 30 of 40 is common (~0.25). Drives the confidence score: shared
    tokens that are rare corpus-wide are strong same-operator evidence; shared
    tokens that show up everywhere are weak.
    """
    n = len(hosts)
    df = defaultdict(int)
    for h in hosts:
        for tok in h["distinctive"]:
            df[tok] += 1
    rarity = {tok: 1.0 - (c / n) for tok, c in df.items()} if n else {}
    return rarity, df


def score_group(shared_tokens, rarity):
    """Confidence from count + rarity of shared distinctive tokens.

    strength = sum of token rarities (a rare token contributes ~1.0, a common
    one ~0.0). Banded so a human can sort on it:
      >=4.0 -> high     (many rare tokens, e.g. the 7-token SASE pair ~6.8)
      >=2.0 -> medium
       <2.0 -> low
    """
    if not shared_tokens:
        return 0.0, "low"
    strength = sum(rarity.get(t, 1.0) for t in shared_tokens)
    if strength >= 4.0:
        band = "high"
    elif strength >= 2.0:
        band = "medium"
    else:
        band = "low"
    return round(strength, 3), band


def cluster_hosts(hosts, threshold, rarity, rarity_link=4.0):
    """Pairwise linkage over distinctive sets -> connected-component groups.

    Two linkage signals, OR'd together:

      1. Raw Jaccard >= threshold. Catches near-identical taxonomies (an
         operator's clusters that look alike, or one cluster behind two LBs).

      2. Rarity-weighted shared mass >= rarity_link. This is the load-bearing
         one. Same operator, different *product* clusters share a distinctive
         core (aicore/common/sdwan/nvo/oms/xcd/numaflow-system) but each cluster
         also carries cluster-local namespaces (gdc/portal vs g2r1/kafka) that
         crater the symmetric Jaccard -- 7 shared tokens out of a 25-token union
         is only 0.28. Yet those 7 tokens appear on *no other host in the
         corpus* (df=3, rarity ~0.955 each). Seven near-unique shared tokens is
         overwhelming same-operator evidence regardless of union size. Weighting
         the shared intersection by corpus rarity recovers the link without
         opening the door to "many shared *common* tokens" false positives: a
         pile of generic shared tokens sums to a low mass and never crosses the
         cutoff. This is why the clusterer needs corpus-wide rarity, not just a
         pairwise set metric.

    Singletons are dropped from the operator-group output (a lone host is not a
    cluster), but they remain available for the exact-duplicate scan, which is a
    different signal entirely.
    """
    n = len(hosts)
    edges = []
    pair_sims = {}
    for i, j in combinations(range(n), 2):
        si, sj = hosts[i]["distinctive"], hosts[j]["distinctive"]
        if not si or not sj:
            continue
        sim = jaccard(si, sj)
        shared = si & sj
        rmass = sum(rarity.get(t, 1.0) for t in shared)
        if sim >= threshold or rmass >= rarity_link:
            edges.append((i, j))
            pair_sims[(i, j)] = round(sim, 3)

    comps = connected_components(n, edges)
    groups = []
    for comp in comps:
        if len(comp) < 2:
            continue
        members = [hosts[i] for i in comp]
        # Shared distinctive tokens = intersection across ALL members. For a
        # drifted multi-host operator this can be small; the union is reported
        # too so the analyst sees the full taxonomy footprint.
        sets = [m["distinctive"] for m in members]
        shared = set.intersection(*sets) if sets else set()
        union = set.union(*sets) if sets else set()
        strength, band = score_group(shared, rarity)
        # internal cohesion: min pairwise sim within the component
        sims = []
        for a, b in combinations(comp, 2):
            key = (a, b) if a < b else (b, a)
            if key in pair_sims:
                sims.append(pair_sims[key])
        groups.append({
            "member_ips": sorted(m["ip"] for m in members),
            "member_cluster_ids": sorted({m["cluster_id"] for m in members if m["cluster_id"]}),
            "shared_distinctive_tokens": sorted(shared),
            "shared_token_count": len(shared),
            "union_distinctive_tokens": sorted(union),
            "confidence_strength": strength,
            "confidence": band,
            "min_pairwise_jaccard": round(min(sims), 3) if sims else None,
        })
    groups.sort(key=lambda g: (-g["confidence_strength"], -len(g["member_ips"])))
    return groups


def exact_duplicate_signals(hosts):
    """Group different IPs by identical helmvalues_bytes and identical cluster_id.

    Two interpretations the analyst must disambiguate:
      - identical helmvalues_bytes : likely ONE cluster behind multiple load
        balancers (the helm values blob is byte-for-byte identical). High value
        but small byte counts (e.g. 25 = an error/empty body) are excluded
        because they collide across unrelated hosts.
      - identical cluster_id       : either same operator running multiple
        clusters with a shared naming scheme, OR a vendor default. Generic
        cluster_ids (cluster-one, default-cluster, ...) are excluded.
    """
    by_bytes = defaultdict(list)
    by_cid = defaultdict(list)
    for h in hosts:
        hb = h["helmvalues_bytes"]
        # Skip null and trivially-small blobs (25 bytes is a stub error body
        # seen across many unrelated hosts -- not a real fingerprint).
        if isinstance(hb, int) and hb > 1000:
            by_bytes[hb].append(h["ip"])
        cid = h["cluster_id"]
        if cid and cid.lower() not in GENERIC_CLUSTER_IDS:
            by_cid[cid].append(h["ip"])

    helm_dups = [
        {"helmvalues_bytes": b, "member_ips": sorted(ips),
         "interpretation": "same cluster behind multiple LBs (identical helm values blob)"}
        for b, ips in by_bytes.items() if len(ips) > 1
    ]
    helm_dups.sort(key=lambda d: (-len(d["member_ips"]), -d["helmvalues_bytes"]))

    cid_dups = [
        {"cluster_id": c, "member_ips": sorted(ips),
         "interpretation": "same operator, multiple clusters (shared non-default cluster_id)"}
        for c, ips in by_cid.items() if len(ips) > 1
    ]
    cid_dups.sort(key=lambda d: -len(d["member_ips"]))
    return helm_dups, cid_dups


def normalize(rows):
    """Project raw rows into the minimal host record the clusterer needs."""
    hosts = []
    for r in rows:
        hosts.append({
            "ip": r.get("ip"),
            "cluster_id": r.get("cluster_id"),
            "provider": r.get("provider"),
            "region": r.get("region"),
            "helmvalues_bytes": r.get("helmvalues_bytes"),
            "namespaces": r.get("namespaces") or [],
        })
    return hosts


def build_report(hosts, threshold, stoplist, rarity_link=4.0):
    for h in hosts:
        h["distinctive"] = distinctive_set(h["namespaces"], stoplist)
    rarity, df = token_rarity(hosts)
    groups = cluster_hosts(hosts, threshold, rarity, rarity_link=rarity_link)
    helm_dups, cid_dups = exact_duplicate_signals(hosts)
    return {
        "summary": {
            "hosts": len(hosts),
            "hosts_with_distinctive_ns": sum(1 for h in hosts if h["distinctive"]),
            "threshold": threshold,
            "rarity_link": rarity_link,
            "operator_candidate_groups": len(groups),
            "helmvalues_duplicate_clusters": len(helm_dups),
            "cluster_id_duplicate_clusters": len(cid_dups),
        },
        "operator_candidate_groups": groups,
        "helmvalues_duplicates": helm_dups,
        "cluster_id_duplicates": cid_dups,
    }


def print_table(report):
    s = report["summary"]
    print("=" * 72)
    print("ns-attribute  --  operator attribution from namespace taxonomy")
    print("=" * 72)
    print(f"hosts: {s['hosts']}  |  with distinctive ns: {s['hosts_with_distinctive_ns']}"
          f"  |  jaccard threshold: {s['threshold']}  |  rarity-link: {s['rarity_link']}")
    print(f"operator-candidate groups: {s['operator_candidate_groups']}"
          f"  |  helm-byte dup sets: {s['helmvalues_duplicate_clusters']}"
          f"  |  cluster_id dup sets: {s['cluster_id_duplicate_clusters']}")
    print()

    groups = report["operator_candidate_groups"]
    if groups:
        print("-- OPERATOR-CANDIDATE GROUPS " + "-" * 43)
        for i, g in enumerate(groups, 1):
            print(f"[{i}] confidence={g['confidence'].upper():<6} "
                  f"strength={g['confidence_strength']:<6} "
                  f"shared_tokens={g['shared_token_count']} "
                  f"min_jaccard={g['min_pairwise_jaccard']}")
            print(f"    IPs        : {', '.join(g['member_ips'])}")
            print(f"    cluster_ids: {', '.join(g['member_cluster_ids']) or '(none)'}")
            print(f"    shared     : {{{', '.join(g['shared_distinctive_tokens'])}}}")
            print()
    else:
        print("-- OPERATOR-CANDIDATE GROUPS: none above threshold")
        print()

    helm = report["helmvalues_duplicates"]
    if helm:
        print("-- HELM-VALUES DUPLICATES (likely one cluster, many LBs) " + "-" * 16)
        for d in helm:
            print(f"    {d['helmvalues_bytes']} bytes -> {', '.join(d['member_ips'])}")
        print()

    cid = report["cluster_id_duplicates"]
    if cid:
        print("-- CLUSTER_ID DUPLICATES (same operator, many clusters) " + "-" * 17)
        for d in cid:
            print(f"    '{d['cluster_id']}' -> {', '.join(d['member_ips'])}")
        print()


def main():
    p = argparse.ArgumentParser(
        prog="ns-attribute",
        description="Cluster cost-API hosts into same-operator candidates from "
                    "their distinctive k8s namespace taxonomy.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="example:\n"
               "  ns-attribute.py finops-probe-results.ndjson\n"
               "  ns-attribute.py results.ndjson --threshold 0.6 --json\n"
               "  cat results.ndjson | ns-attribute.py -",
    )
    p.add_argument("input", help="cost-API NDJSON file (or '-' for stdin)")
    p.add_argument("-t", "--threshold", type=float, default=0.5,
                   help="min Jaccard similarity to link two hosts (default 0.5)")
    p.add_argument("--rarity-link", type=float, default=4.0,
                   help="alt linkage: sum of corpus-rarity over shared distinctive "
                        "tokens >= this also links two hosts, even below the Jaccard "
                        "threshold (default 4.0 -- catches same-operator clusters that "
                        "share a rare core but differ in cluster-local namespaces)")
    p.add_argument("--json", action="store_true",
                   help="emit machine-readable JSON instead of the human table")
    p.add_argument("--stoplist-add", default="",
                   help="comma-separated extra namespaces to treat as platform noise")
    p.add_argument("--stoplist-file",
                   help="file of extra stoplist namespaces, one per line (# comments ok)")
    p.add_argument("--show-stoplist", action="store_true",
                   help="print the effective stoplist and exit")
    args = p.parse_args()

    extra = [t for t in args.stoplist_add.split(",") if t.strip()] if args.stoplist_add else None
    stoplist = build_stoplist(extra=extra, file_path=args.stoplist_file)

    if args.show_stoplist:
        print(json.dumps(sorted(stoplist), indent=2))
        return 0

    rows = load_rows(args.input)
    if not rows:
        print("no usable rows (need at least 'ip' + 'namespaces')", file=sys.stderr)
        return 1

    hosts = normalize(rows)
    report = build_report(hosts, args.threshold, stoplist, rarity_link=args.rarity_link)

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print_table(report)
    return 0


if __name__ == "__main__":
    sys.exit(main())
