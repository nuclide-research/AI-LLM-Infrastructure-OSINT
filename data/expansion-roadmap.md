# Expansion Roadmap — Unsurveyed Platform Categories

_Last updated: 2026-05-28_

14 categories from the research program not yet fully surveyed. Sorted by priority.

---

## Priority 1 — Immediate

### Auth / Access Control / API Gateways
**Platforms:** Kong, Tyk, Apigee self-hosted, OPA, OPAL, Casbin, Authelia, Authentik, Keycloak  
**Platform-intel doc:** Yes (`data/platform-intel/auth-gateways-osint-2026-05-27.md`)  
**Shodan queries:** Yes  
**Candidate dorks:**
- `port:8001 "via: kong" http.status:200`
- `port:8080 "x-tyk-gateway" http.status:200`
- `port:8181 "v1/data" http.status:200`

**Why:** Auth gateway exposure bypasses all downstream AI/LLM stack protection. Kong/Tyk ship with no/default admin auth. OPA leaks infra topology unauthenticated. Highest credential exposure at the perimeter — compromise here invalidates all downstream controls.

---

## Priority 2 — Short-Term

### Feature Stores & Long-Term Memory
**Platforms:** Feast, Tecton OSS, Hopsworks, Mem0, Letta, MemGPT, Zep  
**Platform-intel doc:** Partial (specialty-data-layers doc covers Feast/Hopsworks)  
**Shodan queries:** No — needs new query file  
**Candidate dorks:**
- `port:6566 "feature_names" http.status:200`
- `port:6566 "feast" http.status:200`
- `"tecton" "feature" port:8080`

**Why:** Feature stores and agent memory layers leak entity mappings, embedding vectors, and real-time feature values unauthenticated by default. Distinct from vector DBs. Critical for RAG/agent persistence chains.

---

### Specialty Data Layers (ClickHouse, Cassandra, Redis Stack, MinIO)
**Platforms:** ClickHouse, Apache Cassandra, Redis Stack, MinIO, Vespa, DuckDB-HTTP  
**Platform-intel doc:** Yes (`specialty-data-layers-osint-2026-05-27.md`)  
**Shodan queries:** No — needs new query file  
**Candidate dorks:**
- `http.title:"ClickHouse" port:8123`
- `port:9042 "Apache Cassandra"`
- `port:6379 "redis_version"`

**Why:** ClickHouse/Cassandra ship no auth by default, expose full AI feature vectors and LLM request logs. Redis Stack CVE-2025-49844 (RCE) actively exploited. MinIO auth-off on many deployments. All store high-value AI training and inference data.

---

### Workflow & Event Orchestration
**Platforms:** Temporal, Prefect, Dagster, Argo Workflows, Kafka, NATS  
**Platform-intel doc:** Yes (`workflow-orchestration-osint-2026-05-27.md`)  
**Shodan queries:** Yes  
**Status:** Argo Workflows surveyed 2026-05-27 (100% auth). Temporal/Prefect deferred.  
**Candidate dorks:**
- `port:7233 "temporal" http.status:200`
- `port:4200 "prefect" http.status:200`

**Why:** Temporal/Prefect expose full workflow history including secrets/args. Kafka misconfigs leak event streams. CVE-2026-29059 (Windfall — Temporal path traversal, CVSS 10.0) has public exploit.

---

### Experiment Tracking Systems (stragglers)
**Platforms:** W&B self-hosted, ClearML, Comet ML, Neptune.ai, Aim, Sacred  
**Platform-intel doc:** Yes (`experiment-tracking-osint-2026-05-27.md`)  
**Shodan queries:** Yes  
**Status:** ClearML 81/81 auth-off confirmed. Comet default creds `admin:admin` pre-24.9.8. Sacred/other stragglers unrun.

---

## Priority 3 — Medium-Term

### Cost, Billing & Usage Analytics
**Platforms:** OpenMeter, Lago, Helicone cost analytics, showback/chargeback dashboards  
**Platform-intel doc:** No  
**Shodan queries:** No  
**Candidate dorks:**
- `"openmeter" port:8080`
- `"lago" port:3000 http.status:200`
- `"helicone" "usage" port:3000`

**Why:** Cost/billing dashboards expose operator API quotas, usage patterns, and provider-key spend data. Langfuse analytics endpoint leaks per-tenant usage on signup-open instances.

---

### Evaluation, Benchmarking & Regression Harnesses
**Platforms:** Promptfoo, DeepEval, Confident AI, OpenAI Evals self-hosted, Helm  
**Platform-intel doc:** No  
**Shodan queries:** No  
**Candidate dorks:**
- `http.html:"promptfoo" port:3000`
- `http.html:"deepeval" port:8000`
- `"confident" "eval" port:8080`

**Why:** Eval dashboards expose test prompts, expected outputs, and model comparison results. Self-hosted eval harnesses leak evaluation corpus and benchmark data.

---

### Governance, Compliance & Audit Logging
**Platforms:** OpenMetadata, DataHub, Apache Atlas, Marquez lineage  
**Platform-intel doc:** No  
**Shodan queries:** Yes (`ml-governance-queries.md`)  
**Why:** Metadata/lineage services expose data pipeline DAGs, asset ownership, and compliance tags. Audit aggregators leak per-model access logs and user-data associations.

---

### Data Labeling & Annotation Systems
**Platforms:** Argilla, Label Studio, Prodigy, CVAT, RLHF preference-data tools  
**Platform-intel doc:** No  
**Shodan queries:** Yes  
**Candidate dorks:**
- `http.html:"argilla" port:6900`
- `http.html:"label-studio" port:8080`

**Why:** Label Studio/Argilla misconfigs expose annotation data. RLHF tools leak training preferences and human feedback datasets.

---

## Priority 4 — Lower Priority

### Network Perimeter & Service Mesh
**Platforms:** Istio, Linkerd, Cilium, Pomerium  
**Platform-intel doc:** No | **Shodan queries:** No  
**Candidate dorks:** `port:15000 "istio" http.status:200`  
**Why:** Istio dashboard port 15000 leaks sidecar configs, mTLS cert store, policy rules. Requires K8s ingress knowledge — not the cheap-VPS surface class.

---

### Safety / Guardrail & Policy Engines
**Platforms:** LlamaGuard, NeMo Guardrails, Lakera Guard self-hosted, Guardrails AI  
**Platform-intel doc:** Yes (`safety-guardrail-osint-2026-05-28.md`)  
**Shodan queries:** Yes  
**Status:** 2 LLM Guard instances surveyed 2026-05-28 (F1: Prometheus metrics open; F2: LLM Guard v0.0.10 unauth metrics).

---

### Classical ML & Auxiliary Model Services
**Platforms:** Recommender systems, ranking engines, fraud classifiers  
**Platform-intel doc:** No | **Shodan queries:** No  
**Why:** Fraud classifiers leak detection thresholds. Recommender systems expose user preference data. Low standardized endpoint surface — requires bespoke fingerprinting.

---

### Secrets Management (stragglers)
**Platforms:** Vaultwarden, Consul, LaunchDarkly OSS  
**Platform-intel doc:** Yes | **Shodan queries:** No  
**Candidate dorks:** `"vaultwarden" port:8000`, `port:8500 "consul" http.status:200`

---

## Priority 5 — Defer

### On-Device & Edge Inference
**Platforms:** Browser WebGPU runtimes, Core ML, TensorFlow Lite, model-distribution services  
**Platform-intel doc:** No | **Shodan queries:** No  
**Why:** Shodan-dark (no HTTP servers); physical-impact tier but inventory-only use case. Low immediate attack surface.

---

## Coverage Gaps by Type

| Gap Type | Categories | Action |
|----------|-----------|--------|
| Has intel doc, no Shodan queries | Feature Stores, Specialty Data Layers, Secrets Mgmt | Write query files |
| Has Shodan queries, no intel doc | Governance/Audit Logging, Data Labeling | Write platform-intel docs |
| Neither | Cost/Billing, Eval/Benchmarking, Network Perimeter, Classical ML, On-Device | Full new category build |
| Partial coverage | Experiment Tracking, Safety/Guardrails, Workflow Orchestration | Complete straggler surveys |
