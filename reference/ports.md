# Common AI/LLM Infrastructure Ports

Cross-cutting port reference for AI/ML-adjacent services. Useful for Shodan/Censys/FOFA queries, nmap/naabu scan prioritization, firewall audits, and asset discovery.

Sorted numerically. Where a port hosts multiple AI/ML services, the primary ones are listed first.

## Quick-Reference Table

| Port | Service(s) | Notes |
|------|-----------|-------|
| **80 / 443** | Generic HTTP(S), Dify, Flowise, reverse-proxied everything | Filter by `http.title:` / HTML fingerprint |
| **1337** | Jan, Devika | Hacker-cute defaults |
| **1984** | LangSmith | |
| **2375** | Docker daemon (unauth) | RCE → host foothold |
| **2379** | etcd (Milvus metadata), Kubernetes control plane | |
| **3000** | Flowise, Open WebUI, AnythingLLM, AgentGPT, SuperAGI, Langfuse, Promptfoo, OpenDevin, Grafana | Most crowded port in AI |
| **3001** | AnythingLLM | |
| **4000** | LiteLLM Proxy | Provider keys live here |
| **4040** | Apache Spark UI | Often co-deployed with ML pipelines |
| **4317** | OpenTelemetry gRPC (OTLP) | LLM observability transport |
| **4318** | OpenTelemetry HTTP (OTLP) | LLM observability transport |
| **4567** | Rivet | |
| **5000** | MLflow | Models, artifacts, experiments |
| **5001** | KoboldCpp | |
| **5050** | pgAdmin | Often default creds |
| **5432** | PostgreSQL + pgvector, Supabase, Neon, Timescale | |
| **5500** | ChromaDB (alt) | |
| **5601** | Kibana, OpenSearch Dashboards | Vector index admin |
| **5678** | n8n | AI workflow automation |
| **6006** | Phoenix/Arize, TensorBoard | Traces + training viz |
| **6333** | Qdrant (HTTP) | Snapshots downloadable |
| **6334** | Qdrant (gRPC) | |
| **6379** | Redis / Redis Stack (vector search) | Often no auth |
| **6443** | Kubernetes API server | ML workload orchestration |
| **6900** | Argilla | RLHF/annotation data |
| **7474** | Neo4j Browser | Graph memory stores |
| **7501** | Lightning AI | |
| **7687** | Neo4j Bolt, Memgraph | |
| **7860** | Gradio, LangFlow, unsloth, text-generation-webui | HuggingFace Spaces default |
| **7997** | Infinity (embeddings) | |
| **8000** | LangChain, vLLM, Triton, FastAPI generic, ChromaDB, AutoGPT, BentoML, Ray Serve, MetaGPT, Mem0, many `/v1/*` OpenAI-compat | Single most common LLM port |
| **8001** | RedisInsight | |
| **8008** | ClearML | |
| **8080** | LocalAI, llama.cpp, Vespa, BabyAGI, Axolotl, Determined AI, Kubeflow, Airflow, Helicone, Dgraph, NVIDIA, Vast.ai, HF TEI/TGI, Phidata | Generic "alt-HTTP" |
| **8081** | mongo-express | |
| **8088** | Hadoop YARN ResourceManager | Training data pipelines |
| **8089** | Splunk HEC | Sometimes LLM log sink |
| **8108** | Typesense | API key enumeration risk |
| **8123** | LangGraph Studio, ClickHouse | |
| **8161** | ActiveMQ Web Console | ML pipeline message broker |
| **8265** | Ray Dashboard | Cluster job submission, RCE |
| **8443** | SageMaker Notebook, alt-HTTPS | |
| **8501** | Streamlit | |
| **8529** | ArangoDB | |
| **8787** | Cloudflare AI Gateway, Portkey, RStudio Server | |
| **8882** | Marqo | |
| **8888** | Jupyter, RunPod | RCE if no token |
| **9000** | MinIO (Milvus backing), Portainer | Vector blobs in buckets |
| **9090** | Prometheus | Every ML stack exports metrics here |
| **9091** | Milvus metrics, Zilliz | |
| **9092** | Apache Kafka | LLM event streams, training pipelines |
| **9200** | Elasticsearch / OpenSearch | `dense_vector` / kNN |
| **9400** | NVIDIA DCGM | GPU telemetry |
| **9870** | Hadoop NameNode (HDFS) | Training data at rest |
| **9998** | Apache Tika | Document ingestion |
| **10250** | Kubelet | K8s node attack surface |
| **11434** | **Ollama** | Most-exposed LLM runtime in 2025-26 |
| **19530** | Milvus (gRPC) | |
| **27017** | MongoDB | Increasingly used as vector store |
| **50070** | Hadoop NameNode (legacy) | |

## Patterns Worth Knowing

### Highest-yield single-port queries
- **`port:11434`**, catches tens of thousands of unauth Ollama instances. Model-naming leaks org context (e.g. `acme-internal-rag:latest` discloses tenant identity before authenticating).
- **`port:7860`**, Gradio/HuggingFace Spaces ecosystem; favicon hash `-1294819032` catches reverse-proxied instances that strip the title.
- **`port:8000` + `"/v1/chat/completions"`**, OpenAI-compatible endpoint regardless of underlying engine. vLLM, LM Studio, llama.cpp, LocalAI, text-generation-webui all collapse into this.
- **`port:6006`**, historically TensorBoard, now also Phoenix/Arize for LLM traces. Same port, very different exposure surface: training metrics vs. live prompt/response logs.

### Port ranges by deployment pattern
- **Enthusiast / self-hosted:** 1337, 4567, 7501, 8123, 11434, less likely to have org-grade auth.
- **Production-ish web UIs:** 3000, 8080, 7860, SaaS-flavored, sometimes wrapped in Cloudflare but often not.
- **Data plane (never meant to be public):** 5432, 6379, 9200, 19530, 27017, direct database exposure = bypass of any auth layer the app imposes.
- **Control / admin planes:** 2375, 2379, 6443, 8265, 9000, one of these exposed means the entire workload is owned.

### Co-location signals
If you see these ports together on one host, infer the stack:
- **`11434 + 3000`** → Ollama + Open WebUI (self-hosted private ChatGPT)
- **`6333 + 8000 + 4000`** → Qdrant + a RAG app + LiteLLM proxy
- **`5000 + 8265 + 9400`** → MLflow + Ray + NVIDIA DCGM (training cluster)
- **`9200 + 5601 + 3000`** → Elasticsearch + Kibana + Langfuse (RAG observability stack)
- **`8888 + 8265`** → Jupyter + Ray (notebook-driven ML cluster)

### Ports that are *always* worth a second look
| Port | Why |
|------|-----|
| **2375** | Unauth Docker daemon = host RCE via `/containers/create` |
| **8265** | Ray cluster job submission = arbitrary code execution across GPU nodes |
| **6443 / 10250** | K8s API / Kubelet = full workload control if unauth |
| **11434** | Ollama exposes `/api/generate` → free inference + model enumeration |
| **4000** | LiteLLM proxy admin UI leaks master provider keys if misconfigured |

## Scanning Tips

```bash
# Fast first-pass of common AI ports with naabu
naabu -host <target> -p 2375,3000,4000,5000,5432,6006,6333,6379,7860,8000,8080,8265,8888,9090,9200,11434,19530

# Nmap service detection on the long list
nmap -sV -p 80,443,1337,1984,2375,2379,3000,3001,4000,4040,4317,4318,4567,5000,5001,5050,5432,5500,5601,5678,6006,6333,6334,6379,6443,6900,7474,7501,7687,7860,7997,8000,8001,8008,8080,8081,8088,8089,8108,8123,8161,8265,8443,8501,8529,8787,8882,8888,9000,9090,9091,9092,9200,9400,9870,9998,10250,11434,19530,27017,50070 <target>

# Shodan facet to see which ports dominate a given org
shodan search --facets port org:"Example Inc" "api" | head
```

## Contributing

New AI-adjacent port? Open a PR adding a row (keep sorted numerically) with the service name and a `Notes` column entry when the exposure has non-obvious impact. See [CONTRIBUTING.md](../CONTRIBUTING.md).
