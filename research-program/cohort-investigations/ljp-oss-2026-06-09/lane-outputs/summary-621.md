# Per-IP Investigation Harness — DCWF 621+671 Synthesis

_Generated 2026-06-10 00:18:46 UTC by `cohort-harness.py`._

Source IP list: `cohort-megaset.txt` (N=491)
Probed: 420 of 491 (alive=420, dead=71 skipped at scanner)

## Signal extraction (out of probed)

| Signal | Count |
|---|---|
| aimap fingerprint returned | 327 |
| SPA APP_CONFIG captured | 315 |
| /openapi.json parsed | 53 |
| /v1/models with data array | 7 |

## Platform distribution

| Platform | Count |
|---|---|
| Sub2API | 316 |
| unknown | 61 |
| Grok2API | 39 |
| cousin | 2 |
| QClaw | 1 |
| OpenClaw | 1 |

## Host-class distribution (A/B/C/D/E)

| Class | Count | Meaning |
|---|---|---|
| D_private_closed_pool | 327 | private/closed (app present, reg off, pay off) |
| unknown | 40 | indeterminate |
| A_open_registration | 26 | open registration enabled (claimable accounts) |
| E_auth_gate_everywhere | 25 | auth-gate everywhere (only 4xx, no public surface) |
| B_commercial_paid | 2 | payment_enabled true (commercial reseller) |

## Distinct operator pivots (`api_base_url` from APP_CONFIG)

| Count | api_base_url |
|---|---|
| 1 | `https://api.0x8099.ccwu.cc` |
| 1 | `https://subcn.231017.xyz` |
| 1 | `https://api.yunjie.host/v1` |
| 1 | `https://api.1cfy.top` |
| 1 | `https://www.cfgo.shop` |
| 1 | `https://sub2api.us.xiaofantuan.cn` |
| 1 | `http://159.65.136.59` |
| 1 | `http://api.haomao.chat:8080` |
| 1 | `https://api.holdzywoo.top/v1` |
| 1 | `https://www.brainary.cn` |
| 1 | `http://168.138.75.153:8080` |
| 1 | `http://172.93.32.55:8080/` |
| 1 | `https://sub2api.applane.qzz.io` |
| 1 | `https://sub2api.jobao.win` |
| 1 | `https://api.htops.top` |
| 1 | `https://api.lingzhiai.cloud/v1` |
| 1 | `http://43.163.7.45:8080` |
| 1 | `https://key.benniao.run` |
| 1 | `https://subss.miaolme.com` |
| 1 | `https://abfoods.cc/` |
| 1 | `https://66.42.58.167:8443/` |
| 1 | `https://sub2api.mel0dy.cc` |

## Sensitive-substring hits (0 hosts)

_No hosts surfaced sensitive substrings under the FP-gated regex set._

## DCWF stance

Per-IP investigation harness executed across 491 cohort hosts. 420 alive with banner+aimap+APP_CONFIG+openapi+models signals captured. Platform distribution: Sub2API=316, unknown=61, Grok2API=39, cousin=2, QClaw=1, OpenClaw=1. Host-class distribution: D=327, unknown=40, A=26, E=25, B=2. 0 hosts with sensitive substring hits (verbatim listed above).

Per-IP records: `~/syllabus/cohort-perip/<ip>.json`
Master CSV: `~/syllabus/cohort-perip-master.csv`
Master JSON: `~/syllabus/cohort-perip-master.json`

Identity-surface only; NO POSTs; Mullvad VPN active throughout.
