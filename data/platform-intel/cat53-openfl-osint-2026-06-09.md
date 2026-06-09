# Cat-53 OpenFL — Pre-Assessment OSINT

**Target:** OpenFL (Open Federated Learning) — `securefederatedai.github.io/openfl`
**Repo (canonical):** `github.com/securefederatedai/openfl`
**Status:** LF AI & Data incubation project since 2023-03 (Intel + Penn + VMware + Flower Labs); upstream **archive notice posted** — community pointed at Flower.
**Compiled:** 2026-06-09. Doc + source research only, no live probe.

---

## 1. Auth Modes & Deploy Config

Two API surfaces ship in-tree: **TaskRunner / Aggregator-Collaborator** (the original `fx` workflow) and **Director / Envoy / Interactive API** (long-lived federation).

**Default is mTLS, not optional TLS.**
`AggregatorGRPCServer.__init__` defaults: `use_tls=True, require_client_auth=True, root_certificate=None, certificate=None, private_key=None`. `require_client_auth` is *ignored* when `use_tls=False` — meaning the only way to drop to TLS-without-client-cert is also the way that drops TLS entirely. There is no "TLS, no client auth" middle setting documented; the design is mTLS-or-nothing.
(source: `openfl.readthedocs.io/en/v1.7.1/_autosummary/openfl.transport.grpc.aggregator_server.AggregatorGRPCServer.html`)

**Insecure modes that exist:**
- `fx director start --disable-tls -c director_config.yaml` — explicit CLI flag, documented in v1.6 Interactive API docs. Intended for "trusted environments."
- Interactive-API `Federation(...)` accepts a kwarg to disable mTLS for the same reason.
- `use_tls=False` on the gRPC server class.
(source: `openfl.readthedocs.io/en/v1.6/about/features_index/interactive.html`; troubleshooting page v1.7.1.)

**PKI provisioning:** OpenFL's `fx pki` utility downloads and wraps **smallstep `step-ca` + `step`** binaries. `step ca certificate <CN> <crt> <key> --token …` is the documented enroll path. CN convention: **FQDN for the Director, collaborator-name for an Envoy, API-name for the interactive node** (source: `openfl.readthedocs.io/en/latest/developer_guide/utilities/pki.html`). So step-ca is the *default-shipped* CA, not just one option.

**Version drift on the auth module:** the older `intel/openfl` and the renamed `securefederatedai/openfl` repos both have the same `aggregator.py` and `aggregator_server` defaults across `develop` (verified by source-tree URLs returned in search). Release notes through v1.7–v1.9 mention "fix for an issue that would prevent enabling TLS in distributed environments" — i.e. TLS-on was occasionally broken in practice in earlier point releases. Worth flagging because operators who hit that may have shipped `--disable-tls` as the workaround.

---

## 2. Shodan Fingerprint & Population Signal

**Default ports (documented):**
- **Director gRPC: 50051** (hard-coded sample in `director_config.yaml`, "director on localhost:50051"). Envoys connect with `--director-port 50051`.
- **Aggregator gRPC:** no single canonical default; `aggregator.yaml` ships a placeholder, plan-defined per workspace. Many tutorials use **50051 or 50052**.
- **Step-CA:** smallstep default **8443** (not OpenFL-set, but co-deployed when `fx pki` is used).

**Visibility caveat:** Director/Envoy/Aggregator are gRPC-over-mTLS. Shodan's HTTP-body / HTTPS-body grabbers return little against gRPC servers that require client certs — most of this population is **Shodan-dark by default**. Route discovery via Stage 0c scanner (full handshake) + Censys (`services.tls.certificates.leaf_data.subject` patterns), not Shodan HTML facets. (Insight #77 applies.)

**Dorks — ranked low to high FP risk:**

1. `ssl.cert.subject.CN:"step-ca"` paired with port 8443 — high specificity, low FP, but selects *any* step-ca deployment (not just OpenFL).
2. `ssl.cert.issuer.CN:"OpenFL"` / `ssl.cert.subject.O:"OpenFL"` — speculative; only fires if the operator used the OpenFL sample CA names. High specificity if any hit.
3. Censys: `services.port:50051 and services.service_name:"GRPC"` then leaf-cert SAN containing `director`, `envoy`, or `aggregator` substrings — best population signal. Run via Stage 0b.
4. Censys: TLS handshake on 50051/50052 with `tls.certificates.leaf_data.subject.common_name` matching `envoy`/`director`/`agg` — operator-attribution surface (Insight #51, TLS CN sweep class).
5. Shodan: `port:50051 "grpc"` — high FP (Cilium Hubble, Jaeger, generic gRPC services), only useful when filtered with cert CN above.

`http.html:` / `http.headers:` / `product:` filters return zero on gRPC-over-TLS-with-client-cert — confirmed pattern from prior surveys, route to Censys + scanner.

---

## 3. API Surface & Data Exposure

**gRPC services (from `openfl/protocols/`):**
- **`FederationDirector`** — Envoy registration, experiment registration from Interactive API, shard-descriptor exchange, envoy heartbeat, experiment status polling.
- **`FederationAggregator`** / `Aggregator` — `GetTasks`, `GetAggregatedTensor`, `SendLocalTaskResults`, `GetTrainedModel`. This is where rounds actually happen.
- **Envoy** runs a client-side gRPC stub to Director; not itself a listening service by default.

**Unauth reachable without a client cert:**
Almost nothing on a properly-configured deployment — the mTLS handshake fails before any RPC is parsed. **However**, on a `--disable-tls` deployment:
- Director: experiment metadata, envoy registry list, shard descriptors. Metadata-only.
- Aggregator: `GetTasks` / `GetAggregatedTensor` are reachable; calling them triggers a round / returns the current global model state. That is past the "metadata-only" threshold — a `GetTrainedModel` would exfiltrate the model itself.

**gRPC reflection:** **unknown — sources do not state.** Source not reviewed line-by-line in this OSINT pass. Worth a Stage 3v verify probe (`grpc.reflection.v1alpha.ServerReflection.ServerReflectionInfo`) on any unauth host found.

---

## 4. CVEs & Prior Research

**Direct OpenFL CVEs:** zero discoverable via GitHub Advisory Database search, NVD, or Intel PSIRT keyword search. The repo's `SECURITY.md` exists but **no GHSA records published** against `securefederatedai/openfl` as of compile date. (Search: `site:github.com securefederatedai openfl GHSA` — returned only generic GHSA infra pages.)

**Indirect / dependency:** release notes reference zlib CVEs (pre-1.2.12) — transitive only.

**Class-of-bug exposure (un-CVE'd but live):** OpenFL serializes model state for transit. The 2025 paper *"The Art of Hide and Seek: Making Pickle-Based Model Supply Chain Poisoning Stealthy Again"* (arXiv 2508.19774) enumerates 22 pickle-based model-loading paths across 5 frameworks; FL frameworks broadly are in scope. **NVFlare (NVIDIA's analogous FL framework) had unauthenticated pickle-deserialization RCE — CVE tracked at exploit-db 51051, NVFLARE < 2.1.4.** OpenFL has not been audited publicly for the same class; absence of finding is not absence of risk.

**Academic prior art:** OpenFL is the framework behind the **FeTS / BraTS federation** (Penn + Intel, 71 healthcare institutions, six continents, brain tumor segmentation +33% accuracy vs local-only). Multiple security/privacy-preserving-FL papers cite OpenFL as the testbed; none surface as offensive security research against the framework itself.

---

## 5. Deployment Patterns

- **Medical imaging consortia:** FeTS (71 sites), Penn Medicine, MONAI tutorials publish OpenFL-on-MedNIST examples (`Project-MONAI/tutorials`). Heavy academic / hospital deployment.
- **Pharma:** named publicly as a sector by Intel + LF AI marketing; specific firms not disclosed.
- **Insurance:** named publicly; specific firms not disclosed.
- **Aerospace:** OpenFL is "the only federated learning framework approved for use on the International Space Station" per LF AI announcement (2023-03). Operationally interesting if any ground-segment Aggregator is reachable.
- **Intel Tiber Secure Federated AI** = the commercial Intel offering built on OpenFL; suggests Intel-operated managed deployments exist.

**Geographic concentration:** US (Penn + Intel + NIH-funded sites) and EU (BraTS federation + LF AI European participants). APAC presence lighter.

**Data flowing:** medical imaging (MRI, multi-sequence brain), clinical tabular, financial (insurance/banking tutorials). Most sensitive class on actual round data = PHI/medical-imaging tensors. The Aggregator never sees raw data by design — only model deltas — but a stolen global model post-round is itself sensitive (membership inference, model-inversion attacks against medical FL is published research).

---

## 6. Ecosystem Co-Deployment

- **step-ca** on adjacent port (default 8443) — installed by `fx pki` provisioning. Strong co-location signal; finding a step-ca next to a 50051 listener raises confidence the 50051 is OpenFL.
- **Aggregator persistence:** model checkpoints land on **local filesystem** by default (`save/` under the workspace). No S3 / cloud-storage default — workspace-relative paths. Operators bolt on object storage manually. Implication: a host running an OpenFL Aggregator likely has checkpoint .pbuf files at predictable paths on disk; if any web service co-hosts, those are at risk of misindexing.
- **MLflow co-deployment:** **unknown — sources do not state native integration.** OpenFL has its own metric logging (TensorBoard hooks documented); MLflow is not in the default stack. May appear in custom user pipelines.
- **Gramine / Intel SGX:** Intel-promoted confidential-compute wrapper. Means some deployments run Aggregator/Director inside SGX enclaves — defensive posture, but attestation endpoint may itself be a recon surface.

---

## Sources

- `openfl.readthedocs.io/en/latest/` (docs root, v1.6, v1.7.1, v1.9)
- `openfl.readthedocs.io/en/v1.7.1/_autosummary/openfl.transport.grpc.aggregator_server.AggregatorGRPCServer.html`
- `openfl.readthedocs.io/en/v1.6/about/features_index/interactive.html`
- `openfl.readthedocs.io/en/latest/developer_guide/utilities/pki.html`
- `github.com/securefederatedai/openfl` (canonical) + `github.com/intel/openfl` (legacy redirect)
- `github.com/Project-MONAI/tutorials/blob/main/federated_learning/openfl/openfl_mednist_2d_registration/README.md`
- `lfaidata.foundation/blog/2023/03/09/intels-transition-of-openfl-primes-growth-of-confidential-ai/`
- `iopscience.iop.org/article/10.1088/1361-6560/ac97d9` (OpenFL paper, Phys. Med. Biol., 2022)
- `pmc.ncbi.nlm.nih.gov/articles/PMC9715347/` (same paper, OA mirror)
- `arxiv.org/html/2508.19774v1` (pickle-poisoning, class-of-bug context)
- `exploit-db.com/exploits/51051` (NVFlare CVE — sibling-framework comparator)
- `intel.com/content/www/us/en/software/federated-ai.html` (Tiber Secure Federated AI)

## Open Questions for Stage 3v Verify

1. Is gRPC reflection enabled on Director/Aggregator by default? (Not stated in docs; source-tree read required.)
2. What is the actual default Aggregator port in `aggregator.yaml` defaults (vs tutorial-set)?
3. Does `--disable-tls` log a warning? Telemetry behavior on the insecure path.
4. Are there pre-shipped sample/test certs in the repo whose CNs could fingerprint dev/lab deployments?
