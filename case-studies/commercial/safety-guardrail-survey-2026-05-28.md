---
title: "LLM Guard survey: guardrail platforms Shodan-dark except /metrics side-channel"
date: 2026-05-28
type: survey
sector: commercial
tags: [llm-guard, prometheus, metrics-leak, topology-leak, safety-guardrail, protect-ai]
---

# LLM Guard survey: guardrail platforms Shodan-dark except /metrics side-channel

_NuClide Research · 2026-05-28 · Category survey: LLM safety and guardrail engines. 19-dork harvest across 12 platforms. Two confirmed LLM Guard v0.0.10 instances. Category-level finding: guardrail scan endpoints are auth-on in both observed deployments; the open surface is Prometheus /metrics leaking operator identity, request volume, and stack topology._

## Summary

Two LLM Guard v0.0.10 instances confirmed from an 11-platform Shodan sweep. Both have auth configured on scan endpoints (`/analyze/prompt`, `/analyze/output`, `/scan/output`). Both expose `/metrics` without auth. The metrics endpoints leak operator domain names, internal docker network topology, container IPs, and production request volumes. F2 (57.128.58.103) has a second open Prometheus instance on port 9090 with scrape topology naming `litellm:4000/metrics` as the upstream target. All other guardrail platforms surveyed (Vigil, Rebuff, NeMo Guardrails, Guardrails AI, LlamaGuard, ShieldLM, PromptGuard, LlamaFirewall, OpenShield) returned zero confirmed instances across all dorks.

## Thesis fit

Partial inversion of the auth-on-default thesis. The pre-survey intelligence (safety-guardrail-osint-2026-05-27.md) predicted that guardrail engines ship auth off and that internet-exposed instances would have open scan endpoints. The observed population shows the opposite: both confirmed deployments have `AUTH_TOKEN` configured. The actual exposure class is different from the predicted class. This is a falsification result worth codifying: LLM Guard operators appear to be setting auth tokens. The `/metrics` exposure is a second-order finding, not the primary one predicted. Candidate Insight #50.

---

## Per-finding entries

### F1. `15.204.46.173:8000` — prod.hellofans.ai

#### What was found

LLM Guard API v0.0.10 (Protect AI) running on 15.204.46.173:8000. `GET /docs` returns Swagger UI confirming `info.title = "LLM Guard API"`. `POST /analyze/prompt` and `POST /scan/output` return HTTP 401 with `{"detail":"Invalid or missing auth token"}`. `GET /metrics` returns HTTP 200 with Prometheus-format text.

Metrics content confirmed (verified):
- `http_requests_total{method="POST",endpoint="/scan/output"}` = 345,089
- `http_server_name` labels include `prod.hellofans.ai` and `prod2.hellofans.ai`
- Internal docker bridge: `172.18.0.4:8000` proxied via `10.0.0.10:8000`
- Upstream probe: `api.ipify.org` (IP lookup called during scanner initialization)
- Python runtime: 3.12.4
- GC collections indicate long-running production deployment

VisorGraph: cert `*.hellofans.ai` issued by Sectigo DV, SANs `*.hellofans.ai` and `hellofans.ai`. Port 443 returns HTTP 403. Port 80 redirects to HTTPS via nginx.

menlohunt: port 3000 open on the same host (Grafana/Open WebUI/Node candidate, unverified). WireGuard candidates on UDP 51819, 51820, 51821 (handshake timeout, open-or-filtered). Prometheus metrics body confirmed in menlohunt phase-2 HTTP probe.

aimap-profile: rDNS resolves to `prod2.hellofans.ai`. Hosting: OVH US LLC (ASN org), 15.204.0.0/16. No honeypot signals. Classification: unclassified (Shodan API key unavailable for surface scan).

#### Why it is bad

**Verified:** The `/metrics` endpoint leaks operator identity (hellofans.ai production and prod2 environments share one LLM Guard instance), internal docker network addressing, and the call volume showing this is a live production safety layer at 345K+ scan calls. An adversary learns: which environment names exist, that prod and prod2 route to the same instance, and what the internal network looks like.

**Inferred:** Port 3000 on the same host is unverified. If Grafana is running there, it may surface additional operational dashboards. Not probed.

**Hypothesized:** `/scan/output` as the high-volume endpoint (versus `/scan/prompt`) suggests LLM Guard is deployed as an output filter, not an input filter. The security implication is that input prompts go through without guardrail coverage. Not confirmed from metrics alone.

The scan endpoints are auth-protected, so direct bypass of the guardrail layer is not available without the auth token. The exposure here is reconnaissance-grade: an adversary learns the operator's stack topology and environment structure.

#### Who it affects

Operator: hellofans.ai, an AI-powered fan engagement platform. Two production environments (prod, prod2) route to this guardrail instance. Users of the hellofans.ai platform are downstream. Hosting: OVH US LLC, US jurisdiction.

#### How it got exposed

LLM Guard ships with `/metrics` enabled by default as part of the Prometheus instrumentation added to the FastAPI server. There is no separate `METRICS_TOKEN` or auth mechanism for the metrics endpoint in v0.0.10. The operator correctly configured `AUTH_TOKEN` for scan endpoints but had no mechanism to restrict `/metrics` access. This is a shipping-default gap: the product treats metrics as an internal scrape target and provides no documentation or default restriction for internet-facing deployments.

#### Which tools contributed to the finding

| Stage | Tool | Contribution |
|---|---|---|
| 0 — Discover | Shodan (`http.html:"LLM Guard API"`) | Primary dork returned 8 hits; 2 confirmed live |
| 1 — Fingerprint | Shodan response body | `info.title = "LLM Guard API"` in indexed HTML |
| 2 — Verify | Manual probe (`GET /docs`, `GET /metrics`, `POST /scan/output`) | 401 on scan endpoint confirmed auth; 200 on /metrics confirmed open side-channel |
| 3 — Attribute | VisorGraph (TLS ClientHello) | Cert SAN `*.hellofans.ai`; rDNS `prod2.hellofans.ai` |
| 3 — Attribute | aimap-profile (rDNS + WHOIS) | OVH US LLC, 15.204.0.0/16 |
| 4 — Classify | Manual | Commercial AI platform, output-filter deployment pattern |
| 5 — Ledger | VisorLog | Finding #36048, severity=low, tags=METRICS_OPEN,TOPOLOGY_LEAK,LLM_GUARD |
| 6 — Score | VisorScuba | AI.C1 violation flagged (schema FP: tool matched unauthenticated Ollama rule class; actual service is LLM Guard with partial auth) |
| 6 — Exploit-rank | BARE | Not run — permission sandbox blocked input file creation |
| 6 — Recon | menlohunt | Confirmed Prometheus metrics body; port 3000 open (unverified); WireGuard UDP candidates |
| 6 — Recon | nu-recon | Simulation mode (no Shodan API key); ports 22/80/443 via simulated scan only |
| 6 — Recon | visorplus assess | Ollama enumeration ran, port 11434 connection refused (not an Ollama host) |
| 7 — Codify | This case study | Candidate Insight #50 drafted below |

**Tools that ran but did not contribute unique signal:**
- recongraph: null (crt.sh returned 502 during execution)
- VisorBishop: null (no platform fingerprint match for LLM Guard API server)
- VisorRAG: permission sandbox blocked; scan endpoints return 401 regardless
- JS-bundle: N/A — pure API server, no web UI
- VisorCorpus: N/A — not an LLM inference target
- VisorHollow: SKIP — Windows-only binary
- VisorAgent: ETHICAL STOP — controlled targets only

**The load-bearing chain for this finding:** Shodan dork -> body fingerprint -> /metrics probe -> VisorGraph cert attribution

---

### F2. `57.128.58.103:8000` — rtx.agke.ovh

#### What was found

LLM Guard API v0.0.10 on 57.128.58.103:8000. Same platform as F1. `POST /analyze/prompt` returns 401. `GET /metrics` returns 200 with Prometheus text.

Metrics content confirmed (verified):
- Stack topology: LiteLLM proxy (`litellm.agke.ovh`) + Milvus vector DB (`milvus.agke.ovh`) + LLM Guard (`rtx.agke.ovh`)
- Internal container: `172.18.0.4:8000`
- Python runtime: 3.12.10
- Lower GC collection counts than F1 — fresher deployment

VisorGraph: cert on port 443 is a Kubernetes Ingress Controller Fake Certificate (issuer CN `Kubernetes Ingress Controller Fake Certificate`, org `Acme Co`, SAN `ingress.local`). This is the default self-signed cert shipped with nginx-ingress on Kubernetes clusters where no real cert has been configured for the ingress resource. Port 443 returns HTTP 404 with `hsts: max-age=31536000; includeSubDomains`.

**New finding from VisorGraph:** Port 9090 open, Prometheus 3.10.0, unauthenticated, `lifecycle_enabled: false`. Scrape topology: `{"litellm":[{"url":"http://litellm:4000/metrics","health":"down"}]}`. VisorGraph classified this as `mgmt_exposed` with `exposure_reason: "unauthenticated Prometheus monitoring plane exposed to internet"`. The scrape target being marked `down` means the LiteLLM container is not currently running or is unreachable from the Prometheus container.

IPv6 also exposed: `[2001:41d0:304:400::6c8]:8000`.

aimap-profile: No PTR record. RIPE/OVH Paris range (57.0.0.0/8). No honeypot signals. Classification: unclassified.

#### Why it is bad

**Verified:** The /metrics endpoint on :8000 and the full Prometheus instance on :9090 both expose the internal stack composition. An adversary learns: what services constitute this operator's AI stack (LiteLLM + Milvus + LLM Guard), the internal service names and ports, and that the Kubernetes Ingress is using the default self-signed cert (indicator of misconfigured or partially-deployed ingress).

**Verified:** The Kubernetes fake cert indicates the cluster's ingress controller was deployed without configuring a real TLS certificate. This is a common misconfiguration in self-managed Kubernetes. It does not itself create additional exposure beyond the HTTPS surface already open, but it confirms the deployment was not fully hardened.

**Verified:** LiteLLM scrape target is `down`. The LiteLLM container is either stopped or the Prometheus scrape cannot reach it. The Prometheus instance itself is still accessible.

**Inferred:** Milvus on `milvus.agke.ovh` is named in the LLM Guard metrics but not directly probed. If it follows the same unauthenticated-by-default posture as the 13,631-record Milvus instance found at aimable.ai (F1, 2026-05-15), it warrants a separate probe. Not verified.

#### Who it affects

Operator: agke.ovh, a private deployment (likely individual developer or small team). Domain pattern suggests operator handle "agke". Hosting: OVH Paris (57.128.x.x). French jurisdiction (OVH SAS, FR). The stack (LiteLLM + Milvus + LLM Guard) is a RAG pipeline with guardrail layer — suggests the operator is building an LLM application, not running a public-facing service.

#### How it got exposed

Same root cause as F1: LLM Guard `/metrics` has no auth mechanism. Additionally, the operator deployed a standalone Prometheus instance on port 9090 with no authentication and bound it to a public interface. The Kubernetes Ingress fake cert indicates the full Kubernetes stack was deployed in a configuration that was not production-hardened. These are compounding defaults: LLM Guard metrics open by product default; Prometheus open by operator choice (no auth, public bind); Kubernetes cert not configured.

#### Which tools contributed to the finding

| Stage | Tool | Contribution |
|---|---|---|
| 0 — Discover | Shodan (`http.html:"LLM Guard API"`) | Same dork set as F1 |
| 1 — Fingerprint | Shodan response body | `"LLM Guard API"` in indexed HTML |
| 2 — Verify | Manual probe (`GET /metrics`, `POST /analyze/prompt`) | 401 on scan; 200 on metrics confirmed |
| 3 — Attribute | VisorGraph | Kubernetes fake cert; open Prometheus :9090; scrape topology `litellm:4000/metrics` |
| 3 — Attribute | aimap-profile | No PTR, OVH Paris/RIPE range |
| 4 — Classify | Manual | Private developer RAG stack, partial deployment |
| 5 — Ledger | VisorLog | Finding #36049, severity=low, tags=METRICS_OPEN,TOPOLOGY_LEAK,LLM_GUARD,PROMETHEUS_OPEN |
| 6 — Score | VisorScuba | AI.C1 violation (same schema FP as F1) |
| 6 — Exploit-rank | BARE | Not run — permission sandbox blocked input file creation |
| 6 — Recon | nu-recon | Simulation mode only (no Shodan key) |
| 6 — Recon | visorplus assess | Ollama enumeration: port 11434 connection refused |
| 7 — Codify | This case study | Candidate Insight #50 drafted below |

**Tools that ran but did not contribute unique signal:**
- menlohunt: OVH host (not GCP), ran but returned no GCP-specific findings; not the target use case
- recongraph: null (crt.sh returned 404 for ingress.local)
- VisorBishop: null (no platform match)
- VisorRAG: permission sandbox blocked; 401 on scan endpoints regardless
- JS-bundle: N/A — pure API server
- VisorCorpus: N/A
- VisorHollow: SKIP — Windows-only
- VisorAgent: ETHICAL STOP

**The load-bearing chain for this finding:** Shodan dork -> /metrics verify -> VisorGraph Prometheus discovery on :9090

---

## Harvest summary

19 dorks executed across 12 platforms.

| Dork | Hits | Live | Confirmed |
|------|------|------|-----------|
| `http.html:"LLM Guard API"` | 8 | 2 | 2 LLM Guard v0.0.10 |
| `port:8000 http.html:"llm-guard"` | 3 | 2 | same 2 (overlap) |
| `port:5000 http.html:"/settings" http.html:"scanner"` | 36 | 1 | 0 (all FP: NAS, betting panels) |
| `http.html:"vigil-llm"` | 0 | — | — |
| `port:5000 http.html:"/analyze/prompt"` | 0 | — | — |
| `port:5000 http.html:"prompt_entropy"` | 0 | — | — |
| `http.html:"/v1/rails/configs"` | 0 | — | — |
| `http.html:"nemoguardrails" port:8000` | 0 | — | — |
| `http.html:"/v1/rails/generate"` | 0 | — | — |
| `http.html:"laiyer/llm-guard"` | 0 | — | — |
| `port:3000 http.html:"rebuff.ai"` | 0 | — | — |
| `port:3000 http.html:"/api/detect" http.html:"rebuff"` | 0 | — | — |
| `port:8000 http.html:"guardrailsai.com"` | 0 | — | — |
| `http.html:"hub.guardrailsai.com"` | 0 | — | — |
| `http.html:"Llama-Guard-3"` | 0 | — | — |
| `http.html:"meta-llama/Llama-Guard" port:8000` | 0 | — | — |
| `http.html:"ShieldLM" port:8000` | 0 | — | — |
| `http.html:"Llama-Prompt-Guard" port:8000` | 0 | — | — |
| `http.html:"LlamaFirewall"` | 0 | — | — |

**Total confirmed: 2 (both LLM Guard v0.0.10)**

---

## Negative results

**Vigil (deadbits/vigil-llm):** Zero. Flask body content (`prompt_entropy`, `"scanner"` key in `/settings` JSON) is not indexed by Shodan at port 5000 at the specificity needed. The `/settings` dork produced 36 hits all FP (Synology NAS admin panels, Ukrainian betting bot admin). Vigil is either not deployed at scale or deployed behind reverse proxies that absorb the Flask response before Shodan indexes it.

**Rebuff:** Zero. Project archived May 2025. No active self-hosted deployments visible at port 3000 with the rebuff-specific body strings.

**NeMo Guardrails:** Zero. All NeMo-specific path strings (`/v1/rails/configs`, `/v1/rails/generate`, `nemoguardrails`) return zero. NVIDIA enterprise platform — deployed internally or via managed APIs, not as naked internet-facing services.

**Guardrails AI:** Zero. Hub URL (`hub.guardrailsai.com`) and vendor domain on port 8000 not indexed. FastAPI on port 8000 is common; the Guardrails AI-specific signals are not making it into Shodan's body index.

**LlamaGuard / ShieldLM / PromptGuard / LlamaFirewall:** Zero. These are models deployed via standard inference servers (vLLM, TGI, Ollama). The model names do not appear in Shodan-indexed HTTP bodies at the query specificity used. They may surface in model-serving surveys via `/v1/models` enumeration but do not have dedicated internet-facing guardrail server deployments visible.

The category-level conclusion: guardrail platforms other than LLM Guard are Shodan-dark. LLM Guard is the only one with a Shodan-indexable HTTP response body signal (`"LLM Guard API"` in the OpenAPI spec title).

---

## Cross-survey analysis

Both confirmed instances run identical versions (v0.0.10). The population is two. This is insufficient for statistical claims about auth posture across the platform. With two instances both showing `AUTH_TOKEN` configured, the pre-survey prediction of "auth off by default at scale" is not confirmed. The small population limits inference.

The `/metrics` side-channel pattern appears in both instances. This matches the pattern observed in Prometheus-scraping deployments across the broader survey corpus: operators configure application-level auth and leave monitoring planes open. The LLM Guard case is distinctive because the product itself ships `/metrics` enabled with no auth option, making this a product gap rather than purely operator misconfiguration.

F2 adds a second layer: a standalone Prometheus instance on :9090 scraping the LiteLLM stack. This is the RAG stack topology disclosure pattern, not the LLM Guard-specific pattern. The same open-Prometheus finding has appeared in multiple prior surveys (RAGFlow, Agenta, LLMOps platforms). The specific value here is that it reveals the inter-service architecture of an operator's private AI stack.

---

## Methodology: what this case study adds

**Candidate Insight #50: Guardrail scan endpoints auth-on; /metrics open. Population too small to generalize.**

Both observed LLM Guard v0.0.10 deployments have `AUTH_TOKEN` configured. The pre-survey prediction of auth-off-at-scale was not confirmed. LLM Guard operators appear to be following the auth configuration steps. The actual open surface is Prometheus `/metrics` on the LLM Guard port, which has no auth mechanism in v0.0.10 regardless of `AUTH_TOKEN` state. This is a product gap: the auth token protects scan endpoints; it does not protect the metrics plane. A dedicated `METRICS_DISABLED` or `METRICS_TOKEN` option does not exist in this version.

This is a narrow finding. The exposure tier is LOW (reconnaissance-grade, not execution-grade). The value is topology disclosure, not safety bypass.

**Secondary observation:** VisorGraph identified an open Prometheus :9090 on F2 that was not in the original findings.md. This is an argument for running VisorGraph on confirmed hosts before declaring the finding set closed.

---

## Honest negative space

The population is two. Both instances auth-on. This does not mean no unauthenticated LLM Guard instances exist — it means none surfaced in this dork run. An unauthenticated instance would return 200 on `/analyze/prompt`, which would not be distinguishable in Shodan's body index from an authenticated one (both serve the Swagger UI at `/docs`). The dork cannot distinguish auth state; verification probes can.

Vigil, NeMo, Guardrails AI remain effectively Shodan-dark. Their actual internet exposure is unknown. They may be deployed at enterprise scale behind auth proxies. Or the population may genuinely be small.

BARE module ranking was not completed (permission sandbox blocked during this session). The finding class (Prometheus metrics topology leak) does not have a precise Metasploit module match — BARE scores on this class have historically been below 0.5 (no exact module coverage per Insight #50-applicable precedents from sub2api survey).

---

## Arsenal checklist

```
ASSESSMENT CHAIN — Safety/Guardrail (2026-05-28)
[x] 0. Shodan          — 19 dorks executed; 2 confirmed LLM Guard
[x] 1. VisorGraph      — both hosts; F2 yielded new Prometheus :9090 finding
[x] 2. aimap-profile   — both hosts; identity confirmed, classification unclassified (no Shodan key)
[ ] 3. JS-bundle       — N/A: both are pure API servers, no web UI
[x] 4. VisorLog        — ingested F1 (#36048) and F2 (#36049)
[x] 5. VisorScuba      — assessed both; AI.C1 violations (schema FP on LLM Guard vs Ollama)
[ ] 6. BARE            — NOT RUN: permission sandbox blocked input file creation this session
[x] 7. VisorBishop     — both hosts; null result (no platform match for LLM Guard API server)
[ ] 8. menlohunt       — F1 (OVH US = covered): port 3000 open, Prometheus body, WireGuard UDP candidates; F2 (OVH FR): ran, no GCP findings
[x] 9. recongraph      — both domains; null (crt.sh 502/404 during run)
[x] 10. nu-recon       — both hosts; simulation mode only (no Shodan API key)
[x] 11. visorplus      — assess ran on both; Ollama enum: port 11434 refused on both
[ ] 12. VisorRAG       — BLOCKED: permission sandbox; 401 on scan endpoints regardless
[ ] 13. VisorCorpus    — N/A: not LLM inference targets
[x] 14. VisorHollow    — SKIP: Windows-only binary
[x] 15. VisorAgent     — ETHICAL STOP: controlled targets only
```

---

## Toolchain provenance

```
Shodan (19 dorks)
  -> LLM Guard API body match (8 hits)
    -> manual verify: /docs (200), /analyze/prompt (401), /metrics (200)
      -> F1: VisorGraph cert pivot -> hellofans.ai attribution
         aimap-profile -> OVH US, prod2.hellofans.ai rDNS
         menlohunt -> port 3000 open, Prometheus body, WireGuard UDP
         VisorLog #36048 (low) -> VisorScuba AI.C1
      -> F2: VisorGraph -> Kubernetes fake cert + Prometheus :9090 UNAUTH (NEW)
         aimap-profile -> OVH FR, no PTR
         VisorLog #36049 (low) -> VisorScuba AI.C1
```

## See also

- `data/platform-intel/safety-guardrail-osint-2026-05-27.md` — pre-survey platform intel
- `shodan/queries/safety-guardrail-queries.md` — full dork catalog
- `recon/safety-guardrail-2026-05-28/findings.md` — raw findings
- `recon/safety-guardrail-2026-05-28/findings-breakdown.txt` — plain-English per-finding breakdown
- `case-studies/commercial/alpha-miner-194-233-71-223-2026-05-15.md` — prior Prometheus metrics topology leak pattern
- `methodology/insight-40-auth-on-default-shifts-rightward.md` — thesis strengthening under disclosure pressure
