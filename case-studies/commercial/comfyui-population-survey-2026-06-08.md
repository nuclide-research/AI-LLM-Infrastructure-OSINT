---
type: survey
category: generative-ai-workflow-ui
platform: comfyui
date: 2026-06-08
researcher: NuClide Research
predecessor: comfyui-cloud-survey-2026-05.md
---

# ComfyUI Default-Port Population Survey: 186 Unauth Hosts, 6.6 TB VRAM

_NuClide Research · 2026-06-08_
_Predecessor: [`comfyui-cloud-survey-2026-05.md`](comfyui-cloud-survey-2026-05.md)_

---

## Summary

Population-scale Shodan survey of ComfyUI on default port 8188, the AI image-synthesis node-graph UI shipped by `comfyanonymous/ComfyUI`. The platform has **no authentication concept** — there are no auth config flags in the framework, no master key, no built-in basic-auth. Any operator who exposes `--listen 0.0.0.0` is exposing every endpoint.

**Headline numbers.** 808 unique IPs harvested from Shodan dork `http.title:"ComfyUI" port:8188` (821 total per API). 240 responded on :8188 (Shodan cache decay 70%, matching Insight #77). Of the 240 live, **186 returned the strict `/system_stats` marker without auth — 77.5 percent of LIVE ComfyUI on the default port is unauthenticated.** 29 hosts (12 percent) returned 401, i.e. an operator-deployed reverse proxy or basic-auth wrapper. The remaining ~10 percent were 4xx/5xx/non-JSON FPs.

**Exposure metrics.** 6,655 GB of total VRAM and 23,848 GB of RAM exposed across the 186 confirmed hosts. 15 hosts expose more than 80 GB VRAM each. The top compute-theft target is a single Chinese host (`113.240.68.47`, China Telecom Hunan) running an **8× NVIDIA A100-SXM4-80GB cluster, 634 GB combined VRAM**. The next ring includes NVIDIA H200 NVL, H20, GH200 480GB (two on Lambda Labs commercial GPU cloud), and multiple Blackwell-class RTX PRO 6000 workstation cards — several on residential ISPs (Comcast VT, Telecom Italia FTTx, Korea Telecom KORNET, China Telecom, China Unicom).

**Method-shift result (Insight candidate).** The 2026-05-04 predecessor survey used masscan across 76 tier-2 cloud /16s plus 25 Hetzner /16s — roughly 5.25 million IPs sent SYN packets — and confirmed **6** unauthenticated ComfyUI instances. This survey, a passive Shodan API call plus 808 individual HTTP probes, confirmed **186** — a 31× yield with zero broadcast scan packets. For platforms whose `http.title` string is uniquely indexable, passive-Shodan dominates active-sweep at default-port scale.

<!-- ksat-tag:auto-generated:start -->
## DCWF KSAT coverage

Wardrobe outfit: `ai-infra-hunt`. NICE / DCWF KSATs exercised by this run:

- **672 (AI Test & Evaluation Specialist):** T5919 (adversarial testing in operationally realistic environment — the marker-probe step), T5904 / T5858 (per-host risk assessment), K7004 / K7044 (T&E frameworks / V&V tools = aimap-class probe), S7067 (low-prob / high-impact ML data risks — the GPU-compute theft surface).
- **733 (AI Risk & Ethics Specialist):** T5893 / T5882 (responsible AI practices — fingerprint-not-exfiltrate), T5904 / T5868 (lifecycle risk assessment).
- **NICE 541:** T0028 (authorized penetration testing), T0188 (audit findings + remediation), K0342 (pentest tools), S0001 / S0051 (vuln scan / pentest tools), T0247 (T&E verification), K0107 / K0118 (cross-jurisdiction posture, evidence preservation).

<!-- ksat-tag:auto-generated:end -->

---

## Methodology

```
Stage 0   Shodan API (live, 9282 query credits)
            dork = http.title:"ComfyUI" port:8188   → 821 total
            shodan download --limit 1000             → 808 unique IPs saved

Stage 0c  Verifier (verify.py) — 100-thread, 6s timeout, strict /system_stats
            require: HTTP 200 + JSON with top-level "system" AND "devices" keys
            honeypot pre-filter: AS63949 salt "wW0sffoqsk.EM" (0 hits)
            → 240 live, 186 unauthenticated, 29 auth-401, 17 FP, 8 4xx/5xx

Stage 2   Cert pivot on Lambda /24 (192.222.50.182 / .196)
            192.222.50.196 → CN=kemuri.top (operator domain on rented GPU box)
            /24 shadow scan :8188 → only 2/254 reachable (not a Lambda default)

Stage 3   WHOIS + rDNS attribution on top-15-VRAM hosts (manual)

Stage 6   VisorLog ingest → comfyui-2026-06-08.db (186 events)
```

**Read-only metadata only.** The methodology's restraint ethic is load-bearing on this category because the same endpoint that confirms identity (`/system_stats`) is one URL away from a `/prompt` submission that would consume operator GPU and write outputs to operator disk. The survey explicitly did *not*:

- submit any `/prompt` payload (no compute theft, no output writes),
- read `/history` contents (no prompt-text or output-image exfil),
- upload via `/upload/image`,
- download via `/view/<filename>`,
- enumerate `/object_info` per host (custom-node loadout, deferred per-disclosure).

Identity, version, GPU model name, and VRAM total were read from `/system_stats`. Names are the finding.

---

## Findings

### Distribution

| metric | value |
|---|---|
| Shodan total | 821 |
| Unique IPs harvested | 808 |
| Live on :8188 | 240 (29.7 %) |
| Confirmed UNAUTH | **186 (77.5 % of live)** |
| Auth-gated (401) | 29 (12.1 %) |
| Probe FPs / 4xx-5xx | 25 (10.4 %) |
| Total VRAM exposed | **6,655 GB** |
| Total RAM exposed | 23,848 GB |
| Hosts > 80 GB VRAM | 15 |
| Hosts > 40 GB VRAM | 46 |
| ComfyUI versions seen | 25+ (0.18 – 0.24 range) |

### Top-15 compute-theft fleet

| IP | VRAM | GPU(s) | Attribution |
|---|---:|---|---|
| 113.240.68.47 | 634 GB | 8× NVIDIA A100-SXM4-80GB | China Telecom Hunan (CN) — enterprise AI cluster on telco-residential range |
| 89.169.110.216 | 197 GB | CPU | Nebius FI (Yandex AI-cloud spinoff) |
| 103.180.163.218 | 140 GB | H200 NVL | HOSTGOI Technologies (IN) |
| 24.147.1.98 | 126 GB | CPU | Comcast Vermont residential cable |
| 206.168.190.15 | 126 GB | CPU | 1GSERVERS US bare-metal |
| 91.99.156.133 | 126 GB | CPU | Hetzner FSN1 (DE) |
| 173.208.175.148 | 125 GB | CPU | WholeSale Internet (US) |
| 87.31.88.253 | 122 GB | NVIDIA **GB10** (next-gen Grace Blackwell) | Telecom Italia FTTx residential |
| 165.246.44.113 | 120 GB | NVIDIA **GB10** | APNIC range (AU) |
| 117.50.47.140 | 95 GB | NVIDIA **H20** (China-export Hopper) | UCloud Shanghai (CN) |
| 14.36.217.167 | 95 GB | NVIDIA RTX PRO 6000 Blackwell Max-Q | Korea Telecom KORNET residential |
| 221.219.98.199 | 95 GB | NVIDIA RTX PRO 6000 Blackwell | China Unicom Beijing |
| 212.123.219.27 | 95 GB | NVIDIA RTX PRO 6000 Blackwell Max-Q | Multimedia Resources SL (ES) |
| 192.222.50.182 | 94 GB | NVIDIA **GH200 480GB** | Lambda Labs (US commercial GPU cloud) |
| 192.222.50.196 | 94 GB | NVIDIA **GH200 480GB** | Lambda Labs, leaf cert CN=`kemuri.top` |

The Lambda Labs pair is the standout for a commercial-tier finding: two enterprise-class GH200 systems on a major US GPU rental platform, neither auth-gated. The host at `.196` presents a Let's Encrypt cert with `CN=kemuri.top` — i.e. the operator's own domain on top of a Lambda-leased GPU. The substrate is Lambda, the deployment is the operator's; the exposure is the operator's responsibility, but Lambda's UX does not push operators away from `--listen 0.0.0.0`.

The residential-ISP cluster (Comcast, Telecom Italia, KORNET, China Telecom, China Unicom) is a distinct class: enterprise-grade GPUs deployed behind a home broadband NAT-passthrough or business cable, with no firewall in front of the ComfyUI HTTP listener. These are individual operators with no opsec running expensive AI hardware on the public internet.

### Version spread

ComfyUI versions observed range from 0.18 to 0.24. Top versions: 0.20.1 (18), 0.18.1 (17), 0.21.1 (12), 0.19.3 (11), 0.22.0 (10). Most operators stay within a few minor versions of upstream — no abandoned-deploy long-tail visible at this scale.

---

## Risk

ComfyUI's exposed endpoints constitute a stacked surface:

1. **Compute theft.** `POST /prompt` accepts an arbitrary workflow JSON for execution. Anyone on the internet who can reach :8188 can drive the operator's GPU, billed to the operator, with outputs written to the operator's disk.
2. **Workflow / prompt content disclosure.** `GET /history` returns the full history of completed jobs — the workflow JSON (operator's IP, model parameters, custom nodes used), prompt text, and the output filenames. For commercial operators this is product-IP-class disclosure.
3. **Generated-content access.** `GET /view/<filename>` reads any file produced or referenced by past jobs.
4. **Arbitrary file write.** `POST /upload/image` accepts arbitrary file content into the ComfyUI input directory.
5. **Custom-node code execution.** ComfyUI custom nodes are arbitrary Python imported at workflow time. An attacker who can submit a workflow referencing a known-vulnerable custom node (or who can upload a node via a chained vector) reaches arbitrary code execution on the host.
6. **System reconnaissance.** `GET /object_info` returns the entire installed custom-node manifest — operator fingerprint, model files referenced, and CVE-mapping surface.

Severity per finding: **critical** when VRAM ≥ 80 GB (enterprise compute on offer to the public), **high** when a CUDA device is present at any VRAM tier, **medium** for CPU-only configurations (data exposure still applies, compute-theft surface limited).

The platform-level fix is unavailable: ComfyUI ships with no auth abstraction. The operator-level fix is a reverse proxy (nginx + basic-auth, Cloudflare Access, Tailscale) — exactly what the 29 auth-401 hosts in the population have already deployed.

---

## Toolchain provenance

```
shodan count "http.title:\"ComfyUI\" port:8188"        →  821
shodan download comfyui-8188 ...                       →  808 IPs
verify.py (Python urllib + ThreadPoolExecutor, 100 wk) →  186 confirmed
dig + whois (top-15 attribution)                       →  named operators
openssl s_client (Lambda /24 cert pivot)               →  CN=kemuri.top
visorlog --db comfyui-2026-06-08.db ingest             →  186 events
```

Wardrobe outfit: `ai-infra-hunt` (T0028 / T0188 / K0342 / S0001 / S0051 / T0247 / K0107 / K0118).
Syllabus context: PoisonedRAG (USENIX '25), RAG-Extraction Dual-Path Runtime Integrity, Topic-FlipRAG — adjacent generative-AI threat literature (image-workflow analog).

---

## Insight candidate

**Passive Shodan beats active broadcast scan by 31× for title-indexable platforms.** When `http.title` carries a uniquely identifying string, the Shodan crawler has already populated the answer set; an active-scan reconstruction across millions of IPs produces a strict subset because (a) it only covers the cloud /16s in scope, and (b) Shodan's crawl reaches behind some operator firewalls that block masscan-class probes. ComfyUI 2026-05-04: masscan over 5.25M IPs ⇒ 6 unauth. ComfyUI 2026-06-08: Shodan title dork + 808 HTTP probes ⇒ 186 unauth. Same platform, same auth posture, 31× findings.

Promote when a second title-indexable platform reproduces the ratio.

---

## Honest negative space

- Default port 8188 only. The 176,140-host alt-port population (cloud GPU rentals: RunPod proxies, Vast.ai, Modal, Replicate-staging) is *not* in this survey. That sample dwarfs default-port by 215× and almost certainly contains a larger absolute count of unauthenticated instances; auth posture there depends on the cloud-provider proxy contract, not the operator. Sample-200 of the alt-port population is the next move.
- aimap has no ComfyUI fingerprint. `verify.py` is acting as the fingerprint here; a proper aimap enumerator + tome probe-config is owed.
- Honeypot pre-filter only checks the AS63949 salt. Other honeypot classes (gardiner.systems, Greynoise scanner-tagged ranges) are not cross-referenced in this run.
- No Censys cross-population delta yet (Step 0b). Free Platform tier credit budget allows 45 view-credits/week — 15 spent on the top-15 here would still leave headroom for next survey.
