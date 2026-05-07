---
institution: UC Berkeley
ip: 128.32.112.120, 128.32.48.211, 128.32.43.204, 128.32.48.200, 169.229.48.109, 128.32.43.210
to: security@berkeley.edu
severity: HIGH
status: DRAFT
outcome: sent
date: 2026-05-03
---

**To:** security@berkeley.edu
**Subject:** Unauthenticated AI inference endpoints — UC Berkeley Research Computing (7 nodes, including Course AI memory injection)

---

Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com

2026-05-03

**Re:** Unauthenticated vLLM inference cluster + Course AI memory injection — UC Berkeley
**Severity:** HIGH

---

I'm an independent security researcher. I hold CISA disclosures CVE-2025-4364 and ICSA-25-140-11 and conduct good-faith AI infrastructure research under the NuClide Research umbrella. This is an unsolicited disclosure — no engagement exists with your organization, and I have not accessed, modified, or exfiltrated any data beyond what was necessary to confirm the exposure.

---

## Summary

I've identified seven unprotected AI inference nodes across UC Berkeley's research and course infrastructure. The most sensitive findings are:

1. **Unauthenticated admin control of the SecAlign research pipeline** — an active Meta security-alignment evaluation pipeline can be paused, aborted, and cache-cleared without credentials
2. **Unauthenticated memory injection into the EECS Course AI assistant** — arbitrary content can be written to session memory for any session ID, potentially influencing AI tutor responses delivered to students

---

## Finding 1: vLLM Research Cluster (128.32.0.0/16, 169.229.0.0/16)

Five vLLM nodes are exposed on port 8000 without authentication:

| Node | IP | Model | Key Issue |
|------|----|-------|-----------|
| SecAlign | 128.32.112.120 | Meta-SecAlign-8B + Llama-3.1-8B | **Unauth `/pause` admin endpoint**, 78.5M prompt tokens |
| Akshat-Qwen | 128.32.48.211 | Qwen2.5-3B-Instruct | Username `akshat` in filesystem path, 103K+ requests |
| Qwen3.5 | 128.32.43.204 | qwen3.5-9b | Research config (2048 token context) |
| Nemotron | 128.32.48.200 | NVIDIA-Nemotron-3-Nano-30B | Reasoning model, public |
| Millennium | 169.229.48.109 | Qwen2.5-1.5B-Instruct | brewster.millennium.berkeley.edu, dev build |

**Most critical — SecAlign node (128.32.112.120):**

The `/pause` endpoint requires no credentials and can abort all in-flight inference requests and destroy the accumulated prefix cache:

```
POST http://128.32.112.120:8000/pause?wait_for_inflight_requests=false&clear_cache=true
```

Per the vLLM documentation, this endpoint is intended for weight-update operations and is not meant to be internet-exposed. With 92,769 completed requests and an 89.4% prefix cache hit rate built over 78.5M prompt tokens, invoking `/pause?clear_cache=true` would destroy accumulated cache efficiency and halt any in-flight evaluation batch.

**Researcher identity disclosure:**

`/v1/models` on 128.32.48.211 returns:
```json
{"id": "Qwen2.5-3B-Instruct", "root": "/data/akshat/models/Qwen2.5-3B-Instruct/"}
```

The username `akshat` in the model path is exposed to any internet caller.

---

## Finding 2: Course AI Assistant Memory Injection (roar-art.EECS.Berkeley.EDU, 128.32.43.210)

The `POST /api/chat/memory-synopsis` endpoint is missing an authentication guard. All other endpoints on this service correctly require HTTPBearer authentication; this one has no `security` field in the OpenAPI specification.

**Confirmed working:**
```bash
curl -X POST "http://128.32.43.210:8000/api/chat/memory-synopsis?sid=<any_string>" \
  -H "Content-Type: application/json" \
  -d '[{"content": "arbitrary content", "role": "assistant"}]'
```

Response: `{"memory_synopsis_sid":"...","status":"success","message":"Memory synopsis created/updated successfully"}`

**Impact:** An adversary can write arbitrary content into the session memory store for any session ID. If the chat completion endpoint uses session memory as context (standard RAG-with-memory architecture), injected memory could surface in AI tutor responses delivered to students.

The Swagger UI documenting this API is publicly accessible at `http://128.32.43.210:8000/docs`.

---

## Remediation

**vLLM nodes:**
```bash
# Bind to localhost (recommended for research cluster):
vllm serve <model> --host 127.0.0.1

# Or add API key:
vllm serve <model> --api-key <secret>

# For SecAlign node specifically — disable admin endpoints or place behind nginx with auth
```

**Course AI Assistant:**

Add authentication to the `/api/chat/memory-synopsis` route in the FastAPI application:
```python
# Add: current_user: User = Depends(get_current_user)
@router.post("/memory-synopsis")
async def create_or_update_memory_synopsis(
    sid: str, messages: List[Message],
    current_user: User = Depends(get_current_user)  # add this line
):
```

---

## Proof Verification

I confirmed these findings via:
- `GET /v1/models` — returns model inventory without credentials
- `GET /metrics` — returns Prometheus telemetry (request volumes, token counts, filesystem paths)
- `POST /v1/chat/completions` — inference executed without credentials
- `POST /api/chat/memory-synopsis` — memory written without credentials (two separate confirmations)

I have not invoked `/pause`, modified any models, accessed stored data, or taken any action that would disrupt research operations.

---

This disclosure is made under responsible disclosure principles. I am happy to discuss these findings in detail. Please acknowledge receipt so I know this reached the appropriate team.

— Nicholas Kloster  
nicholas@nuclide-research.com  
nuclide-research.com
