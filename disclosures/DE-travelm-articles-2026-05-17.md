Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com

2026-05-17

**Re:** Unauthenticated Elasticsearch with AI/RAG workload, TravelM (travelm.de / ai.travelm.de). German multilingual travel AI
**IP / Host:** `84.247.170.209` (cluster `docker-cluster (ba8004666068)`)
**Severity:** HIGH

---

I'm an independent security researcher conducting good-faith AI infrastructure research under the NuClide Research umbrella (CISA disclosures CVE-2025-4364, ICSA-25-140-11). This is an unsolicited coordinated disclosure. No engagement exists with your organization. I have not read, modified, or exfiltrated documents. Only index metadata (schema, counts, sizes) needed to identify the exposure.

---

## Summary

The Elasticsearch endpoint at `http://84.247.170.209:9200` is reachable from the public internet with no authentication. The cluster carries one or more AI / RAG workloads (dense_vector or knn_vector fields). Traefik default certificate (no SNI binding); Shodan previously surfaced ai.travelm.de hostname on this IP.

**State (verified 2026-05-17):** MID-WIPE: extortion marker planted, full multilingual content corpus still alive

## Infrastructure

| Field | Value |
|---|---|
| IP | `84.247.170.209` |
| ES version | Elasticsearch 8.16.0 |
| Cluster name | `docker-cluster (ba8004666068)` |
| Country | Germany |
| Hosting | Contabo GmbH |


### Alive on the cluster

| Index | Docs | Size | Notes |
|---|---:|---:|---|
| `place_de` | 10,825 | 228.1 MB | 1536d — German place catalogue |
| `place_fr` | 266 | 5.5 MB | 1536d — French places |
| `place_es` | 115 | 2.6 MB | 1536d — Spanish places |
| `place_en` | 205 | 4.2 MB | 1536d — English places |
| `article_de` | 72 | 1.4 MB | 1536d — German articles |
| `article_es` | 61 | 1.2 MB | 1536d — Spanish articles |
| `article_en` | 58 | 1.1 MB | 1536d — English articles |
| `article_fr` | 54 | 1 MB | 1536d — French articles |
| `event_fr` | 5 | 121.7 KB | 1536d — French events |


## Extortion marker

An index named `read_me` is present on the cluster. This is the calling card of the **Meow / Indexrm extortion campaign**, an automated wipe-and-ransom operation. The marker indicates the attacker has already enumerated your cluster and either has wiped the data or is about to.

Sample marker content typically contains a ransom note pointing to a Bitcoin wallet and an email channel (`wendy.etabw@gmx.com` or one of two clone actor channels, `scandal@onionmail.org`, `db-recovery@sharebot.net`). We have separately reported all three channels to abuse contacts.

**Do not pay.** Our wallet-blockchain analysis (mempool.space) shows only ~5 victims across thousands of marked hosts have paid; the wallet has received roughly 0.018 BTC against a population of 4,400+ marked instances. Paying does not get your data back. The campaign is wipe-first, ransom-as-afterthought.


## Why it matters

The full multilingual travel-content corpus (place_de 10,825 docs, plus French/Spanish/English/Italian/Russian articles and events) is alive on this cluster. The attacker has planted the 'read_me' marker but has not begun deletion. Take it offline now.

## One-line fix

Bind the Elasticsearch HTTP listener to the loopback interface and require authentication for any non-local client. For a Docker deployment:

```
docker run -p 127.0.0.1:9200:9200 -e xpack.security.enabled=true elasticsearch:8.16.0
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
