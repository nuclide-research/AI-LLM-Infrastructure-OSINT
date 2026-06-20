---
type: insight
id: 100
slug: brown-2018-to-2026-delta-as-insight-40-evidence
date-drafted: 2026-06-09
status: stub-pending-data
survey: cat-x-ros-2026-06-09
lane: D
parents: [40, 99]
depends-on-data-from: A
---

# Insight #100 (STUB, PENDING DATA) — Brown 2018 to 2026 delta is the Insight #40 evidence point for ROS

**Status:** STUB drafted pre-data by Lane D during Cat-X-ROS Robotics survey 2026-06-09. The Insight cannot be confirmed or refuted until Lane A's harvest completes and the 2026 rosmaster + rosbridge populations are measured. This stub stages the analysis framework so the Insight is publishable the moment the data lands.

## Claim (conditional)

Brown et al. 2018 (arxiv:1808.03322, ICRA 2019) "Hijacking robots from anywhere" performed IPv4 scans Dec 2017 to Jan 2018 and recorded:

- **100+ rosmaster instances per scan**
- **28 countries**
- **70%+ on .edu / research networks**
- Demonstrated POC takeover with consent (read camera, move robot).

Cat-X-ROS 2026 is the 8-year follow-up. The delta between the 2018 baseline and the 2026 measured population is the Insight #40 evidence point for ROS specifically. Three outcomes are possible:

### Outcome A — Population MATERIALLY DOWN + cohort shifted toward commercial
Interpretation: operator-side mitigation pressure is working. Universities pulled rosmaster off the public internet (CISO awareness, network segregation, VPN deployment) but the LAN-architected protocol default remains open — confirming Insight #99's routing rule. This is the *operator-hygiene migration* prediction. Insight #40 CONFIRMED via the operator-deployment-hygiene mechanism, not the protocol-default-shift mechanism.

### Outcome B — Population MATERIALLY UP or unchanged
Interpretation: the population growth of robotics (commercial AMR / AGV / agricultural / drone) has outrun the operator-hygiene migration on universities. Net 2026 number masks an internal cohort shift. Insight #40 thesis REFUTED for LAN-architected protocols if no compensating operator-hygiene migration is detectable.

### Outcome C — Population UNCHANGED but cohort identical (still 70%+ .edu)
Interpretation: 8 years of disclosure pressure produced no change. Strongest refutation of Insight #40 for LAN-architected protocols and confirmation of Insight #99's routing rule's predictive value (the routing rule predicted in advance that no shift was expected on this class).

## Required data (Lane A dependency)

- 2026 rosmaster count from Stage 0 Shodan + Stage 0b Censys cross-pop. Censys is load-bearing here because Brown 2018 used active IPv4 scans which detect 11311 directly; Shodan's 11311 coverage is spotty, Censys via SSH banner cross-pop is the compensating measurement.
- 2026 rosbridge_server count from Stage 0 Shodan (`http.title:"Tabby"`-equivalent unconstrained dork).
- WHOIS classification of confirmed rosmaster hosts:
  - `.edu` / research network percentage
  - commercial robotics vendor percentage
  - cloud-relay (operator forwarding from LAN) percentage
  - residential / unattributable percentage
- Country distribution of confirmed rosmaster hosts.
- Operator-attribution markers from Stage 3v verify (topic names that signal sector: warehouse, surgical, agricultural, drone).

## Analysis framework (apply post-Lane-A)

```
Let N_2026 = measured 2026 rosmaster count from Stage 0+0b.
Let R_edu_2026 = fraction of N_2026 on .edu / research networks.
Let R_commercial_2026 = fraction on commercial robotics vendor or operator networks.
Let C_2026 = number of unique countries.

Baseline (Brown 2018):
  N_2018 = 100 (approximate, per-scan)
  R_edu_2018 = 0.70+
  C_2018 = 28

Decision:
  if N_2026 / N_2018 < 0.5 and R_commercial_2026 > R_commercial_2018-equivalent:
    Outcome A — operator-hygiene migration confirmed
  elif N_2026 / N_2018 >= 1.0:
    Outcome B — population growth outran migration; refutation conditional on cohort drift
  elif N_2026 / N_2018 ~= 1.0 and R_edu_2026 ~= R_edu_2018:
    Outcome C — no migration detectable; Insight #40 refuted for LAN-architected class
```

Caveats baked into the analysis framework:

1. Brown's 100+ figure is per-scan; Shodan + Censys is rolling-crawl cache. Comparison is approximate, NOT precision.
2. Brown's IPv4 active scan caught Tier-A 11311. Cat-X-ROS uses Shodan + Censys cross-pop which may undercount Shodan-spotty 11311. Lane A's Censys delta is therefore load-bearing for the comparison.
3. Operator hygiene migration may be invisible to a pure external-scan measurement if operators moved rosmaster behind a VPN concentrator that itself is the new exposed surface. A 0 rosmaster count + an increase in operator-owned VPN concentrators does NOT mean operators stopped using ROS; it means the threat surface migrated.

## What this Insight will support post-data

- The Cat-X-ROS final case study Summary section gets a definitive claim about the auth-on-default thesis for LAN-architected protocols, with citations and numbers.
- Insight #99's routing rule gets its first publishable evidence point (the predictor's prediction was correct or incorrect).
- Future LAN-architected category surveys (MQTT, OPC UA, BACnet) inherit the analysis framework as a template.

## Promotion criteria

Promote from STUB-PENDING-DATA to numbered Insight #100 when:

1. Lane A's Stage 0 + 0b harvest completes with verified N_2026, R_edu_2026, C_2026 numbers.
2. Orchestrator reconciles all 4 lane verdicts.
3. The analysis framework above resolves to one of Outcomes A/B/C with citation.
4. Nick explicitly directs publication.

## What this does NOT claim pre-data

- Does NOT predict the outcome. All three outcomes (A, B, C) are entertained; no anchoring.
- Does NOT critique Brown 2018's measurement. The 100+ / 28-country / 70%-edu baseline is the published standard; comparison is approximate but the only available 8-year baseline.
- Does NOT propose disclosure to specific operators on the basis of the count. Disclosure routing is in `shodan/cat-x-ros-2026-06-09/disclosure-routing-template.md` and is sector-class, not per-operator, pre-orchestrator-direction.

## References

- Brown et al. 2018, "Hijacking robots from anywhere" — arxiv:1808.03322, ICRA 2019
- `methodology/insight-40-auth-on-default-shifts-rightward.md` (parent thesis)
- `methodology/insight-99-auth-on-default-routing-rule-internet-vs-lan-architected.md` (sibling routing rule)
- `case-studies/commercial/cat-x-ros-survey-2026-06-09.md` (parent case study)
- `data/platform-intel/cat-x-ros-osint-2026-06-09.md` (Stage -1 master brief)
