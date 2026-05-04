#!/bin/bash
# datalabel-discovery-runbook.sh — Masscan + multi-platform probe pipeline for the
# Data Labeling / Annotation cross-cloud survey.
#
# Run as: bash datalabel-discovery-runbook.sh
# Requires: sudo (masscan), masscan, ~/AI-LLM-Infrastructure-OSINT/data/datalabel-probe.py

set -euo pipefail

RECON_DIR="$HOME/recon/datalabel-tier2-2026-05-04"
PROBE="$HOME/AI-LLM-Infrastructure-OSINT/data/datalabel-probe.py"
HONEYPOT_LIST="$HOME/recon/ollama-tier2-2026-05-04/as63949-honeypot-fleet.txt"
PORTS="6900,8000,8080"
RATE="10000"

mkdir -p "$RECON_DIR"
cd "$RECON_DIR"

echo "=== Step 1/6: gather tier-2 cloud /16 prefixes ==="
RANGES_FILE="$RECON_DIR/tier2-ranges.txt"
for candidate in \
  "$HOME/recon/mcp-tier2-2026-05-04/scaleway-ranges.txt" \
  "$HOME/recon/mcp-tier2-2026-05-04/tier2-ranges.txt" \
  "$HOME/recon/qdrant-tier2-2026-05-04/tier2-ranges.txt" \
  "$HOME/recon/milvus-tier2-2026-05-04/tier2-ranges.txt" \
  "$HOME/recon/chromadb-tier2-2026-05-04/tier2-ranges.txt" \
  "$HOME/recon/ollama-tier2-2026-05-04/tier2-ranges.txt" \
  "/tmp/tier2-all-ranges.txt"; do
  if [[ -f "$candidate" ]]; then
    cp "$candidate" "$RANGES_FILE"
    echo "  reused: $candidate ($(wc -l < "$RANGES_FILE") prefixes)"
    break
  fi
done

if [[ ! -f "$RANGES_FILE" ]]; then
  echo "ERROR: no tier-2 ranges file found in any prior survey dir."
  echo "Generate one via BGP/WHOIS for AS12876 (Scaleway), AS16276 (OVH), AS63949 (Linode/Akamai)."
  exit 1
fi

echo
echo "=== Step 2/6: masscan ports $PORTS at $RATE pps ==="
sudo masscan -iL "$RANGES_FILE" -p "$PORTS" --rate "$RATE" --wait 5 \
  -oG "$RECON_DIR/tier2-datalabel-masscan.txt"

echo
echo "=== Step 3/6: extract unique (ip:port) targets ==="
awk '/Host:/ {
  ip=$4
  for (i=1; i<=NF; i++) if ($i ~ /^Ports:/) {
    split($(i+1), p, "/")
    print ip ":" p[1]
  }
}' "$RECON_DIR/tier2-datalabel-masscan.txt" | sort -u > "$RECON_DIR/tier2-datalabel-targets.txt"
echo "  unique (ip:port): $(wc -l < "$RECON_DIR/tier2-datalabel-targets.txt")"

echo
echo "=== Step 4/6: filter AS63949 honeypot fleet ==="
if [[ -f "$HONEYPOT_LIST" ]]; then
  comm -23 \
    <(awk -F: '{print $1}' "$RECON_DIR/tier2-datalabel-targets.txt" | sort -u) \
    <(sort -u "$HONEYPOT_LIST") \
    > "$RECON_DIR/tier2-datalabel-ips-clean.txt"
  awk -F: 'NR==FNR {keep[$0]=1; next} keep[$1]' \
    "$RECON_DIR/tier2-datalabel-ips-clean.txt" \
    "$RECON_DIR/tier2-datalabel-targets.txt" \
    > "$RECON_DIR/tier2-datalabel-targets-clean.txt"
  echo "  post-filter: $(wc -l < "$RECON_DIR/tier2-datalabel-targets-clean.txt")"
else
  cp "$RECON_DIR/tier2-datalabel-targets.txt" "$RECON_DIR/tier2-datalabel-targets-clean.txt"
fi

echo
echo "=== Step 5/6: probe (200 threads) ==="
python3 "$PROBE" \
  --in "$RECON_DIR/tier2-datalabel-targets-clean.txt" \
  --out "$RECON_DIR/tier2-datalabel-confirmed.jsonl" \
  --threads 200

echo
echo "=== Step 6/6: summary ==="
echo "  Confirmed: $(wc -l < "$RECON_DIR/tier2-datalabel-confirmed.jsonl" 2>/dev/null || echo 0)"
echo
echo "  Per-platform breakdown:"
for plat in Argilla LabelStudio doccano CVAT Prodigy; do
  n=$(grep -c "\"platform\": \"$plat\"" "$RECON_DIR/tier2-datalabel-confirmed.jsonl" 2>/dev/null || echo 0)
  printf "    %-15s %s\n" "$plat" "$n"
done
echo
echo "  Auth-on vs auth-off (where measured):"
echo "    auth_required:true:  $(grep -c '"auth_required": true' "$RECON_DIR/tier2-datalabel-confirmed.jsonl" 2>/dev/null || echo 0)"
echo "    auth_required:false: $(grep -c '"auth_required": false' "$RECON_DIR/tier2-datalabel-confirmed.jsonl" 2>/dev/null || echo 0)"
echo
ls -la "$RECON_DIR"/*.txt "$RECON_DIR"/*.jsonl 2>/dev/null

echo
echo "Done. Synthesize into case-studies/commercial/data-labeling-cloud-survey-2026-05.md"
