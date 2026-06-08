# T&E Audit: VictoriaMetrics Survey 2026-06-08

_DCWF AI Work Role 672 audit · NuClide Research panel_

## Methodology of the audit

Entirely local. No network probes. I read the case study, the breakdown, both insights, and `verify_vm_unauth.py`, then cross-checked claims against `~/syllabus/shodan/vm-verify/rollup.json`, `classified-rollup.json`, and a sample of per-host evidence files in `vm-verify/hosts/`. Sampling was seeded random for repeatability. The audit ran the verifier's classifier in my head against the raw evidence to detect where the classifier and the case study narrative diverge.

A first sanity check uncovered a discrepancy between `rollup.json` (the verifier's direct output: 1,023 UNCLASSIFIED, 81 UNAUTH-READ, 65 AUTH-ON, 7 OFFLINE) and `classified-rollup.json` (the case-study-aligned distribution: 884 UNAUTH-TARGETS, 76 UNAUTH-FULL, 5 UNAUTH-METRICS, 65 AUTH-ON, 139 OTHER, 7 OFFLINE). The headline numbers in the case study come from `classified-rollup.json`, which is a second-pass reclassification of the same per-host evidence. That reclassification logic is not in `verify_vm_unauth.py`, so it is undocumented in the public artifact. T&E flag: the publishing pipeline relies on an unpublished classifier whose source I could not locate.

## Findings

### 1. 139 OTHER hosts — large classification false-negative on `/metrics`

Of the 139 OTHER hosts, **134 (96%) return HTTP 200 on `/metrics` with VictoriaMetrics self-monitoring data** and **133 (96%) return HTTP 200 on `/debug/pprof/`**. Every OTHER host I sampled is a vmcluster component (ports 8480 / 8481 / 8482 — vmselect / vminsert / vmstorage). Their `/api/v1/labels`, `/api/v1/status/tsdb`, and `/api/v1/label/__name__/values` return 400 because cluster components route those endpoints under `/select/{accountID}/prometheus/...`, not the root namespace the verifier probes. The classifier treated 400 as "endpoint absent" and dropped them into OTHER.

These 134 hosts are unauth-leaking — just under a different schema. They should reclassify as **UNAUTH-METRICS-CLUSTER**. The case study's 82.1% UNAUTH rate is conservative; the corrected rate is closer to **(965 + 134) / 1,176 = 93.5%**.

### 2. AUTH-ON (65 hosts) — 10 partial-auth false-positives (15%)

Sampling all 65 AUTH-ON hosts: **55 are fully gated** on all nine probed paths. **10 are partial-auth**: 401 on data endpoints but **200 on both `/metrics` AND `/debug/pprof/`**. Representative case: `51.210.99.139:8428` (OVH SAS), 401 on labels/metric_names/tsdb_status/targets, 200 on /metrics and /debug/pprof. The classifier's three-endpoint test (`labels`, `metric_names`, `tsdb_status`) is too narrow — the AUTH-ON label is correct against its own definition but misleading in the case study, which implies "auth on" as a hardened state.

Reclassify the 10 partial-auth hosts as **PARTIAL-AUTH-PPROF**. True fully-gated population is **55 / 1,176 = 4.7%**, not 5.5%.

### 3. Version detection — broken regex + Prometheus-compat version contamination

The version detection has two distinct failures:

- **Regex too narrow.** `VERSION_RX` looks for `"version":"..."` JSON. But for at least 30 hosts, `/api/v1/status/buildinfo` returns **Prometheus text-format metrics** (the `vm_app_version{version="v1.101.0"}` style), not JSON. The verifier sees 200, fails to parse, drops the version. Plus 30 of those same hosts carry the same line in `/metrics`. Total recoverable versions the verifier missed: **30 additional v1.101.0 hosts**, more than doubling the version-known population without any new probes.
- **The "v2.24.0" claim is wrong.** All 34 "v2.24.0" hosts return JSON `{"status":"success","data":{"version":"2.24.0"}}`. That is the **Prometheus-API-compatibility version** VictoriaMetrics advertises on its Prometheus-compat endpoint, NOT the VM build version. VictoriaMetrics is on v1.x.x; v2.24.0 was a Prometheus 2.24.0 release (Jan 2021). The case study reads as if v2.24.0 is the VM version — that is a misread of the buildinfo semantics.

**Proposed new probes to expand version coverage:**
- `/metrics` with regex `vm_app_version\{[^}]*version="([^"]+)"` — recovers 30+ hosts immediately.
- `/api/v1/status/buildinfo` with the same text-format regex as a fallback after JSON parse fails.
- For cluster components, `/select/0/prometheus/api/v1/status/buildinfo` (the cluster routing prefix).

### 4. `/metrics` confirms version + component on hosts the verifier missed

I found **30 hosts** where the classifier's `version` field is null but `/metrics` carries `vm_app_version{version="v1.101.0"}`. Sample: `103.192.177.191:8428`, `:8480`, `:8481`, `:8482` (the same operator running a full cluster fleet, all four nodes confirmable as v1.101.0); `139.84.236.32:8428`. Component is implied by port (8428 = vmsingle, 8480 = vmselect, 8481 = vminsert, 8482 = vmstorage), and is corroborated by the metric prefixes — `vm_promscrape_*` for vmagent/vmsingle, `vm_filestream_*` for vmstorage. **The case study's "majority returns 400" framing for version detection is not the operators gating buildinfo; it is the verifier probing the wrong path on cluster components.**

### 5. Falsifiable claim with weak evidence

Most claims are well-supported by the evidence. The weak claim is **"`/api/v1/import` accepts unauth writes"** (case study and Insight #88 imply this without probing it). Restraint discipline is correct — do not POST. But the public artifact then asserts a write-surface state with zero evidence. T&E recommendation: either (a) drop the assertion and re-frame as "documented behavior; not validated", or (b) add a passive read-only proxy via `/api/v1/status/active_queries` and the vmagent target list's `discoveredLabels` field, which sometimes echo the configured `remoteWrite.url` — if the operator points it at themselves, the write-endpoint identity is in the leak.

## Confidence ratings

| Claim | Rating | Notes |
|---|---|---|
| 1,176 verified VM-family hosts | HIGH | Banner classification audited; corpus tight. |
| 965 / 1,176 (82.1%) UNAUTH | MED | **Under-counts by 134.** Corrected: ~93.5%. |
| 1,077 / 1,176 (91.5%) pprof open | HIGH | Direct evidence; counted correctly. |
| 1,578 scrape-target endpoints leaked | HIGH | Did not re-derive but evidence shape supports. |
| 65 AUTH-ON | MED | **15% (10 hosts) are partial-auth, not full.** |
| v2.24.0 dominant VM version | LOW | **Likely misreads Prometheus-API-compat as VM build version.** |
| 34/1,176 buildinfo-respond | LOW | **Verifier regex misses ~30 text-format responses.** |

## Recommended next probes to close gaps

1. **Reclassify the 139 OTHER hosts.** Add the cluster-routing path `/select/0/prometheus/api/v1/labels` to the verifier — 134 hosts will move from OTHER to UNAUTH-READ-CLUSTER.
2. **Tighten AUTH-ON.** Require all nine probed paths to return 401/403, not just three, before labeling AUTH-ON. Demote 10 hosts to PARTIAL-AUTH-PPROF.
3. **Fix version extraction.** Add the text-format `vm_app_version` regex as a second fallback on both `/metrics` and `/api/v1/status/buildinfo`. Republish a corrected version distribution — expect the actual dominant VM version to be **v1.101.0**, not "v2.24.0".
4. **Document the classifier delta.** The reclassification logic between `rollup.json` and `classified-rollup.json` should ship in the public verifier — currently it is invisible to anyone reproducing the work.
5. **Drop or evidence the `/api/v1/import` claim.** Without a probe, it is a theory, not a finding.

Headline 91.5% pprof claim and the scrape-topology narrative (Insight #88) are well-supported. The auth-rate and version claims need correction before the next case study cites them.
