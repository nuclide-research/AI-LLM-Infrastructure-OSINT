# Insight #92 — Cross-Platform Co-Deployment Multiplies Exposure (Candidate)

_NuClide Research · 2026-06-08 · Origin: cross-corpus operator hunt against today's three surveys._

---

## Statement

When the same operator runs multiple unauth platforms on the same host, the disclosure value is **more than the sum of the per-platform leaks**. Each unauth surface enriches the others: an attacker who can read scrape topology AND collection schemas AND configuration dumps can JOIN the disclosed data layers into a far more actionable map than any single platform's leak would produce alone. Cross-platform co-deployment is therefore a risk multiplier, not a risk additive.

## Derivation

Cross-corpus analysis against today's three surveys (Chroma campaign, VictoriaMetrics, Prometheus) found **8 IPs running both VictoriaMetrics and Prometheus on the same host** (commonly VM on 8428/8429 + Prometheus Alertmanager on 9093). All eight are at least partially unauth on both platforms. All eight have `/debug/pprof/` open on the VM side and on the Prometheus side. Three of eight leak 11–15 scrape targets on the VM side AND emit Prometheus Alertmanager rules on the Prometheus side.

For these eight operators, the attacker's reconstruction is straightforward:

- VM's `/api/v1/targets` provides internal hostnames the operator monitors
- Prometheus' `/api/v1/status/config` (when present on the host's other Prometheus instance) provides remote_write URLs and AlertManager URLs
- Together the leaks reveal the monitoring control-plane topology — what hosts are being watched, where the metrics are forwarded to, who gets alerted, and on what conditions

The operator deployment decision that produces both unauth surfaces is a single one: "I run my monitoring stack on this box and I don't restrict network reach." Each platform inherits the decision; the platforms together inherit the disclosure consequence.

## Why "more than additive"

If platform A leaks N items and platform B leaks M items independently, additive disclosure is N+M items. The co-deployment multiplier exceeds this when the items at A and the items at B can be JOINed by a shared key — which is the case for monitoring co-deployment, because every leaked item is keyed on hostname / service / job, all in the operator's same naming convention. The leaks compose, not concatenate.

Concrete example from the 8 same-IP cases: an operator's VM /api/v1/targets leaks `cadvisor-production01.menta.uz`. Their colocated Prometheus alerting rules may include a rule named "high-memory-cadvisor-prod01" — the same host, but as the alerting subject rather than as the scrape target. Cross-platform, the attacker now knows that this host both produces metrics and triggers alerts when those metrics exceed thresholds. The next step (fake the metric to trigger or suppress the alert) becomes operational.

## The multiplier is not unique to monitoring

The principle generalizes wherever the data classes share an identifier. Examples:

- **AI/ML co-deployment.** Chroma (collection names, RAG corpora) + Langfuse (per-trace user IDs) on the same host: collection name + trace user_id = per-customer RAG behavior.
- **Vector + serving.** Qdrant (collection names) + vLLM (model + endpoint) on same host: which models query which corpora.
- **Compute + observability.** Kubernetes kubelet (pod inventory) + Prometheus on same operator's network: which pods run which workloads, monitored under which alert rules.

The multiplier value depends on the join key richness, not on platform similarity.

## Action / discrimination

When a survey identifies an unauth host on platform A, **the next probe should be a port sweep for platform B-Z that share an identifier class with A**. Specifically:

- Monitoring host found unauth → probe :9090, :9091, :9093, :8428, :8429, :8480, :8481, :8482 for co-resident monitoring
- AI/ML host found unauth → probe vector-DB ports + serving ports for co-resident AI stack
- Coordination host found unauth → probe Consul/etcd/Nomad ports for co-resident coordination stack

The disclosure-routing implication: an operator surfaced in multiple categorical surveys is a **multiplied-risk operator**. They should sort to the top of the disclosure pipeline regardless of which individual finding is most severe, because the cross-leak compound exceeds any single finding.

## Tooling

A 50-line cross-corpus tool reads N rollups, indexes per-IP and per-/24-subnet, and emits the multi-corpus operator list. Same input shape as glance compare. Output is the operator-rank-by-corpora-count, ready to drive disclosure priority.

The 8 same-IP cases identified today were found in approximately 15 lines of Python over the harvest hosts.json files. The compound finding exists in any program that has run more than one substrate-tier survey but hasn't cross-correlated.

## Cross-references

- Insight #88 (scrape topology = org chart): Insight #92 is what happens when an attacker can read two org charts from the same operator. The shared keys make the second org chart far more valuable than the first.
- Insight #89 (framework-level auth bypass): when the bypass propagates across BOTH co-deployed platforms (each Go-binary inheriting `_ "net/http/pprof"`), the operator cannot remediate either by configuration.
- Insight #91 candidate (config-dump endpoints): co-deployment with Prometheus is the easy upgrade — once one platform leaks its config, the rest of the operator's stack is enumerated.

## Falsifier

The multiplier claim is falsifiable. Re-run cross-corpus analysis against a population where operators do NOT co-deploy (e.g., shared-tenant SaaS where each platform runs on isolated VMs). If the multi-corpus operator list is empty in such a population, the multiplier does not generalize — it is a self-hosted-operator phenomenon only. Worth checking against a Vector-database-only population that doesn't include monitoring; if 0% overlap with monitoring populations, the finding holds as "co-deployment in self-hosted operator infra" and doesn't extend to managed-SaaS.

## Status

Candidate. Two surveys of the same substrate tier (VM + Prometheus) on the same day, plus one AI/ML-tier survey (Chroma), produced enough data for an initial codification. Confirmation requires:

1. One more substrate-tier survey that yields cross-overlap with VM or Prometheus (next candidate: OpenTelemetry Collector per the DCWF 902 roadmap)
2. One more AI/ML-tier survey that yields cross-overlap with Chroma (next candidate: Qdrant + Milvus combined)

Promote to numbered Insight once cross-overlap exists on both substrate AND AI tiers.
