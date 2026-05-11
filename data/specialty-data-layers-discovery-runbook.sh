#!/bin/bash
# specialty-data-layers-discovery-runbook.sh — Masscan + aimap pipeline for
# the Specialty data layers tier (ClickHouse / Apache Pinot / ScyllaDB REST
# + DuckDB-backed API products discovered via Shodan facet bucketing).
#
# Methodology discipline: aimap is the fingerprinter. No per-survey bespoke
# Python probe. All fingerprints live in aimap
# and use the conjunctive matcher schema (status_code + json_field +
# header_contains/body_contains, all required) — see SYNTHESIS-2026-05
# Methodology Insight #6 for the substring-FP correction lesson and
# Methodology Insight #7 for the Shodan-facet substring-FP variant
# discovered during DuckDB-HTTP bucketing 2026-05-05.
#
# Run as:  bash specialty-data-layers-discovery-runbook.sh
# Requires: sudo (masscan), masscan, aimap >= v1.5.0, jq

set -euo pipefail

RECON_DIR="$HOME/recon/specialty-data-layers-tier2-$(date +%F)"
HONEYPOT_LIST="$HOME/recon/ollama-tier2-2026-05-04/as63949-honeypot-fleet.txt"

# Specialty data layer ports:
#   8123    ClickHouse HTTP
#   8443    ClickHouse HTTPS (alt)
#   9000    Apache Pinot Controller (collision with ClickHouse native TCP, Whisper, MinIO API,
#           Apache Pinot broker default — aimap conjunctive-match discriminates)
#   9042    Cassandra/ScyllaDB CQL native (binary protocol — separate TCP banner check, not aimap)
#   10000   ScyllaDB REST API (collision with Webmin — aimap discriminates via /api-doc/ shape)
#   3001    DuckDB-API products (Amulet Scan family — fingerprint added to aimap v1.4.0)
#   9999    DuckDB-HTTP httpserver-extension default (canonical, but no in-the-wild confirmed yet)
PORTS_HTTP="8123,8443,3001,9999,10000,9000"
PORTS_TCP_BANNER="9042"
RATE="10000"

mkdir -p "$RECON_DIR"
cd "$RECON_DIR"

echo "=== Step 1/6: gather tier-2 cloud /16 prefixes ==="
RANGES_FILE="$RECON_DIR/tier2-ranges.txt"
for candidate in \
  "$HOME/recon/compute-orch-tier2-2026-05-05/tier2-ranges.txt" \
  "$HOME/recon/browser-agent-tier2-2026-05-04/tier2-ranges.txt" \
  "$HOME/recon/llm-gateway-tier2-2026-05-04/tier2-ranges.txt" \
  "$HOME/recon/ollama-tier2-2026-05-04/tier2-ranges.txt" \
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
echo "=== Step 2/6: masscan tier-2 cloud at $RATE pps on $PORTS_HTTP ==="
echo "  output: $RECON_DIR/masscan-http.gnmap"
echo "  expected wall time: ~30 min for 1,017 prefixes / ~3.55M IPs"
sudo masscan \
  -iL "$RANGES_FILE" \
  -p "$PORTS_HTTP" \
  --rate "$RATE" \
  --wait 5 \
  -oG "$RECON_DIR/masscan-http.gnmap"

echo
echo "=== Step 3/6: masscan port 9042 (Cassandra/Scylla CQL — TCP banner only) ==="
sudo masscan \
  -iL "$RANGES_FILE" \
  -p "$PORTS_TCP_BANNER" \
  --rate "$RATE" \
  --wait 5 \
  -oG "$RECON_DIR/masscan-cql.gnmap"

echo
echo "=== Step 4/6: extract unique IPs ==="
awk '/Host:/ {print $4}' "$RECON_DIR/masscan-http.gnmap" | sort -u > "$RECON_DIR/ips-http.txt"
awk '/Host:/ {print $4}' "$RECON_DIR/masscan-cql.gnmap" | sort -u > "$RECON_DIR/ips-cql.txt"
echo "  HTTP-tier IPs: $(wc -l < "$RECON_DIR/ips-http.txt")"
echo "  CQL-tier IPs:  $(wc -l < "$RECON_DIR/ips-cql.txt")"

echo
echo "=== Step 5/6: filter AS63949 honeypot fleet ==="
if [[ -f "$HONEYPOT_LIST" ]]; then
  comm -23 \
    <(sort -u "$RECON_DIR/ips-http.txt") \
    <(sort -u "$HONEYPOT_LIST") \
    > "$RECON_DIR/ips-http-clean.txt"
  comm -23 \
    <(sort -u "$RECON_DIR/ips-cql.txt") \
    <(sort -u "$HONEYPOT_LIST") \
    > "$RECON_DIR/ips-cql-clean.txt"
  echo "  HTTP after honeypot filter: $(wc -l < "$RECON_DIR/ips-http-clean.txt") IPs"
  echo "  CQL  after honeypot filter: $(wc -l < "$RECON_DIR/ips-cql-clean.txt") IPs"
else
  cp "$RECON_DIR/ips-http.txt" "$RECON_DIR/ips-http-clean.txt"
  cp "$RECON_DIR/ips-cql.txt"  "$RECON_DIR/ips-cql-clean.txt"
  echo "  (honeypot list not found; skipping filter)"
fi

echo
echo "=== Step 6a/6: aimap fingerprint + deep enumeration on HTTP tier ==="
aimap \
  -list "$RECON_DIR/ips-http-clean.txt" \
  -ports "$PORTS_HTTP" \
  -threads 50 \
  -timeout 6s \
  -o "$RECON_DIR/aimap-report.json"

echo
echo "=== Step 6b/6: CQL native-protocol banner check on port 9042 ==="
# Cassandra/ScyllaDB CQL native protocol identifies via OPTIONS frame:
#   client → server: \x04\x00\x00\x00\x05\x00\x00\x00\x00 (CQL v4 OPTIONS)
#   server → client: \x84\x00\x00\x00\x06... (SUPPORTED frame, version+stream+opcode echo)
# A proper structured handshake (not substring matching) is the methodology rule.
# Implemented as a small inline Python helper below.
cat > "$RECON_DIR/cql_banner_probe.py" <<'PYEOF'
import socket, struct, sys, json
TIMEOUT = 4.0
results = []
for ip in sys.stdin.read().split():
    try:
        s = socket.create_connection((ip, 9042), timeout=TIMEOUT)
        s.sendall(b"\x04\x00\x00\x00\x05\x00\x00\x00\x00")  # CQL v4 OPTIONS
        hdr = s.recv(9)
        if len(hdr) >= 9:
            version, flags, stream, opcode, length = struct.unpack(">BBhBI", hdr)
            if version & 0x80 and opcode == 0x06:  # SUPPORTED
                body = s.recv(min(length, 8192))
                fingerprint = "scylla" if b"SCYLLA" in body or b"scylla" in body else "cassandra-or-compatible"
                results.append({"ip": ip, "cql_native": True, "version": version & 0x7f, "fingerprint": fingerprint, "body_len": length})
        s.close()
    except Exception as e:
        results.append({"ip": ip, "cql_native": False, "error": str(e)[:80]})
print(json.dumps(results, indent=2))
PYEOF
python3 "$RECON_DIR/cql_banner_probe.py" < "$RECON_DIR/ips-cql-clean.txt" > "$RECON_DIR/cql-banners.json"
echo "  CQL banner results: $RECON_DIR/cql-banners.json"
jq -r '[.[] | select(.cql_native==true)] | length as $n | "\($n) confirmed Cassandra/ScyllaDB hosts"' "$RECON_DIR/cql-banners.json"

echo
echo "=== Done ==="
echo "  Tier-2 ranges:    $RANGES_FILE"
echo "  HTTP masscan:     $RECON_DIR/masscan-http.gnmap"
echo "  CQL  masscan:     $RECON_DIR/masscan-cql.gnmap"
echo "  Cleaned IP lists: $RECON_DIR/ips-{http,cql}-clean.txt"
echo "  aimap report:     $RECON_DIR/aimap-report.json"
echo "  CQL banners:      $RECON_DIR/cql-banners.json"
echo
echo "Next: ingest into VisorLog -> nuclide.db"
echo "  jq -c '.services[]' $RECON_DIR/aimap-report.json | \\"
echo "    visorlog --db ~/AI-LLM-Infrastructure-OSINT/data/nuclide.db ingest --format ndjson"
echo
echo "Then: re-score via VisorScuba"
echo "  visorscuba --db ~/AI-LLM-Infrastructure-OSINT/data/nuclide.db assess"
