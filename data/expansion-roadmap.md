# Expansion Roadmap — Unsurveyed Platform Categories

_Last updated: 2026-05-28 (reconciled against filesystem + data/nuclide.db ledger, not hand-status)_

Status fields below are derived from artifact presence (`data/platform-intel/`, `shodan/queries/`) and ledger evidence (`data/nuclide.db`, 25,660 events), not manual tracking. Where the two disagree, the filesystem and ledger win.

**Reconciliation note (2026-05-28):** prior versions of this file marked several existing artifacts as missing (Specialty Data Layers queries, Eval/Benchmarking intel doc + queries, auth-gateway queries) and listed completed surveys as deferred (Temporal, ML Governance). Those drifted within a day of being written. The active worklist is now the genuinely cold set only.

---

## Active worklist — genuinely untouched, Shodan-viable

Three categories have **neither** an intel doc nor a Shodan query file, and confirm near-zero in the ledger. Driving these in priority order. Each runs the full arsenal starting at step 0 (Shodan harvest).

### 1. K8s FinOps Cost-Allocation (Kubecost / OpenCost)  _(Priority 1 of worklist)_
**CORRECTION (2026-05-28):** "Cost/Billing/Usage Analytics" broadly was ALREADY surveyed 2026-05-19 (`cost-billing-analytics-survey-2026-05-19.md` → Insight #37). That survey covered OpenMeter (30 hits via port:8888), Lago (703), Helicone (rare), Phoenix (95-host cohort), LiteLLM-spend. Those are DONE. The genuine remaining gap is the **K8s FinOps cost-allocation class** — Kubecost + OpenCost — which the prior survey did not touch.
**Platforms:** Kubecost, OpenCost (CNCF)
**Intel doc:** None (needs Stage −1) · **Query file:** in progress · **Harvest (2026-05-28):** Kubecost 116 (`http.title:"Kubecost"`), OpenCost ~9 genuine of 31 (`http.html:"opencost"`, ETag 1.96.0 + favicon 2140086526)
**Surface:** cost-model API on :9090 (Kubecost `/model/allocation`, OpenCost `/allocation/compute`)
**Why:** Cost-model API exposes cluster cost allocation, namespace/workload topology, and cloud spend. Prime Insight #37 test: UI fronted by ingress while the cost-model API stays auth-off on the same/adjacent port.

### 2. Network Perimeter & Service Mesh  _(Priority 2 of worklist)_
**Platforms:** Istio, Linkerd, Cilium, Pomerium
**Intel doc:** None · **Query file:** None · **Ledger:** zero hits
**Candidate dorks:** `port:15000 "istio" http.status:200`

**Why:** Istio dashboard :15000 leaks sidecar configs, mTLS cert store, policy rules. Higher skill floor — needs K8s ingress knowledge, not cheap-VPS surface class.

### 3. Classical ML & Auxiliary Model Services  _(Priority 3 of worklist)_
**Platforms:** Recommender systems, ranking engines, fraud classifiers
**Intel doc:** None · **Query file:** None · **Ledger:** `recommender` 1, `fraud` 1 (both incidental)

**Why:** Fraud classifiers leak detection thresholds. Recommender systems expose user-preference data. Low standardized endpoint surface — requires bespoke fingerprinting. Most build-heavy of the three.

---

## Deferred — untouched but structurally Shodan-dark

### On-Device & Edge Inference
**Platforms:** Browser WebGPU runtimes, Core ML, TensorFlow Lite, model-distribution services
**Intel doc:** None · **Query file:** None
**Why:** No HTTP servers to fingerprint — Shodan-dark. Inventory-only use case, not a Discover→Verify candidate. Stays deferred until a non-Shodan methodology is defined.

---

## Artifacts complete — survey not yet run

### Auth / Access Control / API Gateways
**Platforms:** Kong, Tyk, Apigee self-hosted, OPA, OPAL, Casbin, Authelia, Authentik, Keycloak
**Intel doc:** `auth-gateway-osint-2026-05-27.md` ✓ · **Query file:** `auth-gateway-queries.md` ✓
**Ledger:** `keycloak` 45, `authentik` 2, `kong` 1 — incidental, no formal survey run
**Why:** Auth gateway exposure bypasses all downstream AI/LLM stack protection. Kong/Tyk ship with no/default admin auth. OPA leaks infra topology unauthenticated. Highest credential exposure at the perimeter. **Ready to run — artifacts exist, just needs the chain.**

### Evaluation, Benchmarking & Regression Harnesses
**Platforms:** Promptfoo, DeepEval, Confident AI, OpenAI Evals self-hosted, Helm
**Intel doc:** `ai-eval-redteam-osint-2026-05-27.md` ✓ · **Query file:** `ai-eval-redteam-queries.md` ✓ (+`23-ai-safety-eval.md`)
**Ledger:** `promptfoo` 1 incidental, survey not run
**Why:** Eval dashboards expose test prompts, expected outputs, model comparison results. Self-hosted harnesses leak evaluation corpus. **Ready to run.**

---

## Has queries / probe, no intel doc

### Data Labeling & Annotation Systems
**Platforms:** Argilla, Label Studio, Prodigy, CVAT, RLHF preference-data tools
**Intel doc:** None · **Query file:** `22-data-labeling.md` ✓ (+`datalabel-probe.py`, `datalabel-discovery-runbook.sh`)
**Ledger:** `label studio` 1, `cvat` 3 — incidental
**Action:** Write platform-intel doc, then run. Probe tooling already built.

### Feature Stores & Long-Term Memory
**Platforms:** Feast, Tecton OSS, Hopsworks, Mem0, Letta, MemGPT, Zep
**Intel doc:** Partial (Feast/Hopsworks in specialty-data-layers doc) · **Query file:** `26-mem0-agent-memory.md` ✓ (mem0 only)
**Ledger:** `mem0` 6, `zep` 1
**Action:** Dedicated feature-store intel doc + query coverage for Feast/Tecton/Letta/Zep.

---

## Has intel doc, no dedicated query file

### Secrets Management (stragglers)
**Platforms:** Vaultwarden, Consul, LaunchDarkly OSS
**Intel doc:** Yes · **Query file:** None dedicated
**Ledger:** `consul` 1,830 hits (largely service-discovery noise, not confirmed secrets-store findings — needs disambiguation)
**Candidate dorks:** `"vaultwarden" port:8000`, `port:8500 "consul" http.status:200`
**Action:** Write query file; disambiguate Consul service-discovery noise from secrets exposure.

---

## Survey active or complete

| Category | Intel | Queries | State (ledger / session) |
|----------|:---:|:---:|---|
| Specialty Data Layers | ✓ | ✓ (+`20-...-clickhouse.md`) | **Active** — `clickhouse` 1,925, `minio` 100; clickhouse-state.json live |
| Workflow & Event Orchestration | ✓ | ✓ | Argo (197), NATS, Temporal (Sanio/BI/Voomi, 2026-05-28) done; Prefect/Dagster open |
| ML Governance / Compliance / Audit | ✓ | ✓ | **Surveyed 2026-05-28** — 31 OpenMetadata + 25 DataHub all auth-enforced (negative result, not in findings ledger; do not re-run) |
| Experiment Tracking | ✓ | ✓ | ClearML 81/81 auth-off confirmed; Sacred straggler open |
| Safety / Guardrails | ✓ | ✓ | **Active 2026-05-28** — LLM Guard instances, latest ledger row |

---

## Coverage Gaps by Type

| Gap Type | Categories | Action |
|----------|-----------|--------|
| Genuinely untouched, Shodan-viable | Cost/Billing, Network Perimeter, Classical ML | **Active worklist — full arsenal, priority order** |
| Untouched, Shodan-dark | On-Device/Edge | Deferred (no HTTP surface) |
| Artifacts complete, survey not run | Auth Gateways, Eval/Benchmarking | Run the chain |
| Has queries, no intel doc | Data Labeling, Feature Stores (partial) | Write intel doc, then run |
| Has intel, no query file | Secrets Mgmt | Write query file |
| Survey active/complete | Specialty Data Layers, Workflow Orch, ML Governance, Experiment Tracking, Safety/Guardrails | Maintain / finish stragglers |
