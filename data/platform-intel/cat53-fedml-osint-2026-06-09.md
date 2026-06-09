# Cat-53 FedML / TensorOpera OSINT

Date: 2026-06-09
Researcher: NuClide Research
Scope: doc + source research only, no live probing.

FedML (rebranded TensorOpera) is a federated-learning + distributed-training framework. Two surfaces co-exist: the open-source coordinator (`fedml` PyPI, FedML-AI/FedML on GitHub) and the hosted MLOps platform at open.fedml.ai / TensorOpera.ai. Latest OSS release `v0.8.9` (Oct 2023); PyPI continues to publish point releases of the same line. Product lines: **Octopus** (cross-silo FL), **Beehive** (cross-device / mobile / IoT), **Parrot** (simulator), **MLOps** (orchestration overlay). Apache-2.0.

## 1. Auth modes & deploy config

OSS coordinator: backend = **`MQTT_S3`** by default. Two config files referenced from `fedml_config.yaml`:

```yaml
comm_args:
  backend: "MQTT_S3"
  mqtt_config_path: config/mqtt_config.yaml
  s3_config_path: config/s3_config.yaml
```

`mqtt_config.yaml` carries `BROKER_HOST` / `BROKER_PORT` / `MQTT_USER` / `MQTT_PWD`. **The shipped example points at TensorOpera's hosted broker** (mqtt.fedml.ai variant referenced in docs / shared open MQTT backbone behind open.fedml.ai). Self-hosted Mosquitto/EMQX is supported but a non-default substitution — operators reusing the example file are by default federating *through* the TensorOpera broker rather than running their own.

Hosted MLOps onboarding is **`fedml login <YourUserId>`** SSH'd onto each device; the agent binds to TensorOpera, auto-OTA-upgrades, and proxies all communication via the hosted MQTT + S3 layer. Web dashboard (open.fedml.ai / TensorOpera.ai) is account-auth'd — there is no documented self-hosted dashboard binary; the "on-premise" install is hosted-control-plane + on-prem workers.

Unknown — primary docs do not state whether the example `mqtt_config.yaml` enables `MQTT_USER`/`MQTT_PWD` by default, or whether the hosted broker accepts anonymous topic subscription from devices that have not bound. Tutorials show credential fields but example values are placeholder; source confirmation required.

S3: any S3-compatible endpoint; gradient blobs are uploaded to S3 and only the pointer travels MQTT (the "S3 message" half of MQTT_S3). Bucket creds in `s3_config.yaml`; ACL posture is operator responsibility, not framework-enforced.

## 2. Shodan fingerprint & population signal

Self-hosted footprint (Octopus deploying its own backend):

- MQTT broker on **1883** (plain) / **8883** (TLS) — Mosquitto or EMQX
- gRPC server (alternative backend, `grpc_server.py`) — operator-chosen port
- MLOps device agent — Python process, no public listening port on the device side; client-initiated outbound

Hosted/TensorOpera footprint: there is no per-customer self-hosted dashboard to fingerprint via HTTP. The interesting population is **FL operators who exposed their MQTT broker** for FedML or who run an unbound `fedml-server` process.

Suggested dorks (rank: low-FP first):

1. `ssl.cert.subject.cn:"*.fedml.ai"` — direct attribution, near-zero FP, but selects only TensorOpera infra.
2. `"fedml" port:1883` (and 8883) — MQTT banner + FedML hint, medium FP; broker banners rarely carry product strings, so this leans on cert/CONNECT topic prefixes.
3. `product:"Mosquitto" "fedml"` — same idea, banner-mode.
4. `http.html:"FedML" http.html:"MLOps"` — for any forks running a self-served console; high FP without version anchor.
5. `http.favicon.hash:<unknown — pull from open.fedml.ai live and lock>` — favicon hash unknown from doc research; harvest in Step 0 before locking.

MQTT-side, FedML's topic namespace is structured (`fedml_<runId>_<role>_<id>`); a CONNECT-then-`$SYS/#` or wildcard-`#` subscribe (where the broker is anonymous) would surface FedML-pattern topics distinctly. This is a verification probe, not a passive fingerprint.

## 3. API surface & data exposure

The OSS distribution is **not a REST-first system**. The "API surface" is MQTT topics + S3 object reads. Public OSS docs do not enumerate `/api/v1/runs|projects|devices` paths — those endpoints exist on the hosted TensorOpera control plane and require account auth.

Practical unauth exposure modes when an operator deploys naively:

- **Anonymous MQTT broker** = full subscription to FedML topic tree. Run/device/round metadata, possibly serialized gradient pointers, model-update messages. If MQTT_S3 is the backend the gradients live in S3; if `MQTT` alone, the payload is inline.
- **Open S3 bucket** named in `s3_config.yaml` = gradient blobs and checkpoints directly readable.
- **Unauthenticated gRPC** (`grpc_server.py`) = direct entry to `sendMessage` (see CVE-2026-5536).

Unknown — the hosted dashboard's exact endpoint map. Source X (TensorOpera docs) describes the UI without enumerating routes; only an authenticated browse would confirm.

## 4. CVEs & prior research

- **CVE-2026-5535** — path traversal in `FileUtils.java` MQTT message handler, FedML <= 0.8.9, CWE-22, remote, public exploit. [vuldb.com/vuln/355288](https://vuldb.com/vuln/355288)
- **CVE-2026-5536** — insecure deserialization in `grpc_server.py` `sendMessage`, FedML <= 0.8.9, remote. [cve.imfht.com/detail/CVE-2026-5536](https://cve.imfht.com/detail/CVE-2026-5536?lang=en)

No SECURITY.md or GHSA entries on the FedML-AI/FedML repo as of this read. The Java `FileUtils.java` lives in the **Beehive** Android edge SDK — the path-traversal class hits cross-device deployments specifically. The gRPC bug hits Octopus when the operator picked the gRPC backend instead of MQTT_S3.

No documented default credentials on the OSS distribution. Hosted platform uses per-account API keys via `fedml login`.

## 5. Deployment patterns

Three populations:

- **Research consortia** — hospital networks, the EU stroke-management FL PaaS (arxiv 2410.13869) builds directly on FedML. Health data flows as gradients, never as records; the data-class is "model derivatives of PHI," not PHI itself.
- **Edge / IoT** — Jetson, Pi, Android. Beehive SDK; Java surface; CVE-2026-5535 applies here.
- **Commercial / TensorOpera tenants** — hosted control plane, on-prem GPUs bound via `fedml login`.

K8s pattern: [FederatedAI/KubeFATE](https://github.com/FederatedAI/KubeFATE/blob/master/docs/Deploy_FedML_Agent_to_Kubernetes.md) ships a `Deploy_FedML_Agent_to_Kubernetes.md` — FedML agent as a Deployment, no Ingress required (outbound MQTT only). Operators who *do* add Ingress create their own dashboard surface.

## 6. Ecosystem co-deployment

- **Mosquitto / EMQX** on same host (1883/8883) — direct dependency, not optional, when MQTT_S3 backend is used.
- **MinIO / AWS S3 / S3-compatible** — gradient + checkpoint store.
- **PyTorch Serve, vLLM, Triton** — co-deployed for the model-serving half (TensorOpera Serve).
- **Prometheus / Grafana** — typical, not framework-coupled.
- MLflow / W&B — not the default; FedML has its own run tracking through MLOps. Co-deployment is operator-discretion, surfaces independently in their own fingerprints.

## Sources

- [FedML-AI/FedML GitHub](https://github.com/FedML-AI/FedML) — README, releases (v0.8.9 latest tag).
- [mqtt_s3_fedavg_mnist_lr_example.md](https://github.com/FedML-AI/FedML/blob/master/doc/en/cross-silo/examples/mqtt_s3_fedavg_mnist_lr_example.md) — MQTT_S3 backend config.
- [doc.fedml.ai MLOps user guide](https://doc.fedml.ai/mlops/user_guide.html) — `fedml login` flow, OTA, CLI commands.
- [docs.tensoropera.ai on-prem install](https://docs.tensoropera.ai/launch/on-prem/install) — `fedml login` device-binding to hosted control plane.
- [Octopus introduction (TensorOpera blog)](https://blog.tensoropera.ai/fedml-octopus-getting-started-federated-machine-learning/) — product-line scope.
- [CVE-2026-5535 (vuldb)](https://vuldb.com/vuln/355288) — Beehive Java path traversal.
- [CVE-2026-5536 (imfht)](https://cve.imfht.com/detail/CVE-2026-5536?lang=en) — gRPC deserialization.
- [EU stroke FL PaaS (arxiv 2410.13869)](https://arxiv.org/pdf/2410.13869) — clinical deployment pattern.
- [KubeFATE FedML agent on K8s](https://github.com/FederatedAI/KubeFATE/blob/master/docs/Deploy_FedML_Agent_to_Kubernetes.md) — K8s pattern.
