---
type: host
---

# NATS JetStream: ParamWallet Production Ledger + AI Pipeline (Open Pub/Sub)
_Survey date: 2026-05-09 | Operator: ParamWallet (paramwallet.com) | Severity: CRITICAL_

## Summary

`141.148.212.34` (Oracle Cloud Mumbai). Production NATS JetStream cluster running an **AI document-processing pipeline coupled to a private blockchain ledger**. NATS protocol port 4222 advertises no auth requirement; unauthenticated clients can list streams, read all message contents, and publish to any subject. Workspace `hil-taloja` (likely Hindustan Infrastructure Ltd. Taloja, Mumbai industrial area). TLS cert `*.paramwallet.com` ties the host to ParamWallet, a fintech wallet/payment platform. AI pipeline (`AI_TASKS`, `DOCUMENTS`) feeds a smart-contract gateway (`GATEWAY`, `TRANSACTIONS`, `LEDGER_NODES`, `OFFCHAIN`). An attacker on the open NATS port can inject ledger transactions, poison AI classifications, and alter document state-machine transitions.

<!-- ksat-tag:auto-generated:start -->
## DCWF KSAT coverage

Auto-derived from DCWF AI work-role rule files (`ksat-tag`).

- **672 (AI Test & Evaluation Specialist):** K7003, K7004, S7068, S7070, S7075, T5904, T5919
- **733 (AI Risk & Ethics Specialist):** K7040, T5868
- **overlap (Common AI KSATs (all 5 roles)):** K1158, K1159, K22, K6900, K6935, K7003, K942

<!-- ksat-tag:auto-generated:end -->

## Identity & Stack

| Field | Value |
|---|---|
| IP | 141.148.212.34 |
| Cloud | Oracle Cloud, Airoli/Mumbai IN |
| Cert | `*.paramwallet.com` (Sectigo RSA DV) |
| NATS version | 2.10.29 (jetstream enabled, file storage at `/data/jetstream`) |
| Open ports | 22 (SSH 8.2p1), 443 (nginx 1.18, *.paramwallet.com cert, 502 Bad Gateway), **4222 (NATS, no auth)**, **8222 (NATS monitoring HTTP)**, 8080+8443 (Jenkins 2.401.1), 9000 (SonarQube), 4444, 7946, 8001 |
| Ledger software | Custom, identified by `node_id`, `pubkey`, `raft_addr`, `version: 0.9.4` in KV_LEDGER_NODES |
| Pipeline ID | `pipe:sys:define-schema-v1` |
| IPFS reference | `ipfs://QmVzWZ1mukYV3tukFQmxHJ6AoSm9GMJv7fsjWHh5Tt2KCX` (schema doc) |

## Stream Inventory (12 streams, all readable + writable unauth)

| Stream | Subjects | Retention | Storage | Purpose |
|---|---|---|---|---|
| **AI_TASKS** | `ai.extract`, `ai.predict.*`, `ai.anomaly`, `ai.classify` | workqueue | memory | AI inference task queue |
| **DOCUMENTS** | `documents.raw.*`, `documents.processed.*` | limits (7d) | file (2GB) | Document state machine |
| **GATEWAY** | `gateway.>` | limits (7d) | file (1GB) | API/portal ingress |
| **TRANSACTIONS** | `transactions.pending`, `transactions.confirmed` | workqueue | file | Pending → confirmed ledger txns |
| **OFFCHAIN** | `offchain.define.*`, `offchain.config.*`, `offchain.registry.*`, `offchain.txn.*` | limits | file | Off-chain state |
| **STATE_MACHINE** | `sm.transition.*`, `sm.created.*` | limits | file | Pipeline state transitions |
| **SYNC** | `sync.confirmed.*` | limits | file | Inter-node sync |
| **NOTIFICATIONS** | `notifications.intent.>` | limits | file | Internal notifications |
| **KV_GATEWAY_CACHE** / `_CONFIG` / `_BATCHES` | `$KV.GATEWAY_*.>` | limits | file | KV state |
| **KV_LEDGER_NODES** | `$KV.LEDGER_NODES.>` | limits | file | Live ledger node registry |

## Decoded Live Data

### KV_LEDGER_NODES.node-1 (current state)
```json
{
  "node_id": "node-1",
  "pubkey": "0x043f0c2a559a16da34193f8d88aeee733330ead3cc932ebff1982348f4dab47f80fdcff989e660b51d668a3a96ef37f2738fea51d462c6745085f7704ca4c0d424",
  "raft_addr": "12.0.1.186:7004",
  "state": "active",
  "version": "0.9.4",
  "timestamp": 1778364328
}
```
The ledger node's secp256k1 public key, internal raft consensus address, and software version are leaked. Version `0.9.4` of a custom ledger pre-1.0. Likely undocumented externally.

### transactions.pending (4 messages, all "Commerce" KYC schema definitions)
Each transaction defines a `Broker` schema with **L_AddressLocality, L_City, L_Country, L_Department, L_Description, L_Email, L_Identifier, L_LegalName, L_Organization, L_PostalCode, L_Region, L_StreetAddress, L_TaxID, L_Telephone**.
- `from`/`nodeID`: `0x32709F05Ca0c385d75B029509c90859bf03a14FB`
- Workspace: `hil-taloja`
- All transactions are signed (`fromSignedHash`, `nodeSignedHash`, both 65-byte ECDSA)

### gateway.notify (batch.completed)
```json
{
  "trigger": "batch.completed",
  "pipelineId": "pipe:sys:define-schema-v1",
  "workspace": "hil-taloja",
  "payload": {"status": "completed", "submitted": 1, "synced": 0, "total": 1}
}
```

## Attack Chain (no auth required end-to-end)

```
attacker → nats://141.148.212.34:4222 (CONNECT, no creds)
        ├── SUB ai.classify   → inject malicious classification labels into AI_TASKS workqueue
        ├── SUB documents.raw.* → read every raw document submitted to the pipeline
        ├── PUB transactions.pending {batchId, transactions:[{...crafted KYC schema...}]} → ledger ingestion
        ├── PUB gateway.ingest.high.pipe:sys:define-schema-v1.hil-taloja → inject batch into prod workspace
        └── PUB $KV.LEDGER_NODES.node-1 {state:"inactive"} → mark node down (denial via state poisoning)
```

The `auth_required: True` flag from `/varz` HTTP endpoint **is set in config but not enforced**, raw NATS protocol connect succeeds, returns PONG, and accepts subscriptions. Likely cause: a `no_auth_user` is configured in NATS server config granting anonymous connect to the system account.

## Severity Justification

1. **Production data**: timestamps (`createdAt: 1778067121735` ≈ 2026-05-06) confirm active pipeline.
2. **Multi-stream + multi-account leak**: 12 streams, 17 consumers, 27 API calls, 366KB JetStream storage.
3. **Crypto material**: secp256k1 pubkey of ledger nodes (signature forgery via key disclosure not directly possible, but transaction provenance/attribution analysis enabled).
4. **AI poisoning**: `AI_TASKS` is a workqueue with retention `workqueue`. Unauthenticated PUB to `ai.extract`/`ai.classify` will be dequeued by downstream consumers as legitimate work.
5. **Adjacent services**: same host runs Jenkins (CVE-laden 2.401.1), SonarQube on 9000, all reachable.

## Disclosure Targets

| Channel | Address |
|---|---|
| ParamWallet primary | security@paramwallet.com (verify), or via paramwallet.com contact form |
| Hosting abuse | abuse@oracle.com (Oracle Cloud Infrastructure) |
| WHOIS / domain | (lookup paramwallet.com WHOIS for registrant) |
| Indian CERT-In | incident@cert-in.org.in (cross-border financial regulator) |

## Remediation

1. Immediately set `auth_required: true` and **rotate or assign the `no_auth_user` to a deny-all account** (`accounts.{deny_pub:[">"], deny_sub:[">"]}`). Closes pub/sub.
2. Bind 4222 + 8222 to `127.0.0.1` or VPC-internal only; expose to clients via a TLS+JWT or NKey-authenticated leaf node.
3. Audit JetStream messages for adversarial publishes since stream creation (`first_ts: 2026-05-06T11:32:01.71Z`).
4. Rotate ledger node keypair if stream-write-as-node was possible (verify via signature replay).
5. Patch nginx 1.18.0 (CVE-2025-23419, CVE-2024-7347), Jenkins 2.401.1, SonarQube. All surface on the same host.
