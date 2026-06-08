# 733 — Risk, Ethics, Jurisdiction

**Target:** 113.240.68.47:8188 (ComfyUI 0.23.0, 8x NVIDIA A100-SXM4-80GB, 634 GB VRAM aggregate, 1.08 TB system RAM)
**Operator:** unknown (no rDNS, no TLS cert on 8188, no banner-disclosed identity)
**Netblock:** CHINANET HUNAN PROVINCE NETWORK (China Telecom, AS4134/AS4837 family), Changsha, Hunan
**Researcher:** NuClide Research / Nicholas Kloster, nicholas@nuclide-research.com
**Date:** 2026-06-08
**Lane:** DCWF 733 — AI Risk & Ethics Specialist
**Sibling artifact:** `672-tne-enumeration.md` (DCWF 672 T&E, metadata enumeration)

---

## 1. Jurisdiction

The host is physically and administratively in the People's Republic of China. Three statutes structure any data-processing or AI-compute activity on it.

### 1.1 PIPL — Personal Information Protection Law (effective 2021-11-01)

PIPL is China's omnibus personal-information statute, in form and intent the PRC analog to GDPR.

Relevance to this host:

- **PIPL applies to the processing of personal information of natural persons within the PRC**, including by an operator located in China. If the ComfyUI workflow loadout processes any personal information — face references (PuLID / InstantID / PhotoMaker / InsightFace), identity-bearing prompts, identity-bearing reference images, audio/voice samples, video frames containing identifiable subjects — that processing is squarely within PIPL.
- **PIPL imposes "PI handler" obligations**: lawful basis, transparency, purpose limitation, security measures, breach notification, DPO appointment above thresholds, and a privacy program with categorization and incident response.
- An **unauthenticated public ComfyUI endpoint with `/history`, `/view/<filename>`, `/queue`, and `/upload/image` exposed to the open internet is, on its face, a PIPL Article 9 / 51 security-measures failure** for any operator processing PI through it. The lack of access control means a "PI leak / unauthorized disclosure" condition is structurally pre-created.
- PIPL has **extraterritorial reach** (Art. 3) for processing outside the PRC aimed at PRC natural persons — not directly relevant here (the operator is in-country) but relevant to anyone connecting from abroad and feeding prompts in.

### 1.2 DSL — Data Security Law (effective 2021-09-01)

DSL is the data-tier counterpart to PIPL: it covers all data (not just personal data) and introduces classified-and-graded data protection.

Relevance:

- **Article 21**: data must be classified and graded per its importance to national security, public interest, and lawful rights; "important data" and "core data" carry heightened obligations.
- **Article 27**: data-processing activities must establish a full-lifecycle security management system, security training, and technical safeguards proportionate to the grade. An unauthenticated 8x A100 inference cluster fails the technical-safeguard test on its face.
- **Article 31** (cross-border) interacts with CSL: if the operator is later classified as a Critical Information Infrastructure operator (see CSL below), data localization and cross-border transfer security assessment kick in.
- **Article 35** — data requests by foreign authorities require PRC approval. Not relevant to NuClide (we are not requesting data); flagged for completeness.

### 1.3 CSL — Cybersecurity Law (effective 2017-06-01; major amendment effective 2026-01-01)

CSL is the foundational cyber statute and the regulatory home of Critical Information Infrastructure (CII).

Relevance:

- **Article 21** (Multi-Level Protection Scheme / MLPS 2.0): all network operators must implement classified protection. Running a public unauthenticated AI inference cluster is below the floor of MLPS Level 2, which is the minimum for systems handling production user data.
- **CII designation** (Articles 31, 37): industries including telecom, finance, energy, water, transport, public services, e-government, and "other infrastructure that, if damaged or leaked, may severely threaten national security." A commercial AI-as-a-service operator running on a China Telecom commercial line is unlikely to be formally designated CII, but it is plausibly serving CII customers. **Pending the data-class confirmation in §3**, we treat CII designation as undetermined.
- **2026-01-01 CSL amendment** introduces explicit AI compliance provisions: AI ethics standards, AI risk monitoring, and security assessments for AI products and services. The host's current posture (unauthenticated, no rate limit, model-set exposed, history queryable) fails the spirit of these provisions even before formal rules are finalized.
- **Generative AI Measures** (Cyberspace Administration of China, effective 2023-08-15) require security assessments for generative AI services provided to the public in the PRC. A public-internet-reachable ComfyUI fits the description of a generative AI service made available to the public; whether it is a "service" in the regulatory sense depends on whether the operator markets it. The exposure pattern is consistent with no security assessment having been done.

### 1.4 Unauthorized-access analog

PRC Criminal Law **Article 285** criminalizes unauthorized intrusion into computer information systems and the obtaining of data, with heightened penalties for systems in state affairs, national defense, or cutting-edge science and technology. Any third party submitting a `/prompt` to this open ComfyUI — including foreign researchers — would expose themselves to Article 285 liability under PRC law, in addition to US Computer Fraud and Abuse Act exposure. This is the load-bearing reason for the restraint discipline in §4.

---

## 2. Export-control context

The cluster is **8x NVIDIA A100-SXM4-80GB**. This is the original, unconstrained A100 — not the A800 China-spec part with NVLink throttled to 400 GB/s, and not the H20 China-only Hopper.

### 2.1 Timeline (US BIS, AI accelerator controls to PRC end-use)

| Date | Action |
|------|--------|
| **2022-10-07** | BIS rule: license required to export A100 and H100 to PRC end-users; 600 GB/s interconnect threshold becomes a control parameter |
| Late 2022 | NVIDIA introduces **A800** (A100 silicon, NVLink throttled to 400 GB/s) and **H800** (H100 silicon, ~300 GB/s) for the PRC market |
| **2023-10-17** | BIS removes the interconnect-bandwidth threshold; A800 and H800 swept into the controls; "performance density" and "total processing performance" become the gates |
| Late 2023 / 2024 | NVIDIA introduces **H20** as the post-October-2023 China-compliant Hopper; A800/H800 no longer exportable |
| 2025 | Trump-era reversal of broad chip ban; NVIDIA and AMD cleared to resume China sales of certain compliant SKUs; A100 itself remains restricted |

### 2.2 How does this operator have 8x A100-SXM4-80GB?

The A100-SXM4-80GB itself has never been exportable to PRC end-users since 2022-10-07. There are three coherent acquisition stories:

1. **Pre-ban purchase (legal at time of import).** A100 launched 2020; the 80GB SXM4 SKU shipped mid-2021. A Chinese operator could have legally imported a full HGX 8x A100 baseboard between 2021 and 2022-10-07. This is the cleanest story and the most common explanation for in-country A100 inventory today.

2. **Gray-market import (sanctions evasion).** Documented pattern: A100/H100 silicon routed through Hong Kong, Singapore, Malaysia, Vietnam intermediaries; sold to PRC operators at a premium. Multiple press reports in 2023–2024 confirm an active black market for the originally-banned A100/H100 parts in China. BIS has opened investigations.

3. **Cloud-resold / colocation from a pre-ban operator.** A Chinese cloud or AI-lab that imported A100 capacity pre-ban could be reselling slices. A commercial residential-class China Telecom IP fronting an HGX board is unusual for a Tier-1 cloud; this argues against this story, but it cannot be excluded without identifying the operator.

We **do not assert** which of (1)–(3) is the case. We document that all three are open, and that the export-control posture is a real and undetermined risk variable independent of the data-protection posture.

### 2.3 NuClide posture on the export-control angle

NuClide is a US-based independent research entity. The presence of restricted-class hardware in a foreign jurisdiction is a finding to **document, not investigate**. We do not contact BIS. We do not contact Department of Commerce. We do not contact the FBI. The export-control posture is included here for full risk characterization of the case study — disclosure routing in §5 stays inside the cyber-incident channels.

---

## 3. Data-class candidates (metadata only — no body reads)

Per the 672-T&E enumeration (model folders listed via `/models` endpoint, custom-node extensions visible via `/extensions`, system stats via `/system_stats`), the workflow loadout exposes the following capability classes. **No `/history` body, no `/view`, no `/prompt` queue contents were read.**

### 3.1 Image-generation content class

Standard ComfyUI model directories present: `checkpoints`, `loras`, `vae`, `text_encoders`, `diffusion_models`, `controlnet`, `gligen`, `style_models`, `embeddings`, `upscale_models`, `ipadapter`, `inpaint`.

Implications:
- General-purpose image generation. Content-risk class includes **deepfake generation, IP-violating generation (commercial-character infringement), and CSAM-risk surface** by default of the capability. Capability presence is not evidence of use. No prompt history was read.

### 3.2 Identity-content / face-identity class — CONFIRMED at capability layer

Identity-specific model folders present:

| Folder | Capability |
|---|---|
| `insightface` | Face detection / face embedding (ArcFace lineage) |
| `instantid` | Identity-preserving generation from a single reference face |
| `pulid` | Pure ID customization — identity-preserving image gen |
| `photomaker` | Identity-conditioned generation from face photos |
| `facexlib` | Face processing library (restoration, parsing, landmarks) |

Implications:
- **Identity-content risk is structural, not speculative.** The operator has explicitly installed the full face-ID stack. Capability for non-consensual identity-conditioned image generation (the technical substrate of "deepfake" and "face-swap" misuse) is present and provisioned. The risk class is confirmed at the capability layer regardless of any actual prompt evidence.

### 3.3 Audio / voice class

Folders present: `mmaudio`, `wav2vec2`, `audio_encoders`.

Implications:
- Audio synthesis / voice processing capability. Combined with the face-ID stack, this is the substrate for **audio-visual deepfake generation** (face + voice). Capability only; no prompt evidence.

### 3.4 Video / frame-interpolation class

Folders present: `frame_interpolation`, `optical_flow`, `dynamicrafter_models`, `VHS_video_formats`.

Implications:
- Video synthesis / animation capability. Standard image-to-video pipeline.

### 3.5 LLM-on-cluster class

Folders present: `llm`, `LLM`, `t5`, `prompt_generator`, `unet_gguf`, `clip_gguf`.

Implications:
- Cluster hosts not only diffusion models but also LLM weights (GGUF format suggests llama.cpp-class quantized LLMs alongside the diffusion stack). `prompt_generator` indicates LLM-driven prompt expansion for image gen. **The cluster is mixed-modality**, not pure image-gen.

### 3.6 Chinese-native model signal — INDETERMINATE from metadata alone

The custom-node list includes `comfy-kitchen` and `comfy-aimdo` (Chinese-author ComfyUI extensions are common on PRC-operated rigs but neither is uniquely diagnostic). The `checkpoints` folder name is enumerated but file contents are not read. Cannot confirm Hunyuan / ChatGLM / Qwen / DeepSeek / Baidu-native model presence from the metadata reads alone. **No assertion made.**

### 3.7 Commercial-IP-model class — INDETERMINATE

Cannot confirm presence of unlicensed MidJourney-style or RunwayML-style models without reading checkpoint filenames or hashes. **No assertion made.**

### 3.8 Data-class summary

| Class | Status | Basis |
|---|---|---|
| Image generation (general) | CONFIRMED at capability layer | Standard ComfyUI model folders + 634 GB VRAM provisioned |
| Identity-content / face-ID | CONFIRMED at capability layer | `insightface`, `pulid`, `instantid`, `photomaker`, `facexlib` folders all present |
| Audio / voice | CONFIRMED at capability layer | `mmaudio`, `wav2vec2`, `audio_encoders` folders |
| Video | CONFIRMED at capability layer | `frame_interpolation`, `dynamicrafter_models` folders |
| LLM (text gen) | CONFIRMED at capability layer | `llm`, `LLM`, `t5`, `unet_gguf`, `clip_gguf` folders |
| Chinese-native model loadout | INDETERMINATE | Folder names not diagnostic; would require checkpoint-file enumeration |
| Commercial-IP-model use | INDETERMINATE | Would require checkpoint-file enumeration |
| Actual prompt content / output content | NOT READ — restraint | `/history`, `/view/<filename>`, `/queue` bodies untouched |

---

## 4. Restraint statement — what we will NOT do, and why

This host is reachable and unauthenticated. We treat it as **inviolate**. The following are explicitly off the table for this case study, with the legal authority for each restraint named.

| Action | Status | Why |
|---|---|---|
| `POST /prompt` — submit a workflow | NEVER | Compute theft. US CFAA 18 U.S.C. §1030(a)(4) (fraud + value), PRC Criminal Law Article 285 (unauthorized intrusion). Even a no-op workflow consumes GPU-seconds the operator pays for. |
| `GET /history` body — read prompt history | NEVER | Operator content disclosure. PIPL Article 9, 51 (unlawful access to PI), PRC CL 285. The endpoint is reachable from `/history`'s JSON envelope at the metadata layer; bodies are out of scope. |
| `GET /view/<filename>` — read generated outputs | NEVER | Operator content disclosure, possible identity-image disclosure (face-ID loadout means any output may contain a third-party face). PIPL Article 28 (sensitive PI — biometric/facial), DSL Article 27, PRC CL 285. |
| `GET /queue` body — read live in-flight prompts | NEVER | Same logic as `/history`. The shape of the queue is metadata; queue contents are user data. |
| `POST /upload/image` — write to operator disk | NEVER | Active write. PRC CL 286 (intentional damage / unauthorized modification), US CFAA §1030(a)(5) (damage / modification without authorization). Even a benign image upload is a write to a third-party system. |
| SSH (port 22) probing beyond banner | NEVER | Authentication attempt against a foreign government-adjacent telco line. Banner fingerprint already collected (OpenSSH 8.9p1 Ubuntu 3ubuntu0.15). |
| CVE exploitation (any) against this host | NEVER | Out of scope for any NuClide engagement on a third-party PRC host with no authorization. |
| Re-probe at any cadence | NEVER (single read pass only) | Repeated probing approaches "monitoring" which is a different legal class than a one-time external observation. |
| Naming the operator publicly before disclosure | NEVER | Operator is not yet identified. If identified later (via cert pivot, JS bundle, image-tag pattern in `/object_info`), naming is deferred until after the CNCERT / abuse-channel notification window closes. |
| Contacting BIS / Commerce / FBI re: A100 sourcing | NEVER | Out of NuClide's lane. We are a cyber-incident researcher, not an export-control enforcement agency. The export-control posture is documented in §2 for the case-study record; routing is §5. |

### 4.1 What we DID do (for the record, to close the loop)

- One pass of unauthenticated metadata-only reads against documented ComfyUI endpoints: `/system_stats`, `/models`, `/extensions`, `/object_info` shape only (not full body inventories of every node-class), `/history` envelope (JSON shape — confirmed reachable, body not retained), `/queue` envelope.
- Banner grab on 22 (OpenSSH version string) and 8188 (HTTP title `ComfyUI`).
- Shodan host record (already public via Shodan crawl).
- WHOIS on the netblock.
- No authentication attempt. No write. No prompt submission. No CVE probe.

The bright line: **shape and capability are metadata. Bodies of prompts, queue items, and outputs are operator content and are not ours to read.**

---

## 5. Disclosure routing

The operator is unidentified at the time of this writeup. Routing therefore has to climb the chain.

| Tier | Channel | Identifier | Status |
|---|---|---|---|
| 1. Operator (direct) | none | no rDNS, no TLS cert on 8188, no JS-bundle-leaked branding yet | **NOT POSSIBLE** at this time |
| 2. Netblock abuse | `anti-spam@chinatelecom.cn` (general CHINANET abuse) | per WHOIS on 113.240.0.0/16 | viable, low-fidelity (spam-tuned mailbox) |
| 2b. Netblock abuse | `13348615181@189.cn` (CHINANET-HN registrant contact) | per WHOIS, Hunan-province POC | viable, more local |
| 3. National CERT | CNCERT/CC — China National Computer Network Emergency Response Technical Team / Coordination Center | `cncert@cert.org.cn` (international coordination address commonly listed in their FIRST profile) and the web intake at `www.cert.org.cn` | **RECOMMENDED PRIMARY** |
| 3b. National vulnerability DB | CNVD — China National Vulnerability Database (operated by CNCERT) | `cnvd.org.cn` web intake | for systemic / vendor-class findings (ComfyUI ecosystem), not for this single-host exposure |
| 4. Substrate provider | this IS the substrate — China Telecom is the ISP | covered by Tier 2 | n/a |
| 5. Upstream regulator | Cyberspace Administration of China (CAC) | no public-facing foreign-researcher intake | NOT recommended — political-risk surface, not a coordinated-disclosure channel |
| 6. US side (US-CERT / CISA) | CISA does not coordinate disclosures to PRC operators | n/a | not applicable |

### 5.1 Recommendation

**Primary channel: CNCERT/CC.** Rationale:
- It is China's FIRST-member national CERT and the stated intake for cybersecurity incident reports including from non-PRC reporters ("incident reports from users at home and abroad").
- It has the relationship with China Telecom to route an abuse notification with weight that `anti-spam@chinatelecom.cn` does not.
- It has the legal authority under CSL Article 51 to require remediation by the network operator.

**Secondary channel (parallel CC, not primary): `anti-spam@chinatelecom.cn`.** Sets a paper trail to the netblock owner; very likely to be silent; included so the netblock cannot later claim no notice.

**Do NOT route to:** CAC directly (political), BIS / Commerce (out of lane), media (operator unidentified — speculative reporting risk).

### 5.2 Operating posture on send

**This template is a DRAFT. Do not send today.** Per NuClide protocol, disclosure goes through Nick. The draft is staged so the case study has a complete artifact; the send decision is separate.

---

## 6. DRAFT CNCERT notification template — DO NOT SEND

```
To: cncert@cert.org.cn
Cc: anti-spam@chinatelecom.cn
From: Nicholas Kloster <nicholas@nuclide-research.com>
Subject: Coordinated disclosure — unauthenticated AI inference cluster on
         CHINANET-HN, 113.240.68.47, 8x NVIDIA A100 exposed

Dear CNCERT/CC,

I am an independent security researcher based in the United States
(NuClide Research, https://nuclide-research.com). I am writing to
report an exposed AI compute cluster on a CHINANET Hunan Province
Network address, in accordance with coordinated-disclosure practice.

ASSET
  IP:       113.240.68.47
  Location: Changsha, Hunan (per Shodan / WHOIS)
  Netblock: CHINANET HUNAN PROVINCE NETWORK
  Observed: 2026-06-08 UTC

EXPOSURE
  Port 8188/tcp: ComfyUI 0.23.0 — open to the public internet with no
                 authentication. Standard ComfyUI control endpoints
                 reachable.
  Port 22/tcp:   OpenSSH 8.9p1 Ubuntu 3ubuntu0.15. Not probed by us
                 beyond the banner.

HARDWARE
  The reachable /system_stats endpoint reports the host is provisioned
  with 8x NVIDIA A100-SXM4-80GB GPUs (~634 GB aggregate VRAM) and
  approximately 1 TB of system RAM. The cluster is currently in active
  use (some GPU memory in use).

WHY THIS MATTERS
  An unauthenticated ComfyUI control surface on this class of hardware
  permits:
    - Submission of arbitrary inference workloads by any internet host
      (uncontrolled use of the operator's compute and electricity).
    - Read access to the operator's prompt history and generated output
      files via the documented /history and /view endpoints.
    - Write access to the operator's filesystem via the documented
      /upload/image endpoint.
  The model-folder enumeration shows the installation includes face-
  identity model classes (InsightFace, InstantID, PuLID, PhotoMaker).
  An exposed surface of this kind risks disclosure of personal
  information in the meaning of PIPL Articles 28 and 51, and falls
  below the technical-safeguard floor implied by DSL Article 27 and
  CSL Article 21.

WHAT I DID NOT DO
  I did not submit any prompts. I did not read prompt-history bodies.
  I did not read /view outputs. I did not attempt SSH authentication.
  I did not upload any file. I read only documented endpoint metadata
  to confirm the exposure, then stopped.

WHAT I AM REQUESTING
  Coordination with the network operator (China Telecom Hunan) and
  the end operator to:
    1. Bind ComfyUI to localhost or place it behind authentication.
    2. Confirm the operator is aware of the exposure window.

EVIDENCE
  Shodan host record, raw enumeration outputs, and the full case-study
  artifact are available on request to a CNCERT-verified address.

I will not publish the operator identity, if and when determined, for
ninety (90) days from the date of this notification or until the
exposure is remediated, whichever is sooner.

Respectfully,
Nicholas Kloster
NuClide Research
nicholas@nuclide-research.com
https://nuclide-research.com
```

---

## 7. 733-lane summary line for the case study top sheet

> The host sits inside three overlapping PRC regulatory regimes (PIPL / DSL / CSL) and the exposure pattern fails the technical-safeguard floor of all three. The hardware (8x A100-SXM4-80GB) is BIS-restricted; acquisition path is undetermined and out of NuClide's lane. The capability-layer data-class profile confirms image-gen, face-identity, audio, video, and LLM classes; prompt-content classes are not read by restraint discipline. Disclosure routes to CNCERT/CC as primary, with CHINANET abuse as parallel CC. Draft staged; send decision deferred.

---

## Sources

- [China's Personal Information Protection Law (PIPL) — Bloomberg Law](https://pro.bloomberglaw.com/insights/privacy/china-personal-information-protection-law-pipl-faqs/)
- [Data Protection Laws of the World — China (DLA Piper)](https://www.dlapiperdataprotection.com/index.html?c=CN)
- [China Data Privacy Laws: PIPL, CSL & DSL Compliance Guide (Recording Law)](https://www.recordinglaw.com/world-laws/world-data-privacy-laws/china-data-privacy-laws/)
- [What is China's Data Security Law? — Securiti](https://securiti.ai/china-data-security-law/)
- [China's New Data Security Law: What International Companies Need to Know — Orrick](https://www.orrick.com/en/Insights/2021/09/Chinas-New-Data-Security-Law-What-International-Companies-Need-to-Know)
- [CNCERT/CC — FIRST.org member team page](https://www.first.org/members/teams/cncert-cc)
- [CNCERT/CC — About Us (cert.org.cn English)](https://www.cert.org.cn/publish/english/index.html)
- [BIS October 2022 / 2023 export-control timeline — GamersNexus](https://gamersnexus.net/gpus-news/timeline-gpu-export-controls-nvidia-gpu-bans-ai-gpu-black-market)
- [Understanding the Biden Administration's Updated Export Controls — CSIS](https://www.csis.org/analysis/understanding-biden-administrations-updated-export-controls)
- [US Export Controls and China: Advanced Semiconductors — Congress.gov CRS R48642](https://www.congress.gov/crs-product/R48642)
- [China gets banned Nvidia AI chips via gray markets — Asia Times](https://asiatimes.com/2024/01/china-gets-banned-nvidia-ai-chips-via-gray-markets/)
