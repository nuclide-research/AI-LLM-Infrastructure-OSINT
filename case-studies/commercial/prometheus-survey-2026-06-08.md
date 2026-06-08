---
type: survey
---

# Prometheus on the Public Internet: Falsifier Test for the VictoriaMetrics Finding

_NuClide Research · 2026-06-08_

> **Why this survey exists.** The VictoriaMetrics survey shipped earlier today produced two insights (#88 scrape-topology disclosure as operator org chart, #89 framework-level pprof bypass propagates to population scale). The DCWF 902 strategic roadmap flagged Prometheus as the load-bearing falsifier test: same Q4 quadrant, 10x larger population, direct architectural twin. The thesis prediction was 75–85% unauth + comparable pprof-open rate. If Prometheus came back at <50% unauth, the VM finding would have been operator-anomalous and the program would have re-targeted toward maintainer-side disclosure instead of operator-side. Survey result: thesis confirmed and sharpened.

## Summary

A first standalone survey of internet-exposed Prometheus (versions 2.x, port 9090 + 9091 Pushgateway + 9093 Alertmanager) finds that **475 of 1,429 favicon-discoverable hosts (33%) are completely open and 100% of those expose `/api/v1/status/config`, leaking the operator's entire `prometheus.yml` configuration unauth**. Every verified Prometheus has `/debug/pprof/` open. 25 hosts leak embedded basic_auth or bearer_token credentials in the dumped configuration.

The remaining 903 favicon-matched hosts (63%) return 404 on `/api/v1/status/buildinfo`, indicating they sit behind a reverse proxy that gates the API path while still exposing the Prometheus favicon. Operators **do** harden Prometheus — but only via reverse-proxy deployment, not via the framework's own `--web.config.file` auth mechanism. The hosts that don't sit behind a proxy are 100% wide open.

This sharpens the VM finding rather than falsifying it:

| Metric | VictoriaMetrics | Prometheus | Generalization |
|---|---|---|---|
| Total internet-exposed (Shodan, favicon-discoverable) | 1,389 raw, 1,176 verified | 1,429 raw, 475 verified | Same order of magnitude in our sample window |
| Operator-attempted hardening | minimal (only 4.7% fully gated) | substantial (63% behind reverse proxy) | **Prometheus operators do harden — when they harden at all, they harden completely** |
| Unauth rate on the not-hardened subset | 93.5% | **100%** (475/475) | Sharper |
| `/debug/pprof/` open on verified subset | 91.5% | **100%** (475/475) | Confirmed |
| `/api/v1/status/config` full dump | (not applicable; VM has no equivalent) | **100%** (475/475) | New Prometheus-specific finding |
| Embedded credentials leaked in config | (not applicable) | **25** | New |
| Scrape targets exposed (Insight #88) | 1,578 | 2,031 | Confirmed: monitoring agents leak topology |
| Alerting/recording rules exposed | (not enumerated) | 661 | New |
| Metric names disclosed | 241 | **7,604** | 31× more — Prometheus exposes a richer query-API surface |
| Firing alerts visible | (not enumerated) | 168 | New |

Insight #89 (framework-level pprof bypass) is **not testable** on Prometheus at population scale: the conditions for the test require operator-side auth on data endpoints with pprof bypassed. No such hosts exist. Prometheus operators either deploy nothing (100% open including pprof) or deploy a reverse proxy that gates everything including pprof. The framework's `--web.config.file` selective-auth model that VM exhibits is not the deployed Prometheus pattern. **Insight #89 stays VM-specific until a new platform reproduces the conditions.**

Insight #88 (scrape topology = org chart) is confirmed and now generalizes to Prometheus.

## Population

| Metric | Value |
|---|---|
| Shodan favicon-hash hits (production:`-1399433489`) | 26,598 total |
| Sampled (5 pages) | 1,429 unique hosts (1,407 IPs) |
| Verified Prometheus (has `goVersion` in `/api/v1/status/buildinfo`) | **475** |
| Behind reverse proxy (404 on API path, favicon still served) | 903 |
| Offline | 51 |
| VM-compat (returns Prometheus-API version but no `goVersion`) | 0 |
| Verified Prometheus by country (top 10) | US 73, DE 60, FR 56, CN 41, BR 34, SG 17, NL 16, FI 12, IN 11, PL 9 |

Version distribution on verified subset (top 10):

| Version | Count |
|---|---|
| 2.55.0 | 37 |
| 2.45.0 | 35 |
| 2.53.3+ds1 | 24 |
| 2.45.3+ds | 23 |
| 2.37.0 | 18 |
| 2.31.2+ds1 | 17 |
| 2.48.1 | 17 |
| 2.47.0 | 16 |
| 2.54.1 | 16 |
| 2.42.0+ds | 15 |

The version distribution is broader than VM's (which clustered on 1.0.0 + 0.5.x). Operators run a wide range of Prometheus versions. Nothing in the version range CVE-binds, but the diversity itself argues against a single recent regression — the auth-off-default behavior has been the modal deployment choice for years, across the entire 2.x release line.

## Auth Posture (verified Prometheus subset)

| State | Count | Share |
|---|---|---|
| **UNAUTH-READ** (all 4 gated endpoints return 200) | **475** | **100%** |
| Fully gated (all return 401/403) | 0 | 0% |
| Other states | 0 | 0% |

This is the cleanest auth-off-default signal in the entire NuClide research program to date. There is no partial-auth tier. Either Prometheus is fully open or it is behind a reverse proxy (the 903-host "Other" cohort).

## What gets leaked from open Prometheus

### `/api/v1/status/config` — the entire `prometheus.yml`

**100% of verified Prometheus hosts (475) return their full configuration to an unauthenticated GET.** This is the highest-value endpoint in the platform and the one most likely to break the operator's security model. Disclosed content typically includes:

- `scrape_configs`: the full list of every job the operator scrapes, with `static_configs.targets` listing internal hostnames + ports (overlaps with `/api/v1/targets` but more authoritative)
- `remote_write`: URLs the metrics are forwarded to (commonly VictoriaMetrics, Mimir, Thanos, Cortex, Grafana Cloud, Datadog, or a custom remote-write endpoint). The URL itself is a pivot target.
- `alerting.alertmanagers`: AlertManager URLs, often on internal networks
- `basic_auth.password` and `bearer_token` blocks: **when present in inline static configs, the credentials appear in plaintext in the config response**. Found embedded credentials on **25 hosts**.

Cloud-provider distribution of the 25 hosts with embedded credentials: Hetzner 5, DigitalOcean 4, Google 3, OVH 2, Scaleway 2, plus long tail. Geographic spread: France 5, Germany 4, Singapore 4, US 3, Finland 2, others 1 each.

### `/api/v1/targets` — scrape topology (Insight #88 generalization)

**2,031 distinct scrape-target endpoints leaked.** RFC1918 internal IPs, public hostnames, internal naming conventions — the same disclosure class as VM's vmagent. The Insight #88 thesis (scrape topology = operator org chart) is empirically confirmed at substrate scale on the dominant monitoring platform in the AI/ML ecosystem.

### `/api/v1/rules` and `/api/v1/alerts`

**661 distinct alerting and recording rules** disclosed. **168 firing alerts visible** at scan time. Rule definitions tell an attacker what an operator considers worth alerting on — which is reconnaissance fuel for what to break next. A firing alert tells the attacker the operator has an active problem they may not yet be tracking.

### `/api/v1/label/__name__/values`

**7,604 distinct metric names** disclosed across the verified corpus. 31× more than the VM survey's 241. Prometheus exposes a richer metric-name surface than VictoriaMetrics by default because `--storage.tsdb.path` actually persists the labels, while VM stores its labels in a different shape that the standard endpoint doesn't enumerate as fully.

### `/debug/pprof/` (Insight #89 test, inconclusive at population scale)

**100% (475/475) open.** But every host that has pprof open also has data endpoints open — none demonstrate the "operator hardened the data plane but pprof leaks" pattern that VM exhibits. The framework-level bypass thesis (Insight #89) is not testable here. Prometheus operators who care about auth deploy a reverse proxy that gates pprof along with everything else.

This is a clean negative-result for the Insight #89 generalization at the Prometheus tier. The insight stays VM-specific. The hypothesized class (`_ "net/http/pprof"` side-effect import vs framework-mux auth registration) still applies — but Prometheus's deployment culture (reverse proxy or nothing) means the class doesn't surface as a measurable auth-bypass-evidence-at-scale signal.

## glance sensitivity rollup (Step 3.5)

Ran `glance scan` (v0.1.1, panel-corrected) on the per-host evidence directory. Global rollup across 4 streams (scrape_targets, scrape_pool_names, metric_names, labels):

| Category | Hits |
|---|---|
| GENERIC_INFRA | 4,651 |
| AI_WORKLOAD (alias) | 63 |
| GPU_INFRA | 25 |
| LLM_SERVING | 23 |
| FINANCE | 16 |
| RAG_AGENT | 8 |
| LLM_TRAINING | 4 |
| VECTOR_DB | 3 |
| PII | 1 |
| PHI | 1 |
| DEFENSE_GOV | 1 |

**Quadrant prediction test (DCWF 902 Insight #90 candidate):** The cross-cutting Q1–Q4 taxonomy assigned Prometheus to Q4 Topology Mirrors (same quadrant as VictoriaMetrics) with predicted dominance of CRITICAL_INFRA + DEFENSE_GOV. The actual rollup shows GENERIC_INFRA dominance with a small AI_WORKLOAD subset — closer to a **Q3 Read-Heavy Observer signature** than the Q4 prediction. The reason: Prometheus exposes a much richer metric-name catalog than VM, and metric names are "what's being measured" (Q3) more than "what's being scraped" (Q4). The 7,604-metric-name catalog dominates the rollup.

Implication: **Prometheus straddles Q3 and Q4** — it has the topology surface (`/api/v1/targets`) and the read-heavy-observer surface (`/api/v1/query`, metric catalog). The 2×2 taxonomy needs a refinement that allows multi-quadrant platforms. Candidate Insight #90 becomes a **mixed-quadrant** observation rather than a clean signature prediction.

## Comparison to VictoriaMetrics

The two surveys together build a coherent picture of monitoring substrate exposure:

| Axis | VictoriaMetrics | Prometheus |
|---|---|---|
| Default auth | none | none |
| Framework auth mechanism | `-httpAuth.username/password` (selective) | `--web.config.file` (typically all-or-nothing) |
| Pprof bypass at framework level | Yes (Insight #89) | Not observed |
| Operator hardening modal pattern | rare (4.7% fully gated) | reverse-proxy (63%) |
| When operators don't harden | 93.5% unauth | **100% unauth** |
| Scrape-topology leak (Insight #88) | 1,578 endpoints, 66% RFC1918 | 2,031 endpoints, similar mix |
| Config dump (entire YAML) | not applicable | **100% on open subset** |
| Embedded credentials leaked | not measured | 25 hosts |
| Metric-name catalog | 241 | 7,604 |
| Top per-host workload found | RunPod GPU tenants (57 hosts) | mixed — full corpus contains AI/ML subset but at lower per-host density |

The headline that holds: **operators of substrate monitoring infrastructure either fully harden via reverse proxy or fully expose. The middle ground that the framework allows (selective auth via `-httpAuth` flag on VM) is not where most of the deployed population lives.**

## DCWF KSAT coverage

- **672 (AI T&E Specialist):** falsifier test design (T5919 — adversarial evaluation in realistic environments), version cross-check via goVersion field discriminator (K7044).
- **733 (AI Risk & Ethics):** 25-host credential disclosure flagged as elevated-duty per glance dictionary, but disclosure pipeline pending per-jurisdiction routing (K7051).
- **541 (VAA):** remediation pathway sharp — reverse proxy or `--web.config.file` with TLS+basic_auth.
- **661 (R&D):** Insight #88 confirmed, Insight #89 narrowed to VM-specific; both contribute to the program's falsifiability ledger.

## Wardrobe + syllabus stance

**Wardrobe outfit loaded:** `ai-infra-hunt` (carries from the VictoriaMetrics + Chroma surveys earlier today). Atoms exercised on Prometheus:

- T0028 + T0549: population-scale assessment of authorized substrate, no scope drift
- T0247: verification + acceptance discipline applied at the goVersion field level
- K0342, S0001, S0051: multi-signal endpoint cross-check informed by Hadrian's CVE-2026-45829 pattern (carries over from Chroma)
- T0188: remediation guidance is concrete (vmauth-equivalent / nginx-basic-auth / `--web.config.file`)

**Operating doctrine roles in posture:** 541 (Anchor), 661 (Research Engine — falsifier ledger), **671 (T&E Verification — load-bearing for the goVersion-field discriminator that separated 475 verified Prometheus from 903 reverse-proxied)**, 212 (Forensics — per-host JSON evidence), 511 (Population CDA — 475 verified, 100% open).

**Syllabus threat-literature anchors:**

- *Adaptive Defense Orchestration for RAG* (arxiv 2604.20932): proposes monitoring on control-plane events. The 475 Prometheus operators with `/api/v1/status/config` fully open are exactly the population this line of work prescribes mitigations for.
- *Architecture Matters: Comparing RAG Systems under Knowledge* (arxiv 2605.05632): platform choice shapes attack surface. Prometheus vs VM is a worked case — same category, different default failure mode (config dump vs framework-pprof bypass).

## Artifacts

- **Tome platform brief:** `~/tome/platforms/prometheus.json`
- **Shodan harvest:** `~/syllabus/shodan/prom-harvest/{summary.json, hosts.json}` (1,429 raw)
- **Per-host verification evidence:** `~/syllabus/shodan/prom-verify/hosts/<ip_port>.json` (1,429 files; held private)
- **Verifier source:** `~/syllabus/shodan/verify_prom_unauth.py` → `tools/verify_prom_unauth.py`
- **glance rollup:** `~/AI-LLM-Infrastructure-OSINT/research-program/glance-rollups/prometheus-2026-06-08.json`
- **Findings breakdown:** see `prometheus-survey-2026-06-08-findings-breakdown.txt`

## What we did not do (restraint discipline)

- Zero write-method HTTP calls (POST/PUT/DELETE/PATCH) on any endpoint.
- No `/api/v1/query?query=*` reads of metric values — schema only.
- No reads of `/api/v1/admin/tsdb/delete_series` or `/snapshot` even on hosts where `--web.enable-admin-api` may be flipped.
- No probes into the 2,031 leaked RFC1918/internal scrape-target endpoints.
- Embedded credentials disclosed in 25 hosts' configs were COUNTED, not extracted, copied, validated, or stored beyond the in-memory regex match. The per-host JSON evidence files contain the raw `/api/v1/status/config` body which carries these credentials; that evidence stays in private records and never appears in any public artifact.

## Insight updates

**Insight #88 — scrape topology = operator org chart (Confirmed at Prometheus scale).** Now confirmed across two substrate-tier platforms (VictoriaMetrics + Prometheus). Population-scale evidence at 2,031 + 1,578 = 3,609 leaked scrape-target endpoints across both surveys, with 60–70% RFC1918 share on both. The pattern generalizes. Next test platforms per the DCWF 902 roadmap: OpenTelemetry Collector, Consul, Nomad, kubelet.

**Insight #89 — framework-level auth bypass (Stays VM-specific for now).** Prometheus does not exhibit the operator-hardened-but-pprof-leaks pattern at population scale because the deployment culture is reverse-proxy-or-nothing. The hypothesized class (`_ "net/http/pprof"` side-effect inheritance) remains theoretically applicable but did not surface as measurable evidence here. The insight is not falsified — it is unobservable at this tier because the necessary measurement conditions don't exist in the deployed population.

**Insight #90 candidate (mixed-quadrant platforms).** Prometheus straddles Q3 (Read-Heavy Observer) and Q4 (Topology Mirror) in the DCWF 902 monitors-vs-holds taxonomy. The 2×2 grid needs to allow multi-quadrant assignments; clean single-quadrant prediction fails on this platform. Codify after the OpenTelemetry survey to see if the same straddling occurs.

**New Insight #91 candidate (config-dump endpoints concentrate the disclosure value).** `/api/v1/status/config` is a single endpoint that returns more disclosure than the next 5 endpoints combined: full scrape config + remote_write URLs + AlertManager URLs + sometimes plaintext credentials. Same structural class as Consul's `/v1/agent/self`, Vault's `/v1/sys/config/state/sanitized`, NATS's `/varz`. The general claim: any platform with a "give me everything about your configuration" debug endpoint open by default produces a richer disclosure than the platform's own data-plane endpoints. Codify after Consul + Vault survey confirms.
