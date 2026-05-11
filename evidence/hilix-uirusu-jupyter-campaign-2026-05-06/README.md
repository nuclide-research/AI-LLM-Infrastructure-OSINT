# Hilix-classic + Uirusu/2.0 Jupyter-targeting IoT botnet campaigns

NuClide Research evidence pack · 2026-05-06 / 2026-05-07

This directory contains the public-facing forensic evidence from a multi-victim, multi-actor IoT botnet operation that exploits **unauthenticated Jupyter Notebook on port 8888** as a Linux-foothold vector. Two confirmed victims (Universität Ulm Med Faculty CL1 + Tencent Cloud Beijing customer), two distinct Mirai-derivative botnet families compromising the same population.

Background and methodology insights:

- Full case study: [`../../case-studies/commercial/multi-hilix-jupyter-campaign-2026-05-06.md`](../../case-studies/commercial/multi-hilix-jupyter-campaign-2026-05-06.md)
- Vendor-template threat-class study (CL1 as exemplar): [`../../case-studies/commercial/vendor-template-default-no-auth-research-instruments.md`](../../case-studies/commercial/vendor-template-default-no-auth-research-instruments.md)
- Synthesis paper Methodology Insights #10, #13, #14, #14a: [`../../case-studies/commercial/SYNTHESIS-2026-05.md`](../../case-studies/commercial/SYNTHESIS-2026-05.md)

## Contents

```
ulm/
  ulm-forensic-dump.json              # full kernel-WebSocket forensic enumeration of
                                      # 134.60.110.66 (Cortical Labs CL1-2544-043) - 19
                                      # commands run via the unauth Jupyter kernel:
                                      # process list, attacker bash history, sudo -l,
                                      # connections, cl-analyser daemon state, dmesg,
                                      # /etc/passwd, who, listeners
  ulm-TPC3-reverse-shell.ipynb        # attacker notebook with active socat reverse
                                      # shell to 172.233.96.208:3053 (Hilix-classic C2)
  ulm-Untitled-recon.ipynb            # attacker recon notebook (13 cells with outputs)
                                      # - sudo -l revelation, failed Hilix.x86_64
                                      # download attempt (architecture mismatch)
  ulm-cl-system-config.json           # legit CL1 hardware calibration (sys_id
                                      # CL1-2544-043, ADC/DAC trim values) - vendor
                                      # context for forensic analysis

tencent/
  _recon.ipynb                        # Uirusu/2.0 reconnaissance notebook
  Untitled1.ipynb                     # 28-cell attacker working notebook - DDoS launch
                                      # via 2.js (target a.intincity.promo) + /etc/shadow
                                      # root-password modification attempt
  Untitled6-af_alg-kernel-exploit.ipynb # AF_ALG kernel exploit (uid=0(root) confirmed
                                      # in cell output)
  _recon.py                           # reconnaissance shell-cmd wrapper
  2.js                                # Layer-7 HTTP/2 HPACK DDoS-for-hire tool
                                      # (Node.js, multi-process cluster, proxy rotation)

IOCs.txt                              # all indicators of compromise (IPs, hashes,
                                      # filenames, command patterns, exploit bundle)
MANIFEST.sha256                       # SHA256s of every file in this evidence pack
```

## What's NOT included (and why)

**Live malware binaries** are NOT committed to this public repository:

- `Hilix.x86_64` (SHA256 `ee51b236e57d96521da5fb820242c23996dcc691d3df8830655801b2a516bb72`)
- `vcimanagement.x64` Uirusu/2.0 (SHA256 `38dce395aa82fea8b4ea00de17e14f3b7db9a5ebb28e82529ed66aa2b0f44eb0`)

Reasons:

1. **GitHub Acceptable Use Policy** prohibits malware distribution
2. **Responsible-disclosure norms** for IoT-botnet samples, sharing should be via VirusTotal / MalwareBazaar / direct researcher-to-researcher, not random-clone-attacker access
3. **The hashes in `IOCs.txt`** are sufficient for any defender's AV/EDR/VirusTotal lookup against their own samples

### Public sample availability

NuClide submitted both samples to **VirusTotal** and **MalwareBazaar** on 2026-05-07. Pre-submission lookups confirmed both were not previously known to either platform, AlienVault OTX, or GitHub-indexed code, these were the **first public submissions** of both samples to any industry sharing platform.

**MalwareBazaar** (abuse.ch, direct ELF download for verified researchers, `infected`-password ZIP):

- **Hilix.x86_64:** https://bazaar.abuse.ch/sample/ee51b236e57d96521da5fb820242c23996dcc691d3df8830655801b2a516bb72/
- **Uirusu/2.0** (`vcimanagement.x64`): https://bazaar.abuse.ch/sample/38dce395aa82fea8b4ea00de17e14f3b7db9a5ebb28e82529ed66aa2b0f44eb0/

Reporter: `nuclide`. Tags applied: `Mirai`, `Hilix`/`Uirusu`, `IoT-Botnet`, `Linux`, `ELF`, `Jupyter` (foothold), plus `Huawei-HG532` + `ThinkPHP` for the Uirusu sample. The Uirusu entry carries a `dropped_by_sha256` relationship to Hilix to preserve the multi-actor-convergence link in MalwareBazaar's graph.

**VirusTotal** (broad AV/EDR detection coverage, propagates into industry telemetry feeds):

- **Hilix.x86_64:** https://www.virustotal.com/gui/file/ee51b236e57d96521da5fb820242c23996dcc691d3df8830655801b2a516bb72
- **Uirusu/2.0** (`vcimanagement.x64`): https://www.virustotal.com/gui/file/38dce395aa82fea8b4ea00de17e14f3b7db9a5ebb28e82529ed66aa2b0f44eb0

Researchers can pull samples directly from MalwareBazaar (free Auth-Key from `auth.abuse.ch`) or VirusTotal (with appropriate API tier). AV/EDR vendors pick up the hashes through their normal VT-feed and MalwareBazaar daily-batch integrations.

For direct researcher-to-researcher transfer (e.g., Cortical Labs vendor team for fleet-audit purposes), email `nicholas@nuclide-research.com`.

**Tencent operator's personal AI-agent context files** are NOT included:

The Tencent victim is running a legitimate personal LLM-agent workspace ("lightclawbot" using an OpenClaw-class framework, `AGENTS.md`, `SOUL.md`, `IDENTITY.md`, `USER.md`, `BOOTSTRAP.md`, `MEMORY.md`, `TOOLS.md`, `HEARTBEAT.md`, `memory/`, `state/`, `skills/`, `docs/`). These are operator-IP belonging to a third party who happens to also be a botnet victim, publishing them without consent would compound the harm. The case study describes their existence at the categorical level (operator runs a personal AI agent on Tencent Cloud Beijing); the actual files are not republished.

## Provenance

All Ulm-host files were retrieved via the **same unauthenticated Jupyter API the attacker used**, `GET /api/contents/<path>` and `POST /api/kernels/<id>/channels` WebSocket exec. No privilege escalation, no exploitation of any vulnerability beyond the operator's existing token-disabled-Jupyter posture.

Tencent attacker files retrieved via `GET /api/contents/<path>` only (the Tencent host had no active kernel at probe time, so no kernel exec was needed). Operator's own files were excluded from the pack at retrieval time per the privacy principle above.

## Disclosure status

All disclosures sent 2026-05-06 / 2026-05-07 from `nicholas@nuclide-research.com`:

| Recipient | Subject |
|---|---|
| `cert@uni-ulm.de` + `dfn-cert@dfn-cert.de` | Ulm victim, initial + post-forensic-gather + port-80 dashboard 2nd-pass |
| `abuse@tencent.com` | Tencent victim |
| `abuse@akamai.com` + `abuse@linode.com` | Hilix-classic C2 `172.233.96.208` |
| `abuse@cogentco.com` | Hilix-classic malware-distro `38.87.117.84` |
| `net-abuse@eonix.net` | Uirusu/2.0 C2 `173.232.146.173` |
| `support@corticallabs.com` | CL1 vendor-fleet advisory (initial + evidence pack + standalone case-study followup) |

Pull responses will trickle in over 7-30 days; outcomes will be tracked separately.

## Contact

Nicholas Michael Kloster
nicholas@nuclide-research.com
AI-LLM-Infrastructure-OSINT
