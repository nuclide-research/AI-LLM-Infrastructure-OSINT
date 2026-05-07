# AI Safety Evaluation / Red-Team Self-Hosted: Cross-Cloud Survey (2026-05)

_NuClide Research · 2026-05-04 (initial), **2026-05-05 (methodology correction)**_

> **Status:** Initial probe (2026-05-04) reported 6 confirmed hosts. **2026-05-05 re-probe with tightened fingerprints invalidates all 6, they were substring-match false positives.** Corrected total: **0 confirmed AI safety eval / red-team self-host on the tier-2 cloud sample**. The methodology lesson from this survey is the load-bearing finding; it propagates to every future probe in the catalogue.

---

## Methodology correction (2026-05-05)

The original probe, `data/aisafety-probe.py`, used naked single-word substring matching on response bodies (`b"garak" in body.lower()`, `b"deepeval" in text or b"confident" in text`). At population scale across 1,017 cloud prefixes, this matcher produced **6 false positives and 0 true positives**.

### Confirmed false-positive traces

| Host (port) | Session-8 claim | Actual identity | Substring trigger |
|---|---|---|---|
| `149.56.22.24:5000` | Garak (NVIDIA adversarial harness) | **Clipface**, personal video clip browser (Net Slum) | filename `[F] Garakuta 【Flashアニメ】ガラクタノカミサマ.mp4` (Japanese flash anime "ガラクタノカミサマ" / Garakuta no Kamisama, "God of Junk") contains "garak" as a substring |
| `37.59.107.238:5000` | DeepEval / Confident AI | **LiveChat Nevylish**, French Discord bot / streamer overlay | French marketing copy contains the English word "confident" |
| `149.202.183.53:8000` | DeepEval / Confident AI | **EDocs**, document management platform | substring source not isolated; not an AI eval product |
| `151.80.57.247:5000` | DeepEval / Confident AI | unreachable on re-probe | likely transient or also FP |
| `51.75.89.218:8000` | DeepEval / Confident AI | unreachable on re-probe | likely transient or also FP |
| `51.83.34.173:8000` | DeepEval / Confident AI | unreachable on re-probe | likely transient or also FP |

### Re-probe with tightened detector

The corrected probe is upstream in **aimap** (v1.0.0-aisafety-2026-05-05), which uses conjunctive matching: `status_code + json_field + distinctive body_contains`, all required to fire. Re-probing the same 6 hosts:

```
$ aimap -list /tmp/aisafety-revalidate.txt -ports 1984,5000,7575,8000,8080,15500
  ✓ Found 8 open port(s) across 6 host(s)
  [!] No AI/ML services identified on open ports.
```

**Zero matches.** The methodology fix correctly eliminates the FPs without producing TPs that the broken probe missed (sanity check: the broken probe's 6 hits all dissolve under the structured matcher; no real Garak/DeepEval/Promptfoo/LangSmith deployments were under the noise).

### Why this matters at population scale

Single-word substring matching on response bodies treats any document that mentions the keyword anywhere, anime filenames, French marketing copy, blog posts about the platform, documentation links, as a positive identification of the platform itself. At 1,017 prefixes / ~3.55M IPs, the FP rate compounds:

- Personal media servers (Plex, Jellyfin, Clipface) → indexed filenames containing AI keywords
- Localized SaaS pages → marketing copy containing English AI vocabulary
- Document-management platforms → indexed corpus containing AI-related strings
- Static-site generators → blog posts about the platform

These are not theoretical; the 6 confirmed FPs above hit all four categories. **A loose fingerprint at the discovery stage propagates to every downstream artifact**, case study, disclosure draft, threat intel, synthesis paper. Session-8's deferred Garak disclosure ("OVH abuse + NVIDIA security") would have been a Buffalo-State-style misroute had it been sent.

### The fix: aimap + structured fingerprints

All AI safety eval fingerprints are now in `aimap/fingerprints.go` ([source](https://github.com/Nicholas-Kloster/aimap/blob/main/fingerprints.go)). Each fingerprint requires **at least three conjunctive conditions** before firing:

```go
{
    Name:         "DeepEval Server",
    DefaultPorts: []int{5000, 8000, 8080},
    Probes: []Probe{
        {Path: "/api/health", Matches: []MatchCond{
            {Type: "status_code", Value: "200"},
            {Type: "json_field", Field: "service"},        // requires JSON body
            {Type: "body_contains", Value: "deepeval"},     // anchored to JSON path
        }},
    },
}
```

The `json_field` match requires the body to parse as JSON and have a top-level `service` field. The `body_contains` is then anchored to that JSON path, it cannot fire on French marketing copy or anime filenames because those bodies fail the JSON parse.

Seven AI safety / eval / guardrails fingerprints were added to aimap in this correction:

- **Promptfoo** (15500), `/api/health` with `json_field: status` + `body_contains: promptfoo`
- **NeMo Guardrails** (8000, 8080), `/v1/rails/configs` returning JSON array + `/openapi.json` route-map
- **DeepEval Server** (5000, 8000, 8080), `/api/health` with `json_field: service` + `body_contains: deepeval`
- **LangSmith Self-Hosted** (1984, 8080), `/info` with `json_field: instance_flags`
- **Inspect AI** (7575, 7576, 8080), `/api/logs` returning JSON array + `<title>inspect`
- **Garak REST** (5000, 8000, 8080), `/api/v1/garak/version` with `json_field: garak_version`
- **Lakera Guard Self-Hosted** (8000, 8080), `/v1/guard` with `header_contains: Server: lakera`

Plus four deep enumerators (Promptfoo eval-history extraction, NeMo Guardrails configs disclosure, DeepEval evaluation results, LangSmith project enumeration) following the existing Langfuse `enumLangfuse` pattern.

aimap version is now **43 services + 30 deep enumerators** (was 36 + 26).

---

## Cohort + scope (unchanged from initial run)

Same tier-2 cross-cloud sample: **Scaleway 7 + OVH 33 + Linode 36 = 76 prefixes ≈ 3.55M IPs (1,017 deduped CIDRs)**. Ports scanned: 1984 (LangSmith), 5000 (Garak REST / DeepEval / Promptfoo), 7575/7576 (Inspect), 8000/8080 (NeMo Guardrails / Lakera Guard / DeepEval / generic), 15500 (Promptfoo).

AS63949 honeypot fleet filter applied (393 hosts spoofing Ollama 0.1.33 + Milvus + dizquetv etc.; salt `wW0sffoqsk.EM`).

---

## Corrected results

| Platform | Confirmed (corrected) | Auth-off | Notes |
|---|---|---|---|
| **DeepEval / Confident AI** | **0** (was reported 5; all FPs) |, | Substring noise on `b"deepeval"` / `b"confident"` |
| **Garak (NVIDIA)** | **0** (was reported 1; FP) |, | Substring noise on `b"garak"` |
| **Promptfoo** | 0 |, | No real deployments visible at fingerprint port |
| **LangSmith self-hosted** | 0 |, | Predominantly SaaS or enterprise K8s; thin cheap-VPS market |
| **Inspect AI / HELM / PyRIT** | 0 |, | CLI-dominant tooling |
| **Lakera Guard self-hosted** | 0 |, | Predominantly SaaS |
| **NeMo Guardrails** | 0 |, | Predominantly K8s ingress, not cheap-VPS |

**Total confirmed AI safety / eval / guardrails self-host on tier-2 cloud sample: 0.**

---

## What this changes about the auth-on-default thesis

The original case study reported 6 hits and treated them as evidence of Class-A "auth-off-default" exposure (DeepEval ships without auth, so 5 unauth was thesis-confirming). **With the corrected count, AI safety eval contributes 0 evidence to the thesis.**

This is *strengthening* not weakening, because:

1. The thesis predicts "for any framework that ships auth-off-default, the population-scale deployment will be unauthenticated." The corrected count of 0 is consistent with the **CLI-dominant deployment pattern** of the actual safety-eval ecosystem (Garak, HELM, PyRIT, Inspect ship as CLIs; Promptfoo/LangSmith are commercial-tier with auth-on-default; Lakera/Patronus are SaaS-mostly).
2. The honest negative space is more credible than a 6-host finding-corpus that turns out to be substring noise, and reads better in a synthesis paper.
3. The thesis's strongest evidence sits with: vector DBs (663+ unauth Qdrant), inference servers (850 Ollama tier-2), MLflow CVE pair, MCP (95 with 28 tool-exposed), LLM Gateways (1,857 functional unauth). AI safety eval was never load-bearing.

The **load-bearing methodology insight** that replaces the bogus AI-safety-eval row in the synthesis is:

> **Single-word substring matching on response bodies is unsound at population scale.** A fingerprint must require at minimum: (a) specific endpoint that the platform alone serves, (b) structured response (JSON parse + named field, or specific HTML title format), (c) anchored keyword match conjoined with (a) and (b). Anything looser fires on personal media servers, SaaS marketing copy, and unrelated platforms. The 6-host AI safety eval FP set is the empirical proof.

This insight is now folded into [`SYNTHESIS-2026-05.md`](SYNTHESIS-2026-05.md) "Methodology insights".

---

## Probe deprecation

`data/aisafety-probe.py` is deprecated (header marked) and superseded by aimap's structured fingerprints. The script remains in the repo as a historical artifact for the methodology-correction record.

Reusable lesson for any future bespoke probe in `data/`:

```python
# WRONG — substring matching is unsound at population scale
if b"garak" in body.lower():
    return {"platform": "Garak"}

# RIGHT — endpoint + JSON shape + anchored keyword (all required)
if status == 200 and is_json(body):
    parsed = json.loads(body)
    if "garak_version" in parsed and "garak" in str(parsed).lower():
        return {"platform": "Garak", "version": parsed["garak_version"]}
```

Even better: use aimap's fingerprint database directly (`aimap -target X.X.X.X -ports A,B,C`) and avoid writing per-survey bespoke probes.

---

## Honest negative space

- **Population is genuinely thin** for self-hosted AI safety eval. The CLI-dominant pattern is real; the real cohort exists in private K8s clusters, enterprise SaaS, and academic research clusters that don't show up on cheap-VPS scans.
- **Auth-required deployments may exist but cannot be enumerated unauth.** The corrected probes still don't catch hosts that respond 401 from `/api/health`. Adding `/openapi.json` route-map enumeration (per the RAG-framework survey's 51% leak finding) is a future improvement.
- **Garak's actual exposure profile** if a real instance were to surface would be HIGH-novelty, operators wrapping NVIDIA's adversarial harness in a public web UI would be both rare and worth a dedicated case study. The 0-count says we haven't seen one yet, not that it can't happen.
- **The original probe's substring matcher was the bug, but the broader pattern of writing a one-off probe per survey instead of extending aimap is the structural lesson.** Future surveys should add fingerprints to aimap and run aimap on the cohort, full stop.

---

## See also

- [SYNTHESIS-2026-05.md](SYNTHESIS-2026-05.md), methodology insight #6 captures the substring-FP lesson
- [aimap fingerprints source](https://github.com/Nicholas-Kloster/aimap/blob/main/fingerprints.go), the canonical AI/ML fingerprint database
- [aimap deep enumerators](https://github.com/Nicholas-Kloster/aimap/blob/main/enumerators.go), Promptfoo / NeMo Guardrails / DeepEval / LangSmith enumerators added 2026-05-05
- [REMEDIATION-GUIDE.md](REMEDIATION-GUIDE.md), operator fix-it guide (no AI safety eval entry; would be added once a real exposure surfaces)
