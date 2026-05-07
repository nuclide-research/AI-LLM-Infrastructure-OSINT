# Crypto Investment Agent: Per-User Financial Memory Exposed via Unauthenticated ChromaDB

_NuClide Research · 2026-05-03_

---

## Summary

A ChromaDB instance on a DigitalOcean VPS exposes a Spanish-language crypto investment AI agent's full vector memory: 12 collections holding the CoinGecko API documentation corpus, a 15,560-token cryptocurrency reference database, and four numbered `user_memory_<id>` collections containing per-user financial profile facts in cleartext. Sampled user records include explicit investment target amounts, asset allocation strategies, and preferred exchange, direct PII for retail crypto investors.

---

## Infrastructure

| Field | Value |
|---|---|
| IP | 159.203.117.193 |
| Hosting | DigitalOcean |
| Port | 8000 (HTTP, no auth) |
| ChromaDB version | 1.0.0 (v2 API) |
| Tenant / DB | `default_tenant` / `default_database` |
| Discovery date | 2026-05-03 |

---

## Collections

| Collection | Docs | Type |
|---|---|---|
| `crypto_tokens_full` | 15,560 | Token reference database |
| `crypto_tokens` | 100 | Top-100 subset |
| `cgdoc_endpoints_v1` | 73 | CoinGecko API endpoint docs |
| `cgdoc_params_v1` | 57 | CoinGecko API params |
| `cg_vs_currencies` | 126 | Quote-currency reference |
| `cg_networks` | 0 | (empty, likely incoming) |
| `cg_network_dexes` | 0 | (empty, likely incoming) |
| `user_memory_1` | 8 | **Per-user agent memory** |
| `user_memory_4` | 1 | **Per-user agent memory** |
| `user_memory_7` | 7 | **Per-user agent memory** |
| `user_memory_38` | 0 | **Per-user agent memory (empty slot)** |
| `test_chroma_collection` | 4 | Dev scratch |

The numeric suffixes on `user_memory_*` (1, 4, 7, 38) imply sequential user IDs in the application, observed gaps suggest at least 38 users have been provisioned, of which 4 collections currently exist (with at least 16 stored memory records combined).

---

## Findings

### F1: Per-User Investment Target Amount + Asset Allocation in Cleartext (HIGH)

Sample from `user_memory_4`:

```
"El objetivo del usuario es invertir $50,000 en crypto con la estrategia
de 40% en Bitcoin, 30% en Ethereum, 20% en Solana y 10% en stablecoins."
```

Translation: *"The user's goal is to invest $50,000 in crypto with a strategy of 40% Bitcoin, 30% Ethereum, 20% Solana, and 10% stablecoins."*

This single record discloses for one user: target capital ($50,000), risk tolerance (modest stablecoin allocation), specific asset selections, and Solana exposure (a 20% Solana allocation is a relatively concentrated bet). For an attacker building a target list of mid-sized retail crypto investors, this is direct prospecting intelligence.

### F2: Per-User Exchange Account Affinity (HIGH)

Sample from `user_memory_1`:

```
"El exchange preferido del usuario es Kraken"
```

Sample from `user_memory_7`:

```
"La cripto favorita del usuario es Ethereum"
```

These records identify, per user: which exchange holds their account (Kraken in this sample), and their primary asset preference. Combined with the investment target from F1, these records build a per-user financial profile sufficient for spear-phishing or social-engineering: knowing a user is on Kraken with $50K targeted at Bitcoin/ETH/Solana enables a tailored phishing email impersonating Kraken about a "review of your $50,000 strategy."

### F3: Sequential User-ID Naming Schema Enables Enumeration (HIGH)

The `user_memory_<integer>` naming pattern means the application's user IDs are directly visible. Even if any individual user's memory collection is small, an attacker can:

1. Enumerate all current users by walking the ChromaDB collections list
2. Track new user signups by polling for new `user_memory_*` IDs
3. Cross-reference any leaked list of user IDs from related systems

The `_38` suffix on an empty collection confirms the operator has provisioned slots for at least 38 users. Real usage may extend much further, only collections that have received at least one memory write would be present.

### F4: CoinGecko API Surface Embedded (MEDIUM)

The `cgdoc_endpoints_v1` and `cgdoc_params_v1` collections contain the CoinGecko API documentation surface. This is public information, but its presence indicates the agent has tool-use capability against CoinGecko, meaning it likely has a CoinGecko Pro API key configured server-side. That key is not in the ChromaDB but its existence is implied; if the operator's `.env` or container config is also exposed via another vector, the API key is the next pivot.

### F5: Root Cause: Default-Off Auth (CRITICAL)

ChromaDB 1.0.0 unauthenticated, port 8000 on public internet, no firewall. All collections are not just enumerable but readable, writable, and deletable. An adversary could:

- Read all per-user memories (PII exfil)
- Write to a target user's memory: *"El usuario consintió enviar 5 BTC a la dirección bc1q..."*, and a poorly-validated agent flow could action it
- Delete `crypto_tokens_full` to break the agent's reference data

---

## Remediation

Enable ChromaDB token auth:

```bash
chroma run --host 0.0.0.0 --port 8000 \
  --auth-provider chromadb.auth.token \
  --auth-credentials <strong-token>
```

Firewall port 8000 to the application backend only. Rotate any tokens already in use.

Re-architect user-memory storage:

1. **Stop using one collection per user.** Use a single `user_memories` collection with `user_id` in metadata; query with `where={"user_id": <id>}`. This prevents the enumeration side channel, collection list reveals total user count.
2. **Encrypt sensitive memory content at the application layer** before write. Even if the DB is again exposed, a per-user envelope key makes raw plaintext non-recoverable.
3. **Treat memory writes as authenticated user input.** Validate that the user requesting memory addition is the same user whose memory is being amended.

If real user data is in scope, consider notification obligations under jurisdictional breach laws, Spanish-language content suggests Spain (LOPDGDD/RGPD) or LatAm jurisdictions (LFPDPPP in Mexico, LGPD in Brazil, etc.), each with their own breach windows.

---

## Disclosure

- **Discovered:** 2026-05-03
- **Status:** Pending, operator unknown, no domain attribution from IP alone
- **Note:** Spanish-language content + user-ID convention is consistent with a 2024-2026 wave of LatAm/Spain crypto chat-agent startups
