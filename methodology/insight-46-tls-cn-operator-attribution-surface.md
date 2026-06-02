---
type: methodology
insight_number: 46
title: "TLS certificate subject CN is a precise operator-attribution surface; operators who embed platform brand names in cert CN are doing intentional TLS termination, making cert-CN dorks stable against CDN proxying and more precise than HTML body matching."
---

# Insight #46. TLS cert subject CN as operator-attribution surface

_Source: LLM orchestration category-01 re-run, 2026-05-19. `ssl.cert.subject.cn:openai` returned 965 hosts; `ssl.cert.subject.cn:litellm` returned 812; `ssl.cert.subject.cn:ollama` returned 244. Total: 2,021 self-attributed operator hosts across three platform classes._

## The rule

An operator who names a TLS certificate after the AI platform they're running (`openai.mycompany.com`, `litellm-prod`, `ollama-inference`) has:

1. Provisioned a custom TLS certificate (not a default self-signed cert)
2. Configured DNS to point to their deployment
3. Deliberately named the cert using the platform brand

This is a high-signal attribution surface. The operator's choice is preserved in the Certificate Transparency log (RFC 6962), which means:

- The attribution persists even if the operator adds a CDN layer between the host and the public internet
- It is visible in Shodan's `ssl.cert.subject.cn` index without requiring live HTTP access
- It predates and survives operator-side changes to HTTP headers, title tags, or HTML content

**CN-dork discovery is complementary to, not competitive with, HTML body dorks.** They select different subpopulations.

## Empirical basis (LLM orchestration re-run, 2026-05-19)

| Dork | Hits | Platform class |
|---|---|---|
| `ssl.cert.subject.cn:openai` | 965 | OpenAI-compatible API hosts (LiteLLM, one-api, new-api, custom wrappers) |
| `ssl.cert.subject.cn:litellm` | 812 | LiteLLM self-hosted deployments with custom CN |
| `ssl.cert.subject.cn:ollama` | 244 | Ollama deployments with custom CN |
| **Total** | **2,021** | Across 3 platform classes |

Cross-comparison against the Server-header population from the same session (`"Server: ollama"` returned 33 confirmed in the primary corpus): the two populations have minimal overlap. Operators in the CN-based population are running TLS termination + reverse-proxy frontends; they will typically NOT appear in Server-header dorks because the proxy (nginx/caddy/traefik) masks the upstream `Server:` header.

**The CN-based population and the Server-header population are largely disjoint.** Both are needed for complete coverage.

## Procedural rules this insight generates

1. **Add `ssl.cert.subject.cn:<platform>` to every dork catalog.** For any platform survey, write at least one CN-anchored dork alongside the Server-header and body dorks. CN dorks find the proxy-fronted population that Server-header dorks miss.

2. **CN attribution is high-precision for operator identity.** An operator who names their cert `litellm.acme-corp.com` has told you both the platform AND the org. This is the first attribution step before VisorGraph cert-pivot and VisorSD ASN sweep.

3. **CN hits warrant VisorGraph pivoting.** A CN-identified host's cert SANs often list the operator's other services. Feed CN-dork hits into VisorGraph as additional seeds alongside the IP-based seeds.

4. **Distinguish CN-class from SAN-class.** `ssl.cert.subject.cn:X` matches the primary cert identity. `ssl.cert.san:X` matches Subject Alternative Names. The SAN class is broader (catches wildcard certs that cover the platform subdomain) but has higher FP rate. Use CN for precision attribution, SAN for coverage extension.

5. **CN dorks are stable over time.** Unlike HTML content (which operators update) or Server headers (which proxy configs change), a cert CN is set at issuance time and typically persists until cert renewal. A cert CN observed today in Shodan may reflect an issuance from 1-2 years ago.

## Relationship to prior insights

- **Insight #47 (TLS-CN class is attribution-only, not platform confirmation)**: the necessary follow-up. CN-dork discovery identifies operators, not auth state. See Insight #47 before making any auth-state claim based on CN hits.
- **Insight #35 (side-channel attribution: high precision, low recall)**: CN-based attribution is an instance of this class. High precision (the operator named themselves); low recall (only operators with custom TLS certs appear).
- **Insight #65 (TLS cert dork selection bias)**: the related finding for Argo Workflows — ssl:"ArgoProj" selects managed production (all 401), not quick-start vulnerable instances. Same structural mechanism: TLS-configured operators are more security-conscious.

## See also

- `case-studies/commercial/llm-orchestration-rerun-2026-05-19.md` §11 (Codify)
- `methodology/insight-47-tls-cn-attribution-only-not-platform-confirmation.md`: required companion insight
- `methodology/insight-35-side-channel-attribution-high-precision-low-recall.md`
- `methodology/insight-65-tls-cert-dork-selection-bias.md`
