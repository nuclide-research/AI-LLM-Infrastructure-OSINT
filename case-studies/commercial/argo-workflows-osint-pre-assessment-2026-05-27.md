---
type: osint-brief
---

# Argo Workflows — Pre-Assessment OSINT Brief (2026-05-27)

_NuClide Research · 2026-05-27_
_Status: OSINT complete. Survey chain: pending._
_6-agent parallel research. Sources: primary docs, source code, CVE databases, published prior research._

---

## What This Is

Intelligence gathered before the population scan to fine-tune dork selection, fingerprint design, verification methodology, and scope. Not a survey — a survey prep document. The scan chain runs after this.

---

## The Target

**Argo Workflows** — Kubernetes-native workflow engine by argoproj. Used at population scale in ML/MLOps pipelines (Kubeflow v1 compiles to Argo; Hera, Couler, and direct YAML users on top). Created and maintained by Intuit; adopted by BlackRock, Adobe, Cisco, NVIDIA, Tesla, TripAdvisor (CNCF end-user data). Production use grew 115% YoY as of 2022.

This is not a dev-sandbox tool. Confirmed hosts are running real production ML training pipelines.

---

## Auth Posture

**Tier A\*** — auth optional, off by design in the server mode path.

### Auth Modes

Four modes; one disables all credential requirements:

| Mode | Behavior |
|---|---|
| `client` | Caller supplies K8s bearer token; validated against K8s API; requests run as caller's SA |
| `server` | **No credential required.** Server appends empty string to auth list; `GetMode("")` returns `(Server, true)`; all requests run as `argo-server` SA. Confirmed at source: `gatekeeper.go` explicitly handles the empty-string case. |
| `sso` | OIDC token required; maps to SA via RBAC |
| `hybrid` (server+client) | Valid bearer token → client mode; no token → server mode (unauth) |

### What Ships Where

| Install path | Auth config | Effective behavior |
|---|---|---|
| Binary default (v3.0+) | `--auth-mode=client` | Safe |
| Official quickstart manifest | `--auth-mode=server --auth-mode=client` | **Hybrid = unauth access with no token** |
| Helm chart default | `authModes: []` (empty) → no flags passed | Inherits binary default → `client` (safe, but silent) |
| Gateway-auth operators | Explicitly set `--auth-mode=server` to drop token requirement | **Unauth when gateway is absent/misconfigured** |

The quickstart manifest has shipped hybrid mode since v3.0 and still does on the current main branch. Operators who followed the quickstart and exposed port 2746 without an ingress auth layer are the primary population.

---

## Fingerprint

### Port

**2746** — Argo-exclusive. Default HTTPS (self-signed). HTTP requires explicit `--secure=false`.

Alternate exposure: `:80`/`:443` via reverse proxy, `:8080` in dev setups.

### HTML at Root (`/`)

Page title: **`"Argo"`** — NOT `"Argo Workflows"`. The existing nuclei template's `shodan-query: title:"Argo Workflows"` is wrong and hits docs sites.

Distinctive body signals:
- `assets/favicon/favicon-32x32.png` — exact favicon path in HTML source (non-standard; not served at `/favicon.ico`)
- `meta name="robots" content="noindex"`
- `<div id="app"></div>` (SPA mount point)

No distinctive `Server:` header — gRPC-gateway does not advertise itself.

### API Responses

`GET /api/v1/version` (effectively public, minimal auth check):
```json
{
  "version": "v3.5.2",
  "buildDate": "...",
  "gitCommit": "...",
  "gitTag": "v3.5.2",
  "gitTreeState": "clean",
  "goVersion": "go1.21.5",
  "compiler": "gc",
  "platform": "linux/amd64"
}
```
Distinctive field combo: `gitTag` + `gitTreeState` + `compiler` + `platform`.

### TLS Cert (Default Self-Signed)

Issuer CN: `"Argo Workflows"` — confirmed Shodan-indexable.
Alternate: `CN=localhost` (older versions).

### Shodan Dorks (Ranked)

| Rank | Dork | FP Risk |
|---|---|---|
| 1 | `port:2746 http.title:"Argo"` | Low — port is Argo-exclusive + correct title |
| 2 | `http.html:"assets/favicon/favicon-32x32.png" "noindex"` | Low — catches proxied instances |
| 3 | `ssl.cert.issuer.cn:"Argo Workflows"` | Low — default cert, confirmed indexable |
| 4 | `"gitTag" "gitTreeState" "compiler" "platform"` | Low — API response field combo |
| 5 | `port:2746 "argoproj"` | Low — JS bundle + port |
| ❌ | `http.title:"Argo Workflows"` | **HIGH FP — hits readthedocs, not live servers** |

Run all 5 variants; populations overlap but do not fully coincide (proxied instances not on 2746, cert dork catches different TLS profiles).

---

## Verification Primitive

Single request. Definitive. No false-positive risk.

```bash
curl -sk https://TARGET:2746/api/v1/userinfo
```

**Unauth confirmed:** response contains `serviceAccountName` (non-empty)
```json
{"serviceAccountName":"argo-server","serviceAccountNamespace":"argo"}
```

**Auth enforced:** `{}` or HTTP 401/403

This is the same probe E.V.A Security used to find ~3,000 unauth instances in November 2024.

---

## Population Estimate

| Source | Count | Date | Method |
|---|---|---|---|
| E.V.A Security | ~3,000 unauth | Nov 2024 | Internet-wide scan via `/api/v1/userinfo` |
| NuClide Argo CD parallel | 4,577 confirmed from ~10,900 Shodan candidates | 2026-05-16 | Full chain (Argo CD, not Workflows) |
| Estimated Argo Workflows total (auth+unauth) | 5,000–15,000 | — | Based on Argo CD order of magnitude, Workflows more commonly behind ingress |

E.V.A scan is ~6 months old. Population has likely grown.

---

## Attack Surface on Unauth Instances

### argo-server ClusterRole Permissions (Inherited by All Callers in Server Mode)

```
configmaps:    get, watch, list, create, update
secrets:       get, create
pods:          get, list, watch, delete
pods/exec:     (included)
pods/log:      (included)
serviceaccounts: get, list, watch
argoproj.io/*: create, get, list, watch, update, patch, delete (all workflow resources)
```

Every unauthenticated caller executes with these permissions against the cluster.

### High-Value Endpoints

| Endpoint | Severity | Impact |
|---|---|---|
| `POST /api/v1/workflows/{namespace}` | **CRITICAL** | Arbitrary container execution. Cryptominer deployment documented in the wild (Intezer 2021). |
| `POST /api/v1/workflows/{ns}/{name}/pods/{pod}/exec` | **CRITICAL** | Unauthenticated pod exec. SA has `pods/exec` cluster-wide. |
| `GET /api/v1/workflows/{namespace}` | HIGH | Full workflow spec + `status.nodes` resolved values. Credentials passed as parameters appear in plaintext. |
| `GET /api/v1/workflows/{ns}/{name}/log` | HIGH | Container stdout/stderr. Pipeline steps commonly print credentials to stdout in debug mode. |
| `/artifacts/`, `/artifact-files/` (all) | HIGH | Full artifact download via server's S3/GCS creds. Model weights, datasets, pipeline outputs. |
| `GET /api/v1/workflow-templates/{namespace}` | HIGH | Template definitions. CVE-2026-28229: `Authorization: Bearer nothing` exfils embedded K8s secrets. |
| `GET /api/v1/archived-workflows` | HIGH | Historical workflow data with resolved parameter values. |
| `DELETE /api/v1/workflows/{ns}/{name}` | HIGH | Destroy running pipelines. |
| `GET /api/v1/userinfo` | LOW | Confirms unauth; leaks SA identity. |
| `GET /metrics` | LOW | `argo_workflows_info` label contains version string. Workflow counts, queue depths. |

### Namespace Targets (Query in This Order)

`argo` → `kubeflow` → `ml-pipeline` → `training` → `data-science` → `mlflow` → `production` → `staging` → `minio`

`kubeflow` and `ml-pipeline` namespaces carry the highest credential density — KFP v1 compiles to Argo and passes S3/GCS keys, MLflow tokens, and dataset paths as workflow parameters.

### Credential Patterns on Exposed Instances

- **AWS `accessKey`/`secretKey`** — in artifact repository config or hardcoded in workflow parameters (most common misuse)
- **GCS service account JSON key** — via `serviceAccountKeySecret` in artifact specs
- **MLflow tracking tokens** — `MLFLOW_TRACKING_TOKEN` env var, common in training pipelines
- **Database connection strings** — feature store, metadata DB, passed as parameters
- **Container registry pull secrets** — `imagePullSecrets` in pod spec
- **Internal service DNS** — `mlflow.mlflow.svc.cluster.local`, `postgres.data.svc.cluster.local` in parameter values
- **Private ECR/GCR image paths** — in template container image fields

The `status.nodes` section of a completed workflow contains resolved output values from each step — data extracted from files, API call responses, intermediate results. This is often richer than `spec.arguments.parameters`.

---

## CVE Landscape

| CVE | CVSS | Impact | Threshold |
|---|---|---|---|
| GHSA-rc7p-gmvh-xfx2 (no CVE) | Moderate (advisory) | Server-mode unauth → arbitrary container exec. In-the-wild exploitation confirmed 2021. | All with `--auth-mode=server` |
| **CVE-2026-28229** / GHSA-56px-hm34-xqj5 | High (C:H) | `Authorization: Bearer nothing` exfils ALL WorkflowTemplates including embedded K8s secrets, S3/GCS creds, SA tokens. | < 3.7.11 / < 4.0.2 |
| CVE-2024-53862 / GHSA-h36c-m3rf-34h9 | High | Fake token retrieves all archived workflows from the archive DB. | < 3.6.2 / 3.5.13 |
| CVE-2025-62156 | High (8.1) | ZipSlip path traversal in artifact extraction — writes to `/etc/passwd`, `/etc/crontab`. | < 3.6.12 / 3.7.3 |
| CVE-2025-66626 | High (8.1) | Broken fix for CVE-2025-62156 — symlink traversal bypasses patch; overwrites argoexec binary. | < 3.6.14 / 3.7.5 |
| CVE-2026-31892 / GHSA-3wf5-g532-rcrr | High (8.9) | `podSpecPatch` at submission time bypasses Strict/Secure template mode → privileged container → node compromise. | < 3.7.11 / 4.0.2 |
| GHSA-jcc8-g2q4-9fxq | High | Unauthenticated webhook OOM DoS — pre-auth body load at `/api/v1/events/`. | < 3.7.14 / 4.0.5 |
| GHSA-3775-99mw-8rp4 | High | Incomplete fix for CVE-2026-31892 — `hostNetwork`, `securityContext`, `serviceAccountName` still bypass templateReferencing Strict mode. | < 4.0.5 |

**Version extraction from `/api/v1/version` maps each confirmed host to its CVE exposure window. Run this on every confirmed host.**

### Research Gaps We Can Fill

- No nuclei template for CVE-2026-28229 (`Bearer nothing` template exfil)
- No nuclei template for CVE-2024-53862 (archived workflow fake-token bypass)
- The E.V.A Nov 2024 scan (~3,000 hosts) has not been followed up with full-stack chain verification in any published research
- GHSA-xchc-cqwg-g76q (Sync ConfigMap CRUD zero-auth) appears under-researched

---

## Argo Ecosystem Co-Deployment

### Port Map

| Component | Port(s) | Auth posture |
|---|---|---|
| Argo Workflows (argo-server) | **2746** (primary) | Tier A* — see above |
| Argo CD | 8080 (HTTP), 443 (HTTPS) | Tier C — auth-on-default, 99.93% hold posture (NuClide survey 2026-05-16) |
| Argo Events (eventsource webhook) | 12000 | Per-eventsource; no fixed port |
| Argo Rollouts dashboard | 3100 | HTTP; local kubectl plugin or NodePort |

### Shadow Sweep Priorities

| Port | Service | Priority | Notes |
|---|---|---|---|
| 2379 | etcd | **HIGHEST** | Open etcd → `/registry/secrets/` → SA tokens for every namespace → cluster takeover. One confirmed host found with `/registry/` K8s control-plane data root accessible (NuClide etcd survey). Argo unauth + etcd open = cluster-takeover class, not data-exposure class. |
| 9090 | Prometheus | HIGH | `/api/v1/status/config` leaks full scrape_configs: K8s API URL, etcd endpoints, every internal service name. |
| 9100 | node_exporter | HIGH | `/metrics` — OS, HW, BIOS, kernel. Nuclei: `node-exporter-metrics.yaml`. Typically world-reachable. |
| 6379 | Redis | HIGH | Argo uses Redis for DAG state offload. No-auth default common in Helm installs. |
| 9000/9001 | MinIO | HIGH | Artifact repository. Prior NuClide survey baseline. |
| 10250 | kubelet | HIGH | Rare; unauth kubelet = cluster-wide RCE. |
| 8080 | Argo CD | MED | Co-deployed; same cluster, same operator. Auth-on-default but OIDC tenant IDs disclosed via `/api/v1/settings`. |
| 3000 | Grafana | MED | kube-prometheus-stack companion. Default `admin:admin` until v9.x. |
| 2375 | Docker daemon | MED | Bare-metal or DinD setups. |
| 9901 | Envoy admin | MED | `/config_dump` on service-mesh clusters leaks full mesh topology. |

**WorkflowExec → SA token → K8s API chain:**
Submit workflow → exec into pod → read `/var/run/secrets/kubernetes.io/serviceaccount/token` → use against K8s API server (6443) authenticated as Argo SA → if SA has `pods/exec` cluster-wide → execute into any pod in the cluster.

### Cert-Pivot (VisorGraph)

Three cert classes in production:

1. **`CN=localhost` / `CN=Argo Workflows` self-signed** — identifies default-config install. `ssl.cert.issuer.cn:"Argo Workflows"` is the Shodan dork.
2. **`CN=Kubernetes Ingress Controller Fake Certificate`** — cluster-level pivot. Same cert on all ingress-exposed services. SAN sweep finds Argo CD, Grafana, Prometheus on same cluster.
3. **Operator-configured domain cert** — high-value VisorGraph anchor. CN/SAN reveals org identity, internal DNS, may expose wildcard covering other services (`*.ops.corp.com`).

---

## aimap Fingerprint (Build Before Survey)

No existing Argo Workflows fingerprint in aimap as of 2026-05-27. Port 2746 is in `port_classes.go` workflow-orch class but no matching entry in `fingerprints.go`.

Required fingerprint spec:

```go
Fingerprint{
    Name: "Argo Workflows",
    DefaultPorts: []int{2746},
    Probes: []Probe{
        {
            Path: "/api/v1/version",
            MatchCond: []Condition{
                {Type: CondStatus, Value: "200"},
                {Type: CondBodyContains, Value: "gitTag"},
                {Type: CondBodyContains, Value: "gitTreeState"},
                {Type: CondBodyContains, Value: "compiler"},
            },
        },
    },
}

// Auth classifier (deep enum)
// GET /api/v1/userinfo → json_field serviceAccountName non-empty → UNAUTH

// Deep enum steps:
// 1. Extract version string from /api/v1/version → classify CVE exposure
// 2. List workflows across target namespaces: argo, kubeflow, ml-pipeline, training, data-science, mlflow
// 3. CVE-2026-28229 probe: GET /api/v1/workflow-templates/{ns} with Authorization: Bearer nothing
// 4. Extract spec.arguments.parameters from workflow list → credential pattern detection
// 5. Enumerate /api/v1/cron-workflows → reveals pipeline schedules + data cadence
// 6. Shadow sweep: 2379, 9090, 9100, 6379, 9000, 10250
```

---

## Prior Research

| Source | Date | Finding |
|---|---|---|
| Intezer (Robinson + Fishbein) | Jul 2021 | First documented in-the-wild exploitation. Monero cryptominers via unauth Argo Workflows. Covered by Threatpost, BleepingComputer. |
| Ada Logics / OSTIF / CNCF | 2022 | Comprehensive audit. 26 issues found; 6 in Argo Workflows. Produced CVE-2022-29164. |
| E.V.A Security | Nov 2024 | ~3,000 publicly exposed unauth instances via internet-wide `/api/v1/userinfo` scan. Blog post with full attack chain. |
| Endor Labs | Dec 2025 | Discovered CVE-2025-66626 by auditing the patch for CVE-2025-62156. Broken-fix-as-research-signal methodology. |
| Upwind | 2024 | Documented CVE-2024-53862 and cluster-takeover demo chain. |

**Nuclei template exists:** `http/misconfiguration/argo-workflows-unauth.yaml` — probes `/api/v1/workflows/argo`, matches `metadata` + `items` in body. Shodan-query metadata in the template is incorrect (`title:"Argo Workflows"` — hits docs sites). No template for CVE-2026-28229 or CVE-2024-53862.

**No CISA KEV entries** for Argo Workflows as of 2026-05-27.

---

## Session Notes

- 6-agent parallel OSINT run: auth modes, Shodan fingerprint, API surface, CVEs, ML deployment patterns, ecosystem co-deployment
- All 6 agents completed; findings synthesized above
- Next: build aimap fingerprint → JAXEN harvest (all 5 dork variants) → full chain

---

## References

- E.V.A Security (Nov 2024): https://www.evasec.io/blog/argo-workflows-uncovering-the-hidden-misconfigurations
- Intezer (Jul 2021): https://intezer.com/blog/new-attacks-on-kubernetes-via-misconfigured-argo-workflows/
- OSTIF audit (2022): https://ostif.org/our-audit-of-argo-is-complete-critical-and-high-severity-security-issues-found-and-fixed/
- Argo auth mode docs: https://argo-workflows.readthedocs.io/en/latest/argo-server-auth-mode/
- Practical hardening: https://blog.argoproj.io/practical-argo-workflows-hardening-dd8429acc1ce
- GHSA-56px-hm34-xqj5 (CVE-2026-28229): https://github.com/argoproj/argo-workflows/security/advisories/GHSA-56px-hm34-xqj5
- CVE-2025-66626 (Endor Labs): https://www.endorlabs.com/learn/when-a-broken-fix-leads-to-rce-how-we-found-cve-2025-66626-in-argo
- gatekeeper.go source: https://github.com/argoproj/argo-workflows/blob/main/server/auth/gatekeeper.go
- argo-server-clusterole.yaml: https://github.com/argoproj/argo-workflows/blob/main/manifests/cluster-install-no-crds/argo-server-rbac/argo-server-clusterole.yaml
