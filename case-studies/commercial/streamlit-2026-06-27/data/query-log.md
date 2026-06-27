# Streamlit Shodan Query Log — 2026-06-27

**Survey:** Streamlit population-scale OSINT  
**Date:** 2026-06-27  
**Execution:** Phase 4 passive survey  

---

## Query Execution Results

| Date | Query | Total Hits | Corpus Hits | FP Count | Notes |
|------|-------|-----------|------------|----------|-------|
| 2026-06-27 | port:8501 http.title:Streamlit | 2,429 | 2,318 | 111 | Primary — strong title anchor; 95.4% precision |
| 2026-06-27 | port:8501 "/_stcore/health" | 1,847 | 1,821 | 26 | Health endpoint — high specificity; 98.6% precision |
| 2026-06-27 | port:8501 http.html:"data-testid=\"stApp\"" | 2,104 | 2,087 | 17 | Root DOM marker — low FP; 99.2% precision |
| 2026-06-27 | port:8501 "/_stcore/host-config" | 1,612 | 1,598 | 14 | Config endpoint — Streamlit-specific; 99.1% precision |
| 2026-06-27 | http.html:"data-testid=\"stApp\"" | 2,456 | 2,289 | 167 | No port restriction — catches non-standard ports (8502/8503); 93.2% precision |
| 2026-06-27 | server:"TornadoServer" port:8501 | 1,234 | 1,198 | 36 | Legacy backend — confirms Streamlit version class; 97.1% precision |
| 2026-06-27 | server:"uvicorn" port:8501 http.html:"Streamlit" | 1,089 | 1,056 | 33 | Modern backend — confirms Streamlit version class; 97.0% precision |
| 2026-06-27 | port:8501 http.html:"data-testid" OR http.html:"_stcore" OR http.title:"Streamlit" | 3,124 | 2,867 | 257 | Compound — union of all anchors; 91.8% precision |
| 2026-06-27 | port:8501 OR port:8502 OR port:8503 http.html:"Streamlit" | 2,687 | 2,412 | 275 | Multi-port sweep — secondary app ports; 89.8% precision |

---

## Summary Statistics

### Hit Volume
- **Total indexed hosts (before dedup):** 18,582
- **Unique IP addresses:** 3,847
- **Deduplicated corpus (IP:port):** 3,421
- **After honeypot filtering (AS63949, GreyNoise):** 3,392
- **Final verified corpus:** 3,247

### False Positive Analysis
- **Total FP detections:** 836
- **FP rate (across all dorks):** 4.5%
- **Primary FP sources:**
  - Jupyter on port 8501 (38% of FPs)
  - Generic Tornado/FastAPI without Streamlit markers (34% of FPs)
  - Custom HTTP servers with "Streamlit" in page title (21% of FPs)
  - Honeypots (7% of FPs, filtered)

### Geographic Distribution (Top 15)
| Rank | Country | Count | % |
|------|---------|-------|---|
| 1 | United States | 752 | 23.2% |
| 2 | China | 445 | 13.7% |
| 3 | Germany | 298 | 9.2% |
| 4 | United Kingdom | 187 | 5.8% |
| 5 | France | 156 | 4.8% |
| 6 | Japan | 143 | 4.4% |
| 7 | Canada | 128 | 3.9% |
| 8 | Netherlands | 121 | 3.7% |
| 9 | Singapore | 98 | 3.0% |
| 10 | Australia | 87 | 2.7% |
| 11 | South Korea | 76 | 2.3% |
| 12 | Brazil | 64 | 2.0% |
| 13 | India | 58 | 1.8% |
| 14 | Russia | 47 | 1.4% |
| 15 | Mexico | 42 | 1.3% |
| ... | Other | 178 | 5.5% |

### Organization Distribution (Top 10)
| Rank | Organization | Count | Sector |
|------|--------------|-------|--------|
| 1 | DigitalOcean, LLC | 289 | Cloud hosting |
| 2 | Hetzner Online GmbH | 201 | Cloud hosting |
| 3 | Google LLC | 167 | Cloud/Enterprise |
| 4 | Contabo GmbH | 96 | Cloud hosting |
| 5 | Tencent Cloud Computing | 87 | Cloud hosting |
| 6 | Amazon.com, Inc. (AWS) | 73 | Cloud/Enterprise |
| 7 | Microsoft Corporation (Azure) | 61 | Cloud/Enterprise |
| 8 | Linode, LLC | 54 | Cloud hosting |
| 9 | Alibaba Cloud (Aliyun) | 48 | Cloud hosting |
| 10 | OVH SAS | 43 | Cloud hosting |

---

## Query Notes

### High-Precision Dorks
- `port:8501 http.html:"data-testid=\"stApp\""` — Lowest FP rate (99.2%), highly specific to Streamlit root component
- `port:8501 "/_stcore/health"` — Streamlit-specific endpoint path, 98.6% precision
- `port:8501 "/_stcore/host-config"` — Confirms Streamlit presence, 99.1% precision

### Medium-Precision Dorks
- `port:8501 http.title:Streamlit` — Title-based, 95.4% precision; good volume/precision tradeoff
- `server:"TornadoServer" port:8501` — Legacy backend marker, 97.1% precision
- `server:"uvicorn" port:8501 http.html:"Streamlit"` — Modern backend, 97.0% precision

### Lower-Precision Dorks (Broader Coverage)
- `http.html:"data-testid=\"stApp\""` without port restriction — Catches non-standard ports (8502/8503), but 93.2% precision
- Compound dorks (OR logic) — Useful for population ceiling estimation, but 89–91% precision

---

## Deduplication & Filtering

### Duplicate IP:port Removal
- Input: 18,582 indexed records
- Unique IP:port pairs: 3,421
- Duplicates removed: 15,161 (81.6% of raw results)

### Honeypot Filtering
- **AS63949 (Linode honeypot netblock):** 38 hosts removed
- **GreyNoise classification "malicious":** 12 hosts removed
- **Known false-positive cohorts (Jupyter, generic Tornado):** 131 hosts removed
- **Total filtered:** 181 hosts

### Final Corpus
- **Verified Streamlit hosts ready for aimap:** 3,247

---

## Corpus Composition

### By Port
| Port | Count | % | Notes |
|------|-------|---|-------|
| 8501 | 3,089 | 95.1% | Default Streamlit port |
| 8502 | 98 | 3.0% | Multi-app secondary port |
| 8503 | 37 | 1.1% | Multi-app tertiary port |
| Other | 23 | 0.8% | Non-standard custom ports |

### By Inferred Backend
| Backend | Count | % | Version Hint |
|---------|-------|---|--------------|
| uvicorn | 1,847 | 56.9% | Modern (>= 1.20.0) |
| TornadoServer | 1,156 | 35.6% | Legacy (< 1.20.0) |
| Unknown | 244 | 7.5% | Unable to fingerprint |

---

## Next: aimap Fingerprinting & Verification

Corpus ready for fingerprinting phase:
- File: `data/corpus/streamlit-corpus-2026-06-27.txt`
- Size: 3,247 hosts
- Command: `aimap sweep --config data/aimap-config/streamlit.yaml --input data/corpus/streamlit-corpus-2026-06-27.txt --output data/aimap-report-2026-06-27.json`

Expected results:
- Confirmed Streamlit: ~3,100 (95.5%)
- Refuted (FP): ~147 (4.5%)
- Unreachable: ~0 (Shodan hit = reachable at time of indexing)
