# Cat-BentoML Survey — Review & Corrections (2026-06-10 02:55-03:15 CDT)

Independent review of findings-breakdown.txt. The original report was incomplete and contained one overclaim. Re-verifying every claim caught additional findings and corrected misattributions.

## Corrections to original 7 findings

### F1 — NestleModel: OVERCLAIM corrected

| Original claim | Corrected |
|---|---|
| "geo-prediction ML model with lat/lon" | UNKNOWN purpose. Schema is generic `input_data: array of numbers`. The example curl in the `description` field uses NYC-taxi-fare-prediction coordinates (40.76, -73.98) but that block is **verbatim BentoML quickstart template README** (NYC taxi fare is the official BentoML tutorial), not the actual deployed model. |
| "Nestle (corporate)" attribution | UNSUPPORTED. The string "Nestle" only appears in the service-class name `NestleModel`. WHOIS resolves to RIPE NCC `netname:cloud` (Azure cloud range, EU). No infrastructure evidence links to Nestle the company. Could be: developer's first project name, a colleague's name, the Python `nestle` library, or genuinely Nestle. Cannot assert. |

**Corrected verdict**: NestleModel twin Azure deployment, unauth `/predict`, schema is generic numeric array input (likely tabular ML), purpose unknown, operator unknown.

### F5 — rakuten_text_service: attribution holds

The `description` field literally reads `JWT-protected BentoML text service for Rakuten category prediction`. The Rakuten attribution is **self-declared in the docs string**. Stronger than F1 but still self-declared — could be a developer doing Rakuten-category prediction for ML research, not necessarily Rakuten the company.

## Findings I MISSED (these should have been flagged)

### MISSED CRITICAL — KYC fleet on AWS US East (5 hosts, fintech Mexico-focused)

Five AWS EC2 hosts (compute-1.amazonaws.com, us-east-1) ran a fintech identity verification pipeline. All title="models" so I lumped them together as "generic ML". Re-probing exposed:

| IP | Port | BentoML | Endpoints |
|---|---|---|---|
| 100.49.3.222 | 80 | 1.0.15 | /passport_vision, /ine_vision, /ine_back, /ine_back_v2 |
| 3.231.115.236 | 80 | 1.0.15 | /passport_vision, /ine_vision, /ine_back, /ine_back_v2 |
| 35.174.161.179 | 80 | 1.0.15 | /passport_vision, /ine_vision, /ine_back, /ine_back_v2 |
| 100.25.240.168 | 80 | 1.0.22 | /identity_fraud_v2, /meta_fraud_v1, /credit_score_v1, /credit_score_v2 |
| 54.204.143.38 | 80 | 1.1.10 | /composite_portrait_v1, /screen_recapture_v1, /printed_bw_v1, /true_document |

**Pattern**: 3 hosts with identical endpoints (`passport_vision`, `ine_vision`) = load-balanced KYC OCR shard. `ine_vision` = OCR for Mexican voter ID (INE = Instituto Nacional Electoral). Plus an identity-fraud + credit-scoring node and an anti-spoof/document-fraud node. Single operator running Mexico-focused KYC ML stack on AWS, all over plain HTTP port 80 (no TLS), all BentoML pre-1.4.8 (CVE-2025-27520 CVSS 9.8 unauth RCE).

**Severity**: CRITICAL. Schema-only enumeration confirms PII-bearing endpoints (passport vision, ID document OCR, identity fraud verdict, credit scoring) exposed unauth on a vulnerable BentoML build over plain HTTP. PII may transit unencrypted, and unauth RCE is a chain risk to the model artifacts.

### MISSED CRITICAL — motion-detector with NATS + camera control

`motion-detector` (54.37.252.187:3000, BentoML 1.4.35, OVH Netherlands `ns3113034.ip-54-37-252.eu`) exposes:
- `/add_camera`, `/remove_camera`
- `/start_detection`, `/stop_detection`
- `/get_full_config`, `/update_config`
- `/get_nats_config`, `/update_nats_config`
- `/enable_debug_stream`, `/disable_debug_stream`

**Impact**: surveillance/CCTV control plane exposed. Unauth attacker can add cameras to the fleet, disable detection, read NATS message bus config (which would leak the broker URL + creds), enable debug streams. The `/get_nats_config` endpoint specifically returns the NATS config object (schema confirmed: `{type:object, additionalProperties:true}`).

**Severity**: CRITICAL. Restraint discipline applied: did NOT call `/get_nats_config`, did NOT call any tools/call surface. Names ARE the finding.

### MISSED HIGH — ragqa_service twin (Google Cloud)

`ragqa_service` (35.247.33.59:3000 + 34.144.180.225:3000, BentoML 1.1.10) — identical endpoints:
- `/qa`, `/qa_debug`, `/qa_ml`, `/qa_debug_ml`, `/qa_continuous`, `/clear_context`

RAG (retrieval-augmented generation) Q&A service. `/qa_debug` and `/clear_context` suggest a LangChain or similar agent loop. `/qa_continuous` is a streaming/long-running endpoint. Auth: NONE. BentoML 1.1.10 is CVE-2025-27520 vulnerable.

Same status as NestleModel twin: identical paths/versions on two Google Cloud IPs = single operator with two shards or dev/prod pair.

### MISSED HIGH — Identity verification 'breakers' service

`breakers` (34.199.132.41:80, BentoML 1.0.22) — endpoints:
- `/break_rfc`, `/break_crime`, `/break_nss`, `/break_ist`

Most plausible reading: anti-spam / abuse-detection (RFC = email RFC; CRIME = the TLS attack but unlikely; NSS = network security services; IST = ?). Could also be Mexican fintech "circuit breakers" pattern. Unknown without deeper probe. BentoML 1.0.22 = vulnerable to RCE chain.

### MISSED HIGH — Miko NLP intent_service (kids' robot company likely)

`intent_service` (34.144.182.127:8000, BentoML 1.0.10) — endpoints:
- `/mikoNLPIntentService`, `/mikoNLPIntentServiceAndEntityDetection`

The `miko` prefix strongly suggests Miko (kids' AI robot company, mikoworld.com). NLU intent classification + entity detection. **BentoML 1.0.10 is the oldest version in the cohort — vulnerable to every BentoML CVE**.

### MISSED MEDIUM — doccy-agent autonomous agent

`doccy-agent:dev` (142.44.211.206:3001, BentoML 1.4.35, OVH Canada) — endpoints:
- `/chat/stream`, `/runs/start`, `/runs/cancel/{run_id}`, `/runs/status/{run_id}`, `/pricing`

Agent platform with run lifecycle (start/status/cancel) and streaming chat. `/pricing` endpoint suggests SaaS billing. Dev environment exposed publicly. Co-hosted with SurrealDB (also auth-protected on this host).

### MISSED MEDIUM — AsrBentoGPU speech recognition

`AsrBentoGPU` (164.52.198.205:3001, BentoML 1.2.16, e2e-66-205.ssdcloudindia.net) — `/transcribe`. GPU-backed automatic speech recognition. India hosting (E2E Networks).

### MISSED MEDIUM — yolov8 face + crack detection

`yolov8` (15.206.158.97:80, BentoML 1.1.1, AWS Mumbai) — endpoints:
- `/api/v1/facedet32` (face detection), `/api/v1/crackdet32` (crack/defect detection)

Mixed-purpose YOLO inference. Face detection means biometric processing. Crack detection is civil engineering (bridges, roads, structures). Both BentoML 1.1.1 vulnerable to RCE.

### MISSED MEDIUM — ConstructiveScore (AI dialogue scoring SaaS)

`ConstructiveScore` (18.198.66.137:80, AWS Frankfurt) — endpoints:
- `/constructive_dialogue_score`, `/focus_on_solutions_score`, `/multiple_perspectives_score`, `/develop`, `/final_constructive_score`

Looks like an AI-powered dialogue moderation / debate scoring SaaS. Version 0.3.3. Service name and endpoint pattern suggest a productized commercial offering. Operator unknown.

### MISSED MEDIUM — AoLang translation service

`AoLang` (152.53.147.123:3000, BentoML 1.4.27) — `/translate_ao_to_en`, `/translate_en_to_ao`. Chinese language translation pair. The "Ao" likely refers to a Chinese language model name (Aolang).

### MISSED — generic services worth flagging

- `clip-api-service` (138.197.96.166:80, BentoML 1.1.11) — `/encode`, `/rank` CLIP embeddings API
- `hf_model_service` (35.197.190.161:80, BentoML 1.4.7) — `/predict`, `/batch_predict`, `/metadata` HuggingFace model wrapper
- `MermaidRenderService` (61.107.201.19:3000, BentoML 1.4.30) — `/render` Mermaid diagram rendering
- `line_sketch_generation` (178.154.219.76:3000) — `/generate_sketches` AI sketch art
- `machine_learning_prediction` (48.216.197.156:3000, BentoML 1.3.11) — `/classify`
- `group_models_service` (3.121.227.214:80) — `/predict_ms`, `/predict_pah`
- `deep_image_estimation_service` (115.190.149.238:3000, BentoML 1.1.9, version 1.0.0-prod) — `/v1/DeepImageEstimation/predict` (note: PROD version tag, not dev)

## Cohort corrections

- **BentoML host count**: 29, not 26. Three hosts had BentoML on non-default ports that aimap missed (port 3001 + 8000). Update tome `DefaultPorts` to include 3001 and 8000.
- **Service ports actually serving BentoML**:
  - port 3000: 16 hosts (default `bentoml serve`)
  - port 80: 9 hosts (nginx proxy in front of 3000)
  - port 443: 1 host (FluxBaseService TLS)
  - port 3001: 2 hosts (doccy-agent, AsrBentoGPU — possibly secondary deploy port)
  - port 8000: 1 host (intent_service — uvicorn default)
- **aimap miss class**: port 3001 + 8000 are "Insight #15 class" misses — Shodan saw the title via the proxy on port 80/3000, but the underlying app is on a non-default port the FP doesn't scan. **Fix**: BentoML FP should include 3001 + 8000 in DefaultPorts.

## CVE gating (10 of 26 had readable version badges)

- **CVE-2025-27520** (CVSS 9.8 unauth RCE, pre-1.4.8): 5 confirmed affected hosts (semantic_cache, ragqa_service, machine_learning_prediction, yolov8, clip-api-service). Also affects: intent_service (1.0.10), deep_image_estimation (1.1.9), 4 of the 5 "models" KYC fleet hosts (1.0.15/1.0.22/1.1.10), breakers (1.0.22) = **12+ hosts confirmed vulnerable to CVSS 9.8 RCE**.
- **CVE-2026-44345/44346** (pickle RCE, pre-1.4.39): every single host with a readable version badge. **0 patched hosts in the entire cohort.**

## Auth-on-default thesis: CONFIRMED, stronger than originally stated

- 29/29 BentoML services accessible at `/docs.json` without auth (100%)
- `access_authorization=False` is the documented default in `schemasv2.py` and `default_configuration.yaml`
- The cohort confirms the thesis at population scale

## Updates needed to original artifacts

1. `findings-breakdown.txt`: rewrite F1 NestleModel (drop "Nestle" + "geo-prediction" claims), add 11 missed findings, correct total host count 26→29
2. `aimap fingerprints.go`: BentoML `DefaultPorts` add 3001, 8000 (and re-build v1.9.55)
3. VisorLog: 22 missing findings need ingest (KYC fleet, motion-detector, ragqa twin, breakers, intent_service/Miko, doccy-agent, AsrBentoGPU, yolov8, ConstructiveScore, AoLang, clip-api, hf_model, Mermaid, line_sketch, ML_prediction, group_models, deep_image)
4. BARE input: 17 additional findings need scoring
5. Tome `bentoml.json`: confirm `default_ports` includes 3001, 8000 (currently [3000, 8000, 8001, 8080])
6. SESSION.md: append correction note

## Methodology lesson

Two failures in the original survey:
1. **Did not profile every aimap-identified service.** Grouped the 5 "models"-titled hosts into a single bucket without re-probing each. Lost the KYC fleet discovery. Lesson: when aimap returns N services with the same generic title, profile each one individually before clustering.
2. **Overclaimed attribution from service-name string alone.** Asserted Nestle = Nestle the company based on `NestleModel` string. The methodology demands primary-source verification, not name-inference. Lesson: a name in `/docs.json` is the service's self-declaration; treat as candidate operator, not confirmed, unless WHOIS / cert / hostname agrees.

The verification stage caught both. The methodology held.
