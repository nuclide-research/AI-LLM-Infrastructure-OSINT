# Cat-53 Federated Learning - Syllabus-Grounded Threat Model

**Date:** 2026-06-09
**Survey:** Cat-53 Federated Learning (flower / fedml / nvflare / openfl / fate)
**Purpose:** Anchor verification primitive design and aimap fingerprint conjuncts in the published attack literature. This is the *threat reference*, not a target list. Targets come from Stage 0 (Shodan + Censys).

## 0. Why FL is a research-novel attack surface

A federated learning coordinator is structurally different from every prior survey category. Vector DBs leak read-only data. Model serving leaks model outputs. Tracking platforms leak metadata. An FL coordinator **accepts write traffic from any peer it considers a client** - model gradients flowing inward, aggregated into a global model that ships back out to every other client. The threat is not just disclosure; it is *integrity*: an unauthenticated aggregator lets an outside party silently rewrite the model that every legitimate participant downloads.

This makes FL the cleanest test yet of the auth-on-default thesis. Where prior surveys measured *exposure*, an FL survey measures *integrity surface* - and the restraint ethic must be strictest, because the active-probe boundary line moves: the metadata-read line is the same (round count, participant list, task name), but anything that submits gradients or joins a round is across the ethical-stop line.

## 1. Threat taxonomy (literature-grounded)

### T1 - Model poisoning via unauthenticated participation (CRITICAL)

**Mechanism.** An aggregator that does not authenticate its clients accepts gradient updates from any peer that completes the FL protocol handshake. The submitted gradients enter the aggregation function and shift the global model.

**Sources:**
- Xie et al. ICLR 2020 - *Distributed Backdoor Attacks against Federated Learning* (DBA). Splits a backdoor trigger across multiple Byzantine clients; the aggregated trigger backdoors the global model while individual updates evade norm-clipping defenses.
- Mahloujifar et al. ICML 2019 - *Universal Multi-Party Poisoning Attacks*. Shows the poisoning bound holds across aggregation rules.
- Xu et al. USENIX Security 2024 - *ACE: A Model Poisoning Attack on Contribution Estimation*. Targets the contribution-scoring layer specifically.
- Gu et al. USENIX Security 2025 - *DP-BREM: Differentially-Private and Byzantine-Robust*. The recent state of defenses, implicitly enumerating the attack surface they have to cover.

**Verification stance (NuClide).** **Inner-A only.** We confirm by reading the coordinator's source/config that the auth mode is `insecure`/`no-tls`/`POC`/`AUTH_ENABLED=False` and that the gRPC/HTTP submit-update endpoint is reachable. We do not submit gradients. We do not join a round. "Coordinator accepts unauthenticated client connections" is the finding, framed as *integrity surface open, integrity not exercised* on the verification-rung grid (Insight #68).

### T2 - Gradient inversion / training-data reconstruction (CRITICAL)

**Mechanism.** Any party that observes a client's gradient update (the aggregator itself, an in-path passive observer, or a colluding client where the protocol shares updates) can reconstruct the training data that produced that gradient. Recent work breaks even *secure aggregation*.

**Sources:**
- Carletti et al. USENIX Security 2025 - *SoK: Gradient Inversion Attacks*. Systematizes the family; key result: GI is feasible across the standard FL protocol family.
- Du et al. USENIX Security 2025 - *SoK: On Gradient Leakage in Federated Learning*. Parallel SoK from a different research group.
- NDSS - *Scale-MIA: Scalable Model Inversion Attack against Secure Federated Learning via Latent Space Reconstruction*. Scales beyond toy datasets; defeats secure aggregation.
- NDSS - *RAIFLE: Reconstruction Attacks on Interaction-Based Federated Learning with Adversarial Data Manipulation*.
- NDSS - *URVFL: Undetectable Data Reconstruction Attack on Vertical FL*.
- Tan et al. USENIX Security 2024 - *Defending Against Data Reconstruction Attacks in FL: An Information-Theoretic Approach* (enumerates the surface in defending it).

**Verification stance.** **Read-only metadata.** We enumerate whether the coordinator uses secure aggregation (`SecAgg`), whether DP noise is applied at the client, and whether gradient updates are observable over the wire (TLS termination point matters). We never capture or reconstruct an actual gradient. The presence of an unauthenticated coordinator + observable gradient channel is the integrity finding; reconstruction is the *consequence* that justifies the severity label, established by literature citation, not by our own reproduction.

### T3 - Metadata leakage (HIGH - and the load-bearing actionable signal)

**Mechanism.** FL coordinators expose round state, participant lists, task/job names, model architecture descriptors, and client device fingerprints. Like the MLflow/Langfuse pattern, **names are the finding** - a participant list naming three hospitals, a job name `breast_mri_phase2_2026`, a task descriptor pointing to `clinical_v3_run10` reveals the operator and the data class without any payload read.

**Sources:**
- Du et al. USENIX Security 2025 - *SoK: On Gradient Leakage*, §5 (metadata as auxiliary signal).
- The Cat-47 Mem0/Zep/Letta survey (2026-06-08) established the operational principle: 27 user-session UUIDs were the finding; the conversation contents were not read. Same principle here.

**Verification stance.** **Standard NuClide enumerate-only.** Pull the round-state JSON, the participant list, the job/task names. Class the operator from those. Honor the restraint ethic.

### T4 - Cross-platform attribution via cert pivot (METHODOLOGY)

**Mechanism.** FL platforms - particularly NVFlare, OpenFL, FATE - depend on PKI provisioning toolchains (step-ca for OpenFL, NVFlare's `provision` tool, FATE's RollSite cert chain). The certificates they mint carry consortium identifiers in subject CNs and SANs. Direct-IP TLS probe with no SNI surfaces the operator's OV/EV cert; CT-log SAN enumeration via Censys extends the consortium graph.

**Verification stance.** Stage 3 attribution; cert pivot via VisorGraph. Insight #19 (CDN-fronted SPA tells) and the cert-pivot attribution methodology generalize cleanly to FL.

### T5 - Co-deployed adjacent surface (Insight #12 generalization)

**Mechanism.** Operators who ship an FL coordinator auth-off ship other services auth-off on the same host. Expected adjacencies:
- **MQTT broker** (FedML uses Mosquitto/EMQX for gradient transport - open broker = read all model updates in real time)
- **MLflow** (the upstream/downstream tracking system for the FL training runs)
- **MinIO / S3-compatible** (FATE stores model artifacts; NVFlare aggregator output)
- **MySQL** (FATE backend)
- **Prometheus** / **Grafana** (training metrics - including loss curves that imply data class)
- **K8s API** (KubeFATE, Helm-deployed Flower/NVFlare)

**Verification stance.** IP-direct shadow sweep on every confirmed FL host per the standing rule. Treat MQTT-on-1883 as an AI signal when adjacent to an FL coordinator (Insight #20).

## 2. Required verification primitives (encoded into aimap fingerprints)

Per Insight #6 (conjunctive marker-anchored matchers), each FL platform's aimap fingerprint must conjoin three signals:

| Platform | Conjunct 1 (endpoint) | Conjunct 2 (structured response) | Conjunct 3 (anchored keyword) |
|---|---|---|---|
| Flower | gRPC reflection on `/grpc.reflection.v1.ServerReflection` | `service "flwr.proto.fleet.v1.Fleet"` in reflection enum | `flwr` in service name (not free text) |
| NVFlare | Overseer `/api/v1/heartbeat` | JSON with `{"sp_end_point": ..., "primary_sp": ...}` | `sp_end_point` field name (NVFlare-unique) |
| FedML MLOps | `/api/v1/cli/version` or similar | JSON with version + edition fields | `fedml` in response object |
| OpenFL | gRPC on Director/Envoy | reflection enum naming `openfl.federation` services | `openfl.federation` proto package |
| FATE FATEFlow | `/v1/version/get` | JSON `{"data": {"FATE": "x.x.x"}}` | `FATE` literal in `data` key |
| FATE FATEBoard | `/index.html` or `/favicon.ico` | HTTP title `FATEBoard` + Vue.js asset signature | favicon hash (compute from upstream) |

**Anti-match (`body_not_contains`).** Login pages, OAuth redirect URLs, "FATE" as a substring of "fortunate"/"federate". Conjunctive logic enforced by aimap's `matchFingerprints` per the methodology Stage 1 spec.

## 3. Verification primitive selection (Stage 2)

The **single-endpoint definitive primitive** per platform:

| Platform | Primitive | Authoritative outcome |
|---|---|---|
| Flower | gRPC reflection enum + version RPC | If reflection enumerates `Fleet` service AND `GetServerInfo` returns version unauth -> integrity surface open |
| NVFlare | `GET /api/v1/heartbeat` on overseer | 200 with `{"primary_sp": ..., "sp_end_point": ...}` unauth -> coordinator publicly enumerable; `GET /api/v1/promote` (if 200/4xx-with-shape) -> control surface |
| FedML | `GET /api/v1/version` and MQTT 1883 CONNECT anonymous | Version 200 + MQTT CONNECT-ACCEPTED -> coordinator + transport open (gradient real-time read) |
| OpenFL | gRPC reflection without client cert | Empty reflection (cert required) -> auth on default; populated reflection -> insecure mode |
| FATE FATEFlow | `POST /v1/job/list` (with empty filter) | 200 with `data.jobs[]` populated -> full job enumeration unauth |
| FATE FATEBoard | `GET /` | Title `FATEBoard` + no redirect -> dashboard open |

Each primitive is a **single request** returning either a definitive structured response (finding) or an auth-protected shape (refutation). No multi-step "is it open" inferences. No 200-equals-unauth heuristics (Insight #16).

## 4. Restraint contract (hard floor for Cat-53)

The boundary is stricter than other categories. Do not:

- Submit a gradient update, model weight, or any FL protocol message that creates state on the coordinator.
- Call `/start_round`, `/submit_update`, `/register_client`, or equivalent on any platform.
- Join an FL training round, even as a passive client.
- Persist any aggregator-returned global model bytes (the model itself is the operator's IP).
- Subscribe to an MQTT broker topic that carries live gradients (this *is* observing training data via the gradient inversion class).

Do:

- Pull metadata (version, round count, participant count, task names).
- Read the WHOIS, cert chain, and reverse DNS.
- Enumerate gRPC service descriptors via reflection (the metadata, not the call).
- Read public docs / GitHub for operator-identifying patterns.

This contract is recorded here because it is the load-bearing ethical line for the entire category, and it must hold for every host without exception. Inner-A / outer-1 (host identified as running vulnerable version, request deliberately not exercised) is the published claim level for Cat-53; inner-B (request actually exercised) requires a controlled lab target with VisorAgent.

## 5. Disclosure routing seeds

FL deployments concentrate in:

- **Medical research consortia** - disclose to the institution's CISO + privacy office. PHI exposure framing.
- **Pharma R&D** - disclose to the regulatory/security contact; IP exposure framing.
- **Banking/finance (especially FATE in CN)** - disclose to the operator + CNVD for CN-located. Credit-scoring data exposure framing.
- **Public-good consortia** (Owkin, Rhino Health, MELLODDY) - these will likely have responsible-disclosure programs.

Per Insight #4, WHOIS is authoritative for routing. Do not infer disclosure target from the FL job name.

## 6. Expected findings shape (a priori)

Based on the auth-on-default thesis and prior surveys:

- **Flower (insecure-default toggle exists)** - expect ~10-30% unauth at population scale, by analogy to Phoenix (Insight #13).
- **NVFlare (POC mode = unsecure-default)** - expect concentrated unauth where operators "demo" deployed and never rotated to production; medical-cluster bias.
- **FedML (split OSS / SaaS)** - expect MQTT broker exposure higher than HTTP dashboard exposure (transport vs UI layer).
- **OpenFL (auth-on default, step-ca)** - expect ~0% unauth or near-zero, by analogy to Langfuse (Insight #13 contrapositive). A high unauth rate here would *falsify* the auth-on-default-protects framing and itself be publishable.
- **FATE (heavy on-prem, CN-concentrated)** - expect higher unauth than Western platforms by operator-baseline; FATEBoard publicly indexed should be common.

These are predictions, not findings. Stage 2 verification decides.

## See also

- `~/.claude/nuclide-internal/METHODOLOGY.md` §3 (verification rungs, Insight #68 grid)
- `~/AI-LLM-Infrastructure-OSINT/case-studies/commercial/SYNTHESIS-2026-05.md`
- Cat-47 Agent Memory case study (2026-06-08) - the metadata-as-finding pattern this survey inherits
- Cat-46c VictoriaMetrics / Cat-46d Prometheus surveys - the framework-default-propagation pattern (Insight #89) is the analogue for FL coordinator defaults
