# Keystone disclosure recipient resolution

Date: 2026-06-20
Purpose: document how the disclosure recipient for keyst.one was resolved, from primary
sources, before any message left.

## What was checked

| Source | Result |
|---|---|
| `keyst.one/.well-known/security.txt` | HTTP 404. No security.txt. |
| `keyst.one/security.txt` | HTTP 404. |
| `keyst.one/security` | HTTP 404. No published security policy page. |
| `KeystoneHQ/keystone3-firmware` SECURITY.md and `.github/SECURITY.md` | Absent. |
| Dedicated `security@keyst.one` | Not found in any vendor source. |

## What the vendor actually publishes

Primary source: the `## Contact` section of the firmware README in Keystone's own
canonical engineering repo, `KeystoneHQ/keystone3-firmware`, states verbatim:

> For support or inquiries, please contact us at eng@keyst.one

Address frequency across the KeystoneHQ org code (gh code search, literal `@keyst.one`):

```
  21  support@keyst.one     customer-facing support
   6  eng@keyst.one         engineering contact (README-published)
   5  renfeng@keyst.one     individual
   2  yu@keyst.one          individual
   1  sora@keyst.one        individual
```

## Decision

- To:  `eng@keyst.one`, the engineering address Keystone publishes in its own README,
  the closest thing they offer to a security or engineering disclosure channel.
- Cc:  `support@keyst.one`, the highest-attention customer-facing inbox; guarantees a human
  opens a ticket if engineering routing is slow.

No dedicated security mailbox exists, so both are used to maximize the chance the report
reaches an owner quickly. Individual addresses were not used.

Send identity: nicholas@nuclide-research.com (the researcher's real, attributable address).

## Status

SENT 2026-06-20 by Nicholas Kloster from nicholas@nuclide-research.com to eng@keyst.one,
Cc support@keyst.one, with the technical report attached. Disclosure clock started.

Open follow-on gates:
1. Vendor acknowledgement / remediation. If no response, a follow-up nudge is the next step.
2. ATLAS Keystone case study (AML.CS, oracle-tuned RAG poisoning) stays held until Keystone
   is remediated or agrees to attribution; then submit sanitized. The mitigation and
   sub-technique contributions for AML.T0070 do not depend on this and can go separately.
