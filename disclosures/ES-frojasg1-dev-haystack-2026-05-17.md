Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com

2026-05-17

**Re:** Unauthenticated Elasticsearch with AI/RAG workload, frojasg1-ia.es customer (no AI data observed, looks like a developer test box)
**IP / Host:** `51.91.106.5` (cluster `docker-cluster (083f5e907db8)`)
**Severity:** LOW

---

I'm an independent security researcher conducting good-faith AI infrastructure research under the NuClide Research umbrella (CISA disclosures CVE-2025-4364, ICSA-25-140-11). This is an unsolicited coordinated disclosure. No engagement exists with your organization. I have not read, modified, or exfiltrated documents. Only index metadata (schema, counts, sizes) needed to identify the exposure.

---

## Summary

The Elasticsearch endpoint at `http://51.91.106.5:9200` is reachable from the public internet with no authentication. The cluster carries one or more AI / RAG workloads (dense_vector or knn_vector fields). TLS SAN includes frojasg1-ia.es.

**State (verified 2026-05-17):** ALIVE / NOT EXTORTED / clean dev

## Infrastructure

| Field | Value |
|---|---|
| IP | `51.91.106.5` |
| ES version | Elasticsearch 7.9.2 |
| Cluster name | `docker-cluster (083f5e907db8)` |
| Country | France |
| Hosting | OVH |


### Alive on the cluster

| Index | Docs | Size | Notes |
|---|---:|---:|---|
| `haystack_test` | 0 | 208 B | empty Haystack test index |
| `label` | 0 | 208 B | empty |


## Why it matters

Sending to OVH abuse as an informational notice. The customer at 51.91.106.5 has an unauthenticated Elasticsearch 7.9.2 on port 9200 with empty 'haystack_test' and 'label' indices. No user data observed; cluster looks like a developer test box. Two notes for the customer:

1. ES 7.9.2 is end-of-life. Upgrade or take offline.
2. Once they begin indexing real data, the cluster will be visible to extortion crews running the same Elasticsearch sweeps that hit several other operators in our 2026-05-17 survey. Recommend the customer bind to 127.0.0.1 before that happens.

## One-line fix

Bind the Elasticsearch HTTP listener to the loopback interface and require authentication for any non-local client. For a Docker deployment:

```
docker run -p 127.0.0.1:9200:9200 -e xpack.security.enabled=true elasticsearch:7.9.2
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
