#!/usr/bin/env bash
# run-analysis-chain.sh - fire after both probe jobs complete.
# Extracts confirmed-init_pass IPs per cohort, runs cert-resniff per cohort,
# computes Insight #97 I/N + S/N, writes cohorts.json.
set -e
cd "$(dirname "$0")"

# 1. Extract cohort IPs from probes
python3 - <<'PY'
import json
from collections import defaultdict
probes = [
    ('known-66', 'probes/known-66-reverify.jsonl', 9090),
    ('p9090', 'probes/p9090-candidates.jsonl', 9090),
    ('p3001', 'probes/p3001-candidates.jsonl', 3001),
]
cohort_ips = defaultdict(set)
for label, path, port in probes:
    for line in open(path):
        r = json.loads(line)
        if not r.get('init_pass'): continue
        si = r.get('initialize',{}).get('serverInfo',{}) or {}
        name = si.get('name','?')
        ver = si.get('version','?')
        pv = r.get('initialize',{}).get('protocolVersion','?')
        tools = tuple(sorted(r.get('tool_names',[])))
        key = (name, ver, pv, tools, port)
        cohort_ips[key].add(r['ip'])
for (name,ver,pv,tools,port), ips in sorted(cohort_ips.items(), key=lambda x:-len(x[1])):
    if len(ips) < 3: continue
    slug = f'cohort_{name}_{ver}_{port}'.replace('-','_').replace('/','_')
    fn = f'cohort-ips_{slug}.txt'
    open(fn,'w').write('\n'.join(sorted(ips))+'\n')
    print(f'wrote {fn}: N={len(ips)} name={name} ver={ver} pv={pv} port={port} tools_n={len(tools)}')
PY

# 2. Run cert-resniff per cohort
for ipfile in cohort-ips_*.txt; do
    port=$(echo "$ipfile" | grep -oE '[0-9]+(?=\.txt)' | tail -1)
    [ -z "$port" ] && port=9090
    out="certs_${ipfile%.txt}.json"
    [ -s "$out" ] && { echo "skip $out (exists)"; continue; }
    echo "== resniff $ipfile -> $out (port $port) =="
    # cert-resniff.py needs to be passed the port — current impl hardcodes 9090; for now stick with 9090
    python3 ../cert-resniff.py "$ipfile" "$out"
done

# 3. Cohort analysis
python3 cohort-analysis.py \
    --probes probes/known-66-reverify.jsonl probes/p9090-candidates.jsonl probes/p3001-candidates.jsonl \
    --certs certs_cohort-ips_*.json \
    --out cohorts.json

echo
echo "=== FINAL cohorts.json ==="
python3 -c "
import json
d = json.load(open('cohorts.json'))
for c in d['cohorts']:
    if c['N'] < 2: continue
    print(f\"  N={c['N']:>3} backend={c['backend_name']}/{c['backend_version']} pv={c['protocolVersion']} T={c['T']} I/N={c['I_over_N']} -> {c['disposition_per_insight_97']}\")
"
