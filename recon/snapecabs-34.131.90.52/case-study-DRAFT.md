# Snap-E Cabs — Unauthenticated ScyllaDB REST API + Fleet Telemetry Exposure
**Target:** 34.131.90.52 (GCP Delhi, India)  
**Operator:** EC Wheels India Private Limited (Snap-E Cabs) / Steelman Telecom Ltd (BSE SME: STML 543622)  
**Date:** 2026-05-28  
**Status:** DRAFT — Weapons squad schema pending

---

## Summary

Snap-E Cabs, an Indian EV ride-hailing startup (600+ Tata Tigor EVs, Kolkata), operates a ScyllaDB cluster on GCP Delhi with the management REST API and Prometheus metrics endpoint exposed to the internet with zero authentication. The cluster holds 106 tables spanning real-time vehicle telemetry, driver PII, passenger ride logs, ADAS device data from vehicle-mounted Forward Collision Warning systems, live video stream session management, and an active ML configuration layer. The Alternator (DynamoDB-compatible) API on port 8000 is auth-enforced; the REST API on port 10000 and Prometheus on port 9180 are not.

Prometheus metrics confirm this is an active production cluster (not staging), with 369K auth_token operations and 348K IoT device operations recorded since last restart, despite the cluster being named "Test Cluster."

---

## Operator Profile

| Field | Value |
|---|---|
| Company | EC Wheels India Private Limited |
| Parent | Steelman Telecom Limited (BSE SME STML 543622) |
| Brand | Snap-E Cabs |
| Fleet size | 600+ Tata Tigor EVs |
| Location | Kolkata, West Bengal, India (ops); New Delhi (GCP region) |
| Founded | February 2022 |
| Revenue | INR 54.9 crore (FY2025) |
| Funding | $5M total ($4.6M IPV, 2024; $2.5M Seed, Sep 2025) |
| Head of Technology | Abhrodeep Mukherjee (may have departed to Heritage Mobility) |
| Dispatch platform | JungleWorks Tookan (SaaS) + proprietary ScyllaDB backend |

---

## Findings

### F1 — ScyllaDB REST API Unauthenticated (CRITICAL)

**Host:** 34.131.90.52:10000  
**Service:** ScyllaDB REST API (Seastar httpd)  
**Auth:** NONE

The ScyllaDB admin REST API is internet-accessible without credentials. Confirmed via:

```bash
# Cluster name
curl -s http://34.131.90.52:10000/storage_service/cluster_name
# → "Test Cluster"

# Keyspace list
curl -s http://34.131.90.52:10000/storage_service/keyspaces
# → ["alternator_snapecabs-ride-logs","alternator_driver-data","alternator_vehicle-current-state",...]

# Version
curl -s http://34.131.90.52:10000/storage_service/release_version
# → "3.0.8"
```

The REST API exposes destructive management operations (flush, repair, drain, decommission) with no credential check. Read operations expose full cluster topology, all keyspace schemas, and table metadata.

**ScyllaDB version 3.0.8** is a 2021 build. [TODO: CVE check for this version line]

### F2 — Prometheus Metrics Unauthenticated (HIGH)

**Host:** 34.131.90.52:9180  
**Auth:** NONE

Full ScyllaDB Prometheus metrics exposed. Confirms active production traffic:

| Table | Operations |
|---|---|
| auth_tokens | 369,085 |
| fcw-warnings | 361,641 |
| fcw-iot-device | 348,332 |
| fcw_device_current_status_replica | 340,827 |
| vehicle-current-state | 12,475 |
| emqx-commands-logs | 1,817 |

Total Alternator operations: ~2M UpdateItem, 613K BatchWriteItem, 240K GetItem. This is live production traffic.

### F3 — 106 Tables: Fleet Telemetry + Driver PII + Video Streams (CRITICAL — unverified tier)

Full table inventory from REST API (schema-only enumeration, no records read):

**Fleet Telemetry / IoT:**
`fcw-warnings`, `fcw-iot-device`, `fcw_device_current_status`, `fcw_device_current_status_replica`, `fcw_ignition_data`, `adas_linux_device_messages`, `device-status`, `device_list`, `device_certificates`, `emqx-*` (6 tables), `vehicle-current-state`, `IotData`

**Driver / Passenger PII:**
`user_accounts`, `auth_tokens`, `driver-data`, `driver-vehicle-mapping`, `driver-performance`, `firebase_device_token`, `passenger-occupancy-report`

**Ride Operations:**
`snapecabs-ride-logs`, `trip-info`, `mahindra-trip-payloads`, `fleet-daily-summary`, `route-path`, `route-info`, `address_book`, `support_helpdesk_ticket`

**Live Video Streaming:**
`device-streaming`, `android-livestream`, `vp2-streaming-url`, `video-demand-request`, `footage_video_file`, `live_stream_settings`, `live-stream-vp2`, `vp2-streaming-url`, `download-sd-card-vp2`, `sdcard_playback_request`

**ML / AI:**
`ml-config`, `ml-config-device-request`, `fleetgpt_subscription`

### F4 — Unauthenticated Vehicle Search API (LOW)

**Host:** apiltd.snapecab.com (Cloudflare-proxied Express.js fleet API)  
**Endpoint:** `GET /api/security/vehicles/search?term={term}`  
**Auth:** NONE (returns 200 JSON, no auth challenge)

Vehicle search returns data without authentication. Core `/api/vehicles` endpoint returns 401. The `security` sub-path is missing auth middleware.

### F5 — Multiple Services Co-located on App Tier (INFO)

**Host:** 168.144.144.137 (DigitalOcean Bangalore)  
Four internet-facing services:
- Port 3000: "LTD FLEET MANAGEMENT" React dashboard
- Port 5000: Admin API (JWT-gated), Vite/shadcn panel
- Port 8000: Main PHP website
- Port 8080: "Sufin Green" — unrelated EV company sharing this host

---

## Architecture

```
Passenger/Driver App (com.snape / product.driver.snapecabs)
    ↓
JungleWorks Tookan (dispatch SaaS, AWS CloudFront)
    ↓
Proprietary backend: apiltd.snapecab.com (Express.js, Cloudflare)
    ↓
168.144.144.137 (DigitalOcean Bangalore) — Web + Admin tier
    ↓
34.131.90.52 (GCP Delhi) — ScyllaDB Alternator
    ↑
AIS140 IoT devices in 600+ vehicles → EMQX MQTT → ScyllaDB
```

---

## Chain Results

| Tool | Result |
|---|---|
| JAXEN | 1 IP imported, no Shodan enrichment (API key invalid) |
| aimap | ScyllaDB REST confirmed, AUTH=NONE |
| VisorGraph | 0 nodes/edges — bare GCP IP, no domain pivot chains |
| aimap-profile | GCP Delhi, no honeypot signals |
| JS-bundle | apiltd.snapecab.com API base found; /api/security/vehicles/search unauth confirmed |
| VisorLog | 2 events ingested |
| VisorScuba | [TODO: review output] |
| BARE | No applicable module (top: auxiliary_dos_scada_beckhoff_twincat, 0.46 — below threshold) |
| VisorCorpus | Built |
| VisorRAG | Recall run |
| VisorAgent | Deferred (ethical-stop) |
| menlohunt | [TODO] |
| recongraph | [TODO] |
| nu-recon | [TODO] |

---

## Contact Surface

- support@snapecabs.com (grievance officer)
- Mayank Bindal, CEO — LinkedIn: linkedin.com/in/mayank-bindal-47765177
- No bug bounty program
- No security@ address
- BSE-listed — financial regulatory disclosure obligations under SEBI

---

## Impact

An unauthenticated actor can:
1. Read full cluster topology and all table schemas via REST API
2. Read all Prometheus metrics revealing operational state and table activity
3. Invoke destructive management operations (flush, repair, drain) via REST API
4. Access vehicle search endpoint without authentication on the Express API

Data at risk (schema-confirmed, records not accessed):
- Real-time GPS positions of 600+ EVs
- Driver profiles and performance data
- Ride logs including Mahindra vehicle trip payloads
- ADAS device telemetry (Forward Collision Warning data)
- Live video stream session tokens
- Authentication tokens (369K active operations)
- IoT device certificates

