# Cat-16 BI/Dashboards — Scan Summary (Step 0c)

Date: 2026-06-28. Input: 3,325 harvested IPs. naabu connect-scan + httpx body-capture.

## Liveness
- 2,723 / 3,325 hosts live (82%) — beats ~29% Shodan-cache baseline (local-dump seeds fresher)
- 7,129 open IP:port pairs; 6,825 banners read with body

## Fingerprint-confirmed clean-live (vendor-unique body/header signal)
| Platform  | Confirmed hosts | Signal                          |
|-----------|-----------------|---------------------------------|
| Redash    | 1,051           | CSP `frame-src redash.io`       |
| Superset  | 612             | body `data-bootstrap` / version |
| Metabase  | 131             | `metabase.SESSION` / Bootstrap  |
| Lightdash | 0               | none found (Insight #40 holds)  |
| unmatched | 57%             | catch-all/decoy/proxy (FP rule) |

## Candidate findings (CANDIDATE — verify lane confirms; restraint observed)
| Finding                                    | Count | Severity | Notes |
|--------------------------------------------|-------|----------|-------|
| Metabase setup-token (CVE-2023-38646 RCE)  | 126   | CRITICAL?| pre-auth RCE candidate; 96% of confirmed MB. VERIFY version range + token, do NOT fire payload |
| Redash setup-wizard (claimable admin)      | 21    | HIGH     | exposed /setup = first-admin claim; do NOT POST |

## Lightdash = 0 (thesis-confirming negative)
Newest, most-hardened BI tool: zero exposed instances in population. Confirms Insight #40
rightward auth-shift across the BI category. Superset(admin/admin) > Redash(login-wall) > Lightdash(locked).

## Measurement note
First banner pass used -irh (headers only): under-counted body-signal platforms (Superset showed 3,
true 612). Re-ran with -irr (body) + -fr (follow-redirect). Header-only is invalid for Superset/Lightdash.
