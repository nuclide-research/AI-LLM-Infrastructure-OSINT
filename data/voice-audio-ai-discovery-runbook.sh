#!/bin/bash
# voice-audio-ai-discovery-runbook.sh — Masscan + aimap pipeline for the
# Voice / Audio AI tier survey.
#
# Platforms: Whisper ASR family, Coqui XTTS, Piper TTS, RVC voice cloning,
#            OpenVoice, ChatTTS, F5-TTS, Pipecat / Vocode / LiveKit voice agents.
#
# Auth posture across category: skews Tier-A "no auth concept". Whisper
# transcription endpoints leak compute; voice-cloning servers leak both
# compute AND fraud-relevant model surfaces.
#
# Methodology: aimap is the fingerprinter. Conjunctive matchers separate
# Whisper from generic /docs FastAPI hits, and the voice-cloning family
# (RVC / GPT-SoVITS / Applio) from generic Gradio (port 7860 collision).
#
# Run as:  bash voice-audio-ai-discovery-runbook.sh
# Requires: sudo (masscan), masscan, aimap

set -euo pipefail

RECON_DIR="$HOME/recon/voice-audio-ai-tier2-$(date +%F)"
HONEYPOT_LIST="$HOME/recon/ollama-tier2-2026-05-04/as63949-honeypot-fleet.txt"
AIMAP_PORTS="80,443,1984,2379,3000,3001,4000,4040,4200,5000,5001,5002,5678,6333,7575,7576,7860,7865,7880,7897,8000,8001,8020,8080,8081,8088,8123,8233,8265,8443,8501,8787,8888,8889,9000,9090,9091,9966,10000,10087,10200,11434,15500,18080,18789,19530,30000,51000,55000"

# Voice/Audio AI ports — primary masscan targets:
#   5002    Mozilla TTS / Coqui legacy
#   7860    Gradio default (Whisper / OpenVoice / F5-TTS / ChatTTS / many)
#   7865    RVC WebUI default
#   7880    LiveKit default
#   7897    GPT-SoVITS default
#   8000    Pipecat / Vocode / general FastAPI
#   8020    Coqui XTTS server
#   9000    onerahmet/openai-whisper-asr-webservice canonical port
#   9966    ChatTTS sometimes
#   10087   rsxdalv/tts-generation-webui
#   10200   Piper TTS HTTP wrapper
SCAN_PORTS="5002,7860,7865,7880,7897,8000,8020,9000,9966,10087,10200"
RATE="10000"

mkdir -p "$RECON_DIR"
cd "$RECON_DIR"

echo "=== Step 1/5: gather tier-2 cloud /16 prefixes ==="
RANGES_FILE="$RECON_DIR/tier2-ranges.txt"
for candidate in \
  "$HOME/recon/bi-dashboard-tier2-$(date +%F)/tier2-ranges.txt" \
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
  echo "  no tier-2 range file found — building from Scaleway/OVH/Linode AS list"
  python3 - <<'PY' > "$RANGES_FILE"
import urllib.request, json, ipaddress
asns = ['AS12876','AS24940','AS63949','AS16276','AS35280']  # Scaleway, Hetzner, Linode/Akamai, OVH
for asn in asns:
    try:
        url = f'https://stat.ripe.net/data/announced-prefixes/data.json?resource={asn}'
        with urllib.request.urlopen(url, timeout=15) as r:
            data = json.loads(r.read())
        for p in data['data']['prefixes']:
            pfx = p['prefix']
            if ':' not in pfx:
                print(pfx)
    except Exception as e:
        print(f'# {asn} err: {e}')
PY
  echo "  generated $(wc -l < "$RANGES_FILE") prefixes"
fi

echo ""
echo "=== Step 2/5: masscan ports $SCAN_PORTS at $RATE pps ==="
MASSCAN_OUT="$RECON_DIR/masscan-$(date +%F).txt"
sudo masscan -iL "$RANGES_FILE" -p "$SCAN_PORTS" --rate "$RATE" \
  -oL "$MASSCAN_OUT" 2>&1 | tail -3

OPEN_LIST="$RECON_DIR/open-hosts.txt"
grep "^open" "$MASSCAN_OUT" | awk '{print $4}' | sort -u > "$OPEN_LIST"
echo "  $(wc -l < "$OPEN_LIST") unique IPs with at least one voice/audio port open"

echo ""
echo "=== Step 3/5: filter known honeypot fleet ==="
if [[ -f "$HONEYPOT_LIST" ]]; then
  FILTERED="$RECON_DIR/open-hosts-filtered.txt"
  comm -23 <(sort "$OPEN_LIST") <(sort "$HONEYPOT_LIST") > "$FILTERED"
  echo "  $(wc -l < "$OPEN_LIST") → $(wc -l < "$FILTERED") after AS63949 honeypot filter"
  TARGET_LIST="$FILTERED"
else
  echo "  honeypot list not found — skipping filter"
  TARGET_LIST="$OPEN_LIST"
fi

echo ""
echo "=== Step 4/5: aimap fingerprint sweep ==="
AIMAP_OUT="$RECON_DIR/aimap-$(date +%F).json"
aimap -list "$TARGET_LIST" -ports "$AIMAP_PORTS" -threads 50 \
  -timeout 6s -o "$AIMAP_OUT" 2>&1 | tail -20

echo ""
echo "=== Step 5/5: summary by service ==="
if [[ -f "$AIMAP_OUT" ]]; then
  python3 - <<PY
import json
data = json.load(open("$AIMAP_OUT"))
counts = {}
for h in data.get('hosts', []):
    for s in h.get('services', []):
        name = s.get('service', 'unknown')
        counts[name] = counts.get(name, 0) + 1
for name, n in sorted(counts.items(), key=lambda x: -x[1]):
    print(f"  {n:>4}  {name}")
PY
fi

echo ""
echo "Output: $RECON_DIR"
