---
to: abuse@digitalocean.com
cc: abuse@nuclide-research.com
severity: CRITICAL
ip: 159.203.42.211, 178.62.225.198
institution: DigitalOcean (159.203.42.211 chat-safety pipeline + 178.62.225.198 proplay.co workplace surveillance), 30+ days unremediated
status: DRAFT
outcome: sent
date: 2026-05-06
---

**To:** abuse@digitalocean.com
**Cc:** abuse@nuclide-research.com
**Subject:** Persistent unauth NVIDIA Triton Inference Servers (CSAM-adjacent chat-safety classifier + workplace-surveillance pipeline), 30+ days unremediated, 159.203.42.211 + 178.62.225.198

---

Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com

2026-05-06

**Re:** Two persistent unauthenticated NVIDIA Triton Inference Servers on DigitalOcean customer hosts
**IPs:** 159.203.42.211 + 178.62.225.198 (proplay.co)
**Severity:** CRITICAL
**Original disclosure window:** 2026-04-04 (NuClide Triton survey); re-verified live 2026-05-06 (>30 days unremediated)

---

I'm an independent security researcher conducting good-faith AI infrastructure research under the NuClide Research umbrella (CISA disclosures CVE-2025-4364, ICSA-25-140-11). This is a re-disclosure / escalation following the persistence of the exposure beyond the standard 30-day remediation window.

---

## Summary

Two DigitalOcean customer hosts have been running NVIDIA Triton Inference Server `2.47.0` unauthenticated on port 8000 since at least 2026-04-04, first documented in NuClide's [Triton cloud survey](https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT/blob/main/case-studies/commercial/triton-cloud-survey-2026-05.md). Re-verification today (2026-05-06) confirms the chat-safety host is still serving the same model ensembles unauthenticated. The companion host has been silent on Mullvad-routed re-probe and may be filtering or remediated; provider verification requested.

### Host 1: 159.203.42.211 (chat-safety pipeline)

`POST http://159.203.42.211:8000/v2/repository/index` returns six ONNX ensembles, all in `READY` state:

```
contrastive_regenerations_v8        (chat regeneration / paraphrase) - 4,412 inferences
minors_v3_run10                      (MINOR-DETECTION classifier) - 134,015,210 lifetime inferences  ← +6.6M since 2026-04-04
s_minors_v3_run19                    (second MINOR-DETECTION classifier) - 123,583,585 lifetime inferences
photo_request_detector_v2            (photo-solicitation detector) - 19,884,366 lifetime inferences
sexting-bert-base-cased-221027-151601  (sexting classifier) - 93,405,870 lifetime inferences
smart-reply-roberta-large-230409-210324 (smart-reply ranker) - 883 inferences
```

**Total: ~370 million lifetime inferences across the safety-classifier suite.**

**Last inference timestamp on `minors_v3_run10`: 2026-05-06 22:13 UTC**, the classifier is actively serving production traffic *as of the disclosure timestamp*. The +6.6M-inference delta on the minor classifier between the 2026-04-04 baseline (127.4M) and today (134.0M) confirms the platform is processing ~206K probes/day sustained against this single safety classifier.

The two minor-detection classifiers + photo-solicitation detector + sexting classifier are the safety-classifier ensemble for an adult-chat / dating / DM platform. Each model is reachable as a black-box oracle via `POST /v2/models/<name>/infer` without authentication. The CSAM-risk angle:

- An attacker submits crafted inputs to `minors_v3_run10` and observes pass/fail
- After enough probes, an evasion pattern emerges (these classifiers are reliably bypassable when probable as a black-box oracle)
- The evasion is reused on the operator's downstream chat platform, where the same classifier presumably gates whether content reaches a human moderation queue
- A counterparty exhibiting "minor" patterns evades the safety net, direct CSAM-class consequence

This is the strongest-stakes finding in NuClide's 2026-05 survey series.

### Host 2: 178.62.225.198 (proplay.co: workplace-surveillance pipeline)

Reverse-DNS resolves to `proplay.co` via passive-DNS pivot. Original survey documented Triton with workplace-surveillance YOLOv8 face / cellphone / clean-desk / emotion classifiers.

Re-probe from Mullvad Miami exit returned no response on common ports (8000/8001/8002/80/443/22). This may be:
- Remediation (best case)
- Mullvad-IP filtering by an upstream WAF
- Migration to a new IP

DigitalOcean abuse should be able to confirm via direct customer query.

---

## Reproduction (host 1, non-destructive)

```bash
$ curl -s 'http://159.203.42.211:8000/v2'
{"name":"triton","version":"2.47.0","extensions":["classification","sequence","model_repository","model_repository(unload_dependents)","schedule_policy","model_configuration","system_shared_memory","cuda_shared_memory","binary_tensor_data","parameters","statistics","trace","logging"]}

$ curl -s -X POST 'http://159.203.42.211:8000/v2/repository/index' | jq -r '.[].name' | sort -u
contrastive_regenerations_v8_onnx_inference
minors_v3_run10_onnx_inference
photo_request_detector_v2_onnx_inference
s_minors_v3_run19_onnx_inference
sexting-bert-base-cased-221027-151601_onnx_inference
smart-reply-roberta-large-230409-210324_onnx_inference
[+ matching _model and _tokenize sub-ensembles]
```

Verification was non-destructive: `GET /v2`, `POST /v2/repository/index`. **No `infer` calls were made.** No data was extracted from the classifiers. The exposure is confirmed solely by the published model inventory.

---

## Why this matters

The chat-safety classifier ensemble is the operator's PRODUCTION CSAM-detection apparatus. It being externally probable as a black-box oracle is a child-safety risk that scales independently of the operator's downstream moderation processes. An attacker:

1. Probes the classifiers to find evasion strings (no auth required, no cost to attacker)
2. Reuses evasion strings against the live platform
3. Defeats the safety classifier in the wild

The 127.4M lifetime inference count documented in the prior survey establishes this is a production-scale workload, not a research deployment.

For a chat platform that handles adult content with minor-detection as a hard requirement, this is a CRITICAL operator-side defect, the classifier needs to be bound to localhost (the standard Triton deployment pattern) or fronted by a network-layer auth gate.

---

## Remediation (for the customers)

Bind Triton to localhost or restrict via firewall:

```bash
# Triton's HTTP port should bind to 127.0.0.1, not 0.0.0.0
tritonserver --http-address 127.0.0.1 ...

# Or firewall the public interface:
ufw deny 8000/tcp
ufw allow from <admin-IP> to any port 8000
```

If Triton must be externally reachable for a multi-host inference architecture, place it behind a reverse proxy with JWT or mTLS:

```
client → nginx (validates JWT) → triton on 127.0.0.1:8000
```

NVIDIA's deployment guide covers this auth pattern: https://docs.nvidia.com/deeplearning/triton-inference-server/user-guide/docs/customization_guide/deploy.html

---

## Reference

Full case study (with adversarial threat-class taxonomy and persistent-exposure timeline):
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT/blob/main/case-studies/commercial/multi-triton-chat-safety-2026-05-06.md

Original Triton survey (2026-04-04, with the 127.4M inference count and full ensemble inventory at first discovery):
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT/blob/main/case-studies/commercial/triton-cloud-survey-2026-05.md

Cross-survey synthesis (Class C, Adversarial probing of safety classifiers):
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT/blob/main/case-studies/commercial/SYNTHESIS-2026-05.md

Happy to coordinate verification with the customer, or to provide a tighter exploit demonstration under a non-destructive scope. Given the CSAM-adjacent nature, expedited remediation is requested.

Regards,
Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT
