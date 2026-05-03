# NVIDIA Triton Inference Server on Public Cloud — Auth Posture Survey

_NuClide Research · 2026-05-03_

---

## Summary

Reused the 22,765 port-8000 hits from the prior ChromaDB sweep and fingerprinted them for NVIDIA Triton Inference Server (`GET /v2` body match `"name":"triton"`). **2 confirmed Triton instances**, both **unauthenticated**, both on DigitalOcean. Each exposes a complete production AI inference pipeline — model inventory, schemas, Prometheus metrics, and the inference endpoints themselves — to anyone on the internet.

Triton is uncommon on cloud VPSes (operators typically run it inside Kubernetes clusters behind cloud load balancers), so the small absolute count is expected. What is striking is what the two instances actually do: one is a high-volume chat-platform safety pipeline (including a child-safety minor-detection classifier with **127.4 million** inferences logged), the other is a workplace-surveillance image pipeline (face detection + emotion + cellphone + clean-desk monitoring).

Triton ships with no authentication on its REST or gRPC endpoints. RBAC requires explicitly enabling extensions and providing tokens at startup; neither operator has done so. The Prometheus `/metrics` endpoint on port 8002 is also unauth and discloses inference counts per model — a passive way for a competitor to track the operator's platform scale and engagement.

---

## Methodology

```
masscan -iL <28 cloud /16 CIDRs> -p 8000 (from earlier ChromaDB sweep)
  → 22,765 port-8000 hits

triton-probe.py (200-thread fingerprint)
  GET /v2 → match '"name":"triton"' in JSON body
  → 2 confirmed Triton instances

curl /v2/repository/index → POST {} for full model list
curl /v2/models/<name>     → schema (input/output dtypes, shapes, platform)
curl :8002/metrics         → Prometheus inference counters
```

---

## Findings Summary

| Metric | Value |
|---|---|
| Cloud /16 ranges scanned | 28 (DO/Hetzner/Vultr) |
| Masscan hits on :8000 | 22,765 |
| Triton REST confirmed | **2** |
| Unauthenticated | **2 (100%)** |
| Repository-index queryable | **2** |
| Prometheus metrics queryable on :8002 | **2** |

### Hosting

| Provider | Confirmed |
|---|---|
| DigitalOcean (NJ + AMS) | 2 |
| Hetzner | 0 |
| Vultr | 0 |

---

## Finding 1 — Chat-Platform Safety Pipeline with 127M-inference Minor-Detection Classifier (CRITICAL)

**Host:** `159.203.42.211:8000` (DigitalOcean US — Newark)
**Triton version:** 2.47.0
**Auth:** none on REST, gRPC (8001), or Prometheus (8002)

**Loaded models (all `READY`, all `onnxruntime_onnx` platform):**

| Model | Inferences (Prometheus counter) | Inferred role |
|---|---|---|
| `minors_v3_run10_onnx_model` | **127,422,587** | **Child-safety minor-detection classifier (BERT, binary)** |
| `s_minors_v3_run19_onnx_model` | 117,622,617 | Stricter / variant minor classifier |
| `sexting-bert-base-cased-221027-151601_onnx_model` | 89,125,657 | Sexting detection (BERT-cased, fine-tuned 2022-10-27) |
| `photo_request_detector_v2_onnx_model` | 18,924,442 | "Is the user requesting a photo" classifier |
| `contrastive_regenerations_v8_onnx_model` | 4,052 | Message regeneration scorer |
| `smart-reply-roberta-large-230409-210324_onnx_model` | 811 | Auto-reply scorer (RoBERTa-large, fine-tuned 2023-04-09) |

Each model has a `_tokenize` and `_inference` sibling forming a complete preprocessing → model → postprocessing chain.

**Schemas (all text classifiers):**

```
inputs:  input_ids (INT32)  + token_type_ids (INT32) + attention_mask (INT32)  — BERT-style
outputs: output (FP32, [-1, 2])   — binary classifier (or [-1, 1] for regressors)
platform: onnxruntime_onnx
```

### What this is

A complete **chat platform safety + auto-reply pipeline**. The model name patterns (`sexting-*`, `photo_request_detector`, `minors_*`, `smart-reply-roberta-large`) are characteristic of a messaging product where users send each other text messages and the platform applies automated content moderation + AI-generated reply suggestions in real time.

The volume is very high: 127.4 million minor-detection inferences logged on the platform's lifetime indicates a substantial active user base. The training-date suffixes in model names (`221027-151601`, `230409-210324`) are millisecond-resolution timestamps embedded by the operator's MLOps pipeline — a DevOps tell that this team trains models often.

### Why it matters

The unauth state on this instance has multiple distinct severities:

1. **Adversarial probing of the minor-detection classifier.** Anyone on the internet can submit tokenized text via `/v2/models/minors_v3_run10_onnx_model/infer` and observe the model's score. This enables an adversary to **map the classifier's decision boundary** and craft messages that evade detection. Child-safety classifiers are the highest-stakes class of safety system; their evasion patterns are valuable to bad actors and protectable by the operator.
2. **Free LLM-style inference.** The `smart-reply-roberta-large` and `contrastive_regenerations_v8` models are AI-content-generation models running on the operator's GPU. An attacker can submit arbitrary text and use the operator's compute for free.
3. **Model-architecture and version disclosure.** The BERT-cased variant + RoBERTa-large + training timestamps disclose the operator's exact safety-system architecture. A competitor reading this can replicate the design.
4. **Operational telemetry leak.** Prometheus on `:8002` returns per-model inference counters without auth — a passive way to monitor the operator's scale, A/B test rollouts, and traffic patterns.
5. **Model exfiltration potential.** Triton's repository-control extension is enabled (`extensions: model_repository, model_repository(unload_dependents)` per the `/v2` server info). If `--model-control-mode=explicit` is set (we did not test write operations), an attacker can `unload` and `load` models, including potentially loading attacker-controlled malicious model files.

### Platform-class identification (most likely product category)

The model lineup is distinctive enough to category-identify the product class with high confidence, even though the specific operator is not externally visible.

**The fingerprint:**

| Feature | Implication for product class |
|---|---|
| `sexting-bert` as a *named* category (not "explicit" / "NSFW") | Sexting is tracked as a distinct *feature* of the platform, not a behavior to suppress |
| `photo_request_detector` (binary classifier on whether the user is *asking* for a photo) | Person-to-person messaging where photo exchange is a core flow |
| Two minor-detection classifiers (`v3_run10` + `s_v3_run19`) running side-by-side at ~100M+ each | Mature safety engineering with active iteration — at least 19 retraining cycles, champion-vs-challenger A/B eval |
| `smart-reply-roberta-large` (scorer) + `contrastive_regenerations_v8` (scorer) | AI-suggested replies and AI-rewritten messages, scored by these models |
| Inference ratios: safety stack ~127M, AI-suggestion stack ~811-4K | Safety system is OLD AND HEAVY (mature production); AI-suggestion features are NEW AND LIGHT (recently rolled out) |

**The three product classes consistent with this fingerprint:**

1. **(most likely) AI-assisted creator-to-fan chat platform.** A service that helps OnlyFans-style creators reply to fans at scale by suggesting AI-generated responses. The category exploded 2023-2024. Vendors include Supercreator.ai, FanFix, OnlyMonster, FanPilot, Replia, etc. The math fits: a creator-chat service must screen for minors (legal requirement), allow sexting (the entire product use case), detect photo requests (creator-fan messaging is heavily photo-mediated), and apply AI to scale creator response volume across many simultaneous fan conversations.
2. **Standalone sexting / dating-with-NSFW chat app** that's adding AI features. Volume scale (100M+ safety inferences) puts the operator at "real production with substantial user base," not a side project.
3. **Anonymous-chat or social-discovery app** in the Whisper / Yubo / MeetMe class adding AI features. Possible but the photo-request-detector + smart-reply-on-sexting combination skews more toward purpose-built sexting product than incidental.

The DigitalOcean infrastructure (vs AWS-class cloud), English-language stack, and timing of model timestamps (2022-2023) are all consistent with category 1 — the OnlyFans-creator-tooling startup ecosystem that emerged in that window and runs heavily on cheap cloud VPSes.

### Operator attribution

Bare DigitalOcean VPS — no HTTP/443 service, no reverse DNS, no co-located public brand on this IP. Certspotter / crt.sh do not allow IP-only CT lookups (results require an eTLD). Direct Google / DuckDuckGo searches on the distinctive model names (`sexting-bert-base-cased-221027-151601`, `s_minors_v3_run19`, `photo_request_detector_v2`, `contrastive_regenerations_v8`) returned zero hits — these are operator-proprietary models, not published to Hugging Face or in academic papers.

Operator identification options NuClide deliberately did not pursue:

- **Adjacent-IP CT scan of the DigitalOcean /24 around 159.203.42.211** to find a co-located brand domain. This is straightforward but warrants explicit scope; see disclosure note.
- **Probing the classifier with sample text** to learn what platform-specific phrasings it's tuned for. This crosses the line of using the operator's compute.
- **Downloading the model files via Triton's repository-fetch endpoints** to inspect tokenizer configs / model cards. This would be operator-IP exfiltration.

The cleanest path to operator identity is the **DigitalOcean abuse channel**: when the abuse complaint is filed, DO knows which customer owns this IP and can act under their AUP without ever revealing the customer to NuClide. The second-cleanest is vendor pattern-matching by someone familiar with the OF-creator-tooling ecosystem who would recognize this exact architectural style.

---

## Finding 2 — Workplace-Surveillance Image Pipeline (HIGH)

**Host:** `178.62.225.198:8000` (DigitalOcean Amsterdam)
**Triton version:** 2.62.0
**Auth:** none on REST, gRPC (8001), or Prometheus (8002)

**Loaded models (all `READY`, all `tensorrt_plan` except orchestrator):**

| Model | Inferences | Platform | Inferred role |
|---|---|---|---|
| `face_detection_trt` | 7,304 | TensorRT | YOLOv8-style face detector (input 640×640×3, output 20-class grid) |
| `cellphone_trt` | 7,304 | TensorRT | Cellphone-in-hand detector (5-class) |
| `clean_desk_trt` | 7,304 | TensorRT | Desk cleanliness / objects detector (7-class) |
| `emotion_trt` | 786 | TensorRT | FER (Facial Emotion Recognition) — 48×48 grayscale, 5-class |
| `orchestrator` | 7,328 | Python BLS | Multi-model dispatcher with per-call flags |

**Orchestrator schema (the customer-facing API):**

```
inputs:
  IMAGE_BYTES        : BYTES   — raw image
  DO_CELLPHONE       : BOOL    — run cellphone detection
  DO_FACE            : BOOL    — run face detection
  DO_CLEANDESK       : BOOL    — run clean-desk detection
  DO_EMOTION         : BOOL    — run emotion classification
  DO_VERIFY          : BOOL    — run face verification (?)
  DO_HEADPOSE        : BOOL    — run head-pose estimation
  CELLPHONE_CONF     : FP32    — confidence threshold
  CELLPHONE_IOU      : FP32    — IoU threshold for NMS
  FACE_CONF, FACE_IOU, CLEANDESK_CONF, CLEANDESK_IOU, HEADPOSE_CONF, HEADPOSE_IOU
  RETURN_BOXES       : BOOL    — return bounding boxes
  DEBUG_MODE         : BOOL    — debug output
outputs:
  RESULTS_JSON       : BYTES
```

### What this is

A **workplace-surveillance / call-center monitoring AI pipeline**. The combination of cellphone-in-hand detection, clean-desk-policy detection, emotion classification, face detection + verification, and head-pose estimation is characteristic of:

- Remote-worker monitoring (is the worker at their desk? on their phone? showing positive emotion?)
- Call-center QA (face presence + emotion + cleanliness during calls)
- Retail-store security (employee compliance with phone/desk policy)

The orchestrator's `DEBUG_MODE` and `RETURN_BOXES` flags are developer-API features, suggesting this is a B2B service where the operator's customers integrate directly. The lower inference volume (~7K each) suggests pilot deployment or single-customer scale.

### Why it matters

1. **Privacy-grade surveillance system exposed unauth.** Anyone on the internet can submit images and run face detection, emotion classification, and headpose estimation through the operator's pipeline. Free inference on someone else's GPU.
2. **Customer-facing API surface revealed.** The orchestrator schema is the operator's actual product interface. A competitor can clone the API design and offer a competing service.
3. **Operator identity inferable from API design.** "DO_VERIFY" + "HEADPOSE" + "CLEAN_DESK" combo is distinctive enough to potentially identify the vendor in this niche space.

### Operator attribution

Bare DigitalOcean Amsterdam VPS — no HTTP/443, no reverse DNS, no brand. Like Finding 1, operator attribution requires side-channel investigation.

---

## Root Cause: Triton Default Auth-Off

NVIDIA Triton Inference Server ships with no authentication. The relevant flags are:

```bash
tritonserver --http-restricted-api=<api-name> \
             --http-restricted-protocol=<protocol>:headername=token \
             --grpc-restricted-api=<api-name> \
             --grpc-restricted-protocol=<protocol>:headername=token
```

Without these, all REST endpoints (model inventory, model config, inference, repository control, statistics, system shared memory, CUDA shared memory) are open to any client. Neither of the two confirmed instances had any `--http-restricted-*` configuration.

This matches the pattern across the entire NuClide vector-DB / inference-stack survey: the data plane and inference plane of the modern AI stack ship without authentication, and operators rarely enable it before exposing the service to the public internet.

---

## Cross-Survey Pattern: AI Infrastructure Auth Posture (updated)

| Platform | Sample | Unauthenticated | Default | Survey |
|---|---|---|---|---|
| Qdrant | 61 | 100% | auth-off | [qdrant-cloud-survey-2026-05.md](qdrant-cloud-survey-2026-05.md) |
| ChromaDB | 48 | 100% | auth-off | [chromadb-cloud-survey-2026-05.md](chromadb-cloud-survey-2026-05.md) |
| Milvus | 33 | 100% | RBAC-off | [milvus-cloud-survey-2026-05.md](milvus-cloud-survey-2026-05.md) |
| **Triton Inference Server** | **2** | **100%** | **auth-off** | **this file** |
| Elasticsearch | 42 | mixed | auth-off in 7.x | [elasticsearch-cloud-survey-2026-05.md](elasticsearch-cloud-survey-2026-05.md) |
| Flowise | 43 | 0% | auth-on (since CVE-2024-36420) | [flowise-cloud-survey-2026-05.md](flowise-cloud-survey-2026-05.md) |
| n8n | 1,006 | 0% | auth-on (since v0.166.0) | [n8n-cloud-survey-2026-05.md](n8n-cloud-survey-2026-05.md) |
| Jupyter | 18 (univ) | 0% | PAM/LDAP standard | [jupyter-survey-2026-05.md](jupyter-survey-2026-05.md) |

Vector DBs (Qdrant/Chroma/Milvus) and inference servers (Triton) all ship without authentication. The orchestration / workflow / notebook tier (Flowise/n8n/Jupyter) has moved to auth-on by default. The pattern is clear and persistent.

---

## Disclosure Posture

Both findings are unauthenticated production AI infrastructure with significant content sensitivity. The chat-platform safety pipeline (Finding 1) is particularly serious because:

- A child-safety classifier exposed for adversarial probing has direct child-protection implications
- The operator presumably has commercial obligations to their users that include classifier integrity

For both findings:
1. Operator identification via DigitalOcean abuse channel is the primary contact route (no brand domain available).
2. DigitalOcean has standing under their AUP to notify the customer.
3. The Triton auth misconfiguration is trivial to fix — operators just need to bind to localhost or enable API restrictions.

Coordinated disclosure to DigitalOcean abuse for both IPs is recommended.

---

## Remediation

```bash
# Option A: bind Triton to localhost only (recommended for backend-only deployments)
tritonserver --http-address=127.0.0.1 --grpc-address=127.0.0.1 ...

# Option B: enable API restrictions (token required per protocol)
tritonserver --http-restricted-api=model-repository,inference \
             --http-restricted-protocol=model-repository:authorization=<secret> \
             --http-restricted-protocol=inference:authorization=<secret> \
             ...

# Option C: firewall ports 8000/8001/8002 to the application backend's CIDR
ufw deny 8000 && ufw deny 8001 && ufw deny 8002
```

---

## NuClide Pipeline Artifacts

| Stage | Notes |
|---|---|
| Discovery | Reused 22,765 IPs from chromadb-cloud-survey-2026-05 port-8000 masscan |
| Fingerprint | `triton-probe.py` — 200-thread `/v2` body-match for `"name":"triton"` |
| Schema enumeration | `/v2/repository/index` POST {}, `/v2/models/<name>` GET — confirmed 11 distinct loaded models across 2 hosts |
| Telemetry leak | `:8002/metrics` Prometheus counters captured — per-model inference totals |
| Findings ledger | To be ingested into `data/nuclide.db` via VisorLog |

---

## References

- Triton Inference Server REST API: https://docs.nvidia.com/deeplearning/triton-inference-server/user-guide/docs/customization_guide/inference_protocols.html
- Triton authentication / restricted APIs: https://github.com/triton-inference-server/server/blob/main/docs/customization_guide/inference_protocols.md
- Cross-survey index: [index.md](index.md)
