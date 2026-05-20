# DePaul University: Campus-Wide Port-3000 Population — Live Open WebUI Auth-On, DHCP-Rotated Hosts, Mixed Student Dev Work

_NuClide Research · 2026-05-19_

---

## Summary

DePaul's institutional network surfaces 20+ hosts with port 3000 open when scoped via Shodan `org:"DePaul University"`. Only 4 of these have HTTP title `"Open WebUI"`; the rest are student dev servers (React apps, project portfolios, course assignments). Of the 4 Open WebUI hosts, one was the original signup-open target captured during Stage-0 (`lpc-eduroam-187-239.eduroam-employee.depaul.edu`) — that hostname's DHCP-assigned IP has since rotated and the host is no longer reachable. Three other employee-network Open WebUI hosts are visible in Shodan; one (`140.192.183.141`) was verified at probe time as Open WebUI v0.4.7 with `enable_signup: false` (auth-on, NOT exploitable for takeover). Documents the DHCP-rotation operational pattern + the "port 3000 ≠ Open WebUI" false-positive class at the .edu institutional scope.

---

## Infrastructure

| Field | Value |
|---|---|
| Org | DePaul University |
| Network ranges observed | `140.192.x.x` (employee + eduroam) and `75.102.x.x` (loop wireless + resnet + depaulsecure + guest) |
| Subdomain patterns | `*.eduroam-employee.depaul.edu`, `*.eduroam-student.depaul.edu`, `*.depaulsecure-student.depaul.edu`, `*.loop-wireless.depaul.edu`, `*.lpc-wireless.depaul.edu`, `*.rrh-resnet.depaul.edu`, `*.unh-resnet.depaul.edu`, `*.loop-depaul-guest.depaul.edu`, `*.openarea-sac-lev-occ.depaul.edu` |
| Total hosts with port 3000 open (per Shodan `org:"DePaul University" port:3000`) | 20+ as of 2026-05-19 sweep |
| Of those, with HTTP title "Open WebUI" | 4 (one DHCP-rotated, three still indexable) |

---

## Stage-0 target (DHCP-rotated)

`lpc-eduroam-187-239.eduroam-employee.depaul.edu` (`140.192.187.239:3000`) — at Stage-0 capture time, returned Open WebUI v0.3.32 with `enable_signup: true` per the Shodan body cache. By the time wave-1 direct verification ran, the DNS hostname no longer resolved (the eduroam DHCP lease rotated). The IP `140.192.187.239` itself was probed indirectly via Shodan-cached data; not re-verified live.

This DHCP-rotation behavior is characteristic of `eduroam-employee` subnets — devices on the network get short-lived DHCP leases, and hostnames embed the assigned IP octets (so when the lease rotates, the hostname rotates too).

---

## Wave-1 direct-verified host: `140.192.183.141:3000`

`GET http://140.192.183.141:3000/api/config` returned 200 with:

```json
{
  "status": true,
  "name": "Open WebUI",
  "version": "0.4.7",
  "default_locale": "",
  "oauth": {"providers": {}},
  "features": {
    "auth": true,
    "auth_trusted_header": false,
    "enable_ldap": false,
    "enable_api_key": true,
    "enable_signup": false,
    "enable_login_form": true
  }
}
```

**Class memberships observed:**
- `enable_signup: false` — public self-registration DISABLED on this host. No signup-open class. NOT exploitable for takeover.
- `enable_api_key: true` — post-authentication API-key minting enabled (requires an existing authenticated account first).
- Version 0.4.7 — older release-line.
- `auth: true`, `enable_login_form: true` — standard auth-on posture.

So this DePaul host (presumably a faculty/staff laptop on eduroam-employee) has a CORRECT Open WebUI configuration. Contrasts with the Stage-0 captured signup-open behavior on the other DHCP-rotated host.

---

## Additional Shodan-visible hosts (not direct-probed for `/api/config`)

Per Shodan `hostname:depaul.edu product:"Open WebUI"` and `org:"DePaul University" port:3000`:

- `loop-eduroam-183-141.eduroam-employee.depaul.edu` → 140.192.183.141 (= the verified host above)
- `lpc-eduroam-187-239.eduroam-employee.depaul.edu` → 140.192.187.239 (rotated, no longer reachable)
- `lpc-eduroam-186-106.eduroam-employee.depaul.edu` → 140.192.186.106 (no `/api/config` response at probe time — direct probe got "all connection attempts failed")
- `loop-eduroam-183-195.eduroam-employee.depaul.edu` → 140.192.183.195 (no `/api/config` response at probe time)

Of these 4 employee-network OW-titled hosts, only `140.192.183.141` was live + reachable at probe time. Two others did not respond to direct TCP connect. One had rotated away.

---

## False-positive observation: port 3000 ≠ Open WebUI

The Shodan `org:"DePaul University" port:3000` query returned 20+ hosts. Of those, only 4 have HTTP title `"Open WebUI"`. The other 16+ have varied HTTP titles indicating they are student dev servers, course projects, or vanity sites:

- `Fuzzy Cheetahs Softball` (likely a node.js / Vite student project portfolio)
- `Lifespring Health Initiative — Transforming Lives Through Health Communication in Malawi` (student health-communication project)
- `Justice in a Flash · Child Support & Alimony Enforcement (Illinois / Cook County)` (student civic-tech project)
- `React App` (Vite / Create React App default placeholder — multiple instances)
- (others with empty / generic titles)

**Class observation**: at the .edu institutional scope, port 3000 is a heavily-shared port between Open WebUI, Grafana, Node.js dev servers, Vite/CRA student projects, and arbitrary HTTP services. Filtering by `port:3000` alone produces a high-FP set; anchoring on `http.title:"Open WebUI"` (or `/api/config` body match) is required to disambiguate.

---

## Operator attribution (per Insight #4)

- **Org**: DePaul University (per Shodan org-tag on these IPs; ARIN registration of `140.192.0.0/16` and `75.102.0.0/16` ranges)
- **Network type**: residential / wireless / eduroam (mostly DHCP-assigned IPs on student / employee wireless networks, not faculty / lab static IPs)
- **Implication**: most port-3000 services on DePaul's network are user-spawned on personal devices, not institutional services. The institutional posture: any user on campus wifi can stand up arbitrary services that become internet-accessible during their DHCP lease.

---

## Cross-tool confirmations

- aimap wave-1 (`-ports-class llm-gateway`) — surfaced `140.192.183.141:3000` Open WebUI; the other DePaul IPs were either not in the wave-1 target list or didn't respond
- Direct `/api/config` probes on the 4 OW-titled hosts — only `140.192.183.141` returned 200; the others returned connection errors or rotated away
- Shodan org-search — `org:"DePaul University" port:3000` returned 20+ hosts with varied titles (the FP observation)

---

## Class-membership summary (no tier labels per survey convention)

- DHCP-rotation operational class — OBSERVED (Stage-0 captured signup-open host's hostname no longer resolves at wave-1)
- Live OW auth-on class — OBSERVED on `140.192.183.141`
- Multiple-OW-instance-per-institution class — OBSERVED (4 different employee hosts running OW at various times)
- Port-3000 false-positive class at .edu institutional scope — OBSERVED (only 4/20+ port-3000 hosts are actually OW)
- Wireless/residential user-spawned service exposure class — OBSERVED (institutional posture allows any user on campus wifi to publish internet-reachable services)

Data-membership (which specific user, which specific OW account, which specific session) not tested per restraint ethic.

---

## Discovery method

- **Initial surfacing**: Stage-0 dork-map of 1,629 verified Shodan dorks scoped to `hostname:.edu` — `lpc-eduroam-187-239.eduroam-employee.depaul.edu` hit the Open WebUI title-and-port dork.
- **Wave-1 verification**: direct `/api/config` probe found the original hostname unresolvable (DHCP rotation); searched `org:"DePaul University" port:3000` to find adjacent hosts; probed the 4 OW-titled adjacent hosts and verified `140.192.183.141` live with auth-on posture.

---

## Source artifacts

- Workspace: `~/recon/edu-llm-infra-2026-05-19/`
- Initial probe: `arsenal-out/critical-openwebui-results.json` (DePaul section, showing DNS_FAIL on original hostname)
- Wave-1 DePaul re-search: `stage2-wave2/gap-fill.json` (DePaul-141, DePaul-106, DePaul-195 sections)
- aimap-profile: `arsenal-out/aimap-profile/depaul.json`
- Shodan org-search output (20+ port-3000 hosts): captured during wave-1 investigation

---

## Pattern observation — campus-wireless service exposure

DePaul's `eduroam-employee` subnet appears to assign DHCP IPs that are then visible from the public internet. Combined with the institutional culture of standing up React/Vite/Node services on port 3000 (for development, coursework, demos), the network surfaces a dense + ephemeral population of services. Most are short-lived and benign. A small fraction (~20%) are Open WebUI — of those, deployment posture varies per individual.

This is the opposite of USM's centrally-managed JupyterHub fleet pattern. DePaul's exposure profile is "campus network as public-internet sandbox" — useful to know when scoping disclosures: per-host outreach to individual users may be more effective than central IT for ephemeral / personal-device exposures.
