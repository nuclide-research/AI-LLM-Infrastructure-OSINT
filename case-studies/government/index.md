# Government AI Infrastructure Exposures

_NuClide Research — ongoing · Updated 2026-05-02_

Unauthenticated Ollama instances discovered on government networks. Identified via hostname TLD filtering (`.gov`, `.go.id`, `.gov.br`, `.gov.tw`, `.mil`, etc.).

---

## Structure

- `US/` — United States federal and state government
- `international/CC/` — all other countries, grouped by ISO country code

---

## Discovery Method

Primary signal: Shodan `port:11434 hostname:".<tld>"` across 25 government TLD patterns.
Unlike university sweeps (which use `org:university`), government nodes often don't self-identify by org name — hostname TLD filtering is more reliable.

```bash
python3 data/ollama-recon.py --government --vpn-country id   # Indonesia focus
python3 data/ollama-recon.py --government --rotate-every 5   # rotate VPN every 5 probes
```

---

## Confirmed Findings

| File | Organization | Country/Tier | Severity | Key Finding |
|------|--------------|--------------|----------|-------------|
| [aws-govcloud.md](US/aws-govcloud.md) | AWS GovCloud (us-gov-east-1) | US Federal | CRITICAL | 10 models, DeepSeek + MiniMax cloud proxy, JOSIE custom AI persona, CVE-2025-63389 |
| [indonesia-cluster.md](international/ID/indonesia-cluster.md) | Indonesia Government Cluster | Indonesia | CRITICAL | 5 nodes: 2 account takeovers, RAG pipeline on ICT ministry, Claude-distilled model on provincial server |
| [kominfo-jateng.md](international/ID/kominfo-jateng.md) | Dinas Kominfo Prov. Jawa Tengah | Indonesia · Central Java | CRITICAL | Account takeover (name=da298cd9ca86), BGE-M3 RAG pipeline, sijoli gov system |
| [kaltara-province.md](international/ID/kaltara-province.md) | Pemerintah Provinsi Kalimantan Utara | Indonesia · N. Kalimantan | CRITICAL | Account takeover (name=7a3686b3df54), Claude 4.6 Opus distilled model, tool-calling model |

---

## Scale (sampled 2026-05-02)

| TLD | Gov Entity | Hits |
|-----|-----------|------|
| `.gov` (via hostname) | US federal + false positives | 14 raw / 6 GovCloud actual |
| `.go.id` | Indonesia government | 7 |
| `.gov.br` | Brazil government | 4 |
| `.gov.tw` | Taiwan Government Service Network | 3 |
| `.mil` | False positives (CANTV Venezuela) | 2 |
| Others | 1 each: MX, JP, IN | 3 |

---

## SOP

1. **Density scan** — `shodan count` across all TLD patterns to find where nodes cluster
2. **Connect Mullvad** — geo-appropriate exit node (`--vpn-country <cc>`)
3. **Probe** — `--government --vpn-guard [--rotate-every N]`
4. **Triage** — takeovers first, then cloud proxies, then plain unauth
5. **Write case study** — per-node if notable, cluster file if same country/org
6. **Disclose** — national CERT (ID-CERT, US-CERT/CISA) + agency contact
