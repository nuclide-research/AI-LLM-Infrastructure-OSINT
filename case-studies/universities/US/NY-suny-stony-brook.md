# SUNY Stony Brook: Biology Department, OLMo Research Stack + Cloud Proxy

_NuClide Research · 2026-05-01_

---

## Summary

SUNY Stony Brook Biology Department server (`040-218.bio.sunysb.edu`) is running Ollama with the full Allen AI OLMo-3 research stack (olmo-3, olmo-3.1-32b-think, olmo-3.1-32b-instruct) alongside `gpt-oss:latest` cloud proxy and several Gemma 4 models. Unauthenticated, publicly accessible.

---

## Infrastructure

| Field | Value |
|---|---|
| IP | 129.49.40.218 |
| rDNS | `040-218.bio.sunysb.edu` |
| Org | State University of New York at Stony Brook |
| Department | Biology |
| Country | US, New York |
| Open ports | 11434 (Ollama, **public**) |

---

## Models

| Model | Size | Notes |
|---|---|---|
| gpt-oss:latest | ? | ☁️ Cloud proxy |
| olmo-3:latest | ? | Allen AI OLMo-3 |
| olmo-3.1:32b-think | ? | Allen AI OLMo-3.1 reasoning |
| olmo-3.1:32b-instruct | ? | Allen AI OLMo-3.1 instruct |
| mistral-small3.2:latest | ? |, |
| gemma4:26b | ? |, |
| gemma4:latest | ? |, |
| lfm2:latest | ? | Liquid FM-2 |

---

## Findings

**F1, Biology Research Server (HIGH):** OLMo models (Allen AI's open research language models) suggest active NLP/bioinformatics research. Model injection via CVE-2025-63389 affects research outputs.

**F2, Cloud Proxy Exposure (HIGH):** `gpt-oss:latest` present. Status (200 OK vs 401) not confirmed in final probe.

**F3, Model Injection (HIGH):** All models injectable via CVE-2025-63389.

---

## Disclosure

- **Discovered:** 2026-05-01
- **Status:** Pending outreach to SUNY Stony Brook IT Security

---

## Re-verification (2026-05-19 .edu sweep, via visorgoose)

The same host (`040-218.bio.sunysb.edu`, 129.49.40.218) re-surfaced during the 2026-05-19 visorgoose `--tld .edu` scan (after the G8 fix unlocked `.edu` TLD support).

### Wave-2 observations (verifying continued exposure)

`GET http://129.49.40.218:11434/api/version` → 200 with `{"version":"0.20.7"}` — same version as Stage-0 capture.
`GET .../api/tags` → 200 with 8-model inventory; first entry `olmo-3:latest` (consistent with prior).
`GET .../api/ps` → 200 with `{"models":[]}` — no model currently loaded in resident memory at probe time.

Host continues to expose the Ollama API on port 11434 with the OLMo research-stack inventory documented above. **No state change observed between 2026-05-01 and 2026-05-19** — the host remains live with the same auth-on-default posture.

This is informational confirmation, not a new finding. The host re-surfaced because visorgoose's `.edu` TLD support (G8 fix) caught it via the CT-log + DNS resolution pipeline alongside the IDs from the 2026-05 capture. Cross-tool convergence (Stage-0 dork-map + visorgoose CT-log harvest + direct probe) on the same host adds confidence to the operator-attribution and service-classification confidence.

### Class-membership update (no tier labels per survey convention)

- 18-day continued-exposure observation — OBSERVED
- Consistent cross-tool identification (Stage-0 + visorgoose + direct probe) — OBSERVED
- No remediation observed — OBSERVED (the host's posture is unchanged since the 2026-05-01 documentation)

### Source artifacts (wave-2 re-verification)

- visorgoose state: `~/recon/edu-llm-infra-2026-05-19/stage2-wave2/visorgoose-edu-state.json` (SUNY-SB-bio-218 entry)
- visorgoose report: `~/recon/edu-llm-infra-2026-05-19/stage2-wave2/visorgoose-edu-report.md`
- Direct probe: `~/recon/edu-llm-infra-2026-05-19/stage2-wave2/vg-priority-direct-probe.json` (SUNY-SB-bio-218 section)
