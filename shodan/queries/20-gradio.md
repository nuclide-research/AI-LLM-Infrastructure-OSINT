# 20. Gradio / Stable Diffusion WebUI (A1111) / Langflow

_Section created: 2026-05-09_

Port 7860 is Gradio's default but is heavily shared with other ML tools (Stable Diffusion A1111, Langflow, RVC, various HuggingFace-style demos). Distinguishing platforms requires response-body fingerprinting beyond the port. Gradio ships with no auth by default (`share=False` but no login gate); A1111 has no built-in auth. Langflow added `LANGFLOW_AUTO_LOGIN` gating in v1.5.

**Survey result (2026-05-03):** 481 port-7860 hits across 28 cloud /16 ranges → **16 confirmed** (9 Langflow, 1 A1111, 6 generic Gradio). Sparse result — most operators run these on `--listen 127.0.0.1` or behind reverse proxies on 80/443. Voice/audio AI tools (RVC, OpenVoice, Bark, F5-TTS) also default to 7860 and are covered separately in `17-voice-audio-ai.md`.

**Auth posture:** T1 for generic Gradio and A1111 (no auth concept). T2 for Langflow post-v1.5 (`LANGFLOW_AUTO_LOGIN` must be explicitly disabled, but many operators leave it open).

**CVE watch:**
- `CVE-2024-36420` — Flowise (not Gradio; shares port patterns) pre-auth RCE.
- `CVE-2026-33017` — Langflow: unauth code execution via flow execution endpoint (observed in NuClide CVE-research-lab finding 2026-05-03).
- No current Shodan-level CVE for base Gradio; risk is compute-theft and embedded API key exposure.

---

**Shodan indexing note:** Port-constrained bare strings (`"component_count" port:7860`, `"txt2img" port:7860`) return 0. Drop the port constraint or use `http.html:` — both recover the population. `http.html:"gr-app"` (135) is the best Gradio CSS class signal; `"gradio"` bare (252) is broadest.

## Generic Gradio

| Shodan Query | Verified hits | Notes |
|---|---|---|
| `"gradio"` | **252** | Broadest; any indexed field |
| `http.html:"gr-app"` | **135** | Gradio DOM container class; best precision |
| `http.html:"gradio-container"` | 15 | CSS class variant |
| `port:7860` | — | Default port; heavily shared (A1111, RVC, Langflow, TTS tools) |
| `port:7860 http.html:"gradio"` | 3 | Port-constrained; most operators run behind reverse proxy |
| `port:7860 http.html:"gr-app"` | — | Port + DOM class |
| `port:7860 http.html:"/info"` | — | Gradio `/info` endpoint in page source |
| `port:7860 http.status:200` | — | Live + responding |
| `http.html:"gradio" port:7860` | 3 | HTML-scoped on default port |
| `http.favicon.hash:2021239869` | — | Gradio favicon hash |
| `http.favicon.hash:2021239869 port:7860` | — | Favicon + default port |
| `ssl.cert.subject.cn:"gradio"` | — | TLS cert CN |
| `hostname:"gradio" port:7860` | — | rDNS + default port |

---

## Stable Diffusion WebUI (Automatic1111 / AUTOMATIC1111)

| Shodan Query | Verified hits | Notes |
|---|---|---|
| `http.html:"txt2img"` | **52** | A1111 tab identifier; works without port constraint |
| `http.html:"AUTOMATIC1111"` | **11** | Repo name in HTML; any port |
| `"dreamshaper"` | **23** | Popular checkpoint name; proxy for community SD deployments |
| `"stable-diffusion-webui"` | 7 | A1111 repo name in any indexed field |
| `"sdapi"` | 5 | A1111 API path bare string |
| `http.html:"stable diffusion"` | — | SD WebUI in page source |
| `http.html:"img2img"` | — | A1111 tab identifier |
| `http.html:"checkpoint"` | — | Model checkpoint references in A1111 UI |
| `http.html:"safetensors"` | — | Model format reference in A1111 page source |
| `port:7860 http.html:"txt2img"` | 0 | Port constraint kills the signal; use without port |
| `port:7860 http.html:"sdapi"` | 0 | Same; drop port constraint |

---

## Langflow

| Shodan Query | Notes |
|---|---|
| `port:7860 http.html:"langflow"` | Langflow on default port |
| `port:7860 http.html:"Langflow"` | Capitalized form |
| `http.html:"langflow" port:7860` | HTML-scoped |
| `http.html:"/api/v1/auto_login"` | Langflow-specific auth endpoint; presence in source = likely Langflow |
| `http.html:"/api/v1/users/whoami"` | Langflow API endpoint |
| `"Langflow" port:7860` | Bare-string on default port |
| `http.title:"Langflow" port:7860` | Title-based; Langflow sets a custom title |
| `port:7860 http.html:"auto_login"` | auto_login parameter |

---

## InvokeAI / ComfyUI on 7860

| Shodan Query | Notes |
|---|---|
| `port:7860 http.html:"InvokeAI"` | InvokeAI (ships on 9090 default but alt deployments use 7860) |
| `port:7860 http.html:"invokeai"` | Lowercase |
| `port:7860 http.html:"ComfyUI"` | ComfyUI (default 8188, but alt deploys use 7860) |

---

## HuggingFace Spaces / generic ML demos

| Shodan Query | Notes |
|---|---|
| `port:7860 http.html:"huggingface"` | HuggingFace-style deployment in source |
| `port:7860 http.html:"spaces"` | HF Spaces clone on personal VPS |
| `port:7860 http.html:"transformers"` | HuggingFace Transformers in source |
| `port:7860 http.html:"model_id"` | Model ID reference (HF-style naming) |
| `port:7860 http.html:"pipeline"` | HF pipeline identifier |

---

## Cloud-provider scoped

| Shodan Query | Notes |
|---|---|
| `port:7860 org:"hetzner"` | Hetzner (researcher labs, single finding in survey) |
| `port:7860 org:"digitalocean"` | DigitalOcean (A1111 finding in survey) |
| `port:7860 org:"vultr"` | Vultr |
| `port:7860 org:"amazon"` | AWS |
| `port:7860 org:"google"` | GCP |
| `port:7860 country:US` | US-scoped |
| `port:7860 country:CN` | China |
| `port:7860 country:DE` | Germany |
| `port:7860 country:IN` | India |
| `port:7860 -port:443` | Non-HTTPS only |

---

## Combined

| Shodan Query | Notes |
|---|---|
| `port:7860 (http.html:"gradio" OR http.html:"stable diffusion" OR http.html:"langflow")` | Full port-7860 AI sweep |
| `port:7860 (http.html:"txt2img" OR http.html:"sdapi" OR http.html:"stable-diffusion-webui")` | A1111-specific sweep |
| `port:7860 (http.html:"gradio" OR http.html:"Gradio") -http.html:"langflow" -http.html:"stable diffusion"` | Pure Gradio (exclude SD and Langflow) |
| `(port:7860 OR port:7861 OR port:7862) http.html:"gradio"` | Gradio across common alt ports |
