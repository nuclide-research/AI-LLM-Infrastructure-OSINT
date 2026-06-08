---
type: campaign-attribution
---

# Chroma `trust_remote_code` RCE Mass-Exploitation Campaign (CVE-2026-45829)

_NuClide Research · 2026-06-08_

---

## Summary

On **2026-06-02 between 00:02:06 and 00:04:05 UTC** (119 seconds, single sweep), a single threat actor hit at least **204 globally-exposed Chroma vector databases** with a proof-of-stage exploit targeting CVE-2026-45829 (Chroma `embedding_function.trust_remote_code=True` remote code execution via `transformers.AutoConfig.from_pretrained()` on attacker-controlled model identifiers). Six days later, on 2026-06-08, **201 of 307 verified unauth Chroma hosts (65%) still carry attacker canary collections**, indicating no detection or cleanup by the operators.

The campaign is attribution-grade because the attacker deposited paired canary collections (`probe-base-<ns>` and `probe-ef-<ns>`, matched timestamps) with embedded `model_name: "/nonexistent/cve45829<RAND>"` payloads. The RAND suffix is a per-host attribution token, almost certainly used as a DNS or HTTP callback identifier when the exploit succeeded.

NuClide observed the campaign passively during a Cat-02 vector-DB ledger correction sweep. The corpus had been collected for an auth-posture survey; the canary pattern was clean enough that a 60-line Python diff classified the campaign within minutes of pulling the bodies.

The result is two findings, not one:
1. **Campaign attribution finding** — active exploitation of CVE-2026-45829 in the wild, dated and dimensioned, with attacker TTPs preserved.
2. **80 disclosure candidates** — Chroma hosts with real, non-canary collections (resume RAG, healthcare RAG, enterprise knowledge bases, e-commerce product corpora) still open with no auth. These are unrelated to the campaign and require separate disclosure.

---

## Campaign Dimensions

| Metric | Value |
|---|---|
| Corpus origin | Cat-02 ChromaDB sweep, 2026-06-08 00:46 UTC |
| TIER-2 unauth Chroma confirmed | 307 |
| Hosts carrying campaign canaries (still, after 6d) | **201** (65%) |
| Hosts with no canaries (CLEAN-OPEN, real workloads) | 80 (26%) |
| Hosts unauth + empty (no collections) | 26 (8%) |
| Unique canary timestamp pairs across corpus | 204 |
| Earliest canary timestamp | 2026-06-02 00:02:06.119 UTC |
| Latest canary timestamp | 2026-06-02 00:04:05.139 UTC |
| Total campaign span | **119 seconds** |
| Distinct UTC hours | 1 (single burst) |
| Unique CVE token strings observed | 8 |

---

## Attacker TTPs

### Canary collection convention

Each compromised host receives a paired collection set per probe iteration:
```
probe-base-<19-digit-nanosecond-timestamp>
probe-ef-<19-digit-nanosecond-timestamp>     # same timestamp as the base
```

The naming maps to HNSW index hyperparameters (`base` = base layer, `ef` = exploration factor). On hosts running Chroma ≥ 0.6.x the collections include a `configuration_json.hnsw_configuration` block with stock HNSW defaults (`ef_construction=100`, `M=16`, `space=l2`).

### Exploit payload

The collection config carries:
```json
"embedding_function": {
  "type": "known",
  "name": "sentence_transformer",
  "config": {
    "device": "cpu",
    "kwargs": {"trust_remote_code": true},
    "model_name": "/nonexistent/cve45829<RAND>"
  }
}
```

`trust_remote_code=True` is the load-bearing flag. When Chroma instantiates the embedding function (lazily, on first `add` or `query`), it calls `transformers.AutoConfig.from_pretrained(model_name, trust_remote_code=True)`. The `/nonexistent/cve45829<RAND>` path resolves to a HuggingFace lookup; if the attacker controls the namespace (or the lookup is sandboxed through their proxy), arbitrary Python in `configuration_<X>.py` runs in the Chroma worker context.

The path prefix `/nonexistent/` is the diagnostic dead-giveaway: the attacker is *not* trying to execute code on this pass — they are confirming the host will accept the staged config. The RAND token (per-host unique) lets them correlate which hosts the second-stage payload should target.

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
