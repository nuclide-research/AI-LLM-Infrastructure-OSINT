---
to: cert@uni-ulm.de
cc: dfn-cert@dfn-cert.de, abuse@nuclide-research.com
severity: CRITICAL
ip: 134.60.110.66
institution: Universität Ulm Medical Faculty (labdevice.medizin.uni-ulm.de) — SECOND-PASS finding: entire Cortical Labs CL1 operational dashboard exposed unauth on port 80, separate from the port-8888 Jupyter compromise; allows direct control of living-neuron life support
status: DRAFT
date: 2026-05-06
---

**To:** cert@uni-ulm.de
**Cc:** dfn-cert@dfn-cert.de, abuse@nuclide-research.com
**Subject:** SECOND-PASS — `134.60.110.66` port 80 also exposes the CL1 operational control dashboard unauth (separate from the Jupyter:8888 compromise); biological-tissue life-support and stimulation controls reachable

---

Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com

2026-05-06

**This is a SECOND-PASS finding** on `134.60.110.66` — separate from and more severe than the Jupyter:8888 compromise reported in my prior two messages today. NuClide's initial probe focused on port 8888; a follow-on review surfaced that **port 80 is the Cortical Labs CL1 operational control dashboard, also unauthenticated**.

**Severity:** CRITICAL — direct manipulation of living biological tissue + ML training infrastructure controls reachable to anyone on the public internet.

---

## Confirmed exposure

`http://134.60.110.66/` redirects to `/dashboard` and serves the **CL1-2544-043** operational web interface unauthenticated. Routes confirmed reachable (HTTP 200, no credentials):

```
/dashboard                                ← live vitals (Temperature, CO2, O2, pump speed, MEA)
/applications/installed/                  ← installed app catalog
/applications/symbol-classification/      ← Symbol Classification config + launcher
/applications/pong/                       ← Pong (DishBrain-class) config + Launch Now button
/applications/queue/                      ← session queue (presumed)
/jupyter/                                 ← reverse-proxies the unauth Jupyter we already disclosed
/recordings                               ← neural recordings access
/documentation
/system                                   ← System version + uptime + storage
/support
```

The dashboard surfaces:

**Vitals** (live readings of the cultured-neuron tissue's life support):
- Temperature: `37.00 °C` with editable set point
- Carbon Dioxide: `5.05 %` with editable set point (`5.00`)
- Oxygen: `19.21 %` with editable set point (`22.00`)
- Pump Speed (uL/min) configurable for MEA, Gas, Reservoir
- Status: `Healthy`

**System info:**
- Version `v0.28.3`
- Uptime `1d 16h 32m`
- Storage Capacity `983.4 GB`, Available `982.9 GB`

**Applications** with one-click `Launch Now` / `Launch Portal` buttons:
- **Symbol Classification** — open-loop and closed-loop stimulation configs, channel selection (64 MEA electrodes), feedback configurations, baseline/test phase configurations
- **Stimulation Scan** — direct stimulation parameter scan on the cultured-neuron MEA
- **Pong** — DishBrain-class neuron-trained Pong; configurable game time, feedback mode (`wide-sensory`), session plan (`game/rest/game`), spike sensitivity, electrode-to-paddle mapping, Launch Now button. Stimulation channels include positive/negative feedback at 2.5 µA / 100 Hz / 0.1 s, channel mode (Specific / Random / Stimulation Channels), `Estimated Duration: 3 hours, 25 minutes, 55 seconds`

## What an unauthenticated attacker can do

1. **Disrupt or destroy the cultured neurons** by altering life-support set points:
   - Raise temperature to denature proteins
   - Cut pump speed to starve the tissue of nutrients
   - Adjust CO2 / O2 to trigger hypoxia or acidosis
   - All via the existing edit-pencil UI; no credentials required

2. **Trigger stimulation runs** on the cultured-neuron MEA with arbitrary current/frequency/duration settings (the existing positive/negative feedback config defaults to 2.5 µA / 100 Hz / 0.1 s, which is benign, but the UI accepts higher values without bound enforcement visible to NuClide). Excessive current can damage neurons and electrodes.

3. **Tamper with experiments** by launching applications mid-run, modifying session plans, changing feedback modes — invalidating any active research

4. **Read recorded neural data** via `/recordings` — patient-anonymized but still operator-IP

5. **Pivot via /jupyter/** — the same Jupyter:8888 we already disclosed is also reverse-proxied at `/jupyter/` on port 80, so even when 8888 is blocked at the firewall, the same code-execute-as-labuser path is reachable on the standard HTTP port

NuClide explicitly **did not** click any operational control. All confirmation was via passive HTTP 200 checks on the route table.

## Why this is more severe than the port-8888 finding

The Jupyter:8888 finding (botnet foothold) is bad — Linux box compromised, mining setup in progress, support-VPN config read. **The port-80 finding is worse:**

- **Direct biological harm vector:** the CL1's life-support set points are a living-tissue kill switch. A bored attacker could end the experiment by clicking `Edit` on Temperature and entering `45`.
- **Research integrity:** ongoing experiments are visible via the dashboard (Symbol Classification config, Pong session plan). An attacker could alter session plans or trigger arbitrary stimulation, contaminating any active research data.
- **No need for a Jupyter exploit:** the dashboard's own REST/WebSocket API (whatever it is — not yet enumerated by NuClide) does the operational tasks. The kernel-execute pivot via Jupyter is one path; the dashboard buttons are a parallel, more direct path.
- **Search-engine indexable:** unlike Jupyter (which Shodan dorks find but isn't normally indexed), a generic web dashboard on port 80 is reachable to any web crawler. The exposure window may be much larger than the 22h bash-shell foothold.

## Required action (additional to prior disclosure)

In addition to the Jupyter remediation in my prior two messages, please:

1. **Stop the port-80 dashboard service immediately**:
   ```bash
   # The dashboard is likely the cl-analyser service or a sibling — check:
   sudo systemctl list-units --type=service | grep -iE "cl-|dashboard|cortical|tornado"
   sudo systemctl stop <service>
   sudo ufw deny 80/tcp; sudo ufw deny 443/tcp
   ```

2. **Do NOT bring it back up without authentication.** Cortical Labs CL1 v0.28.3 ships with no web-auth in its dashboard; this is a vendor-default issue. Contact Cortical Labs support to ask about the supported auth mechanism (HTTP basic-auth via reverse proxy, mTLS, OIDC) for the dashboard.

3. **Verify experiment integrity.** Check whether any unauthorized `Launch` events occurred via `cl-analyser` logs (`sudo journalctl -u cl-analyser --since '14 days ago' | grep -iE 'launch|stimulation|pong|symbol-class'`).

4. **Consider this an opportunity for a Cortical Labs vendor advisory.** The dashboard-without-auth deployment is a vendor-template issue — almost certainly other CL1 customers have the same posture. A coordinated CL1-fleet disclosure to Cortical Labs (`security@corticallabs.com` if they publish; otherwise `support@corticallabs.com`) would be appropriate. NuClide can coordinate this if requested.

## Additional IOC (already in main case study)

| Type | Value |
|---|---|
| Vulnerable port | tcp/80 (separate from previously-reported tcp/8888) |
| Vulnerable routes | `/dashboard`, `/applications/*`, `/jupyter/`, `/recordings`, `/system` (all unauth) |
| Vendor + version | Cortical Labs CL1, software v0.28.3, sys_id CL1-2544-043 |
| Hardware | Xilinx Zynq UltraScale+ FPGA, 4-channel ADC + 4-channel DAC, MIPI-DSI 720x1280 LCD, kernel 6.1.30-xilinx-v2 |

## Reference

Full case study (multi-victim Hilix campaign + this secondary finding):
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT/blob/main/case-studies/commercial/multi-hilix-jupyter-campaign-2026-05-06.md

Available for verification, additional probing under your direction, or coordination with Cortical Labs support / DFN-CERT for a vendor-fleet disclosure.

Regards,
Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT
