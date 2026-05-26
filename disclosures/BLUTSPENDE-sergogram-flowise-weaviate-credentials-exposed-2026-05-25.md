---
to: info@blutspende.net
cc: abuse@nuclide-research.com
severity: CRITICAL
ip: 37.60.255.27
institution: "blutspende.net — German blood donation organization. Internal IT documentation including plaintext server credentials, internal IP addresses, server names, BitLocker PINs, and blood donation operational data exposed in an unauthenticated Weaviate vector database at gpt.sergogram.com."
status: DRAFT
outcome: pending
date: 2026-05-25
---

**To:** info@blutspende.net
**Cc:** abuse@nuclide-research.com
**Subject:** CRITICAL: Ihre IT-Zugangsdaten und interne Serverinfrastruktur sind öffentlich zugänglich — sofortiger Handlungsbedarf / Your IT credentials and internal server infrastructure are publicly accessible — immediate action required

---

Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com

2026-05-25

---

This is an unsolicited good-faith disclosure under the NuClide Research umbrella (CISA disclosures CVE-2025-4364, ICSA-25-140-11). Severity: **CRITICAL**. Recommend immediate action — this is not a standard 90-day window issue. Your internal IT credentials are accessible to any internet user right now.

I am contacting info@blutspende.net because I could not find a published security contact. Please forward this to your IT security team immediately.

---

## What was found

Your organization's internal IT documentation has been ingested into an AI chatbot knowledge base operated by a third-party service provider (gpt.sergogram.com, hosted on a Contabo server in Nuremberg, Germany). That server's database is open to the public internet without any authentication.

We retrieved the following from the database without credentials:

**Plaintext server credentials:**
```
IH-DBSERVER\operator  Pw: operator
```

**Internal servers named in the corpus:**
- IH-DBSERVER, IH-DBBACKUP12
- KAR-IMPSRV-02, KAR-IMPSRV-03
- BAD-DA-02, BAD-DA-07

**Internal IP addresses visible in the corpus:**
- 172.23.111.65, 172.23.111.70
- 10.1.11.187, 10.1.11.191, 10.20.41.70

**Operational data confirmed in the corpus:**
- BitLocker PIN convention: 1910FFMx (site-coded)
- Domain join procedures for Blutspende.net
- Baramundi MDM configuration
- Blood donation unit numbering tables (Entnahmenummer ranges, MOB-DV series, Frankfurt/FFM and Baden-Baden/BB locations)
- Lab equipment procedures: IH 1000 blood typing analyzers (Bio-Rad)
- Email security policy (NoSpamProxy, confidentiality classification tiers)
- Network segmentation details (DMZ placement of lab devices)
- References to VNC passwords stored in a linked document

This data was recovered from an unauthenticated Weaviate vector database at IP 37.60.255.27, port 8080. The database has been open since at least August 2024 based on the build date of the software running on the server.

---

## What this means

Anyone with internet access can query this database. The plaintext credential above is a working server login if the server is still running with that username and password. The internal IP ranges, server names, and network architecture details provide a map of your internal environment to any party who found it before we did.

We did not access your internal network. We retrieved this data only from the external Weaviate database.

---

## What needs to happen immediately

1. **Change the password** on IH-DBSERVER\operator and audit all systems listed in the corpus for unauthorized access.
2. **Contact the service provider** (sergogram.com / the operator of gpt.sergogram.com) and request that they take the Weaviate database offline immediately and delete your data.
3. **Audit what data was provided** to the third-party AI service provider and assess whether additional credentials, documents, or PII were included.
4. **Review access logs** on the named internal servers for the period since August 2024.

If you cannot reach the service provider, Contabo GmbH (the hosting provider at 37.60.255.27) can be contacted via their abuse channel to take the server offline: abuse@contabo.com.

---

## About NuClide Research

NuClide Research is an independent security research organization based in Denver, Colorado, USA. We publish responsible disclosures and work with organizations to resolve exposures. This notification is sent in good faith with no commercial intent. We have not shared or published this data and will not do so while remediation is in progress.

Nicholas Michael Kloster
nicholas@nuclide-research.com
nuclide-research.com
CISA CVE-2025-4364, ICSA-25-140-11
