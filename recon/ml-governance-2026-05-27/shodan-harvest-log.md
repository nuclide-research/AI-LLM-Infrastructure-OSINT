# ML Governance Shodan Harvest — 2026-05-27
**Method:** Playwright authenticated web scraping (page.evaluate + direct URL navigation)
**Date:** 2026-05-27
**Pages scraped per query:** 1-3 (up to 30 results/page)

| Query | Total Hits | IPs Collected | Port |
|-------|------------|---------------|------|
| `http.title:"OpenMetadata" port:8585` | 55 | 30 | 8585 |
| `http.html:"open-metadata" port:8585` | 0 | 0 | 8585 |
| `http.html:"openmetadata" port:8080` | 1 | 1 | 8080 |
| `http.title:"DataHub" port:9002` | 25 | 25 | 9002 |
| `http.html:"datahubproject" port:9002` | 0 | 0 | 9002 |
| `port:21000 http.title:"Atlas"` | 0 | 0 | 21000 |
| `port:21000 http.html:"Apache Atlas"` | 0 | 0 | 21000 |
| `http.html:"marquezproject" port:5000` | 0 | 0 | 5000 |
| `http.html:"amundsen" port:5001` | 0 | 0 | 5001 |
| `http.html:"registered-models" port:5000` | 0 | 0 | 5000 |
| `http.html:"/api/3/action" http.html:"ckan"` | 4 | 2 | 80/443 |
| `port:8585 http.html:"openmetadata"` | 56 | 30 | 8585 |

**Notes:**
- Q1 and Q12 are near-identical OpenMetadata dorks (title vs html). Q12 yielded 1 additional IP (34.56.227.179). Combined dedup: 31 unique IPs at 8585.
- Q4 and Q1 share one IP: 103.166.182.206 (listed at both ports — likely dual-service host).
- Q11 (CKAN) returned 4 hits across 2 IPs at ports 80 and 443. No port filter was applied; recorded as :80.
- Atlas (Q6/Q7), Marquez (Q8), Amundsen (Q9), MLflow registered-models (Q10), DataHub html (Q5) all returned zero — either not indexed or require different dorks.
- Apache Atlas port 21000 zero hits suggests the default port is not widely exposed or Shodan hasn't indexed it.

**Total unique IP:port pairs:** 59
- OpenMetadata (8585): 31
- OpenMetadata (8080): 1
- DataHub (9002): 25
- CKAN (80): 2
