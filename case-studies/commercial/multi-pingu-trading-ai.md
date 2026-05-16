---
type: multi-host
---

# Unknown Operator: Pingu Crypto Trading AI + Nova Molecular Optimization: Live Strategy IP Exposed via Unauthenticated Qdrant

_NuClide Research · 2026-05-03_

---

## Summary

A single Qdrant instance on a Vultr host exposes two parallel autonomous AI agent systems without authentication. The first, "Pingu", is a live crypto trading AI with active positions, real PnL history, and multi-paragraph LLM reasoning traces for BTC/ETH/SOL decisions. The second, "Nova", is an autonomous molecular optimization agent participating in what appears to be a computational chemistry competition, with unreleased batch results and leaderboard rankings. Both systems use Mem0 for long-term memory persistence. All 25 collections are fully readable and scrollable with no API key.

Disclosure: Pending operator identification.

---

## Infrastructure

| Field | Value |
|---|---|
| IP | 45.76.20.46 |
| Hoster | Vultr (US) |
| Service | Qdrant vector database |
| Port | 6333 (HTTP, no auth) |
| Qdrant version | Not pinned at time of discovery |
| Collections | 25 total |
| Operator | Unknown |

---

## Collection Inventory

| Collection | System | Category |
|---|---|---|
| `pingu_btc` | Pingu | BTC trade memory |
| `pingu_eth` | Pingu | ETH trade memory |
| `pingu_sol` | Pingu | SOL trade memory |
| `pingu_master` | Pingu | Master strategy memory |
| `pingu_rules` | Pingu | Trading rules |
| `pingu_setups` | Pingu | Setup patterns |
| `pingu_levels` | Pingu | Price level memory |
| `trade_outcomes` | Pingu | Historical trade results |
| `strategy_decisions` | Pingu | Full AI reasoning traces |
| `account_moves` | Pingu | Account action log |
| `account_insights` | Pingu | Account-level analysis |
| `system_signals` | Pingu | Signal feed |
| `nova_status_checks` | Nova/Pingu shared | Competition status |
| `system_learnings` | Pingu | Performance analytics |
| `mol_batch_results` | Nova | Molecular batch outputs |
| `mol_reactant_profiles` | Nova | Reactant data |
| `mol_analysis` | Nova | Analytical results |
| `mol_constraints` | Nova | Optimization constraints |
| `mol_decisions` | Nova | Agent decisions |
| `mol_scores` | Nova | Scoring data |
| `mol_findings` | Nova | Research findings |
| `findings` | Nova | Strategy/leaderboard |
| `mem0_memories` | Both | Mem0 long-term memory |
| `mem0migrations` | Both | Mem0 schema migrations |

---

## Findings

### F1: Live Crypto Trading System with Active Position Data (HIGH)

`trade_outcomes` contains real trade records with execution prices, PnL, and direction. Data is current, most recent timestamps in April 2026.

Sample record:
```json
{
  "prediction_id": "3a795fdf-...",
  "asset": "BTC",
  "direction": "long",
  "outcome": "hit_tp1",
  "pnl_pct": 0.648508,
  "reasoning": "long BTC at 77100.0",
  "timestamp": "2026-04-17T14:27:11"
}
```

`system_learnings` exposes rolling performance analytics:

> "7-day performance: 62% accuracy (10/16), avg PnL -6.0%. TP1:5 TP2:0 SL:5 expired:6. By asset: BTC: 64.3% (14 trades, avg -39.6%); SOL: 50.0% (2 trades, avg +228.7%)"

This discloses: historical win/loss rate, average PnL per asset, stop-loss frequency, and the operator's current live performance baseline, all commercially sensitive.

---

### F2: Full LLM Reasoning Traces for Trading Decisions Exposed (HIGH)

`strategy_decisions` stores multi-paragraph AI reasoning outputs for each BTC/ETH/SOL trade decision. These are not summaries, they are complete chains of thought.

Sample (condensed):
```json
{
  "asset": "BTC",
  "direction": "wait",
  "rsi": 22.9,
  "rsi_note": "deeply oversold",
  "funding_rate": "...",
  "analysis": "multi-factor analysis including RSI values, funding rates, market structure...",
  "justification": "..."
}
```

`pingu_rules` and `pingu_setups` expose the strategy ruleset and pattern library used to generate these decisions, the complete proprietary trading system logic is readable.

An adversary can reconstruct the full strategy, predict entry/exit behavior, or front-run positions.

---

### F3: Nova Molecular Optimization Competition Results Exposed (MEDIUM)

`findings` contains structured leaderboard data from an ongoing molecular optimization competition.

Sample:
```json
{
  "type": "strategy_leaderboard",
  "batch_strategies": [
    {
      "rank": 1,
      "strategy": "aldehyde_170060_exploit",
      "avg_score": 0.1115,
      "best_score": 0.1491,
      "mols": 150
    }
  ]
}
```

`nova_status_checks` reveals real-time competitive positioning:
```json
{
  "check_type": "competitive_status",
  "epochs_checked": "21553-21558",
  "our_best_ranks": {"21553": 26, "21554": 20},
  "winning_vbs": {"21553": 0.1482}
}
```

Exposure: unreleased batch results, best-performing molecular strategies, and epoch-by-epoch ranking history. A competitor with access could replicate or undercut the top-ranked strategy before submission closes.

---

### F4: Mem0 Long-Term Memory Store Fully Readable (MEDIUM)

`mem0_memories` and `mem0migrations` expose the Mem0 framework's persistent memory state for both agent systems. This includes cross-session learnings, behavioral patterns, and potentially any contextual facts the agents were instructed to remember about the operator, accounts, or targets.

---

### F5: Root Cause: Qdrant API Key Authentication Not Enabled (HIGH)

Qdrant ships with authentication disabled by default. Enabling it requires one configuration line:

```yaml
# config/config.yaml
service:
  api_key: "<strong-random-key>"
```

No firewall rule restricts port 6333 to localhost or a private CIDR. The instance is directly internet-reachable.

---

## Remediation

Enable Qdrant API key auth:

```yaml
service:
  api_key: "<strong-random-key>"
```

Firewall port 6333 to the application host only. Rotate if the system interacts with exchange APIs, Mem0 memories may contain API credentials or account identifiers ingested during agent operation.

---

## Disclosure

- **Discovered:** 2026-05-03
- **Operator:** Unknown, no domain attribution at time of writing
- **Status:** Pending operator identification; will disclose on identification
