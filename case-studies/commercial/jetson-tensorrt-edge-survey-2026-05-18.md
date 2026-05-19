---
title: "Jetson, TensorRT, and edge-AI: a population survey of NVR and inference exposure"
date: 2026-05-18
type: survey
sector: commercial
tags: [edge-ai, jetson, nvr, frigate, codeproject-ai, deepstack, motioneye, docker-registry, deception-fleet, insight-13, insight-32]
---

# Jetson, TensorRT, and edge-AI: a population survey of NVR and inference exposure

_NuClide Research · 2026-05-18 · 10,224 candidates harvested, 296 verified-unauth across 9 platform classes, two deception fleets identified (598 hosts)._

## Summary

The survey scoped as "Jetson / TensorRT edge" found that the dominant exposed
population on the public internet is not the Jetson hardware itself. It is the
edge-AI applications that ship with Jetson and run on similar hardware
elsewhere. The four largest classes are Frigate (205 unauthenticated of 447
reachable), CodeProject.AI (39 of 40), DeepStack (24 of 25), and motionEye (18
of 64). Frigate alone produced 15 hosts where `/api/config` returns YAML
containing back-end RTSP camera URLs with plaintext credentials.

Two multi-service deception fleets surfaced in Stage 2 verify and were
filtered before classification. A 22-host fleet served byte-identical
92-byte `Server: Triton` banners to Shodan and now serves
`Server: Icecast 2.4.4` on every path. A 576-host fleet matches dorks for
many products by rotating titles per request while serving GitLab markers in
a 137KB body. Both are documented in [Insight #32](../../methodology/insight-32-deception-fleet-multi-service-emulation.md).

## Thesis fit

The auth-on-default thesis predicts that products which ship without
authentication will appear at population scale with the unauth posture intact,
while products that ship auth-on will appear at population scale gated. This
survey confirms both directions on the same day:

- **Frigate (205 unauth of 447 reachable, 46%)** confirms the unauth direction.
  Auth was added default-on in Frigate 0.13. Of the 205 unauth instances, 99
  run 0.17.1, the current release, where fresh installs are gated. The upgrade
  path does not enforce auth even when fresh installs do. This is the
  load-bearing case for [Insight #13](../../methodology/insight-13-shipping-defaults-load-bearing.md).
- **Scrypted (0 unauth of 300 reachable, 0%)** confirms the auth-on direction.
  Scrypted ships an auth-required management console. At population scale every
  reachable instance enforces it. This is the falsification-confirmation for
  [Insight #25](../../methodology/insight-25-scrypted-class.md) the thesis
  predicts.

---

## Verified findings by class

| Class | Verified unauth | Reachable | Real rate | Severity tier |
|---|---|---|---|---|
| Frigate NVR | 205 | 447 | 46% | up to CRIT (RTSP creds plaintext) |
| CodeProject.AI Server | 39 | 40 | 98% | HIGH (LLM-jacking compute theft) |
| DeepStack AI | 24 | 25 | 96% | HIGH (admin reachable) |
| motionEye | 18 | 64 | 28% | MED (camera config + recordings) |
| Docker Registry (unauth) | 5 | 5 | 100% | HIGH (image manifests pullable) |
| nvidia_smi_exporter | 5 | 5 | 100% | LOW (GPU info disclosure) |
| GPU Dashboards (SNU) | 2 | 2 | 100% | MED (researcher identity + topology) |
| gpustat-web | 1 | 1 | 100% | LOW |
| Russian "NVIDIA AI Hub" | 1 | 1 | 100% | INFO (brand misuse, unverified) |
| **Total verified-unauth** | **300** | **590** | **51%** | |

Triton (0 of 27, all 22 reachable hosts are deception-fleet) is recorded
separately. Scrypted (0 of 300, all auth-gated) confirms the
auth-on-default direction.

## Frigate severity breakdown (205 unauth)

| Severity | Count | What is exposed |
|---|---|---|
| **CRIT, RTSP credentials in plaintext** | 15 | `/api/config` returns YAML with `rtsp://user:password@...` URLs |
| HIGH, RTSP URLs and camera topology | 168 | `/api/config` reveals back-end camera URLs without plaintext credentials |
| MED, config exposed, no camera detail | 19 | `/api/config` 200 but generic (operator uses go2rtc proxy or embedded config) |
| INFO, version-only | 3 | `/api/version` 200 but `/api/config` unreachable |

Frigate version distribution top-5: 0.17.1 (99), 0.16.4 (19), 0.16.3 (16),
0.17.0 (15), 0.16.1 (8). The unauth population spans 0.12 through the current
0.17. Auth was added default-on in 0.13. The 99 instances running 0.17.1
without auth are the load-bearing observation: a current-release fresh install
requires auth, but a 0.12-era operator who has upgraded to 0.17.1 keeps the
unauth posture intact across the version line.

## RTSP-creds-in-plaintext Frigate hosts (sample 5 of 15)

| Host | Frigate ver | Cameras | Config size |
|---|---|---|---|
| `108.35.204.121:5000` | 0.17.1 | 5 | 65KB |
| `136.56.13.220:5000` | 0.17.1 | 5 | 27KB |
| `158.160.92.9:9000` | 0.16.4 | 2 | 33KB |
| `174.65.105.55:5000` | 0.17.0 | 5 | 29KB |
| `179.73.147.244:5000` | 0.14.1 | 1 | 26KB |

The remaining 10 are in `verify_frigate.jsonl`. Each carries the same exposure
shape: `/api/config` returns the full operator YAML, including
`go2rtc.streams.<camera>.url` entries with `rtsp://user:password@<ip>:<port>/...`
strings. An attacker who reads `/api/config` can connect directly to the
back-end IP camera and watch live video, bypassing Frigate entirely.

---

## Standout single-host findings

### F1. Frigate operator with 15 instances, 5 of them critical (cross-finding)

The 15 plaintext-credential Frigate hosts are 15 distinct operators on 15
different consumer ISPs (Verizon, Comcast, Spectrum, Yandex Cloud, Telefónica
Brazil, others). Each one independently exposed `/api/config` on a residential
or small-business uplink. The unauth posture is not a single misconfigured
fleet; it is the population behavior of a class of operators who run Frigate on
port 5000 directly from a home or office.

### F2. SNU GPU dashboard, researcher identity leak

`147.46.244.146:8001` runs a custom GPU monitoring dashboard at Seoul National
University. The `/api/snapshot` endpoint returns:

- 6-server cluster topology
- 30 A100-SXM4-80GB GPUs
- Researcher name `donghyun`
- Project name `openpi-actionrep`
- Full training command line
- NAS mount path `/mnt/snu_nas/data/donghyun/...`

This is academic-tier identity-and-infrastructure leak. The researcher's name,
the project they are training, the hardware they are training on, and the
storage path of their dataset are all reachable unauthenticated. The
`/api/metrics` endpoint on the second SNU dashboard (`147.46.240.92:50000`)
adds 4 SSH targets on non-standard port 16870 with the `iil@` username.

### F3. Auriga NVIDIA Isaac Lab / ROS 2 robotics pipeline (Docker Registry)

`47.93.158.253:5000` is an unauthenticated Docker Registry V2 on Aliyun CN.
The `/v2/_catalog` endpoint lists 15 repositories totaling ~150GB. The
manifests reveal a mobile autonomous robot development pipeline: the operator
builds multi-arch (aarch64 + x86_64) images for `base_chassis_navigation_arm`,
runs NVIDIA Isaac Lab inside the container, and uses ROS 2 for the robotics
middleware. Any internet-reachable client can `docker pull` the images.

### F4. Mexican telecom operator with RTX A6000 ($4-5K workstation GPU)

`189.155.64.244:9202` runs `nvidia_smi_exporter` on a residential UniNet
(`uninet.net.mx`) connection. The `/metrics` endpoint returns the GPU model:
`NVIDIA RTX A6000`, a premium workstation card priced $4,000-5,000. The
combination (premium hardware, residential consumer ISP, public exposure)
suggests a small-business or independent-researcher operator who installed
the exporter for personal monitoring and exposed the consumer-line public IP.
This is a low-severity info-disclosure finding on its own. As a chain
primitive (target identification for follow-on attacks) it is a useful
fingerprint.

### F5. Russian "NVIDIA AI Hub" brand misuse candidate

`193.58.122.16:3000` runs a Russian-language LLM proxy service at
`play2go.cloud`, advertising "free access to 200+ NVIDIA neural networks"
including Llama 3.1, DeepSeek, and Trellis 3D. The legitimacy of the
NVIDIA branding is not verified. The service may be an LLM-jacking-style proxy
that fronts customer LLM API keys, or a legitimate NVIDIA channel partner
(unlikely given hosting on `play2go.cloud` and Russian-only UX). Flagged for
follow-on attribution work.

---

## Deception fleets (filtered before classification)

### Fleet A: Triton 92-byte / Icecast pattern

| Field | Value |
|---|---|
| Stage 0 dork | `"Server: Triton" port:8000` |
| Candidates returned | 27 hosts |
| Fingerprint | byte-identical 92-byte `Server: Triton` JSON banner |
| Current state | 22 reachable, all return `Server: Icecast 2.4.4` empty body |
| Real Triton found | 0 |
| ASN spread | Linode, Leaseweb, Stark Industries (UA/HU/AL, bulletproof hosting), Oracle Svenska, Reliable Communications, Webhorizon, others |

### Fleet B: Shinobi / GitLab rotating-title pattern

| Field | Value |
|---|---|
| Stage 0 dork | `http.title:"Shinobi"` |
| Candidates returned | 1,926 IP:port (1,043 unique IPs) |
| Fingerprint | rotating titles per request (TamasiPHNAS, Cisco Codec, Acorn Management, wiportal-mobile, BigAnt Admin, Laravel, Shinobi, others); GitLab `og:site_name` in body; ~137KB response |
| Identified fleet hosts | 576 (30% of candidates) |
| Real Shinobi (body-marker pass) | 361 |
| ASN concentration | Aliyun CN, `101.200.0.0/16` heavy |

The diagnostic, recurrence, and procedural implications are in
[Insight #32](../../methodology/insight-32-deception-fleet-multi-service-emulation.md).

---

## Per-finding tool attribution

The four largest verified-unauth classes ran the full Stage 0-7 chain. Per
the methodology and the per-finding template, each finding records which tool
produced which signal. Below is the chain for the Frigate-RTSP-creds
class (the highest-severity tier in this survey).

### F-Frigate-15. 15 hosts leaking RTSP credentials in plaintext

#### What was found

`/api/config` on 15 Frigate instances returns the operator's YAML
configuration, including `go2rtc.streams.<camera_name>.url` strings of the
form `rtsp://<user>:<password>@<camera_ip>:<port>/<path>`. The credentials
are the operator's back-end IP camera credentials, embedded in the live
running Frigate config and served unauthenticated to any HTTP client that
requests `/api/config` over the public internet.

#### Why it is bad

**Verified**: an internet-reachable client reads `/api/config`, parses the
RTSP URLs, and gains direct access to the camera credentials. The operator's
own back-end cameras become directly viewable by anyone who can issue an
HTTP GET to the Frigate port.

**Inferred (not exercised per the restraint ethic)**: the credentials likely
work against the back-end IP cameras at their `rtsp://` URLs. We did not run
the connect probe. The chain step from "credential read" to "camera feed
viewed" is one VLC client away.

**Hypothesized**: the same credentials may be reused on adjacent services
(camera admin web UI, operator NAS, operator network gear) per the
known IP-camera-firmware default-credential reuse pattern. Not exercised.

#### Who it affects

The 15 operators are on consumer ISPs across 6 countries (US, Brazil,
Russia, Mexico, Italy, Argentina, others). Each is a residential or
small-business deployment running Frigate behind a residential or small-business
uplink. The downstream-affected parties are the operator themselves
(camera feeds), camera subjects (anyone visible in the camera frame), and the
operator's network (the back-end cameras and any pivoted device).

#### How it got exposed

Frigate's `/api/config` endpoint is intentionally readable from the web UI
because the UI needs the config to render the dashboard. Before Frigate 0.13
the API surface had no authentication layer at all. Frigate 0.13 added
authentication default-on. The upgrade path does not enforce the new default
for existing deployments. An operator who started on 0.12 and upgrades
through to 0.17.1 keeps the `auth: enabled: false` posture from their old
config. The current release ships secure for fresh installs; in-place
upgrades inherit the old posture.

This is the load-bearing case for [Insight #13](../../methodology/insight-13-shipping-defaults-load-bearing.md):
"shipping defaults are load-bearing because the population at any moment is a
mix of fresh installs and upgraded-from-old installs; the secure-default fix
takes one full upgrade cycle plus operator action to propagate."

#### Which tools contributed to the finding

| Stage | Tool | Contribution |
|---|---|---|
| 0 Discover | JAXEN | Shodan dork `http.html:"Frigate" port:5000` produced 447 IP:port candidates |
| 1 Fingerprint | aimap | `frigate` body marker + `/api/version` JSON shape confirmed Frigate class |
| 2 Verify | `verify_frigate.py` (custom probe; aimap deep-enum for Frigate is in v1.10 roadmap) | `GET /api/config`, parse YAML, check for `rtsp://` substring and `:.*@` credential pattern |
| 3 Attribute | VisorGraph | WHOIS + ASN per host; no cert pivots (Frigate is HTTP, no TLS by default on this class) |
| 4 Classify | aimap-profile | `commercial/residential` per WHOIS; 15 hosts flagged `clinical-tier urgency` due to camera feed access |
| 5 Ledger | VisorLog | 894 events ingested to `nuclide.db`, 15 with severity=`critical`, tags `NVR FRIGATE UNAUTH RTSP-CREDS-LEAK CAMERA-ACCESS` |
| 6 Score | VisorScuba | 894/894 "passing" against AI Security Baseline. 0 violations recorded. Methodology gap noted: NVR and edge-AI apps do not carry the LLM / INFERENCE / VECTOR-DB tags the Rego policies check for. The Rego baseline must add an NVR / camera-feed policy class for Frigate-tier findings to be scored as violations |
| 6 Exploit-rank | BARE | Top match `tp_link_ncxxx_bonjour_command_injection` at 0.515. Below the 0.6 first-party-authz threshold. No commodity-CVE chain applies; the exposure is shipping-default and operator-config, not a CVE class |
| 6 Adversarial corpus | VisorCorpus | 137 cases built for the survey, including kb_exfiltration (18), prompt_injection (16), infra_discovery (15), tenant_cross_leak (15). The Frigate-RTSP class contributed to the kb_exfiltration and infra_discovery sets |
| 7 Codify | this case study + Insight #32 | |

**Tools that ran and produced null signal for this class**:
- **VisorGoose**: 0 government TLDs in the Frigate candidate set (Frigate is consumer / commercial; no `.gov` operators). Null is a result.
- **VisorBishop / VisorSD**: ASN sweeps produced no new candidates beyond JAXEN's harvest for this class.
- **menlohunt**: 0 GCP-EASM matches (Frigate operators are on consumer ISPs, not GCP-hosted).
- **recongraph**: ran for the standout single-host findings; not material for the 15-host class.
- **nu-recon**: ran for the SNU GPU dashboards and the Russian NVIDIA Hub; not for the Frigate class.
- **VisorPlus**: orchestrator runner; the chain was driven by hand for this survey for the per-class control.
- **JS-bundle extract**: Frigate UI bundles do not embed secrets; the secrets are in the runtime config, not the bundle.

**Tools recorded as non-runs with reason** (per the methodology):
- **VisorHollow**: `[—] not applicable, Windows-only` (it is a Windows process-injection benchmark).
- **VisorAgent**: `[—] not fired at the survey set, ethical-stop. Active LLM exploitation is reserved for controlled targets`.
- **VisorRAG**: ran in adversarial-confirmation mode against the survey's VisorCorpus on a controlled target, not against the operator hosts.
- **cortex**: auth-context analyzer not material for an unauthenticated class.

**The load-bearing chain for this finding**: JAXEN -> aimap -> `verify_frigate.py` -> VisorLog -> case-study codification.

---

## Cross-survey and cross-finding analysis

### Real rate by platform class

The 51% verified-real rate aggregated across the survey confirms
[Insight #15](../../methodology/insight-15-dork-hits-vs-platform-instances.md)
at the multi-class population level. Per-class real rates split into two
populations:

- **Marker-strong classes**: CodeProject.AI (98%), DeepStack (96%), Docker
  Registry (100%), nvidia_smi_exporter (100%). The Shodan dork picks up the
  product-specific marker (a route, a header, a body string) that no other
  product emits. The real rate is near 100%.
- **Marker-weak classes**: motionEye (28%), Frigate (46%). The Shodan dork
  picks up a string that other products and honeypots also emit. The real
  rate drops sharply.

This generalizes the procedural rule:
**when constructing a dork, prefer a unique route or header over a title or
body word**. The dorks for the marker-strong classes anchor on a route
(`/v1/log/list`, `/admin`, `/v2/_catalog`, `nvidia_smi_exporter` metric prefix);
the dorks for the marker-weak classes anchor on a body word (`Frigate`,
`MotionEye`) that appears in fan pages, vendor marketing, and deception
fleets.

### Provider distribution

The unauth Frigate population skews consumer ISP heavy. The unauth Docker
Registries skew cloud heavy (Hetzner, Aliyun, Volcano Engine, HostPapa, APNIC).
The unauth CodeProject.AI population skews small-business or hobbyist VPS.
This is the **operator-tier-by-platform** pattern. The hosting provider is a
proxy for the operator's deployment maturity, and the deployment maturity
predicts the class of findings.

### Persistence

No prior survey covered the Frigate or CodeProject.AI population. This survey
establishes the baseline. A re-survey in 30, 90, and 180 days will produce
the first persistence measurement for the edge-AI population, comparable to
the agent-framework persistence measurement in
[Insight #30](../../methodology/insight-30-persistence-without-pressure.md).

---

## Methodology, what this case study adds

1. **[Insight #32 (new)](../../methodology/insight-32-deception-fleet-multi-service-emulation.md)**:
   multi-service deception fleets emulate target-specific services for
   Shodan scanners by rotating titles per request. Filter on body markers, not
   title. Two fleets identified in this survey (22 Triton, 576 Shinobi).
2. **[Insight #13 confirmed at the Frigate population level](../../methodology/insight-13-shipping-defaults-load-bearing.md)**:
   shipping defaults are load-bearing, and the upgrade path does not enforce
   them. The 99 unauth instances running Frigate 0.17.1, where fresh installs
   require auth, are the load-bearing observation.
3. **[Insight #15 generalized](../../methodology/insight-15-dork-hits-vs-platform-instances.md)**:
   the ~50% real-rate split by marker type. Marker-strong classes (route /
   header anchored) hit ~96-100%; marker-weak classes (title / body
   anchored) drop to ~30-50%. The procedural rule for new dork construction
   is to anchor on a route or header.
4. **[Insight #25 falsification-confirmation](../../methodology/insight-25-scrypted-class.md)**:
   Scrypted at 300/300 reachable instances all auth-gated confirms the
   auth-on-default direction of the thesis. The thesis is bidirectional and
   tested both ways in the same day.

## Honest negative space

- **VisorScuba scoring gap**: 894/894 events recorded as "passing" against
  the AI Security Baseline despite 15 critical RTSP-credential leaks. The
  Rego policies in the baseline check for LLM, INFERENCE, and VECTOR-DB
  tags; they do not check NVR or CAMERA-ACCESS tags. The scoring layer
  underreports edge-AI camera findings until an NVR / camera-feed policy
  class is added.
- **Shinobi auth-state on the 361 real instances**: the verify probe checked
  body markers and used the wrong API path for the auth-gate test. The auth
  state of the 361 real Shinobi instances is undetermined. Carry-forward to
  re-run the verify with the correct Shinobi API path.
- **RTSP/GStreamer port 8554 (~911 candidates)**: deferred. The probe is a
  different protocol (RTSP `DESCRIBE`, not HTTP). The marginal value over
  the Frigate findings already in hand was judged low for this session.
- **Jetson SSH (port 22, ~10 candidates)**: deferred. The default-credential
  test is write-tier and requires explicit operator authorization.
- **The deception fleet's other emulation targets**: today's survey caught
  the fleet on Triton and Shinobi. The fleet's rotating-title pool includes
  IP camera, NVR, ERP, GitLab, and PHP application titles. Cross-survey
  filtering of past harvests is the natural next pass.

## Disclosure queue (verified scope)

| Tier | Class | Count | Routing |
|---|---|---|---|
| **CRIT** | Frigate, RTSP credentials in plaintext | 15 | Per-operator disclosure via WHOIS abuse contact. Frigate-the-project is not the target (the framework added auth-on-default in 0.13); the deployments are. |
| HIGH | Frigate, RTSP URLs and topology exposed | 168 | Aggregate disclosure to the Frigate project; per-operator only for high-value targets |
| HIGH | CodeProject.AI, `/v1/log/list` unauth | 39 | Aggregate disclosure to the CodeProject.AI project; per-operator on a sample |
| HIGH | DeepStack, `/admin` reachable | 24 | Aggregate to DeepStack-AI (deepquestai); per-operator on a sample |
| HIGH | Docker Registry V2 unauth | 5 | Per-operator. Each registry is a distinct organization with a distinct chain. F1-mfgbot (Hetzner), F2-Harbor mirror (HostPapa), F3-NVIDIA GPU Operator mirror (Volcano Engine), F4-RAG-on-Jetson (APNIC JP), F5-Auriga Isaac Lab (Aliyun CN) |
| MED | motionEye | 18 | Aggregate to motionEye project |
| MED | SNU GPU dashboards | 2 | Per-operator to Seoul National University CERT |
| LOW | nvidia_smi_exporter | 5 | Per-operator on a sample; not all operators consider GPU model a sensitive leak |
| INFO | Russian "NVIDIA AI Hub" brand misuse | 1 | Forward to NVIDIA trademark / brand-protection if attribution work confirms it is not a legitimate NVIDIA channel partner |

## Toolchain provenance

```
Stage 0 Discover    JAXEN                   10,224 candidates across 6 dork batches
Stage 1 Fingerprint aimap                   9 platform classes confirmed
Stage 2 Verify      custom probes + aimap   296 verified-unauth, 2 deception fleets filtered
                    (verify_frigate.py, verify_codeproject.py, verify_nvr.py,
                     verify_scrypted.py, verify_shinobi.py, verify_triton.py)
Stage 3 Attribute   VisorGraph              ASN, WHOIS, jurisdiction per host
Stage 4 Classify    aimap-profile           tier per-finding (CRIT/HIGH/MED/LOW/INFO)
Stage 5 Ledger      VisorLog                894 events ingested to nuclide.db (0 deduped)
Stage 6 Score       VisorScuba              894/894 passing (gap noted, no NVR Rego policy)
Stage 6 Exploit     BARE                    max 0.598 motionEye Bavision-IP-cam; all under first-party-authz threshold; no commodity-CVE chain
Stage 6 Corpus      VisorCorpus             137 cases (77 HIGH, 26 MED, 19 LOW, 15 CRIT)
Stage 7 Codify      this case study + Insight #32
```

## See also

- [Insight #32, multi-service deception fleets](../../methodology/insight-32-deception-fleet-multi-service-emulation.md)
- [Insight #13, shipping defaults are load-bearing](../../methodology/insight-13-shipping-defaults-load-bearing.md)
- [Insight #15, dork hits vs platform instances](../../methodology/insight-15-dork-hits-vs-platform-instances.md)
- [Insight #25, Scrypted as the auth-on falsification confirmation](../../methodology/insight-25-scrypted-class.md)
- [Insight #1, protocol-strict probing self-filters honeypots](../../methodology/insight-01-protocol-strict-self-filters-honeypots.md)
- [Code-assistants population survey, 2026-05-18](./code-assistants-population-survey-2026-05-18.md), same-day partner survey establishing the per-finding tool-attribution template
- Raw harvest: `~/recon/jetson-tensorrt-2026-05-18/`
