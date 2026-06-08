---
type: survey
---

# VictoriaMetrics on the Public Internet: Auth Posture + Scrape-Topology Leak Survey

_NuClide Research · 2026-06-08_

---

## Summary

A first standalone survey of internet-exposed VictoriaMetrics (vmsingle / vmagent / vmcluster / vmalert) finds that **965 of 1,176 verified hosts (82%) leak read-only data without authentication**, and **1,077 of 1,176 (91%) leave `/debug/pprof/` open regardless of `-httpAuth` configuration** (upstream issue #3060 at population scale). The dominant leakage is not metric data itself, but **scrape topology**: vmagent's `/api/v1/targets` endpoint discloses the internal infrastructure each vmagent is monitoring. Across the corpus we extract **1,578 scrape-target endpoints, 66% of which are RFC1918 internal IPs** that no public observer should ever see.

The category founder is dominated by **highproxies.com** (Aventice LLC, AS9009 + others), which runs 208 globally distributed proxy servers each exposing vmagent on :8429 without auth. That single operator alone leaks the topology of their proxy fleet across 18 geographies.

Auth-off-default thesis: **confirmed** for VictoriaMetrics, with a sharper twist than the Chroma case. Chroma's leak was collection names (the RAG corpus identity). VictoriaMetrics leaks scrape topology — effectively, the **org chart of the engineering team baked into monitoring configs**. Service names (`app-btc`, `app-merchant`, `app-rates`, `cadvisor-production01.menta.uz`, `arno-contabo-storage-01.infra-cloud.nebre.net`) tell an attacker which databases, message buses, and business-logic services run inside, organized by team and environment.

---

## Population

| Metric | Value |
|---|---|
| Shodan-discoverable raw hits (8 dorks, page-1 cap 1000) | 1,389 |
| After dork-FP strip via scanner banner-body classification | **1,176 verified VM-family** |
| Unique IPs in verified corpus | 349 (with multi-port multi-component on same IP) |
| Dominant single-org concentration | **Aventice LLC (highproxies.com) = 208 hosts** |
| Top countries | US 253, CN 208, JP 72, FR 57, NL 54, DE 47, RO 34, UK 27 |
| Verified version on the subset that exposes `/api/v1/status/buildinfo` | v2.24.0 (only 34/1,176 hosts respond; majority returns 400) |

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

| State | Count | Share |
|---|---|---|
| **UNAUTH-TARGETS** (vmagent /api/v1/targets returns scrape config without auth) | 884 | 75.2% |
| **UNAUTH-FULL** (vmagent + vmsingle endpoints BOTH unauth on same host) | 76 | 6.5% |
| **UNAUTH-METRICS** (vmsingle /labels + /metric_names + /tsdb_status unauth) | 5 | 0.4% |
| AUTH-ON (all gated endpoints return 401/403) | 65 | 5.5% |
| Other (partial / response shape drift) | 139 | 11.8% |
| Offline | 7 | 0.6% |
| **Total UNAUTH (any tier)** | **965** | **82.1%** |

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

A smaller subset of hosts (vmsingle / vmcluster, 81 confirmed) expose the full metric-name catalog via `/api/v1/label/__name__/values`. Top finding **`103.81.139.164:8428`** returns 130 unique metric names including:
```
celery_worker_cpu_cores, celery_worker_cpu_percent
avg_bandwidth, avg_broadcast, avg_discard, avg_error, avg_latency_5m
bias_current, bias_current_raw
PhysicalName, CPUTotal1min
```

The `bias_current` + `avg_bandwidth` + `PhysicalName` signature is consistent with **network-equipment / RF-monitoring** infrastructure (optical/radio fiber backbone). Confirmed unauth at v2.24.0 with `/debug/pprof/` also open and 9 scrape targets visible.

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

- No POSTs to `/api/v1/import` (write surface) — we know it accepts unauth writes; we did not test.
- No POSTs to `/api/v1/admin/tsdb/delete_series` (data deletion) — we know it's gated only by `-deleteAuthKey` which defaults empty.
- No POSTs to `/api/v1/admin/tsdb/snapshot/create` (DoS via disk fill) — same.
- No reads of metric VALUES via `/api/v1/query` — schema only, no record reads.
- No internal-network reconnaissance via the leaked scrape-target IPs — the RFC1918 addresses stay on the page; we count them, we do not probe them.

The leak is the finding. Reading the leaked values would shift posture from research to exploitation.
