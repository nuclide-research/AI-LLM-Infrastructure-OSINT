---
type: synthesis
---

# Meow / Indexrm Elasticsearch extortion — multi-actor campaign scope (2026-05-17)

_NuClide Research · 2026-05-17 (session 17b continuation)_
_Companion to: [`22-ai-stack-attribution-2026-05-17.md`](22-ai-stack-attribution-2026-05-17.md) + [`es-clickhouse-cross-stack-2026-05-17.md`](es-clickhouse-cross-stack-2026-05-17.md)_

---

## Summary

Structural probe of `read_me` indices across 150 wiped Elasticsearch hosts
(deterministic random sample from the 3,604 fully-wiped hosts in the
2026-05-17 re-survey). The check answers a question we got wrong this
morning from a 3-host sample: **is this one actor or many?**

Result: **at least three distinct actors operating the campaign in
parallel.** The dominant actor accounts for 91% of wiped hosts, but is
not the sole operator. Each actor uses different infrastructure
(wallets, contact emails, note schemas) — they're not a single
coordinated entity.

| Actor | Hosts (of 150) | BTC Wallet | Contact Email | Note Schema | Demand | Income |
|---:|---:|---|---|---|---:|---:|
| **A** (dominant) | 130 (91%) | `bc1q38rjul6gdamfflf6p4ukz0ymtvfgfv2j9saf6r` | `wendy.etabw@gmx.com` | `[message]` 1-field | 0.0041 BTC | ~0.018 BTC (5 paid) |
| **B** | 12 (8%) | `bc1quwlw8djc7hfamf3qpspma34uh9dr6w4kudfu8p` | `db-recovery@sharebot.net` | `[amount, bitcoin, email, message, warning]` 5-field | (varies) | 0 BTC |
| **C** | 1 (1%) | `bc1qvrryy2vsq4jekejs8z2elkt3sxmhlyad06ymvr` | `scandal@onionmail.org` | `[message, timestamp, warning]` 3-field | 0.0035 BTC | 0 BTC |

Three different operators, three different tool stacks (inferable from
the three different `read_me` index schemas), three different
infrastructure choices (GMX vs sharebot vs Tor-routed onionmail). Only
Actor A is monetizing. Actors B and C have zero income on their wallets
to date — they're either newer deployments, less effective copy, or
victims have learned to stop paying.

---

## What this overturned

A 3-host sample taken 2 hours earlier (104.197.153.228, 104.248.1.214,
101.44.26.183) all carried identical notes attributed to Actor A. From
that sample I confidently extrapolated: *"single-actor campaign at
population scale."* Coordinated disclosure went to UCloud for the
hospital host (`106.75.127.240`) naming Actor A.

The host is actually Actor C's. A correction was sent within an hour;
the framing in the original message was wrong for that specific host.

This is the **second instance in one session** of the same class of
mistake codified in Insight #29 — extrapolating from a small homogeneous
sample to a heterogeneous population. The morning's mistake was about
population-state (snapshot ≠ rate); this one was about actor
attribution (3-host sample ≠ population composition).

The procedural correction now in Insight #29 (postscript):

> Every per-host claim that depends on an actor / classifier / category
> attribution must be verified on that specific host, not inferred from
> population-level patterns. The population stats describe the prior;
> the per-host probe is the evidence that updates it.

---

## How the three actors differ — operational fingerprints

### Actor A (dominant — 91%)

- **Wallet:** `bc1q38rjul6gdamfflf6p4ukz0ymtvfgfv2j9saf6r` — 5 paid victims, ~0.018 BTC received, swept out
- **Email:** `wendy.etabw@gmx.com` — GMX German free webmail
- **Per-host code:** `0SH7HH1Q72JL` (identical across hosts — template lie)
- **Note schema:** single-field `message` containing the full prose
- **URL:** `https://tli.sh/73x1k` → `https://paste.sh/3S0XQFln#5h8mVtIQ3_-hvSvhAwstTNLJ` (E2E-encrypted pastebin)
- **Demand:** 0.0041 BTC (~$400)
- **Operational signatures:** China-victim awareness (the paste.sh follow-up has explicit P2P/VPN guidance for Chinese victims), free clearnet infrastructure, no Tor, no per-host customization

This is the actor we initially attributed and whose attribution holds for the **majority** of the wiped population. The full Actor A deep-dive lives in the session-17b evidence pack: `evidence/2026-05-17-meow-attribution/`.

### Actor B (~8%)

- **Wallet:** `bc1quwlw8djc7hfamf3qpspma34uh9dr6w4kudfu8p` — 0 paid victims, 0 BTC
- **Email:** `db-recovery@sharebot.net` — sharebot.net (less-common domain, possibly attacker-controlled)
- **Note schema:** 5-field structured — `amount`, `bitcoin`, `email`, `message`, `warning`. The schema-level structure indicates the actor wrote a more deliberate ransom-note template (separating identifiers from prose), which usually means slightly more professional tooling

Zero income suggests this actor's deployment is either much smaller, much newer, or much less effective. The structured-schema choice is interesting — it would let an automated decoder (the victim's response automation) parse the actor's fields without regex. We have not yet looked into whether sharebot.net is actor-controlled, a compromised legitimate service, or a typo on `sharebox.net` / similar.

### Actor C (~1%, but includes the hospital host)

- **Wallet:** `bc1qvrryy2vsq4jekejs8z2elkt3sxmhlyad06ymvr` — 0 paid victims, 0 BTC
- **Email:** `scandal@onionmail.org` — **Tor-routed email service**, much more opsec-aware than the other two actors
- **Note schema:** 3-field structured — `message`, `timestamp`, `warning`
- **Demand:** 0.0035 BTC (~$350)
- **Operational signatures:** Uses Tor-routed mail (defensible against subpoena), slightly lower demand (possibly market-segmentation), and **anomalous note-count** (the hospital host carries 112 read_me documents vs other actors' 1 — Actor C plants multiple ransom notes per host)

Actor C is the **most opsec-aware** of the three but also the most marginal in terms of population share. The fact that the hospital host on UCloud (270K+ patient-record vectors) is one of Actor C's targets is operationally interesting — either coincidence or selective targeting.

---

## What this means for the population

**Of 4,776 confirmed-unauth ES hosts re-probed today:**

- ~92% have an extortion-marker `read_me` index (population-state)
- Of those, ~91% are Actor A's; ~8% Actor B; ~1% Actor C (estimated from 150-host sample)
- Only Actor A has any paid-victim income on the wallet

**Of 4,411 with extortion-marker yesterday:**

- ~4,015 are Actor A's
- ~353 are Actor B's
- ~44 are Actor C's (the hospital is in this cohort)

**Implication for disclosure framing:**

- A bulk-disclosure batch built from yesterday's wiped-host list now needs **per-host actor classification** before send. A single template that names "Actor A" works for 91% of hosts and is wrong for 9%. Insight #29's per-host-verification rule applies.
- aimap v1.9.9 (shipped earlier today) added a `compromised_by_extortion` classifier that detects the read_me marker. A v1.9.10 follow-up should additionally extract the actor identifier (wallet / email) and tag the host accordingly — moving from "is compromised: yes/no" to "is compromised by actor X."

**Methodology lesson:**

This is a refinement of Insight #15 (dork-hits-are-not-platform-instances) and Insight #16 (200-is-platform-identity-not-auth-state) applied to extortion-actor attribution: **a sample's identity is the sample's identity, not the population's.** Per-host claims need per-host evidence.

---

## Toolchain provenance

```
fast-probe         [x] 150-host concurrent probe (40 workers), 6-second timeout per request
                       Restraint: read_me _mapping (metadata) + read_me _search size=1 (attacker-broadcast)
                       No probing of operator's actual data indices
mempool.space      [x] wallet investigation on all 3 attacker BTC addresses
                       Actor A: 5 paid, ~0.018 BTC swept
                       Actor B: 0 paid, 0 BTC
                       Actor C: 0 paid, 0 BTC
aimap v1.9.9       [—] not used for this probe — protocol-strict structural check predates the classifier; will fold the multi-actor signature into v1.9.10's enumElasticsearch
visorlog           [x] events from earlier ingest stand
```

---

## See also

- [`22-ai-stack-attribution-2026-05-17.md`](22-ai-stack-attribution-2026-05-17.md) — the 22-host attribution sweep (parent case)
- [`es-clickhouse-cross-stack-2026-05-17.md`](es-clickhouse-cross-stack-2026-05-17.md) — the day's parent survey
- [`../../methodology/insight-29-overwhelming-prior-state-look-at-deltas-not-snapshots.md`](../../methodology/insight-29-overwhelming-prior-state-look-at-deltas-not-snapshots.md) — the meta-rule (with this case's instance in the postscript)
- [`../../methodology/insight-28-survey-shelf-life-exposure-to-extortion.md`](../../methodology/insight-28-survey-shelf-life-exposure-to-extortion.md) — first instance of the same class of mistake earlier today
- [`../../evidence/2026-05-17-meow-attribution/`](../../evidence/2026-05-17-meow-attribution/) — evidence pack incl. multi-actor scope NDJSON
