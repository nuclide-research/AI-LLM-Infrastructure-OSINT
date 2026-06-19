# Lane C — Corpus Contamination Audit (LBot deception fleet)

_NuClide Research · 2026-06-19 · read-only audit, no corpus files modified_

## Question

The Cat-Langflow LBot fleet poisons two things at once: `http.title:` population dorks
(rotating fake titles per request) AND scanner success-matchers (catch-all 200 JSON stuffed
with `code`/`data`/`message`/`registerEnabled`-class fields, fake versions, fake tokens,
`uid=0(root)`, `proof_file=/tmp/a`). How much of the existing NuClide corpus inherited
counts from this poison without a functional verification step?

## Headline

The corpus is NOT freshly contaminated. The fleet was ALREADY documented (Insight #32,
2026-05-18 Jetson survey) and 38 of 85 title-dork case studies cite fleet-awareness. The
real debt is twofold:

1. **The LBot fleet is the SAME fleet family as Insight #32's "Fleet B."** Confirmed by
   `/16` overlap: LBot canned-page IP `101.200.142.223` sits inside the `101.200.0.0/16`
   Aliyun range named as Fleet B's home. Same rotating-title technique, same ~135-137KB
   canned page, same multi-ASN spread. Langflow/Gitea/Ghost is the fleet's 2026-06 emulation
   set; Shinobi/GitLab was its 2026-05 set. The corpus's own Insight #32 open question
   ("how many other platform classes does this fleet emulate?") now has Langflow as a
   confirmed answer.

2. **Insight #32's mandated cross-survey re-check (item #3) was never executed.** It named a
   re-verify list (Triton, Frigate, Shinobi, OpenHands, Ollama, LLM-gateways) but no
   reclassification artifact exists, and the list predates the FLAG-READ population surveys
   (Dify/Open-WebUI/RAGFlow/FastGPT) that are the most matcher-exposed. That re-check is the
   load-bearing follow-up.

## Contamination vectors (two distinct ones)

```
VECTOR A — TITLE-DORK POPULATION INFLATION
  Fleet rotates fake <title> per request to match many http.title: dorks at once.
  Impact: the RAW "indexed hits" number (Stage 0) is inflated by fleet members.
  Defense already in corpus: tome strict dork adds http.html body anchor; most surveys
  drop to a live/body-probed subset before reporting a "confirmed" count.
  Residual risk: surveys that report the RAW indexed number as the finding.

VECTOR B — SUCCESS-MATCHER POISONING  (the dangerous one)
  Fleet serves catch-all 200 JSON on ANY path, wrapping these keys verbatim:
    code, data, message, status, success, token, accessToken, refreshToken,
    csrfToken, CSRFToken, userId, role, privileges, version, commit, registerEnabled-class
  A survey whose "confirmed/open" verdict = "did this JSON field equal X" matches the
  fleet's forged field with no way to tell it from a real instance.
  Defense: confirm the capability FUNCTIONALLY (token authenticates a real action; nonsense
  path must NOT 200), not by reading a flag.
```

## Ranked list — potentially-contaminated prior surveys

Ranked by (matcher exposure to Vector B) x (population size / finding stakes).

### TIER 1 — RE-VERIFY (flag-read matcher the fleet forges, large or high-stakes population)

| # | Survey | Count at risk | Matcher (what was read) | Why exposed | Vector |
|---|--------|---------------|-------------------------|-------------|--------|
| 1 | **ragflow-population-survey-2026-06-06** | **618 REGISTER_OPEN of 709 live (87.2%)** | `GET /v1/system/config` -> `{"code":0,"data":{"registerEnabled":1},"message":"success"}` | Fleet's mega-JSON contains `code`,`data`,`message`,`Register`-class keys AND serves catch-all 200. Dork was BARE `http.title:"RAGFlow"` (tome strict adds `http.html:"infiniflow"`, not used). Register confirmed by FLAG, never by an actual register POST (restraint, correctly). | A+B |
| 2 | **sub2api-population-2026-05-19** | 25 confirmed of 7,720 indexed | inner `"code":0` status flag (HTTP-200-wrapped) | Exact `"code":0` wrapper the fleet forges. Title is generic gateway. | A+B |
| 3 | **fastgpt-population-survey-cat34-2026-06-08** | REGISTER_OPEN/SIGNUP_OPEN class | register/signup config flag read | Same flag-read class; FastGPT title + config JSON forgeable. | A+B |
| 4 | **safety-guardrail-population-survey-2026-05-19** | 538 confirmed, SIGNUP_OPEN subset | signup-open config flag | Multi-title dork (`Guardrails`,`LiteLLM`...), flag-read verdict. | A+B |

### TIER 2 — SPOT-CHECK (flag-read but small/low-rate, so fleet inflation is bounded)

| # | Survey | Count | Note |
|---|--------|-------|------|
| 5 | dify-population-survey-2026-06-06 | 6 SIGNUP_OPEN (0.6%), 939 config-disclosure | Matcher `/console/api/system-features` `is_allow_register` is flag-read and forgeable, BUT signup-open rate is tiny (0.6%); the 939 "config-disclosure" number is the inflatable one. Re-anchor the 939 on a Dify-unique body string + nonsense-path negative. |
| 6 | openwebui-population-survey-2026-06-06 | SIGNUP_OPEN 11.1% (2,689/5,097-class) | Flag-read signup; moderate rate. Open-WebUI title is high-collision. |
| 7 | agenta-llmops-observability-survey-2026-05-22 | 14 confirmed, SIGNUP_OPEN | small n, low stakes. |
| 8 | langgraph-server-survey-2026-05-25 | 16 of 499 | flag-read, small confirmed set. |
| 9 | visorbishop-iter8-survey-2026-05-11 (Prefect) | 46,048 hits cited | raw-hits number cited; confirm the reported figure is hits not "confirmed". |
| 10 | agent-memory-population-survey-2026-05-16 (Zep) | 70 confirmed | flag-read; small. |
| 11 | experiment-tracking-population-survey-2026-05-16 | 2 confirmed | n=2; negligible. |
| 12 | khoj-survey-2026-06-08 | 7 confirmed of 411 | status-code class; small. |

### TIER 3 — RE-CHECK COLLECTION/PORT COUNTS (different fleet, same family, NOT title)

| # | Survey | Count at risk | Vector |
|---|--------|---------------|--------|
| 13 | **milvus-attu-survey-2026-05** | 763 reachable / 303 Attu-open / 593 REST-unauth / 330 populated / **1,224- and 704-collection findings** | Survey has NO honeypot/fleet de-dup (0 mentions). Its SIBLING surveys (milvus-tier2, ollama-tier2) explicitly documented 393 AS63949 fleet hosts forging `/v2/vectordb/collections/list` with `accessToken`/`csrfToken`/`proof_file:/tmp/a`/`uid=0(root)` on port 19530. The collection-count findings may include fleet-forged collection lists. RE-CHECK the 763 against the 393 fleet IP set. |

### NOT CONTAMINATED (verified resistant — no action)

- **kubeflow-population-survey-2026-06-08** — 619 title hits, but verdict anchored on
  `/pipeline/apis/v1beta1/experiments` returning a real `experiments` key; 560 explicitly
  labeled "Shodan-title FP". Model survey for resistance.
- **gradio-port-7860-survey-2026-05** — discovery was masscan on `port:7860` (NOT a title
  dork) + endpoint fingerprint; the one "fully unauth" Langflow used `/api/v1/users/whoami`
  returning the actual superuser account (functional). The other 8 classified by
  `auto_login` status code — re-confirm those 8 are real Langflow (`package":"Langflow"`),
  but the discovery path is fleet-resistant.
- **langgraph-studio-population-survey-2026-06-07**, **openhands/comfyui/meilisearch/
  label-studio/argilla/chainlit (2026-06-08)**, **tabby (2026-06-09)** — STRONG functional
  anchors, fleet-aware where relevant.
- The 47 "no-fleet-mention" surveys are mostly BODY-PROBE anchored (live JSON from a
  platform-unique path); fleet mention absent != matcher weak. Only the FLAG-READ subset
  above is genuinely exposed.

## Most-at-risk platforms (tome cross-check)

Every title-dorked tome platform HAS a body-verified `strict` tier; the exposure is when a
survey used `basic` (bare title) and stopped at a flag. Highest-collision titles the fleet
is most likely stuffing next, by generic-title + JSON-config-flag matcher:

```
RAGFlow      basic=http.title:"RAGFlow"        strict adds http.html:"infiniflow"   <- USE STRICT
Dify         basic=http.title:"Dify"           /console/api/system-features flag    <- functional-confirm
Open WebUI   basic=http.title:"Open WebUI"     high-collision title                 <- USE STRICT + favicon
FastGPT      (cat34)                            register flag                        <- functional-confirm
LibreChat    basic=http.title:"LibreChat"      strict adds favicon + port:3080
MaxKB / QAnything / Quivr / Casibase           generic title + config-flag class
Gitea/Ghost  (NOT in tome AI corpus)           fleet's CURRENT primary emulation    <- any future Gitea/Ghost title dork is pre-poisoned
```

## Scope estimate

- Title-dork case studies total: **85**
- Cite fleet-awareness: **38** (45%) — the methodology already propagated
- No fleet mention: **47** — but most are BODY-PROBE anchored, not matcher-weak
- **Genuinely flag-read AND fleet-forgeable: ~12 surveys (Tiers 1-3 above)**
- **Should be re-verified now: 4 (Tier 1) + 1 (Tier 3 milvus-attu) = 5 priority re-verifications**
- Of those, ONE carries real disclosure stakes: **RAGFlow 618 REGISTER_OPEN.**

## Prioritized re-verification recommendation

```
P0  RAGFlow 618 REGISTER_OPEN
    Re-probe the 618 with the LBot discriminator pair:
      POSITIVE: /v1/system/config returns RAGFlow-unique shape AND a RAGFlow-unique body
                marker elsewhere (http.html:"infiniflow" / RAGFlow asset path)
      NEGATIVE: GET /v1/<random-nonsense> must NOT return 200 (catch-all detector)
      FUNCTIONAL (optional, scope permitting): registerEnabled=1 means the register form
                renders — confirm the RAGFlow SPA loads, not a 135KB canned blob.
    Cross-ref the 618 IPs against harvest-raw.txt (93 LBot IPs) + the 393 AS63949 set.
    Expected outcome: real RAGFlow REGISTER_OPEN count is likely LOWER than 618; report the
    delta as the corrected figure. This is the only re-verify with disclosure weight.

P1  milvus-attu 763 / collection-count findings
    Diff the 763 reachable IPs against the 393 AS63949 fleet IP list already in the
    milvus-tier2/ollama-tier2 surveys. Any overlap host's collection list is forged.
    Re-state collection counts (1,224 / 704) excluding fleet hosts.

P2  sub2api / fastgpt / safety-guardrail (Tier 1 small-n)
    Re-anchor each on a nonsense-path negative guard. Low stakes; batch as one pass.

P3  Codify
    - Promote the LBot==Fleet-B link into Insight #32 as confirmed (close its open question
      for the Langflow/Gitea/Ghost emulation set).
    - New procedural rule (Insight #32 item #2 strengthened): for ANY config-flag matcher
      (registerEnabled / is_allow_register / SIGNUP_OPEN / "code":0), the verdict requires a
      nonsense-path NEGATIVE guard in the same probe run. Flag-read alone is now insufficient.
    - Add `body_not_contains` fleet markers (stok, proof_file, 5bda17e7 commit, the "jack"
      JWT shape) to aimap as a global negative conjunct for the title-dork platform class.
```

## One-line bottom line

The fleet did not silently corrupt the corpus — it was already named — but the
config-flag population surveys (RAGFlow 618 chief among them) inherited a matcher the fleet
forges, and Insight #32's mandated cross-survey re-check was never run. Run it now, starting
with RAGFlow.
