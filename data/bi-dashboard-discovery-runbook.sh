#!/bin/bash
# bi-dashboard-discovery-runbook.sh — Masscan + aimap pipeline for the
# BI / Dashboard / Visualization tier survey.
# Platforms: Metabase (3000), Apache Superset (8088), Redash (5000), Grafana (3000)
#
# Methodology: aimap is the fingerprinter. Conjunctive matchers distinguish
# platforms sharing port 3000 (Metabase vs Grafana vs Open WebUI etc.).
# No bespoke Python probes — see Methodology Insight #6.
#
# Run as:  bash bi-dashboard-discovery-runbook.sh
# Requires: sudo (masscan), masscan, aimap

set -euo pipefail

RECON_DIR="$HOME/recon/bi-dashboard-tier2-$(date +%F)"
HONEYPOT_LIST="$HOME/recon/ollama-tier2-2026-05-04/as63949-honeypot-fleet.txt"
AIMAP_PORTS="80,443,1984,2379,3000,3001,4000,4040,4200,5000,5001,5678,6333,7575,7576,7860,8000,8001,8080,8081,8088,8123,8233,8265,8443,8501,8787,8888,8889,9000,9090,9091,10000,11434,15500,18080,18789,19530,30000,51000,55000"

# BI/Dashboard ports:
#   3000   Metabase, Grafana (collision — aimap conjunctive matcher separates them)
#   5000   Redash (also Flowise alt, aimap conjunctive matcher separates)
#   8088   Apache Superset (unique port, minimal collision)
SCAN_PORTS="3000,5000,8088"
RATE="10000"

mkdir -p "$RECON_DIR"
cd "$RECON_DIR"

echo "=== Step 1/5: gather tier-2 cloud /16 prefixes ==="
RANGES_FILE="$RECON_DIR/tier2-ranges.txt"
for candidate in \
  "$HOME/recon/browser-agent-tier2-2026-05-04/tier2-ranges.txt" \
  "$HOME/recon/llm-gateway-tier2-2026-05-04/tier2-ranges.txt" \
  "$HOME/recon/rag-framework-tier2-2026-05-04/tier2-ranges.txt" \
  "$HOME/recon/datalabel-tier2-2026-05-04/tier2-ranges.txt" \
  "/tmp/tier2-all-ranges.txt"; do
  if [[ -f "$candidate" ]]; then
    cp "$candidate" "$RANGES_FILE"
    echo "  reused: $candidate ($(wc -l < "$RANGES_FILE") prefixes)"
    break
  fi
done

if [[ ! -f "$RANGES_FILE" ]]; then
  echo "ERROR: no tier-2 ranges file found. Rebuild from Scaleway/OVH/Linode ASN prefix lists." >&2
  exit 1
fi

echo
echo "=== Step 2/5: masscan tier-2 cloud at $RATE pps on ports $SCAN_PORTS ==="
echo "  output: $RECON_DIR/masscan.gnmap"
echo "  expected wall time: ~20 min for 1,017 prefixes / ~3.55M IPs (3 ports)"
echo
sudo masscan \
  -iL "$RANGES_FILE" \
  -p "$SCAN_PORTS" \
  --rate "$RATE" \
  --wait 5 \
  -oG "$RECON_DIR/masscan.gnmap"

echo
echo "=== Step 3/5: extract unique IPs from masscan output ==="
awk '/Host:/ {print $4}' "$RECON_DIR/masscan.gnmap" | sort -u > "$RECON_DIR/ips.txt"
echo "  unique IPs with open ports: $(wc -l < "$RECON_DIR/ips.txt")"

echo
echo "=== Step 4/5: filter AS63949 honeypot fleet ==="
if [[ -f "$HONEYPOT_LIST" ]]; then
  comm -23 \
    <(sort -u "$RECON_DIR/ips.txt") \
    <(sort -u "$HONEYPOT_LIST") \
    > "$RECON_DIR/ips-clean.txt"
  echo "  after honeypot filter: $(wc -l < "$RECON_DIR/ips-clean.txt") IPs"
else
  cp "$RECON_DIR/ips.txt" "$RECON_DIR/ips-clean.txt"
  echo "  (honeypot list not found; skipping filter)"
fi

echo
echo "=== Step 5/5: aimap fingerprint + deep enumeration ==="
echo "  output: $RECON_DIR/aimap-report.json"
echo "  platforms: Metabase, Apache Superset, Redash, Grafana (+ full 56-fp sweep)"
aimap \
  -list "$RECON_DIR/ips-clean.txt" \
  -ports "$AIMAP_PORTS" \
  -threads 50 \
  -timeout 6s \
  -o "$RECON_DIR/aimap-report.json"

echo
echo "=== Done ==="
echo "  Tier-2 ranges:    $RANGES_FILE"
echo "  Raw masscan:      $RECON_DIR/masscan.gnmap"
echo "  Cleaned IP list:  $RECON_DIR/ips-clean.txt"
echo "  aimap report:     $RECON_DIR/aimap-report.json"
echo
echo "Next steps:"
echo "  1. bash data/visor-chain-runner.sh bi-dashboard  (full chain: visorgraph + profile + contact + visorlog + visorscuba + bare + visorcorpus)"
echo "  2. Write case study: case-studies/commercial/bi-dashboard-cloud-survey-$(date +%Y-%m).md"
