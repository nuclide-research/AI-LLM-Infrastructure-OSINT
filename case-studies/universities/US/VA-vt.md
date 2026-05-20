# Virginia Polytechnic Institute and State University (Virginia Tech): DHCP Node

_NuClide Research · 2026-05-01_

---

## Summary

Virginia Tech has at least 4 Ollama-running IPs in Shodan; only `h80adf308.dhcp.vt.edu` (128.173.243.8) responds publicly. The DHCP hostname indicates a desktop or workstation on the campus DHCP pool rather than a dedicated server. 5 models, no cloud proxies.

---

## Infrastructure

| Field | Value |
|---|---|
| IP | 128.173.243.8 |
| Hostname | h80adf308.dhcp.vt.edu |
| Organization | Virginia Polytechnic Institute and State Univ. |
| Country | United States (Virginia) |
| Open ports | 11434 (Ollama, public) |

Additional VT IPs in Shodan (198.82.9.219, 198.82.11.101, 198.82.13.6) did not respond, likely firewalled or offline.

---

## Model Inventory

| Model | Size |
|---|---|
| `smollm2:135m` | 0.3GB |
| `qwen3:30b` | 18.6GB |
| `qwen:latest` | 2.3GB |
| `qwen2.5:32b` | 19.9GB |
| `llama3.2:latest` | 2.0GB |

---

## Findings

### F1: Researcher Workstation Publicly Exposed (LOW)

DHCP hostname pattern (`h80adf308.dhcp.vt.edu`) indicates a laptop or desktop on campus DHCP. No cloud proxies, no credential leak. Standard unauthenticated Ollama exposure on a workstation.

### F2: CVE-2025-63389 Injectable (HIGH)

All models injectable via unauthenticated `/api/create`.

---

## Remediation

```bash
OLLAMA_HOST=127.0.0.1:11434
systemctl restart ollama
```

---

## Disclosure

- **Discovered:** 2026-05-01
- **Status:** Pending outreach to VT IT Security (vt.edu)

---

## Second host (2026-05-19 .edu sweep): `hc652b6f5.dhcp.vt.edu`

A second VT-attributed host appeared during the 2026-05-19 .edu LLM-infra survey wave-1, running Open WebUI on a DHCP-assigned IP within VT's institutional range.

### Infrastructure

| Field | Value |
|---|---|
| IP | 198.82.182.245 |
| rDNS | `hc652b6f5.dhcp.vt.edu` (DHCP-assigned hostname pattern) |
| Second hostname | `office.scholars.bond` (resolves to same IP — third-party domain pointing into VT's network, see note below) |
| Org (WHOIS) | Virginia Polytechnic Institute and State Univ. (`OrgName: Virginia Polytechnic Institute and State Univ.`, `NetName: VPI-BLK`, CIDR `198.82.0.0/16`) |
| City | Prices Fork, VA |
| Open ports observed | 80 (Apache 2.4.58), 3000 (Open WebUI uvicorn) — Shodan reports 4 ports total; client-side direct probes to :80 returned connection-reset (likely ACL filtering my IP), Shodan sees it |

### Observations — Open WebUI v0.6.26

`GET http://hc652b6f5.dhcp.vt.edu:3000/api/config` returned 200 with:

```json
{
  "status": true,
  "name": "Open WebUI",
  "version": "0.6.26",
  "default_locale": "",
  "oauth": {"providers": {}},
  "features": {
    "auth": true,
    "auth_trusted_header": false,
    "enable_signup_password_confirmation": false,
    "enable_ldap": false,
    "enable_api_key": true,
    "enable_signup": true,
    "enable_login_form": true,
    "enable_websocket": true,
    "enable_version_update_check": true
  }
}
```

**Class memberships observed:**
- `enable_signup: true` — public self-registration class OBSERVED
- `enable_api_key: true` — post-authentication API-key minting enabled
- **Combined**: signup-open AND post-auth API-key minting both enabled means an attacker can self-register AND then self-mint API keys that bypass UI controls. This is a layered exposure not present on hosts with only one or the other flag.
- `enable_ldap: false`, no OIDC providers

### Notable details — `office.scholars.bond` second hostname

Shodan's hostname collection shows two distinct hostnames resolving to `198.82.182.245`:
- `hc652b6f5.dhcp.vt.edu` — VT's institutional DHCP naming convention
- `office.scholars.bond` — third-party domain registered under the `.bond` TLD (generic-TLD, sometimes used for casual/personal sites, dynamic DNS providers, or vanity domains)

The `.bond` TLD has no inherent meaning. Most plausible: a researcher or staff member at VT pointed a personal/vanity domain at their DHCP-assigned VT workstation IP. The Apache on :80 may be serving a different vhost depending on the Host header (the :80 redirect behavior visible in Shodan history vs the connection-reset to my direct probe suggests vhost-based routing or ACL).

### Cross-tool confirmations

- `aimap -ports-class llm-gateway` — surfaced Open WebUI service classification
- `visorbishop` (post-G5 fix) — tool-internal output: `open-webui auth=signup-open severity=critical` with `api_keys_enabled: True, signup_open: True` indicators (this host is the cleanest demonstration of the layered exposure)
- Direct `/api/config` probe — verified independently
- Shodan host record — confirms 4 open ports (with the Apache on :80 visible in Shodan's scan path that I couldn't reach from my client)

### Class-membership summary (no tier labels per survey convention)

- Open WebUI signup-open class — OBSERVED
- Post-auth API-key minting class — OBSERVED
- Combined "signup-open + API-key minting" elevation class — OBSERVED (layered: signup grants account, account grants API key, API key bypasses UI controls)
- Multi-hostname (DHCP + vanity-TLD) class — OBSERVED

Data-membership (specific signup, specific API-key generation, specific elevation flow) not tested per restraint ethic.

### Source artifacts

- Workspace: `~/recon/edu-llm-infra-2026-05-19/`
- Initial probe: `arsenal-out/critical-openwebui-results.json` (VT section)
- WHOIS: `arsenal-out/whois-5-confirmed.txt`
- Shodan host data: `arsenal-out/shodan-host-vt.txt` (shows both hostnames + the connection-resetting Apache on :80)
- visorbishop wave-1 revalidation: `stage2-wave2/arsenal/visorbishop-wave1-revalidate.json` (VT entry with `api_keys_enabled: True, signup_open: True` indicators)
