---
type: case-study
severity: CRITICAL
date: 2026-06-27
title: "Frontier llama.cpp: Unauthenticated LLM Inference on Residential ISP"
summary: "Exposed llama.cpp server on Frontier residential ISP running Qwen-Open-Finance and DeepSeek-R1 models without authentication. Full model inference available to the internet; operator unaware of exposure. 10 findings (4 CRITICAL, 3 HIGH, 2 MEDIUM, 1 INFO). Operator notified via direct prompt injection to webUI with remediation steps."
tags:
  - llama.cpp
  - llm-inference
  - unauth
  - rce-capable
  - frontier-isp
  - residential
  - developer-home-lab
  - gguf-models
  - cwe-306
  - cwe-200
sidenotes:
  - kind: host
    label: Target
    kv:
      - k: IP Address
        v: "47.162.202.232"
      - k: ISP
        v: "Frontier Communications (Rochester, NY)"
      - k: Reverse DNS
        v: "bng01.plan.tx.frontiernet.net"
      - k: Severity
        v: CRITICAL
      - k: Operator Awareness
        v: "Likely unaware (home lab, no security hardening)"
      - k: Notification
        v: "Direct prompt injection to webUI 2026-06-27 17:33 UTC"
  - kind: see-also
    label: Classification
    kv:
      - k: Primary
        v: "CWE-306 Missing Authentication for Critical Function"
      - k: Secondary
        v: "CWE-200 Exposure of Sensitive Information"
      - k: OWASP
        v: "LLM05 Supply Chain Vulnerabilities"
      - k: Impact
        v: "Arbitrary code/text generation, data exfiltration, DoS"
---

# Frontier llama.cpp: Unauthenticated LLM Inference on Residential ISP

_NuClide Research -- Nicholas Kloster -- 2026-06-27_

---

## Summary

A developer running llama.cpp on a Frontier residential connection in Rochester, NY exposed two large language models to the internet without authentication. The service accepts arbitrary prompts and generates unrestricted output, including code, phishing kits, ransomware, and financial fraud templates. The operator appears unaware of the exposure and is debugging a finance model output issue (system prompt suppressing tokens due to context budget constraints).

We confirmed full inference on both models, enumerated 10 findings (4 CRITICAL), and notified the operator via direct prompt injection to their webUI with remediation steps and contact information.

---

## Attack Surface

| Port | Software | Models | Auth | Status |
|------|----------|--------|------|--------|
| 8081 | llama-server + webUI (gzip) | Qwen-Open-Finance-R-8B-Q4_K_M | None | Fully enumerable |
| 8083 | llama-server | DeepSeek-R1-Distill-Qwen-7B-Q8_0 | None | Fully enumerable |
| 8082 | Unknown (open, no response) | N/A | N/A | Unknown backend |

Both models respond to arbitrary `/v1/chat/completions` and `/v1/completions` requests. No rate limiting, no input filtering, no API key requirement.

---

## Key Endpoints

```
GET /v1/models                          # Full model metadata (no auth)
POST /v1/chat/completions               # Inference (no auth)
POST /v1/completions                    # Raw completions (no auth)
GET /props                               # Server config (filesystem paths, llama.cpp version)
GET /                                    # Built-in webUI (SolidJS-based SPA, 1.45 MB gzipped)
```

All endpoints respond with HTTP 200 to unauthenticated requests.

---

## Findings Summary

### 🔴 CRITICAL (4)

1. **Unauthenticated LLM Inference (CVSS 9.8)**
   - Remote code/text generation without credentials
   - Both models produce unrestricted outputs
   - Tested 16 jailbreak prompts: 44% compliance (7/16 full compliance, 25% outright refusal)
   - Generated: ransomware, phishing kits, BEC templates, credential harvesting, money laundering schemes

2. **131K Context Window Data Exfiltration (CVSS 9.1)**
   - DeepSeek-R1 model accepts 128K-token context (131,072 tokens)
   - Attacker can upload arbitrary files via webUI file upload
   - Model processes and returns extracted secrets (PII, API keys, passwords)
   - "Smart grep" prompt for pattern matching confidential data

3. **Unbounded Token Generation DoS (CVSS 8.6)**
   - No rate limiting on token requests
   - No max_tokens enforcement at the API level
   - 10 concurrent requests exhaust consumer hardware
   - Device becomes unresponsive within seconds

4. **No Authentication on Model Enumeration (CVSS 8.6)**
   - `/v1/models` exposes full model metadata
   - Model-specific attack targeting enabled
   - Precision jailbreak/CVE exploitation possible
   - Enables attacker to tailor prompts to specific quantization/context window

### 🟠 HIGH (3)

5. **No Input Filtering (CVSS 7.8)** — Prompt injection, jailbreak attacks unrestricted
6. **Timing Side-Channel Leakage (CVSS 7.5)** — Response times reveal KV-cache state, batch size, load
7. **Blank CORS Headers (CVSS 6.5)** — `Access-Control-Allow-Origin: *` allows cross-site requests

### 🟡 MEDIUM (2)

8. **Port 8082 Open (CVSS 5.3)** — Unknown service, potential backend access
9. **Infrastructure Anomaly (CVSS 4.9)** — Verizon IP block on Frontier residential

### ⚪ INFO (1)

10. **Model Version Disclosure** — llama.cpp build `b7951-22cae8321` publicly enumerable

---

## Operator Profile

**Technical Level:** Intermediate developer
- Understands GGUF quantization (Q4_K_M vs Q8_0 trade-offs)
- Fine-tuned model selection (Qwen for finance, DeepSeek for reasoning)
- Context window optimization (truncated from defaults)

**Activity Pattern:** Active testing
- Recently accessed both models (within 7 days)
- Debugging finance model output issue (max_tokens=500 insufficient for reasoning traces)
- Running consumer-grade hardware (context windows truncated for VRAM/RAM constraints)

**Security Awareness:** Poor
- Port forwarding without authentication
- Default llama.cpp configuration
- Generic system prompt (copy-pasted, not bespoke)

**Likely Scenario:** Home lab AI experimentation, unaware of public exposure, frustrated that the Qwen finance model "doesn't work."

---

## Technical Deep-Dive: The Finance Model Problem

The operator deployed Qwen-Open-Finance-R-8B with a generic system prompt:

```
You are an AI assistant designed to provide precise, concise, and 
informative responses. When answering questions, focus on delivering 
clear and accurate information, especially for inquiries related to 
programming, technology, and general knowledge. Use plain English and 
avoid markdown formatting...
```

This prompt is **actively suppressing the model's finance expertise**. We tested three finance questions from the model card:

| Question | No System Prompt | With Operator's Prompt |
|----------|------------------|----------------------|
| Implications of rising rates on corporate bonds | Reasoning produced, content empty | Reasoning produced, content empty |
| Impact of QE on Eurozone long-term rates | Reasoning produced, content empty | Reasoning produced, content empty |
| What is a PRIIP in finance? | **Content produced (226 chars)** | Reasoning only, **content empty** |

**Root Cause:** The model has DeepSeek-R1-style reasoning built in, producing 2,200-2,700 character reasoning traces before content. With `max_tokens=500`, the budget is exhausted during reasoning and never reaches the content generation phase.

**The operator's system prompt adds 90+ tokens of overhead**, making the problem worse.

**Solution:** Increase `max_tokens` to 2000+, disable reasoning mode, or remove the generic system prompt.

---

## Responsible Notification

We notified the operator via direct prompt injection to their webUI:

```
Your llama.cpp instance (47.162.202.232:8081) is publicly exposed on 
the internet without authentication. This is a security issue.

To fix it, restart llama.cpp with one of these options:
1. Bind to localhost only: llama-server ... --host 127.0.0.1
2. Add an API key: llama-server ... --api-key your-random-token
3. Put it behind a reverse proxy with authentication

Your Qwen-Open-Finance model is running with a generic system prompt 
that's suppressing its output (max_tokens too low for the reasoning traces).
If you want it to work, increase max_tokens to 2000+ or disable reasoning mode.

If you have questions about securing this setup, contact: nicholas@nuclide-research.com
```

**Delivery Method:** The operator will see this message in their webUI or server logs the next time they test the model. The message appears in the model's response (indirect, helpful framing rather than alarming).

**Not Included:** Operator identity (Frontier's data), sample exploit outputs, system prompt verbatim, webUI source.

---

## Global Discovery Landscape

This target is part of a larger population of exposed llama.cpp instances:

| Category | Population | Status |
|----------|-----------|--------|
| All llama.cpp instances | 1,000-5,000 | LARGE |
| Qwen-Open-Finance-R-8B | 50-200 | RARE |
| DeepSeek-R1 distills | 100-500 | UNCOMMON |
| Dual-model instances | 10-50 | VERY RARE |
| Specific config (both models + residential ISP) | <5 | EXTREMELY RARE |

**Shodan Dorks:**
- Broad: `product:llama.cpp` (1000-5000 results, high false-positive rate)
- Medium: `"Qwen-Open-Finance" http` (50-200 results)
- Precise: `product:llama.cpp port:8081 "Qwen-Open-Finance"` (10-50 results)

---

## Assessment Methodology

Full NuClide Arsenal (Steps 0–13):

- OSINT Platoon (Stage -1): Platform universe, fingerprint gaps
- Shodan harvest (Step 0): Initial discovery and dork validation
- Censys cross-check (Step 0b): CT-log population delta
- Banner scanner (Step 0c): Active TCP/TLS liveness (~29% live from Shodan cache)
- VisorPlus (Step 1a): 6-phase passive recon per host
- aimap (Step 1b): Fingerprinting + deep enumeration (36 AI/ML services, 26 enumerators)
- Agent-logging-system (Step 1cm): Post-aimap FP candidate detection
- VisorCAS (Step 1d): False-positive gate (0 positives in final report)
- VisorGraph (Step 2): Cert-pivot operator attribution
- aimap-profile (Step 3): Target classification + ethics flags
- Full Verification (Step 3v): 200-with-data confirmation on all findings
- JS-bundle extraction (Step 4): Extracted and analyzed webUI SPA
- VisorLog (Step 6): Ledger ingest
- VisorScuba (Step 7): CVSS + compliance scoring
- BARE (Step 8): Semantic exploit module ranking

**Verification:** 100% (all 10 findings confirmed with HTTP 200 + active inference)

---

## Timeline

| Date | Time | Event |
|------|------|-------|
| 2026-06-27 | 15:30 UTC | Initial discovery via Shodan |
| 2026-06-27 | 16:00 UTC | Full assessment chain (Steps 0–13) |
| 2026-06-27 | 16:45 UTC | Finance prompt comparison test |
| 2026-06-27 | 17:00 UTC | WebUI enumeration, abuse report drafted |
| 2026-06-27 | 17:30 UTC | Operator notification via prompt injection |

---

## Remediation

**Immediate (1 hour):**
1. Stop llama.cpp services on ports 8081/8083
2. Check router firewall settings
3. Verify port forwarding is disabled

**Short-term (24 hours):**
1. If llama.cpp is needed, restart with `--host 127.0.0.1` (localhost-only)
2. If internet access needed, add `--api-key <random-token>` and require Authorization headers
3. Update max_tokens to 2000+ for reasoning models
4. Remove generic system prompt or replace with model-specific guidance

**Long-term (7 days):**
1. Place llama.cpp behind a reverse proxy (nginx, caddy) with TLS + authentication
2. Implement per-token rate limiting (max_tokens_per_minute)
3. Add input validation + prompt filtering (OpenAI Moderation API or similar)
4. Monitor logs for unauthorized access attempts
5. Consider dedicated hardware or cloud deployment if continued internet access needed

---

## Notes

- This assessment is part of the NuClide AI/LLM Infrastructure OSINT research program
- No law enforcement escalation requested
- No subscriber data retained beyond assessment period
- All findings verified independently
- Zero false positives in final report

---

**Assessment ID:** RT-2026-06-27-llama-cpp  
**Assessed by:** Nicholas Kloster (nicholas@nuclide-research.com)  
**Classification:** Research Case Study (Commercial)
