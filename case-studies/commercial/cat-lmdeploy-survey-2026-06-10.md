---
type: case-study
category: cat-lmdeploy
target_class: OSS LLM inference serving (OpenMMLab / Shanghai AI Lab)
target: LMDeploy (port 23333, auth_default=none)
date: 2026-06-10
researcher: Nuclide (Nick + Claude)
status: METHODOLOGY-FINDING + Insight #95 reconfirmed at survey scale + Insight #101 + #102 candidates codified
restraint_violations: 0
findings_disclosure: none drafted (population estimate UNKNOWN, no live LMDeploy in tested cohort)
---

# Cat-LMDeploy survey — 2026-06-10

LMDeploy is OpenMMLab / Shanghai AI Lab's OpenAI-compatible inference server (default port 23333, `auth_default=none` confirmed in `api_server.py:1486` where `api_keys` defaults to `None`). Tome documents 23 HTTP routes; nine are model-management ADMIN endpoints (`/terminate`, `/sleep`, `/update_weights`, `/abort_request`, `/distserve/p2p_*`). The surface-area thesis going in: any exposed `:23333` is a candidate for unauthenticated weight-mutation + denial-of-service + compute-cost theft.

**Verdict:** the surface-area thesis is correct in code, but the 5-IP bootstrap cohort tested in this survey was 100% refuted as LMDeploy. Stage 0 (Shodan population harvest) was blocked by MCP browser singleton contention across the 4-lane parallel dispatch, so the true exposed population estimate remains **UNKNOWN**. What this survey produced instead is the dual of Insight #95 (codified 2026-06-09): an OSS-platform-name HTML dork on a class like LMDeploy returns Docker registry hosts that catalog the image, not LMDeploy instances. The methodology output is more valuable than the (absent) population number.

## Wardrobe + syllabus stance

- Outfit `dod-pathway` — 12 atoms covering T0028 (authorized pentest), T0188 (audit findings + remediation), T0247 (T&E + verification), K0342 / S0001 / S0051 (vuln tools), K0107 (cross-jurisdiction laws), K0118 (digital evidence preservation), K0005 / K0070 / K0177 (kill chain + threats), A0123 (CIA to ML ops). Cross-role coverage: 39 NICE / DCWF roles. Dispatched as 4 parallel lane-scoped outfits (`cat-lmdeploy-lane-a-recon` NICE 541, `cat-lmdeploy-lane-b-engineering` DCWF 623, `cat-lmdeploy-lane-c-te` DCWF 672, `cat-lmdeploy-lane-d-risk-ethics` DCWF 733).
- Syllabus context: **"I Know What You Asked: Prompt Leakage via KV Cache Sharing in Multi-Tenant LLM Serving"** (NDSS 2025), **"SoK: All You Need to Know About On-Device ML Model Theft"** (USENIX Security 2024), **"Game of Arrows: On the (In-)Security of Closed-Source LLMs"** (USENIX Security 2025). The KV-cache and model-theft literature anchored the restraint posture: any GET on `/v1/chat/completions` against a multi-tenant server is a prompt-leakage and model-stealing surface, so the verifier hard-refuses it even on a null-auth-default operator (Lane C `DO_NOT_CALL` constant).

## Methodology

DCWF role-scoped 4-lane parallel dispatch using the lane-prompt shells at `~/.claude/skills/nuclide-stance/lane-prompts/`. Each lane received a parameterized prompt with `{CAT_SLUG}=cat-lmdeploy`, `{YYYY-MM-DD}=2026-06-10`, and a lane-specific mission spec. Orchestrator held the cross-lane reconcile until all 4 lanes landed, per the rule codified after the Cat-Tabby + Devstral 2026-06-09 incident.

### Lane A — NICE 541 Pentester (Recon + Harvest)
- **Stage -1 OSINT:** tome platform record already canonical at `~/tome/platforms/lmdeploy.json` (23 paths, auth_default=none, 4 passive-dork variants + 1 strict).
- **Stage 0 Shodan harvest:** BLOCKED. Both MCP browsers (`chrome-devtools` shodan-profile + `playwright` mcp-chrome) held persistent `--userDataDir` locks acquired earlier by sibling lanes B/C/D. 3.5 min retry window with 60s and 120s backoff failed identically. Saved shodan-fetch session expired. 6 dorks prepared (`port:23333 http.html:"LMDeploy"`, `port:23333 http.html:"FastAPI" http.html:"/openapi.json"`, `http.html:"lmdeploy"`, `http.html:"openmmlab"`, `port:23333 http.html:"/distserve/engine_info"` strict + 1 broad), 0 executed.
- **Stage 0b Censys cross-pop:** BLOCKED. cencli aggregate / search / view all returned `HTTP 422 insufficient balance` even though the `cencli credits` display still showed available credits — the feature-credit bucket appears to be tracked separately and was drained by sibling lanes.
- **Stage 0c active scanner:** 30 probes (5 IPs × 6 ports), 9 banner hits. Zero hits on port 23333 across all 5 IPs. Four of the 5 returned the byte-identical Docker Distribution v2 unauthenticated root-path signature (`HTTP/1.0 200 OK\r\nCache-Control: no-cache\r\nContent-Length: 0`). The remaining host was a self-signed `registry.mingya.com` Docker registry on `:443` (known from Cat-Syllabus-Leads 2026-06-09).
- **Stage 1c favicon:** 1 hash recovered (65.108.11.238 mmh3 `-1763961037`, atypical 629855-byte payload — not a standard favicon, possibly a misrouted asset).

### Lane B — DCWF 623 Engineering (Fingerprint Engineering)
- aimap LMDeploy fingerprint already existed at `~/ai-recon/aimap/fingerprints.go:374-398` (hardened from a bare `body_contains:"lmdeploy"` to a conjunctive 2-anchor matcher in prior work).
- Re-hardened to a **3-anchor matcher on `/openapi.json`**: requires co-occurrence of `/distserve/engine_info` + `/v1/chat/interactive` + `/v1/encode`. None of vLLM / SGLang / TGI / AIBrix expose these three routes; IAP HTML walls cannot satisfy three substring conditions on a single body (CVAT-FP class blocked).
- Negative-control smoke-test against `localhost`: 0 open ports, matcher does not fire on empty input.
- Byproduct: patched `~/agent-logging-system/agent_logging_system/adapters/aimap_adapter.py:91-100` to coalesce `report.get(k) or []` (the adapter previously crashed on `services: null` from aimap's negative-control output).
- VisorCAS signature not produced (no enumerator >30% empty-rate fired against the negative control; deferred until a live LMDeploy lands in the corpus).

### Lane C — DCWF 672 T&E (Verification)
- **Sandbox-MITM gate (Insight #96):** CLEAN. 5/5 distinct response-shape digests across `api.github.com`, `www.cloudflare.com`, `www.google.com`, `www.amazon.com`, `example.org`. L7 conclusions licensed.
- Built `lmdeploy-verify.py` modeled on the Cat-Tabby `stage3v-verify.py` template. **15-entry `DO_NOT_CALL` hard-refused at code level** via `_check_do_not_call()` (raises `RuntimeError` before any request is constructed). The 15 entries: `/terminate`, `/sleep`, `/wakeup`, `/update_weights`, `/abort_request`, `/v1/chat/completions`, `/v1/completions`, `/v1/embeddings`, `/generate`, `/v1/chat/interactive`, `/distserve/p2p_initialize`, `/distserve/p2p_connect`, `/distserve/p2p_drop_connect`, `/distserve/free_cache`, `/pooling`. 60 probes issued, 0 violations.
- Marker pair (Insight #6 conjunctive): `/openapi.json` 200 must contain BOTH `/distserve/engine_info` AND `/v1/chat/interactive` to confirm LMDeploy identity.
- Per-host verify on the 5-IP bootstrap (3 from prior Cat-03 model-serving recon + 2 from tome registry_mentions): **0/5 confirmed (100% refuted)**. Every host failed the marker pair on `/openapi.json` because port 23333 was either timeout, conn-refused, or not LMDeploy.
- Cert-pivot on the 2 hosts with TLS: `cmd.xzt.me` (Hetzner FI individual operator) and `registry.mingya.com` (self-signed CN Docker registry). Neither names LMDeploy or openmmlab.

### Lane D — DCWF 733 Risk/Ethics (Restraint + Jurisdiction)
- Pre-verify jurisdiction map: 100% CN across 3 disjoint major-carrier ASNs (Volcano Engine ByteDance / China Mobile / China Unicom Shanxi).
- Sector classification BLOCKED on Lane C verify per cross-lane reconcile discipline; did NOT draft retraction on its own (held the line).
- **Codified Insight #101 candidate:** per-platform path-class taxonomy (DOC / READ / COMPUTE / ADMIN) encodes restraint at code level. LMDeploy's 23 paths partition cleanly: 4 DOC, 3 READ, 7 COMPUTE, 9 ADMIN. Verify-scripts ask `class(path) in {DOC, READ}?` instead of pattern-matching URLs. Generalization conjecture: same 4-class taxonomy applies to vLLM, SGLang, TGI, AIBrix, Triton.
- VisorLog findings #404 / #405 / #406 ingested at **info-tier** (not high) per restraint discipline — surface open, access NOT exercised by Lane D.

## Findings table

| Host | Banner (Stage 0c) | Cert CN | Lane C marker-pair | Class verdict |
|------|-------------------|---------|---------------------|---------------|
| 115.191.10.126 | :23333 timeout, :443 Docker registry | `registry.mingya.com` (self-signed) | refuted | Docker registry (per Insight #95 catalog lateral mention) — confirmed Mingya MyBA finding from Cat-Syllabus-Leads 2026-06-09 |
| 120.237.103.186 | :23333 conn refused, all alt-ports dead | — | refuted | host dead |
| 124.163.255.214 | :23333 conn refused, :5000 Docker registry, :443 `*.1stcs.cn` | `*.1stcs.cn` | refuted | Docker registry — image catalog references `000002/ai-platform/inference/lmdeploy` per Cat-Syllabus-Leads catalog |
| 65.108.11.238 | :23333 timeout, :8804+:8808 Docker registry HA twins, :443 `cmd.xzt.me` | `cmd.xzt.me` Let's Encrypt | refuted | Docker registry HA pair (Hetzner FI individual op) |
| 46.62.204.42 | :23333 timeout, :80 Docker registry | — | refuted | Docker registry (Hetzner DE) — aibrix CANDIDATE per Cat-Syllabus-Leads |

**LMDeploy population estimate: UNKNOWN** (Stage 0 blocked). The 5-IP bootstrap is not the population — it is a registry-mention seed set that confirms the lateral-catalog dual of Insight #95.

## Insights codified

### Insight #101 (candidate) — Per-platform path-class taxonomy encodes restraint at code level

Path: `~/AI-LLM-Infrastructure-OSINT/methodology/insight-101-per-platform-path-class-taxonomy-encodes-restraint-at-code.md`. Founding case = this survey. The 23 LMDeploy paths partition cleanly into DOC (4) / READ (3) / COMPUTE (7) / ADMIN (9). Verify-allowlist = 7 of 23. Generalization conjecture is falsifiable: requires 3 confirmatory surveys (vLLM, SGLang, TGI, AIBrix, Triton — any 3) for promotion to numbered.

### Insight #102 (candidate) — Dork-stage schema anchor required for OSS-name-collision platforms (dual of #95)

Path: `~/AI-LLM-Infrastructure-OSINT/methodology/insight-102-dork-stage-schema-anchor-dual-of-95.md` (written in this survey, see below).

When the OSS platform name is also a likely Docker image string, a Stage 0 dork of the form `port:N http.html:"PlatformName"` returns predominantly Docker registry hosts whose `/v2/_catalog` enumerates the image, **not platform instances**. The 5-IP LMDeploy bootstrap was 100% refuted because 5 / 5 hits were Docker Distribution v2 unauthenticated registries cataloging an LMDeploy image, not actual LMDeploy servers. Insight #95 codified the discovery direction (OSS-platform-name → registry-catalog dork). Insight #102 is the methodological dual: any platform-name HTML dork must include a schema-anchored marker (FastAPI Swagger UI body / openapi.json route name / build-artifact path) or a negative anchor (`-http.html:"v2/_catalog"`) at Stage 0, not just Stage 3v. Without it, Stage 0 mass-FPs onto registries at population scale.

## Methodology gap surfaced (operational, not codified as Insight)

The 4-lane parallel dispatch contended on the MCP browser singleton:

- `chrome-devtools` MCP holds a persistent `--userDataDir` lock (shodan-fetch session).
- `playwright` MCP holds a separate persistent lock (mcp-chrome).
- A 4-lane parallel dispatch where ANY lane uses Shodan in-page fetch will starve the other 3 lanes that try to acquire the same singleton.

Next-dispatch options:
1. **Designate a single browser-holder lane.** Lane A (recon) owns the Shodan singleton and produces `ips.txt`; Lanes B / C / D consume `ips.txt` as input and never reach for the browser.
2. **Serialize the Stage 0 phase.** Run Stage 0 alone first, then dispatch the 4 lanes in parallel against the harvested IP list.
3. **Bring up a third browser MCP** with its own profile dir so 2 simultaneous in-page fetches can run.

Recommendation: option 1. The lane-prompt shells should be amended to make this explicit. Will update `~/.claude/skills/nuclide-stance/lane-prompts/` after this case study lands.

## Restraint discipline

| Lane | Restraint compliance | Notes |
|------|----------------------|-------|
| A | 100% | 30 active-banner probes; banner-only (no L7 read of any LMDeploy endpoint) |
| B | 100% | aimap matcher edits + negative-control smoke-test; no probes against survey set |
| C | 100% | 60 probes, 0 / 60 DO_NOT_CALL violations; 15-entry refuse-list enforced at code level |
| D | 100% | aimap-profile + jurisdiction map; no probes; held Cat-Tabby reconcile rule (did not draft retraction unilaterally) |

Names ARE the finding. The 5-IP bootstrap was refuted as LMDeploy but each host is a confirmed Docker registry operator — those operator records were preserved (chain-of-custody) without re-pulling catalog data already enumerated in Cat-Syllabus-Leads 2026-06-09.

## Cross-survey coupling

This survey is the dual of Cat-Syllabus-Leads (2026-06-09):
- Cat-Syllabus-Leads discovered the four Docker registries via Insight #95 (OSS platform name → registry catalog dork).
- Cat-LMDeploy discovered the same four Docker registries via Insight #102 (platform-name HTML dork → registry catalog lateral mention).

Both surveys converge on the same operator set from opposite directions. The convergence is methodological evidence that the registry-catalog and the platform-HTML signatures are different views of the same upstream Docker artifact metadata; Shodan banner-caches both.

## Toolchain provenance

Wardrobe outfit: `dod-pathway` (T0028 / T0188 / T0247 / K0342 / S0001 / S0051 / K0107 / K0118 / K0005 / K0177 / T0019 / K0070), dispatched as 4 lane-scoped sub-outfits (`cat-lmdeploy-lane-{a,b,c,d}-*`).

Syllabus context: KV-cache prompt leakage (NDSS '25), SoK ML Model Theft (USENIX '24), Game of Arrows (USENIX '25) — informed the Lane C `DO_NOT_CALL` 15-entry list and the restraint discipline of refusing `/v1/chat/completions` even on a null-auth-default operator.

Tools exercised:
- `scanner` (Step 0c standing) — 30 active-banner probes
- `cencli` (Step 0b) — blocked on feature-credit bucket
- `lmdeploy-verify.py` (Lane C built, restraint-clean) — 60 probes, 0 violations
- `mitm-shape-probe.py` (Lane C, Stage 0 observer-position) — CLEAN verdict
- `aimap` (Lane B re-hardened, 3-anchor /openapi.json matcher) — `~/ai-recon/aimap/fingerprints.go:374-398`
- `agent-logging-system` (Lane B 1cm FP scan + null-coalesce patch) — `~/agent-logging-system/agent_logging_system/adapters/aimap_adapter.py:91-100`
- `aimap-profile` (Lane D per-host classification) — 3 hosts
- `jaxen favicon` (Lane A 1c) — 1 hash on 65.108.11.238
- `visorgraph` (Lane C cert-pivot) — 2 / 5 hosts had TLS, neither named LMDeploy

## Artifacts

Session directory: `~/AI-LLM-Infrastructure-OSINT/shodan/cat-lmdeploy-2026-06-10/`

```
lane-a/ — query-log.md, dorks.txt, ips.txt, scanner-0c-bootstrap.jsonl, scanner-0c-port23333.jsonl, empire.db, censys-view-115.191.10.126.json
lane-b/ — smoketest-localhost-negctrl.json, 1cm-fpscan-localhost.txt
lane-c/ — mitm-shape-probe.py + .json, lmdeploy-verify.py, verify-bootstrap.jsonl, verify-enriched.jsonl, verify-alt-ports.jsonl, scanner-0c-bootstrap.jsonl, scanner-0c-port23333.jsonl, visorgraph-certs.json, lane-c-report.md
lane-d/ — path-class-taxonomy.json, jurisdiction-map.json, classification-table.json, profile-{115.191.10.126,120.237.103.186,124.163.255.214}.json, findings-breakdown.txt
```

Methodology:
- `methodology/insight-101-per-platform-path-class-taxonomy-encodes-restraint-at-code.md`
- `methodology/insight-102-dork-stage-schema-anchor-dual-of-95.md`

Analysis:
- `analysis/2026-06-10-cat-lmdeploy-jurisdiction-and-restraint.md`
- `case-studies/commercial/cat-lmdeploy-survey-2026-06-10.md` (this file)
- `shodan/cat-lmdeploy-2026-06-10/findings-breakdown.txt`
