Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com

2026-05-17

**Re:** Unauthenticated Elasticsearch with AI/RAG workload, Equant Tech (lms.equant-tech.com). Waffarha deals LMS
**IP / Host:** `161.97.148.0` (cluster `waffarha-cluster (waffarha-node)`)
**Severity:** HIGH

---

I'm an independent security researcher conducting good-faith AI infrastructure research under the NuClide Research umbrella (CISA disclosures CVE-2025-4364, ICSA-25-140-11). This is an unsolicited coordinated disclosure. No engagement exists with your organization. I have not read, modified, or exfiltrated documents. Only index metadata (schema, counts, sizes) needed to identify the exposure.

---

## Summary

The Elasticsearch endpoint at `http://161.97.148.0:9200` is reachable from the public internet with no authentication. The cluster carries one or more AI / RAG workloads (dense_vector or knn_vector fields). TLS SAN includes lms.equant-tech.com (Egyptian LMS hosting Waffarha deals/coupons content).

**State (verified 2026-05-17):** MID-WIPE: extortion marker planted, course data still alive

## Infrastructure

| Field | Value |
|---|---|
| IP | `161.97.148.0` |
| ES version | OpenSearch 2.11.0 |
| Cluster name | `waffarha-cluster (waffarha-node)` |
| Country | Egypt (hosted Germany / Contabo) |
| Hosting | Contabo GmbH |


### Alive on the cluster

| Index | Docs | Size | Notes |
|---|---:|---:|---|
| `waffarha-deals` | 355 | 6.6 MB | 768d — deals/coupons content with embeddings |
| `.plugins-ml-model-group` | 6 | 17.5 KB | OpenSearch ML model group metadata |
| `.plugins-ml-model` | 16 | 55.9 KB | OpenSearch ML model registry |
| `.plugins-ml-task` | 16 | 10.2 KB | OpenSearch ML training tasks |


## Extortion marker

An index named `read_me` is present on the cluster. This is the calling card of the **Meow / Indexrm extortion campaign**, an automated wipe-and-ransom operation. The marker indicates the attacker has already enumerated your cluster and either has wiped the data or is about to.

Sample marker content typically contains a ransom note pointing to a Bitcoin wallet and an email channel (`wendy.etabw@gmx.com` or one of two clone actor channels, `scandal@onionmail.org`, `db-recovery@sharebot.net`). We have separately reported all three channels to abuse contacts.

**Do not pay.** Our wallet-blockchain analysis (mempool.space) shows only ~5 victims across thousands of marked hosts have paid; the wallet has received roughly 0.018 BTC against a population of 4,400+ marked instances. Paying does not get your data back. The campaign is wipe-first, ransom-as-afterthought.


## Why it matters

The 'waffarha-deals' index (355 docs, 768d embeddings) is your Waffarha LMS knowledge base and is still alive on the cluster. The attacker has planted the 'read_me' marker but has not deleted the data yet. Snapshot before they finish.

## One-line fix

Bind the Elasticsearch HTTP listener to the loopback interface and require authentication for any non-local client. For a Docker deployment:

```
docker run -p 127.0.0.1:9200:9200 -e xpack.security.enabled=true elasticsearch:2.11.0
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
