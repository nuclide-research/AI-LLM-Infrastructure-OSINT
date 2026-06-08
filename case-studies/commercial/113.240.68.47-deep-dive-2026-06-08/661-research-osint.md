# 661 R&D Researcher — Public OSINT Report: 113.240.68.47

**Role:** NICE 661 R&D Researcher (NuClide Research)
**Target:** `113.240.68.47:8188` — confirmed unauthenticated ComfyUI host
**Netblock:** `113.240.68.0/24` (CHINANET-HN, mnt-by MAINT-CHINANET-HN)
**ASN:** AS63835 — CT-HuNan-Changsha-IDC
**Date:** 2026-06-08
**Restraint posture:** Public records only. Zero interaction with target. Zero authentication attempts.

---

## 1. Direct public mentions of 113.240.68.47

### Web search (Google/Bing via WebSearch tool)
- Query `"113.240.68.47"` (exact): **0 substantive hits.** Only numerical-coincidence noise (tax tables, fee schedules, drug stats). The exact IP string has no published presence on the indexed web as of 2026-06-08.
- Query `"113.240.68.47" site:github.com OR site:greynoise.io OR site:abuseipdb.com`: **0 direct matches.** Top results are unrelated bad-bot blocker / proxy-list files that contain similar numeric strings but not this IP.

### GitHub code search (gh CLI)
- `"113.240.68.47"` exact-quoted across all of public GitHub: **0 results.** `total_count: 0`.
- `"113.240.68."` (prefix, all files): **3 hits**, all incidental:
  1. `bbhpgh/eypg/src/ip.txt` — Chinese 1-yuan-lottery (一元云购) proxy list. Contains similar IPs but **not 113.240.68.47**. Confirmed by direct grep.
  2. `TOMXVPN/Public-cloud-cidr/ipv4.nft` — nftables `define Allow4` set. Contains literal entry `113.240.68.0/24,`. Lists the whole /24 as part of a broad cloud/hosting CIDR allowlist (the repo's `ipv4.nft` aggregates many cloud/ISP prefixes). This is netblock-level inclusion, not target-specific intel.
  3. `cqkaier/stady_C/python/security/whlg.txt` — 1500-line list of `proto://host:port` targets. Contains `http://113.240.68.8:8089`. **Sibling host on the same /24, different port.** Repo path `python/security/` and content style (port-scan / weak-pwd target list) strongly suggest a Chinese-origin recon or weak-credential sweep harvest. The exact IP 113.240.68.47 is **not** in this file.

### Wayback Machine
- `https://archive.org/wayback/available?url=113.240.68.47` -> `archived_snapshots: {}`
- `https://archive.org/wayback/available?url=113.240.68.47:8188` -> `archived_snapshots: {}`
- **Verdict: never archived.** No snapshot of any URL on this host exists in the Internet Archive.

### Conclusion on direct mentions
The IP 113.240.68.47 has **zero public mentions** across web search, GitHub code, and Wayback Machine as of 2026-06-08. The first public footprint we are aware of is the Shodan/Censys infrastructure record itself (next section).

---

## 2. Threat-intel verdicts

| Source | Result | Method |
|---|---|---|
| **Greynoise community API** (`api.greynoise.io/v3/community/113.240.68.47`) | **404 — IP not observed** by Greynoise sensor fleet. | Direct REST call. 404 on a non-Enterprise community endpoint means Greynoise has not seen this IP scanning/probing the internet. |
| **AbuseIPDB** | **403 to WebFetch** (anti-bot). Cannot retrieve programmatically without an account / session. Listed for completeness; deferred to manual browser check. | Web-UI gated. |
| **VirusTotal** | SPA-rendered; WebFetch returned only the title shell, no detection data. Deferred to manual browser check. | SPA. |
| **AlienVault OTX** | SPA-rendered; "Loading..." only. Deferred to manual browser check. | SPA. |
| **Github CriticalPathSecurity/Zeek-Intelligence-Feeds** (`sip.intel`) | Returned by search-engine query, but the IP is **not** in the file (verified by similar-prefix search). | Public threat-intel feed. |
| **mitchellkrogza/apache-ultimate-bad-bot-blocker** (`bad-ip-addresses.list`) | Search-engine match on similar prefix only; **113.240.68.47 not in the list.** | Public abuse list. |

**Net verdict:** The two threat-intel sources we can verify programmatically (Greynoise + the public bad-bot/threat-intel feeds in GitHub) **do not list this IP.** It is not currently flagged as a known scanner, proxy, abuse source, or malware C2 in any public feed I can confirm. Manual browser verification of AbuseIPDB / VirusTotal / OTX is the open item — to be completed out of band, not through this tool.

---

## 3. Censys structured view

`cencli view ip/113.240.68.47` -> **HTTP 422 "insufficient balance."** Censys Free plan credits exhausted as of session start; the platform's structured record (labels, services, threats, greynoise sub-field, life_cycle EOL) could not be retrieved this session. Re-queue when credits reset (weekly cap = 24 cr per memory `reference_censys_expert`).

**Substitute — Shodan InternetDB** (free, no API key required):
```json
{
  "ip": "113.240.68.47",
  "ports": [8188],
  "cpes": ["cpe:/a:python:python:3.13", "cpe:/a:comfy:comfyui:0.21.1"],
  "tags": ["ai"],
  "hostnames": [],
  "vulns": []
}
```

Key fields:
- **Single open port** in Shodan's view: 8188 (ComfyUI default).
- **Version-pinned CPE:** `cpe:/a:comfy:comfyui:0.21.1` — Shodan has fingerprinted the exact ComfyUI release.
- **Tag:** `ai` — Shodan's auto-tagger has classified this as AI infrastructure.
- **vulns:** empty (no Shodan-tracked CVEs for ComfyUI 0.21.1 / Python 3.13 at the IP level). Absence of `vulns` is not absence of risk — Shodan's vuln field tracks CVE-CPE matches, not ComfyUI's documented unauth-RCE-by-design surface.
- **No reverse DNS hostname** — bare IP, no PTR set. Consistent with bring-up of a rented GPU box without DNS hygiene.

**ipinfo.io supplementary record:**
- Org: CHINANET HUNAN PROVINCE NETWORK
- ASN: AS63835 (CT HuNan Changsha IDC), type **hosting**
- Location: Changsha, Hunan, China
- Abuse contact: `anti-spam@chinatelecom.cn`, registered address No. 31 Jingrong Street, Beijing
- Privacy flags: `Hosting: detected`; VPN/Proxy/Tor/Relay/Residential = not detected
- RPKI: valid

---

## 4. GitHub / scan-dataset hits

| Repo | Path | What it shows | Relevance |
|---|---|---|---|
| `TOMXVPN/Public-cloud-cidr` | `ipv4.nft` | `113.240.68.0/24,` literally listed in `define Allow4 = {...}` | Confirms the /24 is publicly catalogued as a cloud/hosting block. Allowlist-style nftables aggregation. Not target-specific. |
| `cqkaier/stady_C` | `python/security/whlg.txt` | `http://113.240.68.8:8089` present (line ~early-list) | **Sibling host on same /24 was on someone's port-scan target list.** Strong indication this /24 has seen Chinese-origin recon. Internet DB on 113.240.68.8 today shows only port 9000 open — the 8089 from the list is stale or post-mitigation. |
| `bbhpgh/eypg` | `src/ip.txt` | Proxy/lottery target list; **113.240.68.47 not present** | False positive. Coincidental prefix in a different IP. |
| `mitchellkrogza/apache-ultimate-bad-bot-blocker` | `bad-ip-addresses.list` | Not present | Negative — not flagged as a bad bot. |
| `CriticalPathSecurity/Zeek-Intelligence-Feeds` | `sip.intel` | Not present | Negative — not in this Zeek SIP intel feed. |

**Net:** The /24 has documented recon attention from Chinese-origin actors (whlg.txt). The specific host 113.240.68.47 is not (yet) in any public threat or scan dataset I can verify.

---

## 5. Candidate operator identities

### Searches run
- `"8x A100" "80GB" Changsha Hunan AI cluster` -> no specific hit linking 8xA100-80GB clusters to a named Changsha tenant.
- `"Hunan University" OR "Central South University" AI lab GPU cluster A100 ComfyUI` -> no specific hit.
- `"长沙" "A100" "8卡" 算力 ComfyUI 出租` (Chinese: Changsha + A100 + 8-card + compute + ComfyUI + rental) -> hits on **national-scale GPU rental marketplaces** (`apetops.com`, `gogpu.cn`, `luchentech.com`, `idcsp.com`, `jaeaiot.com`, `china2077.com`). None geo-pin to Changsha specifically; they aggregate compute across China.
- `"AS63835" China Telecom HuNan Changsha IDC ComfyUI exposed` -> confirms AS63835 is **a colocation IDC at No.293 Wanbao Avenue, Changsha**, hosting 3,397 domains across 1,136 IPs (per ipinsight.io / webtechsurvey).

### Candidate identity ranking

| # | Hypothesis | Confidence | Reasoning |
|---|---|---|---|
| 1 | **GPU-rental / 算力租赁 (suanli zulin) tenant** — a customer leasing an 8xA100-80GB box from a Chinese GPU-rental marketplace, with the box racked at the China Telecom Changsha IDC at No.293 Wanbao Ave. | **High.** | The A100-SXM4-80GB 8-GPU SKU is the canonical "high-end rental" SKU advertised by every major Chinese suanli-zulin vendor. China Telecom IDC hosting is the standard substrate. Bare-IP, no PTR, no DNS, unauth ComfyUI on default port 8188 = classic "tenant brought up the box and exposed the dev UI" anti-pattern, matched many times in our prior commercial-tenant case studies. |
| 2 | **Hunan-based AI startup / lab** using a leased ChinaNet Hunan IDC server for model R&D, ComfyUI deployed for in-house art/diffusion experimentation. | **Medium.** | Same physical substrate fits, but no named Hunan startup / university surfaced in searches. Hunan U and Central South U have published AI research but no public link to this prefix or this hardware footprint. |
| 3 | **Honeypot / decoy** masquerading as exposed compute. | **Low.** | The hardware claim (8xA100-80GB / 634GB VRAM) is high-cost for a honeypot. Honeypot fleets in CN tend to cluster on Akamai/Linode prefixes (see memory `reference_as63949_honeypot_fleet`), not on a single residential-style ChinaNet IDC IP. No AS63949-like clustering visible here. |
| 4 | **Hunan provincial state-affiliated AI compute** (e.g., a Hunan provincial "算力中心" — there are public announcements of provincial AI compute centers in Changsha). | **Low.** | Provincial compute centers typically run through dedicated APN / private interconnect, not over a public ChinaNet IDC IP with the ComfyUI default port wide open. Inconsistent with state-grade deployment hygiene. |

**Most likely:** Hypothesis #1 (GPU-rental tenant) by a wide margin. The disclosure target should likely be **the IDC's abuse contact (`anti-spam@chinatelecom.cn`)** as upstream, with parallel attempts to identify the rental marketplace if any operator artefact surfaces in the captured ComfyUI history.json / models.json / extensions.json. Restraint posture: do not push disclosure until a confirmed operator surfaces.

### Hunan University / Central South University
- **No public-facing AI lab page or research output ties either university to 113.240.68.0/24, AS63835, or to ComfyUI infrastructure.** Both universities have published ML research but their compute is routed through CERNET / Hunan provincial education ASNs, not AS63835 (which is a commercial IDC).

### kemuri.top cross-check
- `kemuri.top` resolves to a wholly unrelated entity: **"Kemuri" is the title of a Japanese yokai-hunting PS5 action game (Unseen / Ikumi Nakamura, 2027 release)**. The `.top` domain returns nothing connecting it to AI infrastructure, Hunan, or this IP. **No linkage.** Logged as a confirmed null on this lead.

---

## 6. Wayback Machine hits

- `113.240.68.47` -> 0 snapshots.
- `113.240.68.47:8188` -> 0 snapshots.
- This host has **never been archived** by the Internet Archive. The current OSINT capture (our case study) is the first known public record of this host's response surface.

---

## Summary — Insight #N candidate

**Insight (candidate):** A high-end unauthenticated ComfyUI host on a Chinese commercial IDC can be **completely OSINT-dark** outside the Shodan/Censys infrastructure indices — zero web mentions, zero GitHub mentions, zero Wayback snapshots, zero Greynoise observations, not in any public bad-IP feed. The /24 around it shows signs of prior Chinese-origin recon attention (sibling host in a port-scan list), but the target itself is invisible to every public-record source except infrastructure scanners. This is the **operator-OSINT-dark / scanner-OSINT-visible** asymmetry: defenders looking for evidence of exposure through reputation feeds or web search will find nothing; only infrastructure scanners (Shodan/Censys/aimap-class) surface the exposure. Anchors NuClide's standing argument that infrastructure-scanner-grade tooling is irreplaceable in AI-infra coverage.

## Open items (deferred)

- AbuseIPDB / VirusTotal / OTX **manual browser** verification (the three SPA/anti-bot threat-intel surfaces).
- **Censys structured view** — re-queue when free-tier credits reset.
- **Sibling-host triage** on `113.240.68.8` — port 9000 currently open per Shodan InternetDB; not the target, but on the same /24 and on a third-party scan list. Logged as a related observation; out of scope for THIS host's deep-dive.

---

**File location:** `/home/cowboy/AI-LLM-Infrastructure-OSINT/case-studies/commercial/113.240.68.47-deep-dive-2026-06-08/661-research-osint.md`
