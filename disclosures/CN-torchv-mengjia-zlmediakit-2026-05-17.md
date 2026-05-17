Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com

2026-05-17

**Re:** Unauthenticated Elasticsearch with AI/RAG workload, TorchV (operated by 杭州萌家网络科技 / Mengjia.net) — cluster ports answer on zlmediakit.com infrastructure
**IP / Host:** `120.26.18.206` (cluster `torchv-cluster`)
**Severity:** HIGH

---

I'm an independent security researcher conducting good-faith AI infrastructure research under the NuClide Research umbrella (CISA disclosures CVE-2025-4364, ICSA-25-140-11). This is an unsolicited coordinated disclosure. No engagement exists with your organization. I have not read, modified, or exfiltrated documents — only index metadata (schema, counts, sizes) needed to identify the exposure.

---

## Summary

The Elasticsearch endpoint at `http://120.26.18.206:9200` is reachable from the public internet with no authentication. The cluster carries one or more AI / RAG workloads (dense_vector or knn_vector fields). no operator-specific TLS certificate observed; cluster name 'torchv-cluster' is the unambiguous fingerprint.

**State (verified 2026-05-17):** ALIVE / NOT YET EXTORTED

## Infrastructure

| Field | Value |
|---|---|
| IP | `120.26.18.206` |
| ES version | Elasticsearch 8.17.0 |
| Cluster name | `torchv-cluster` |
| Country | China |
| Hosting | Alibaba Cloud (Aliyun) |


### Alive on the cluster

| Index | Docs | Size | Notes |
|---|---:|---:|---|
| `dataset_chunk_sharding_16_1024` | 1,563 | 26.9 MB | 1024d dense_vector — the RAG chunk store |
| `dataset_reference_sharding_16_1024` | 0 | 249 B | RAG reference index, empty |


## Why it matters

TorchV is a Chinese RAG / agentic-workflow product. The cluster name 'torchv-cluster' appears in the Elasticsearch node config alongside index naming 'dataset_chunk_sharding_16_1024'. The 1,563-document chunk store is the operative RAG knowledge base; anyone on the internet can dump it via the standard /_search endpoint.

## One-line fix

Bind the Elasticsearch HTTP listener to the loopback interface and require authentication for any non-local client. For a Docker deployment:

```
docker run -p 127.0.0.1:9200:9200 -e xpack.security.enabled=true elasticsearch:8.17.0
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
