# Insight #93 — Pre-Assessment Squad Port Assumption Causes Systematic Population Under-Count (Candidate)

_NuClide Research · 2026-06-09 · Origin: Cat-Tabby survey, four-platform code-assistant straggler._

---

## Statement

A pre-assessment OSINT squad (Stage -1) that bakes its assumed default port into **every dork variant** systematically under-counts the actual platform population at Stage 0. The squad's port assumption inherits from a single source — usually the `--port` flag default in the upstream README quickstart — and propagates through basic/strict/version dorks alike, producing a coherent-but-wrong sub-population view.

The fix is mechanical: **every dork set must include at least one variant without a `port:N` constraint.** A platform that listens on the operator-default port (which often differs from the `--port` flag default, because operators follow the docker-compose recommendation rather than the binary flag) becomes invisible to a port-constrained dork set.

## Derivation

Cat-Tabby survey, 2026-06-09. Stage -1 squad-1 researched TabbyML's auth posture, deployment patterns, and Shodan fingerprint set. The squad correctly identified Tabby v0.11.0+ ships with `webserver` mode (a Next.js front-end) on port 8080 per the binary `--port` flag default, and produced these dorks:

- basic: `port:8080 "Tabby"` → 2 hits
- strict: `port:8080 http.html:"Tabby" http.html:"AI coding"` → 3 hits
- version: `port:8080 http.html:"Tabby" http.html:"swagger-ui"` → 0 hits

Total visible Tabby population per the squad's dork set: 5 hits maximum.

At Stage 0 the survey tested `http.title:"Tabby"` (no port constraint) as a sanity check after the squad's dorks returned suspiciously low population numbers. Result: **97 hits, 94 unique IPs.** Port distribution of the 94 hits:

| Port | Count | % of population |
|---|---|---|
| 9090 | 40 | 42.6% |
| 8000 | 11 | 11.7% |
| 443 | 8 | 8.5% |
| 80 | 7 | 7.4% |
| 9000 | 6 | 6.4% |
| 8080 | 5 | 5.3% |
| Long tail (9999, 8010, 12399, 8180, 2048, 9190, 8003, 9443, 9165, 8001, 39001, 8008, 9445, 9099, 3000) | 17 | 18.1% |

The squad's port:8080-constrained dork set caught 5/94 = **5.3% of the real population.**

The squad's reasoning was not incorrect — the Tabby binary `--port` flag default is genuinely 8080. But the **docker-compose quickstart** recommends mapping host port 9090 to container 8080. Operators copy the docker-compose quickstart rather than reading the binary's `--help`. The operator-default port (9090) and the squad-read flag-default port (8080) diverge — and the actual population follows the operator-default.

## Why this is a class of mistake, not a one-time miss

The same pattern would manifest on any platform where:

1. The binary's `--port` flag default differs from the operator-deployment-template default (docker-compose, Helm, Kubernetes manifest), AND
2. The Stage -1 squad's OSINT pass reads the binary flag rather than walking three or four real deployment configs

These conditions are common in the LLM/AI infrastructure space because docker-compose is the dominant deployment template and operators frequently set non-default port mappings to avoid collision with other services on the same host.

Examples of platforms where this pattern is plausible and worth re-testing at Stage 0:

- vLLM (`--port 8000` flag default; many docker-compose templates use 8080 or 8001)
- Ollama (`OLLAMA_HOST=:11434` is well-known but private deployments often run on 11435/11436/8080 behind reverse proxy)
- Text-Generation-WebUI (binary default :7860 vs docker-compose :5000/:7860 split)
- Langfuse (binary :3000 vs operator-deployed :3001 to avoid collision with Grafana on 3000)

## Action — mechanical fix at Stage -1

Every squad's dork output must include **at least one variant with no `port:N` constraint and no `http.html:` body anchor that requires a specific port**. This variant exists to *measure the cost of the port assumption*. The standard sanity-check pattern:

| Dork tier | Has port constraint | Purpose |
|---|---|---|
| basic | yes (squad-default) | Population at the assumed-default port |
| basic-unconstrained | **no** | Population across ALL ports → measures the assumption cost |
| strict | yes (squad-default) | Lower-FP version of basic at default port |
| version | yes | Version-disclosing cohort |

If `basic-unconstrained / basic > 5×`, the squad's port assumption is wrong. Re-derive the operator-default port from the docker-compose template and the survey corpus before continuing.

## Tooling

- `tome platforms <slug>` for the canonical per-platform dork set, written back by Stage -1 squads. After this survey, every tome platform JSON must carry a `basic-unconstrained` dork tier; current Cat-Tabby `tabby.json` was updated 2026-06-09 to include `http.title:"Tabby"` as the canonical basic dork (the previous `port:8080 "Tabby"` is retained as the version-cohort comparison).
- shodan-fetch in-page Promise.all (`evaluate_script` with the JS_FIRST_PAGE pattern) is the right primitive to fan out a basic-unconstrained dork — costs 0 query credits, returns the per-port distribution as a side effect of the cohort facet pull.
- aimap fingerprint `DefaultPorts[]` should be drawn from the *real distribution* (per Cat-Tabby tabby.json `port_distribution_2026_06_09`), not the squad's assumed default.

## Related

- Insight #15 (50% rule) — the dork-vs-real conversion rate floor. This insight extends #15 to a **distinct** failure class: #15 catches identity-FP at the matched-population level; #93 catches population-FN at the dork-coverage level.
- Insight #21 (port-first beats brand-dork for low-footprint platforms) — Cat-Tabby is the canonical example of this *plus* the squad-assumption variant. Without the unconstrained sanity dork, even the right brand string returns a port-blind under-count.
- Insight #14 (port selection follows operator intent, not IANA rank) — the operator-intent angle. #93 sharpens to: the operator's intent is encoded in the *docker-compose quickstart*, not the `--port` flag.

## Case study reference

`case-studies/commercial/cat-tabby-survey-2026-06-09.md` — Cat-Tabby Code-Assistant Stragglers Survey.
