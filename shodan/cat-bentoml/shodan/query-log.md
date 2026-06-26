# BentoML Shodan Query Log — cat-bentoml
Date: 2026-06-26

| dork | hits | notes |
| ---- | ---- | ----- |
| `"Server: BentoML Service"` | 0 | Server header not in html body — route to Censys |
| `http.title:"BentoML Inference Service"` | 0 | New title format (v1.x) not indexed or very rare |
| `http.title:"BentoML Prediction Service"` | 70 | **BEST HIT** — legacy title (pre-v1.0), bulk of population |
| `"Server: BentoML Service" http.html:"x-bentoml-name"` | 0 | Conjunctive; both fail in html body |
| `http.html:"BentoMLUI.mount"` | 0 | JS bundle content — not captured in html body |
| `http.html:"x-bentoml-name"` | 0 | JSON response field — route to Censys |
| `port:3000 http.html:"BentoML"` | 17 | Broad port+string; lower precision but additive |
| `"BentoML"` | 2 | Generic fulltext; minimal additive value |

## Observations
- Population skewed to legacy title "BentoML Prediction Service" — operators running old builds
- Server header + JSON response dorks (0 hits) are expected: Shodan web UI html body only captures HTML, not headers/JSON
- Route `"Server: BentoML Service"` and `x-bentoml-name` signals to Step 0b Censys
- 57 unique IPs harvested; 9 appear in 2+ dorks (higher confidence)

## Variant dorks (null_result_handler output, run after zero hits)
| dork | hits | notes |
| ---- | ---- | ----- |
| `http.html:"BentoML Inference Service"` | 0 | HTML body still misses it |
| `http.html:"Server: BentoML Service" port:3000` | 0 | Header not in html body, as expected |
| `ssl.cert.subject.cn:"bentoml"` | 38 | **NEW** — cert-CN pivot; 10 additive IPs; likely *.bentoml.ai SaaS certs |
| `http.html:"contact@bentoml.com"` | 0 | JSON response field, not HTML |
| `http.html:"x-bentoml-request-id"` | 0 | Response header, not HTML body |

## Final Shodan Harvest
- 57 IPs from HTML-body dorks
- +10 from cert-CN variant (ssl.cert.subject.cn:"bentoml")
- **Total: 67 IPs in ips-raw.txt**
- Imported to empire.db via jaxen --no-lookup
