# Insight #84: Cloud-native guardrail wrappers expand operator blast radius in every case. No LiteLLM cloud-wrapper is fully transparent.

**Codified:** 2026-06-07. Cat-33 Phase 5 Lane D Slice D survey over LiteLLM cloud-native guardrail hooks.
**Source:** `data/platform-intel/cat33-lane-d-slice-d-cloud-deltas-2026-06-07.md` (3 cloud-native + 1 OSS framework).
**Family:** Insight #74 (gateway-as-master-key-multiplier), Insight #78 (shared-deployment-kit-operator-class-exposure), Insight #62 (ai-agent-service-colocation-compound-attack-surface).
**Falsifiability tier:** medium. n=3 cloud-native plus 1 OSS (Presidio); a fourth distinct cloud-wrapper case would promote.

## The pattern

LiteLLM wraps three cloud-native guardrail surfaces (AWS Bedrock Guardrails, OpenAI Moderation, Azure Content Safety) plus one OSS framework (Microsoft Presidio). In each case, the underlying cloud or framework API is unchanged. The wrapper layer is the same library, the same auth, the same documented contract. Yet in each case, the wrapper introduces a NEW operator-side attack surface that does not exist when the customer calls the cloud API directly.

| Target | Underlying API | New surface introduced by LiteLLM wrapper |
|---|---|---|
| AWS Bedrock Guardrails | unchanged | AWS creds centralized at CVE-rich LiteLLM proxy; `_redact_pii_matches` post-processing layer |
| OpenAI Moderation | unchanged | `api_base` operator-overrideable, NOT allowlisted. Misconfig = full exfil redirect of every moderated message. |
| Azure Content Safety | unchanged | Hardcoded `MAX_TEXT_LENGTH = 10000` word-boundary chunking introduces a cross-chunk evasion vector direct callers do not have. |
| Microsoft Presidio | unchanged | Default `api_base` scheme is plaintext `http://` when scheme is missing. PII unencrypted in transit by default on any non-loopback Presidio deployment. |

The pattern is structural. When LiteLLM mediates the call, the operator's blast radius is the LiteLLM proxy itself plus the cloud target. The CVE history of LiteLLM (14 NVD + 8 GH Advisories at last count, including CVE-2026-40217 sandbox escape) attaches to every wrapped cloud call. Calling the cloud API directly avoids that attachment.

## Why this matters

The customer who chose AWS Bedrock or OpenAI or Azure for compliance reasons (FedRAMP, ISO 27001, SOC 2) inherits LiteLLM's compliance posture the moment they wrap the call through LiteLLM. The wrapped path is not a transparent passthrough; it is a new system with the cloud target as a subsystem. The customer's threat model has to change to account for LiteLLM as a privileged middleman.

This is structurally similar to Insight #74 (gateway-as-master-key-multiplier): a layer that centralizes credentials and adds operator-side decision logic widens the blast radius even when the underlying API is unchanged. Insight #84 extends #74 from auth multiplexers to guardrail wrappers. The pattern is general for any LiteLLM-style wrapping layer.

## How to apply

- When surveying customer deployments of LiteLLM guardrail wrappers, note which cloud target they wrap. A wrapped Bedrock Guardrail is not the same threat model as a direct Bedrock Guardrail call.
- When writing a disclosure that involves LiteLLM-wrapped cloud guardrails, name both layers. The customer may not realize the wrapper layer is in scope.
- For population surveys: dorks that find LiteLLM proxies should be cross-referenced against dorks that find the underlying cloud guardrail target. The two populations overlap; the overlap is the blast-radius-expanded subset.

## Special note on Presidio

The Presidio default-scheme finding (`http://` when scheme missing) is the most concrete-operator-trap class of the four. A misconfigured customer puts PII over plaintext HTTP across whatever network sits between LiteLLM proxy and the Presidio deployment. If the Presidio deployment is in the same cluster as LiteLLM (the documented default), the risk is bounded by the cluster boundary. If the customer points LiteLLM at a remote Presidio (e.g., on a separate k8s namespace, separate VPC, or external service), PII traverses the network unencrypted. The customer is unlikely to notice until a packet capture or a transit-layer audit catches it.

## DCWF KSAT fit

- 672: T5919 (verify at the wrapper boundary, not just the target), K7044 (V&V tooling against multi-layer wrappers).
- 733: T5904 (risk assessment of compound systems), T5882 (responsible AI process for wrapped guardrails).
- Overlap: K7003 (AI security risks at the wrapper layer), K22 (network: where the wrapper sits).
