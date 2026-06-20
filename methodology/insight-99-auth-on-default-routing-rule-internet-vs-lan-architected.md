---
type: insight
id: 99
slug: auth-on-default-routing-rule-internet-vs-lan-architected
date-drafted: 2026-06-09
status: stub-pre-reconcile
survey: cat-x-ros-2026-06-09
lane: D
parents: [40]
---

# Insight #99 (STUB) — Auth-on-default thesis (Insight #40) is sub-class to a routing rule

**Status:** STUB drafted pre-reconcile by Lane D during Cat-X-ROS Robotics survey 2026-06-09. Insight #40 ("auth-on-default strengthens across OSS generations under disclosure pressure") needs a routing rule attached: the thesis applies to one platform class and not to another. The Cat-X-ROS survey is the first survey to put both classes side-by-side in the same category and force the disambiguation.

## Claim

Insight #40 holds for **internet-facing platforms** — software shipped with an HTTP/HTTPS API surface that the project anticipates being exposed to the public internet from day one. For those platforms, disclosure pressure across the OSS generation timeline produces auth-on-default migration: Tabby v0.11.0+ webserver mode, Langfuse SIGNUP_OPEN flip, LibreChat REG_OPEN flip, MLflow tracking-server auth knob, JupyterLab 4.x token-on-by-default, JetPack 6 Jupyter token-on-by-default (NVIDIA-side, Cat-X-ROS Stage -1 Squad 5).

Insight #40 does NOT auto-apply to **LAN-architected protocols** — software whose original design assumes a trusted LAN substrate, where authentication is intentionally NOT in the protocol because the protocol expects the LAN itself to be the security boundary. These platforms can ship open by default for years and not shift right under disclosure pressure, because the "fix" requires re-engineering the protocol architecture, not flipping a config default.

The Cat-X-ROS survey demonstrates the second class. ROS1 (rosmaster, rosbridge_server) shipped open in 2010 and remains open by default in 2026 — 16 years. ROS2 DDS shipped open in 2017 with SROS2 as an opt-in secured stack; remains open by default in 2026 — 9 years. web_video_server has never shipped with an auth knob.

## The mechanism

LAN-architected protocols that shift right require:

1. Per-node cryptographic identity provisioning (SROS2: per-node X.509 certs + governance policy + per-topic permissions XML)
2. Operator tooling for the provisioning workflow that fits the existing deployment UX (docker-compose, ros2 launch files, robot fleet management consoles)
3. Documentation that survives the docker-quickstart -> production-deployment migration without losing the security posture
4. A clear answer to "what happens when a new robot joins the fleet" (the dynamic node enrollment problem)

Each of those is a several-engineer-year effort that the maintainers do not pay for and downstream operators do not see the value of until after a Brown-2018-class disclosure. Disclosure pressure on the LAN-architected class therefore migrates the *operator-side* mitigation (VPN, reverse proxy, network segregation) but does not migrate the protocol default. The Insight #40 mechanism (maintainer flips a default in a release) does not fire because the maintainer has no single config knob to flip.

## The routing rule

For any future category survey, before predicting whether Insight #40 will be confirmed or refuted:

1. Classify the platform set by architecture origin:
   - **Internet-facing**: project README contains a `curl http://your-deployment` example. Default network exposure assumption is public internet. Examples: Tabby webserver mode, Langfuse, LibreChat, MLflow, Jupyter, Foxglove Cloud.
   - **LAN-architected**: project README contains a `rosrun` / `ros2 launch` example with no host configuration. Default network exposure assumption is the LAN. Examples: rosmaster, rosbridge_server, ROS2 DDS, web_video_server, foxglove_bridge (self-hosted, not Cloud), MQTT brokers without TLS, OPC UA default deployments.

2. Apply Insight #40 prediction only to the internet-facing subset.

3. For the LAN-architected subset, predict:
   - Default ships open and continues to ship open across the timeline.
   - Operator-side mitigation is the migration path (VPN, segregated VLAN, reverse-proxy auth, firewall).
   - Population-level exposure measurement is therefore a measure of operator-deployment hygiene, NOT a measure of protocol auth posture.
   - Disclosure pressure produces *bridge-platform* rewrites (e.g. Foxglove Cloud paid SaaS = auth-on; foxglove_bridge self-hosted = Tier-A), not protocol-level shifts.

## Why this matters operationally

A blunt "does this survey confirm or refute Insight #40" question is malformed when the category mixes both classes. Cat-X-ROS mixes internet-facing (Jetson JetPack 6 Jupyter, Foxglove Cloud) and LAN-architected (rosmaster, ROS2 DDS, web_video_server). The reconciled answer is: thesis CONFIRMED for the internet-facing subset (JetPack 6 shifted right), thesis NOT-APPLICABLE for the LAN-architected subset (no migration mechanism, no expected shift, no refutation if no shift observed).

This stops a future report from asserting "ROS refutes Insight #40" — which would be a category error.

## Promotion criteria

Promote from STUB to numbered Insight #99 when:

1. Cat-X-ROS Robotics survey finalizes with measured 2026 rosmaster/rosbridge/DDS population numbers AND the LAN-architected class is documented in the final case study.
2. ONE additional category survey reuses the routing rule to correctly predict (in advance) that Insight #40 would or would not apply.

## What this does NOT claim

- Does not retract Insight #40. Sub-classes #40 with a routing rule attached.
- Does not predict that LAN-architected platforms NEVER shift right. SROS2 exists. JetPack 6 is the example of a LAN-adjacent platform shifting. The routing rule says "do not *assume* the shift will happen on the LAN-architected timeline" — which is the load-bearing point.
- Does not predict ROS will remain insecure forever. Operator-side mitigation IS the migration path; this Insight just clarifies WHERE to measure the shift (operator-deployment hygiene, not protocol default).

## References

- `methodology/insight-40-auth-on-default-shifts-rightward.md` (parent Insight, sub-classed by this stub)
- `data/platform-intel/cat-x-ros-osint-2026-06-09.md` (Stage -1 evidence inputs)
- `case-studies/commercial/cat-x-ros-survey-2026-06-09.md` (parent case study)
- Brown et al. 2018, IOActive 2017, Dieber et al. ROS security series, Roboception SROS2 research
