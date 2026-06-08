# Risk & Ethics Review: VictoriaMetrics Survey 2026-06-08

_DCWF AI Work Role 733 audit · NuClide Research panel_

## 1. Sensitivity Classification of Leaked Targets

Parsed `evidence.targets.body` across all 960 vmagent hosts where `/api/v1/targets` returned HTTP 200 (the published case study cites 884 — the 76-host delta reflects partial bodies that still parsed as 200). Across that population, page-1 yields 1,578 distinct `scrapeUrl` values and 2,966 `job` labels. Bag-of-fields regex classification against operator-attribution heuristics:

| Bucket | Hosts matched | Notes |
|---|---|---|
| GENERIC_INFRA (cadvisor / node-exporter / kube / nginx / grafana) | 646 | the standard observability stack; no operator-identity leakage |
| AI/ML | 1 | `nvidia_gpu_exporter` only; no LLM-fingerprint targets in page-1 |
| HEALTHCARE | 1 (false-positive candidate) | `live.health.theloopa.com` — substring "health" but Loopa is an art-tech vendor; needs manual confirmation before tagging |
| FINANCE | 3 | one RabbitMQ ops cluster, one `app-btc/app-merchant` pool (named example: a self-hosted crypto-payment gateway operator), one Cloudpayments.ru blackbox probe |
| CRITICAL_INFRA | 1 | `power_scrapper` job-label on an Indian ISP host running vmalert |
| DEFENSE/GOV | 0 | no `.mil/.gov/.go.` strings, no defense-contractor tells in page-1 |
| PERSONAL_PII | 0 | no `user/customer/profile` discriminators above the false-positive floor |
| Unclassified | 81 | hosts whose page-1 body contained scrape state but no attribution string |

Practical reading: at population scale this leak is **operator-generic** infrastructure telemetry, not a PII/PHI/PCI mass disclosure. The named-operator risk concentrates on the long-tail (~5 hosts) where the scrape config exposes a vertical fingerprint — and those are the disclosure-priority hosts.

Note on AD_TECH bucket: dropped from final reporting because the regex caught the literal word "metrics" on every host. Bucket overfit, not signal.

## 2. Cross-Jurisdiction Disclosure Routing — Aventice LLC

Aventice LLC (highproxies.com) carries 208 of 1,176 hosts (17.7%), but the org name papers over the real attribution: those 208 hosts sit on **five downstream ASNs** — M247 Europe SRL (AS9009, 124 hosts), QuickPacket LLC (AS46261, 34), Cogent (AS174, 29), Enzu Inc (AS18978, 14), SECURED SERVERS LLC (AS20454, 7). Aventice is the *reseller*; the hosting substrate is multi-jurisdictional and the actual VM operators are Aventice's downstream customers, not Aventice itself.

That matters for ethics calculus three ways. **First**, Aventice cannot remediate misconfiguration on a customer's VM — they would have to enforce a policy update across the proxy fleet and the customers operating the metrics stack. **Second**, paid-proxy services are dual-use infrastructure: legitimate scraping/SEO/QA customers share the surface with abuse actors, and a bulk disclosure to Aventice risks tipping abuse actors that the infra is being studied. **Third**, the abuse-facing posture means Aventice's security contact may treat unsolicited disclosure adversarially (as recon) rather than cooperatively.

Recommended routing: do **not** disclose host-by-host to Aventice. Disclose the *systemic finding* — "your fleet's vmagent default exposes `/api/v1/targets` without auth, here are aggregate counts, no per-host IPs" — to security@highproxies.com (or the WHOIS abuse contact for AS9009 M247 if Aventice doesn't expose a security channel). Treat per-host IPs as redacted in any external artifact. The disclosure asks Aventice to push a fleet-wide configuration baseline, not to triage 208 individual customer tickets.

## 3. CN / RU / IR Hosts

Sanctioned-jurisdiction breakdown of the 1,389-host harvest:

- **China**: 412 hosts. Concentrated in AS4134 (Chinanet, 142), AS37963 (Aliyun, 63), AS58461 (CHINANET, 41), AS4812 (Shanghai Telecom, 39), AS4837 (CNCGroup, 30), plus AS45090 (Tencent, 18).
- **Russian Federation**: 22 hosts. Long tail; top ASNs AS9123 (4), AS198610 (3), AS50340 (3), AS200350 (3).
- **Iran**: 2 hosts. AS31549 (1), AS49801 (1).

Total: **436 hosts (31% of harvest) sit in a jurisdiction we cannot file responsible disclosure into.**

Correct posture: we have a **public-research safe harbor** for the population-statistics layer — counts, version distributions, ASN buckets, and the generalized class of vulnerability are publishable research, the same way Censys/Shodan/Shadowserver publish them. We do **not** have safe harbor to publish IP-level identifiers for sanctioned-jurisdiction operators in a way that hands a targeting list to a third party.

Redaction recommendation for the case study: aggregate CN/RU/IR hosts at the ASN level only, do not publish IPs, do not publish operator org names where they map to identifiable downstream operators (state media, state-owned enterprises). Note explicitly in the case study that disclosure routing is not available for this 31% subset and that aggregated reporting is the deliberate posture, not an oversight.

## 4. Leaked Metric Names — Dual-Use Ethics

The case-study-highlighted host running `bias_current`, `avg_latency_5m`, `PhysicalName` resolves to an Indian fiber-ISP (`ssfibernet.com`, AS136372) running vmalert on port 8880. The metric vocabulary is **optical-transport telemetry**, not RF/SIGINT: `bias_current` is SFP/optical-transceiver laser bias current, `PhysicalName` is an SNMP interface descriptor, `avg_latency_5m`/`device_bandwidth`/`congestion_*` are carrier-grade router telemetry. This is **critical-infrastructure-grade** (an ISP's optical backbone observability) but not defense/intel. The case study should correct the framing from "RF/network monitoring" to "carrier optical telemetry."

The dual-use ethics question still stands. When a survey accidentally surfaces a target whose mere identification carries operational risk — utility SCADA, ISP transport plane, defense-cleared cloud, hospital EHR — the survey artifact itself becomes the attack-surface document. The obligation is asymmetric: aggregate population statistics are fair research output, but a single named operator in a sensitive vertical deserves a private, direct disclosure path *before* the survey publishes, and the survey body should redact that operator to a category-level pseudonym ("a South Asian fiber-ISP running vmalert with unauthenticated metric-name catalog") rather than an attributable IP or hostname.

That principle generalizes. The **count** of critical-infrastructure-tagged hosts is publishable; the **identifying string** is not, even on a single-host case study, until the operator has had a private window to remediate. The current case-study language exposes one identifiable critical-infrastructure operator and should be edited before further distribution.

## 5. Restraint-Ethic Audit

Read `~/AI-LLM-Infrastructure-OSINT/tools/verify_vm_unauth.py` and the working copy at `~/syllabus/shodan/verify_vm_unauth.py`. Findings:

- Zero `POST`, `PUT`, `DELETE`, `PATCH` calls. The only HTTP method used is `aget()` (line 63), which calls `s.get(url, ssl=False, allow_redirects=False)`. Single GET per endpoint, no method override.
- The 9 probed paths are all **read-only** VictoriaMetrics endpoints: `/api/v1/status/buildinfo`, `/api/v1/status/tsdb`, `/api/v1/labels`, `/api/v1/label/__name__/values`, `/api/v1/targets`, `/api/v1/rules`, `/api/v1/alerts`, `/metrics`, `/debug/pprof/`.
- `/api/v1/import` (write surface) and `/api/v1/admin/tsdb/delete_series` (destructive) are **explicitly excluded** in the module docstring (lines 7–10) and never appear in `PATHS`.
- `/debug/pprof/` is read-only but capable of leaking goroutine dumps + heap snapshots; the verifier reads the index page only (body capped at 5000 chars) and does not pull `/debug/pprof/heap` or `/debug/pprof/profile`. That's inside the restraint envelope but worth flagging — the case study should note the verifier touched the pprof *index*, not the heap/profile sub-endpoints.

**Restraint claim verified.** The case-study assertion ("we did not POST to /api/v1/import") is accurate and stronger than stated — no write-method calls at all, against any endpoint.

## Disclosure-Pipeline Risk Tier

| Operator category | Volume | Risk tier | Routing posture |
|---|---|---|---|
| Generic observability stack (cadvisor/node-exporter/kube) | 646 hosts | **LOW** | Aggregate-only in case study; no individual outreach |
| Aventice/highproxies fleet (multi-ASN reseller) | 208 hosts | **MED** | One systemic disclosure to Aventice security + AS9009 M247 abuse; no per-host IPs |
| Carrier optical telemetry / ISP transport-plane | 1 named, est. 5–15 in long tail | **HIGH** | Private direct disclosure to operator; redact to category in public artifact until remediated |
| Crypto-payment / finance self-hosted gateways | 3 named | **HIGH** | Private direct disclosure; named operator (`app-btc/app-merchant` and the Cloudpayments.ru probe) carries financial-impact severity |
| Healthcare candidate (`live.health.theloopa.com`) | 1 | **MED** (pending confirmation) | Manual verification before tagging; if confirmed clinical, escalate to HIGH and private route |
| AI/ML (nvidia_gpu_exporter only) | 1 | **LOW** | Generic exporter; no LLM-fingerprint surface in page-1 |
| CN-jurisdiction operators | 412 hosts | **REDACT** | Aggregate at ASN level only; no IPs, no operator names, no disclosure routing available |
| RU-jurisdiction operators | 22 hosts | **REDACT** | Same |
| IR-jurisdiction operators | 2 hosts | **REDACT** | Same |
| Unclassified (page-1 no attribution string) | 81 hosts | **LOW** | Aggregate-only |
