# Medical & Edge AI — Shodan Query Catalog (Survey 28)

_NuClide Research · 2026-05-15_

Survey target: medical imaging AI infrastructure (MONAI Label, MONAI Deploy /
Clara, Orthanc, dcm4che) and edge-AI compute (NVIDIA NIM containers, Triton-
hosted Clara/MONAI models, Holoscan, Jetson). DICOM-class platforms carry PHI
by definition — HIPAA tier handling required.

Discovery anchor (port-first per Insight #21):
- Tier-A high-signal ports: **8042** (Orthanc HTTP), **8043** (Orthanc HTTPS),
  **4242** (Orthanc DICOM TCP), **11112** (DICOM standard TCP).
- Tier-A broad ports: **8000** (MONAI Label, NVIDIA NIM, uvicorn/FastAPI),
  **8080** (dcm4chee-arc, DICOMweb), **8443** (dcm4chee-arc TLS, Orthanc TLS).

aimap fingerprints (5 new, v1.9.4+, 2026-05-15):
- MONAI Label Server — `/info/` + json_field `trainers`/`strategies`/`scoring`/`datastore`
- Orthanc DICOM Server — `/system` + json_field `DicomAet`/`ApiVersion` + `Orthanc`
- dcm4che / dcm4chee-arc — `/dcm4chee-arc/aets` array + `/dcm4chee-arc/` html
- DICOMweb (QIDO-RS) — `/studies` (or `/dicomweb/studies`) array + DICOM tag `0020000D`
- NVIDIA NIM — `/v1/metadata` + json_field `modelInfo`

---

## Tier-1 brand dorks (when Shodan is live)

| Q-ID | Query | Expected use |
|---|---|---|
| Q1 | `"Orthanc Explorer"` | Orthanc web UI title — high precision |
| Q2 | `"orthanc" port:8042` | Orthanc REST on canonical port |
| Q3 | `http.title:"Orthanc Explorer"` | UI title — disambiguates from any "orthanc" mention |
| Q4 | `"Server: Mongoose" port:8042` | Orthanc 1.x embeds Mongoose HTTP server on 8042 — high-precision header |
| Q5 | `port:8042 "DicomAet"` | `/system` JSON leakage in banner |
| Q6 | `"MONAI Label"` | MONAI Label info-page string |
| Q7 | `"monai-label-app"` | MONAI Label internal class string |
| Q8 | `"MONAI Inference"` | MONAI Deploy MAP inference service |
| Q9 | `"NVIDIA Triton" "clara"` | Clara models running on Triton |
| Q10 | `"NVIDIA Triton" "monai"` | MONAI Deploy / Holoscan over Triton |
| Q11 | `"dcm4che" OR "dcm4chee-arc"` | dcm4che archive deployments |
| Q12 | `http.title:"dcm4chee Archive UI"` | dcm4chee-arc web UI |
| Q13 | `"keycloak" "dcm4chee"` | Keycloak-fronted dcm4chee (auth state may be misconfigured) |
| Q14 | `"NVIDIA NIM" OR "nvcr.io/nim/"` | NIM container metadata |
| Q15 | `"holoscan" port:8000,8081,8443` | Holoscan HTTP surface (uncommon) |
| Q16 | `"jetson" "jetpack"` | Jetson edge devices reporting JetPack version |
| Q17 | `"DeepStream"` | NVIDIA DeepStream SDK exposure |

## Tier-2 favicon / TLS pivots

| Q-ID | Query | Notes |
|---|---|---|
| Q18 | `http.favicon.hash:<orthanc-hash>` | Compute hash from a live Orthanc and pivot |
| Q19 | `ssl.cert.subject.cn:"*.dcm4che.org"` | Project domains |
| Q20 | `ssl.cert.subject.cn:"*.orthanc-server.com"` | Vendor cert |
| Q21 | `org:"Mayo Clinic" port:8042,8043,8080,8443` | Hospital ASN sweeps — example pattern |
| Q22 | `org:"National Health Service" port:8042,11112` | NHS England |
| Q23 | `org:"Hospital" port:8042,4242,11112,8043` | Generic hospital org filter |

## Tier-3 cross-protocol DICOM

DICOM C-FIND/C-MOVE on TCP — protocol-strict probe required, not HTTP.

| Q-ID | Query | Notes |
|---|---|---|
| Q24 | `port:104 dicom` | Standard DICOM port 104 (rarely on internet) |
| Q25 | `port:11112` | Common alternate DICOM port — bare TCP, fingerprint via aimap TCP probe |
| Q26 | `port:4242 "Orthanc"` | Orthanc DICOM TCP banner |

## FP traps already documented (do not re-run)

- **Port 4242 ≠ always Orthanc.** Some Postgres deployments and at least one
  game server use 4242. Probe with the DICOM A-ASSOCIATE handshake or pivot
  to the same host's port 8042/8043 for HTTP confirmation. Do not classify
  on TCP banner alone.
- **`"orthanc"` (lowercase, naked dork)** matches research-tool source-code
  mirrors and forum posts indexed by Shodan's HTML scraper. Anchor to port
  8042/8043 or to the `DicomAet` JSON field.
- **`product:"NVIDIA"`** is too broad — captures GPU drivers, Jetson default
  banners, gaming servers. Conjoin with port + service path.
- **DICOMweb `/studies` returning `[]`** is a 200 but content-free; classify
  as "exposed endpoint with no content" — operator-empty archive, distinct
  from gated. Use the DICOM tag key (`0020000D`) anywhere in body as the
  identity-conjunct, not the array itself.

## Verification protocol (per host)

```bash
# Orthanc REST
curl -s --max-time 6 http://<ip>:8042/system | jq '{Name,Version,ApiVersion,DicomAet}'
curl -s --max-time 6 http://<ip>:8042/statistics  # study/series/instance counts — restraint: names only
curl -s --max-time 6 http://<ip>:8042/studies | jq 'length'  # study count

# MONAI Label
curl -s --max-time 6 http://<ip>:8000/info/ | jq '{name,version,labels,models:(.models|keys)}'

# dcm4chee-arc
curl -s --max-time 6 http://<ip>:8080/dcm4chee-arc/aets | jq 'length'

# DICOMweb
curl -s --max-time 6 http://<ip>:8080/dicomweb/studies | jq '. | length'

# NVIDIA NIM
curl -s --max-time 6 http://<ip>:8000/v1/metadata | jq '.modelInfo[].shortName'
```

## Ethical-stop boundary

DICOM endpoints carry PHI by definition. The restraint ethic applies in full:
**enumerate count, not content.** Pull study/series/instance counts from
`/statistics`; pull study UIDs only to the extent needed to confirm presence
of real (vs test) data; never retrieve any DICOM instance (`/instances/{id}/file`
or `/wadors/.../frames/...`). Patient-name / patient-ID fields are the finding —
their **existence** is the disclosure trigger, never their values.
