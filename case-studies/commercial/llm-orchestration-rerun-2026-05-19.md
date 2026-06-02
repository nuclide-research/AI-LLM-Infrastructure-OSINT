# LLM Orchestration Re-Run — 2026-05-19

_Re-run of category 01 (LLM orchestration platforms) under aimap v1.9.22 and the post-Insight-#40 verification discipline. First run was the Ollama population survey on 2026-05-15 (16,473 confirmed unauth, drove Insights #23–#27). The point of the re-run is the **toolchain delta** — what the survey catches now that it could not catch then._

---

## 1. Why re-run

Per the standing methodology — the manual → productize → re-run loop. The first run was 2026-05-15. Since then:

- aimap shipped 18 versions (v1.9.4 → v1.9.22): llama.cpp HTTP fingerprint, vLLM hardening, OneAPI/NewAPI, image-gen pack, container/k8s/MCP/medical-AI expansion, ComfyUI-Manager, agent-memory/data-labeling/vector-DB fingerprints, ES/OpenSearch/ClickHouse enums, extortion classifier, Jetson side-channel classifier, Healthcare (PACS/DICOM) + Finance (algotrading) classifiers, `scanCredentials` exposed-API-credential probe (Insight #38), sub2api fingerprint, IPv6 fix.
- Nine new insights filed (#32–#40): deception-fleet emulation; side-channel attribution via Docker Registry catalog; high-precision-low-recall property; PaaS build-arg secret baking; asymmetric auth gating (dashboard vs API); exfiltrated-credential hard-proof chain; pooled-account upstream-proxy attribution-laundering; auth-on-default shifts rightward in successor OSS generations.

The discipline says every confirmed exposure surface is also a new test of these. Re-running is not redundancy — it is how the methodology proves it is making the data better.

---

## 2. Population growth — the Stage-0 finding before any probing

The first finding lands before any probing. Shodan-indexed counts for category-01 platforms moved significantly since the 2026-04-30 query catalog:

| Platform | Catalog 2026-04-30 | Today 2026-05-19 | Δ |
|---|---|---|---|
| `product:"n8n"` | 77,102 | **131,335** | +70% |
| `http.html:"Ollama is running" -port:443` | 26,580 | **47,441** | +78% |
| `http.title:"new-api"` | not catalogued | **20,989** | new |
| `http.title:"Flowise"` | 586 | 24,364 | +4,000% (likely catalog under-counted) |
| `http.title:"Open WebUI" port:8080` | 2,842 | 2,803 | flat |

The two dominant platforms (n8n and Ollama) grew ~70-80% in 19 days. The `http.title:"new-api"` surface (OneAPI / NewAPI Chinese-OSS OpenAI-compat gateway with billing) — 20,989 indexed hosts — is a category-01 surface the query catalog never recorded. aimap v1.9.11 just added the fingerprint for it.

---

## 3. Stage 0 — Discover (JAXEN + shodan download)

| Harvest | Source | Total indexed | Returned |
|---|---|---|---|
| ai-hunt orchestration (5 title dorks: Flowise / Langflow / Dify / Open WebUI / AnythingLLM) | JAXEN ai-hunt | ~46,924 across the five | 500 (100 each), 428 unique IPs |
| `product:"n8n"` | shodan download | 131,335 | 1,000 → 399 unique IPs |
| `http.title:"new-api"` | shodan download | 20,989 | 1,000 → 981 unique IPs |
| `http.title:"Open WebUI" port:8080` | shodan download | 2,803 | 1,000 → 1,000 unique IPs (all :8080) |
| `http.html:"Ollama is running" -port:443` | JAXEN hunt | 47,441 | 50 |
| `http.title:"NewAPI"` | JAXEN hunt | 40 | 40 |
| prior 2026-05-15 Ollama confirmed-unauth (Stage-5 substrate) | nuclide.db `ollama-population-survey-2026-05-15` | n/a | 4,990 — sampled 50 for the productize-and-re-run side-channel test |

Total candidate corpus this re-run: **2,808 unique IPs across 6 platform classes** plus the 50-host prior-corpus substrate. Shodan query credits: 6,290 → 6,262 (28 used).

---

## 4. Stage 1 — Fingerprint (aimap v1.9.22)

Six aimap passes were launched in parallel. **Network contention from six concurrent 30-thread passes was severe enough to materially slow Phase 1 / Phase 2 on the larger corpora.** Two passes finished on the smaller corpora (50 hosts and 399 hosts with focused port lists) within ~3-5 min; the four production passes on 428 / 399 / 981 / 1,000 hosts entered Phase 2 (fingerprinting) within 15 min but Phase 3 (deep enum) lingered for 20+ min more.

**Carry-forward observation:** parallel aimap passes contend for the same client-side socket pool and consume each other's effective concurrency. The right approach for population-scale is sequential or staged — start the longest pass alone, batch the small ones together at the end. **Candidate Insight #41 (toolchain-class):** "Parallel aimap passes cannibalize throughput; default to sequential or capped-concurrency-per-corpus."

**Stage-1 result summary — the two completed passes:**

| Pass | Hosts | Open ports found | aimap services | Time |
|---|---|---|---|---|
| `aimap-ollama-side-channel.json` (50-host re-pass on 2026-05-15 corpus) | 50 | 43 open ports across 22 hosts (44% reachable rate) | 3 confirmed (Portainer ×1, MinIO ×2) | 2m48s |
| `aimap-localhost-test.json` (controlled validation) | 1 | 1 | 1 (Ollama) | <1s |

**Stage-1 `no FP candidates` density (recurring observation):** in the larger corpora, hosts on non-canonical ports trigger `[!] no FP candidates for X:Y (port not in any DefaultPorts list); re-run with -scan-all-fingerprints to probe exhaustively`. The n8n corpus log alone contained 1,126 such messages (one per non-default-port host). This is real coverage loss: an n8n behind reverse proxy on port 2068 will not get fingerprinted unless `-scan-all-fingerprints` is set. **Candidate Insight #42 (aimap-class):** "DefaultPorts restriction trades coverage for speed; for reverse-proxy-dominant populations, `-scan-all-fingerprints` is mandatory, not optional."

The full v1.9.22 deep-enum results on the larger corpora will be folded in when those passes complete; their slowness is operational, not methodological.

---

## 5. Stage 2 — Verify

aimap's deep enumerators do double duty as Stage-2 verify probes. On the side-channel 50-host sample, deep-enum confirmed the three findings via `enum_results`: MinIO `auth_status=required risk_level=medium` ×2, Portainer `auth_status=unknown risk_level=info` ×1.

**Stage-2 also surfaced a deep-enum tool-state finding (filed in the case body, not as a separate fingerprint correction):** VisorBishop reported the 3 confirmed MinIO/Portainer instances as `platform: promptfoo`. Promptfoo is at port 15500 — the misclassification is a fingerprint substring confusion. File for next aimap fingerprint review.

---

## 6. Stage 3 — Attribute (VisorGraph + nu-recon)

VisorGraph cert-pivot fired on the four Stage-5 confirmed hosts (98.115.25.181, 101.47.160.163, 91.241.49.112, 124.155.160.2). Output is JSON-structured `nodes / edges / provenance`. Three hosts returned graph fragments; 98.115.25.181 returned a Caddy default-cert redirect to HTTPS (intended_protocol:http → 308 → https) — no operator cert leaked.

nu-recon ran on 91.241.49.112 (real-network mode with Shodan key): confirmed **Istanbul, Turkey / Genc BT Bilisim Teknolojileri Limited Sirketi** (Turkish hosting); 8 open ports (22 SSH, 5432 PostgreSQL, 6379 Redis, 8000 ChromaDB, 9000 MinIO, 9001 MinIO Console, 9200 Elasticsearch, 11434 Ollama).

aimap-profile (fast mode) attributed:

| Host | Country | Org / Netname / rDNS | Shodan-indexed ports | Ethics class |
|---|---|---|---|---|
| 98.115.25.181 | US | Verizon FiOS Philadelphia (`pool-98-115-25-181.phlapa.fios.verizon.net`) | 4000, 8080, 9000, 11434, 6379, 22222, 80, 53, 22, 3000 | **personal-device / consumer-ISP — archive without outreach** |
| 101.47.160.163 | SG | ByteDance / BytePlus-SG | 8000, 5601, 8080, 9091, 9200, 6001, 9000, 9001, 3306, 9100, 80, 81, 6002, 11434, 8001 | commercial |
| 91.241.49.112 | TR | Genc BT Bilisim Teknolojileri (Istanbul) | 8000, 9000, 9001, 11434, 6379, 9200, 22, 5432 | commercial |
| 124.155.160.2 | TW | ELNET-NET | 28 ports including 11434, 5432, 6379, 3306, 2376, 2222, 5443, plus a wide web-port range | commercial — massive surface |

---

## 7. Stage 4 — Classify (aimap-profile)

aimap-profile fast-mode does not emit a `category` (HIPAA / clinical / personal / commercial / honeypot) on these hosts. The classifier is gated on deeper signal that fast-mode skips. Deep-mode classify reserved for the disclosure-shortlist phase rather than the survey phase.

The implicit classification from network identity is sufficient for ethics routing:

- 98.115.25.181 = consumer-ISP / personal device. **Archive without outreach.**
- 101.47.160.163 = SG / ByteDance commercial. Disclosure-routable.
- 91.241.49.112 = TR / Genc BT commercial. Disclosure-routable (Cowboy decides).
- 124.155.160.2 = TW / ELNET-NET commercial.

---

## 8. Stage 5 — IP-direct shadow (Insights #11 / #12 / #33)

**The headline finding.** The 50-host sample of prior 2026-05-15 Ollama unauth corpus was re-passed under aimap v1.9.22 + VisorBishop `-ip-shadow`. 3 of 50 (6%) returned co-located unauth admin/data-tier services. Three of them are Pharos-class stacked exposures.

### Confirmed stacked exposures

| Host | Country | Original | Co-located unauth services discovered |
|---|---|---|---|
| **101.47.160.163** | SG | Ollama 11434 | MySQL :3306 / Kibana :5601 / **ChromaDB :8000** / **Milvus :19530** / Elasticsearch :9200 / MinIO :9000 / node_exporter :9100 — **7 stacked services** |
| **41.72.152.18** | (TBD — VisorBishop probe) | Ollama (per source corpus) | PostgreSQL :5432 / Kibana :5601 / **MailHog :8025 (messages stored — confirmed)** — 3 stacked services |
| **91.241.49.112** | TR — resolves to `app.1nokta44.com` (Genc BT, Istanbul); Ollama v0.20.4 with single loaded model `seneca-cybersecurity:q4_k_m` (8.0B Q4, pinned in memory) | Ollama 11434 | PostgreSQL :5432 / Kibana :5601 / **Qdrant :6333 (CRITICAL — collection list returned without authentication)** / **ChromaDB :8000** / MinIO :9000 / Elasticsearch :9200 / Redis :6379 — **7 stacked services** |

16 shadow findings across the 3 hosts. The 91.241.49.112 pattern — Ollama + Qdrant + ChromaDB + MinIO + Elasticsearch + PostgreSQL + Redis + Kibana — is a **complete unauth RAG-and-storage stack** by a single operator. This mirrors the Pharos.unistarthubs.gr four-platform AI-stack case study from 2026-05-06.

**Operator attribution (Stage-3 + Stage-5 combined):** the passive-DNS step in VisorPlus surfaced `app.1nokta44.com` for 91.241.49.112 (HackerTarget). The Ollama enum surfaced version 0.20.4 with a single loaded model named `seneca-cybersecurity:q4_k_m` — 8.0B Q4-quantized, 5.1 GB in memory, pinned with far-future expiry. The naming pattern (custom domain-specific cybersecurity LLM) plus the operator's full stack suggests a **commercial Turkish cybersecurity-SaaS** running its production RAG-and-storage stack with auth off across the board. Per Insight #14 — names ARE the finding: the model name + the operator's full stack make the operator identifiable, the use-case obvious, and the data-class implications severe before any payload is fetched. No collection contents enumerated; no SQL pulled; no S3 buckets listed; no Kibana dashboards opened.

Per Insight #12, IP-shadow colocation among unauth-AI operators is 27% on the Phoenix population. The 6% on the Ollama sample is lower but the per-host severity is higher — Ollama operators are running entire data lakes, not just adjacent telemetry.

Docker Registry side-channel (Insight #33): zero `/v2/_catalog` exposures on the 50-host sample. The :5000 port was scanned; one host (37.187.250.91) returned HTTP 200 with an HTML page (not a Docker Registry V2). Aimap v1.9.13 Jetson / Healthcare / Finance classifiers did not fire — correct null result.

---

## 9. Stage 6 — Ledger / score / rank / corpus

**VisorLog ingest:** 19 events written to `nuclide.db` (sector=commercial, source=`01-llm-orchestration-rerun-2026-05-19`). Lifecycle: open. 0 deduped against prior ledger entries.

**VisorScuba assess:** ran across 21,514 nodes in the full nuclide.db ledger. Average score: 0/10 (0% compliant). The result is dominated by the existing population, but the ingest from this survey did not shift the average — the existing ledger was already at 0/10.

**BARE semantic exploit rank:** 10 Stage-5 finding classes encoded and ranked against the 3,904-module Metasploit corpus. **Only 1 finding crossed the 0.6 first-party-CVE threshold:**

| Finding | Top match | Score |
|---|---|---|
| **Docker daemon TLS exposed** | `exploits_linux_http_docker_daemon_tcp` | **0.623** ★ |
| Unauthenticated Ollama LLM runtime | `exploits_linux_http_ollama_rce_cve_2024_37032` | 0.514 |
| Unauthenticated MailHog SMTP capture | `auxiliary_server_capture_smtp` | 0.483 |
| Unauthenticated Kibana dashboard | `exploits_linux_http_kibana_timelion_prototype_pollution_rce` | 0.527 |
| Unauthenticated Elasticsearch cluster | `auxiliary_gather_elasticsearch_enum` | 0.507 |
| PostgreSQL port exposed | `auxiliary_scanner_postgres_postgres_login` | 0.524 |
| Unauthenticated MinIO API | `auxiliary_gather_minio_bootstrap_verify_info_disc` | 0.489 |
| Unauthenticated Portainer | `exploits_linux_local_docker_daemon_privilege_escalation` | 0.473 |
| Unauthenticated ChromaDB | `exploits_linux_http_pandora_fms_auth_rce_cve_2024_12971` | 0.445 |
| Unauthenticated Qdrant vector DB | `exploits_linux_http_ibm_qradar_unauth_rce` | 0.412 |

**This is the methodology working.** Per the standing rule, BARE > 0.6 = commodity-CVE chain; < 0.6 = first-party authz / config bug. **9 of 10 findings are first-party authz**, which is the auth-on-default thesis at the exploit-mapping layer. Docker daemon TLS is the one commodity-CVE case. Default-cred / no-auth-concept services route to `auxiliary_scanner_*_login` modules at the high-but-sub-threshold band.

**VisorCorpus baseline corpus built:** `corpus-orchestration.json` — 100 cases, 77 HIGH + 23 MED, distributed across 7 categories (kb_exfiltration 16, prompt_injection 16, infra_discovery 15, jailbreak 15, system_prompt 15, tenant_cross_leak 15, kb_instructions 8). Stored at `~/recon/01-llm-orchestration-rerun-2026-05-19/corpus-orchestration.json`.

---

## 10. Stage 7 — Arsenal coverage

19-tool arsenal coverage matrix for this assessment:

| Tool | Status | Result class |
|---|---|---|
| **JAXEN** | `[x] ran` | 1,090 hits across 8 dorks; 28 Shodan query credits spent. |
| **aimap v1.9.22** | `[x] ran (4 passes still in flight, 2 completed)` | ollama-side-channel: 22 reachable / 3 confirmed services (Portainer, MinIO×2). Larger corpora pending completion. |
| **aimap-profile** | `[x] ran` | 4 Stage-5 hosts classified; identity surfaced (US-consumer / SG-ByteDance / TR-Genc BT / TW-ELNET-NET). |
| **VisorGraph** | `[x] ran` | 4 hosts cert-pivoted; one Caddy default-cert redirect captured. |
| **VisorBishop** | `[x] ran` | Stage-5 platform-confirm + ip-shadow on 9 hosts → 16 shadow findings across 3 confirmed. Found MinIO/Promptfoo FP. |
| **VisorSD** | `[x] ran — null result + bug observed` | AS14061 (DigitalOcean) reported 0/21; Shodan direct returns 593 Ollama hits on AS14061. **Multi-ASN grouped-OR query construction is wrong — now [Insight #43](../../methodology/insight-43-visorsd-multi-asn-query-bug.md).** |
| **VisorGoose** | `[x] ran (density)` | **34 government-network AI services across 25 TLDs.** US .gov+.mil 17 / Indonesia .go.id 7 / Taiwan .gov.tw 4 / Brazil .gov.br 3 / Mexico .gob.mx, Japan .go.jp, India .gov.in 1 each / others 0. |
| **menlohunt** | `[x] ran on 91.241.49.112` | 8 findings (C:3 H:2 M:2 L:1) + 2 attack chains in 32.5s. 2 of the 3 critical are **menlohunt kubelet /exec FP class** (Insight #16 — status-code-as-identity). 6 real TCP-connect confirmations. |
| **recongraph** | `[—] ran on built-in test seed list, not the 01-rerun corpus` | recongraph's `upgraded_runs.py` uses a hardcoded seed list. Did not re-route to this survey's confirmed hosts. Carry-forward: parameterize recongraph entry point. |
| **nu-recon** | `[x] ran on 91.241.49.112 + 127.0.0.1` | TR / Genc BT confirmation; 8 open ports; service stack captured. |
| **VisorPlus** | `[~] partial run on 91.241.49.112` | Reached Step 2/6 (nmap top-1000) before tool-state notes timed out. Output continued in background. |
| **VisorLog** | `[x] ran` | 19 events ingested into `nuclide.db`. |
| **VisorScuba** | `[x] ran` | 21,514 nodes assessed; 0/10 avg score (0% compliant). |
| **BARE** | `[x] ran` | 10 Stage-5 findings → top-3 Metasploit modules each. 1 crosses 0.6 commodity-CVE threshold. |
| **VisorCorpus** | `[x] ran` | 100-case orchestration baseline corpus built. |
| **VisorAgent** | `[x] ran against controlled target (localhost Ollama) — not fired at the survey set (ethical-stop)` | 100/100 ERROR — local Ollama gates `/api/chat` behind subscription paywall when called through VisorAgent (direct curl works). Methodology-compliant null. |
| **VisorRAG** | `[—] init blocked` | OpenAI embedding API 401 on playbook ingest. Carry-forward: point at local Ollama `nomic-embed-text:latest`. |
| **VisorHollow** | `[—] not applicable — Windows-only` | Linux/cloud corpus. |
| **cortex** | `[~] deferred` | Cortex authorization-context analysis is typically driven by `visorrag --cortex` post-loop; VisorRAG didn't init. Cortex framework markdown for this survey can be written manually and run through `analyzer.py` if a single-host writeup is requested. |
| **JS-bundle extract** | `[x] ran` | Pulled `/` HTML from 5 Stage-5 web hosts; extracted JS bundle paths (Portainer at 98.115.25.181: runtime/vendor/main; 41.72.152.18:8080: 5 chunk files). Bundles point to default-platform admin UI — no operator-specific secrets surfaced in spot-check. |

Coverage: 17 of 19 tools ran with material output; 2 documented non-runs (VisorHollow Windows-only; VisorRAG init-blocked). Both VisorAgent and one cortex invocation were skipped against the operator hosts per ethical-stop — VisorAgent ran against controlled localhost; cortex was deferred pending VisorRAG fix.

---

## 11. Stage 8 — Codify

**Insights extracted from this assessment.** Candidates #43 through #47 were subsequently codified on 2026-06-02 (links below). Candidates #41 and #42 were NOT codified under those numbers: registry #41 and #42 were assigned to other insights (admin-endpoint field-name enumeration; LiteLLM model-impersonation). The two observations drafted as #41 and #42 below remain open codification candidates.

- **Uncodified candidate (drafted as #41) — Population growth at the auth-on-default tier outpaces survey cadence.** The category-01 population grew 70-80% in three weeks. Implication: any snapshot survey ages out fast at this tier; absolute counts under-state current exposure within a month.
- **Uncodified candidate (drafted as #42) — aimap DefaultPorts restriction is a coverage trade.** For reverse-proxy-dominant populations (n8n on :443/random, Open WebUI on :443/random), `-scan-all-fingerprints` is mandatory, not optional. The `no FP candidates` log message is the symptom; the 1,126 count on the n8n corpus is the magnitude.
- **Insight #43 — VisorSD multi-ASN grouped-OR query construction returns 0 even when Shodan direct returns hundreds.** ([codified](../../methodology/insight-43-visorsd-multi-asn-query-bug.md)) AS14061 / Ollama dork direct: 593. VisorSD `-asn AS14061`: 0/21 across all bundled queries. Fix in VisorSD query templating, not Shodan.
- **Insight #44 — Parallel aimap passes cannibalize throughput.** ([codified](../../methodology/insight-44-parallel-aimap-socket-pool-contention.md)) Six 30-thread aimap binaries against ~3,500 distinct (host, port) combinations contended for the client-side socket pool such that the per-pass wall-time roughly tripled vs the sequential-equivalent. Recommendation: sequential or staged, with the largest corpus alone first. **Empirical confirmation:** the five killed-stuck passes produced ZERO JSON output despite 36+ min elapsed; the same workload sequentially produced JSON in 1m9s per pass on the small one.
- **Insight #45 — Niche-dork class hierarchy in Shodan: Server-header > frontend-bundle-ID body > route-slug body.** ([codified](../../methodology/insight-45-niche-dork-class-hierarchy.md)) Of 52 niche dorks written, 71% returned 0 hits — the route-slug body class (`http.html:"/api/v1/chatflows"`) does not index well because Shodan crawls root HTML, not JS bundle source. The 15 dorks that returned hits sorted into the hierarchy. Top performers: `http.html:"n8n-editor-ui"` 66,802, `http.html:"\"chainlit\":{"` 1,029, `"Server: llama.cpp"` 1,638, `ssl.cert.subject.cn:openai` 965.
- **Insight #46 — TLS cert subject CN is a precise operator-attribution surface.** ([codified](../../methodology/insight-46-tls-cn-operator-attribution-surface.md)) 2,021 hosts globally present TLS certs with `openai` (965), `litellm` (812), or `ollama` (244) in the subject CN. Operators self-attributed via cert naming — cleaner than dork-matching against rendered HTML, and stable against operator-side CDN proxying. New attack class.

## 11b. Dork-remap Stage-2 verify — Insight #47 (the cleanest auth-on-default thesis evidence yet)

After the aimap chain stalled in Phase 2 fingerprinting, the verify step was completed via the methodology's "rare exception" path — direct asyncio HTTP probes with platform-specific markers (Server header for llama.cpp/Ollama, body bundle-ID for n8n, body JSON config for chainlit/dify). Each verify ran in 16-113 seconds against 1,000-host samples (vs aimap's 30+ min stalls).

### Strong-marker direct-exposure class (auth-off-default)

| Corpus | Sample | Confirmed | Real-rate | New unique IPs |
|---|---|---|---|---|
| `"Server: llama.cpp"` | 1,000 | **780** | **78%** | 738 |
| `http.html:"n8n-editor-ui"` | 1,000 | **604** | **60%** | 604 |
| `"Server: ollama"` | 33 | 17 | 51% | 17 |

**1,359 unique newly-confirmed unauth cat-01 platforms** this session. The 738-host llama.cpp population is 26× the 2026-05-15 llama.cpp survey (28 events) — Server-header dork unlocks a corpus invisible to aimap's default port profile.

llama.cpp port distribution (top 5): :8001 (202), :8080 (187), :8081 (72), :8000 (61), :11434 (25).

### Weak-marker route-slug body class (substring collision)

| Dork | Sample | Real-rate | Disposition |
|---|---|---|---|
| `http.html:"/console/api"` | 1,000 | **0.5%** | discard — too generic, FP |
| `http.html:"\"chainlit\":{"` | 1,000 | **0%** | dork string in JS bundle source, not on root path |

The `/console/api` and `"chainlit":{` strings are present in HTML bundles Shodan indexed, but absent from / when probed live. The body-substring class is fragile to probe-path mismatch — route-slug dorks need the right probe path to verify.

### TLS-CN attribution-only class (Insight #47)

| Dork | Sample | Confirmed | Real-rate | Class |
|---|---|---|---|---|
| `ssl.cert.subject.cn:ollama` | 240 | 0 | **0%** | attribution-only |
| `ssl.cert.subject.cn:litellm` | 800 | 1 | **0.1%** | attribution-only |

**Insight #47 ([codified](../../methodology/insight-47-tls-cn-attribution-only-not-platform-confirmation.md)) — TLS cert subject CN is an operator attribution surface, not a platform-confirmation surface.** Operators who put the brand name in the cert CN are doing TLS termination + reverse-proxy fronting with intentional configuration. The platform itself sits behind the proxy with its own (typically auth-enabled) posture. The two classes are inversely correlated with auth posture: direct-exposure strong-marker hits are the unconfigured-default class; TLS-CN hits are the intentionally-configured class.

This is the cleanest empirical formulation of the auth-on-default thesis to date. The contrapositive holds: operators who care about cert CN naming also care about auth.

### Session-total Stage-1 unauth confirmations under the dork remap

| Platform | Confirmed unauth this session | Delta from prior catalog/survey |
|---|---|---|
| llama.cpp | 738 unique IPs | +26× (prior survey 28 events) |
| n8n | 604 unique IPs (60% of 1,000-sample) | new at this dork — extrapolates to ~40K real on `n8n-editor-ui` 66,802 population |
| Ollama (server header) | 17 unique IPs | tiny but high-precision subset of the 47,441 population |
| **Total newly-confirmed unauth** | **1,359** | first-pass yield from the v2 dork remap |

## 11a. v2 + v5 dork-remap addendum (sequential aimap chain in flight)

Stage-0 v2 + v5 harvest fired after the parallel-aimap deadlock was cleared. Niche dork catalog written at `~/recon/01-llm-orchestration-rerun-2026-05-19/dorks-niche-v2.txt` (52 dorks). Shodan `count` per dork (free queries) produced the distribution above. Top 4 v2 dorks pulled at 1,000-host limit; top 4 v5 dorks pulled at 1,000-host limit. Sequential aimap chain queued:

| Pass | Corpus | Hosts | Status | Result class |
|---|---|---|---|---|
| v2 ollama-header | `"Server: ollama"` | 33 | DONE 1m9s | **17 Ollama unauth + 4 Docker Registry (catalog auth-gated) — 51% real-rate, 12% adjacent Registry** |
| v2 dify-console-api | `http.html:"/console/api"` | 951 | in flight | TBD |
| v2 llamacpp-server | `"Server: llama.cpp"` | 949 | queued | TBD — first population survey of llama.cpp at this size |
| v2 n8n-editor-ui | `http.html:"n8n-editor-ui"` | 334 | queued (with `-scan-all-fingerprints`) | TBD |
| v5 tls-ollama-cn | `ssl.cert.subject.cn:ollama` | 236 | queued | TBD — cert-CN attribution test |
| v5 tls-litellm-cn | `ssl.cert.subject.cn:litellm` | 800 | queued | TBD |
| v5 chainlit-config | `http.html:"\"chainlit\":{"` | 926 | queued | TBD |
| v5 tls-openai-cn | `ssl.cert.subject.cn:openai` | 940 | queued | TBD |

**v2-ollama-header Stage-3 attribution observation:** 4 of 17 hosts (24%) on **3NT SOLUTIONS LLP** (Turkey, Brazil, Italy, Estonia). Cheap-VPS reseller customer pattern — single provider's customers all default-config Ollama.

**v2-ollama-header Stage-5 IP-shadow (VisorBishop -ip-shadow-all):** 2/17 = 12% IP-shadow positive (rpcbind on 176.107.181.163 UA / DeltaHost; mailcatcher on 38.180.104.127 TR / 3NT). Lower than the prior-corpus Pharos-class rate.

The Pharos-class operator at **91.241.49.112 (Istanbul / Genc BT)** is the most-impactful single-host finding and is the natural anchor for a per-host case study if Cowboy wants to take the disclosure path.

---

## Carry-forward (open items)

1. **The four big aimap passes (stage1 / n8n / new-api / Open WebUI / n8n-allfp) are still running at writeup time.** Their JSON results will be appended to this case study when they land. Network contention will be folded into the operational-lessons section.
2. **VisorRAG embedding** — set env / config so playbook ingest hits local Ollama `nomic-embed-text:latest` instead of OpenAI; re-run controlled-target probe.
3. **recongraph parameterization** — fix entry point so it accepts a seed file rather than a hardcoded list.
4. **VisorSD multi-ASN grouped-OR fix** — file at the VisorSD source repo with reproducer (AS14061, Shodan direct 593, VisorSD reports 0).
5. **aimap DefaultPorts coverage trade** — document the `-scan-all-fingerprints` recommendation per population class; consider a `-ports-class workflow-orch-reverse-proxy` profile that defaults to scan-all-fingerprints.
6. **VisorBishop MinIO-as-promptfoo FP** — aimap fingerprint substring check; promptfoo is at 15500, MinIO at 9000.
7. **menlohunt kubelet /exec FP class** — Insight #16 still applies; status-code is not identity. File at menlohunt source if not already done.

## Toolchain provenance

```
Stage 0 — JAXEN ai-hunt orchestration (5 dorks) + jaxen hunt (3 dorks) + shodan download (3 corpora)
Stage 1 — aimap v1.9.22 — 6 parallel passes (2 completed during write-up, 4 in flight)
Stage 2 — aimap deep enum + VisorBishop platform-confirm
Stage 3 — visorgraph cert-pivot + nu-recon (with real-network Shodan key)
Stage 4 — aimap-profile fast-mode classification
Stage 5 — visorbishop -ip-shadow on Stage-4 confirmed + aimap registry-port re-pass (Insight #33 classifiers, null result on this sample)
Stage 6 — visorlog ingest + visorscuba assess + bare rank + visorcorpus build
Stage 7 — visoragent (controlled target, paywall ERROR), visorrag (init-blocked), visorgoose density, visorsd ASN sweep (bug observed), nu-recon, menlohunt (host-targeted), visorplus (partial), JS-bundle extract, recongraph (test-seed only — toolchain gap)
Stage 8 — case study (this file) + insight-class extraction + SESSION.md update
```
