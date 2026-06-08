# NuClide Research - Session State

## 2026-06-08 — SUBSTRATE MARATHON + GLANCE BUILD

Four surveys + two new public tools + 8 DCWF panel reports + cross-corpus methodology.

### Surveys shipped today

| Cat | Platform | Verified | Headline |
|---|---|---|---|
| Cat-02 | ChromaDB (CVE-2026-45829 campaign) | 269 1.x | 200/269 (74%) carry attacker canaries 6 days post-burst. Hadrian nuclei template run by unknown third party 2026-06-02 |
| Cat-46c | VictoriaMetrics | 1,176 | 93.5% unauth, 91.5% pprof open, 1,578 scrape targets leaked, framework #3060 bypass confirmed |
| Cat-46d | Prometheus | 475 verified | 100% unauth on verified subset. 100% prometheus.yml leak. 25 hosts with plaintext basic_auth in dumped config |
| Cat-47 | Agent Memory (Mem0/Letta/Zep/Cognee) | 36 | 10 Zep + 1 Mem0 confirmed unauth. 27 user-session UUIDs leaked. MemMorph paper attack class reachable |

### Tools shipped

- `glance` v0.1.1 (public at github.com/nuclide-research/glance) — schema-only sensitivity analyzer with sealed-mode default. DCWF 4-role panel-audited and corrected in same session
- `constellation` v0.1.0 — cross-corpus operator hunt sibling tool
- 5 per-category verifiers (`verify_chroma_campaign.py`, `verify_chroma_version.py`, `verify_vm_unauth.py`, `verify_prom_unauth.py`, `verify_agentmem.py`)

### Insights codified (numbered + candidates)

- #87 — canary persistence as monitoring proxy (numbered, panel-validated)
- #88 — scrape topology = operator org chart (numbered, generalized VM + Prometheus)
- #89 — framework-level auth bypass propagates to population scale (numbered, VM-specific after Prometheus falsifier)
- #90 candidate — mixed-quadrant platforms (Prometheus straddles Q3 + Q4)
- #91 candidate — config-dump endpoints concentrate disclosure value
- #92 candidate — cross-platform co-deployment multiplies exposure (constellation finding)
- #93 candidate — syllabus-driven surveys produce denser case studies than population-first alone
- #94 candidate — agent-memory leaks compound forward in time

### Methodology contributions

- Paper-first target selection (syllabus drove Cat-47 from MemMorph paper)
- Cross-corpus operator hunt (constellation tool)
- DCWF 4-role panel audit pattern applied twice (VM survey + glance tool)
- Body-content classifier gap caught three times this session (glance v0.1.0 `\b` boundary; VM 134-vmcluster reclassification; Cat-47 21% FP rate). Recommend body-shape validation as default check in next-version verifiers.

### What's next

- v0.2 verifiers with body-shape validation as default check (lesson learned three times today)
- OpenTelemetry Collector survey per DCWF 902 roadmap (next Insight #88 generalization test on the substrate-monitoring tier)
- 80 Chroma CLEAN-OPEN operator disclosure pipeline (deferred from today)
- 25 Prometheus credential-disclosure operator notification pipeline (per DCWF 733 cascade)
- Promote Insight #92 to numbered after one more substrate + one more AI-tier confirmation
- Verifier sanity-check audit of remaining 4 existing verifiers (chroma/vm/prom/agentmem) for the body-content classifier gap class

---

## 2026-06-06 (afternoon/evening) — RESEARCH-PROGRAM SCAFFOLD + LIBRECHAT DEEP DIVE

### research-program/ directory built (`0a1e85c`, `3950a5a`, `3a6a782`)

New top-level directory at `~/AI-LLM-Infrastructure-OSINT/research-program/` indexing the entire program across three layers (research thread + NICE role + disclosure state). 66 markdown files total covering NICE pathways, literature corpora, surveys, tools, disclosures, insights.

---

## 2026-06-08 (full-day close) — Eight-category sweep + Changsha deepfake rig + ShadowRay 2.0

### What changed this session

- **8 platform surveys shipped + pushed** (Cat-46 ComfyUI / 46b Meilisearch / Marqo / 47 Ray / 48 Kubeflow / 49 Label Studio / 50 Chainlit / 51 Argilla / 52 Khoj)
- **1 single-target deep dive** on `113.240.68.47` (Changsha 8x A100 deepfake-production rig: 616,898 voice-clone jobs, 2,423 hours of synthesized audio)
- **2 detector tools shipped** to `~/garlic/`: `comfyui_ghost_detect.py` (6-signal) + `shadowray_detect.py` (5-signal)
- **3 IR hand-off packages drafted** (Censys ARC for ComfyUI/GHOST, Oligo Security + Anyscale for Ray/ShadowRay 2.0, Cat-04 research bundle)
- **3 published-grade articles drafted** (Medium: Changsha deepfake rig; defender advisory: ShadowRay 5-signal self-check; X-post: HK Meilisearch botnet headline)
- **README full rewrite** from audited counts + GitHub about + topics + homepage refreshed
- **v0.5.0 release tagged + cut** with full notes
- **`/nuclide-stance` skill saved** (togglable wardrobe + syllabus stance for future sessions)
- **Auth-friction gradient** anchored across 11+ platforms; new ceiling (Argilla 0%) and new floor (Langfuse 88.9%) measured same-day

### Tools that did not run

VisorPlus, VisorSD, VisorGoose, VisorGraph, recongraph, nu-recon, menlohunt, VisorScuba, BARE, VisorCorpus, VisorRAG, VisorAgent, VisorHollow, cortex. The day was breadth (8 categories) not depth.

### What's next

- **Send the 3 IR hand-offs** (Censys ARC + Oligo + Anyscale + GCP abuse for Kubeflow B2B SaaS). All staged in `assessments/` as DRAFT.
- **Publish Medium article** on Changsha deepfake rig. Editor is open in browser.
- **File Insight #90 (auth-friction gradient)** as a numbered methodology insight. Currently a synthesis-only finding.
- **Operator attribution for the Kubeflow GCP SaaS pair.** Customer base reads as B2B retail-execution AI; routing via GCP abuse will identify them through GCP's tenant relationship.
- **Re-survey Chainlit** when population crosses ~50 hits (n=5 is below population-claim threshold).
- **Productize the 5-signal ShadowRay + 6-signal GHOST classifiers into aimap enumerators** so future Ray/ComfyUI surveys auto-classify attacker-fleet hosts.
- **Carry-over:** LiteLLM upstream PR #29896 still open; Censys credits exhausted (reset triggers ComfyUI alt-port full sweep + Cat-29 :2746 census).

