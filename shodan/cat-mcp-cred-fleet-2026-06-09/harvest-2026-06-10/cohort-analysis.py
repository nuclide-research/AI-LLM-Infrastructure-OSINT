#!/usr/bin/env python3
"""
cohort-analysis.py - Group probe results into B=1, T=1 cohorts and compute
Insight #97 I/N + S/N ratios.

Inputs:
  --probes path1.jsonl path2.jsonl ...   (mcp-initialize-probe.py output)
  --certs path1.json path2.json ...      (cert-resniff.py output, optional)

Output:
  cohorts.json with per-cohort: hosts, backend (serverInfo + protocolVersion),
  tools[], I, S, N, I/N, S/N, disposition.
"""
import argparse
import json
from collections import Counter, defaultdict


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--probes", nargs="+", required=True)
    ap.add_argument("--certs", nargs="*", default=[])
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    # Load probes
    probe_by_ip = {}
    for path in args.probes:
        for line in open(path):
            r = json.loads(line)
            if r.get("init_pass"):
                probe_by_ip[r["ip"]] = r

    # Load certs
    cert_by_ip = {}
    for path in args.certs:
        for r in json.load(open(path)):
            cert_by_ip[r["ip"]] = r

    # Group by (serverInfo.name, serverInfo.version, protocolVersion, sorted tools tuple)
    cohorts = defaultdict(list)
    for ip, r in probe_by_ip.items():
        si = r.get("initialize", {}).get("serverInfo", {}) or {}
        name = si.get("name", "?")
        ver = si.get("version", "?")
        pv = r.get("initialize", {}).get("protocolVersion", "?")
        tools = tuple(sorted(r.get("tool_names", [])))
        key = (name, ver, pv, tools)
        cohorts[key].append(ip)

    # Compute I/N + S/N per cohort
    out_cohorts = []
    for (name, ver, pv, tools), ips in sorted(cohorts.items(), key=lambda x: -len(x[1])):
        issuers = Counter()
        subjects = Counter()
        certs_seen = 0
        for ip in ips:
            c = cert_by_ip.get(ip, {})
            for k, v in c.items():
                if k.startswith("sni_") and isinstance(v, dict):
                    iss = v.get("issuer", {}).get("commonName") or v.get("issuer", {}).get("organizationName") or "?"
                    sub = v.get("subject", {}).get("commonName") or v.get("subject", {}).get("organizationName") or "?"
                    issuers[iss] += 1
                    subjects[sub] += 1
                    certs_seen += 1
                    break
        N = len(ips)
        I = len(issuers)
        S = len(subjects)
        in_ratio = I / certs_seen if certs_seen else None
        sn_ratio = S / certs_seen if certs_seen else None
        # Disposition rule from Insight #97 candidate
        if certs_seen and N >= 5:
            if in_ratio >= 0.30:
                disp = "HONEYPOT_CANDIDATE (I/N >= 0.30 with B=1 T=1)"
            elif in_ratio <= 0.05:
                disp = "LEGITIMATE_OPERATOR (I/N <= 0.05 with B=1 T=1)"
            else:
                disp = f"AMBIGUOUS (I/N = {in_ratio:.3f})"
        else:
            disp = "INSUFFICIENT_DATA"
        out_cohorts.append({
            "backend_name": name,
            "backend_version": ver,
            "protocolVersion": pv,
            "tools": list(tools),
            "T": len(tools),
            "N": N,
            "certs_seen": certs_seen,
            "I_distinct_issuers": I,
            "S_distinct_subjects": S,
            "I_over_N": in_ratio,
            "S_over_N": sn_ratio,
            "disposition_per_insight_97": disp,
            "ips_sample": ips[:10],
            "top_issuers": issuers.most_common(8),
            "top_subjects": subjects.most_common(8),
        })

    json.dump({"cohorts": out_cohorts, "total_init_pass_hosts": len(probe_by_ip)}, open(args.out, "w"), indent=2)
    print(f"[+] wrote {args.out}")
    print(f"[+] init_pass hosts: {len(probe_by_ip)}; distinct cohorts: {len(out_cohorts)}")
    for c in out_cohorts:
        if c["N"] >= 3:
            print(f"    N={c['N']:>3} B={c['backend_name']}/{c['backend_version']} pv={c['protocolVersion']} T={c['T']} I/N={c['I_over_N']} -> {c['disposition_per_insight_97']}")


if __name__ == "__main__":
    main()
