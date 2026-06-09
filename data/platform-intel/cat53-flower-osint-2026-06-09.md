# Cat-53 — Flower (flwr.ai) Pre-Assessment OSINT

**Target:** Flower Framework (flwrlabs/flower, "Friendly Federated AI Framework")
**Date:** 2026-06-09
**Scope:** Doc + source recon for a survey of internet-exposed Flower coordinators. No live probing.
**Disambiguation:** `flwr.ai` (Flower Labs, federated learning) — NOT `mher/flower` (Celery web UI). CVE-2022-30034 OAuth bypass is the *Celery* Flower, not this target.

---

## 1. Auth modes & deploy config

**Default posture is `--insecure` in every official example.** The canonical multi-machine compose file (`framework/docker/complete/compose.yml`) launches SuperLink, SuperExec, and every SuperNode with `--insecure` as the first arg. The official "Quickstart with Docker" and "Deploy on Multiple Machines" guides reproduce this. The Deployment Engine guide explicitly says `--insecure` "tells the SuperLink to operate in an insecure mode, allowing unencrypted communication" and is "suitable only for local testing."

**TLS is optional, not required.** SuperLink accepts `--ssl-ca-certfile / --ssl-certfile / --ssl-keyfile`. Omit them + omit `--insecure` and the process refuses to start. The path of least resistance is therefore `--insecure`.

**SuperNode authentication** (per `how-to-authenticate-supernodes`): two modes.
- *Automatic mode* — timestamp-signed requests, replay-resistant, confirms node identity but does **not** restrict which nodes can join. Effectively "anyone can be a node, we just verify they're consistently the same anyone."
- *Allowlist mode* — pubkey allowlist on SuperLink (`--auth-list-public-keys`).

Exit code 303 (`SUPERNODE_STARTED_WITHOUT_TLS_BUT_NODE_AUTH_ENABLED`) confirms node-auth requires TLS — so an `--insecure` SuperLink runs **no node-auth at all**.

**SuperExec auth** — shared-secret HMAC interceptor, marked *experimental* in current docs (as of v1.30.x). Off by default.

**Version history.** Node authentication landed in the 1.9 / 1.10 window (token-based RPC auth referenced in releases). Pre-1.9 deployments have no node-auth surface period. SuperExec HMAC is later (1.2x experimental). The repo's own quickstarts still ship `--insecure` in 2026 — unknown whether any release flips the default; changelog text does not assert it.

## 2. Shodan fingerprint & population signal

**Default ports (canonical):**
- `9091` — ServerAppIO API (internal SuperLink↔ServerApp)
- `9092` — Fleet API (SuperNode↔SuperLink) — *most likely externally exposed*
- `9093` — Exec / Control API (CLI↔SuperLink) — *also externally exposed in compose*
- `9094–9095` — SuperNode ClientApp APIs (per-node; multi-node = sequential)

All three SuperLink ports are **gRPC over HTTP/2**. No HTTP dashboard ships with core Flower (no favicon to hash). gRPC over TLS = ALPN `h2`; plaintext gRPC = HTTP/2 cleartext (`h2c`).

**Cert CN patterns** — Helm chart and docs use `superlink` as the default service name / SAN. Compose service names: `superlink`, `supernode-1/2`, `superexec-serverapp`, `superexec-clientapp-1/2`.

**Suggested dorks (ranked FP-risk ascending):**
1. `port:9093 "grpc-status"` — Exec API, narrow. Highest signal/lowest FP if it banners.
2. `port:9092,9093,9091 product:"gRPC"` — broad gRPC harvest, FP-heavy, requires Step 0c scanner strip.
3. `ssl.cert.subject.CN:"superlink"` — Helm/compose default SAN; populates the TLS-enabled subset (the security-mature tail per Insight #72 dork-population-substitution).
4. `ssl:"flwr" OR ssl:"Flower Labs"` — CT-log/cert pivot via Censys preferred.
5. `"flwr-superlink"` HTTP body — Docker label / k8s pod-name leak via misconfigured reverse proxy.

**Shodan-dark warning.** Plain gRPC over TCP returns no HTTP body; Shodan's `http.html:` / `http.headers:` filters return 0 for SuperLink. Censys (Step 0b) and an active full-handshake banner grab (Step 0c scanner) are mandatory — Shodan alone will under-count by a wide margin. This matches the Cat-29 Argo 2746 pattern (Shodan-dark on the data port).

## 3. API surface & data exposure

**gRPC services (protobuf names per source tree):**
- `Fleet` (9092) — node registration, task pull, task result push. *Public-facing.*
- `Exec` (9093) — `StartRun`, `ListRuns`, `StreamLogs`, `StopRun`. *Public-facing.* This is the high-value control plane.
- `ServerAppIo` (9091) — typically loopback, but compose maps it.

**Unauth read potential (`--insecure` SuperLink):**
- `Exec.ListRuns` — run IDs, FAB hash, run status, timestamps. **Metadata-only — no model weights.**
- `Exec.StreamLogs` — live training logs. Often leaks dataset names, client counts, hyperparameters, exception traces.
- `Fleet`-side — node count via observable registration churn.
- `StartRun` — *write* surface. Submitting a FAB would constitute exploitation; **do not call.** Names ARE the finding.

**gRPC reflection.** Unknown — source default is framework-dependent. The grpc-go default is *off*; grpc-python's `add_reflection_service` is opt-in. Flower source must be grepped to confirm; treat as "probably off" but verify with a `grpc.reflection.v1alpha.ServerReflection` probe during the survey (read-only, fingerprint-safe).

**Restraint line.** `ListRuns` + `StreamLogs` = metadata-only reads. Sufficient to prove unauth control-plane exposure. Stop before `StartRun` / `PushTaskRes` / model-weight retrieval.

## 4. CVEs & prior research

**Zero CVEs against flwrlabs/flower as of 2026-06-09.** CVE-2022-30034 (`GHSA-q4qm-xhf9-4p8f`) is the Celery web UI; cvedetails.com Flower Project = same Celery tool. No GHSA entries against `flwrlabs/flower`. No HackerOne public disclosures. No nuclei templates targeting Flower FL. No bug-bounty writeups located.

This is a **green-field surface.** The auth-on-default thesis (Insight #40) predicts the disclosure pressure curve hasn't hit Flower yet — consistent with `--insecure` still shipping as the quickstart default.

## 5. Deployment patterns

- **Healthcare / pharma** — Rhino FCP × Flower Labs partnership (Feb 2025) targets pharma/healthcare federations. Real production Rhino deployments wrap Flower in their hardened layer — direct-internet SuperLink there is unlikely. **Loose academic/biomedical SuperLinks are the realistic exposure tier.**
- **Academic / .edu** — Flower's prototyping-friendly rep (per the 2025 arxiv 2511.00037 benchmark vs FLARE/Substra) drives university deployments. Cross-reference with the Cat-49 global-university LLM map.
- **Helm operators** — `exalsius/flower-operator` (k8s CRDs for SuperLink/SuperNode), `hpn-bristol/kubeFlower` (academic). Both default to ClusterIP but examples show LoadBalancer for cross-cluster federations — the exposure path.
- **NVFLARE crossover** — NVIDIA's `nvflare.app_opt.flower.applet` runs Flower inside FLARE; those deployments inherit FLARE's auth posture, not Flower's.
- **Namespace conventions** — `flwr`, `flower`, `fl-system`, `federated-learning`.

## 6. Ecosystem co-deployment (shadow-sweep priorities)

Expected colocated ports on a Flower coordinator host:
1. **MLflow** `5000` — experiment tracking, near-universal pairing
2. **Prometheus** `9090` — adjacent to `9091/9092/9093`, easy operator slip
3. **Weights & Biases** local server `8080`
4. **PyTorch Serve** `8080/8081/8082` — post-aggregation model serve
5. **Ray dashboard** `8265` — distributed training crossover
6. **Jupyter** `8888` — academic deployments especially
7. **MinIO / S3** `9000/9001` — FAB / checkpoint storage

**Cert-pivot attribution.** Wildcard CNs on the SuperLink cert (`*.fl.<institution>.edu`, `*.federated.<corp>`) will pivot to the colocated MLflow / W&B / dashboard via Censys SAN expansion. This is the operator-attribution path per `reference_tls_cn_sweep_attack_class`.

---

## Open unknowns (flag for active phase)

- gRPC reflection default in current Flower release — verify per-version.
- Whether any release has flipped quickstart away from `--insecure` — changelog scan needed.
- SuperExec HMAC auth default state in v1.30.x — docs say "experimental," off by default; confirm in source.
- Real-world ratio of Rhino-wrapped vs bare SuperLink in the population (the survey will answer).

## Sources

- [Flower Network Communication](https://flower.ai/docs/framework/ref-flower-network-communication.html)
- [Enable TLS connections](https://flower.ai/docs/framework/how-to-enable-tls-connections.html)
- [Authenticate SuperNodes](https://flower.ai/docs/framework/how-to-authenticate-supernodes.html)
- [Exit code 303 — no-TLS + node-auth conflict](https://flower.ai/docs/framework/ref-exit-codes/303.html)
- [Deploy SuperLink using Helm](https://flower.ai/docs/framework/helm/how-to-deploy-superlink-using-helm.html)
- [Quickstart with Docker](https://flower.ai/docs/framework/docker/tutorial-quickstart-docker.html)
- [Deploy on Multiple Machines with Docker Compose](https://flower.ai/docs/framework/docker/tutorial-deploy-on-multiple-machines.html)
- [Canonical compose.yml — `--insecure` default](https://github.com/flwrlabs/flower/blob/main/framework/docker/complete/compose.yml)
- [flwr/superlink Docker image](https://hub.docker.com/r/flwr/superlink)
- [Flower releases / changelog](https://github.com/flwrlabs/flower/releases)
- [exalsius/flower-operator (k8s)](https://github.com/exalsius/flower-operator)
- [hpn-bristol/kubeFlower](https://github.com/hpn-bristol/kubeFlower)
- [Rhino FCP × Flower Labs partnership (2025-02-24)](https://www.rhinofcp.com/news/rhino-flower-partnership)
- [Benchmarking FL Frameworks: FLARE / Flower / Substra (arxiv 2511.00037)](https://arxiv.org/abs/2511.00037)
- [Supercharging FL with Flower and NVIDIA FLARE (arxiv 2407.00031)](https://arxiv.org/pdf/2407.00031)
- [NVFLARE Flower applet docs](https://nvflare.readthedocs.io/en/2.6/_modules/nvflare/app_opt/flower/applet.html)
- [gRPC reflection — security trade-off](https://grpc.io/docs/guides/reflection/)
- [CVE-2022-30034 (Celery Flower, NOT this target)](https://github.com/advisories/GHSA-q4qm-xhf9-4p8f)
