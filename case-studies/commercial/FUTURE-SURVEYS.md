# Future Surveys — AI/ML Infrastructure Categories Not Yet Covered

_NuClide Research · 2026-05-04_
_Companion to: [`SYNTHESIS-2026-05.md`](SYNTHESIS-2026-05.md)_

---

The 2026-05 survey series covers 19+ platform classes. Several adjacent categories remain unsurveyed and are catalogued here as a roadmap. Each entry includes:

- **Port(s)** to masscan
- **Fingerprint** (the canonical signature for the probe to use)
- **Auth posture in framework default** (Tier-A no-auth-concept, Tier-A* auth-optional-off, Tier-B setup-wizard, Tier-C auth-on-default)
- **Risk class** if exposed
- **Status** (planned / partial / not-yet)

Anyone running NuClide's tier-2 cloud range list ([`/tmp/tier2-all-ranges.txt`](https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT) — Scaleway 7, OVH 33, Linode 36 = 3.55M IPs) can pick a category and run the survey using the same masscan-then-probe pattern documented in the existing case studies.

---

## Compute orchestration / training tier

Most are Tier-A "no auth concept" on the dashboard endpoint. Auth is bolted on by surrounding infra (K8s ingress + auth proxy), not the framework itself.

| Platform | Port | Fingerprint | Tier | Risk | Status |
|---|---|---|---|---|---|
| **Ray Dashboard** | 8265 | GET `/` returns Ray UI HTML; GET `/api/jobs` lists jobs | A | CVE-2023-48022 ShadowRay actively exploited (job-submission RCE); job logs leak | not-yet (task #50; partial — empty in tier-2 sample) |
| **Dask Dashboard** | 8787 | GET `/status` returns Bokeh-rendered Dask page | A | Cluster topology + worker info disclosure; expensive ops triggerable | not-yet |
| **Apache Spark UI** | 4040, 8080 | GET `/` returns Spark Master / Application UI | A | Job logs + driver state + sometimes credentials in env | not-yet |
| **Apache Airflow** | 8080 | GET `/login` returns Airflow login page | A* (auth optional, off-by-default in older versions) | DAG-run history, sometimes plaintext credentials in connections | not-yet |
| **Prefect** | 4200 | GET `/api/health` returns `{"status":"healthy"}` | A* | Flow runs + state | not-yet |
| **Temporal** | 7233 (gRPC), 8080 (web UI) | GET `/api/v1/cluster-info` | A* | Workflow history | not-yet |
| **Kubeflow / KServe** | varies (K8s ingress) | `/v1/models` OpenAPI | varies | Model serving + pipeline metadata | not-yet — K8s ingress profile, separate from cheap-VPS surface |
| **BentoML** | 3000 | GET `/` returns BentoML service page; `/docs` Swagger | A* | Model serving + sometimes file upload | not-yet |

---

## Embeddings infrastructure

| Platform | Port | Fingerprint | Tier | Risk | Status |
|---|---|---|---|---|---|
| **TEI (HuggingFace Text Embeddings Inference)** | 80, 3000, 8080 | GET `/info` returns `{"model_id":"...","max_concurrent_requests":..., "model_pipeline_tag":"feature-extraction"}` | A | Compute theft; model fingerprinting | not-yet |
| **llama.cpp HTTP server** | 8080 | GET `/health` returns `{"status":"ok"}`; GET `/props` returns model props | A | Compute theft, prompt injection | not-yet |

---

## Specialty vector DBs

| Platform | Port | Fingerprint | Tier | Risk | Status |
|---|---|---|---|---|---|
| **Weaviate** | 8080 | GET `/v1/meta` returns Weaviate version JSON; GET `/v1/schema` lists classes | A* (anonymous-access on by default in `auth.anonymous_access.enabled=true`) | Same as Qdrant — vector data + schema disclosure | not-yet — port 8080 conflicts heavily |
| **pgvector** (PostgreSQL extension) | 5432 | TCP banner + `SELECT pgvector_version();` | A* (Postgres auth — depends on operator) | Vector data via SQL injection / weak creds | not-yet — needs auth-bypass enumeration |
| **Redis Stack** (with vector search) | 6379 | TCP `*1\r\n$4\r\nINFO\r\n` returns Redis info | A* (default ALLOW-ANY in dev configs) | Vector + cache + sometimes sessions | not-yet |
| **LanceDB** | various | GET `/api/v1/database/list` | A | RAG store | not-yet |
| **Vespa** | 8080 | GET `/state/v1` returns Vespa health JSON | A | Search + vector | not-yet |
| **Typesense** | 8108 | GET `/health` returns `{"ok":true}`; X-TYPESENSE-API-KEY header for auth | A* | Document index + facets | not-yet |
| **Meilisearch** | 7700 | GET `/health` returns `{"status":"available"}` | A* (master-key auth optional) | Document index | not-yet |
| **Apache Solr** | 8983 | GET `/solr/admin/info/system` | A* | Document index + sometimes RCE via velocity templates | not-yet |

---

## LLM observability / tracing

| Platform | Port | Fingerprint | Tier | Risk | Status |
|---|---|---|---|---|---|
| **Langfuse** | 3000 | GET `/api/public/health` returns Langfuse health JSON | C (auth-on-default) | LLM trace history if signup-open | not-yet |
| **Phoenix (Arize)** | 6006 | GET `/v1/traces` OTLP JSON | A* | LLM call traces, sometimes PII in prompts | not-yet |
| **Helicone** | varies | gateway pattern — proxy logs | A* | LLM call history | not-yet |
| **TruLens self-hosted** | varies | dashboard fingerprint | A* | Eval traces | not-yet |

---

## Image generation / vision (beyond port 7860 surveyed)

| Platform | Port | Fingerprint | Tier | Risk | Status |
|---|---|---|---|---|---|
| **ComfyUI** | 8188 | GET `/system_stats` returns GPU info; GET `/queue` lists running jobs | A | Compute theft + workflow exfil + GPU info | not-yet |
| **Roboflow self-hosted** | varies | API key required | C | Custom model serving | not-yet |
| **YOLOv8 / MMDetection inference servers** | varies (often 8000) | Custom HTTP API | A* | Compute theft, prompt injection (multimodal) | partial — some seen via Triton survey |

---

## Speech & Audio AI (extended — beyond port 9000 already surveyed)

| Platform | Port | Fingerprint | Tier | Risk | Status |
|---|---|---|---|---|---|
| **Coqui XTTS server** | 8020 | GET `/api/tts` returns TTS server response | A | Compute theft (voice cloning), trademark/voice misuse | not-yet |
| **Mozilla TTS / Coqui TTS legacy** | 5002 | GET `/api/tts` | A | Same | not-yet |
| **Bark / MusicGen Gradio UIs** | 7860 | GET `/` returns Gradio UI | A | Compute theft | partial — covered by gradio survey but not isolated for audio |
| **Pipecat / LiveKit voice agents** | varies (WebRTC + signaling) | Custom protocol | A* | Voice-call abuse, real-time-conversation manipulation | not-yet |
| **pyAnnote diarization** | varies | Custom HTTP API | A | Speaker-ID compute theft | not-yet |
| **F5-TTS / E2-TTS / OpenVoice / ChatTTS** | varies | Custom HTTP API | A | Voice cloning compute theft | not-yet |

---

## ML lifecycle / model registries

| Platform | Port | Fingerprint | Tier | Risk | Status |
|---|---|---|---|---|---|
| **W&B self-hosted** | 8080, 443 | GET `/api/health` returns `{"version":"..."}` | C (auth-on-default) | Experiment data if signup-open | not-yet |
| **ClearML server** | 8080, 8081, 8008 | GET `/version` returns ClearML version | A* | Experiment data | not-yet |
| **Comet ML self-hosted** | varies | API token required | C | Experiment data | not-yet |
| **Neptune.ai** | varies | API token required | C | Experiment data | not-yet — managed-mostly |
| **DVC remote storage** | S3-compat | bucket-policy depends on operator | varies | Model artifacts, training data | partial — covered by MinIO survey |

---

## Agent platforms (newer / autonomy)

| Platform | Port | Fingerprint | Tier | Risk | Status |
|---|---|---|---|---|---|
| **AutoGen Studio** | 8081 | GET `/` returns AutoGen Studio UI; GET `/api/agents` | A* | Agent definitions + sometimes credentials in tools | not-yet |
| **CrewAI Studio** | varies | dashboard fingerprint | A* | Agent definitions | not-yet |
| **LangGraph servers** | various | GET `/openapi.json` shows LangGraph schema | A* | Graph definitions, sometimes prompts | not-yet |
| **BabyAGI / SuperAGI** | varies | dashboard fingerprint | A* | Agent state, sometimes API keys | not-yet |

---

## Specialty data layers (often AI-adjacent)

| Platform | Port | Fingerprint | Tier | Risk | Status |
|---|---|---|---|---|---|
| **ClickHouse** | 8123 (HTTP), 9000 (TCP) | GET `/?query=SELECT+1` returns `1`; HTTP banner `ClickHouse-` | A* | OLAP query access — sometimes including AI training datasets | not-yet — partial signal during chroma probe (port 9000 collision) |
| **DuckDB HTTP server** | varies | Custom HTTP API | A* | Embedded analytics queries | not-yet |
| **Cassandra / ScyllaDB** | 9042 (CQL native), 7000 (gossip) | TCP banner + `SELECT release_version FROM system.local` | A* | NoSQL data + sometimes AI feature stores | not-yet |
| **Apache Pinot** | 9000 (controller), 8000 | GET `/cluster/info` | A* | Real-time analytics | not-yet — port 9000 collision with whisper |

---

## Dev-tooling AI / coding agents

| Platform | Port | Fingerprint | Tier | Risk | Status |
|---|---|---|---|---|---|
| **Continue.dev servers** | varies | Custom config endpoint | A* | LLM proxy abuse | not-yet |
| **Tabby self-hosted** | 8080 | GET `/` returns Tabby UI; GET `/v1beta/health` | A* | Code-completion compute theft | not-yet |
| **Aider** | typically not server-mode | n/a | n/a | n/a | not-applicable (CLI-only) |

---

## Specialty domains

| Platform | Port | Fingerprint | Tier | Risk | Status |
|---|---|---|---|---|---|
| **NVIDIA Clara** (medical AI) | varies | Triton-class APIs | A* | Medical-data compute theft | not-yet |
| **MONAI Deploy** | varies | Triton/KServe-class | A* | Medical-imaging | not-yet |
| **ROS interfaces** | 11311 (master), 9090 (rosbridge) | XML-RPC banner | A | Robot fleet control | not-yet |
| **TensorRT inference servers** | varies | Custom HTTP API | A* | Compute theft | not-yet — partial via Triton |
| **Jetson endpoints** | varies | Custom edge-AI protocols | A | Compute / sensor theft | not-yet |

---

## Methodology template

For any platform above, the probe pattern is:

```bash
# 1. Masscan the canonical port across the tier-2 cloud /16 ranges
sudo masscan -iL /tmp/tier2-all-ranges.txt -p<port> --rate 10000 --wait 5 -oG /tmp/<platform>-masscan.txt

# 2. Filter to unique IPs
awk '/Host:/ {print $4}' /tmp/<platform>-masscan.txt | sort -u > /tmp/<platform>-ips.txt

# 3. Run the framework-specific fingerprint probe (200-thread Python)
/home/cowboy/security-tools/bin/python3 /tmp/<platform>-probe.py < /tmp/<platform>-ips.txt > /tmp/<platform>-confirmed.jsonl

# 4. Filter AS63949 honeypot fleet pollution if probe is permissive
/home/cowboy/security-tools/bin/python3 /tmp/honeypot-detector.py < /tmp/<platform>-ips.txt | comm -23 /tmp/<platform>-ips.txt -

# 5. Cert-pivot identified hosts on port 443 for operator attribution
while read ip; do
  cn=$(timeout 4 bash -c "echo | openssl s_client -connect $ip:443 -servername $ip 2>/dev/null" | openssl x509 -noout -ext subjectAltName 2>/dev/null | tail -1)
  echo "$ip → $cn"
done < /tmp/<platform>-confirmed-ips.txt
```

The existing case studies serve as templates — the [`speech-audio-cloud-survey-2026-05.md`](speech-audio-cloud-survey-2026-05.md) is the most recent example following this pattern.

---

## Why this list exists

The auth-on-default thesis predicts: **for any framework that ships without authentication enabled by default, the population-scale deployment will be unauthenticated.** Each unsurveyed platform above is an opportunity to either:

1. **Confirm the thesis** on a new platform class (extends the evidence base)
2. **Falsify the thesis** if a platform with auth-off-default ships ~0% unauth at population scale (would be a meaningful counter-example, none observed yet)

The list also serves as a roadmap for any contributor who wants to add coverage. NuClide's tooling (`aimap`, `recongraph`, `BARE`) already covers many of the fingerprints above; running them at population scale on tier-2 cloud ranges is the work product.

---

## See also

- [`SYNTHESIS-2026-05.md`](SYNTHESIS-2026-05.md) — completed-survey synthesis
- [`REMEDIATION-GUIDE.md`](REMEDIATION-GUIDE.md) — operator fix-it guide for the platforms covered
- [`index.md`](index.md) — index of all completed case studies
