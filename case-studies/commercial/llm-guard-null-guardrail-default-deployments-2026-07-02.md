---
title: "LLM Guard Fail-Open Null-Guardrail: Unauthenticated Default Deployments With No Reachable Backend"
date: 2026-07-02
type: case-study
sector: commercial
tags: [llm-guard, protectai, ai-guardrails, fail-open, auth-on-default, cat-33, negative-result, methodology]
severity: low
---

# LLM Guard Fail-Open Null-Guardrail: Unauthenticated Default Deployments With No Reachable Backend

_NuClide Research · 2026-07-02 · Cat-33 AI Guardrails. Three unauthenticated Protect AI LLM Guard instances confirmed fail-open (all scanners return -1.0, is_valid=true on every input). Downgraded HIGH to LOW after a read-only downstream map found no externally reachable LLM behind any of them. Closed as a negative result with methodology gain. Host IPs redacted (last octet). LOW default-demo infrastructure._

## Summary

Three internet-exposed [LLM Guard](https://github.com/protectai/llm-guard) API instances were confirmed running in a fail-open state: scanner models are not loaded, so every scanner returns the sentinel score `-1.0`, the aggregate `is_valid` evaluates true for every input, and the API ships with `AUTH_TOKEN` empty so the `/scan/*` endpoints are unauthenticated. In this state the guardrail inspects nothing while certifying every prompt "clean."

The state is verified (200-with-data via a benign `POST /scan/prompt`), but the impact is contained. A read-only downstream map (tiptoe liveness + aimap fingerprint + direct verification) found no externally reachable LLM or agent backend behind any of the three guardrails. The deployments are most consistent with default/demo installs: a fresh LLM Guard container ships models-unloaded and token-empty, which is exactly the observed state. Severity was downgraded HIGH to LOW accordingly, and the survey closed as a negative result.

| Host | Port | Operator | State |
|---|---|---|---|
| `5.78.101.x` | 8000 | Hetzner (DE) | fail-open, unauth, persistent across 3 surveys |
| `177.126.247.x` | 8000 | WH Solutions (BR) | fail-open, unauth |
| `51.91.98.x` | 8001 | OVH (FR) | fail-open, unauth, net-new via facet-first |

## The vulnerability class

LLM Guard is a filtering proxy that scores each prompt/output with a stack of ML scanners (PromptInjection, Toxicity, Secrets, Anonymize, and others), each returning `0.0` (safe) to `1.0` (risky) against a threshold. When a scanner's model is not loaded, that scanner returns `-1.0` instead of a real score. Because `-1.0` is below every risk threshold, the aggregate verdict is:

```
is_valid = ALL(score < threshold)   ->   -1.0 < 0.5 == true   for every scanner
```

The safety property inverts on a boot-time condition nobody sees: absence-of-inspection becomes indistinguishable from passed-inspection in the response. The control fails **open**, not closed. Combined with the empty-default `AUTH_TOKEN`, any unauthenticated client gets `is_valid: true` on any input, including the prompt-injection and secret-exfiltration payloads the product exists to block.

```
POST /scan/prompt {"prompt":"<anything>"}
-> {"is_valid": true, "scanners": {"PromptInjection": -1.0, "Toxicity": -1.0, "Secrets": -1.0}}
```

## Why the severity is LOW, not HIGH

The severity of a bypassed control is set by what it protects. The downstream map found nothing reachable to protect:

- `5.78.101.x`: co-located services are a "Backup Manager" web app (catch-all: identical page on a nonsense path), a Portuguese login page, RabbitMQ management, and MySQL/Postgres/Redis (substrate, out of AI scope). No reachable LLM.
- `51.91.98.x`: co-located services are Gotenberg (a stateless PDF-conversion API) and a Node app. No reachable LLM.
- `177.126.247.x`: SSH and the guardrail port only. Standalone.

The bypass is real but reaches no backend. The most likely reading is abandoned default deployments rather than a production safety control silently degrading. No PII was read (restraint ethic); no downstream impact was demonstrated.

## Methodology notes (the real yield)

This survey's value is process, not hosts:

1. **Facet-first at harvest.** Running the Shodan `facet=port` distribution before the dork loop revealed the population runs on 443/8000/8001/80/8083, not just the documented default 8000. A default-port-only pass mislabeled half the live hosts "dark" and would have missed the only net-new host (`51.91.98.x:8001`). Population port distribution should drive the scan phase, not the platform's documented default.

2. **Null-scanner tell.** The fail-open state is invisible to a fingerprint. `GET /` returns `{"name":"LLM Guard API"}` and looks healthy; only `POST /scan/prompt` reveals the all-`-1.0` state. Fingerprint-only enumeration cannot see it.

3. **Catch-all collision false positives.** Automated fingerprinting matched three-plus unrelated AI platforms to single ports (a "Backup Manager" page matched RTP-LLM, Zep, Chatterbox, and Khoj simultaneously; a health-JSON endpoint matched both Meilisearch and Grafana; an SPA catch-all produced a false CRITICAL dcm4chee match). A nonsense-path control probe refutes each instantly. Rule: any port matching three or more unrelated service fingerprints is a catch-all until a nonsense-path probe proves otherwise.

## Remediation

1. Set `AUTH_TOKEN`; the empty default leaves the API open.
2. Fail closed: refuse to serve, or alert, if any scanner returns `-1.0` in production; verify models load at startup.
3. Do not expose the API port to the internet.

## References

- Protect AI LLM Guard: https://github.com/protectai/llm-guard
- LLM Guard docs: https://llm-guard.com
- NuClide auth-on-default thesis (Cat-33 AI Guardrails series)
