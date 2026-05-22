# Session Analysis: Population-Survey Megabatch

**Date:** 2026-05-15
**Session:** 14
**Classification:** Internal / Research Use Only
**Toolchain:** aimap v1.9.4 → v1.9.5, JAXEN, fast_enum direct-prober family, VisorLog, VisorScuba, BARE, VisorBishop, VisorGraph, VisorSD, VisorGoose, menlohunt, VisorCorpus, cortex, nu-recon, shodan_paginate
**Repos updated:** AI-LLM-Infrastructure-OSINT (04c7677, 59cb40b, 656776b, da8bfce, e7e8a32, 02a260b, 215730e, 1c5a649, 661f6e8, 7a604fd) · aimap (a888100, b157c86)

---

## 1. Overview

### Objective

Map exposed AI/ML and supporting infrastructure at population scale. The day ran eleven population-scale surveys plus one named-operator single-host case. The research goal is fixed: map, find, and discover the absence of security in LLM/AI stacks. The auth-on-default thesis is the lens. Each survey either confirms it or tries to break it.

Three thesis questions were under test this session:

1. Does the auth-on-default pattern hold when a platform is re-surveyed through a different discovery channel? Tested by re-walking Ollama on Shodan after prior masscan-on-cloud-prefix surveys.
2. Does the thesis split cleanly along framework defaults? Tested by surveying paired platforms with opposite shipping defaults: Argo CD (auth-on) against Consul (auth-off).
3. Does the audio-AI modality behave like the text-AI modality? Tested by closing Survey 17 across Whisper ASR, voice-cloning, and voice-agents.

### Scope and Constraints

- **Target domains/IPs:** Shodan-indexed populations for eleven platform classes. Ollama (port 11434), llama.cpp HTTP server, Whisper ASR, voice-cloning (RVC/GPT-SoVITS/Applio/OpenVoice/ChatTTS/F5-TTS), voice-agents (LiveKit/Pipecat/Vocode), unauth Docker daemon (port 2375), etcd (port 2379), HashiCorp Vault (port 8200), HashiCorp Consul, Argo CD. Plus one operator host handed over by Nick: 194.233.71.223.
- **Allowed techniques:** passive Shodan harvest, country-faceted pagination, read-only HTTP GET and HEAD, banner grab, schema and metadata enumeration, public-by-design endpoint probing, cross-survey corpus diffing.
- **Ethical limitations:**
  - No data exfiltration — metadata and schema enumeration only
  - No destructive API calls
  - No use of discovered credentials
  - Data-tier probes: connection attempt only (does auth gate exist? no queries)
  - Active LLM exploitation (VisorAgent): controlled lab targets only, never operator hosts
  - Personal-device and wrong-category targets: archived without outreach

---

## 2. Environment and Tooling

### Claude Code Operation

This was a big-batch day. Eleven surveys ran across roughly nine hours, from the Ollama survey commit at 21:04 to the Argo CD commit at 06:11 the next morning. The orchestrator held strategy and survey sequencing. Each survey was a discrete unit: harvest, verify, cross-diff, ledger-ingest, commit.

The discovery scale forced a tooling decision early. aimap PHASE 3 deep-enumeration was found to run single-threaded per process despite a `-threads N` flag. On the Ollama corpus that meant a projected three to five hours of wall time for verification alone. The orchestrator pivoted to a `fast_enum` direct-prober pattern: a purpose-built read-only verifier per platform, 80 to 200 threads, streaming JSONL output. The Ollama verification then finished in 161 seconds instead of 50-plus minutes. The same pattern carried every subsequent survey: `fast_enum_llamacpp.py`, `fast_enum_docker.py`, `fast_enum_whisper.py`, `fast_enum_etcd.py`, `fast_enum_vault.py`, `fast_enum_consul.py`, `fast_enum_argocd.py`. The underlying aimap bug was fixed the same session in v1.9.4.

Two aimap fingerprints shipped mid-session as a direct product of survey findings. v1.9.4 added the llama.cpp server fingerprint after the alpha-miner host exposed a fingerprint miss. v1.9.5 added the etcd fingerprint, used as the canonical signature for the etcd survey.

### Tools Used

| Tool | Role | Config notes |
|---|---|---|
| shodan_paginate | Stage-0 discovery: paged Shodan harvest | Country-faceted to evade page-70 HTTP 500 (Insight #23) |
| JAXEN | Stage-0 asset ingest into empire.db | Used on the alpha-miner single-host case (13 assets) |
| aimap | Fingerprint signature source; v1.9.4 llama.cpp + v1.9.5 etcd shipped this session | PHASE 3 single-thread bug found and fixed |
| fast_enum family | Population-scale read-only verifier (one per platform) | 80–200 threads, 6s timeout, streaming JSONL |
| VisorLog | Ledger ingest into nuclide.db (ECS schema) | 16,099 events across the day's surveys |
| VisorScuba | Compliance scoring (OPA/Rego) | Rego rules are Ollama-specific; null on llama.cpp/etcd |
| BARE | Metasploit semantic ranking | CVE-2024-37032 ranked #1 across Ollama findings |
| VisorBishop | IP-shadow adjacent-port sweep | shadow_count=0 on every row — port set too narrow (recorded) |
| VisorGraph | Cert-pivot operator attribution | Null on Ollama/llama.cpp/alpha-miner — these platforms ship no TLS |
| VisorSD | ASN/org dork sweep | 0/21 on AS141995 (alpha-miner); Ollama dorks not in the bundled stack |
| VisorGoose | gov-TLD density sweep | 33 gov-TLD hits across 25 TLDs on the Ollama harvest |
| menlohunt | GCP EASM | 10 findings / 3 chains on the one GCP-resident Ollama sample host |
| VisorCorpus | Adversarial corpus generation | 500-case strict hybrid corpus + 135-case finance baseline; kept local |
| cortex | Auth-context analyzer | severity=critical on alpha-miner; schema-mismatch glue pending for batch use |
| nu-recon | Single-host passive deep-read | Load-bearing discovery tool on the alpha-miner case |
| VisorRAG | RAG adversarial confirmation | [—] blocked — OpenAI embeddings API 401 (key absent) |
| recongraph | Seed-polymorphic recon graph | [—] not run — entrypoint packaging bug in this environment |
| VisorAgent | Active LLM exploitation | [—] list-mode only — ethical-stop, never pointed at survey or operator hosts |
| VisorHollow | Windows process-injection benchmark | [—] not applicable — Windows-only binary |
| JS-bundle extract | SPA hidden-API extraction | Ran on alpha-miner SPA (105 KB, no hidden surface); null on Ollama set |

*A null result is a result. recongraph and VisorRAG were blocked by environment faults and are recorded as such. VisorHollow and VisorAgent are the two standing non-run categories.*

### Notable Configuration

The load-bearing configuration finding this session is the Shodan pagination ceiling, codified as Insight #23. On the basic Shodan plan the `/shodan/host/search` API returns HTTP 500 after a depth cap near page 70 on high-population dorks. The `http.html:"Ollama is running"` dork reported 40,508 total hits but delivered only 1,611 unique IPs before the cap fired. The workaround: split the population query along a `country:` facet so each sub-query stays under the depth ceiling. Seventeen country slices recovered 20,890 unique IPs against the truncated 1,611.

Two further harvest constraints shaped the corpora:

- **Dork-population dedup.** Raw Shodan hit counts overstate the unique-IP population. The Ollama html dork returned 6,900 records for 1,611 unique IPs, 4.3 records per IP. Every harvest deduped on `(ip_str, port)` before counting.
- **Honeypot post-filter.** The AS63949 honeypot fleet salts banners with kitchen-sink JSON markers. Shodan banners are too short to carry those markers, so harvest-time honeypot detection caught zero. The post-aimap response-shape filter is the load-bearing one. The Ollama corpus came back honeypot-free at 0%.

Verification ran on `fast_enum` direct probers at 80 to 200 threads with a 6-second timeout. No Shodan API key constraint blocked the harvest. VPN state did not shape the population surveys.

---

## 3. Methodology

The pipeline for every survey was identical: Discover, Verify, Attribute, Classify, Ledger, cross-diff. Verification is the load-bearing stage. A scanner produces candidates. Verification produces findings.

### Enumeration approach

Each survey began with a Shodan-walk harvest. The discovery channel itself is a methodology axis, the lesson codified as Insight #23. The Ollama re-survey is the proof case. The prior tier-1+2 surveys masscanned 5.38M IPs across six budget-cloud ranges and confirmed 1,192 unauth Ollama. The Shodan-walk this session walked `product:Ollama port:11434` (18,191 unique IPs) merged with the country-faceted `http.html:"Ollama is running"` harvest (20,890 unique IPs). Union: 25,092 candidate IPs. The two channels surface disjoint populations. The Shodan-walk caught roughly 3,720 AWS hosts that the budget-cloud masscan never scoped. The methodology lesson: discovery-channel coverage is multiplicative, not redundant. A survey aimed at population completeness must use both.

For the audio-AI platforms a second enumeration lesson surfaced. Voice-cloning's Gradio-based platforms are Shodan-dark. The platform-identifying strings live inside JS bundles Shodan does not index, so the brand-dork harvest returned mostly noise. The voice-cloning survey is honest about this: a true population survey of those platforms requires masscan on Gradio default ports, not a Shodan-walk.

### Candidate identification

Candidates were distinguished from unrelated services by conjunctive fingerprint markers, never single-token brand strings. The voice-cloning survey is the sharp re-confirmation of Insight #15: the `http.title:"RVC"` dork returned 49 candidates and 37 were false positives, an 82% FP rate. "RVC" matched Rockville Centre restaurants, a doctor named R. Van Coevorden, RVC Paint, an RVC Volunteer Center, a Synology NAS named "RVC". Single-token title dorks for common-acronym platforms are not merely lossy, they are dominated by noise. The fix is a second conjunct or a port-first harvest.

Each platform had its own identity conjunct. Ollama: `/api/tags` returning a JSON model list plus `owned_by` markers. llama.cpp: `Server: llama.cpp` header plus `/v1/models` with `owned_by:llamacpp` plus `/props`. Whisper: the `whisper-asr-webservice` Swagger title plus `/openapi.json` schema plus an `/asr` endpoint. Docker daemon: `/version` plus `/info` returning JSON on port 2375. etcd: `/version` plus a `/v2/keys/` listing. Vault: `/v1/sys/seal-status`. Consul: `/v1/agent/self` plus `acl` fields. Argo CD: `/api/version` plus `/assets/config.json`.

### Validation checks

Validation confirmed each candidate as a live, real, unauthenticated instance. The governing rule is Insight #16: a status code is platform identity, not auth state. A 200 proves the service is up, not that the data behind it is exposed. The data-layer probe is what confirms the exposure.

- **Ollama:** GET `/api/version` plus `/api/tags`. The model list proves live unauth. `POST /api/show` then enumerates the Modelfile SYSTEM directive (Insight #24).
- **llama.cpp:** GET `/v1/models` plus `/props`. The `/props` chat_template is the operator-configuration surface.
- **Docker daemon:** `/info` and `/containers/json` returning JSON confirms root-RCE-by-design exposure.
- **etcd:** `/v2/keys/` returning a JSON key listing confirms the namespace is enumerable unauth.
- **Vault:** `/v1/sys/seal-status` and `/v1/sys/init` are public-by-design. An uninitialized state confirms a takeover candidate.
- **Consul:** `/v1/agent/self` with `acl_disabled=true` confirms no ACL gating.
- **Argo CD:** `/api/v1/settings` plus an `/api/v1/applications?limit=1` probe. An anonymous-read response confirms the misconfiguration.

The cross-survey diff is itself a validation and discovery move. Each confirmed corpus was diffed against every other corpus the same day. The overlaps surfaced the worst-class findings: hosts running two unauthenticated surfaces at once.

The Insight #15/#16 family governs the count discipline. Insight #15: dork hits are not platform instances. Insight #16: status code is identity, not auth state. Insight #23: discovery-channel coverage is multiplicative. Insight #24: operator workload is visible through configuration-disclosure endpoints. Insight #25 was confirmed at population scale this session: auth-on-default platforms hold their posture under survey, the falsification result.

### Safeguards

No brute forcing. No privilege escalation. No data exfiltration. No write-tier operations. No credential use. Specific restraint decisions this session:

- The etcd survey listed top-level key names only. It never read `/v2/keys/<full-path>`, which would expose stored values. The key namespace is intelligence-relevant. The values are not enumerated.
- The Vault survey probed only public-by-design endpoints. It never called `/v1/secret/*`, `/v1/auth/*`, or `/v1/sys/mounts`. The three uninitialized Vaults were not initialized. They are documented as claim-able, not claimed.
- The Consul survey listed KV keys only, `?keys=true`, never values. It never issued POST, PUT, or DELETE.
- The Argo CD survey never posted to `/auth/login` and never tested credentials.
- The Docker daemon survey did read-only enumeration only. It never called `/containers/create`, `/images/pull`, or `/exec`, any of which would have demonstrated root shell on the host.
- The voice-agent survey confirmed the LiveKit token-mint endpoint returns valid JWTs. It never connected to a target with one of those tokens, which would have burned operator compute.
- On the alpha-miner host, the plugin loader exposed `subprocess.run` and `os.popen` as registered plugins. The survey did not invoke `/api/plugins/install/`, `/api/plugins/reload/`, or `/api/templates/user/run/`. The capability is inferred from metadata. The names are the finding.
- VisorAgent ran in list-mode only and was never pointed at a survey or operator host.

---

## 4. Execution Trace

Reconstructed from git commit timestamps and case-study sequencing. The trace is survey-granular. SESSION.md has no Session 14 header, and the May 15 work is logged as a chain of "(continued)" entries, so timestamps below the survey level are not recoverable.

| Time | Action | Outcome / Decision |
|---|---|---|
| ~17:00 | Single-host case: 194.233.71.223 handed over by Nick. Full 19-tool arsenal run. | alpha-miner FastAPI quant platform, partial-auth, plugin-loader RCE-by-design. llama.cpp colocated unauth. Commercial 3Proxy fleet colocated. Severity CRITICAL. aimap fingerprint missed llama.cpp despite `Server: llama.cpp` header. |
| ~18:00 | Ollama re-survey selected. Shodan-walk harvest begins. Page-70 HTTP 500 hit on the html dork. | Country-faceted retry across 17 slices. 25,092 union candidate IPs. Insight #23 in formation. |
| ~19:00 | aimap PHASE 3 found single-threaded. Projected 3–5h verification. | Pivot to `fast_enum` direct prober. 161s verification. aimap v1.9.4 fix shipped (commit a888100): llama.cpp fingerprint plus parallel PHASE 3. |
| 21:04 | Ollama survey committed (04c7677). | 16,473 confirmed unauth. 13.8× extension over the prior 1,192. AWS ~3,720 hosts. 1,007 SYSTEM-prompt leaks, 133 operator-customized. Insights #23 and #24 codified. 4,891 events to nuclide.db. |
| 21:38 | llama.cpp HTTP server survey committed (59cb40b). | 1,652 candidates → 965 confirmed unauth. HY-MT1.5 216-host single-operator fleet on AS54801. 29 hosts colocated with unauth Ollama. chat_template corpus axis. 677 events. |
| 21:57 | Voice-cloning survey committed (da8bfce). Survey 17 batch 2. | 49 candidates, 37 FPs (82%). Gradio platforms Shodan-dark. Insight #15 re-confirmed at upper bound. 11 events. |
| 22:07 | Voice-agent survey committed (e7e8a32). Survey 17 batch 3. | 184 LiveKit confirmed. Twirp API auth-on-default (0/184). 31/42 example-app frontends mint JWTs unauth, 74%. Tier-A* slot. 83 events. |
| 22:16 | Unauth Docker daemon survey committed (656776b). Category 12 Docker leg. | 602 candidates → 286 confirmed unauth (100% of responsive port-2375). 21 stacked Docker-plus-Ollama hosts. Cryptojacked host 122.152.235.121 (10 redminer containers). |
| 22:23 | Whisper ASR survey committed (02a260b). Survey 17 batch 1. Survey 17 fully closed. | 537 candidates → 230 confirmed unauth. 145 with unauth POST-audio reachable. Whisper added to the Tier-A platform list. |
| 23:18 | etcd survey committed (215730e). Category 12 etcd leg. Built on aimap v1.9.5. | 3,766 candidates → 3,014 confirmed unauth. 969 v2-key-listable. 237 attacker-write-spray victims, two in-the-wild campaigns. 4 hosts run both etcd and Docker daemon. |
| 23:46 | Vault survey committed (1c5a649). | 2,530 candidates → 912 confirmed. 901 unsealed. 3 uninitialized full-takeover candidates. Tier-Special bootstrap-window slot added. |
| 00:26 (May 16) | Consul survey committed (661f6e8). Largest single survey of the run. | 6,593 candidates → 4,105 confirmed unauth. 100% acl_disabled. 56 hosts with `pwned_scw` attacker spray. HashiCorp trinity closed within 24h. |
| 06:11 (May 16) | Argo CD survey committed (7a604fd). | 10,900 candidates → 4,577 confirmed. Auth-on-default holds at 99.93%. 3 anonymous-read misconfigs. Cleanest Tier-C confirmation of the run. |

---

## 5. Findings

> **Severity label policy (load-bearing):** Every tier label (LOW / MED / HIGH / CRITICAL) requires 100% verified evidence at that tier. Unverified observations are UNRATED. Inferred plus hypothesized stacks do NOT promote to a tier. Only verified components produce labels.

Findings are grouped by platform class. The day produced eleven population-scale corpora and one named-operator host. Verified-unauth counts are the load-bearing numbers.

### 5.1 alpha-miner — 194.233.71.223 — quant platform with plugin-loader RCE and colocated open LLM

| Field | Value |
|---|---|
| **Name/ID** | 194.233.71.223, rDNS `vmi2733226.contaboserver.net`, Contabo Asia, Singapore, AS141995 |
| **Type** | FastAPI/Uvicorn quant trading platform (port 8000) + llama.cpp (port 11434) + 3Proxy commercial fleet (ports 10000–11007) |
| **Evidence** | Six `/api/*` endpoints returned 200 with sensitive data unauth (user roster, RBAC policy, plugin registry). `/api/plugins` lists `subprocess.run` and `os.popen` as registered plugins with description `test`. `/v1/models` on port 11434 returned a Microsoft BitNet-b1.58-2B-4T model unauth. |
| **Observed exposure** | Partial-auth: the OAuth2 scheme exists and is enforced on at least one endpoint, but six discoverable endpoints serve sensitive data unauth. Plugin loader accepts arbitrary Python `module.attr` strings. llama.cpp fully unauth, no rate limit. |
| **Severity** | HIGH (verified). The plugin-loader RCE primitive is inferred from metadata, not invoked, so the RCE itself is UNRATED pending verification. The six unauth data endpoints and the unauth llama.cpp are verified-in-hand and carry the HIGH label. |

**Potential impact:** An unauthenticated actor reads the full user roster and RBAC matrix, enumerates the plugin registry, and uses the colocated llama.cpp for free inference. The presence of `subprocess.run` and `os.popen` in the registry indicates the operator already verified the loader accepts execution primitives, which makes `/api/plugins/install/{package}` a plausible unauthenticated host-RCE primitive. This host also pairs a paid commercial proxy SaaS with an unauthenticated open LLM on the same VPS. A paying proxy customer has a one-hop anonymizing path to free inference. This is the first instance in the survey corpus of the commercial-proxy plus open-LLM colocation pattern, an LLMjacking attribution-laundering vector.

### 5.2 Ollama population — 16,473 confirmed unauthenticated

| Field | Value |
|---|---|
| **Name/ID** | Ollama Shodan-walk population, port 11434 |
| **Type** | LLM model-serving framework |
| **Evidence** | `fast_enum` verification of 25,092 union candidate IPs. 16,473 returned `/api/tags` model lists unauth. 1,007 returned a non-empty SYSTEM directive via `/api/show`. |
| **Observed exposure** | Unauthenticated by framework default. No auth concept exists in Ollama. 4,987 hosts expose the `:cloud` paid-quota billing surface. 1,007 leak operator SYSTEM prompts; 133 of those are operator-customized deployments. |
| **Severity** | HIGH (verified). 16,473 hosts confirmed unauth, model-serving compute and operator workload disclosure. Per-host gov findings escalate per evidence: see below. |

**Potential impact:** Compute theft, model theft, paid-quota drain on the `:cloud` surface. The `/api/show` SYSTEM-prompt corpus discloses what operators built on top of the framework: an Indonesian provincial-government job-information assistant (SI-JACK), a Bitcoin ETF options-trading analyst, a Turkish industrial-robotics expert, Brazilian-Portuguese business chatbots. Two per-host findings carry a CRITICAL label on verified evidence: `103.107.245.11` (`sijoli-11-245-107.jatengprov.go.id`, DINAS KOMINFO Provinsi Jawa Tengah, Indonesian provincial government) and `103.156.110.80` (Pemerintah Provinsi Kalimantan Utara, Indonesian provincial government). Both are verified gov-infrastructure RAG deployments on unauthenticated Ollama. The POSTECH cluster (Korea) leaks an Ollama Cloud Connect URL, raising a subscription-takeover path. 117 academic and government hostnames appeared in the harvest.

### 5.3 llama.cpp HTTP server population — 965 confirmed unauthenticated

| Field | Value |
|---|---|
| **Name/ID** | llama.cpp server population, `product:"llama.cpp"` |
| **Type** | LLM model-serving framework (OpenAI-compatible) |
| **Evidence** | 1,652 candidates verified via `fast_enum_llamacpp.py`. 965 confirmed unauth. 196 with `/completion` and `/v1/chat/completions` reachable. 746 expose chat_template via `/props`. |
| **Observed exposure** | Unauthenticated. 216 of 217 hosts on AS54801 (Zillion Network Inc.) run the identical `HY-MT1.5-1.8B-Q4_K_M.gguf` Tencent Hunyuan machine-translation model. 29 hosts also run unauth Ollama on the same VPS. |
| **Severity** | HIGH (verified). 965 confirmed unauth model-serving hosts. The HY-MT1.5 cluster is a single operator running a 216-host commercial inference fleet unauthenticated, the largest operator-attributed cluster surfaced this year. |

**Potential impact:** Compute theft on the 196 hosts with the completion endpoint reachable. The chat_template corpus is the llama.cpp analogue of the Ollama SYSTEM-prompt corpus: 33 operator-customized templates form the discovery tail, including an operator signature `HauhauCS` across four Gemma-uncensored hosts. The 29-host llama.cpp-plus-Ollama colocation scales the alpha-miner attribution-laundering pattern to a population class.

### 5.4 etcd population — 3,014 confirmed unauthenticated — two in-the-wild attacker campaigns

| Field | Value |
|---|---|
| **Name/ID** | etcd population, port 2379 |
| **Type** | Distributed key-value store (Kubernetes cluster-state backend) |
| **Evidence** | 3,766 candidates verified via `fast_enum_etcd.py`. 3,014 confirmed unauth. 969 with `/v2/keys/` reachable returning JSON key listings. 2,949 with `/metrics` open. 237 hosts show random 32-character attacker-written keys; 600 distinct attacker keys observed. 24 hosts show a `/chatgpt_probe` key. |
| **Observed exposure** | Unauthenticated. 0 TLS-required. The v2 API key listing is accessible with no auth. 237 hosts confirmed victims of an active write-spray campaign. 24 hosts hit by a separate named probing campaign. 18 hosts hit by both. |
| **Severity** | HIGH (verified). 3,014 confirmed unauth secrets-store-class hosts. The 237 attacker-write-spray victims are direct evidence of in-the-wild exploitation: these hosts ARE compromised. |

**Potential impact:** Each unauthenticated etcd is a secrets-store leak class. The v2 key namespace is enumerable. If v2 is write-enabled, an attacker writes arbitrary keys. The 237 random-key-spray hosts show the classic write-access fingerprinting pattern: an attacker writes a uniquely-named test key to confirm write access, then re-visits to verify persistence, typical pre-staging for a second-stage attack. The 189,432-key trio (`106.75.147.217`, `106.75.187.29`, `42.240.135.119`) is a single 3-node operator cluster with all three peers exposed. Four hosts run both unauth etcd and unauth Docker daemon: root RCE plus cluster-state dump, the worst-class stacked exposure of the day. One host (`8.134.51.47`) shows a `/registry/` key, the Kubernetes control-plane data root.

### 5.5 HashiCorp Vault population — 912 confirmed — three uninitialized takeover candidates

| Field | Value |
|---|---|
| **Name/ID** | Vault population, port 8200 |
| **Type** | Secrets-management platform |
| **Evidence** | 2,530 candidates verified via `fast_enum_vault.py` against public-by-design endpoints only. 912 confirmed Vault. 901 unsealed (98.8%). 3 returned an uninitialized state on `/v1/sys/init`. |
| **Observed exposure** | Three Vaults are uninitialized: `152.228.173.65:8200`, `37.187.244.6:8200`, `57.129.62.35:8200`, all v1.16.3. Anyone who calls `POST /v1/sys/init` becomes the root-token holder. The matching version suggests one operator who deployed three instances and never returned to initialize. |
| **Severity** | HIGH (verified). Three uninitialized Vaults are claim-able full-takeover candidates. The bootstrap endpoint is unauth by design as a one-shot operation; an operator who deploys and does not immediately initialize leaves the platform claim-able for the duration of that window. |

**Potential impact:** An attacker who initializes one of the three uninitialized Vaults becomes its root-token holder and controls all secrets the operator subsequently stores. Vault's auth-on-default for `/v1/secret/*` and `/v1/auth/*` is intact at the population layer. The framework correctly gates secret access. The three uninitialized hosts are the bootstrap-window exception. Operator attribution via `cluster_name` surfaced `mhy-cgpaas-vault-cn-prod` across five hosts: miHoYo Cloud Game PaaS production clusters, five production Vault instances visible.

### 5.6 HashiCorp Consul population — 4,105 confirmed unauthenticated — largest survey of the run

| Field | Value |
|---|---|
| **Name/ID** | Consul population, `product:Consul` |
| **Type** | Service-discovery and configuration platform |
| **Evidence** | 6,593 candidates verified via `fast_enum_consul.py` against read-only endpoints. 4,105 confirmed Consul. 100% returned `acl_disabled=true`. 3,811 catalog-listable. 3,846 KV-key-listable (keys only, values not read). 56 hosts have `pwned_scw` registered as a service. |
| **Observed exposure** | 100% of responsive Consul on the public internet has no ACL gating. The service catalog and KV key namespace are enumerable unauth. 56 hosts confirmed victims of an attacker spray that registers a `pwned_scw` service to mark conquered hosts. |
| **Severity** | HIGH (verified). 4,105 confirmed unauth service-discovery hosts. The 56 `pwned_scw` hosts are direct evidence of in-the-wild exploitation via Consul write access. |

**Potential impact:** The service catalog discloses the operator's entire mesh. One host (`51.250.82.249`) shows 1,294 services in its registry. An 8-node Alibaba Cloud operator cluster has all eight peers exposed with an identical 925-service count per peer. Top catalogued services include 1,223 Redis clusters and 102 Vault instances, meaning 102 operators run Consul to service-discover their Vault, a direct link to the day's Vault survey. The `pwned_scw` spray is the third distinct attacker campaign documented this day across three platforms.

### 5.7 Argo CD population — 4,577 confirmed — auth-on-default holds at 99.93%

| Field | Value |
|---|---|
| **Name/ID** | Argo CD population, `http.title:"Argo CD"` |
| **Type** | Kubernetes GitOps continuous-delivery platform |
| **Evidence** | 10,900 candidates verified via `fast_enum_argocd.py` against public-by-design endpoints. 4,577 confirmed Argo CD. 3 returned anonymous-read responses (`anonymousUserEnabled: true` in `argocd-cm`). |
| **Observed exposure** | 99.93% of confirmed Argo CD enforces authentication. 3 hosts (`18.189.197.228:80`, `18.118.178.219:443`, `3.135.97.239:443`) have anonymous read enabled by operator misconfiguration. The last two are one operator's 2-host cluster. |
| **Severity** | OBSERVED. This is a falsification-confirmation result. Argo CD ships auth-on-default and the population confirms it: 4,574 of 4,577 hosts hold the posture. The 3 misconfigured hosts are MED (verified anonymous-read of GitOps application state). |

**Potential impact:** On the 3 misconfigured hosts an unauthenticated actor reads the GitOps application inventory. The headline result is the falsification confirmation: a platform that ships auth-on-default keeps that posture at population scale. 1,138 hosts configure Dex/OIDC SSO; OIDC issuer disclosure via `/api/v1/settings` surfaced roughly 250 named Azure AD tenants and specific Okta-tenanted organizations including 1X Technologies, iRhythm Technologies, and Notta.

### 5.8 Unauth Docker daemon population — 286 confirmed unauthenticated

| Field | Value |
|---|---|
| **Name/ID** | Docker daemon population, port 2375 |
| **Type** | Container-runtime HTTP API |
| **Evidence** | 602 candidates verified via `fast_enum_docker.py`. 286 confirmed unauth. 100% of responsive port-2375 hosts unauth. 379 containers and 1,586 images visible. Host `122.152.235.121` has 10 `redminer:latest` cryptominer containers staged. |
| **Observed exposure** | Every responsive port-2375 host is unauth, matching the framework spec where 2375 is the unauth port and 2376 is the TLS-auth variant. 21 hosts also run unauth Ollama on the same VPS. |
| **Severity** | HIGH (verified). Each unauth Docker daemon is root RCE on the host by API design. The cryptojacked host is a verified active compromise. |

**Potential impact:** `POST /containers/create` with a host-root bind mount plus a chroot command yields a shell on the host. The 21 Docker-plus-Ollama hosts are stacked operator catastrophes: root RCE plus AI workload, full host takeover plus model tampering. The cryptojacked host shows the unauth-Docker-daemon to cryptojacker pipeline at confirmed-active scale. STARK INDUSTRIES SOLUTIONS LTD, a provider widely reported as bulletproof hosting, accounts for 9 of the 286 hosts.

### 5.9 Whisper ASR population — 230 confirmed unauthenticated

| Field | Value |
|---|---|
| **Name/ID** | Whisper ASR population (Survey 17 batch 1) |
| **Type** | Speech-to-text inference service |
| **Evidence** | 537 candidates verified via `fast_enum_whisper.py`. 230 confirmed unauth. 145 with `/asr` or `/v1/audio/transcriptions` reachable for unauth POST. 137 ship the canonical `ahmetoner/whisper-asr-webservice` Swagger title. |
| **Observed exposure** | Unauthenticated by container default. The `whisper-asr-webservice` Docker image ships no auth. 145 hosts accept unauth audio POST. |
| **Severity** | MED (verified). 230 confirmed unauth ASR hosts, compute-theft surface. No PHI or clinical hostnames surfaced this run, so no higher tier is supported by evidence. |

**Potential impact:** Anyone can POST a multi-minute audio file and burn the operator's GPU or CPU on Whisper-large-v3 transcription. This is the audio-modality analogue of the Ollama `/api/generate` compute-theft surface. 13 hosts run both unauth Whisper and unauth Ollama, the multi-modal stacked operator class: an attacker pipes audio through Whisper to Ollama end-to-end on the operator's resources.

### 5.10 Voice-agent population — 184 LiveKit confirmed — 74% unauth token-mint

| Field | Value |
|---|---|
| **Name/ID** | Voice-agent population (Survey 17 batch 3), LiveKit-dominant |
| **Type** | Real-time voice-AI platform |
| **Evidence** | 303 candidates verified. 184 LiveKit confirmed. The Twirp room API returned 0 unauth `ListRooms` responses across all 184. 31 of 42 example-app frontends mint participant JWTs unauth via `/api/connection-details` or `/api/token`. |
| **Observed exposure** | Two separate auth tiers. LiveKit's Twirp API is auth-on-default (Tier-C, 0/184 unauth). LiveKit's example-deployment frontend ships the token-mint endpoint unauth (Tier-A*, 31/42, 74%). |
| **Severity** | MED (verified). 31 hosts mint full-participant JWTs unauth. The JWT grants `roomJoin`, `canPublish`, `canSubscribe`, `canPublishData`. One host (`34.58.247.238`) mints tokens with `roomCreate: true`. |

**Potential impact:** Anyone with a minted JWT connects to the operator's voice-agent room, publishes audio to talk to the AI, and burns the operator's LLM, STT, and TTS compute on every utterance. The leaked `serverUrl` field discloses operator deployments: an Italian banking voice agent (`banca-bqopqpjr.livekit.cloud`), an India Skilling Bot, a debt-collection bot, interview-screening bots. These are categories where unauth voice-agent abuse has direct real-world impact. One host runs both the unauth voice-agent frontend and unauth Ollama. This finding establishes the Tier-A* methodology slot: framework-auth-tier and example-template-auth-tier are separate axes.

### 5.11 Voice-cloning population — methodology finding, Shodan-dark

| Field | Value |
|---|---|
| **Name/ID** | Voice-cloning population (Survey 17 batch 2) |
| **Type** | Voice-conversion and TTS platforms (Gradio-based) |
| **Evidence** | 49 candidates from 7 brand-dorks. 37 false positives (82%). 6 real commercial voice-cloning hosts, 5 Coqui TTS demo servers, 1 defensive Deepfake Awareness Portal. |
| **Observed exposure** | The 6 real hosts are commercial voice-clone SaaS with admin-gated voice models. The 5 Coqui TTS hosts expose `/api/tts` unauth, base public models only. |
| **Severity** | OBSERVED / UNRATED. The population is severely undercounted because Gradio platforms are Shodan-dark. The survey's contribution is methodological, not a verified population count. |

**Potential impact:** The actionable output is a methodology lesson, not an exposure tier. Voice-cloning's Gradio-based platforms hide their brand strings in JS bundles Shodan does not index. A real population survey requires masscan on Gradio default ports. The 5 Coqui TTS hosts have an unauth compute-theft surface but proving it crosses the restraint line. No operator-uploaded named voices surfaced.

---

### Findings by severity

**CRITICAL** — `103.107.245.11` and `103.156.110.80`: verified Indonesian provincial-government RAG deployments on unauthenticated Ollama. Gov infrastructure, verified data class.

**HIGH** — alpha-miner host (verified unauth data endpoints + unauth llama.cpp); Ollama population (16,473 confirmed); llama.cpp population (965 confirmed); etcd population (3,014 confirmed, 237 confirmed-compromised); Vault (3 uninitialized takeover candidates); Consul (4,105 confirmed, 56 confirmed-compromised); Docker daemon (286 confirmed, 1 confirmed-compromised cryptojacked host).

**MED** — Whisper ASR (230 confirmed unauth compute-theft surface); voice-agent token-mint (31 hosts mint full-participant JWTs); Argo CD 3 anonymous-read misconfigs.

**LOW** — Argo CD OIDC issuer disclosure (named tenant enumeration via a public endpoint).

**OBSERVED** — Argo CD auth-on-default holds at 99.93%, the falsification-confirmation result; LiveKit Twirp API auth-on-default at 0/184.

**UNRATED** — alpha-miner plugin-loader RCE primitive (inferred from metadata, not invoked); voice-cloning population count (Shodan-dark, undercounted).

---

## 6. Risk Assessment

### Overall Posture

The posture is systemic, not isolated. Across eleven population surveys the auth-on-default thesis held in every direction it was tested. The pattern is not a scatter of misconfigured hosts. It is a property of the platforms.

The day confirmed the central methodological split. Platforms divide into auth-tiers, and the tier predicts the population outcome:

- **Tier A** — no auth concept in the framework. Ollama, llama.cpp, Whisper, vLLM, Triton. Population unauth rate 95 to 100%.
- **Tier A*** — auth optional, off by default in the example-deployment template. LiveKit's `/api/connection-details` starter. 74% unauth at population.
- **Tier A**** — auth off by default in framework config, operator must opt in. Consul ACLs. 100% unauth at population. No operator opts in.
- **Tier C** — auth on by default. Argo CD, Vault's secret API, LiveKit's Twirp API. 99.67 to 100% hold the posture.
- **Tier-Special** — bootstrap endpoint unauth by design for a one-shot window. Vault `/v1/sys/init`. Creates a takeover surface for the duration of the pre-init window.

The same operator demographic, k8s-adjacent infrastructure engineers, produced opposite outcomes on Argo CD and Consul. The only variable is the shipping default. This reproduces Insight #13: shipping defaults are load-bearing.

### Confidentiality

Operator data is at risk across every Tier-A and Tier-A** corpus. Ollama discloses installed models, paid-quota billing surface, and via `/api/show` the operator SYSTEM prompts that fingerprint real business deployments. etcd discloses cluster-state key namespaces and, where v2 is reachable, the structure of stored secrets. Consul discloses the full service mesh, every Redis cluster, every co-located Vault. Argo CD's OIDC issuer disclosure enumerates named corporate tenants. The two Indonesian provincial-government hosts expose gov RAG pipelines.

### Integrity

Integrity is already compromised on confirmed hosts. The etcd survey found 237 hosts with attacker-written keys and the Consul survey found 56 hosts with an attacker-registered `pwned_scw` service. Three distinct attacker campaigns are documented this day across three platforms: the Ollama `leak_model_*` spray (1,072 victims), the etcd random-32-char-key spray (237 victims), and the Consul `pwned_scw` spray (56 victims). An unauthenticated actor with write access to etcd or Consul can corrupt cluster state and service-discovery records. The three uninitialized Vaults allow an attacker to seize root and control all future secrets.

### Availability

Availability is degradable across the compute-bearing corpora. Every unauth Ollama, llama.cpp, and Whisper host is a free-compute surface, exhaustible by an unauthenticated actor. The 4,987 Ollama hosts on the `:cloud` billing surface are paid-quota drain targets. The 31 voice-agent hosts burn LLM, STT, and TTS compute on every utterance an attacker sends. Each unauth Docker daemon allows container deletion and host disruption. The cryptojacked Docker host is the demonstrated end state: operator compute fully appropriated.

### Systemic Patterns

- **Shared root cause.** The framework shipping default is the single variable. Auth-on-default platforms hold; auth-off-default platforms fail at population scale. This is one root cause expressed across eleven surveys.
- **Cross-platform colocation.** Hosts running two unauthenticated surfaces at once are the worst class. 21 Docker-plus-Ollama hosts, 29 llama.cpp-plus-Ollama hosts, 14 etcd-plus-Ollama hosts, 4 etcd-plus-Docker hosts, 13 Whisper-plus-Ollama hosts. The cross-survey diff is the discovery move that surfaces them.
- **Attribution-laundering.** The alpha-miner host introduced the commercial-proxy plus open-LLM colocation pattern. The llama.cpp survey found it at 29 hosts. A paid proxy customer gets a one-hop anonymizing path to free inference.
- **In-the-wild exploitation at population scale.** Three attacker campaigns, three platforms, one day. The unauth-AI-and-infra surface is not a theoretical risk. It is being actively claimed.
- **Operator-template propagation.** LiveKit's example app ships the token-mint endpoint unauth. Operators clone the example and inherit the posture. The framework gets a Tier-C grade; the operator inherits Tier-A*.

---

## 7. Recommendations

### R1 — Tier-A frameworks shipping no auth concept (Ollama, llama.cpp, Whisper)

Operators cannot configure auth that the framework does not expose. The fix is network-layer.

```bash
# Bind the listener to loopback, front it with an authenticating reverse proxy
OLLAMA_HOST=127.0.0.1:11434 ollama serve
# nginx in front, basic-auth or OAuth proxy, TLS terminated at the proxy
```

This works because it removes the service from the public internet entirely. The only path to the model becomes the authenticated proxy. It prevents compute theft, model theft, paid-quota drain, and SYSTEM-prompt disclosure.

### R2 — Tier-A** frameworks shipping auth off by default in config (Consul)

The operator must opt in to ACLs. The survey found 100% do not.

```hcl
# consul config: ACLs default-deny, then grant explicit tokens
acl {
  enabled        = true
  default_policy = "deny"
  down_policy    = "extend-cache"
}
```

This works because `default_policy = "deny"` inverts the failure mode. An unconfigured ACL system then refuses access instead of granting it. It prevents service-mesh disclosure and the `pwned_scw`-class write spray.

### R3 — etcd unauth key store

```bash
# require client-cert TLS and peer auth; never expose 2379 plaintext
etcd --client-cert-auth --trusted-ca-file=/etc/etcd/ca.crt \
     --cert-file=/etc/etcd/server.crt --key-file=/etc/etcd/server.key
# disable the v2 API surface entirely on v3 deployments
etcd --enable-v2=false
```

`--client-cert-auth` gates the API behind a certificate. `--enable-v2=false` removes the v2 key-listing surface that 969 hosts exposed. Together they prevent cluster-state disclosure and the write-spray pattern.

### R4 — Vault uninitialized takeover window

```bash
# initialize immediately after deploy; never leave a Vault un-init on a public IP
vault operator init -key-shares=5 -key-threshold=3
# until initialized, bind to loopback or a private subnet only
```

The init operation must be unauth by design as a one-shot bootstrap. The fix is to close the window: initialize at deploy time, and never expose an uninitialized Vault to a routable address. This prevents the `POST /v1/sys/init` takeover.

### R5 — Docker daemon root-RCE surface

```bash
# never expose 2375; use the TLS-auth socket 2376, or local socket only
dockerd --tlsverify --tlscacert=ca.pem --tlscert=server-cert.pem \
        --tlskey=server-key.pem -H=0.0.0.0:2376
```

Port 2375 is unauth by spec. Moving to 2376 with `--tlsverify` requires a client certificate for every API call. This prevents the `/containers/create` host-root escape.

### R6 — Example-template auth-tier (LiveKit and similar)

Operators deploying from an example app must audit the example's auth posture before exposing it. Add server-side auth in front of any token-mint endpoint.

```javascript
// gate /api/connection-details: require a session before minting a JWT
if (!req.session?.user) return res.status(401).end();
```

This works because the LiveKit token-mint endpoint ships unauth in the starter for demo convenience. A session check makes the JWT mint a privileged operation. It prevents anonymous room-join and the per-utterance compute drain.

### Future automation

Population drift is the recurring threat. The Ollama Shodan dork grew 52% in 15 days. Surveys should run on a schedule, not on demand.

```bash
# periodic per-platform exposure check across an org's public ranges
aimap -list your-public-ips.txt \
      -ports 11434,8000,2375,2379,8200,8500,3000,9000 \
      -scan-all-fingerprints -o report.json
# diff against the prior run; alert on any new confirmed-unauth host
```

A scheduled run plus a delta diff catches a new exposure within a survey cycle instead of within a quarter. The cross-survey diff should be standing automation: any host appearing in two confirmed-unauth corpora is auto-flagged as a stacked exposure.

---

## 8. Limitations and Assumptions

| # | Limitation | Risk Implication |
|---|---|---|
| L1 | Analysis reconstructed from case studies and git history. SESSION.md has no Session 14 header; execution trace is survey-granular, not timestamp-granular. | Sub-survey ordering and intra-survey timing are inferred from commit timestamps, not logged directly. |
| L2 | Voice-cloning's Gradio-based platforms are Shodan-dark; the survey saw 49 candidates against a true population estimated 100 to 200× larger. | The voice-cloning population count is not a finding. It is a methodology placeholder pending a masscan follow-up. |
| L3 | etcd v3 uses gRPC primarily; the survey probed only the v2 HTTP gateway. v3-only hosts return 404 on `/v2/keys/` and look auth-protected to this prober. | The 969 v2-key-listable count is a lower bound. The true unauth-listing etcd population is larger. |
| L4 | The Kubernetes control-plane subset of etcd was detected via the `/registry/` top-level key signal, which caught 1 host. Real k8s clusters may hide their data behind v3-only gRPC. | The k8s-secrets-exposure tier is undercounted. A gRPC follow-up survey is needed. |
| L5 | aimap PHASE 3 deep-enumeration was single-threaded; verification ran on custom `fast_enum` direct probers instead. The aimap-native deep-enum path was not exercised at population scale this session. | The fast_enum probers cover a narrower endpoint set per platform than aimap's full deep-enum. Some secondary attributes were not collected. |
| L6 | Write-tier operations were never tested on any platform, per the restraint ethic. | The survey confirms unauth read or unauth bootstrap. It does not confirm write access except where an attacker already demonstrated it (the etcd and Consul spray victims). |
| L7 | VisorBishop reported `confirmed=false` on all high-value Ollama hosts and shadow_count=0 on every llama.cpp row; its known-service set and IP-shadow port set are too narrow. | The 15-port IP-direct adjacency sweep (Insight #12 territory) did not execute. Adjacent-port exposures around the confirmed hosts were not measured. |
| L8 | VisorRAG was blocked on a missing OpenAI embeddings key; recongraph failed on an entrypoint packaging bug; cortex had a JSON-vs-markdown schema mismatch for batch use. | Three tools produced no output. RAG adversarial confirmation and seed-polymorphic graphing were not run. |
| L9 | Internal-only deployments behind a firewall are invisible to a Shodan-walk by definition. | Every population count is a count of the publicly-indexed surface, not the total deployed population. |
| L10 | Operator attribution on the alpha-miner host did not reconcile: Vietnamese-pattern usernames on an Indonesian-domain-cluster Contabo VPS. Attribution confidence is recorded as low. | The named-operator claim on that host is held at low confidence. The technical-exposure claims are reproducible from a single unauth GET and are high confidence. |

---

## 9. Proof of Concept (PoC) Illustrations

> PoCs use minimal, read-only interactions. No operator data extracted. No credentials used. No exploit payloads. They demonstrate existence and risk conceptually only.

### PoC 1: Ollama unauthenticated model-list probe

**Scenario:** An unauthenticated actor confirms an Ollama host is live and reads the operator's installed-model list.

```
REQUEST:
  GET /api/tags HTTP/1.1
  Host: <operator-host>:11434

RESPONSE:
  HTTP/1.1 200 OK
  Content-Type: application/json

  {"models":[
    {"name":"<model>:<tag>","size":<int>,"modified_at":"<timestamp>",
     "details":{"family":"<family>","parameter_size":"<size>"}}
  ]}
```

**Demonstrated:** The host is a live, unauthenticated Ollama instance. The actor now knows the installed models and can target the compute. It does NOT confirm SYSTEM-prompt exposure; that requires a separate `POST /api/show` probe. It does NOT invoke `/api/generate`, which would consume operator compute. The 200 confirms identity. The JSON body confirms the exposure (Insight #16).

### PoC 2: etcd v2 unauthenticated top-level key listing

**Scenario:** An unauthenticated actor enumerates the top-level key namespaces of an exposed etcd, without reading any stored value.

```
REQUEST:
  GET /v2/keys/ HTTP/1.1
  Host: <operator-host>:2379

RESPONSE:
  HTTP/1.1 200 OK
  Content-Type: application/json

  {"action":"get","node":{"dir":true,"nodes":[
    {"key":"/<namespace>","dir":true},
    {"key":"/<namespace>","dir":true}
  ]}}
```

**Demonstrated:** The etcd v2 API is reachable with no auth and the top-level key namespaces are enumerable. The namespace names reveal usage: `/registry` indicates a Kubernetes control plane, `/service` indicates a service registry, a random 32-character key indicates an attacker has already write-tested the host. The PoC lists key NAMES only. It does NOT issue `GET /v2/keys/<full-path>`, which would return stored values. It does NOT write a key. The restraint boundary is the difference between namespace structure (intelligence) and stored secrets (exfiltration).

### PoC 3: LiveKit example-app unauthenticated participant-token mint

**Scenario:** An unauthenticated actor requests a participant JWT from a LiveKit example-app frontend and inspects the granted permissions, without connecting to the voice-agent.

```
REQUEST:
  POST /api/connection-details HTTP/1.1
  Host: <operator-host>:<port>
  Content-Type: application/json

  {"room":"<arbitrary>","identity":"<arbitrary>"}

RESPONSE:
  HTTP/1.1 200 OK
  Content-Type: application/json

  {"serverUrl":"wss://<operator-deployment>",
   "roomName":"<room>",
   "participantToken":"<JWT>",
   "participantName":"<identity>"}

  -- JWT payload (decoded, not verified) --
  {"video":{"room":"<room>","roomJoin":true,
            "canPublish":true,"canSubscribe":true,"canPublishData":true}}
```

**Demonstrated:** The example-app frontend mints a full-participant JWT with no authentication. The token grants room-join, publish, and subscribe. The `serverUrl` discloses the operator's named LiveKit deployment. The PoC mints and decodes the token only. It does NOT use the token to connect to the LiveKit server, which would join the operator's room and burn LLM, STT, and TTS compute on every utterance. The minted-and-decoded token is proof the surface exists. Connecting would cross the compute-theft line.

---

*Prepared by NuClide Research (Nicholas Kloster + Claude Sonnet 4.6) · Session 14 · 2026-05-15*
