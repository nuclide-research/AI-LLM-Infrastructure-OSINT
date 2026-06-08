# Insight #87 — Canary Persistence as Operator-Monitoring Proxy

_NuClide Research · 2026-06-08 · Origin: ChromaDB CVE-2026-45829 campaign attribution._

---

## Statement

The fraction of a host population that still carries a known adversary canary N days after a mass-exploitation burst is a direct proxy for that population's collection-level monitoring posture. High persistence (>50% canary-still-present after a week) means the operators do not watch for new collection creation. The auth-on-default population overlaps the no-observability population by construction — the same operator decision (deploy the default, walk away) produces both.

## Derivation

The 2026-06-02 Chroma campaign deposited paired canary collections (`probe-base-<ns>` and `probe-ef-<ns>`) on every Shodan-discoverable unauth Chroma host in a 119-second window. On 2026-06-08, six days later:

  201 of 307 verified-unauth hosts (65%) still carry the canary collections.

A trivially-detectable string (`probe-base-1780358529676380700`) sat in the default-tenant collection list for 144 hours and 201 operators did not see it. The canary persistence rate is the monitoring failure rate.

## Why operators miss it

- Chroma has no built-in collection-creation audit log.
- The default tenant + default database paths are the well-known ones; collections appearing there look "normal" to a glance.
- The collection NAME is the only thing that flags the canary as adversary-created — and no operator is grepping their collection list for `^probe-(base|ef)-` patterns.
- The exploit class itself (`trust_remote_code=True` in `embedding_function.config.kwargs`) does not show up in conventional logs because it's a configuration field of a collection, not an action.

## Use of the rule

When you survey a platform where attackers can leave attribution-grade artifacts (named collections, named topics, named queues, schema mutations), pull the artifact list and grep for adversary patterns *before* assuming the deployment is clean. The persistence rate gives you a second number to publish alongside the auth-on-default rate:

  - auth-on-default rate    = "what fraction of operators ship with no auth?"
  - canary-persistence rate = "what fraction of those operators do not monitor what gets created?"

These are different population characteristics. The first measures the deployment decision; the second measures the operational posture.

## Cross-references

- Insight #8 (auth probing): a corrected probe stage that distinguishes 200-with-data from 200-without-data. Canary detection extends Insight #8 by adding pattern-match-on-content as a tier of analysis above pure auth-state.
- Insight #76 (auth-permissive baseline): the auth-permissive population is the population where this canary signal is even readable. On auth-on populations the campaign would have been blocked before the canary could be deposited.

## Tooling

The detection takes 60 lines of Python and runs at 30 concurrency in 24 seconds across a 307-host corpus. It is fully reusable for any platform with an unauth-readable list-of-named-things endpoint (Qdrant collections, Milvus collections, Weaviate classes, Redis keys, etcd prefixes, Postgres databases). The general form:

  GET /list-of-things → response body → regex for adversary-pattern names → count → publish.

If the value is non-zero on your own internal infrastructure, you have already missed at least one campaign and you do not have collection-creation monitoring.
