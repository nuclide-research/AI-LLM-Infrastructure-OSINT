# LLM Orchestration Platforms & Frameworks (2026)

A categorized reference list of LLM orchestration, agent, and workflow frameworks. Many entries overlap across categories; the ~25 in **Core** and **Multi-Agent** are the ones most teams actually evaluate.

---

## Core Frameworks

| Framework | Notes |
|---|---|
| **LangChain** | General-purpose, chain-based; broadest ecosystem and integrations |
| **LangGraph** | LangChain's graph-based agent runtime; stateful, checkpointing, time-travel |
| **LlamaIndex** | Data/RAG-focused; ingestion, indexing, retrieval |
| **Haystack** *(deepset)* | Production-oriented, component-based pipelines; RAG & search |
| **DSPy** *(Stanford)* | Declarative "programming, not prompting"; prompt optimization |
| **AdalFlow** | Lightweight, RAG-origin pipeline framework |

---

## Multi-Agent / Agentic Frameworks

| Framework | Notes |
|---|---|
| **AutoGen / AG2** *(Microsoft Research)* | Conversational multi-agent; research & R&D |
| **CrewAI** | Role-based "crews"; rapid prototyping, low boilerplate |
| **OpenAI Agents SDK** | Handoff-based; production successor to Swarm (OpenAI-locked) |
| **Google ADK** | Hierarchical agent tree; optimized for Gemini, A2A support |
| **Anthropic Agent SDK** | Tool-use chain with sub-agents; Claude-native, MCP memory |
| **Smolagents** *(Hugging Face)* | Code-generating agents; model-agnostic via LiteLLM |
| **Pydantic AI** | Type-safe, "FastAPI feeling"; validated structured outputs |
| **MetaGPT** | Multi-agent for software-development workflows |
| **Mastra** | TypeScript-native; popular for Next.js stacks |
| **Agno** *(formerly Phidata)* | High-performance multi-modal runtime (AgentOS) |
| **CAMEL** | Early role-playing multi-agent framework |
| **TaskWeaver** | Code-first task decomposition |
| **Griptape** | Modular Python; pipelines, workflows, "off-prompt" memory |
| **Letta** *(formerly MemGPT)* | Stateful agents with persistent long-term memory |
| **fast-agent** | MCP-enabled agents & workflows |
| **Axflow** | TypeScript, code-first NL application framework |
| **Marvin** *(Prefect)* | "Ambient intelligence" / multi-agent orchestration |
| **OpenAGI** | Self-improving autonomous daemon agent |
| **OpenAI Swarm** | Experimental predecessor to the Agents SDK |
| **Vision Agents** | Voice/vision multimodal real-time agents |

---

## Autonomous / Goal-Driven Agents

| Tool | Notes |
|---|---|
| **AutoGPT** | Pioneered the autonomous-agent era (now archived CLI) |
| **BabyAGI** | Task-driven autonomous agent loop pattern |
| **AgentGPT** | Browser-based autonomous agents, zero setup |
| **SuperAGI** | Dev-first open-source autonomous agent platform with UI |

---

## Enterprise / Microsoft Ecosystem

| Platform | Notes |
|---|---|
| **Semantic Kernel** *(Microsoft)* | Enterprise SDK; .NET, Java, Python; Azure/Copilot integration |
| **Microsoft Agent Framework** | Merge of Semantic Kernel + AutoGen; native A2A support |
| **IBM watsonx Orchestrate** | Proprietary; NLP workflow automation, governance focus |
| **Azure PromptFlow** | Evaluation-driven prompt/flow orchestration on Azure |

---

## Workflow / Durable Execution Engines

| Engine | Notes |
|---|---|
| **Temporal** | Durable execution; strong retry/state semantics |
| **Prefect** | Python-first data/AI workflow orchestration |
| **Dagster** | Asset-based data/workflow orchestration |
| **Inngest** | Event-driven durable workflows |
| **n8n** | Workflow-first, visual automation |
| **Zapier** | No-code; connects 8,000+ apps |

---

## Low-Code / Visual Builders

| Builder | Notes |
|---|---|
| **Flowise** | Open-source visual builder on LangChain |
| **Dify** | Beginner-friendly drag-and-drop; very high GitHub stars |
| **Langflow** | Visual canvas on the LangChain ecosystem |
| **Rivet** *(Ironclad)* | Visual prompt-graph programming environment |
| **Gumloop** | Lightweight visual builder for prototyping |
| **Stack AI** | Low-code platform for AI automations/workflows |
| **Vellum** | Enterprise controls, audit trails, fast iteration |
| **Sim Studio** | Visual agent/workflow builder |
| **Kubiya** | DevOps-focused agent orchestration |

---

## Managed Cloud Platforms

| Platform | Notes |
|---|---|
| **AWS Bedrock Agents / AgentCore** | Managed orchestration; model-agnostic foundation models |
| **Google Vertex AI Agent Builder / Agent Engine** | Managed Google Cloud agent infrastructure |
| **Salesforce Agentforce** | Low-code enterprise agent platform |
| **Strands Agents** *(AWS SDK)* | Minimal-boilerplate agent SDK |
| **Multi-Agent Orchestrator** *(AWS)* | Multi-agent routing/coordination |

---

## Coding-Specific Agents

| Tool | Notes |
|---|---|
| **OpenHands** *(formerly OpenDevin)* | Autonomous software-engineering agent |
| **Aider** | Terminal-based AI pair programmer |

---

## LLM Gateways / Routing

| Gateway | Notes |
|---|---|
| **LiteLLM** | Unified API across 100+ providers; routing, fallbacks |
| **Portkey** | Enterprise gateway; semantic caching, guardrails |
| **Helicone** | Observability-first proxy/gateway |
| **OpenRouter** | "App store" of LLM APIs; 300+ models, no infra |
| **Bifrost** *(Maxim AI)* | Go-based low-latency gateway; MCP, failover |
| **Kong AI Gateway** | API-gateway-grade governed routing |
| **Cloudflare AI Gateway** | Edge caching, global routing |
| **BricksLLM** | Open-source enterprise gateway |
| **Orq.ai** | LLMOps + serverless orchestration, routing, evals |

---

## Structured Output / Prompt-Programming Libraries

| Library | Notes |
|---|---|
| **Instructor** | Pydantic-validated structured outputs with retries |
| **Outlines** | Constrained / structured generation |
| **Guidance** *(Microsoft)* | Constrained generation & control flow |
| **Mirascope** | Lightweight, Pythonic LLM call abstractions |

---

## DAG / Pipeline Libraries

| Library | Notes |
|---|---|
| **Burr** *(DAGWorks)* | State-machine framework for LLM apps |
| **Hamilton** *(DAGWorks)* | Dataflow/DAG framework for pipelines |
| **Apache Camel** *(via LangChain4j)* | Enterprise integration routing for AI pipelines |

---

## Lightweight / Niche / LLMOps

| Tool | Notes |
|---|---|
| **Microchain** | Minimalist orchestration (not actively maintained) |
| **Agenta** | Open-source LLMOps: prompt mgmt, evals, observability |

---

### Quick Picks by Use Case

| Use Case | Recommended Starting Point |
|---|---|
| General / broadest ecosystem | LangChain |
| Stateful production agents | LangGraph |
| RAG / retrieval-heavy | LlamaIndex |
| Role-based multi-agent | CrewAI |
| Research / conversational agents | AutoGen / AG2 |
| OpenAI-native | OpenAI Agents SDK |
| Google Cloud-native | Google ADK / Vertex AI |
| Claude-native | Anthropic Agent SDK |
| Enterprise / Azure / .NET | Semantic Kernel |
| Prompt optimization | DSPy |
| Structured pipelines | Haystack |
| TypeScript / Next.js | Mastra |
| Type-safe agents | Pydantic AI |
| Durable execution | Temporal / Prefect |
| Low-code / visual | Dify / Langflow / Flowise |
| Multi-provider routing | LiteLLM / OpenRouter / Portkey |

---

*Compiled June 2026. The landscape moves fast — there are now 40+ frameworks; most teams need only 2–3.*
