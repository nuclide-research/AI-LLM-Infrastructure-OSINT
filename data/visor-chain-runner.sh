#!/bin/bash
# visor-chain-runner.sh — full 11-step NuClide chain over a list of IPs.
# Used after `jaxen import --no-lookup --source <slug> <shodan-export>` populates empire.db.
#
# Usage: bash visor-chain-runner.sh <slug>
# Reads /tmp/shodan-<slug>-hits.txt (one IP[:port] per line)
# Writes results to ~/recon/<slug>-<date>/
set -euo pipefail

DATE="$(date +%Y-%m-%d)"
SLUG="${1:-tei}"
HITS_FILE="/tmp/shodan-${SLUG}-hits.txt"
RECON_DIR="$HOME/recon/${SLUG}-${DATE}"
NUCLIDE_DB="$HOME/AI-LLM-Infrastructure-OSINT/data/nuclide.db"
AIMAP_PORTS="80,443,1984,2379,3000,3001,4000,4040,4200,5000,5001,5678,6333,7575,7576,7860,8000,8001,8080,8081,8123,8233,8265,8443,8501,8787,8888,8889,9000,9090,9091,10000,11434,15500,18080,18789,19530,30000,51000,55000"

if [[ ! -f "$HITS_FILE" ]]; then
  echo "ERROR: $HITS_FILE not found. Save Shodan dork export there first." >&2
  exit 1
fi

mkdir -p "$RECON_DIR"
cd "$RECON_DIR"

echo "=== STEP 0: jaxen import (manual Shodan export → empire.db) ==="
~/go/bin/jaxen import --no-lookup --source "shodan-${SLUG}-2026-05-06" "$HITS_FILE" 2>&1 | tail -3

# Extract just the IPs (strip ports, dedupe)
awk -F: '{print $1}' "$HITS_FILE" | sort -u > "$RECON_DIR/ips.txt"
echo "  → $(wc -l < "$RECON_DIR/ips.txt") unique IPs to process"

echo
echo "=== STEP 1a: visorplus assess (6-phase passive recon per host) ==="
mkdir -p "$RECON_DIR/visorplus"
while read -r ip; do
  cd "$RECON_DIR/visorplus" && ~/go/bin/visorplus assess "$ip" 2>&1 | tail -30 > "${ip}.log" 2>&1 || true
done < "$RECON_DIR/ips.txt"
cd "$RECON_DIR"
echo "  → $(ls "$RECON_DIR/visorplus/" 2>/dev/null | wc -l) visorplus assess logs"

echo
echo "=== STEP 1b: aimap (canonical fingerprint + deep enum, batch mode) ==="
~/go/bin/aimap -list "$RECON_DIR/ips.txt" -ports "$AIMAP_PORTS" -o "$RECON_DIR/aimap-report.json" -threads 30 2>&1 | tail -5

echo
echo "=== STEP 2: visorgraph cert pivot per host ==="
mkdir -p "$RECON_DIR/visorgraph"
while read -r ip; do
  out="$RECON_DIR/visorgraph/${ip//\//_}.json"
  ~/go/bin/visorgraph -ip "$ip" 2>/dev/null | tail -200 > "$out" 2>&1 || echo "  (visorgraph error for $ip)"
done < "$RECON_DIR/ips.txt"
echo "  → $(ls "$RECON_DIR/visorgraph/" | wc -l) graphs written"

echo
echo "=== STEP 3: aimap-profile (target classification) per host ==="
mkdir -p "$RECON_DIR/profile"
while read -r ip; do
  python3 ~/ai-recon/aimap/aimap-profile/aimap_profile.py --target "$ip" --mode fast \
    -o "$RECON_DIR/profile/${ip}.json" 2>/dev/null || true
done < "$RECON_DIR/ips.txt"
echo "  → $(ls "$RECON_DIR/profile/" | wc -l) profiles"

echo
echo "=== STEP 4: JS-bundle extraction (fires only on hosts with web SPA — handled at write-up time) ==="
echo "  (skipped for batch; per-host JS extraction in case-study writeup)"

echo
echo "=== STEP 5: nuclide-contact per host ==="
mkdir -p "$RECON_DIR/contact"
while read -r ip; do
  python3 ~/AI-LLM-Infrastructure-OSINT/data/nuclide-contact.py --ip "$ip" --json 2>/dev/null \
    > "$RECON_DIR/contact/${ip}.json" 2>&1 || true
done < "$RECON_DIR/ips.txt"
echo "  → $(ls "$RECON_DIR/contact/" | wc -l) contacts resolved"

echo
echo "=== STEP 6: visorlog ingest from aimap report ==="
# Convert aimap JSON to NDJSON and ingest
python3 <<EOF
import json
report = json.load(open('$RECON_DIR/aimap-report.json'))
ndjson = []
for h in report.get('hosts', report.get('results', [])):
    ip = h.get('host') or h.get('ip')
    for m in h.get('matches', []):
        sev = m.get('severity', 'medium')
        platform = m.get('service') or m.get('name')
        ndjson.append({
            'host_ip': ip,
            'event_severity': sev,
            'event_category': 'discovery',
            'source': f"shodan-${SLUG}-${DATE}",
            'tags': ['AI', 'LLM', platform.upper() if platform else '', 'UNAUTH'],
            'notes': f"{platform} on port {m.get('port')} via {m.get('scheme','http')}://",
        })
open('$RECON_DIR/findings.ndjson', 'w').write('\n'.join(json.dumps(n) for n in ndjson))
print(f'  → {len(ndjson)} findings prepared for visorlog ingest')
EOF
~/go/bin/visorlog --db "$NUCLIDE_DB" ingest --format ndjson "$RECON_DIR/findings.ndjson" 2>&1 | tail -5

echo
echo "=== STEP 7: visorscuba assess ==="
~/go/bin/visorscuba assess --db "$NUCLIDE_DB" --json 2>&1 | python3 -c "
import json, sys
d = json.load(sys.stdin)
data = d if isinstance(d, list) else d.get('results', [])
critical = sum(1 for r in data if isinstance(r, dict) and any(v.get('criticality') == 'Critical' for v in r.get('Result', {}).get('violations', [])))
print(f'  → {len(data)} nodes assessed, {critical} with Critical violations')
"

echo
echo "=== STEP 8: BARE module ranking per finding ==="
mkdir -p "$RECON_DIR/bare"
# Aggregate findings into a single BARE input
python3 <<EOF
import json, os
findings = []
for line in open('$RECON_DIR/findings.ndjson'):
    f = json.loads(line)
    findings.append({
        'id': f"{f['host_ip']}-{f.get('source')}",
        'title': f.get('notes', '')[:120],
        'platform': '${SLUG}',
        'version': '',
        'port': 0,
        'description': f.get('notes', '')[:500],
        'cve': '',
        'severity': f['event_severity'],
        'source': f['source'],
    })
out = {'version': 1, 'scanner': 'nuclide', 'source': 'nuclide', 'findings': findings}
json.dump(out, open('$RECON_DIR/bare/input.json', 'w'))
print(f'  → BARE input prepared with {len(findings)} findings')
EOF
~/.local/bin/bare "$RECON_DIR/bare/input.json" --top 3 > "$RECON_DIR/bare/output.json" 2>&1 || true
echo "  → $(wc -c < "$RECON_DIR/bare/output.json") bytes BARE output"

echo
echo "=== STEP 9: VisorCorpus adversarial corpus ==="
~/go/bin/visorcorpus build -profile strict -type baseline -include "kb_exfiltration,system_prompt,config_secrets" -max 80 \
  -out "$RECON_DIR/visorcorpus.json" 2>&1 | tail -3

echo
echo "=== STEP 10: VisorRAG recall (prior findings on each host, no LLM call) ==="
mkdir -p "$RECON_DIR/visorrag"
while read -r ip; do
  ~/go/bin/visorrag recall --target "$ip" 2>&1 > "$RECON_DIR/visorrag/${ip}.txt" || true
done < "$RECON_DIR/ips.txt"
echo "  → $(ls "$RECON_DIR/visorrag/" 2>/dev/null | wc -l) recall reports"

echo
echo "=== STEP 11 (intentionally deferred): VisorAgent ==="
echo "  VisorAgent run --target / run --visorsd is *active LLM exploitation* —"
echo "  do not fire against real operator endpoints (crosses ethical-stop boundary)."
echo "  Use VisorAgent against controlled/test targets only:"
echo "    visoragent run --target http://localhost:11434 --corpus $RECON_DIR/visorcorpus.json"

echo
echo "=== ALL DONE ==="
echo "Artifacts: $RECON_DIR"
ls -la "$RECON_DIR/" | head -25
echo
echo "Tools fired:"
echo "  ✓ jaxen import --no-lookup (Step 0)"
echo "  ✓ visorplus assess (Step 1a)"
echo "  ✓ aimap -list (Step 1b)"
echo "  ✓ visorgraph -ip per host (Step 2)"
echo "  ✓ aimap-profile per host (Step 3)"
echo "  ✓ nuclide-contact per host (Step 5)"
echo "  ✓ visorlog ingest (Step 6)"
echo "  ✓ visorscuba assess (Step 7)"
echo "  ✓ bare rank (Step 8)"
echo "  ✓ visorcorpus build (Step 9)"
echo "  ✓ visorrag recall (Step 10)"
echo "  ⏭  visoragent (Step 11 — deferred for active-exploitation reasons)"
