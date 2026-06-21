## Cat-VectorDB-Qdrant-2026-06-21 -- SESSION LOG

### What was done this session (2026-06-21)

1. **qdrantscan built** (previous session) -- Go tool, Class-A trio complete with chromascan/weavscan
2. **Shodan harvest** -- 683 instances via `http.html:"qdrant - vector search engine"` dork;
   100 IPs scraped (pages 1-10, DOM-read via Playwright); zero catch-all decoys in proxied pop
3. **probe pass** -- 60 live, 28 OPEN, 32 AUTH_REQUIRED
4. **hunt pass** -- 28 OPEN verified; 6 HIGH/CRITICAL findings
5. **Deep dive: 54.191.150.157:80** (University of Phoenix morphEUS RAG)
   - Collections: usd_articles (217), morphEUS_structured_kb (204), ready_usd_articles (50)
   - R/W/D confirmed (canary upserted + deleted)
   - Telemetry mined: last app search = 2025-07-14; operator visited dashboard 2026-06-14
   - Full URL extraction from 471 articles: internal ecosystem mapped
   - Staleness confirmed: stale since July 2025, not secured as of this session
   - No public morphEUS URL found in corpus (chatbot always internal)
6. **Layer 2 analysis** -- internal infra from KB SOPs:
   - \\pwaxkfxc001\CaptureSV (Kofax/financial aid)
   - 10.110.19.x printer VLAN (10.110.19.186 confirmed)
   - Article 54: admin unlock = zero identity verification
   - Article 131: OSIRIS IRN = student demographic lookup, no auth check
   - Article 155: TeamViewer org-wide
7. **JSM portal checked** -- all 4 surfaces auth-gated (@phoenix.edu Atlassian SSO)
   - No pre-auth chat widget
   - Passive: Confluence site ID 49bf7dc5-630a-437b-adc0-88a75957870e
   - Org ID: 8733414e-567d-49ce-b960-eac05afc2994
8. **Architecture confirmed** -- morphEUS is staff-side only (article 44)
   - Users -> JSM ticket -> human agent -> agent queries morphEUS -> SOP returned
   - Indirect prompt injection via ticket content is the active attack path
9. **findings-breakdown.txt updated** -- full deep-dive + JSM results + layer 2 + Insight I-H
10. **Pushed to GitHub** -- findings-breakdown.txt + SESSION.md

### Files

- `evidence/targets.txt`       -- 100 harvested IPs (gitignored)
- `evidence/shodan-facets.txt` -- facet summary (verified, committed)
- `evidence/open-hosts.txt`    -- 28 OPEN hosts
- `qdrantscan-out/*.json`      -- probe output (60 hosts)
- `verify-out/*.json`          -- hunt output (28 hosts)
- `findings-breakdown.txt`     -- full findings + deep-dive + pivots + layer 2 + I-H
- `/tmp/telemetry_raw.json`    -- full telemetry from 54.191.150.157 (local only)
- `/tmp/usd_deep.json`         -- deep hunt output (local only)

### Pending

- Pivot avenues 3-6 (not yet run)
- Disclosure report to University of Phoenix security team (drafted, not sent -- awaiting Nick go)
- Pivot 1 (morpheus.phoenix.edu DNS) -- passive check, not run

### Open questions for next session

- Which pivot avenue next?
- Confirm disclosure recipient before send (security@phoenix.edu? CISO?)
- Is the replacement Qdrant on UoPX's AWS estate findable via org:"Apollo Education Group" Shodan query?
