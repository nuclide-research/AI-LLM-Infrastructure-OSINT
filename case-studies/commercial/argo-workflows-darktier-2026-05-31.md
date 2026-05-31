# Dark-Tier Probe Result (Option A) — 2026-05-31

## Premise (overturned)
Option A assumed Shodan's 355 `port:2746` hosts were a harvestable Argo population
that body-dorks missed. Harvested 193 (web UI caps at 200 results / 20 pages without
query credits; "Result limit reached" at page 21).

## Result: 193/193 no application response
Direct probe of all 193 on :2746 → 0 Argo-confirmed, 0 unauth, 0 auth-enforced,
193 no-response.

## Root cause (diagnosed, not assumed)
- TCP layer: SYN-ACK completes on a fraction (bash /dev/tcp sees "open" on some).
- Application layer: every protocol (HTTPS, HTTP/1.1, h2c prior-knowledge) returns
  HTTP 000. openssl s_client gets SSL_ERROR_SYSCALL immediately after ClientHello.
- The hosts RST the connection as soon as the client sends application bytes.
- Confirmed NOT a vantage artifact: re-tested from Mullvad US (Kansas City) AND
  Sweden (Malmo) exits — identical SSL_ERROR_SYSCALL both times.
- Confirmed NOT a sandbox egress block: portquiz.net:2746 returns HTTP 200 from
  the same environment (non-standard port egress works).

## Conclusion
Shodan's `port:2746` + "no data returned" tier is NOT the E.V.A unauth population.
Shodan recorded only a SYN-ACK; it never pulled a banner — for the same reason our
probe can't: these hosts reset application-layer connections from external clients.
They are neither confirmed-Argo nor externally probeable from a normal vantage.
This is connection-level filtering (scrubbing middlebox / source-whitelist firewall /
tarpit), heavy on Alibaba (8.x/47.x/120.x) and Tencent (43.x) cloud ranges.

The E.V.A Nov-2024 ~3000 unauth count therefore came from hosts that answered the
application layer for E.V.A — either hosts Shodan undersamples, or the 443-fronted
tier (which our ssl-dork DID reach: all 33 auth-walled). Reaching a true unauth
population would require masscan with full-handshake banner-grab (not SYN-scan) from
a non-filtered vantage, then application probe — and even then, the RST behavior may
hold from any single vantage.
