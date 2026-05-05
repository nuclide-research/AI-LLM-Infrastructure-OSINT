# AI Safety Evaluation / Red-Team Self-Hosted — Cross-Cloud Survey (2026-05)

_NuClide Research · 2026-05-04 (in progress)_

> **Status:** Methodology + scaffolding complete. Discovery scan in progress. Synthesis section will fill as data lands.

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

_(populated as the masscan + probe pipeline completes)_

| Source | Hits | Confirmed | Auth-on | Auth-off |
|---|---|---|---|---|
| Combined tier-2 (3 providers) | TBD | TBD | TBD | TBD |

### By platform

| Platform | Confirmed | Auth-off | Notes |
|---|---|---|---|
| Promptfoo | TBD | TBD | TBD |
| LangSmith self-hosted | TBD | TBD | TBD |
| DeepEval | TBD | TBD | TBD |
| Garak (web wrapper) | TBD | TBD | TBD |

---

## Notable findings

_(populated)_

---

## Honest negative space

- **Garak is primarily CLI** — only operators who explicitly wrap it in a web UI will be visible. The "no Garak found" finding may simply mean operators haven't web-exposed it, not that they aren't running it.
- **Patronus and AILuminate** are managed/SaaS-mostly; self-host populations are thin.
- **LangSmith self-hosted** typically requires LangChain Plus license; paying customers tend to deploy with auth correctly.

---

## See also

- [`SYNTHESIS-2026-05.md`](SYNTHESIS-2026-05.md)
- [`FUTURE-SURVEYS.md`](FUTURE-SURVEYS.md)
- [`data/aisafety-probe.py`](../../data/aisafety-probe.py)
