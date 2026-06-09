# Cat-53 - Federated Learning (Shodan query catalog)

**Survey date:** 2026-06-09
**Population sweep window:** 06:35–06:42 UTC
**Operator:** NuClide / Cat-53 Federated Learning research program

## Verified dorks

### FATE (WeBank / LF AI)

| Dork | Total | After --clean | Notes |
|------|-------|--------------|-------|
| `http.title:"FATE Board"` | 12 | 12 | The canonical FATEBoard title dork. Lowercase `fateboard` returns 0; case-sensitive on Shodan title index. |
| `http.html:"FATEFLow"` | 2 | 1 | FATEFlow REST API surface. Tiny but real. Distinct from FATEBoard. |
| `http.html:"server.board.login.username"` | 0 | 0 | Default-cred body marker - null on Shodan. Likely defender-cleaned, route to active probe. |
| `http.title:"fateboard"` | 0 | 0 | Case mismatch on Shodan index. Do not re-run. |
| `port:8080 "fateboard"` | 0 | 0 | No 8080-anchored hits. |
| `port:9380 "FATE"` | 0 | 0 | FATEFlow REST 9380 not banner-indexed. Route to scanner. |
| `port:4670 "eggroll"` | 0 | 0 | Eggroll cluster manager Shodan-dark. |
| `html:"FATEBoard"` | 0 | 0 | Bare-keyword body dork - null. |

**FP trap:** the literal `fateboard` (lowercase) returns 0 hits but `"FATE Board"` (CamelCase, space) returns 12. Lock to case-sensitive variant. Verified 2026-06-09.

### Flower (flwr)

| Dork | Total | After --clean | Notes |
|------|-------|--------------|-------|
| `ssl.cert.subject.CN:"superlink"` | 15 | 13 | High-quality cert-based fingerprint. 2 CDN drops. |
| `port:9092 "grpc"` | 3 | 3 | Tight, plausible Fleet-service tail. |
| `port:9091 "grpc"` | 201 | 196 | **FP-suspect.** Port 9091 is widely used (Prometheus, Confluent Schema Registry, generic gRPC); the dork over-broadcasts. Per Insight #15 (~50% rule) expect ≤50% real Flower. Send to scanner + aimap. |
| `port:9093 "grpc-status"` | 0 | 0 | Surprising - expected this as the canonical Exec/Control port. Either gRPC-over-TLS hides the status string from Shodan, or port:9093 banners are sparse. Route to scanner. |
| `"flwr.proto"` | 0 | 0 | Body dork too specific to be Shodan-indexed. |

**FP trap:** `port:9091 "grpc"` is the broad-net dork. Mark every IP from it as Tier-3 candidate, require aimap + scanner verification before counting.

### NVFlare

| Dork | Total | After --clean | Notes |
|------|-------|--------------|-------|
| `http.title:"NVFLARE Dashboard"` | 0 | 0 | Either everyone's patched (CVE-2026-24178), or population was always gRPC-only. |
| `http.html:"nvflare-dashboard/api/v1"` | 0 | 0 | Same as above. |
| `http.title:"NVIDIA FLARE"` | 0 | 0 | Generic variant - null. |
| `"sp_end_point" "primary_sp"` | 0 | 0 | Body of overseer heartbeat response - null. |

**Inference:** NVFlare is entirely Shodan-dark on commodity dorks. Population exists per OSINT (medical consortia, Owkin, Rhino), but is structurally not on the public HTTP-banner index. **Route to Censys CT-log + scanner.**

### OpenFL

| Dork | Total | After --clean | Notes |
|------|-------|--------------|-------|
| `port:50051 "openfl"` | 0 | 0 | Body-anchored - null. |
| `"openfl.federation"` | 0 | 0 | Proto package name not banner-indexed. |
| `ssl.cert.subject.O:"smallstep"` | 0 | 0 | step-ca org cert null on Shodan. |

**Inference:** gRPC-over-mTLS confirmed Shodan-dark. Upstream is archived (community migration to Flower). Route to Censys.

### FedML / TensorOpera

| Dork | Total | After --clean | Notes |
|------|-------|--------------|-------|
| `ssl.cert.subject.CN:"*.fedml.ai"` | 0 | 0 | Wildcard cert not in Shodan index. |
| `ssl.cert.subject.CN:"fedml.ai"` | 0 | 0 | Bare-domain CN - null. |
| `port:1883 "fedml"` | 0 | 0 | MQTT broker FedML-tagged - null on Shodan. |
| `ssl:"tensoropera"` | 4 | 0 | All 4 CDN-dropped. Route to Censys. |

**Inference:** Self-hosted FedML MQTT brokers are not banner-indexed against the brand string. **Route to Censys + active MQTT probe.**

## Totals

| Bucket | IPs |
|--------|-----|
| FATE (Board + Flow) | 13 |
| Flower (cert + port:9092 + port:9091-tier3) | 212 |
| NVFlare | 0 |
| OpenFL | 0 |
| FedML | 0 |
| **Total unique IPs harvested** | **223** |

## Stage 0 closing notes

- Population is heavily Shodan-dark - consistent with FL = gRPC-over-TLS + research-consortium + on-prem deployment baseline. Three of five platforms returned 0 hits on every dork tier.
- **Stage 0b Censys is now load-bearing**, not optional. NVFlare, OpenFL, FedML populations only exist there.
- Flower port:9091 dork is the FP-suspect tail per Insight #15 - Stage 0c scanner banner-grab + Stage 1b aimap fingerprint must filter it before any population number is published.
- FATE harvest is small (~13) but high-yield: every FATEBoard hit is a default-cred candidate + auth-off REST API candidate.

## Source

- Harvest method: `jaxen hunt --clean --max 500` against Shodan REST API (key live, 9065 query credits at start, ~30 burned this stage).
- Storage: `shodan/cat53-fl-2026-06-09/empire.db` (223 distinct IPs, 225 (ip,port) tuples).
- IP list: `shodan/cat53-fl-2026-06-09/ips.txt`.
