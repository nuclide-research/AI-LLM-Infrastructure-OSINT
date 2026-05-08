# VeroTX evidence bundle — 2026-05-07

Critical findings on `34.60.153.0` (VeroTX, Inc., AI procurement platform).

## What's in here

| File | Purpose |
|---|---|
| `MANIFEST.sha256` | SHA-256 of every evidence file. Header documents witness chain. |
| `MANIFEST.sha256.ots` | OpenTimestamps receipt anchoring the manifest hash to Bitcoin blockchain via 4 OTS calendar servers. |
| `findings.ndjson` | Per-finding NDJSON with severity + description + reference module. |
| `wayback-submissions.txt` | Wayback Machine submission URLs (third-party archive witnesses). |
| `raw/cap-*.http` | Full HTTP responses with server-asserted `Date:` headers + `X-Kong-Request-Id` / `X-Request-Id` / `X-Trace-Id` IDs that exist in the operator's own logs. |
| `raw/tls-*.txt` | TLS handshake transcripts with full cert chain (independently verifiable via crt.sh CT logs). |
| `raw/evidence-*.json` | Parsed JSON responses from Kong admin API + Keycloak OIDC discovery + FastAPI health/openapi. |
| `raw/visorgraph-*.json` | NuClide VisorGraph passive-recon graph nodes (cert pivots + service nodes). |
| `raw/bare-input.json` / `raw/bare-output.json` | NuClide BARE semantic exploit-module match (corpus 3,904 Metasploit modules). |

## Witness chain — five independent timestamp witnesses

The same evidence is anchored five separate ways. Repudiating it requires colluding with all five:

### 1. OpenTimestamps → Bitcoin blockchain (`MANIFEST.sha256.ots`)
The OTS receipt is submitted to four calendar servers. They batch incoming hashes and write Merkle roots to Bitcoin. Once a Bitcoin block confirms (~10-60 min after submission), the manifest hash is cryptographically anchored — no entity can change history. Verify with:

```
ots verify MANIFEST.sha256.ots
ots upgrade MANIFEST.sha256.ots  # after ~1h, fetches the Bitcoin attestation
ots info MANIFEST.sha256.ots
```

### 2. Wayback Machine snapshots (`wayback-submissions.txt`)
Each public-facing URL was submitted to web.archive.org for archival. Wayback then returns a permalink with timestamp. Independently verifiable via Internet Archive. Provides operator-independent proof that "this URL returned this content at this UTC time."

### 3. Server-asserted `Date:` headers (`raw/cap-*.http`)
Each HTTP capture preserves the response in full. Kong and FastAPI signed `Date: Fri, 08 May 2026 02:02:28 GMT` themselves — the operator's own infrastructure asserted the timestamp. Cannot be repudiated without the operator admitting their server's clock was wrong (which still places the event in time).

### 4. Operator-side log correlation (request IDs)
Captures preserve `X-Kong-Request-Id`, `X-Request-Id`, `X-Trace-Id` values minted by VeroTX's own systems. These IDs exist in the operator's own logs. The operator can verify the IDs match their records — denying authenticity requires fabricating the operator's own log database.

### 5. CT log cert evidence (`raw/tls-*.txt` + `raw/visorgraph-*.json`)
TLS handshakes captured every cert chain. The certs are issued by Let's Encrypt + Google Trust Services and submitted to Certificate Transparency logs (RFC 6962). The CT logs are append-only, distributed, and independently witnessed by Google, Cloudflare, DigiCert, Sectigo, and others. Verify any cert via crt.sh:

```
https://crt.sh/?q=auth.verotx.com
https://crt.sh/?q=demo.verotx.com
```

## Independent verification

Anyone with this directory can verify nothing has been tampered with:

```
sha256sum -c MANIFEST.sha256        # confirms file integrity
ots verify MANIFEST.sha256.ots      # confirms the manifest existed at the OTS-anchored time
```

If both pass, the bundle is authentic and the timestamps are real. If either fails, evidence has been tampered with.

## Researcher

Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com
ICS/OT specialist; CISA disclosures: CVE-2025-4364, ICSA-25-140-11.
