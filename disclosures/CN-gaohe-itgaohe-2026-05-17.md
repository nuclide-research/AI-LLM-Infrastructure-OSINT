Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com

2026-05-17

**Re:** Unauthenticated Elasticsearch with AI/RAG workload, Gaohe IT (itgaohe.com)
**IP / Host:** `120.27.113.59` (cluster `docker-cluster (1f42c439c34e)`)
**Severity:** HIGH

---

I'm an independent security researcher conducting good-faith AI infrastructure research under the NuClide Research umbrella (CISA disclosures CVE-2025-4364, ICSA-25-140-11). This is an unsolicited coordinated disclosure. No engagement exists with your organization. I have not read, modified, or exfiltrated documents. Only index metadata (schema, counts, sizes) needed to identify the exposure.

---

## Summary

The Elasticsearch endpoint at `http://120.27.113.59:9200` is reachable from the public internet with no authentication. The cluster carries one or more AI / RAG workloads (dense_vector or knn_vector fields). TLS SAN includes itgaohe.com.

**State (verified 2026-05-17):** MID-WIPE: extortion marker planted, AI data still alive

## Infrastructure

| Field | Value |
|---|---|
| IP | `120.27.113.59` |
| ES version | Elasticsearch 8.12.2 |
| Cluster name | `docker-cluster (1f42c439c34e)` |
| Country | China |
| Hosting | Alibaba Cloud (Aliyun) |


### Alive on the cluster

| Index | Docs | Size | Notes |
|---|---:|---:|---|
| `ai-index` | 65 | 1.2 MB | 1536d (OpenAI text-embedding-3-large) — the AI knowledge base |


## Extortion marker

An index named `read_me` is present on the cluster. This is the calling card of the **Meow / Indexrm extortion campaign**, an automated wipe-and-ransom operation. The marker indicates the attacker has already enumerated your cluster and either has wiped the data or is about to.

Sample marker content typically contains a ransom note pointing to a Bitcoin wallet and an email channel (`wendy.etabw@gmx.com` or one of two clone actor channels, `scandal@onionmail.org`, `db-recovery@sharebot.net`). We have separately reported all three channels to abuse contacts.

**Do not pay.** Our wallet-blockchain analysis (mempool.space) shows only ~5 victims across thousands of marked hosts have paid; the wallet has received roughly 0.018 BTC against a population of 4,400+ marked instances. Paying does not get your data back. The campaign is wipe-first, ransom-as-afterthought.


## Why it matters

An attacker has planted the Meow extortion marker (index name 'read_me') on this cluster. Your AI knowledge base ('ai-index', 65 documents, 1536d OpenAI embeddings) is still alive. The attacker has not yet deleted it. Take it offline and restore from backup before they do.

## One-line fix

Bind the Elasticsearch HTTP listener to the loopback interface and require authentication for any non-local client. For a Docker deployment:

```
docker run -p 127.0.0.1:9200:9200 -e xpack.security.enabled=true elasticsearch:8.12.2
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
