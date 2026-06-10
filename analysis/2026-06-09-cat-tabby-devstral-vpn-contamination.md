# Session Analysis: Cat-Tabby + Devstral Stage 0 — VPN-Exit Response-Rewriting Contamination

**Date:** 2026-06-09
**Session:** Cat-Tabby + Devstral re-validation (later session)
**Classification:** Internal / Research Use Only — methodology codification
**Toolchain:** chrome-devtools MCP browser, shodan-fetch, Python aiohttp prober, Mullvad WireGuard (`us-phx-wg-206` -> Miami exit)
**Repos updated:** AI-LLM-Infrastructure-OSINT (analysis + insight + case-study retraction + SESSION.md)
**Lane:** D (DCWF 733 AI Risk & Ethics Specialist) — methodology integrity, restraint, evidence preservation
**Outfit:** `cat-tabby-lane-d-risk-ethics` (K0107 / K0118 / K0003 / K0002 / A0123 / K0004)

---

## 1. Overview

The Cat-Tabby + Devstral re-validation ran Stage 0 (`/api/tags` first-pass) across the 10,895-host confirmed-unauth Ollama corpus while egressing through a Mullvad WireGuard tunnel (Phoenix entry, Miami exit). First pass returned 1,217 code-model-loaded hosts (434 Devstral), and a shadow-sweep then a direct Tabby identity probe on the 753 self-hosted subset surfaced 117 hosts with port 9090 open and 66 "confirmed Tabby" via `/auth/signin` title match. Lane A re-probed three of the 66 Tabby hits and three of the 1,217 code-model hits moments later; the re-probes returned EMPTY `/auth/signin` bodies and DIFFERENT model loadouts on the same IPs. The divergence class is consistent with a response-rewriting layer (VPN-exit transparent proxy, or upstream MITM) substituting templated responses on the first pass and real responses on the second. The full 1,217 / 434 / 117 / 66 cross-section is therefore inner-A / outer-0 per Insight #68 (logic confident, no live host actually exercised via a clean route) and is retracted pending a clean-route paired-probe re-validation. The discipline win: zero disclosures were sent based on the contaminated numbers — Lane D restraint held the artifact in place until verification ran.

## 2. Tooling

| Tool | Role | Notes |
|---|---|---|
| chrome-devtools MCP | Shodan UI browser session for harvest | Authenticated, 0 API credits |
| shodan-fetch (in-page `fetch()`) | Population harvest | Returned 10,895-host corpus (carry-forward from earlier survey) |
| Python aiohttp prober (`code-model-probe.py`) | Stage 0 `/api/tags` first-pass + shadow-sweep + Tabby `/auth/signin` identity probe | 60 concurrent, 8s timeout |
| Mullvad WireGuard | Egress routing | `us-phx-wg-206` entry, Miami exit — the contamination surface |
| `paired-probe.py` (Lane A) | Re-probe of contaminated subset | The instrument that caught the divergence |
| `mitm-shape-probe.py` | Post-incident shape-of-rewriting characterization | First step of the Stage 0 sandbox-MITM check that should have been Stage 0 prerequisite |

## 3. Methodology gap

Methodology §3 ("Distrust your observation position") is standing advice. The canonical NuClide recongraph and VisorGraph both run a formal sandbox-MITM consistency check at startup that downgrades L7 conclusions when an intercepting environment is detected. The Stage 0 prober used here did NOT run that check — it assumed the VPN-exit was transparent and that a 200-with-data on `/api/tags` was an authoritative read of the target's actual model loadout. It was not. The single sentence that should have been a Stage 0 prerequisite (and was not):

> Before any L7 conclusion is drawn from a non-local routing layer, run the sandbox-MITM consistency check (recongraph / VisorGraph carry the reference implementation) and pair every probe with a delayed re-probe whose hash must match.

This is the same class of gap Insight #11 calls out for source-vs-framing but applied to the network-path layer instead of the documentation layer: the routed observation point is framing; the host's real response is the primary source.

## 4. Execution trace

| Time (approx) | Action | Outcome |
|---|---|---|
| T+0 | Stage 0 first-pass `/api/tags` across 10,895-host corpus, VPN-routed | 1,217 "code-model-loaded" (434 Devstral) |
| T+0 | Shadow-sweep on 753 self-hosted subset, VPN-routed | 117 hosts with `:9090` open |
| T+0 | Direct Tabby identity probe (`/auth/signin` title match) on the 117 | 66 "confirmed Tabby" |
| T+~minutes | Lane A `paired-probe.py` on 3 of 66 Tabby hits | EMPTY `/auth/signin` bodies — no `<title>Tabby` |
| T+~minutes | Lane A `paired-probe.py` on 3 of 1,217 code-model hits | DIFFERENT model loadouts (e.g. `qwen2.5:1.5b` instead of `codellama:13b` on same IP) |
| T+~minutes | Contamination class identified: response-rewriting (VPN-exit or upstream transparent proxy) | All Stage 0 cross-section results flagged inner-A / outer-0 |
| T+~minutes | Stage 0 results RETRACTED. No disclosure sent. Lane D evidence-preservation marker placed. | Discipline win: restraint held; methodology gap codified. |

## 5. Findings — per-probe divergence evidence

The contamination class is "templated response on first-pass, real response on re-probe." Two divergence shapes observed:

1. **Tabby `/auth/signin` shape divergence.** First pass: HTTP 200 with `<title>Tabby` in body across 66 hosts (substituted template). Re-probe moments later on a 3-host sample: HTTP 200 with EMPTY or non-template body (no `<title>Tabby`). Bodies on the re-probe did not contain the Tabby identity marker the first probe had observed. The first-pass match was a path-injected template, not the host's real `/auth/signin`.
2. **Ollama `/api/tags` model-loadout divergence.** First pass: model list including `codellama:13b` (and the Devstral 434-host subset). Re-probe moments later on a 3-host sample: a DIFFERENT model list on the SAME IP — for example `qwen2.5:1.5b` replacing `codellama:13b`. Same `/api/tags` endpoint, same IP, minutes apart, different JSON. The model-name selection on first-pass appears to have been chosen from a templated catalog the rewriting layer associates with code-assistant hunting traffic.

This is the load-bearing evidence that the Stage 0 cross-section is inner-A / outer-0. The numbers (1,217 / 434 / 117 / 66) are reproducible by re-running through the same contaminated path — they are confident and wrong.

## 6. Risk assessment — prior NuClide surveys potentially similarly contaminated

Every prior NuClide survey that egressed through a VPN/proxy and did NOT run the sandbox-MITM consistency check at Stage 0 is a candidate for similar contamination. By date / category:

| Survey | Date | Routing layer | Re-probe paired? | Status |
|---|---|---|---|---|
| Cat-Tabby + Devstral (this) | 2026-06-09 | Mullvad WG `us-phx-wg-206` -> Miami | Yes (caught it) | Stage 0 RETRACTED |
| Cat-Tabby (earlier same day, 4-platform) | 2026-06-09 | Mullvad (same session) | No (3v marker-anchored but no path consistency check) | LOW RISK — 3v Lane C used conjunctive markers (`chat_model` + `webserver`) that templated-response substitution is unlikely to forge; verify on next re-run |
| Cat-54 OTel / Tracing | 2026-06-09 | Mullvad (same session window) | No | LOW-MEDIUM RISK — port-class probes; 88% verify rate on SigNoz is plausible but should be re-validated on a clean route |
| Cat-Syllabus-Leads (aibrix / lmdeploy / rtp-llm) | 2026-06-09 | Mullvad (same session window) | No | LOW RISK — registry-catalog dorks not L7 endpoint reads |
| Population walks (Ollama walk 2026-05-15, university LLM 2026-05-19 onward) | 2026-05-15+ | Mixed (some Mullvad, some direct) | No formal pair-probe | UNKNOWN RISK — flag for re-run with `paired-probe.py` schema |
| Cat-02 VectorDB rounds | 2026-06-03/04 | Mixed | No | LOW RISK — verify ran direct data-layer reads with vector-DB-specific schema (harder to forge templates for) |

The recurrence-class risk is concentrated in surveys that (a) used VPN/proxy egress, (b) relied on a single `/api/tags`-class or `/auth/signin`-class identity probe as the truth, and (c) did not pair-probe. Cat-Tabby Stage 3v's marker-discipline (`chat_model` + `webserver` conjunctive, `<title>Tabby` body anchor with TLS-CN cross-check on a different routing window) substantially de-risks the earlier same-day survey, but a clean-route re-run is the right confirmation.

## 7. Recommendations — procedural fixes

1. **Make sandbox-MITM consistency check a Stage 0 PREREQUISITE, not §3 standing advice.** The check exists in recongraph and VisorGraph. Lift the reference implementation into a standalone script (`stage0-mitm-check.sh`) and gate every survey on it. If the check trips, downgrade all L7 conclusions to inner-A / outer-0 until a clean route is established.
2. **Embed paired-probe schema in shodan-fetch, aimap, and scanner output.** Every L7 probe records a re-probe (T+N seconds, typically 30-120s) and emits `paired_match: true|false|skipped`. Any record with `paired_match != true` does NOT earn a tier label.
3. **Route diversity at Stage 0.** Where the routing layer is non-local (VPN/proxy), require at least two distinct exits (Mullvad exit A + direct or Mullvad exit B) and require both to agree on the identity probe before promoting from candidate to confirmed.
4. **Make Insight #68's Depth(A/B) x Breadth(0/1/2) language LOAD-BEARING in the verify-rung schema.** A contaminated result is inner-A / outer-0 by definition: logic-only, no live host actually tested via a clean route. The vocabulary already exists — wire it into the output.
5. **Lane D evidence-preservation marker.** Per K0118: contaminated datasets are preserved INTACT, never deleted, marked with a chain-of-custody note (`EVIDENCE-CONTAMINATED.txt`) explaining why they are kept and what class of evidence they constitute.

## 8. Limitations

- We have not yet characterized the rewriting layer. Open question: is the substitution at the Mullvad exit (unlikely — Mullvad's documented architecture is L3/L4), at an upstream transit ISP on the Miami exit, or at a transparent proxy injected somewhere between Mullvad and the targets? `mitm-shape-probe.py` is the first step; full characterization is queued.
- The 1,217 / 434 / 117 / 66 numbers are retained as evidence of the contamination class, not as findings. They cannot be used as a population baseline until a clean-route re-run produces the actual numbers.
- The 3-sample re-probe is sufficient to identify the contamination class; it is not sufficient to estimate the contamination rate across the full 10,895-host corpus. A clean-route re-run with paired-probe across the entire corpus is the proper measurement.

## 9. PoC illustrations — divergence evidence

```
# Tabby /auth/signin first-pass (VPN-routed, T+0)
GET /auth/signin -> 200, body contains "<title>Tabby"   [66/117 hosts]

# Same IP /auth/signin re-probe (VPN-routed, T+~minutes, sample n=3)
GET /auth/signin -> 200, body EMPTY (no <title>Tabby)   [3/3 sampled]
```

```
# Ollama /api/tags first-pass (VPN-routed, T+0)
GET /api/tags -> 200, {"models":[...,"codellama:13b",...]}   [example]

# Same IP /api/tags re-probe (VPN-routed, T+~minutes, sample n=3)
GET /api/tags -> 200, {"models":[...,"qwen2.5:1.5b",...]}    [different loadout, same IP]
```

The class is: SAME IP, SAME ENDPOINT, MINUTES APART, DIFFERENT BODY. That cannot be host-side variability for an unauthenticated read of a static config endpoint. The variable is somewhere between us and the host, on our side.

## 10. K0107 / K0118 discipline notes

- **K0107 (cross-jurisdiction):** zero disclosures sent. The 1,217 "exposed code-model hosts" and the 66 "confirmed Tabby" were identified internally, never communicated to any operator, CERT, or vendor. The restraint discipline held — even with confident-looking numbers, no contact was made before the verification step. This is the discipline win the methodology is designed to produce.
- **K0118 (digital evidence preservation):** `probe-results.jsonl`, `code-loaded-hosts.jsonl`, `tabby-on-shadow-9090.jsonl`, `sanity-probe.jsonl`, `shadow-sweep.jsonl` preserved INTACT. `EVIDENCE-CONTAMINATED.txt` placed in the survey directory as chain-of-custody marker. These files are evidence of the contamination class — they are the documented instance the codified Insight #96 will cite.

---

_Lane D close. The methodology gap is documented, the candidate Insight is drafted, the case study is retracted at the Stage 0 cross-section, SESSION.md carries the disclosure. The 1,217 / 434 / 117 / 66 numbers stay on disk as evidence, never as findings._
