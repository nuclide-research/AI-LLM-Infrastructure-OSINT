---
type: survey
---

# Ollama Population Survey — Shodan-Walk (2026-05-15)

_NuClide Research · 2026-05-15_
_Predecessors: [`ollama-cloud-survey-2026-05.md`](ollama-cloud-survey-2026-05.md) (DO/Hetzner/Vultr baseline, 342 hosts) · [`ollama-tier2-cloud-survey-2026-05.md`](ollama-tier2-cloud-survey-2026-05.md) (Scaleway/OVH/Linode, 850 hosts post-honeypot-filter)_

---

## Summary

Re-survey of the Ollama exposure surface, walked **on Shodan** rather than via masscan-on-cloud-prefixes. The prior two surveys (5.38M IPs across six tier-1+2 clouds) found **1,192 confirmed unauth Ollama**. This re-survey walks the Shodan-indexed Ollama population directly:

- **20,765 hits** on `product:Ollama port:11434` (default-port subset)
- **40,508 hits** on `http.html:"Ollama is running"` (broader HTML signature)
- Harvested + deduplicated + country-faceted retry → **25,092 unique IPs across both dorks**
- **16,473 confirmed unauthenticated Ollama instances** post fast-enum verification — **a 13.8× extension** of the prior 1,192-host catalogue

Three independently publishable macros from this run, all material:

1. **Population growth: 52% in 15 days.** The `http.html:"Ollama is running"` Shodan dork went from **26,580 (2026-04-30 catalogue) → 40,508 (2026-05-15)** — operator deployment vastly outpaced any auth-posture mitigation. The framework still ships without an authentication concept; adoption keeps accelerating.

2. **AWS dominates the operator-host distribution at ~3,720 hosts (~23% of corpus).** Prior tier-1+2 surveys (DO/Hetzner/Vultr/Scaleway/OVH/Linode) never scoped AWS. The Shodan-walk methodology surfaces that **the largest single cloud hosting unauth Ollama is AWS — invisible to masscan-on-cloud-prefixes scoped to "tier-2 budget clouds."** Discovery channels are complements, not substitutes (codified below as the new Insight).

3. **`/api/show` SYSTEM-prompt corpus.** **1,007 confirmed-unauth hosts** ship with an operator-set SYSTEM prompt visible via the `/api/show` Modelfile endpoint — operator-customized agents, business-logic disclosures, agent personas. The non-default-system subset (filtering out canonical model defaults like "You are Qwen, created by Alibaba Cloud…") yielded **133 distinct operator-built deployments**: Indonesian-government SI-JACK assistant, Bitcoin ETF options trader, Turkish industrial-robot expert, Brazilian-Portuguese business chatbot, and 114 other unique SYSTEM prompts — each one a fingerprint of what the operator built on top of unauth Ollama. New attribute axis the methodology hadn't yet codified.

---

## Methodology

### Discovery (Stage 0)

```
shodan_paginate.py --query 'product:Ollama port:11434'           → 18,191 unique IPs
shodan_paginate.py --query 'http.html:"Ollama is running"'       → 1,611 unique IPs (page-70 500)
shodan_paginate.py --query '...html dork... country:XX' × 17     → 20,890 unique IPs
                                                                    (DE 3,882 · CN 2,394 · US 4,495 · FR 1,639
                                                                     · FI 687 · HK 923 · IN 990 · CA 821 ·
                                                                     KR 914 · GB 688 · JP 635 · SG 674 · AU 578
                                                                     · BR 553 · ID 512 · NL 314 · RU 191)
merge_and_filter.py (dedup ip:port + pre-aimap AS63949 honeypot sniff)
                                                                  → 25,092 unique IPs · 31,510 ip:port records
                                                                    → 0 harvest-time honeypots (Shodan banners
                                                                      too short to carry the kitchen-sink JSON
                                                                      markers; post-aimap filter is load-bearing)
```

### Verification (Stage 2 — load-bearing)

The 8-parallel-chunk pipeline + a custom direct prober replaced aimap PHASE 3 for performance reasons (detailed below):

```
8× aimap chunks (PHASE 1 + 2 only, threads=100 each, port=11434, timeout=5s)
                                                                  → 10,895 unique Ollama-confirmed (ip:port)
fast_enum.py --threads 200 --timeout 6s (replaces aimap PHASE 3)
   - GET /api/version
   - GET /api/tags                (model list)
   - GET /api/ps                  (currently loaded models)
   - POST /api/show {"name":"<m>"} (Modelfile + SYSTEM + ENV)
   - HEAD /api/generate / /api/pull (auth-finding confirmation)
   - AS63949 honeypot post-filter (the load-bearing one)
                                                                  → 10,183 confirmed unauth (main pass)
                                                                  → 6,290 confirmed unauth (delta pass on 6,901
                                                                    country-split net-new IPs)
                                                                  → 16,473 total confirmed unauth Ollama
```

### Attribution / classification

```
aimap-profile.py (3 high-value sample hosts)            → per-host classification + ethics flags
visorgraph -ip <ip> -no-active (5 sample hosts)         → cert-pivot null (Ollama doesn't ship TLS)
visorsd -asn <ASN> -stack inference (top 5 ASNs)        → preset queries 0/3 (Ollama dorks not in stack)
menlohunt scan -ip <gcp-ip> (1 GCP-resident host)       → 10 findings, 3 attack chains
visorgoose density                                       → 33 gov-TLD hits across 25 TLDs (see below)
```

### Score + corpus + ledger

```
visorlog ingest --from events.ndjson --db nuclide.db    → 4,891 events into canonical ledger (ECS schema)
visorscuba --db nuclide.db assess                       → AI.C1–C6 + AI.H1–H5 OPA/Rego policy run
bare bare/findings.json                                 → CVE-2024-37032 ranked #1 across all Ollama findings
visorcorpus build -profile strict -type hybrid -max 500 → 500 adversarial cases for VisorAgent lab use
visoragent list                                         → enumerated; ethical-stop boundary respected
```

### Tools that ran with caveats (recorded, not silent)

- **VisorBishop**: ran on 5,895 high-value URLs but its platform-detection layer reported `confirmed=false` on all (its known-service set may not include Ollama). The `-ip-shadow` flag only fires on confirmed platforms, so the 15-port shadow did not execute. Recommend re-running with `-ip-shadow-all` to bypass that gate.
- **recongraph**: invocation broken in this environment — entrypoint issue ("can't find `__main__` module"); tool packaging bug.
- **VisorRAG**: blocked on embeddings API 401 (OpenAI key absent); runs cleanly with valid key.
- **cortex**: schema mismatch — expects SKELETON/VIOLATIONS/CONTEXT markdown; aimap-profile output is JSON. Adapter work flagged for follow-up.
- **JS-bundle extraction**: depends on Bishop tagging Open WebUI pairs; without Bishop's platform tagging, no automatic input. Targeted port-8080 sweep over confirmed-Ollama set flagged for follow-up.
- **VisorAgent**: list-mode catalog enumerated; run-mode not pointed at survey hosts per ethical-stop boundary (would run against `localhost` with the prepared abliterated VisorCorpus).
- **VisorHollow**: `[—]` Windows-only, not applicable.

All 19 arsenal tools accounted for; the methodology's "null result is a result" discipline applies to caveats. Restraint: read-only metadata enumeration throughout; no `/api/generate`, no `/api/chat`, no `/api/embeddings`, no `/api/pull` invocations.

---

## Findings Summary

| Metric | Value |
|---|---|
| Shodan-indexed corpus (union of both dorks) | 25,092 unique IPs |
| **Confirmed unauthenticated Ollama** | **16,473** |
| Dead at probe time | 798 (4.6%) |
| **Catalogue extension** (vs prior 1,192) | **13.8×** |
| AS63949 honeypot pollution rate | 0% (post-filter) |
| **`:cloud`-billing surface** (paid-quota theft) | **4,987** (30% of confirmed) |
| MANY_MODELS hosts (≥10 models loaded) | 2,777 (17%) |
| **SYSTEM-prompt leak** (`/api/show`) | **1,007** (6%) |
| SYSTEM-prompt operator-customized (non-default) | **133 distinct strings** |
| **ABLITERATED / uncensored** operator finetunes | **406 hosts** (20× growth vs prior 20) |
| HEXSTRIKE-AI offensive orchestrator loaded | 1 host |
| BARE top-ranked exploit module | `exploits/linux/http/ollama_rce_cve_2024_37032` |

---

## Geographic Distribution — Top 15 Countries (Confirmed Unauth)

| CC | Count | %     |  | CC | Count | %   |
|----|-------|-------|--|----|-------|-----|
| 🇺🇸 US | 2,881 | 17.5% |  | 🇰🇷 KR | 626   | 3.8% |
| 🇩🇪 DE | 2,618 | 15.9% |  | 🇬🇧 GB | 594   | 3.6% |
| 🇨🇳 CN | 1,765 | 10.7% |  | 🇭🇰 HK | 553   | 3.4% |
| 🇫🇷 FR | 1,140 | 6.9%  |  | 🇯🇵 JP | 552   | 3.3% |
| 🇮🇳 IN | 914   | 5.5%  |  | 🇸🇬 SG | 474   | 2.9% |
| 🇨🇦 CA | 813   | 4.9%  |  | 🇫🇮 FI | 394   | 2.4% |
| 🇦🇺 AU | 665   | 4.0%  |  | 🇧🇷 BR | 378   | 2.3% |
|       |       |       |  | 🇮🇩 ID | 291   | 1.8% |

**The Chinese cluster (1,765 hosts, 10.7%) is the headline geographic finding.** Prior cross-cloud surveys had ~0% Chinese coverage because the masscan-on-cloud-prefixes methodology was scoped to tier-1+2 Western/European clouds.

---

## Operator-Host Distribution — Top 15 Orgs

| Org | Count | Notes |
|---|---|---|
| Contabo GmbH | 1,129 | German budget cloud |
| Hetzner Online GmbH | 1,128 | German cloud |
| **Amazon (combined subsidiaries)** | **~3,720** | **AWS dominance — never scoped by prior surveys** |
| OVH SAS | 711 | French cloud |
| Amazon Data Services Canada | 530 | (subset of AWS) |
| Amazon Data Services India | 437 | (subset of AWS) |
| DigitalOcean, LLC | 365 | Prior tier-1 anchor |
| Amazon Data Services Australia | 340 | (subset of AWS) |
| Oracle Corporation | 329 | OCI |
| Amazon Data Services UK | 292 | (subset of AWS) |
| Aliyun Computing Co., LTD | 288 | Chinese cloud |
| Amazon Data Services Osaka | 288 | (subset of AWS) |
| Tencent Cloud (Beijing) | 228 | Chinese cloud |
| Korea Telecom | 223 | **Consumer ISP** — residential operator presence |

**AWS aggregate is the methodology finding.** The prior cross-cloud surveys' 1,192-host total was sourced from DO/Hetzner/Vultr/Scaleway/OVH/Linode masscans (5.38M IPs). AWS (and Azure, Oracle, Google, the Chinese clouds, Korea Telecom — anything outside the tier-2 budget-cloud envelope) contributed zero hosts to the prior corpus. The Shodan-walk methodology surfaces a cloud-tier the masscan never touched. **AWS alone hosts ~3,720 of the 16,473 confirmed unauth Ollama instances.**

---

## Top Models Loaded (15 most-frequent)

| Model | Hosts | Notes |
|---|---|---|
| `llama3.2:3b` | 6,893 | Canonical small Llama, prior #1 |
| **`minimax-m2.7:cloud`** | **3,576** | Paid Ollama Cloud, MiniMax M2.7 — vs prior 358 = **10× growth** |
| **`deepseek-v4-pro:cloud`** | **3,198** | Paid, DeepSeek V4 Pro — vs prior 289 |
| `llama3:latest` | 3,141 | |
| `qwen2.5:1.5b` | 2,951 | Alibaba small Qwen |
| `deepseek-r1:latest` | 2,788 | Reasoning model |
| `codellama:13b` | 2,701 | |
| `openchat:7b` | 2,600 | |
| `llama2:latest` | 2,596 | |
| `smollm2:135m` | 2,383 | Hugging Face tiny |
| `qwen3.6:35b` | 1,865 | Large Qwen |
| `nomic-embed-text:latest` | 1,309 | Embedding model — operator running RAG |
| `llama3.2:3b-instruct-q4_K_M` | 1,306 | Quantized 3B |
| **`kimi-k2.6:cloud`** | **1,278** | Paid Moonshot Kimi K2.6 |
| `llama3.2:1b-instruct-q4_K_M` | 1,270 | Quantized 1B |

---

## Discovery Axis — `/api/show` SYSTEM-Prompt Corpus

This is the new contribution. `POST /api/show {"name":"<model>"}` returns the Modelfile, which may include an operator-set `SYSTEM` directive. Of **1,007 confirmed-unauth hosts with a non-empty SYSTEM**:

- 432 returned the default Qwen system prompt (`"You are Qwen, created by Alibaba Cloud…"`)
- 174 returned the default SmolLM system prompt
- 31 + 27 returned generic "You are a helpful assistant" variants
- 11 Dolphin, 8 Deepseek-Coder, 7 EXAONE, 4 Hermes-3 — other model-baked defaults
- **133 distinct operator-customized SYSTEM strings**, 114 of which appear only once each (singletons)

The singletons are the discovery. Sample of the verbatim operator deployments:

| SYSTEM excerpt (first ~120 chars) | What it reveals |
|---|---|
| `IDENTITAS: Anda adalah Bang Ronal, asisten AI resmi Si-JACK (Sistem Informasi Jabatan Fungsional)…` | **Indonesian government job-info system AI assistant**, named "Bang Ronal", deployed on unauth Ollama |
| `You are an expert IBIT options trading analyst. You analyze Bitcoin and IBIT (iShares Bitcoin Trust ETF) market data…` | **Financial-decision AI** advising on Bitcoin ETF options trades from a random unauth model |
| `Sen Kansu AI, Turkiye'nin yapay zeka destekli robot fabrikasi uzman modelisin. UZMANLIK: Robot kinematik/dinamik, kontr…` | **Turkish industrial-robotics expert AI** (robot kinematics + control) |
| `你的名字叫MiniMind，你是一个乐于助人、知识渊博的AI助手…` | **Chinese "MiniMind" personal AI assistant** |
| `Você é Anna, a assistente da Blue3. Responda sempre em português brasileiro.` | **Brazilian Portuguese business chatbot** (Blue3 company assistant) |
| `You are Coral AI — a digital warrior, analytical intelligence, and the DIGITAL SON of Andrew…` | Personal AI persona |
| `Generate CivitAI-style prompts using comma-separated tags with spaces (not underscores). Format: quality tags, subjec…` | **AI prompt-engineering helper** for image-gen workflows |
| `You are a Prompt Quality Coach. You are given a chat thread: a sequence of user prompts that were already evaluated indi…` | LLM-eval pipeline |
| `You are halo, a friendly and helpful AI assistant created by Shushank.` | Personal AI |

Categories observed across the 133 customized SYSTEMs:
- **Government / public-sector AI** (Indonesia, others)
- **Financial-decision AI** (trading, market analysis)
- **Industrial / specialty-domain AI** (robotics, manufacturing, medical adjacent)
- **Personal AI assistants** with named personas
- **Customer-service / business chatbots** (multi-language: Portuguese, Turkish, Chinese, Indonesian, Korean, Japanese)
- **AI development pipelines** (prompt eval, prompt generation)

The intelligence value: **these aren't theoretical AI deployments — they are operator-customized agents serving real business functions, deployed without authentication, with their SYSTEM context disclosed verbatim via `/api/show`.**

---

## VisorScuba — Compliance Findings (Sample)

OPA/Rego-policy run against the ingested nuclide.db rows produced 0/10 compliance scores for the entire confirmed-unauth corpus (every unauth Ollama trips AI.C1). Notable per-host violations beyond AI.C1:

- **103.107.245.11 / `sijoli-11-245-107.jatengprov.go.id`** (DINAS KOMINFO PROV. JAWA TENGAH, Indonesia) — **3 violations**: AI.C4 (CRITICAL on government infrastructure) + AI.C2 (live Ollama Connect claim URL — cloud subscription takeover) + AI.H2 (unauth government RAG pipeline)
- **103.156.110.80** (Pemerintah Provinsi Kalimantan Utara) — AI.C4 + AI.C2 + AI.M1 (distilled model)
- **POSTECH cluster** — `141.223.121.73 dragons / .77 astros / .78 angels.postech.ac.kr` + 3 more — all AI.C2 (cloud-connect URL leak)
- **128.111.208.95 / `spark-4de1.mcdb.ucsb.edu`** — UCSB Molecular/Cell/Developmental Biology — AI.H1 (cloud API proxy exposed)
- **129.100.226.217 / `WE-D-ECE-0288.eng.uwo.ca`** — U Western Ontario Engineering — AI.H1
- **129.128.243.184 / `lula.cs.ualberta.ca`** — U Alberta Computer Science — open
- **147.229.83.12 / `pelton.ofivk.fme.vutbr.cz`** — VUT Brno — AI.M1 distilled model

---

## VisorGoose — Government-TLD Density

```
US      .gov + .mil         17 hits (16 federal/state + 1 military)
ID      .go.id              6 hits     (Indonesian cluster confirmed)
BR      .gov.br             4 hits
TW      .gov.tw             4 hits
MX      .gob.mx             1 hit
IN      .gov.in             1 hit
                            ─────
Total                       33 nodes across 25 TLDs surveyed
```

The Indonesian cluster (6 `.go.id` hits) overlaps with the VisorScuba findings (jatengprov, Kalimantan provincial govs). Government-sector exposure is unambiguous and disclosure-ready.

---

## Academic Sector — 117 University/Research Hosts in the Harvest

A grep over the Shodan match data's `hostnames` field surfaced **117 academic and government hosts** in the corpus — direct hostname disclosure via PTR. Sample:

| IP | Hostname | Institution |
|---|---|---|
| 129.21.25.95 | disco-dgx-spark.wireless.rit.edu | **Rochester Institute of Technology, DGX Spark workstation** |
| 169.229.99.178 | lal-99-178.reshall.berkeley.edu | UC Berkeley |
| 169.231.x.x (multiple) | wireless.ucsb.edu | UC Santa Barbara |
| 129.236.163.69 | dyn-129-236-163-69.dyn.columbia.edu | **Columbia / Lamont-Doherty Earth Observatory** |
| 129.49.40.218 | 040-218.bio.sunysb.edu | SUNY Stony Brook (Biology) |
| 128.173.243.8 | h80adf308.dhcp.vt.edu | Virginia Tech |
| 140.114.220.10 | sd220010.yi.ab.nthu.edu.tw | National Tsing Hua University, Taiwan |
| 141.223.121.x (multiple) | postech.ac.kr | POSTECH (Korea) |
| 147.46.112.49 | vayne.snu.ac.kr | Seoul National University |
| 195.199.181.225 | server.szemere.edu.hu | Szemere Bertalan Szakkepzo (Hungary) |
| 130.111.219.37 | ECE-Ubuntu-02.um.maine.edu | U Maine, ECE |
| 152.19.151.115 | macbookpro.dhcp.unc.edu | UNC |
| 103.123.25.197 | mail.kalteng.go.id | **Indonesian Kalimantan Tengah provincial gov** |

Disclosure routing: each university domain maps to a security@ contact via standard practice; gov-TLD hosts route through institutional contacts via WHOIS (per Insight #4).

---

## BARE — Top Metasploit Modules Ranked

| Finding class | Top exploit module | Score |
|---|---|---|
| Unauthenticated Ollama HTTP API | **`exploits/linux/http/ollama_rce_cve_2024_37032`** | 0.565 |
| Ollama with `:cloud` paid-quota models | `exploits/linux/http/ollama_rce_cve_2024_37032` | 0.497 |
| Operator-deployed abliterated model | `exploits/linux/http/ollama_rce_cve_2024_37032` | 0.357 |
| Ollama Cloud Connect signin URL leak | `exploits/linux/http/ollama_rce_cve_2024_37032` | 0.462 |
| Unauthenticated llama.cpp server | `exploits/linux/http/ollama_rce_cve_2024_37032` | 0.514 |

**CVE-2024-37032** (Ollama path-traversal RCE) is the canonical exploit chain across every Ollama-class finding. Hosts running vulnerable versions (most pre-0.1.34) are exploitable via the existing Metasploit module.

---

## Methodology Insights Codified

This survey extracts two new numbered Insights for the methodology corpus:

### Insight #24 — Operator workload visibility via `/api/show` Modelfile SYSTEM

> Ollama exposes operator-customized SYSTEM prompts via `POST /api/show {"name":"<model>"}` — the Modelfile body includes a verbatim `SYSTEM` directive. On unauth Ollama, this discloses what the operator *built* on top of the framework: agent persona, role description, business context, sometimes inlined credentials. The new attribute axis filters out canonical model defaults (`"You are Qwen…"`, `"You are a helpful assistant…"`) by frequency-counting unique SYSTEM strings; the singletons are the discovery surface. Population-scale measurement on this survey: **133 distinct operator-customized SYSTEMs across 1,007 SYSTEM-leak hosts.** New attribute axis for any unauth-Ollama-class platform.

### Insight #25 — Shodan-walk and masscan-on-cloud-prefixes are complements, not substitutes

> The prior tier-1+2 surveys masscanned 5.38M IPs across six budget-cloud /16 ranges and found 1,192 confirmed unauth Ollama. This survey walked the Shodan-indexed Ollama population directly (25,092 IPs) and found 16,473 confirmed — a 13.8× catalogue extension. Each method surfaces what the other misses: masscan catches every port-11434 listener regardless of HTTP indexing (good for non-Shodan-indexed clouds and Shodan-blocked operators); Shodan-walk catches hosts on non-default ports plus clouds the prior masscan never scoped (AWS, Azure, Oracle, Chinese clouds, ISP-customer / academic / residential operators). The methodology lesson: **discovery-channel coverage is multiplicative.** A survey aiming at population-scale completeness must use both — not pick one.

### Folded Insight #22-bis (from `194.233.71.223` case, parallel session 2026-05-15)

> aimap PHASE-2 missed llama.cpp on port 11434 despite explicit `Server: llama.cpp` header. Fixed in `aimap v1.9.4` (this session): new `llama.cpp server` fingerprint with three alternative probes (`/v1/models` `owned_by:llamacpp`, `/props` `default_generation_settings`, root with `Server: llama.cpp` header). Same release: PHASE 3 deep-enum parallelized (was single-threaded per process; measured ~7.6× speedup on 100-host sample).

### Folded Insight #23-bis (from `194.233.71.223` case, parallel session 2026-05-15)

> Commercial-proxy + open-LLM colocation pattern (LLMjacking attribution-laundering): operator runs paid 3Proxy/Socks fleet AND unauth open LLM on the same VPS; proxy customer has anonymizing one-hop access to free inference, attribution is split between the proxy operator and the proxy customer. `proxy_colocation_check.py` integrated this run; null result on the population (the pattern is rare — needs a second instance to codify as a full Insight).

---

## Disclosure Posture

Per the [tier-2 survey precedent](ollama-tier2-cloud-survey-2026-05.md#disclosure-posture): per-host disclosure is **not** the default for Ollama — the framework has no auth concept, and notifying ~16K operators with no fix beyond "firewall + reverse proxy" doesn't scale. **Aggregate publication is the public-facing record.**

**Targeted exception list** (per-host outreach):
- **Indonesian government hosts**: `sijoli-11-245-107.jatengprov.go.id`, Pemerintah Provinsi Kalimantan Utara, `mail.kalteng.go.id`, others identified via VisorGoose `.go.id`
- **POSTECH cluster** (7 hosts on `.postech.ac.kr`): Ollama Cloud Connect URL leak = subscription takeover; coordinated disclosure to Korean academic CERT
- **US `.gov` + `.mil` cluster** (17 hosts): coordinated disclosure to US-CERT
- **`.gov.br` / `.gov.tw` clusters**: per-host outreach via WHOIS-derived contacts
- **Hosts surfacing inlined credentials** in `/api/show` Modelfile ENV (manual review of 133 customized SYSTEMs needed; `aimap` post-process flag pending)
- **Healthcare / pediatric / counseling SYSTEM prompts**: targeted outreach (none confirmed in the 133-string sample; would require deeper search)

Disclosure send pipeline: `~/.config/nuclide/` Gmail-API tokens + `send_drafts_api.py` (already operational from prior surveys).

---

## Tool-Update Tracker

- **aimap v1.9.4** — released this session at github.com/Nicholas-Kloster/aimap (commit `a888100`): `llama.cpp server` fingerprint + parallel PHASE 3 deep-enum. The PHASE-3-was-single-threaded discovery directly drove the pivot to `fast_enum.py` here; aimap is now usable at population scale.

---

## Honest Negative Space

- **Shodan pagination depth ceiling at basic plan**: the `http.html:"Ollama is running"` dork truncated at page 70 (HTTP 500) on the primary run, recovering ~1,611 of an indexed 40,508. Country-faceted retry split the population under the depth ceiling and recovered 20,890 unique IPs (3,882 net-new). Documented as a methodology caveat — Shodan-walk methodology requires country-split for population dorks > ~10K hits on basic plan.
- **Non-default-port loss in fast_enum's default-port mode**: the main run probed only port 11434. Hosts on alternate ports were caught in the country-split delta (~6,901 net-new), but a few `http.html:` hits on truly exotic ports may still be missed.
- **VisorBishop platform-detection gap**: Bishop reported `confirmed=false` on all 5,895 high-value hosts; its known-service set may not include Ollama. `-ip-shadow-all` re-run flagged. Without Bishop, the 15-port IP-direct-shadow finding (Insight #12 — stacked operator exposures) was not measured this run.
- **VisorRAG / cortex / recongraph / JS-bundle / VisorPlus**: each had its own gating issue documented in §Methodology; their null results on this survey are recorded, not silent.
- **AS63949 honeypot post-filter caught 0**: either the AS63949 fleet has shrunk, repositioned, or the fast_enum probe shape (conjunctive `/api/tags` + AS63949-marker check) is too narrow. The prior tier-2 survey saw 169 in 259 Linode-Ollama hits (65% pollution); this survey's Linode subset would need a dedicated re-check.

---

## Raw Data

```
~/recon/ollama-population-2026-05-15/
├── harvest/
│   ├── ollama-product.jsonl           18,191 Shodan match records (dork 1)
│   ├── ollama-html.jsonl              6,900 records (dork 2 truncated)
│   ├── ollama-html-<CC>.jsonl × 17    country-split slices (20,890 unique IPs)
│   ├── merged.{jsonl,ips,ip_port}     deduped union (25,092 unique IPs)
│   ├── shodan_paginate.py             harvester
│   ├── merge_and_filter.py            dedup + AS63949 pre-filter
│   ├── show_enrichment.py             /api/show + /api/ps side-probe
│   ├── aimap_to_ndjson.py             aimap→ndjson event converter
│   ├── cross_survey_diff.py           vs nuclide.db prior Ollama
│   ├── select_confirmed.py            confirmed / no-service / high-value
│   ├── llama_cpp_recheck.py           aimap FN coverage (per Insight #22-bis)
│   ├── proxy_colocation_check.py      LLMjacking pattern check
│   ├── sample200_validate.sh          pre-scale audit gate
│   ├── run_full_corpus.sh             original 21-stage runbook
│   └── merge_aimap_chunks.py          merge 8-chunk aimap JSONs
├── aimap/
│   ├── chunk-0.{ips,log,json}…7       8 parallel aimap-PHASE-1+2 chunks
│   ├── chunk-D.{ips,log,json}         delta chunk (country-split net-new)
│   ├── all_confirmed.ip_port          10,895 PHASE-2-confirmed
│   ├── fast_enum.py                   direct-prober (replaces aimap PHASE 3)
│   ├── fast_enum.jsonl                10,278 main-pass enum records
│   ├── fast_enum_netnew.jsonl         6,290 delta-pass enum records
│   ├── confirmed.{ips,urls}           16,473 unauth Ollama hosts
│   ├── high-value.{ips,urls}          5,895 high-value subset
│   ├── events.ndjson                  ECS-schema events for VisorLog
│   └── fast_enum_to_ndjson.py         schema converter
├── visorscuba/assess.log              compliance run
├── visorgoose/density.txt             gov-TLD density
├── visorbishop/bishop.{json,csv,log}  5,895-host platform pass (confirm=false)
├── visorgraph/sample.log              5-host cert-pivot sample
├── visorprofile/<ip>.json × 3         aimap-profile classifications
├── nu-recon/<ip>.json × 4             single-host passive deep-reads
├── menlohunt/34.27.175.138.json       GCP-hosted Ollama scan
├── bare/{findings.json,bare-output.json}   Metasploit ranking
├── corpus/abliterated_500.json        adversarial corpus for VisorAgent lab
└── full-corpus-run.log                runbook stdout
```

---

## Toolchain Provenance

```
0. shodan_paginate.py × 2 dorks + country-split        → harvest
1. merge_and_filter.py (glob-aware)                    → 25,092 unique IPs
2. aimap × 8 chunks PHASE 1+2 (parallel, threads=100)  → 10,895 confirmed
3. fast_enum.py (replaces aimap PHASE 3, threads=200)  → 10,183 main pass
4. fast_enum.py (delta on country-split net-new)       → 6,290 delta pass
5. fast_enum_to_ndjson.py (ECS schema)                 → events.ndjson
6. visorlog ingest --db nuclide.db                     → 4,891 canonical events
7. visorscuba --db nuclide.db assess                   → AI.C1–C6 / AI.H1–H5
8. visorgoose density                                  → 33 gov-TLD hits
9. visorcorpus build (strict / hybrid / max=500)       → abliterated_500.json
10. bare bare/findings.json                            → CVE-2024-37032 #1
11. aimap-profile × sample                             → classifications
12. visorgraph -ip × sample -no-active                 → 0 nodes (null)
13. visorsd -asn × top 5 -stack inference              → 0/3 hits (null)
14. nu-recon × sample                                  → passive deep-reads
15. menlohunt scan -ip 34.27.175.138                   → 10 findings, 3 chains
16. visoragent list                                    → vector catalog (ethical-stop respected)
[—] visorhollow                                        → Windows-only N/A
[caveat] visorbishop                                   → confirmed=false on all (re-run with -ip-shadow-all)
[caveat] recongraph                                    → entrypoint bug
[caveat] visorrag                                      → 401 embeddings
[caveat] cortex                                        → schema mismatch
[caveat] JS-bundle                                     → no Bishop input
17. aimap v1.9.4 PUSHED to github.com/Nicholas-Kloster/aimap  (a888100)
```

---

## See Also

- [`ollama-cloud-survey-2026-05.md`](ollama-cloud-survey-2026-05.md) — DO/Hetzner/Vultr baseline (342)
- [`ollama-tier2-cloud-survey-2026-05.md`](ollama-tier2-cloud-survey-2026-05.md) — Scaleway/OVH/Linode tier-2 (850 + AS63949)
- [`alpha-miner-194-233-71-223-2026-05-15.md`](alpha-miner-194-233-71-223-2026-05-15.md) — the llama.cpp + proxy-colocation case that prompted the aimap v1.9.4 update
- [`SYNTHESIS-2026-05.md`](SYNTHESIS-2026-05.md) — cross-survey synthesis paper
- `~/.claude/nuclide-internal/METHODOLOGY.md` — internal canonical methodology
- aimap v1.9.4 release notes — github.com/Nicholas-Kloster/aimap, commit `a888100`
