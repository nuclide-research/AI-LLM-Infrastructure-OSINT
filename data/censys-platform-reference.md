# Censys Platform — Operator Reference (NuClide)

_Authored 2026-06-04 from live exploration of the authenticated Platform UI + CLI.
Account: nuclide-research, **Starter** plan, org `e9655161-8792-440c-916e-d19d30957a55`._

The legacy `search.censys.io` v2 API is deprecated for us; this documents the
**new Censys Platform** (`platform.censys.io` / `cencli`). Supersedes the
"search=403=web-UI-only" note in older memory — **with an org-id, scripted search WORKS.**

---

## 1. The unlock (was the long-standing blocker)

Scripted search returns `403 "requires an organization ID"` UNLESS the org-id is
supplied. The personal-access token alone is a "Free user"; the **org-id** carries
the paid (Starter) entitlement.

```bash
# token (once):
printf '<PAT>' | cencli config auth add --name nuclide --value-file -
# org-id MUST be passed on every command (config activate did NOT stick in testing):
cencli search '<query>' --org-id e9655161-8792-440c-916e-d19d30957a55 -O json
cencli org credits --org-id e9655161-8792-440c-916e-d19d30957a55
```

UI equivalent: every URL carries `?org=<org-id>`.

---

## 2. Plans, credits, hard limits

| Plan | Price | Credits | Result cap | History | Extras |
|---|---|---|---|---|---|
| Free | $0 | 100/mo | 100 (1 page) | none | NL search, AI assistant, **asset-lookup API only (no search API)**, 1 collection (100 assets) |
| **Starter (ours)** | $100 | **500–40,000** | **500 (5 pages)** | **1 week** | advanced protocols, **regex**, expanded API+**MCP**, 2 collections (10k assets), webhooks |
| Enterprise | custom | 200k+ | unlimited | 1+ month | deep app scan, CPE, **web screenshots + live rescan**, **CVE/vuln data**, **threat data**, 15+ collections, SSO |

**Credit model — MEASURED 2026-06-04 (supersedes earlier guesses):**

| Operation | Cost | note |
|---|---|---|
| `search` (UI or CLI, ANY page count incl. `--max-pages 1`) | **5 credits, flat** | ~5-credit floor; pages don't lower it |
| `aggregate` | **5 credits** | NOT cheap (earlier claim was wrong) |
| `view <ip>` | **1 credit** | the cheap per-host primitive |
| cache hit (censys-cache) | **0** | the real saver |

NO server-side caching (identical re-run charges again). Balance: `cencli org credits --org-id …`.
Earlier notes that "the CLI is cheaper than the UI" and "aggregate ≈ 1 credit" were WRONG —
both measured at 5. There is **no free-scrape path** (charge is server-side in the Remix
`.data` loader; devtools can't dodge it).

> **Credit-minimal workflow, in order:**
> 1. **`censys-cache search '<q>'`** (the `~/censys-cache` tool) — checks our local
>    cache first; HIT = 0 credits. Route EVERY Censys query through it. (See [[project-censys-cache]].)
> 2. **Shodan-primary** (free on Freelance) for bulk harvest; Censys only for the gap/delta.
> 3. One 5-credit search returns a LOT (full 500 results + the facet sidebar = port/ASN/
>    software distribution). Extract everything from that single call; never re-query.
> 4. **`cencli view <ip>`** (1 credit) on CONFIRMED hosts → zero-uplink shadow ports +
>    cert + data-tier auth decoders. Cheapest per-host enrichment.
> 5. Never re-run a search; never blind-page.

> **Starter caps at 500 retrievable results/query.** A platform with >500 hosts
> (e.g. LibreChat 3,142) truncates — use aggregations for the true count, and
> narrow with `and` facets (port/ASN/country) to pull the population in slices.

**Two cost-savers Nick should know:**
- **MCP access** is included on Starter — a Censys MCP server can wire directly
  into the toolchain (see §7).
- **Research Access Program** — students/independent researchers qualify for free
  elevated access. Nick (published CISA advisories CVE-2025-4364, ICSA-25-140-11)
  likely qualifies; apply at platform.censys.io → Plans → "Apply for Research Access"
  rather than paying for Starter.

---

## 3. Data model — three collections

| Collection | Size | Field root | What it is |
|---|---|---|---|
| **Hosts** | 219M | `host.*` | an IP and all its services |
| **Web Properties** | 2.2B | `web.*` | a hostname:port web endpoint (vhost-level) |
| **Certificates** | 15B | `cert.*` | every CT-log + scanned leaf cert |

A search hits all three; the result sidebar splits counts by **ASSET TYPES
(Hosts / Web Properties / Certificates)**. Host search and Web-Property search of
the same dork return *different* counts (Coze: 301 hosts vs 428 web-properties vs
267 Shodan) — they are complementary populations; union them.

**Host record (from a live `view`)** contains, with ZERO probing from us:
- `host.services[]` — every open port: protocol, software (vendor/product/version),
  full banner, TLS handshake (version/cipher), the leaf cert (Subject/Issuer DN,
  fingerprint, trust), and **protocol decoders** (FTP auth response, MySQL/Redis/
  Mongo/Postgres handshake → data-tier auth state without connecting).
- `host.labels[]` — auto-classification: `AI`, `DATABASE`, `REMOTE_ACCESS`,
  `HONEYPOT`, `BULLETPROOF`, `OPEN_DIRECTORY`, … (native honeypot filtering!).
- WHOIS (network + org), `host.autonomous_system.asn`, geolocation, reverse/forward DNS.
- Service History, Event History, Related Assets, **Raw Data (JSON)**, "Summarize Host" (AI).
- CVEs panel (shows 0 on Starter — **CVE data is Enterprise-gated**).

**Why this matters for NuClide:** one host `view` replaces Stage 2 (VisorGraph
cert-pivot — the Subject DN is right there), the IP-direct shadow-port sweep
(Insight #12 — the full service list incl. MySQL/Redis/Mongo is right there), and
data-tier auth reads (the decoders) — all with **no packets from our network**.
Proven live: a Flowise-critical host surfaced MySQL/3306 + FTP + SSH + a BT-PANEL
(Chinese aaPanel) cert in a single zero-uplink lookup.

---

## 4. CenQL — query syntax (from live example queries)

| Construct | Meaning | Example |
|---|---|---|
| `field: "x"` | contains / tokenized match | `web.endpoints.http.html_title: "Coze"` |
| `field = "x"` | exact match | `host.services.software.product = "cpanel"` |
| `field: *` | field exists | `host.ip: *` |
| `a and b` / `or` / `not` | boolean | `product:"PAN-OS" and not labels="HONEYPOT"` |
| `{ "a", "b" }` | value-set (OR) | `product = {"netscaler gateway","netscaler"}` |
| `field =~ "regex"` | regex (Starter+) | `host.services: (banner =~ "\\w+\\s+[0-9]+...")` |
| `parent: (sub=x and sub2=y)` | nested grouping on one object | `host.services.software: (vendor="citrix" and product="netscaler")` |

**Key field paths:**
- Host HTTP: `host.services.endpoints.http.html_title`, `…http.favicons.hash_md5`,
  `host.services.protocol`, `host.services.port`, `host.services.software.{vendor,product,version}`
- Host cert: `host.services.cert.parsed.subject_dn`
- Web property: `web.endpoints.http.html_title`, `web.endpoints.http.favicons.hash_md5`,
  `web.software.product`, `web.cert.parsed.subject_dn`, `web.port`
- Cert: `cert.fingerprint_sha256`, `cert.parsed.subject.cn`
- Labels: `host.labels.value = "HONEYPOT"`, `web.labels.value = "OPEN_DIRECTORY"`
- Attribution: `host.autonomous_system.asn`, WHOIS fields

**Always append `and not labels="HONEYPOT"`** — Censys ships native honeypot
classification (complements aimap/VisorCAS honeypot screening, Insight #1).

---

## 5. UI surfaces

- **Search** (`/search?q=…`) — query + faceted sidebar (free facets: software
  vendor/product, ASN, country, port). The sidebar IS a free aggregation preview.
- **Report Builder** (`/search/report/data/table?q=…&field=<any-field>&num_buckets=2000&filter_query=true`)
  — full aggregation/facet on ANY field. URL-driven; use for true population counts
  and port/ASN/title distributions (cheaper than paging raw results).
- **Collections** (`/collections`) — saved asset groups (Starter: 2 collections,
  10k assets each) with **webhooks** → continuous monitoring of a survey population.
- **Search History** (`/home/search-history`), **Tags** (`/tags`) — workflow.
- **Modules:** **Adversary Investigation** (`/explore/threats`), **Critical
  Infrastructure** (`/explore/critical-infrastructure`) — curated threat/ICS hunts.
- **AI assistant / Natural-language search / "Summarize Host"** — NL→CenQL + host summaries.
- **Security Advisories** feed — Censys's own CVE research (PAN-OS, cPanel, etc.).

---

## 6. CLI (`cencli`) — maps to UI, ALL need `--org-id`

| Cmd | Use |
|---|---|
| `search '<cenql>' -O json` | population pull (≤500 on Starter; `--page-size` to limit) |
| `aggregate` | field aggregation (Report Builder equiv) — true counts, cheap |
| `view <ip\|cert\|webproperty>` | full structured record (shadow ports + cert + decoders) |
| `censeye <host>` | auto-generate pivotable queries with rarity bounds |
| `history` | host/cert/web-property history (Starter = 1 week) |
| `org credits --org-id …` | balance |
| `-O json\|yaml\|tree`, `-S` NDJSON streaming | output formats |

---

## 7. How Censys slots into the NuClide chain

- **Stage 0b (cross-population, Insight #69):** run each platform dork against
  host + web-property collections, take the DELTA vs the Shodan corpus — Censys's
  full-port-range catches what Shodan's scheduled crawler misses (proven: Coze on
  38010/20002). Merge delta into `ips.txt`. Use `aggregate` for true counts (beats
  the 500-result cap).
- **Stage 2 (attribution):** the host `view` Subject DN = free cert-pivot seed.
- **Shadow-port sweep (Insight #12):** for any Censys-covered host, the service
  list already enumerates adjacent ports (MySQL/Redis/Mongo) + their auth decoders
  — **prefer this over tiptoe/aimap shadow probing; zero uplink** (serves the
  no-home-internet-saturation rule). Fall back to tiptoe only for hosts Censys
  hasn't scanned recently (1-week history limit on Starter).
- **Honeypot screening:** `and not labels="HONEYPOT"` in every dork.
- **Action item:** evaluate the **Censys MCP server** for direct toolchain wiring;
  apply to the **Research Access Program** (free, Nick qualifies).

**Credit discipline:** 485 credits left of 500. Use `aggregate` for counts,
`view` for confirmed hosts, narrow searches with `and`-facets, never blind-page to 500.
