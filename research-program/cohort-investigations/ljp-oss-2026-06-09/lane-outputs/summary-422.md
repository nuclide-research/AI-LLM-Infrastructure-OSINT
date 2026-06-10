# DCWF 422 Discovery Scale-Up Synthesis

## Multi-source enumeration result

Multi-source enumeration of the LJP-OSS cohort across 5 disparate data sources expanded **491 (original) -> 657 (combined, raw) -> 619 (combined, origin-only)** unique IPs.

The favicon-hash vector recovered population-scale data (16,623 hosts visible in Shodan for hash `1585982716`), confirming the cohort universe is dominated by Sub2API-class instances.

## Per-vector hit counts

| # | Vector | Universe sampled | Raw new IPs | Origin (post-CDN) | Unique attributable |
|---|---|---|---|---|---|
| 1 | Shodan favicon mmh3 (`1585982716`) | 16,623 (Shodan total) | 114 | 114 | 114 |
| 2 | CT logs (6 cached + 9 new ops, crt.sh 502s) | 107 SANs / 32 resolved | 10 | 6 | 6 |
| 3 | HackerTarget reverse-IP (50/day, hit @ 21) | 21 cohort IPs probed | 3 | 3 | 3 |
| 4 | gh code+issue + aggregator README + v2ex (V4+V5 joint URL resolution) | 232 URLs / 28 op-host candidates | 39 | 5 | 5 |

(V4 standalone literal-IP match returned 0; the actionable yield came from resolving the URLs the gh code/issue corpus surfaced. V5 awesome-claude-api README returned 0 new URLs - empty/no LIST.md; useful URLs came from gh code v2ex.com+sub2api.)

## Highest-multiplier vector

**Shodan favicon hash `1585982716`** is the dominant multiplier - 114 origin IPs new vs cohort from a 25-page harvest. The full Shodan-side population (16,623 hosts) is **~33x the existing cohort** (491), so the discovery gap is now in *Shodan pagination depth* (page 22+ stops returning cards) not lack of identifier.

Recommended next move: shard the `http.favicon.hash:1585982716` query across the top 30 countries and top 30 orgs (broken in this run by /search/facet returning Cloudflare 403; pivot to sidebar facets + WORLD_MAP_DATA scraped from a single warm /search page).

## Discovery gap remaining

- Cohort v2 master (raw, CDN included): **657** IPs (5.2% of estimated 12,577)
- Cohort v2 master (origin-only, recommended): **619** IPs (4.9%)
- Gap remaining (origin-only basis): **11,958 IPs** to estimated 12,577

Of the 16,623 Shodan favicon hits, we sampled 200 cards across pages 1-25 and resolved 185 unique IPs. The 100-page-depth cap on Shodan free-tier is the binding constraint; sharding by sidebar facets is the path past it.

## Per-vector multiplier ranking (origin-only new IPs)

| Rank | Vector | Origin-IP yield |
|---|---|---|
| 1 | V1_favicon | 114 |
| 2 | V2_ct | 6 |
| 3 | V4_V5_url_resolution | 5 |
| 4 | V3_reverse_ip | 3 |


## Operational observations (DCWF K0006 / K0070 / K0177)

- **V1 (favicon)** scales orthogonally to V2-V5. The favicon hash is a *contentful* fingerprint - the Sub2API project ships an identical favicon across deploys, so the hash partitions the population sharply. Cloudflare-fronted operators still appear because Shodan crawls the origin during cert refresh windows.
- **V2 (CT)** suffered crt.sh upstream 502s on 9/15 operator queries - the resolution-layer yield came entirely from the 6 cached operator datasets. crt.sh availability is a single point of failure for the CT lane; mirroring to Censys would resolve it.
- **V3 (HackerTarget free)** hit its 50/day cap at 21 cohort IPs. The 21 probes surfaced 33 co-hosted domains - a 1.57x co-hosting density. At full 50/day cap this projects to ~78 co-hosted domains. Yield was 3 new IPs (mostly because cohort IPs sit on dedicated infra, not shared hosting).
- **V4+V5 (leak mining)** surfaces operator URLs, not IPs. The URL-to-IP resolution layer is necessary; without CDN filtering, 87% of yields would be CDN edge nodes (no recon value). After filter, V4+V5 contributed 5 origin IPs - notably the Railway.app egress block `69.46.46.0/24` (sub2api-app-production, sub2api-cn-relay-production).

## Discovery gap analysis (DCWF T0072 / T0181)

The favicon-vector population is **34x bigger** than the existing cohort. The next discovery action is *not* a sixth vector - it is **deeper pagination on V1**, achieved by sharding. The empirical Shodan free-tier depth cap is ~22 pages of 10 cards each (220 cards visible per query), so a 30-country + 30-org shard projects 60 shards x 220 cards = up to 13,200 unique IPs - within range of the 16,623 universe.

## Source files

- `~/syllabus/discovery/favicon-harvest.json` (V1, 185 IPs)
- `~/syllabus/discovery/ct-domains-resolved.json` (V2, 11 IPs)
- `~/syllabus/discovery/reverse-ip.json` (V3, 14 IPs)
- `~/syllabus/discovery/github-leaks.json` (V4, 0 literal IPs)
- `~/syllabus/discovery/aggregator-list.json` (V5, 0 literal IPs)
- `~/syllabus/discovery/leak-urls-resolved.json` (V4+V5 URL->IP, 39 IPs / 5 origin)
- `~/syllabus/discovery/leak-urls-origin-only.json` (V4+V5 CDN-filtered)
- `~/syllabus/discovery/cohort-master-v2.txt` (657 IPs, raw)
- `~/syllabus/discovery/cohort-master-v2-origin-only.txt` (619 IPs, recommended)
