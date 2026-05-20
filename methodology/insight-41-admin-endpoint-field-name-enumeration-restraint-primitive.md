---
type: methodology
insight_number: 41
title: Admin-endpoint field-name enumeration is the Stage-2-deep verify primitive; secret-class field names at documented paths are the finding, no value read required
---

# Insight #40. Admin-endpoint field-name enumeration: names verify the credential, values stay unread

_Source: Network-mesh / Envoy admin survey, 2026-05-19. 34 unauthenticated Envoy admin endpoints returned `/config_dump`. Sixteen of them had `downstream_auth_password.inline_string` populated with a non-empty 10-character string at the documented Envoy redis_proxy DataSource path. The credential was confirmed exposed without the value ever being read. Verification by field-name position; restraint by design._

## The rule

For admin-style endpoints that return a long structured JSON dump (Envoy `/config_dump`, Spring Actuator `/env` and `/configprops`, Kong admin `/config`, Consul `/v1/agent/self`, Vault `/sys/config/state/sanitized`, Traefik `/api/rawdata`, NATS `/varz`), **the Stage-2-deep verify primitive is enumeration of secret-class field names at documented paths, not extraction of values**.

A scanner that records HTTP 200 confirms the endpoint is reachable. A marker-conjunct fingerprint confirms the platform identity. Neither answers whether a credential is *exposed in the body*. To answer that, the verifier walks the JSON tree and records every leaf key whose name belongs to the platform's documented secret class. A populated leaf at a documented credential path **is** the finding. The value is never read.

The restraint ethic and the verification primitive are the same operation here. Other endpoints require sampling values to confirm severity (a leaked S3 URL needs an HTTP HEAD to confirm the bucket is open; a leaked DB connection string needs a port check). An admin-config dump does not. The platform's own API contract makes the field-name placement load-bearing: when Envoy's redis_proxy filter has `downstream_auth_password.inline_string`, the inline_string field is literally the password value per the proto spec. Position-verified is proof-verified.

## Empirical basis

### Envoy `/config_dump` survey (this survey, 2026-05-19)

34 unauthenticated Envoy admin `/config_dump` hits across the network-mesh corpus. Stage-2-deep verifier (`verify_config_dump.py`) walked each response, recording every leaf key whose name matched the secret-class set: `private_key`, `inline_string`, `downstream_auth_password`, `client_secret`, `aws_secret_access_key`, `session_ticket_keys`, `bearer_token`, `password`, etc.

Per-host roll-up:

| Tier | Count | Body evidence |
|---|---|---|
| CRED_INLINE — Redis-AUTH password populated | 16 | `$.configs[*].downstream_auth_password.inline_string` present, value length = 10 chars |
| CRED_REF — TLS private-key filename indirection only | 9 | `$.private_key.filename` present, no `inline_string` |
| TOPOLOGY_ONLY — dump returned, no credential paths populated | 8 | clusters / listeners / routes disclosed; no secret-class leaf hits |
| BODY-TEMPLATE-ONLY — `direct_response.body.inline_string` only (FP class) | 1 | inline_string under route response body, not credentials |

The 16 CRED_INLINE hosts share an identical Envoy fingerprint: build hash `923c4111bb48405ac96ef050c4f59ebbad3d7761/1.14.4/Clean/RELEASE/BoringSSL`, listener `redis_listener::0.0.0.0:1999`, cluster `redis_cluster`, config path `/etc/envoy/envoy.yaml`, hot_restart_version 11.104. All 16 are GCP-hosted (verified WHOIS: Google LLC GOOGL-2 / GOOGLE-CLOUD). PTR-empty across all 16; no TLS on the admin port; visorgraph cert-pivot produces zero nodes. The credential is exposed, the operator is anonymized by GCP-VM design.

The identical 10-character value length across 16 hosts is the shipping-default signal. The Envoy 1.14.4 examples directory ships a `redis_proxy` filter example config that operators copy-paste; the chart-time placeholder was inherited unchanged. Insight #13 (shipping defaults are load-bearing) confirms at fleet scale on a new platform class.

No value was read in the course of the survey. Length, position, and structural placement are sufficient to publish the finding.

### Adjacent platforms where the primitive applies

| Platform | Dump endpoint | Credential-class field paths |
|---|---|---|
| Envoy admin | `/config_dump` | `*.private_key.inline_string`, `*.downstream_auth_password.inline_string`, `*.client_secret`, `*.aws_*` |
| Spring Actuator | `/env`, `/configprops` | `*.password`, `*.secret`, `*.api-key`, `spring.datasource.password`, `*.aws.credentials.*` |
| Kong admin | `/config`, `/services/{}/plugins` | `*.config.credentials.*`, `*.password`, JWT `*.secret` |
| Consul agent | `/v1/agent/self` | `Stats.ACL`, `Config.TLSConfig.KeyFile`, `Config.Datacenter` (topology) |
| Vault sys | `/sys/config/state/sanitized` | sealed by design; if `unsanitized` is reachable, `*.token`, `*.client_token` |
| Traefik | `/api/rawdata` | `*.tls.certificates[*].keyFile`, `*.basicAuth.users`, `*.http.middlewares.*.password` |
| NATS | `/varz` | `auth_required`, `tls_required`, leaf-node creds path |

The primitive transfers across the row. The secret-class field-name list is platform-specific; the verification primitive is shared.

## Diagnostic signals

A host is CRED_INLINE-class when:

1. The admin endpoint returns 200 unauthenticated AND
2. The body parses as the platform's documented dump JSON AND
3. At least one leaf at a documented credential path has a non-empty string value AND
4. The leaf is not a known platform false-positive (`direct_response.body.inline_string` is a route template, not a credential; `allow_credentials` is a CORS boolean, not a credential).

A host is CRED_REF-class when criteria 1 and 2 hold and at least one credential-class leaf has a `filename`-only indirection or empty value — the operator's filesystem layout is disclosed but no value is in the body.

A host is TOPOLOGY_ONLY when criteria 1 and 2 hold and no credential-class leaf is populated — the admin surface is exposed and the platform topology (routes, listeners, clusters) is disclosed, but no credential is in the body. Still a finding; severity medium.

## Procedural rules this insight generates

1. **Build the secret-class field-name list per platform from the protobuf / OpenAPI / Rego spec, not from a memory of "what credentials look like."** The Envoy proto spec is the authoritative source for `downstream_auth_password.inline_string`. The Spring Actuator config-reference is the authoritative source for `spring.datasource.password`. Primary source over framing (the recurring methodology rule); the source spec is what binds field name to credential semantic.

2. **Walk the full JSON tree, not just the top-level documented credentials.** Insight #3 (handshake leaks structure even when invocation is gated) generalizes: the credential leaf may live three levels under a non-secret-named parent. Walk every key, match on substring of the leaf name against the secret-class set, record the full `$.path.to.leaf`.

3. **Anti-FP: filter on parent path, not only on leaf name.** `inline_string` is an Envoy DataSource leaf used in many contexts (cert PEM, password, response body template, header value). The parent path discriminates the credential class. A verifier that records `inline_string` matches without parent-path context produces false positives at the `direct_response.body` level (observed in this survey: 2 hosts had only direct_response body templates, would have been miscounted as CRED_INLINE).

4. **Record value length and value class, never value content.** Length is enough to identify a shared-template signal across a fleet (16/16 hosts with identical value length is the load-bearing signal). The value itself contributes nothing to the finding that the length doesn't already prove.

5. **The verify primitive is per-platform-pluggable, not bespoke.** A future aimap deep-enumerator for Envoy admin should encode the secret-class field-name list and the parent-path discriminators, then emit a per-host roll-up. Promote the survey-time `verify_config_dump.py` into an aimap deep-enumerator.

6. **Tag the finding `<PLATFORM>-FIELD-NAME-VERIFIED`** in VisorLog so downstream consumers can distinguish field-name-position evidence from value-read evidence. Restraint posture is part of the finding's metadata, not separate from it.

## Relationship to prior insights

- **Insight #6 (conjunctive marker-anchored matchers)**: same family at a different layer. #6 is the Stage-1 fingerprint discipline — three conjuncts (endpoint + structured response + anchored keyword) prevent identifying a wrong platform. #40 is the Stage-2-deep verify discipline — three conjuncts (200 status + parsed-JSON shape + secret-class field at documented path) prevent recording a wrong finding tier.

- **Insight #16 (200 is platform identity, not auth state)**: #40 extends. #16 says "a 200 on `/v1/traces` is alive-at-URL, not auth-off; check the data layer." #40 says: when the data layer is itself a long JSON dump, the verify primitive is field-name enumeration at documented credential paths.

- **Insight #18 (storage-tier vs tracker-tier)**: the mistake that exposes an admin tracker does not always propagate to the credential value. 9 of 34 hosts in this survey had `private_key.filename` indirection only — the operator's filesystem layout leaked, but the credential value stayed on disk. Same epistemology: separate the topology disclosure from the value disclosure; the severity tier follows the more conservative answer.

- **Insight #13 (shipping defaults are load-bearing)**: re-confirmed at fleet scale on the Envoy redis_proxy filter. The example config that ships with the Envoy 1.14.4 examples directory inherits forward across 16 operator deployments unchanged.

- **Insight #19 (CDN-fronted SPA → grep JS bundle for `https://api.`)**: parallel structure. #19 says: name-level metadata in an operator-exposed JS bundle is the finding (`api.<brand>.<tld>`). #40 says: name-level metadata in an operator-exposed JSON admin dump is the finding. Both reject the framing that an enumerable name set is "metadata-only and harmless" — the names are operator-authored content and carry the intelligence.

- **The restraint ethic (CLAUDE.md / `/stack` "How we test" blocks)**: the operational discipline and the verification primitive collapse to a single rule on admin-config endpoints. Read names, never values. Position-verified is proof-verified.

## Open questions

- **What fraction of unauthenticated Envoy admin endpoints expose `downstream_auth_password.inline_string` with a populated value?** This survey saw 16 / 34 (47%) at population scale, in a GCP-anonymized fleet. A broader Envoy admin sweep (across Hetzner, OVH, Vultr, Scaleway, DigitalOcean) would map population proportion; the GCP-skew is one cloud's worth of evidence.

- **Does the Envoy 1.14.4 redis_proxy example config ship with the 10-char value?** Confirming this would close the loop on Insight #13 by identifying the literal source of the shipping default. The Envoy upstream `examples/redis/envoy.yaml` (v1.14.4 tag) is the file to read; the operator templates likely derive from it verbatim.

- **Spring Actuator `/env` and `/configprops` at population scale**: known-unsafe by Spring docs since the 2018 advisory yet still ships off-by-default sanitization in many deployments. Apply the field-name enumeration primitive across the population-scale Actuator survey backlog.

- **How does the primitive degrade on adversarial / honeypot admin endpoints?** A deception fleet that fabricates a fake `/config_dump` with realistic-looking field names but no real backing service would defeat field-name-only verification. Protocol-strict handshake conformance (Insight #1) is the cross-check — if the rest of the admin endpoint set (`/clusters`, `/listeners`, `/server_info`) is also internally consistent, the fingerprint is real.
