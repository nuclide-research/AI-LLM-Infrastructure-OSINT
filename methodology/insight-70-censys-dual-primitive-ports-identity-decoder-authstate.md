---
title: "Insight #70: Censys is a dual primitive — full-range ports give identity, protocol decoders give auth-state; never conflate the label with the decoder"
date: 2026-05-31
survey: censys-xref-2026-05-31
thesis_touch: methodology (verification discipline at the data tier; not a thesis data point)
extends: ["insight-69-curated-scan-negative-is-not-host-negative", "insight-16-a-200-is-identity-not-auth-state", "insight-12-ship-one-service-auth-off-ship-them-all", "insight-06-conjunctive-marker-anchored-matchers"]
---

# Insight #70: Censys is a dual primitive

## The lesson

A Censys cross-reference returns two separable things, and treating them as one
ships a wrong number. The first is **identity**: the full-range port sweep shows
which services a host actually runs, including the data tier and second apps a
curated AI-port scan never touches. The second is **auth-state**: the protocol
decoders (`postgres.startup_error`, `redis.ping_response`, an HTTP `302 -> /login`)
report whether each of those services is actually open. A port plus a `DATABASE`
label is identity. The decoder is auth-state. They are different claims, and the
discipline is to never let the first smuggle in the second.

## Evidence (148.113.183.4, Perplexica/OVH, Censys-xref 2026-05-31)

Our RAG survey logged this host as a single confirmed-unauth Perplexica endpoint
(one port). A Censys `view` returned **ten services**: ssh 22, traefik 80/443,
Perplexica 3000, Postgres 5432, a second DB 5436, ports 6001/6002, Redis 6379,
and a Coolify deployment-platform panel on 8000.

Read as identity alone, that is a Postgres + Redis + Coolify catastrophe behind an
unauthenticated app. The decoders said otherwise, and we never connected to the
host to learn it:

- `services[].postgres.startup_error` = `"no PostgreSQL user name specified in
  startup packet"` — alive, demands credentials. Not open.
- `services[].redis.ping_response` = `"NOAUTH Authentication required"` — auth on.
- Coolify :8000 = `302 -> /login` — login-gated.

The data and control tier were **auth-enforced**. The only unauthenticated surface
was the Perplexica app we already had. Stopping at the port list and the labels
would have manufactured a multi-service breach out of a single-app exposure.

## The rule

1. **The port and its software label are identity (surface open). The decoder is
   auth-state.** Quote the decoder, not the label, when classifying auth. This is
   Insight #16 (a 200 is identity not auth) carried down to the data tier.
2. **Read the decoder before claiming a shadow service is open.** `postgres`,
   `redis`, `mongodb.is_master.read_only`, and HTTP redirect/login shape are
   restraint primitives: they classify auth posture from Censys' own decode, so no
   data-tier probe leaves our machine.
3. **Software labels are candidates, banner-verify them.** Censys labeled
   152.53.91.184:8000 `neo4j/DATABASE`; the HTTP body in the same record was an SPA
   titled "RefChecker." The label was a false positive and the banner was the
   primary source (Insight #6 at the indexer layer).

## Corollary: the negative is also a Censys result

The full-range read cuts both ways. The Cat-29 Argo port-2746 dark tier (SYN-ACK
only, RST on application bytes) is invisible to Censys too: across eight hosts
sampled over Alibaba (8/47/101/116/120) and Tencent (43), zero showed port 2746
and six showed no services at all. That is a clean negative that **strengthens**
the dark-tier conclusion — the tier is host-side connection-filtered, not a Shodan
undersample. A Shodan-dark port is not a host negative (Insight #69), and here the
full-range telescope confirms the darkness is real, not instrumental.

## Thesis touch

On 148.113.183.4 the app tier was unauthenticated while the data tier was
authenticated — a partial counter to Insight #12 ("ship one service auth-off, ship
them all auth-off"). The storage tier inherited a safer default than the app tier.
Storage-tier-versus-app-tier default divergence (the Insight #18 shape) is the
reason the per-service decoder matters: you cannot infer the data tier's posture
from the app tier's.

## Access note (corrects the insight-69 access note)

cencli (the Censys Platform CLI) IS authenticated on rooster; its PAT lives in the
cencli keyring, not in `cencli config print`, so a blank-looking config is not
"no creds" — run `cencli credits` to settle it. Free User tier is **24 credits per
week** (not the 100/month the docs imply); `cencli view` costs exactly 1 credit and
**does return full services plus the protocol decoders** on Free. `cencli search`
(population) returns 403 on Free without an organization id, so population sweeps
stay on the web UI / Playwright lane; per-asset `view`/`censeye`/`aggregate` are the
budgeted verification tools. `data/censys-sweep.py` targets the deprecated legacy v2
endpoint and is the wrong tool for the Platform.
