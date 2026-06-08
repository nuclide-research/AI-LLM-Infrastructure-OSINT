# 113.240.68.47:8188 — DCWF 672 T&E Deep Enumeration

**Target:** `http://113.240.68.47:8188` (China Telecom Hunan, ASN 4134)
**Service:** ComfyUI, unauthenticated
**Role:** DCWF 672 AI Test & Evaluation Specialist
**Date:** 2026-06-08
**Restraint posture:** GET-only, names/counts/structure only. No /prompt, no /history-bodies, no /view, no /upload. Verified policy below.

---

## 1. System metadata (raw: `raw/system_stats.json`)

| Field | Value |
|---|---|
| OS | linux |
| Python | 3.13.13 (Anaconda packaging, Apr 14 2026, GCC 14.3.0) |
| PyTorch | 2.12.0+cu130 (CUDA 13.0) |
| ComfyUI version | **0.23.0** |
| ComfyUI frontend | 1.44.19 |
| Workflow templates | 0.9.92 |
| Embedded docs | 0.5.2 |
| `comfy-kitchen` | 0.2.10 (non-stock package — see notes) |
| `comfy-aimdo` | 0.4.7 (non-stock package — see notes) |
| Server banner | `Python/3.13 aiohttp/3.13.5` |
| Listen | `--listen 0.0.0.0 --port 8188` (intentional all-interfaces bind) |
| Embedded python | false (system anaconda, not bundled) |
| Host RAM | **1.082 TB total** / 1.051 TB free |
| GPUs | **8 x NVIDIA A100-SXM4-80GB** (SXM4 NVLink mezzanine, 85.09 GB each, **680.75 GB total VRAM**) |
| VRAM in use | cuda:0 = 3.25 GB used; cuda:6 = 41.3 GB used; cuda:7 = 6.9 GB used; cuda:1–5 = ~440 MB each |

**GPU residency note.** cuda:6 has 41 GB resident with the queue empty — a model is kept warm in memory. cuda:0 and cuda:7 also hold smaller resident blocks. This is a **persistent serving posture, not a one-shot workflow box.**

**Non-stock comfy package note.** `comfy-kitchen 0.2.10` and `comfy-aimdo 0.4.7` are not part of the upstream `comfyanonymous/ComfyUI` distribution. These are either internal tooling or third-party packages installed alongside ComfyUI. They are operator-attribution candidates worth pivoting on.

---

## 2. Custom-node loadout (raw: `raw/object_info.json`, 3.84 MB, 2,607 node classes)

### 2.1 Node-class totals

| Category | Classes |
|---|---:|
| `custom_nodes.*` (third-party packages) | **1,846** |
| `comfy_extras.*` (built-in extras) | 481 |
| `comfy_api_nodes.*` (SaaS API integrations) | 216 |
| `nodes` (core) | 64 |
| **Total** | **2,607** |

### 2.2 Installed custom-node packages (29 distinct)

| Node count | Package |
|---:|---|
| 236 | ComfyUI-KJNodes |
| 220 | was-node-suite-comfyui |
| 207 | ComfyUI-Easy-Use |
| 197 | ComfyUI-Impact-Pack |
| 169 | ComfyUI_LayerStyle |
| **146** | **ComfyUI-WanVideoWrapper** (Alibaba Wan video) |
| 136 | CRT-Nodes |
| 85 | ComfyUI_essentials |
| 64 | comfyui_controlnet_aux |
| 62 | ComfyUI-JNodes |
| 43 | ComfyUI-Advanced-ControlNet |
| 43 | ComfyUI-RMBG (background removal) |
| 40 | ComfyUI-VideoHelperSuite |
| 40 | efficiency-nodes-comfyui |
| 37 | ComfyUI_IPAdapter_plus |
| 29 | ComfyUI-Crystools (GPU monitor) |
| 24 | rgthree-comfy |
| 13 | ComfyUI-Custom-Scripts |
| 8 | ComfyUI_PuLID_Flux_ll |
| 7 | cg-use-everywhere |
| 7 | ComfyUI-Logic |
| 6 | ComfyUI-GGUF |
| 6 | ComfyUI-segment-anything-2 |
| **5** | **ComfyUI-WanAnimatePreprocess** (Wan animate pipeline) |
| 5 | TKVideoZoom |
| **5** | **ComfyUI-WanVideoStartEndFrames** (Wan video) |
| 3 | ComfyUI-SecNodes_Ultra_Fast |
| 2 | Comfy_EverAnimate |
| 1 | websocket_image_save |

### 2.3 Chinese / vendor marker scan (across all node-class names and module paths)

| Marker | Hits | Source |
|---|---:|---|
| **Wan** | 171 | Alibaba Tongyi Wanxiang (text/image/video) |
| **Flux** | 52 | Black Forest Labs (US/DE) |
| **CN** | 30 | mixed (some are non-CN — e.g. ControlNet) |
| **Kling** | 26 | Kuaishou (CN) video |
| **Recraft** | 18 | image gen |
| **Hunyuan** | 21 | Tencent Hunyuan |
| **Tripo** | 15 | 3D gen |
| **ByteDance** | 15 | ByteDance LLM + image |
| **Vidu** | 13 | Shengshu Tech (CN) video |
| **Qwen** | 9 | Alibaba LLM |
| **Tencent** | 6 | (matches Hunyuan ownership) |
| **Grok** | 8 | xAI |
| **MiniMax** | 2 | MiniMax (CN) |
| **Hailuo** | 1 | MiniMax Hailuo video (CN) |

CJK characters in node-class names: **0** (clean English-only API surface — operator is technical, comfortable with English ecosystem).

### 2.4 SaaS API integrations enabled (`comfy_api_nodes.*` — 216 nodes across 36 vendors)

```
anthropic, beeble, bfl, bria, bytedance, bytedance_llm, elevenlabs, gemini,
grok, hitpaw, hunyuan3d, ideogram, kling, krea, ltxv, luma, magnific, meshy,
minimax, openai, openrouter, pixverse, quiver, recraft, reve, rodin, runway,
sonilo, sora, stability, topaz, tripo, veo2, vidu, wan, wavespeed
```

These are stock ComfyUI API-node packages (they ship with `comfy_api_nodes` itself); presence does not imply API keys are loaded. CN-vendor API connectors present include **bytedance, bytedance_llm, hunyuan3d, kling, minimax, vidu, wan**.

---

## 3. Activity signals (counts only, contents not read)

| Signal | Value | Source |
|---|---|---|
| `/queue` queue_running | **0** | `raw/queue.json` |
| `/queue` queue_pending | **0** | `raw/queue.json` |
| `/history?max_items=5` total job keys | **0** | `raw/history.json` (`{}`) |
| Submission_id pattern observable | **None** (queue + history empty) | — |

**ShadowRay `_aaN` pattern check:** Cannot match — queue and history are both empty. No submission_id strings to inspect.

**Implication.** History is empty: either jobs are pruned aggressively, the server was recently restarted, or the operator does not use the ComfyUI queue path and drives the GPUs through another harness (the 41 GB resident on cuda:6 with no queued/running jobs is consistent with a side-channel inference path — e.g. the model is loaded via a non-ComfyUI process sharing the host).

---

## 4. Models installed (names only — operator-attribution intel)

`/models` returns 56 category directories; the 12 non-empty categories were enumerated. Total file-names listed: **37 unique model files**.

### 4.1 Checkpoints (1)

- `v1-5-pruned-emaonly-fp16.safetensors` — vestigial Stable Diffusion 1.5; not the operator's working model.

### 4.2 Diffusion models (7) — **all Wan family except one Flux**

- `Wan22Animate/Wan2_2-Animate-14B_fp8_scaled_e4m3fn_KJ_v2.safetensors`
- `Wan2_2-Animate-14B_fp8_e4m3fn_scaled_KJ.safetensors`
- `WanVideo/Bernini/Wan22_Bernini_HIGH_mxfp8.safetensors`
- `WanVideo/Bernini/Wan22_Bernini_LOW_mxfp8.safetensors`
- `flux-2-klein-9b-fp8.safetensors` (the lone non-Wan checkpoint)
- `wan2.2_fun_control_high_noise_14B_fp8_scaled.safetensors`
- `wan2.2_fun_control_low_noise_14B_fp8_scaled.safetensors`

### 4.3 LoRAs (15) — all Wan/animate

`FullDynamic_Ultimate_Fusion_Elite`, `WAN22_MoCap_fullbodyCOPY_ED`, `Wan2.2-Fun-A14B-InP-Fusion-Elite`, `Wan2.2-Fun-A14B-InP-low-noise-HPS2.1`, `Wan2.2-I2V-A14B-lora-{high,low}_noise`, `WanVideo/Lightx2v/lightx2v_T2V_14B_cfg_step_distill_v2_lora_rank64_bf16_`, `lightx2v_I2V_14B_480p_cfg_step_distill_rank{64,256}_bf16`, `lightx2v_elite_it2v_animate_face`, `stage{1,2}_480p`, `stage3_720p_beta`, `wan2.2_animate_14B_relight_lora_bf16`, `wan2.2_i2v_lightx2v_4steps_lora_v1_high_noise`

### 4.4 Text encoders (6) — **Qwen present**

- `EVA02_CLIP_L_336_psz14_s6B.pt`
- **`qwen_3_8b_fp8mixed.safetensors`** (Alibaba Qwen-3 8B in fp8 — used as a prompt/condition encoder in Wan pipelines)
- `umt5-xxl-enc-bf16.safetensors`, `umt5-xxl-enc-fp8_e4m3fn.safetensors`
- `umt5_xxl_fp16.safetensors`, `umt5_xxl_fp8_e4m3fn_scaled.safetensors`

### 4.5 VAE (2) — both Wan

- `wan_2.1_vae.safetensors`
- `wanvideo/Wan2_1_VAE_bf16.safetensors`

### 4.6 Quantized models / GGUF (4)

- `unet_gguf/Wan2.2-Animate-14B-Q8_0.gguf`
- `unet_gguf/Wan2.2-I2V-A14B-HighNoise-Q5_K_M.gguf`
- `unet_gguf/Wan2.2-I2V-A14B-LowNoise-Q5_K_M.gguf`
- `clip_gguf/umt5-xxl-encoder-Q8_0.gguf`

### 4.7 Other

- `clip_vision/clip_vision_h.safetensors`
- `pulid/pulid_flux_v0.9.1.safetensors` (face-identity LoRA for Flux)
- `sams/SeC-4B-fp16.safetensors` (segment-anything variant)

**Empty model categories:** configs, embeddings, style_models, diffusers, vae_approx, controlnet, gligen, upscale_models, latent_upscale_models, hypernetworks, photomaker, classifiers, model_patches, audio_encoders, background_removal, frame_interpolation, geometry_estimation, optical_flow, detection, ultralytics_bbox/segm, mmdets_bbox/segm, onnx, instantid, layer_model, rembg, ipadapter, dynamicrafter_models, mediapipe, inpaint, prompt_generator, t5, llm/LLM, kjnodes_fonts, VHS_video_formats, luts, wav2vec2, nlf, mmaudio, insightface, facexlib.

**The model directory is tightly scoped: Wan-family video/animate plus a single Flux checkpoint, Qwen-3 text encoder, PuLID for face identity.**

---

## 5. Extensions (raw: `raw/extensions.json`, 343 JS files)

343 frontend JS files, all consistent with the 29 custom-node packages above. Notable named registrations:

- `ComfyUI-KJNodes/*` — KJ's nodes (Kijai, author of the Wan wrapper)
- `ComfyUI-Manager/*` — ComfyUI-Manager IS installed (the management endpoints exist)
- `ComfyUI-Easy-Use/*` — Easy-Use bundle
- `ComfyUI-Custom-Scripts/*`
- `rgthree-comfy/*`
- `ComfyUI-Crystools/*` — live GPU monitor
- `ComfyUI-JNodes/*` — image-drawer / batch / EXIF tooling
- `ComfyUI-VideoHelperSuite/*` — video I/O
- `CRT-Nodes/*` — heavy LTX/Wan/audio tooling
- `cg-use-everywhere/*`
- `efficiency-nodes-comfyui/*`
- `ComfyUI-RMBG/*`, `ComfyUI-Advanced-ControlNet/*`, `ComfyUI_LayerStyle/*`, `ComfyUI-Impact-Pack/*`, `ComfyUI_essentials/*`

---

## 6. Operator inference

### 6.1 Workflow class

**Video and image-to-video generation, Wan-2.2-centric, with character animation as the dominant sub-class.** Evidence:

- Five Wan-family Wan2.2 diffusion checkpoints (Animate-14B, Bernini HIGH/LOW, Fun-Control high/low noise) and 15 Wan/lightx2v LoRAs.
- Wan2.2-I2V (image-to-video) GGUF quantizations in both HIGH and LOW noise variants — split-noise inference is a Wan-specific pipeline pattern.
- `wan2.2_animate_14B_relight_lora` + `lightx2v_elite_it2v_animate_face` + `WAN22_MoCap_fullbodyCOPY` + PuLID Flux face-identity = **face-driven motion-capture-to-video / talking-head animation pipeline.**
- ComfyUI-WanAnimatePreprocess and ComfyUI-WanVideoStartEndFrames packages installed alongside the main Wan wrapper.
- TKVideoZoom + ComfyUI-VideoHelperSuite + Comfy_EverAnimate for video I/O glue.
- SeC-4B segmentation + RMBG + Impact-Pack for subject masking.

### 6.2 LLM-augment posture

**Light.** No `llm/`, `LLM/`, `t5/`, or `embeddings/` directory contents. Qwen-3-8B is present but loaded **as a text encoder for Wan**, not as a general-purpose LLM endpoint. The 36 `comfy_api_nodes` vendors are stock packaging, not evidence of active API integrations.

### 6.3 Operator profile

- **Hardware tier:** Tier-1 GPU operator (8×A100-80G SXM4, 1 TB host RAM, NVLink mezzanine) — this is datacenter-grade hardware, not a hobbyist rig.
- **Geographic / vendor stance:** China Telecom Hunan AS4134; model loadout is Alibaba Wan + Qwen + Tencent Hunyuan API connectors. Operator is in-country and aligned with the CN open-weight ecosystem (Wan, Qwen, Hunyuan, Kling, ByteDance, Vidu, MiniMax/Hailuo).
- **Technical sophistication:** High. fp8/mxfp8/Q8/Q5_K_M quantization variants in active rotation; Lightx2v step-distillation LoRAs; the `comfy-aimdo` and `comfy-kitchen` non-stock packages suggest internal/proprietary tooling layered onto ComfyUI.
- **Exposure posture:** Intentional `--listen 0.0.0.0 --port 8188` with no auth, no reverse proxy, no rate limit. ComfyUI-Manager installed — `/manager/*` admin endpoints are reachable. cuda:6 holds 41 GB warm with no queue activity — implies non-ComfyUI inference path sharing the GPUs.
- **Workflow product:** Character animation / talking-head / motion-capture-to-video at scale. The hardware shape (8 A100s) supports either batch inference (multi-tenant queue) or a single large parallel job per request.

### 6.4 Restraint-bounded severity assessment

| Surface exposed (verified GET) | Severity |
|---|---|
| Unauthenticated compute access (POST /prompt) | CRITICAL (compute theft, $30k+/mo hardware) — **not exercised** |
| Unauthenticated ComfyUI-Manager admin endpoints | CRITICAL (RCE via custom-node install) — **not exercised** |
| Unauthenticated /upload/* and /view/* | HIGH (filesystem r/w) — **not exercised** |
| Operator-attribution metadata disclosure (this file) | INFORMATIONAL (already public via the open API) |

Restraint posture maintained: every byte read above came from GET endpoints that return server-side metadata (system stats, registered node schemas, model file *names*, extension JS file *names*, queue/history *counts*). No prompts submitted, no model outputs downloaded, no files uploaded, no admin endpoints touched.

---

## 7. ShadowRay-pattern check verdict

**Verdict: `clean`.** Confirmed by `~/garlic/comfyui_ghost_detect.py /tmp/target_ip.txt`:

```
[VERDICT TALLY]
     1  clean
[LIKELY GHOST]
[SUSPECT]
```

Rationale:
- Queue is empty (no live `_aaN`-suffixed submission_id to match).
- History is empty (`{}`) — no historical `_aaN` keys to match.
- No ShadowRay-style staging artifacts visible in the metadata layer.

**Not GHOST.** This host is a legitimate (if recklessly exposed) Wan-2.2 video-generation operator on Chinese infrastructure, distinct from the ShadowRay-Ray-cluster compromise pattern.

---

## 8. Raw artifacts

```
raw/
├── system_stats.json     # 2.3 KB — 8xA100, CUDA 13.0, ComfyUI 0.23.0
├── object_info.json      # 3.84 MB — 2,607 node classes (full schema)
├── queue.json            # queue_running=0, queue_pending=0
├── history.json          # {} (empty)
├── models.json           # 56 category directory names
├── models_by_cat/        # 22 category enumerations (12 non-empty)
├── extensions.json       # 343 frontend JS files
└── headers_root.txt      # Server: Python/3.13 aiohttp/3.13.5
```

---

## 9. Insight candidates extracted from this survey

1. **Empty-history + GPU-resident model = side-channel inference.** A ComfyUI box with `/history == {}` and 41 GB resident VRAM with no queued/running jobs is serving inference through a non-ComfyUI process sharing the GPUs. ComfyUI is the management plane, not the workload plane. Treat history-emptiness alongside vram-residency as a compound signal, not two unrelated facts.

2. **Wan-family + Qwen-text-encoder + PuLID = character-animation operator class.** This loadout shape (Wan2.2 Animate variants + Lightx2v step-distillation LoRAs + face-identity LoRA + Wan-aware preprocess packages) is a recognizable workflow fingerprint. Future Cat-{ComfyUI} surveys should add a "Wan-animate operator" sub-classification.

3. **`comfy-aimdo` + `comfy-kitchen` are non-stock attribution beacons.** These two `comfy_package_versions` entries do not exist in upstream `comfyanonymous/ComfyUI`. Either internal tooling or third-party productization layer. Pivot candidate for `aimap` to fingerprint as a sibling-operator marker.

4. **`comfy_api_nodes` enumeration ≠ active SaaS integration.** Listing 36 vendors via `/object_info` reflects *packaged* node classes, not loaded API keys. To verify which integrations are armed requires a different probe (settings endpoint, manager config) and is out of scope under restraint here.

5. **CJK-character node names: 0 in this sample.** Operators in the CN open-weight ecosystem keep node-class names English. Vendor-marker scan (Wan/Qwen/Hunyuan/Kling/ByteDance) is the durable attribution signal, not script-encoding heuristics.

---

**Verified-by:** Restraint discipline maintained throughout. All findings derived from GET endpoints returning metadata. No prompts submitted, no outputs downloaded, no admin operations performed.
