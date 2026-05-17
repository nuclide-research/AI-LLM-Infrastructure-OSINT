Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com

2026-05-17

**Re:** Unauthenticated Elasticsearch with AI/RAG workload, Guangxi Travel Development Technology Co., Ltd. (广西旅发科技股份有限公司, gxota.com)
**IP / Host:** `112.124.16.227` (cluster `es-docker-cluster (es01)`)
**Severity:** HIGH

---

I'm an independent security researcher conducting good-faith AI infrastructure research under the NuClide Research umbrella (CISA disclosures CVE-2025-4364, ICSA-25-140-11). This is an unsolicited coordinated disclosure. No engagement exists with your organization. I have not read, modified, or exfiltrated documents — only index metadata (schema, counts, sizes) needed to identify the exposure.

---

## Summary

The Elasticsearch endpoint at `http://112.124.16.227:9200` is reachable from the public internet with no authentication. The cluster carries one or more AI / RAG workloads (dense_vector or knn_vector fields). TLS certificate carries 53 SAN entries under *.gxota.com (multi-tenant tourism SaaS: car rental zuche.ztc, retail byhshop, business-center API bizcenter-api, regional brands Sanjiang/Wuye/QiuYouLuYou).

**State (verified 2026-05-17):** ALIVE / NOT YET EXTORTED

## Infrastructure

| Field | Value |
|---|---|
| IP | `112.124.16.227` |
| ES version | Elasticsearch 8.18.5 |
| Cluster name | `es-docker-cluster (es01)` |
| Country | China |
| Hosting | Alibaba Cloud (Aliyun) |


### Alive on the cluster

| Index | Docs | Size | Notes |
|---|---:|---:|---|
| `Six dense_vector knowledge bases at 1024d` | tourism KB data | tens of MB | 1024d (Cohere embed-v3 or bge-large class) |
| `South Nanning Night (南宁之夜) knowledge bases` | 0-3 docs each, multiple tenants | small | — |
| `pluginhostappid_wx028a2c6941393cd3` | 12 | 67.2 KB | WeChat MiniProgram plugin index |
| `.monitoring-es-7-2026.05.17` | 99,531 | 36.8 MB | live Elasticsearch monitoring (timestamps show today's date — cluster is actively running) |


## Why it matters

The 53 SAN entries on the TLS certificate indicate this is a multi-tenant tourism SaaS. The Elasticsearch endpoint on port 9200 is bound to the public network with no authentication. Multiple regional Guangxi tourism brands (Sanjiang Travel, Wuye, QiuYouLuYou) appear to share this cluster, so the exposure surface is the entire tenant population, not a single brand.

## One-line fix

Bind the Elasticsearch HTTP listener to the loopback interface and require authentication for any non-local client. For a Docker deployment:

```
docker run -p 127.0.0.1:9200:9200 -e xpack.security.enabled=true elasticsearch:8.18.5
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
