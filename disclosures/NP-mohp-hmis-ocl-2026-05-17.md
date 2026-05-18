---
institution: Government of Nepal. Ministry of Health and Population (HMIS / Open Concept Lab)
ip: 103.69.124.214
to: incident@npcert.org.np; security@hmis.gov.np; mohp@mohp.gov.np
cc: NP-CERT
severity: CRITICAL
status: DRAFT
outcome: drafted
date: 2026-05-17
---

**To:** incident@npcert.org.np (NP-CERT)
**Cc:** Ministry of Health and Population. HMIS team
**Subject:** URGENT, Unauthenticated Open Concept Lab terminology server (ocl.hmis.gov.np) currently under active extortion attack, disclosure window ≤ 12 hours

---

Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com

2026-05-17

**Re:** Unauthenticated Elasticsearch backing the Open Concept Lab clinical-terminology server on `ocl.hmis.gov.np`. Active extortion in progress
**IP / Host:** 103.69.124.214:9200 (TLS cert SAN: `ocl.hmis.gov.np`)
**Severity:** CRITICAL. Government healthcare infrastructure under active automated attack

---

I am an independent security researcher conducting good-faith AI/LLM-infrastructure exposure research. I hold CISA-coordinated disclosures CVE-2025-4364 and ICSA-25-140-11. This is an unsolicited disclosure made under coordinated-disclosure principles. I have not accessed, modified, or exfiltrated any data beyond what is strictly necessary to confirm the exposure and write this notification, and **no document contents from your indices have been read**. Only the index list, cluster identity, and field-type schema metadata were retrieved.

This disclosure is **time-critical**. A live automated extortion campaign (Meow / Indexrm family) is in the process of wiping this host as of 2026-05-17 03:00 UTC. Your data has not yet been deleted but the attacker has established control of the cluster.

---

## What was found

At `103.69.124.214:9200` an Elasticsearch 8.15.2 cluster is reachable over plain HTTP without authentication. The TLS cert on port 443 carries the SAN `ocl.hmis.gov.np`, identifying this host as the Open Concept Lab (OCL) clinical-terminology server within Nepal's national Health Management Information System (`hmis.gov.np`).

A `GET /` request returns:

```
{
  "cluster_name": "docker-cluster",
  "version": { "number": "8.15.2", ... }
}
```

A `GET /_cat/indices` request returns the index list **without requiring credentials**:

| Index | Documents | Size | Notes |
|---|---:|---:|---|
| `concepts` | 318,114 | 27.7 MB | The OCL clinical-concept dictionary (drugs, diagnoses, procedures) with `_embeddings.vector` (dense_vector cosine) field for semantic search |
| `mappings` | 3,806 | 813 KB | Concept-to-code mappings |
| `collections` | 87 | 31.6 KB | OCL concept-collection metadata |
| `organizations` | 3 | 9.3 KB | Org records |
| `sources` | 29 | 22.6 KB | Source vocabulary records |
| `user_profiles` | 9 | 11.2 KB | **Admin / curator account records** |
| `url_registries` | 0 | 249 B | Empty |
| **`read_me`** | **112** | **122.8 KB** | **⚠ Meow extortion index — created by an attacker, your indices have NOT YET been wiped** |

The presence of the `read_me` index indicates an automated extortion actor has already established control. **Typical Meow time-from-index-plant to data-wipe is < 24 hours.** Other unauthenticated Elasticsearch hosts in this campaign (3,604 of 5,037 in our 24-hour window) have been fully wiped, with only the `read_me` index remaining.

**Your data is currently still alive**, the `concepts`, `mappings`, `user_profiles` indices retain their original document counts. **Action within the next ~12 hours has a real chance of preserving the data.**

---

## Why this matters

1. **Open Concept Lab on `ocl.hmis.gov.np`** is the clinical-terminology backbone for Nepal's national health-data ecosystem. A vector-searchable dictionary of clinical concepts (drugs, diagnoses, procedures, ICD-10 / SNOMED mappings) used by downstream systems to standardize records.

2. The `user_profiles` index contains administrator / curator account records. **PII risk if the index is read or exfiltrated before wipe**.

3. The same `hmis.gov.np` domain space (per CT log enumeration) hosts:
   - `fhir.hmis.gov.np`: FHIR healthcare-interoperability gateway
   - `elmis.hmis.gov.np`: electronic Logistics Management (vaccines, drugs)
   - `erecord.hmis.gov.np`: Electronic Records
   - `dashboard.hmis.gov.np`, `monitoring.hmis.gov.np`, `pss.hmis.gov.np`
   - `sudurpashchim.hmis.gov.np` (Far-Western Province deployment)

   I have **not probed those subdomains** as part of this disclosure. They should be audited internally for the same exposure pattern.

4. The 5,037-host Meow campaign currently wiping unauthenticated Elasticsearch worldwide is well-documented; Nepal-specific exposure of a national-health system inside the campaign is materially worse than a generic exposure because (a) the data class is healthcare-system terminology + admin accounts, (b) the operator is a national-government ministry, and (c) the data is mid-extortion not yet wiped.

---

## Immediate actions

1. **Disconnect `103.69.124.214:9200` from the public internet now.** Block at the perimeter or stop the Elasticsearch service.
2. **Take an Elasticsearch snapshot before any other action**, in case the attacker triggers wipe-on-rescan: `POST /_snapshot/<repo>/<name>?wait_for_completion=true`. Store the snapshot off-cluster.
3. **Audit the other `*.hmis.gov.np` subdomains** listed above for the same unauth posture. Each should require `xpack.security.enabled=true` and password-protected `elastic` user.
4. **Rotate `user_profiles` credentials** for any administrator/curator accounts indexed there.
5. **Do not pay the attacker.** Meow / Indexrm extortion notes typically demand cryptocurrency; the operators do not return data after payment.

---

## Permanent remediation (Elasticsearch hardening)

The host is running ES 8.15.2 with `xpack.security.enabled=false`. The default in the official `elasticsearch:8.x` Docker image. To enable authentication:

1. **In `elasticsearch.yml`:**

   ```yaml
   xpack.security.enabled: true
   xpack.security.transport.ssl.enabled: true
   xpack.security.http.ssl.enabled: true
   ```

2. **Set passwords** via:

   ```bash
   bin/elasticsearch-setup-passwords auto
   ```

3. **Restart Elasticsearch.**

4. **Verify** with `curl -u elastic:<password> http://<host>:9200/_cluster/health`. Unauthenticated requests should now return `401`.

---

## What we did and did not do

We **did**:
- Run `GET /` and `GET /_cluster/health` to confirm the cluster is Elasticsearch and identify the version
- Run `GET /_cat/indices` to enumerate the index list and counts
- Read field-type metadata via `GET /<index>/_mapping` on the `concepts` index to confirm `dense_vector` schema
- Resolve the TLS cert SAN via standard `crt.sh` CT-log enumeration

We **did not**:
- Read any document contents from any index (including `read_me`, `user_profiles`, `concepts`)
- Modify, delete, or write to any index
- Probe sibling subdomains (`fhir.hmis.gov.np`, `elmis.hmis.gov.np`, etc.). Those are for your internal team to audit

All findings derive from cluster metadata and field-type schema only. Per restraint protocol: collection / index / field names are sufficient evidence of an exposed RAG/vector workload. Payload reads are unnecessary and out of scope.

---

## Re-verify command

Once the fix is deployed, this command should return `401`:

```bash
curl -i http://103.69.124.214:9200/_cat/indices
```

(Currently returns `200 OK` with the index list as JSON.)

---

## References

- **Elasticsearch security defaults**: Elastic ships X-Pack security available but disabled in the public Docker image (`elasticsearch:8.x`). Enabling auth is a one-line config + a password-setup command. The 71.6% campaign-wipe rate across 5,037 unauth ES hosts in the 2026-05-16 to 2026-05-17 window suggests this default is being aggressively exploited.
- **Meow ransomware**: automated extortion family active against unauth Elasticsearch and MongoDB since 2020. Identifiers in `read_me` documents typically include a cryptocurrency address and a 48-hour wipe threat.
- **NuClide Research methodology**: public OSINT methodology including Insight #28 (24h survey shelf-life for extortion-targeted platforms) is at `https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT/blob/main/methodology/insight-28-survey-shelf-life-exposure-to-extortion.md`.

---

I am available to assist NP-CERT and the Ministry of Health team if useful, at no cost, under the same coordinated-disclosure framing. Please confirm receipt of this report. Even a one-line acknowledgement is sufficient to indicate the message reached the right team.

Time-zone: I am at UTC−6 (Denver, CO, USA).

Nicholas Michael Kloster
   NuClide Research
   nicholas@nuclide-research.com
   PGP: https://nuclide-research.com/pgp.txt
   research portal: https://nuclide-research.com
