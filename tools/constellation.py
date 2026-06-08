#!/usr/bin/env python3
"""
constellation — find operators appearing across multiple NuClide rollups.

Takes N harvest hosts.json files (Shodan extractions per survey) and identifies
operators present in 2+ corpora. Produces a multi-corpus operator ranking.

Insight #92 candidate (cross-platform co-deployment multiplier): operators
appearing in 2+ corpora are multiplied-risk because their disclosed data
layers compose, not concatenate.

USAGE
  constellation hunt <hosts.json>... --output report.json

Each hosts.json has the same shape as the glance-companion harvest output:
  [{ip, port, org, country, asn, hostnames, ...}, ...]
"""
import json, argparse, sys, ipaddress
from pathlib import Path
from collections import defaultdict, Counter

HOSTING_NOISE_FRAGMENTS = {
    'amazonaws','googleusercontent','azure','your-server','linodeusercontent',
    'oraclecloud','digitalocean','tencent-cloud','aliyuncs','huaweicloud',
    'yandex','do-user','contaboserver','startdedicated','vultrusercontent',
    'cluster.local','compute.internal','staticloud','ec2.internal','cdn77',
}

def domain_of(hn):
    parts = hn.lower().strip().split('.')
    if len(parts) >= 2:
        if parts[-2] in ('co','com','org','gov','edu','ac','go') and len(parts) >= 3:
            return '.'.join(parts[-3:])
        return '.'.join(parts[-2:])
    return hn


def slash_24(ip):
    try:
        return str(ipaddress.ip_network(f'{ip}/24', strict=False))
    except: return None


def load_corpus(path):
    """Load Shodan harvest JSON. Returns list of {ip, port, org, country, hostnames}."""
    raw = json.load(open(path))
    out = []
    if isinstance(raw, list):
        for h in raw:
            out.append({
                'ip': h.get('ip',''),
                'port': h.get('port'),
                'org': h.get('org','') or '',
                'country': h.get('country','') or '',
                'asn': h.get('asn','') or '',
                'hostnames': h.get('hostnames',[]) or [],
            })
    elif isinstance(raw, dict):  # chroma-shape: tiered dict
        for tier, hosts in raw.items():
            if not tier.startswith('TIER-'): continue
            for h in hosts:
                target = h.get('target','')
                if ':' in target:
                    ip, port = target.split(':',1)
                else:
                    ip, port = target, None
                hostnames = h.get('hostnames','')
                hns = [x.strip() for x in (hostnames.split(',') if hostnames else [])]
                out.append({
                    'ip': ip,
                    'port': int(port) if port and port.isdigit() else None,
                    'org': h.get('org','') or '',
                    'country': h.get('country','') or '',
                    'asn': h.get('asn','') or '',
                    'hostnames': hns,
                })
    return out


def hunt(corpora):
    """corpora is dict of {name: list-of-hosts}. Returns multi-corpus operator analysis."""
    by_ip = defaultdict(set)         # ip -> set of corpora names
    by_subnet = defaultdict(lambda: defaultdict(set))  # /24 -> corpus -> ips
    by_domain = defaultdict(lambda: defaultdict(set))   # eTLD+1 -> corpus -> ips
    ip_org = {}

    for name, hosts in corpora.items():
        for h in hosts:
            ip = h['ip']
            by_ip[ip].add(name)
            ip_org[ip] = h['org']
            s24 = slash_24(ip)
            if s24: by_subnet[s24][name].add(ip)
            for hn in h['hostnames']:
                if hn and '.' in hn:
                    d = domain_of(hn)
                    if d and not any(noise in d for noise in HOSTING_NOISE_FRAGMENTS):
                        by_domain[d][name].add(ip)

    # Same-IP multi-corpus
    same_ip = sorted(
        [(ip, list(c)) for ip, c in by_ip.items() if len(c) >= 2],
        key=lambda x: -len(x[1])
    )

    # Multi-corpus /24
    multi_subnet = sorted(
        [(s, {c: list(ips) for c, ips in d.items()}) for s, d in by_subnet.items() if len(d) >= 2],
        key=lambda x: -sum(len(v) for v in x[1].values())
    )

    # Multi-corpus domain
    multi_domain = sorted(
        [(d, {c: list(ips) for c, ips in cd.items()}) for d, cd in by_domain.items() if len(cd) >= 2],
        key=lambda x: -sum(len(v) for v in x[1].values())
    )

    return {
        'same_ip_multi_corpus': [{'ip': ip, 'corpora': c, 'org': ip_org.get(ip,'')} for ip, c in same_ip],
        'multi_corpus_subnets_count': len(multi_subnet),
        'multi_corpus_subnets_top10': multi_subnet[:10],
        'multi_corpus_domains_count': len(multi_domain),
        'multi_corpus_domains_top20': multi_domain[:20],
        'corpora_sizes': {n: len(h) for n, h in corpora.items()},
    }


def main():
    ap = argparse.ArgumentParser(prog='constellation')
    sub = ap.add_subparsers(dest='cmd', required=True)
    h = sub.add_parser('hunt')
    h.add_argument('hosts_files', nargs='+', help='hosts.json files; corpus name inferred from filename')
    h.add_argument('-o', '--output', help='write JSON report')
    h.add_argument('--names', help='comma-separated corpus names (override filename inference)')

    args = ap.parse_args()
    if args.cmd == 'hunt':
        corpora = {}
        names = args.names.split(',') if args.names else None
        for i, p in enumerate(args.hosts_files):
            name = names[i] if names and i < len(names) else Path(p).stem.replace('-hosts','').replace('hosts-','')
            corpora[name] = load_corpus(p)
        report = hunt(corpora)
        out = json.dumps(report, indent=2, default=str)
        if args.output:
            Path(args.output).write_text(out)
            print(f"-> {args.output}")
        # Pretty summary
        print("=== CONSTELLATION REPORT ===")
        for n, sz in report['corpora_sizes'].items():
            print(f"  corpus {n}: {sz} hosts")
        print(f"\nSame-IP multi-corpus operators: {len(report['same_ip_multi_corpus'])}")
        for x in report['same_ip_multi_corpus'][:10]:
            print(f"  {x['ip']:18}  corpora={x['corpora']}  org={x['org'][:40]}")
        print(f"\nMulti-corpus /24 subnets: {report['multi_corpus_subnets_count']}")
        print(f"Multi-corpus operator domains (filtered): {report['multi_corpus_domains_count']}")
        if report['multi_corpus_domains_top20']:
            print(f"\nTop multi-corpus domains:")
            for d, c in report['multi_corpus_domains_top20'][:10]:
                breakdown = ', '.join(f"{k}={len(v)}" for k,v in c.items())
                print(f"  {d:<40}  {breakdown}")

if __name__ == '__main__':
    main()
