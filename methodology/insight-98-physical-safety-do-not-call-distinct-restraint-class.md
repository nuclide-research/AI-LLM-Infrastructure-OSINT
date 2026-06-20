---
type: insight
id: 98
slug: physical-safety-do-not-call-distinct-restraint-class
date-drafted: 2026-06-09
status: stub-pre-reconcile
survey: cat-x-ros-2026-06-09
lane: D
---

# Insight #98 (STUB) — Physical-safety DO_NOT_CALL is a distinct restraint class

**Status:** STUB drafted pre-reconcile by Lane D during Cat-X-ROS Robotics survey 2026-06-09. Promoted to numbered Insight only after orchestrator reconciles all 4 lane verdicts AND the rule is observed to apply in subsequent surveys (Insight discipline: a single survey is a candidate, multi-survey recurrence is an Insight).

## Claim

NuClide's restraint vocabulary built up through Categories 1-X-1 was anchored on a *compute-exfil* DO_NOT_CALL set: completions endpoints, GraphQL mutations, /api/kernels/<id>/execute, repo-write operations, model-pull. The Cat-X-ROS Robotics survey demonstrates a *distinct second class* the existing vocabulary did not cover: motor-command endpoints that **cause physical movement of physical objects** when called.

The two classes are not nested; they are orthogonal. A platform can require:
- compute-exfil restraint only (vector DB, LLM endpoint, MLflow)
- physical-safety restraint only (sterile motor control interface with no compute exfil surface, hypothetical)
- both (rosbridge_server: physical-safety + topic-name enumeration is incidentally a compute / inference surface for the AI nodes downstream)

## Why the Cat-X-ROS survey forced this

The pre-existing DO_NOT_CALL pattern from Cat-Tabby and prior commercial surveys hard-refused completions endpoints. That set was sufficient for software-only categories because every potential restraint violation was a *bit-pattern* operation: an inference invocation, a database read, a credential test, a code-execution kernel call. None of those move a physical object.

ROS adds endpoints that, when called, change the position of a real robot in the real world:

- `rosbridge_server`: `publish` to `/cmd_vel` rotates motor shafts; `send_action_goal` to a navigation action moves a mobile robot; `callService` on a gripper service opens or closes a gripper.
- `rosmaster`: `registerService` on a controller manager hijacks the controller graph.
- `ROS2 DDS`: any DataWriter publication to `/cmd_vel`, lifecycle transitions, or `/fmu/in/*` PX4 drone command topics.
- `foxglove_bridge`: `publish`, `advertise`, `callService`, `setParameters`.
- `nav2` / `moveit`: navigation goals and trajectory executions.

These are not "loud" software requests. They cause a robot arm to swing, a mobile base to roll, a drone to fly. Brown et al. 2018 demonstrated this with consent. The restraint discipline is therefore not "don't make the host notice you in their logs"; it is "don't *physically* touch the operator's hardware."

## Operational implication

The DO_NOT_CALL constant in `stage3v-verify.py` is *not* a stricter version of the Cat-Tabby DO_NOT_CALL; it is a parallel set covering a different harm class. NuClide's restraint vocabulary needs a second axis:

| Axis | Harm class | Example endpoints | Restraint mechanism |
|---|---|---|---|
| compute-exfil | data egress, inference invocation, credential brute, code execution | /v1/completions, /api/kernels/<id>/execute, GraphQL mutations | hard-refuse at code level; mark surface-open-access-not-exercised |
| physical-safety | motor movement of real-world hardware causing potential physical damage | publish to /cmd_vel, send_action_goal, callService on actuator, publish to /fmu/in/* | hard-refuse at code level; topic names ARE the finding; DESCRIBE/listChannels/enumerate-only |

Both axes use the same mechanism (code-level hard refusal) but the *justification* is different: compute-exfil is governed by ethics + scope-gate + legal-equivalent rule; physical-safety adds bodily-harm and property-damage potential as the load-bearing boundary.

## What this changes in the methodology

1. Per-category lane briefs must declare both axes explicitly: which compute-exfil endpoints are out-of-scope, and which physical-safety endpoints are out-of-scope.
2. VisorScuba compliance controls need a `BLUE-PHYS-*` family (`BLUE-PHYS-001` is the first, see `visorscuba-blue-phys-001.rego` in the Cat-X-ROS shodan/ directory).
3. aimap-profile classification needs a `physical_actuation: bool` flag per platform fingerprint, so downstream verify stages can pick up the restraint axis automatically.
4. Disclosure-routing K0107 mapping (Lane D) must include sector-specific bodily-harm regulators (aviation: CAA/FAA; medical: FDA/EMA; industrial: OSHA equivalents) as channel-class options separate from CERT.

## What this does NOT claim

- It does not claim ROS is uniquely bad. The restraint class is platform-class-driven, not platform-identity-driven. Any future category that includes hardware-actuation surfaces (industrial control protocols, USB-HID-over-IP, voice-coil drivers exposed over the network) inherits the same restraint class.
- It does not claim Cat-Tabby's restraint vocabulary was wrong. It was correct for that category's harm class.
- It does not claim a numbered Insight yet. STUB pre-reconcile, multi-survey recurrence required for promotion.

## Promotion criteria

Promote from STUB to numbered Insight #98 when:

1. Cat-X-ROS Robotics survey finalizes and the physical-safety DO_NOT_CALL set is documented in the final case study.
2. ONE additional category survey (likely a future ICS/OT-adjacent or drone-fleet category) reuses the physical-safety axis with its own platform-specific list.

Until then this is a candidate.

## References

- `case-studies/commercial/cat-x-ros-survey-2026-06-09.md` (parent case study)
- `shodan/cat-x-ros-2026-06-09/EVIDENCE-INTACT.txt` (DO_NOT_CALL set enforced)
- `shodan/cat-x-ros-2026-06-09/visorscuba-blue-phys-001.rego` (compliance control stub)
- Brown et al. 2018, "Hijacking robots from anywhere" (arxiv:1808.03322)
- IOActive 2017, "Hacking Robots Before Skynet"
- Dieber et al., ROS security paper series
