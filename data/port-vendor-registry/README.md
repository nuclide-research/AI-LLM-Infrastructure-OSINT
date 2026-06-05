# Master Port / Vendor Registry

Collected 2026-06-05 from the nuclide-research GitHub repos. Single source of
truth for vendor -> port -> fingerprint -> dork mapping across the research project.

## Files

| File | Rows | What |
|------|------|------|
| `MASTER-port-vendor-registry.csv` | 410 | The merged registry. One row per vendor. |
| `port_classes.csv` | 174 | Port-level companion (aimap `-ports-class` profiles). Port is the key, not vendor. |
| `aimap.csv` | 196 | Raw aimap fingerprint extract (backbone). |
| `dorks.csv` | 421 | Raw Shodan dork extract (OSINT catalog + JAXEN). |
| `supplementary.csv` | 53 | Extra ports/auth from scanner, tiptoe, menlohunt, tome. |

## MASTER columns

`vendor, category, default_ports, protocol, shodan_dorks, probe_paths,
signature_markers, severity, auth_posture, auth_evidence, has_enumerator,
supplementary_notes, sources`

- `default_ports` — union across aimap + tome + scanner + menlohunt (`;`-joined).
- `shodan_dorks` — all dorks for the vendor (` | `-joined).
- `signature_markers` — body/header/json discriminators that ID the service.
- `auth_posture` — codified auth-on-default label from the curated
  `vendor-port-registry.csv` `default_auth` field, aggregated per vendor:
  `unauth-on-default` / `auth-on-default` / `mixed` / `trust-network-only`.
  Bracketed qualifiers carry the default-cred tell, e.g.
  `unauth-on-default [OFF (minioadmin:minioadmin)]`.
- `auth_evidence` — empirical backing from the nuclide.db event ledger
  (29,404 events), e.g. `ledger 2176/2176 unauth`. Format = `unauth/total surveyed`.
  Blank where the vendor was not surveyed.
- `has_enumerator` — aimap ships a deep enum_*.go for this vendor.
- `sources` — which repos contributed the row.

## Coverage

- 192 vendors with an aimap fingerprint
- 296 vendors with at least one Shodan dork
- 330 vendors with at least one port
- 293 vendors with a codified auth_posture
- 49 vendors with empirical ledger auth evidence
- 83 vendors with a deep enumerator
- 34 normalized categories

## Auth-on-default thesis (the research point)

Of the 293 vendors with a resolved posture:

| posture | vendors |
|---------|---------|
| unauth-on-default | 196 |
| mixed | 82 |
| auth-on-default | 13 |
| trust-network-only | 2 |

Empirical ledger confirms it at host scale: etcd 2176/2176, Consul 1827/1827,
Envoy Admin 33/33, OpenHands 136/136 — all unauth. Refutation cases the ledger
surfaces (surveyed population came back authed): OpenClaw 0/563, LangGraph 0/1.

## Source repos

aimap (fingerprints.go, port_classes.go, enum_*.go) · AI-LLM-Infrastructure-OSINT
(shodan/queries/ 32 category catalogs) · JAXEN · scanner · tiptoe · menlohunt · tome.

## Regenerate

`/tmp/port-harvest/merge.py` rebuilds MASTER from the four extract CSVs.
Re-clone aimap/JAXEN/tome to `/tmp/port-harvest/` and re-run the extractors to refresh.

## Known noise

A handful of dork-only vendors carry a category from the OSINT catalog that
differs from where aimap would file them (e.g. a TTS dork landing under a search
category). Vendor/port/dork data is correct; treat `category` as a soft grouping.
