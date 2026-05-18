---
type: survey
---

# Unauth Docker Daemon Population Survey (2026-05-15)

_NuClide Research · 2026-05-15 (late evening, fifth survey of the day)_
_Category 12. Containers & orchestration; Docker daemon leg_

---

## Summary

Survey of the Shodan-indexed Docker daemon population on port 2375. The canonical unauth port for the Docker HTTP API. Port 2376 is the TLS-auth variant; **port 2375 is unauth by framework spec**, and operators who expose it on the public internet are running with root-equivalent RCE-on-the-host as a default.

- Shodan: `port:2375 "Docker"` → **602 unique IPs**
- Probed via `fast_enum_docker.py` (read-only metadata only: `/version`, `/info`, `/containers/json?all=1`, `/images/json`) in 43 seconds at threads=80
- **286 confirmed unauth Docker daemons** (47.5%; remainder are 297 dead and 19 returning non-200 on `/version`)
- **0 auth-required**: every responsive port-2375 host is unauth (confirms the framework spec)
- **379 containers + 1,586 images** visible across the corpus

Each unauth Docker daemon is **root RCE on the host** by definition: `POST /containers/create` with `Binds:["/:/host"]` + `Cmd:["chroot","/host","sh"]` gives shell on the host. Restraint: this survey does only read-only enumeration. Never `/containers/create`, `/images/pull`, `/exec`, or destructive operations.

---

## Headline sub-findings

### 21 unauth Docker hosts also run unauth Ollama on the same VPS

Cross-survey diff against the day's earlier Ollama survey (16,473 confirmed unauth Ollama) yielded **21 IPs running BOTH** unauth Docker daemon AND unauth Ollama. This is the **stacked operator catastrophe** class:

- Docker daemon root RCE → can dump Ollama state, modify loaded models, exfil any operator data on disk, deploy persistence, escalate to the surrounding cloud-account
- Ollama by itself → compute-theft + model-theft + `:cloud` paid-quota drain
- Together → full host takeover + AI workload tampering

These 21 hosts are higher-priority disclosure targets than either survey's individual findings, because the combined surface gives an adversary both compute access AND host control.

### Cryptojacking: confirmed compromise

**`122.152.235.121`** has 10 instances of the `redminer:latest` cryptocurrency-mining container loaded (all named `/inspect-miner-*`, all in `state=created`). This is the unauth-Docker-daemon → cryptojacker pipeline at confirmed-active scale. `redminer` is a Monero/XMRig-derivative miner; the operator has been compromised and an attacker has staged the miner fleet for execution.

Parallel to the 1,072-victim Ollama `205.237.106.117:8443/attacker/leak_model_*` campaign on the Ollama survey: same class of unauth-AI-tier → attacker-staged exploitation, but on the Docker daemon tier instead of the model-pull tier.

### Suspicious / atypical containers

- `5.78.111.219` runs `ttl.sh/gw-mesher-director:1h` + `11notes/socket-proxy:2.1.3`. Short-TTL ephemeral image + socket-proxy combination is a known pattern in attacker C2 / proxy-pivot infrastructure. Worth flagging for follow-up correlation.

### Container-image distribution

| Image | Count |
|---|---|
| `alpine` (various) | 84 |
| `ubuntu:latest` | 35 |
| `nginx:latest` | 16 |
| `grafana/grafana:latest` | 13 |
| `node:18-alpine` | 13 |
| `python:3.10-slim` | 10 |
| `redis:7-alpine` | 10 |
| **`redminer:latest`** | **10 (single host)** |
| `mcr.microsoft.com/windows/nanoserver:ltsc2022` | 10 |
| `postgres:14`, `mongo:5`, `mysql:8.0`, `prom/prometheus`, `golang:1.19` | 5-9 each |
| **AI-class containers (n8n)** | **2 hosts only** |

The Docker daemon population is mostly **generic infrastructure** (alpine/ubuntu/nginx/python/redis/postgres), not specifically AI deployment. The cross-survey overlap with Ollama is at the host-level, not the container-image-level. Operators expose Docker daemon AND happen to run Ollama on the same VPS, rather than running Ollama via Docker.

---

## Geographic + operator distribution

**Top 10 countries** (of the 286 unauth hosts):

```
US 79 · DE 25 · SG 18 · GB 17 · IN 14 · CN 11 · AU 10 · NL 9 · JP 8 · ID 7
```

**Top 10 orgs:**

```
Microsoft Corporation    26   (Azure)
Google LLC               22   (GCP)
HostPapa                 20   (budget shared hosting)
Hetzner Online GmbH      12
Vultr Holdings           10
The Constant Company     10   (Vultr's parent)
DigitalOcean             10
IONOS SE                 9
STARK INDUSTRIES SOLUTIONS LTD   9
Linode                   7
```

**`STARK INDUSTRIES SOLUTIONS LTD`** at 9 hosts is notable. Stark Industries Solutions is widely-reported as a bulletproof hosting provider associated with cybercrime infrastructure. 9 unauth Docker daemons on a known-bad-host provider is worth flagging for the disclosure decision.

---

## Toolchain Provenance

```
0. shodan_paginate.py 'port:2375 "Docker"'       →  602 unique IPs (32s harvest)
1. fast_enum_docker.py (threads=80, timeout=6s)   →  286 confirmed unauth in 43s
2. /info /containers/json /images/json enum      →  379 containers + 1586 images visible
3. cross-survey diff vs Ollama corpus            →  21 stacked operator catastrophes
```

---

## Honest negative space

- **Docker Registry** (`product:"Docker Registry"` → 15,319 hits) and **etcd** (`port:2379 "etcd"` → 3,768 hits) deferred to follow-up surveys. Both deserve their own restraint planning (registry image-pulls would burn operator bandwidth + access potentially-sensitive operator images; etcd v3 is gRPC-primary, needs probe redesign beyond HTTP `/v2/keys`).
- **`product:Docker` returns 15,636** for the broader Docker daemon universe, not just port 2375. The 602 here is the unauth-port-tagged subset. There are probably hundreds more unauth daemons on non-default ports that this survey didn't reach.
- **No actual exploitation performed**. The 286 hosts are confirmed unauth via `/info` returning JSON, but no `/containers/create` calls were made (which would have demonstrated impact via root-shell on the host). Restraint per CLAUDE.md.

---

## Disclosure posture

Per the broader survey-policy precedent (Ollama / llama.cpp / voice-cloning): **no per-host disclosure for the bulk of unauth Docker daemons**, the framework's `2375 = unauth` design is well-documented and operators chose to expose; aggregate publication is the public record.

**Targeted exception list** for follow-up disclosure:
- The 21 stacked operator catastrophes (unauth Docker + unauth Ollama on same VPS). Root-RCE + AI-data combination is high-severity
- The cryptojacked host `122.152.235.121`. Operator-as-victim notification
- The STARK INDUSTRIES SOLUTIONS LTD 9-host cluster. Likely abuse-network adjacent
- Gov-TLD / academic-TLD hosts if any (none surfaced in this run's geo-distribution top-10, but full IP set needs to be checked against `.gov` / `.edu` reverse-DNS)

---

## See also

- [`ollama-population-survey-2026-05-15.md`](ollama-population-survey-2026-05-15.md): the day's Ollama survey; 21 IPs overlap with this Docker survey
- [`llamacpp-population-survey-2026-05-15.md`](llamacpp-population-survey-2026-05-15.md)
- [`voice-agents-population-survey-2026-05-15.md`](voice-agents-population-survey-2026-05-15.md): closes Survey 17 batch 3
- `shodan/queries/12-containers.md`: the catalog this survey extends; Docker Registry + etcd legs still pending
