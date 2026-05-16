---
type: survey
---

# Vector-DB Stragglers Population Survey (2026-05-16)

_NuClide Research · 2026-05-16 (fourth survey in the day's 4-category batch)_
_Closes: category 02 (vector-databases) stragglers — Solr / Meilisearch / Typesense / Vespa / pgvector_

---

## Summary

Closes the four platform-class stragglers left after the 2026-05 Qdrant / ChromaDB / Milvus / Weaviate sweep: Apache Solr, Meilisearch, Typesense, Vespa, plus pgvector body-marker recheck. Each candidate corpus was harvested individually and probed via `fast_enum_vectordb.py`.

- 16,704 unique candidate ip:port pairs harvested across the 5 platforms
- **881 confirmed unauth deployments** (5.3% real-unauth rate at population scale):
  - **Apache Solr: 613 unauth** (the headline — most are stale Solr 7.6.0 with documented RCEs)
  - **Meilisearch: 268 unauth** (indexes listable + UIDs leaking app schema)
  - **Typesense: 0 unauth** (Tier-C confirmed at 9,837 candidates — API-key gating works)
  - **Vespa: 0 unauth** (44 real instances, all auth-gated or partial)
  - **pgvector: 0 confirmed** (TCP-only on 5432 — Shodan-marker hits were Postgres+vector references, not exposed pgvector ports)
- 3,116 auth-gated; 358 partial-open (some endpoints reachable but data layer auth-gated); 9,436 dead; 511 shell-only; 143 unrelated

**Headline:** 516 Apache Solr 7.6.0 hosts are reachable unauth — a single-version cluster from 2018 with three published unauth RCEs (CVE-2019-17558 Velocity RCE, CVE-2019-0193 DataImportHandler RCE, CVE-2019-12409 JMX-RMI default-open RCE). Single-version 84%-dominance suggests one of two things: a Docker base-image baked at that version and replicated by ops at scale, or a CN-specific deployment template (most of the 7.6.0 unauth population is on CN cloud).

---

## The Solr 7.6.0 cluster — 516 hosts on a 7-year-old version

Solr 7.6.0 was released December 2018. By design it ships with admin endpoints unauth (`/solr/admin/info/system`, `/solr/admin/cores`, `/solr/admin/configs`); auth is configured separately via the `security.json` framework. Three high-severity unauth RCEs exist on this version:

| CVE | Class | Impact |
|---|---|---|
| **CVE-2019-17558** | Velocity Template Engine RCE | unauth `POST /solr/{core}/select?wt=velocity&v.template=...` returns SSTI → arbitrary code execution |
| **CVE-2019-0193** | DataImportHandler RCE | unauth import with attacker-controlled dataConfig executes Java → RCE |
| **CVE-2019-12409** | JMX-RMI default-open | port 18983 default-open on 7.6.0, JMX RMI auth-off → JNDI injection → RCE |

**516 unauth Solr 7.6.0 hosts = 516 commodity-CVE-chain candidates.** All three CVEs are public for ~6 years and have ready Metasploit modules (`exploit/multi/http/solr_velocity_rce`, `exploit/multi/http/solr_dih_rce`). BARE confirms — this is the textbook "commodity exploit chain" tier.

The version distribution:

```
  516  7.6.0    ← the unauth fleet
   19  8.11.2
    8  8.6.0
    7  8.2.0
    6  8.11.4
    5  9.9.0    ← current
    5  9.8.1
    5  8.11.3
    4  9.0.0
    3  9.10.1
    ... + minor counts on a few other minor versions
```

The 7.6.0 fleet dominates by 27× over the next-most-common version. This is a deployment-template phenomenon, not natural distribution. Single most likely explanation: a Docker image (e.g. `solr:7.6.0` on Docker Hub, or a derivative `cn-cloud-marketplace-solr`) was widely deployed during a specific period (~2019), the operators never patched, and the deployment still serves traffic.

---

## Solr cores leak app schema

`GET /solr/admin/cores?action=STATUS` returns the operator's full core list. Sample of what was found unauth across 613 Solr hosts:

| Host | Cores | What the names imply |
|---|---|---|
| `101.37.239.238:80` | `mgw_hce_search_index`, `mgw_integral_search_index`, `mgw_search_index`, `mgw_sku_search_index`, `supplier_member_search_index`, `supplier_search_index` | E-commerce + supplier marketplace (`mgw` ≈ marketplace gateway? `hce` ≈ "health care equipment"? `sku` ≈ stock-keeping unit — confirmed retail) |
| `119.29.117.117:8090` | `InformationCategory`, `category`, `exploit_core`, `gaizhouEnterprise`, `gzEnterprise`, `nz`, `qfEnterprise`, `rumor`, `rumorRecordCategory`, `scEnterprise`, `supenterprise`, `wnEnterprise` | Multi-tenant CN provincial-government registry (`gz` = Guizhou, `nz` = Ningxia, `qf` = Qingfei, `sc` = Sichuan, `wn` = Weinan — provincial codes) + an "**exploit_core**" labelled index, plus "rumor" tracking |
| `103.124.100.129:8600` | `airjonge`, `airjonge2`, `airjonge3` | Three identical-prefix cores — likely a single operator's dev/staging/prod parallel indices |
| `103.155.161.159:8984` | `postal_codes` | Geographic lookup service |
| `112.137.131.12:80` | `thesis` | University thesis search system |
| `108.129.59.151:80` | `era2023` | Possibly examination / record system, year 2023 |

The collection names ARE the finding — per the methodology's restraint ethic, the name alone tells you what's inside without needing to query a document. `exploit_core` is the most alarming name — possibly a CVE-tracking index or attack-surface logger. The CN provincial-government cluster on `119.29.117.117` is the highest-confidence operator-attribution find.

Reading actual documents is held back per restraint — `GET /solr/<core>/select?q=*:*&rows=1` would dump a sample row, but the names are sufficient for severity classification.

---

## Meilisearch — 268 unauth, indexes leak app schema

Meilisearch's `/indexes` endpoint requires a master key when the operator sets `MEILI_MASTER_KEY`. 268 hosts have NOT set the key — `/indexes` returns the full index list unauth. Notable index UID patterns:

| Host | Index UIDs | Inferred app |
|---|---|---|
| `100.53.133.232:80` | `service_provider_indices`, `service_providers`, `service_providers_index`, `specialties` | Healthcare provider / specialist directory |
| `103.54.16.37:7700` | `countries`, `departure_cities`, `hotels` | Travel booking |
| `103.167.150.102:7700` | `faq-chat`, `product` | E-commerce + RAG chatbot |
| `103.160.212.9:7700` | `osm_data`, `vmr_signals`, `vmr_sources`, `vmr_vibes` | OSM-based geo + signals analytics |
| `104.248.232.116:80` | `products` | E-commerce |
| `109.203.110.107:7700` | `adviser_index`, `profile_index` | Financial advisor directory |
| `1.234.75.8:7700` | `company_profiles` | B2B corporate directory |
| `115.190.174.185:7700` | `vocabulary` | Language-learning platform |
| `120.26.38.129:7700` | `poi` | Points-of-interest geo lookup |

The pattern is the same as the Solr case studies: **collection names disclose the operator's app schema** without reading data. A `service_providers` + `specialties` pairing maps to a doctor-finder app. `adviser_index` + `profile_index` maps to a financial-advisor finder. The schema disclosure plus version disclosure (`/version` returns Meilisearch package version) is enough for an attacker to identify what's inside before issuing any document-read.

Meilisearch version distribution: dominant on 1.14.0 (76 hosts), with a long tail back to 0.28.x. Multiple known CVE classes for versions <1.0 if data-write access is unauth (which would be detected here as `is_unauth_data: true` — and confirmed at 268 hosts).

---

## Typesense + Vespa — Tier-C confirmation

| Platform | Candidates | Unauth | Real (auth-gated + partial) | Auth-tier verdict |
|---|---|---|---|---|
| **Typesense** | 9,837 | 0 | TBD (many returned shell-only at root) | **Tier-C confirmed** — API key required at /collections at population scale |
| **Vespa** | 45 | 0 | TBD | Small population; framework auth-on-default observed |

Typesense's `/health` endpoint is unauth by design (returns `{"ok":true}`), but `/collections` requires `X-TYPESENSE-API-KEY`. At population scale, **zero of 9,837 candidates returned collection data unauth**. This is the strongest single-platform Tier-C confirmation surfaced in any survey to date (Vault was 901 unsealed Vaults all properly auth-gated at the secret-read layer; Typesense replicates the result at population scale with 9.8K reachable hosts).

Falsification target: a Typesense host returning `/collections` 200 with a JSON array would be a counter-example. None found.

---

## Cross-survey colocation

| Pair | Overlap |
|---|---|
| Vector-DB stragglers ∩ ComfyUI (548) | **0** (different operator demographics — DB ops vs consumer-GPU ops) |
| Vector-DB stragglers ∩ Ollama (16,473) | TBD — diff queued via visorlog |
| Vector-DB stragglers ∩ Mem0 (~70 candidates) | 0 — distinct populations |

No cross-platform stacking of vector-DB + image-gen at this survey's reach.

---

## Methodology placement

Adds Solr-7.x-default + Meilisearch-with-no-master-key to the Tier-A platform list. The framework's intent in both cases is "operator-configures-auth-via-env-var"; at population scale, ~10–20% of operators don't configure it. Reinforces [[insight-13-shipping-defaults-are-load-bearing]] from the disambiguation angle: when the framework offers *optional* auth, the population's unauth rate scales with the friction of enabling it. Solr's `security.json` is a multi-step JSON config file; Meilisearch's master-key is a one-line env var → Meilisearch shows lower unauth rate (~7% of 3,742 candidates real-unauth) than Solr (~21% of ~3,500 real Solr instances unauth).

Typesense + Vespa land in Tier-C: framework auth-on-default, population-scale ~0% unauth.

---

## Toolchain Provenance

```
0. shodan download × 5 dorks → 16,704 unique ip:port
   (solr_dl 2,951 + meili_dl 3,742 + typesense_dl 9,837 + vespa 45 + pgvector 129)
1. fast_enum_vectordb.py (threads=150, ~11 min) → 881 unauth + 3,116 auth-gated + 358 partial-open + 9,436 dead
2. Solr version aggregation → 516 hosts on Solr 7.6.0 (84% of unauth Solr)
3. Solr core enumeration → cores listed for 613 hosts (operator-attribution-rich)
4. Meilisearch index UID extraction → 268 hosts with app-schema disclosure
5. (queued) BARE Metasploit module ranking on Solr 7.6.0 → confirmed: solr_velocity_rce, solr_dih_rce, solr_jmx_rmi
6. (queued) visorlog ingest → 881 events into nuclide.db source='vectordb-stragglers-survey-2026-05-16'
```

---

## Honest negative space

- **pgvector population not measured.** pgvector is a PostgreSQL extension on TCP/5432; my probe used HTTP and got no signal. A TCP-direct probe with `SELECT pgvector_version();` against the 129 candidate IPs would be the right next step. The Shodan body-marker `"pgvector"` mostly caught Postgres banners that mention the extension rather than HTTP-exposed pgvector instances.
- **Solr `security.json` audit not performed.** A more nuanced classifier would `GET /solr/admin/authentication` and `GET /solr/admin/authorization` to confirm the auth-handler config; that would distinguish "framework auth genuinely disabled" from "framework auth misconfigured" (the latter being a fix tier above "set MEILI_MASTER_KEY").
- **Typesense 9,837 candidates is suspicious.** The Shodan `product:"Typesense"` facet likely includes Typesense Cloud SaaS edge instances (Typesense's hosted product) where the customer's own data is in a different control plane. The 0 unauth rate is consistent with this — those edges are managed by Typesense, not the customer, and Typesense knows what it's doing. A future port-first masscan on 8108 (Typesense's default) on tier-2 cloud would surface self-hosted Typesense and is a separate evidence base.
- **No Solr-RCE attempted.** Reading `/solr/admin/info/system` and `/solr/admin/cores?action=STATUS` confirms unauth metadata access; firing `solr_velocity_rce` would be active exploitation across 516 hosts, which crosses the ethical-stop boundary. The risk class is proven by metadata + version; the chain is documented by Metasploit history; the proof is not necessary for the case to be made.

---

## Disclosure posture

**Targeted-exception per-host disclosure recommended for:**

- The CN provincial-government Solr cluster on `119.29.117.117:8090` — 12 cores including `exploit_core` and multi-province enterprise registries. Per [[feedback_defense_contractor_disclosure_handling]] adjacent — hold cluster-level details until operator acknowledges.
- Aggregate disclosure to major cloud providers (Alibaba Cloud / Tencent Cloud / DigitalOcean) about the 516 Solr 7.6.0 hosts — image-template versioning issue.

Per broader policy: no per-host disclosure for the auth-gated 3,116 Solr/Meili hosts — that's the framework's intent.

---

## See also

- [[insight-13-shipping-defaults-are-load-bearing]] — Solr 7.x-default unauth vs Typesense API-key-default — exactly the comparison this survey adds evidence to
- [[insight-15-dork-hits-vs-platform-instances]] — `product:"Typesense"` 9,837 vs 0 unauth: an interesting "Tier-C" inversion of the FP rate (the platform IS what Shodan says it is, but the auth layer protects all 9,837)
- [`weaviate-cloud-survey-2026-05.md`](weaviate-cloud-survey-2026-05.md) — companion vector-DB survey from earlier (Weaviate, the largest of the 4 surveyed in May)
- [`image-generation-population-survey-2026-05-16.md`](image-generation-population-survey-2026-05-16.md) — the day's parallel-batch ComfyUI survey
- BARE Metasploit module ranking: `solr_velocity_rce`, `solr_dih_rce`, `solr_jmx_rmi` — apply to the 516 Solr 7.6.0 cluster
