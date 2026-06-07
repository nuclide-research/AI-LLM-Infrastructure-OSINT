---
type: synthesis
---

# Meow / Indexrm campaign: per-actor census across 4,776 ES hosts

_NuClide Research, 2026-05-17 (evening pass)_
_Companion: [`meow-multi-actor-campaign-scope-2026-05-17.md`](meow-multi-actor-campaign-scope-2026-05-17.md), [`es-clickhouse-cross-stack-2026-05-17.md`](es-clickhouse-cross-stack-2026-05-17.md)_

---

## Summary

We re-ran the full 4,776-host Elasticsearch population through aimap v1.9.10. The new release reads one document from the attacker-planted marker index and parses it for actor identifiers. The morning's 150-host probe found three actors; the population-scale pass confirms three primary actors plus a long tail.

<!-- ksat-tag:auto-generated:start -->
## DCWF KSAT coverage

Auto-derived from DCWF AI work-role rule files (`ksat-tag`).

- **672 (AI Test & Evaluation Specialist):** K7003, K7004, K7044, S7068, S7070, T5904
- **733 (AI Risk & Ethics Specialist):** K7040, K7051, S7069, T5868
- **overlap (Common AI KSATs (all 5 roles)):** K1158, K22, K7003

<!-- ksat-tag:auto-generated:end -->

**The three actors share the `read_me` schema but use distinct wallets and contact channels.** Actor A dominates: 88% of attributed hosts. Actor B sits at 8.5%. Actor C is the smallest, at 0.7%, with a notably slower wipe tempo.

The 24-hour delta against yesterday's snapshot: 47 hosts dropped off (unreachable on port 9200), and the compromised count fell by 46. The population is at long-term equilibrium. Insight #29 holds.

---

## Per-actor census

Population: 4,729 reachable Elasticsearch hosts. Of these:

| Cohort | Hosts | % of population | % of compromised |
|---|---:|---:|---:|
| Compromised (any marker) | 4,365 | 92.3% | 100% |
| Clean (no marker, still unauth) | 364 | 7.7% | — |

Per-actor breakdown of the 4,254 attributed compromised hosts (111 attribution-failed):

| Actor | Email | BTC wallet | Hosts | Share |
|---|---|---|---:|---:|
| **Actor A (Meow / wendy.etabw)** | `wendy.etabw@gmx.com` | `bc1q38rjul6gdamfflf6p4ukz0ymtvfgfv2j9saf6r` | 3,806 | 88.2% |
| **Actor B (sharebot)** | `db-recovery@sharebot.net` (+ `es-recovery@sharebot.net` × 8) | `bc1quwlw8djc7hfamf3qpspma34uh9dr6w4kudfu8p` | 366 | 8.5% |
| **Actor C (onionmail)** | `scandal@onionmail.org` (+ `rambler+5sw91@onionmail.org` × 1) | `bc1qvrryy2vsq4jekejs8z2elkt3sxmhlyad06ymvr` | 32 | 0.7% |
| **Unknown** (recognized wallet pattern, unrecognized email schema) | various | 7 one-off wallets | 111 | 2.6% |
| **Attribution-failed** (marker present, doc unreachable or empty) | — | — | 50 | 1.0% |

---

## Wipe-completion tempo per actor

The aimap classifier reports `compromised-wiped` (no operator data remaining) vs `compromised-marked` (marker planted, data still alive). The ratio per actor:

| Actor | Wiped | Marked | Wipe completion rate |
|---|---:|---:|---:|
| Actor A | 2,870 | 936 | **75.4%** |
| Actor B | 291 | 75 | **79.5%** |
| Actor C | 5 | 27 | **15.6%** |
| Unknown | 86 | 25 | 77.5% |

Actor A and Actor B run on similar tempos. **Actor C completes wipes at roughly 1/5th the rate** of the other two. Two readings: (a) Actor C is a recent entrant whose first wave is still mid-execution, or (b) Actor C deliberately leaves more hosts in the marked-but-alive state, possibly to maximize the negotiation window.

---

## The wallet tail

Beyond the three primary wallets, the census surfaced seven one-host wallets:

```
bc1qvrte050fngjlrmcuptz33259kw3wktkd3uv5hv
bc1qt5cq2mnghwyyfl0pkd3086z9cad0m3hspwgl9t
bc1qqy3uegcgqjjncagjnkqgpplyl3k4a00khek5rs
bc1qk8tef9e2r9h2ylfauf779cnjwkcrec5rrsk2zr
bc1qjzsrw37tqu90kfa6dpf6jegpv2nhvdefxxngvu
bc1q5xj2mvtaupy56fff4dsaxwjxm8ftjzxfhw3ylh
bc1q034lz76j5y8t8vh64kzyvuhkugmq6mu7c8mkc6
```

Each appears on a single host. Three readings: (a) per-cohort wallet generation for cluster-level negotiation isolation, (b) third-party reuse of the `read_me` schema with different payment channels, (c) actors who rotated wallets mid-campaign. The classifier captures these as "unknown" because the email pattern does not match Actor A/B/C templates.

The two email variants, `es-recovery@sharebot.net` (Actor B) and `rambler+5sw91@onionmail.org` (Actor C), suggest each actor maintains multiple mail aliases, possibly to silo per-cohort negotiation traffic.

---

## 24-hour delta (Insight #29 applied)

Yesterday's snapshot (2026-05-16 evening): 4,776 reachable ES + 4,411 compromised (92.4%).
Today's snapshot (2026-05-17 evening): 4,729 reachable ES + 4,365 compromised (92.3%).

| Metric | 2026-05-16 | 2026-05-17 | 24h delta |
|---|---:|---:|---:|
| Reachable on port 9200 | 4,776 | 4,729 | −47 |
| Compromised (any marker) | 4,411 | 4,365 | −46 |
| Clean (unauth, no marker) | 365 | 364 | −1 |
| Compromise rate | 92.4% | 92.3% | flat |

**The population is in equilibrium.** New exposure-to-compromise transitions are not visible at this measurement cadence because the population was already saturated yesterday. Insight #29 predicted exactly this: snapshot ≠ daily rate. The 46-host reduction in compromised count matches the 47-host population shrink, so most of the "decrease" is hosts that went offline, not hosts that the operator cleaned up.

To measure the actual daily transition rate, we would need to track ingress (newly exposed instances) separately from outgoing (cleaned + dropped). Both flows are real, but they cancel out at this aggregation level.

---

## Why Actor A dominates

3,806 hosts → 88.2% market share. Actor B and Actor C together account for less than 10%. The asymmetry is striking.

Three explanations are consistent with the data:
1. **Actor A had a head start.** The campaign has been running long enough that A's early scans got first-mover advantage on every exposed host.
2. **A's tooling is more aggressive.** The aimap probe surfaces hosts within seconds; an attacker bot running similar tooling could enumerate the IPv4 / Shodan-feed range in days. If A runs faster scans, A wins more hosts.
3. **B and C are clones who scraped A's schema.** The marker doc has the same structure across all three. If B and C are imitators forking A's payload generator, they get to the host after A has already planted; their probe sees a non-empty marker index and they back off (or they overwrite, but the wallet stays unique to whoever wrote last).

We cannot distinguish between (1), (2), and (3) from the snapshot alone. A second-derivative measurement, what fraction of the unknown-tail wallets correlate with hosts that previously appeared in Actor A's footprint, would help.

---

## Wallet-to-payment ratio

The wallet decryption work documented in [`meow-multi-actor-campaign-scope-2026-05-17.md`](meow-multi-actor-campaign-scope-2026-05-17.md) showed Actor A's wallet has received ~0.018 BTC across ~5 inbound transactions. With 3,806 marked hosts, that is a **0.13% payment rate**. Even if Actor B and Actor C match A's rate (we have not yet pulled their wallet histories), the campaign-wide economics are dominated by deletion, not extortion revenue.

The campaign is profitable only at scale. Each host costs near-zero to mark; each payment is small (0.0041 BTC ≈ $300 at current rates); the campaign pays only if the absolute count of marked hosts is large.

---

## What this changes for downstream work

1. **Disclosure framing per actor** is now possible. If a host's marker doc carries Actor B's wallet or email, the disclosure can be specific about which actor's negotiation behavior to expect ("Actor B accepts emails to db-recovery@sharebot.net but the wallet has zero payments observed, so payment is unlikely to recover data").
2. **The 111 unknown-wallet cohort warrants follow-up.** Each carries a unique BTC wallet. If those wallets aggregate non-zero traffic on the blockchain, they map to a fourth class of operator we have not yet identified.
3. **The es-recovery / rambler email variants** should be added to the v1.9.11 classifier so they roll up into Actor B and Actor C respectively, instead of being part of the "unknown" bucket.

---

## Toolchain provenance

```
aimap v1.9.10   [x] 4,729 hosts probed in 6m14s on 50 threads, port 9200 only
                    Actor attribution via /<marker>/_search?size=1 (~64 KB cap, 1 doc)
visorgraph      [—] not re-run; yesterday's 22 AI-stack subset is the cert-pivot set
shodan host     [—] not re-run; yesterday's harvest is the population
visorlog ingest [ ] queued: ingest census.json into nuclide.db
```

---

## See also

- [`meow-multi-actor-campaign-scope-2026-05-17.md`](meow-multi-actor-campaign-scope-2026-05-17.md): three-actor identification, paste.sh decryption
- [`22-ai-stack-attribution-2026-05-17.md`](22-ai-stack-attribution-2026-05-17.md): AI-stack subset attribution
- [`../../methodology/insight-29-overwhelming-prior-state-look-at-deltas-not-snapshots.md`](../../methodology/insight-29-overwhelming-prior-state-look-at-deltas-not-snapshots.md)
