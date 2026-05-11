#!/bin/bash
# compute-orch-discovery-runbook.sh — Masscan + aimap pipeline for the
# compute orchestration tier survey (Spark/Airflow/Dask/Prefect/Temporal/
# BentoML + the existing Ray Dashboard / Kubeflow fingerprints).
#
# Methodology discipline: aimap is the fingerprinter. No per-survey
# bespoke Python probe. All fingerprints live in
# aimap and use the conjunctive matcher
# schema (status_code + json_field, all required) — see SYNTHESIS-2026-05
# Methodology Insight #6 for the substring-FP correction lesson.
#
# Run as:  bash compute-orch-discovery-runbook.sh
# Requires: sudo (masscan), masscan, aimap, jq

set -euo pipefail

RECON_DIR="$HOME/recon/compute-orch-tier2-$(date +%F)"
HONEYPOT_LIST="$HOME/recon/ollama-tier2-2026-05-04/as63949-honeypot-fleet.txt"

# Compute orchestration tier ports:
#   3000    BentoML, Ray Serve (already in aimap)
#   4040    Spark Application UI (per-app)
#   4200    Prefect API
#   8080    Airflow / Kubeflow / Temporal Web / Spark master (collision-prone)
#   8233    Temporal Web alt
#   8265    Ray Dashboard
#   8787    Dask Dashboard
#   18080   Spark History Server
PORTS="3000,4040,4200,8080,8233,8265,8787,18080"
RATE="10000"

mkdir -p "$RECON_DIR"
cd "$RECON_DIR"

echo "=== Step 1/5: gather tier-2 cloud /16 prefixes ==="
RANGES_FILE="$RECON_DIR/tier2-ranges.txt"
for candidate in \
  "$HOME/recon/browser-agent-tier2-2026-05-04/tier2-ranges.txt" \
  "$HOME/recon/llm-gateway-tier2-2026-05-04/tier2-ranges.txt" \
  "$HOME/recon/aisafety-tier2-2026-05-04/tier2-ranges.txt" \
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
  echo "ERROR: no tier-2 ranges file found in any prior survey dir." >&2
  exit 1
fi

echo
echo "=== Step 2/5: masscan tier-2 cloud at $RATE pps on $PORTS ==="
echo "  output: $RECON_DIR/masscan.gnmap"
echo "  expected wall time: ~30 min for 1,017 prefixes / ~3.55M IPs"
echo
sudo masscan \
  -iL "$RANGES_FILE" \
  -p "$PORTS" \
  --rate "$RATE" \
  --wait 5 \
  -oG "$RECON_DIR/masscan.gnmap"

echo
echo "=== Step 3/5: extract unique IPs from masscan output ==="
awk '/Host:/ {print $4}' "$RECON_DIR/masscan.gnmap" | sort -u > "$RECON_DIR/ips.txt"
echo "  unique IPs: $(wc -l < "$RECON_DIR/ips.txt")"

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
aimap \
  -list "$RECON_DIR/ips-clean.txt" \
  -ports "$PORTS" \
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
echo "Next: ingest into VisorLog -> nuclide.db"
echo "  jq -c '.services[]' $RECON_DIR/aimap-report.json | \\"
echo "    visorlog --db ~/AI-LLM-Infrastructure-OSINT/data/nuclide.db ingest --format ndjson"
echo
echo "Then: re-score via VisorScuba"
echo "  visorscuba --db ~/AI-LLM-Infrastructure-OSINT/data/nuclide.db assess"
