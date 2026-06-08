# Strategic Roadmap: Post-VictoriaMetrics Research Direction (2026-06-08)

_DCWF AI Work Role 902 (AI Innovation Leader) audit · NuClide Research panel · Programmatic direction for the 6–8 weeks following the VictoriaMetrics survey (1,176 hosts, Insights #88 + #89)._

The VictoriaMetrics survey did two things at once. It confirmed the auth-off-default thesis at a new substrate tier, and it introduced two structural moves the program had not previously codified: scrape-topology as an org-chart disclosure class (Insight #88), and framework-level auth bypass propagating to population scale (Insight #89). Sections 1–6 below convert those into the next research cycle.

---

## 1. Insight #88 Generalization Roadmap — "monitoring agents leak org charts"

The probe pattern: read a list-of-things endpoint, regex the host portion of each target, classify as RFC1918 / public / hostname, count per host. Reusable on every monitoring agent that maintains a target inventory.

Priority list. Order optimizes for (a) population size, (b) likely unauth rate, (c) AI/ML relevance.

| # | Platform / category | "List of things" endpoint | Expected unauth | Shodan dork | Why it matters for the program |
|---|---|---|---|---|---|
| 1 | **Prometheus** (TSDB tier) | `/api/v1/targets`, `/api/v1/status/config`, `/api/v1/rules` | **HIGH (75–85%)** — VM is bug-for-bug Prometheus; same operator population, larger N | `port:9090 "Prometheus Time Series Collection"` + `http.favicon.hash:-1399433489` | Direct VM analogue. If #88 holds here at scale, the generalization is proven on the largest TSDB population (likely 10–30k hosts). |
| 2 | **Grafana** datasources | `/api/datasources` (auth-required by default) + `/public/build/*` for SSR-leaked names; `/login` HTML often shows org name | **MED (15–25%)** — Grafana ships auth, but `auth.anonymous.enabled=true` is documented common misconfig | `http.title:"Grafana"` + `http.html:"orgRole\":\"Viewer"` | Datasource names ARE the org chart (Prometheus-prod, Postgres-warehouse, Loki-staging). |
| 3 | **OpenTelemetry Collector** | `/debug/tracez`, `/debug/servicez`, `:8888/metrics` | **HIGH (60–75%)** — debug endpoints disabled requires explicit config; ships open in tutorial defaults | `port:8888 "otelcol"` + `http.html:"zpages"` | CNCF-adopted, accelerating. The pipeline names enumerate every source and every sink the operator wires together. |
| 4 | **Telegraf** | `/metrics` (with `[[outputs.prometheus_client]]` enabled) leaks plugin inventory via labels | **MED-HIGH (50–65%)** | `port:9273 "telegraf"` + `product:"Telegraf"` | Influx ecosystem twin to vmagent. Plugin label set = "what is this host scraping." |
| 5 | **Consul** services catalog | `/v1/catalog/services`, `/v1/catalog/nodes`, `/v1/agent/services` | **HIGH (70–80%)** — ACL-off is documented "starter" mode | `port:8500 "consul"` | Service mesh inventory = the org chart with edges. Higher fidelity than VM. |
| 6 | **Nomad** | `/v1/jobs`, `/v1/nodes`, `/v1/agent/members` | **HIGH (65–75%)** — same Hashicorp ACL-off default | `port:4646 "nomad"` | Job names + task groups = which workloads, named by team. |
| 7 | **Kubernetes kubelet read-only** (10255) | `/pods`, `/runningpods`, `/metrics/cadvisor` | **MED (20–35%)** — port mostly closed post-2019 hardening, but the long tail is large | `port:10250 "kubelet"` + `port:10255` | Pod labels expose `app=`, `team=`, `env=` — most explicit org-chart leak in the catalog. |
| 8 | **Datadog Agent** (self-hosted, on-prem) | `/info`, `/status`, `:5000/api/v1/check_run` | **LOW-MED (10–25%)** — binds 127.0.0.1 by default | `product:"Datadog Agent"` + body `"runner":` JSON | Lower hit rate but high-fidelity payload. |
| 9 | **Logstash / Beats** pipeline configs | Logstash `:9600/_node/pipelines`, Filebeat `:5066/?pretty` | **MED (40–55%)** | `port:9600 "logstash"` | Pipeline names + filter chain stages = the log-ingest org chart. |
| 10 | **Grafana Alloy** (vmagent/Prometheus-agent replacement) | `/-/config`, `/api/v1/targets` (Prometheus-compat) | **HIGH (75%+)** — early adopter, defaults in flux | `product:"alloy"` / `http.html:"Grafana Alloy"` | Leading-edge population, earliest-mover signal. |

**Tooling investment.** Build a single shared probe module — `target-list-extractor` — that takes the endpoint URL + a regex profile per platform and returns `{rfc1918_count, public_count, hostname_count, distinct_targets, sample_names}`. The verifier emits the same shape used in `vm-verify/hosts/*.json`. One module → 10 surveys.

**Sequencing.** Prometheus first (largest N, direct VM analogue, fastest falsifier). OpenTelemetry second (CNCF political weight). Consul + Nomad as a paired Hashicorp sweep. Then Telegraf, Alloy, Logstash/Beats, kubelet long-tail, Grafana, Datadog.

---

## 2. Insight #89 Generalization Roadmap — "framework-level pprof bypass"

The hypothesis: any Go binary using `_ "net/http/pprof"` import side-effect on a separate mux than the auth middleware will leak `/debug/pprof/` regardless of operator config.

Test method, in order of cost:
1. **Source-read on GitHub** — search for `_ "net/http/pprof"` + auth-middleware registration line. Zero network cost.
2. **Probe-and-confirm** on an authorized lab instance or self-hosted test deploy.
3. **Population-scale rate measurement** only on platforms where step 1 and step 2 confirm.

| # | Platform | Likely auth model | Pprof hypothesis | Test path | Priority |
|---|---|---|---|---|---|
| 1 | **NATS Server** | NKey/JWT/user-password on client port; HTTP monitor port 8222 separate | Pprof on `:8222/debug/pprof/` likely **bypassed** | Source: `github.com/nats-io/nats-server` | **P0 — fast win** |
| 2 | **Etcd** | client-cert TLS auth | Pprof gated behind `--enable-pprof` flag, default disabled. Hypothesis: **gated by flag**, leak rate moderate where flag flipped | Source: `etcd-io/etcd` mux registration | P0 |
| 3 | **MinIO** (object storage substrate) | Access/secret key auth | Hypothesis: **partially gated**, common misconfig | Source: `minio/minio` pprof registration | P0 — 852-host MinIO corpus already mapped |
| 4 | **Ollama** | None (auth-off by definition) | Hypothesis: **either fully closed or fully open** | Source: `ollama/ollama` import scan | P1 — AI-tier flagship; clear yes/no |
| 5 | **vLLM-router / LiteLLM Go components** | Bearer token | Hypothesis: **likely bypassed in Go subset** | Source: `BerriAI/litellm` Go dir | P1 |
| 6 | **Loki** + **Tempo** (Grafana, both Go) | X-Scope-OrgID multitenancy header | Hypothesis: matches VM's posture | Source: `grafana/loki`, `grafana/tempo` | P1 |
| 7 | **Traefik** / **Caddy** | Per-route middleware | Hypothesis: **gated by separate flag**, but flag flipped is common | Source: `traefik/traefik` mux | P2 |
| 8 | **Argo Workflows / Argo CD** | Bearer JWT | Hypothesis: **gated post-2022**, long tail of old versions still bypassed | Source + version-scoped probe | P2 |

**Output of this sub-roadmap.** A table titled "Framework-Level Pprof Inheritance: Go AI/ML Infrastructure" published as a methodology supplement.

---

## 3. Program-Level Taxonomy Delta — what should ride higher now

| Category | New priority | Why the VM finding moves it |
|---|---|---|
| **Time-Series Databases** | **P0** | VM is the highest-yield single member. InfluxDB, QuestDB, M3DB, Prometheus likely share both auth-off-default and scrape-topology disclosure. |
| **Distributed Coordination Services** | **P0** | Insight #88's "names leak the org chart" goes deeper here. ZooKeeper `mntr`/`cons`, Consul, etcd. |
| **LLM Observability / Tracing** | **P1** | Langfuse/Phoenix/Helicone/TruLens trace data contains scrape-topology-equivalent: prompt-pipeline names, agent-tool inventories. |
| **Event Streaming / Message Buses** | **P1** | Topic names = org chart by another name. Kafka Connect connector configs. |
| **BI / Dashboard / Visualization** | **P1** | Grafana `/api/datasources` is the equivalent endpoint. |
| **Specialty Data Layers** | **P1** | The "what's beneath the AI tier" framing the VM survey validated. ClickHouse is the next VM-class single finding. |
| **Container & Orchestration** | **P1** | Kubelet `/pods` is the most explicit org chart in the catalog. |

**De-prioritize:** the already-saturated tiers (model serving, vector DBs, LLM orchestration). Marginal finding per host there is now low; substrate tier is high.

---

## 4. Cross-Cutting Taxonomy Axis — "monitors vs holds"

The current taxonomy slices by *what the platform does for the AI/ML application*. The VM finding shows a second axis: *what kind of leak the platform's exposure produces*.

```
                       LEAKS DATA RECORDS              LEAKS INFRASTRUCTURE METADATA
                       (rows, embeddings, prompts)     (target lists, service names, topology)
                       ───────────────────────────     ─────────────────────────────────────────
HOLDS THE DATA         Q1: Data-Plane Stores           Q2: Self-Describing Stores
(persistent state)     Chroma, Qdrant, MLflow,         Kafka topics, Schema Registry,
                       Elasticsearch, MinIO,           ClickHouse system.tables,
                       Langfuse traces                 Vespa configs

MONITORS / CONNECTS    Q3: Read-Heavy Observers        Q4: Topology Mirrors    ← VM lives here
(transient view)       Prometheus query API,           vmagent /api/v1/targets,
                       Datadog raw metrics,            Prometheus /targets, Consul catalog,
                       Loki query                      kubelet /pods, OTel collector configs
```

**Operational use at survey-start time.** When a researcher opens a new platform survey:

1. **Which quadrant?**
2. **Q1 → measure record count and field-name PII content.**
3. **Q2 → measure schema entries and field-name leak.**
4. **Q3 → measure query-API openness and value-leak. Restraint: do NOT issue arbitrary queries.**
5. **Q4 → measure the Insight #88 metric: distinct_targets, rfc1918_count, hostname-naming-pattern samples.**

Discriminator between Q1 and Q4: *if I had to describe the operator's internal stack from this endpoint alone, could I?* If yes, it's Q4.

Add a one-line "Quadrant:" tag to each category-taxonomy entry. The methodology can route each survey to the right verifier shape automatically.

---

## 5. Stakeholder Strategy for Issue #3060 at Scale

**Tier-1, direct: VictoriaMetrics maintainers.** Open a new issue or comment on #3060 with population-scale evidence: 91.5% of internet-exposed hosts (1,077/1,176) leak pprof, including hosts that demonstrably configured `-httpAuth`. Recommend in-binary fix: pprof handlers register on the same mux as `-httpAuth.username/password` is enforced.

**Tier-2, ecosystem: CNCF observability TAG and the OpenTelemetry/Prometheus governance channels.** The pattern is structural to Go observability frameworks. A briefing memo to CNCF observability TAG turns a single-vendor issue into an ecosystem-wide best-practice recommendation.

**Tier-3, defender-side: CISA Known Exploited / Secure by Design pledge program.** Insight #89's pattern is exactly what Secure-by-Design is meant to address: framework defaults forcing operator-side mitigation that does not scale. A short brief to CISA's JCDC primes them for future calls when the same pattern appears in critical-infrastructure-adjacent Go frameworks.

**Do not file at:** NCSC-UK without UK-operator-impact angle. Do not write a CVE — it is documented behavior on an open issue.

**Sequencing.** VM maintainers first (30 days). CNCF observability TAG memo second. CISA brief third, only after a second framework (etcd or NATS) confirms the pattern.

---

## 6. What Kills This Research Program

**Failure mode 1: The thesis becomes a tautology.** Every survey confirms it because we only survey categories where we expect it to confirm. Survivorship bias. The doccano survey at 99% auth-on broke this trend once and was published as a methodology lesson. The program needs a recurring "ride into a category where auth-on is the prior" cadence — pick one category per quarter where auth-on is the prior, run the full survey, publish either confirmation or surprise.

**Failure mode 2: Substrate drift makes the thesis non-AI.** VictoriaMetrics monitors infrastructure that the AI/ML world uses, not AI/ML infrastructure proper. Same is true of Kafka, Consul, ClickHouse, kubelet. The program is doing important security work, but is it still AI/LLM infrastructure OSINT, or has it become substrate OSINT? Defensible answer: keep both framings live. The cross-cutting taxonomy in §4 is part of the answer — Q4 (topology mirrors) is a substrate finding regardless of whether the operator above is an LLM operator. The case-study front-matter should tag tier (AI-native / substrate / both).

**Failure mode 3: Framework-level findings shift the disclosure model and the program is unprepared.** Insight #89 introduces a class of finding where the disclosure target is the maintainer, not the operator, and remediation timelines are 1–3 years not 30 days. The program's reporting standard ("What / Why it matters / Chain context / Remediation / References") assumes operator-actionable fixes. For framework-level findings the "Remediation" field shifts from "set this flag" to "patch this binary; here is the upstream issue." Build a parallel reporting template for framework-class findings before the next framework-class finding arrives — at least three more are visible on the #89 generalization roadmap (NATS, MinIO, Loki).

**Has VictoriaMetrics already shifted the thesis enough to require formal reframing?** Yes, but the program can absorb without renaming. The thesis "auth-off is the modal deployment choice across AI infrastructure" survives. Amend with a second clause: **"and where operators do choose auth, framework-level gaps frequently make their choice inoperative."** This is the Insight #89 contribution and it sharpens the thesis without falsifying it.

**The active falsifier to test in the next 6 weeks.** Run the Prometheus survey. If Prometheus comes back at 30% unauth (not 75–85%), VM is anomalous — operators do harden monitoring when the framework makes hardening obvious, and VM's `-httpAuth` mis-design is doing real work. That outcome pushes the program toward maintainer-engagement work and away from per-operator disclosure. If Prometheus comes back at 75%+, the thesis holds at substrate tier and the program continues fanning out along the §1 roadmap. Either result is publishable.

**The program does not die from any of these failure modes; it dies from not noticing them.**

---

_Roadmap horizon: 6–8 weeks. Next checkpoint: 2026-08-03._
