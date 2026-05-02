# Indonesia Government Cluster — 5-Node Survey, 2 Account Takeovers

_NuClide Research · 2026-05-02_

---

## Summary

Five Indonesian government Ollama nodes confirmed live across `.go.id` infrastructure. Two provincial government nodes have live Ollama Connect account takeover URLs. The cluster spans national, provincial, and regency tiers of Indonesian government.

---

## Node Inventory

| IP | Hostname | Organization | Version | Tier | Tags |
|---|---|---|---|---|---|
| 103.107.245.11 | sijoli-11-245-107.jatengprov.go.id | Dinas Kominfo Prov. Jawa Tengah | 0.13.2 | Provincial (ICT dept) | CLOUD · **TAKEOVER** · RAG |
| 103.156.110.80 | ip-103-156-110-80.kaltaraprov.go.id | Pemerintah Provinsi Kalimantan Utara | 0.13.4 | Provincial | CLOUD · **TAKEOVER** · Claude-distilled |
| 103.136.182.113 | tpposyandu.banjarkab.go.id | Pemerintah Kabupaten Banjar | 0.21.0 | Regency | CLOUD |
| 103.123.25.197 | mail.kalteng.go.id | Pemerintah Provinsi Kalimantan Tengah | 0.9.2 | Provincial | mail server |
| 103.55.254.253 | kemkes.go.id | Departemen Kesehatan | — | National (Health Ministry) | offline at probe time |

---

## Account Takeovers

| IP | Username | SSH Pubkey |
|---|---|---|
| 103.107.245.11 | `da298cd9ca86` | `ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIEd19vXJ586h1nPgxSuRVifj6XAtuBnfdKO6H7fN2V7c` |
| 103.156.110.80 | `7a3686b3df54` | `ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAILmUNnGe5hcVp/9f8nTolAN49G+s1RbNMN5uYm1Zfc8y` |

Both usernames are MAC addresses / container IDs — automated or containerized deployments with no account customization.

---

## Notable Findings

**Kominfo Jateng (103.107.245.11):** RAG pipeline confirmed (BGE-M3 multilingual embedder + Qwen3:14b). The hostname `sijoli` likely corresponds to an internal government information system. Document retrieval over an unauthenticated, injectable endpoint on provincial ICT infrastructure.

**Kalimantan Utara (103.156.110.80):** `Qwen3.5-27B-Claude-4.6-Opus-Reasoning-Distilled` — a Claude 4.6 Opus knowledge-distilled local model on a provincial government server. Tool-calling model (`gemma3-it-qat-tools:27b`) also present.

**Banjar Regency (103.136.182.113):** Posyandu health monitoring system (`tpposyandu`) running DeepSeek V4 Pro cloud proxy. Posyandu = Indonesian integrated health post network. AI on a national health data collection system.

**Central Kalimantan (103.123.25.197):** `mail.kalteng.go.id` — the provincial mail server hostname running Ollama v0.9.2 (very old). deepseek-r1:1.5b + llama3.2:3b on what should be a mail relay.

---

## Remediation

```bash
OLLAMA_HOST=127.0.0.1:11434
systemctl restart ollama
```

Block TCP 11434 at the government network perimeter.

---

## Disclosure

- **Discovered:** 2026-05-02
- **Status:** Pending — ID-CERT (idcert.id) and individual agency Kominfo contacts
- **Priority:** CRITICAL (active account takeovers, government ICT infrastructure)
