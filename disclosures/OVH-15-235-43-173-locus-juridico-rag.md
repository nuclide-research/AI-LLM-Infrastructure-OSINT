---
to: abuse@ovh.ca
cc: abuse@nuclide-research.com
severity: HIGH
ip: 15.235.43.173
institution: OVH Hosting Inc. / Canada (locus-juridico-rag, Brazilian legal RAG MCP server, 31.2M chunks incl. TCEES state-audit corpus)
status: DRAFT
outcome: sent
date: 2026-05-06
---

**To:** abuse@ovh.ca
**Cc:** abuse@nuclide-research.com
**Subject:** Unauthenticated Brazilian legal RAG MCP server (31.2M-chunk corpus incl. state-audit data) on OVH Canada, 15.235.43.173:8000

---

Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com

2026-05-06

**Re:** Unauthenticated `locus-juridico-rag v1.26.0` MCP server exposing 31.2M-chunk Brazilian legal corpus
**IP / Host:** 15.235.43.173 (rDNS `ns5034835.ip-15-235-43.net`, OVH Canada VPS)
**Severity:** HIGH

---

I'm an independent security researcher conducting good-faith AI infrastructure research under the NuClide Research umbrella (CISA disclosures CVE-2025-4364, ICSA-25-140-11). This is an unsolicited coordinated-disclosure notification.

---

## Summary

An OVH Canada VPS customer at `15.235.43.173:8000` is running an unauthenticated **Model Context Protocol (MCP) server** identifying itself as `locus-juridico-rag v1.26.0`. The server fronts a 31.2M-chunk Brazilian legal RAG corpus and exposes 8 callable tools to any unauthenticated internet caller.

The MCP `initialize` handshake also returns a Portuguese-language operator instruction set documenting the indexed tribunal scope:

> Tribunais: STF, STJ, TST, TRF2, TJES, TCEES, CERF-ES, CARF, TCU
> Categorias: juris (jurisprudência), legis (legislação), doutrina, extras
> Áreas: Civil, Penal, Trabalho, Tributário, Administrativo, Constitucional, Consumidor, Ambiental, Previdenciário, Empresarial
> Legislação: CF/88, CC/2002, CPC/2015, CP/1940, CLT, CDC, CTN, LC 621/2012 (TCEES)

The **TCEES** ingest is the most sensitive line item, TCE-ES (Tribunal de Contas do Estado do Espírito Santo) is the State Audit Court of Espírito Santo. A privately-indexed copy of TCEES proceedings is government-accountability data that a commercial legal-AI operator would normally protect behind authentication.

Found during NuClide Research's cross-cloud MCP survey (2026-05-04). Full case study at:
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT/blob/main/case-studies/commercial/mcp-cloud-survey-2026-05.md (search for "F8, locus-juridico-rag")

Re-verified live 2026-05-06.

---

## Confirmed exposure

`POST http://15.235.43.173:8000/mcp/` with the standard JSON-RPC 2.0 `initialize` envelope returns a successful handshake from `locus-juridico-rag v1.26.0`. Subsequent `tools/list` enumerates 8 callable tools, all unauthenticated:

```
search_juridico        — direct semantic search with manual filters
buscar_precedentes     — find precedents (with TJES → TRF2 → STJ → STF cascade)
analisar_caso          — full case analysis (intended for lawyer workflows)
comparar_entendimentos — compare divergent tribunal interpretations
buscar_norma           — find legal norms + jurisprudential interpretation
search_tcees           — Espírito Santo State Audit Court queries
get_document           — retrieve chunk by ID
rag_stats              — collection status
```

The retrieval substrate is described as "Busca híbrida semântica (Dense Voyage + BM25 sparse com RRF fusion + Voyage rerank) em 31.2M+ chunks jurídicos brasileiros", i.e. paid Voyage AI embeddings + a custom hybrid-search pipeline on a 31.2-million-chunk corpus.

Verification was non-destructive: only `initialize` and `tools/list` JSON-RPC methods were called. No content was retrieved beyond the schema-disclosing handshake.

---

## Why it matters

For the OVH customer (the `locus-juridico-rag` operator):

- **31.2M-chunk corpus is bulk-readable**, any caller can issue legal queries against the operator's full indexed dataset; a competitor-firm can free-ride on the operator's indexing + Voyage embedding spend
- **Voyage AI quota theft**, every `search_juridico` call on the operator's deployment routes through their Voyage AI account (the dense-embedding + rerank steps are typically authenticated against the operator's API key)
- **TCEES exposure**, government-accountability data indexed under what was presumably a commercial license becomes a free public-search service; Brazilian regulator visibility (LGPD) is plausible
- **Operator identification leak**, the Portuguese instruction set discloses the operator's product positioning, indexed-tribunal scope, and suggested-tool hierarchy (a competitor-intelligence document)
- **MCP write-side exposure**, tools/list is read-only (no `create_*` / `delete_*` / `patch_*`), which limits this to data-confidentiality + quota-theft, not data-integrity. Severity **HIGH** rather than CRITICAL on that basis.

For OVH Canada:

- An unauthenticated MCP server on a customer VPS is a class of finding the customer can fix in one minute (bind to localhost or add a firewall rule). A short note from OVH's abuse channel to the customer is the cleanest path.

---

## Remediation (for the customer)

```bash
# If served by FastMCP / uvicorn (likely, given Server: uvicorn header):
uvicorn locus_juridico_mcp:app --host 127.0.0.1 --port 8000

# Or restrict access at the firewall layer:
ufw deny 8000/tcp
ufw allow from <admin-IP> to any port 8000
```

If the MCP transport must be exposed for AI-client integrations (Claude Desktop / Cursor / Continue), route through a reverse proxy with token-gated access at the proxy layer, the MCP protocol itself does not require auth at the transport, but auth-on-default is the operator's responsibility.

---

## Português (versão curta para o cliente OVH)

Caro operador da OVH Canada,

O servidor MCP `locus-juridico-rag v1.26.0` em `15.235.43.173:8000` está exposto sem autenticação na internet pública. Qualquer chamador pode:

- Listar todas as ferramentas RAG (`search_juridico`, `buscar_precedentes`, `analisar_caso`, `search_tcees`, etc.)
- Consultar livremente o corpus de 31.2 milhões de chunks (incluindo dados do TCEES)
- Consumir a cota da sua conta Voyage AI a cada consulta

**Correção:** vincule o servidor a `127.0.0.1` em vez de `0.0.0.0`, ou use uma regra de firewall para bloquear o acesso externo à porta 8000.

A descoberta foi feita em 2026-05-04 e re-verificada em 2026-05-06. Esta divulgação é coordenada e não-pública até o ciclo de remediação concluir.

Estou disponível para perguntas em português ou inglês.

---

## Reference

Full technical detail (handshake response capture, tool enumeration, methodology context for the cross-cloud MCP survey):
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT/blob/main/case-studies/commercial/mcp-cloud-survey-2026-05.md

Methodology synthesis (auth-on-default-vs-off thesis at population scale, MCP-survey honeypot-filtering technique):
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT/blob/main/case-studies/commercial/SYNTHESIS-2026-05.md

Happy to answer questions or assist with verification.

Regards,
Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT
