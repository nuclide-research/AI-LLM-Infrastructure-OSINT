Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com

2026-05-17

**Re:** Unauthenticated Elasticsearch with AI/RAG workload, Hooper ERP (chatbiz.hooperp.com, 'Hoop AI')
**IP / Host:** `123.60.173.230` (cluster `docker-cluster (bad5d40a4f45)`)
**Severity:** HIGH

---

I'm an independent security researcher conducting good-faith AI infrastructure research under the NuClide Research umbrella (CISA disclosures CVE-2025-4364, ICSA-25-140-11). This is an unsolicited coordinated disclosure. No engagement exists with your organization. I have not read, modified, or exfiltrated documents — only index metadata (schema, counts, sizes) needed to identify the exposure.

---

## Summary

The Elasticsearch endpoint at `http://123.60.173.230:9200` is reachable from the public internet with no authentication. The cluster carries one or more AI / RAG workloads (dense_vector or knn_vector fields). TLS SAN includes chatbiz.hooperp.com (Hooper ERP BI inventory chatbot).

**State (verified 2026-05-17):** FULLY WIPED — extortion marker present, no business data remaining

## Infrastructure

| Field | Value |
|---|---|
| IP | `123.60.173.230` |
| ES version | Elasticsearch 8.18.2 |
| Cluster name | `docker-cluster (bad5d40a4f45)` |
| Country | China |
| Hosting | Huawei Cloud |


### Already wiped (per attacker, between morning probe and second probe today)

| Index | Docs / prior state | Size | Notes |
|---|---:|---:|---|
| `hooper_bi_dws_inventory (deleted)` | — | — | 1536d ERP inventory chatbot data — was alive this morning, now gone |


## Extortion marker

An index named `read_me` is present on the cluster. This is the calling card of the **Meow / Indexrm extortion campaign**, an automated wipe-and-ransom operation. The marker indicates the attacker has already enumerated your cluster and either has wiped the data or is about to.

Sample marker content typically contains a ransom note pointing to a Bitcoin wallet and an email channel (`wendy.etabw@gmx.com` or one of two clone actor channels — `scandal@onionmail.org`, `db-recovery@sharebot.net`). We have separately reported all three channels to abuse contacts.

**Do not pay.** Our wallet-blockchain analysis (mempool.space) shows only ~5 victims across thousands of marked hosts have paid; the wallet has received roughly 0.018 BTC against a population of 4,400+ marked instances. Paying does not get your data back — the campaign is wipe-first, ransom-as-afterthought.


## Why it matters

Earlier today (2026-05-17 morning UTC) this cluster carried index 'hooper_bi_dws_inventory' with 1536-dimensional dense_vector embeddings — your BI inventory chatbot's knowledge base. Within 12 hours the attacker has completed the wipe. Only the 'read_me' extortion marker remains.

## One-line fix

Bind the Elasticsearch HTTP listener to the loopback interface and require authentication for any non-local client. For a Docker deployment:

```
docker run -p 127.0.0.1:9200:9200 -e xpack.security.enabled=true elasticsearch:8.18.2
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
