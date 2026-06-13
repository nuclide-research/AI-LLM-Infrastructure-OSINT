#!/usr/bin/env python3
"""ipmap — per-IP investigation harness for a NuClide survey.

Fuses every per-host data source into one dossier and clusters hosts by operator:
  Shodan /host SSR dossier (org/isp/asn/geo/ports/cves/hostnames)
  + active scanner banners (liveness, fresh versions)
  + aimap deep-enum (AI service identity, auth_status, risk)
  + reverse + forward DNS
  + platform / honeypot tags
-> per_ip_map.json + ip-map.md, grouped by (ASN, /24) operator cluster, sector-flagged.

Restraint: metadata only. No content fetched here beyond DNS + the already-collected banners.
Reusable: drop the standard survey artifacts in CWD and run.
"""
import json, os, socket, ipaddress, re, subprocess
from collections import defaultdict

def load(p, default):
    return json.load(open(p)) if os.path.exists(p) else default

def load_jsonl(p):
    return [json.loads(l) for l in open(p)] if os.path.exists(p) else []

dossiers = load('shodan_dossiers.json', {})
scan = load_jsonl('scan_results.jsonl')
idx = load('master_ip_index.json', {})
hostsj = load('hosts.json', {'hosts': []})
title = {h['ip']: h.get('title', '') for h in hostsj.get('hosts', [])}

# aimap reports (merge all)
aimap_svc, aimap_enum = {}, {}
for f in ['aimap_report.json', 'aimap_vanna_verba.json', 'aimap_fastgpt_attu.json', 'aimap_datalayer.json']:
    d = load(f, {})
    for s in (d.get('services') or []):
        aimap_svc.setdefault(s['host'], []).append({'port': s['port'], 'service': s['service'],
                                                    'version': s.get('version', ''), 'severity': s.get('severity', '')})
    for e in (d.get('enum_results') or []):
        aimap_enum.setdefault(e['host'], []).append({'port': e['port'], 'service': e['service'],
                                                     'auth': e.get('auth_status', ''), 'risk': e.get('risk_level', '')})

scan_ports = defaultdict(list)
for r in scan:
    if (r.get('banner') or '').strip():
        scan_ports[r['ip']].append({'port': r['port'], 'server': (r.get('banner') or '')[:60].split('\n')[0]})

DATA_LAYER = {6333: 'Qdrant', 6334: 'Qdrant-gRPC', 11434: 'Ollama', 19530: 'Milvus', 9091: 'Milvus-metrics',
              3306: 'MySQL', 5432: 'Postgres', 6379: 'Redis', 9200: 'Elasticsearch', 9000: 'MinIO/S3',
              27017: 'Mongo', 5984: 'CouchDB', 8123: 'ClickHouse', 1200: 'unknown-1200'}
SECTOR = {'health': r'health|clinic|med|hospital|pharma|patient|noharm|健康|医疗',
          'gov': r'\.gov|\.gouv|\.gob|govern|ministr|\.mil',
          'edu': r'\.edu|\.ac\.|univers|college|school',
          'finance': r'bank|finan|invest|capital|insur|pay|trading|fintech',
          'industrial': r'industr|factory|tq-industrial|manufactur|scada'}

def rdns(ip):
    try:
        socket.setdefaulttimeout(3); return socket.gethostbyaddr(ip)[0]
    except Exception:
        return ''

def fwd(host):
    try:
        socket.setdefaulttimeout(3); return socket.gethostbyname(host)
    except Exception:
        return ''

def slash24(ip):
    return str(ipaddress.ip_network(ip + '/24', strict=False).network_address)

records = {}
for ip in sorted(idx, key=lambda s: tuple(int(x) for x in s.split('.'))):
    dos = dossiers.get(ip, {})
    meta = idx.get(ip, {})
    ptr = rdns(ip)
    hostnames = sorted(set([h for h in dos.get('hostnames', []) if '.' in h and not h.endswith('clients')] + ([ptr] if ptr else [])))
    # forward-confirm hostnames (do they resolve back?)
    fwd_match = [h for h in hostnames if fwd(h) == ip]
    text = ' '.join([title.get(ip, '')] + hostnames + [dos.get('org', '')]).lower()
    sectors = [s for s, rx in SECTOR.items() if re.search(rx, text)]
    data_layers = sorted({DATA_LAYER[p] for p in dos.get('ports', []) if p in DATA_LAYER}
                         | {DATA_LAYER[s['port']] for s in scan_ports.get(ip, []) if s['port'] in DATA_LAYER})
    records[ip] = {
        'ip': ip, 'platform': meta.get('platform'), 'honeypot_waf': meta.get('honeypot_waf', False),
        'title': title.get(ip, ''),
        'network': {'org': dos.get('org', ''), 'isp': dos.get('isp', ''), 'asn': dos.get('asn', ''),
                    'country': dos.get('country', ''), 'city': dos.get('city', ''), 'slash24': slash24(ip)},
        'dns': {'ptr': ptr, 'hostnames': hostnames, 'domains': dos.get('domains', []), 'forward_confirmed': fwd_match},
        'ports': {'shodan_seen': dos.get('ports', []), 'scanner_live': [s['port'] for s in scan_ports.get(ip, [])]},
        'ai_services': aimap_svc.get(ip, []),
        'auth_verdicts': aimap_enum.get(ip, []),
        'data_layers': data_layers,
        'cves': dos.get('cves', []),
        'sectors': sectors,
    }

# operator clustering: group by ASN + /24, and by shared registrable domain
clusters = defaultdict(list)
for ip, r in records.items():
    key = (r['network']['asn'] or '?', r['network']['slash24'])
    clusters[key].append(ip)
dom_clusters = defaultdict(list)
for ip, r in records.items():
    for d in r['dns']['domains']:
        dom_clusters[d].append(ip)

json.dump({'records': records,
           'operator_clusters_asn_24': {f"{k[0]}|{k[1]}": v for k, v in clusters.items() if len(v) > 1},
           'domain_clusters': {k: v for k, v in dom_clusters.items() if len(v) > 1}},
          open('per_ip_map.json', 'w'), indent=1)

# markdown map
lines = ["# Cat-34 Per-IP Map", "", f"55 hosts. Restraint: metadata only.", ""]
lines.append("## Operator clusters (ASN + /24, >1 host)")
for k, v in sorted(clusters.items(), key=lambda kv: -len(kv[1])):
    if len(v) > 1:
        r0 = records[v[0]]
        lines.append(f"- **{r0['network']['org']}** {k[0]} `{k[1]}/24` ({len(v)}): {', '.join(v)}")
lines.append("\n## Domain clusters (>1 host)")
for d, v in sorted(dom_clusters.items(), key=lambda kv: -len(kv[1])):
    if len(v) > 1:
        lines.append(f"- `{d}` ({len(v)}): {', '.join(v)}")
lines.append("\n## Sector-flagged hosts")
for ip, r in records.items():
    if r['sectors']:
        lines.append(f"- {ip} [{r['platform']}] {','.join(r['sectors'])} :: {r['title'][:40]} :: {', '.join(r['dns']['hostnames'][:2])}")
lines.append("\n## Hosts with exposed data layers")
for ip, r in records.items():
    if r['data_layers']:
        lines.append(f"- {ip} [{r['platform']}] {', '.join(r['data_layers'])}  (auth: {'; '.join(a['service']+'='+a['auth'] for a in r['auth_verdicts']) or 'n/a'})")
open('ip-map.md', 'w').write('\n'.join(lines) + '\n')

print(f"records: {len(records)}")
print(f"operator clusters (>1): {sum(1 for v in clusters.values() if len(v)>1)}")
print(f"domain clusters (>1): {sum(1 for v in dom_clusters.values() if len(v)>1)}")
print(f"sector-flagged: {sum(1 for r in records.values() if r['sectors'])}")
print(f"data-layer hosts: {sum(1 for r in records.values() if r['data_layers'])}")
print("written: per_ip_map.json, ip-map.md")
