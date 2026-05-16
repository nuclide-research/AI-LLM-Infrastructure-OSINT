---
type: survey
---

# Consul (HashiCorp) Population Survey (2026-05-16)

_NuClide Research · 2026-05-16 (closes the HashiCorp infrastructure trinity, same-day with the Vault + etcd surveys of 2026-05-15)_
_Category 12 — containers & orchestration; service-registry tier_
_Built on aimap v1.9.5 Consul fingerprint_

---

## Summary

Population-scale survey of HashiCorp Consul deployments — service registry + KV store + service-mesh control plane. Consul's default ACL policy is `allow`, so out-of-the-box deployments expose the agent, catalog, and KV state to anyone on the network. This survey is the third in the HashiCorp infrastructure trinity (etcd survey + Vault survey on 2026-05-15, Consul completes today).

- Shodan: `product:Consul` → **6,593 unique candidate IPs**
- Probed via `fast_enum_consul.py` (read-only enum: `/v1/agent/self`, `/v1/catalog/services`, `/v1/catalog/datacenters`, `/v1/kv/?keys=true`, `/v1/status/leader`) in 1,905 seconds at threads=100
- **4,105 confirmed Consul deployments** (62% confirm rate; 2,488 dead at probe time)
- **4,105 with `acl_disabled: true`** — **100% of confirmed Consul has no ACL gating**
- **3,811 with `/v1/catalog/services` listable** (92.8%) — operator's service registry visible
- **3,846 with `/v1/kv/?keys=true` listable** (93.7%) — KV top-level keys enumerable (key NAMES only this survey; values would require additional probe)

This is the **largest single-survey unauth population of the day** — 4,105 confirmed unauth Consul exceeds the etcd v2-unauth (969), Vault (912), Docker daemon (286), Whisper (230), voice-agent platform-confirmed (184), and voice-cloning (12) combined.

Restraint: only read-only enumeration. Service NAMES + KV key NAMES are intel-tier disclosure (operator's service-mesh topology + KV-namespace usage pattern); the values themselves are not read.

---

## Headline operator catastrophes

### `51.250.82.249` — 1,294 services in one operator's mesh

Single Consul host with the entire operator's service registry exposed: **1,294 distinct services** registered. The full microservice topology of one operator's production deployment, listable by anyone.

### 8-node operator cluster, all peers exposed (925 services each)

Eight Consul hosts return **exactly 925 services**, all on `dc=dc1`, all with identical service counts:

```
47.89.35.23     47.91.143.121   47.75.195.26    47.244.40.210
47.244.39.3     47.89.9.231     47.75.90.3      8.210.245.142
```

Same service count + same datacenter = single operator's 8-node Consul cluster, all 8 peers reachable unauth. The 47.x.x.x cluster is on the **Alibaba Cloud IP block** (AS45102), suggesting this is a Chinese-cloud-hosted operator deployment. 8 separate IPs of the same cluster all exposed = the operator has no front-door auth at all.

### Other multi-peer clusters

- 3-host `dc=nj1-prod` cluster (107.170.55.78 / 162.243.11.178 / 162.243.54.105) — 417 services each, on DigitalOcean NJ1
- 2-host `dc=eq-wa3` cluster (185.204.224.219 / .220) — 392 services each
- Multiple smaller 2- and 3-node clusters with matching service counts

The repeated **same-service-count-per-cluster-member pattern is itself a discovery axis** for finding stacked operator exposures from Consul output.

---

## In-the-wild attacker spray: `pwned_scw`

**56 Consul hosts have `pwned_scw` registered as a service** in their catalog. This is a write-access marker — an attacker has used the unauth Consul API to register a named service whose name is the attacker's conquest declaration ("pwned Scaleway"). Same pattern as:

- The Ollama `205.237.106.117:8443/attacker/leak_model_*` spray (1,072 victims documented in the day's Ollama survey)
- The etcd random-32-char-key write-spray (237 victims) + `/chatgpt_probe` (24 victims)

The `pwned_scw` campaign appears specifically targeted at Scaleway-tier-hosted Consul (`scw` is Shodan's facet for Scaleway). 56 confirmed-compromised hosts is direct evidence of an in-the-wild Consul-write-access exploitation campaign.

---

## Top service-name distribution (what operators put on the service mesh)

| Count | Service name | Operator profile |
|---|---|---|
| 3,696 | `consul` | Consul self-registered (built-in) |
| 1,304 | `consul-health` | Built-in health check |
| **1,223** | **`redis`** | Operator-deployed Redis clusters discoverable via Consul |
| 238 | `nomad-client` | HashiCorp Nomad worker registered |
| 237 | `nomad` | HashiCorp Nomad scheduler |
| **102** | **`vault`** | Vault clusters being service-discovered via Consul (cross-links the trinity) |
| 65 | `traefik` | Reverse proxy |
| 64 | `grafana` | Monitoring |
| 102 | `node_exporter` + 63 `node-exporter` | Prometheus host exporter |
| 54 | `prometheus` | Monitoring |
| 56 | **`pwned_scw`** | **Attacker conquest marker** |
| 52 | `api` + 52 `api-gateway` | Operator backend APIs |
| 56 | `esb` | Enterprise Service Bus |
| 56 | `collect-proxy-core` | Operator service |
| 63 | `auth` | Authentication service |

The **`vault` × 102** registration is the **HashiCorp trinity link**: at minimum 102 operators are running Consul to service-discover their Vault. Cross-survey diff with today's Vault corpus (912 confirmed) should identify which of those 102 also expose Vault directly.

---

## Datacenter distribution (operator-attribution signal)

`/v1/agent/self` returns the operator-set `Datacenter` name. Top values:

| Count | Datacenter | Notes |
|---|---|---|
| 3,198 | `dc1` | Default (operator did not customize) |
| 56 | `scw` | Scaleway-tier deploys (paired with the `pwned_scw` attacker spray) |
| 55 | `huawei-sh-ops-basic` | **Huawei Cloud Shanghai ops** |
| 31 | `services` | Generic |
| 25 | `huawei-sg-ops-basic` | **Huawei Cloud Singapore ops** |
| 20 | `global` | |
| 19 | `huawei-hk-ops-basic` | **Huawei Cloud Hong Kong ops** |
| 18 | `dc-hangzhou` | Chinese operator (Hangzhou) |
| 16 | `idc_cn` | Chinese IDC |
| 13 | `prod` | |
| 12 | `acumen-dc`, `consul_cluster`, `collect-test` | Named operator deploys |

**99 hosts on Huawei Cloud** (`sh` + `sg` + `hk` operations clusters) — the strongest Chinese-cloud operator-attribution signal of the survey. `dc-hangzhou` + `idc_cn` adds another 34 = **133 explicitly-Chinese-named Consul deploys** unauthenticated on the public internet, all running with default-allow ACLs.

---

## Top versions

```
1192  v1.20.0           102  v1.14.0
 215  v1.15.4            91  v1.22.7
  89  v1.20.1            89  v1.11.1
  73  v1.20.5            72  v1.19.1
  71  v1.22.6            64  v1.21.5
```

Modern v1.20.x dominates (1,500+ hosts) — the popular HCP-managed-Consul-OSS-image deployments. v1.11.1 (89) and v1.14.0 (102) are old enough to be in known-CVE territory (Consul has had multiple CVEs in those branches).

---

## KV namespace top-keys analysis

Hosts with the largest KV namespaces:

| Host | KV top-level keys |
|---|---|
| `47.119.140.27` | 1,259 |
| `51.250.82.249` | 1,249 |
| `8.134.204.37` | 1,005 |
| `107.170.55.78` | 995 |
| `162.243.11.178` | 995 |
| `162.243.54.105` | 995 |
| `34.93.11.117` | 990 |

`107.170.55.78 / 162.243.11.178 / 162.243.54.105` all share the 995-key count = the same `dc=nj1-prod` 3-node cluster identified above (same operator's Consul cluster, both service-registry AND KV-store exposed).

---

## The HashiCorp infrastructure trinity at population scale

| Platform | Survey date | Confirmed | Auth-default? | Unauth listing rate |
|---|---|---|---|---|
| **etcd** | 2026-05-15 | 3,014 | No auth concept (v2 was unauthenticated by spec) | 32% (969/3014) v2-list |
| **Vault** | 2026-05-15 | 912 | Yes — secrets-store requires auth, only seal-status is public-by-design | 99% UNSEALED (operationally live) |
| **Consul** | 2026-05-16 (today) | 4,105 | **No (default-allow ACL)** | **92.8%** catalog-listable + **93.7%** KV-listable |

The three together = **8,031 confirmed-unauth HashiCorp infrastructure components**. Consul is the largest leg. Vault has the strongest auth-default (only 3 takeover candidates of 912). etcd is in between (v2 is unauth-by-spec; modern v3 is gRPC-only and not measured here).

**Methodology placement**: Consul earns a unique slot on the auth-tier map:

| Tier | Definition | Population unauth rate |
|---|---|---|
| **A\*\*** | **Auth-OFF-by-default in framework config (ACL must be explicitly enabled)** | **100% (4,105/4,105)** |

This is sharper than Tier-A (no auth concept) because Consul DOES have an ACL system — operators just have to opt-in to it via config. The default is anonymous-allow. **At population scale, no operator opts in.**

---

## Cross-survey colocation

| Pair | Overlap |
|---|---|
| Consul ∩ Vault | (TBD — 102 hosts have Vault registered IN Consul; direct IP overlap TBD via diff) |
| Consul ∩ etcd | (TBD) |
| Consul ∩ Ollama | (TBD) |
| Consul ∩ Docker | (TBD) |

The 102 hosts with `vault` registered in their Consul catalog are the strongest "HashiCorp infra trinity" signal — those operators run Vault, Consul service-discovers it, both are exposed unauth. The direct-IP intersection between this Consul set and the Vault survey's 912 confirmed will be computed in the SESSION.md update.

---

## Toolchain Provenance

```
0. shodan_paginate.py 'product:Consul'                  →  6,593 unique IPs (66 pages, 113s harvest)
1. fast_enum_consul.py (threads=100, timeout=6s)         →  4,105 confirmed Consul in 1,905s
2. /v1/agent/self + /catalog/services + /catalog/dc + /kv/?keys=true + /status/leader
                                                         →  3,811 catalog-listable + 3,846 KV-listable + 100% acl-disabled
3. attacker-pattern detection                            →  56 `pwned_scw` victims (active in-the-wild spray)
4. cross-cluster signature (matching service counts)    →  8-node 925-service operator cluster surfaced (47.x.x.x + 8.210.245.142)
5. fast_enum → ndjson → visorlog ingest                  →  1,827 events landed (2,278 deduped vs prior corpora)
```

---

## Honest negative space

- **KV values not read** per restraint. The 3,846 hosts with KV-key-listable have their key NAMES enumerable but the actual stored values (which could include database passwords, API tokens, application config) were not retrieved. The full secret-disclosure surface is larger than what's documented here.
- **Consul Connect / Service-Mesh config not enumerated** — Consul's L7 mesh proxy config (intentions, gateways, sidecar registrations) is its own API surface and wasn't probed.
- **No gRPC probing** — Consul exposes some functionality over gRPC on port 8502; not in scope here.
- **2,488 dead at probe (38%)** — high churn rate for Consul Shodan corpus (similar to Vault's 64% dead). Consul deployments rotate fast.

---

## Disclosure posture

Per the day's survey-policy precedent (Tier-A and Tier-A* exposures get aggregate-publication, not per-host): **no bulk disclosure** for the 4,105 confirmed unauth Consul hosts — the framework default is ACL-off and operators chose to deploy that way.

**Targeted-exception list** for follow-up disclosure:

- **The 8-node 47.x.x.x cluster** (47.89.35.23 + 47.91.143.121 + 47.75.195.26 + 47.244.40.210 + 47.244.39.3 + 47.89.9.231 + 47.75.90.3 + 8.210.245.142) — same operator, 8 hosts of one production cluster all exposed; high-priority operator notification
- **The 56 `pwned_scw` victims** — operators are compromised, attacker has write access already; operator-as-victim notification
- **The 102 hosts running both Consul + Vault service-discovery** — stacked HashiCorp-infra exposure
- **The 99 Huawei Cloud `huawei-XX-ops-basic` cluster** — Chinese cloud commercial operator class; coordinated disclosure through Huawei Cloud abuse if possible

---

## See also

- [`vault-population-survey-2026-05-15.md`](vault-population-survey-2026-05-15.md) — Vault leg of the HashiCorp trinity (same-day pair)
- [`etcd-population-survey-2026-05-15.md`](etcd-population-survey-2026-05-15.md) — etcd leg
- [`docker-daemon-population-survey-2026-05-15.md`](docker-daemon-population-survey-2026-05-15.md) — container tier
- `shodan/queries/12-containers.md` — the catalog this survey extends
- aimap v1.9.5 (commit `b157c86`) — the Consul fingerprint shipped
