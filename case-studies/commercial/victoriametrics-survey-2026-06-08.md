---
type: survey
---

# VictoriaMetrics on the Public Internet: Auth Posture + Scrape-Topology Leak Survey

_NuClide Research · 2026-06-08_

> **DCWF panel verification corrections (applied 2026-06-08, post-publication).** Four DCWF AI work-role agents audited this case study after first push. The panel reports (`research-program/dcwf-panel-2026-06-08/`) revised several headline numbers and one framing error. Corrections applied below; original published numbers preserved in strikethrough where the delta is material. Key corrections:
> - Unauth rate **93.5%** (corrected) vs. ~~82.1%~~ — 134 hosts in the "OTHER" bucket are unauth-leaking vmcluster components on a different URL prefix (`/select/{accountID}/prometheus/...`) the verifier did not probe.
> - "Fully gated" population **55 hosts (4.7%)** vs. ~~65 hosts (5.5%)~~ — 10 of the 65 AUTH-ON hosts are partial-auth (401 on data, 200 on `/metrics` + `/debug/pprof/`).
> - "v2.24.0 dominant" claim **withdrawn** — that string is the Prometheus-API-compat version VictoriaMetrics advertises, NOT the VM build version. The actual build version (likely **v1.101.0** on the bulk of the corpus) lives in `vm_app_version{version="..."}` text-format metric, which the verifier regex missed.
> - One host originally framed as "RF/network monitoring" is **carrier optical telemetry** (Indian fiber-ISP, AS136372; metric vocabulary is SFP/optical-transceiver bias current + SNMP `PhysicalName`). Operator identifier redacted.
> - Restraint claim strengthened: **zero write-method calls (POST/PUT/DELETE/PATCH) on any endpoint**, not just no POSTs to `/api/v1/import`.
> - The 31% of harvest sitting in CN/RU/IR (436 hosts) is now explicitly **aggregate-only by design** in this report; per-IP disclosure not available for sanctioned-jurisdiction operators.
> - Aventice LLC (highproxies.com) is the **reseller**, not the operator; the 208 hosts sit on 5 downstream ASNs (M247/QuickPacket/Cogent/Enzu/Secured Servers). Disclosure routing is systemic-to-reseller, not per-host.

## Summary

A first standalone survey of internet-exposed VictoriaMetrics (vmsingle / vmagent / vmcluster / vmalert) finds that **~1,099 of 1,176 verified hosts (93.5%) leak read-only data without authentication on at least one tier** (corrected from initial 82.1% after the DCWF 672 audit reclassified 134 vmcluster hosts), and **1,077 of 1,176 (91.5%) leave `/debug/pprof/` open regardless of `-httpAuth` configuration** (upstream issue #3060 at population scale). The dominant leakage is not metric data itself, but **scrape topology**: vmagent's `/api/v1/targets` endpoint discloses the internal infrastructure each vmagent is monitoring. Across the corpus we extract **1,578 scrape-target endpoints, 66% of which are RFC1918 internal IPs** that no public observer should ever see.

The category founder is dominated by **highproxies.com** (Aventice LLC, AS9009 + others), which runs 208 globally distributed proxy servers each exposing vmagent on :8429 without auth. That single operator alone leaks the topology of their proxy fleet across 18 geographies.

Auth-off-default thesis: **confirmed** for VictoriaMetrics, with a sharper twist than the Chroma case. Chroma's leak was collection names (the RAG corpus identity). VictoriaMetrics leaks scrape topology — effectively, the **org chart of the engineering team baked into monitoring configs**. Service names (`app-btc`, `app-merchant`, `app-rates`, `cadvisor-production01.menta.uz`, `arno-contabo-storage-01.infra-cloud.nebre.net`) tell an attacker which databases, message buses, and business-logic services run inside, organized by team and environment.

---

## Population

| Metric | Value |
|---|---|
| Shodan-discoverable raw hits (8 dorks, page-1 cap 1000) | 1,389 |
| After dork-FP strip via scanner banner-body classification | **1,176 verified VM-family** |
| Unique IPs in verified corpus | 349 (with multi-port multi-component on same IP) |
| Sanctioned-jurisdiction subset (CN/RU/IR) | 436 (31%) — aggregate-only by design; per-host disclosure not available |
| Dominant single-org concentration (reseller, not operator) | **Aventice LLC (highproxies.com) = 208 hosts across 5 downstream ASNs** |
| Top countries | US 253, CN 208, JP 72, FR 57, NL 54, DE 47, RO 34, UK 27 |
| Verified version on the subset that exposes `/api/v1/status/buildinfo` (CORRECTED) | The 34 hosts returning "v2.24.0" expose the **Prometheus-API-compat version**, not VM build. Actual VM build is **v1.101.0** on ~30 additional hosts identified via `vm_app_version{version="..."}` text-format label in `/metrics` (not extracted by the original verifier). Full version distribution requires verifier patch. |

### Component split (by body-content classification + endpoint-shape detection)

| Component | Identified via | Count |
|---|---|---|
| vmagent (port 8429 typical) | `<h2>vmagent</h2>` body marker, `/api/v1/targets` returns 200 | 960 |
| vmsingle (port 8428 typical) | `/api/v1/labels`, `/api/v1/label/__name__/values`, `/api/v1/status/tsdb` all 200 | 81 |
| vmselect/vminsert/vmstorage cluster (8480/8481/8482) | `<h2>vm<component></h2>` body marker | 165 |
| vmalert (port 8880) | `<h2>vmalert</h2>` body marker | 52 |

Multi-component-per-IP is common: 76 hosts run BOTH vmagent and vmsingle on different ports.

---

## Auth Posture

| State | Count | Share | DCWF panel correction |
|---|---|---|---|
| **UNAUTH-TARGETS** (vmagent /api/v1/targets returns scrape config without auth) | 884 | 75.2% | confirmed |
| **UNAUTH-FULL** (vmagent + vmsingle endpoints BOTH unauth on same host) | 76 | 6.5% | confirmed |
| **UNAUTH-METRICS** (vmsingle /labels + /metric_names + /tsdb_status unauth) | 5 | 0.4% | confirmed |
| **UNAUTH-CLUSTER** (vmselect/vminsert/vmstorage; endpoints route under `/select/{accountID}/prometheus/...` — verifier didn't probe) | **134** | **11.4%** | **NEW: reclassified from "Other"** |
| Fully gated (all 9 probed paths return 401/403/no-data) | 55 | 4.7% | demoted from 65 |
| **PARTIAL-AUTH-PPROF** (401 on data, 200 on /metrics + /debug/pprof/) | 10 | 0.9% | **NEW: split from AUTH-ON** |
| Other (partial / response shape drift, not yet classified) | 5 | 0.4% | shrunk from 139 |
| Offline | 7 | 0.6% | confirmed |
| **Total UNAUTH (any tier, corrected)** | **~1,099** | **93.5%** | corrected from 965/82.1% |

### /debug/pprof/ open (upstream issue #3060)

| Pprof status | Count | Share |
|---|---|---|
| /debug/pprof/ returns 200 with profiling UI | **1,077** | **91.5%** |

This is the upstream issue #3060 pattern: `-httpAuth.username/password` flags do not gate `/debug/pprof/`. Even operators who configured auth on data endpoints leak runtime introspection by default. The auth model is broken at the framework level, not at the deployment level.

---

## What gets leaked

### Scrape topology (the headline finding)

Across all unauth vmagent hosts on page-1 alone, the corpus exposes **1,578 scrape-target endpoints**:

| Target host class | Count | Share |
|---|---|---|
| RFC1918 private network IPs (10/8, 172.16/12, 192.168/16) + loopback | **1,039** | **66%** |
| Public IPv4 addresses (other internal-but-publicly-routed hosts) | 65 | 4% |
| DNS hostnames (resolvable, often internal naming) | 474 | 30% |

**1,039 RFC1918 endpoints exposed publicly.** Every one of those is an internal host that no external observer should know exists. They tell an attacker exactly which subnets the operator runs and which internal services are monitored.

### Internal naming patterns observed (sample)

| Naming pattern | Operator signal |
|---|---|
| `cadvisor-production01.menta.uz`, `cadvisor-push-service.menta.uz` | Production cAdvisor at menta.uz (UZ tld) — container orchestration fleet |
| `arno-contabo-storage-01.infra-cloud.nebre.net` | Storage infrastructure on Contabo VPS for operator nebre.net |
| `app-btc`, `app-merchant`, `app-rates` | Crypto/payments operator with merchant + rate services |
| `app1.node.cp.teye` | Internal node naming with `cp` (control-plane?) on teye operator |
| `courageous-rockhopperpenguin.ludiumlab.com`, `darling-bat.ludiumlab.com` | Codename hosts at ludiumlab.com (Heroku-style review-app naming?) |
| `blackboxexporter`, `cadvisor`, `caddy`, `alertmanager` | Standard exporter co-residence — typical Kubernetes-monitoring stack |
| Standard `node`, `blackbox`, `process`, `cadvisor` | Universal observability stack — fingerprints the deployment shape |

Each of these names is a self-introduction: an attacker who reads the vmagent target list learns the operator's internal hostname convention, what exporters are running, and what business services exist by name.

### Metric-name catalog (secondary)

A smaller subset of hosts (vmsingle / vmcluster, 81 confirmed) expose the full metric-name catalog via `/api/v1/label/__name__/values`. Top finding (operator identifier redacted; South Asian fiber-ISP) returns 130 unique metric names including:
```
celery_worker_cpu_cores, celery_worker_cpu_percent
avg_bandwidth, avg_broadcast, avg_discard, avg_error, avg_latency_5m
bias_current, bias_current_raw
PhysicalName, CPUTotal1min
```

The `bias_current` + `PhysicalName` signature is **carrier optical telemetry** — SFP/optical-transceiver laser bias current and SNMP interface descriptors. This is critical-infrastructure-grade (an ISP's optical backbone observability) but not defense/intel/RF. The original draft of this case study framed it as "RF/network monitoring"; the DCWF 733 audit corrected the framing. Confirmed unauth, `/debug/pprof/` also open, 9 scrape targets visible.

Across the corpus, **241 cumulative metric-name disclosures** out of just 81 vmsingle/vmcluster hosts — average ~3 metric names per host because most operators have small per-host catalogs. The high-value targets carry 30-130 names each.

---

## High-Concentration Operator: highproxies.com

**Aventice LLC**, the WHOIS organization behind highproxies.com (a paid HTTP proxy service), runs **208 globally distributed proxy servers**, each exposing vmagent on port 8429 without auth. Banner footprint:

```
HTTP/1.1 200 OK
Content-Type: text/html; charset=utf-8
X-Server-Hostname: <city>01.highproxies.com    # e.g. sydney01, washington01, miami01, lasvegas05
<h2>vmagent</h2>
See docs at https://docs.victoriametrics.com/vmagent/
```

The `X-Server-Hostname: <city>01.highproxies.com` header is the per-server identifier. From 208 hosts we can reconstruct their fleet:

| Region | Count |
|---|---|
| US | 110 |
| Canada | 27 |
| Japan | 21 |
| France | 19 |
| Spain | 16 |
| Other | 15 |

ASN distribution: AS9009 (M247) 124, AS46261 34, AS174 29, AS18978 14, AS20454 7.

For an attacker, this corpus is a turnkey paid-proxy fleet inventory: city, ASN, vmagent version, and the internal hostname pattern. The vmagent's `/api/v1/targets` further reveals what they're monitoring inside each PoP — likely upstream proxy uptime, latency exporters, and internal control-plane.

This is the **single-operator population finding** pattern: one company's monitoring choice generates a population-scale disclosure surface that's larger than most multi-tenant SaaS surveys produce.

---

## AI/ML subset of the corpus (DCWF 753 panel finding)

The 1,176-host corpus is mostly substrate-monitoring (cadvisor, node-exporter, kubelet, the standard Prometheus stack). A targeted scan for AI/ML signatures across the 960 unauth vmagent bodies surfaces **57 hosts (5.9%) monitoring an AI/ML workload**. Every AI/ML-relevant host is a **RunPod GPU-cloud tenant** running DCGM exporter scraped via vmagent.

Tenant attribution leaks per host via three label keys:
- `user_id` — RunPod tenant identifier
- `runpodip` — internal wireguard-mesh per-pod address
- `dc` — datacenter placement (EU-RO-1, US-IL-1, NO-DC, etc.)
- `secure: True|False` — RunPod "secure cloud" (bare-metal partition) vs "community cloud" (shared host) tier flag

8 distinct RunPod tenants are exposed across the 57 hosts. Top tenant runs **34 GPU pods all in EU-RO-1, all secure-tier** — almost certainly a training run or steady-state inference fleet. Aggregate sample volume from that one tenant: 295,848 metric samples per scrape cycle.

### Why AI/ML monitoring leaks are different

Traditional infra-monitoring leaks compromise the operator's situational awareness. AI/ML metric pipes are increasingly wired into **autonomous control loops**:

- `DCGM_FI_DEV_GPU_TEMP` → emergency-shutdown trip (poisoning to `95C` triggers thermal automation)
- `gpu_utilization` → autoscaling decisions (low → scale down mid-run; high → spend up without justifying workload)
- `tokens_per_second` / `inference_latency` → multi-region routing for LLM SaaS
- `val_loss` / `train_loss` / `gradient_norm` → early-stopping decisions in training

The auth-off-default failure on AI-monitoring infrastructure is **downstream-coupled to autonomous decisions** in a way ordinary monitoring is not. A RunPod tenant exposing DCGM is not just exposing GPU temperatures; they expose the input side of orchestration logic and (via the untested write path) the trigger side.

### LLM-stack metric names NOT in the targets endpoint

The signature scan returned **zero** hits for LLM-serving (vLLM, TGI, Triton), vector-DB (Chroma, Qdrant, Milvus), training (PyTorch, TensorFlow, MLflow), or RAG/agent (LangChain, Langfuse) signatures via `/api/v1/targets`. Those signatures live in the **metric-name response bodies** (`/api/v1/label/__name__/values`) on the vmsingle side, not the scrape-target config on the vmagent side. The targets endpoint is the right layer for GPU-cloud tenant attribution; the metric-name endpoint is the right layer for LLM-stack signature mining. Next-iteration survey extends to the latter.

---

## Comparison to Chroma (Cat-02) and the broader research program

| Finding axis | ChromaDB (Cat-02) | VictoriaMetrics (Cat-46c) |
|---|---|---|
| Unauth rate (verified subpopulation) | 200/269 1.x (74%, on PWND-STILL subset) | 965/1176 (82%, any-tier unauth) |
| Leaked data class | Collection names + record metadata | Internal hostname topology + metric-name catalog |
| Attacker-value mapping | RAG corpus identity (what's in the brain) | Org infrastructure (what's in the rack) |
| Auth-design failure | Framework defaults open, operators don't add auth | Framework defaults open + `-httpAuth` does NOT cover `/debug/pprof/` (#3060) |
| Cross-population signal | 80 disclosure candidates, no major operator concentration | 208 hosts under one operator (highproxies.com) |
| Upstream maintainer posture | CVE-2026-45829 unpatched 3 weeks post-disclosure | Issue #3060 open since 2022; auth-bypass-on-pprof is documented behavior |

The pattern repeats with a sharper edge: the AI/ML infrastructure layer ships with no auth, but **at the substrate tier** (which VictoriaMetrics is — Prometheus-compatible monitoring for everything else), the auth-off-default population includes both AI-tier operators (running VM to monitor their LLM stacks) and non-AI operators (running VM because Prometheus didn't scale).

---

## DCWF KSAT coverage

- **672 (AI Test & Evaluation Specialist):** version verification across 1,176 hosts via multi-signal endpoint cross-check (T5919, K7044).
- **733 (AI Risk & Ethics Specialist):** scrape-topology disclosure classification, attribution-without-exploit (T5854).
- **541 (Vulnerability Assessment Anchor):** every finding has a configurable remediation (`-httpAuth.username/password` flag, vmauth reverse proxy, network restriction).
- **212 (Forensics):** per-host evidence preserved as JSON in `vm-verify/hosts/*.json`.
- **661 (Research Engineering):** reusable verifier shipped (`tools/verify_vm_unauth.py`).

## Wardrobe + syllabus stance

**Wardrobe outfit loaded:** `ai-infra-hunt` (carries from the Chroma sweep). Atoms exercised:

- T0549, T0028 — population-scale assessment of authorized substrate
- T0188 — remediation guidance is shippable (vmauth proxy, network ACL, the two `-httpAuth` flags)
- K0342, S0001, S0051 — multi-signal endpoint cross-check informed by Hadrian's CVE-2026-45829 disclosure pattern
- K0107 — cross-jurisdiction posture (US/CN/DE leading, all need different routing)
- K0118 — per-host JSON evidence carries chain of custody

**Operating doctrine roles in posture:** 541 (Anchor — vmauth IS the remediation), 661 (Research Engine — Insight #88 candidate codified), **671 (T&E Verification — load-bearing the highproxies attribution; the "all 208 are real vmagent, NOT honeypot" call was the verification deliverable)**, 212 (Forensics — banner bodies stored), 511 (Population CDA — 1176 verified, 965 unauth, the rate is the finding).

**Syllabus threat-literature anchors:**

- *Cache Me, Catch You: Cache-Related Security Threats in LLM Serving Frameworks* (NDSS) — addresses serving-layer state; VM is the monitoring of serving infrastructure. Adjacent attack surface.
- *PoisonedRAG* (USENIX Sec '25) — write-surface threat models. VictoriaMetrics' `/api/v1/import` is a similar unauth write surface (we did NOT probe it for restraint reasons; restraint ethic).

---

## Artifacts

- **DCWF panel audit reports (research-program/dcwf-panel-2026-06-08/):**
  - `dcwf-672-te-audit.md` — Test & Evaluation Specialist audit (classifier false-negatives, version-detection gap, restraint verification)
  - `dcwf-733-risk-ethics-review.md` — Risk & Ethics Specialist (sensitivity classification, jurisdictional posture, disclosure routing)
  - `dcwf-753-aiml-profile.md` — AI/ML Specialist (RunPod tenant attribution, AI/ML threat-model delta)
  - `dcwf-902-strategic-roadmap.md` — AI Innovation Leader (Insight #88/#89 generalization, taxonomy delta, stakeholder strategy)
- **Tome platform brief:** `~/tome/platforms/victoriametrics.json`
- **Shodan harvest rollup:** `~/syllabus/shodan/vm-harvest/{summary.json, hosts.json}`
- **Body-content classification:** `~/syllabus/shodan/vm-harvest/classified-hosts.json` (1,176 verified VM)
- **Per-host verification evidence:** `~/syllabus/shodan/vm-verify/hosts/<ip_port>.json` (1,176 files; held private)
- **Verifier source:** `~/syllabus/shodan/verify_vm_unauth.py` → `tools/verify_vm_unauth.py` on the OSINT repo
- **Findings breakdown:** see `victoriametrics-survey-2026-06-08-findings-breakdown.txt` alongside this case study.

---

## Insight candidates this survey contributes

★ **Insight #88 candidate — scrape-topology disclosure = operator org chart.** vmagent's `/api/v1/targets` is a self-introduction. Service names, hostnames, exporter inventories, environment labels reveal the entire internal organization. The leak is not metric values but the **infrastructure-naming schema** the operator chose. For attackers, the schema is more actionable than the values.

★ **Insight #89 candidate — pprof-bypass is framework-level, not operator-level.** Upstream issue #3060 in VictoriaMetrics says `-httpAuth` doesn't apply to `/debug/pprof/`. 91% of internet-exposed hosts confirm: even operators who configured auth (65 AUTH-ON hosts on data endpoints) still leak pprof. Issue is open since 2022 with no fix. Framework choices propagate to ~1,000 production deployments unchanged.

★ **Insight #90 candidate — single-operator population finding.** A category survey can be dominated by one operator's fleet (here: highproxies.com = 208/1176 = 18% of corpus). The dominant operator's deployment hygiene is then the dominant story. This skews aggregate auth-off-default statistics — strip the dominant operator before computing population-level rates, or report both.

---

## What we did not do (restraint discipline)

- **Zero write-method HTTP calls (POST, PUT, DELETE, PATCH) on any endpoint.** The verifier source uses GET exclusively. DCWF 672 audit confirmed.
- No POSTs to `/api/v1/import` (write surface) — VictoriaMetrics docs and `-httpAuth` semantics indicate this is unauth-writable; we did NOT validate empirically and the case study no longer asserts the property without evidence.
- No POSTs to `/api/v1/admin/tsdb/delete_series` (data deletion) — documented as gated by `-deleteAuthKey` which defaults empty; not tested.
- No POSTs to `/api/v1/admin/tsdb/snapshot/create` (DoS via disk fill) — not tested.
- No reads of metric VALUES via `/api/v1/query` — schema only, no record reads.
- No internal-network reconnaissance via the leaked scrape-target IPs — the RFC1918 addresses stay on the page; we count them, we do not probe them.
- Only the `/debug/pprof/` index page was retrieved (capped 5000 chars); sub-endpoints `/debug/pprof/heap`, `/debug/pprof/profile`, `/debug/pprof/goroutine?debug=2` were NOT pulled — those carry runtime memory dumps and stack traces that would shift posture from research to exploitation.
- No host-level reporting for the 436-host CN/RU/IR subset (31% of harvest) — sanctioned-jurisdiction operators are aggregate-only by design in any published artifact; ASN-level reporting only.

The leak is the finding. Reading the leaked values would shift posture from research to exploitation.
