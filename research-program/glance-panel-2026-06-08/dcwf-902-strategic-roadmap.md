# Strategic Roadmap: glance v0.1.0 → v1.0.0

_DCWF AI Work Role 902 (AI Innovation Leader) audit · NuClide Research panel · Productization brief for `glance`, the schema-only sensitivity analyzer · 2026-06-08_

`glance` is the youngest tool in the NuClide arsenal but the first one to operationalize the schema-recon discipline as a binary. Its job is to answer "how sensitive is this corpus" without reading the corpus. That capability has been the missing fourth side of the verification ladder — discover, fingerprint, verify, and now **characterize without exposure**. This brief converts that capability into a productization plan.

---

## 1. Where glance Fits in the Toolchain

The standard NuClide chain produces per-host evidence JSON at population scale. By step 1b (aimap deep-enum) and 3v (VERIFY), the program has read enough of each target to confirm category and severity, and downstream steps want to *score* and *report* without re-reading raw values. That gap is glance's home.

**Chain placement: Step 3.5 — "Characterize."** Between 3v (per-host verification) and 6 (visorlog ledger ingest). After verification, glance reads the sealed evidence directory and emits an aggregate rollup. The chain does not need to crack open the corpus a second time to score it.

```
                        ───── existing chain ─────
  0   Shodan / Censys ───> ips.txt
  0c  scanner ───────────> live subset
  1a  VisorPlus ─────┐
  1b  aimap ─────────┼──> per-host JSON  (~/syllabus/<cat>/hosts/*.json)
  1c  jaxen favicon ─┘                          │
  3v  VERIFY (verify_*.py) -> evidence/*.json   │
                                                │
                                                ▼
                        ──── NEW: Step 3.5 ────
                        glance scan <evidence_dir>
                        --source <profile>
                        -o rollup.json
                                                │
                                ┌───────────────┼────────────────┐
                                ▼               ▼                ▼
  6   visorlog  ────────> ledger row     7  visorscuba    12  visor-report
        (severity tag    (sensitivity        (compliance      (per-category
         from rollup)     category mix)       weight by cat)   sensitivity panel)
```

**Consumes:** per-host evidence JSON written by `verify_chroma_campaign.py`, `verify_vm_unauth.py`, or any future per-category verifier. The verifier owns the network read; glance is strictly offline post-processing.

**Produces:** `rollup.json` with three layers (structural counts, sensitivity category counts, statistical shape) plus a global category histogram. No raw values unless `--include-samples N` is passed. The rollup is the canonical input for downstream scoring.

**Chain-runner integration.** Add to `~/AI-LLM-Infrastructure-OSINT/data/visor-chain-runner.sh` between steps 3v and 6:

```bash
# Step 3.5 — characterize the verified corpus without re-reading values
if [ -d "$EVIDENCE_DIR" ]; then
  glance scan "$EVIDENCE_DIR" --source "$CAT_PROFILE" \
    -o "$SURVEY_DIR/rollup.json" --json-only > "$SURVEY_DIR/rollup.txt"
fi
```

**Downstream ingest.**

- **visorlog** reads `rollup.json.global_sensitivity_rollup` and tags each ledger row with the dominant category. Today visorlog severity is hand-set; the rollup makes it programmatic.
- **visorscuba** uses the category mix to weight compliance scoring (PHI hits trigger HIPAA scoring, FINANCE hits trigger PCI scoring, DEFENSE_GOV hits trigger CMMC scoring). Pure pull from glance output — no scuba-side classification needed.
- **visor-report** renders a "Sensitivity Panel" per survey using the structural + category + shape triple. The panel is glance's pretty-table output, captured at chain time.

**Why this placement, not earlier.** Glance presumes a corpus already exists. Running it before verification means scanning Shodan's banner cache, which mixes stale and live and gives sensitivity counts that mean nothing. Running it after verification means every count is grounded in a 200-with-data read. The placement enforces the verification-is-load-bearing rule downstream into the scoring layer.

**Why not as a verifier itself.** Glance does not probe. It reads files. Keeping the read/write boundary clean means the verifier code is auditable for restraint discipline and glance code is auditable for analytic correctness — two small problems instead of one big one.

---

## 2. Productization Roadmap v0.1.0 → v1.0.0

Six capability additions, ordered by priority. P0 = required for v1.0, P1 = highly desirable, P2 = stretch.

| # | Capability | Why | Complexity | Dependencies | Priority |
|---|---|---|---|---|---|
| 1 | **Plugin system for source profiles** | Today profiles are functions in `glance.py`. Every new category survey requires editing the binary. A profile-as-plugin loader (drop `vm-verify.py` in `~/.glance/profiles/`) means the methodology can grow without forking the tool. | M | None | **P0** |
| 2 | **visorlog backend integration** | Glance currently emits standalone JSON. Wire `--ledger` so the rollup writes directly to nuclide.db as a row keyed by (survey, host, category). Downstream queries ("which surveys leaked PHI?") become SQL, not file-grep. | M | visorlog DB schema | **P0** |
| 3 | **`glance compare` — multi-corpus rollup** | The program now has ten+ category surveys with rollups. Cross-survey questions ("which platform class leaks the most PHI?") are answered today by hand-merging JSON. A compare subcommand turns it into one shell command. | M | None internal; consumes own v0.1 output | **P0** |
| 4 | **LLM-based classifier as regex backstop** | The bag-of-fields classifier has a false-negative surface (collection named `documents_2026_01_22` carries PHI but matches nothing). An optional local model pass (Ollama, configurable) classifies names that escaped every regex. Off by default (sealed discipline), opt-in via `--llm-backstop`. Names only — never values. Hashed and rate-limited. | L | Ollama local; sealed-mode contract | P1 |
| 5 | **Differential privacy noise on rollup counts** | When a rollup is published externally (case study, advisory), the per-category counts can be themselves identifying at small N. Add Laplace noise calibrated to a per-survey privacy budget for the "public rollup" output mode. Internal rollup stays exact. | S | None | P1 |
| 6 | **Federated multi-corpus mode** | Two researchers, two air-gapped corpora, one combined rollup. Each side runs `glance scan --emit-shares`, exchanges the noised partials, runs `glance federate` to reconcile. Same compare result, neither side reveals their corpus contents. | L | DP noise (#5) | P2 |

**Deliberately out of scope through v1.0:**

- **GUI / web UI** — works against the "one command per survey" identity. JSON output + downstream visor-report is the right surface.
- **Real-time streaming mode** — glance is offline by design. Streaming reintroduces the read-vs-characterize tension.

The v1.0 thesis: glance is a unix-philosophy filter — sealed corpus in, characterized rollup out, ledger and report do the rest.

---

## 3. `glance compare` — Cross-Category Sensitivity Heatmap

**Subcommand design.**

```bash
glance compare \
  ~/syllabus/cat-01-llm-orch/rollup.json \
  ~/syllabus/cat-02-vectordb/rollup.json \
  ~/syllabus/cat-03-model-serve/rollup.json \
  ~/syllabus/cat-29-argo/rollup.json \
  ~/syllabus/cat-33-ai-email-guard/rollup.json \
  ~/syllabus/vm-verify/rollup.json \
  --output heatmap.json --render ascii
```

**Inputs:** N rollup JSON files (the existing v0.1 output format). No new schema.

**Outputs:** a category-by-survey matrix (rows = surveys, cols = sensitivity categories), each cell = hits per host (normalized for fair comparison across surveys of different sizes). Optional ASCII / SVG / Markdown table renderers.

**Sample heatmap (hits per 100 hosts, shape only):**

```
                          PII   PHI   FIN   DEF   CINF  AI_W  GEN_I
Cat-01 LLM Orchestration   3     1     0     0     0    42    18
Cat-02 Vector DBs         18     7     2     0     1    71     9
Cat-03 Model Serving       5     0     0     0     0    66    11
Cat-04 Training            2     0     0     1     0    58    23
Cat-29 Argo Workflows      1     0     0     0     0    14    51
Cat-31 Data Labeling      31    12     1     0     0    19    14
Cat-32 AI Gateways         9     2    11     0     0    48    16
Cat-33 AI Email Guardrails 22     0     3     0     0    11    27
Cat-34 FastGPT            13     1     0     0     0    52    21
VictoriaMetrics (subst.)   0     0     0     2     8     7    89
─────────────────────────────────────────────────────────────────
Domain leader:           CAT-31 CAT-31 CAT-32 VM    VM   CAT-02 VM
```

**What the heatmap surfaces immediately:**

- **PHI is concentrated in data-labeling** (Cat-31). Disclosure prioritization should follow.
- **AI_WORKLOAD is the modal category everywhere** in the AI tier. Any survey where AI_WORKLOAD does not dominate is either a substrate finding (VM) or a misclassification.
- **CRITICAL_INFRA appears only in VM**. The substrate-vs-AI-native taxonomy split is observable in the data.
- **FINANCE in Cat-32 (AI Gateways)** — the prompt-pricing/billing surface. Worth a deep-dive.

**Implementation footprint:** ~150 LOC. Read the N rollup files, normalize per-survey by host count, render to a Counter-of-Counters. No new dependencies.

---

## 4. Cross-Cutting Insight Extraction — Q1-Q4 × Sensitivity Categories

The DCWF 902 memo of 2026-06-08 introduced the "monitors vs holds" 2×2: Q1 Data-Plane Stores, Q2 Self-Describing Stores, Q3 Read-Heavy Observers, Q4 Topology Mirrors. Glance gives the second axis: sensitivity category mix. Crossing them produces a 4×7 grid that predicts what leaks where.

| Quadrant | Expected dominant category | Why | Confirming evidence |
|---|---|---|---|
| **Q1 Data-Plane Stores** (Chroma, Qdrant, MLflow, Langfuse traces) | **PII + PHI** | Q1 is where records live. The names of collections and projects are application-domain words (`patient_records_2026`, `applicant_resumes`). Bag-of-fields hits at high rate. | Cat-02 Vector DBs: PII 18, PHI 7. Cat-31 Data Labeling: PII 31, PHI 12. |
| **Q2 Self-Describing Stores** (Kafka topics, ClickHouse system.tables, Schema Registry) | **PII + FINANCE** | Schemas embed business domain — `orders`, `payments`, `customers`. | Predicted; needs a dedicated Kafka survey to confirm. |
| **Q3 Read-Heavy Observers** (Prometheus queryAPI, Datadog, Loki) | **AI_WORKLOAD + GENERIC_INFRA** | Observers see metric *labels* not application data. Low PII/PHI rate by design. | Cat-01 LLM Orchestration: AI_WORKLOAD 42, PII 3 — clean Q3 signature. |
| **Q4 Topology Mirrors** (vmagent /api/v1/targets, Consul catalog, kubelet /pods) | **CRITICAL_INFRA + DEFENSE_GOV** | Topology disclosures expose org-chart names. Where the org is a utility or contractor, the org-chart entries match defense/infra dictionaries directly. | VictoriaMetrics: CRITICAL_INFRA 8, DEFENSE_GOV 2 — only column where these are nonzero. Insight #88 generalizes here. |

**The predictive claim.** Each quadrant has a signature category. Surveys that *do not* hit their predicted signature category are flagging either (a) a fingerprint misclassification — the platform isn't in the quadrant we think it is, or (b) a misuse of the platform by the operator. Both are program-worthy findings.

**Operationalization.** Add `--quadrant Q1|Q2|Q3|Q4` to `glance scan`. The tool computes the expected signature category and emits a `quadrant_signature_match: 0.0-1.0` score in the rollup. Visorlog tags low-match surveys for human review.

**Candidate Insight #90** to codify after the next three survey rollups confirm the pattern: *"Sensitivity-category dominance is a function of the platform's data-vs-monitoring posture, not of operator hygiene. Q1 leaks records, Q4 leaks topology. The category mix is a fingerprint."*

---

## 5. Capability Gap to Competitors

**Direct competitors: none.** No public tool does schema-only sensitivity analysis on sealed corpora as its primary function.

| Tool | What they do | What they don't do (glance does) |
|---|---|---|
| **Trufflehog** | Secret scanning in code/repos. | Reads contents. Targets secrets, not category mix. No restraint discipline. |
| **Aikido / Snyk** | SAST/SCA on source code. | Code-side, not corpus-side. |
| **Datadog Cloud Security** | Cloud posture + workload security. Closed source. | Requires agent inside the target. Cannot analyze an external corpus. |
| **Wiz / Orca / Lacework** | Agentless cloud posture. Reads customer cloud APIs. | Inside-the-fence tool. No external-perspective use. |
| **CrowdSec** | Crowdsourced behavioral detection from logs. | Log-side, post-hoc. No corpus characterization. |
| **Microsoft Purview / AWS Macie** | Data classification at rest. | Reads content to classify. Bound to vendor cloud. |
| **Open-source DLP (OpenDLP)** | Pattern-match SSNs, CCs in filesystem scans. | Reads content. Single-pattern PII focus, no taxonomy. |

**What glance does that nothing else does:**

1. **Sealed-mode discipline.** No tool in the comparison set treats "do not read the values" as a contract.
2. **Bag-of-fields category mix.** Seven categories from one corpus in one pass.
3. **Statistical shape as a third channel.** Entropy bucketing distinguishes human-named from random-ID without reading content.
4. **One-command-per-survey ergonomics.** Aligned with the NuClide chain runner pattern.
5. **Public domain license.** Auditable. Embeddable.

**What glance does NOT do that competitors do — and why each is a deliberate scoping choice:**

- **In-place scanning of cloud buckets / SaaS APIs.** Separation is the restraint guarantee.
- **Secret detection.** Different problem. Glance refuses to read values.
- **Real-time / streaming.** Offline-only is the integrity contract.
- **Vulnerability scoring.** Out of scope; visorscuba covers compliance downstream.
- **Enterprise SaaS dashboard.** Different audience, different game.

**Strategic positioning.** Glance is to data classification what nmap is to scanning: a single tool that does one thing and does it composably.

---

## 6. Open-Source Community Strategy

**Target users, in priority order:**

1. **Security researchers** running population-scale studies. NuClide is the founding user; other red-team research groups are the natural second wave.
2. **Internal AI/ML platform teams** who want to characterize their own corpus before exposing it to a vendor classifier. The sealed-mode contract is the unique selling point.
3. **Compliance auditors** doing pre-audit corpus characterization. The category-hit rollup maps directly to HIPAA / PCI / CMMC checklist items.
4. **Journalist-investigators** working on leaked datasets. The sealed contract means they can quantify "how sensitive is this" without reading any individual record.

**The "hello world" demo that lands.** A 30-second README GIF: clone, point at a sample evidence directory shipped in `examples/`, run `glance scan examples/sample-corpus --source generic --name-paths labels`, see the pretty table, see "AI_WORKLOAD: 47 hits, PII: 3 hits."

**Integration that 10x's value.** One-click profile for the dominant data sources:

- `glance kubectl <ns>` — read collection/secret/configmap names from a Kubernetes namespace, never read their values, characterize.
- `glance datadog --account <id>` — read metric names from a Datadog account, characterize. (Read-only API token; never queries values.)
- `glance s3 <bucket>` — read object key names, characterize. (Keys only, never object contents.)

The kubectl one is the cheapest to build and the highest fit for target-user #2 (internal platform teams).

**Contribution pipeline:**

- **Dictionary patches** are the highest-bandwidth contribution. Issue template: `category-suggestion.md`.
- **New source profiles** are the second-most-common PR. Template: copy `extract_vm_verify`, rename, document the input shape.
- **Issues > PRs** for category-mix disputes. The PII-vs-PHI boundary, the AI_WORKLOAD-vs-GENERIC_INFRA boundary — these are taxonomy decisions.
- **CONTRIBUTING.md ships in v0.2** with the dictionary-patch and source-profile templates.

**Launch tactic.** Three blog posts in sequence: (1) "Why sealed-mode matters: restraint as a security tool primitive," (2) "The bag-of-fields classifier — names are the finding," (3) "Comparing ten AI/ML category surveys with one command."

---

_Roadmap horizon: 8–12 weeks to v1.0._  
_Next checkpoint: post-v0.2 release (P0 #1 plugin system + P0 #2 visorlog backend), 2026-07-15._  
_Falsifier: if no external research group adopts glance for their own surveys within 60 days of public launch, the OSS strategy is wrong — likely too NuClide-coupled — and the target-user reordering needs revisiting._
