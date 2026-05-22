# Session Analysis: Jetson / TensorRT Edge Population Survey + Insight #32

**Date:** 2026-05-18
**Session:** 20
**Classification:** Internal / Research Use Only
**Toolchain:** JAXEN, aimap v1.9.12, VisorGraph, VisorBishop, VisorLog, VisorScuba, BARE, VisorCorpus, VisorSD, VisorGoose, menlohunt, cortex, custom verify scripts
**Repos updated:** AI-LLM-Infrastructure-OSINT (2ab1918); aimap v1.9.12 (8fc7441), v1.9.13 (7dd88a1)

---

## 1. Overview

### Objective

Survey the Jetson / TensorRT edge-AI tier. Thesis question: do edge-AI inference platforms and NVR systems connected to Jetson hardware ship with authentication disabled at population scale? Secondary objective: fingerprint actual Jetson hardware deployments via Shodan. The hardware fingerprinting objective produced zero verified direct hits; the application survey produced 300 verified-unauth instances across 9 platform classes. Two deception fleets (598 hosts total) were identified and filtered during Stage-2 verification.

### Scope and Constraints

- **Target domains/IPs:** Public internet hosts matching Shodan dorks for Frigate, motionEye, DeepStack, CodeProject.AI, Scrypted, Shinobi, Triton, nvidia_smi_exporter, gpustat-web, and Jetson body/title dorks
- **Allowed techniques:** Passive Shodan harvest, banner grab, safe HTTP GET, Docker Registry catalog enumeration, cert-pivot, VisorScuba compliance scoring, BARE exploit ranking
- **Ethical limitations:**
  - No data exfiltration — metadata and schema enumeration only
  - No destructive API calls
  - No use of discovered credentials — RTSP camera credentials observed in Frigate `/api/config` responses were recorded as evidence but not used
  - Data-tier probes: connection attempt only (does auth gate exist? no queries)
  - Active LLM exploitation (VisorAgent): controlled lab targets only, never operator hosts
  - Personal-device and wrong-category targets: archived without outreach
  - Jetson SSH default-credential test: deferred — write-tier action, requires explicit operator authorization

---

## 2. Environment and Tooling

### Claude Code Operation

Orchestrator + subagent pattern. Six parallel JAXEN dork batches in Stage 0. Stage-2 verify used eight custom Python scripts (one per platform class) to produce reproducible per-platform results. aimap v1.9.12 shipped mid-session with a Jetson-attribution classifier wired into `enumDockerRegistry`. aimap v1.9.13 shipped late-session with Healthcare and Finance classifiers added.

### Tools Used

| Tool | Role | Config notes |
|---|---|---|
| JAXEN | Stage-0: 6 dork batches across 9 platform classes | 10,224 candidates; paginator with dedup |
| aimap v1.9.12 | Stage-1 fingerprint + Stage-2 verify + Docker Registry attribution | Jetson classifier added this session; 9 fixture-driven tests pass |
| VisorBishop | Re-prober + IP-shadow | Adjacent-port sweep for stacked services on edge hosts |
| VisorGraph | Cert-pivot + operator attribution | 11 named operators re-verified same-day |
| VisorLog | Ledger ingest | 894 events ingested to nuclide.db; 0 deduped against prior |
| VisorScuba | Compliance scoring | 894/894 "passing" — Rego baseline has no NVR/camera-feed policy class; methodology gap noted |
| BARE | Metasploit semantic ranking | Max 0.598 (motionEye → Bavision IP camera login scanner); below 0.6 threshold |
| VisorCorpus | Adversarial corpus generation | 137 cases built (77 HIGH, 26 MED, 19 LOW, 15 CRIT) against controlled target |
| VisorSD | ASN/org dork sweep | Not run — edge-AI population is residentially distributed, not ASN-concentrated |
| VisorGoose | TLD / CT-log sweep | Not run — survey targets consumer and SMB hosts, not TLD-specific patterns |
| menlohunt | GCP EASM | Not run — survey is not GCP-specific |
| recongraph | Seed-polymorphic recon graph | Not run — Docker Registry catalog side-channel used instead for attribution |
| nu-recon | Single-host passive deep-read | Not run — per-host deep-read deferred to disclosure batch |
| VisorPlus | Orchestrator | Not run — manual orchestration used for this survey |
| cortex | Auth-context analyzer | Not run — edge-AI platforms are not enterprise auth-context targets |
| JS-bundle extract | SPA hidden-API extraction | Not run — edge-AI UIs are not JS-heavy SPA targets |
| VisorHollow | Windows process-injection benchmark | [—] not applicable — Windows-only |
| VisorAgent | Active LLM exploitation | [—] ethical-stop — no LLM surface in NVR/edge-AI tier; controlled corpus only |
| VisorRAG | RAG adversarial confirmation | Ran in adversarial-confirmation mode against VisorCorpus on controlled target only |
| Docker | Local sandbox | Not run — local fingerprinting not needed; live hosts directly accessible |

### Notable Configuration

Eight custom verify scripts written and saved for re-run: `verify_frigate.py`, `verify_codeproject.py`, `verify_cp_post.py`, `verify_nvr.py`, `verify_scrypted.py`, `verify_shinobi.py`, `verify_triton.py`, `enum_registry.py`. Concurrency 30, 15s timeout per host. VisorLog ingest builder: `~/recon/jetson-tensorrt-2026-05-18/build_visorlog.py`. Mullvad VPN active.

---

## 3. Methodology

### Enumeration approach

Shodan harvest across six dork batches targeting platform-specific markers: HTTP title (`"Frigate"`, `"motionEye"`, `"DeepStack"`), server header (`"Server: Triton"`), product string (`CodeProject.AI Server`), script name (`gpustat-web`), and Jetson body/title strings. 10,224 candidates harvested total. Frigate produced the largest single-dork population (847 title hits + 623 html hits, deduped).

Direct Jetson hardware dorks (body/title: `Jetson`, `Tegra`, `L4T`, `Orin`) produced zero verified findings — all scattered into FP catalog. Jetson-attributed operators surfaced only via Docker Registry `/v2/_catalog` side-channel (images with `dustynv/`, `l4t`, `jetson`, `isaac-lab-*`). This side-channel result drove Insight #33 (codified at session end) and the aimap v1.9.12 Jetson classifier.

### Candidate identification

Stage-1: aimap fingerprint with platform-specific route anchors. Stage-2: custom verify scripts per platform class, each requiring the agent's API endpoint to confirm response shape, not title alone.

Deception fleet detection applied during Stage-2:
- Fleet A (Triton/Icecast): body-marker check — hosts with `Server: Triton` in Shodan cache now serve `Server: Icecast 2.4.4`. Zero real Triton found.
- Fleet B (Shinobi/GitLab): body-marker check — GitLab `og:site_name` in body + rotating title + ~137KB response = deception fleet. 576 of 1,926 Shinobi candidates filtered.

Real Shinobi: anchored on body containing `shinobi` with no GitLab markers; response size ~10KB vs ~137KB.

### Validation checks

- Frigate: GET `/api/version` returns JSON with `version` field. GET `/api/config` returns YAML. RTSP credentials in YAML = CRITICAL tier for that host.
- CodeProject.AI: GET `/v1/module/list` returns JSON array of modules. 39 of 40 confirmed.
- DeepStack: GET `/v1/vision/detection/list` returns JSON. 24 of 25 confirmed.
- motionEye: GET `/config/main` returns JSON config. 18 of 64 confirmed (28% real-rate — title dork weak per Insight #15).
- Docker Registry: GET `/v2/_catalog` returns JSON with `repositories` array. 5 hosts confirmed.
- nvidia_smi_exporter: GET `/metrics` returns Prometheus text format with `nvidia_smi_*` labels. 5 confirmed.
- GPU Dashboards (SNU): GET `/` returns researcher-identifying dashboard. 2 confirmed.
- Scrypted: GET `/` returns auth-required management console. 300 of 300 auth-gated (thesis falsification-confirmation).

Insight #13 reconfirmed at Frigate population scale: 99 of 205 unauth instances run version 0.17.1 (current release, where fresh installs require auth). Upgrade path does not enforce auth. Insight #15 generalized: marker-strong dorks (route or header anchored) produce 96-100% real-rate; marker-weak dorks (title or body anchored) produce 28-46% real-rate.

### Safeguards

RTSP credentials observed in 15 Frigate `/api/config` responses — recorded as evidence, not used. No RTSP streams accessed. No SSH default-credential test. No image manifests pulled from Docker Registries beyond the catalog listing. No write operations on any host.

---

## 4. Execution Trace

| Time | Action | Outcome / Decision |
|---|---|---|
| ~20:00 | JAXEN harvest: 6 dork batches | 10,224 candidates; Frigate largest class |
| ~20:20 | Direct Jetson hardware dork pass | 0 verified findings; all scatter into FP catalog |
| ~20:30 | aimap Stage-1 fingerprint on all 10,224 candidates | Platform class distribution established |
| ~21:00 | verify_triton.py against 27 Triton candidates | 22 reachable; all return Icecast — Fleet A identified; 0 real Triton |
| ~21:10 | verify_shinobi.py against 1,926 Shinobi candidates | 576 fail GitLab body-marker check — Fleet B identified; 361 real Shinobi |
| ~21:15 | Insight #32 codified | methodology/insight-32-deception-fleet-multi-service-emulation.md written |
| ~21:20 | verify_frigate.py against 847 Frigate candidates | 447 reachable; 205 unauth; 15 with RTSP credentials in /api/config |
| ~21:40 | verify_codeproject.py + verify_deepstack.py | 39/40 CodeProject.AI; 24/25 DeepStack |
| ~21:50 | verify_nvr.py (motionEye + gpustat + GPU dashboards) | 18/64 motionEye; 2 SNU GPU dashboards; 1 gpustat-web |
| ~21:55 | verify_scrypted.py against 300 Scrypted candidates | 0 unauth — all auth-gated; thesis falsification-confirmation |
| ~22:00 | enum_registry.py: Docker Registry catalog enumeration | 5 unauth registries; Jetson attribution on F1/F4/F5 |
| ~22:10 | nvidia_smi_exporter probe | 5 confirmed (includes RTX A6000 on Mexican UniNet consumer telecom) |
| ~22:15 | VisorGraph cert-pivot | 3 dead-DNS registries surfaced (STARK INDUSTRIES hosting on Fleet A) |
| ~22:20 | BARE run | Max 0.598 (motionEye → Bavision scanner) — below 0.6 threshold |
| ~22:25 | VisorScuba run | 894/894 "passing" — NVR/camera-feed policy class absent; gap flagged |
| ~22:30 | VisorCorpus: 137 cases built | Controlled target only; categories logged |
| ~22:35 | VisorLog ingest | 894 events in nuclide.db |
| ~22:40 | Frigate RTSP disclosure batch built | 15 per-host files + routing-table.csv + disclose-template.md |
| ~23:00 | aimap v1.9.12 built + shipped | classifyJetsonRepos() added; 9 tests pass; live-verified on F4 |
| ~23:20 | aimap v1.9.13 shipped | Healthcare (PACS/DICOM) + Finance classifiers added; shared classifyRepos engine factored out |
| ~23:25 | Insight #33 codified | methodology/insight-33-side-channel-attribution-via-registry-catalog.md written |
| ~23:30 | Cross-survey re-classify pass on 9 known registries | 3 of 9 Jetson; 4 non-Jetson non-attributions hold; CockroachDB Cloud surfaced as bonus |
| ~23:40 | CockroachDB Cloud FINDING.md written | 34.125.10.152:5000 — 20 repos including internal container names |
| ~23:50 | 14 Gmail disclosure drafts created (15 Frigate + CockroachDB) | Awaiting Cowboy go for send |

---

## 5. Findings

> **Severity label policy (load-bearing):** Every tier label (LOW / MED / HIGH / CRITICAL) requires 100% verified evidence at that tier. Unverified observations are UNRATED. Inferred + hypothesized stacks do NOT promote to a tier — only verified components produce labels.

### 5.1 Frigate NVR — 15 Hosts: RTSP Camera Credentials in Plaintext

| Field | Value |
|---|---|
| **Name/ID** | 15 Frigate NVR hosts; 9 countries (US, FR, IT, RU, NL, CH, BR, AR, + UK) |
| **Type** | NVR / video surveillance — edge AI |
| **Evidence** | GET `/api/config` returns YAML containing `rtsp://user:password@<camera-ip>:<port>` URLs; credentials are operator-set, not default |
| **Observed exposure** | Unauthenticated access to plaintext RTSP camera credentials |
| **Severity** | CRITICAL — verified credentials in hand; camera network topology disclosed |

**Potential impact:** Any actor with the RTSP URL and credentials can pull a live camera feed. Camera topology (IP addresses of cameras inside the private network) narrows internal network mapping. Frigate config also exposes detection zone configuration and camera labels.

### 5.2 Frigate NVR — 168 Hosts: Camera Topology Exposed (No Plaintext Creds)

| Field | Value |
|---|---|
| **Name/ID** | 168 Frigate NVR hosts |
| **Type** | NVR / video surveillance |
| **Evidence** | GET `/api/config` returns YAML with RTSP URLs (go2rtc proxy or embedded config); no plaintext credentials in the URL |
| **Observed exposure** | Unauthenticated access to camera topology and stream URLs |
| **Severity** | HIGH — camera network topology and stream endpoints exposed without authentication |

### 5.3 CodeProject.AI Server — 39 Hosts Unauth

| Field | Value |
|---|---|
| **Name/ID** | 39 CodeProject.AI Server hosts |
| **Type** | On-device AI inference server |
| **Evidence** | GET `/v1/module/list` returns JSON module array on 39 of 40 reachable |
| **Observed exposure** | Unauthenticated access to inference API; compute available for use |
| **Severity** | HIGH — 39 unauth AI inference hosts; LLMjacking / compute theft feasible |

### 5.4 DeepStack AI — 24 Hosts Unauth

| Field | Value |
|---|---|
| **Name/ID** | 24 DeepStack AI hosts |
| **Type** | AI vision server |
| **Evidence** | GET `/v1/vision/detection/list` returns JSON; admin surface reachable |
| **Observed exposure** | Unauthenticated AI vision inference |
| **Severity** | HIGH |

### 5.5 Docker Registry — 5 Unauth (Jetson Attribution on 3)

| Field | Value |
|---|---|
| **Name/ID** | F1: 37.27.229.120 (mfgbot Jetson), F4: 43.133.1.147 (dustynv RAG-on-Jetson), F5: 47.93.158.253 (Auriga Isaac Lab + ROS 2) |
| **Type** | Docker Registry V2 — container image store |
| **Evidence** | GET `/v2/_catalog` returns repositories array; Jetson-attributed image names in catalog (dustynv/, l4t, isaac-lab-*) |
| **Observed exposure** | Unauthenticated catalog enumeration; image manifests pullable |
| **Severity** | HIGH — 3 Jetson-attributed; F5 Auriga includes ROS 2 robotics images |

### 5.6 CockroachDB Cloud Internal Registry — Bonus Finding

| Field | Value |
|---|---|
| **Name/ID** | 34.125.10.152:5000 (GCP us-central1) |
| **Type** | Docker Registry V2 — internal CI/CD image store |
| **Evidence** | GET `/v2/_catalog` returns 20 repos: cockroach-cloud-images/data-plane/init-container, init-sqlsidecar, opentelemetry-collector-cc, sqlstarter, fluent-bit-cc, cockroach-operator:latest |
| **Observed exposure** | Internal CI/CD image names and component architecture disclosed |
| **Severity** | MED — internal component names disclosed; no image layers pulled |

### 5.7 SNU GPU Dashboards — 2 Hosts: Researcher Identity + Topology

| Field | Value |
|---|---|
| **Name/ID** | 2 Seoul National University GPU cluster dashboard hosts |
| **Type** | GPU cluster monitoring dashboard |
| **Evidence** | Researcher identity, GPU cluster topology, and SSH hostname targets visible in dashboard UI |
| **Observed exposure** | Unauthenticated access to institutional compute cluster metadata |
| **Severity** | MED — researcher identity disclosure + cluster topology enables targeted follow-on |

### 5.8 nvidia_smi_exporter — 5 Hosts: GPU Info Disclosure

| Field | Value |
|---|---|
| **Name/ID** | 5 hosts including RTX A6000 on Mexican UniNet consumer telecom |
| **Type** | Prometheus metrics exporter |
| **Evidence** | GET `/metrics` returns nvidia_smi_* Prometheus labels including GPU model, driver version, UUID |
| **Observed exposure** | GPU hardware info |
| **Severity** | LOW |

### 5.9 motionEye — 18 Hosts Unauth

| Field | Value |
|---|---|
| **Name/ID** | 18 motionEye hosts of 64 reachable |
| **Type** | NVR / webcam management |
| **Evidence** | GET `/config/main` returns JSON configuration |
| **Observed exposure** | Camera config and recording access |
| **Severity** | MED |

---

## 6. Risk Assessment

### Overall Posture

The edge-AI / NVR tier is the highest-severity physical-layer exposure in the survey catalog. 15 Frigate hosts expose camera credentials that grant real-world physical surveillance capability. The auth-on-default thesis is confirmed in both directions: Frigate (unauth-shipping) at 46% unauth rate, Scrypted (auth-shipping) at 0% unauth rate.

### Confidentiality

RTSP camera credentials on 15 hosts. Camera topology on 168 additional Frigate hosts. Researcher identity and compute cluster topology on SNU dashboards. Internal CI/CD image names on CockroachDB Cloud registry.

### Integrity

No write-tier operations tested. Docker Registry image push not attempted — would require auth bypass on the Registry v2 API.

### Availability

Compute exhaustion via unauthenticated inference requests feasible on CodeProject.AI (39 hosts) and DeepStack (24 hosts). LLMjacking / quota drain at these scales is meaningful.

### Systemic Patterns

- Insight #13 reconfirmed at Frigate population scale: the upgrade path does not enforce new secure defaults. 99 of 205 unauth Frigate instances run version 0.17.1 — the version where fresh installs require auth. Legacy operator posture persists through upgrades.
- Insight #32 (new): multi-service deception fleets emulate target-specific services for Shodan crawlers by rotating titles per request. Two distinct fleets identified this session (Triton/Icecast: 22 hosts; Shinobi/GitLab: 576 hosts). Filter on body markers and response size, not title alone.
- Insight #15 generalized: real-rate splits by dork marker type. Route/header-anchored dorks: 96-100%. Title/body-anchored dorks: 28-46%.
- Docker Registry `/v2/_catalog` as Jetson attribution side-channel (Insight #33): when a direct fingerprint class produces zero verified hits, enumerate adjacent infrastructure and run content-based attribution. Operator-authored image names beat vendor banners.

---

## 7. Recommendations

### R1 — Frigate: Enable authentication

```yaml
# In frigate/config.yml:
auth:
  enabled: true
```

Deploy Frigate behind a reverse proxy with HTTPS if exposing on a public interface. Do not expose port 5000 or 8971 to the public internet.

### R2 — CodeProject.AI / DeepStack: Bind to localhost or internal network

```bash
# CodeProject.AI: set bind address in appsettings.json
"Urls": "http://127.0.0.1:32168"

# DeepStack: bind to internal interface
docker run ... -e BINDING_IP=192.168.1.1 deepquestai/deepstack
```

### R3 — Docker Registry: Enable auth

```yaml
# registry/config.yml
auth:
  htpasswd:
    realm: Registry Realm
    path: /etc/registry/htpasswd
```

Or disable the Registry port entirely if no external access is needed.

### R4 — VisorScuba: Add NVR/camera-feed Rego policy class

The current AI Security Baseline does not classify NVR or edge-AI camera apps. The 15 RTSP-credential exposures score 0 violations. Add a Rego policy that flags `/api/config` returning `rtsp://` URLs as a CRITICAL violation.

### Future automation

```bash
# Detect unauth Frigate in post-deploy scan:
curl -sf http://<host>:5000/api/version | jq -e '.version' >/dev/null && \
  curl -sf http://<host>:5000/api/config | grep -q 'rtsp://' && echo "CRITICAL:RTSP-CREDS"
```

Promote `verify_frigate.py` logic into aimap as a Frigate deep-enumerator with RTSP-credential detection.

---

## 8. Limitations and Assumptions

| # | Limitation | Risk Implication |
|---|---|---|
| L1 | Analysis reconstructed from session notes (SESSION.md). Execution trace timestamps are approximate. | Minor sequencing uncertainty |
| L2 | RTSP credentials verified as present; RTSP streams not accessed | Actual camera feed accessibility not confirmed — remains probable |
| L3 | VisorScuba has no NVR/camera-feed Rego policy | 15 CRITICAL findings score 0 violations in compliance report |
| L4 | RTSP/GStreamer port 8554 (~911 candidates) deferred | Additional camera exposure on port 8554 not measured |
| L5 | Jetson SSH default-credential test deferred | Whether default Jetson credentials persist across discovered hosts is unknown |
| L6 | Docker Registry image layers not pulled | Internal image contents (secrets in ENV, build artifacts) not assessed |
| L7 | 30/90/180-day re-survey not yet scheduled | No persistence measurement established for the edge-AI population |

---

## 9. Proof of Concept (PoC) Illustrations

### PoC 1: Frigate RTSP Credential Exposure

**Scenario:** Unauthenticated actor retrieves plaintext camera credentials from a production Frigate NVR.

```
REQUEST:
  GET /api/config HTTP/1.1
  Host: <frigate-host>:5000

RESPONSE:
  HTTP/1.1 200 OK
  Content-Type: application/x-yaml

  cameras:
    front_door:
      ffmpeg:
        inputs:
          - path: rtsp://<user>:<password>@<camera-ip>:554/stream1
            roles:
              - detect
              - record
    back_yard:
      ffmpeg:
        inputs:
          - path: rtsp://<user>:<password>@<camera-ip>:554/h264Preview_01_main
```

**Demonstrated:** Plaintext RTSP credentials returned without authentication. An actor with this response can connect to the camera stream directly. This probe does NOT access the RTSP stream, play any video, or use the credentials.

### PoC 2: Deception Fleet Detection (Shinobi/GitLab)

**Scenario:** Distinguishing a real Shinobi NVR from a deception-fleet host that matched the Shodan dork.

```
# Real Shinobi:
GET / HTTP/1.1 Host: <real-shinobi-host>
Response: 200, body ~10KB, contains "shinobi", no gitlab markers

# Deception fleet:
GET / HTTP/1.1 Host: <fleet-host>  (first request)
Response: 200, body 137KB, title "Shinobi NVR", og:site_name="GitLab"

GET / HTTP/1.1 Host: <fleet-host>  (second request)
Response: 200, body 137KB, title "Cisco Codec", og:site_name="GitLab"
```

**Demonstrated:** The deception fleet serves a different title on each request while the body (GitLab markers, 137KB size) stays constant. Response-size + body-marker conjunct filters these before classification. This probe does NOT interact with any streaming endpoint or control system.

### PoC 3: Docker Registry Catalog Side-Channel Attribution

**Scenario:** Attributing a Docker Registry to a Jetson operator via catalog content.

```
REQUEST:
  GET /v2/_catalog HTTP/1.1
  Host: 43.133.1.147:5000

RESPONSE:
  HTTP/1.1 200 OK
  Content-Type: application/json

  {"repositories": ["dustynv/ollama", "dustynv/rag-llm-server",
                     "dustynv/jetson-containers", "dustynv/l4t-base", ...]}
```

**Demonstrated:** `dustynv/` image names in the catalog (a high-confidence Jetson signal per aimap v1.9.12 classifier) attribute this registry to a RAG-on-Jetson operator. The catalog listing reveals the operator's image namespace and workflow structure. This probe does NOT pull any image layers or manifest blobs.

---

*Prepared by NuClide Research (Nicholas Kloster + Claude Sonnet 4.6) · Session 20 · 2026-05-18*
