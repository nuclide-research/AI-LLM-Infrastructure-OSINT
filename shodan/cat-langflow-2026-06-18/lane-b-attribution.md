# CAT-LANGFLOW 2026-06-18 — Lane B: Fleet Attribution

Passive infrastructure characterization of the 93-host scanner-poisoning deception fleet
surfaced by `http.title:"Langflow"`. All work passive: rDNS (`dig -x`), `whois`, Team Cymru
DNS ASN zone, and analysis of already-captured evidence. No host in the fleet was actively probed.

## Method

- Full population: 93 IPs from `harvest-raw.txt`.
- Per-IP ASN/country via Team Cymru `origin.asn.cymru.com` TXT zone (passive; queries Cymru, not targets).
- rDNS PTR via `dig -x` against 8.8.8.8 for all 93.
- `whois` registrant/netname on a 30-IP spread sample.
- Cross-host payload-identity confirmed from `deep-collect.json` (35 hosts) and the evidence files.

## ASN / Org / Country distribution (full 93)

| ASN | Operator | Hosts | Geo placement (true) |
|-----|----------|------:|----------------------|
| AS16509 | AMAZON-02 (AWS EC2) | 27 | 18 AWS regions, 6 continents (sa-east-1 x3, us-west-2 x2, eu-west-1/2/3, eu-south-1/2, eu-north-1, eu-central-1, ca-west-1, ap-southeast-1/2/3, ap-south-1 x2, ap-northeast-1/2/3, ap-east-1) |
| AS63949 | AKAMAI-LINODE-AP (Linode / Akamai Connected Cloud) | 27 | US x26, NL x1 (region-tagged linodeusercontent PTRs) |
| AS37963 | ALIBABA-CN-NET (Aliyun, Hangzhou) | 19 | CN x14, SG x5 |
| AS45102 | ALIBABA-CN-NET (Alibaba US/intl) | 17 | SG x9, US x8 |
| AS20845 | DIGICABLE (DIGI Hungary, residential cable) | 1 | HU |
| AS200999 | pl-cloudferro (CloudFerro) | 1 | PL |
| AS14618 | AMAZON-AES (AWS) | 1 | US |

Registry-country rollup: US 62, SG 14, CN 14, PL 1, NL 1, HU 1.
(US count is inflated by ARIN registrant-HQ; AWS PTRs prove the real footprint is global, see below.)

### Concentration math
- **4 ASNs carry 90 of 93 hosts (96.8%):** AWS 28 (16509+14618), Linode 27, Aliyun 36 (37963+45102).
- Three hyperscalers, near-even thirds: AWS ~30%, Linode ~29%, Alibaba ~39%.
- Tail: 3 hosts on three unrelated small networks (DIGI HU residential, CloudFerro PL, +1 AWS AES).

## Geographic dispersion (the tell)

The 27 AWS hosts are spread across **18 distinct AWS regions on 6 continents**. No clustering in
one or two regions. A single operator standing up 27 boxes does not scatter them across ap-east-1,
sa-east-1, ca-west-1, eu-north-1 and eu-south-2 simultaneously, that pattern is what you get when
the *same image/container* is launched by *many different tenants* who each defaulted to their own
home region. Aliyun splits CN/SG, Linode splits US/NL, same story.

## Notable rDNS

- **No operator hostnames leak.** Across all 93 hosts, exactly **one** PTR is non-hyperscaler:
  `176.241.17.222 -> 176-241-17-222.pool.digikabel.hu` (DIGI Hungary residential cable pool).
- No v2board panel hostnames, no Tor-exit PTRs, no SNI/CN leakage via rDNS.
- Every other PTR is generic provider boilerplate: `ec2-*.<region>.compute.amazonaws.com`,
  `*.ip.linodeusercontent.com`, or NXDOMAIN (Aliyun hosts carry no PTR).
- `185.3.95.212` and `185.254.220.241` initially looked like bulletproof-range outliers; `185.3.95.212`
  is in fact Linode (`*.linodeusercontent.com`), and `185.254.220.241` is CloudFerro PL with no PTR.
  Neither is an operator-attributable foothold.

## Verdict: DEPLOYED PRODUCT, not one operator

The infrastructure spread refutes single-operator. Evidence:

1. **Disjoint ownership.** 90 hosts split near-evenly across three competing, unrelated hyperscalers
   (AWS / Linode / Alibaba). One operator does not buy in even thirds from three rival clouds.
2. **Globally scattered placement.** 18 AWS regions across 6 continents; CN+SG on Aliyun; US+NL on
   Linode. This is per-tenant default-region behavior, not one operator's deliberate footprint.
3. **Byte-identical bait across all of them.** `deep-collect.json` shows 35 distinct hosts on 35
   distinct IPs all returning the same fabricated `10.0.1+gitea-1.22.0` version, the same
   `in_cluster:true`, the same 200-on-every-endpoint signature. The dedicated evidence files
   (`fake-version-json.txt`, `fake-autologin-jwt.txt`) show the same canned commit and the same
   fabricated "jack" JWT reproduced verbatim host-to-host. Disjoint owners + identical artifact = a
   shared software product, deployed by many parties, **not** a coordinated fleet under one hand.
4. **No shared operator fingerprint in the network layer.** No common netblock, no shared registrant,
   no operator PTR, no shared TLS CN surfacing in rDNS. Nothing ties the hosts together except the
   payload itself.

This is the signature of a **honeypot / deception appliance** (the canned page self-titles "LBot")
distributed as a container or image that anyone can run. Each install lands in whatever cloud and
region its operator already uses. The "fleet" is an emergent population of independent installs of
one deception product, not a botnet or a single actor's spread.

## What the spread implies

- **Attribution is intentionally null.** The product leaks no operator identity at the infra layer.
  Pursuing a single owner is the wrong frame; the right unit is the *software distribution*.
- **The poisoning works precisely because the population is disjoint.** A scanner sees 54k+
  "Langflow" titles across every major cloud and reads it as a huge real population. The diversity of
  hosting *is the camouflage*, it makes the fake cohort look organically distributed.
- **Pivot, if pursued (read-only):** fingerprint the product by its invariant payload bytes (the
  fixed gitea commit, the "jack" JWT, the v2board `umi.js` theme path, the "LBot" title) and treat any
  future host matching that byte-signature as the same product, regardless of ASN. The byte-signature
  is the only durable identifier; ASN/geo are noise by design.
