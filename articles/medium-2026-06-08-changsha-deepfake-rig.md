# A Public Deepfake Factory Is Running on the Chinese Internet, Free For Anyone to Use

## How we found 2,423 hours of cloned voice output, eight A100 GPUs, and a complete face-and-voice deepfake pipeline running unauthenticated on a single Changsha box

_NuClide Research · 2026-06-08_

---

One IP address. Five open ports. Eight A100 GPUs. And a `/tts` endpoint, sitting on the public internet, that has already generated six hundred sixteen thousand voice-clones of arbitrary text in any voice an attacker can find on YouTube.

We are publishing this finding because the operator's identity is not in the public record, the surface has no authentication, and the rest of the security industry's framing of "exposed AI infrastructure" has been treating numbers as the story when the actual story is what is running on the numbers.

This is one box. Here is what is on it.

---

## The shape of the find

```
113.240.68.47    China Telecom Hunan, Changsha (AS63835)

  TCP/22    OpenSSH 8.9p1 Ubuntu                       (banner only)
  TCP/8188  ComfyUI 0.23.0 + ComfyUI-Manager 3.38.1    (unauthenticated)
  TCP/20111 uvicorn FastAPI Edge Runtime API           (voice TTS, unauthenticated)
  TCP/20112 second TTS instance                        (unauthenticated)
  TCP/42113 silent listener                            (identity opaque under restraint)

Hardware  : 8 x NVIDIA A100-SXM4-80GB  (640 GB total VRAM)
            1.08 TB host RAM
            CUDA 13.0, PyTorch 2.12, Python 3.13.13
```

Shodan saw two of those ports. The other three were found by running a real port sweep against the box. The headline is the third one.

---

## The TTS endpoint

Port 20111 serves a FastAPI application calling itself "Edge Runtime API." It exposes a `/health` endpoint, an `/info` endpoint, and a `/tts` endpoint. The `/health` endpoint reports telemetry.

```
total_jobs           616,898
total_seconds          8,725,332  ( = 2,423 hours of generated audio )
total_gpu_hours              474
```

Six hundred and sixteen thousand voice-clone jobs. Two thousand four hundred and twenty three hours of generated speech. Four hundred and seventy four hours of A100 time. This service has been running, at scale, for a while.

The `/tts` endpoint accepts a JSON body. Two fields matter:

- `text` — what you want the voice to say
- `reference_audio_url` — any HTTP or HTTPS URL pointing at an audio sample

It returns a WAV.

The reference-audio-URL field is what makes this finding load-bearing. Anyone with the URL can:

1. Point `reference_audio_url=https://youtube...` at any public clip of any speaker on the internet
2. Submit the text they want that speaker to say
3. Receive a WAV of the cloned voice

This is functionally a public, unauthenticated, free voice-cloning service of the same class as ElevenLabs's commercial tier, running on hardware that the United States Bureau of Industry and Security has prohibited for export to China since October 2022.

We did not test the endpoint. We did not submit any clone job. The restraint discipline that governs NuClide's surveys does not unlock for finding-quality reasons. The capability is documented from the `/health` telemetry and the FastAPI auto-generated OpenAPI document; the cloning is something we know the box does without our needing to make it do so.

---

## The rest of the pipeline

The TTS service does not exist on this box in isolation. The same machine is running a ComfyUI 0.23.0 workflow editor on port 8188, also unauthenticated, with a custom-node loadout that looks like this:

### Face identity (everything you need to put a specific person's face on generated video)

- **InsightFace** — face detection and embedding
- **InstantID** — single-image face injection into diffusion outputs
- **PuLID-Flux** — identity-preserving image generation, Flux backbone
- **PhotoMaker** — multi-image identity blending
- **facexlib** — face landmarks and alignment

### Animation (everything you need to drive that face with motion)

- **Wan-2.2-Animate-14B** (Alibaba) — character animation from reference image
- **WanVideoWrapper** (146 node classes)
- **MoCap fullbody LoRAs** + **Lightx2v step-distillation**

### Audio (everything you need to align the voice to the mouth)

- **mmaudio** — multimodal audio conditioning
- **wav2vec2** — speech feature extraction

### Multi-vendor commercial AI connectors

The `/object_info` endpoint reveals API-key-bearing nodes for: Wan (171 nodes), Hunyuan (21), Kling (26), ByteDance (15), Tripo (15), Vidu (13), Qwen (9), Tencent (6), MiniMax/Hailuo (3). The operator can call into the full Chinese commercial AI ecosystem from this same UI.

### Custom in-house packages

Two non-stock comfy packages appear in the version manifest: `comfy-aimdo 0.4.7` and `comfy-kitchen 0.2.10`. Neither exists in the upstream ComfyUI ecosystem. They were either built in-house by this operator or sourced from a specific developer or studio. Either way they are an attribution fingerprint.

Put together: face identity model + character animation model + voice cloning service + multi-vendor commercial AI access, on a 640 GB VRAM cluster, with no authentication. It is the complete pipeline for producing a video of any specific person saying anything in their own voice.

---

## Why this matters more than a number

Public reporting on exposed AI infrastructure has settled into a pattern: a scanner discloses a count ("over 1,000 ComfyUI", "over 200,000 Ray"), the security press republishes the count, and the conversation moves on. That framing has been correct for ComfyUI, where Censys ARC documented a cryptominer botnet in April. It has been correct for Ray, where Oligo Security extended their March 2024 ShadowRay disclosure to a coordinated November 2025 ShadowRay 2.0 campaign.

What the count framing misses is the operator. A botnet of 1,000 cryptomining boxes is a number. A single box running a turnkey deepfake production line at industrial scale is a story.

The box at 113.240.68.47 is invisible to the existing surveying community. Greynoise has never observed it. The Wayback Machine has no record of it. A direct web search for the IP returns zero results. The neighboring host at .55 in the same /24 has briefly appeared on a Chinese-origin recon target list, and its TLS certificate is issued to **Changsha Jinglüe Zhichuang Information Technology Co.** (长沙经略智创信息技术有限公司, AS-attributed to the same Changsha IDC), but the headline box .47 itself has zero metadata pointing at an operator name.

This is what we mean by **infrastructure-scanner-dark, web-OSINT-dark**: invisible to web search, threat-intel feeds, and the archive layer, but plainly indexable by the platform-fingerprinting tools any researcher (or attacker) can run. The hardness of attribution is, itself, the operator's signature.

---

## The export-control footnote

8× A100-SXM4-80GB is the original, unconstrained A100 part. The United States Bureau of Industry and Security has restricted export of this exact part to PRC end users since October 7, 2022. NVIDIA produced the China-spec H800 and A800 to fill the gap; those were restricted by the October 2023 follow-up rule; and the current China-spec part is the H20.

A complete 8× A100-SXM4-80GB cluster operating in Changsha in June 2026 was acquired by one of three paths: pre-ban procurement (2022-Q3 or earlier), gray-market import through Singapore or Malaysia or Hong Kong shell entities, or cloud resale from a non-PRC tenant. NuClide does not engage in BIS or Commerce reporting; the export-control question is recorded as observed context and the disclosure routing remains in cyber-incident channels.

The substrate provider is China Telecom's Hunan Changsha IDC, abuse contact `anti-spam@chinatelecom.cn`. The national CERT is CNCERT/CC. A draft notification template, marked DO NOT SEND, is staged in NuClide's assessments directory pending review.

---

## What we did not do

The restraint discipline is the methodology. The list of things we did not do is the explicit definition of what makes this a finding rather than an attack.

We did not POST to `/tts`. No voice was cloned by us.
We did not POST to `/prompt`. No image, animation, or video was generated by us.
We did not GET any `/history` body, `/queue` body, or `/view/<filename>`.
We did not POST to `/upload/image`.
We did not attempt any SSH authentication.
We did not exercise the ComfyUI-Manager `install/git_url` RCE.

Every observation is a metadata GET that any operator's own management console would issue against its own infrastructure. Names, counts, version strings, model file names. Names are the finding.

---

## How to check your own surface

If you operate a Ray, ComfyUI, or other unauthenticated AI service on the public internet, the question is not whether you have been "compromised" in the binary-state sense. The question is what your service's `/health` or `/info` or `/system_stats` telemetry says about how it has been used and by whom.

Run this from outside your own VPC:

```bash
# What is the public-internet view of this service?
curl -sI http://<your-host>:<your-port>/

# What does its own telemetry say about its history?
curl -s http://<your-host>:<your-port>/health
curl -s http://<your-host>:<your-port>/info
```

If you find a job-count number larger than the number of jobs you yourself have submitted, the service has been used by someone else. If that someone else used your GPU to clone the voice of a person who did not consent to be cloned, the operator-side accountability for that use is, by the laws of every relevant jurisdiction, yours.

---

## The catalog

This is the fifth finding NuClide is publishing in our 2026-06-08 population sweep. The earlier four are queued or already linked from our OSINT repository.

- ComfyUI default-port re-measurement of the GHOST surface Censys ARC published in April
- Meilisearch unauthenticated cluster including the 66-host Hong Kong SEO content-spam fleet
- Marqo small-population sweep, 100 percent of LIVE unauthenticated
- Ray Dashboard sweep with a five-signal IoC pattern identifying the ShadowRay 2.0 attacker fleet at 463 unique IPs

A single Changsha deepfake rig is the fifth. The pattern across all five is the same: the platform's default authentication posture predicts the operator's exposure rate, and the substrate provider is where the legitimate disclosure pressure can be applied. The platform layer itself has, by-design, opted out.

This is what the modern AI infrastructure exposure surface looks like, this month, on the public internet. The numbers are large because the platforms ship without auth. The operators behind the numbers each have a story. We are starting to publish them, one at a time, with the restraint that comes with not crossing back through the doors the operators left open.

---

_NuClide Research is an independent security-research lab. Our case studies, surveys, and tooling are public at_ `github.com/nuclide-research`. _Contact:_ `nicholas@nuclide-research.com`. _Prior published research includes CISA-coordinated disclosures CVE-2025-4364 and ICSA-25-140-11._
