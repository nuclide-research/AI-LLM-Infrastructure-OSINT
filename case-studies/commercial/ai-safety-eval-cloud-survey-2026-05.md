# AI Safety Evaluation / Red-Team Self-Hosted — Cross-Cloud Survey (2026-05)

_NuClide Research · 2026-05-04 (in progress)_

> **Status:** Discovery + probe complete (2026-05-04). 6 confirmed across the targeted ports — smallest population in the 6-survey series. **AI safety eval is a thin self-host market** in the cheap-cloud tier, but the one Garak hit is novel.

---

## Premise

AI safety evaluation and red-team frameworks (Promptfoo, Garak, DeepEval, Patronus, AILuminate, LangSmith) are themselves attractive exposure targets — their finding-corpus contains adversarial prompts, jailbreak techniques, eval results, and sometimes model behavior under attack. A red-team server's index of "things that worked" is direct competitor intelligence + a prompt-injection ammo dump.

The platforms in scope:

| Platform | Default port | Tier | Auth posture |
|---|---|---|---|
| **Promptfoo evaluators** | 15500 | A* | Auth optional, off by default in standalone mode |
| **Garak** (NVIDIA) | varies | A* | CLI-mode primary; some operators wrap in web UI |
| **DeepEval / Confident AI** | varies | A* | Self-host has no auth concept |
| **LangSmith self-hosted** | 1984 | C | Auth required by default (newer deploys) |
| **AILuminate** (MLCommons) | varies | varies | Limited self-host |
| **Patronus AI** | varies | C | Managed-mostly, API token required |

Auth-on-default thesis: Promptfoo / Garak / DeepEval (no auth concept in default standalone) → expect 100% unauth at the population level. LangSmith has auth-on-default; expect low unauth rate.

---

## Methodology

### Discovery

Same tier-2 cross-cloud pattern: Scaleway 7 + OVH 33 + Linode 36 = 76 prefixes ≈ 3.55M IPs (1,017 deduped CIDRs).

**Ports scanned:** 1984 (LangSmith), 15500 (Promptfoo). **Ports 5000 + 8000 hits reused** from MCP and LLM Gateway scans (Promptfoo, Garak, DeepEval often bind to common ports).

### Probe

`data/aisafety-probe.py` is a multi-platform fingerprint prober. Per (ip, port) it tries port-specific handlers:

| Platform | Probe sequence | Match signature |
|---|---|---|
| **Promptfoo** | `GET /api/health` → `GET /api/results` or `GET /` | health JSON + `promptfoo` marker in body or HTML |
| **LangSmith** | `GET /api/info` | `langsmith` or `langchain` in body |
| **DeepEval** | `GET /api/health` | `deepeval` or `confident` in body |
| **Garak** | `GET /` | `garak` in HTML root |

For each confirmed instance, capture: platform, version, eval count (if reachable unauth), auth posture.

### Filters

- **AS63949 honeypot fleet** filter applied
- **Cross-survey overlap** — port 5000+8000 hits already in MCP/LLM-Gateway scans; deduped at probe
- **Auth-required instances** — recorded but excluded from "exposed eval data" enumeration

### Threat-class taxonomy

| Class | Risk |
|---|---|
| **Adversarial prompt corpus** | HIGH — operator's curated jailbreak/attack library disclosed |
| **Eval-result history** | MEDIUM — what worked against which models, with timestamps |
| **Test-case generators** | MEDIUM — if generators include proprietary prompts |
| **Model behavior captures** | MEDIUM — sometimes captured outputs under adversarial prompts |
| **Project-name / tag disclosure** | LOW-MEDIUM — operator/team identification |

---

## Discovery results

Cross-cloud snapshot. Masscan ports 1984 (LangSmith), 15500 (Promptfoo); ports 5000 + 8000 reused from prior scans.

| Platform | Confirmed | Auth-off | Notes |
|---|---|---|---|
| **DeepEval / Confident AI** | **5** | 4/4 unauth at `/api/health` | Hosts at `149.202.183.53:8000`, `151.80.57.247:5000`, `37.59.107.238:5000`, `51.75.89.218:8000`, `51.83.34.173:8000` (5 records — one host on multiple ports). All returned the deepeval/confident marker in `/api/health`. |
| **Garak (NVIDIA)** | **1** | Auth-off | `149.56.22.24:5000` — `garak` marker in HTML root. **Unusual finding: Garak is normally CLI-only.** This operator has wrapped it in a web UI and exposed it. |
| Promptfoo | 0 | — | None confirmed in the tier-2 sample. Promptfoo's standalone server isn't typically deployed on cheap VPSes. |
| LangSmith self-hosted | 0 | — | None confirmed. LangSmith deployments are predominantly on the SaaS tier or in enterprise K8s, not cheap VPSes. |
| Patronus / AILuminate | 0 | — | Managed-mostly; no self-host population to find. |

The total 5-record population is the smallest of any survey in this 6-category series — by an order of magnitude. **AI safety / red-team self-hosted has a thin commercial-VPS market.** Operators interested in eval/red-team tooling tend to: run them locally as CLIs; use the SaaS versions (Patronus, Confident AI cloud); or deploy in enterprise/internal infrastructure that this scan doesn't surface.

---

## Notable findings

### F1 — Garak self-host with web UI exposed (HIGH novelty — `149.56.22.24:5000`)

Garak is NVIDIA's adversarial LLM testing harness — it generates jailbreak prompts, prompt-injection variants, model-fingerprinting payloads, and tests them against a target LLM to score robustness. Garak's primary distribution is a Python CLI; finding one with a web UI bound to a public IP suggests either:

- An operator has wrapped Garak in a custom Flask/FastAPI front-end to make it accessible to a team
- A research / red-team firm running Garak as a service for clients
- A demo / education deployment

If the web UI exposes the **finding-corpus** (Garak's persisted attack-prompt + result database), this is direct competitor intelligence for adversarial-AI researchers — every prompt that worked against which model, scored. The probe so far has only confirmed the platform identity; deeper probing would extract the actual run-history.

### F2 — DeepEval / Confident AI self-host: 4 instances

DeepEval is the open-source companion to Confident AI's hosted eval platform. Operators self-deploying DeepEval typically run it for internal LLM-app QA — what prompts pass the eval suite, which fail, which models are being benchmarked.

The 4 confirmed are scattered across OVH ranges (`149.202.x`, `151.80.x`, `37.59.x`, `51.75.x`, `51.83.x`) — no fleet pattern, looks like 4 independent operators each running their own instance.

### F3 — Negative finding: Promptfoo + LangSmith zero in cheap-cloud tier

Both have well-defined self-host deployment paths and active commercial tooling, but zero hits in 1,017 prefixes scanned. Two interpretations:

1. The fingerprint endpoints I probed (`/api/health` for both) require auth and the probe got 401/403 — the `try_promptfoo` and `try_langsmith` handlers gate confirmation on positive content match, so auth-required hosts don't get counted
2. Genuinely thin self-host populations on cheap-VPS infrastructure

Likely a mix. Future surveys could add `/openapi.json` enumeration to catch auth-required hosts that still leak the platform identity through the route-map (the same finding pattern as the RAG framework survey's 51% openapi.json leak rate).

### F4 — Cross-tier auth-posture observation

AI safety eval tooling sits between two of the cross-tier patterns documented in SYNTHESIS-2026-05:

- **DeepEval / Garak (4+1)** ship as developer tools without auth concept → reproduces the auth-off-default thesis of the inference-server tier
- **LangSmith / Patronus (0 confirmed)** ship as commercial products with auth-on by default → operators keep that default

The split tracks with the "engineering tooling vs commercial product" distinction — same pattern visible across the entire 2026-05 survey series.

---

## Honest negative space

- **Population is small** (5 hosts at snapshot). Any conclusions are necessarily provisional.
- **CLI-only deployment is the dominant path** for Garak and Promptfoo — their self-host server modes are minor compared to direct command-line use. Network scanning catches only the subset that operators have wrapped in HTTP servers.
- **Probe handlers may underreport** — both `try_promptfoo` and `try_langsmith` require the platform marker in the response body, so auth-required deployments that return 401 without the marker fall through to "not detected" rather than "auth-on."

---

## See also

- [`SYNTHESIS-2026-05.md`](SYNTHESIS-2026-05.md) — auth-posture-by-tier comparison
- [`browser-agent-cloud-survey-2026-05.md`](browser-agent-cloud-survey-2026-05.md) — sibling survey; cross-references the same Garak host independently confirmed in our scan-port overlap
- [`data/aisafety-probe.py`](../../data/aisafety-probe.py) — discovery probe

## Honest negative space

- **Garak is primarily CLI** — only operators who explicitly wrap it in a web UI will be visible. The "no Garak found" finding may simply mean operators haven't web-exposed it, not that they aren't running it.
- **Patronus and AILuminate** are managed/SaaS-mostly; self-host populations are thin.
- **LangSmith self-hosted** typically requires LangChain Plus license; paying customers tend to deploy with auth correctly.

---

## See also

- [`SYNTHESIS-2026-05.md`](SYNTHESIS-2026-05.md)
- [`FUTURE-SURVEYS.md`](FUTURE-SURVEYS.md)
- [`data/aisafety-probe.py`](../../data/aisafety-probe.py)
