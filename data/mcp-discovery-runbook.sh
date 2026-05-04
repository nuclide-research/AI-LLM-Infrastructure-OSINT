#!/bin/bash
# mcp-discovery-runbook.sh — Masscan + probe pipeline for the MCP cross-cloud survey.
#
# Outputs land in $RECON_DIR. Honeypot filter applied via the AS63949 list from
# the ollama-tier2 survey artifacts.
#
# Run as: bash mcp-discovery-runbook.sh
# Requires: sudo (masscan), masscan, ~/AI-LLM-Infrastructure-OSINT/data/mcp-probe.py

set -euo pipefail

RECON_DIR="$HOME/recon/mcp-tier2-2026-05-04"
PROBE="$HOME/AI-LLM-Infrastructure-OSINT/data/mcp-probe.py"
HONEYPOT_LIST="$HOME/recon/ollama-tier2-2026-05-04/as63949-honeypot-fleet.txt"
PORTS="3000,8000,8080,8888"
RATE="10000"

mkdir -p "$RECON_DIR"
cd "$RECON_DIR"

echo "=== Step 1/6: gather tier-2 cloud /16 prefixes ==="
# Reconstruct prefix list from the prior tier-2 surveys' input ranges.
# (Reuses Scaleway 7, OVH 33, Linode 36 = 76 prefixes ≈ 3.55M IPs.)
# If any of the prior survey dirs has a tier-2 ranges file, prefer it.
RANGES_FILE="$RECON_DIR/tier2-ranges.txt"
for candidate in \
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
  echo "Generate one with: see reference_tier2_cloud_osint_methodology memory"
  exit 1
fi

echo
echo "=== Step 2/6: masscan ports $PORTS at $RATE pps ==="
echo "  ETA: ~$(( $(wc -l < "$RANGES_FILE") * 65536 * 4 / 10000 / 60 )) minutes"
sudo masscan -iL "$RANGES_FILE" -p "$PORTS" --rate "$RATE" --wait 5 \
  -oG "$RECON_DIR/tier2-mcp-masscan.txt"

echo
echo "=== Step 3/6: extract unique (ip, port) pairs ==="
awk '/Host:/ {
  ip=$4
  for (i=1; i<=NF; i++) if ($i ~ /^Ports:/) {
    split($(i+1), p, "/")
    print ip ":" p[1]
  }
}' "$RECON_DIR/tier2-mcp-masscan.txt" | sort -u > "$RECON_DIR/tier2-mcp-targets.txt"
echo "  unique (ip:port) targets: $(wc -l < "$RECON_DIR/tier2-mcp-targets.txt")"

echo
echo "=== Step 4/6: filter AS63949 honeypot fleet ==="
if [[ -f "$HONEYPOT_LIST" ]]; then
  comm -23 \
    <(awk -F: '{print $1}' "$RECON_DIR/tier2-mcp-targets.txt" | sort -u) \
    <(sort -u "$HONEYPOT_LIST") \
    > "$RECON_DIR/tier2-mcp-ips-filtered.txt"
  # Re-attach ports
  awk -F: 'NR==FNR {keep[$0]=1; next} keep[$1]' \
    "$RECON_DIR/tier2-mcp-ips-filtered.txt" \
    "$RECON_DIR/tier2-mcp-targets.txt" \
    > "$RECON_DIR/tier2-mcp-targets-clean.txt"
  echo "  post-filter targets: $(wc -l < "$RECON_DIR/tier2-mcp-targets-clean.txt")"
else
  echo "  WARN: honeypot list not at $HONEYPOT_LIST — skipping filter"
  cp "$RECON_DIR/tier2-mcp-targets.txt" "$RECON_DIR/tier2-mcp-targets-clean.txt"
fi

echo
echo "=== Step 5/6: probe MCP handshake on survivors (200 threads) ==="
python3 "$PROBE" \
  --in "$RECON_DIR/tier2-mcp-targets-clean.txt" \
  --out "$RECON_DIR/tier2-mcp-confirmed.jsonl" \
  --threads 200

echo
echo "=== Step 6/6: summary ==="
CONFIRMED="$(wc -l < "$RECON_DIR/tier2-mcp-confirmed.jsonl" 2>/dev/null || echo 0)"
echo "  Confirmed MCP servers: $CONFIRMED"
echo
echo "  Tool-class breakdown (rough — names containing each keyword):"
for kw in read_file write_file run_command bash query execute_sql aws_ slack_ gmail_ fetch_ search_; do
  n=$(grep -ic "\"$kw" "$RECON_DIR/tier2-mcp-confirmed.jsonl" 2>/dev/null || echo 0)
  printf "    %-15s %s\n" "$kw" "$n"
done
echo
echo "  Output artifacts:"
ls -la "$RECON_DIR"/*.txt "$RECON_DIR"/*.jsonl 2>/dev/null

echo
echo "Done. Synthesize into case-studies/commercial/mcp-cloud-survey-2026-05.md"
