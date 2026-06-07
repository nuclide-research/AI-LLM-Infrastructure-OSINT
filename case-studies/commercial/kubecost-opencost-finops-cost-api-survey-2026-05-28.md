---
title: "Unauthenticated FinOps Cost APIs Hand Attackers a Free Cluster Recon Map"
date: 2026-05-28
type: survey
sector: commercial
tags: [kubecost, opencost, finops, cost-model, kubernetes, topology-disclosure, auth-on-default, recon-primitive, cat-finops, insight-37]
---

# Unauthenticated FinOps Cost APIs Hand Attackers a Free Cluster Recon Map

_NuClide Research · 2026-05-28 · 67 internet-exposed Kubecost/OpenCost/cost-model APIs answering with no authentication. The cost number is the bait; the cluster topology it ships alongside is the prize._

## Summary

Sixty-seven Kubernetes cost-tooling endpoints (Kubecost 50, OpenCost 14, vendor-undetermined 3) answer their cost-model API with no authentication. Fifty-nine return full per-namespace cluster topology and summed daily spend on a single unauthenticated GET. That is the finding: a FinOps cost sidecar, deployed to watch the wallet, indexes the entire cluster and then serves that index to anyone who asks. An unauthenticated caller gets a labeled map of every workload namespace, the cluster's security control plane (secret stores, admission controllers, EDR/SIEM), a dollar-denominated ranking of which clusters are the high-value production estates, and on 10 host-rows a co-located AI/LLM workload inventory. No credential needs to leak for any of this. The cost API is the map; the namespaces it reveals are the marked destinations.

<!-- ksat-tag:auto-generated:start -->
## DCWF KSAT coverage

Auto-derived from DCWF AI work-role rule files (`ksat-tag`).

- **672 (AI Test & Evaluation Specialist):** K7003, K7004, K7044, S7068, S7070, S7075, T5858, T5904, T5919
- **733 (AI Risk & Ethics Specialist):** K7051, S7067, T5868, T5882, T5893, T5904
- **overlap (Common AI KSATs (all 5 roles)):** K1158, K1159, K22, K6311, K6900, K6935, K7003, K942

<!-- ksat-tag:auto-generated:end -->

All analysis is offline against the captured probe data (`data/finops-probe-results.ndjson`, 67 rows). No outbound requests were made during this verification pass.

## Thesis fit

Confirms the auth-on-default thesis at the FinOps-tooling layer, and extends it. Kubecost and OpenCost ship the cost-model API with no authentication by default; an operator who fronts the dashboard with an ingress but leaves the API port (80/9090/9003) open gets an internet-exposed data API. The new angle: this is a telemetry sidecar whose entire job is to enumerate the cluster, so when its API is open it leaks more structural intelligence than the AI service it sits beside. The cost tool out-recons the workload.

On Insight #37 (asymmetric UI-gated-but-API-open auth): this population does NOT exhibit the asymmetry. `asymmetric==false` on every row that carries the field, and `ui_status==200` everywhere the UI was reachable. These are open-UI-AND-open-API, not UI-walled-with-an-open-API-behind-it. The recon-primitive finding below is therefore a distinct corollary, not a re-confirmation of #37. See "Methodology — what this survey adds".

---

## Recon → discovery → verification → impact

**Recon.** Shodan harvest for Kubecost/OpenCost serving signatures across ports 80, 9090 (Kubecost frontend nginx, not Prometheus), and 9003 (OpenCost API). aimap v1.9.38 fingerprinted the population: 73 Kubecost service-hits + 22 OpenCost service-hits, nothing else. No LLM servers, vector DBs, or model servers in the aimap layer — the corpus is a pure Kubernetes cost-tooling fleet.

**Discovery.** The probe (`kubecost-opencost-probe.py`) hits `/model/allocation?window=1d&aggregate=namespace` and `/model/clusterInfo`. On 59 hosts the allocation endpoint returned the namespace topology and a summed daily cost in the same JSON object. The realization is that the response is a complete cluster map: namespace inventory, security-tooling inventory, and spend, all unauthenticated.

**Verification.** Confirmation is gated on the service's own JSON shape `{"code":200,"data":[...]}` (`is_costmodel_json`), not a bare HTTP 200, so an SPA or a redirect cannot false-positive. `agg_cost_1d` is the real summed `totalCost` from the returned windows, not an estimate. Namespace names are the literal `aggregate=namespace` keys. The Azure `account` field is parsed from the live clusterInfo body. helmValues is recorded presence-only (status 200 + byte-size); the body is discarded.

**Impact.** Pre-attack reconnaissance at population scale, free and unauthenticated. The attacker maps the control plane to plan around, ranks the population by spend to choose a foothold, and on AI-adjacent hosts finds the litellm/vllm/kubeflow/mlflow/flowise namespaces to target. Read-only information disclosure — no code-exec, no credential theft, no data-write was observed or attempted.

---

## Per-finding entries

### F1. Cost-model API as a pre-attack reconnaissance primitive — 59 hosts — HIGH

#### What was found
59 of 67 rows satisfy `auth_state==OPEN_API AND namespace_count>0 AND namespaces[] non-empty AND confirmed==true`. The `/model/allocation` response returns the full per-namespace topology with no credential. Verified examples: 34.132.86.54 (60 namespaces), 34.152.57.221 (97 namespaces), kc5-aws on 18.224.144.23 and 3.130.111.241 (40 namespaces each).

#### Why it is bad
**Verified:** the complete workload-namespace inventory of the cluster is readable by an anonymous caller. **Inferred (not exercised):** that inventory is the input to every subsequent targeting decision. The eight non-matching rows are 7 OPEN_API with empty namespaces and 1 UI-only host.

#### Tier
HIGH — verified information disclosure of full cluster topology, read-only, no auth.

### F2. The cost API enumerates the cluster's SECURITY control plane — 33 hosts — MEDIUM

#### What was found
Among the 59 data-bearing rows, the namespace arrays name the secret stores and detection tooling outright. Exact-string counts: cert-manager 20, external-secrets 9 (+1 external-secrets-system), gatekeeper-system 6, istio-system 6, amazon-guardduty 4, kyverno 3, calico-system 2, tigera-operator 2, HashiCorp Vault on 2 hosts (20.71.71.254 runs vault + vault-central + vault2026; 51.8.60.216 runs vault), wazuh 1, wiz 1, CrowdStrike Falcon 1 (falcon-system + falcon-kac on 100.50.177.179), ztna1r1 2. kube-system on all 59.

#### Why it is bad
The attacker learns which secret stores, admission policies, and EDR/SIEM to plan around before the first packet. Namespace NAMES only — contents were not read.

#### Tier
MEDIUM — verified architecture-of-controls disclosure, read-only.

### F3. agg_cost_1d turns the population into a dollar-ranked target list — MEDIUM

#### What was found
`agg_cost_1d` is the real summed `totalCost`. Top hosts: 34.180.48.42 $6,836.90/day (12 ns), 34.132.86.54 $1,457.74 (60 ns), 34.205.170.148 $405.54 (29 ns, **dev** cluster g2r1), kc5-aws $279.95 on two IPs, 47.117.109.26 $206.23. Class A sum: $10,528.83/day.

#### Why it is bad
Spend is a proxy for production scale, so the population sorts itself by blast-radius for free. **Honest caveat:** the proxy is noisy. The #3-ranked host is a development cluster, and the single largest topology (34.152.57.221, 97 healthcare/DICOM namespaces) reports $-0.0/day, so pure-spend ranking buries the richest topology. Production ratio is 51/67.

#### Tier
MEDIUM — amplifier of F1; target-ranking intelligence, not a breach.

### F4. Co-located AI/LLM namespaces tie the exposure to the AI-infra thesis — 10 host-rows / ~6 operators — MEDIUM

#### What was found
aicore + aiexpert on kc5-aws (2 IPs, full control plane co-located); litellm + qdrant + vllm-inference on 3.0.69.229; kubeflow + mlflow + litellm + vllm-test on 163.7.145.233 (five per-user `auckland.ac.nz` / `nesi.org.nz` namespaces); flowise + a 97-namespace DICOM/HL7 pipeline on 34.152.57.221; jupyter on three IPs (32.199.28.25 / 34.226.51.152 / 98.85.248.97); kagent on 47.236.162.45; aicore on 34.205.170.148.

#### Why it is bad
Same auth-on-default failure class as the broader AI-infra survey. The cost sidecar indexes the whole cluster, so it becomes a higher-value recon target than the AI service it sits beside. **Correction to prior framing:** 163.7.145.233 is the richest AI-adjacent target and the only one disclosing per-user identities, but it is NOT the only AI target.

#### Who it affects
163.7.145.233: University of Auckland / NeSI national research compute (NZ), HIGH-confidence attribution from the embedded `auckland.ac.nz` / `nesi.org.nz` per-user namespace strings.

#### Tier
MEDIUM — verified topology + per-user identity disclosure; AI-service exploitability NOT exercised.

### F5. OpenCost open API returning real topology + cost — 13 hosts — MEDIUM

#### What was found
13 of 14 OpenCost rows are confirmed open with topology + cost (the 14th, 158.220.105.135, is UI_ONLY_NO_API). 12/13 carry `profile=development`. 52.209.110.72 is the lone host confirmed via the dedicated :9003 API port. Namespace leaks include 51.8.60.216 (vault/gitlab/sonarqube/forgeops/superset).

#### Tier
MEDIUM — verified read of internal namespace topology + per-namespace spend, read-only.

### F6. Vendor-undetermined cost-model: 2 data-exposed, 1 open-but-empty — MEDIUM / LOW

#### What was found
34.205.170.148 (29 ns incl. external-secrets/kafka/aicore/argocd, $405.54/day) and 13.59.104.55 (16 ns incl. clickhouse/opencost, $10.88/day) = verified data exposure (MEDIUM). 51.8.0.154 (Azure eastus, production) = OPEN_API but namespaces/agg_cost absent = surface open, no data (LOW). Vendor stays undetermined because the UI body matched neither the OpenCost favicon nor the Kubecost helmValues signature; null != negative.

#### Tier
MEDIUM (2) / LOW (1).

### F7. helmValues endpoint exposed — PRESENCE ONLY, secret body NOT fetched — 49 hosts — LOW

#### What was found
49 of 67 rows have `helmvalues_exposed==true` (all Kubecost, all OPEN_API), byte-size 5,948–20,684. The probe issues `GET /model/helmValues`, checks `status==200 and size>200`, and DISCARDS the body. No body/secret/credential/token/key field exists anywhere in the dataset.

#### Why it is bad
The Kubecost `/model/helmValues` endpoint typically returns the Helm values blob, which CAN carry cloud credentials. That is the endpoint's potential, not what was observed. **The secret content was never fetched.**

#### Tier
LOW — endpoint exposed, secret content NOT exercised. NOT a credential leak. Confirming content requires a Step-6 re-authorized single-host body fetch (gated outward action, not performed).

### F8. /model/clusterInfo cluster metadata disclosure — 45+ hosts — LOW

#### What was found
clusterInfo returns provider, provisioner (EKS/GKE/AKS), region, k8s version, prod/dev profile, and cluster_id with code 200, including on 5 rows with zero namespaces. cluster_id is the install default "cluster-one" on 44/65 rows.

#### Why it is bad
Generic cloud metadata, read-only. **Correction to prior framing:** there is no "project" field disclosing GCP project IDs; those values are absent from the data. The only true identity discloser is the Azure account UUID (F9).

#### Tier
LOW.

### F9. Azure cloud-account identifier (UUID) leaked unauthenticated — 11 hosts — LOW

#### What was found
11 rows carry a non-null `account`. All 11 are Azure; every non-Azure row is account=null. Parsed from the live clusterInfo body (verified primary-source). Example: 4.234.27.7 -> a425617f-85d1-4efe-95c8-7fe0bf2e09da.

#### Why it is bad
An identifier, not a credential — grants no access alone, and an Azure subscription ID is semi-public by design (appears in ARM paths). 9 of 11 carry co-located data; 2 (51.8.0.154, 48.216.149.154) are account-only with no scraped topology.

#### Tier
LOW — attribution enrichment on the existing open-API population, not a standalone vuln.

### F10. OpenCost has no helmValues endpoint — INFO

#### What was found
14 OpenCost rows show `helmvalues_exposed:false` (bytes:25, a short not-found body) or omit the key; the OpenCost probe path never queries `/model/helmValues`. The CNCF OpenCost build carries no helmValues secret endpoint, so its surface is topology+cost only.

#### Why it is bad
Structural fingerprint, not an exposure. **Caveat:** bytes:25 is NOT a clean OpenCost-vs-Kubecost discriminator (Kubecost host 34.34.221.204 also returns false/bytes:25), and "CNCF build" provenance is inferred, not a field.

#### Tier
INFO.

---

## Tier table

| Class | Count | Tier | Verified basis |
|---|---|---|---|
| Open cost-model API + real topology + cost (recon primitive) | 59 hosts | HIGH | `auth_state==OPEN_API` + `namespace_count>0` + non-empty `namespaces[]` + `confirmed==true`; gated on service JSON `{"code":200,"data":[...]}` |
| Class A subset: topology + positive daily spend | 57 hosts | HIGH | Above + `agg_cost_1d>0`; summed totalCost = $10,528.83/day |
| Class A1: topology verified, spend field <=0 | 2 hosts | HIGH | `namespace_count>0` (19, 97) but `agg_cost_1d` -23.99 / -0.0; topology verified, spend NOT |
| Security control-plane namespaces enumerated | 33 hosts | MEDIUM | Literal `namespaces[]` strings: vault/cert-manager/falcon/wiz/wazuh/kyverno/gatekeeper/guardduty |
| Dollar-ranked target list (spend proxy) | 57-host set | MEDIUM | `agg_cost_1d` real summed value; top $6,836.90/day |
| AI/LLM workload co-location | 10 host-rows / ~6 operators | MEDIUM | Literal AI namespaces (litellm/vllm/kubeflow/mlflow/flowise/aicore) in `namespaces[]` |
| OpenCost open API + topology + cost | 13 hosts | MEDIUM | 13/14 OpenCost rows OPEN_API + `namespace_count>0` + `agg_cost_1d` present |
| cost-model (vendor-undetermined) data-exposed | 2 hosts | MEDIUM | OPEN_API + 29/16 namespaces + cost>0 |
| **helmValues endpoint exposed (secret content NOT exercised)** | **49 hosts** | **LOW** | `helmvalues_exposed==true` = status-200 + byte-size>200 ONLY; **body discarded, never fetched — NOT a credential leak** |
| /model/clusterInfo metadata disclosure | 45+ hosts | LOW | clusterInfo code 200: provider/region/version/profile/cluster_id |
| Azure account UUID leaked | 11 hosts | LOW | Non-null `account`, all Azure, parsed from clusterInfo body |
| Surface-open, no data scraped | 7 hosts | LOW | OPEN_API but `namespace_count==0`/absent, cost 0/absent |
| cost-model open, empty payload | 1 host (51.8.0.154) | LOW | OPEN_API, namespaces/agg_cost absent |
| UI-only, no reachable API | 1 host (158.220.105.135) | INFO | `confirmed==false`, `auth_state==UI_ONLY_NO_API` |
| OpenCost has no helmValues endpoint | structural | INFO | 14 OpenCost rows false/bytes:25 or key absent |

No CRITICAL tier is supportable: no row carries hard proof of code-exec, credential theft, or data-write.

---

## Cross-survey analysis

Dedup matters. The 67 IPs collapse to ~38 distinct operators; the 59 data-bearing rows collapse to 46 distinct `(cluster_id, agg_cost_1d, namespace-set)` signatures. Eleven clusters front the same exposure on multiple IPs (e.g. kc5-aws on 18.224.144.23 + 3.130.111.241 at $279.95/day each; a $25.14/day airflow+jupyterhub cluster on three IPs). Host counts in findings are per-IP (what was probed); severity is per-cluster-exposure.

Notable attributed operators: an MSP/SD-WAN/ZTNA managed-network provider (msp4xiq/sdwan/ztna1r1/xcpgdc); a Ripley LATAM retail estate (cl-/pe-customer-* + cl-ripley-tarjetero, $1,457.74/day); a teleradiology operator (DICOM/HL7/fovia pipeline, 97 namespaces); an Indonesian regional-gov/HR/utility SaaS (bimaphr-*/mloket-pdam/scada); and University of Auckland / NeSI research compute (kubeflow per-user namespaces). Two hosts sit in AWS GovCloud (us-gov-west-1).

Provider spread: AWS 32, GCP 12, Azure 11, custom 5, Alibaba 2, OVH 2, Oracle 1, null 2. Profile: production 51, development 14, null 2. Port: 80 x39, 9090 x27, 9003 x1.

## Methodology — what this survey adds

**Candidate Insight: the unauthenticated FinOps cost-model API is a pre-attack reconnaissance primitive, distinct from Insight #37.**

A telemetry/cost sidecar whose function is to index the entire cluster, when its data API is open, leaks more structural intelligence than the workloads it measures: full namespace topology, the security control-plane inventory, and a spend-ranked target list — independent of and prior to any secret leak. This is NOT Insight #37: #37 is about UI-vs-API auth asymmetry, and this population has no asymmetry (`asymmetric==false`, `ui_status==200` everywhere; open-UI-AND-open-API). The novel claim is the class-of-mistake: a cost/observability sidecar is a higher-value recon target than the service it monitors, because indexing-the-cluster IS its job. If a later survey finds the same pattern on other observability sidecars (Prometheus federation, OpenTelemetry collectors, Grafana data sources), this generalizes to "telemetry sidecars are cluster-wide recon oracles." Stated honestly: the recon-primitive framing is a genuine new corollary; the underlying open-API exposure is the auth-on-default thesis re-confirmed at FinOps scale.

## Honest negative space

- **helmValues content is NOT proven.** 49 hosts expose the endpoint (status + byte-size), but the body was never fetched. The Helm values blob CAN contain cloud credentials; this survey does not show that it does on any host. Upgrading to a credential leak requires a single-host re-authorized fetch.
- **Snapshot is ~1 day stale.** aimap scan 2026-05-28T23:17:43Z, probe data same date. Hosts may have closed, rotated, or moved.
- **Spend ranking misfires.** A dev cluster ranks #3 by cost; the richest topology reports $-0.0/day. Spend is a noisy blast-radius proxy.
- **Three vendors undetermined.** The cost-model class could not be disambiguated (OpenCost CNCF vs Kubecost-derived vs other fork) offline.
- **Attribution ceiling.** The aimap HTTP/TLS layer carries no operator-identifying signal (no cert subjects, generic dashboard titles). All attribution rests on namespace names, cluster_id, Azure tenant GUID, and provider/region. Eleven Azure GUIDs are hard distinct-org anchors but cannot resolve to a named org offline.
- **VisorScuba policy mismatch.** All 134 ledger nodes fired `[AI.C1] Unauthenticated Ollama` — the embedded baseline has no FinOps Rego module. The 0/10 score is formally correct for unauthenticated exposure but the violation label is wrong for this service class.
- **BARE coverage gap.** finops-001 (Kubecost cost-API unauth) scored 0.547, one tick below the 0.55 sentinel; finops-003 (OpenCost) 0.492. The pure cost-API exposure class has no high-confidence MSF-module neighbor; only the helmValues credential-exposure framing crossed the threshold.

## Gated outward follow-ups (require fresh target contact — VPN + explicit go)

These cross the offline line and were NOT performed:
1. One-sample helmValues content confirmation on a single Kubecost host to prove/disprove credential presence (Step-6, single re-authorized GET).
2. cert-pivot attribution via VisorGraph / CT logs to resolve the 11 Azure tenant GUIDs and the unattributed operators to named orgs.
3. Shadow-Prometheus / kubelet adjacency sweep on the same IPs per Insight #62 (tested in this corpus on 9090 and did NOT hold — 9090 is Kubecost nginx, not Prometheus — but worth a dedicated :9100/:10250/:3000 sweep).
4. Direct enum of 163.7.145.233's litellm/mlflow/vllm-test services (AI-service exploitability, currently inferred only).
5. cost-model vendor disambiguation probe (server header, `/model/prometheusQuery` presence, helmValues existence test) on the 3 undetermined hosts.

## Toolchain provenance

```
JAXEN (Shodan harvest) -> aimap v1.9.38 (fingerprint, 67 targets, 95 service-hits)
  -> kubecost-opencost-probe.py (verify: /model/allocation + /model/clusterInfo + /model/helmValues presence)
  -> finops-visorlog-adapter.py + visorlog ingest (ledger: nuclide.db, 67 rows)
  -> visorscuba assess (134 nodes, 0/10 — policy-class mismatch noted)
  -> BARE --min-score 0.4 (coverage gap confirmed for pure cost-API exposure)
  -> offline verification pass (this document)
```

## Outward verification + attribution (2026-05-29, authorized, run through Mullvad)

The offline survey above drew the line at host contact. Two follow-ups then crossed that line under explicit authorization, run through a VPN exit. Both results are recorded here; the offline body is unchanged.

### A. helmValues credential class: confirmed live on one cluster

F7 above tiered helmValues LOW because the body was never fetched. One re-authorized single-cluster fetch now resolves the class. On kc5-aws (both fronting IPs 18.224.144.23 and 3.130.111.241, identical 19,304-byte body, same content hash, so one cluster behind two LoadBalancers), `GET /model/helmValues` returns HTTP 200 with no auth and includes a live `grafana.adminPassword`: 14 characters, not a placeholder or a Helm template. The value was not read or stored; only its length and a SHA-256 prefix were recorded. The other secret-named keys in the blob are references, not values: `federatedStorageConfigSecret` and `cloudIntegrationSecret` hold Kubernetes secret object NAMES, and the two `bearer_token_file` entries hold filesystem PATHS. So this is one genuine inline credential, not a credential dump.

Honest scope: the helmValues credential leak class (macchaffee 2021) is confirmed still live in the field. It is proven on one cluster. The other 48 helmValues-exposed hosts remain presence-only and are not upgraded. Per-host magnitude across the set is not measured.

### B. Shadow adjacency sweep: negative

aimap swept all 66 confirmed IPs on the adjacency ports (3000 Grafana, 9100 node-exporter, 10250 kubelet, 2379 etcd, 6443 API server, 9093 Alertmanager, and others). Zero adjacent surfaces answered. Only the cost service on 9090 was reachable. Insight #62 does not hold for this population: the LoadBalancer fronts only the cost service, and the kubelet/etcd/API server stay internal. This sharpens the survey rather than weakening it. The cost API is the sole external door, and it alone leaks the whole topology. Result file: `data/finops-shadow-sweep.json`.

### C. Operator attribution (osint-platoon, passive only)

A passive osint-platoon run (crt.sh, public DNS/PTR, RDAP/ASN, vendor docs, cached Shodan; no host contact) resolved the SASE-vocabulary cluster:

- **18.224.144.23 (kc5-aws) and 34.205.170.148 (g2r1) = Extreme Networks, Inc. (NASDAQ: EXTR)**, ExtremeCloud IQ / Platform ONE. Two nodes of one multi-region AWS EKS estate. Per-host HIGH, overall MEDIUM. The leaked namespace taxonomy mapped comprehensively to Extreme product vocabulary, then corroborated against live operator endpoints: `uz-redirector` to `uz-rd.extremecloudiq.com` (live login SPA), `msp4xiq` to `msp.extremecloudiq.com`, `nvo` to `extremeplatformone.com/nvo-client`, `sdwan` to `api.extremecloudiq.com/sdwan-api`; crt.sh region-coded `*.extremecloudiq.com` certs and Extreme's own ZTNA user guide bind the `va2-uz`/`oh`-region codes to AWS us-east-1 / us-east-2.
- The confirmed Grafana credential in part A therefore sits on an Extreme Networks production control-plane cluster.
- **34.180.48.42** (the $6,837/day spend leader): attribution NONE. Sole candidate Scoutflo eliminated on scale (7-person pre-seed cannot generate that GCP spend) and stack (Scoutflo is AWS-only per its own GitHub/GitBook; target is GCP/GKE). No operator named from a namespace token alone.
- **47.117.109.26** (Alibaba cn-shanghai): LOW, unnamed tenant; Aliyun is the provider, not the operator.

Method note: namespace-taxonomy clustering resolved the two Extreme hosts to one operator from leaked namespace names alone, before any passive lookup. That is the `ns-attribute` primitive, validated against live data.

Per-target evidence chains: `data/findings-breakdown-34.180.48.42.txt` and the platoon run output. Full session narrative: `analysis/2026-05-29-finops-cost-api-aar.md`.

## See also

- `data/platform-intel/kubecost-opencost-finops-osint-2026-05-28.md` (prior framing / intel doc — superseded by this post-verification result on helmValues tiering and the #37 claim)
- `data/finops-findings-breakdown.txt` (per-tier finding counts + rejected-claim ledger)
- `data/finops-probe-results.ndjson` (ground truth, 67 rows)
