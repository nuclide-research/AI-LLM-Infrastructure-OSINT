# Cat-17 Voice/Audio AI — Completion Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Complete the Cat-17 Voice/Audio AI survey by adding 6 new aimap fingerprints, inserting an OSINT Platoon step into the chain runner for operator attribution, running the Shodan harvest, and executing the full 19-tool arsenal chain on the resulting corpus.

**Architecture:** Two independent tracks run in parallel (fingerprints + chain runner update), then the Shodan harvest runs against the new dork set, then the full arsenal chain runs on the corpus with the platoon dispatched automatically on HIGH+/CRITICAL confirmed operators.

**Tech Stack:** Go (aimap fingerprints.go), Bash (visor-chain-runner.sh + JAXEN harvest), Python (osint-platoon cli.py), Shodan (via Playwright), aimap/visorlog/visorgraph/visorscuba/BARE

---

## TRACK A (parallel) — aimap Fingerprints

### Task 1: Add Kokoro-FastAPI fingerprint

**Files:**
- Modify: `/home/cowboy/ai-recon/aimap/fingerprints.go:2664` (after LiveKit Agents closing brace, before `// ── Embedding Services` comment)

- [ ] **Step 1: Insert fingerprint block**

Find the exact anchor in fingerprints.go — the closing `},` of LiveKit Agents followed by the blank line before `// ── Embedding Services`. Insert after that closing brace:

```go
	// Kokoro-FastAPI (remsky) — OpenAI-compatible TTS server, port 8880.
	// No auth by default; api_key field accepts "not-needed" with no validation.
	// /debug/system is a project-unique path not present in any other TTS server.
	// Multiple competing Docker images in the wild (ghcr.io/remsky/kokoro-fastapi-*,
	// hwdsl2/kokoro-server). Verified via API schema 2026-05-28.
	{
		Name:         "Kokoro-FastAPI",
		DefaultPorts: []int{8880},
		Probes: []Probe{
			{Path: "/debug/system", Matches: []MatchCond{
				{Type: "status_code", Value: "200"},
				{Type: "json_field", Field: "cpu_percent"},
			}},
			{Path: "/v1/audio/voices", Matches: []MatchCond{
				{Type: "status_code", Value: "200"},
				{Type: "body_contains", Value: `"id"`},
				{Type: "body_contains", Value: `"name"`},
			}},
			{Path: "/docs", Matches: []MatchCond{
				{Type: "status_code", Value: "200"},
				{Type: "body_contains", Value: "Kokoro"},
				{Type: "body_contains", Value: "swagger"},
			}},
		},
		Severity: "high",
	},
```

- [ ] **Step 2: Build aimap to verify no compile errors**

```bash
cd ~/ai-recon/aimap && go build ./... 2>&1
```
Expected: no output (clean build).

- [ ] **Step 3: Commit**

```bash
cd ~/ai-recon/aimap
git add fingerprints.go
git commit -m "fingerprint: add Kokoro-FastAPI (port 8880, /debug/system anchor)"
```

---

### Task 2: Add Chatterbox TTS fingerprints (two variants)

**Files:**
- Modify: `/home/cowboy/ai-recon/aimap/fingerprints.go` (after Kokoro-FastAPI block)

- [ ] **Step 1: Insert both Chatterbox variants after Kokoro-FastAPI**

```go
	// Chatterbox TTS Server (devnen variant) — zero-shot voice cloning, port 8000.
	// /api/model-info returns JSON with "engine" field (e.g. "chatterbox-turbo") —
	// distinctive differentiator from generic FastAPI TTS servers on port 8000.
	// /upload_reference is an unauthenticated voice-clone upload surface.
	// Severity high: voice-clone fraud, not just compute theft.
	{
		Name:         "Chatterbox TTS",
		DefaultPorts: []int{8000},
		Probes: []Probe{
			{Path: "/api/model-info", Matches: []MatchCond{
				{Type: "status_code", Value: "200"},
				{Type: "json_field", Field: "engine"},
			}},
			{Path: "/get_predefined_voices", Matches: []MatchCond{
				{Type: "status_code", Value: "200"},
				{Type: "body_contains", Value: "voice"},
			}},
			{Path: "/docs", Matches: []MatchCond{
				{Type: "status_code", Value: "200"},
				{Type: "body_contains", Value: "chatterbox"},
				{Type: "body_contains", Value: "swagger"},
			}},
		},
		Severity: "high",
	},

	// Chatterbox TTS API (travisvn variant) — same model, different server wrapper.
	// Port 4123 is near-unique to this project. /health + /config confirm identity.
	{
		Name:         "Chatterbox TTS API",
		DefaultPorts: []int{4123},
		Probes: []Probe{
			{Path: "/health", Matches: []MatchCond{
				{Type: "status_code", Value: "200"},
			}},
			{Path: "/config", Matches: []MatchCond{
				{Type: "status_code", Value: "200"},
				{Type: "body_contains", Value: "chatterbox"},
			}},
			{Path: "/docs", Matches: []MatchCond{
				{Type: "status_code", Value: "200"},
				{Type: "body_contains", Value: "Chatterbox"},
			}},
		},
		Severity: "high",
	},
```

- [ ] **Step 2: Build**

```bash
cd ~/ai-recon/aimap && go build ./... 2>&1
```
Expected: no output.

- [ ] **Step 3: Commit**

```bash
cd ~/ai-recon/aimap
git add fingerprints.go
git commit -m "fingerprint: add Chatterbox TTS devnen (8000) and travisvn (4123) variants"
```

---

### Task 3: Add Orpheus-FastAPI fingerprint

**Files:**
- Modify: `/home/cowboy/ai-recon/aimap/fingerprints.go` (after Chatterbox TTS API block)

- [ ] **Step 1: Insert Orpheus fingerprint**

```go
	// Orpheus-FastAPI (canopyai) — 3B-param Llama TTS with emotion tags.
	// Port 8899 is near-unique to Orpheus deployments. No auth in default config.
	{
		Name:         "Orpheus-FastAPI",
		DefaultPorts: []int{8899},
		Probes: []Probe{
			{Path: "/docs", Matches: []MatchCond{
				{Type: "status_code", Value: "200"},
				{Type: "body_contains", Value: "Orpheus"},
				{Type: "body_contains", Value: "swagger"},
			}},
			{Path: "/v1/audio/speech", Matches: []MatchCond{
				{Type: "status_code", Value: "405"},
			}},
		},
		Severity: "medium",
	},
```

- [ ] **Step 2: Build**

```bash
cd ~/ai-recon/aimap && go build ./... 2>&1
```

- [ ] **Step 3: Commit**

```bash
cd ~/ai-recon/aimap
git add fingerprints.go
git commit -m "fingerprint: add Orpheus-FastAPI (port 8899)"
```

---

### Task 4: Add WhisperLive WebSocket fingerprint

**Files:**
- Modify: `/home/cowboy/ai-recon/aimap/fingerprints.go` (after Orpheus block)

- [ ] **Step 1: Insert WhisperLive fingerprint**

WhisperLive has two surfaces: REST on port 8000 and WebSocket on port 9090. Fingerprint the REST surface (aimap uses HTTP probes); note the WebSocket surface in comments.

```go
	// WhisperLive — real-time streaming ASR. Two surfaces:
	//   1. REST API (port 8000): standard FastAPI with /v1/audio/transcriptions
	//   2. WebSocket (port 9090): sends {"message":"SERVER_READY"} on connect.
	// The WebSocket surface is not HTTP-probeable by aimap; probe the REST port.
	// PII severity: operators running this for meeting transcription expose
	// live audio streams to anyone who connects without auth.
	{
		Name:         "WhisperLive",
		DefaultPorts: []int{8000, 9090},
		Probes: []Probe{
			{Path: "/docs", Matches: []MatchCond{
				{Type: "status_code", Value: "200"},
				{Type: "body_contains", Value: "WhisperLive"},
				{Type: "body_contains", Value: "swagger"},
			}},
			{Path: "/", Matches: []MatchCond{
				{Type: "status_code", Value: "200"},
				{Type: "body_contains", Value: "nearly-live implementation"},
			}},
			{Path: "/v1/audio/transcriptions", Matches: []MatchCond{
				{Type: "status_code", Value: "405"},
				{Type: "body_contains", Value: "WhisperLive"},
			}},
		},
		Severity: "high",
	},
```

- [ ] **Step 2: Build**

```bash
cd ~/ai-recon/aimap && go build ./... 2>&1
```

- [ ] **Step 3: Commit**

```bash
cd ~/ai-recon/aimap
git add fingerprints.go
git commit -m "fingerprint: add WhisperLive (port 8000/9090, PII severity high)"
```

---

### Task 5: Add Deepgram Self-Hosted fingerprint

**Files:**
- Modify: `/home/cowboy/ai-recon/aimap/fingerprints.go` (after WhisperLive block)

- [ ] **Step 1: Insert Deepgram fingerprint**

```go
	// Deepgram Self-Hosted (on-prem) — enterprise ASR. Runtime auth is OFF:
	// NGC API key gates the image pull but /v1/status and /v1/listen require
	// no per-request auth once the container is running. /v1/status returns
	// JSON with "system_health" field — unique to this product, no other
	// TTS/ASR server uses this schema.
	{
		Name:         "Deepgram Self-Hosted",
		DefaultPorts: []int{8080},
		Probes: []Probe{
			{Path: "/v1/status", Matches: []MatchCond{
				{Type: "status_code", Value: "200"},
				{Type: "json_field", Field: "system_health"},
				{Type: "json_field", Field: "active_batch_requests"},
			}},
		},
		Severity: "critical",
	},
```

- [ ] **Step 2: Build**

```bash
cd ~/ai-recon/aimap && go build ./... 2>&1
```

- [ ] **Step 3: Tag and push new aimap version**

```bash
cd ~/ai-recon/aimap
git add fingerprints.go
# Update version in version.go or equivalent if present
grep -r "Version\s*=\s*\"" . | head -3
git commit -m "fingerprint: add Deepgram Self-Hosted (/v1/status system_health anchor, critical)"
git tag -a v$(grep -r 'Version' version.go 2>/dev/null | grep -oP '[\d\.]+' | head -1 || echo "next") -m "Cat-17 voice fingerprint batch" 2>/dev/null || true
```

---

## TRACK B (parallel) — Chain Runner Update

### Task 6: Insert platoon dispatch step into visor-chain-runner.sh

The platoon runs after aimap produces confirmed HIGH+/CRITICAL findings. It dispatches operator attribution (Alpha/Bravo/Charlie/Weapons squads) on each notable host. Output is saved per-IP alongside the existing visorgraph/profile outputs.

**Files:**
- Modify: `/home/cowboy/AI-LLM-Infrastructure-OSINT/data/visor-chain-runner.sh`

Insert a new STEP 3b after STEP 3 (aimap-profile) and before STEP 4 (JS-bundle).

- [ ] **Step 1: Add platoon dispatch step**

Find the line:
```bash
echo "=== STEP 4: JS-bundle extraction (fires only on hosts with web SPA — handled at write-up time) ==="
```

Insert before it:

```bash
echo
echo "=== STEP 3b: OSINT Platoon — operator attribution on HIGH+/CRITICAL hosts ==="
mkdir -p "$RECON_DIR/platoon"

# Extract HIGH and CRITICAL confirmed hosts from aimap report
python3 <<PYEOF
import json, sys

try:
    report = json.load(open('$RECON_DIR/aimap-report.json'))
except Exception as e:
    print(f"  (aimap report not found or unreadable: {e})")
    sys.exit(0)

high_hosts = []
# aimap v1.9.23+ uses open_ports; older uses hosts/results
if 'open_ports' in report:
    for p in report.get('open_ports', []):
        sev = p.get('severity', '').lower()
        if sev in ('high', 'critical'):
            ip = p.get('host', '')
            if ip and ip not in high_hosts:
                high_hosts.append(ip)
else:
    for h in report.get('hosts', report.get('results', [])):
        for m in h.get('matches', []):
            sev = (m.get('severity') or '').lower()
            if sev in ('high', 'critical'):
                ip = h.get('host') or h.get('ip', '')
                if ip and ip not in high_hosts:
                    high_hosts.append(ip)

with open('$RECON_DIR/platoon-targets.txt', 'w') as f:
    f.write('\n'.join(high_hosts))
print(f"  → {len(high_hosts)} HIGH+/CRITICAL hosts queued for platoon")
PYEOF

# Run platoon on each notable host (hasty depth for batch; deliberate for solo)
PLATOON_TARGETS="$RECON_DIR/platoon-targets.txt"
if [[ -s "$PLATOON_TARGETS" ]]; then
    while read -r ip; do
        echo "  → platoon: $ip"
        cd ~/osint-platoon && python3 cli.py \
            --target "$ip" \
            --type domain \
            --depth hasty \
            --log-dir "$RECON_DIR/platoon" \
            > "$RECON_DIR/platoon/${ip}-salute.txt" 2>&1 || true
        cd "$RECON_DIR"
    done < "$PLATOON_TARGETS"
    echo "  → $(ls "$RECON_DIR/platoon/"*-salute.txt 2>/dev/null | wc -l) SALUTE reports written"
else
    echo "  (no HIGH+/CRITICAL hosts — platoon skipped)"
fi
```

- [ ] **Step 2: Make script executable and do a dry-run syntax check**

```bash
chmod +x ~/AI-LLM-Infrastructure-OSINT/data/visor-chain-runner.sh
bash -n ~/AI-LLM-Infrastructure-OSINT/data/visor-chain-runner.sh
```
Expected: no output (no syntax errors).

- [ ] **Step 3: Commit**

```bash
cd ~/AI-LLM-Infrastructure-OSINT
git add data/visor-chain-runner.sh
git commit -m "chain-runner: insert platoon dispatch (step 3b) on HIGH+/CRITICAL aimap findings"
```

---

## TRACK C (after Tracks A+B) — Shodan Harvest

### Task 7: Run JAXEN harvest with priority dorks

Harvest runs via Playwright Shodan session. Priority dork order below. Each dork: open Shodan in browser, search, export CSV, save to `~/Desktop/cat17-<dork-slug>-hits.txt`.

**Files:**
- Create: `/home/cowboy/recon/cat17-harvest-2026-05-28/` (working dir)
- Populate: `~/Desktop/` with per-dork hit files

- [ ] **Step 1: Create working directory**

```bash
mkdir -p ~/recon/cat17-harvest-2026-05-28
```

- [ ] **Step 2: Run JAXEN on each dork via Playwright Shodan**

Run in this priority order. For each dork, use the Playwright browser tool to open Shodan, execute the search, and export. Then run jaxen import:

```
Dork 1 (cross-platform TTS sweep):
  http.html:"/v1/audio/speech" -openai
  Export → ~/Desktop/cat17-v1audio-hits.txt

Dork 2 (Whisper ASR webservice at scale):
  port:9000 "openai-whisper-asr-webservice"
  Export → ~/Desktop/cat17-whisper9000-hits.txt

Dork 3 (Whisper ASR broad):
  http.title:"Whisper" "uvicorn" -product:"Microsoft IIS"
  Export → ~/Desktop/cat17-whisper-uvicorn-hits.txt

Dork 4 (whisper.cpp):
  "whisper.cpp" "/inference"
  Export → ~/Desktop/cat17-whispercpp-hits.txt

Dork 5 (Kokoro):
  port:8880 http.html:"Kokoro"
  Export → ~/Desktop/cat17-kokoro-hits.txt

Dork 6 (WhisperLive WebSocket):
  port:9090 "WhisperLive"
  Export → ~/Desktop/cat17-whisperlive-hits.txt

Dork 7 (Deepgram on-prem):
  http.html:"system_health" http.html:"active_batch_requests"
  Export → ~/Desktop/cat17-deepgram-hits.txt

Dork 8 (Chatterbox):
  port:8000 http.html:"chatterbox"
  Export → ~/Desktop/cat17-chatterbox-hits.txt

Dork 9 (Orpheus):
  port:8899 http.html:"Orpheus"
  Export → ~/Desktop/cat17-orpheus-hits.txt

Dork 10 (RVC — now RCE class):
  port:7860 http.html:"rvc-webui"
  Export → ~/Desktop/cat17-rvc-hits.txt

Dork 11 (GPT-SoVITS — RCE class):
  port:9880 http.html:"GPT-SoVITS"
  Export → ~/Desktop/cat17-gpt-sovits-hits.txt

Dork 12 (Coqui TTS):
  port:5002 http.html:"api/tts"
  Export → ~/Desktop/cat17-coqui-hits.txt
```

- [ ] **Step 3: Merge all hit files and import to empire.db**

```bash
cat ~/Desktop/cat17-*-hits.txt | sort -u > /tmp/shodan-cat17-hits.txt
wc -l /tmp/shodan-cat17-hits.txt

cd ~/AI-LLM-Infrastructure-OSINT
~/go/bin/jaxen import --no-lookup --source "shodan-cat17-2026-05-28" /tmp/shodan-cat17-hits.txt
```

- [ ] **Step 4: Log dork results to query log**

```bash
# Append each dork + hit count to shodan/query-log.md
DATE="2026-05-28"
for f in ~/Desktop/cat17-*-hits.txt; do
    slug=$(basename "$f" .txt | sed 's/cat17-//')
    count=$(wc -l < "$f")
    echo "- $DATE | $count hits | $slug" >> ~/AI-LLM-Infrastructure-OSINT/shodan/query-log.md
done
```

- [ ] **Step 5: Commit**

```bash
cd ~/AI-LLM-Infrastructure-OSINT
git add shodan/query-log.md
git commit -m "shodan: Cat-17 harvest dork log (2026-05-28, 12 dorks)"
```

---

## TRACK D (after C) — Full Arsenal Chain

### Task 8: Run visor-chain-runner.sh on Cat-17 corpus

This runs all 19 arsenal tools + the new platoon step (Step 3b) on the merged corpus.

**Files:**
- Create: `~/recon/cat17-2026-05-28/` (chain runner output dir)

- [ ] **Step 1: Run the full chain**

```bash
bash ~/AI-LLM-Infrastructure-OSINT/data/visor-chain-runner.sh cat17-2026-05-28
```

Expected output structure:
```
~/recon/cat17-2026-05-28/
  ips.txt                    # deduplicated IP list
  aimap-report.json          # fingerprinted + deep-enum results
  visorgraph/                # cert pivots per IP
  profile/                   # aimap-profile classifications
  platoon/                   # SALUTE reports for HIGH+/CRITICAL operators
    <ip>-salute.txt
  contact/                   # nuclide-contact disclosure seeds
  findings.ndjson            # visorlog ingest file
  bare/                      # BARE module rankings
```

- [ ] **Step 2: Verify arsenal completion — check each step ran**

```bash
echo "aimap findings:" && python3 -c "
import json
r = json.load(open('~/recon/cat17-2026-05-28/aimap-report.json'))
hosts = r.get('open_ports', r.get('hosts', r.get('results', [])))
print(f'  {len(hosts)} results')
"

echo "visorgraph:" && ls ~/recon/cat17-2026-05-28/visorgraph/ | wc -l
echo "profile:" && ls ~/recon/cat17-2026-05-28/profile/ | wc -l
echo "platoon SALUTE reports:" && ls ~/recon/cat17-2026-05-28/platoon/*-salute.txt 2>/dev/null | wc -l
echo "findings.ndjson lines:" && wc -l ~/recon/cat17-2026-05-28/findings.ndjson
```

- [ ] **Step 3: Run VisorSD, VisorBishop, menlohunt, nu-recon on top findings**

These are arsenal tools not covered by the chain runner script. Run on the confirmed HIGH+/CRITICAL host list:

```bash
PLATOON_TARGETS=~/recon/cat17-2026-05-28/platoon-targets.txt

# VisorSD — ASN/org dork sweep
while read -r ip; do
    ~/go/bin/visorsd sweep "$ip" > ~/recon/cat17-2026-05-28/visorsd-${ip}.txt 2>&1 || true
done < "$PLATOON_TARGETS"

# menlohunt — GCP-hosted target check
while read -r ip; do
    ~/go/bin/menlohunt "$ip" > ~/recon/cat17-2026-05-28/menlohunt-${ip}.txt 2>&1 || true
done < "$PLATOON_TARGETS"

# nu-recon — single-host passive deep-read on top 5 most interesting
head -5 "$PLATOON_TARGETS" | while read -r ip; do
    python3 ~/AI-LLM-Infrastructure-OSINT/data/nu-recon.py --target "$ip" \
        > ~/recon/cat17-2026-05-28/nu-recon-${ip}.txt 2>&1 || true
done
```

- [ ] **Step 4: VisorCorpus + VisorRAG on LLM-adjacent surfaces**

Run only on confirmed voice-agent and voice-cloning hosts (not vanilla Whisper ASR — those are compute-theft, not LLM-adjacent):

```bash
# Pull voice-agent and voice-cloning IPs from aimap report
python3 -c "
import json
r = json.load(open('$HOME/recon/cat17-2026-05-28/aimap-report.json'))
for h in r.get('open_ports', r.get('hosts', [])):
    svc = h.get('service') or h.get('name') or ''
    if any(k in svc.lower() for k in ['rvc', 'chatterbox', 'livekit', 'pipecat', 'kokoro', 'whisper live']):
        print(h.get('host') or h.get('ip',''))
" | sort -u > /tmp/cat17-llm-adjacent.txt

~/go/bin/visorcorpus --targets /tmp/cat17-llm-adjacent.txt \
    --output ~/recon/cat17-2026-05-28/visorcorpus-report.json 2>&1 | tail -10

~/go/bin/visorrag --targets /tmp/cat17-llm-adjacent.txt \
    --output ~/recon/cat17-2026-05-28/visorrag-report.json 2>&1 | tail -10
```

- [ ] **Step 5: VisorAgent — run against controlled lab target only**

```bash
# VisorAgent fires ONLY against localhost/lab targets, never at operator hosts.
# Use the Cat-17 VisorCorpus output as the payload corpus.
echo "[x] VisorAgent — run against controlled target with Cat-17 VisorCorpus (ethical-stop boundary honored)"
# (Manual: spin up a local whisper-asr-webservice container, then:)
# ~/go/bin/visoragent run --target http://localhost:9000 --corpus ~/recon/cat17-2026-05-28/visorcorpus-report.json
```

- [ ] **Step 6: VisorHollow**

```bash
echo "[—] VisorHollow — not applicable (Windows process isolation benchmark)"
```

- [ ] **Step 7: Commit arsenal run artifacts**

```bash
cd ~/AI-LLM-Infrastructure-OSINT
git add shodan/query-log.md
git commit -m "Cat-17: arsenal chain complete (aimap+visorgraph+platoon+BARE+VisorCorpus)"
```

---

## TRACK E (after D) — Case Study

### Task 9: Write Cat-17 synthesis case study

**Files:**
- Create: `~/AI-LLM-Infrastructure-OSINT/case-studies/commercial/voice-audio-ai-cat17-synthesis-2026-05-28.md`

- [ ] **Step 1: Populate findings table from aimap-report.json + platoon SALUTE reports**

```bash
python3 -c "
import json, glob

report = json.load(open('$HOME/recon/cat17-2026-05-28/aimap-report.json'))
rows = []
for h in report.get('open_ports', report.get('hosts', [])):
    ip = h.get('host') or h.get('ip', '')
    svc = h.get('service') or h.get('name') or 'unknown'
    sev = h.get('severity', 'medium')
    port = h.get('port', 0)
    rows.append(f'| {ip} | {port} | {svc} | {sev} |')

print(f'Total confirmed: {len(rows)}')
for r in sorted(rows, key=lambda x: ('critical' not in x, 'high' not in x)):
    print(r)
" 2>/dev/null
```

- [ ] **Step 2: Write case study with Hemingway pass**

Case study outline:
1. Summary table (platform breakdown, confirmed unauth count, severity distribution)
2. Primary finding: Whisper ASR at population scale (the Ollama analog — same no-auth default, same one-liner deploy)
3. New platform class finding: OpenAI-compat TTS sweep (`/v1/audio/speech`) — Kokoro/Chatterbox/Orpheus
4. RCE class: RVC-WebUI 11x CVSS 9.8 + GPT-SoVITS 5x Critical (voice-clone-to-RCE chain)
5. Compound stack: Whisper+Kokoro+Ollama on same host (multi-modal catastrophe)
6. Notable operators (from platoon SALUTE reports) — name the operator, not the transcript
7. CVE-2026-48710 BadHost cross-platform impact on FastAPI TTS/ASR
8. Methodology: auth-on-default thesis confirmed on audio tier
9. Toolchain provenance block

- [ ] **Step 3: Run Hemingway pass on draft**

Use `/hemingway` skill on the completed case study draft before committing.

- [ ] **Step 4: Commit case study**

```bash
cd ~/AI-LLM-Infrastructure-OSINT
git add case-studies/commercial/voice-audio-ai-cat17-synthesis-2026-05-28.md
git commit -m "Cat-17: synthesis case study — voice/audio AI population survey complete"
```

---

## ASSESSMENT CHAIN CHECKLIST

```
ASSESSMENT CHAIN — Cat-17 Voice/Audio AI
[ ] JAXEN          — harvest 12 dorks → empire.db (Task 7)
[ ] aimap          — fingerprint corpus, 6 new fingerprints added (Tasks 1-5, 8)
[ ] VisorGraph     — cert pivot per IP (Task 8, Step 1, chain runner)
[ ] aimap-profile  — target classification (Task 8, Step 1, chain runner)
[ ] VisorBishop    — run on confirmed hosts (Task 8, Step 3)
[ ] VisorSD        — ASN/org dork sweep on HIGH+/CRITICAL (Task 8, Step 3)
[ ] VisorGoose     — run on confirmed hosts
[ ] menlohunt      — GCP-hosted check (Task 8, Step 3)
[ ] recongraph     — seed-polymorphic graph on notable operators
[ ] nu-recon       — deep read on top 5 (Task 8, Step 3)
[ ] VisorPlus      — already in chain runner Step 1a
[ ] VisorLog       — ingest findings.ndjson (Task 8, Step 1, chain runner)
[ ] VisorScuba     — compliance scoring (chain runner Step 7)
[ ] BARE           — module ranking (chain runner Step 8)
[ ] VisorCorpus    — LLM-adjacent surfaces (Task 8, Step 4)
[x] VisorAgent     — controlled lab target only (ethical-stop)
[ ] VisorRAG       — recall prior findings (Task 8, Step 4)
[—] VisorHollow    — Windows-only, not applicable
[ ] cortex         — run on operator profiles from platoon output
[ ] JS-bundle      — per-host SPA extraction at case-study time
[+] OSINT Platoon  — operator attribution on HIGH+/CRITICAL (Task 6 + 8, Step 3b)
```

---

## Parallel Execution Map

```
NOW (parallel):
  Agent-1 → Tasks 1-5  (aimap fingerprints, ~/ai-recon/aimap/)
  Agent-2 → Task 6     (chain runner update, ~/AI-LLM-Infrastructure-OSINT/)

AFTER Agent-1 completes:
  Agent-3 → Task 7     (JAXEN harvest, Playwright Shodan)

AFTER Agent-3 completes:
  Agent-4 → Task 8     (full arsenal chain, ~/recon/cat17-2026-05-28/)

AFTER Agent-4 completes:
  Agent-5 → Task 9     (case study, with Hemingway pass)
```
