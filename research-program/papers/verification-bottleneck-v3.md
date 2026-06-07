---
title: "The Verification Bottleneck"
author: NuClide Research
date: 2026-06-07
status: v3 (Hemingway pass)
---

# The Verification Bottleneck

## 1. The thesis

Verification is the load-bearing stage. The scan is the easy part.

Of 79 codified methodology insights from a yearlong AI-infrastructure research program, 39 are verification-stage decisions, 22 are codification, and 18 are scanning. The verify step is half the methodology and twice the scanning bucket.

NuClide Research ran population-scale surveys on category after category of AI infrastructure: model-serving, vector databases, LLM orchestration, agent platforms, MCP servers, AI-email-guardrails. About 240 case studies and 79 numbered insights came out. We coded each insight by the stage in the pipeline where it broke.

The thesis is small and load-bearing: at population scale, the verify step is where method correctness lives. The scan produces candidates. Skip verification and you publish confident, reproducible, wrong numbers.

## 2. The discipline

The NuClide pipeline has eight stages: Discover, Fingerprint, **Verify**, Attribute, Classify, Ledger, Score, Codify.

```
Discover → Fingerprint → VERIFY → Attribute → Classify → Ledger → Score → Codify
                            │
                            └── 200-with-data is the gate
```

- **Discover**: Shodan, Censys, certificate transparency, OSINT platoons. Output: an IP-port list.
- **Fingerprint**: aimap classifies each host against a registry of ~220 AI-infrastructure platform definitions. Output: a candidate set with claimed severities (CRITICAL / HIGH / MEDIUM / LOW / INFO).
- **VERIFY**: re-probe with a marker request. Read the response. Decide whether the claim survives contact. The gate is 200-with-data. A status code is not a finding. A body that confirms the platform without confirming auth is surface-open, not a finding.
- **Attribute**: WHOIS, RDAP, cert Subject CN, operator profile.
- **Classify**: HIPAA/clinical, personal, commercial, research, honeypot, government. Drives disclosure routing.
- **Ledger**: VisorLog ingests verified findings into nuclide.db, survey-scoped.
- **Score**: VisorScuba overlays AI control frameworks (DoD Responsible AI, GDPR, healthcare PHI) on the survey-scoped subset.
- **Codify**: every survey closes with a numbered insight.

Two principles run through every stage.

**Principle one: 200-with-data is the gate.** A status code is identity, not auth state. A body that confirms the platform but not the auth claim is surface-open. The data layer beats the framing layer. The marker probe beats the dork. Insight #16 (`status-code-is-identity-not-auth-state`), Insight #52 (`an-http-200-at-an-api-path-is-not-that-api`), and Insight #68 (`verification-rungs-claim-ladder`) are the canonical statements.

**Principle two: names are the finding. Do not exfiltrate.** Verification reads enough to confirm reach. Not more. Enumerate vector-database collection names. Do not read the records. Enumerate the model list. Do not invoke inference. Read the schema, never the rows. The restraint ethic makes NuClide findings safe to disclose without exposing the operator's customers to harm via the report itself.

## 3. The evidence: 79 insights bucketed

We coded every numbered insight against the pipeline-stage rubric.

| Bucket | Count | Share |
|---|---|---|
| Verification | 39 | 49% |
| Codification | 22 | 28% |
| Scanning | 18 | 23% |
| **Total** | **79** | (#48 reserved) |

Bucketing artifact: `research-program/insight-bucketing-2026-06-07.md`.

The methodology lesson NuClide takes home from a survey is more often a lesson about how to know whether a candidate is real than a lesson about how to find candidates. Five worked examples.

**Insight #40: Auth-on-default shifts rightward in successor OSS generations.** The modal OSS LLM-infrastructure project ships with authentication ON by default. Exposed unauthenticated hosts are operator misconfigurations, not project misdesigns. The successor releases harden the surface that drove the prior disclosure. The thesis is falsifiable at the verify step, not the scan step.

**Insight #68: The verification-rung grid.** Every claim NuClide makes carries a verification status: depth (code reading vs live confirmation) and breadth (one host vs population). The pair is orthogonal. Depth-deep, breadth-narrow is one host verified hard. Depth-shallow, breadth-wide is a hundred hosts that returned 200 with nobody reading the body. Claim language binds to the rung. "Critical class-level default credential" requires depth (read the credential's effect) and breadth (population sample, not n=1).

**Insight #73: Header-versioned APIs are invisible to header-less fingerprinters.** CVAT uses Django REST Framework's `AcceptHeaderVersioning`. The identity endpoint returns the platform-confirming JSON only with `Accept: application/vnd.cvat+json`. Generic `Accept` returns 404 or 406. The aimap fingerprinter sent generic Accept and missed all 30 candidates. A re-probe with the right header confirmed all 30. The fingerprinter zero was a tool artifact, not a population fact.

**Insight #77: Passive Shodan is an MCP crypto-sieve.** MCP is Shodan-dark on passive banners. The protocol's identifying content appears only in the response to a POSTed `initialize`. The one dork with recall, the generic JSON-RPC error banner, returns a crypto-mining-dominated false-positive set. Bitcoin, Ethereum, IPFS, stratum pools all emit the same error shape. Discovery produces noise. Verification depth runs the full MCP lifecycle handshake to confirm identity (you reached an MCP server) and capability (what tools it exposes).

**Insight #80: DMARC enforcement is a funding-stage proxy.** A 410-vendor `dig _dmarc` sweep produced a monotonic relationship between policy strictness and funding stage in AI-security vendors. 0% enforcement at YC and pre-seed. 100% at Series C and later. Mid-bands trended upward. The pattern pays dividends only at scale. Its side finding (53% of broader AI-infra domains publish no DMARC at all, vs 13% in AI-security) only emerges when the verify step covers the full population.

Three more insights form the canonical statement of the verify gate. Insight #51 (`port-number-names-a-candidate-not-a-finding`): a TCP-open is not a service. Insight #16 (`status-code-is-identity-not-auth-state`): an HTTP 200 confirms identity, not auth state. Insight #52 (`an-http-200-at-an-api-path-is-not-that-api`): a server answers 200 for paths it does not implement. Insight #52's source case: a 147-finding cohort where every body was an HTML document, not GCP metadata. Reading the body would have stripped all 147 in one pass. Port to status to body. Three rungs of "what does this evidence actually say."

Insight #78 (`shared-deployment-kit-operator-class-exposure`) is the kit case. Three independent operators in xTom Japan ran LiteLLM Enterprise v1.82.6 with the same favicon hash and the same auth-off configuration. The fingerprint of the kit, not the operator, was the classifier. Verifying one instance classified the others. A scan would have produced three independent CRITICALs. A verify-step collapses them to one kit-level exposure with a known population.

The codified lesson is almost never "we found a new dork" or "we built a new fingerprint." It is "we learned what a 200 actually means here" or "we learned how to refute a one-host extrapolation." The methodology is a methodology of the verify step.

## 4. The case: Cat-03 Model Serving, 39 candidates to 6 verified

Cat-03 Model Serving ran 2026-06-05. Consumer-grade OpenAI-compatible inference servers: llama.cpp, vLLM, KoboldCpp, Ollama, SillyTavern, faster-whisper, One API, New API, Open WebUI, SGLang, GPT4All, HuggingFace TGI, and adjacent platforms. All serve LLM inference over HTTP on a small set of well-known ports.

The pipeline ran in full. Discovery surfaced 5,018 unique IPs from 17 Shodan and 9 Censys queries. The scanner collapsed that to 158 live hosts. aimap classified 72 into 19 platform classes and flagged 20 CRITICAL plus 19 HIGH candidates. 39 in total.

The verify step ran.

6 of 39 candidates verified as unauthenticated with a 200-with-data read. 21 were refuted as false positives. 12 were surface-open: the platform was present and reachable but no proof of unauth was exercised, so they are not findings. The candidate-to-finding ratio is 6.5x.

A pre-verification candidate insight, numbered #78 in the live scheme, claimed that One API and its fork New API ship with a `root/123456` default credential at the class level. Basis: a single live host, `121.28.161.118`, where the credential worked and returned `data.role: 100` (root admin). The 9-host population sweep returned 0/9. The candidate was refuted. One API ships first-run password setup. The single host was a lazy-operator outlier. This survey confirmed the auth-on-default thesis, not refuted it. The pre-verification framing would have published a confident, reproducible, wrong claim that an entire vendor class ships with default credentials.

A second pre-verification candidate, #79, claimed an unauthenticated Ollama instance on `121.153.39.157:11434` was proxying a paid Ollama Connect cloud subscription. The verify step confirmed it: `/api/tags` returned 40 models including `deepseek-v4-pro:cloud` with `remote_host: ollama.com`. Any internet host could invoke the paid model through the open Ollama. Real finding. The verify step kept this one and killed the other.

A third candidate, #80 in the pre-verification scheme (later retracted; the live #80 is the DMARC proxy), claimed provincial Indonesian government AI hosts: `jatengprov.go.id` and `kaltaraprov.go.id`. The verify step traced the claim back to VisorScuba. The two `*.go.id` hosts were prior-Ollama-survey carryover from a 2026-05-15 walk. They were never in the Cat-03 corpus. We retracted the candidate and added a process insight: filter VisorScuba output to the survey's own ingested events before attribution. The verify step caught the program from publishing its own ledger noise as a fresh finding. Without it, NuClide would have published two hosts that did not belong to the survey at all.

The most material finding was a single AT&T residential host, `108.210.175.159`, running an enthusiast local-LLM stack on home broadband. Shodan saw three of the four exposed services. The fourth, Ollama on :11434, was Shodan-dark and surfaced only on the active scanner pass. The operator put basic auth on the front-end (SillyTavern) and left the inference backends wide open (KoboldCpp on :5001, Ollama on :11434). Front door locked, backend exposed. We codified the pattern as candidate insight #82: front-end-secured / backend-exposed asymmetry. The attack surface is the dependency graph, not the front door.

The verify step also produced a nine-class false-positive catalog. Four "GPT Researcher" candidates were Gradio Whisper Playgrounds catching the marker on a generic `/api/report 405` catch-all. One "Lunary" was CheckRef behind a generic `/api/v1/health`. One "h2oGPT" was KoboldCpp; both serve `/openai_api/v1/models` and the disambiguator (Server header) was not anchored. Two TTS candidates collided with ZenTao on :8000. Each FP traced back to a fingerprint that lacked a positive body marker or a framework negative-match. Each became a queued aimap fix. The verify step generated four new bugs against the fingerprinter and the data needed to fix them.

39 to 6. Five candidate-insight outcomes: one refuted, one confirmed, one retracted, two proposed. Nine FP classes. None of this is visible at the scan or fingerprint stages.

## 5. The vocabulary: DCWF KSAT coverage

A DoD reader will recognize the activity but not the vocabulary. The DoD Cyber Workforce Framework defines five AI work-roles with per-role KSAT catalogs. Roles 672 (AI Test & Evaluation) and 733 (AI Risk & Ethics) fit NuClide's work. Roles 623, 753, and 902 cover implementation, adoption, and leadership, which NuClide does not do.

We built ksat-tag: a Go tool that parses a case study, applies keyword and pattern rules per role, and inserts an auto-generated tag block. Idempotent. One run covered all 240 case studies. The matrix at `data/dcwf-ksat-coverage-matrix-2026-06-07.csv` records which KSAT IDs each case study touched.

Four KSATs hit at least 90%. K1158 (cybersecurity principles) at 100%. K22 (network and security methodologies) at 98%. K7003 (AI security risks, threats, vulnerabilities, mitigations) at 97%. S7068 (organizational and project-level AI risk identification) at 96%. Every survey, at the floor, is a network-level AI-risk story.

Four KSATs hit below 10%. K7045 (AI lifecycle) at 3%. S7076 (bias in datasets and outputs) at 5%. K7052 (risk and bias assessment principles) at 6%. S7069 (lifespan risk) at 6%. One KSAT at 0%: K7020 (DoD AI Ethical Principles).

K7020 at 0% across 240 case studies is itself a finding. NuClide produces evidence relevant to DoD AI Ethical Principles in nearly every survey. PHI exposure on unauth inference servers. Attribution gaps. Model-impersonation fraud. Blind spots that map onto responsible, equitable, traceable, reliable, governable. The program does not use the vocabulary. The retro-tagger fixes the vocabulary. It does not fix the coverage gaps.

The coverage gaps are real. Bias testing in datasets (S7076) at 5%: infrastructure surveys do not exercise model outputs, so bias assessment is out of scope by methodology. Lifecycle (K7045) at 3%: NuClide takes population snapshots and does not track operators through deploy-update-retire cycles. Lifespan risk (S7069) at 6%: same reason.

The overlay does not claim DCWF-compliance. It makes the verification thesis legible inside DoD vocabulary. The verify step is T5919 (adversarial test in operationally realistic environments) plus T5904 (risk assessment on AI applications). The auth-on-default thesis is K7003 (AI security risks, threats, vulnerabilities, mitigation). The shared vocabulary lets a DoD reader read the paper without translating every term.

## 6. The byproducts

**DMARC enforcement as a funding-stage proxy.** A 410-vendor `dig _dmarc` sweep produced two findings.

First, in the AI-security subsample with funding-stage data (n=31), DMARC strictness scaled monotonically with stage. 0% enforcement at YC and pre-seed. 100% at Series C and later. Mid-bands trended upward. A 50ms passive DNS query lets a researcher infer approximate funding stage, SOC2 audit pressure, and engineering maturity. The signal holds at the extremes and is noisier in the middle. Codified as Insight #80.

Second, the side finding. Across the registry (n=410), 53% of resolvable vendor domains publish no DMARC at all. In the AI-security subcategory, 13% lack DMARC entirely. AI-security trails enterprise SaaS broadly and leads the broader AI-infrastructure population by roughly 4x on basic email hygiene. Hypothesis: SOC2 pressure scales with enterprise-sales motion, not funding stage. The side finding only emerges when the verify step covers the full population.

**Argo Workflows on port 2746, partial refutation.** A candidate insight, `reference-dork-population-substitution`, proposed that `ssl:`-style Shodan dorks select for DNS-configured and security-conscious operators, blinding the researcher to a Shodan-dark tier on `:2746`. The Cat-29 survey from 2026-05-31 found 0 unauth out of 33 probed via `ssl:"Argo Workflows"`, all gated by IAP or AzureAD.

The Lane 1A probe tested one variant: among the 156 hosts already on the `ssl:` population, do any expose `:2746` publicly? 156 of 156 connections timed out at 5 seconds. The variant "operators who expose `:443` with Argo certs also expose `:2746`" is refuted. The broader hypothesis (cert-invisible Argo operators on `:2746`) needs a `port:2746` discovery on a different dork population. Queued for 2026-06-08 credit reset. Partial refutation is a verification-step output. We learned what the data could and could not say.

## 7. The implications

**Defenders.** A scanner report at population scale is a candidate set, not a finding set. The 6.5x correction in the Cat-03 worked example is on the lower end. Surveys with bolder fingerprint claims correct harder. If the security operations workflow consumes scanner output as finding output, the headline number lies and the alert backlog stays full of false positives. Bake verification into the workflow. The 200-with-data gate plus a marker probe plus a population check is the cheapest place to add discipline.

**Vendors.** A NuClide disclosure has already been re-probed. The candidate-to-finding ratio is small by design. This is not a bug-bounty firehose. The curated set is the deliverable. Expect the report to name the specific data read, the specific endpoint queried, the specific operator host confirmed. Expect the report to not have read the customer's data. The restraint ethic is load-bearing.

**The field.** A 49% verification-stage rate in the codified lessons of a yearlong AI-infrastructure research program is the meta-finding. The interesting research lives at the verify step. Publishing scanners is easy. Publishing verification rubrics is rare. Few papers exist on what counts as proof at population scale. More would help.

## 8. Limits and caveats

The 79-insight denominator is small. The 49% rate will move with more data. Verification-stage decisions compound, so the ratio drifts slowly, but a year from now the share could be 45% or 55%.

The bucketing rubric is a judgment call at the boundaries. Three of the 79 codings are flagged as disputed. The shape of the distribution does not change if all three flip. The precise share by half a percentage point does.

The DCWF overlay is post-hoc. NuClide was not designed against the framework. A program built against DCWF from day one would surface different gaps. K7020 at 0% is a vocabulary observation, not a critique.

The Cat-03 worked example is one survey out of dozens. The 6.5x correction is real but not modal. Some surveys correct 1.5x, some 12x. The methodology is the same shape across all of them.

The Cat-29 :2746 refutation is partial. The full hypothesis is still open. The temptation to round up a partial result into a complete result is the kind of verification-stage error this paper is about.

## 9. Conclusion

Verification is the load-bearing stage. The scan is the easy part. Skip verification and your population-scale finding rate is confident, reproducible, and wrong. NuClide invests in verification. That is why the candidate-to-finding ratio looks the way it does. That is why the insights bucket the way they do. The next yearlong project of this kind should design the discipline before the dork.

---

## Provenance

- v1 (4,144 words) shipped 2026-06-07.
- v2 (4,831 words) added canonical-triplet sub-section and retracted-candidate walkthrough.
- v3 (this file, ~3,400 words) Hemingway pass: cut buried lede, cut meta-announcements, cut "because" subordinations, cut long sentences, removed Latinate filler.
- Bucketing artifact: `research-program/insight-bucketing-2026-06-07.md`.
- Source case studies: `case-studies/commercial/`, in particular Cat-03 (`cat03-model-serving-survey-2026-06-05.md`).
- Source insights: `methodology/insight-NN-*.md`, in particular #16, #40, #51, #52, #68, #73, #77, #78, #80.
- Tagger source: `~/ksat-tag/`. Matrix: `data/dcwf-ksat-coverage-matrix-2026-06-07.csv`.
