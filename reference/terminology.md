# Terminology Primer

Shorthand for the AI/ML stack as it appears throughout this repository. Skip this page if you already live in it.

| Term | Meaning |
|---|---|
| **Artifact Store** | Where trained models, weights, embeddings, and datasets actually live on disk. In self-hosted AI, this is almost always MinIO or S3. Compromise here means exfiltrating the model itself, not just the inference endpoint. |
| **Feature Store** | Centralized repository of ML features used for both training and serving. Feast and Tecton are the common names. Rare on Shodan, but a positive hit leaks the feature definitions that power production models. |
| **GraphRAG / Knowledge Graph** | Hybrid retrieval architecture combining a vector database with a graph database for relationship-aware retrieval. Neo4j + a vector store is the common pairing. |
| **MCP (Model Context Protocol)** | 2025–2026 standard for connecting LLMs to tools, filesystems, and databases. The protocol was designed for stdio transport but deploys increasingly over HTTP/SSE, which is where exposure happens. See [shodan/queries/10-mcp-servers.md](../shodan/queries/10-mcp-servers.md). |
| **OLAP + Vector** | Hybrid analytical databases (ClickHouse, Cassandra 5.x+) that handle both classical OLAP queries and semantic vector search. Shows up in analytics-heavy AI stacks. |
| **LLMjacking** | 2024-coined term for attacks that hijack exposed LLM endpoints or leaked API keys to run inference on someone else's provider bill. MCP servers and exposed LiteLLM proxies are primary targets. |
| **RAG (Retrieval-Augmented Generation)** | Architecture pattern that retrieves relevant documents from a vector store before passing them to an LLM. RAG stacks accumulate enterprise document sets, see [shodan/queries/07-rag-stacks.md](../shodan/queries/07-rag-stacks.md). |
| **Specialty Data Layers** | General-purpose analytic / wide-column / embedded-analytical platforms (ClickHouse, DuckDB, Cassandra/ScyllaDB, Pinot, Druid, StarRocks) that the AI/ML ecosystem co-opts for AI-adjacent work, feature stores, training-data lakes, real-time analytics over inference logs, ML classifier state. Predate the modern AI stack but get wired into it. See [reference/category-taxonomy.md](category-taxonomy.md#specialty-data-layers). |
| **Tier (T1 / T2 / T3)** | Exposure tier used throughout this repo. T1 = unauth by default. T2 = auth common but misconfigured or has known bypass CVEs. T3 = recon / fingerprint only, not an immediate finding. |
