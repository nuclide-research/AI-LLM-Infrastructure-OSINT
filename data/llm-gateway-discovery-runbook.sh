#!/bin/bash
# llm-gateway-discovery-runbook.sh — Masscan + multi-platform probe pipeline for the
# LLM Gateways / OpenAI-Compat Proxies cross-cloud survey.
#
# Run as: bash llm-gateway-discovery-runbook.sh
# Requires: sudo (masscan), masscan, ~/AI-LLM-Infrastructure-OSINT/data/llm-gateway-probe.py

set -euo pipefail

RECON_DIR="$HOME/recon/llm-gateway-tier2-2026-05-04"
PROBE="$HOME/AI-LLM-Infrastructure-OSINT/data/llm-gateway-probe.py"
HONEYPOT_LIST="$HOME/recon/ollama-tier2-2026-05-04/as63949-honeypot-fleet.txt"
PORTS="1234,1337,3000,4000,5000,8080"
RATE="10000"

mkdir -p "$RECON_DIR"
cd "$RECON_DIR"

echo "=== Step 1/6: gather tier-2 cloud /16 prefixes ==="
RANGES_FILE="$RECON_DIR/tier2-ranges.txt"
for candidate in \
  "$HOME/recon/mcp-tier2-2026-05-04/scaleway-ranges.txt" \
  "$HOME/recon/mcp-tier2-2026-05-04/ovh-ranges.txt" \
  "$HOME/recon/mcp-tier2-2026-05-04/linode-ranges.txt" \
  "/tmp/tier2-all-ranges.txt"; do
  if [[ -f "$candidate" ]]; then
    echo "  found: $candidate ($(wc -l < "$candidate") prefixes)"
  fi
done

# Combine all per-provider range files from MCP survey
cat "$HOME/recon/mcp-tier2-2026-05-04/"*-ranges.txt 2>/dev/null | sort -u > "$RANGES_FILE"
echo "  combined tier-2 ranges: $(wc -l < "$RANGES_FILE") prefixes"

if [[ ! -s "$RANGES_FILE" ]]; then
  echo "ERROR: no tier-2 ranges files found. Run the MCP survey first to generate them."
  exit 1
fi

echo
echo "=== Step 2/6: masscan ports $PORTS at $RATE pps ==="
sudo masscan -iL "$RANGES_FILE" -p "$PORTS" --rate "$RATE" --wait 5 \
  -oG "$RECON_DIR/tier2-llm-gateway-masscan.txt"

echo
echo "=== Step 3/6: extract unique (ip:port) targets ==="
awk '/Host:/ {
  ip=$4
  for (i=1; i<=NF; i++) if ($i ~ /^Ports:/) {
    split($(i+1), p, "/")
    print ip ":" p[1]
  }
}' "$RECON_DIR/tier2-llm-gateway-masscan.txt" | sort -u > "$RECON_DIR/tier2-llm-gateway-targets.txt"
echo "  unique (ip:port): $(wc -l < "$RECON_DIR/tier2-llm-gateway-targets.txt")"

echo
echo "=== Step 4/6: filter AS63949 honeypot fleet ==="
if [[ -f "$HONEYPOT_LIST" ]]; then
  comm -23 \
    <(awk -F: '{print $1}' "$RECON_DIR/tier2-llm-gateway-targets.txt" | sort -u) \
    <(sort -u "$HONEYPOT_LIST") \
    > "$RECON_DIR/tier2-llm-gateway-ips-clean.txt"
  awk -F: 'NR==FNR {keep[$0]=1; next} keep[$1]' \
    "$RECON_DIR/tier2-llm-gateway-ips-clean.txt" \
    "$RECON_DIR/tier2-llm-gateway-targets.txt" \
    > "$RECON_DIR/tier2-llm-gateway-targets-clean.txt"
  echo "  post-filter: $(wc -l < "$RECON_DIR/tier2-llm-gateway-targets-clean.txt")"
else
  cp "$RECON_DIR/tier2-llm-gateway-targets.txt" "$RECON_DIR/tier2-llm-gateway-targets-clean.txt"
fi

echo
echo "=== Step 5/6: probe (200 threads) ==="
python3 "$PROBE" \
  --in "$RECON_DIR/tier2-llm-gateway-targets-clean.txt" \
  --out "$RECON_DIR/tier2-llm-gateway-confirmed.jsonl" \
  --threads 200

echo
echo "=== Step 6/6: summary ==="
echo "  Confirmed: $(wc -l < "$RECON_DIR/tier2-llm-gateway-confirmed.jsonl" 2>/dev/null || echo 0)"
echo
echo "  Per-platform breakdown:"
for plat in "LiteLLM Proxy" "LocalAI" "oobabooga (Text Generation WebUI)" "LM Studio" "Jan AI / Cortex" "OneAPI / NewAPI" "OpenAI-compat (generic)"; do
  n=$(grep -c "\"platform\": \"$plat\"" "$RECON_DIR/tier2-llm-gateway-confirmed.jsonl" 2>/dev/null || echo 0)
  printf "    %-40s %s\n" "$plat" "$n"
done
echo
echo "  Top owned_by tags (provider-key indicators):"
jq -r '.owned_by[]?' "$RECON_DIR/tier2-llm-gateway-confirmed.jsonl" 2>/dev/null | sort | uniq -c | sort -rn | head -10
echo
ls -la "$RECON_DIR"/*.txt "$RECON_DIR"/*.jsonl 2>/dev/null

echo
echo "Done. Synthesize into case-studies/commercial/llm-gateways-cloud-survey-2026-05.md"
