# Session Analysis: Service Mesh Control Planes Survey

_2026-05-31. Network Perimeter / Service Mesh. New platform class. Findings #36200-36216, Insight #71._

## 1. Overview

### Objective
Resume and complete the in-flight Service Mesh survey (Istio/Kiali, Cilium/Hubble,
Linkerd, Pomerium): a new platform class that tests the auth-on-default thesis
against planes which have no authentication layer at all, only network placement.

### Scope and Constraints
23 candidate hosts harvested in the prior session via Shodan title-dorks. In-scope
roadmap category. Passive and identification-only: fingerprint and confirm
auth-state, enumerate topology metadata (namespace and metric names), never stream
the data plane. Censys credit-limited (7 -> 1 this week).

## 2. Environment and Tooling

### Claude Code Operation
Orchestrator-direct (Opus). aimap source edited and rebuilt locally; arsenal run by hand, in order.

### Tools Used
aimap v1.9.42 (built this session, +9 fingerprints), grpcurl, VisorGraph,
aimap-profile, cencli (Censys), VisorLog, VisorScuba, BARE, VisorBishop, menlohunt,
nu-recon, recongraph, VisorSD, VisorAgent. VisorGoose/VisorPlus/VisorRAG/VisorCorpus
recorded with scoping reason. VisorHollow N/A (Windows).

### Notable Configuration
rooster, no VPN. Shodan API key invalid this session (nu-recon degraded to
simulated; VisorSD dry-run). Censys cencli authenticated (PAT in keyring), free tier.

## 3. Methodology

### Enumeration approach
Shodan title-dorks (prior session) for the console tier. aimap had zero mesh
fingerprints, so the first action was to productize nine into aimap before any
verification, then run.

### Candidate identification
aimap v1.9.42, `-ports-class network-mesh` (re-curated to real introspection ports).
21 service matches across 23 hosts.

### Validation checks
Per-plane data-layer probe ordered first in each fingerprint, so `MatchPath`
classifies auth-state in one run (Insight #16). Kiali confirmed via
`/kiali/api/namespaces` (anonymous cluster read), not the gated `/api/config`.
kube-apiserver confirmed via `/version` only (anon `/api/v1/namespaces` denied).
gRPC relay covered by grpcurl ServerStatus (counts only).

### Safeguards
Restraint ethic throughout: namespace and metric names enumerated as the finding;
no Hubble `GetFlows`, no record pagination, no credential use. Hubble UI flow-data
implication left at logic level (inner-A), not exercised. data_accessed: false.

## 4. Execution Trace

1. Loaded methodology + Stage -1 intel (service-mesh-perimeter-osint-2026-05-31.md).
2. Verified all 19 arsenal binaries present.
3. Read aimap matcher schema; built 9 mesh fingerprints + port-class update + 19 tests; v1.9.41 -> v1.9.42; full suite green.
4. aimap run vs 23 hosts: 21 matches.
5. Parsed report: MatchPath classification (Kiali 4 anon, k8s 3 identity-only, Cilium metrics, Hubble UI 9).
6. grpcurl 4245 on 12 Cilium hosts: 0 reachable.
7. VisorGraph cert-pivot + aimap-profile + Censys view (Brazil/GCP confirmed).
8. VisorLog ingest #36200-36216 (verified per-host severities).
9. VisorScuba (vacuous), BARE (recon class), VisorBishop (0 shadow), menlohunt, nu-recon, recongraph, VisorSD, VisorAgent.
10. Wrote case study, breakdown, Insight #71, query-catalog update, this analysis.

## 5. Findings

### 5.1 Kiali anonymous cluster-read — 4 hosts (HIGH)
`/kiali/api/namespaces` returns the full namespace array unauthenticated via the
Kiali ServiceAccount. 109.237.70.159 (Rancher), 146.56.204.28 (KubeSphere),
34.101.217.236 (GKE+ArgoCD), 34.151.222.47 (479 ns, Brazilian AI chatbot platform).
inner-B/outer-1. Cluster-wide recon delivered as an API.

### 5.2 Cilium Hubble metrics unauth — 159.138.129.194 (MED)
9962 + 9965 leak `cilium_drop_count_total` / `hubble_flows_processed_total`
(workload and flow-graph topology). inner-B/outer-1.

### 5.3 Hubble UI console exposed — 9 hosts (LOW; 34.166.133.241 MED)
No login by design. 34.166.133.241 also CVE-2025-23047 (CORS:*). Relay 4245 internal
on all 12, so flow data not reachable from our vantage (flow exposure inner-A only).

### 5.4 kube-apiserver exposed, anon-secured — 3 hosts (LOW)
v1.29.0 on public 6443; `/version` anon-readable, `/api/v1/namespaces` anon denied.
The authn-backed plane held under the same exposure. The discriminator for Insight #71.

## 6. Risk Assessment

### Overall Posture
Confirms the auth-on-default thesis at its limiting case (no auth layer). Among
exposed placement-only planes, the unauthenticated rate is effectively total by
construction.

### Confidentiality
High exposure: cluster topology, namespace inventory, service graph, mesh
identities readable anonymously. The 479-namespace host exposes a commercial AI
product's full dev/review surface.

### Integrity / Availability
Not exercised. Kiali anonymous strategy is read-scoped by the Kiali SA; the risk is
reconnaissance, not direct mutation. Envoy `/quitquitquit` (sidecar DoS) exists in
the class but was not in the reachable corpus.

### Systemic Patterns
Control TYPE predicts the outcome (network-position fails, RBAC holds) on the same
hosts. Console tier exposed, data-plane tier internal. Managed cloud does not
co-expose the data tier (0 shadow), unlike self-hosted.

## 7. Recommendations

### R1 — Kiali anonymous strategy
Set `auth.strategy: token` or `openid`. Never anonymous on a publicly reachable install.

### R2 — Cilium Hubble
Do not expose UI/Relay; `hubble.relay.tls.server.enabled=true`; bind metrics internal; patch CVE-2025-23047.

### Future automation
Extend aimap with a gRPC probe type (`grpc_service_list` / `grpc_call`) to fingerprint
Hubble Relay 4245 directly (the highest-value surface is currently grpcurl-manual).
Add a VisorScuba control for cluster-introspection planes (AI baseline 0/0 here).
Add mesh ports to the menlohunt EASM port set.

## 8. Limitations and Assumptions

- Console-dork corpus measures the console tier only. The data-plane introspection
  tier (15000/15014/4191/4245) is Shodan-dark and unmeasured; needs Censys full-range
  (credit-exhausted, 1 left) or tiptoe/naabu. Deferred lane.
- 6 of 10 Kiali title-hits did not confirm via the data-layer probe (the :443
  TLS-ingress hosts): gated auth-on or title reflection (Insight #15, ~50% rule).
- Hubble UI flow-data exposure is logic-level (inner-A), deliberately not exercised.
- Shodan key invalid: nu-recon simulated, VisorSD dry-run only.
- Attribution rests on namespace names + Censys geolocation; cert-pivot was thin
  (bare cloud IPs).

## 9. Proof of Concept (PoC) Illustrations

Kiali anonymous cluster read (metadata only, no workload payload):

```
$ curl -s http://34.151.222.47/kiali/api/namespaces | jq 'length'
479
$ curl -s http://109.237.70.159:20001/kiali/api/namespaces | jq -r '.[].name' | head
application-overlay
cattle-fleet-system
cattle-impersonation-system
...
```

kube-apiserver discriminator (anon denied, the control that held):

```
$ curl -sk https://159.138.129.194:6443/version          # 200, gitVersion v1.29.0 (identity)
$ curl -sk https://159.138.129.194:6443/api/v1/namespaces # 403 Forbidden (RBAC holds)
```

Hubble Relay restraint boundary (ServerStatus only, never GetFlows):

```
$ grpcurl -plaintext -max-time 5 <host>:4245 observer.Observer/ServerStatus  # counts+version, rung 2
# observer.Observer/GetFlows is NEVER called — it streams live L7 traffic records (content exfil).
```
