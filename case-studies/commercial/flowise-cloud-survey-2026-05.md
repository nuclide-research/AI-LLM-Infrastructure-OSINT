# Flowise on Public Cloud: Auth Posture Survey

_NuClide Research · 2026-05-03_

---

## Summary

Sweep of 1.83M IPs across 28 cloud-provider /16 ranges (DigitalOcean, Hetzner, Vultr) on port 3000 → 20,581 live hosts → **43 confirmed Flowise instances** via the `/api/v1/ping` → `pong` fingerprint. **Zero unauthenticated, exploitable instances.** All real Flowise responders return `401 Unauthorized` on `/api/v1/chatflows`, `/api/v1/credentials`, `/api/v1/apikey`, and `/api/v1/variables`.

This is a useful negative-space result: Flowise operators on the three largest self-hosting clouds are uniformly hardened. The default-no-auth posture documented in CVE-2024-36420 disclosures appears to have produced operator behavior change.

---

## Methodology

**Discovery pipeline:**

```
masscan -iL <28 cloud /16 CIDRs> -p 3000 --rate 2000
  → 20,581 unique live hosts on :3000

httpx -path /api/v1/ping -mc 200 -ms "pong"
  → 43 Flowise instances confirmed

aiapp-probe.py (deep enumeration)
  → version, chatflows, credentials, apikey, variables
```

**Why `/api/v1/ping` is the definitive fingerprint:**
The endpoint returns a 4-byte `pong` body (or `{"ping":"Pong","when":"..."}` JSON in some builds). No other software in the public-internet response distribution returns exactly that on that path. Filter rate: 99.79% reduction (20,581 → 43).

---

## Findings Summary

| Metric | Value |
|---|---|
| Live hosts on :3000 | 20,581 |
| Confirmed Flowise | 43 |
| Unauthenticated `/api/v1/chatflows` | **0** |
| Unauthenticated `/api/v1/credentials` | **0** |
| Unauthenticated `/api/v1/apikey` | **0** |
| Pong-decoy false positives (every path returns "pong") | 2 |
| CVE-2024-36420 candidates (Flowise <1.8.2) | 0 |

---

## Version Distribution (41 real Flowise instances)

| Version line | Count | Notes |
|---|---|---|
| 3.1.x (3.1.0, 3.1.1, 3.1.2) | 10 | Latest stable |
| 3.0.x (3.0.1–3.0.13) | 14 | Currently maintained |
| 2.2.x (2.2.2, 2.2.3, 2.2.7, 2.2.7-patch.1, 2.2.8) | 7 | Older but post-CVE patch baseline |
| 2.1.x (2.1.2, 2.1.3, 2.1.4) | 3 | Pre-2.2 series, several CVE candidates if auth bypassed |
| Version unknown | 7 | `/api/v1/version` returned non-standard response |

**Authenticated 2.1.x instances of interest** (auth-protected, but version-disclosed):
- `167.172.141.12:3000`, v2.1.4 (DigitalOcean)
- `167.71.129.40:3000`, v2.1.2 (DigitalOcean)
- `116.202.187.140:3000`, v2.1.3 (Hetzner)

These are not exploitable as-is, but version disclosure via `/api/v1/version` on an unauth path is a low-severity information leak.

---

## Pong-Decoy Anti-Pattern

Two hosts (`138.197.11.255:3000`, `167.172.37.195:3000`) return `pong` (or `{"ping":"Pong",...}`) for **every path probed**, including `/api/v1/credentials`, `/api/v1/chatflows`, `/api/v1/apikey`. These are not real Flowise instances. Most likely:

1. Reverse-proxy fallback handlers misconfigured to mirror a Flowise health-check probe
2. Honeypots tuned specifically for Flowise scanning campaigns
3. Custom monitoring endpoints that return `pong` for any HTTP request

**Defender takeaway:** if your scan toolchain treats `/api/v1/ping` → "pong" as definitive evidence of Flowise, you'll false-positive on these. The probe should also verify `/api/v1/version` returns a structured `{"version":"x.y.z"}` and that `/api/v1/chatflows` returns either a JSON array (200) or a proper Flowise 401 envelope `{"error":"Unauthorized Access"}`.

---

## Why This Matters

Flowise's `/api/v1/credentials` endpoint, when exposed, returns stored API keys for every connected provider (OpenAI, Anthropic, Cohere, etc.). An unauthenticated instance is a multi-key compromise. CVE-2024-36420 (path traversal, <1.8.2) provided an additional pathway to the same data even on auth-on instances.

The empirical result here, 0 of 43 cloud-hosted instances exposed, is a directionally positive indicator that Flowise operator hygiene has improved post-CVE. It does **not** indicate that Flowise is universally safe; the next phase of this research should target:

- **Residential ISPs and small VPS providers**, different operator population
- **Older deployments** (pre-2.0) that are no longer auto-updated
- **University and research-cloud ranges**, tested separately under the universities/ catalogue

---

## Probe Tooling

- `data/aiapp-probe.py`, Python deep prober supporting Flowise, Dify, AnythingLLM, LangFlow, n8n, LibreChat, LM Studio, LocalAI, Open WebUI, RAGFlow, Jupyter, LiteLLM, AUTOMATIC1111/ComfyUI, Apache Airflow, Qdrant, ChromaDB, Elasticsearch.
- httpx filter command: `httpx -p 3000 -path /api/v1/ping -mc 200 -ms "pong" -threads 100 -timeout 5`

---

## Discoverer

NuClide Research, nicholas@nuclide-research.com

No data was accessed, modified, or exfiltrated. All 43 confirmed instances were probed only on documented unauthenticated endpoints (`/api/v1/ping`, `/api/v1/version`) and on data endpoints to determine auth posture (response code only, no payload extraction attempted on 401 returns).
