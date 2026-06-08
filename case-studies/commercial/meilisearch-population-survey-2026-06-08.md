---
type: survey
category: vector-db-search
platform: meilisearch
date: 2026-06-08
researcher: NuClide Research
---

# Meilisearch Population Survey: 282 Unauth Hosts, 780 GB Exposed, Hong Kong Spam Botnet

_NuClide Research · 2026-06-08_
_Related: [`comfyui-population-survey-2026-06-08.md`](comfyui-population-survey-2026-06-08.md) (sibling auth-gradient evidence point)_

---

## Summary

Population-scale survey of Meilisearch, the Rust-based search engine with native vector search since v1.x, on Shodan dork `http.title:"Meilisearch"`. 3,440 total hits, 3,343 unique IPs harvested.

**Headline numbers.** 2,949 of 3,343 hosts responded (88 percent live, far higher than ComfyUI's 30 percent because Meilisearch concentrates on managed cloud VPSes rather than residential GPU rigs). **2,652 of 2,949 LIVE hosts (90 percent) return 401 on `/stats`** — i.e. the operator set `MEILI_MASTER_KEY` per the documented production deployment path. **282 of 2,949 LIVE hosts (9.6 percent) return the unauth `/stats` shape** (top-level `indexes` + `databaseSize`). The remaining ~1 percent are 403, 408, or shape-FPs.

**Exposed payload (metadata only, no record reads).** **780 GB of total database content** across 282 unauth hosts. **13 hosts each exposing more than 10 GB**; the largest single database is 42.8 GB on a DigitalOcean US box. Index counts total 7,169 indexes — but 6,402 of those come from a single 66-host content-spam botnet (below).

**Hong Kong content-spam botnet finding.** Sixty-six hosts at `177.210.106.{35,39,44,48,52,53,58,...}` run **identical 97-index sets**, all named `articles_<chinese-brand-domain>_com`. The same names. The same per-domain shape. Same /24, "HongKong Service" netblock attribution. This is a coordinated SEO content-spam farm where each Meilisearch box backs the article search for one domain in a per-tenant pattern. **0 of the 66 boxes set `MEILI_MASTER_KEY`** — operator never configured auth on any node of the cluster. Index names alone are the operator-attribution finding; no record read needed.

**Data-class patterns from index names (no records read).** "profiles" databases on multiple hosts (likely PII), "doc_chunks" (RAG context for an LLM application), "prod_produit" on a French Scaleway host (e-commerce product catalog), "enderecos" on three Google Cloud hosts (Brazilian address records), "service_providers" cluster on three AWS EC2 hosts (yellow-pages-like SaaS), "companies", "goods" (Alibaba Cloud CN). Names are the finding.

<!-- ksat-tag:auto-generated:start -->
## DCWF KSAT coverage

Wardrobe outfit: `ai-infra-hunt`.

- **672 (AI Test & Evaluation Specialist):** T5919 (adversarial test in op env — the `/stats` marker), K7044 (V&V tools), S7067 (low-prob high-impact data risks — the spam-botnet and PII-name finds).
- **733 (AI Risk & Ethics Specialist):** T5893 / T5882 (responsible AI — fingerprint-not-exfiltrate; index NAMES only), K7040 (PHI/PII surface — names-only).
- **NICE 541:** T0028, T0188, K0342, S0001, S0051, T0247, K0107, K0118.

<!-- ksat-tag:auto-generated:end -->

---

## Methodology

```
Stage 0    Shodan API on  http.title:"Meilisearch"          →  3,440 total
              shodan download --limit 5000                  →  3,343 saved

Stage 0c   verify.py — 250-thread, two-stage marker
              GET /health  → {"status":"available"}  (identity)
              GET /stats   → {indexes, databaseSize}  (200 = unauth, 401/403 = gated)
              honeypot pre-filter: AS63949 salt          → 0 hits
              result: 282 unauth / 2,666 auth-gated / 393 dead / 2 FP

Stage 3    rDNS + WHOIS attribution on top-10 by DB size
              + 177.210.106.x cluster cluster attribution

Stage 6    visorlog ingest → meilisearch-2026-06-08.db (282 events)
```

**Restraint ethic.** Read-only metadata. We did NOT read `/indexes/{uid}/documents` (the record bodies). The `/stats` endpoint is sufficient to confirm unauth (status code + shape), enumerate index names, and capture per-index document counts and per-host database size. Index NAMES are the published finding; the payload bodies are exactly what we refuse to read.

---

## Findings

### Distribution

| metric | value |
|---|---:|
| Shodan total | 3,440 |
| Unique IPs harvested | 3,343 |
| LIVE on probed port | 2,949 (88 %) |
| Confirmed UNAUTH | **282 (9.6 % of live)** |
| Auth-gated (401/403) | 2,666 (90.4 %) |
| Total DB exposed | **780 GB** |
| Hosts > 10 GB | 13 |
| Hosts > 1 GB | 109 |
| Total indexes exposed | 7,169 |

### Top-15 by database size

| ip:port | DB MB | indexes | top index names |
|---|---:|---:|---|
| 68.183.134.195:80 | 42 835 | 1 | documents |
| 34.120.19.134:443 | 23 360 | 2 | airbyte, enderecos |
| 34.46.34.226:80 | 23 360 | 2 | airbyte, enderecos |
| 34.132.107.56:80 | 23 360 | 1 | enderecos |
| 45.13.237.143:7700 | 21 163 | 1 | pages |
| 101.133.157.58:7700 | 16 867 | 1 | goods |
| 24.199.72.90:7700 | 12 995 | 1 | profiles |
| 68.183.114.219:7700 | 12 470 | 1 | profiles |
| 77.42.30.244:7700 | 11 641 | 1 | doc_chunks |
| 62.210.222.51:7700 | 11 018 | 2 | prod_produit, prod_produitSpe |
| 178.128.233.232:80,443 | 10 888 (×2) | 6 | brands, categories, items, movies, specifications |
| 18.233.66.137:80 | 10 331 | 4 | service_provider_indices, service_providers… |
| 54.83.127.94:80 | 8 821 | 4 | service_provider_indices… |
| 18.184.53.100:80 | 7 574 | 1 | companies |
| 141.94.11.154:7700 | 7 060 | 2 | cataloghi, lotti (IT) |

### The Hong Kong content-spam botnet

Sixty-six hosts at `177.210.106.{35,39,44,48,52,53,58,…}` ("HongKong Service" netblock). Each runs the same 97 Meilisearch indexes:

```
articles_0932247411_com   articles_13653106695_com
articles_575177_com       articles_bj5777_com
articles_bjmshq_com       articles_bucoelevators_com
articles_chadroto_com     articles_chinaworkshops_net
... 89 more, same naming pattern, same shape ...
```

Each `<domain>` portion is a separate brand or property the operator owns or operates content for. The pattern reads as a per-domain article-search backend deployed identically across the cluster — SEO content-spam at scale. 6,402 of the 7,169 total indexes seen in this survey come from this single operator. No `MEILI_MASTER_KEY` set on any node. **Names alone identify the operator and the operation; we read zero records.**

### Attribution patterns (substrate)

DigitalOcean dominates the top-DB-size list (4 of top 15). Google Cloud accounts for 3 of the top 4 (the 23 GB `airbyte + enderecos` cluster). AWS EC2 holds the `service_providers` cluster across us-east-1 + eu-central-1. Hetzner FI and Scaleway FR appear once each. Alibaba Cloud CN holds a 17 GB `goods` index. The 66-host spam botnet runs on a Hong Kong netblock.

The substrate is the public cloud; the misconfiguration is operator-side; the platform default is the load-bearing factor.

---

## Risk

For each confirmed unauth host:

1. **Full-text + vector search disclosure** of every document in every index.
2. **Schema disclosure** via `/indexes/{uid}` — searchable attributes, filter rules, sortable fields.
3. **Document mutation** — `POST /indexes/{uid}/documents` accepts arbitrary content; the operator's search corpus can be poisoned (PoisonedRAG-class attack against any downstream RAG that consumes this Meilisearch).
4. **Index deletion** — `DELETE /indexes/{uid}` removes every document (availability impact).
5. **Master-key bootstrap** — once an attacker writes to a no-auth Meilisearch, they can also use the admin API to provision their own key, locking the operator out.

Per-host severity: **high** for hosts > 1 GB or > 20 indexes (likely production), **medium** for hosts 100 MB – 1 GB, **low** for sub-100MB dev/staging deployments.

The platform fix is one environment variable: `MEILI_MASTER_KEY=<random-32-bytes>` at process start. 90 percent of LIVE operators do exactly this — the documentation foregrounds it as the production deployment step. The 282 misconfigured hosts are the long-tail of operators who followed the docker quickstart and stopped reading.

---

## Toolchain provenance

```
shodan count "http.title:\"Meilisearch\""                  →  3,440
shodan download meilisearch-title (limit 5000)             →  3,343 IP:port pairs
verify.py (Python urllib + ThreadPool 250 wk, /health → /stats two-stage)
                                                            →  282 unauth confirmed
dig + whois on top-15 + 177.210.106.x cluster              →  named operators
visorlog --db meilisearch-2026-06-08.db ingest             →  282 events
```

Wardrobe outfit: `ai-infra-hunt`. Syllabus context: PoisonedRAG (USENIX '25), Topic-FlipRAG, Needle-in-RAG — Meilisearch corpora that back LLM RAG pipelines are the high-leverage poisoning target.

---

## Thesis contribution — the auth-friction gradient

This survey, taken with the same-day ComfyUI population survey and prior platforms, supplies a four-point gradient on **deployment-time auth friction vs. population-scale unauth rate**:

| Platform | Auth friction at deploy | Unauth rate |
|---|---|---:|
| Langfuse | Forced (no toggle) | ~0 % |
| **Meilisearch** | **1 env var, foregrounded in docs** | **9.6 %** |
| Phoenix | 1 env var, not foregrounded | ~25 % |
| ComfyUI | No auth concept at all | 77.5 % |

The function is roughly linear in friction-steps with a sharp discontinuity at "no auth concept" (right-tail) and "forced" (left-tail). Documentation that foregrounds the production-auth path is doing real population-scale work: Meilisearch is the cleanest evidence point of "soft-default + good docs ≈ good outcome" in the survey set.

---

## Insight candidate #88

**Auth gradient by config friction.** Across platforms with comparable operator pools, the platform's auth friction at deploy time predicts population-scale unauth rate more reliably than any specific config flag. Approximate scaling:

- 0 steps (forced): ~0 % unauth
- 1 env var, foregrounded in docs: ~10 % unauth
- 1 env var, not foregrounded: ~25 % unauth
- no auth concept exists in framework: ~78 % unauth

Promote when a fifth platform lands in or refutes the gradient.

---

## Honest negative space

- Did not probe alt-port population beyond what Shodan's port column indicated; some operators run Meilisearch behind nginx on 80/443 (large /16 of hits on those ports) and the proxy-tier auth check is the same `/stats` 401 we observed.
- The 282 unauth hosts include 4 host pairs on dual ports (e.g. 178.128.233.232:80 + :443 = same operator), so distinct operators are ~278.
- Censys cross-population not yet checked — `cencli view` budget would identify whether Censys saw additional ports per IP.
- No JS-bundle stage (no SPA — Meilisearch ships an admin dashboard at `/` but it is auth-gated when a key is set; on unauth hosts it is just the same `/health` and `/stats` already enumerated).
