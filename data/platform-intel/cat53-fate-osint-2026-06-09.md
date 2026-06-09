# Cat-53 FATE (Federated AI Technology Enabler) — OSINT brief

**Date:** 2026-06-09. **Origin:** WeBank (Shenzhen). Donated to LF AI & Data 2019.
**Scope:** Doc + source only; no live probing. **Components:** FATEBoard, FATEFlow, RollSite (1.x), OSX (2.x), Eggroll, KubeFATE, MySQL backend.

## 1. Auth modes & deploy config

- **FATEBoard.** Spring Boot. `application.properties` ships `server.board.login.username=admin` / `.password=admin` (FATE issue #2942, RtD). Single admin, no SSO. KubeFATE `cluster.yaml` carries same default.
- **FATEFlow.** Auth OFF by default. `conf/service_conf.yaml`: `authentication.client.switch=false`, `authentication.site.switch=false`. Site auth (HMAC-SHA1, `http_secret_key`) is opt-in (FATE-Flow 1.9.1 Certification doc).
- **RollSite (1.x).** No app-layer auth in default route table; party identity = `party_id` claim. mTLS optional, off by default.
- **OSX (2.x replacement).** gRPC sync + streaming. Same party-ID-in-header trust model; TLS optional.
- **Eggroll (4670 clustermanager / 4671 nodemanager).** Internal RPC, no auth — assumes private subnet.
- **KubeFATE service.** JWT auth on the control-plane API only; FATE workloads it deploys keep their defaults.

FATE 1.x → 2.x (alpha 2024-02): RollSite→OSX swap, Flow API reshape. **Auth defaults unchanged across the cut.**

## 2. Shodan fingerprint & population

Default ports (KubeFATE `cluster.yaml`, FATE-Flow config docs, OSX guide):

| Port | Component |
|------|-----------|
| 8080 | FATEBoard (HTTP) |
| 9380 | FATEFlow HTTP API |
| 9360 | FATEFlow gRPC |
| 9370 | RollSite (1.x) / OSX default reuse |
| 9883 | OSX HTTP (2.x exchange) |
| 4670 / 4671 | Eggroll clustermanager / nodemanager |
| 3306 | MySQL backend |

Geo skew: heavy CN (Tencent Cloud, Alibaba Cloud, WeBank). EU/US thin (LF AI demos, vSphere ML extension).

Dorks (low → higher FP):

1. `http.title:"fateboard"` — vendor-unique. **Low FP.**
2. `http.html:"server.board.login.username"` — leaked properties. **Low FP, low pop.**
3. `port:9380 http.html:"fate_flow"` — Flow landing. **Medium FP** (docs mirrors echo).
4. `port:9883 "osx"` — OSX exchange; anchor on co-port 9370. **Medium-high FP.**
5. Favicon-hash pivot once a board is verified.

## 4. API surface & data exposure

FATEFlow REST (9380, `/v1/`) when site/client auth off (default):

- `/v1/job/list`, `/v1/job/query` — job_id, party_id, role (host/guest/arbiter), status, `f_runtime_conf` (raw pipeline JSON with party host:port and data table names).
- `/v1/data/upload|download`, `/v1/table/info` — table namespace + schema. Feature names regularly include `id_card`, `mobile`, `salary`, `credit_score`, hospital-encounter columns.
- `/v1/component/output/data` — intermediate model output.
- `/v1/model/list|load` — deployed-model inventory.
- `/v1/party/info`, `/v1/site/info` (1.9+) — local party identity / site_name.

FATEBoard (8080) exposes the entire job topology: guest/host/arbiter party IDs, model lineage, table names, runtime conf. **Schema + party-ID is the finding** — restraint: do not pull table contents.

## 5. CVEs & prior research

- **No CVE assignments** in NVD or GitHub Advisory DB for `FederatedAI/FATE` or `FederatedAI/FATE-Flow` (queried advisory endpoints, both empty 2026-06-09).
- `use_deserialize_safe_module` flag exists in Flow config 1.7+ — implies internal awareness of unsafe pickle/PyYAML in the pipeline runtime; no public CVE attached.
- No CNVD entries surfaced in CN-language search (unknown — direct cnvd.org.cn query not exercised).
- Disclosure channel: `FATE-security@groups.io` (FATE-Community SECURITY.md).
- Academic FL-poisoning / membership-inference papers cite FATE as target; none file CVEs.

**Bottom line:** zero public CVEs across 6+ years and a WeBank-scale framework while shipping auth-off defaults — either underexamined or under-disclosed.

## 6. Deployment patterns

WeBank-published production cases:
- **SME credit risk** — WeBank + partner banks, RSA-PSI joins, Hetero-LR AUC +12%.
- **National e-fapiao (invoice) centre** — federated credit rating, default rate halved.
- **Healthcare** — WeBank + Tencent + hospitals, stroke prediction on Tencent Cloud.
- **Insurance** — referenced, operators unnamed.
- **EU** — LF AI pilots; no named operators.

Sensitive data classes inferable from schemas: national ID, mobile, salary, credit score, encounter features, invoice party IDs. HIPAA-equivalent + financial-PII even at schema layer.

## 7. Ecosystem co-deployment

- **MySQL 3306** — FATEFlow metadata. Default `fate_dev` root password historically.
- **Redis** — FATE-Serving model registry.
- **Pulsar / RabbitMQ / nginx** — KubeFATE Helm Spark mode.
- **HDFS / Spark** — `spark` engine backend (alt to eggroll).
- **Eggroll cluster** — clustermanager + N nodemanagers on private subnet.
- **fate-operator** (kubeflow) — third-party CRD operator, less common.

Cloud clustering: Tencent Cloud (native), Alibaba Cloud, on-prem CN bank DCs.

## Sources

- github.com/FederatedAI/FATE (master, v1.9.0, v1.10.0); github.com/FederatedAI/FATE-Flow; github.com/FederatedAI/KubeFATE (`k8s-deploy/kubefate.yaml`, `docs/configurations/FATE_cluster_configuration.md`).
- federatedai.github.io/FATE-Flow/{1.7.2, 1.9.0, 1.9.1}; fate-flow.readthedocs.io/en/{v1.7.0, v1.8.0, v1.10.1}.
- FATE issue #2942 (FATEBoard admin/admin); discussion #4602 (2.0.0-alpha + OSX).
- lfaidata.foundation/projects/fate; FATE JMLR paper (jmlr.org/papers/volume22/20-815/20-815.pdf).
- WeBank SME-credit case (Medium @FateFedAI). SECURITY.md: github.com/FederatedAI/FATE-Community.
- GitHub Advisory DB FederatedAI/FATE + FederatedAI/FATE-Flow — both empty 2026-06-09.

## Unknowns / contradictions

- **OSX port 9883 vs 9370** — KubeFATE 2.0 chart and some 1.x configs both reuse 9370 in single-port mode; first verified hosts resolve which is modal.
- **Flow default-auth in the wild** — docs say off; some Helm overlays flip on; treat default-off as modal but verify per host.
- **CN CVE/CNVD coverage** — search empty; cnvd.org.cn direct query not exercised this round.
