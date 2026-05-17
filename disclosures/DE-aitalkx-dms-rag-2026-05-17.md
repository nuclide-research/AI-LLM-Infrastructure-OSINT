Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com

2026-05-17

**Re:** Unauthenticated Elasticsearch with AI/RAG workload, AItalkx (aitalkx.com) — DMS RAG / document workflow
**IP / Host:** `84.247.189.64` (cluster `docker-cluster (372e2468a9d2)`)
**Severity:** HIGH

---

I'm an independent security researcher conducting good-faith AI infrastructure research under the NuClide Research umbrella (CISA disclosures CVE-2025-4364, ICSA-25-140-11). This is an unsolicited coordinated disclosure. No engagement exists with your organization. I have not read, modified, or exfiltrated documents — only index metadata (schema, counts, sizes) needed to identify the exposure.

---

## Summary

The Elasticsearch endpoint at `http://84.247.189.64:9200` is reachable from the public internet with no authentication. The cluster carries one or more AI / RAG workloads (dense_vector or knn_vector fields). TLS SAN includes aitalkx.com.

**State (verified 2026-05-17):** MID-WIPE: extortion marker planted, DMS document corpus still alive

## Infrastructure

| Field | Value |
|---|---|
| IP | `84.247.189.64` |
| ES version | OpenSearch 2.19.1 |
| Cluster name | `docker-cluster (372e2468a9d2)` |
| Country | Germany |
| Hosting | Contabo GmbH (registrar: Vautron Rechenzentrum AG) |


### Alive on the cluster

| Index | Docs | Size | Notes |
|---|---:|---:|---|
| `dms_data` | 6,762 | 6.3 MB | primary document store |
| `dms_vectors` | 1,727 | 30.4 MB | knn_vector 768d — DMS document embeddings |
| `n_general_document_generaldocument` | 258 | 785.6 KB | general documents |
| `n_general_document_dms_purchase_order_workflow` | 58 | 87.8 KB | purchase-order workflow documents |
| `n_general_folder_generalfolder` | 106 | 86.9 KB | folder hierarchy |
| `n_general_folder_workspace` | 59 | 53.3 KB | workspaces |
| `dms_documentvectors` | 0 | 208 B | knn_vector schema, empty |


## Extortion marker

An index named `read_me` is present on the cluster. This is the calling card of the **Meow / Indexrm extortion campaign**, an automated wipe-and-ransom operation. The marker indicates the attacker has already enumerated your cluster and either has wiped the data or is about to.

Sample marker content typically contains a ransom note pointing to a Bitcoin wallet and an email channel (`wendy.etabw@gmx.com` or one of two clone actor channels — `scandal@onionmail.org`, `db-recovery@sharebot.net`). We have separately reported all three channels to abuse contacts.

**Do not pay.** Our wallet-blockchain analysis (mempool.space) shows only ~5 victims across thousands of marked hosts have paid; the wallet has received roughly 0.018 BTC against a population of 4,400+ marked instances. Paying does not get your data back — the campaign is wipe-first, ransom-as-afterthought.


## Why it matters

Your DMS RAG corpus is fully exposed: 6,762 document records, 1,727 knn_vector embeddings (dms_vectors, 768d), plus purchase-order workflow documents. The 'read_me' marker is in place. Take it offline before the attacker completes the wipe.

## One-line fix

Bind the Elasticsearch HTTP listener to the loopback interface and require authentication for any non-local client. For a Docker deployment:

```
docker run -p 127.0.0.1:9200:9200 -e xpack.security.enabled=true elasticsearch:2.19.1
```

If the cluster is on a host network: set `network.host: 127.0.0.1` in `elasticsearch.yml`, restart, then put it behind a reverse proxy or VPN with authentication.

For OpenSearch clusters: enable the security plugin with `plugins.security.disabled: false`.

## Reference

Companion case study with the full 22-host survey:
AI-LLM-Infrastructure-OSINT/blob/main/case-studies/commercial/22-ai-stack-attribution-2026-05-17.md

Companion methodology notes:
- Snapshot vs delta measurement (Insight #29)
- WHOIS over slug heuristics for disclosure routing (Insight #04)

Happy to provide additional forensic detail if useful. No response is required.

Regards,
Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com
