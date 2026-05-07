---
title: Vendor-template default-no-auth on research-instrument web stacks — pattern recognition + fleet-audit roadmap
date: 2026-05-06
class: vendor-template
category: meta-finding
status: open-research
methodology: vendor-fingerprint + adjacent-population audit
---

# Vendor-template default-no-auth on research-instrument web stacks

NuClide Research · 2026-05-06

## Thesis

When a research/lab-instrument vendor ships a turnkey appliance whose default configuration includes:

- An embedded Jupyter Notebook with `--no-token` set in the systemd unit, AND/OR
- An operational web dashboard on port 80/443 with no authentication required, AND/OR
- Vendor-administered remote-access toggles (Support VPN, Admin Access) defaulted ENABLED

…then **the population-scale exposure is the vendor's choice, not the operator's**. Customer-side hardening cannot fix it without firmware updates. The compromise rate at scale tracks the fraction of customers who put the device on a public IP, not the fraction who failed to follow security best-practice.

This note generalizes the **Cortical Labs CL1** finding from 2026-05-06 (one customer compromised at Universität Ulm Med Faculty by a Hilix-class IoT botnet via the unauthenticated default-deployment Jupyter) into a **vendor-template-class threat** likely affecting other research/lab-instrument fleets.

## The CL1 finding in one paragraph

`134.60.110.66` (`labdevice.medizin.uni-ulm.de`, sys_id `CL1-2544-043`, software `v0.28.3`) was a Cortical Labs CL1 "biological computer" — a $35K research instrument with cultured human neurons on a Xilinx Zynq UltraScale+ FPGA microelectrode array — running publicly-accessible at the operator's Med Faculty lab. The default deployment exposed: (a) full operational web dashboard on port 80 (life-support set points editable, Pong/Symbol-Classification application launchers, neural recording downloads), (b) embedded Jupyter Notebook on port 8888 with token-disabled, (c) `Support VPN: Enabled` + `Admin Access: Enabled` toggles defaulted ON. A Hilix botnet operator landed via the unauth Jupyter on 2026-04-29, established a reverse-shell foothold, ran reconnaissance, attempted an x86_64 cryptominer (failed: device is ARM), came back 6 days later with a working socat reverse shell (lived 24h), and was setting up a Miniforge-based ARM64 cryptominer when NuClide intervened by terminating the attacker process via the same unauth Jupyter API the attacker used. Full case at [`multi-hilix-jupyter-campaign-2026-05-06.md`](multi-hilix-jupyter-campaign-2026-05-06.md). Vendor disclosure sent to `support@corticallabs.com` recommending fleet-wide audit + firmware push.

## Why this generalizes

The CL1's default-no-auth posture is not unique to Cortical Labs. The pattern recurs because the **engineering economics push every research-instrument vendor toward the same defaults**:

1. **The intended deployment context is "behind the lab firewall."** Vendors design assuming the device is on a private subnet that institutional IT manages. Auth-on-default would create friction when the device is correctly deployed (lab researcher just wants to open Jupyter and start running notebooks). So auth defaults to off.

2. **The customer's research staff are not security operators.** A neuroscientist setting up a CL1, a microscopist setting up a Nikon Ti2-E controller, a chemist setting up a mass-spec acquisition box — none of them want to deal with TLS certs and OIDC. Auth-on-default would generate vendor-support tickets every time the customer hit a credential issue, which the vendor doesn't want.

3. **The vendor's own remote-support workflow assumes default-on access.** Cortical Labs' Support VPN + Admin Access toggles being defaulted ENABLED is consistent with "if support asks, the customer can immediately give us in" being the design goal. Auth-required-by-default would disrupt the support pathway.

4. **The institutional-IT-firewall expectation is empirically wrong.** Across the universe of research labs, a meaningful fraction expose their instruments on a public IP — sometimes deliberately (remote collaborators), sometimes by misconfiguration (NAT default forward, IPv6 leak, "I'll temporarily port-forward and forget"). For any vendor with N customers, some f×N are publicly reachable, and the f is non-zero.

The CL1 incident demonstrates that **f×N goes to "fully compromised within days"** when the default is no-auth and a botnet finds the Shodan dork. The botnet doesn't need to know the vendor or the device class — it just needs the unauth Jupyter banner.

## Adjacent vendor candidates for fleet audit

Vendors and product classes likely sharing the same default-no-auth pattern, organized by adjacency to the CL1:

### Direct adjacency — neuroscience MEA recording / closed-loop platforms

| Vendor | Product class | Likely posture |
|---|---|---|
| **Open Ephys** | OE Acquisition Board + GUI | Open-source GUI runs locally; researchers often expose via Jupyter for remote analysis |
| **Plexon** | Cereplex / OmniPlex / PL2 systems | Windows-based; less Jupyter-default but vulnerable to RDP-class exposures |
| **Multichannel Systems (MCS)** | MEA2100 / W2100 / MC_Rack | Embedded Linux on newer products; web dashboard pattern |
| **Blackrock Neurotech** | Cereplex / NeuroPort / Utah-Array systems | Embedded Linux with researcher-facing controllers |
| **Tucker-Davis Technologies (TDT)** | Synapse, RZ-series processors | TDT Synapse on Windows but acquisition heads run RTOS/Linux |
| **NeuroNexus / Modular Bio** | NeuroNexus headstages | Less networked but increasingly so on newer products |
| **Cambridge Electronic Design** | Spike2 / Power1401 | Older Windows but has network-control surfaces |
| **Intan Technologies** | RHX systems | RHX recording controller often headless w/ Jupyter wrappers in research labs |

### Microscopy automation

| Vendor | Product class | Likely posture |
|---|---|---|
| **Nikon** | NIS-Elements + Ti2-E controller | Windows-based PCs; remote control via NIS-Elements Network |
| **Leica / Zeiss** | LAS X / ZEN automation servers | Windows acquisition PCs with shared-folder + RDP exposure |
| **Olympus / Evident** | cellSens with remote-control modules | Same |
| **ASI / Prior Scientific** | Stage controllers | Embedded Linux + serial-over-IP web frontend on newer models |
| **Andor / Photometrics** | Camera controller PCs | Often Linux-based with vendor-supplied web dashboards |

### Bioreactors / lab automation

| Vendor | Product class | Likely posture |
|---|---|---|
| **Eppendorf** | BioFlo / DASGIP / BioSpec controllers | Embedded Linux with web dashboard |
| **Sartorius** | BIOSTAT B / Univessel SU controllers | Same |
| **Tecan** | Fluent / Freedom EVO | Windows-based, but newer EVOWare runs networked |
| **Hamilton** | Microlab STAR / VANTAGE | Windows + .NET web management |
| **Beckman Coulter** | Biomek i-Series | Windows + LIMS integration with default web ports |

### Mass spec / chromatography

| Vendor | Product class | Likely posture |
|---|---|---|
| **Thermo Fisher** | Q-Exactive / Orbitrap controllers, Xcalibur | Windows-based, often network-connected for data transfer |
| **Waters** | Empower / OneLab | Web-server model — patches exist but customer adoption varies |
| **Agilent** | OpenLab CDS / MassHunter | Same — web-based with admin login but defaults vary |
| **Bruker** | Compass / TopSpin / DataAnalysis | Linux + web-control |

### Edge-AI inference appliances

| Vendor | Product class | Likely posture |
|---|---|---|
| **NVIDIA Jetson** | Jetson AGX/Xavier/Orin dev kits | Default JupyterLab on port 8888 in many vendor-shipped images |
| **Intel** | OpenVINO / NUC-AI dev kits | Anaconda + Jupyter exposed by default in dev-kit images |
| **AWS DeepLens** | (EOL but units remain in deployment) | Default device-shadow + local ports |
| **Coral / Google** | Coral Dev Board | Web dashboard + Jupyter default |
| **Roboflow / OpenVINO** | Self-hosted inference servers | Per-vendor; default-no-auth common in dev images |

The above is a candidate list for **vendor-fingerprint surveying** — where the goal is to identify each vendor's distinctive default-deployment HTTP fingerprints (favicon hashes, page titles, header strings, characteristic JSON shapes) and then probe the cloud/research-network IP space for matches.

## Methodology for surveying the vendor-template class

Standard NuClide cloud-platform surveys probe by *platform* (e.g., Qdrant, MLflow, Milvus). The vendor-template class needs a different methodology because the discoverable signature is the **vendor's web stack**, not the underlying tool:

1. **Enumerate vendor candidates** — publicly-listed product catalogs, scientific-instrument review databases, university procurement lists.
2. **Vendor-fingerprint the default-deployment signature** — install the default vendor image in a controlled lab (or borrow a customer's screenshot), capture the exact HTTP signature of the management UI:
   - Favicon hash for `jaxen pivot`
   - Page title
   - Distinctive HTML / JS imports
   - Banner / version-disclosure endpoints
3. **Sweep the wider IPv4 space** for the fingerprint — Shodan dork (when API is available) or methodical masscan with a strict aimap-style fingerprint.
4. **Per-hit deep enumeration** — auth-state check, customer attribution (cert pivot, rDNS), software version, default-toggles (Support VPN, Admin Access, etc.).
5. **Vendor-coordinated disclosure** — send to the vendor as the leverage point, NOT individual customer-by-customer. The vendor is the only party with the global customer list and the firmware-push capability.

## What vendors should ship instead

Concrete recommendations for vendors of research/lab-instrument web stacks:

1. **Auth required by default at install time.** First-boot wizard generates a strong random admin password, displays it on a directly-attached console (LCD / serial) but never via the network.
2. **Embedded Jupyter Notebook with token-required by default.** `jupyter notebook --no-token` should be a deliberate operator-side override, not the vendor default.
3. **Localhost-bind by default.** Web dashboard listens on `127.0.0.1:80` only; remote access through SSH tunnel or vendor-supplied authenticated reverse-proxy.
4. **Support VPN / Admin Access defaulted OFF.** Customer must explicitly enable when coordinating with vendor support; auto-disable after N hours.
5. **Health-monitor heartbeat to a vendor-controlled service** that detects publicly-reachable instances (the vendor knows their IP allocation; can flag when a customer's IP starts answering on port 80 to scanner-like sources).
6. **Coordinated-disclosure security.txt** at `/.well-known/security.txt` on the device + the vendor's main domain.
7. **Default firewall rule** that blocks WAN-facing ingress to the management ports unless the operator runs an explicit `enable-public-access` command.

## Why the CL1 case is particularly useful as an exemplar

- **Concrete victim.** Universität Ulm Med Faculty is an identified institution with a real device and a real compromise — not a hypothetical.
- **Active malware on the device.** Hilix payload was tried (failed: arch mismatch); attacker came back manually with a portable shell. Multiple attacker artifacts on disk.
- **Vendor-side levers exist.** Cortical Labs has a customer list, firmware-push capability, and a `support@corticallabs.com` channel. This is contrast to (e.g.) Hilix-infected consumer routers where the vendor has no customer list and 8-year-old EOL'd hardware.
- **The biological-tissue dimension makes the harm profile concrete.** Setting `Temperature → 45°C` on a CL1 dashboard kills cultured human neurons in real time. This is unusually direct.
- **The vendor's product is novel and well-named** — Cortical Labs CL1 is the first commercialized "biological computer." The case study has narrative reach beyond the security community.

## Open research questions

1. **What's the true CL1 fleet size?** Cortical Labs has shipped some number of CL1s globally — what fraction are on public IPs? `https://corticallabs.com/cl1.html` doesn't disclose. Vendor disclosure response will tell us.
2. **Is the second confirmed victim (Tencent Cloud Beijing customer at `101.34.81.166`) also a CL1?** That host has the OpenClaw AI-agent framework running but the operator's `lightclawbot` agent wasn't a Cortical Labs identity. Probably not — same Hilix campaign, different operator class. Worth confirming.
3. **What's the cross-vendor sweep methodology yield?** Pick one adjacent vendor (e.g., Intan RHX, Open Ephys), build a vendor-fingerprint, sweep IPv4. NuClide doesn't have the resources for full cross-vendor work; this is a roadmap for future research.
4. **How does the vendor-template threat class compare to the supply-chain threat class?** Supply-chain compromise (vendor pushes malicious firmware) and vendor-template default-config (vendor's defaults are insecure) are both vendor-amplified, but defensible differently. Worth a separate write-up.

## References

- Cortical Labs CL1 case study (full forensic detail) — [`multi-hilix-jupyter-campaign-2026-05-06.md`](multi-hilix-jupyter-campaign-2026-05-06.md)
- Cortical Labs CL1 product page — https://corticallabs.com/cl1.html
- Cortical Labs vendor disclosure (sent today) — [`disclosures/CORTICALLABS-vendor-CL1-default-no-auth.md`](../../disclosures/CORTICALLABS-vendor-CL1-default-no-auth.md)
- Cross-survey synthesis Methodology Insight #10 — [`SYNTHESIS-2026-05.md`](SYNTHESIS-2026-05.md)
- Vendor-coordinated disclosure best practices (CERT/CC) — https://www.kb.cert.org/vuls/howto/
