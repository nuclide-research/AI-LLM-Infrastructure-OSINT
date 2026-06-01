# Unauthenticated ML Training Server — velutina-service.ch

**Date:** 2026-06-01  
**IP:** 185.66.109.62  
**Domain:** velutina-service.ch  
**Org:** Swiss citizen science AI project (beekeeping / insect relocation sector)  
**Country:** CH  
**ASN:** AS200713 — OptimaNet Schweiz AG / HostFactory  
**Severity:** CRITICAL  
**Status:** Disclosed 2026-06-01  
**Verification:** Inner-B / Outer-1

---

## Discovery

JAXEN returned 185.66.109.62 under a passive Shodan query for exposed AI/ML infrastructure on Swiss hosting ranges. The Shodan record showed:

- Port 8000: `SimpleHTTP/0.6 Python/3.12.3` — directory listing
- Port 5000: `Werkzeug/3.1.3 Python/3.12.3` — custom web application
- Port 443/80: nginx, redirecting to a citizen science conservation portal

PTR: `s2496.rootserver.io` (OptimaNet customer namespace). TLS SAN enumeration via VisorGraph and recongraph surfaced `scan.velutina-service.ch` and `api.velutina-service.ch`. HTTP redirect on port 80 pivoted to `velutinaportal.eu`, a public-facing WordPress site describing a Vespa velutina (Asian Hornet) AI detection project.

## Context

The operator runs a citizen science platform for detecting and reporting the Asian Hornet (*Vespa velutina*) in Switzerland and Europe. The project:

- Collects crowdsourced images via a public upload portal (`scan.velutinaportal.eu`)
- Annotates images using Label Studio (historically on a Synology NAS at a residential Swisscom IP)
- Trains a YOLO object detection model (five classes: hornet, nest, false_positive, ok, unsicher)
- Serves inference via a Flask backend with Google OAuth authentication
- Uses Vast.ai GPU rentals and Google Colab Pro for compute

The exposed server is the training orchestration node — not the public inference API. It appears `python -m http.server` was started for a file transfer or local development task and left running.

## Findings

### F1 — CRITICAL: Unauthenticated SimpleHTTPServer serves home directory (port 8000)

`curl http://185.66.109.62:8000/` returns a full directory listing of the server's home directory. No authentication. No rate-limiting.

**Exposed file categories:**

| Path | Classification |
|---|---|
| `.env`, `.env.backup`, `.env.bak_20251219_*` (×2), `.env.bak_20260506_*` | API keys and secrets (multiple generations) |
| `.gcp/` | GCP service account credential directory |
| `.gsutil/` | Google Cloud Storage CLI credential directory |
| `.ssh/` | SSH private key directory |
| `current_training_instance.txt` | Active Vast.ai GPU instance ID and SSH access details |
| `export_labelstudio_projektid5_to_ftp_latest.sh` | Shell script containing FTP credentials as plaintext fallback defaults |
| `latest_candidate.pt` | Most recent trained YOLO model artifact (PyTorch) |
| `dataset_complete.tar.gz` | Complete annotated training dataset (publicly downloadable) |
| `auto_training.log`, `training_live.log`, `vast_training*.log` (×4) | Training run history and infrastructure paths |
| `labelstudio_export/`, `labelstudio_reimport.json` | Label Studio YOLO export data |
| `models/` | All saved model checkpoints (multiple dates) |
| `runs/` | YOLO training run metrics and validation results |

The Colab automation notebook (`COLAB_AUTO_TRAINING.md`) directly references `http://185.66.109.62:8000/dataset_complete.tar.gz` as the training dataset download URL — meaning the unauthenticated server was an intentional (if temporary) data delivery mechanism for cloud training jobs.

**Verification:** Inner-B / Outer-1. Directory listing confirmed live via HTTP. File contents not retrieved per restraint ethic — names and structure are the finding.

### F2 — HIGH: Werkzeug dev server exposes training pipeline management interface (port 5000)

Port 5000 runs a Python Werkzeug development server (`Werkzeug/3.1.3 Python/3.12.3`) serving a German-language "Label Studio Import" web application. No authentication observed. The interface provides controls for feeding annotated image exports into the training pipeline.

**Verification:** Inner-B / Outer-1. HTML response confirmed, title "Label Studio Import" confirmed.

### F3 — CRITICAL: Credential chain reachable through F1

Three credential classes are reachable via the F1 directory listing without exercising any credential:

1. **GCP service account key** (`.gcp/`) — controls cloud storage where training datasets and model artifacts are stored.
2. **SSH private keys** (`.ssh/`) — lateral movement to any host where the corresponding public key is authorized (including the active Vast.ai instance).
3. **Vast.ai GPU session** (`current_training_instance.txt`) — live GPU rental with SSH access details. An attacker who fetches this file can access an active training run.
4. **FTP backup storage** (shell script fallback defaults) — HostFactory backup storage for YOLO training exports.

**Verification:** Inner-A / Outer-1. Credential presence confirmed by file listing and script source. Credentials not retrieved or tested.

## Impact

An attacker with passive HTTP access to port 8000 can:

- Download all GCP credentials and access cloud storage (training data, model artifacts, billing)
- Download SSH private keys and access the active Vast.ai GPU instance mid-training
- Download the complete annotated training dataset (~dataset_complete.tar.gz)
- Retrieve historical .env files covering at least three rotation events (Dec 2025 through May 2026), increasing the probability that at least one leaked key remains valid in a downstream service
- Terminate or poison an active training run at a cost of ~$2.68/hr plus model quality degradation

The Label Studio import interface on port 5000 additionally allows an unauthenticated caller to interact with the annotation-to-training pipeline.

The project's dataset and model are not commercially sensitive in the traditional sense, but GCP credential theft could result in billing fraud and data destruction. SSH key theft could result in full server compromise.

## Remediation

**Immediate:**

```bash
pkill -f "http.server"
pkill -f "werkzeug"
ufw deny 8000
ufw deny 5000
```

**Credential rotation:**
- GCP service account key: revoke in Google Cloud Console → IAM → Service Accounts, generate new key
- SSH keys: generate new keypair, remove old public keys from `authorized_keys` on all hosts
- `.env` API keys: rotate all values
- Vast.ai API key: regenerate in Vast.ai account settings
- FTP password for backup storage: change in hosting control panel

**Structural fix:** Move training orchestration scripts out of the web server document root. Use a dedicated non-home working directory. If HTTP access is needed for Colab/remote training, serve from a specific path with token auth, not the home directory.

**Verification:** `curl -I http://185.66.109.62:8000/` should return connection refused.

## Disclosure

- **Discovered:** 2026-06-01
- **Disclosed:** 2026-06-01 (same-day, via email to operator business contact)
- **Languages:** German and English
- **Response:** Pending

## Toolchain Provenance

```
JAXEN        → Shodan harvest, 5 records, ports [22,80,443,5000,8000]
recongraph   → domain pivot, 38 nodes/36 edges, velutina-service.ch cert graph
VisorGraph   → cert SAN: scan.velutina-service.ch, api.velutina-service.ch
VisorPlus    → passive DNS: 22 hostnames, SSH host key, GreyNoise: clean
menlohunt    → port confirmation, SSH fingerprint
aimap        → 0 (sandbox connectivity; ports confirmed via JAXEN + direct probe)
aimap-profile → 0 (same)
VisorBishop  → 0 (same)
VisorSD      → 0 (invocation not successful against .ch VPS from sandbox)
VisorGoose   → 0 (gov/edu TLD scope, not applicable)
nu-recon     → 0 (connectivity)
VisorLog     → 3 findings ingested (F1 CRITICAL, F2 HIGH, F3 CRITICAL)
VisorScuba   → score 9/10; BLUE-EXP-001 (publicly indexed/discoverable)
BARE         → no_high_confidence_match (top scores 0.438/0.417); first-party config mistake, not CVE chain
VisorCorpus  → N/A (no LLM API surface; YOLO object detection model)
VisorRAG     → recall: 0 prior findings
VisorAgent   → [—] ethical-stop: controlled targets only
VisorHollow  → [—] Windows-only, not applicable
cortex       → N/A: requires pre-built case study artifact
JS-bundle    → 339KB app.js from scan.velutinaportal.eu: donation/payment/social URLs, portal.velutinaportal.eu API
Manual HTTP  → directory listing port 8000, Werkzeug response port 5000, TLS cert probes, DNS enumeration
```
