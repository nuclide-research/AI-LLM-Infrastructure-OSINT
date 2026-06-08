# NVIDIA NIM + Triton population survey

**Date:** 2026-06-08
**Lead:** NuClide Research
**Survey dir:** `surveys/nvidia-nim-2026-06-08/`
**Status:** **NULL FINDING — zero verified-exposed inference servers in the 314-candidate pool.** The narrowing collapses to honeypot + lifecycle-stale + cross-class FP.

## Summary

We ran the chain against NVIDIA's two flagship inference-serving products: NIM (`nvidia-nim`, `:8000`, OpenAI-compat) and Triton Inference Server (`triton-inference-server`, `:8000` / `:8001` / `:8002`). Both ship with `auth_default=none`. We expected a meaningful exposed-unauth population in line with vLLM (4 verified earlier) and SGLang (1 verified).

The actual finding is negative and important.

| layer | pop | what survived |
|---|---:|---|
| Shodan `http.title:"NIM"` | 138 | ~99 % unrelated "NIM" word hits (school-district Network Information Manager portals, NIM Licenses, Bak Nim, vue-nim-webrtc, Nim GPT, etc.) |
| Shodan `http.title:"NVIDIA NIM"` | 2 | 1 portal page ("Try NVIDIA NIM APIs", Beijing Volcano Engine demo), 1 product ("NVIDIA NIM 负载均衡器 v1.4.0" load balancer, Oracle) |
| Shodan `"nim-llm"` | 1 | 1 Azure host on port 5000, banner mention only |
| Shodan `http.html:"nvcr.io"` | 0 | tome dork tier-3, zero |
| Shodan `"triton-inference-server"` | 49 | **48 of 49** are AWS-hosted ClickHouse instances (host `3.106.251.165` alone contributes ~10 ports, 999 open ports on that host, scanner-honeypot signature) |
| Shodan `http.title:"Triton"` | 314 | filterable to 42 ip-pairs with title exactly "NVIDIA Triton Inference Server" |
| Active verify on those 42 | 42 | 1 honeypot (7 ports, same IP), 1 Synology DSM, 1 Plex Media Server, 39 hosts dead (IPs cycled). Real Triton population: **0** |

The chain produced a real finding: the shape of the trap, not an exposed inference server.

## Methodology — what the chain did

**Tome corpus check.** NVIDIA NIM is already covered in the tome platform corpus (sourced from `Generative AI on Kubernetes` ch01). Triton lives implicitly as the backend NIM wraps. Dork tiers pre-built (basic / strict / version).

**Shodan harvest.** Three NIM dork tiers returned 1 / 2 / 0. The `http.html:` filter cannot reach NIM's API surface — NIM exposes JSON on `/v1/*`, Shodan crawls `/`, and `/` on NIM has no HTML to match. This is the dork-population-substitution failure: `http.html:` is HTML-body-only on the web UI; JSON-only API endpoints are systematically excluded.

Variant expansion: 10 alternative dorks at round 1 (titles, banner strings, JSON markers). Only `http.title:"NIM"` (138) and `"triton-inference-server"` (49) returned meaningful counts. Both turned out to be false-positive-dominated.

**Censys.** Free tier with 100 credits remaining, held in reserve. The Shodan-dark thesis (NIM JSON API not surfaced via passive HTML dorks) is the same population-substitution failure on either index; spending Censys credits on the same axis was unlikely to break the pattern.

**Active liveness sweep.** Direct curl across all 69 ip:port candidates surfaced the lifecycle problem: 39 of 69 returned no response (000), meaning the IPs have cycled away since the Shodan crawl. AWS EC2 elastic IPs reassign frequently; the Shodan banner is a snapshot, not a contract.

**aimap.** Ran with `-scan-all-fingerprints` across the 68 discovered shadow ports. Produced empty report, consistent with `0 NIMs` (aimap's NIM fingerprint matches `/v1/models` and `nvcr.io` markers, neither present on these hosts).

**VisorGraph cert-pivot.** 338 probes across the 42 IPs surfaced two informative cert CNs: `priv-10.1.1.91` on `13.244.74.78` (internal IP as cert subject, Synology lifecycle artifact, matched `SentinelProtectionServer/7.3`) and `Gozargah` on `13.244.203.188` (the developer alias for Marzban, an Iranian-origin Xray/V2Ray panel; that IP now runs uvicorn, was advertising Triton title in the past).

**Verification — the load-bearing stage.** The honeypot finding came from a single structural test: identical-bytes-on-arbitrary-path. `15.161.228.100:5558` returns 2355 bytes of randomized HTML on `/v2/health/ready`, `/v2/models`, `/v2/whatever_garbage_path`, and `/`. Same content, different "random" strings each fetch. Real Triton returns: `200 OK` with empty body on `/v2/health/ready`, structured JSON `{"name":"triton","version":"..."}` on `/v2`, JSON list of model IDs on `/v2/models`, and `404` on garbage paths. This host is bait.

## The bait host — 15.161.228.100

- AWS Data Services Italy (AMAZON-MXP, AS16509)
- 7 ports advertised: 5558, 5858, 8908, 12108, 12508, 18108, 24808 — all titled "NVIDIA Triton Inference Server" in Shodan
- Body: randomized HTML with a stable favicon (`/favicon_17c62c5b-6450-4c61-a190-9ac65041fd01.ico`, 1078B) and a randomized content block of tag-soup (`h2.detail`, `pre`, `section`, `code.summary`, `article`, `aside`, etc.) full of base64-style random strings
- Server header: `Amazon-Cloud-Drive` (no relation to real Amazon Drive)
- Catchall: any request path that isn't `/v2` or `/favicon*` returns the same 2355B template
- `/v2` anomaly: returns 8 bytes `__schema` — the GraphQL introspection query name. Possibly a Hasura-shaped fallthrough, possibly a tracking marker the operator seeded. Either way, not Triton

Classification: a Triton-impersonation honeypot on a single AWS Italy IP across 7 ports. The bait HTML's role is to fool Shodan title scrapers into indexing the host as Triton; the favicon ID and the catchall behavior are the operator's fingerprint.

The 13.244.74.78 (Synology DSM cert CN `priv-10.1.1.91` + `SentinelProtectionServer/7.3`) and 13.244.203.188 (Plex Media Server on Windows 7) hits are lifecycle false positives — the AWS IP was hosting Triton at the moment of the Shodan crawl, has since been reassigned. Both are real services, neither is Triton.

## Candidate insights (numbered later if confirmed by another survey)

1. **NIM/Triton title dorks are honeypot-dominated.** `http.title:"NIM"` is 99 % unrelated word hits; `http.title:"Triton"` collapses to 1 single-host honeypot fleet after lifecycle-drop. The product-name-in-HTML-title dork has near-zero signal on this platform class.
2. **NIM is Shodan-dark by design.** OpenAI-compat APIs serve JSON, not HTML, at `/`. Shodan's default crawl reaches `/`, not `/v1/models`. The auth-on-default thesis is *unmeasurable* here through passive HTML indexing; only active probing on `/v1/models` would surface the population. Same likely true for vLLM, SGLang, TGI on canonical setup. Recall: vLLM/SGLang surfaced in earlier surveys via HTML titles when the Swagger `/docs` page was crawled — operator-dependent, not platform-default.
3. **"NVIDIA Triton Inference Server" title without other signal = lifecycle-cycled or honeypot.** Real Triton operators either (a) put auth in front, (b) silence the title via mass-config, or (c) the title-bearing hosts have been reassigned. The crawl snapshot lies; verification is load-bearing.
4. **One-host shadow-port fleets are bait, not a deployment.** `15.161.228.100` advertising on 7 high-numbered ports (5558, 5858, 8908, 12108, 12508, 18108, 24808) with identical content is honeypot signature. Real Triton deployments would have configuration drift across ports and would not give identical bodies on `/v2/health/ready` and `/v2/wrong_path`.

## What the chain did *not* yield

- No exposed NIM API
- No exposed Triton API
- No model-name enumeration
- No restraint event to log (nothing was reachable)
- No disclosure surface

The whole chain is the answer here. The negative result, with the bait signature documented, is the deliverable.

## Toolchain provenance

- **shodan CLI** with API key (9,069 credits remaining): 13 distinct dork variants run, all logged to `dork-counts.txt` + `dork-pivots.txt` + `dork-pivots-r2.txt`. Note: the `feedback_shodan_playwright_only` memory record incorrectly claimed both API keys were dead — verified live this session (`shodan info` returned 9,069 / 5,120 credits). Memory entry needs correction.
- **tome** (canonical platform corpus): NIM JSON confirmed, probe scaffold `GET :8000/v1/models` with marker `nvcr.io`
- **visorgraph** with `-rps 4`, 32 workers: 338 probes, 0 edges, 5 nodes after fixed-point — passive cert-pivot did not propagate (each host is an isolated island, no shared certs)
- **aimap** with `-scan-all-fingerprints -threads 12 -timeout 8s`: empty report, consistent with `0 NIM/Triton` (no `nvcr.io` markers, no `/v1/models` 200s)
- **curl** for the verifier sweep (66 lines in `verify-liveness.csv`): 39/69 = 000, 7/69 = bait, 4/69 = lifecycle FP (Synology), 1/69 = lifecycle FP (Plex)
- **whois** for the bait host AS attribution

## Files

- `dork-counts.txt` — 3 tome dork tier results
- `dork-pivots.txt` — 10 round-1 dork variants
- `dork-pivots-r2.txt` — 6 round-2 variants including Triton pivot
- `targets.txt` — 69 ip:port pairs harvested
- `ips.txt` — 42 unique IPs
- `ports.csv` — 68 unique shadow ports
- `nvidia-nim-strict.json.gz` — Shodan 2 NIM-title hits
- `nim-llm-strict.json.gz` — Shodan 1 nim-llm hit
- `triton-tight.json.gz` — Shodan 48 ClickHouse FP hits
- `triton-title.json.gz` — Shodan 312 Triton-title hits
- `title-NIM.json.gz` — Shodan 137 NIM-word hits
- `visorgraph.json` + `visorgraph.err` — cert-pivot run
- `verify-liveness.csv` — 69-row active probe sweep
