# Embedding Services Survey Runbook
## Category 27: TEI, infinity-embedding, custom FastAPI wrappers

**Date authored:** 2026-05-21  
**Status:** Live — first run complete (1 host confirmed)  
**Anchor case:** 46.4.204.44 (Hetzner DE / BAAI/bge-m3 / OpenVINO)

---

## Category Definition

Embedding services differ from LLM inference servers:

- **No conversational API** — input is text, output is a float vector
- **Shodan-dark problem** — many return bare JSON (`{"embedding_dimension":1024,...}`) that Shodan's HTML crawler indexes as empty or near-empty; `http.html:` dorks fail
- **High operator diversity** — TEI (HuggingFace), infinity-embedding, custom FastAPI wrappers, OpenVINO Model Server, all using different port conventions
- **Backend exposure pattern** — FastAPI wrapper on one port, raw OVMS/TorchServe on a second port, both internet-facing

Target platforms:
- HuggingFace TEI (Text Embeddings Inference) — default port 8080, probe `/info`
- infinity-embedding — default port 7997, probe `/openapi.json` for "Infinity Emb"
- Custom FastAPI + OpenVINO — any port, probe `/` for `embedding_dimension` JSON field
- OpenVINO Model Server (OVMS) — typically port 9000, probe `/v1/config`

---

## Discovery Pipeline

### Stage 0: Shodan dorks (if credits available)

Embedding services are largely Shodan-dark. The HTML crawler doesn't index JSON-only roots. Use these dorks when credits are fresh:

```
http.html:"embedding_dimension"
http.html:"Infinity Emb"
http.html:"model_pipeline_tag"
http.html:"feature-extraction"
port:7997
```

JAXEN command:
```bash
SHODAN_API_KEY=$KEY jaxen hunt --dork 'http.html:"embedding_dimension"' --out /tmp/shodan-embedding-hits.txt
SHODAN_API_KEY=$KEY jaxen hunt --dork 'http.html:"Infinity Emb"' --out /tmp/shodan-embedding-hits.txt
```

**Known limitation:** Shodan search credits exhaust monthly (both standard and freelance tiers). Confirmed 2026-05-21: both keys return "Insufficient query credits." Fall back to masscan.

### Stage 1: Masscan tier-2 cloud ranges

Tier-2 cloud ranges (Scaleway, OVH, Hetzner, DigitalOcean, Linode) are dense with self-hosted GPU workloads. Port selection:

```bash
sudo masscan -p 7997,8000,8001,8002,8080,3000 \
  -iL ~/recon/tier2-ranges.txt \
  --rate 5000 \
  -oL ~/recon/embedding-tier2-${DATE}/masscan/raw-hits.txt
```

Port rationale:
- `7997` — infinity-embedding default
- `8001` — common FastAPI embedding port (TEI alternate, custom)
- `8000,8080` — generic FastAPI/uvicorn defaults
- `8002,3000` — LiteLLM and LocalAI overlap; broad net

**2026-05-21 result:** 6,544 hits → 6,527 unique ip:port (port 7997: 334 hits, 8080: 2,577, 8000: 1,396, 3000: 1,334, 8001: 504, 8002: 399)

Parse masscan output:
```bash
grep "^open" masscan/raw-hits.txt | awk '{print $3, $4}' | \
  python3 -c "import sys; [print(f'{p} {ip}') for p,ip in [l.split() for l in sys.stdin]]" | \
  awk '{print $2":"$1}' | sort -u > targets.txt
```

### Stage 2: Async probe (embed-probe.py)

```bash
python3 embed-probe.py
# reads masscan/raw-hits.txt
# writes confirmed.jsonl
# 120 concurrent, 2s connect / 3s read / 10s deadline per host
```

Probe paths and matchers:
```python
PROBES = [
    ("/info", "GET", [("json_field","model_pipeline_tag"), ("body_contains","feature-extraction")]),  # TEI
    ("/openapi.json", "GET", [("body_contains","Infinity Emb")]),                                      # infinity
    ("/", "GET", [("json_field","embedding_dimension")]),                                              # FastAPI custom
    ("/health", "GET", [("json_field","embedding_dimension")]),                                        # FastAPI health
    ("/", "GET", [("json_field","embed")]),                                                            # FastAPI embed field
    ("/v1/models", "GET", [("json_field","data"), ("body_contains","embedding")]),                    # OpenAI-compat
    ("/v1/models", "GET", [("json_field","data"), ("body_contains","feature-extraction")]),           # TEI v1
    ("/", "GET", [("body_contains","ApplicationConfig")]),                                            # LocalAI
]
```

**2026-05-21 result:** 0 confirmed from 6,526 masscan targets. Root cause: the 334 port-7997 hits were stale (masscan found them open; hosts not serving infinity-embedding). Port-8080/8000 hits were generic web services.

### Stage 3: aimap batch fingerprint

```bash
# Extract unique IPs from masscan
grep "^open" masscan/raw-hits.txt | awk '{print $4}' | sort -u > ips.txt

~/go/bin/aimap \
  -list ips.txt \
  -ports 3000,7997,8000,8001,8002,8080 \
  -o aimap/aimap-report.json \
  -threads 50
```

aimap has 120 fingerprints covering embedding services. Wait for completion before analyzing. ETA: ~90min for 6,273 IPs at 50 threads.

---

## Per-Host Arsenal Chain

Once a confirmed host is identified (via probe or aimap), run the full chain:

```bash
IP=46.4.204.44
SLUG=embedding-tier2-2026-05-21
KEY=3f7C2zSDEOfBUSBmSJNgt4JVZW4ED6d3
RECON_DIR=~/recon/$SLUG
```

### Step 1: aimap deep enum

```bash
~/go/bin/aimap -target $IP -ports 8001,9000 -o $RECON_DIR/aimap/${IP}-deep.json
```

### Step 2: VisorPlus passive recon

```bash
~/go/bin/visorplus assess $IP 2>&1 | tee $RECON_DIR/visorplus/${IP}.log
```

### Step 3: VisiorGraph cert-pivot

```bash
~/go/bin/visorgraph -ip $IP 2>/dev/null > $RECON_DIR/visorgraph/${IP}.json
```

### Step 4: aimap-profile classification

```bash
python3 ~/ai-recon/aimap/aimap-profile/aimap_profile.py \
  --target $IP --mode fast \
  -o $RECON_DIR/profile/${IP}-profile.json
```

### Step 5: Shodan host deep read

```bash
curl -s "https://api.shodan.io/shodan/host/$IP?key=$KEY" | python3 -m json.tool
```

Key fields: `org`, `isp`, `asn`, `hostnames`, `domains`, `ports`, `data[].product`, `data[].http.html`

### Step 6: TOME scan (passive + active)

```bash
SHODAN_API_KEY=$KEY ~/projects/oreilly-osint-tool/tome scan $IP
SHODAN_API_KEY=$KEY ~/projects/oreilly-osint-tool/tome scan $IP --active
```

**Note:** TOME corpus does not currently include custom FastAPI embedding services (embedding_dimension pattern) or OpenVINO Model Server. This is a corpus gap — add `embedding-api.json` and `openvino-model-server.json` platforms.

### Step 7: Manual OVMS enumeration (if port 9000 present)

```bash
# Get model list
curl -s "http://$IP:9000/v1/config" | python3 -m json.tool

# Get model metadata (input tensor shapes)
curl -s "http://$IP:9000/v1/models/<model_name>/metadata" | python3 -m json.tool

# Verify inference endpoint
curl -s -X POST "http://$IP:8001/embed" \
  -H "Content-Type: application/json" \
  -d '{"text":"test"}' | python3 -m json.tool | head -10
```

### Step 8: VisorLog ingest

Prepare findings NDJSON:
```json
{"host_ip":"IP","port":8001,"source":"aimap","event_type":"unauth_access","event_severity":"medium","notes":"...","platform":"embedding-api-fastapi","timestamp":"..."}
```

```bash
~/go/bin/visorlog --db ~/AI-LLM-Infrastructure-OSINT/nuclide.db \
  ingest --format ndjson $RECON_DIR/findings.ndjson
```

### Step 9: BARE exploit ranking

```bash
~/.local/bin/bare $RECON_DIR/bare/input.json --top 5
```

### Step 10: VisorCorpus

```bash
~/go/bin/visorcorpus build -profile strict -type baseline \
  -include "kb_exfiltration,system_prompt,config_secrets" -max 50 \
  -out $RECON_DIR/visorcorpus.json
```

### Step 11: VisorScuba

```bash
~/go/bin/visorscuba assess \
  --db ~/AI-LLM-Infrastructure-OSINT/nuclide.db --json
```

---

## TOME Corpus Gaps Found

Two platforms missing from the 17-platform corpus:

**1. Custom FastAPI Embedding API**
Signal: GET `/` returns JSON with `embedding_dimension` field, `Server: uvicorn`
Model disclosure: `model_name`, `backend` fields in root response
Ports: typically 8001, 8000

**2. OpenVINO Model Server (OVMS)**
Signal: GET `/v1/config` returns model version status JSON
Port: typically 9000
API: TF Serving (`/v1/models/<name>:predict`) + OVMS-native
No auth by default on public deployments

Add these platforms to `platforms/embedding-api.json` and `platforms/openvino-model-server.json` in the TOME corpus.

---

## Key Findings: 46.4.204.44 (2026-05-21)

| Surface | Port | Auth | Details |
|---------|------|------|---------|
| Custom FastAPI embedding | 8001 | none | BAAI/bge-m3 1024-dim, OpenVINO INT8, `/embed` + `/embed/batch` live |
| OpenVINO Model Server | 9000 | none | v2026.0.0, model `bge-m3` AVAILABLE, `/v1/config` leaks model list, CORS `*` |
| SSH | 22 | key | OpenSSH |

**Operator profile:** Hetzner VPS (Köln, DE), AS24940, no custom domain (bare `clients.your-server.de`), GreyNoise: no data. Research or personal deployment.

**Impact:** Unrestricted embedding extraction — any text input returns BAAI/bge-m3 vector. Backend OVMS accessible directly — model architecture metadata exposed. No rate limiting observed.

---

## Lessons / Reproductibility Notes

1. **Masscan port 7997 hits are frequently stale.** 334 hits → 0 confirmed. infinity-embedding deployments are transient. Run embed-probe.py immediately after masscan, not hours later.

2. **embed-probe.py needs HTTPS support.** All 6,526 targets probed over HTTP only. Services with TLS termination are invisible to the current probe.

3. **aimap is the reliable net.** 120 fingerprints catch what embed-probe.py misses. The confirmed host 46.4.204.44 was found via Shodan (the aimap deep enum run), not masscan.

4. **Hetzner 46.4.x.x ranges not in tier2-ranges.txt.** The canonical Hetzner prefix for this is `46.4.0.0/16`. Add to tier2-ranges.txt for future runs.

5. **OVMS always co-located with FastAPI wrapper.** When you find a custom embedding FastAPI on port 8001, probe port 9000 for the OVMS backend immediately. Pattern confirmed here.

6. **Shodan search credits exhaust mid-month.** Both keys (standard + freelance) exhausted before this survey began. Shodan host API (`/shodan/host/{ip}`) still works — use for per-host enrichment but not discovery dorks.
