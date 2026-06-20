# Coding Education Chatbot -- Unauth RWD on Italian Programming Q&A Knowledge Base

**Date:** 2026-06-20
**Tool:** weavscan
**Severity:** HIGH
**Status:** CONFIRMED -- unauth read + write + delete

---

## Target

```
IP:       5.78.79.3
Port:     8080  (Weaviate)
Service:  Weaviate 1.33.5
Hosting:  Hetzner Online
Auth:     NONE
```

---

## Data (2 Classes, 32 Records)

| Class | Records | Content |
|-------|---------|---------|
| ChatbotKnowledgeBase | 29 | Italian-language programming Q&A pairs |
| SecurityTest | 3 | Batch processing queue records |

### Schema (ChatbotKnowledgeBase)

```
botId      text    -- bot identifier (CUID)
sourceId   text    -- source chunk identifier (CUID)
content    text    -- Q&A pair or documentation chunk
```

### Sample Records

Single bot: `cmk3aiq8t0041sdvs0jzzjrb5`

```
Q: È sbagliato copiare codice da internet?
A: No, copiare codice per imparare è normale. L'importante è capire cosa fa
   quel codice e modificarlo, invece di usarlo senza comprenderlo.

Q: Cos'è una variabile?
A: Una variabile è un contenitore che serve a memorizzare un valore, come un
   numero o un testo, per poterlo riutilizzare nel programma.

Q: Devo capire tutto prima di scrivere codice?
A: No. È normale non capire tutto subito. S...

Q: Cos'è un errore di sintassi?
A: Un errore di sintassi indica che il codice non rispetta...

Q: Qual è il linguaggio migliore per iniziare a programmare per hobby?
A: Un buon linguaggio per iniziare è...
```

Additional content scraped from Codecademy (codecademy.com) -- "Coding Fundamentals" course, 78 languages.

### SecurityTest Class

```
batch_id    text    -- "batch_1778698309_0", "_1", "_2"
```

Batch processing queue records -- no sensitive content.

---

## Access Matrix

| Operation | Result | HTTP |
|-----------|--------|------|
| Read | YES | 200 |
| Write | YES | 200 |
| Delete | YES | 204 |

---

## Impact

### Read -- Knowledge Base Exfiltration

29 records of an Italian-language coding education chatbot. Not high-sensitivity content (programming Q&A + public Codecademy content). Value: competitor intelligence on the chatbot's knowledge base composition.

### Write -- Educational Misinformation

Injecting false programming guidance or deliberately incorrect answers into the knowledge base poisons the chatbot's responses to learners. False answers about syntax errors, variable types, or language selection could mislead beginner programmers.

### Pattern

Same CUID ID pattern (cmk3... prefix = earlier than cmm/cmn/cmo) as the Russian chatbot SaaS platform. Likely the same underlying SaaS platform serving Italian-language customers.

---

## Tool Reference

Found with **weavscan**.
https://github.com/nuclide-research/weavscan
