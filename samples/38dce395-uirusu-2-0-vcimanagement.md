---
title: "vcimanagement.x64 — Uirusu/2.0 Mirai-derivative IoT botnet"
date: 2026-05-07
sha256: 38dce395aa82fea8b4ea00de17e14f3b7db9a5ebb28e82529ed66aa2b0f44eb0
md5: 654c32932b22fc8b0b486c2ecdeb1613
file_name: vcimanagement.x64
file_size: 784152
file_type: ELF
file_arch: x86_64
family: Mirai
variant: Uirusu/2.0
mb_url: https://bazaar.abuse.ch/sample/38dce395aa82fea8b4ea00de17e14f3b7db9a5ebb28e82529ed66aa2b0f44eb0/
vt_url: https://www.virustotal.com/gui/file/38dce395aa82fea8b4ea00de17e14f3b7db9a5ebb28e82529ed66aa2b0f44eb0
mb_first_seen: 2026-05-07
reporter: nuclide
dropped_by_sha256: ee51b236e57d96521da5fb820242c23996dcc691d3df8830655801b2a516bb72
dropped_by_malware: Hilix
tags:
  - Mirai
  - Uirusu
  - IoT-Botnet
  - Linux
  - ELF
  - Jupyter
  - Huawei-HG532
  - ThinkPHP
related_research:
  - case-studies/commercial/multi-hilix-jupyter-campaign-2026-05-06.md
related_disclosures:
  - disclosures/EONIX-173-232-146-173-uirusu-c2.md
  - disclosures/TENCENT-101-34-81-166-jupyter-compromise.md
---

# vcimanagement.x64 (Uirusu/2.0)

Mirai-derivative IoT botnet, x86-64 ELF build. Recovered 2026-05-06 from a Tencent Cloud Beijing victim host (`101.34.81.166`) that had been compromised via unauthenticated Jupyter Notebook on port 8888 and was also infected sequentially by Hilix-classic (separate sample, see `dropped_by_sha256`).

The botnet author's signature is the literal User-Agent string `Uirusu/2.0`, *uirusu* / ウイルス is Japanese for "virus."

## Bundled exploit modules

This sample is broader than the Hilix-classic build. Embedded RCE primitives:

- **UPnP-Huawei-HG532** SOAP CmdInjection (CVE-2017-17215)
- **ThinkPHP** invokefunction RCE (CVE-2018-20062)
- **MVPower DVR** ViewLog.asp RCE
- **Hardcoded Huawei `dslf-config:HuaweiHomeGateway`** Digest-auth admin RCE

## Indicators

- **C2 / payload distribution:** `173.232.146.173` (Eonix Corporation, rDNS `zknotes.com`, separately reported to `net-abuse@eonix.net`)
- **Payload paths:** `/bins/x86`, `/mips`, `/8UsA.sh` (shell installer)
- **Campaign argv:** `mips`, `ThinkPHP`
- **Foothold pattern:** open Jupyter `:8888` → kernel exec → reverse shell → drop bot

## Public availability

- **MalwareBazaar:** [bazaar.abuse.ch/sample/38dce395...](https://bazaar.abuse.ch/sample/38dce395aa82fea8b4ea00de17e14f3b7db9a5ebb28e82529ed66aa2b0f44eb0/) (reporter: `nuclide`, auto-classified `Mirai` family; carries `dropped_by_sha256` link to the Hilix sample)
- **VirusTotal:** [virustotal.com/gui/file/38dce395...](https://www.virustotal.com/gui/file/38dce395aa82fea8b4ea00de17e14f3b7db9a5ebb28e82529ed66aa2b0f44eb0)
- **First public submission:** 2026-05-07 (NuClide). Pre-submission lookups confirmed not previously known to VT, MB, AlienVault OTX, or GitHub-indexed code.

## Source

Full incident: [`multi-hilix-jupyter-campaign-2026-05-06`](../case-studies/commercial/multi-hilix-jupyter-campaign-2026-05-06.md). Evidence pack: [`evidence/hilix-uirusu-jupyter-campaign-2026-05-06`](../evidence/hilix-uirusu-jupyter-campaign-2026-05-06/).
