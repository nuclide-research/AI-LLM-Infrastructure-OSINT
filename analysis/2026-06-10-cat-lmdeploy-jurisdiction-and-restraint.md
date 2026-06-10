---
survey: Cat-LMDeploy 2026-06-10
lane: D — DCWF 733 AI Risk & Ethics (Restraint + Jurisdiction)
wardrobe_atoms: [K0107, K0118, K0003, K0002, A0123, K0004]
population: 3 IPs from `port:23333 http.html:"LMDeploy"` (tome basic dork)
restraint_violations: 0
candidate_insight: 101
---

# Cat-LMDeploy 2026-06-10 — Jurisdiction Map + Restraint Discipline (Lane D)

## TL;DR

LMDeploy (OpenMMLab / Shanghai AI Laboratory, port 23333, auth_default=`none` per api_server.py:1486) surfaces a 3-host CN-saturated cohort. Jurisdiction concentration: 100% CN across 3 distinct major-carrier ASNs (Volcano Engine / CMNET / Unicom Shanxi). Pre-verify operator-class split: 1 commercial-cloud (Volcano Engine tenant `registry.mingya.com`), 1 enterprise-K8s (CMNET tenant w/ kube-apiserver banner), 1 hobby/lab (Unicom Shanxi ADSL pool — aimap-profile auto-tagged `education` triggering CFAA flag). Population too small for population-level generalization, exactly the size where Insight #68 high-depth/low-breadth restraint applies.

Methodology contribution: candidate Insight #101 promotes path-class taxonomy from per-platform special-cases to a 4-class structure (DOC / READ / COMPUTE / ADMIN). Founding case is LMDeploy's 23 documented paths partitioning cleanly. Verify-scripts ask `class?` not `pattern-match URL?`.

Lane D restraint posture: 0 violations. All artifacts derived from RDAP + Shodan-cached banners + aimap-profile passive fast-mode + tome cross-reference. Zero calls to COMPUTE or ADMIN routes from this lane.

## Jurisdiction distribution

| IP | Country | ASN | Carrier | rDNS | Pre-verify class |
|----|---------|-----|---------|------|-------------------|
| 115.191.10.126 | CN | AS137718 (CNNIC) | Volcano Engine (ByteDance) | — (hostname `registry.mingya.com`) | commercial-cloud-tenant |
| 120.237.103.186 | CN | China Mobile CMNET | China Mobile | — | enterprise-or-K8s (kube-apiserver banner observed) |
| 124.163.255.214 | CN | AS4837 | China Unicom Shanxi | `*.adsl-pool.sx.cn.` | hobby-or-lab-self-host |

100% CN. Compare to peer survey Cat-BentoML 2026-06-10: top countries US/36, DE/6, CN/5, KR/5, IN/4 (US-dominant). Same platform-category (inference serving), opposite jurisdiction skew. Operator-demographic == developer-demographic prior confirmed at this snapshot.

ASN heterogeneity within the CN cohort: 3 different major carriers (cloud / mobile / wireline), 3 different operator classes (commercial-tenant / enterprise / individual). The platform is the same; the deployment topology cross-cuts socio-technical strata. No cluster signal (no shared ASN, no shared certificate operator).

## Sector classification (pre-verify)

| Sector | Count | Hosts | Confidence |
|--------|-------|-------|------------|
| commercial (cloud-tenant) | 1 | 115.x — provisional FINANCE if Mingya == insurance brokerage cohort | LOW — hostname-suggestive only |
| commercial (K8s) | 1 | 120.x | LOW — kube-apiserver alone insufficient to fix sector |
| education/individual | 1 | 124.x | MEDIUM — ADSL-pool + 15 open legacy ports + aimap-profile auto-tag |

Final sector classifications BLOCKED on Lane C verify output. The platform itself (LMDeploy) is sector-neutral; the **model name in `/v1/models` is the sector tell**. Default install is `internlm/internlm2_5-7b-chat` (general-purpose). Deviations from default = sector signal:
- `*medqa*`, `*clinical*`, `*med-*` → medical (HIPAA/equivalent)
- `*fintech*`, `*finance*`, `*credit*` → financial
- `*k12*`, `*kids*`, `*moe*` → minor-data (COPPA/PIPL Article 31 minor protections)
- `internlm/*`, `openmmlab/*`, `Qwen/*` → general-purpose

## Ethics flags

| Flag | Hosts | Source |
|------|-------|--------|
| EDUCATION_or_INDIVIDUAL | 124.163.255.214 | aimap-profile classification.ethics_flags |
| PROVISIONAL_FINANCE | 115.191.10.126 | hostname-suggestive (`registry.mingya.com`); REQUIRES Lane C confirm |
| MEDICAL / MINOR_DATA | 0 | no pre-verify signals; awaits Lane C /v1/models |

Zero hard medical/minor flags pre-verify. Soft financial flag on one host requires confirmation via tenant directory cross-ref + Lane C model inventory.

## Restraint discipline executed

1. **Enumerate metadata, do not exfiltrate.** Only RDAP + Shodan-cached banners + aimap-profile passive mode + tome cross-ref. No live calls to any LMDeploy host. Verified violation count: **0**.
2. **DO_NOT_CALL at code level (Lane C scope).** Path-class taxonomy artifact (`path-class-taxonomy.json`) hands Lane C a 4-class allowlist; verify-script enforcement is Lane C's responsibility. Lane D defines the structure.
3. **Ethical-stop boundary.** VisorAgent NOT run; survey-set hosts excluded per protocol.
4. **Evidence preservation (K0118).** All raw aimap-profile JSON preserved at `lane-d/profile-<ip>.json`. Wire-shape Lane C MITM gate output preserved at `lane-c/mitm-shape-probe.json` (CLEAN — 5 distinct digests). No contaminated evidence to mark; chain-of-custody markers not required for this lane this run.
5. **Cross-jurisdiction (K0107).** Routing class mapped per host (CNCERT/CC + carrier abuse + tenant security@ where applicable). **No disclosure drafted, routed, or recommended.** Per `feedback-no-disclosure-recommendations` and Cat-Tabby reconciliation rule.

## Candidate Insight #101 — path-class taxonomy

LMDeploy's 23 documented paths partition cleanly into 4 safety classes (DOC=4, READ=3, COMPUTE=7, ADMIN=9). Verify-scripts that ask `class(path) in {DOC, READ}?` move restraint from per-platform URL semantics into a single tome-stored allowlist. Codified at `methodology/insight-101-per-platform-path-class-taxonomy-encodes-restraint-at-code.md`. Falsifiable; founding case n=1 platform, requires 3 more for promotion to confirmed.

The Lane D framing: tome already encodes auth_default, misconfig_patterns, pivot_paths. Path-class is the missing layer that turns the restraint ethic from documentation into code enforcement.

## Cross-lane dependency lock

Lane C verify-script output (any host's `/openapi.json` + `/v1/models` + `/metrics` body) is the load-bearing dependency for final sector classification. Per Cat-Tabby 2026-06-09 incident discipline: Lane D does NOT retract, downgrade, or amend pre-verify classifications based on its own lane alone or on Lane B/C in-progress hypotheses. Orchestrator reconciles all 4 lane verdicts.

If Lane C confirms a live LMDeploy instance on any of the 3 IPs, that single host becomes a high-confidence case study; the cohort claim stays population-tentative at n=3.

If Lane C cannot reach any of the 3 IPs (Shodan cache stale, GFW interference, or active block), Insight #101 still stands — it is a structural claim about tome-encoded path semantics, not about live-host availability.

## Artifacts written this lane

- `~/AI-LLM-Infrastructure-OSINT/shodan/cat-lmdeploy-2026-06-10/lane-d/path-class-taxonomy.json` — 4-class LMDeploy path partition
- `~/AI-LLM-Infrastructure-OSINT/shodan/cat-lmdeploy-2026-06-10/lane-d/jurisdiction-map.json` — RDAP / ASN / carrier breakdown
- `~/AI-LLM-Infrastructure-OSINT/shodan/cat-lmdeploy-2026-06-10/lane-d/classification-table.json` — per-host operator + sector + ethics
- `~/AI-LLM-Infrastructure-OSINT/shodan/cat-lmdeploy-2026-06-10/lane-d/profile-{ip}.json` — aimap-profile raw output (3 files)
- `~/AI-LLM-Infrastructure-OSINT/methodology/insight-101-per-platform-path-class-taxonomy-encodes-restraint-at-code.md` — candidate Insight #101
- `~/AI-LLM-Infrastructure-OSINT/analysis/2026-06-10-cat-lmdeploy-jurisdiction-and-restraint.md` — this file
- VisorLog ingest: findings #404 / #405 / #406 (info-tier, LMDEPLOY-CANDIDATE tagged)

## Open questions for orchestrator

1. Lane C verdict: live LMDeploy on any of 3 IPs?
2. If yes, sector tell from `/v1/models` body?
3. Does `registry.mingya.com` correspond to Mingya Insurance Brokerage? (Lane B or orchestrator brand-resolution lookup; Lane D will not query.)
4. Promotion criteria for Insight #101: which 3 additional platforms (vLLM / SGLang / TGI / Triton / AIBrix) should the path-class structure be tested against next?

## Wardrobe + syllabus stance

DCWF 733 AI Risk & Ethics Specialist atoms exercised: K0107 (cross-jurisdiction laws + investigative tools) via 100% CN routing class mapping; K0118 (digital evidence preservation) via aimap-profile JSON snapshot + Lane C wire-shape evidence; K0003 (laws/regulations/ethics) via Insight #101 framing restraint as code-level enforcement; K0002 (risk management) via class-aware operator-risk delineation (commercial vs enterprise vs individual); A0123 (CIA to ML ops) via the COMPUTE/ADMIN class split distinguishing availability (terminate/sleep) from integrity (update_weights) from confidentiality (encode/embeddings); K0004 (privacy principles) via PIPL Article 31 minor-data hook embedded in sector classifier.

Syllabus anchor: this survey extends the auth-on-default thesis (Insight #40) into a CN-developer-origin platform and finds the same null-default pattern (api_server.py:1486 — `Default to None, which means no authentication required`). Disclosure-pressure-rightward shift hypothesis under-tested for CN-origin platforms; n=3 insufficient.
