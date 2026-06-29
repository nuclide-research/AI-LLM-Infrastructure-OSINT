# Cat-16 Redash Setup-Wizard Candidates (claimable admin)

Date: 2026-06-28. Source: Shodan `http.title:"Redash Initial Setup"` (20 hits) -> live httpx read.
CSP-confirmed = carries `frame-src redash.io` (squad strict fingerprint). Status CANDIDATE.
Finding: exposed `/setup` lets an unauthenticated visitor create the first admin = instance takeover.
RESTRAINT: page-render is the finding. Verify lane GETs `/setup` to confirm form renders. NEVER POSTs.

## CSP-confirmed live setup hosts: 14

- http://13.114.94.90:80  (302 -> setup flow, redash CSP present)
- http://141.98.199.66:5000  (302 -> setup flow, redash CSP present)
- http://147.139.174.41:5000  (302 -> setup flow, redash CSP present)
- http://151.106.41.4:5000  (302 -> setup flow, redash CSP present)
- http://18.169.167.31:80  (302 -> setup flow, redash CSP present)
- http://34.146.65.22:5000  (302 -> setup flow, redash CSP present)
- http://34.34.217.74:5000  (302 -> setup flow, redash CSP present)
- http://35.76.81.200:80  (302 -> setup flow, redash CSP present)
- http://35.78.223.69:80  (302 -> setup flow, redash CSP present)
- http://54.175.242.57:80  (302 -> setup flow, redash CSP present)
- https://13.159.122.214:443  (302 -> setup flow, redash CSP present)
- https://18.176.25.64:443  (302 -> setup flow, redash CSP present)
- https://35.74.226.223:443  (302 -> setup flow, redash CSP present)
- https://54.210.52.34:443  (302 -> setup flow, redash CSP present)

## False positives stripped at banner layer: 4

- http://34.34.217.74:80  'Apache2 Ubuntu Default Page: It works'  (no redash CSP = not Redash)
- http://34.34.217.74:80  'Apache2 Ubuntu Default Page: It works'  (no redash CSP = not Redash)
- https://13.115.223.155:443  'Index | mxHero & Box Link Manager'  (no redash CSP = not Redash)
- https://13.115.223.155:443  'Index | mxHero & Box Link Manager'  (no redash CSP = not Redash)
