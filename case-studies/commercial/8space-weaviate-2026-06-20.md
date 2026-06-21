---
type: case-study
severity: MEDIUM
date: 2026-06-20
title: "8Space: Unauthenticated Read, Write, and Delete on a Workplace-Safety RAG Vector Store"
summary: "8Space, a Romanian occupational health and safety SaaS, ran a Weaviate vector store with no authentication. We confirmed unauth read, write, and delete against a four-class schema. The schema was empty at the time of testing, so severity is MEDIUM today and escalates to HIGH once populated with hazard, PPE, and Romanian equipment-inspection records."
tags:
  - weaviate
  - vector-database
  - unauth
  - cwe-306
  - ohs-compliance
  - saas
sidenotes:
  - kind: host
    label: Target
    kv:
      - k: Operator
        v: "8Space (app.8space.io)"
      - k: Sector
        v: "Occupational Health and Safety SaaS"
      - k: Location
        v: "Nuremberg, DE (Hetzner Online)"
      - k: Severity
        v: MEDIUM
      - k: Disclosed
        v: "2026-06-20"
  - kind: see-also
    label: Classification
    kv:
      - k: Primary
        v: "CWE-306 Missing Authentication for Critical Function"
      - k: Secondary
        v: "CWE-284 Improper Access Control"
      - k: OWASP
        v: "LLM04 Data and Model Poisoning"
---

# 8Space: Unauthenticated Read, Write, and Delete on a Workplace-Safety RAG Vector Store

_NuClide Research -- Nicholas Kloster -- 2026-06-20_

---

## Summary

8Space runs a workplace safety and OHS compliance platform at app.8space.io. The web app is auth-gated. The Weaviate vector store behind it is not. Anyone on the internet could read the schema, write objects, and delete entire classes without credentials.

The schema was empty at the time of testing. Four classes were defined, all with zero records. That is why severity is MEDIUM today. The store was pre-production, staging, or recently wiped. The access primitives are real and confirmed. Once the classes hold the data they are built for, the same open door becomes a path to safety-guidance poisoning and compliance-record falsification.

We confirmed read, write, and delete. We reversed the one record we wrote.

---

## Attack Surface

| Port | Software | Role | Auth |
|------|----------|------|------|
| 8080 | Weaviate 1.27.4 | RAG vector database -- 4-class schema, 0 records | None |
| 7700 | Meilisearch | Search index | Auth-gated |
| 9443 | Portainer 2.41.1 | Docker management UI | Auth-gated |
| 8090 | Beszel | System monitoring | Partial (health open, 0 monitored systems) |
| 5000 | Express.js | Application backend | Internal only |

Port 8080 was the open door. The web app, the search index, the container manager, and the monitoring agent all asked who was calling. Weaviate did not.

Host: 49.13.228.92, RDNS static.92.228.13.49.clients.your-server.de, Hetzner Online, Nuremberg, Germany. Port 50051 (gRPC) showed open via nmap, unconfirmed by the scan tool.

---

## Operator Attribution

8Space, app.8space.io, a Romanian workplace safety and OHS compliance SaaS.

Evidence:
- Port 80 redirects to https://app.8space.io/
- Login page title reads "Login | 8Space"
- Schema classes prefixed `Ro` carry an `authorizedCompanyPin` field, the Romanian CUI tax number
- Classes model occupational health and safety domains: PPE labels, hazard labels, equipment inspection certifications

---

## Data Exposed

Four classes, zero records. The schema described what the platform intends to store, not data that was present.

| Class | Domain | Notable fields |
|-------|--------|----------------|
| WorkPosition | Job position definitions | positionId, employerId, name, description, linkedJobs |
| WorkJob | Job task hazard analysis | jobId, employerId, hazardLabels, ppeLabels, activityType |
| RoElectrical | Romanian electrical inspection records | machineName, manufacturer, measuredValue, meetsConditions, authorizedCompanyName, authorizedCompanyPin |
| RoMechanicalEngineering | Romanian mechanical inspection records | machineName, manufacturer, measuredValue, meetsConditions, authorizedCompanyName, authorizedCompanyPin |

The `WorkJob` class is the safety-critical slice. Its `hazardLabels` and `ppeLabels` fields define what protective equipment a worker is required to use for a given task. The `RoElectrical` and `RoMechanicalEngineering` classes hold `meetsConditions`, a PASS or FAIL compliance result per machine, plus `authorizedCompanyPin`, the Romanian CUI tax identifier of the certified inspection company. These map to Romanian regulated equipment certification, likely ISCIR pressurized-equipment or electrical-installation inspection records.

No records were present, so nothing was exfiltrated. The schema and field names are the finding. They describe the data class at risk: occupational safety guidance and regulated equipment compliance results tied to identifiable Romanian companies.

---

## What We Confirmed

**Read:** Pulled the full schema without credentials. Four classes returned, all with zero objects. HTTP 200.

**Write:** Posted one canary object to `WorkPosition` via the batch endpoint. Weaviate returned STATUS=SUCCESS. HTTP 200. Canary ID `5f970cad-25b3-46f7-80ec-dcfbb50440ec`.

**Delete:** Removed the canary. HTTP 204.

Node topology: node1, status HEALTHY, version 1.27.4, lastSnapshotIndex 0, meaning no recovery point exists.

The one record we wrote we removed. No other writes or class deletions were performed against the live store.

---

## Impact

**Current state, 0 records:** Schema exposed. Read, write, and delete confirmed. No data to exfiltrate. The risk today is the open primitive, not data loss.

**When populated, escalates to HIGH:**

Read. Romanian company equipment inspection records become legible. The `authorizedCompanyPin` (CUI) is a company regulatory identifier. Pass and fail results per machine, per company, become readable. GDPR exposure follows if individual inspectors are named.

Write, safety-guidance poisoning. `WorkJob` hazardLabels and ppeLabels define required protective equipment. A false record can strip PPE requirements from a hazardous task. Electrical, mechanical, and pressurized-equipment work then proceeds without protection. If the 8Space RAG agent surfaces these records as authoritative guidance, the result is physical safety risk to workers.

Write, compliance-record falsification. `RoElectrical` and `RoMechanicalEngineering` store `meetsConditions` for regulated equipment. False PASS records for equipment that should fail create liability exposure for the authorized inspection company and put the employer in regulatory breach.

Delete. Wipes all job hazard analysis, equipment certifications, and position definitions. With lastSnapshotIndex 0 there is no recovery point, so a class delete is complete platform data loss.

---

## Remediation

**Immediate:** Firewall port 8080 to the internal network only. The web app reaches Weaviate from inside the host. No outside party needs to.

**Short-term:** Enable Weaviate's API-key or OIDC authentication. Restrict the gRPC port 50051 the same way. Confirm Meilisearch, Portainer, and Beszel stay credentialed.

**Medium-term:** Plant canary objects in the production store to detect unauthorized writes. Configure snapshots so lastSnapshotIndex is non-zero and a recovery point exists. Add periodic schema and record-count monitoring to catch unexpected deletes.

---

## Disclosure

Finding documented 2026-06-20 under NuClide Research responsible-disclosure practice. Prior coordinated disclosures from this researcher include CVE-2025-4364 and ICSA-25-140-11, both through CISA.
