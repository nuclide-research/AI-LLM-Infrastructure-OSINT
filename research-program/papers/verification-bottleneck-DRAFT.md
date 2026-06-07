---
title: "The Verification Bottleneck: Why Scanning Is Easy And Method Lives In The Last Stage"
author: NuClide Research
date: 2026-06-07
status: DRAFT (Phase 4 of 9-item plan, 2026-06-07)
---

# The Verification Bottleneck

_Working draft. Section completion status at end of file._

## 1. The premise

The AI infrastructure surface grew from a few thousand exposed inference endpoints in 2024 to a population that spans every Western and Asian cloud, every commodity GPU host, every AI-first SaaS, and a long tail of self-hosted operators in 2026. A weekend's worth of Shodan and Censys queries surfaces tens of thousands of candidate hosts running LLM gateways, vector databases, agent frameworks, MLOps consoles, and the model-serving inference layer underneath all of them. The candidates pour in. The question is what to do with them.

Most published security research on this surface treats the scan as the load-bearing artifact. A research note will lead with a Shodan dork, report a count, and report a finding rate. The implicit method is: dork yields candidates; candidates equal findings; finding rate is the headline number. That method is wrong at population scale.

NuClide Research has spent the last year running this kind of survey on category after category of AI infrastructure: model-serving, vector databases, LLM orchestration, agent platforms, MCP servers, AI-email-guardrails, and more. The aggregate output is a corpus of about 250 case studies and 79 numbered methodology insights. We coded each insight by the stage in the pipeline where the methodology breaks: scanning, verification, or codification. The result is the headline of this paper.

Of 79 codified insights, 49% are verification-stage decisions, 28% are codification-stage decisions, and only 23% are scanning-stage decisions. Verification is the largest single bucket and roughly twice the size of the scanning bucket. The macro claim is small and load-bearing: at population scale, the verify step is where method correctness lives. The scan only produces candidates. If you skip the verify step, you produce a confident, reproducible, and wrong number.

The rest of the paper is the evidence. Section 2 defines the pipeline. Section 3 walks through the 79-insight bucketing. Section 4 is the canonical worked example: a model-serving survey where 39 CRITICAL/HIGH candidates produced 6 verified findings and one refuted candidate-insight. Section 5 overlays the DoD Cyber Workforce Framework KSAT vocabulary, which honestly surfaces where the program is strong (97% coverage on K7003 AI security risks) and where it has gaps (0% on K7020 DoD AI Ethical Principles by name). Section 6 walks through two methodology byproducts from the same week: a DMARC-as-funding-stage-proxy primitive and a partial test of dork-population substitution on Argo Workflows. Section 7 spells out the implications for defenders, vendors, and the field. Sections 8 and 9 are the honest caveats and the closing.

## 2. The discipline

The pipeline that produces NuClide findings has eight named stages: Discover, Fingerprint, **Verify**, Attribute, Classify, Ledger, Score, Codify.

```
Discover → Fingerprint → VERIFY → Attribute → Classify → Ledger → Score → Codify
                            │
                            └── 200-with-data is the gate
```

- **Discover**: Shodan, Censys, certificate-transparency logs, OSINT platoons. Produces an IP-port list.
- **Fingerprint**: aimap, a Go-language declarative fingerprinter, classifies each host:port against a registry of ~220 AI-infrastructure platform definitions. Produces a candidate set with claimed severities (CRITICAL / HIGH / MEDIUM / LOW / INFO).
- **VERIFY**: the load-bearing stage. For every CRITICAL and HIGH candidate, re-probe with a marker request, read the response, and decide whether the claim survives contact with the host. The gate is "200-with-data": a finding requires reading something. A non-error status code is not a finding. A response body that confirms the platform but does not confirm the auth claim is a surface-open, not a finding.
- **Attribute**: WHOIS, RDAP, certificate Subject CN, operator profile via aimap-profile. Produces operator identity for the verified finding.
- **Classify**: assign a category (HIPAA/clinical, personal, commercial, research, honeypot, government). Drives the disclosure-routing decision.
- **Ledger**: VisorLog ingests verified findings into nuclide.db. Survey-scoped, not ledger-wide, so a verified finding belongs to exactly one survey and cross-survey aggregation is auditable.
- **Score**: VisorScuba compliance scoring against AI-relevant control frameworks (DoD Responsible AI, GDPR data-subject access, healthcare PHI rules) given the survey-scoped subset.
- **Codify**: every survey closes with a numbered Insight in `methodology/insight-NN-*.md`. The data layer produces findings; the codification layer produces methodology.

Two principles run through every stage.

**Principle one: 200-with-data is the verification gate.** A status code is not a finding. An open port is not a finding. A platform-specific response body that confirms unauthenticated reach is a finding. The data layer trumps the framing layer. The marker probe trumps the dork. If the data does not survive a marker probe, the candidate is rejected; if the data confirms a richer claim than the marker, the candidate is upgraded. Insight #16 (`status-code-is-identity-not-auth-state`), Insight #52 (`an-http-200-at-an-api-path-is-not-that-api`), and Insight #68 (`verification-rungs-claim-ladder`) are the canonical statements of this principle. There are more.

**Principle two: names ARE the finding. Do not exfiltrate.** Verification requires reading enough to confirm reach. It does not require reading more than that. Enumerate the names of vector-database collections to confirm the collection exists; do not read the records. Enumerate the model list on an unauth inference server to confirm the host serves Llama-3; do not invoke inference. Read the schema, never the rows. This is the restraint ethic. It makes NuClide findings safe to disclose without exposing the operator's customers to further harm via the report itself.

The discipline is the methodology. Most of what follows in Section 3 is a per-insight examination of the verify-step decisions that this discipline forces.

## 3. The evidence: 79 insights bucketed

The codification layer of the NuClide pipeline produces a numbered methodology insight at the close of every survey. The full file set lives in `methodology/insight-NN-*.md`. As of 2026-06-07 the corpus is 79 numbered insights (#48 reserved, never assigned). We coded each one against the pipeline-stage rubric in Section 2 and counted the buckets.

| Bucket | Count | Share of corpus |
|---|---|---|
| Verification | 39 | 49% |
| Codification | 22 | 28% |
| Scanning | 18 | 23% |
| **Total** | **79** | (full bucketing artifact: `research-program/insight-bucketing-2026-06-07.md`) |

Verification is the largest single bucket and roughly twice the size of the scanning bucket. The methodology lesson NuClide takes home from a survey is more often a lesson about how to know whether a candidate is real than it is a lesson about how to find candidates in the first place. Five worked examples drive that home.

**Insight #40: Auth-on-default thesis shifts rightward in successor OSS generations.** The macro thesis of the NuClide program is auth-on-default: the modal OSS LLM-infrastructure project ships with authentication ON by default, and the population of exposed unauthenticated hosts is a population of operator misconfigurations, not project misdesigns. Insight #40 is a refinement: the thesis strengthens across successor generations of the same project family. When a disclosure lands against OSS project X, the next-generation release or sibling fork hardens the specific surface that drove the disclosure. The lesson is verification-stage because it is about what counts as evidence for or against the thesis. The thesis is falsifiable at the verify step, not the scan step.

**Insight #68: The verification-rung grid.** Every claim NuClide makes carries a verification status expressed as a *pair*: depth (code reading vs live confirmation) and breadth (single host vs population). The pair is orthogonal. A claim that is depth-deep but breadth-narrow (one verified host, no population sweep) is different from a claim that is depth-shallow but breadth-wide (a hundred hosts that all returned 200 but nobody read the body). Claim language is bound to the rung; "critical class-level default credential" requires both depth (read the credential's effect) and breadth (population sample, not n=1). Insight #68 is the canonical verify-step rubric; the rest of the codified verification insights are special cases of it.

**Insight #73: Header-versioned APIs are invisible to header-less fingerprinters.** Computer Vision Annotation Tool (CVAT) uses Django REST Framework's `AcceptHeaderVersioning`. Its identity endpoint returns the platform-confirming JSON *only* when the request carries the vendor media type `Accept: application/vnd.cvat+json`. With a generic `Accept`, content negotiation returns 404 or 406. The aimap fingerprinter sent generic Accept and missed the entire CVAT population. The verification probe pass missed it too. A re-probe with the right header confirmed all 30 candidates. The lesson is verification-stage in spirit: the fingerprinter zero is a tool artifact, not a population fact, and only a verify-step re-probe with corrected parameters distinguishes the two.

**Insight #77: Passive Shodan is an MCP crypto-sieve; the lifecycle handshake is the depth-gate.** The Model Context Protocol is Shodan-dark on passive banners because the protocol's identifying content appears only in the response to a POSTed `initialize` request. The one dork that has real recall, the generic JSON-RPC error banner, returns a crypto-mining-dominated false-positive set (Bitcoin, Ethereum, IPFS, stratum pools all emit the same error shape). Discovery alone produces a noisy candidate set. Verification depth then has to go through the full MCP lifecycle handshake to confirm both *identity* (you reached an MCP server) and *capability* (what tools it exposes). The pre-filter is at the data layer, not the dork layer. Three-quarters of the methodology lives in the verify step.

**Insight #80: DMARC enforcement rate is a funding-stage proxy in AI-security vendors.** Codified the day this paper was drafted. A 410-vendor `dig _dmarc` sweep produced a clean monotonic relationship between policy strictness and funding stage in AI-security vendors: 0% enforcement at YC/pre-seed, 100% at Series C and later, with the mid-bands trending upward. The pattern is a verification-step byproduct because it only pays dividends once you re-probe at scale, and because its side finding (53.4% of broader AI-infra domains have no DMARC at all, vs ~13% in the AI-security subcategory) is itself a verification-step claim about what the population actually looks like.

Across these five and the 34 other verification-stage insights, one observation recurs: the codified lesson is almost never "we found a new dork" or "we built a new fingerprint." It is "we learned what a 200 actually means here," or "we learned how to refute a one-host extrapolation," or "we learned what shape of evidence the framing actually demands." The methodology is overwhelmingly a methodology of the verify step.

Three further insights form the canonical statement of the verify gate and deserve a tight grouping. Insight #51 (`port-number-names-a-candidate-not-a-finding`) says that a TCP-open is not a service. Insight #16 (`status-code-is-identity-not-auth-state`) says that an HTTP 200 from a platform endpoint confirms identity, the platform is alive at the URL and chose to answer, but does not confirm auth state. Insight #52 (`an-http-200-at-an-api-path-is-not-that-api`) extends the same lesson one layer up: a web server answers 200 for paths it does not implement, and a scanner that confirms an API by accepting the 200 produces confident, reproducible, wrong CRITICALs. Insight #52 was sourced to a 147-finding cohort where every single body was an HTML document, not GCP metadata. The scanner had named candidates as findings without checking what was in the body. Reading the body would have stripped 147 false-CRITICALs in one pass. The triplet runs port to status to body. Each rung answers "what does this evidence actually say" and gives the verify-step language its precision.

Insight #78 (`shared-deployment-kit-operator-class-exposure`) sits at the verify step from a different angle. Three independent operators in xTom Japan ran LiteLLM Enterprise v1.82.6 with the same favicon hash and the same auth-off configuration. The fingerprint of the kit, not the operator, was the load-bearing classifier. Verifying one instance immediately classified the others. Finding one host generalized to a population without re-probing each member. A scan would have produced three independent CRITICALs and a verify-step would have collapsed them to one kit-level exposure with a known population. The lesson is verification-stage and structural: when a fingerprint travels in a deployment kit, the verify step's output is a population call, not a per-host call.



## 4. The case: Cat-03 Model Serving, 39 candidates to 6 verified

The cleanest worked example of the verify step's load is the Cat-03 Model Serving survey, run 2026-06-05.

The category covers consumer-grade OpenAI-compatible inference servers: llama.cpp, vLLM, KoboldCpp, Ollama, SillyTavern, faster-whisper, One API, New API, Open WebUI, SGLang, GPT4All, HuggingFace TGI, and several adjacent platforms. The shared property is that they all serve LLM inference over an HTTP API on a small set of well-known ports.

The survey ran the full eight-stage pipeline. Discovery produced 5,018 unique IPs across 17 Shodan and 9 Censys queries. The scanner stage (active TCP-TLS banner-grab on the Cat-03 port set) collapsed that to 158 live hosts. The fingerprint stage (aimap) classified 72 of those 158 into 19 platform classes and flagged 20 CRITICAL plus 19 HIGH candidates: 39 in total.

Then the verify step ran. The result of the verify step is the headline of this section.

Of 39 candidates, **6 verified as genuinely unauthenticated** with a 200-with-data read. Twenty-one were refuted as false positives. Twelve were surface-open: the platform was present and reachable but no proof of unauth was exercised, so they are not findings. The candidate-to-finding ratio is 6.5x. The pre-verification framing was wrong on most of the candidate set.

The instructive part is what specifically broke.

A pre-verification candidate insight, marked #78 in the live numbering scheme, claimed that One API and its fork New API ship with a `root/123456` default credential that holds at population scale. The basis was a single live host (`121.28.161.118`) where the credential worked and returned `data.role: 100` (root admin). Generalizing from n=1 to "class-level default" is the verify-step error that this candidate insight encoded. The 9-host population sweep run during verification returned 0/9 acceptance. The candidate insight was **refuted**. One API ships first-run password setup; the single host was a lazy-operator outlier. The auth-on-default thesis was confirmed, not bucked, by this survey. If we had reported the pre-verification framing, we would have published a confident, reproducible, and wrong claim that an entire vendor class ships with default credentials.

A second pre-verification candidate, #79, claimed that an unauthenticated Ollama instance on `121.153.39.157:11434` was proxying a paid Ollama Connect cloud subscription. The verify step confirmed this with hard proof: `/api/tags` returned 40 models including `deepseek-v4-pro:cloud` with `remote_host: ollama.com`. Any internet host could invoke the paid model through the open Ollama. This is a real finding. The verify step kept this one and killed the other.

A third candidate, #80 in the pre-verification scheme (later retracted; the live #80 is the DMARC funding-stage proxy), claimed that the survey had surfaced provincial Indonesian government AI hosts: `jatengprov.go.id` and `kaltaraprov.go.id`. The verify step traced the claim back to VisorScuba, the compliance-scoring tool, and found that those hosts were prior-survey carryover in the ledger-wide assessment, not Cat-03 hits. The candidate was **retracted**, and a process insight was added: filter VisorScuba output to the survey's own ingested events before attribution. Without the verify step's cross-check, NuClide would have published a survey claim that included two hosts that were never actually in the Cat-03 corpus.

The most material finding of the survey was a single AT&T residential host, `108.210.175.159`, running an enthusiast local-LLM stack on home broadband. Shodan saw three of the four exposed services on this host. The fourth, Ollama on :11434, was Shodan-dark and surfaced only on the active scanner pass. The composite story: the operator put basic auth on the front-end (SillyTavern), then left the inference backends the front-end depends on (KoboldCpp on :5001 and Ollama on :11434) wide open. Front door locked, backend exposed. This pattern was codified as candidate insight #82, the front-end-secured / backend-exposed asymmetry in enthusiast local-LLM stacks. The attack surface is the dependency graph, not the front door.

In addition, the verify step produced a nine-class false-positive catalog. Four "GPT Researcher" candidates were Gradio Whisper Playgrounds catching the marker probe on a generic `/api/report 405` catch-all. One "Lunary" was actually CheckRef behind a generic `/api/v1/health` endpoint. One "h2oGPT" was actually KoboldCpp; both serve `/openai_api/v1/models` and the disambiguator (Server header) was not anchored in the fingerprint. Two TTS candidates (Coqui, Chatterbox) collided with ZenTao on :8000. Each FP was traced back to a specific aimap fingerprint that lacked a positive body marker or a framework negative-match. Each FP became a v-bump aimap fingerprint fix queued as root-cause work, not catalog cruft. The verify step generated four new bugs against the fingerprinter and the data needed to fix them.

The 39-to-6 number is the headline. The five candidate-insight outcomes (one refuted, one confirmed, one retracted, two proposed) are the texture. The nine-class FP catalog is the byproduct. None of this is visible at the scan or fingerprint stages. All of it lives in the verify step.

The retracted candidate deserves a deeper walkthrough because it shows how the verify step catches errors the discipline introduces in itself, not just errors in the framing. The original pre-verification candidate insight, drafted before the verify pass closed, asserted that the survey had surfaced provincial Indonesian government AI infrastructure as a category-first hit. The named hosts were `jatengprov.go.id` (Central Java) and `kaltaraprov.go.id` (North Kalimantan). The framing was clean: Cat-03 had reached its first government category, and the surfaced surface was provincial DINAS KOMINFO infrastructure. A claim worth disclosing under the responsible AI engagement model. The verify step traced the assertion back to VisorScuba, the compliance-scoring stage that takes a survey's verified findings and overlays AI control frameworks (DoD Responsible AI, GDPR, healthcare PHI rules). VisorScuba reported the two `*.go.id` hosts as in-scope. VisorScuba was wrong, not maliciously but procedurally: the tool runs over the nuclide.db ledger ledger-wide by default, and the ledger holds ~25,000 events from every prior survey. The two government hosts were prior-Ollama-survey carryover from a 2026-05-15 walk. They were never in the Cat-03 corpus. The candidate was retracted. A process insight was added: filter VisorScuba output to the survey's own ingested events before attribution. This catch is structural: the verify step caught the program from publishing its own ledger noise as a fresh finding. The methodology lesson is that even the discipline's own tooling needs verification against the survey it claims to score. Without the verify step's cross-check on the ledger boundary, NuClide would have published two hosts that did not belong to the survey at all, and the program's credibility would have absorbed the cost.



## 5. The vocabulary: DCWF KSAT coverage matrix

A DoD-adjacent reader looking at NuClide research output will recognize the activity but may not recognize the vocabulary. The DoD Cyber Workforce Framework (DCWF) defines five AI work-roles and a per-role catalog of Knowledge, Skills, Abilities, and Tasks (KSATs). Roles 672 (AI Test & Evaluation Specialist) and 733 (AI Risk & Ethics Specialist) are the cleanest fits for NuClide's work; the other three (623 AI/ML Specialist, 753 AI Adoption Specialist, 902 AI Innovation Leader) cover the implementation, adoption, and leadership sides that NuClide does not operate in.

To make NuClide work legible in DoD vocabulary, we built a small Go tool (`ksat-tag`) that parses a case-study Markdown file, applies keyword and pattern rules drawn from each role's KSAT catalog, and inserts an auto-generated tag block into the file. Idempotent. One commit covered all 240 case studies. The companion matrix (`data/dcwf-ksat-coverage-matrix-2026-06-07.csv`) records which KSAT IDs each case study touched.

The coverage profile is informative.

Four KSATs hit at least 90% of case studies. K1158 (cybersecurity principles) at 100%. K22 (network and security methodologies) at 98%. K7003 (AI security risks, threats, vulnerabilities, and mitigations) at 97%. S7068 (skill in identifying organizational and project-level AI risks, including AI security risks) at 96%. This is the program's spine: every survey is, at the floor, a network-level AI-risk story.

Four KSATs hit below 10% of case studies. K7045 (knowledge of the AI lifecycle) at 3%. S7076 (skill in testing for bias in datasets and AI system outputs) at 5%. K7052 (knowledge of principles, methods, and tools for risk and bias assessment, including assessment of failures) at 6%. S7069 (skill in identifying risk over the lifespan of an AI solution) at 6%. And one KSAT at exactly 0%: K7020 (knowledge of DoD AI Ethical Principles).

The 0% on K7020 across 240 case studies is itself a finding. NuClide produces evidence relevant to DoD AI Ethical Principles in nearly every survey: PHI exposure on healthcare-adjacent unauth inference servers, attribution gaps, model-impersonation fraud, blind spots that map directly onto the responsible / equitable / traceable / reliable / governable framework. The program just does not use the vocabulary. The retro-tagger fixes the vocabulary gap. It does not fix the coverage gaps.

The coverage gaps are real. Bias testing in datasets and AI system outputs (S7076) at 5% is honest: infrastructure surveys do not exercise model outputs, so bias assessment is out of scope by methodology. AI lifecycle (K7045) at 3% is honest: NuClide takes snapshots of a population at a moment in time and does not track operators across deploy-update-retire cycles. Lifecycle risk (S7069) at 6% is honest for the same reason.

The point of including this overlay in this paper is not to claim DCWF-compliance. It is to make the verification thesis legible inside DoD vocabulary. The verify step in NuClide language is `T5919 Test AI tools against adversarial attacks in operationally realistic environments` plus `T5904 Perform risk assessment on AI applications` in DCWF language. The auth-on-default thesis is `K7003 Knowledge of AI security risks, threats, vulnerabilities, and potential risk mitigation solutions` in DCWF language. The shared vocabulary lets a DoD reader pick up the rest of the paper without translating every term.

## 6. The byproducts

Two byproducts from the same working week as this paper illustrate the verify-at-scale principle from different angles.

**DMARC enforcement rate as a funding-stage proxy.** A 410-vendor `dig _dmarc` sweep across the AI-infrastructure registry produced two findings worth reporting separately. First, in the AI-security subsample where we had funding-stage data (n=31), DMARC strictness scales monotonically with stage: zero percent enforcement at YC/pre-seed, 100% at Series C and later, mid-bands trending upward. A single 50-millisecond passive DNS query lets a researcher infer approximate funding stage, SOC2 audit pressure, and engineering maturity without scraping LinkedIn or Crunchbase. The signal is robust at the extremes; it is noisier in the mid-bands but trends in the predicted direction. The methodology is publishable as a cheap pre-engagement primitive (`methodology/insight-80-dmarc-funding-stage-proxy.md`).

Second, the side finding. Across the broader AI-infrastructure registry (n=410, no stage filter), 53.4% of resolvable vendor domains publish no DMARC record at all. Compare to the AI-security subcategory, where roughly 13% of vendors lack DMARC entirely. AI-security vendors trail enterprise SaaS broadly, but they are roughly four times ahead of the broader AI-infrastructure ecosystem on basic email hygiene. Hypothesis: SOC2 pressure scales with enterprise-sales motion, not with funding stage per se. The byproduct is a verification-step output because it only pays dividends once you re-probe at scale, and the side finding only emerges when the verify step covers the full population.

**Argo Workflows on port 2746, partial refutation.** A separate candidate insight, `reference-dork-population-substitution`, proposed that `ssl:`-style Shodan dorks select for operators who are DNS-configured and security-conscious, blinding the researcher to a Shodan-dark tier of operators who expose only `:2746` (the Argo Server gRPC/HTTP port) and not `:443`. The Cat-29 survey from 2026-05-31 found 0 unauth out of 33 probed via the `ssl:"Argo Workflows"` dork, all gated by IAP or AzureAD. The question: is the unauth tier hiding on `:2746`?

The Lane 1A probe of this paper's plan tested one variant of the hypothesis: among the 156 hosts already surfaced by the `ssl:` dork, do any expose `:2746` publicly? Answer: no. 156 out of 156 connections timed out at 5 seconds. The variant "operators who expose `:443` with Argo certs also expose `:2746`" is refuted. The broader hypothesis (cert-invisible Argo operators on `:2746`) is still untested; that requires a `port:2746` discovery on a different dork population, queued for 2026-06-08 when credit budgets reset. The partial-refutation closure is itself a verification-step output: we learned what the data could and could not say about the hypothesis, which is more useful than guessing.

## 7. The implications

So what.

**For defenders.** A scanner report at population scale is a candidate set, not a finding set. The 6.5x correction in the Cat-03 worked example is not unusual; if anything it is on the lower end of corrections we see in surveys where the fingerprint claims are bolder than the data supports. If the security operations workflow consumes scanner output as finding output, the headline number lies, the alert backlog stays full of false positives, and the team's calibration drifts in the wrong direction. Bake verification into the workflow. The verification gate (200-with-data, marker probe, population check) is the cheapest place in the pipeline to add discipline.

**For vendors.** When a NuClide disclosure arrives, the framing has already been re-probed. The candidate-to-finding ratio is small by design. This is not a bug-bounty firehose; the curated set is the deliverable. Vendors should expect the report to name the specific data that was read, the specific endpoint that was queried, and the specific operator host that was confirmed. Vendors should also expect that the report will not have read the customer's data; the restraint ethic is load-bearing for the disclosure flow.

**For the field.** A 49% verification-stage rate in the codified lessons of a yearlong AI-infra research program is the methodology meta-finding. The interesting research lives at the verify step, not the scan step. Publishing scanners is easy; publishing verification rubrics is rare. The community would benefit from more papers on what counts as proof at population scale, fewer papers on what to ask Shodan.

## 8. Limits and caveats

The 79-insight denominator is small. The 49% verification rate will move with more data, in either direction. We expect the ratio to drift slowly because verification-stage decisions compound (every new survey's verification rubric is informed by prior verification-stage insights), but a year from now the share could be 45% or 55%.

The bucketing rubric is a judgment call at the boundaries. Three of the 79 codings are flagged as disputed in the bucketing artifact: a second coder might move them across the boundary. The shape of the distribution does not change if all three flip; the precise share by half a percentage point does.

The DCWF overlay is post-hoc. The NuClide program was not designed against the framework, so the overlay is necessarily a translation, not a native fit. A program designed against DCWF from the start would surface different gaps and different strengths. The K7020 0% reading should be read as a vocabulary observation, not a critique.

The Cat-03 worked example is one survey out of dozens. The 6.5x candidate-to-finding correction is real but is not the modal correction; some surveys have 1.5x corrections, some have 12x. The methodology is the same shape across all of them. The number is illustrative, not normative.

The Cat-29 :2746 partial refutation is partial. The full hypothesis is still open. We disclose this honestly in Section 6 because the temptation to round up a partial result into a complete result is exactly the kind of verification-stage error this paper is about.

## 9. Conclusion

Verification is the load-bearing stage. The scan is the easy part. If you only invest in scanning, your population-scale finding rate is confident, reproducible, and wrong. NuClide invests in verification; that is why the candidate-to-finding ratio looks the way it does; that is why the codified insights bucket the way they do; that is the program. The next yearlong project of this kind should design the discipline before the dork.


---

## Section completion status (v2)

| Section | Words target | Status |
|---|---|---|
| 1. Premise | ~400 | ✓ v1 first draft |
| 2. Discipline | ~600 | ✓ v1 first draft |
| 3. Evidence bucketing | ~1,200 | ✓ v2 expanded (added canonical triplet #16/#51/#52 + Insight #78 kit-level case) |
| 4. Cat-03 case | ~1,500 | ✓ v2 expanded (added retracted-candidate walkthrough on VisorScuba ledger-boundary catch) |
| 5. DCWF | ~800 | ✓ v1 first draft |
| 6. Byproducts | ~600 | ✓ v1 first draft |
| 7. Implications | ~600 | ✓ v1 first draft |
| 8. Caveats | ~400 | ✓ v1 first draft |
| 9. Conclusion | ~200 | ✓ v1 first draft |

Current word count: ~4,800 (v2 with two expansion blocks added). Target total: 6,000-8,000.

## v2 completion notes

- Section 3 added: the canonical verify-gate triplet (Insight #51 port-to-service, #16 status-to-auth, #52 status-to-API) as a tight cluster, plus Insight #78 (kit-level fingerprint generalization) as the population-call case.
- Section 4 added: the Cand #80 retraction walkthrough showing that the verify step catches errors the discipline introduces in itself, not just framing errors. VisorScuba ledger-boundary cross-check is the named lesson.
- Em-dash re-pass: clean (post-v2 verification).

## Remaining pre-publication work

- Hemingway editorial pass per the `hemingway` skill, on the whole document.
- Operator-anonymized quotes from Sluice and (once disclosed) Capitol.ai.
- Title vote: candidate alternatives are still in the paper-outline file.
- Citation links: verify every `methodology/insight-NN-*.md` link is valid.
