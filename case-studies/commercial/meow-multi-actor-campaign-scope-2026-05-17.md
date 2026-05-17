---
type: synthesis
---

# Meow / Indexrm Elasticsearch extortion. Three actors. (2026-05-17)

_NuClide Research · 2026-05-17_
_Companion to: [`22-ai-stack-attribution-2026-05-17.md`](22-ai-stack-attribution-2026-05-17.md), [`es-clickhouse-cross-stack-2026-05-17.md`](es-clickhouse-cross-stack-2026-05-17.md)_

---

## Summary

We sampled 150 of the 3,604 fully-wiped Elasticsearch hosts from this morning's re-probe. We read the `read_me` index on each one. Three different actors are running the campaign in parallel.

| Actor | Hosts (of 150) | Wallet | Email | Note Schema | Demand | Income |
|---:|---:|---|---|---|---:|---:|
| A | 130 (91%) | `bc1q38rjul6gdamfflf6p4ukz0ymtvfgfv2j9saf6r` | `wendy.etabw@gmx.com` | `[message]` | 0.0041 BTC | 0.018 BTC, 5 paid |
| B | 12 (8%) | `bc1quwlw8djc7hfamf3qpspma34uh9dr6w4kudfu8p` | `db-recovery@sharebot.net` | `[amount, bitcoin, email, message, warning]` | varies | 0 BTC |
| C | 1 (1%) | `bc1qvrryy2vsq4jekejs8z2elkt3sxmhlyad06ymvr` | `scandal@onionmail.org` | `[message, timestamp, warning]` | 0.0035 BTC | 0 BTC |

Three wallets. Three contact addresses. Three different note schemas (the mapping shapes differ across hosts, which means three different tools). Only Actor A is monetizing.

---

## How we got here from a wrong inference

We sampled three wiped hosts earlier today. All three carried the same ransom note. We extrapolated single-actor at population scale. We sent a coordinated disclosure to UCloud for the hospital host (`106.75.127.240`) that named Actor A.

The host is actually Actor C's. The cert pivot and aimap probe were correct on the technical exposure. The actor attribution was wrong. A correction went out within an hour.

The error is the same shape as the Insight #28 retraction earlier today. A small sample's identity is not the population's identity. Insight #29 codifies this.

---

## Per-actor profile

### Actor A

Wallet `bc1q38rjul6gdamfflf6p4ukz0ymtvfgfv2j9saf6r`. Five paid victims. About 0.018 BTC received and swept out.

Email `wendy.etabw@gmx.com`. GMX free German webmail.

Per-host code `0SH7HH1Q72JL`. Identical across hosts, which means the "corresponds to your database" claim is a template lie.

URL `https://tli.sh/73x1k`. Redirects to a `paste.sh` page with end-to-end client-side encryption. We decrypted the page with the key in the URL fragment. The follow-up text restates the demand. It also includes P2P + VPN guidance for Chinese victims buying Bitcoin under PBOC restrictions, which matches the victim population's skew toward Tencent and Aliyun hosts.

Note schema is single-field `message` carrying the prose. Demand is 0.0041 BTC, roughly $400.

### Actor B

Wallet `bc1quwlw8djc7hfamf3qpspma34uh9dr6w4kudfu8p`. Zero paid victims. Zero income.

Email `db-recovery@sharebot.net`. The domain is less-common.

Note schema is five fields: `amount`, `bitcoin`, `email`, `message`, `warning`. The structured schema lets an automated decoder parse fields without regex. That choice suggests slightly more deliberate tooling.

### Actor C

Wallet `bc1qvrryy2vsq4jekejs8z2elkt3sxmhlyad06ymvr`. Zero paid victims. Zero income.

Email `scandal@onionmail.org`. Tor-routed mail. Defensible against subpoena.

Note schema is three fields: `message`, `timestamp`, `warning`. Demand is 0.0035 BTC, slightly lower than Actor A.

Anomalous: this actor plants 112 documents in the `read_me` index. Other actors plant one. The hospital host on UCloud (`106.75.127.240`) is one of this actor's targets.

---

## Restraint

We read the `read_me` mapping and one document per host. That is attacker-broadcast content. The actor wrote it for victims to read.

We did not read any other index on any of the 150 hosts. No operator data, no patient records, no PII. Only the attacker's own message.

---

## Implication for disclosure framing

A bulk-disclosure batch from yesterday's wiped-host list now needs per-host actor classification before send. A template that names Actor A works for 91% of hosts and is wrong for 9%. Each disclosure draft should re-probe the target host and extract the wallet and email before composing the body.

aimap v1.9.9 (shipped this morning) adds the `compromised_by_extortion` classifier. A v1.9.10 follow-up should extract the actor identifier and tag the host. Then disclosure templates can be per-actor-aware.

---

## Toolchain provenance

```
fast-probe   [x] 150-host concurrent probe (40 workers, 6s timeout)
                read_me _mapping (metadata) and read_me _search size=1 (attacker-broadcast)
                no probing of operator data indices on any of the 150
mempool.space [x] wallet investigation on all 3 attacker wallets
                A: 5 paid, 0.018 BTC swept
                B: 0 paid, 0 BTC
                C: 0 paid, 0 BTC
aimap v1.9.9 [—] not used for this probe. v1.9.10 will fold the multi-actor
                extraction into enumElasticsearch.
visorlog     [x] earlier ingest stands
```

---

## See also

- [`22-ai-stack-attribution-2026-05-17.md`](22-ai-stack-attribution-2026-05-17.md)
- [`es-clickhouse-cross-stack-2026-05-17.md`](es-clickhouse-cross-stack-2026-05-17.md)
- [`../../methodology/insight-29-overwhelming-prior-state-look-at-deltas-not-snapshots.md`](../../methodology/insight-29-overwhelming-prior-state-look-at-deltas-not-snapshots.md)
- [`../../methodology/insight-28-survey-shelf-life-exposure-to-extortion.md`](../../methodology/insight-28-survey-shelf-life-exposure-to-extortion.md)
- [`../../evidence/2026-05-17-meow-attribution/`](../../evidence/2026-05-17-meow-attribution/)
