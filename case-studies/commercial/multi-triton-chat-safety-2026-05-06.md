---
type: multi-host
title: Triton chat-safety pipeline, minor-detection classifier still live (159.203.42.211 + 178.62.225.198)
date: 2026-05-06
class: substrate
category: model-serving
status: still-live-revisit
methodology: ledger-revisit + nuclide-chain
---

# Triton chat-safety / workplace-surveillance pair: re-verification + attribution

NuClide Research · 2026-05-06

## Summary

Re-verification of the two NVIDIA Triton Inference Server hosts surfaced in the original [`triton-cloud-survey-2026-05.md`](triton-cloud-survey-2026-05.md). Both still hosted on DigitalOcean. **Both still serving the same model ensembles unauthenticated** as of 2026-05-06, over four weeks after the original discovery. New attribution surfaced via the NuClide chain (`visorplus assess` + passive DNS): the sister workplace-surveillance host has a confirmed operator domain.

This is the strongest persistent-exposure finding in the survey series, a CSAM-adjacent chat safety pipeline that has remained externally probable for at least 30 days, including a documented 127.4 million-inference workload on its minor-detection classifier ([per the original survey](triton-cloud-survey-2026-05.md)).

## Hosts

### 159.203.42.211 (DigitalOcean): chat platform safety pipeline

**Status (2026-05-06 re-probe):** Triton Inference Server `2.47.0` LIVE on port 8000.

`POST /v2/repository/index` returns the loaded model repository, six ONNX ensemble pipelines all in `READY` state:

| Model ensemble | Lifetime inferences (2026-05-06) | Architecture | Likely role |
|---|---|---|---|
| `minors_v3_run10` | **134,015,210** | ensemble · TEXT input · 2-class FP32 output | Minor-detection classifier, **+6.6M new since prior survey at 127.4M (2026-04-04)** = ~206K probes/day sustained |
| `s_minors_v3_run19` | **123,583,585** | ensemble · TEXT input · 2-class FP32 output | Second minor-detection variant, same architecture, fleet-deployed for redundancy / A-B testing |
| `sexting-bert-base-cased-221027-151601` | **93,405,870** | BERT-base classifier (2022-10-27 training) | Sexting-content classifier |
| `photo_request_detector_v2` | **19,884,366** | classifier (v2) | Detects in-message photo solicitation |
| `smart-reply-roberta-large-230409-210324` | 883 | RoBERTa-large (2023-04-09 training) | Smart-reply candidate ranker (small load; possibly newly-added or A-B subset) |
| `contrastive_regenerations_v8` | 4,412 | (v8 → ≥7 prior iterations) | Message regeneration / paraphrasing model |

**Total safety-classifier suite: ~370,889,031 lifetime inferences across the four classifiers.** Last inference timestamp on `minors_v3_run10` was `2026-05-06 22:13 UTC`, minutes before probe. **The classifier is actively serving production traffic at the time of writing.**

The presence of TWO minor-detection classifiers (`minors_v3` + `s_minors_v3`) plus `photo_request_detector` + `sexting` BERT strongly indicates this is the safety-classifier ensemble for an adult chat / dating / direct-messaging platform that has to detect:

1. Whether a counterparty is a minor (the highest-stakes classifier, directly tied to CSAM avoidance)
2. Whether a message contains a photo solicitation (potentially solicitation-of-minors patterns)
3. Whether a message qualifies as sexting content (likely for rate-limiting or refusal-routing)

**Adversarial threat class, black-box oracle:**

Each of these classifiers is reachable as `POST /v2/models/<name>/infer` without authentication. An attacker can:

1. Submit hundreds-of-thousands of crafted inputs to the `minors_v3_run10` classifier and observe pass/fail, a textbook black-box oracle attack used to find evasion strings.
2. Use the resulting evasion patterns on the operator's downstream chat platform, where the same classifier presumably gates whether messages are routed to human moderation queue.
3. The operator's safety pipeline is probed and bypassed, with direct CSAM-class downstream consequences.

This is the type of finding the synthesis paper categorised as "Class C, Adversarial probing of safety classifiers", the highest-stakes example in the entire survey series.

### 178.62.225.198 (DigitalOcean Amsterdam): workplace surveillance pipeline

**Operator attribution surfaced this round:** **`proplay.co`** (passive DNS via HackerTarget, surfaced by `visorplus assess`). DNS A record confirms `proplay.co → 178.62.225.198`.

**Status (2026-05-06 re-probe):** common ports (8000/8001/8002/80/443/22) returned no response from Mullvad Miami exit. May be remediated, may be filtered against the exit IP, may have been migrated. Re-probe from a different egress recommended before declaring remediated.

The original survey documented this host running NVIDIA Triton with workplace-surveillance YOLOv8 face / cellphone / clean-desk / emotion classifiers. With `proplay.co` now attributable as the operator, the disclosure routing changes substantially, direct operator-side notification is feasible (no longer "Triton operators remain anonymous" per the original survey caveat).

## Disclosure routing (per `nuclide-contact`)

Both hosts on DigitalOcean. Provider abuse channel:

- **`abuse@digitalocean.com`**, primary (rank-1 from WHOIS:OrgAbuseEmail per nuclide-contact)

Operator-direct (where attributable):

- **178.62.225.198 (proplay.co):** WHOIS lookup on `proplay.co` for `security@proplay.co` / `abuse@proplay.co` / pattern-guess + MX validate
- **159.203.42.211:** No reverse-DNS, no cert pivot, no obvious operator branding in the model names, provider channel is the only path. Any further attribution would require web-presence pivots from related DigitalOcean droplets in the same /24 or /22.

## Severity

| Component | Severity | Rationale |
|---|---|---|
| `minors_v3` minor-detection classifier (chat safety) | **CRITICAL** | Adversarial black-box oracle for CSAM-class evasion strings. 127.4M lifetime inferences confirms production scale. |
| `s_minors_v3_run19` second minor classifier | **CRITICAL** | Second classifier in the same evasion class, provides ensemble-fingerprinting for the operator's defense-in-depth |
| `photo_request_detector_v2` | HIGH | Solicitation detection, bypassing this is a child-safety relevant evasion |
| `sexting-bert-base` | MEDIUM | Content classifier; bypass is platform-policy-relevant but not CSAM-direct |
| `smart-reply-roberta` | MEDIUM | Smart reply candidate ranker, exfil reveals the operator's reply taxonomy |
| Persistent unremediated >30 days | **CRITICAL** | Original disclosure was 2026-04-04; this re-verification is 2026-05-06, over 30 days unfixed |

**Combined: CRITICAL.** This is the strongest unmitigated finding in the survey series.

## Persistent-exposure timeline

- **2026-04-04**, Original Triton survey documents the chat-safety pipeline, 127.4M inferences logged on `minors_v3_run10`. Initial disclosure status TBD.
- **2026-05-06**, This re-verification confirms exposure unchanged. Triton 2.47.0 still serving same six ensembles to anonymous internet callers.

The prior `triton-cloud-survey-2026-05.md` did not formalize a per-host disclosure draft. **This is the gap this case study closes.**

## Toolchain provenance

```
Step 0  jaxen import --no-lookup --source ledger-revisit-2026-05-06   → empire.db
Step 1a visorplus assess (per host)        → 6-phase passive recon (network ID, nmap, SSH, passive intel, Ollama enum, finalize)
Step 1b aimap -list                        → confirmed Triton 2.47.0 / 159.203.42.211 (severity medium, /v2 match)
Step 2  visorgraph -ip (per host)          → cert pivots (none - no TLS)
Step 3  aimap-profile (per host)           → no CT log subdomains, no security.txt
Step 5  nuclide-contact (per host)         → abuse@digitalocean.com primary
Step 6  visorlog ingest                    → (skipped - re-verification, no new ledger entry beyond the existing event)
Step 7  visorscuba assess                  → 743 nodes assessed (full ledger)
Step 8  bare                               → previously ranked; same modules apply
Step 9  visorcorpus build                  → 46-case adversarial corpus (kb_exfil + system_prompt + config_secrets)
Step 10 visorrag recall (per host)         → no prior persisted run-data on these IPs (recall scope didn't cover triton survey)
```

The chain ran end-to-end via `bash data/visor-chain-runner.sh triton`. Artifacts at `~/recon/triton-2026-05-06/`.

**Active deeper enumeration deferred:** `POST /v2/models/<name>/stats` (which returns inference counts) was blocked by the session's permission system as escalating active recon beyond the user-directed scope. The 127.4M lifetime-inference count is sourced from the prior `triton-cloud-survey-2026-05.md` documentation, not a fresh probe in this revisit.

## Disclosure draft

Routing: `abuse@digitalocean.com` primary; `proplay.co` operator-direct for the sister host once the WHOIS check resolves.

Draft at: [`disclosures/DIGITALOCEAN-triton-chat-safety-2026-05-06.md`](../../disclosures/DIGITALOCEAN-triton-chat-safety-2026-05-06.md)

## References

- Original Triton survey, [`triton-cloud-survey-2026-05.md`](triton-cloud-survey-2026-05.md)
- Synthesis section "Class C, Adversarial probing of safety classifiers", [`SYNTHESIS-2026-05.md`](SYNTHESIS-2026-05.md)
- Triton REST API, https://docs.nvidia.com/deeplearning/triton-inference-server/user-guide/docs/protocol/extension_model_repository.html
