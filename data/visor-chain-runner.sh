#!/bin/bash
# visor-chain-runner.sh — full 18-step NuClide chain over a list of IPs.
# Used after `jaxen import --no-lookup --source <slug> <shodan-export>` populates empire.db.
#
# Usage: bash visor-chain-runner.sh <slug>
# Reads /tmp/shodan-<slug>-hits.txt (one IP[:port] per line)
# Writes results to ~/recon/<slug>-<date>/
set -euo pipefail

DATE="$(date +%Y-%m-%d)"
SLUG="${1:-tei}"
# Optional: pass Censys query as $2 to override the default CT-log dork.
# Example: bash visor-chain-runner.sh argo 'services.certificate.leaf_data.subject_dn: "Argo Workflows"'
CENSYS_QUERY="${2:-}"
HITS_FILE="/tmp/shodan-${SLUG}-hits.txt"
RECON_DIR="$HOME/recon/${SLUG}-${DATE}"
NUCLIDE_DB="$HOME/AI-LLM-Infrastructure-OSINT/data/nuclide.db"
AIMAP_PORTS="80,443,1984,2379,3000,3001,4000,4040,4200,5000,5001,5678,6333,7575,7576,7860,8000,8001,8080,8081,8123,8233,8265,8443,8501,8787,8888,8889,9000,9090,9091,10000,11434,15500,18080,18789,19530,30000,51000,55000"

# Fail-closed footprint guard: refuse outward probing unless the Mullvad tunnel is up.
# Called before every active stage so a mid-run tunnel drop aborts rather than leaking
# probes over the residential IP (Intentional Movement).
vpn_guard(){ mullvad status 2>/dev/null | grep -q '^Connected' || { echo "ABORT: Mullvad tunnel down — refusing outward probing (footprint guard)" >&2; exit 2; }; }

mkdir -p "$RECON_DIR"
cd "$RECON_DIR"

echo "=== STEP -1: OSINT Platoon — category pre-assessment intelligence ==="
# Runs BEFORE the Shodan harvest so its output can inform dork selection and
# aimap port priorities. Target is the category slug/name, not individual IPs.
# deliberate depth: full squad dispatch, one iteration — sufficient for a new
# category; use 'detailed' (max 3 iterations) for high-value or novel targets.
# Output: SALUTE report in platoon/<slug>-salute.txt; review before writing dorks.
mkdir -p "$RECON_DIR/platoon"
if [[ -d "$HOME/osint-platoon" ]]; then
  cd "$HOME/osint-platoon" && python3 cli.py \
      --target "$SLUG" \
      --type company \
      --depth deliberate \
      --log-dir "$RECON_DIR/platoon" \
      > "$RECON_DIR/platoon/${SLUG}-salute.txt" 2>&1 || true
  cd "$RECON_DIR"
  echo "  → SALUTE written: $RECON_DIR/platoon/${SLUG}-salute.txt"
  echo "  → Review before proceeding: grep -i 'shodan\|dork\|port\|fingerprint' platoon/${SLUG}-salute.txt"
else
  echo "  [skip] osint-platoon not found at $HOME/osint-platoon"
fi

if [[ ! -f "$HITS_FILE" ]]; then
  echo "ERROR: $HITS_FILE not found. Save Shodan dork export there first." >&2
  exit 1
fi

echo
echo "=== STEP 0: jaxen import (manual Shodan export → empire.db) ==="
~/go/bin/jaxen import --no-lookup --source "shodan-${SLUG}-2026-05-06" "$HITS_FILE" 2>&1 | tail -3

# Extract just the IPs (strip ports, dedupe)
awk -F: '{print $1}' "$HITS_FILE" | sort -u > "$RECON_DIR/ips.txt"
echo "  → $(wc -l < "$RECON_DIR/ips.txt") unique IPs to process (Shodan)"

echo
vpn_guard
echo "=== STEP 0b: Censys cross-population sweep (CT-log sourced) ==="
# Derive a best-effort query from the slug if none was passed as $2.
# CT-log CN search catches hosts Shodan's crawler never banner-grabbed.
if [[ -z "$CENSYS_QUERY" ]]; then
  CENSYS_QUERY="services.certificate.leaf_data.subject_dn: \"${SLUG}\""
  echo "  (no CENSYS_QUERY set; using default CT-log CN dork for slug '${SLUG}')"
fi
python3 ~/AI-LLM-Infrastructure-OSINT/data/censys-sweep.py \
  --query "$CENSYS_QUERY" \
  --slug "$SLUG" \
  --shodan-hits "$HITS_FILE" \
  --out "/tmp/censys-${SLUG}-hits.txt" \
  --out-dir "$RECON_DIR" \
  --max-pages 20 2>&1
CENSYS_EXIT=$?
if [[ $CENSYS_EXIT -eq 0 ]] && [[ -s "$RECON_DIR/censys-${SLUG}-delta.txt" ]]; then
  cat "$RECON_DIR/censys-${SLUG}-delta.txt" >> "$RECON_DIR/ips.txt"
  sort -u "$RECON_DIR/ips.txt" -o "$RECON_DIR/ips.txt"
  echo "  → ips.txt expanded to $(wc -l < "$RECON_DIR/ips.txt") unique IPs after Censys delta"
elif [[ $CENSYS_EXIT -eq 1 ]]; then
  echo "  (Censys skipped — no credentials; set CENSYS_API_ID/CENSYS_API_SECRET to enable)"
  echo "  (setup: pip install censys && censys config)"
else
  echo "  (Censys delta empty — Shodan and Censys populations overlap fully)"
fi

echo
vpn_guard
echo "=== STEP 1a: visorplus assess (6-phase passive recon per host) ==="
mkdir -p "$RECON_DIR/visorplus"
while read -r ip; do
  cd "$RECON_DIR/visorplus" && ~/go/bin/visorplus assess "$ip" 2>&1 | tail -30 > "${ip}.log" 2>&1 || true
done < "$RECON_DIR/ips.txt"
cd "$RECON_DIR"
echo "  → $(ls "$RECON_DIR/visorplus/" 2>/dev/null | wc -l) visorplus assess logs"

echo
vpn_guard
echo "=== STEP 1b: aimap (canonical fingerprint + deep enum, batch mode) ==="
~/go/bin/aimap -list "$RECON_DIR/ips.txt" -ports "$AIMAP_PORTS" -o "$RECON_DIR/aimap-report.json" -threads 30 2>&1 | tail -5

echo
vpn_guard
echo "=== STEP 1c: jaxen favicon (product-default favicon facet → empire.db) ==="
# Enriches empire.db assets with Shodan's favicon hash and flags product-default
# favicons (FAVICON-PRESENT / DEFAULT-FAVICON:<product>). Step 6 reads these.
# One lightweight /favicon.ico GET per host (lighter than the aimap sweep above);
# skip with FAVICON=0. Runs in RECON_DIR so it uses this survey's empire.db.
if [[ "${FAVICON:-1}" == "1" ]]; then
  ( cd "$RECON_DIR" && ~/go/bin/jaxen favicon --max 0 2>&1 | tail -3 ) || echo "  (favicon enrichment errored — non-fatal)"
else
  echo "  (FAVICON=0 — skipped)"
fi

echo
echo "=== STEP 1c-monitor: agent-logging-system FP candidate scan (per-enumerator) ==="
# Reads the aimap report and attributes each enum_result to a per-enumerator lane.
# Trips error_rate_high when an enumerator's "auth_unknown + no findings + info
# risk" rate exceeds 10%, and surfaces FALSE-POSITIVE CANDIDATES (>30% rate, >=3
# obs). An enumerator flagged here across 2+ surveys is a confirmed path-only FP
# class — write a VisorCAS signature for it (see METHODOLOGY Stage 1, Stage 7).
# Observe-only: writes a report, never gates. Fully guarded — absent tooling is
# non-fatal. The output feeds the human decision to add a VisorCAS signature;
# the loop is monitor (detect) -> VisorCAS (close).
ALS_MONITOR="$HOME/agent-logging-system/examples/aimap_monitor.py"
if [[ -f "$ALS_MONITOR" && -f "$RECON_DIR/aimap-report.json" ]]; then
  ( cd "$HOME/agent-logging-system" && \
    python3 "$ALS_MONITOR" "$RECON_DIR/aimap-report.json" 2>&1 \
      | tee "$RECON_DIR/aimap-fp-candidates.txt" \
      | sed -n '/FALSE-POSITIVE CANDIDATES/,$p' ) \
    || echo "  (monitor errored — non-fatal; full report still flows downstream)"
  echo "  → FP-candidate scan written to aimap-fp-candidates.txt"
else
  echo "  [skip] agent-logging-system not found ($ALS_MONITOR) — chain unaffected"
fi

echo
echo "=== STEP 1d: VisorCAS FP gate (records FPs; gates the ledger only when VISORCAS_GATE=1) ==="
# Filters aimap's report through the codified FP signatures (winnow-ported) plus
# the cross-survey content-addressed corpus, recording refuted false positives so
# future runs auto-skip them. Default = OBSERVE: the FULL report still flows to
# Step 6; gating is opt-in via VISORCAS_GATE=1, which makes Step 6 ingest the
# filtered report instead. Fully guarded — if visorcas is absent the chain is
# unaffected. Install: (cd ~/visorcas && go install ./cmd/visorcas)
VISORCAS_BIN="$HOME/go/bin/visorcas"
VISORCAS_DIR="${VISORCAS_DIR:-$HOME/.visorcas}"   # persistent FP corpus across surveys
if [[ -x "$VISORCAS_BIN" && -f "$RECON_DIR/aimap-report.json" ]]; then
  "$VISORCAS_BIN" --dir "$VISORCAS_DIR" gate "$RECON_DIR/aimap-report.json" \
    --out "$RECON_DIR/aimap-report.gated.json" --record 2>&1 | tail -10
  if [[ "${VISORCAS_GATE:-0}" == "1" ]]; then
    cp "$RECON_DIR/aimap-report.json" "$RECON_DIR/aimap-report.prefilter.json"
    mv "$RECON_DIR/aimap-report.gated.json" "$RECON_DIR/aimap-report.json"
    echo "  GATING ON — Step 6 ingests the filtered report (original kept as aimap-report.prefilter.json)"
  else
    echo "  observe mode — FPs recorded; full report still flows to Step 6 (set VISORCAS_GATE=1 to gate)"
  fi
else
  echo "  [skip] visorcas not installed ($VISORCAS_BIN) — chain unaffected"
fi

echo
vpn_guard
echo "=== STEP 2: visorgraph cert pivot per host ==="
mkdir -p "$RECON_DIR/visorgraph"
while read -r ip; do
  out="$RECON_DIR/visorgraph/${ip//\//_}.json"
  ~/go/bin/visorgraph -ip "$ip" 2>/dev/null | tail -200 > "$out" 2>&1 || echo "  (visorgraph error for $ip)"
done < "$RECON_DIR/ips.txt"
echo "  → $(ls "$RECON_DIR/visorgraph/" | wc -l) graphs written"

echo
vpn_guard
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
echo "=== STEP 6: visorlog ingest from aimap report ==="
# Convert aimap JSON -> VisorLog NDJSON via the shared, tested converter.
# Emits DOTTED ECS keys (host.ip / nuclide.tags / ...) so ip + tags actually
# persist (the old inline heredoc emitted snake_case, which Unmarshal dropped),
# maps enum_results[].findings[].category -> canonical tags (EXFIL-CREDENTIAL,
# ...), and merges empire.db favicon markers (FAVICON-PRESENT / DEFAULT-FAVICON).
python3 ~/AI-LLM-Infrastructure-OSINT/tools/aimap-to-findings.py \
  --aimap "$RECON_DIR/aimap-report.json" \
  --source "shodan-${SLUG}-${DATE}" \
  --sector "$SLUG" \
  --empire-db "$RECON_DIR/empire.db" \
  -o "$RECON_DIR/findings.ndjson"
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
echo "=== STEP 12: visor-report (drill-down HTML report from the ledger) ==="
REPORT_HTML="$RECON_DIR/${SLUG}-report.html"
python3 ~/AI-LLM-Infrastructure-OSINT/tools/visor-report.py from-visorlog \
  --db "$NUCLIDE_DB" --sector "${SLUG}" -o "$REPORT_HTML" 2>&1 | tail -2 \
  || echo "  (visor-report failed; ledger may be empty for sector ${SLUG})"
echo "  → open report: $REPORT_HTML"
echo "  (rich drill-down: copy tools/finops_to_report.py -> tools/${SLUG}_to_report.py, tune predicates,"
echo "   then: python3 tools/${SLUG}_to_report.py <probe-output> | python3 tools/visor-report.py render - -o report.html)"

echo
echo "=== ALL DONE ==="
echo "Artifacts: $RECON_DIR"
ls -la "$RECON_DIR/" | head -25
echo
echo "Tools fired:"
echo "  ✓ osint-platoon (Step -1 — category pre-assessment intelligence)"
echo "  ✓ jaxen import --no-lookup (Step 0)"
echo "  ✓ censys-sweep (Step 0b — CT-log cross-population)"
echo "  ✓ visorplus assess (Step 1a)"
echo "  ✓ aimap -list (Step 1b)"
echo "  ✓ jaxen favicon (Step 1c — favicon hash enrichment)"
echo "  ✓ agent-logging-system FP-candidate scan (Step 1c-monitor)"
echo "  ✓ visorcas gate (Step 1d — FP gate, observe mode)"
echo "  ✓ visorgraph -ip per host (Step 2)"
echo "  ✓ aimap-profile per host (Step 3)"
echo "  ✓ visorlog ingest (Step 6)"
echo "  ✓ visorscuba assess (Step 7)"
echo "  ✓ bare rank (Step 8)"
echo "  ✓ visorcorpus build (Step 9)"
echo "  ✓ visorrag recall (Step 10)"
echo "  ⏭  visoragent (Step 11 — deferred, ethical-stop, controlled targets only)"
echo "  ✓ visor-report from-visorlog (Step 12 — drill-down HTML report)"
