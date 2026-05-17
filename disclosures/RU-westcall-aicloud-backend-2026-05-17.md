Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com

2026-05-17

**Re:** Unauthenticated Elasticsearch with AI/RAG workload, WestCall LTD customer running cluster 'aicloud-backend' (Russian AI cloud, k3s)
**IP / Host:** `81.94.155.178` (cluster `docker-cluster (9f6ada389230) — cluster name 'aicloud-backend' visible on the node`)
**Severity:** HIGH

---

I'm an independent security researcher conducting good-faith AI infrastructure research under the NuClide Research umbrella (CISA disclosures CVE-2025-4364, ICSA-25-140-11). This is an unsolicited coordinated disclosure. No engagement exists with your organization. I have not read, modified, or exfiltrated documents — only index metadata (schema, counts, sizes) needed to identify the exposure.

---

## Summary

The Elasticsearch endpoint at `http://81.94.155.178:9200` is reachable from the public internet with no authentication. The cluster carries one or more AI / RAG workloads (dense_vector or knn_vector fields). no operator-specific TLS certificate; cluster name 'aicloud-backend' on the node config.

**State (verified 2026-05-17):** MID-WIPE: extortion marker planted, 6.6 GB Russian news index still alive

## Infrastructure

| Field | Value |
|---|---|
| IP | `81.94.155.178` |
| ES version | OpenSearch 2.14.0 |
| Cluster name | `docker-cluster (9f6ada389230) — cluster name 'aicloud-backend' visible on the node` |
| Country | Russia |
| Hosting | WestCall LTD (RU-WEST-CALL-20020815) |


### Alive on the cluster

| Index | Docs | Size | Notes |
|---|---:|---:|---|
| `russian_news` | 286,385 | 6.6 GB | 384d (all-MiniLM-L6-v2 embeddings) — Russian news article corpus |


## Extortion marker

An index named `read_me` is present on the cluster. This is the calling card of the **Meow / Indexrm extortion campaign**, an automated wipe-and-ransom operation. The marker indicates the attacker has already enumerated your cluster and either has wiped the data or is about to.

Sample marker content typically contains a ransom note pointing to a Bitcoin wallet and an email channel (`wendy.etabw@gmx.com` or one of two clone actor channels — `scandal@onionmail.org`, `db-recovery@sharebot.net`). We have separately reported all three channels to abuse contacts.

**Do not pay.** Our wallet-blockchain analysis (mempool.space) shows only ~5 victims across thousands of marked hosts have paid; the wallet has received roughly 0.018 BTC against a population of 4,400+ marked instances. Paying does not get your data back — the campaign is wipe-first, ransom-as-afterthought.


## Why it matters

I have no operator contact for this host. Sending to your network's RIPE-registered abuse address with a request to forward to the responsible customer.

The customer's cluster 'aicloud-backend' on 81.94.155.178:9200 carries a 286,385-document, 6.6 GB Russian news corpus ('russian_news', 384d MiniLM embeddings) and an attacker-planted 'read_me' Meow extortion marker. The data is still alive. The customer is at imminent risk of total loss.

## One-line fix

Bind the Elasticsearch HTTP listener to the loopback interface and require authentication for any non-local client. For a Docker deployment:

```
docker run -p 127.0.0.1:9200:9200 -e xpack.security.enabled=true elasticsearch:2.14.0
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
