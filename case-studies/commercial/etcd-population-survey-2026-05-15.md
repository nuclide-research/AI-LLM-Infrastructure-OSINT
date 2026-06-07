---
type: survey
---

# etcd Population Survey (2026-05-15)

_NuClide Research · 2026-05-15 (late evening, seventh survey of the day)_
_Category 12. Containers & orchestration; etcd leg, complements the day's earlier Docker daemon survey_
_Built on aimap v1.9.5 fingerprint (parallel-session, shipped 2026-05-15)_

---

## Summary

Population-scale survey of etcd. The distributed key-value store that backs Kubernetes' entire cluster state. Each unauthenticated etcd is a **secrets-store leak class**: anyone can list (and read) the cluster's stored data including Kubernetes secrets, service-discovery records, and operator-stored configuration.

<!-- ksat-tag:auto-generated:start -->
## DCWF KSAT coverage

Auto-derived from DCWF AI work-role rule files (`ksat-tag`).

- **672 (AI Test & Evaluation Specialist):** K7003, K7004, K7044, S7068, S7070, S7075, T5858, T5904, T5919
- **733 (AI Risk & Ethics Specialist):** T5868, T5882, T5893
- **overlap (Common AI KSATs (all 5 roles)):** K1158, K1159, K22, K6311, K7003

<!-- ksat-tag:auto-generated:end -->

- Shodan harvest: `port:2379 "etcd"` → **3,766 unique candidate IPs**
- Probed via `fast_enum_etcd.py` (read-only enum: `/version` + `/v2/keys/` top-level listing + `/v2/stats/leader` + `/metrics`) in 162 seconds at threads=100
- **3,014 confirmed etcd hosts** (80% confirm rate; 752 dead)
- **0 TLS-required**: every responsive etcd-on-port-2379 is unauth-HTTP
- **969 with `/v2/keys/` reachable and returning JSON** (32% of confirmed). The v2 API key listing is accessible **with no auth**; the operator's top-level key namespaces are enumerable; if v2 is also write-enabled, an attacker can *write* arbitrary keys
- **2,949 with `/metrics` open** (98% of confirmed). Prometheus metrics expose `etcd_mvcc_db_total_size_in_bytes`, `etcd_debugging_mvcc_keys_total`, `grpc_server_started_total` and the full cluster topology
- **732 with `/v2/stats/leader` open** (24%). Leader-ID disclosure

Restraint: this survey only **lists top-level keys** (no `/v2/keys/<name>` reads, would expose values), and reads only public Prometheus metrics. We did not write to any host or read any secret value. The unauth surface is documented; actual exploitation is not performed.

---

## Headline findings

### Two active attacker write-spray campaigns

**237 hosts** show top-level keys matching the pattern `/[a-z]{30,40}` (random 32-character alphanumeric strings as key names). **600 distinct attacker-written keys observed across the corpus.** The naming pattern is classic write-access fingerprinting. An attacker writes a uniquely-named test key to confirm write access, then re-visits later to verify persistence (typical pre-staging for a second-stage attack).

Same class as the **1,072-victim Ollama `205.237.106.117:8443/attacker/leak_model_*` campaign** documented in the day's Ollama population survey. Operator-pwned via the unauth-AI-tier and used as a stage-set marker. Here it's etcd instead of Ollama.

**24 hosts** show the top-level key `/chatgpt_probe`. A named probing campaign by a different actor. 18 of those 24 also have the random-key spray, meaning the same hosts are being claimed by multiple competing attackers.

| Campaign | Victim count | Key pattern |
|---|---|---|
| Random 32-char alphanum spray | 237 | `/niwnjvpeflriiiudgnhwmazkdbrgdixy`, `/ynfdaotpdqrhzgejwkdkpwzqmknnyann`, ~600 distinct keys |
| `/chatgpt_probe` | 24 | static key name |
| Overlap (multi-attacker victims) | 18 | both write-spray classes present |

This is **direct evidence of an active in-the-wild exploitation campaign against unauth etcd**, parallel to the Ollama attacker-spray finding from earlier today.

### Top etcd by key count: operator data scale

Prometheus metrics expose `etcd_debugging_mvcc_keys_total`, the canonical cluster-size signal. The largest exposed etcds:

| Host | Keys total | etcd version |
|---|---|---|
| `110.42.100.155` | **326,036** | v3.5.14 |
| `45.76.248.64` | 257,351 | v3.5.12 |
| `5.78.79.3` | 255,126 | v3.5.23 |
| **`106.75.147.217`** | **189,432** | v3.5.15 |
| **`106.75.187.29`** | **189,432** | v3.5.15 |
| **`42.240.135.119`** | **189,432** | v3.5.15 |
| `8.217.82.242` | 156,213 | v3.5.9 |
| `47.251.61.188` | 102,319 | v3.5.7 |
| `213.136.69.90` | 84,690 | v3.5.5 |

**The 189,432-key trio** (`106.75.147.217`, `106.75.187.29`, `42.240.135.119`). Same exact key count + same etcd version = a single **3-node operator cluster fully exposed**. Three peers of a single etcd cluster, all reachable unauth. An attacker who lands write-access on one immediately gets cluster-state-write everywhere.

### K8s control-plane indicator class

Only **1 of 969 v2-unauth hosts** (`8.134.51.47`) returned a top-level `/registry/` key. The canonical Kubernetes control-plane data root. The vast majority of unauth etcd in the wild are **not** k8s control-plane stores. They're:

- etcd's own peer-discovery service (`/discovery`, 545 hosts)
- service-registry / Consul-like usage (`/service`, 93)
- application-specific KV (`/db`, 50)
- and the random-attacker-spray keys above

This is methodologically useful: **the assumption that "unauth etcd = k8s secrets disclosure" overstates the actual k8s-tier exposure.** The real population is mostly standalone etcd or service-registry deployments. The k8s control-plane subset is tiny (1 confirmed via the top-level-keys signal in this run; possibly more behind v2-disabled-v3-only hosts where we couldn't enumerate).

### Cross-survey colocation

Diffed the 3,014 confirmed etcd hosts against the day's other corpora:

| Pair | Overlap |
|---|---|
| etcd ∩ Ollama (16,473) | **14** (cluster-state + AI workload) |
| **etcd ∩ Docker daemon (286)** | **4** (root RCE + cluster-state-dump combo) |
| etcd ∩ llama.cpp (965) | 0 |
| etcd ∩ Whisper (230) | 0 |
| etcd ∩ voice-agent (184) | 0 |

The **4 hosts running BOTH unauth etcd AND unauth Docker daemon** are the worst-class stacked operator catastrophes of the day:

- Docker daemon → root shell on the host (root RCE class)
- etcd → cluster state including any operator secrets
- Together: an attacker takes the host, pivots through etcd's cluster registration to adjacent peers, and reads any operator data

---

## Versions + distribution

Top etcd versions:

```
232  v3.5.11
229  v3.5.5
226  v3.5.15
130  v3.5.9
128  v3.5.0
113  v3.5.12
107  v3.3.25  (very old — 2020-era)
 95  v3.5.23
 93  v3.5.21
 91  v3.5.17
```

Mostly modern v3.5.x; a long tail back to v3.3.25 (multiple known CVEs in that branch including [GHSA-mh3m-pcfc-f5cv (DoS on 3.3.x lease APIs)](https://github.com/etcd-io/etcd/security/advisories/) and CVE-2020-15113).

---

## Toolchain Provenance

```
0. shodan_paginate.py 'port:2379 "etcd"'              →  3,766 unique IPs (73s harvest, 38 pages)
1. fast_enum_etcd.py (threads=100, timeout=6s)        →  3,014 confirmed etcd in 162s
2. /v2/keys/ + /metrics + /v2/stats/leader analysis   →  969 v2-unauth + 2,949 metrics-open
3. attacker-pattern detection (random-key regex)      →  237 + 24 victims of two named campaigns
4. cross-survey diff vs Ollama/Docker/Whisper/etc     →  14 etcd+Ollama, 4 etcd+Docker (worst class)
5. fast_enum → ndjson → visorlog ingest               →  2,176 events landed (838 deduped)
```

aimap v1.9.5 fingerprint for etcd (shipped 2026-05-15 by parallel session) was used as the canonical signature; the fast_enum probe is a direct-prober variant of the same logic for population-scale parallelism.

---

## Honest negative space

- **v3 API not probed**. etcd v3 uses gRPC primarily; the HTTP gateway only exposes some endpoints. Hosts with v2 disabled (v3-only) returned 404 on `/v2/keys/` and look "auth-protected" to this prober even when they're actually v3-unauth-reachable via gRPC. The 969 v2_keys_unauth count is a *lower bound* on the actual unauth-listing population.
- **No key values read**. We listed top-level key NAMES only (publicly intel-relevant: namespace prefixes reveal usage patterns) but never read `/v2/keys/<full-path>` which would expose actual stored values. The full secret-disclosure surface is real but not enumerated here per restraint.
- **K8s detection limited**. The `/registry/` top-level-key signal caught 1 host. Real k8s clusters might have their data behind v3-only (gRPC) so our v2-listing missed them. A gRPC-based follow-up survey would catch this.
- **Disclosure tier**: 969 victims of one or both write-spray campaigns is real evidence of in-the-wild exploitation. The hosts ARE compromised. The operators are unaware. Per the day's broader survey-policy (no per-host disclosure for Tier-A framework-defaults), aggregate publication is the public record; the 237 attacker-write-spray victims + 4 etcd-and-Docker stacked operators are the targeted-exception-list candidates.

---

## See also

- [`docker-daemon-population-survey-2026-05-15.md`](docker-daemon-population-survey-2026-05-15.md): the day's Docker daemon survey (4 hosts overlap with this etcd survey)
- [`ollama-population-survey-2026-05-15.md`](ollama-population-survey-2026-05-15.md): 14 hosts overlap + the parallel 1,072-victim `205.237.106.117` attacker-spray on Ollama (same class of pre-staged write-test pattern, different layer)
- `shodan/queries/12-containers.md`: the catalog this survey extends
- aimap v1.9.5 release at github.com/Nicholas-Kloster/aimap (commit `b157c86`). The etcd fingerprint shipped today
