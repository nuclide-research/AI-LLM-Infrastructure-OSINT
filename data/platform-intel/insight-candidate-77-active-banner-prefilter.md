# Candidate Insight #77 — active-banner scan is the liveness/version/FP-strip bridge

**Source:** Cat-02 Vector DB virgin re-birth, scanner pass 2026-06-05 (PoC in
`github.com/nuclide-research/scanner` → `results/poc-cat02-vectordb-2026-06-05.md`).

**Claim:** between passive discovery (Shodan/Censys) and deep enumeration (aimap), an active
TCP/TLS banner scan is not optional polish — it does three load-bearing things in one cheap pass that
are otherwise missing or done expensively at the deep-enum stage:

1. **Liveness.** Shodan returns *cached* candidates. On this corpus, 3,362 harvested IPs → **965 live
   (29%)**. Running aimap on the raw list wastes ~70% of effort on dead/stale hosts. The active
   handshake is what converts "Shodan saw this once" into "up right now."
2. **Fresh version.** Banner-at-scan-time (Qdrant 1.13.4–1.17.1 observed) is what scopes
   version-bounded CVEs; Shodan's cached version drifts.
3. **Dork-FP strip at the banner layer.** 122 of the harvested hosts (114 nginx + 8 Cloudflare) were
   dork false positives (the ~50% rule, Insight #15) — caught for the price of a TCP connect, before
   aimap spends a deep probe. Plus 63 auth-401 gated hosts pre-flagged.
4. **(bonus) Shadow-port discovery.** Same pass surfaced ~550 IP-direct-shadow exposures (Insight #12):
   240 Attu/Grafana, 170 MinIO, 63 Prometheus, 55 Docker-registry, 21 etcd — the stacked-exposure tier.

**Division of labor:** scanner = **wide + shallow** (liveness, version, FP-strip, port discovery across
many IPs/ports); aimap = **narrow + deep** (protocol enumeration, vector-use confirmation) on the clean
subset. Scanner-after-Shodan makes aimap both cheaper and more accurate.

**Corollary — banner ≠ use (ties to Insight #16).** The scanner (like Shodan) sees the connection
banner, not the database schema. It cannot confirm vector-use for a general DB (Redis/Mongo/ClickHouse)
— that needs aimap's protocol read (FT._LIST, SHOW INDEXES, _mapping). Active banner gets you to
"live + version + product"; only deep enum gets you to "vector-confirmed."

**Pipeline (standing):** `passive discovery → active banner (liveness+version+FP-strip) → deep enum`.
The active-banner step runs on every harvest; it is not skippable. Chain position = Step 0c.
