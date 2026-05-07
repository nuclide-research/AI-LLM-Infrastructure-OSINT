# 3. Model Serving & Inference

_Section verified: April 22, 2026 11:38_

The runtime layer that exposes models over HTTP. Most modern serving stacks emulate the OpenAI API surface (`/v1/chat/completions`, `/v1/models`, `/v1/embeddings`), making them trivially fingerprintable, and often trivially abusable as free compute (LLMjacking).

## Inference Servers

| Shodan Query | Notes |
|---|---|
| `"SillyTavern"` | 9,030 hits, LLM frontend (chat/RP workloads); most-exposed model-serving surface in this catalogue |
| `http.html:"/v1/chat/completions"` | **6,238 hits**, canonical OpenAI-compat fingerprint (path appears in HTML responses; covers vLLM, llama.cpp, LMDeploy, LM Studio, most inference servers) |
| `http.html:"/v1/models"` | 6,089 hits, same category, paired canonical OpenAI-compat path |
| `"llama.cpp"` | 1,483 hits, most-deployed specific server (bare banner match) |
| `"llama.cpp" port:8080` | 461 hits, llama.cpp on default port |
| `"vLLM"` | 356 hits, banner match |
| `"/v1/chat/completions"` | 225 hits, banner-level path leak |
| `"/v1/models"` | 216 hits, banner-level path leak |
| `http.html:"vllm"` | 188 hits, vLLM in HTML body |
| `http.html:"llama.cpp"` | 81 hits, llama.cpp in HTML |
| `"sglang"` | 60 hits, SGLang structured-generation server, OpenAI-compat |
| `"koboldcpp"` | 59 hits, KoboldCpp banner (all ports) |
| `"koboldcpp" port:5001` | 54 hits, KoboldCpp default port |
| `("koboldcpp" OR "koboldai")` | 47 hits, grouped OR catches AI Horde workers (unparenthesized breaks) |
| `"koboldai"` | 46 hits, KoboldAI web UI |
| `"Seldon"` | 33 hits, Seldon Core model deployment (k8s) |
| `http.html:"lm studio"` | 173 hits, LM Studio in HTML body (best LM Studio fingerprint) |
| `port:1234 "model"` | 71 hits, LM Studio default port with model term |
| `http.html:"sglang"` | 74 hits, SGLang in HTML body |
| `http.html:"seldon"` | 20 hits, Seldon in HTML body |
| `http.title:"Seldon"` | 10 hits, Seldon title match |
| `"LM Studio"` | 12 hits, LM Studio banner match |
| `http.html:"nvidia nim"` | 12 hits, NVIDIA NIM microservices in HTML |
| `http.html:"/v1/embeddings"` | 90 hits, embeddings path in HTML |
| `"/v1/embeddings"` | 8 hits, embeddings path banner leak |
| `"Triton Inference Server"` | 7 hits, NVIDIA Triton (use exact phrase; bare "Triton" returns 1,809 polluted) |
| `"lmdeploy"` | 5 hits, InternLM LMDeploy engine |
| `"vLLM" port:8000` | 2 hits, vLLM on default port |
| `port:8000 "openai" "model"` | 1 hit, OpenAI-compat on 8000 with model list |
| `http.html:"GPT4All"` | 2 hits, GPT4All in HTML body |
| `"llama" "completion"` | 2 hits, llama completion term combo (no port) |
| `"GPT4All"` | 1 hit, GPT4All desktop server banner |
| `"NVIDIA NIM"` | 1 hit, NIM exact phrase (2026 deployments still sparse on public internet) |
| `"aphrodite"` | 362 hits, ⚠️ bare term is Greek-mythology noise, not the vLLM fork |
| `"Aphrodite Engine"` | 1 hit, exact phrase (specific-but-rare) |

**Canonical query recommendation:** For OpenAI-compatible inference discovery, `http.html:"/v1/chat/completions"` (6,238) is the best single query, it catches every server emulating the OpenAI API surface regardless of underlying implementation. Pair with `http.html:"/v1/models"` for a narrow overlap.

```
GET /v1/models HTTP/1.1  {"object":"list","data":[{"id":"meta-llama/Llama-3.1-70B-Instruct",
  "object":"model","created":1713300000,"owned_by":"vllm"}]}
```
Typical vLLM response on an exposed port. Model name reveals what's hosted; `/v1/chat/completions` on the same port is reachable with no auth.

## Embedding / Reranking

| Shodan Query | Notes |
|---|---|
| `http.html:"TEI"` | 332 hits, TEI in HTML (best TEI fingerprint) |
| `http.html:"jina"` | 83 hits, Jina in HTML |
| `http.html:"sentence-transformers"` | 31 hits, sentence-transformers in HTML |
| `"text-embeddings-inference"` | 5 hits, TEI banner match |
| `"sentence-transformers"` | 5 hits, banner match |
| `"Jina" "embeddings"` | 4 hits, Jina banner + term |
| `"Jina" "embeddings" port:8080` | 2 hits, Jina on default port |
| `"infinity" "embedding"` | 1 hit, Infinity embedding server |
| `"Cohere"` | 1,603 hits, bare brand name, contaminated by SaaS references / unrelated docs |

**Pollution flagged:** `http.html:"infinity"` alone returns **7,794 hits**, but `"infinity" "embedding"` collapses to 1 hit. "Infinity" is a generic English word polluting 7,793 unrelated hits. Do not use `http.html:"infinity"` as a fingerprint.

**Cohere note:** Cohere's rerank is primarily a cloud API product; self-hosted rerank instances are rare on the public internet. Bare `"Cohere"` at 1,603 is brand-name noise, not server fingerprints, narrow before trusting.

## Audio / Speech / Vision Inference

| Shodan Query | Notes |
|---|---|
| `http.title:"Whisper"` | 444 hits, Whisper ASR web UI |
| `http.html:"faster-whisper"` | 190 hits, faster-whisper in HTML |
| `http.title:"Bark"` | 120 hits, Suno Bark text-to-audio |
| `http.title:"Piper"` | 103 hits, Piper TTS title |
| `http.html:"coqui"` | 55 hits, Coqui in HTML |
| `"faster-whisper"` | 32 hits, faster-whisper banner |
| `"PaddleOCR"` | 28 hits, PaddleOCR service (banner form) |
| `"whisper.cpp" "/inference"` | 16 hits, whisper.cpp HTTP server, free ASR compute |
| `"coqui" "tts"` | 13 hits, Coqui TTS banner + term |
| `"piper" "tts"` | 8 hits, Piper neural TTS (RPi/edge) |
| `"vocode"` | 4 hits, Vocode voice-agent framework |
| `http.html:"vocode"` | 2 hits, Vocode in HTML |
| `"paddleocr" port:8080` | 1 hit, PaddleOCR (default port, narrow) |
