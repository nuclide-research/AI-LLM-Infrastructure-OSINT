# 29. Workflow Orchestration (K8s-Native)

_NuClide Research · 2026-05-27_
_Pre-assessment OSINT complete. Survey: IN PROGRESS._

K8s-native workflow orchestration platforms expose REST APIs and UI dashboards that carry full pipeline state, resolved parameters (including credentials), artifact access, and in misconfigured deployments, unauthenticated container execution.

---

## Argo Workflows

**Auth posture:** Tier A* — `--auth-mode=server` disables all credential requirements. The official quickstart manifest explicitly ships both `--auth-mode=server` and `--auth-mode=client` (hybrid), preserving unauthenticated access on the development path. Binary default (v3.0+) is `client` (safe), but the quickstart path is the dominant exposure vector.

**Confirmed population:** ~3,000 unauth instances (E.V.A Security, November 2024 internet scan via `/api/v1/userinfo` probe).

**Source:** `gatekeeper.go` explicitly appends empty string to `authorizations` when no header is present — server mode always matches, regardless of input. The bypass is by design for the server auth mode.

| Shodan Query | Notes | FP Risk |
|---|---|---|
| `port:2746 http.title:"Argo"` | Canonical port (Argo-exclusive) + correct page title. **Primary dork.** | Low |
| `http.html:"assets/favicon/favicon-32x32.png" "noindex"` | Distinctive HTML body strings. Catches reverse-proxied instances (no port lock). | Low |
| `ssl.cert.issuer.cn:"Argo Workflows"` | Default self-signed cert issuer. Confirmed Shodan-indexable. | Low |
| `"gitTag" "gitTreeState" "compiler" "platform"` | Unique field combination from `/api/v1/version` JSON response. | Low |
| `port:2746 "argoproj"` | JS bundle string + port lock. Secondary. | Low |
| `port:2746 http.title:"Argo Workflows"` | **WRONG — hits docs/readthedocs sites, not live servers.** Live page title is `"Argo"`. Do not use. | High |

**⚠️ Nuclei template `argo-workflows-unauth.yaml` has incorrect `shodan-query: title:"Argo Workflows"` in metadata.** The correct live-server title is `"Argo"`.

### Verification Probe

Single request, definitive — no false-positive risk:

```bash
# Unauth detection — server mode confirmed if serviceAccountName is non-empty
curl -sk https://TARGET:2746/api/v1/userinfo | jq .

# Response: server mode (UNAUTH)
{"serviceAccountName":"argo-server","serviceAccountNamespace":"argo","subject":"system:serviceaccount:argo:argo-server","issuer":"kubernetes/serviceaccount"}

# Response: auth enforced
{}
```

### Fingerprint (aimap — not yet implemented as of 2026-05-27)

```
Port:     2746
Probe:    GET /api/v1/version
Match:    status=200 AND body_contains("gitTag") AND body_contains("gitTreeState") AND body_contains("compiler")
Auth:     GET /api/v1/userinfo → json_field serviceAccountName non-empty
DeepEnum: namespace sweep (argo, kubeflow, ml-pipeline, training, data-science, mlflow)
          CVE-2026-28229 probe (Authorization: Bearer nothing → /api/v1/workflow-templates/{ns})
          version extraction → CVE window classification
```

### High-Value Endpoints (Unauth Instances)

| Endpoint | Severity | Data |
|---|---|---|
| `POST /api/v1/workflows/{namespace}` | **CRITICAL** | Arbitrary container execution — cryptominer entry point (Intezer 2021) |
| `POST .../pods/{pod}/exec` | **CRITICAL** | Unauthenticated exec into running pods; argo-server SA has `pods/exec` cluster-wide |
| `GET /api/v1/workflows/{namespace}` | HIGH | Full spec + `status.nodes` resolved values; credentials passed as params appear in plaintext |
| `GET .../log` | HIGH | Container stdout/stderr including credentials printed by pipeline steps |
| `/artifacts/` all endpoints | HIGH | Full artifact download (model weights, datasets, pipeline outputs) via server's S3/GCS credentials |
| `GET /api/v1/workflow-templates/{namespace}` | HIGH | Template definitions; CVE-2026-28229: `Authorization: Bearer nothing` exfils embedded K8s secrets |
| `GET /api/v1/userinfo` | LOW | Confirms unauth; leaks SA identity |
| `GET /metrics` | LOW | Workflow counts, version, queue depths; `argo_workflows_info` label contains version string |

### CVE Coverage

| CVE | Impact | Threshold |
|---|---|---|
| GHSA-rc7p-gmvh-xfx2 (no CVE) | Server-mode unauth → arbitrary container exec | All versions with `--auth-mode=server` |
| CVE-2026-28229 / GHSA-56px-hm34-xqj5 | `Authorization: Bearer nothing` exfils ALL WorkflowTemplates incl. embedded secrets | < 3.7.11 / < 4.0.2 |
| CVE-2024-53862 / GHSA-h36c-m3rf-34h9 | Fake token retrieves all archived workflows | < 3.6.2 / 3.5.13 |
| CVE-2025-62156 / CVE-2025-66626 | ZipSlip RCE chain in artifact extraction; symlink bypass of patched fix | < 3.6.14 / 3.7.5 |
| CVE-2026-31892 / GHSA-3wf5-g532-rcrr | `podSpecPatch` bypasses Strict/Secure template reference mode → privileged container | < 3.7.11 / 4.0.2 |
| GHSA-jcc8-g2q4-9fxq | Unauthenticated webhook OOM DoS via `/api/v1/events/` — pre-auth, pre-sig-verify body load | < 3.7.14 / 4.0.5 |

Version available from `/api/v1/version` → map every confirmed host to its CVE exposure window.

### Namespace Targets on Confirmed Hosts

Query these namespaces in priority order: `argo`, `kubeflow`, `ml-pipeline`, `training`, `data-science`, `mlflow`, `production`, `staging`, `minio`

`kubeflow` and `ml-pipeline` namespaces carry the highest credential density (KFP v1 compiles directly to Argo; training jobs pass S3/GCS keys, MLflow tokens, and dataset paths as workflow parameters).

### Shadow Sweep Ports (Every Confirmed Host)

| Port | Service | Priority | Notes |
|---|---|---|---|
| 2379 | etcd | **HIGHEST** | Open etcd → `/registry/secrets/` → SA tokens for every namespace → cluster takeover |
| 9090 | Prometheus | HIGH | `/api/v1/status/config` leaks full scrape_configs + internal service topology |
| 9100 | node_exporter | HIGH | `/metrics` — OS/HW/kernel info; typically world-reachable |
| 6379 | Redis | HIGH | Argo uses Redis for DAG state offload; no-auth default common in Helm installs |
| 9000/9001 | MinIO | HIGH | Artifact repository; prior survey baseline |
| 10250 | kubelet | HIGH | Rare; unauth kubelet = cluster-wide RCE |
| 8080 | Argo CD | MED | Co-deployed on same cluster; auth-on-default but same operator |
| 3000 | Grafana | MED | kube-prometheus-stack companion |
| 2375 | Docker daemon | MED | Present on bare-metal or DinD setups |
| 9901 | Envoy admin | MED | `/config_dump` leaks full mesh topology on service-mesh clusters |

**Chain:** Argo unauth → etcd open → `/registry/secrets/argo/argo-server-token` → K8s API authenticated as cluster-scoped SA → cluster-wide control. Etcd co-location upgrades Argo from data-exposure class to cluster-takeover class.

### Cert-Pivot Notes (VisorGraph)

Three cert classes in production:

1. **`CN=localhost` self-signed** — no pivot value; identifies unmanaged default-config install
2. **`CN=Kubernetes Ingress Controller Fake Certificate`** — cluster-level pivot; same cert on all ingress-exposed services; SAN sweep finds Argo CD, Grafana, Prometheus on same cluster
3. **Operator-configured domain cert** — high-value VisorGraph anchor; CN/SAN reveals org identity, internal DNS, may expose other services on wildcard

VisorGraph anchors: `ssl.cert.issuer.cn:"Argo Workflows"` (class 1), ingress fake cert fingerprint (class 2), operator domain from CN (class 3).

### ML Operator Profile

Dominant user orgs: Intuit (creator/4,000+ engineers), BlackRock, TripAdvisor, Adobe, Cisco, NVIDIA, Tesla (CNCF end-user data). Production use grew 115% YoY (2022). Confirmed hosts are running real ML training pipelines, not sandboxes.

**Credential patterns on exposed instances:**
- AWS `accessKey`/`secretKey` in artifact repository config or hardcoded in workflow parameters
- GCS service account JSON key via `serviceAccountKeySecret`
- MLflow tracking tokens (`MLFLOW_TRACKING_TOKEN` env var)
- Database connection strings (feature store, metadata DB)
- Private container registry pull secrets
- Internal service DNS (`mlflow.mlflow.svc.cluster.local`, `postgres.data.svc.cluster.local`)

### Reference

- E.V.A Security (Nov 2024): https://www.evasec.io/blog/argo-workflows-uncovering-the-hidden-misconfigurations
- Intezer (Jul 2021, in-the-wild exploitation): https://intezer.com/blog/new-attacks-on-kubernetes-via-misconfigured-argo-workflows/
- OSTIF/Ada Logics audit (2022): https://ostif.org/our-audit-of-argo-is-complete-critical-and-high-severity-security-issues-found-and-fixed/
- Argo auth mode docs: https://argo-workflows.readthedocs.io/en/latest/argo-server-auth-mode/
- Practical hardening guide: https://blog.argoproj.io/practical-argo-workflows-hardening-dd8429acc1ce
- Nuclei template: `http/misconfiguration/argo-workflows-unauth.yaml`
- NuClide pre-assessment brief: `case-studies/commercial/argo-workflows-osint-pre-assessment-2026-05-27.md`

---

## Temporal (Workflow Orchestration — not yet surveyed)

Port 7233 (gRPC), 8080 (web UI). `GET /api/v1/cluster-info`. Tier A*. Workflow history exposure. Survey pending.

## Kubeflow / KServe (not yet surveyed)

K8s ingress profile — separate from cheap-VPS surface. `/v1/models` OpenAPI. Exposure dependent on ingress auth config. Survey pending.
