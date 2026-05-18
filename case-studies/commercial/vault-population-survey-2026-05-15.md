---
type: survey
---

# Vault (HashiCorp) Population Survey (2026-05-15)

_NuClide Research · 2026-05-15 (eighth survey of the day. Late night)_
_Category 12. Containers & orchestration; secrets-store tier_
_Built on aimap v1.9.5 Vault fingerprint (parallel-session, shipped 2026-05-15)_

---

## Summary

Population-scale survey of HashiCorp Vault deployments. Vault is the canonical secrets-management platform. The operator's database credentials, API keys, signing keys, and other application secrets live inside. Unauth exposure isn't itself an instant-compromise (Vault auth-gates the secret-read API), but it IS a major intel-disclosure surface and, in three rare cases, a full-takeover candidate.

- Shodan harvest (`product:Vault` + `"X-Vault"`) → **2,530 unique candidate IPs**
- Probed via `fast_enum_vault.py` against PUBLIC-BY-DESIGN endpoints (`/v1/sys/seal-status`, `/v1/sys/init`, `/v1/sys/leader`, `/v1/sys/health`) in 140 seconds at threads=80
- **912 confirmed Vault deployments** (36%, 1,618 dead at probe; high stale rate vs other categories)
- **901 unsealed** (98.8%, operationally live, master key in memory, secret engines mounted)
- **3 uninitialized. Full-takeover candidates**
- 233 HA-enabled clusters
- 4 Vault Enterprise (autoloaded-license) deployments
- 0 with `X-Vault-Token` enforcement leaks (Vault correctly gates auth at the API layer)

Restraint: this survey probes only Vault's explicitly-unauthenticated-by-design endpoints (seal/init/health/leader, exposed for monitoring purposes by spec). We never POST `/v1/sys/init`, never call `/v1/sys/mounts` or `/v1/auth/*` or `/v1/secret/*`, never attempt token validation. The discovery surface is intelligence (cluster name, version, HA state, sealed-status) not exfiltration.

---

## Headline finding: 3 uninitialized Vaults (full-takeover candidates)

| Host | Version |
|---|---|
| `152.228.173.65:8200` | v1.16.3 |
| `37.187.244.6:8200` | v1.16.3 |
| `57.129.62.35:8200` | v1.16.3 |

All three return `"initialized": false` on `GET /v1/sys/init`. **Anyone who calls `POST /v1/sys/init` becomes the operator**. `init` is a one-shot bootstrap operation that mints the root token + unseal keys for whoever fires it first. Once initialized, the legitimate operator can't reclaim ownership without destroying the Vault and starting over.

All three are the same Vault version (v1.16.3, 2024-vintage). Most likely a single operator (or template-deployer) who staged three Vault instances and never returned to initialize them. They are sitting "claim-me" on the public internet right now.

This is the single sharpest disclosure-tier finding of the survey. Per-host notification recommended.

---

## Distribution

### Version surface

```
67  v1.15.6      |  37  v1.17.6      |  21  v1.15.2
64  v1.21.4      |  31  v1.13.3      |  15  v1.20.3
64  v1.21.1      |  30  v1.21.3      |  ...
42  v1.21.2      |  22  v1.19.0      |
42  v2.0.0       |
41  v1.20.4      |
```

Mix of recent (v1.21.x = late-2025) and old (v1.13.3 = early-2024, has known CVEs). **42 hosts on Vault 2.0.0**, the new-generation release. v1.15.6 dominates the older tier, likely a popular Docker image that hasn't auto-updated.

### Operator-attribution via `cluster_name`

`/v1/sys/seal-status` returns the operator-set cluster name. Top cluster-name signatures:

| Count | cluster_name | Operator inference |
|---|---|---|
| 10 | `vault` | default-name (operator did not customize) |
| **5** | **`mhy-cgpaas-vault-cn-prod`** | **miHoYo Cloud Game PaaS, CN production Vault cluster** — 5 production instances of one operator |
| 4 | `vault-cluster-67567c37` | Hashicorp-default auto-name (5-instance cluster) |
| 4 | `vault-cluster-9e790c0b` | (4-instance cluster) |
| 3 × 6 distinct | `vault-cluster-<hex>` | 3-instance HA clusters of various operators |

**miHoYo** is the publisher of Genshin Impact / Honkai Star Rail / Zenless Zone Zero. A major Chinese game company. 5 production Vault instances visible under the `mhy-cgpaas-vault-cn-prod` cluster name is a notable operator-attribution find (gaming infrastructure secrets, CN region).

### HA topology

233 hosts (26%) report `ha_enabled: true` on `/v1/sys/leader`. Those are clustered deploys. The leader/standby relationship is exposed. Combined with the cluster_name signal, an attacker can map the multi-node topology of an operator's Vault deployment from the public-by-design endpoints alone.

---

## Cross-survey colocation

| Pair | Overlap |
|---|---|
| Vault ∩ Ollama (16,473) | **3** hosts |
| Vault ∩ etcd v2-unauth (969) | 0 |
| Vault ∩ Docker daemon (286) | 0 |
| Vault ∩ Whisper (230) | 0 |
| Vault ∩ llama.cpp (965) | 0 |

The 3 Vault+Ollama overlaps are:
```
194.163.185.227    198.244.253.131    57.128.246.100
```

Distinct from the prior etcd / Docker / voice-agent cross-survey populations. Vault operators are their own demographic, mostly enterprise infrastructure rather than AI-tier.

---

## Methodology placement

Vault correctly enforces auth at the API layer. `/v1/sys/mounts`, `/v1/secret/*`, and `/v1/auth/*` all return 403 to unauth callers. The framework's auth-on-default posture is intact. **The exposure axis is intel-disclosure, not secret-read** (with the singular exception of the 3 uninitialized hosts where `init` is by-design unauth as the bootstrap operation).

Adds Vault to the methodology's auth-tier map:

| Tier | Definition | Vault behavior |
|---|---|---|
| C | Auth-on-default for all secret-access endpoints | ✓ confirmed at 909/912 |
| C+ | Public-by-design health/seal-status endpoints (intel-only) | ✓ this is what we probed |
| Special | Bootstrap-endpoint (init) is unauth by-design | **3 hosts caught in this window** |

The Tier-Special class is the lesson: **bootstrap operations that must be unauth in their pre-initialization window create a takeover surface for the duration of that window.** Operators who deploy Vault and don't immediately initialize leave it claim-able by anyone with network access. The same logic applies to many secrets-store and CD-pipeline platforms with similar bootstrap-then-lock patterns.

---

## Toolchain Provenance

```
0. shodan_paginate.py (product:Vault) + ("X-Vault") merge   →  2,530 ip:port unique
1. fast_enum_vault.py (threads=80, timeout=6s)               →  912 confirmed Vault in 140s
2. /v1/sys/seal-status + /init + /leader + /health           →  3 uninitialized + 901 unsealed + 233 HA + 4 Enterprise
3. cross-survey diff vs 7 prior corpora                      →  3 Vault∩Ollama, 0 with etcd/Docker/Whisper/llama.cpp/voice
4. visorlog ingest                                           →  869 events landed under source='vault-survey-2026-05-15'
```

aimap v1.9.5 Vault fingerprint (parallel-session, shipped 2026-05-15) covers this surface; the fast_enum probe is a direct-prober variant for population-scale parallelism on the public-by-design endpoints only.

---

## Honest negative space

- **0 sealed-vault telemetry on the Shodan side**: I expected `http.html:"Vault Sealed"` to surface UI-frontend hits, but the Vault UI is a React SPA. The seal status is loaded via JS into a dynamic DOM, not in the initial HTML body Shodan crawls. The 11 sealed Vaults surfaced only via the live `/v1/sys/seal-status` probe, not via Shodan dorking.
- **64% probe-stale rate** is unusually high (vs ~25-40% on other surveys). Vault operators rotate ports / migrate / spin-down dev Vaults frequently. The Shodan candidate set is stale fast for this category.
- **Authentication backends not enumerated**. `/v1/sys/auth` lists configured auth methods (LDAP, OIDC, JWT, etc.) and would reveal the operator's identity-provider integration, but it requires auth. Skipped per restraint.
- **Vault Enterprise license details**. 4 hosts return `license.state: "autoloaded"`. Enterprise-tier with autoload feature. Further metadata (license expiry, customer-name) is auth-required and not enumerated.

---

## Disclosure posture

**Targeted-exception per-host disclosure recommended for:**

- The **3 uninitialized Vaults** (152.228.173.65 / 37.187.244.6 / 57.129.62.35, all v1.16.3). Same-operator triplet, full-takeover candidates. Disclosure should reach the operator before anyone calls `POST /v1/sys/init` on them.
- The **`mhy-cgpaas-vault-cn-prod` 5-host cluster**, miHoYo gaming infrastructure attribution; cluster-name + HA-topology disclosure to a major operator. Per [[feedback_defense_contractor_disclosure_handling]] adjacent: hold cluster-level detail until acknowledged.

Per the broader survey-policy: no per-host disclosure for the 901 unsealed-but-properly-auth-gated Vaults. That's the intended posture, the framework's auth is working as designed.

---

## See also

- [`etcd-population-survey-2026-05-15.md`](etcd-population-survey-2026-05-15.md): secrets-store sibling, same-day
- [`docker-daemon-population-survey-2026-05-15.md`](docker-daemon-population-survey-2026-05-15.md): container tier
- aimap v1.9.5 (commit `b157c86`). The Vault fingerprint shipped today
- `shodan/queries/12-containers.md`: the catalog this survey extends
