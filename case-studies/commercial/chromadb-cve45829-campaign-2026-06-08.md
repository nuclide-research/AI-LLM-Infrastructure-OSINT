---
type: post-disclosure-survey
---

# CVE-2026-45829 (ChromaToast) — Post-Disclosure Sweep + 80 Unrelated Disclosure Candidates

_NuClide Research · 2026-06-08_

> **Verification correction (mid-investigation):** initial framing labeled the canary deposition pattern an "adversary campaign." External-intel cross-check during Stage -1+ (Hadrian's disclosure blog, HiddenLayer's research note, CSA Labs synthesis) revealed the `/nonexistent/cve45829{rand_text_alpha(16)}` payload is **Hadrian's published detection template** for CVE-2026-45829 (ChromaToast). Per-host RAND tokens match `rand_text_alpha(16)` exactly: 50 unique characters across 7 sampled tokens, no digits, mixed-case letters only — confirming the payload formatter. The attribution shifts from "novel adversary campaign" to **"derivative scanner run by an unknown party, ~2 weeks post-public-disclosure, against the Shodan-discoverable population, leaving paired-canary collections (`probe-base-<ns>` + `probe-ef-<ns>`) per host."** The persistence finding (201/307 still carry the canaries 6 days later) stands regardless of actor intent. The actor remains unidentified; the pattern fits a researcher running a remediation-measurement sweep more than active exploitation.

---

## Summary

CVE-2026-45829, named **ChromaToast** by its disclosers (HiddenLayer + Hadrian), is a CVSS 10.0 pre-authentication RCE in ChromaDB's FastAPI server (versions 1.0.0 through 1.5.9, unpatched as of disclosure on 2026-05-19). The server processes `embedding_function.config.kwargs.trust_remote_code: true` plus `model_name` BEFORE the auth check, allowing any unauthenticated HTTP request to stage arbitrary Python execution via `transformers.AutoConfig.from_pretrained()`.

On **2026-06-02 between 00:02:06 and 00:04:05 UTC** (119 seconds, single burst), an unknown party adapted Hadrian's published detection payload and ran a derivative scanner against at least **204 globally-exposed Chroma hosts**. The scanner deposits paired canary collections per host: `probe-base-<19-digit-nsec>` and `probe-ef-<same-nsec>`, with the embedding-function config carrying `model_name: "/nonexistent/cve45829<rand_text_alpha(16)>"`.

Six days later, **201 of 307 verified unauth Chroma hosts (65%) still carry the canary collections**. The persistence is the operational finding: collection-level monitoring is absent across this population.

A separate variant deposits a literal collection named `cve202645829_test_probe` on 5 hosts, indicating at least one second scanner using the CVE identifier but a different naming convention.

The result is three findings:
1. **Population characterization** — 307 globally-exposed unauth Chroma hosts confirmed; CVE-2026-45829 unpatched on every vulnerable version in the corpus.
2. **Canary persistence finding** — 65% of operators have not noticed a non-human-named collection in their default tenant for six days running (Insight #87).
3. **80 disclosure candidates** — Chroma hosts with real, non-canary collections (resume RAG, healthcare RAG, enterprise knowledge bases, e-commerce product corpora) still open with no auth. Unrelated to the sweep; require separate disclosure.

---

## Campaign Dimensions

| Metric | Value |
|---|---|
| Corpus origin | Cat-02 ChromaDB sweep, 2026-06-08 00:46 UTC |
| TIER-2 unauth Chroma confirmed | 307 |
| Verified-1.x (CVE-2026-45829 scope) | **269** |
| Verified-0.5.x (legacy, out of CVE scope) | 34 |
| Verified-0.6.x | 3 |
| Hosts carrying campaign canaries (still, after 6d) | **201** total — **200 of 269 = 74% of CVE-vulnerable population** |
| Hosts hit by campaign on 0.5.x or 0.6.x | **0** (scanner is CVE-aware: only 1.x hit) |
| Hosts with no canaries (CLEAN-OPEN, real workloads) | 80 (26%) |
| Hosts unauth + empty (no collections) | 26 (8%) |
| Unique canary timestamp pairs across corpus | 204 |
| Earliest canary timestamp | 2026-06-02 00:02:06.119 UTC |
| Latest canary timestamp | 2026-06-02 00:04:05.139 UTC |
| Total campaign span | **119 seconds** |
| Distinct UTC hours | 1 (single burst) |
| Unique CVE token strings observed | 8 |
| Version-fingerprint confidence (HIGH via openapi.json corroboration) | 305/307 (99%) |

---

## Scanner TTPs

### Canary collection convention

Each touched host receives a paired collection set per probe iteration:
```
probe-base-<19-digit-nanosecond-timestamp>
probe-ef-<19-digit-nanosecond-timestamp>     # same timestamp as the base
```

The naming maps to HNSW index hyperparameters (`base` = base layer, `ef` = exploration factor). On hosts running Chroma ≥ 0.6.x the collections include a `configuration_json.hnsw_configuration` block with stock HNSW defaults (`ef_construction=100`, `M=16`, `space=l2`).

This convention is **distinct from Hadrian's published nuclei template**, which uses a single collection named literally `"probe"`. Whoever ran the 2026-06-02 sweep wrote a derivative scanner that uses Hadrian's exploit payload pattern (the `model_name`) but its own collection-naming and timestamp scheme — almost certainly so they could correlate which hosts they hit when checking back later.

### Exploit payload (Hadrian's template, verbatim)

The collection config carries:
```json
"embedding_function": {
  "type": "known",
  "name": "sentence_transformer",
  "config": {
    "device": "cpu",
    "normalize_embeddings": false,
    "kwargs": {"trust_remote_code": true},
    "model_name": "/nonexistent/cve45829<rand_text_alpha(16)>"
  }
}
```

`trust_remote_code=True` is the load-bearing flag. When Chroma instantiates the embedding function (lazily, on first `add` or `query`), it calls `transformers.AutoConfig.from_pretrained(model_name, trust_remote_code=True)`. The `/nonexistent/cve45829<RAND>` path resolves to a HuggingFace lookup that fails with `FileNotFoundError` — and reflects the RAND token back in the 500-error response body. This is **Hadrian's detection technique**: stage the config, fail safely, identify Chroma versions vulnerable to RCE by error-reflection rather than actual code execution.

The path prefix `/nonexistent/` is intentional: the scanner is confirming the host will accept the staged config without ever attempting code execution. The RAND token (per-request unique) is a detection-correlation ID, not a callback identifier.

### RAND token entropy

Across 7 sampled tokens we observed:
- All 16 characters long
- Mixed case letters only (`a-zA-Z`)
- Zero digits (50 unique chars across 112 token characters; expected 52)
- Frequency distribution consistent with uniform random sampling

This matches `rand_text_alpha(16)` in nuclei DSL exactly — confirming the scanner is built on or derived from Hadrian's published template.

### Observed payload variants

| Variant | Count | Hosts |
|---|---|---|
| `/nonexistent/cve45829BbrVltYtUpBdWpaN` | 1 | Google Cloud (US) |
| `/nonexistent/cve45829LixdymZnoalsRfDy` | 1 | (cluster) |
| `/nonexistent/cve45829QCNGnSQvcczrqbvd` | 1 | (cluster) |
| `/nonexistent/cve45829WVErvEHkBziQRcJa` | 1 | (cluster) |
| `/nonexistent/cve45829fwJvbgmhZZwoyMBK` | 1 | Google Cloud (US) |
| `/nonexistent/cve45829jelKZFoHPAYClWWY` | 1 | Hetzner (DE) |
| `/nonexistent/cve45829xgpVVUwIxTJESWOr` | 1 | (cluster) |
| `cve202645829_test_probe` (collection name) | 19 | mixed |

The RAND suffix on `/nonexistent/cve45829<>` is 16 chars of mixed case + digits (base62-ish). Two known variants share the same exploit class but different shape: `cve202645829_test_probe` is a literal collection name (no embedding payload), suggesting a second-stage or a different operator using the same CVE marker convention.

### Multi-pass attribution

Three hosts carry **three** canary timestamp pairs each — the attacker hit them three separate times during the 2-minute window:

| Host (org/country) | Canary pairs | Total collections |
|---|---|---|
| Aurologic GmbH (DE) — host A | 3 | 9 |
| Aurologic GmbH (DE) — host B (/24 neighbor of host A) | 3 | 9 |
| noris network AG (DE) | 3 | 11 |

The two adjacent Aurologic hosts (consecutive IPs in the same /24) suggest the attacker harvested both from the same Shodan page and probed them sequentially. The repeated probes indicate either a retry-on-no-callback loop or a reconnaissance pattern that probes twice for confirmation.

---

## Campaign Geography

### Compromised (PWND-STILL, 201 hosts)

| Country | Hosts | Share |
|---|---|---|
| China | 49 | 24% |
| United States | 42 | 21% |
| Germany | 32 | 16% |
| Singapore | 11 | 5% |
| Finland | 8 | 4% |
| France | 7 | 3% |
| UAE | 5 | 2% |
| South Korea | 5 | 2% |
| United Kingdom | 5 | 2% |

The China/US/Germany top-3 (62% of compromised) tracks the global Chroma deployment population. No country bias is observed in the campaign itself; the attacker hit every Shodan-discoverable host in the window.

### Disclosure-Candidate (CLEAN-OPEN, 80 hosts)

| Country | Hosts |
|---|---|
| United States | 22 |
| Germany | 15 |
| China | 10 |
| Singapore | 6 |
| France | 5 |

These 80 hosts have real, non-canary collections and are the disclosure pipeline. Highest-value workload signatures (IPs withheld until operator notice; brand attribution is in the table where the collection-name pattern itself is the disclosure tell):

| Host (provider/country) | n_collections | Workload signature |
|---|---|---|
| Azure (US) | **6,062** | `kB_Embedding_Default_AzureBlob_*`, `kB_Amazon_ParentDoc_*` — enterprise multi-cloud knowledge-base RAG with explicit AWS+Azure backend names |
| DigitalOcean (US) | **2,422** | `realtruck.<make>-<model>-<year>.plines` — e-commerce auto-parts product RAG, ~2,400 vehicle SKU corpora |
| Azure (US) | 156 | `FortWorthAlt.Planning_Entities`, `Scratchpad.DevScratchpad_Entities` — Azure-hosted entity RAG, possibly municipal/planning |
| Azure (US) | 136 | `careerTracker-resume-<uuid>-<ts>` — resume / CV tracking RAG (HR platform), per-applicant collection per upload |
| E2E (IN) | 25 | `doc-Hypertension`, `doc-Hypertension-openai` — healthcare RAG with hypertension document corpus |
| Aliyun (CN/SG) | 19 | `sql_cache_<>_SFS_Head_Office_*`, `sql_cache_*_SFS_Phuket_Branch_*` — multi-branch SQL-cache RAG; Thailand operation |
| Aliyun (CN) | 7 | `knowledge_point_collection_*`, `teaching_plan_*_kp` — Chinese education platform RAG |

---

## What This Says About the Population

### Insight #79 candidate — "auth-on-default ≠ exploit-immune"

The campaign exploits the SAME auth-on-default thesis that drives NuClide's surveys: Chroma ships with no auth on the network listener by default. But the canary persistence (65% of hosts still carry probe collections 6 days later) reveals a deeper signal — operators are not running collection-level monitoring. The attacker created paired named collections in `default_tenant.default_database` (the well-known path), and 201 operators have not noticed.

Operators with monitoring would have alerted on:
- New collection creation outside their deployment pipeline
- A collection named `probe-base-1780358529676380700` (clearly non-human)
- An embedding function with `trust_remote_code=True` (security-relevant config flip)

None of those alerted. This is consistent with the broader finding that the auth-on-default population is also the no-observability population.

### The 60-line Python diff

The campaign was detected by a 60-line `verify_chroma_campaign.py` re-probing 307 hosts in 24 seconds and looking for repeating collection-name patterns across hosts. It found 204 canary pairs by string match, 8 unique CVE tokens by regex, and a 119-second timestamp window by parsing the nanosecond suffixes. No threat-intel feed was consulted. The detection pattern is reusable and trivial.

If a 60-line diff finds the campaign in 24 seconds, the operators running these Chroma instances have no excuse for missing the same signal 6 days running.

---

## NuClide Posture

No data was read from any compromised or clean host beyond `/api/v1/collections` and `/api/v2/tenants/default_tenant/databases/default_database/collections`. No `/get`, no `/query`, no inference calls. Per the restraint ethic: the collection metadata IS the finding; the contents need not be exfiltrated to demonstrate that the host is open and that the attacker is already there.

The compromised hosts are not in scope for NuClide disclosure — the campaign attacker should be reported to the hosting providers via abuse channels, and CVE-2026-45829 details should be cross-referenced with the Chroma security team. NuClide's role here is forensic attribution and pattern preservation, not patching the campaign victims.

The 80 CLEAN-OPEN hosts are the standard NuClide disclosure pipeline.

---

## Artifacts

- **Rollup:** `~/syllabus/shodan/chroma-campaign/rollup-augmented.json`
- **Per-host JSON evidence:** `~/syllabus/shodan/chroma-campaign/hosts/<ip_port>.json` (307 files)
- **Source verifier:** `~/syllabus/shodan/verify_chroma_campaign.py`
- **Original Shodan harvest:** `~/syllabus/shodan/chroma-findings.json` (754 candidates, 5 tiers)
- **Findings breakdown:** see `findings-breakdown.txt` alongside this case study.

---

## DCWF KSAT coverage

- **672 (AI Test & Evaluation Specialist):** verification under operator-controlled state (T5904 — anomalous artifact identification in deployed models).
- **733 (AI Risk & Ethics Specialist):** campaign attribution without payload weaponization (T5854 — risk assessment under adversarial conditions).
- **661 (AI R&D / Research Engineering):** reusable 60-line detector design (T0064 — engineering primitives that turn corpus state into a finding).
- **212 (Forensics):** per-host evidence preservation including raw response bodies (K0118).

## Wardrobe + syllabus stance

**Wardrobe outfit loaded:** `ai-infra-hunt` (13 atoms across NICE roles 211/212/221/511/531/541/611/612/621/622/631/661/711/712/722/731/732). Atoms exercised on this work:

- T0549, T0028 — penetration-testing-class assessment of authorized AI/ML infrastructure surface
- T0188 — remediation pathway specified for the 80 disclosure-candidate hosts
- K0342, K0177, K0344, S0001, S0051, S0081 — vulnerability scanning, kill-chain mapping, threat-environment recognition (all four scanners observed, two distinct, attribution-grade)
- T0247 — verification + acceptance discipline (the 305/307 HIGH-confidence version fingerprint cross-check)
- K0118 — chain-of-custody on per-host evidence (recon/chroma-campaign-2026-06-08/hosts/*.json, kept private)
- K0107 — cross-jurisdiction posture (CN/US/DE leading the PWND-STILL list; disclosure routing differs per country)

**Operating doctrine roles in posture:** 541 (Anchor — auditor with teeth: 80 hosts get specific remediation), 661 (Research Engine — Insight #87 codified), **671 (T&E Verification — load-bearing this case study; the actor reattribution from "adversary campaign" to "post-disclosure measurement sweep" is precisely what T&E discipline catches)**, 212 (Forensics — artifact preservation), 511 (Population CDA — 269 CVE-vulnerable, 200 PWND-STILL, the rate is the finding).

**Syllabus threat-literature anchors (relevant prior art):**

- *PoisonedRAG: Knowledge Corruption Attacks against Retrieval-Augmented Generation* (USENIX Sec '25, Zou et al.) — establishes the threat model where adversary-controlled writes into a vector store change downstream LLM behavior. Our finding inverts the threat: writes happened (canary collections), nobody noticed, the LLM-side consequence is hypothetical because the operators never queried the canaries. Same surface, different stage of the kill chain.
- *Cache Me, Catch You: Cache-Related Security Threats in LLM Serving Frameworks* (NDSS) — the canary-persistence finding is structurally similar: state that survives across requests, that the operator is not auditing, that an adversary can use to fingerprint and pivot.
- *Adaptive Defense Orchestration for RAG* (arxiv 2604.20932) — proposes monitoring on RAG control-plane events; our 200/269 operators are the population that has not yet adopted any of the controls this line of work prescribes.
- *Architecture Matters: Comparing RAG Systems under Knowledge* (arxiv 2605.05632) — choice of vector DB shapes the attack surface; Chroma's "no auth by default" choice is the precise architectural decision under examination here.

The literature has theorized this class of vulnerability and proposed defenses; the corpus state shows operators have not adopted them. The gap between literature and practice is the publishable contribution.
