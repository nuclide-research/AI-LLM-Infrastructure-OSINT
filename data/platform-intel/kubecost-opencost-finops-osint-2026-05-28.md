---
title: "Platform Intel: Kubecost / OpenCost (K8s FinOps cost-allocation)"
date: 2026-05-28
type: platform-intel
category: k8s-finops-cost-allocation
status: pre-assessment-complete
thesis_relevance: auth-off-by-default architecture, no-CVE (documentation-only fixes) — pure thesis-confirmation surface
---

# Kubecost / OpenCost — Pre-Assessment Platform Intelligence

Stage −1 pre-assessment OSINT (web/docs/CVE/source research only; no live-host contact) for the **K8s FinOps cost-allocation** slice. This slice was NOT covered by the 2026-05-19 cost/billing survey (which covered Phoenix/LangSmith/Lago/Helicone/OpenMeter → Insight #37). Kubecost + OpenCost are the genuine gap.

**One-line thesis framing:** both ship **no authentication by default**, both were fixed via documentation rather than code after prior disclosures, and both expose a cost-model API that leaks cluster cost allocation, namespace/workload topology, and cloud-account attribution. This is the auth-on-default thesis in its purest form. Insight #37 (asymmetric dashboard-vs-API auth) is the operative lens: an ingress fronting the UI does not gate the `/model/` (Kubecost) or `:9003` (OpenCost) cost-model API.

---

## Platform disambiguation (load-bearing)

| Signal | Standalone OpenCost | Kubecost |
|---|---|---|
| API base path | `/allocation` (NO `/model/` prefix) | `/model/allocation` |
| Primary API port | **9003** | **9090** |
| UI port | 9090 (nginx SPA) | 9090 (nginx, same pod as cost-model) |
| k8s service name | `opencost` | `kubecost-cost-analyzer` |
| Verification GET | `:9003/allocation?window=1d` | `:9090/model/allocation?window=2d` |
| Response top-level | `{"code":200,"data":[...]}` | `{"code":200,"data":[...]}` (same) |

The `/model/` path prefix + port are the discriminator. Kubecost embeds OpenCost's cost-model, so metric names overlap (`kubecost_*` prefix appears in both — OpenCost inherited it from Kubecost's code).

---

## 1. Auth posture (the thesis-confirming fact)

**Kubecost:** auth OFF by default. Helm chart (`cost-analyzer-helm-chart` values.yaml): `saml.enabled=false`, `oidc.enabled=false` (both enterprise-license-gated), `ingress.enabled=false`, `service.type=ClusterIP port 9090`. The cost-model router (`cost-model/pkg/costmodel/router.go`) registers every route with **no auth middleware**; the only gated routes are `POST /serviceKey` and the `/cloud/config/*` admin routes, and `adminAuthMiddleware` only enforces when the operator explicitly sets `ADMIN_TOKEN` (not set by default). Security-conscious deploy = operator-applied ingress + oauth2-proxy / nginx basic-auth / ALB Cognito. None are defaults.

**OpenCost:** NO built-in auth. swagger.json defines no security schemes; the Backstage plugin docs state plainly "OpenCost does not have any authentication at the API level." Helm `adminToken.enabled=false` default. Hardened deploy = authenticating ingress / NetworkPolicy / KubeRBACProxy (OpenShift).

**Both:** default `service.type=ClusterIP` gives incidental protection ONLY until an operator exposes via LoadBalancer/NodePort/ingress — at which point the full API is open. The exposed population is exactly the operators who did that without adding an auth overlay.

---

## 2. Verification primitives (definitive, read-only, zero side-effect)

### Kubecost
```
GET http://<host>:9090/model/allocation?window=2d&aggregate=namespace&accumulate=true
```
Populated 200 → `{"code":200,"data":[{"kube-system":{"properties":{"cluster":"<name>","namespace":"kube-system"},"cpuCost":..,"ramCost":..,"totalCost":>0,...}}]}`
- `code==200` + non-empty `data` + any `totalCost>0` → real cluster cost data exposed.
- `code==200` + empty/zero data → open API, no scraped data yet (still a finding).
- 401/403 → auth layer present. 200 HTML login → frontend auth; probe `/model/` backend directly anyway (Insight #37).

**Attribution probe (zero data):** `GET :9090/model/clusterInfo` → cloud provider + account + region + provisioner (EKS/GKE/AKS).
**Credential-leak probe (HIGH severity, macchaffee 2021, unpatched):** `GET :9090/model/helmValues` → full install-time Helm values, can include cloud API keys / passwords if passed via values. **Enumerate presence; do not extract secret bodies beyond confirming the leak class.**

### OpenCost
```
GET http://<host>:9003/allocation?window=1d&aggregate=namespace
```
Populated 200 → same `{"code":200,"data":[{ns:{...cpuCost,ramCost,totalCost...}}]}` shape.
Fallback if only 9090 exposed: `GET :9090/allocation?window=1d` (UI nginx proxies to 9003 depending on BASE_URL).
**Secondary confirm:** `GET :9003/metrics` containing `kubecost_cluster_info` or `node_cpu_hourly_cost` → OpenCost exporter regardless of allocation-data state.

---

## 3. Data exposure class

Cost-model API returns: namespace / pod / controller / label cost allocation; cpuCost/ramCost/pvCost/gpuCost/networkCost/totalCost + efficiency metrics; cluster name, cloud provider, account ID, region (`/clusterInfo`); cloud invoice data when billing integration configured (`/cloudCost`: AWS CUR, GCP billing export, invoiceEntityID/accountID). Kubecost additionally: `/model/allPods|allNodes|allDeployments` = full k8s manifests (notveg.ninja 2024); `/model/helmValues` = install secrets.

Severity tiering (per Insight #37):
- UI gated + cost-model API open = **MEDIUM-HIGH** (read of cluster cost/topology)
- + `/cloudCost` returning real invoice data = **HIGH** (cloud-account financial exposure)
- + `/helmValues` leaking credentials (Kubecost) = **HIGH/CRITICAL** (credential exposure, pivot to cloud account)
- Open UI + open API + populated data = **CRITICAL**

---

## 4. CVEs / prior research

**Zero CVEs, zero GHSAs, not in CISA KEV** for either platform's core. Vendor position: authentication is the operator's responsibility; both prior disclosures (macchaffee 2021 `/api/allPods`+`/helmValues`; notveg.ninja 2024 `/model/all*`) were fixed documentation-only, no code-level auth added. Nuclei: `http/misconfiguration/unauth-kubecost.yaml` exists (dashboard title detection only, severity medium); no OpenCost template. This no-CVE-but-open-by-architecture status IS the finding — it is the thesis, not a patch gap.

Related (no CVE): `kubecost/gcp-marketplace#9` — three service accounts with wildcard verb access on pods/nodes/clusterroles → privesc to cluster-admin via ClusterRoleBinding; `#2409` — `REMOTE_WRITE_PASSWORD`/`CLOUD_PROVIDER_API_KEY` plaintext env vars.

---

## 5. Fingerprint / dorks (ranked, FP risk)

### Kubecost
1. `http.favicon.hash:611531125` — lowest FP (confirmed in prior research)
2. `http.title:"Cluster Overview | Kubecost"` — exact title, modern versions
3. `http.title:"Kubecost"` — broader, older installs **[harvested 2026-05-28 = 116]**
4. `ssl.cert.subject.cn:kubecost` / `:"cost-analyzer"` — VisorGraph cert pivot for TLS-terminated exposures
- DO NOT use bare `port:9090` (Prometheus/Cockpit collision); title/favicon is the discriminator.
- ETag empirically carries version on Kubecost frontend (observed 2.8.0 / 3.0.6-eks-addon-8 / 3.1.3); agent flagged unconfirmed-from-docs — treat as strong-but-verify version signal.

### OpenCost
1. `http.html:"opencost" http.headers:"ETag: \"1.96.0\""` — ETag is build-time-static in opencost-ui nginx template; low FP **(explains the 1.96.0 seen across all harvested hosts)**
2. `"kubecost_cluster_info" port:9003` / `"node_cpu_hourly_cost" port:9003` — metric-name dorks, low FP, if Shodan indexed `/metrics`
3. `http.html:"opencost"` — broad **[harvested 2026-05-28 = 31, ~9 genuine]**
4. favicon `2140086526` — MED confidence (Parcel build-hash may vary), supporting signal only
- Run dorks on BOTH 9003 (API, definitive) and 9090 (UI, broader pop).

### FP EXCLUSION
`opencost.de` (Universität Regensburg) = German "openCost Registry" construction-cost data standard, zero relation to CNCF OpenCost. Exclude by hostname, German-language body ("Bauwerksdaten"/"Leistungsverzeichnis"), or absence of `{"code":200}` JSON / `node_cpu_hourly_cost` metric. (Confirmed FP in 2026-05-28 harvest: 132.199.150.68.)

---

## 6. Shadow surface (IP-direct, Insight #12) + VisorGraph pivot

Both co-deploy a monitoring stack. Adjacent ports for the shadow sweep on every confirmed host:

| Port | Service | Value |
|---|---|---|
| 9090 | Kubecost UI / OpenCost UI / Prometheus | disambiguate by body (`/-/healthy`, `<title>Prometheus`) |
| 9003 | OpenCost API | primary OpenCost target |
| 3000 | Grafana | default creds `admin/admin` common adjacent finding |
| 8080 | kube-state-metrics | `kube_pod_info` / `kube_secret_info` = full topology + secret NAMES |
| 9093 | Alertmanager | leaks alert rules |
| 10250 | kubelet | separate finding class |
| 6443 | kube-apiserver | separate finding class |

**The Prometheus instance is the amplifier** (Sysdig research): exposed Prometheus `/api/v1/targets` discloses internal service topology; `kube_secret_info` leaks secret names; `kube_pod_info` leaks workload layout. Highest-information-density leak on the shadow sweep.

**VisorGraph seed:** parse `kubecost_cluster_info{cluster_id="..."}` from `/metrics`; pivot the cluster_id / ingress CN to CT logs. Direct-IP TLS (no SNI) on 443/6443 surfaces the cloud account's OV/EV cert.

---

## 7. Next steps (correct methodology order)

1. **Verify** the harvested population (Kubecost 116, OpenCost ~9) with the primitives above — read-only, restraint ethic: enumerate namespace/cluster names + confirm `totalCost>0`, do NOT extract `/helmValues` secret bodies beyond confirming the leak class. **[outward-facing — gated on Nick's go]**
2. **aimap gap:** no fingerprint exists for either (Insight #20). Build a `kubecost`/`opencost` fingerprint (port + `/model/allocation` vs `/allocation` + `{"code":200}` + `totalCost` conjunct) → productize → re-run (manual→productize→re-run discipline).
3. **Attribute** (VisorGraph cert-pivot), **Classify** (aimap-profile), **Ledger** (VisorLog), **Score** (VisorScuba), **Codify** (candidate insight: FinOps cost-model API auth-off-default + helmValues credential-leak chain).

## Sources
Kubecost: cost-analyzer-helm-chart values.yaml; cost-model router.go; macchaffee.com 2023 disclosure; wiki.notveg.ninja 2024 disclosure; nuclei-templates unauth-kubecost.yaml; kubecost/gcp-marketplace#9.
OpenCost: opencost.io docs (install/api/metrics); opencost-helm-chart values.yaml; opencost-ui nginx template; swagger.json; Backstage opencost plugin; Sysdig exposed-Prometheus research.
