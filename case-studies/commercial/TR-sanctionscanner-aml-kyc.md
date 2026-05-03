# sanctionscanner.com — Turkish AML/KYC Compliance SaaS — 79M KYB Records + Live Client Monitoring Exposed

_NuClide Research · 2026-05-03_

---

## Summary

sanctionscanner.com is a Turkish AML/KYC compliance SaaS serving financial institutions. Their production Elasticsearch cluster — three nodes — was reachable on port 9200 with `xpack.security.enabled=false` and no network firewall. The cluster holds 79 million Know Your Business (KYB) company records, 6.2 million individual sanctions/watchlist records, 877K document-number records, and two live client monitoring queries screening real persons in real time. A prior automated ransomware bot already found it — a `read_me` extortion index is present. NuClide independently confirmed full read access without credentials.

Disclosed to info@sanctionscanner.com + security@elastic.co on 2026-05-03.

---

## Infrastructure

| Field | Value |
|---|---|
| IP | 168.119.90.62 |
| Hoster | Hetzner DE |
| Cluster name | eu-cluster |
| Nodes | es01, es02, es03 |
| Elasticsearch version | 7.17.19 |
| Runtime | Docker Compose |
| Open port | 9200 (TCP, no auth) |
| Operator | sanctionscanner.com (Istanbul, TR) |

---

## Index Inventory

| Index | Document count | Category |
|---|---|---|
| `kyb_data_index_prod` | 79,067,927 | KYB company records |
| `allsearchindexv2prod` | 6,230,703 | Individual sanctions/watchlist records |
| `documentsearchindexprod` | 877,138 | Document number records (tax IDs, reg numbers) |
| `ongoing_monitoring_organization_2_queries` | 2 | Live client screening queries |
| `read_me` | 1 | Extortion demand (prior attacker) |

---

## Findings

### F1 — 79M KYB Company Records Unauthenticated (CRITICAL)

`kyb_data_index_prod` is fully readable. Records cross-reference global business registries against sanctions lists — the core commercial product.

Proof:
```
GET http://168.119.90.62:9200/kyb_data_index_prod/_search?size=3
HTTP 200 — live records returned, no authentication
```

Sample record fields:
```json
{
  "id": "...",
  "companyName": "...",
  "companyNumber": "...",
  "cleanFullName": "...",
  "status": "...",
  "establishmentDate": "...",
  "listTypeId": "...",
  "matchRate": "...",
  "isDeleted": false
}
```

Observed sample: Colombian business registry entities cross-referenced against sanctions lists. The `matchRate` field indicates sanctions-screening score for each entity.

GDPR Article 9 applies where natural persons are identifiable through company records (sole traders, beneficial owners, etc.).

---

### F2 — 6.2M Individual Sanctions/Watchlist Records Unauthenticated (CRITICAL)

`allsearchindexv2prod` contains individual records sourced from global sanctions and watchlist databases.

Sample record fields:
```json
{
  "id": "...",
  "fullName": "...",
  "cleanFullName": "...",
  "nationalities": [...],
  "listId": "...",
  "typeId": "...",
  "isIndividual": true,
  "createdDate": "..."
}
```

`listId` references OFAC SDN, EU Consolidated List, UN Security Council, and PEP databases. Exposure of this index enables:
- Enumeration of which sanctioned individuals are in the screening corpus
- Identification of persons whose names return no match (negative screening intelligence)
- PEP list membership inference — special-category data under GDPR Article 9

---

### F3 — Live Client Monitoring Queries Expose Real Persons Being Screened (HIGH)

`ongoing_monitoring_organization_2_queries` contains active screening jobs submitted by a sanctionscanner.com client (organizationId: 2).

Sample record:
```json
{
  "id": 20,
  "cleanQueryString": "ADEM YILMAZ",
  "listType": 1,
  "organizationId": 2,
  "period": 1
}
```

This discloses: which real persons a financial institution is actively monitoring, the institution's customer/counterparty list in aggregate, and the monitoring cadence (`period`). This is live operational data from a paying client — not historical. A second query record is also present.

---

### F4 — Prior Ransomware Extortion Index Present (HIGH)

The `read_me` index was written by an automated Elasticsearch ransomware bot before NuClide's discovery. NuClide did not place this index.

Extortion note content:
- Demanded 0.0041 BTC to `bc1q38rjul6gdamfflf6p4ukz0ymtvfgfv2j9saf6r`
- Contact address: `wendy.etabw@gmx.com`
- Consistent with the Meow/ElasticSearch ransomware campaign pattern

Implication: the cluster was already found, accessed, and potentially exfiltrated before this disclosure. GDPR Article 33 (72-hour breach notification) obligations are therefore likely already triggered regardless of whether the operator paid the ransom — the data was accessible to an unauthenticated third party with sufficient time to operate.

---

### F5 — Root Cause: xpack.security Disabled Cluster-Wide (CRITICAL)

All three nodes (es01, es02, es03) share the same Docker Compose configuration with:
```yaml
ES_JAVA_OPTS: "-Xms512m -Xmx512m"
xpack.security.enabled: "false"
network.host: "0.0.0.0"
```

`network.host=0.0.0.0` binds port 9200 to all interfaces including the public NIC. `xpack.security.enabled=false` disables the Elasticsearch native authentication layer. The combination is the standard misconfiguration responsible for the majority of Elasticsearch mass-exposure incidents since 2017.

---

## Regulatory Context

| Framework | Relevant provision |
|---|---|
| GDPR | Article 9 — special category data (sanctions/PEP status is sensitive); Article 33 — breach notification within 72h where exfiltration cannot be ruled out |
| FATF Recommendation 10 | Customer due diligence data must be protected; exposure of KYB/KYC screening results undermines AML integrity |
| Turkish KVKK | Law No. 6698, Article 12 — data controller must take technical measures to prevent unauthorized access |

---

## Remediation

```yaml
# docker-compose.yml — apply to all three nodes
environment:
  - xpack.security.enabled=true
  - xpack.security.transport.ssl.enabled=true
  - network.host=_local_
```

Rotate all Elasticsearch credentials post-fix. Audit access logs from the prior-attacker window. File GDPR Article 33 notification with applicable supervisory authority if exfiltration cannot be excluded.

---

## Disclosure

- **Discovered:** 2026-05-03
- **Disclosed to:** info@sanctionscanner.com + security@elastic.co on 2026-05-03
- **Status:** Awaiting acknowledgment
- **Prior attacker evidence:** `read_me` extortion index present; breach likely predates this disclosure
