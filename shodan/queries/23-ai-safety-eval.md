# 23. AI Safety Evaluation / Red-Team Self-Hosted

_Section created: 2026-05-09_

Self-hosted AI safety evaluation, adversarial probing, and guardrails platforms. Their finding-corpus may itself be sensitive when exposed: adversarial prompt libraries, evaluator outputs, and red-team test results contain proprietary attack vectors. LLM call traces stored by LangSmith/Langfuse (see §5) often include user PII.

**Survey result (2026-05-04, corrected 2026-05-05):** Initial probe reported 6 confirmed hosts; tightened fingerprints invalidated all 6 as false positives (substring noise on `"garak"` / `"confident"` / `"deepeval"`). **Corrected total: 0 confirmed AI safety eval / red-team self-host on the 3.55M-IP tier-2 cloud sample.** The ecosystem is CLI-dominant (Garak, HELM, PyRIT, Inspect AI ship as CLIs with no HTTP server mode); the HTTP-serving tier (Promptfoo, LangSmith, NeMo Guardrails) deploys predominantly in managed cloud or enterprise K8s rather than cheap-VPS.

**Auth posture:**
- **Promptfoo**: T2 — has built-in web UI on port 15500 but auth is optional; most deployments are localhost-only.
- **LangSmith self-hosted**: T2 — auth on by default; enterprise tier.
- **NeMo Guardrails**: T2 — `/v1/rails/configs` sometimes open.
- **Garak REST**: T1 — no auth if HTTP server mode used, but CLI-dominant deployment makes this rare.
- **DeepEval**: T1 — no auth on the self-host HTTP server endpoint.

**Fingerprinting lesson from this survey:** Single-word substring matching (`"garak"`, `"deepeval"`, `"confident"`) on response bodies fires on anime filenames, French marketing copy, and unrelated platforms at population scale. Conjunctive matching (status_code + json_field + anchored body_contains) is required. All fingerprints below reflect this constraint.

---

**Shodan indexing note:** Port-constrained bare strings return 0 for most AI safety eval platforms. `port:15500` returns 730 but the port is shared — `http.html:"promptfoo"` (22) and `http.title:"promptfoo"` (17) are the precision signals. `port:1984 http.status:200` returns 3,061 (port shared). `http.html:"langsmith"` (96) is the LangSmith working query.

## Promptfoo

| Shodan Query | Verified hits | Notes |
|---|---|---|
| `http.html:"promptfoo"` | **22** | Best precision; HTML-scoped any port |
| `http.title:"promptfoo"` | **17** | Title-based |
| `port:15500` | 730 | Port-only; shared with other services — use HTML fingerprint to confirm |
| `http.html:"/api/evals"` | — | Promptfoo eval history endpoint path |
| `http.html:"promptfoo"` | 22 | Any port (reverse-proxied Promptfoo) |
| `hostname:"promptfoo"` | — | rDNS pattern |
| `ssl.cert.subject.cn:"promptfoo"` | — | TLS cert CN |

---

## LangSmith (self-hosted)

| Shodan Query | Verified hits | Notes |
|---|---|---|
| `http.html:"langsmith"` | **96** | Best signal; HTML-scoped any port |
| `http.title:"LangSmith"` | **67** | Title-based |
| `"langsmith"` | 42 | Bare-string any field |
| `port:1984 http.status:200` | 3,061 | Port shared; noisy — confirm with HTML fingerprint |
| `port:1984 "langsmith"` | 0 | Port-constrained bare string does not work |
| `http.html:"/info" port:1984` | — | LangSmith info endpoint (`json_field: instance_flags`) |
| `hostname:"langsmith"` | — | rDNS pattern |
| `ssl.cert.subject.cn:"langsmith"` | — | TLS cert CN |

---

## NeMo Guardrails

| Shodan Query | Notes |
|---|---|
| `port:8000 "nemo" "guardrails"` | NeMo Guardrails on default port |
| `port:8080 "nemo" "guardrails"` | Alt port |
| `http.html:"nemo-guardrails"` | Package identifier in source |
| `http.html:"/v1/rails/configs"` | NeMo Guardrails config endpoint path |
| `http.html:"/v1/rails/generate"` | Guardrails generation endpoint |
| `"NeMo Guardrails"` | Product name in any indexed field |
| `hostname:"guardrails"` | rDNS pattern |

---

## DeepEval

| Shodan Query | Notes |
|---|---|
| `port:8000 "deepeval" http.html:"/api/health"` | DeepEval server on port 8000 with health endpoint; conjunctive |
| `port:5000 "deepeval" http.html:"/api/health"` | DeepEval on port 5000 |
| `port:8080 "deepeval" http.html:"/api/health"` | DeepEval on port 8080 |
| `http.html:"deepeval" http.html:"confident"` | DeepEval + Confident AI co-occurrence; reduces FP vs single-word match |
| `http.html:"/api/test-cases"` | DeepEval test-case endpoint path |
| `hostname:"deepeval"` | rDNS pattern |
| `ssl.cert.subject.cn:"deepeval"` | TLS cert CN |

---

## Garak (NVIDIA adversarial harness — REST mode)

| Shodan Query | Verified hits | Notes |
|---|---|---|
| `http.html:"garak"` | 23 | **High FP risk** — fires on Japanese anime filenames, non-AI pages; CLI-dominant deployment means 0 confirmed REST servers at population scale. Use conjunctive match. |
| `http.html:"garak" http.html:"nvidia"` | — | Conjunction reduces FP rate |
| `http.html:"/api/v1/garak/version"` | 0 | Endpoint path not indexed by Shodan |
| `"garak_version"` | 0 | JSON field name not indexed |
| `hostname:"garak"` | — | rDNS; still check for false positives |

---

## Inspect AI

| Shodan Query | Notes |
|---|---|
| `port:7575` | Inspect AI default web port |
| `port:7576` | Inspect AI alt port |
| `port:7575 http.html:"inspect"` | Inspect on default port |
| `http.html:"/api/logs" port:7575` | Inspect AI log endpoint; JSON array response |
| `http.title:"inspect" port:7575` | Title-based |
| `"inspect-ai"` | Package identifier |

---

## Lakera Guard (self-hosted)

| Shodan Query | Notes |
|---|---|
| `port:8000 "lakera"` | Lakera Guard on port 8000 |
| `port:8080 "lakera"` | Lakera Guard on port 8080 |
| `http.html:"/v1/guard" port:8000` | Guard endpoint path; `Server: lakera` header expected |
| `"lakera" "guard"` | Product name conjunction |
| `hostname:"lakera"` | rDNS pattern |
| `ssl.cert.subject.cn:"lakera"` | TLS cert CN |

---

## Combined

| Shodan Query | Notes |
|---|---|
| `(port:15500 OR port:1984 OR port:7575 OR port:7576)` | Dedicated-port AI safety eval sweep |
| `(http.html:"promptfoo" OR http.html:"langsmith" OR http.html:"nemo-guardrails" OR http.html:"deepeval")` | Full product sweep |
| `(hostname:"promptfoo" OR hostname:"langsmith" OR hostname:"deepeval" OR hostname:"guardrails")` | rDNS sweep |
| `(ssl.cert.subject.cn:"promptfoo" OR ssl.cert.subject.cn:"langsmith" OR ssl.cert.subject.cn:"deepeval")` | TLS cert sweep |
