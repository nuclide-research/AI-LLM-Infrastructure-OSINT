---
type: survey
---

# ROS Robotics Population Survey (2026-05-16)

_NuClide Research · 2026-05-16 (Survey 5 of the day's 10-category batch)_
_Closes: category 28 (medical-edge-ai / robotics leg). ROS master / rosbridge / Jetson edge_

---

## Summary

Population survey of ROS (Robot Operating System) deployments. The canonical robotics middleware stack. ROS master :11311 speaks XMLRPC, rosbridge :9090 speaks WebSocket+HTTP. Both leak topic/node names when reachable unauth, and ROS is **physical-impact tier**, topics like `/cmd_vel`, `/joint_states`, `/move_base` map to physical actuators on robots.

- 28 candidates harvested (`port:11311 http.status:200` + `port:9090 http.html:"ros"`)
- Probed via `fast_enum_ros.py` (XMLRPC `getSystemState` for :11311, HTTP probe for :9090)
- **0 confirmed live ROS master, 0 confirmed live rosbridge**

**Result: Shodan-dark category.** Confirms [[insight-21-port-first-discovery-for-low-footprint-platforms]]. ROS master :11311 is TCP-XMLRPC (not HTTP-indexed by Shodan), and rosbridge :9090 is shared with many other services. The real ROS population needs masscan tier-2 on :11311 / :9090 with strict-conjunctive verification (`getSystemState` returning a `<methodResponse>`).

---

## Why this matters anyway

The null result is informative as a methodology checkpoint:

1. **Shodan-dark confirmation.** ROS robotics joins the Insight #21 Shodan-dark family (alongside Letta, A1111, Forge, SD.Next, Fooocus from prior surveys). The dork strategy that worked for AI-application-layer platforms (Ollama, ComfyUI, Elasticsearch) does not work for protocol-layer platforms like ROS that don't expose HTTP-indexable strings.

2. **Physical-impact tier is genuinely understudied.** The ROS population, likely 10s to 1000s of exposed instances at masscan-tier-2 reach, represents the highest-risk tier of any survey on the auth-on-default thesis (publish to `/cmd_vel` on an exposed ROS master = move a physical robot). The fact that this tier is Shodan-dark means it's been mostly invisible to opportunistic scanners; the operators get a false sense of safety from "Shodan doesn't see us."

3. **Deferred to a masscan-tier survey.** Per the methodology's manual→productize→re-run loop: the fingerprint code (XMLRPC `getSystemState` probe + rosbridge WebSocket marker) is built and ready in `fast_enum_ros.py`. A masscan tier-2 sweep on :11311 + :9090 across DigitalOcean/Hetzner/Vultr/Linode/Scaleway/OVH (3.55M IPs) is the next step. Estimated yield: 100s of unauth ROS masters at population scale.

---

## What an exposed ROS master would disclose

For documentation purposes (deferred-survey roadmap):

`getSystemState` returns three lists:
- **Publishers**: list of `[topic, [node1, node2]]`. Every topic being published
- **Subscribers**: same shape. Every topic being consumed
- **Services**: same shape. Every named service

Topic names ARE the finding for ROS:

- `/cmd_vel` → velocity command publisher = mobile robot, attacker can drive
- `/joint_states` → joint positions = robotic arm/quadruped
- `/move_base` → autonomous navigation goal endpoint
- `/camera/image_raw` → camera feed publisher
- `/odom` → odometry (location tracking)
- `/scan` → LiDAR scan
- `/imu` → inertial measurements (drone/quadruped)
- `/gripper_command` → robotic gripper actuator

`/cmd_vel + /scan + /odom` on the same master = mobile robot (likely a delivery robot, warehouse AGV, or hobbyist build). `/joint_states + /gripper_command + /move_base` = collaborative robot arm. Any combination with `/camera/image_raw` exposes the workspace view.

---

## Honest negative space

- **The 28 Shodan candidates returned mostly proxies/load-balancers** that have :11311 or :9090 open but don't forward to a real ROS master. ROS master is a TCP-XMLRPC service; HTTP-on-:11311 with `getSystemState` returning a 200-shaped reply is what we look for, and 0 of 28 returned that.
- **rosbridge :9090 also Shodan-dark.** Port :9090 is shared with Prometheus pushgateway, JupyterHub default, etc. The few `port:9090 http.html:"ros"` hits surfaced were likely false-positive (HTML mentioning "ros" in unrelated context).
- **The 0/28 result does NOT mean ROS has 0 exposed instances.** It means Shodan can't find them. Per Insight #21, the move is port-first masscan.
- **No masscan tier-2 attempted** in this survey. The discovery-channel pivot is the right next step but is its own multi-hour operation.

---

## Methodology placement

Adds ROS robotics to the catalog of **Shodan-dark platform classes**:

| Platform | Why Shodan-dark | Discovery channel needed |
|---|---|---|
| ROS master :11311 | TCP-XMLRPC, not HTTP-indexed | masscan tier-2 + XMLRPC `getSystemState` probe |
| rosbridge :9090 | Port shared with many services | masscan + body-marker filter |
| Letta agent-memory :8283 | Port shared, brand string in JS only | masscan + `/v1/health` JSON-shape probe |
| AUTOMATIC1111 :7860 | Gradio SPA, brand string in JS | masscan + `/sdapi/v1/options` probe |
| Forge / SD.Next :7860 | Same as A1111 | same |
| Fooocus :7865 | Gradio SPA | same |
| SwarmUI :7801 | Port shared | masscan + body marker |
| InvokeAI :9090 | Port shared with rosbridge etc. | masscan + `/api/v1/app/version` probe |

ROS specifically is a special case because of the physical-impact tier. Once the population is mapped, the disclosure pattern needs to be carefully thought through (operator-attribution before any aggregate publication; surfaces controlling physical hardware deserve coordinated disclosure not aggregate-publication).

---

## Toolchain Provenance

```
0. shodan search × 2 dorks → 28 unique candidates (port:11311 + port:9090 "ros")
1. fast_enum_ros.py (threads=20) → 0 ROS, 0 rosbridge confirmed
2. (deferred) masscan tier-2 + XMLRPC strict probe → estimated 100s of real instances
3. (deferred-pending-discovery) visorlog ingest, aimap fingerprint codification
```

---

## See also

- [[insight-21-port-first-discovery-for-low-footprint-platforms]]. Exactly the case ROS fits
- [`agent-framework-stragglers-population-survey-2026-05-16.md`](agent-framework-stragglers-population-survey-2026-05-16.md): same day's Shodan-dark companion
- `case-studies/commercial/FUTURE-SURVEYS.md`: ROS listed under specialty-domains (robotics leg) as "genuinely unmapped. Highest-novelty, physical-impact tier"
