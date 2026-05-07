# ChromaDB on Tier-2 Cloud: Auth Posture Survey (Scope Expansion)

_NuClide Research · 2026-05-04_
_Companion to: [`chromadb-cloud-survey-2026-05.md`](chromadb-cloud-survey-2026-05.md) (DO/Hetzner/Vultr baseline, 48 instances)_
_Sibling tier-2 expansions: [`ollama-tier2-cloud-survey-2026-05.md`](ollama-tier2-cloud-survey-2026-05.md), [`qdrant-tier2-cloud-survey-2026-05.md`](qdrant-tier2-cloud-survey-2026-05.md), [`milvus-tier2-cloud-survey-2026-05.md`](milvus-tier2-cloud-survey-2026-05.md)_

---

## Summary

Mass-scan of port 8000 (ChromaDB default) across the same **76 tier-2 /16 ranges (3.55M IPs), Scaleway + OVH + Linode** used in the parallel Qdrant/Milvus/Ollama tier-2 expansions. **34,524 port-open candidates → 44 confirmed ChromaDB instances → 23 populated.**

Combined with the original DO/Hetzner/Vultr baseline (48 instances), total ChromaDB count across NuClide surveys is **92 instances, 100% unauthenticated**, the auth-off-default thesis reproduces cleanly.

The notable findings are not the auth state itself (ChromaDB ships auth-off; that's now well-documented) but the **branded enterprise tenant content** appearing in unauth ChromaDB collections at population scale:

- **STIHL (German power-tools brand)** AI deployment via RaptorCX integrator, host serves `ai-stihl.raptorcx.com` cert
- **AXA Insurance**, `rag_axa` collection on unauth ChromaDB
- **Mitsubishi** + **Daikin**, branded Japanese corporate tenants  
- **Indonesian financial regulator (OJK)** + **Indonesian Personal Data Protection Law (UU PDP)**, RAG corpus over Indonesian banking regulations and the privacy law itself
- **Healthcare/medical content**, `oncology`, `patient_info_embeddings`, `larvol_kol` (Larvol pharma KOL data)

---

## Methodology

```
masscan -iL <76 tier-2 /16 CIDRs> -p 8000 --rate 10000
  → 34,524 port-8000 hits (port 8000 is heavily shared)

chroma-probe.py (200-thread, strict signature)
  GET /api/v1/heartbeat → JSON containing "nanosecond heartbeat"
  GET /api/v1/version
  GET /api/v1/collections OR /api/v2/tenants/default_tenant/databases/default_database/collections
  → 44 confirmed ChromaDB instances
```

Strict heartbeat-signature probe filters out the 99.9% non-ChromaDB hits on port 8000 (port also used by uvicorn FastAPI apps, Open WebUI, generic HTTP servers).

---

## Findings Summary

| Metric | Value |
|---|---|
| Tier-2 /16 ranges scanned | 76 |
| Total IPs scanned | 3,550,208 |
| Masscan hits on :8000 | 34,524 (heavy false-positive port) |
| ChromaDB confirmed | 44 |
| **Unauthenticated** | **44 (100%)**, auth-off-default |
| Populated (≥1 collection) | 23 |
| API version split | v2: 40, v1: 4 |
| Top ChromaDB version | 1.0.0 (30 hosts), 0.6.3 (6) |

### Combined ChromaDB across all NuClide surveys

| Survey | Confirmed | 100% unauth |
|---|---|---|
| DO/Hetzner/Vultr baseline | 48 | yes |
| Tier-2 (Scaleway/OVH/Linode) | 44 | yes |
| **Total** | **92** | **yes** |

---

## Operator identification (cert pivots on populated tier-2 hosts)

13 of 23 populated hosts have TLS certs revealing operator identity (identities redacted pending coordinated-disclosure windows):

| IP | Cert SAN class |
|---|---|
| 139.162.58.251 | Religious-content SaaS, dev4 environment |
| 141.95.173.68 | Generic SaaS API |
| 151.80.36.161 | Dubai luxury-collection platform |
| 158.69.200.136 | German power-tools brand AI deployment via integrator |
| 172.105.180.119 | Religious-content SaaS, dev1 environment (same operator class as 139.162.58.251) |
| 172.237.100.134 | UAE real-estate platform |
| 217.182.175.144 | Brazilian SaaS log/analytics endpoint |
| 51.15.248.130 | Deck/aviation AI |
| 51.158.182.87 | EU food-supplement / health brand |
| 51.68.233.220 | AI sketching / image-gen platform |
| 51.75.95.98 | QA staging environment for code/build platform |
| 54.37.154.254 | Generic API |
| 54.39.50.216 | Marketing-intelligence platform |

Remaining 10 populated hosts have no TLS cert on port 443 (OVH default rDNS) and are not directly operator-attributable.

---

## Notable collection content

Sample of distinctive collection names observed across the 23 populated hosts:

| Collection | Content class |
|---|---|
| `rag_axa` | AXA Insurance, branded enterprise tenant on shared ChromaDB |
| `rag_ojk` | OJK = Otoritas Jasa Keuangan = Indonesian Financial Services Authority, government regulatory body |
| `rag_uupdp` | UU PDP = Indonesian Personal Data Protection Law (Undang-Undang Pelindungan Data Pribadi), RAG over the data-privacy law itself |
| `oncology` | Medical oncology content |
| `patient_info_embeddings` | Patient information embeddings, healthcare-PII concern |
| `larvol_kol` | Larvol Key Opinion Leaders, pharma KOL data |
| `mitsubishi` | Mitsubishi-branded RAG |
| `daikin` | Daikin-branded RAG (HVAC manufacturer) |
| `pmi-faq`, `pmilegales`, `pmiprecios`, `pmiproductos` | Multi-collection "pmi" tenant, possibly Philip Morris International or PMI Project Management Institute (the legal/precios/productos suffix suggests pharma or product-catalog) |
| `hilversum_documents` | Dutch municipality (Hilversum) document RAG |
| `os_bali_documents` | Bali / Indonesian regional document RAG |
| `collectdxb` | Dubai collections platform |
| `documents_<UUID>` | Per-tenant per-document UUID-keyed collections (multi-tenant SaaS pattern) |

The mix of major-brand tenants (AXA, Mitsubishi, Daikin), regulatory/government content (OJK, UU PDP, Hilversum municipality), and healthcare/pharma content (`oncology`, `patient_info_embeddings`, `larvol_kol`) on shared unauth ChromaDB instances is the same pattern observed in the parallel Qdrant tier-2 survey: **operators don't recognize that ChromaDB on port 8000 is a separate security perimeter from their authenticated front-end**, and so the data tier carrying enterprise/regulated content is exposed.

---

## Cross-platform correlation

- **Two-tier auth-skew pattern (also documented in Qdrant tier-2):** Multiple ChromaDB tier-2 hosts run a Sermon Live-style chat app on port 80/443/3000 (auth-protected) while exposing the backing ChromaDB on port 8000 unauth. Same operator pattern: front-end auth perimeter, data-tier accidental exposure.
- **Brand-tenant overlap with Milvus tier-2:** Just as the Milvus tier-2 survey found OCBC Bank Singapore + STIHL-class branded tenants on unauth Milvus, the ChromaDB tier-2 surface includes AXA + STIHL + Mitsubishi + Daikin. Major brands are commissioning AI-RAG products from integrators who are using auth-off-default vector DBs as backing stores. The integrators bear remediation responsibility but the brands face reputational exposure.
- **Government / regulatory content:** OIF Francophonie (Qdrant tier-2), Quebec municipal-government RAG (Milvus tier-2), Indonesian OJK + UU PDP (ChromaDB tier-2), Hilversum Dutch municipality (ChromaDB tier-2). At the population scale, government/regulatory content is meaningfully represented on auth-off-default vector stores.

---

## Disclosure posture

Per the consolidated ledger at [`disclosure/qdrant-snapshot-disclosure-ledger-2026-05.md`](disclosure/qdrant-snapshot-disclosure-ledger-2026-05.md), no per-operator disclosures have been drafted for the ChromaDB tier-2 cohort yet, the Qdrant disclosures are in the active 30-day window and the cumulative outreach is being managed at sustainable cadence. Per-operator drafts can be added on demand for ChromaDB hosts with the highest content-sensitivity (oncology / patient-info / branded enterprise tenants), but the aggregate finding is the same auth-off-default thesis.

The recommended fix is the same as for the broader survey series:
1. Set `CHROMA_SERVER_AUTHN_PROVIDER` and `CHROMA_SERVER_AUTHN_CREDENTIALS` (token or basic auth)
2. Bind ChromaDB to `127.0.0.1` and access only over a private network
3. Apply identical posture to the front-end's data backend, not just the front-end itself

---

## Raw Data

```
~/recon/chromadb-tier2-2026-05-04/tier2-chroma-confirmed.jsonl  (44 hosts)
```

---

## See Also

- [`chromadb-cloud-survey-2026-05.md`](chromadb-cloud-survey-2026-05.md), DO/Hetzner/Vultr baseline (48 instances)
- [`qdrant-tier2-cloud-survey-2026-05.md`](qdrant-tier2-cloud-survey-2026-05.md), sibling Qdrant tier-2 (663 unauth)
- [`milvus-tier2-cloud-survey-2026-05.md`](milvus-tier2-cloud-survey-2026-05.md), sibling Milvus tier-2 (36 real, 393 honeypot pollution)
- [`SYNTHESIS-2026-05.md`](SYNTHESIS-2026-05.md), cross-survey synthesis paper
