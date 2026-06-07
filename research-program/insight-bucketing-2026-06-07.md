# Insight Bucketing — Section 3 Prep for the Verification Paper

_Created 2026-06-07. Phase 4 prep. Codes every numbered insight in `methodology/insight-*.md` into one of three buckets: scanning-stage, verification-stage, codification-stage. The headline claim of the verification paper rests on the tally produced here._

## Rubric

- **Scanning-stage**: about choosing the dork, picking the port, finding the right banner, selecting a discovery channel, building a fingerprint. Failure mode = missed a candidate or fired on a generic match. The fix lives in `shodan/queries/`, `aimap/fingerprints/`, or the dork ladder.
- **Verification-stage**: about whether a candidate is real, what counts as proof, how a marker probe differs from a status code, FP catalogs, refutations. Failure mode = wrong claim from a true scan. The fix lives in `methodology/`, the verification rubric, or a candidate insight refutation.
- **Codification-stage**: about how to write up, attribute, name, summarize, classify findings AFTER verification. Failure mode = a verified finding gets the wrong label, scope, or owner. The fix lives in case-study templates, attribution methodology, or the registry.

Disputed cases (where a strong second coder would disagree) are flagged with `?`.

## Tally

| Bucket | Count | % of 79 |
|---|---|---|
| Verification-stage | 39 | 49% |
| Codification-stage | 22 | 28% |
| Scanning-stage | 18 | 23% |
| **Total** | **79** | (#48 reserved, never assigned) |

**Headline:** verification is the single largest bucket and is roughly 2x the scanning bucket. The codified lessons from a yearlong AI-infra research program show that the verify step is where method correctness is decided more often than any other stage.

## Per-insight coding

### Scanning-stage (18)

| # | Slug | Why scanning |
|---|---|---|
| 03 | capabilities-object-schema-leak | what to look for in capability JSON |
| 06 | conjunctive-matchers-required | dork composition |
| 09 | cross-survey-correlation-discovery-vector | discovery channel |
| 12 | ip-direct-shadow | discovery pattern |
| 14 | yield-vs-port-class-alignment | port selection |
| 19 | spa-headless-api-exposure-tell | fingerprint shape |
| 20 | aimap-catalog-gaps `?` | fingerprint gap; arguably verification |
| 21 | port-first-discovery-for-low-footprint-platforms | discovery method |
| 23 | discovery-channel-coverage-is-multiplicative | channel selection |
| 43 | visorsd-multi-asn-query-bug | tool bug at discovery |
| 44 | parallel-aimap-socket-pool-contention | tool bug at fingerprint |
| 45 | niche-dork-class-hierarchy | dork hierarchy |
| 56 | langgraph-self-identifying-json-fingerprint | fingerprint |
| 66 | default-ports-must-be-survey-driven | port selection |
| 67 | voice-api-servers-shodan-dark-json-root | Shodan-dark + JSON root |
| 73 | header-versioned-apis-evade-headerless-fingerprinters | fingerprint bug |
| 75 | http-admin-ports-kill-cert-pivot | cert-pivot limitation |
| 77 | mcp-shodan-cryptosieve-lifecycle-depthgate | Shodan-stage lifecycle |

### Verification-stage (39)

| # | Slug | Why verification |
|---|---|---|
| 01 | protocol-strict-self-filters-honeypots | honeypot detection = verification |
| 07 | shodan-facet-bucketing-fp-class | FP bucketing |
| 08 | auth-bypass-via-misconfiguration-redirects | proof shape |
| 11 | source-code-is-authority | primary source over framing |
| 15 | dork-hits-vs-platform-instances | dork validity at scale |
| 16 | status-code-is-identity-not-auth-state | canonical: proof vs label |
| 22 | protocol-strict-handshakes-against-multi-protocol-honeypots | honeypot |
| 25 | falsification-confirmation-tier-c-platforms | proof tier |
| 26 | shodan-facet-fp-rate-escalates-with-token-commonality | FP at scale |
| 30 | multi-port-identical-responses-identify-honeypots | honeypot |
| 31 | app-builder-brand-in-output | brand mislabel — proof shape |
| 32 | deception-fleet-multi-service-emulation | honeypot |
| 36 | paas-build-arg-secret-baking | proof shape |
| 37 | asymmetric-auth-gating-dashboard-vs-api | proof shape |
| 38 | exfiltrated-credential-hard-proof-chain | proof chain |
| 40 | auth-on-default-shifts-rightward-in-successor-generations | the macro thesis = verification result |
| 41 | admin-endpoint-field-name-enumeration-restraint-primitive | restraint primitive |
| 47 | tls-cn-attribution-only-not-platform-confirmation | distinction at proof step |
| 49 | ollama-cloud-signin-public-exposure | what counts as proof |
| 51 | port-number-names-a-candidate-not-a-finding | canonical: candidate vs finding |
| 52 | an-http-200-at-an-api-path-is-not-that-api | canonical: proof |
| 53 | a-hostname-label-is-not-a-cloud-project-identifier | canonical: name vs proof |
| 54 | metabase-setup-token-self-authorizing-credential | proof shape |
| 55 | auth-gated-api-signup-open-default | proof shape |
| 57 | partial-auth-failure-class | proof shape |
| 58 | vite-dev-server-in-production | proof shape |
| 59 | n8n-split-surface-auth-gap | proof shape |
| 60 | redis-stack-ft-list-vector-tier-enumeration | proof shape |
| 61 | redisinsight-api-databases-credential-leak | proof shape |
| 64 | agent-manifest-prerun-disclosure | proof shape |
| 65 | tls-cert-dork-selection-bias | dork validity (population-substitution) |
| 68 | verification-rungs-claim-ladder | canonical: the rubric |
| 69 | curated-scan-negative-is-not-host-negative | proof shape |
| 70 | censys-dual-primitive-ports-identity-decoder-authstate | decoder vs identity |
| 71 | network-placement-as-auth | auth definition |
| 72 | ships-auth-but-default-open-registration | registration tier |
| 76 | app-auth-on-operator-debris-auth-off | proof shape |
| 79 | aspirational-name-field-attribution-hierarchy | name vs ID |
| 80 | dmarc-funding-stage-proxy | passive primitive at verify step |

### Codification-stage (22)

| # | Slug | Why codification |
|---|---|---|
| 02 | single-template-auth-off-propagates | pattern naming |
| 04 | whois-driven-contact-resolution | attribution post-find |
| 05 | same-day-remediation-feedback-loop | engagement cycle |
| 10 | vendor-template-default-no-auth | pattern naming |
| 13 | shipping-defaults-load-bearing | pattern naming |
| 17 | platform-class-operators-are-mono-platform | population pattern |
| 18 | storage-tier-hygiene-exceeds-tracker-tier | cross-tier pattern |
| 24 | operator-workload-visibility-via-api-show `?` | borderline verification |
| 27 | docker-image-template-version-dominance | pattern naming |
| 28 | survey-shelf-life-exposure-to-extortion | post-find ethic |
| 29 | overwhelming-prior-state-look-at-deltas-not-snapshots | analysis discipline |
| 33 | side-channel-attribution-via-registry-catalog | attribution |
| 34 | persistence-without-pressure | post-find pattern |
| 35 | side-channel-attribution-high-precision-low-recall | attribution |
| 39 | pooled-account-attribution-laundering | attribution |
| 42 | litellm-model-impersonation-fraud | pattern naming |
| 46 | tls-cn-operator-attribution-surface | attribution |
| 50 | ovms-backend-colocation | compound pattern |
| 62 | ai-agent-service-colocation-compound-attack-surface | compound pattern |
| 63 | install-experience-predicts-auth-posture | population pattern |
| 74 | gateway-as-master-key-multiplier | compound risk |
| 78 | shared-deployment-kit-operator-class-exposure | compound pattern |

## Note on the original "18 of 21" claim

The verification-paper outline I wrote earlier in this session used "18 of 21 codified insights are verification-stage failures." That number is from older memory and predates the current insight corpus. The fresh bucketing across all 79 numbered insights yields 39/79 = 49%. The rhetorical headline of the paper needs to update.

Better candidate headlines from the fresh tally:

- "Of 79 codified lessons from a yearlong AI-infra research program, verification-stage decisions account for nearly half — twice the rate of scanning-stage decisions."
- "Across 79 codified insights, the verify step produces more methodology than the scan step by a factor of 2."
- "Verification accounts for 49% of codified lessons. Scanning accounts for 23%. Codification accounts for 28%. The middle stage is the load-bearing one."

The thesis is unchanged: verification is where method correctness lives. The specific number to quote is now well-anchored.

## Disputed codings to revisit

- **#20** (aimap-catalog-gaps): I coded scanning because the failure is in the fingerprinter. A second coder could argue the lesson is about the verification check catching the catalog gap. Keep `?` flag.
- **#24** (operator-workload-visibility-via-api-show): coded codification because it's about a pattern in API responses; could be verification if read as a proof-shape lesson.
- **#65** (tls-cert-dork-selection-bias): coded verification (dork validity at the scaling step). A second coder could call this scanning (dork choice). Both are defensible.

## Next step

Section 3 of the paper draws from this table directly. Write Section 3 next; cite this file as the supporting bucketing artifact.
