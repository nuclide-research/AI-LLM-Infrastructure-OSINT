---
type: survey
category: llm-chat-framework
platform: chainlit
date: 2026-06-08
researcher: NuClide Research
---

# Chainlit at Population Scale: 80 Percent Anonymous Chat on a Framework That Ships Auth-Off

_NuClide Research . 2026-06-08_

---

## Summary

Population-scale survey of **Chainlit** (the LLM chat framework built on FastAPI / uvicorn used to wrap LangChain and LlamaIndex prototypes as web UIs) via the Shodan dork `"chainlit"`. 19 total hits, 13 live, 5 confirmed Chainlit deployments.

**Headline.** 4 of 5 verified Chainlit instances on the open internet (80 percent) require no authentication. An anonymous visitor can open the chat UI and, per Chainlit's design, submit prompts that consume the operator's backend LLM credits and quota. The one auth-gated host in the sample (an AI bathroom-renovation visualizer named "Renovis" on Contabo, Germany) reports `requireLogin=true` and returns 401 on `/user`.

**Population caveat.** n=19 is below the threshold where a population finding carries the same weight as Cat-04 Ollama (~16k hosts) or Cat-49 Label Studio (407). This is a niche framework that mostly hides behind a domain-fronting CDN. The 80 percent unauth rate among the visible cohort is a directional signal, not a population-scale claim. A re-survey when Chainlit's Shodan footprint crosses ~50 is queued.

**Framework-default thesis.** Chainlit's documented default is auth-off. The framework ships with no authentication unless the operator adds `@cl.password_auth_callback` or sets OAuth environment variables. The 80 percent unauth rate at population scale (4/5 verified) is what an auth-off-default framework looks like when no countervailing pressure is applied. This is the auth-on-default thesis (Insight #40) read in reverse: the framework default propagates to the operator default.

<!-- ksat-tag:auto-generated:start -->
## DCWF KSAT coverage

Wardrobe outfit: `ai-infra-hunt`.

- **672 (AI Test & Evaluation Specialist):** T5919, K7044, S7067, T5904.
- **733 (AI Risk & Ethics Specialist):** T5893 / T5882, K7040 (anonymous prompt submission consumes operator LLM credits; the operator's budget is the asset).
- **NICE 541:** T0028, T0188, K0342, S0001, S0051, T0247, K0107, K0118.

<!-- ksat-tag:auto-generated:end -->

---

## Methodology

```
Stage 0    Shodan API on  "chainlit"             ->  19 hits
            shodan search --fields ...           ->  19 IP:port saved
            (alt http.title:"Chainlit"           ->  0 hits)

Stage 0c   verify.py. 8-thread, 10s timeout
            Rung A (identity):
              GET /                              ->  og:url contains
                                                    github.com/Chainlit/chainlit
                                                    og:image -> chainlit-cloud.s3
                                                    Server: uvicorn
              GET /project/translations          ->  Chainlit-shaped JSON
            Rung B (auth posture):
              GET /auth/config                   ->  JSON with requireLogin,
                                                    passwordAuth, headerAuth,
                                                    oauthProviders keys
            Rung C (access confirmation):
              GET /user                          ->  200 anon -> unauth
                                                    401/403  -> auth-required

            Verdict requires identity + auth-state agreement.
            No POST. No /message. No chat history reads. No uploads.
```

**Restraint posture.** GET only. The endpoints touched per confirmed host were `/`, `/auth/config`, `/user`, `/project/translations`. The verifier never submitted a prompt, never opened a chat thread, never replayed a session cookie. Project names ("Renovis", "POC AI Assistant", "Gefuhlsfreund") were taken from the same `<title>` tag Shodan had already indexed. On the unauth hosts, no chat history was read and no LLM call was triggered.

---

## The endpoint-discovery story

The task brief named `/auth-config` and `/project/init` as the Chainlit auth probes. The first verifier run treated both as Chainlit identity markers and returned 200 on all 5 confirmed hosts. The 200 was the SPA catch-all serving the HTML index for any unknown path - identical to the Cat-49 Label Studio and Cat-50 Argilla SPA-defeats-status-code pitfall.

Pulling the JS bundle (`/assets/index-Dfxzo6t5.js`) and grepping for fetch endpoints surfaced the modern Chainlit API surface: `/auth/config`, `/auth/jwt`, `/user`, `/login`, `/logout`, `/project/translations`, `/project/threads`. The endpoint names in the brief were a pre-v1 schema. After updating the verifier the false-positive 200 collapsed and the survey produced clean unauth verdicts on 4 hosts (`requireLogin=null` + `/user=200`) and a clean auth verdict on 1 (`requireLogin=true` + `/user=401`).

**Insight candidate.** **Framework endpoint schemas drift across major releases; ALWAYS pull the JS bundle and grep for fetch targets before pinning verifier paths.** The pre-v1 path `/auth-config` survives in tutorials and Stack Overflow answers indexed years ago; the modern path `/auth/config` is in the bundle string table. A path-driven verifier that does not re-anchor on the bundle drifts silently.

---

## Findings

### Verdict tally

| Bucket | Count | % of pop | % of live |
| --- | --- | --- | --- |
| unauth_chainlit_confirmed | 4 | 21.1 | 30.8 |
| auth_chainlit_confirmed | 1 | 5.3 | 7.7 |
| fp_not_chainlit | 8 | 42.1 | 61.5 |
| dead | 6 | 31.6 | - |

Of the 5 verified Chainlit hosts, 4 (80 percent) are unauth.

### Confirmed Chainlit fleet

**Unauth (4):**

| Host | Title | Hoster | Bundle |
| --- | --- | --- | --- |
| 202.61.192.86:9000 | Gefuhlsfreund | netcup (DE) | huWggE6U.js |
| 34.87.75.26:8500 | POC AI Assistant | Google GCE | Dfxzo6t5.js |
| 49.13.207.111:8081 | Assistant | Hetzner (DE) | Dfxzo6t5.js |
| 52.72.141.190:80 | Assistant | AWS EC2 + ELB | 1i5IMwCp.js |

**Auth-required (1):**

| Host | Title | Hoster | Bundle | Note |
| --- | --- | --- | --- | --- |
| 158.220.122.105:8500 | Renovis | Contabo (DE) | Dfxzo6t5.js | AI Bathroom Renovation Visualizer. `requireLogin=true`. `/user=401`. Posture-correct: login wall in front of the LLM. |

### JS bundle clusters (version-cohort proxy)

| Bundle hash | Hosts | Note |
| --- | --- | --- |
| index-Dfxzo6t5.js | 3 | Largest cluster - same build, three independent operators. Suggests a shared PyPI Chainlit release with a release date narrow enough to dominate the visible fleet. |
| index-huWggE6U.js | 1 | Gefuhlsfreund |
| index-1i5IMwCp.js | 1 | 52.72.141.190 |
| index-87533cb5.js | 1 | 157.90.251.84 - whitelabel fork, og:* identity stripped. Not bucketed as Chainlit because the canonical markers are gone. |
| index-DorR7aTz.js | 1 | Additional FP |

Chainlit does not expose an unauthenticated `/version` endpoint; the SPA catch-all serves the HTML shell on any unknown route. Bundle hash is the available version proxy. The 3-host Dfxzo6t5 cluster suggests either a shared image (PyPI Chainlit release) or three operators who pulled the same pinned version within a narrow window.

### Substrate

| Hoster | Confirmed Chainlit | Auth-state |
| --- | --- | --- |
| Hetzner (DE) | 1 | unauth |
| netcup (DE) | 1 | unauth |
| Contabo (DE) | 1 | auth |
| Google GCE | 1 | unauth |
| AWS EC2 + ELB | 1 | unauth |

European hobbyist hosters (Hetzner / netcup / Contabo) account for 3 of 5 confirmed hosts. These are common low-cost VPS providers where independent developers stand up demo apps quickly. The AWS deployment is the only one fronted by a load balancer; the others are uvicorn-direct on non-standard ports (8081, 8500, 9000).

---

## Why 8 false positives

The Shodan body-text dork `"chainlit"` matches any HTML containing the literal string. The 8 FP hits include a BioStar 2 access-control UI, an Apache 404 page, an ASP.NET request-rejected page, a Fusion AIQ SaaS landing, a Universitatsklinikum Ulm site, and a UniCredit-Bulbank bot site. A vite SPA on Hetzner (157.90.251.84) was a structural match (TAGS-INJECTION-PLACEHOLDER, `index-*.js`, `index-*.css`) but had all og:* identity stripped - likely a Chainlit fork or whitelabel; bucketed as FP because the canonical signature is gone.

**Lesson.** The Chainlit body-text dork has a 42 percent FP rate. The markers that survive at population scale are `og:url -> github.com/Chainlit/chainlit` and `og:image -> chainlit-cloud.s3.eu-west-3.amazonaws.com`. Both are baked into Chainlit's upstream `index.html` template; they only fall away when the operator deliberately edits the template. A tighter dork variant - `http.html:"chainlit-cloud.s3"` or `http.html:"github.com/Chainlit/chainlit"` - would lift FP rate but the host body marker is not in Shodan's `http.html` index for most of these, and the title dork returned 0.

---

## Restraint

GET only. No prompts submitted. No chat threads opened. No file uploads. No history reads.

The 4 unauth hosts would be appropriate disclosure candidates under the standard NuClide protocol. No disclosure is being initiated from this survey per the policy of leaving disclosure decisions to the principal researcher.

The names "Renovis", "POC AI Assistant", "Gefuhlsfreund", "Assistant" all came from the public HTML `<title>` tag. Substrate attribution came from Shodan's WHOIS-derived `org` field. Nothing on the chat side was touched.

---

## Toolchain provenance

- shodan CLI v1.31 (Shodan API, NuClide Freelance tier, US-made, ~9075 query credits at start of survey).
- Python 3.12 with `requests` 2.x for the verifier. `urllib3` warnings disabled for self-signed TLS. Single-file, ~200 lines.
- `verify.py` source: `~/AI-LLM-Infrastructure-OSINT/data/chainlit-2026-06-08/verify.py`.
- Verifier output: `verify-results.json` in the same directory.

The verifier was rewritten once after the initial run revealed the pre-v1 endpoint schema in the task brief was stale. The path schema correction (`/auth-config` -> `/auth/config`, addition of `/user` as the access-confirmation rung, addition of `/project/translations` as the secondary identity marker) was sourced from the live JS bundle string table - the same artifact every Chainlit client uses to know where to call. No POST, no chat read, no history dump.

---

## Position relative to the auth-on-default thesis

| Platform | Default | Population unauth rate | Source |
| --- | --- | --- | --- |
| Ollama (Cat-04) | auth-off | ~95% | reference_ollama_population_2026_05_15_summary |
| Weaviate (Cat-02) | auth-off | dominant unauth tier | project_survey_cat02_vector_databases |
| Langfuse (Cat-15) | varies by release | 88.9% (signup-open by default) | (per memory) |
| Label Studio (Cat-49) | auth-on | 0.2% | argilla-survey-2026-06-08 |
| Argilla (Cat-49 sibling) | auth-on (mandatory API key) | 0% | argilla-survey-2026-06-08 |
| **Chainlit (Cat-50)** | **auth-off** | **80% (4/5, small n)** | this survey |

The framework default sets the policy at population scale. Operators do not flip the switch. Chainlit's 80 percent unauth rate at n=5 is small-sample but directionally consistent with the auth-off-default cohort. The labeling cohort (Label Studio + Argilla) remains the strictest auth posture in the NuClide measurement set; the chat-UI cohort (Ollama + Chainlit) remains the most permissive.
