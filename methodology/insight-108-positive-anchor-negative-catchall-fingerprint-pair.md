---
type: methodology
insight_number: 108
title: "Positive-anchor + negative-catch-all fingerprint pair: a vendor-UNIQUE field the fleet never fakes (package:Langflow) beats a generic-substring triple the fleet can stuff, and a nonsense path must NOT return 200 to clear the catch-all responder"
status: candidate
codified: 2026-06-19
source_survey: Cat-Langflow 2026-06-18 (35 health_check triple-match FPs cleared, 2 real Langflow recovered)
falsifiability_tier: high
falsified_by: a scanner-poisoning fleet that learns to stuff the vendor-unique positive anchor itself (e.g. emits "package":"Langflow" in its mega-JSON) while still catch-all 200ing nonsense paths, breaking the positive anchor's discriminating power
related_insights: [6, 16, 32, 52, 56, 95, 102, 107]
---

# Insight #108 - Positive-anchor + negative-catch-all fingerprint pair

## The pattern

Insight #107's scanner-poisoning fleet defeats generic-substring fingerprints by
pre-stuffing the marker space. The fix is a TWO-PART fingerprint, and both parts
are mandatory:

1. **Positive anchor on a vendor-UNIQUE schema field** the fleet does not bother
   to fake, NOT a generic substring the fleet can stuff. For Langflow the anchor
   is `GET /api/v1/version` body contains `"package":"Langflow"`. The fleet fakes
   a Gitea-shaped version object (`"version":"10.0.1+gitea-1.22.0"`) and never
   emits the `package` field, because faking it would require knowing this exact
   discriminator. A generic triple ("body contains status AND chat AND db")
   matched the fleet's 135KB canned HTML and its mega-JSON both; it produced 35
   false positives and zero real findings.

2. **Negative catch-all guard**: a nonsense path must NOT return 200. Issue one
   request to `/api/v1/<random>`. A 200-with-canned-body disqualifies the host
   regardless of what the positive anchor said, because a catch-all responder
   will echo a 200 on EVERY path including the one your positive anchor probes.
   The guard is the floor under the anchor: without it, a sufficiently aggressive
   fleet that also stuffed the anchor string would pass.

The two parts attack the two failure modes. The positive anchor defeats
under-specificity (a generic substring matches too much). The negative guard
defeats the catch-all (any path returns 200, so even a specific path probe is
unreliable on a catch-all host). Neither alone is sufficient against the #107
fleet; the pair is.

## The discriminating principle

A fingerprint field's value is inversely proportional to how easy it is to stuff.

- **Generic substrings** (`status`, `chat`, `db`, a `<title>` keyword) are
  free for the fleet to include and appear by accident in unrelated bodies.
  Worthless as a sole anchor.
- **Vendor-unique schema keys** that only the real platform's serializer emits
  (`"package":"Langflow"`; cf. Insight #56's LangGraph self-identifying JSON
  fingerprint) cost the fleet specific knowledge to fake and rarely collide.
  High-value anchors.
- **Functional proof** (the strongest tier): the real open platform's
  `auto_login` token authenticates a privileged endpoint (`/api/v1/flows/`
  returns 200), where the fleet's fabricated token does not. This is Insight #16
  taken to its end - identity is not the 200, identity is what the credential
  the response handed you can actually DO. The fleet's "jack" JWT is expired and
  authenticates nothing; the real platform's token works. Use functional proof to
  separate "real platform, open" from "real platform, hardened" after the schema
  anchor has separated "real platform" from "fleet."

## The Langflow fingerprint (concrete)

```
# POSITIVE anchor (identity):
GET /api/v1/version  ->  body contains "package":"Langflow"
                         (fleet emits Gitea-shaped version, never this key)

# NEGATIVE guard (catch-all detector, run FIRST):
GET /api/v1/<random-nonsense>  ->  MUST NOT return 200-with-body
                         (catch-all responder 200s every path)

# FUNCTIONAL proof (auth state, only for hosts that pass the two above):
POST /api/v1/auto_login token  ->  GET /api/v1/flows/ with that token == 200
                         (real OPEN Langflow; hardened returns 400/403)
```

The generic `health_check` triple (`status` + `chat` + `db`) is INSUFFICIENT
ALONE and should be demoted to a pre-filter at most, never a confirmation.

## Empirical founding case - Cat-Langflow 2026-06-18

- 35 IPs / 76 port-combos "confirmed" by the generic triple-match: ALL false
  positive, all #107 fleet.
- Re-run with the `package:Langflow` positive anchor + nonsense-path negative
  guard: 35/35 fleet hosts cleared (fleet returns Gitea version, and 200s the
  nonsense path), 2 real Langflow recovered.
  - `172.241.24.136:443` Langflow v1.5.0.post2 HARDENED (auto_login 400, flows/vars 403; config 200 leaks feature-flags only)
  - `24.152.39.20:7860` Langflow v1.7.3 HARDENED (auto_login 400, flows/vars/config 403)
- Both real instances `AUTO_LOGIN=False`. Functional proof tier never reached an
  open state - both hardened, consistent with Insight #40 (disclosure-pressure
  hardening; Langflow had the Flodrix botnet mass-exploitation campaign and three
  CISA-KEV CVEs across 2025-2026). 0 open instances found.

## Relationship to #95 and #102 (the same family, a different substrate)

This insight is in the schema-anchor family with #95 and #102, but the substrate
it corrects for is different:

- **#95** (OSS name as registry dork): the platform name surfaces in Docker
  registry `/v2/_catalog` JSON; the dork lands on REGISTRIES cataloging the
  image. Fix: probe `/v2/_catalog` to confirm "registry," not "platform."
- **#102** (dork-stage schema anchor for OSS-name-collision): the name lands on a
  collision substrate (Docker registries, OR distinct same-named projects like
  GraphRAG). Fix: anchor the DORK on a schema marker only the intended platform
  emits, pushing the anchor upstream to Stage 0.
- **#108** (this insight): the title lands on a SCANNER-POISONING FLEET (#107)
  that actively stuffs generic markers to defeat substring fingerprints. The
  collision is adversarial, not incidental. Fix: a vendor-unique POSITIVE anchor
  the fleet does not fake, PAIRED with a NEGATIVE catch-all guard the fleet cannot
  pass. #95 and #102 face passive substrates (a registry is not trying to look
  like Langflow); #108 faces an active adversary engineering the collision. That
  is why #108 needs the negative guard that #95 and #102 do not - a passive
  substrate does not 200 a nonsense path on purpose; the #107 fleet does.

The shared family lesson (Insight #6, conjunctive marker-anchored matchers,
applied at every stage) holds across all three. #108 adds the negative conjunct
as a co-equal partner to the positive conjunct, specifically because the
adversary is the one constructing the collision.

## How to apply (generalizes past Langflow)

1. **For every title/keyword dork, pair a positive schema anchor with a negative
   catch-all guard.** The positive anchor is a vendor-unique key from the
   platform's own serializer (find it in source - Insight #11, source is
   authority). The negative guard is one nonsense-path request that must NOT 200.

2. **Demote generic-substring triples to pre-filters.** A `status`/`chat`/`db`
   style triple narrows the candidate set cheaply but NEVER confirms. Confirmation
   requires the vendor-unique key.

3. **Run the negative guard BEFORE the positive anchor.** Cheaper to disqualify a
   catch-all host on one nonsense request than to reason about why its positive
   anchor matched.

4. **Reach functional proof for auth-state, not identity.** Once identity is
   nailed by the schema anchor, separate open from hardened by what a returned
   credential can DO, not by a 200 (Insight #16, #52). The fleet's tokens
   authenticate nothing; a real open platform's do.

5. **Encode both conjuncts in the tome platform JSON and the aimap fingerprint.**
   Add a `positive_anchor` field (vendor-unique key + path) and a
   `negative_catchall_guard: true` flag to every platform that has been seen
   under a poisoned title dork. The aimap matcher runs the guard as a first-class
   negative conjunct (`nonsense_path_must_not_200`).

## Relationship to prior insights

- **Insight #6 (conjunctive matchers required)**: this insight is the specific
  positive+negative conjunct pair the #107 fleet forces. #6 said "use multiple
  conditions"; #108 says "one of those conditions must be a NEGATIVE catch-all
  guard when an adversarial fleet is in the population."
- **Insight #16 (a 200 is identity not auth state)** and **#52 (an HTTP 200 at an
  API path is not that API)**: #108 is the operational fingerprint that enforces
  both. The catch-all 200 is the purest case of #52; the functional-proof tier is
  the purest case of #16.
- **Insight #56 (LangGraph self-identifying JSON fingerprint)**: the
  positive-anchor exemplar - a vendor-unique JSON key is the right anchor. #108
  generalizes #56 into a rule and pairs it with the negative guard.
- **Insight #32 / #107 (deception fleets)**: #108 is the fingerprint discipline
  that survives them. #107 describes the adversary; #108 is the defense.
- **Insight #95 / #102 (schema-anchor family)**: same family, passive substrate;
  #108 is the adversarial-substrate member that adds the negative catch-all guard.
- **Insight #40 (auth-on-default shifts rightward)**: explains why the 2 real
  Langflow recovered by this fingerprint are both hardened - the platform's CVE /
  botnet pressure drove operators to `AUTO_LOGIN=False`.

## Falsifiability

Falsified if the #107 fleet learns to stuff the vendor-unique positive anchor
itself (emits `"package":"Langflow"` in its mega-JSON) while still catch-all
200ing nonsense paths. At that point the positive anchor loses discriminating
power and only the negative catch-all guard + functional proof remain - the
fingerprint degrades from a pair to a guard-plus-proof. Worth re-checking on the
next Langflow survey whether the fleet has adapted.

## See also

- `shodan/cat-langflow-2026-06-18/FINDINGS-CONSOLIDATED.md` - the founding survey
- `shodan/cat-langflow-2026-06-18/real-langflow-authposture.json` - the 2 recovered real Langflow
- `shodan/cat-langflow-2026-06-18/deep-collect.json` - 35 hosts, all fleet (Gitea version)
- `insight-107-scanner-poisoning-mega-json-deception-fleet.md` - the fleet this fingerprint defeats
- `insight-56-langgraph-self-identifying-json-fingerprint.md` - the positive-anchor exemplar
- `insight-102-dork-stage-schema-anchor-dual-of-95.md` - the passive-substrate schema-anchor sibling
- `insight-52-an-http-200-at-an-api-path-is-not-that-api.md` - the catch-all 200 principle

---

_Status: CANDIDATE. Promotion pending one additional survey applying the
positive-anchor + negative-catch-all pair to a second poisoned title dork and
either recovering the real platform tier OR confirming the fleet adapted. Cite
Cat-Langflow 2026-06-18 as the founding evidence._
