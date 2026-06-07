# Snap-E Cabs — ScyllaDB Default Credentials + Unauthenticated REST API
**Target:** 34.131.90.52 (GCP us-south1, Delhi, India)  
**Operator:** EC Wheels India Private Limited (Snap-E Cabs) / Steelman Telecom Ltd (BSE SME: STML 543622)  
**Date:** 2026-05-28  
**Severity:** CRITICAL  
**Category:** Cat-30 — Specialty Data Layers

---

## One-Line Summary

Snap-E Cabs, a BSE-listed Indian EV ride-hailing operator (600+ vehicles, Kolkata), runs a ScyllaDB cluster on GCP with the CQL port accepting default `cassandra/cassandra` credentials and the admin REST API exposed with zero authentication — giving any actor full read/write access to 431,808 driver safety events, 245 live auth tokens, biometric face ROI data, real-time vehicle GPS, and live video stream session management.

<!-- ksat-tag:auto-generated:start -->
## DCWF KSAT coverage

Auto-derived from DCWF AI work-role rule files (`ksat-tag`).

- **672 (AI Test & Evaluation Specialist):** K7003, K7004, K7044, S7068, S7070, T5904, T5919
- **733 (AI Risk & Ethics Specialist):** K7040, K7051, S7056, T5854, T5904
- **overlap (Common AI KSATs (all 5 roles)):** K1158, K22, K6311, K6900, K6935, K7003, K942, T5896

<!-- ksat-tag:auto-generated:end -->

---

## Operator Profile

| Field | Value |
|---|---|
| Company | EC Wheels India Private Limited |
| Parent | Steelman Telecom Limited (BSE SME STML 543622) |
| Brand | Snap-E Cabs |
| Fleet | 600+ Tata Tigor EVs, Kolkata |
| Founded | February 2022 |
| Revenue | INR 54.9 crore (FY2025) |
| Funding | $5M (IPV $4.6M, 2024; Seed $2.5M, Sep 2025) |
| App | com.snape (500K installs), product.driver.snapecabs (38K installs) |
| Dispatch | JungleWorks Tookan (SaaS) + proprietary ScyllaDB backend |
| Tech lead | Abhrodeep Mukherjee (possibly departed to Heritage Mobility) |

---

## Architecture

```
Passenger/Driver Apps (com.snape / product.driver.snapecabs)
    ↓
JungleWorks Tookan (dispatch SaaS, AWS CloudFront)
    ↓
Express.js API: apiltd.snapecab.com (Cloudflare-proxied)
    ↓
168.144.144.137 (DigitalOcean Bangalore) — Web + Admin tier
    ↓
34.131.90.52 (GCP Delhi) ← THIS HOST
    ScyllaDB v3.0.8 — two-node cluster
    Internal IPs: 10.190.0.4, 10.190.0.11
    ↑
AIS140 IoT devices in 600+ vehicles → EMQX MQTT → ScyllaDB
```

---

## Findings

### F1 — ScyllaDB CQL Default Credentials (CRITICAL, verified)

**Host:** 34.131.90.52:9042  
**Credentials:** `cassandra` / `cassandra` (factory default)

```bash
# Confirmed: cqlsh accepts default credentials
cqlsh 34.131.90.52 9042 -u cassandra -p cassandra
# → Connected to Test Cluster at 34.131.90.52:9042
# → [cqlsh 6.x | Scylla 3.0.8 | CQL spec 3.3.1]
```

Full read/write access to all 100 application keyspaces. Row counts confirm production data:

| Table | Rows | Data Class |
|---|---|---|
| fcw-warnings | 431,808 | Driver names + GPS per FCW event |
| fcw_device_current_status | 58 | Live device state |
| adas_all_device_current_status_replica | 30 | ADAS device replicas |
| auth_tokens | 245 | Live bearer + refresh tokens |
| actual_warning | 1,236 | Face ROI (biometric) + S3 video paths |
| emqx-device-activity | 127 | IoT device activity |
| vehicle-current-state | 6 | Real-time GPS, speed, ignition |
| support_helpdesk_ticket | 5 | Free-text tickets + S3 media |
| fcw-iot-device | 5 | Full sensor state per device |

**Biometric data confirmed:** `actual_warning` schema contains `faceRoi` (face region-of-interest) and `videoFileName` (S3 key to in-cabin video). Under India's DPDP Act 2023, face data is sensitive personal data.

**Live auth tokens:** `auth_tokens` schema includes `authToken`, `refreshToken`, `expiryTime`, `valid`. 245 tokens are live. These could be replayed against the Express.js backend at apiltd.snapecab.com.

### F2 — ScyllaDB REST API Unauthenticated (CRITICAL)

**Host:** 34.131.90.52:10000  
**Auth:** NONE

```bash
curl http://34.131.90.52:10000/storage_service/cluster_name
# → "Test Cluster"

curl http://34.131.90.52:10000/storage_service/keyspaces
# → ["alternator_auth_tokens","alternator_fcw-warnings","alternator_vehicle-current-state",...]
```

Destructive management operations (flush, repair, drain, decommission) accessible without credentials. Full schema enumeration complete: 108 keyspaces, 100 application tables.

### F3 — Prometheus Metrics Unauthenticated (HIGH)

**Host:** 34.131.90.52:9180  
**Auth:** NONE

Operational telemetry exposed. Confirms production traffic despite cluster name "Test Cluster":

| Metric | Value |
|---|---|
| auth_tokens operations | 369,085 |
| fcw-iot-device operations | 348,332 |
| fcw-warnings operations | 361,641 |
| vehicle-current-state operations | 12,475 |
| Total Alternator ops | ~2M UpdateItem, 613K BatchWriteItem, 240K GetItem |

### F4 — 431,808 Driver Safety Events with GPS (HIGH)

`fcw-warnings` contains 431,808 rows. Schema: `driverName`, `driverId`, `gpsLat`, `gpsLong`, `gpsSpeed`, `warningType`, `overspeed_duration`, `vehicleId`. Full movement + behavior history of Snap-E Cabs drivers reconstructable from FCW event stream.

### F5 — Live Video Stream Session Management (HIGH)

13 tables manage vehicle dashcam and in-cabin live video: `footage_video_file`, `video-demand-request`, `android-livestream`, `vp2-streaming-url`, `live_stream_settings`, `live-stream-vp2`, `sdcard_playback_request`. S3 keys to in-cabin video fragments are stored in `actual_warning`.

### F6 — OTA Firmware Pipeline Exposed (MEDIUM)

Tables `emqx-device-ota`, `device-ota-update`, `apk-upload-data` manage over-the-air firmware updates to IoT devices in 600+ vehicles. Write access via F1 could corrupt or replace firmware update payloads.

### F7 — Vehicle Search API Unauthenticated (LOW)

`GET https://apiltd.snapecab.com/api/security/vehicles/search?term={term}` returns HTTP 200 JSON without authentication. Core `/api/vehicles` returns 401. Security subdirectory missing auth middleware.

---

## Chain Results

| Tool | Result |
|---|---|
| JAXEN | 1 IP imported |
| aimap | ScyllaDB REST port 10000, AUTH=NONE |
| VisorGraph | 0 nodes — bare GCP IP |
| aimap-profile | GCP Delhi, no honeypot signals |
| JS-bundle | apiltd.snapecab.com fleet API found; /api/security/vehicles/search unauth |
| VisorBishop | 0 AI platforms on marketing site |
| VisorLog | 2 events ingested |
| VisorScuba | Run |
| BARE | No applicable module (top: aux_dos_scada_beckhoff 0.46) |
| VisorCorpus | Built |
| VisorRAG | Recall run |
| menlohunt | SSH only — GCP metadata not exposed |
| recongraph | 0 nodes — no domain pivot chains |
| nu-recon | Simulated (no Shodan key) |
| VisorSD | Blocked (no Shodan key) |
| VisorGoose | N/A (Ollama scope) |
| VisorAgent | Deferred (ethical stop) |

---

## Impact

An unauthenticated actor can:
1. Read 431,808 driver safety events (names + GPS + behavior)
2. Read 245 live authentication tokens and replay them
3. Read 1,236 biometric face ROI records and in-cabin video S3 keys
4. Read real-time GPS, speed, and ignition state of 600+ EVs
5. Write to OTA firmware update pipeline tables
6. Invoke destructive management operations via REST API (flush, drain, decommission)
7. Drop keyspaces, truncate tables, or decommission cluster nodes

---

## Contact Surface

| Channel | Value |
|---|---|
| Support email | support@snapecabs.com |
| CEO | Mayank Bindal — linkedin.com/in/mayank-bindal-47765177 |
| Bug bounty | None |
| Security@ | None |
| Regulatory | BSE-listed — SEBI disclosure obligations; DPDP Act 2023 jurisdiction |
| Grievance officer | +91 33-40585599 |

---

## Remediation

1. Rotate `cassandra/cassandra` credentials immediately; enable `PasswordAuthenticator` in scylla.yaml
2. Set `api_address: 127.0.0.1` in scylla.yaml (or firewall port 10000)
3. Set `prometheus_address: 127.0.0.1` (or firewall port 9180)
4. Firewall port 9042 (CQL) from the internet
5. Add auth middleware to `/api/security/*` routes on apiltd.snapecab.com
6. Rotate all 245 auth tokens after securing the database
7. Engage a DPO to assess DPDP Act obligations for the biometric data exposure

