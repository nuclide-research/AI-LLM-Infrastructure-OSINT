---
type: case-study
title: "Collector Scraper API — AI-Powered PII Extraction Service, Unauthenticated"
date: 2026-05-25
severity: HIGH
sector: commercial
tags: [LangGraph, PII, scraping, Scaleway, lead-generation, agent-framework]
summary: "Two Scaleway nodes in Paris run an unauthenticated API built to extract emails, phone numbers, and coordinates from business directory listings. No authentication on the extraction endpoint."
---

# Collector Scraper API — AI-Powered PII Extraction Service, Unauthenticated

**Date:** 2026-05-25
**Targets:** 51.15.237.90 · 51.158.97.152
**ASN:** Scaleway SAS, Paris, France (AS12876)
**Hostnames:** 90-237-15-51.instances.scw.cloud · 152-97-158-51.instances.scw.cloud
**OS:** Ubuntu 24.04 (OpenSSH 9.6p1 Ubuntu-3ubuntu13.16)
**Severity:** HIGH
**Category:** AI-powered PII collection service, unauthenticated

---

## Context

Two Scaleway nodes in Paris run an unauthenticated API built to extract emails, phone numbers, and coordinates from business directory listings. The service uses a LangGraph multi-step workflow as the extraction engine. Version 2.0. No authentication on the extraction endpoint.

The `/extract` endpoint is open. There is no auth layer.

---

## What Was Found

### F1. Unauthenticated PII Extraction API (HIGH)

Both nodes return identical responses at port 8000:

```
GET http://51.15.237.90:8000/
→ HTTP 200
→ {
    "message": "Collector Scraper API",
    "version": "2.0.0",
    "features": [
      "Enhanced phone extraction with regex and phonenumbers library",
      "Fast email extraction with optimized regex",
      "LangGraph-based extraction workflow",
      "Multi-strategy field extraction",
      "Geographic location detection",
      "Cluster-based country detection"
    ],
    "endpoints": {
      "docs": "/docs",
      "redoc": "/redoc",
      "places_extraction": "/extract"
    }
  }
```

"Enhanced" in two feature descriptions and "2.0.0" in the version string: a v1 existed. Version 2.0 improved the extractors.

```
GET http://51.15.237.90:8000/health
→ {"status":"healthy","service":"collector-scraper","version":"2.0.0"}
```

Both nodes healthy. Both running identically. This is not a single dev machine.

### F2. Full API Schema Disclosed (MEDIUM)

`GET /openapi.json` returns the full extraction contract without authentication:

```json
{
  "title": "Collector Scraper API",
  "description": "Enhanced web scraping and data extraction service with improved phone and email extractors",
  "version": "2.0.0"
}
```

The `/extract` endpoint accepts a `POST` with a `PlaceInstance` body:

```json
{
  "_id": "MongoDB id (optional)",
  "place_name": "required",
  "place_type": "required",
  "blocks": [
    {
      "block_id": "...",
      "sections": [
        {
          "section_id": "price",
          "fields": [{"field_id": "...", "value": null, "metadata": {}}]
        }
      ]
    }
  ]
}
```

The `PlaceInstance` schema matches Google Maps and similar business directory records: place name, place type, nested field blocks for pricing, contacts, and hours. The `_id` field is a MongoDB ObjectId. The service pulls a directory record, runs the LangGraph workflow, and writes the enriched output back.

The pipeline fills in what the directory record is missing: emails, phone numbers, coordinates, and a country label.

---

## The Threat Model

**For the operator:** The `/extract` endpoint is unauthenticated. Anyone can POST a `PlaceInstance` and trigger the full extraction workflow on the operator's compute and IP. Legal risk follows if the target source's terms of service prohibit scraping.

**For the people whose contact data is being collected:** The service aggregates PII from web sources across an unknown scope of targets. "Cluster-based country detection" puts this outside any single market. The MongoDB backend stores the enriched records. What that database holds and who reads it is not visible from outside. The pipeline runs. The data goes somewhere.

**The LangGraph role:** The extraction workflow is multi-step. LangGraph sequences the steps: fetch source, extract fields, detect location, assign country cluster. A single-strategy extractor does not need an agent framework. LangGraph handles branching and retry when one strategy fails and the next must run.

---

## Attribution

Both hosts are bare Scaleway instances. No custom domain. No PTR record beyond `*.instances.scw.cloud`. Both run Ubuntu 24.04 on identical SSH versions. No GreyNoise history. No passive DNS results beyond the default hostname.

VisorGraph returned 0 nodes, 0 edges on both hosts. No TLS. No certificate. No cert pivot. The operator has not registered a domain for this service.

Two nodes in the same cloud, same config, same version. The service is operational, not experimental.

---

## Thesis Placement

This case adds a category we had not catalogued before: AI-powered PII collection services. The surveyed LangGraph deployments are tools left open by accident. This service is built to harvest contact data and runs open by design.

The operator uses LangGraph as an extraction orchestrator, not as a conversational agent. "Multi-strategy field extraction" is the tell. One strategy fails and LangGraph tries the next. This is agent infrastructure applied to data harvesting.

**See also:** [LangGraph Server Survey (2026-05-25)](commercial/langgraph-server-survey-2026-05-25.md) for full population context.
