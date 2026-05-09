# 25. Elasticsearch / OpenSearch

_Section created: 2026-05-09_

Elasticsearch and OpenSearch are the canonical unstructured-data search engines in the AI stack: they back RAG pipelines, LLM observability stores (MLflow artifact logs, Phoenix traces), AML/KYC compliance databases, and AI-generated content indexes. Elasticsearch 7.x and earlier shipped with **security disabled by default**; 8.x flipped the default to auth-on. The population-scale finding is that a substantial fraction of 7.x deployments remain deployed and unpatched in the 8.x era.

**Survey result (2026-05-03):** 313 masscan hits on port 9200 across 28 cloud /16 ranges (partial, ~40% coverage) → **42 confirmed unauthenticated ES/OpenSearch instances** (38 ES, 4 OpenSearch). ~18 ransomed/wiped (only `read_me` index). ~16 with production data. Notable: AML/KYC compliance SaaS with 79 million KYB records + 6.2 million individual sanctions-list entries at `168.119.90.62:9200` (Hetzner). Vietnamese AI image service API logs with customer credentials. Nepal government procurement notices.

**Auth posture:** T1 for pre-8.x deployments (auth disabled by default). T2 for 8.x (auth on by default, but `xpack.security.enabled: false` is a documented workaround that operators apply to "simplify" deployment).

**CVE watch:**
- `CVE-2021-22145` — Elasticsearch < 7.14.0: node crash via malformed log request (DoS).
- `CVE-2023-31419` — Elasticsearch < 8.9.0: stack overflow in Painless scripting (pre-auth DoS in some configurations).
- `CVE-2024-23445` — Elasticsearch: unauthenticated RCE in JNDI lookup via vulnerable log4j (if unpatched node runs old log4j).
- Ransomware: unauth Elasticsearch has been a primary ransomware target since 2017 ("Meow" bot, "READ_ME_TO_RECOVER_YOUR_DATA" pattern observed in ~18 survey instances).

---

## Core fingerprints

| Shodan Query | Notes |
|---|---|
| `port:9200 "elasticsearch"` | Elasticsearch on default HTTP port |
| `port:9200 http.html:"elasticsearch"` | HTML-scoped |
| `port:9200 "cluster_name"` | Elasticsearch root response field; highest precision |
| `port:9200 "cluster_name" "version"` | Root response JSON structure |
| `port:9200 "tagline"` | Elasticsearch root response always includes `"tagline": "You Know, for Search"` |
| `port:9200 "You Know, for Search"` | Exact tagline; very high precision |
| `port:9200 http.status:200` | Open (no auth redirect) |
| `port:9200 -port:443` | Non-HTTPS direct exposure |
| `elasticsearch port:9200` | Bare-string on default port |
| `"elasticsearch" port:9200 -port:443` | Non-HTTPS; higher misconfiguration probability |
| `product:"Elastic"` | Shodan service fingerprint |
| `product:"Elastic" port:9200` | Service fingerprint + default port |
| `product:"Elastic" -port:443` | Non-HTTPS service fingerprint |
| `http.html:"/_cat/indices"` | Cat indices endpoint path in source |
| `http.html:"/_cluster/health"` | Cluster health endpoint path |
| `http.html:"/_cat/nodes"` | Cat nodes endpoint path |

---

## OpenSearch

| Shodan Query | Notes |
|---|---|
| `port:9200 "opensearch"` | OpenSearch on default port |
| `port:9200 http.html:"opensearch"` | HTML-scoped |
| `port:9200 "OpenSearch"` | Capitalized form |
| `"opensearch" port:9200 "cluster_name"` | OpenSearch with cluster name field |
| `port:9200 "distribution":"opensearch"` | OpenSearch distribution field in root response |
| `hostname:"opensearch"` | rDNS pattern |

---

**Shodan indexing note:** JSON field syntax queries (`"number":"7."`) return 0 — Shodan's basic plan does not parse JSON field paths with escaped quotes. Use substring matching on the version string directly. `port:9200 "7.17"` (1,542) is the working ES 7.17 query.

## Version targeting (auth-off era)

| Shodan Query | Verified hits | Notes |
|---|---|---|
| `port:9200 "7.17"` | **1,542** | ES 7.17.x (latest 7.x, auth-off default); version string in response body |
| `port:9200 "7.10"` | 13 | ES 7.10.x |
| `port:9200 "version" "cluster_name"` | 91 | Generic ES structure; any version with both fields indexed |
| `port:9200 "lucene_version"` | 70 | Lucene version field in ES root response |
| `port:9200 "cluster_uuid"` | 60 | Cluster UUID field in ES root response |
| `port:9200 "number":"7."` | 0 | JSON field syntax not supported; use substring form above |
| `port:9200 "number":"6."` | 0 | Same; ES 6.x indexed via `port:9200 "6.8"` etc. |

---

## Ransomware / wiped instances

| Shodan Query | Notes |
|---|---|
| `port:9200 "read_me"` | "Read me to recover data" ransomware index pattern |
| `port:9200 "READ_ME"` | Uppercase variant |
| `port:9200 "RECOVER"` | Ransom recovery message |
| `port:9200 "Meow"` | "Meow" bot attack remnant (wipes data, renames indices) |
| `port:9200 "read_me_to_recover"` | Full ransomware index name pattern |

---

## AI/ML-specific indices (high-value targeting)

| Shodan Query | Verified hits | Notes |
|---|---|---|
| `port:9200 "mlflow"` | — | MLflow artifact logs in ES |
| `port:9200 "kyb_data"` | 0 | KYB/KYC compliance data — not Shodan-indexed; masscan-only discovery (79M record AML platform found via direct /16 sweep) |
| `port:9200 "kyb_data_index"` | 0 | Index name variant; same — masscan required |
| `port:9200 "sanctions"` | — | Sanctions database indices |
| `port:9200 "aml"` | — | AML-related indices |
| `port:9200 "embeddings"` | — | Vector embedding storage in ES |
| `port:9200 "langchain"` | — | LangChain ES integration indices |
| `port:9200 "openai"` | — | OpenAI-integrated ES deployment |
| `port:9200 "vector"` | — | Vector search indices |
| `port:9200 "semantic"` | — | Semantic search ES deployment |

---

## Cloud-provider scoped

| Shodan Query | Notes |
|---|---|
| `port:9200 "You Know, for Search" org:"hetzner"` | Hetzner (KYC SaaS finding at `168.119.90.62`) |
| `port:9200 "You Know, for Search" org:"digitalocean"` | DigitalOcean |
| `port:9200 "You Know, for Search" org:"amazon"` | AWS (often Elasticsearch Service instances misconfigured) |
| `port:9200 "You Know, for Search" org:"ovh"` | OVH |
| `port:9200 "You Know, for Search" org:"linode"` | Linode |
| `port:9200 "You Know, for Search" org:"scaleway"` | Scaleway |
| `port:9200 "You Know, for Search" country:US` | US-scoped |
| `port:9200 "You Know, for Search" country:DE` | Germany |
| `port:9200 "You Know, for Search" country:CN` | China |
| `port:9200 "You Know, for Search" country:IN` | India |
| `port:9200 "You Know, for Search" country:BR` | Brazil |
| `port:9200 "You Know, for Search" org:"university"` | Academic research clusters |
| `port:9200 "You Know, for Search" org:"hospital"` | Healthcare (EHR/medical data risk) |

---

## Elasticsearch combined with AI stack

| Shodan Query | Notes |
|---|---|
| `port:9200 "cluster_name" org:"amazon"` | AWS ES — high-value, often misconfigured IAM |
| `port:9200 "cluster_name" -port:443 org:"hetzner"` | Hetzner unauth ES |
| `port:9200 "number":"7." org:"digitalocean"` | DigitalOcean ES 7.x (auth-off default tier) |
| `(port:9200 OR port:9243) "elasticsearch"` | ES HTTP + HTTPS alt port |
| `port:9200 "You Know, for Search" -port:443` | All unauth ES, non-HTTPS |
| `port:9200 "You Know, for Search" http.status:200` | HTTP 200 (no auth redirect) — directly accessible |

---

## Kibana (ES companion, sometimes exposes index data via UI)

| Shodan Query | Notes |
|---|---|
| `http.title:"Kibana"` | Kibana UI; broadest |
| `http.title:"Kibana" port:5601` | Default Kibana port |
| `http.title:"Kibana" -port:443` | Non-HTTPS Kibana |
| `"Kibana" port:5601` | Bare-string on default port |
| `http.html:"kibana" port:5601` | HTML-scoped |
| `port:5601 http.status:200` | Live Kibana without auth redirect |
| `http.title:"Kibana" org:"hetzner"` | Hetzner-hosted |
| `http.title:"Kibana" org:"digitalocean"` | DigitalOcean-hosted |
| `http.title:"Kibana" org:"amazon"` | AWS-hosted |
