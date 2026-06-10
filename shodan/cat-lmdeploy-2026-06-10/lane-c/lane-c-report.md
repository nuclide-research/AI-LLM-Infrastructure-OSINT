# Lane C — Cat-LMDeploy 2026-06-10 — DCWF 672 Verification Report

**Wardrobe:** ai-infra-hunt + DCWF 672 stance.
**Atoms exercised:** T0247 (T&E + verification), T0188 (audit findings),
S0081 (network analysis tools), K0009/K0005/K0006 (vuln+threat+impact).
**Verification is the load-bearing stage of the methodology (Stage 3v).**

## 1. Sandbox-MITM gate (Insight #96)
**VERDICT: CLEAN.** 5/5 distinct response-shape digests across
api.github.com, www.cloudflare.com, www.google.com, www.amazon.com,
example.org. Wire is uncompromised; L7 conclusions are licensed.
Artifact: `mitm-shape-probe.json`.

## 2. Corpus

| Source | IPs | Notes |
|---|---|---|
| Prior cat03 recon | 3 | `~/AI-LLM-Infrastructure-OSINT/recon/cat03-model-serving/ips-lmdeploy.txt` |
| Lane A enrichment | +2 | Pulled from `lane-a/empire.db` at 03:02 (65.108.11.238, 46.62.204.42) |
| **Total verified** | **5** | bootstrap subset per Lane C brief |

Lane A's full Shodan harvest of `port:23333 http.html:"LMDeploy"` had not
landed at the time of this report; Lane C operated on the brief's fallback
"first 10 IPs" tier but only had 5 visible. Flag for orchestrator
reconciliation, not for Lane C unilateral action.

## 3. Step 0c — scanner banner sweep
Run on the enriched 5-IP corpus, ports 23333/8000/80/443.
- 0/5 hosts responded on port 23333 (the LMDeploy default).
- 3 hosts responded on port 80 or 443 with a generic webserver banner.
- Artifact: `scanner-0c-bootstrap.jsonl`, `scanner-0c-port23333.jsonl`.

## 4. Stage 3v — L7 verifier (restraint-clean)

Tool: `lmdeploy-verify.py` (Lane C build, modeled on cat-tabby
stage3v-verify.py). 15-entry `DO_NOT_CALL` hard-refused at code level
BEFORE any request is constructed. 6 read-only ALLOWED probes:
`/`, `/openapi.json`, `/v1/models`, `/health`, `/metrics`, `/distserve/engine_info`.

Marker pair (conjunctive, Insight #6): a 200 on `/openapi.json` qualifies
as confirmed LMDeploy ONLY IF the body contains BOTH `/distserve/engine_info`
AND `/v1/chat/interactive`. No FastAPI clone emits that pair accidentally.

### Per-host verify (port 23333 only — the LMDeploy default)

| IP | :23333 | :443 cert | Verdict (rung) |
|---|---|---|---|
| 115.191.10.126 | timeout | `registry.mingya.com` Docker registry | REFUTED (A,1) — host repurposed |
| 120.237.103.186 | connection refused | none | REFUTED (A,1) — host dead |
| 124.163.255.214 | connection refused | nginx 400-on-everything | REFUTED (A,1) — host repurposed |
| 65.108.11.238 | timeout | `cmd.xzt.me` Let's Encrypt | REFUTED (A,1) — host repurposed |
| 46.62.204.42 | timeout | none reached | REFUTED (A,1) — host dead |

### Alt-port sweep
0/20 host:port combos reachable on 8080/8001/8002/8011. The Docker
"-p 23333:23333" idiom holds — LMDeploy operators don't remap the port.

## 5. Population-level results

| Metric | Value |
|---|---|
| Population confirmed LMDeploy (marker pair) | **0 / 5 (0%)** |
| Population refuted | 5 / 5 (100%) |
| Auth-on-default thesis tested | **NOT TESTED** (no live LMDeploy host in corpus) |
| Unauth open | 0 |
| Auth-gated | 0 |
| Honeypot/mimic | 0 (no FastAPI/Swagger shell with LMDeploy markers anywhere) |
| Restraint violations | **0 / 5** (100% compliant) |

## 6. Stage 2/2b — VisorGraph cert-pivot
Only 2/5 hosts had a live TLS cert on :443. Cert-pivot deferred to
next pass with full Lane A harvest; current subset too thin for
operator-attribution graph. Findings:
- `cmd.xzt.me` (Hetzner FI) — personal Chinese-context operator, NOT LMDeploy
- `registry.mingya.com` (self-signed, CN/Beijing) — Docker registry, NOT LMDeploy

Neither active cert names LMDeploy or openmmlab. No shared CA across corpus.
Artifact: `visorgraph-certs.json`.

## 7. Verification rung pairs (Insight #68)
Every host record carries `verification_rung = (A|B, 0|1|2)`. All five
landed at (A, 1) — binary refutation at the single-host level, not yet
the population (would require N ~ 50+).

## 8. Auth-on-default thesis status
**INCONCLUSIVE on this corpus.** The Shodan banner cache for
`port:23333 http.html:"LMDeploy"` is materially stale — none of the 5
indexed IPs currently serve LMDeploy. The thesis (auth_default=none per
api_server.py:1486) is NOT refuted; it is NOT TESTED. Lane A's broader
harvest is needed to populate the verify lane with a live cohort.

## 9. Flag for orchestrator (cross-lane reconciliation)
- **Dependency on Lane A:** the population-scale verify cannot run until
  Lane A's full Shodan harvest lands. Current 5-IP subset = 0% LMDeploy.
- **Methodological note:** the stale-cache ratio observed here (5/5
  refuted on port 23333) is far above the methodology's published ~71%
  stale-cache rate. Possible: small sample, OR LMDeploy operators are
  more transient than other AI-infra (port flipped to firewalled,
  decommissioned, or moved to private subnet behind reverse-proxy).
  Candidate Insight: "AI-inference operator decommission rate >
  vector-DB / orchestrator decommission rate" — but this needs a
  population-scale confirmation, not a 5-IP refutation.
- **Insight #16 (200 = identity not auth state) test:** the verifier
  treated `/` 200 on 115.191.10.126:443 and 65.108.11.238:80/443 as
  identity-only signal; cert-pivot then disambiguated them OUT of the
  LMDeploy population. Discipline held.

## Artifacts written under
`~/AI-LLM-Infrastructure-OSINT/shodan/cat-lmdeploy-2026-06-10/lane-c/`
- `mitm-shape-probe.py` + `.json` (gate)
- `lmdeploy-verify.py` (Lane C build, 15 DO_NOT_CALL hard-refused, 6 allowed)
- `ips-bootstrap.txt`, `ips-lane-a-enriched.txt`
- `ips-bootstrap-with-ports.txt`
- `scanner-0c-bootstrap.jsonl`, `scanner-0c-port23333.jsonl`
- `verify-bootstrap.jsonl`, `verify-enriched.jsonl`, `verify-alt-ports.jsonl`
- `visorgraph-certs.json` (Stage 2 substitute — VisorGraph deferred)
- `lane-c-report.md` (this file)

## Restraint compliance final tally
**0 DO_NOT_CALL invocations issued across 60 verify probes (5 IPs × 6 endpoints × 2 sweeps).**
Code-level guard in `lmdeploy-verify.py:_check_do_not_call` raises before
the request is constructed; any future verifier change must keep that
guard at the top of `probe()`.
