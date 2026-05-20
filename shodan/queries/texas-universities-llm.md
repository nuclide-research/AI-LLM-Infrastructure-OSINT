# Texas University LLM Infrastructure — Shodan Query Catalog

_Scoped catalog for finding exposed LLM/AI infrastructure on Texas university `.edu` domains.  Covers 66 institutions across the UT, A&M, Texas State, UH, Tech systems plus independents and private universities._

**Authoring note:** queries use vendor-unique signatures (ports, specific titles, niche paths) not coarse body matches. Hostname batches keep Shodan queries under ~1000 chars.

---

## Hostname Groups

### TX-PUB-1 — UT System + Health (11)

```
(hostname:utexas.edu OR hostname:utdallas.edu OR hostname:uta.edu OR hostname:utsa.edu OR hostname:utep.edu OR hostname:utrgv.edu OR hostname:utpb.edu OR hostname:uttyler.edu OR hostname:utsouthwestern.edu OR hostname:uth.edu OR hostname:uthscsa.edu)
```

### TX-PUB-2 — Texas A&M System (10)

```
(hostname:tamu.edu OR hostname:tamuc.edu OR hostname:tamucc.edu OR hostname:tamuk.edu OR hostname:tamusa.edu OR hostname:tamut.edu OR hostname:tamiu.edu OR hostname:pvamu.edu OR hostname:tarleton.edu OR hostname:wtamu.edu)
```

### TX-PUB-3 — Texas State / UH / Tech / Other Public (16)

```
(hostname:txstate.edu OR hostname:lamar.edu OR hostname:shsu.edu OR hostname:sulross.edu OR hostname:uh.edu OR hostname:uhcl.edu OR hostname:uhd.edu OR hostname:uhv.edu OR hostname:ttu.edu OR hostname:ttuhsc.edu OR hostname:angelo.edu OR hostname:sfasu.edu OR hostname:msutexas.edu OR hostname:tsu.edu OR hostname:twu.edu OR hostname:unt.edu)
```

### TX-PRIV-1 — Major Private (10)

```
(hostname:rice.edu OR hostname:baylor.edu OR hostname:smu.edu OR hostname:tcu.edu OR hostname:trinity.edu OR hostname:stmarytx.edu OR hostname:acu.edu OR hostname:udallas.edu OR hostname:uiw.edu OR hostname:stedwards.edu)
```

### TX-PRIV-2 — Small Private + HBCU (16)

```
(hostname:hsutx.edu OR hostname:hputx.edu OR hostname:lcu.edu OR hostname:ollusa.edu OR hostname:schreiner.edu OR hostname:tlu.edu OR hostname:southwestern.edu OR hostname:htu.edu OR hostname:jarvis.edu OR hostname:wiley.edu OR hostname:pqc.edu OR hostname:swau.edu OR hostname:umhb.edu OR hostname:letu.edu OR hostname:dbu.edu OR hostname:hbu.edu)
```

---

## Per-Service Queries

### 1. Ollama (port 11434)

Local LLM runtime. Default unauth, exposes `/api/tags`, `/api/generate` (RCE-adjacent via model pull).

```
port:11434 (hostname:utexas.edu OR hostname:utdallas.edu OR hostname:uta.edu OR hostname:utsa.edu OR hostname:utep.edu OR hostname:utrgv.edu OR hostname:utpb.edu OR hostname:uttyler.edu OR hostname:utsouthwestern.edu OR hostname:uth.edu OR hostname:uthscsa.edu)
port:11434 (hostname:tamu.edu OR hostname:tamuc.edu OR hostname:tamucc.edu OR hostname:tamuk.edu OR hostname:tamusa.edu OR hostname:tamut.edu OR hostname:tamiu.edu OR hostname:pvamu.edu OR hostname:tarleton.edu OR hostname:wtamu.edu)
port:11434 (hostname:txstate.edu OR hostname:lamar.edu OR hostname:shsu.edu OR hostname:sulross.edu OR hostname:uh.edu OR hostname:uhcl.edu OR hostname:uhd.edu OR hostname:uhv.edu OR hostname:ttu.edu OR hostname:ttuhsc.edu OR hostname:angelo.edu OR hostname:sfasu.edu OR hostname:msutexas.edu OR hostname:tsu.edu OR hostname:twu.edu OR hostname:unt.edu)
port:11434 (hostname:rice.edu OR hostname:baylor.edu OR hostname:smu.edu OR hostname:tcu.edu OR hostname:trinity.edu OR hostname:stmarytx.edu OR hostname:acu.edu OR hostname:udallas.edu OR hostname:uiw.edu OR hostname:stedwards.edu)
port:11434 (hostname:hsutx.edu OR hostname:hputx.edu OR hostname:lcu.edu OR hostname:ollusa.edu OR hostname:schreiner.edu OR hostname:tlu.edu OR hostname:southwestern.edu OR hostname:htu.edu OR hostname:jarvis.edu OR hostname:wiley.edu OR hostname:pqc.edu OR hostname:swau.edu OR hostname:umhb.edu OR hostname:letu.edu OR hostname:dbu.edu OR hostname:hbu.edu)
```

Banner variant (catches 11434 + reverse-proxied :443/:80 Ollama):
```
"Ollama is running" (hostname:utexas.edu OR hostname:tamu.edu OR hostname:rice.edu OR hostname:utdallas.edu OR hostname:uta.edu OR hostname:utsa.edu OR hostname:utep.edu OR hostname:utrgv.edu OR hostname:utpb.edu OR hostname:uttyler.edu OR hostname:utsouthwestern.edu)
```

### 2. Open WebUI (Ollama frontend)

```
http.title:"Open WebUI" (hostname:utexas.edu OR hostname:utdallas.edu OR hostname:uta.edu OR hostname:utsa.edu OR hostname:utep.edu OR hostname:utrgv.edu OR hostname:utpb.edu OR hostname:uttyler.edu OR hostname:utsouthwestern.edu OR hostname:uth.edu OR hostname:uthscsa.edu)
http.title:"Open WebUI" (hostname:tamu.edu OR hostname:tamuc.edu OR hostname:tamucc.edu OR hostname:tamuk.edu OR hostname:tamusa.edu OR hostname:tamut.edu OR hostname:tamiu.edu OR hostname:pvamu.edu OR hostname:tarleton.edu OR hostname:wtamu.edu)
http.title:"Open WebUI" (hostname:txstate.edu OR hostname:lamar.edu OR hostname:shsu.edu OR hostname:sulross.edu OR hostname:uh.edu OR hostname:uhcl.edu OR hostname:uhd.edu OR hostname:uhv.edu OR hostname:ttu.edu OR hostname:ttuhsc.edu OR hostname:angelo.edu OR hostname:sfasu.edu OR hostname:msutexas.edu OR hostname:tsu.edu OR hostname:twu.edu OR hostname:unt.edu)
http.title:"Open WebUI" (hostname:rice.edu OR hostname:baylor.edu OR hostname:smu.edu OR hostname:tcu.edu OR hostname:trinity.edu OR hostname:stmarytx.edu OR hostname:acu.edu OR hostname:udallas.edu OR hostname:uiw.edu OR hostname:stedwards.edu)
http.title:"Open WebUI" (hostname:hsutx.edu OR hostname:hputx.edu OR hostname:lcu.edu OR hostname:ollusa.edu OR hostname:schreiner.edu OR hostname:tlu.edu OR hostname:southwestern.edu OR hostname:htu.edu OR hostname:jarvis.edu OR hostname:wiley.edu OR hostname:pqc.edu OR hostname:swau.edu OR hostname:umhb.edu OR hostname:letu.edu OR hostname:dbu.edu OR hostname:hbu.edu)
```

### 3. vLLM / OpenAI-Compatible Inference (port 8000)

```
port:8000 "/v1/models" (hostname:utexas.edu OR hostname:utdallas.edu OR hostname:uta.edu OR hostname:utsa.edu OR hostname:utep.edu OR hostname:utrgv.edu OR hostname:utpb.edu OR hostname:uttyler.edu OR hostname:utsouthwestern.edu OR hostname:uth.edu OR hostname:uthscsa.edu)
port:8000 "/v1/models" (hostname:tamu.edu OR hostname:tamuc.edu OR hostname:tamucc.edu OR hostname:tamuk.edu OR hostname:tamusa.edu OR hostname:tamut.edu OR hostname:tamiu.edu OR hostname:pvamu.edu OR hostname:tarleton.edu OR hostname:wtamu.edu)
port:8000 "/v1/models" (hostname:txstate.edu OR hostname:lamar.edu OR hostname:shsu.edu OR hostname:sulross.edu OR hostname:uh.edu OR hostname:uhcl.edu OR hostname:uhd.edu OR hostname:uhv.edu OR hostname:ttu.edu OR hostname:ttuhsc.edu OR hostname:angelo.edu OR hostname:sfasu.edu OR hostname:msutexas.edu OR hostname:tsu.edu OR hostname:twu.edu OR hostname:unt.edu)
port:8000 "/v1/models" (hostname:rice.edu OR hostname:baylor.edu OR hostname:smu.edu OR hostname:tcu.edu OR hostname:trinity.edu OR hostname:stmarytx.edu OR hostname:acu.edu OR hostname:udallas.edu OR hostname:uiw.edu OR hostname:stedwards.edu)
```

vLLM-specific (engine string):
```
"vllm" "/v1/models" (hostname:utexas.edu OR hostname:tamu.edu OR hostname:rice.edu OR hostname:ttu.edu OR hostname:uh.edu OR hostname:unt.edu OR hostname:utdallas.edu OR hostname:utsa.edu)
```

### 4. LiteLLM Proxy

```
http.title:"LiteLLM" (hostname:utexas.edu OR hostname:utdallas.edu OR hostname:uta.edu OR hostname:utsa.edu OR hostname:utep.edu OR hostname:utrgv.edu OR hostname:utpb.edu OR hostname:uttyler.edu OR hostname:utsouthwestern.edu OR hostname:uth.edu OR hostname:uthscsa.edu)
http.title:"LiteLLM" (hostname:tamu.edu OR hostname:tamuc.edu OR hostname:tamucc.edu OR hostname:tamuk.edu OR hostname:tamusa.edu OR hostname:tamut.edu OR hostname:tamiu.edu OR hostname:pvamu.edu OR hostname:tarleton.edu OR hostname:wtamu.edu)
http.title:"LiteLLM" (hostname:rice.edu OR hostname:baylor.edu OR hostname:smu.edu OR hostname:tcu.edu OR hostname:trinity.edu OR hostname:stmarytx.edu OR hostname:acu.edu OR hostname:udallas.edu OR hostname:uiw.edu OR hostname:stedwards.edu)
```

Path variant (`/health/liveliness` is LiteLLM-specific):
```
http.html:"/health/liveliness" (hostname:utexas.edu OR hostname:tamu.edu OR hostname:rice.edu OR hostname:ttu.edu OR hostname:uh.edu OR hostname:unt.edu)
```

### 5. AnythingLLM

```
http.title:"AnythingLLM" (hostname:utexas.edu OR hostname:utdallas.edu OR hostname:uta.edu OR hostname:utsa.edu OR hostname:utep.edu OR hostname:utrgv.edu OR hostname:utpb.edu OR hostname:uttyler.edu OR hostname:utsouthwestern.edu OR hostname:uth.edu OR hostname:uthscsa.edu)
http.title:"AnythingLLM" (hostname:tamu.edu OR hostname:tamuc.edu OR hostname:tamucc.edu OR hostname:tamuk.edu OR hostname:tamusa.edu OR hostname:tamut.edu OR hostname:tamiu.edu OR hostname:pvamu.edu OR hostname:tarleton.edu OR hostname:wtamu.edu)
http.title:"AnythingLLM" (hostname:rice.edu OR hostname:baylor.edu OR hostname:smu.edu OR hostname:tcu.edu OR hostname:trinity.edu OR hostname:stmarytx.edu OR hostname:acu.edu OR hostname:udallas.edu OR hostname:uiw.edu OR hostname:stedwards.edu)
```

### 6. Flowise (low-code LLM orchestration)

```
http.title:"Flowise" (hostname:utexas.edu OR hostname:utdallas.edu OR hostname:uta.edu OR hostname:utsa.edu OR hostname:utep.edu OR hostname:utrgv.edu OR hostname:utpb.edu OR hostname:uttyler.edu OR hostname:utsouthwestern.edu OR hostname:uth.edu OR hostname:uthscsa.edu)
http.title:"Flowise" (hostname:tamu.edu OR hostname:tamuc.edu OR hostname:tamucc.edu OR hostname:tamuk.edu OR hostname:tamusa.edu OR hostname:tamut.edu OR hostname:tamiu.edu OR hostname:pvamu.edu OR hostname:tarleton.edu OR hostname:wtamu.edu)
http.title:"Flowise" (hostname:rice.edu OR hostname:baylor.edu OR hostname:smu.edu OR hostname:tcu.edu OR hostname:trinity.edu OR hostname:stmarytx.edu OR hostname:acu.edu OR hostname:udallas.edu OR hostname:uiw.edu OR hostname:stedwards.edu)
```

### 7. Langflow

```
http.title:"Langflow" (hostname:utexas.edu OR hostname:utdallas.edu OR hostname:uta.edu OR hostname:utsa.edu OR hostname:utep.edu OR hostname:utrgv.edu OR hostname:utpb.edu OR hostname:uttyler.edu OR hostname:utsouthwestern.edu OR hostname:uth.edu OR hostname:uthscsa.edu)
http.title:"Langflow" (hostname:tamu.edu OR hostname:tamuc.edu OR hostname:tamucc.edu OR hostname:tamuk.edu OR hostname:tamusa.edu OR hostname:tamut.edu OR hostname:tamiu.edu OR hostname:pvamu.edu OR hostname:tarleton.edu OR hostname:wtamu.edu)
http.title:"Langflow" (hostname:rice.edu OR hostname:baylor.edu OR hostname:smu.edu OR hostname:tcu.edu OR hostname:trinity.edu OR hostname:stmarytx.edu OR hostname:acu.edu OR hostname:udallas.edu OR hostname:uiw.edu OR hostname:stedwards.edu)
```

### 8. Dify

```
http.title:"Dify" (hostname:utexas.edu OR hostname:utdallas.edu OR hostname:uta.edu OR hostname:utsa.edu OR hostname:utep.edu OR hostname:utrgv.edu OR hostname:utpb.edu OR hostname:uttyler.edu OR hostname:utsouthwestern.edu OR hostname:uth.edu OR hostname:uthscsa.edu)
http.title:"Dify" (hostname:tamu.edu OR hostname:tamuc.edu OR hostname:tamucc.edu OR hostname:tamuk.edu OR hostname:tamusa.edu OR hostname:tamut.edu OR hostname:tamiu.edu OR hostname:pvamu.edu OR hostname:tarleton.edu OR hostname:wtamu.edu)
http.title:"Dify" (hostname:rice.edu OR hostname:baylor.edu OR hostname:smu.edu OR hostname:tcu.edu OR hostname:trinity.edu OR hostname:stmarytx.edu OR hostname:acu.edu OR hostname:udallas.edu OR hostname:uiw.edu OR hostname:stedwards.edu)
```

### 9. Text Generation WebUI (Oobabooga)

```
http.title:"Text generation web UI" (hostname:utexas.edu OR hostname:utdallas.edu OR hostname:uta.edu OR hostname:utsa.edu OR hostname:utep.edu OR hostname:utrgv.edu OR hostname:utpb.edu OR hostname:uttyler.edu OR hostname:utsouthwestern.edu OR hostname:uth.edu OR hostname:uthscsa.edu)
http.title:"Text generation web UI" (hostname:tamu.edu OR hostname:tamuc.edu OR hostname:tamucc.edu OR hostname:tamuk.edu OR hostname:tamusa.edu OR hostname:tamut.edu OR hostname:tamiu.edu OR hostname:pvamu.edu OR hostname:tarleton.edu OR hostname:wtamu.edu)
http.title:"Text generation web UI" (hostname:rice.edu OR hostname:baylor.edu OR hostname:smu.edu OR hostname:tcu.edu OR hostname:trinity.edu OR hostname:stmarytx.edu OR hostname:acu.edu OR hostname:udallas.edu OR hostname:uiw.edu OR hostname:stedwards.edu)
```

### 10. Lobe Chat / NextChat / LibreChat

```
http.title:"Lobe Chat" (hostname:utexas.edu OR hostname:tamu.edu OR hostname:rice.edu OR hostname:utdallas.edu OR hostname:uta.edu OR hostname:utsa.edu OR hostname:ttu.edu OR hostname:uh.edu OR hostname:unt.edu)
http.title:"NextChat" (hostname:utexas.edu OR hostname:tamu.edu OR hostname:rice.edu OR hostname:utdallas.edu OR hostname:uta.edu OR hostname:utsa.edu OR hostname:ttu.edu OR hostname:uh.edu OR hostname:unt.edu)
http.title:"LibreChat" (hostname:utexas.edu OR hostname:tamu.edu OR hostname:rice.edu OR hostname:utdallas.edu OR hostname:uta.edu OR hostname:utsa.edu OR hostname:ttu.edu OR hostname:uh.edu OR hostname:unt.edu)
```

### 11. NewAPI / OneAPI (Chinese OSS OpenAI-compat gateway)

```
http.title:"new-api" (hostname:utexas.edu OR hostname:tamu.edu OR hostname:rice.edu OR hostname:utdallas.edu OR hostname:uta.edu OR hostname:utsa.edu OR hostname:ttu.edu OR hostname:uh.edu OR hostname:unt.edu)
http.title:"One API" (hostname:utexas.edu OR hostname:tamu.edu OR hostname:rice.edu OR hostname:utdallas.edu OR hostname:uta.edu OR hostname:utsa.edu OR hostname:ttu.edu OR hostname:uh.edu OR hostname:unt.edu)
```

### 12. MLflow

Research-heavy at universities. **Note:** aimap enumMLflow appends a hardcoded CVE — version-verify before treating as exploitable.

```
http.title:"MLflow" (hostname:utexas.edu OR hostname:utdallas.edu OR hostname:uta.edu OR hostname:utsa.edu OR hostname:utep.edu OR hostname:utrgv.edu OR hostname:utpb.edu OR hostname:uttyler.edu OR hostname:utsouthwestern.edu OR hostname:uth.edu OR hostname:uthscsa.edu)
http.title:"MLflow" (hostname:tamu.edu OR hostname:tamuc.edu OR hostname:tamucc.edu OR hostname:tamuk.edu OR hostname:tamusa.edu OR hostname:tamut.edu OR hostname:tamiu.edu OR hostname:pvamu.edu OR hostname:tarleton.edu OR hostname:wtamu.edu)
http.title:"MLflow" (hostname:rice.edu OR hostname:baylor.edu OR hostname:smu.edu OR hostname:tcu.edu OR hostname:trinity.edu OR hostname:stmarytx.edu OR hostname:acu.edu OR hostname:udallas.edu OR hostname:uiw.edu OR hostname:stedwards.edu)
```

### 13. Langfuse / Phoenix / W&B (LLM observability)

```
http.title:"Langfuse" (hostname:utexas.edu OR hostname:tamu.edu OR hostname:rice.edu OR hostname:ttu.edu OR hostname:uh.edu OR hostname:unt.edu OR hostname:utdallas.edu OR hostname:utsa.edu)
http.title:"Phoenix" (hostname:utexas.edu OR hostname:tamu.edu OR hostname:rice.edu OR hostname:ttu.edu OR hostname:uh.edu OR hostname:unt.edu OR hostname:utdallas.edu OR hostname:utsa.edu)
"Weights & Biases" (hostname:utexas.edu OR hostname:tamu.edu OR hostname:rice.edu OR hostname:ttu.edu OR hostname:uh.edu OR hostname:unt.edu OR hostname:utdallas.edu OR hostname:utsa.edu)
```

### 14. JupyterHub / JupyterLab (LLM workflow common)

JupyterHub auth-on-default since v1.x; JupyterLab on bare port 8888 from `jupyter lab --ip 0.0.0.0` remains the unauth surface.

```
http.title:"JupyterHub" (hostname:utexas.edu OR hostname:utdallas.edu OR hostname:uta.edu OR hostname:utsa.edu OR hostname:utep.edu OR hostname:utrgv.edu OR hostname:utpb.edu OR hostname:uttyler.edu OR hostname:utsouthwestern.edu OR hostname:uth.edu OR hostname:uthscsa.edu)
http.title:"JupyterHub" (hostname:tamu.edu OR hostname:tamuc.edu OR hostname:tamucc.edu OR hostname:tamuk.edu OR hostname:tamusa.edu OR hostname:tamut.edu OR hostname:tamiu.edu OR hostname:pvamu.edu OR hostname:tarleton.edu OR hostname:wtamu.edu)
http.title:"JupyterHub" (hostname:txstate.edu OR hostname:lamar.edu OR hostname:shsu.edu OR hostname:sulross.edu OR hostname:uh.edu OR hostname:uhcl.edu OR hostname:uhd.edu OR hostname:uhv.edu OR hostname:ttu.edu OR hostname:ttuhsc.edu OR hostname:angelo.edu OR hostname:sfasu.edu OR hostname:msutexas.edu OR hostname:tsu.edu OR hostname:twu.edu OR hostname:unt.edu)
http.title:"JupyterHub" (hostname:rice.edu OR hostname:baylor.edu OR hostname:smu.edu OR hostname:tcu.edu OR hostname:trinity.edu OR hostname:stmarytx.edu OR hostname:acu.edu OR hostname:udallas.edu OR hostname:uiw.edu OR hostname:stedwards.edu)
http.title:"JupyterLab" (hostname:utexas.edu OR hostname:tamu.edu OR hostname:rice.edu OR hostname:utdallas.edu OR hostname:uta.edu OR hostname:utsa.edu OR hostname:ttu.edu OR hostname:uh.edu OR hostname:unt.edu OR hostname:baylor.edu OR hostname:smu.edu OR hostname:tcu.edu OR hostname:utsouthwestern.edu OR hostname:ttuhsc.edu)
```

### 15. Streamlit (common LLM demo wrapper)

```
http.title:"Streamlit" (hostname:utexas.edu OR hostname:utdallas.edu OR hostname:uta.edu OR hostname:utsa.edu OR hostname:utep.edu OR hostname:utrgv.edu OR hostname:utpb.edu OR hostname:uttyler.edu OR hostname:utsouthwestern.edu OR hostname:uth.edu OR hostname:uthscsa.edu)
http.title:"Streamlit" (hostname:tamu.edu OR hostname:tamuc.edu OR hostname:tamucc.edu OR hostname:tamuk.edu OR hostname:tamusa.edu OR hostname:tamut.edu OR hostname:tamiu.edu OR hostname:pvamu.edu OR hostname:tarleton.edu OR hostname:wtamu.edu)
http.title:"Streamlit" (hostname:rice.edu OR hostname:baylor.edu OR hostname:smu.edu OR hostname:tcu.edu OR hostname:trinity.edu OR hostname:stmarytx.edu OR hostname:acu.edu OR hostname:udallas.edu OR hostname:uiw.edu OR hostname:stedwards.edu)
```

### 16. Gradio (LLM/ML demo wrapper)

```
http.html:"gradio-app" (hostname:utexas.edu OR hostname:utdallas.edu OR hostname:uta.edu OR hostname:utsa.edu OR hostname:utep.edu OR hostname:utrgv.edu OR hostname:utpb.edu OR hostname:uttyler.edu OR hostname:utsouthwestern.edu OR hostname:uth.edu OR hostname:uthscsa.edu)
http.html:"gradio-app" (hostname:tamu.edu OR hostname:tamuc.edu OR hostname:tamucc.edu OR hostname:tamuk.edu OR hostname:tamusa.edu OR hostname:tamut.edu OR hostname:tamiu.edu OR hostname:pvamu.edu OR hostname:tarleton.edu OR hostname:wtamu.edu)
http.html:"gradio-app" (hostname:rice.edu OR hostname:baylor.edu OR hostname:smu.edu OR hostname:tcu.edu OR hostname:trinity.edu OR hostname:stmarytx.edu OR hostname:acu.edu OR hostname:udallas.edu OR hostname:uiw.edu OR hostname:stedwards.edu)
```

### 17. ChromaDB

```
port:8000 "chroma" (hostname:utexas.edu OR hostname:tamu.edu OR hostname:rice.edu OR hostname:ttu.edu OR hostname:uh.edu OR hostname:unt.edu OR hostname:utdallas.edu OR hostname:utsa.edu OR hostname:baylor.edu)
http.title:"ChromaDB" (hostname:utexas.edu OR hostname:tamu.edu OR hostname:rice.edu OR hostname:ttu.edu OR hostname:uh.edu OR hostname:unt.edu OR hostname:utdallas.edu OR hostname:utsa.edu OR hostname:baylor.edu)
```

### 18. Qdrant (vector DB)

```
port:6333 (hostname:utexas.edu OR hostname:utdallas.edu OR hostname:uta.edu OR hostname:utsa.edu OR hostname:utep.edu OR hostname:utrgv.edu OR hostname:utpb.edu OR hostname:uttyler.edu OR hostname:utsouthwestern.edu OR hostname:uth.edu OR hostname:uthscsa.edu)
port:6333 (hostname:tamu.edu OR hostname:tamuc.edu OR hostname:tamucc.edu OR hostname:tamuk.edu OR hostname:tamusa.edu OR hostname:tamut.edu OR hostname:tamiu.edu OR hostname:pvamu.edu OR hostname:tarleton.edu OR hostname:wtamu.edu)
port:6333 (hostname:rice.edu OR hostname:baylor.edu OR hostname:smu.edu OR hostname:tcu.edu OR hostname:trinity.edu OR hostname:stmarytx.edu OR hostname:acu.edu OR hostname:udallas.edu OR hostname:uiw.edu OR hostname:stedwards.edu)
```

### 19. Weaviate (vector DB)

```
port:8080 "weaviate" (hostname:utexas.edu OR hostname:tamu.edu OR hostname:rice.edu OR hostname:ttu.edu OR hostname:uh.edu OR hostname:unt.edu OR hostname:utdallas.edu OR hostname:utsa.edu OR hostname:baylor.edu)
http.html:"/v1/meta" "weaviate" (hostname:utexas.edu OR hostname:tamu.edu OR hostname:rice.edu OR hostname:ttu.edu OR hostname:uh.edu OR hostname:unt.edu OR hostname:utdallas.edu OR hostname:utsa.edu OR hostname:baylor.edu)
```

### 20. Milvus (vector DB — common with academic stacks)

```
port:19530 (hostname:utexas.edu OR hostname:tamu.edu OR hostname:rice.edu OR hostname:ttu.edu OR hostname:uh.edu OR hostname:unt.edu OR hostname:utdallas.edu OR hostname:utsa.edu OR hostname:baylor.edu OR hostname:utsouthwestern.edu OR hostname:ttuhsc.edu)
```

### 21. NVIDIA Triton Inference Server

```
http.title:"Triton Inference" (hostname:utexas.edu OR hostname:tamu.edu OR hostname:rice.edu OR hostname:ttu.edu OR hostname:uh.edu OR hostname:unt.edu OR hostname:utdallas.edu OR hostname:utsa.edu OR hostname:baylor.edu)
port:8001 "triton" (hostname:utexas.edu OR hostname:tamu.edu OR hostname:rice.edu OR hostname:ttu.edu OR hostname:uh.edu OR hostname:unt.edu OR hostname:utdallas.edu OR hostname:utsa.edu)
```

### 22. NVIDIA DCGM (GPU compute dashboard)

```
"DCGM" port:9400 (hostname:utexas.edu OR hostname:utdallas.edu OR hostname:uta.edu OR hostname:utsa.edu OR hostname:utep.edu OR hostname:utrgv.edu OR hostname:utpb.edu OR hostname:uttyler.edu OR hostname:utsouthwestern.edu OR hostname:uth.edu OR hostname:uthscsa.edu)
"DCGM" port:9400 (hostname:tamu.edu OR hostname:tamuc.edu OR hostname:tamucc.edu OR hostname:tamuk.edu OR hostname:tamusa.edu OR hostname:tamut.edu OR hostname:tamiu.edu OR hostname:pvamu.edu OR hostname:tarleton.edu OR hostname:wtamu.edu)
"DCGM" port:9400 (hostname:rice.edu OR hostname:baylor.edu OR hostname:smu.edu OR hostname:tcu.edu OR hostname:trinity.edu OR hostname:stmarytx.edu OR hostname:acu.edu OR hostname:udallas.edu OR hostname:uiw.edu OR hostname:stedwards.edu)
```

### 23. Ray Dashboard (distributed LLM training/inference)

```
port:8265 "Ray" (hostname:utexas.edu OR hostname:tamu.edu OR hostname:rice.edu OR hostname:ttu.edu OR hostname:uh.edu OR hostname:unt.edu OR hostname:utdallas.edu OR hostname:utsa.edu OR hostname:baylor.edu OR hostname:smu.edu)
http.title:"Ray Dashboard" (hostname:utexas.edu OR hostname:tamu.edu OR hostname:rice.edu OR hostname:ttu.edu OR hostname:uh.edu OR hostname:unt.edu OR hostname:utdallas.edu OR hostname:utsa.edu)
```

### 24. Whisper / Coqui TTS (audio AI)

```
http.title:"Whisper" (hostname:utexas.edu OR hostname:tamu.edu OR hostname:rice.edu OR hostname:utsouthwestern.edu OR hostname:ttuhsc.edu OR hostname:uth.edu OR hostname:uthscsa.edu OR hostname:unthsc.edu)
http.html:"coqui" (hostname:utexas.edu OR hostname:tamu.edu OR hostname:rice.edu OR hostname:ttu.edu OR hostname:uh.edu OR hostname:unt.edu OR hostname:utdallas.edu OR hostname:utsa.edu)
```

### 25. LocalAI / GPT4All / PrivateGPT

```
http.title:"LocalAI" (hostname:utexas.edu OR hostname:tamu.edu OR hostname:rice.edu OR hostname:ttu.edu OR hostname:uh.edu OR hostname:unt.edu OR hostname:utdallas.edu OR hostname:utsa.edu)
http.title:"PrivateGPT" (hostname:utexas.edu OR hostname:tamu.edu OR hostname:rice.edu OR hostname:ttu.edu OR hostname:uh.edu OR hostname:unt.edu OR hostname:utdallas.edu OR hostname:utsa.edu)
http.title:"GPT4All" (hostname:utexas.edu OR hostname:tamu.edu OR hostname:rice.edu OR hostname:ttu.edu OR hostname:uh.edu OR hostname:unt.edu OR hostname:utdallas.edu OR hostname:utsa.edu)
```

---

## Geo-Scoped Fallback Queries (state:TX + .edu)

For services hosted on cloud infra with .edu in hostname but not university-owned IP space, geo-restricted scans catch what the hostname approach misses:

```
state:TX hostname:.edu port:11434
state:TX hostname:.edu http.title:"Open WebUI"
state:TX hostname:.edu http.title:"MLflow"
state:TX hostname:.edu http.title:"JupyterHub"
state:TX hostname:.edu http.title:"AnythingLLM"
state:TX hostname:.edu http.title:"Flowise"
state:TX hostname:.edu port:6333
state:TX hostname:.edu port:8000 "/v1/models"
state:TX hostname:.edu "DCGM" port:9400
state:TX hostname:.edu http.html:"gradio-app"
```

---

## Per-University Direct Queries (Top 10 R1/R2)

For granular per-institution sweeps, the template `<service> hostname:<uni>`:

| University | Ollama | Open WebUI | MLflow | JupyterHub |
|------------|--------|------------|--------|------------|
| UT Austin | `port:11434 hostname:utexas.edu` | `http.title:"Open WebUI" hostname:utexas.edu` | `http.title:"MLflow" hostname:utexas.edu` | `http.title:"JupyterHub" hostname:utexas.edu` |
| Texas A&M | `port:11434 hostname:tamu.edu` | `http.title:"Open WebUI" hostname:tamu.edu` | `http.title:"MLflow" hostname:tamu.edu` | `http.title:"JupyterHub" hostname:tamu.edu` |
| Rice | `port:11434 hostname:rice.edu` | `http.title:"Open WebUI" hostname:rice.edu` | `http.title:"MLflow" hostname:rice.edu` | `http.title:"JupyterHub" hostname:rice.edu` |
| UH | `port:11434 hostname:uh.edu` | `http.title:"Open WebUI" hostname:uh.edu` | `http.title:"MLflow" hostname:uh.edu` | `http.title:"JupyterHub" hostname:uh.edu` |
| UT Dallas | `port:11434 hostname:utdallas.edu` | `http.title:"Open WebUI" hostname:utdallas.edu` | `http.title:"MLflow" hostname:utdallas.edu` | `http.title:"JupyterHub" hostname:utdallas.edu` |
| UT Arlington | `port:11434 hostname:uta.edu` | `http.title:"Open WebUI" hostname:uta.edu` | `http.title:"MLflow" hostname:uta.edu` | `http.title:"JupyterHub" hostname:uta.edu` |
| UT San Antonio | `port:11434 hostname:utsa.edu` | `http.title:"Open WebUI" hostname:utsa.edu` | `http.title:"MLflow" hostname:utsa.edu` | `http.title:"JupyterHub" hostname:utsa.edu` |
| Texas Tech | `port:11434 hostname:ttu.edu` | `http.title:"Open WebUI" hostname:ttu.edu` | `http.title:"MLflow" hostname:ttu.edu` | `http.title:"JupyterHub" hostname:ttu.edu` |
| UNT | `port:11434 hostname:unt.edu` | `http.title:"Open WebUI" hostname:unt.edu` | `http.title:"MLflow" hostname:unt.edu` | `http.title:"JupyterHub" hostname:unt.edu` |
| Baylor | `port:11434 hostname:baylor.edu` | `http.title:"Open WebUI" hostname:baylor.edu` | `http.title:"MLflow" hostname:baylor.edu` | `http.title:"JupyterHub" hostname:baylor.edu` |
| SMU | `port:11434 hostname:smu.edu` | `http.title:"Open WebUI" hostname:smu.edu` | `http.title:"MLflow" hostname:smu.edu` | `http.title:"JupyterHub" hostname:smu.edu` |
| TCU | `port:11434 hostname:tcu.edu` | `http.title:"Open WebUI" hostname:tcu.edu` | `http.title:"MLflow" hostname:tcu.edu` | `http.title:"JupyterHub" hostname:tcu.edu` |

Replace `<uni>` with any of the 66 domains in the Hostname Groups section above.

---

## Health-Sciences-Specific Queries (HIPAA-relevant)

UT Southwestern, UT Health Houston, UT Health San Antonio, Texas Tech HSC, UNT Health Science, A&M Health Science deploy clinical-research AI — elevated impact if exposed.

```
(hostname:utsouthwestern.edu OR hostname:uth.edu OR hostname:uthscsa.edu OR hostname:ttuhsc.edu OR hostname:unthsc.edu OR hostname:tamu.edu) (port:11434 OR http.title:"Open WebUI" OR http.title:"MLflow" OR http.title:"AnythingLLM" OR http.html:"gradio-app" OR port:8000 "/v1/models")
```

---

## Pivot Queries

Once a confirmed host is identified, pivot via:

```
ssl.cert.subject.cn:<uni>.edu
asn:<uni-asn>
net:<uni-cidr>
```

Major Texas .edu ASNs (operator-owned, not cloud):
- UT Austin: `AS3994`
- Texas A&M: `AS18458`, `AS6585`
- Rice: `AS40009`
- UNT: `AS17175`
- UH: `AS40220`
- Texas Tech: `AS18380`

Stacked-exposure sweep on known university IP space:
```
asn:AS3994 (port:11434 OR port:6333 OR port:8000 OR port:9400 OR http.title:"Open WebUI" OR http.title:"MLflow")
asn:AS18458 (port:11434 OR port:6333 OR port:8000 OR port:9400 OR http.title:"Open WebUI" OR http.title:"MLflow")
asn:AS40009 (port:11434 OR port:6333 OR port:8000 OR port:9400 OR http.title:"Open WebUI" OR http.title:"MLflow")
```

---

## Notes & Honest Negative Space

- **Hostname substring matching:** Shodan's `hostname:` is a substring filter, so `hostname:utexas.edu` matches `cs.utexas.edu`, `gpu.utexas.edu`, etc. No wildcards needed.
- **Cloud-hosted shadow IT:** University labs often deploy on personal AWS/GCP/Hetzner accounts with no .edu DNS. The hostname approach misses these. Cross-reference with `org:"University of Texas"` etc. and cert pivots on confirmed hosts.
- **VPN-gated services:** Many university LLM deployments sit behind campus VPN — Shodan won't see them. Surface area here is only what's publicly indexable.
- **Auth-on-default check:** A 200 to the service entry point is platform identity, not auth posture (Insight #16). Verify with a data-layer probe (`/api/tags`, `/v1/models`, `/api/ollama/api/tags`).
- **JupyterHub auth-on-default:** Per Insight from survey 18, modern JupyterHub enforces auth — university hits are inventory/version disclosure, not unauth access. JupyterLab on bare port 8888 is the unauth surface.

---

## Domain Reference (full list)

**UT System (11):** utexas.edu, utdallas.edu, uta.edu, utsa.edu, utep.edu, utrgv.edu, utpb.edu, uttyler.edu, utsouthwestern.edu, uth.edu, uthscsa.edu

**Texas A&M System (10):** tamu.edu, tamuc.edu, tamucc.edu, tamuk.edu, tamusa.edu, tamut.edu, tamiu.edu, pvamu.edu, tarleton.edu, wtamu.edu

**Texas State System (4):** txstate.edu, lamar.edu, shsu.edu, sulross.edu

**UH System (4):** uh.edu, uhcl.edu, uhd.edu, uhv.edu

**Texas Tech System (3):** ttu.edu, ttuhsc.edu, angelo.edu

**Other Public (5):** sfasu.edu, msutexas.edu, tsu.edu, twu.edu, unt.edu (also unthsc.edu)

**Major Private (10):** rice.edu, baylor.edu, smu.edu, tcu.edu, trinity.edu, stmarytx.edu, acu.edu, udallas.edu, uiw.edu, stedwards.edu

**Small Private + HBCU (16):** hsutx.edu, hputx.edu, lcu.edu, ollusa.edu, schreiner.edu, tlu.edu, southwestern.edu, htu.edu, jarvis.edu, wiley.edu, pqc.edu, swau.edu, umhb.edu, letu.edu, dbu.edu, hbu.edu

**Total: 66 institutions** (some health-science centers shared with parent system count).
