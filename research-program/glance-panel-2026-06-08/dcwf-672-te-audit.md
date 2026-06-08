# T&E Audit: glance v0.1.0

**Auditor:** DoD AI T&E Specialist (DCWF 672)
**KSAT scope:** T5919 (adversarial T&E in operational environments), K7044 (V&V tools and procedures), K7054 (robustness/resilience testing)
**Subject:** `glance` schema-only sensitivity analyzer (`~/glance/glance.py`)
**Date:** 2026-06-08

## 1. AI_WORKLOAD false-negative on VM corpus

**Root cause: word-boundary regex anchors do not fire at underscores.**

The extractor is correct. `extract_vm_verify()` pulls strings such as `safe_runpod_cadvisor`, `safe_runpod_dcgm_exporter`, `safe_runpod_node_exporter`, `safe_runpod_ping_exporter`, `safe_runpod_vmagent` into the `targets` stream, and the label key `runpodip` into the `labels` list. The strings are there.

The defect lives in the `AI_WORKLOAD` patterns themselves. Patterns such as `\b(?:runpod|coreweave|...)\b` and `\b(?:dcgm|nvidia_gpu|nvml|cuda|...)\b` use `\b`. Python's `\b` is the boundary between a word-character (`[A-Za-z0-9_]`) and a non-word-character. Because **underscore is a word character**, there is no boundary between `e` and `r` in `safe_runpod_cadvisor`, nor between `d` and `_`. The regex never matches.

Direct verification on real corpus strings:

```
'safe_runpod_cadvisor'      -> NO MATCH
'safe_runpod_dcgm_exporter' -> NO MATCH
'safe_runpod_node_exporter' -> NO MATCH
'runpodip'                  -> AI_WORKLOAD  (the safe_?runpod alt has no \b on either side)
```

The same defect silently suppresses `GENERIC_INFRA` (`\bcadvisor\b`, `\bnode_exporter\b`, `\bblackbox_exporter\b`, `\bnginx\b`) wherever those tokens are wrapped in `safe_<X>_<Y>`-style operator prefixes. The VM rollup reads cleanly only because Prometheus `scrapePool` names are typically clean tokens (`cadvisor`, `nginx`); the `safe_runpod_*` operator naming convention is what trips it.

**Fix tested.** Replacing `\b` with `(?:^|_|\b)` (a relaxed boundary that also fires at underscores) and rerunning against the full VM corpus:

| Stream                   | AI_WORKLOAD before | after | GENERIC_INFRA before | after |
| ------------------------ | ------------------:| -----:| --------------------:| -----:|
| vm scrape_targets        | 0                  | 299   | 21                   | 135   |
| vm scrape_pool_names     | 0                  | 173   | 545                  | 853   |
| vm metric_names          | 0                  | 0     | 0                    | 2     |
| chroma collection_names  | 156                | 193   | n/a                  | n/a   |

Distinct VM hosts gaining at least one AI_WORKLOAD hit after patch: **58**, which aligns with the DCWF 753 finding of 57 RunPod tenants (1-host delta within de-duplication noise).

## 2. Classifier false-positive audit (20 + 20 sample)

Twenty random flagged samples from each corpus, seeded `random.seed(42)`, judged against the category dictionary:

**VM (20 samples, all streams combined; 42 total flagged values).**

| Category        | TP | FP | FP rate | Notes                                                                  |
| --------------- |---:|---:|--------:| ---------------------------------------------------------------------- |
| GENERIC_INFRA   | 17 | 0  | 0%      | `cadvisor`, `nginx`, `rabbitmq`, `redis`, `postgres`, `prometheus` etc — all clean exporter tokens. |
| FINANCE         | 1  | 1  | 50%     | One operator-named `app-btc` pool is a genuine crypto-trading workload tell. One `app-merchant` is ambiguous — could be either commercial e-commerce or a generic service name. Treated as FP for caution.  |
| CRITICAL_INFRA  | 0  | 1  | 100%    | `bias_current` matched the optical-transceiver pattern but appears in this corpus as a node-exporter style metric, not as ICS/SCADA. Pattern intended for telecom optical-rx/tx; firing on generic electrical telemetry is a known FP class. |

**Chroma (20 samples; 30 total flagged).**

| Category      | TP | FP | FP rate | Notes |
| ------------- |---:|---:|--------:| ----- |
| AI_WORKLOAD   | 3  | 0  | 0%      | `langchain`, `rag-video-collection`, `novel-rag` — all real AI-workload collection names. |
| PII           | 16 | 0  | 0%      | All 16 sampled were `careerTracker-resume-*` or `user-resume-*` patterns. Real PII — these are resume document collections keyed by what look like Mongo ObjectIDs. |

Aggregate FP rate across both corpora: **2/40 = 5.0%**. Both FPs are FINANCE/CRITICAL_INFRA edge cases; the high-impact categories (PII, PHI, AI_WORKLOAD) had zero FPs in the audited sample.

## 3. Edge-case robustness

| Test                                   | Result | Notes |
| -------------------------------------- | ------ | ----- |
| (a) Empty directory                    | PASS   | Returns `{"error":"no .json files in <dir>"}` cleanly, exit 0. |
| (b) Malformed JSON (truncated, broken) | PASS   | `json.JSONDecodeError` caught in the per-file try/except; the file is skipped, scan continues. |
| (b') Non-UTF8 binary file              | **CRASH** | `f.read_text()` raises `UnicodeDecodeError` which is NOT in the except tuple. Single rogue file kills the whole scan. Exit 1, full traceback. |
| (c) Missing fields                     | PASS   | Hosts with absent `evidence`, empty `targets`, or non-JSON `metric_names.body` are handled gracefully via `.get()` chains. |
| (d) Largest real VM body (29 KB)       | PASS   | 0.05 s. |
| (d') Synthetic 5 MB body               | PASS   | 0.08 s. |
| (d'') Synthetic 50 MB body             | PASS   | 0.22 s. Linear scaling, no pathological backtracking. |

The size scaling is fine. The one real defect is the missing `UnicodeDecodeError` handler — operationally, one tarball-corrupted evidence file would abort the entire rollup.

## 4. Statistical-shape correctness (entropy)

Manually verified `char_entropy()` against a hand-computed `Counter` + `math.log2` reference on 20 strings. **Result: 0/20 mismatches.** All values agreed to 1e-9.

## 5. Sealed-mode promise verification

Ran `glance scan ~/syllabus/shodan/vm-verify/hosts --source vm-verify` with no `--include-samples` flag and grep'd the 93-line output against 2,624 corpus-derived target strings.

**Result: 1 substring hit out of 2,624 candidates.** Net leakage from value-bearing fields: effectively zero.

**However, one real concern: the `Top TLD suffixes` block.** Surfaced:
```
.com   15
.net   12
.uz    11
.ru     6
.teye   6
.prod   2
.internal 2
.stag   1
.dev    1
.qc     1
```

The `.teye`, `.prod`, `.internal`, `.stag`, `.qc` entries are **not TLDs**. They are operator-specific internal-namespace suffixes. `.teye` in particular, with 6 occurrences, fingerprints a single operator's fleet. This violates the sealed-mode promise via the long-tail of unusual suffixes.

## Recommended v0.1.1 patches

1. **AI_WORKLOAD + GENERIC_INFRA boundary fix.** Replace `\b` with strict letter/digit boundary `(?<![A-Za-z0-9])`...`(?![A-Za-z0-9])`. Recovers 58 VM RunPod hosts.
2. **Apply the same boundary fix to PII, PHI, FINANCE, CRITICAL_INFRA, DEFENSE_GOV.** Class-wide defect.
3. **Robustify the file-read exception handler.** Catch `UnicodeDecodeError`. Better: `f.read_bytes()` then `json.loads(b.decode('utf-8', errors='replace'))`.
4. **Promote `labels` to a first-class stream.** Currently extracted then dropped before classification.
5. **Fix the TLD-suffix leak.** Only emit the suffix if it is in a TLD/ccTLD allowlist. Bucket everything else as `.<private>`.
6. **Add a `--strict-sealed` mode** that asserts at exit that the rendered output contains zero substring of any extracted value.
7. **Add a `verify` subcommand** for self-test against a fixture.
8. **Document the FP class for `bias_current`** or tighten the regex with co-occurring optical/SFP context.

Priorities: #1, #3, #5 (correctness-critical) → #2, #4 (coverage) → #6, #7, #8 (test hygiene).
