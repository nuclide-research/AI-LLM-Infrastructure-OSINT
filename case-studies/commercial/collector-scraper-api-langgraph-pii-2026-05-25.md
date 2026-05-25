---
type: case-study
title: "Collector Scraper API — AI-Powered PII Extraction Service, Unauthenticated"
date: 2026-05-25
severity: HIGH
sector: commercial
tags: [LangGraph, PII, scraping, Scaleway, lead-generation, agent-framework]
summary: "A production-grade AI service built to extract emails, phone numbers, and geographic data from business directory listings runs two Scaleway nodes in Paris with no authentication on the extraction endpoint."
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

Most LangGraph deployments found in this survey are AI assistants or data tools left open by accident. This one is different. The Collector Scraper API is a production-grade service built specifically to extract personal contact information from the web, using a LangGraph multi-step workflow as its extraction engine. It runs on two Scaleway VPS nodes in Paris, version 2.0, with no authentication on the extraction endpoint.

The service is not accidentally exposed. There is no auth layer to have forgotten. The `/extract` endpoint is simply open.

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

The word "Enhanced" in two feature descriptions signals this is not a first build. A v1 existed. v2.0 improved the extractors.

```
GET http://51.15.237.90:8000/health
→ {"status":"healthy","service":"collector-scraper","version":"2.0.0"}
```

Both nodes healthy, both running identically. This is not a single dev machine.

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

The `PlaceInstance` schema matches the record structure of Google Maps and similar business directory APIs: place name, place type (restaurant, hotel, shop), nested blocks of field data (pricing, contacts, hours). The `_id` field is a MongoDB ObjectId. The service pulls records from a directory, runs the LangGraph extraction workflow, and writes the enriched output back.

The extraction pipeline fills in what the directory record is missing: email addresses, phone numbers, geographic coordinates, and a cluster-assigned country label.

---

## The Threat Model

**For the operator:** The `/extract` endpoint is unauthenticated. Anyone can POST a PlaceInstance and trigger the full LangGraph extraction workflow on the operator's infrastructure. That means the operator's compute, the operator's IP address, and the operator's potential legal exposure if the extraction violates the terms of service of whichever source is being scraped.

**For the people whose contact data is being collected:** The service is purpose-built to aggregate PII from web sources at scale. "Cluster-based country detection" means this is international in scope, not a single-market tool. The MongoDB backend stores the enriched records. What that database contains and who accesses it is not visible from the outside. The extraction pipeline runs. The data goes somewhere.

**The LangGraph role:** The extraction workflow is multi-step, not a single regex pass. LangGraph coordinates the steps: fetch source, extract fields with multiple strategies in sequence, detect location, assign country cluster. A single-strategy extractor would not need an agent framework. The framework is present because the task is complex enough to require sequencing and retry logic.

---

## Attribution

Both hosts are bare Scaleway instances with no custom domain and no PTR record beyond the Scaleway default (`*.instances.scw.cloud`). Both run Ubuntu 24.04 on identical SSH versions. No GreyNoise history, no passive DNS results beyond the default hostname.

VisorGraph returned 0 nodes, 0 edges on both hosts. No TLS, no certificate, no cert pivot. The operator has not registered a domain for this service.

Two production nodes in the same cloud, same config, same version. The service is operational, not experimental.

---

## Thesis Placement

This case extends the auth-on-default thesis into a category not previously catalogued: AI-powered data collection services. Most unauth AI infrastructure is a tool left open. This is a collection service, built to harvest PII, running open by design. Auth was not forgotten. The extraction endpoint is the product.

The LangGraph framework's role here is notable. It is being used as an extraction orchestrator, not as a conversational agent. The "multi-strategy field extraction" feature is the tell: LangGraph handles the branching logic when one extraction strategy fails and another must be tried. This is agent infrastructure applied to data harvesting.

**See also:** [LangGraph Server Survey (2026-05-25)](commercial/langgraph-server-survey-2026-05-25.md) for full population context.
