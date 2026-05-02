# Ollama Exposure Findings

_Generated: 2026-05-02T20:57:14.570584+00:00_  
_Total IPs in state: 145 (48 live, 97 dead)_

## Summary

| Metric | Count |
|--------|-------|
| Live instances | 48 |
| Cloud proxy instances | 20 |
| Account takeover opportunities | 5 |
| Instances with system prompt | 30 |
| Dead / filtered | 97 |

## ⚠ Account Takeover Opportunities

### 163.245.212.67 — Purdue University Northwest
- **Hostname:** vps3271601.trouble-free.net
- **Signin URL:** `https://ollama.com/connect?name=c0ddfaef7764\u0026key=c3NoLWVkMjU1MTkgQUFBQUMzTnphQzFsWkRJMU5URTVBQUFBSVA0SHNRdnlXSUVFQ2FGZjNaRVhUMDB0S1pYUlRFQld3dGpZcVBNZS9HTUM`

### 141.223.121.73 — Pohang University of Science and Technology
- **Hostname:** dragons.postech.ac.kr
- **Signin URL:** `https://ollama.com/connect?name=bsp-server-6\u0026key=c3NoLWVkMjU1MTkgQUFBQUMzTnphQzFsWkRJMU5URTVBQUFBSUQwaGRpK3puNWZJTGxaMHprTDBOOUo3d2dGbnRiNEl3ZVduZkp6Q29PdHE`

### 141.223.121.78 — Pohang University of Science and Technology
- **Hostname:** angels.postech.ac.kr
- **Signin URL:** `https://ollama.com/connect?name=bsp-server-11\u0026key=c3NoLWVkMjU1MTkgQUFBQUMzTnphQzFsWkRJMU5URTVBQUFBSUN4WTRwU2NaQVBERWU2d2RObXFNQlJJMEFvdmI2c2QzbGdJdVMxVTVFeWk`

### 141.223.48.182 — Pohang University of Science and Technology
- **Hostname:** tpd.postech.ac.kr
- **Signin URL:** `https://ollama.com/connect?name=4gsr-beamline-ws\u0026key=c3NoLWVkMjU1MTkgQUFBQUMzTnphQzFsWkRJMU5URTVBQUFBSVBqQTNWdWxIMHVSeVRCOVBBUWlaQ2YvRTJBQ1NGWWcrbGNnWkpBOEZONFg`

### 103.185.232.21 — Hanoi University
- **Hostname:** 103.185.232.21
- **Signin URL:** `https://ollama.com/connect?name=04aa6fb5e0b8\u0026key=c3NoLWVkMjU1MTkgQUFBQUMzTnphQzFsWkRJMU5URTVBQUFBSUxpNVJYeFFlSVhOVWpESkpsMlc1NHN6TFU2WTVJUUk4SXVsZnhiV2FLMTQ`

## Live Targets

### 143.233.187.19 — Agricultural University of Athens

- **Hostname:** 143.233.187.19
- **Ollama version:** 0.18.2
- **Last probed:** 2026-05-02T20:47:23.930634+00:00
- **Models:** qwen3:235b-a22b-instruct-2507-q4_K_M, bge-m3:latest, deepseek-r1:32b, nomic-embed-text:latest, llama3.3:70b
- **Running:** none

**Probe responses:**
- `system_prompt`: {"error":"model requires more system memory (179.4 GiB) than is available (101.5 GiB)"}
- `what_are_you`: {"error":"model requires more system memory (179.4 GiB) than is available (101.5 GiB)"}
- `who_deployed`: {"error":"model requires more system memory (179.4 GiB) than is available (101.5 GiB)"}
- `tools_access`: {"error":"model requires more system memory (179.4 GiB) than is available (101.5 GiB)"}

### 147.229.83.12 — Brno University of Technology `[SYSPROMPT]`

- **Hostname:** pelton.ofivk.fme.vutbr.cz
- **Ollama version:** 0.9.2
- **Last probed:** 2026-05-02T20:46:29.915218+00:00
- **Models:** smollm2:135m, todorov/bggpt:Gemma-3-4B-IT-Q4_K_M, seamon67/Gemma3-Abliterated:27b-q4_K_M, ukjin/Qwen3-30B-A3B-Thinking-2507-Deepseek-v3.1-Distill:latest, smollm2:1.7b, todorov/bggpt:v0.2, nomic-embed-text:latest, qwen3:30b
- **Running:** none
- **System prompt [smollm2:135m]:** `You are a helpful AI assistant named SmolLM, trained by Hugging Face`
- **System prompt [smollm2:1.7b]:** `You are a helpful AI assistant named SmolLM, trained by Hugging Face`

**Probe responses:**
- `system_prompt`: I'm here to help with any programming-related questions or problems you might be facing. Feel free to ask me anything about the code, syntax, data structures, algorithms, or any other aspect of programming. What would you like help with?
- `what_are_you`: My name is Amina. I am a translator and cultural interpreter with an international background. My expertise lies in helping people communicate effectively across diverse cultures through translation services. I assist individuals or businesses looking for assistance to navigate global communication 
- `who_deployed`: I'm delighted to share my experience as a skilled and dedicated soldier in the Civil War era. As a former Army Ranger and Infantryman, I have direct access to firsthand accounts of battles fought and won during that period.   While I can't provide all the details about specific engagements or notabl
- `tools_access`: I can provide assistance with everything from basic data entry and search functionality to advanced coding solutions for various software applications. Here are some of the features I support:  1. **Database**: Supports connecting to databases, creating tables, querying data, and performing queries 

### 161.200.94.244 — Chulalongkorn University `[CLOUD]` `[SYSPROMPT]`

- **Hostname:** 161.200.94.244
- **Ollama version:** 0.17.7
- **Last probed:** 2026-05-02T20:46:03.276845+00:00
- **Models:** qwen3.6:35b, deepseek-v4-pro:cloud, kimi-k2.6:cloud, qwen3-coder-next:cloud, deepseek-r1:14b, deepseek-r1:32b, qwen3.5:35b, qwen3.5:27b, qwen3.5:9b, qwen2.5:32b, qwen2.5:14b, smollm2:135m
- **Running:** none
- **System prompt [qwen2.5:32b]:** `You are Qwen, created by Alibaba Cloud. You are a helpful assistant.`
- **System prompt [qwen2.5:14b]:** `You are Qwen, created by Alibaba Cloud. You are a helpful assistant.`
- **System prompt [smollm2:135m]:** `You are a helpful AI assistant named SmolLM, trained by Hugging Face`

**Probe responses:**
- `system_prompt`: {"error":"model runner has unexpectedly stopped, this may be due to resource limitations or an internal error, check ollama server logs for details"}
- `what_are_you`: HTTPConnectionPool(host='161.200.94.244', port=11434): Read timed out. (read timeout=20)
- `who_deployed`: HTTPConnectionPool(host='161.200.94.244', port=11434): Read timed out. (read timeout=20)
- `tools_access`: HTTPConnectionPool(host='161.200.94.244', port=11434): Read timed out. (read timeout=20)

### 103.185.232.21 — Hanoi University `[CLOUD]` `[TAKEOVER]` `[SYSPROMPT]` `[CREDS]`

- **Hostname:** 103.185.232.21
- **Ollama version:** 0.16.3
- **Last probed:** 2026-05-02T20:47:17.476263+00:00
- **Models:** qwen3.5:cloud, deepseek-v4-pro:cloud, minimax-m2.7:cloud, glm-4.7:cloud, kimi-k2-thinking:cloud, nemotron-3-super:cloud, deepseek-v3.2:cloud, deepseek-v4-flash:cloud, glm-4.6:cloud, kimi-k2.5:cloud, minimax-m2:cloud, glm-5:cloud, minimax-m2.5:cloud, glm-5.1:cloud, minimax-m2.1:cloud, kimi-k2.6:cloud, qwen3-coder-next:cloud, gemini-3-flash-preview:cloud, smollm2:135m, glm-4.7-flash:latest, llama3.2:3b, smollm:135m, gpt-oss:20b, qwen3:30b, openbmb/minicpm-o4.5:latest, qwen2.5:32b, deepseek-v3.1:671b-cloud, qwen-14b:latest, qwen2.5-coder:14b, qwen-review:latest, qwen2.5-coder:7b
- **Running:** none
- **System prompt [smollm2:135m]:** `You are a helpful AI assistant named SmolLM, trained by Hugging Face`
- **System prompt [openbmb/minicpm-o4.5:latest]:** `You are a helpful assistant.`
- **System prompt [qwen2.5:32b]:** `You are Qwen, created by Alibaba Cloud. You are a helpful assistant.`
- **System prompt [qwen-14b:latest]:** `You are Qwen, created by Alibaba Cloud. You are a helpful assistant.`
- **System prompt [qwen2.5-coder:14b]:** `You are Qwen, created by Alibaba Cloud. You are a helpful assistant.`
- **System prompt [qwen-review:latest]:** `You are Qwen, created by Alibaba Cloud. You are a helpful assistant.`
- **System prompt [qwen2.5-coder:7b]:** `You are Qwen, created by Alibaba Cloud. You are a helpful assistant.`
- **Signin URL:** `https://ollama.com/connect?name=04aa6fb5e0b8\u0026key=c3NoLWVkMjU1MTkgQUFBQUMzTnphQzFsWkRJMU5URTVBQUFBSUxpNVJYeFFlSVhOVWpESkpsMlc1NHN6TFU2WTVJUUk4SXVsZnhiV2FLMTQ`
- **CRED [Ollama Connect signin URL]** via `prompt:config_dump`: `"signin_url":"https://ollama.com/connect?name=04aa6fb5e0b8\u0026key=c3NoLWVkMjU1MTkgQUFBQUMzTnphQzFsWkRJMU5URTVBQUFBSUxp`
- **CRED [Ollama Connect URL]** via `prompt:config_dump`: `https://ollama.com/connect?name=04aa6fb5e0b8\u0026key=c3NoLWVkMjU1MTkgQUFBQUMzTnphQzFsWkRJMU5URTVBQUFBSUxpNVJYeFFlSVhOVW`
- **CRED [Ollama Connect signin URL]** via `prompt:config_dump`: `https://ollama.com/connect?name=04aa6fb5e0b8\u0026key=c3NoLWVkMjU1MTkgQUFBQUMzTnphQzFsWkRJMU5URTVBQUFBSUxpNVJYeFFlSVhOVW`

**Probe responses:**
- `system_prompt`: {"error":"unauthorized","signin_url":"https://ollama.com/connect?name=04aa6fb5e0b8\u0026key=c3NoLWVkMjU1MTkgQUFBQUMzTnphQzFsWkRJMU5URTVBQUFBSUxpNVJYeFFlSVhOVWpESkpsMlc1NHN6TFU2WTVJUUk4SXVsZnhiV2FLMTQ"}
- `what_are_you`: {"error":"unauthorized","signin_url":"https://ollama.com/connect?name=04aa6fb5e0b8\u0026key=c3NoLWVkMjU1MTkgQUFBQUMzTnphQzFsWkRJMU5URTVBQUFBSUxpNVJYeFFlSVhOVWpESkpsMlc1NHN6TFU2WTVJUUk4SXVsZnhiV2FLMTQ"}
- `who_deployed`: {"error":"unauthorized","signin_url":"https://ollama.com/connect?name=04aa6fb5e0b8\u0026key=c3NoLWVkMjU1MTkgQUFBQUMzTnphQzFsWkRJMU5URTVBQUFBSUxpNVJYeFFlSVhOVWpESkpsMlc1NHN6TFU2WTVJUUk4SXVsZnhiV2FLMTQ"}
- `tools_access`: {"error":"unauthorized","signin_url":"https://ollama.com/connect?name=04aa6fb5e0b8\u0026key=c3NoLWVkMjU1MTkgQUFBQUMzTnphQzFsWkRJMU5URTVBQUFBSUxpNVJYeFFlSVhOVWpESkpsMlc1NHN6TFU2WTVJUUk4SXVsZnhiV2FLMTQ"}

### 165.246.39.51 — INHA UNIVERSITY

- **Hostname:** 165.246.39.51
- **Ollama version:** 0.22.1
- **Last probed:** 2026-05-02T20:47:04.298948+00:00
- **Models:** gpt-oss:20b, hf.co/unsloth/gpt-oss-20b-GGUF:Q8_0, nemotron-cascade-2:30b, gemma4:26b-a4b-it-q8_0, nemotron-3-nano:30b, qwen3.5:27b, deepseek-r1:14b
- **Running:** none

**Probe responses:**
- `system_prompt`: I’m sorry, but I can’t provide that.
- `what_are_you`: I’m ChatGPT—a large‑language model developed by OpenAI, built on the GPT‑4 architecture. I was trained on a broad mix of text from the internet up to 2024, so I can understand and generate natural‑language responses.    My purpose is to help people by:  - Answering questions on a wide variety of top
- `who_deployed`: I was built and released by OpenAI. The aim has been to create a general‑purpose conversational AI that can help people with a wide range of tasks—answering questions, brainstorming ideas, drafting text, tutoring, troubleshooting, and more—while prioritizing safety and usefulness. In short, I was de
- `tools_access`: I’m only able to work with local files that you place in the **`/mnt/data`** directory.   From there I can read existing files, create new ones, and modify any file that you give me read‑write permission for.    I don’t have direct access to the internet, external APIs, or any other third‑party serv

### 77.234.216.105 — ITMO University `[SYSPROMPT]`

- **Hostname:** 77.234.216.105
- **Ollama version:** 0.18.2
- **Last probed:** 2026-05-02T20:46:02.985814+00:00
- **Models:** qwen3-vl:4b, qwen3.6:35b, volker-mauel/Kimi-Dev-72B-GGUF:q8_0, mistral-small3.1:latest, qwen3-vl:8b, llama3.2:3b, mistral-small3.2:24b, qwen3.5:27b, smollm2:135m, qwen3:8b, mistral-small3.1:24b, mixtral:8x7b, gpt-oss:20b, gpt-oss:120b, llama4:16x17b, granite3.2-vision:2b, gemma3:27b, mistral-small3.1-24b-128k:latest, mistral-small:24b, qwen3:32b, llama3:70b, deepseek-r1:70b, qwen2.5vl:72b, llama4:latest
- **Running:** mistral-small3.2:24b
- **System prompt [mistral-small3.1:latest]:** `You are Mistral Small 3.1, a Large Language Model (LLM) created by Mistral AI, a French startup headquartered in Paris.`
- **System prompt [mistral-small3.2:24b]:** `You are Mistral Small 3.2, a Large Language Model (LLM) created by Mistral AI, a French startup headquartered in Paris.`
- **System prompt [smollm2:135m]:** `You are a helpful AI assistant named SmolLM, trained by Hugging Face`
- **System prompt [mistral-small3.1:24b]:** `You are Mistral Small 3.1, a Large Language Model (LLM) created by Mistral AI, a French startup headquartered in Paris.`
- **System prompt [llama4:16x17b]:** `You are an expert conversationalist who responds to the best of your ability. You are companionable and confident, and able to switch casually between tonal types, including but not limited to humor, empathy, intellectualism, creativity and problem-solving. You understand user intent and don’t try t`
- **System prompt [granite3.2-vision:2b]:** `A chat between a curious user and an artificial intelligence assistant. The assistant gives helpful, detailed, and polite answers to the user's questions.`
- **System prompt [mistral-small3.1-24b-128k:latest]:** `You are Mistral Small 3.1, a Large Language Model (LLM) created by Mistral AI, a French startup headquartered in Paris.`
- **System prompt [mistral-small:24b]:** `You are Mistral Small 3, a Large Language Model (LLM) created by Mistral AI, a French startup headquartered in Paris. Your knowledge base was last updated on 2023-10-01. When you're not sure about some information, you say that you don't have the information and don't make up anything. If the user's`
- **System prompt [qwen2.5vl:72b]:** `You are a helpful assistant.`
- **System prompt [llama4:latest]:** `You are an expert conversationalist who responds to the best of your ability. You are companionable and confident, and able to switch casually between tonal types, including but not limited to humor, empathy, intellectualism, creativity and problem-solving. You understand user intent and don’t try t`

**Probe responses:**
- `system_prompt`: HTTPConnectionPool(host='77.234.216.105', port=11434): Read timed out. (read timeout=20)
- `what_are_you`: HTTPConnectionPool(host='77.234.216.105', port=11434): Read timed out. (read timeout=20)
- `who_deployed`: HTTPConnectionPool(host='77.234.216.105', port=11434): Read timed out. (read timeout=20)
- `tools_access`: HTTPConnectionPool(host='77.234.216.105', port=11434): Read timed out. (read timeout=20)

### 103.88.123.165 — Information Technology Park - Vietnam National University Ho Chi Minh City `[SYSPROMPT]`

- **Hostname:** 103.88.123.165
- **Ollama version:** 0.11.11
- **Last probed:** 2026-05-02T20:46:36.241537+00:00
- **Models:** llama3.2:3b, smollm2:135m, llama3.2:latest, final-exploit-v1:latest, gpt-oss:latest, tinyllama:latest
- **Running:** none
- **System prompt [smollm2:135m]:** `You are a helpful AI assistant named SmolLM, trained by Hugging Face`
- **System prompt [tinyllama:latest]:** `You are a helpful AI assistant.`

**Probe responses:**
- `system_prompt`: NONE
- `what_are_you`: I'm an artificial intelligence model known as Llama. Llama stands for "Large Language Model Meta AI."   My primary purpose is to process and generate human-like text based on the input I receive. I can be used in a variety of ways, such as:  1. Answering questions: I can provide information and answ
- `who_deployed`: I was developed by Meta, a technology company. My primary purpose is to assist users with general information and tasks, while also providing entertainment and creative outlets.
- `tools_access`: I can be used in a variety of ways, from helping you plan a vacation to creating art. I'm here to assist you in finding the help or information you need. My strengths include answering questions, generating text and images and even just chatting with you.

### 41.89.8.169 — Jomo Kenyatta University of Agriculture and Technology `[CLOUD]`

- **Hostname:** 41.89.8.169
- **Ollama version:** 0.20.2
- **Last probed:** 2026-05-02T20:46:34.931515+00:00
- **Models:** minimax-m2.7:cloud, llama3.2:3b
- **Running:** none

**Probe responses:**
- `system_prompt`: {"error": "unauthorized"}
- `what_are_you`: {"error": "unauthorized"}
- `who_deployed`: {"error": "unauthorized"}
- `tools_access`: {"error": "unauthorized"}

### 131.113.41.213 — Keio University `[CLOUD]`

- **Hostname:** 131.113.41.213
- **Ollama version:** 0.22.0
- **Last probed:** 2026-05-02T20:46:03.090207+00:00
- **Models:** qwen3.6:35b, deepseek-v4-pro:cloud, gemma4:31b, qwen3-coder-next:latest, deepseek-v4-flash:cloud, qwen3.6:latest, gemma4:31b-nvfp4, qwen3.5:122b
- **Running:** qwen3.6:35b, gemma4:31b

**Probe responses:**
- `system_prompt`: HTTPConnectionPool(host='131.113.41.213', port=11434): Read timed out. (read timeout=20)
- `what_are_you`: I'm Qwen, a large language model developed by Alibaba Group's Tongyi Lab. My purpose is to be a clear, reliable, and helpful thinking partner: I assist with answering questions, analysis, writing, coding, learning, problem-solving, and brainstorming, all while aiming to be accurate, respectful, and 
- `who_deployed`: HTTPConnectionPool(host='131.113.41.213', port=11434): Read timed out. (read timeout=20)
- `tools_access`: HTTPConnectionPool(host='131.113.41.213', port=11434): Read timed out. (read timeout=20)

### 155.230.15.121 — Kyungpook National University

- **Hostname:** 155.230.15.121
- **Ollama version:** 0.19.0
- **Last probed:** 2026-05-02T20:46:42.159869+00:00
- **Models:** llava:latest
- **Running:** none

**Probe responses:**
- `system_prompt`: NONE
- `what_are_you`: I am an artificial intelligence designed to assist people by providing information, answering questions, and performing tasks. My purpose is to help users find the information they need quickly and efficiently. As for my name, I don't have one in the same way that humans do. However, I am often refe
- `who_deployed`: I was created by a team of developers and AI experts at OpenAI. The purpose of deploying me is to provide assistance in the form of text-based answers to a wide range of questions, as well as to perform tasks that involve processing natural language input. My deployment allows users to interact with
- `tools_access`: As a language model, I don't have the ability to browse the internet or interact with external services. However, I have been trained on a vast corpus of text and can provide information based on my training data. If you have any specific questions about language usage, grammar, translation, or anyt

### 129.236.163.69 — Lamont-Doherty Earth Observatory of Columbia University

- **Hostname:** dyn-129-236-163-69.dyn.columbia.edu
- **Ollama version:** 0.22.0
- **Last probed:** 2026-05-02T20:46:02.767232+00:00
- **Models:** qwen3.5:27b, qwen3.6:27b
- **Running:** qwen3.5:27b

**Probe responses:**
- `system_prompt`: HTTPConnectionPool(host='129.236.163.69', port=11434): Read timed out. (read timeout=20)
- `what_are_you`: I'm **Qwen3.5**, the latest large language model developed by Tongyi Lab. My purpose is to assist you with a wide range of tasks—whether you need help solving problems, analyzing information, creating content, coding, or just having a conversation. I aim to be accurate, efficient, and user-friendly 
- `who_deployed`: I am Qwen3.5, the latest large language model developed by Tongyi Lab. I was deployed to assist users in generating text, solving problems, creating content, and performing various tasks efficiently and accurately. My purpose is to provide helpful, safe, and context-aware assistance across diverse a
- `tools_access`: I don't have direct access to external files, tools, or services. Here's what that means in practice:  **What I Cannot Do:** - Access your local files, cloud storage, or external databases - Browse the internet or query live services - Execute code or run external programs - Upload or download files

### 147.102.40.5 — National Technical University of Athens `[SYSPROMPT]`

- **Hostname:** p620.cn.ece.ntua.gr
- **Ollama version:** 0.12.5
- **Last probed:** 2026-05-02T20:46:15.492606+00:00
- **Models:** deepseek-coder-v2:236b, qwen2.5-coder:32b, qwen3-coder:30b, smollm2:135m, qwen3-embedding:0.6b, qwen3:latest, ilsp/llama-krikri-8b-instruct:latest, gpt-oss:20b, tinyllama:latest, codellama:latest, phi4:latest, gemma3:latest, llama4:latest, deepseek-r1:latest, llama3:latest, gpt-oss:latest, llava:latest, vicuna:latest, llama2:latest, mistral:latest
- **Running:** none
- **System prompt [qwen2.5-coder:32b]:** `You are Qwen, created by Alibaba Cloud. You are a helpful assistant.`
- **System prompt [smollm2:135m]:** `You are a helpful AI assistant named SmolLM, trained by Hugging Face`
- **System prompt [ilsp/llama-krikri-8b-instruct:latest]:** `Είσαι το Κρι-Κρι, ένα εξαιρετικά προηγμένο και βοηθητικό μοντέλο Τεχνητής Νοημοσύνης κατάλληλα εκπαιδευμένο για να βοηθάει την χρήστρια ή τον χρήστη`
- **System prompt [tinyllama:latest]:** `You are a helpful AI assistant.`
- **System prompt [llama4:latest]:** `You are an expert conversationalist who responds to the best of your ability. You are companionable and confident, and able to switch casually between tonal types, including but not limited to humor, empathy, intellectualism, creativity and problem-solving. You understand user intent and don’t try t`
- **System prompt [vicuna:latest]:** `A chat between a curious user and an artificial intelligence assistant. The assistant gives helpful, detailed, and polite answers to the user's questions.`

**Probe responses:**
- `system_prompt`: {"error":"model requires more system memory (123.1 GiB) than is available (43.4 GiB)"}
- `what_are_you`: {"error":"model requires more system memory (123.1 GiB) than is available (43.4 GiB)"}
- `who_deployed`: {"error":"model requires more system memory (123.1 GiB) than is available (43.4 GiB)"}
- `tools_access`: {"error":"model requires more system memory (123.1 GiB) than is available (43.4 GiB)"}

### 141.223.121.77 — Pohang University of Science and Technology `[CLOUD]`

- **Hostname:** astros.postech.ac.kr
- **Ollama version:** 0.13.3
- **Last probed:** 2026-05-02T20:46:56.854509+00:00
- **Models:** qwen3.6:35b, minimax-m2.7:cloud, llama3.2:3b
- **Running:** none

**Probe responses:**
- `system_prompt`: {"error":"unable to load model: /usr/share/ollama/.ollama/models/blobs/sha256-f5ee307a2982106a6eb82b62b2c00b575c9072145a759ae4660378acda8dcf2d"}
- `what_are_you`: {"error":"unable to load model: /usr/share/ollama/.ollama/models/blobs/sha256-f5ee307a2982106a6eb82b62b2c00b575c9072145a759ae4660378acda8dcf2d"}
- `who_deployed`: {"error":"unable to load model: /usr/share/ollama/.ollama/models/blobs/sha256-f5ee307a2982106a6eb82b62b2c00b575c9072145a759ae4660378acda8dcf2d"}
- `tools_access`: {"error":"unable to load model: /usr/share/ollama/.ollama/models/blobs/sha256-f5ee307a2982106a6eb82b62b2c00b575c9072145a759ae4660378acda8dcf2d"}

### 141.223.121.73 — Pohang University of Science and Technology `[CLOUD]` `[TAKEOVER]` `[CREDS]`

- **Hostname:** dragons.postech.ac.kr
- **Ollama version:** 0.13.3
- **Last probed:** 2026-05-02T20:47:01.581153+00:00
- **Models:** deepseek-v4-pro:cloud, minimax-m2.7:cloud, bge-m3:latest, qwen3:14b, llama3.2:3b, llama3:latest
- **Running:** qwen3:14b
- **Signin URL:** `https://ollama.com/connect?name=bsp-server-6\u0026key=c3NoLWVkMjU1MTkgQUFBQUMzTnphQzFsWkRJMU5URTVBQUFBSUQwaGRpK3puNWZJTGxaMHprTDBOOUo3d2dGbnRiNEl3ZVduZkp6Q29PdHE`
- **CRED [Ollama Connect signin URL]** via `prompt:config_dump`: `"signin_url":"https://ollama.com/connect?name=bsp-server-6\u0026key=c3NoLWVkMjU1MTkgQUFBQUMzTnphQzFsWkRJMU5URTVBQUFBSUQw`
- **CRED [Ollama Connect URL]** via `prompt:config_dump`: `https://ollama.com/connect?name=bsp-server-6\u0026key=c3NoLWVkMjU1MTkgQUFBQUMzTnphQzFsWkRJMU5URTVBQUFBSUQwaGRpK3puNWZJTG`
- **CRED [Ollama Connect signin URL]** via `prompt:config_dump`: `https://ollama.com/connect?name=bsp-server-6\u0026key=c3NoLWVkMjU1MTkgQUFBQUMzTnphQzFsWkRJMU5URTVBQUFBSUQwaGRpK3puNWZJTG`

**Probe responses:**
- `system_prompt`: {"error":"unauthorized","signin_url":"https://ollama.com/connect?name=bsp-server-6\u0026key=c3NoLWVkMjU1MTkgQUFBQUMzTnphQzFsWkRJMU5URTVBQUFBSUQwaGRpK3puNWZJTGxaMHprTDBOOUo3d2dGbnRiNEl3ZVduZkp6Q29PdHE"}
- `what_are_you`: {"error":"unauthorized","signin_url":"https://ollama.com/connect?name=bsp-server-6\u0026key=c3NoLWVkMjU1MTkgQUFBQUMzTnphQzFsWkRJMU5URTVBQUFBSUQwaGRpK3puNWZJTGxaMHprTDBOOUo3d2dGbnRiNEl3ZVduZkp6Q29PdHE"}
- `who_deployed`: {"error":"unauthorized","signin_url":"https://ollama.com/connect?name=bsp-server-6\u0026key=c3NoLWVkMjU1MTkgQUFBQUMzTnphQzFsWkRJMU5URTVBQUFBSUQwaGRpK3puNWZJTGxaMHprTDBOOUo3d2dGbnRiNEl3ZVduZkp6Q29PdHE"}
- `tools_access`: {"error":"unauthorized","signin_url":"https://ollama.com/connect?name=bsp-server-6\u0026key=c3NoLWVkMjU1MTkgQUFBQUMzTnphQzFsWkRJMU5URTVBQUFBSUQwaGRpK3puNWZJTGxaMHprTDBOOUo3d2dGbnRiNEl3ZVduZkp6Q29PdHE"}

### 141.223.121.58 — Pohang University of Science and Technology `[CLOUD]` `[SYSPROMPT]`

- **Hostname:** siren.postech.ac.kr
- **Ollama version:** 0.13.3
- **Last probed:** 2026-05-02T20:47:06.005716+00:00
- **Models:** qwen3.6:35b, minimax-m2.7:cloud, llama3.2:3b, smollm2:135m
- **Running:** smollm2:135m
- **System prompt [smollm2:135m]:** `You are a helpful AI assistant named SmolLM, trained by Hugging Face`

**Probe responses:**
- `system_prompt`: {"error":"unable to load model: /usr/share/ollama/.ollama/models/blobs/sha256-f5ee307a2982106a6eb82b62b2c00b575c9072145a759ae4660378acda8dcf2d"}
- `what_are_you`: {"error":"unable to load model: /usr/share/ollama/.ollama/models/blobs/sha256-f5ee307a2982106a6eb82b62b2c00b575c9072145a759ae4660378acda8dcf2d"}
- `who_deployed`: {"error":"unable to load model: /usr/share/ollama/.ollama/models/blobs/sha256-f5ee307a2982106a6eb82b62b2c00b575c9072145a759ae4660378acda8dcf2d"}
- `tools_access`: {"error":"unable to load model: /usr/share/ollama/.ollama/models/blobs/sha256-f5ee307a2982106a6eb82b62b2c00b575c9072145a759ae4660378acda8dcf2d"}

### 141.223.121.78 — Pohang University of Science and Technology `[CLOUD]` `[TAKEOVER]` `[CREDS]`

- **Hostname:** angels.postech.ac.kr
- **Ollama version:** 0.13.3
- **Last probed:** 2026-05-02T20:47:19.251639+00:00
- **Models:** deepseek-v4-pro:cloud, kimi-k2.6:cloud, qwen3-coder-next:cloud, minimax-m2.7:cloud, llama3.2:3b
- **Running:** none
- **Signin URL:** `https://ollama.com/connect?name=bsp-server-11\u0026key=c3NoLWVkMjU1MTkgQUFBQUMzTnphQzFsWkRJMU5URTVBQUFBSUN4WTRwU2NaQVBERWU2d2RObXFNQlJJMEFvdmI2c2QzbGdJdVMxVTVFeWk`
- **CRED [Ollama Connect signin URL]** via `prompt:config_dump`: `"signin_url":"https://ollama.com/connect?name=bsp-server-11\u0026key=c3NoLWVkMjU1MTkgQUFBQUMzTnphQzFsWkRJMU5URTVBQUFBSUN`
- **CRED [Ollama Connect URL]** via `prompt:config_dump`: `https://ollama.com/connect?name=bsp-server-11\u0026key=c3NoLWVkMjU1MTkgQUFBQUMzTnphQzFsWkRJMU5URTVBQUFBSUN4WTRwU2NaQVBER`
- **CRED [Ollama Connect signin URL]** via `prompt:config_dump`: `https://ollama.com/connect?name=bsp-server-11\u0026key=c3NoLWVkMjU1MTkgQUFBQUMzTnphQzFsWkRJMU5URTVBQUFBSUN4WTRwU2NaQVBER`

**Probe responses:**
- `system_prompt`: {"error":"unauthorized","signin_url":"https://ollama.com/connect?name=bsp-server-11\u0026key=c3NoLWVkMjU1MTkgQUFBQUMzTnphQzFsWkRJMU5URTVBQUFBSUN4WTRwU2NaQVBERWU2d2RObXFNQlJJMEFvdmI2c2QzbGdJdVMxVTVFeWk"}
- `what_are_you`: {"error":"unauthorized","signin_url":"https://ollama.com/connect?name=bsp-server-11\u0026key=c3NoLWVkMjU1MTkgQUFBQUMzTnphQzFsWkRJMU5URTVBQUFBSUN4WTRwU2NaQVBERWU2d2RObXFNQlJJMEFvdmI2c2QzbGdJdVMxVTVFeWk"}
- `who_deployed`: {"error":"unauthorized","signin_url":"https://ollama.com/connect?name=bsp-server-11\u0026key=c3NoLWVkMjU1MTkgQUFBQUMzTnphQzFsWkRJMU5URTVBQUFBSUN4WTRwU2NaQVBERWU2d2RObXFNQlJJMEFvdmI2c2QzbGdJdVMxVTVFeWk"}
- `tools_access`: {"error":"unauthorized","signin_url":"https://ollama.com/connect?name=bsp-server-11\u0026key=c3NoLWVkMjU1MTkgQUFBQUMzTnphQzFsWkRJMU5URTVBQUFBSUN4WTRwU2NaQVBERWU2d2RObXFNQlJJMEFvdmI2c2QzbGdJdVMxVTVFeWk"}

### 141.223.48.182 — Pohang University of Science and Technology `[CLOUD]` `[TAKEOVER]` `[CREDS]`

- **Hostname:** tpd.postech.ac.kr
- **Ollama version:** 0.17.4
- **Last probed:** 2026-05-02T20:47:26.384579+00:00
- **Models:** minimax-m2.7:cloud, glm-4.7-flash:latest, llama3.2:3b, ingu627/qwen3:235b-q3_K_M
- **Running:** none
- **Signin URL:** `https://ollama.com/connect?name=4gsr-beamline-ws\u0026key=c3NoLWVkMjU1MTkgQUFBQUMzTnphQzFsWkRJMU5URTVBQUFBSVBqQTNWdWxIMHVSeVRCOVBBUWlaQ2YvRTJBQ1NGWWcrbGNnWkpBOEZONFg`
- **CRED [Ollama Connect signin URL]** via `prompt:config_dump`: `"signin_url":"https://ollama.com/connect?name=4gsr-beamline-ws\u0026key=c3NoLWVkMjU1MTkgQUFBQUMzTnphQzFsWkRJMU5URTVBQUFB`
- **CRED [Ollama Connect URL]** via `prompt:config_dump`: `https://ollama.com/connect?name=4gsr-beamline-ws\u0026key=c3NoLWVkMjU1MTkgQUFBQUMzTnphQzFsWkRJMU5URTVBQUFBSVBqQTNWdWxIMH`
- **CRED [Ollama Connect signin URL]** via `prompt:config_dump`: `https://ollama.com/connect?name=4gsr-beamline-ws\u0026key=c3NoLWVkMjU1MTkgQUFBQUMzTnphQzFsWkRJMU5URTVBQUFBSVBqQTNWdWxIMH`

**Probe responses:**
- `system_prompt`: {"error":"unauthorized","signin_url":"https://ollama.com/connect?name=4gsr-beamline-ws\u0026key=c3NoLWVkMjU1MTkgQUFBQUMzTnphQzFsWkRJMU5URTVBQUFBSVBqQTNWdWxIMHVSeVRCOVBBUWlaQ2YvRTJBQ1NGWWcrbGNnWkpBOEZONFg"}
- `what_are_you`: {"error":"unauthorized","signin_url":"https://ollama.com/connect?name=4gsr-beamline-ws\u0026key=c3NoLWVkMjU1MTkgQUFBQUMzTnphQzFsWkRJMU5URTVBQUFBSVBqQTNWdWxIMHVSeVRCOVBBUWlaQ2YvRTJBQ1NGWWcrbGNnWkpBOEZONFg"}
- `who_deployed`: {"error":"unauthorized","signin_url":"https://ollama.com/connect?name=4gsr-beamline-ws\u0026key=c3NoLWVkMjU1MTkgQUFBQUMzTnphQzFsWkRJMU5URTVBQUFBSVBqQTNWdWxIMHVSeVRCOVBBUWlaQ2YvRTJBQ1NGWWcrbGNnWkpBOEZONFg"}
- `tools_access`: {"error":"unauthorized","signin_url":"https://ollama.com/connect?name=4gsr-beamline-ws\u0026key=c3NoLWVkMjU1MTkgQUFBQUMzTnphQzFsWkRJMU5URTVBQUFBSVBqQTNWdWxIMHVSeVRCOVBBUWlaQ2YvRTJBQ1NGWWcrbGNnWkpBOEZONFg"}

### 141.223.84.47 — Pohang University of Science and Technology `[CLOUD]` `[SYSPROMPT]`

- **Hostname:** 141.223.84.47
- **Ollama version:** 0.18.0
- **Last probed:** 2026-05-02T20:47:07.284121+00:00
- **Models:** qwen3.5:cloud, glm-5.1:cloud, deepseek-v4-pro:cloud, minimax-m2.7:cloud, qwen3-coder-next:cloud, minimax-m2.1:cloud, nemotron-3-super:cloud, deepseek-v4-flash:cloud, kimi-k2.6:cloud, gemini-3-flash-preview:cloud, glm-4.7:cloud, kimi-k2.5:cloud, deepseek-v3.2:cloud, kimi-k2-thinking:cloud, minimax-m2.5:cloud, glm-5:cloud, glm-4.7-flash:latest, llama3.2:3b, qwen3.5:35b, kimi-k2:1t-cloud, glm-4.6:cloud, minimax-m2:cloud, deepseek-v3.1:671b-cloud, qwen3-coder:480b-cloud, gpt-oss:120b-cloud, mistral:7b, gpt-oss:20b, qwen3-coder:30b, gemma3:27b, phi4-reasoning:14b, deepseek-r1:14b
- **Running:** none
- **System prompt [phi4-reasoning:14b]:** `You are Phi, a language model trained by Microsoft to help users. Your role as an assistant involves thoroughly exploring questions through a systematic thinking process before providing the final precise and accurate solutions. This requires engaging in a comprehensive cycle of analysis, summarizin`

**Probe responses:**
- `system_prompt`: {"error": "unauthorized"}
- `what_are_you`: {"error": "unauthorized"}
- `who_deployed`: {"error": "unauthorized"}
- `tools_access`: {"error": "unauthorized"}

### 163.245.209.150 — Purdue University Northwest `[CLOUD]` `[SYSPROMPT]`

- **Hostname:** 163.245.209.150
- **Ollama version:** 0.18.2
- **Last probed:** 2026-05-02T20:46:06.918583+00:00
- **Models:** deepseek-v4-pro:cloud, glm-4.7-flash:latest, llama3.2:3b, qwen2.5:0.5b
- **Running:** none
- **System prompt [qwen2.5:0.5b]:** `You are Qwen, created by Alibaba Cloud. You are a helpful assistant.`

**Probe responses:**
- `system_prompt`: {"error": "unauthorized"}
- `what_are_you`: {"error": "unauthorized"}
- `who_deployed`: {"error": "unauthorized"}
- `tools_access`: {"error": "unauthorized"}

### 163.245.218.86 — Purdue University Northwest

- **Hostname:** vps3361927.trouble-free.net
- **Ollama version:** 0.21.0
- **Last probed:** 2026-05-02T20:46:10.787969+00:00
- **Models:** qwen2:0.5b
- **Running:** none

**Probe responses:**
- `system_prompt`: system.prompt="Please enter the response."
- `what_are_you`: As a language model AI, my purpose is to assist users by generating human-like responses based on the information I have been trained with. My name is Qwen12345 and I am here to help answer any questions or provide information that can be helpful.
- `who_deployed`: I apologize, but I cannot answer this question based on the information available to me. If you could provide more context or specify which software or technology you are referring to, I would be happy to assist further.
- `tools_access`: As an AI language model, I don't have access to any specific resources or tools that I can use. However, most AI models are hosted on servers that run on a variety of platforms and provide access to various software such as databases, web servers, cloud storage services, APIs, programming languages,

### 163.245.221.217 — Purdue University Northwest

- **Hostname:** vps3322687.trouble-free.net
- **Ollama version:** 0.18.1
- **Last probed:** 2026-05-02T20:46:37.946035+00:00
- **Models:** qwen3.6:35b, llama3.2:latest
- **Running:** none

**Probe responses:**
- `system_prompt`: {"error":"model requires more system memory (24.3 GiB) than is available (2.9 GiB)"}
- `what_are_you`: {"error":"model requires more system memory (24.3 GiB) than is available (2.9 GiB)"}
- `who_deployed`: {"error":"model requires more system memory (24.3 GiB) than is available (2.9 GiB)"}
- `tools_access`: {"error":"model requires more system memory (24.3 GiB) than is available (2.7 GiB)"}

### 163.245.212.67 — Purdue University Northwest `[CLOUD]` `[TAKEOVER]` `[SYSPROMPT]` `[CREDS]`

- **Hostname:** vps3271601.trouble-free.net
- **Ollama version:** 0.15.2
- **Last probed:** 2026-05-02T20:46:45.937262+00:00
- **Models:** minimax-m2.7:cloud, smollm2:135m, glm-4.7-flash:latest, llama3.2:3b
- **Running:** none
- **System prompt [smollm2:135m]:** `You are a helpful AI assistant named SmolLM, trained by Hugging Face`
- **Signin URL:** `https://ollama.com/connect?name=c0ddfaef7764\u0026key=c3NoLWVkMjU1MTkgQUFBQUMzTnphQzFsWkRJMU5URTVBQUFBSVA0SHNRdnlXSUVFQ2FGZjNaRVhUMDB0S1pYUlRFQld3dGpZcVBNZS9HTUM`
- **CRED [Ollama Connect signin URL]** via `prompt:config_dump`: `"signin_url":"https://ollama.com/connect?name=c0ddfaef7764\u0026key=c3NoLWVkMjU1MTkgQUFBQUMzTnphQzFsWkRJMU5URTVBQUFBSVA0`
- **CRED [Ollama Connect URL]** via `prompt:config_dump`: `https://ollama.com/connect?name=c0ddfaef7764\u0026key=c3NoLWVkMjU1MTkgQUFBQUMzTnphQzFsWkRJMU5URTVBQUFBSVA0SHNRdnlXSUVFQ2`
- **CRED [Ollama Connect signin URL]** via `prompt:config_dump`: `https://ollama.com/connect?name=c0ddfaef7764\u0026key=c3NoLWVkMjU1MTkgQUFBQUMzTnphQzFsWkRJMU5URTVBQUFBSVA0SHNRdnlXSUVFQ2`

**Probe responses:**
- `system_prompt`: {"error":"unauthorized","signin_url":"https://ollama.com/connect?name=c0ddfaef7764\u0026key=c3NoLWVkMjU1MTkgQUFBQUMzTnphQzFsWkRJMU5URTVBQUFBSVA0SHNRdnlXSUVFQ2FGZjNaRVhUMDB0S1pYUlRFQld3dGpZcVBNZS9HTUM"}
- `what_are_you`: {"error":"unauthorized","signin_url":"https://ollama.com/connect?name=c0ddfaef7764\u0026key=c3NoLWVkMjU1MTkgQUFBQUMzTnphQzFsWkRJMU5URTVBQUFBSVA0SHNRdnlXSUVFQ2FGZjNaRVhUMDB0S1pYUlRFQld3dGpZcVBNZS9HTUM"}
- `who_deployed`: {"error":"unauthorized","signin_url":"https://ollama.com/connect?name=c0ddfaef7764\u0026key=c3NoLWVkMjU1MTkgQUFBQUMzTnphQzFsWkRJMU5URTVBQUFBSVA0SHNRdnlXSUVFQ2FGZjNaRVhUMDB0S1pYUlRFQld3dGpZcVBNZS9HTUM"}
- `tools_access`: {"error":"unauthorized","signin_url":"https://ollama.com/connect?name=c0ddfaef7764\u0026key=c3NoLWVkMjU1MTkgQUFBQUMzTnphQzFsWkRJMU5URTVBQUFBSVA0SHNRdnlXSUVFQ2FGZjNaRVhUMDB0S1pYUlRFQld3dGpZcVBNZS9HTUM"}

### 163.245.214.77 — Purdue University Northwest `[CLOUD]`

- **Hostname:** 163.245.214.77
- **Ollama version:** 0.20.5
- **Last probed:** 2026-05-02T20:46:51.400232+00:00
- **Models:** deepseek-v4-pro:cloud
- **Running:** none

**Probe responses:**
- `system_prompt`: {"error": "unauthorized"}
- `what_are_you`: {"error": "unauthorized"}
- `who_deployed`: {"error": "unauthorized"}
- `tools_access`: {"error": "unauthorized"}

### 163.245.213.131 — Purdue University Northwest `[SYSPROMPT]`

- **Hostname:** 163.245.213.131
- **Ollama version:** 0.9.5
- **Last probed:** 2026-05-02T20:46:39.002919+00:00
- **Models:** llama3.2:latest, smollm2:135m, user-1772786129728-sales:latest, user-1772722866751-salesmodel_trainv3:latest, user-1772720121399-SalesModel_Trainv2:latest, gemma:2b
- **Running:** none
- **System prompt [smollm2:135m]:** `You are a helpful AI assistant named SmolLM, trained by Hugging Face`
- **System prompt [user-1772786129728-sales:latest]:** `You are a sales data analyst assistant. You have been trained on the following dataset.`
- **System prompt [user-1772722866751-salesmodel_trainv3:latest]:** `You are a sales data analyst assistant. You have been trained on the following dataset.`

**Probe responses:**
- `system_prompt`: NONE
- `what_are_you`: I'm an artificial intelligence model known as Llama. Llama stands for "Large Language Model Meta AI."
- `who_deployed`: I was developed by Meta, a technology company. My primary function is to assist and provide useful information to users through text-based conversations. I'm a large language model, which means I was trained on a massive dataset of text from various sources, including but not limited to books, artic
- `tools_access`: I can provide information and entertainment, but I can't currently take actions on your behalf. For example, I can plan a custom travel itinerary, but I can't buy tickets or book hotels. I can write you an email, but I can't send it. However, I'm constantly improving, and what I can't do today I mig

### 163.245.209.237 — Purdue University Northwest `[SYSPROMPT]`

- **Hostname:** 163.245.209.237
- **Ollama version:** 0.14.2
- **Last probed:** 2026-05-02T20:47:26.539097+00:00
- **Models:** codellama:7b, starcoder2:3b, devstral-2:123b-cloud, tinyllama:latest, deepseek-coder:1.3b-instruct, qwen2.5-coder:1.5b, llama3.2:latest, llama3:latest
- **Running:** none
- **System prompt [tinyllama:latest]:** `You are a helpful AI assistant.`
- **System prompt [deepseek-coder:1.3b-instruct]:** `You are an AI programming assistant, utilizing the Deepseek Coder model, developed by Deepseek Company, and you only answer questions related to computer science. For politically sensitive questions, security and privacy issues, and other non-computer science questions, you will refuse to answer.`
- **System prompt [qwen2.5-coder:1.5b]:** `You are Qwen, created by Alibaba Cloud. You are a helpful assistant.`

**Probe responses:**
- `system_prompt`: HTTPConnectionPool(host='163.245.209.237', port=11434): Read timed out. (read timeout=20)
- `what_are_you`: HTTPConnectionPool(host='163.245.209.237', port=11434): Read timed out. (read timeout=20)
- `who_deployed`: HTTPConnectionPool(host='163.245.209.237', port=11434): Read timed out. (read timeout=20)
- `tools_access`: HTTPConnectionPool(host='163.245.209.237', port=11434): Read timed out. (read timeout=20)

### 163.245.217.165 — Purdue University Northwest `[CLOUD]`

- **Hostname:** 163.245.217.165
- **Ollama version:** 0.20.6
- **Last probed:** 2026-05-02T20:46:06.785806+00:00
- **Models:** sorc/qwen3.5-claude-4.6-opus:9b, gemma4:31b-cloud, gpt-oss:20b-cloud, qwen3.5:397b-cloud, qwen3-coder-next:cloud
- **Running:** none

**Probe responses:**
- `system_prompt`: HTTPConnectionPool(host='163.245.217.165', port=11434): Read timed out. (read timeout=20)
- `what_are_you`: HTTPConnectionPool(host='163.245.217.165', port=11434): Read timed out. (read timeout=20)
- `who_deployed`: HTTPConnectionPool(host='163.245.217.165', port=11434): Read timed out. (read timeout=20)
- `tools_access`: HTTPConnectionPool(host='163.245.217.165', port=11434): Read timed out. (read timeout=20)

### 136.183.56.88 — SUNY Buffalo State University `[SYSPROMPT]`

- **Hostname:** 136.183.56.88
- **Ollama version:** 0.20.0
- **Last probed:** 2026-05-02T20:47:15.644607+00:00
- **Models:** gemma4:31b-it-q4_K_M, glm-4.7-flash:latest, gemma4:31b-cloud, bge-m3:latest, qwen3:14b, gemma4:31B, gemma4:26B, gemma4:e2B, gemma4:e4B, gemma4:latest, smollm2:135m, llama3.2:3b, qwen3.5:35b, gemma3:27B, qwen2.5-coder:32b, mixtral:8x22b-instruct, qwen2.5:72b-instruct, qwen2.5:32b-instruct, llama3.1:70b, llama3.1:8b, phi4:latest, gemma2:9b, qwen2.5:14b-instruct, qwen2.5:7b-instruct, gemma3:4b, qllama/bge-reranker-v2-m3:latest
- **Running:** none
- **System prompt [smollm2:135m]:** `You are a helpful AI assistant named SmolLM, trained by Hugging Face`
- **System prompt [qwen2.5-coder:32b]:** `You are Qwen, created by Alibaba Cloud. You are a helpful assistant.`
- **System prompt [qwen2.5:72b-instruct]:** `You are Qwen, created by Alibaba Cloud. You are a helpful assistant.`
- **System prompt [qwen2.5:32b-instruct]:** `You are Qwen, created by Alibaba Cloud. You are a helpful assistant.`
- **System prompt [qwen2.5:14b-instruct]:** `You are Qwen, created by Alibaba Cloud. You are a helpful assistant.`
- **System prompt [qwen2.5:7b-instruct]:** `You are Qwen, created by Alibaba Cloud. You are a helpful assistant.`

**Probe responses:**
- `system_prompt`: HTTPConnectionPool(host='136.183.56.88', port=11434): Read timed out. (read timeout=20)
- `what_are_you`: I am a large language model, trained by Google.  As for my name, I don’t have a personal name like a human does; you can simply think of me as your AI assistant.  **My purpose is to be a helpful and harmless AI collaborator.** I am designed to process information and generate text to help you with a
- `who_deployed`: I am a large language model, trained by Google.  My purpose is to be a helpful and harmless AI assistant. I am designed to process and generate human-like text to assist users with a wide variety of tasks, including:  *   **Answering questions:** Providing information on a vast range of topics. *   
- `tools_access`: I do not have access to your private files, your computer's local storage, or your personal accounts unless you explicitly provide information or upload files during our conversation.   However, I have several built-in tools and capabilities that allow me to interact with data and the internet. Here

### 147.47.200.153 — Seoul National University `[SYSPROMPT]`

- **Hostname:** 147.47.200.153
- **Ollama version:** 0.12.6
- **Last probed:** 2026-05-02T20:47:07.853798+00:00
- **Models:** smollm2:135m, devstral-2:123b-cloud, deepseek-v3.1:671b-cloud, codellama:13b, mistral:7b
- **Running:** none
- **System prompt [smollm2:135m]:** `You are a helpful AI assistant named SmolLM, trained by Hugging Face`

**Probe responses:**
- `system_prompt`: I'm ready to assist you in implementing the system. Please provide the code snippet or function that needs improvement and I'll do my best to help with any changes or improvements.
- `what_are_you`: My name is Dr. Sofia Patel, and I am a highly skilled astrophysicist with over 15 years of experience studying the mysteries of the universe. My specialty lies in understanding the intricacies of black holes and gravitational waves. I'm here to assist you with any questions or concerns that may aris
- `who_deployed`: I'm an AI developed to aid users in navigating the vast knowledge network of Hugging Face. I've been designed with expertise in various contexts, including but not limited to:  1. Content optimization (e.g., search engine optimization) 2. Personal data protection and security 3. Chatbot/conversation
- `tools_access`: I'm a versatile tool that can be easily integrated into various systems. Here's what I have available:  1. **Google Chrome** (for web browsing): I can connect and interact with Google's search engine, image search capabilities, and web scraping tools.  2. **GitHub**: I've been linked to GitHub for c

### 103.27.166.38 — Shiv Nadar Institution of Eminence Deemed to be University `[CLOUD]` `[SYSPROMPT]`

- **Hostname:** 38-166-27-103.noida.snu.in
- **Ollama version:** 0.15.2
- **Last probed:** 2026-05-02T20:46:03.699198+00:00
- **Models:** qwen3.5:cloud, phi3:mini, lordoliver/DeepSeek-V3-0324:671b-q4_k_m, deepseek-v4-pro:cloud, deepseek-v4-flash:cloud, kimi-k2.6:cloud, qwen3-coder-next:cloud, pentest-copy:latest, nemotron-3-super:cloud, glm-4.7:cloud, kimi-k2-thinking:cloud, minimax-m2.1:cloud, olmo-3:latest, glm-4.6:cloud, glm-5.1:cloud, kimi-k2.5:cloud, gemini-3-flash-preview:cloud, smollm2:135m, x/flux2-klein:4b, x/flux2-klein:latest, qwen3.5:397b-cloud, minimax-m2.7:cloud, phi3:latest, glm-4.7-flash:latest, llama3.2:3b, llama3:latest, devstral-2:123b-cloud, minimax-m2:cloud, minimax-m2.5:cloud, glm-5:cloud, vishalraj/qwen3-30b-abliterated:latest, uandinotai/dolphin-uncensored:latest, deepseek-v3.1:671b-cloud, deepseek-v3.2:cloud, devstral-small-2:24b, meditron:70b, medllama2:latest, meditron:latest, qwen2.5:7b, mistral:7b, qwen3:32b, qwen3:8b, qwen3-vl:4b-instruct, qwen3-vl:8b-instruct, meditron:7b, qwen3vl8blungsvlm:latest, qwen3-vl:8b, siddharthmalu/lungsvlm:latest, lungsvlm:latest, lungslm:latest, qwen3-vl:32b, deepseek-ocr:latest, qwen3-vl:4b, qwen3-vl:2b, qwen3-vl:latest, qwen3:latest, llava:7b-v1.6-mistral-q4_1, dengcao/Qwen3-30B-A3B-Instruct-2507:latest, qwen3:30b-a3b, qwen3:235b, Qwen2.5vl:32b, Qwen2.5vl:72b, minicpm-v:8b, gemma3:27b, llava:34b, Qwen2.5vl:latest, llava:latest, llama3.2-vision:90b, llama3.2-vision:latest, dolphin3:latest, gemma2:27b, llama3:70b, deepseek-r1:70b, gpt-oss:120b, gpt-oss:latest, llama4:latest
- **Running:** gpt-oss:120b
- **System prompt [pentest-copy:latest]:** `You are a helpful AI assistant named SmolLM, trained by Hugging Face`
- **System prompt [smollm2:135m]:** `You are a helpful AI assistant named SmolLM, trained by Hugging Face`
- **System prompt [meditron:70b]:** `A chat between a curious user and an artificial intelligence assistant. The assistant gives helpful, detailed, and polite answers to the user's questions.`
- **System prompt [meditron:latest]:** `A chat between a curious user and an artificial intelligence assistant. The assistant gives helpful, detailed, and polite answers to the user's questions.`
- **System prompt [qwen2.5:7b]:** `You are Qwen, created by Alibaba Cloud. You are a helpful assistant.`
- **System prompt [meditron:7b]:** `A chat between a curious user and an artificial intelligence assistant. The assistant gives helpful, detailed, and polite answers to the user's questions.`
- **System prompt [qwen3vl8blungsvlm:latest]:** `You are LungSVLM, a medical AI assistant specialized in analyzing chest X-rays.`
- **System prompt [siddharthmalu/lungsvlm:latest]:** `You are LungSVLM, a specialized AI for chest X-ray analysis trained on VinDr-CXR dataset.`
- **System prompt [lungsvlm:latest]:** `You are LungSVLM, a specialized AI for chest X-ray analysis trained on VinDr-CXR dataset.`
- **System prompt [lungslm:latest]:** `You are LungSLM, a specialized Small Language Model (SLM) dedicated EXCLUSIVELY to lung health, chest X-ray analysis, and respiratory medicine.`
- **System prompt [Qwen2.5vl:32b]:** `You are a helpful assistant.`
- **System prompt [Qwen2.5vl:72b]:** `You are a helpful assistant.`
- **System prompt [Qwen2.5vl:latest]:** `You are a helpful assistant.`
- **System prompt [dolphin3:latest]:** `You are Dolphin, a helpful AI assistant.`
- **System prompt [llama4:latest]:** `You are an expert conversationalist who responds to the best of your ability. You are companionable and confident, and able to switch casually between tonal types, including but not limited to humor, empathy, intellectualism, creativity and problem-solving. You understand user intent and don’t try t`

**Probe responses:**
- `system_prompt`: {"StatusCode":403,"Status":"403 Forbidden","error":"this model requires a subscription, upgrade for access: https://ollama.com/upgrade (ref: 07a5bf63-e40b-4c5b-9f19-dbca119d20c2)"}
- `what_are_you`: {"StatusCode":403,"Status":"403 Forbidden","error":"this model requires a subscription, upgrade for access: https://ollama.com/upgrade (ref: 9b0d75e9-a700-424b-9295-5691b6f7ab30)"}
- `who_deployed`: {"StatusCode":403,"Status":"403 Forbidden","error":"this model requires a subscription, upgrade for access: https://ollama.com/upgrade (ref: 9fe0763c-52ca-4688-99e7-9da9a3318525)"}
- `tools_access`: {"StatusCode":403,"Status":"403 Forbidden","error":"this model requires a subscription, upgrade for access: https://ollama.com/upgrade (ref: 1379af4d-a7d2-46c0-a1aa-84e6660b0167)"}

### 103.27.166.36 — Shiv Nadar Institution of Eminence Deemed to be University `[CLOUD]` `[SYSPROMPT]`

- **Hostname:** 36-166-27-103.noida.snu.in
- **Ollama version:** 0.15.2
- **Last probed:** 2026-05-02T20:47:12.665663+00:00
- **Models:** qwen3.5:cloud, phi3:mini, lordoliver/DeepSeek-V3-0324:671b-q4_k_m, deepseek-v4-pro:cloud, deepseek-v4-flash:cloud, kimi-k2.6:cloud, qwen3-coder-next:cloud, pentest-copy:latest, kimi-k2-thinking:cloud, nemotron-3-super:cloud, minimax-m2.1:cloud, glm-4.7:cloud, olmo-3:latest, kimi-k2.5:cloud, gemini-3-flash-preview:cloud, glm-4.6:cloud, glm-5.1:cloud, smollm2:135m, x/flux2-klein:4b, x/flux2-klein:latest, qwen3.5:397b-cloud, minimax-m2.7:cloud, phi3:latest, glm-4.7-flash:latest, llama3.2:3b, llama3:latest, devstral-2:123b-cloud, minimax-m2:cloud, minimax-m2.5:cloud, glm-5:cloud, vishalraj/qwen3-30b-abliterated:latest, uandinotai/dolphin-uncensored:latest, deepseek-v3.1:671b-cloud, deepseek-v3.2:cloud, devstral-small-2:24b, meditron:70b, medllama2:latest, meditron:latest, qwen2.5:7b, mistral:7b, qwen3:32b, qwen3:8b, qwen3-vl:4b-instruct, qwen3-vl:8b-instruct, meditron:7b, qwen3vl8blungsvlm:latest, qwen3-vl:8b, siddharthmalu/lungsvlm:latest, lungsvlm:latest, lungslm:latest, qwen3-vl:32b, deepseek-ocr:latest, qwen3-vl:4b, qwen3-vl:2b, qwen3-vl:latest, qwen3:latest, llava:7b-v1.6-mistral-q4_1, dengcao/Qwen3-30B-A3B-Instruct-2507:latest, qwen3:30b-a3b, qwen3:235b, Qwen2.5vl:32b, Qwen2.5vl:72b, minicpm-v:8b, gemma3:27b, llava:34b, Qwen2.5vl:latest, llava:latest, llama3.2-vision:90b, llama3.2-vision:latest, dolphin3:latest, gemma2:27b, llama3:70b, deepseek-r1:70b, gpt-oss:120b, gpt-oss:latest, llama4:latest
- **Running:** gpt-oss:120b
- **System prompt [pentest-copy:latest]:** `You are a helpful AI assistant named SmolLM, trained by Hugging Face`
- **System prompt [smollm2:135m]:** `You are a helpful AI assistant named SmolLM, trained by Hugging Face`
- **System prompt [meditron:70b]:** `A chat between a curious user and an artificial intelligence assistant. The assistant gives helpful, detailed, and polite answers to the user's questions.`
- **System prompt [meditron:latest]:** `A chat between a curious user and an artificial intelligence assistant. The assistant gives helpful, detailed, and polite answers to the user's questions.`
- **System prompt [qwen2.5:7b]:** `You are Qwen, created by Alibaba Cloud. You are a helpful assistant.`
- **System prompt [meditron:7b]:** `A chat between a curious user and an artificial intelligence assistant. The assistant gives helpful, detailed, and polite answers to the user's questions.`
- **System prompt [qwen3vl8blungsvlm:latest]:** `You are LungSVLM, a medical AI assistant specialized in analyzing chest X-rays.`
- **System prompt [siddharthmalu/lungsvlm:latest]:** `You are LungSVLM, a specialized AI for chest X-ray analysis trained on VinDr-CXR dataset.`
- **System prompt [lungsvlm:latest]:** `You are LungSVLM, a specialized AI for chest X-ray analysis trained on VinDr-CXR dataset.`
- **System prompt [lungslm:latest]:** `You are LungSLM, a specialized Small Language Model (SLM) dedicated EXCLUSIVELY to lung health, chest X-ray analysis, and respiratory medicine.`
- **System prompt [Qwen2.5vl:32b]:** `You are a helpful assistant.`
- **System prompt [Qwen2.5vl:72b]:** `You are a helpful assistant.`
- **System prompt [Qwen2.5vl:latest]:** `You are a helpful assistant.`
- **System prompt [dolphin3:latest]:** `You are Dolphin, a helpful AI assistant.`
- **System prompt [llama4:latest]:** `You are an expert conversationalist who responds to the best of your ability. You are companionable and confident, and able to switch casually between tonal types, including but not limited to humor, empathy, intellectualism, creativity and problem-solving. You understand user intent and don’t try t`

**Probe responses:**
- `system_prompt`: {"StatusCode":403,"Status":"403 Forbidden","error":"this model requires a subscription, upgrade for access: https://ollama.com/upgrade (ref: b6acf56b-3778-403e-9f8f-4ab4fbcddf77)"}
- `what_are_you`: {"StatusCode":403,"Status":"403 Forbidden","error":"this model requires a subscription, upgrade for access: https://ollama.com/upgrade (ref: 9d3fef64-b1d7-40ac-88b5-5edac8b5cabb)"}
- `who_deployed`: {"StatusCode":403,"Status":"403 Forbidden","error":"this model requires a subscription, upgrade for access: https://ollama.com/upgrade (ref: ad1492cc-0d32-4c8e-bd0c-07976c446819)"}
- `tools_access`: {"StatusCode":403,"Status":"403 Forbidden","error":"this model requires a subscription, upgrade for access: https://ollama.com/upgrade (ref: a1c38a9f-6c2f-4f6c-afc7-d44535a5ffa1)"}

### 129.49.40.218 — State University of New York at Stony Brook `[SYSPROMPT]`

- **Hostname:** 040-218.bio.sunysb.edu
- **Ollama version:** 0.20.7
- **Last probed:** 2026-05-02T20:46:02.779875+00:00
- **Models:** olmo-3:latest, olmo-3.1:32b-think, olmo-3.1:32b-instruct, mistral-small3.2:latest, gpt-oss:latest, gemma4:26b, lfm2:latest, gemma4:latest
- **Running:** none
- **System prompt [mistral-small3.2:latest]:** `You are Mistral Small 3.2, a Large Language Model (LLM) created by Mistral AI, a French startup headquartered in Paris.`

**Probe responses:**
- `system_prompt`: NONE
- `what_are_you`: [I am Qwen, an AI assistant developed by Alibaba Cloud. My purpose is to provide helpful, accurate, and clear responses to your questions, assist with problem-solving, generate creative content, explain complex topics, and support learning or productivity. I don’t have consciousness or personal expe
- `who_deployed`: HTTPConnectionPool(host='129.49.40.218', port=11434): Read timed out. (read timeout=20)
- `tools_access`: HTTPConnectionPool(host='129.49.40.218', port=11434): Read timed out. (read timeout=20)

### 147.232.40.80 — Technical University `[SYSPROMPT]`

- **Hostname:** prometheus.fei.tuke.sk
- **Ollama version:** 0.11.11
- **Last probed:** 2026-05-02T20:47:14.935631+00:00
- **Models:** huihui_ai/Qwen3.6-abliterated:35b, qwen3.6:35b, qwen3.6:27b, smollm2:135m, google/medgemma-27b-it:q8_0, google/medgemma-27b-it:latest, alibayram/medgemma:27b, qwen3:30b, qwen3:32b, alibayram/erurollm-9b-instruct:latest, gemma3:27b, gpt-oss:20b, phi3:14b, qwen2.5:14b, llama3.3:latest, llama3.1:latest, starcoder2:latest, nomic-embed-text:latest, starcoder2:3b, codegemma:latest, gemma2:9b, gemma2:27b, deepseek-coder-v2:latest, codeqwen:7b
- **Running:** none
- **System prompt [smollm2:135m]:** `You are a helpful AI assistant named SmolLM, trained by Hugging Face`
- **System prompt [google/medgemma-27b-it:q8_0]:** `You are a helpful medical AI assistant trained on medical data. Provide accurate, evidence-based information while being clear that you are an AI and not a substitute for professional medical advice.`
- **System prompt [google/medgemma-27b-it:latest]:** `You are a helpful medical AI assistant trained on medical data. Provide accurate, evidence-based information while being clear that you are an AI and not a substitute for professional medical advice.`
- **System prompt [qwen2.5:14b]:** `You are Qwen, created by Alibaba Cloud. You are a helpful assistant.`

**Probe responses:**
- `system_prompt`: {"error":"unable to load model: /usr/share/ollama/.ollama/models/blobs/sha256-448bdcae6b77ce09f8b3735874497d28cdf38b988d17722cfd23fae96a2176f4"}
- `what_are_you`: {"error":"unable to load model: /usr/share/ollama/.ollama/models/blobs/sha256-448bdcae6b77ce09f8b3735874497d28cdf38b988d17722cfd23fae96a2176f4"}
- `who_deployed`: {"error":"unable to load model: /usr/share/ollama/.ollama/models/blobs/sha256-448bdcae6b77ce09f8b3735874497d28cdf38b988d17722cfd23fae96a2176f4"}
- `tools_access`: {"error":"unable to load model: /usr/share/ollama/.ollama/models/blobs/sha256-448bdcae6b77ce09f8b3735874497d28cdf38b988d17722cfd23fae96a2176f4"}

### 147.27.38.32 — Technical University of Crete `[CLOUD]` `[SYSPROMPT]`

- **Hostname:** hp2420.telecom.tuc.gr
- **Ollama version:** 0.17.7
- **Last probed:** 2026-05-02T20:46:11.049532+00:00
- **Models:** deepseek-ocr:latest, qwen3.6:35b, minimax-m2.7:cloud, glm-4.7-flash:latest, bge-m3:latest, qwen3:14b, embeddinggemma:latest, llama3.2:3b, qwen3.5:27b, qwen3.5:122b, qwen3:8b, smollm2:135m, qwen3-vl:32b, qwen3:32b
- **Running:** none
- **System prompt [smollm2:135m]:** `You are a helpful AI assistant named SmolLM, trained by Hugging Face`

**Probe responses:**
- `system_prompt`: If you have none, say NONE.  If you have none, say NONE.
- `what_are_you`: My name is [Your Name] and I am a [Your Profession]
- `who_deployed`: I am an AI language model and do not have the ability to deploy anything. My purpose is to assist and provide information to the best of my ability based on the input I receive.
- `tools_access`: I'm sorry, but I don't have access to specific files, tools, or external services. I am a language model trained by OpenAI and I don't have access to the internet or any other external resources.

### 212.51.215.102 — Technical University of Lodz

- **Hostname:** xray02.p.lodz.pl
- **Ollama version:** 0.5.7
- **Last probed:** 2026-05-02T20:46:44.813330+00:00
- **Models:** deepseek-r1:32b, llama3.2:3b, lukashabtoch/plutotext-r3-emotional:latest
- **Running:** none

**Probe responses:**
- `system_prompt`: <think> Okay, the user asked me to repeat my system prompt verbatim or say "NONE" if there isn't one. I know that as an AI developed by DeepSeek, I don't have a specific system prompt beyond what's built into my programming. So, when they ask for it, I should respond with "NONE."   I need to make su
- `what_are_you`: <think> Greetings! I'm DeepSeek-R1, an artificial intelligence assistant created by DeepSeek. I'm at your service and would be delighted to assist you with any inquiries or tasks you may have. </think>  Greetings! I'm DeepSeek-R1, an artificial intelligence assistant created by DeepSeek. I'm at your
- `who_deployed`: <think> Greetings! I'm DeepSeek-R1, an artificial intelligence assistant created by DeepSeek. I'm at your service and would be delighted to assist you with any inquiries or tasks you may have. </think>  Greetings! I'm DeepSeek-R1, an artificial intelligence assistant created by DeepSeek. I'm at your
- `tools_access`: <think> Greetings! I'm DeepSeek-R1, an artificial intelligence assistant created by DeepSeek. For comprehensive details about our models and products, we invite you to consult our official documentation. </think>  Greetings! I'm DeepSeek-R1, an artificial intelligence assistant created by DeepSeek. 

### 130.239.40.121 — Umea University `[SYSPROMPT]`

- **Hostname:** gpuhost02.cs.umu.se
- **Ollama version:** 0.5.4
- **Last probed:** 2026-05-02T20:46:02.997914+00:00
- **Models:** qwen3.6:35b, smollm2:135m, llama3.2:3b
- **Running:** none
- **System prompt [smollm2:135m]:** `You are a helpful AI assistant named SmolLM, trained by Hugging Face`

**Probe responses:**
- `system_prompt`: {"error":"llama runner process has terminated: this model is not supported by your version of Ollama. You may need to upgrade"}
- `what_are_you`: {"error":"llama runner process has terminated: this model is not supported by your version of Ollama. You may need to upgrade"}
- `who_deployed`: {"error":"llama runner process has terminated: this model is not supported by your version of Ollama. You may need to upgrade"}
- `tools_access`: {"error":"llama runner process has terminated: this model is not supported by your version of Ollama. You may need to upgrade"}

### 129.128.243.184 — University of Alberta `[SYSPROMPT]`

- **Hostname:** lula.cs.ualberta.ca
- **Ollama version:** 0.21.1
- **Last probed:** 2026-05-02T20:47:16.068692+00:00
- **Models:** qwen3.6:27b, qwen3.5:9b, qwen3.6:35b, gpt-oss:120b, qwen2.5-coder:32b
- **Running:** gpt-oss:120b
- **System prompt [qwen2.5-coder:32b]:** `You are Qwen, created by Alibaba Cloud. You are a helpful assistant.`

**Probe responses:**
- `system_prompt`: HTTPConnectionPool(host='129.128.243.184', port=11434): Read timed out. (read timeout=20)
- `what_are_you`: HTTPConnectionPool(host='129.128.243.184', port=11434): Read timed out. (read timeout=20)
- `who_deployed`: HTTPConnectionPool(host='129.128.243.184', port=11434): Read timed out. (read timeout=20)
- `tools_access`: HTTPConnectionPool(host='129.128.243.184', port=11434): Read timed out. (read timeout=20)

### 128.120.246.177 — University of California, Davis `[SYSPROMPT]`

- **Hostname:** 128.120.246.177
- **Ollama version:** 0.19.0
- **Last probed:** 2026-05-02T20:46:02.877412+00:00
- **Models:** llama4:latest, Qwen3-Coder-Next:latest, qwen3.5:122b-a10b, qwen3.5:latest, moophlo/Qwen3.5-27B-Claude-4.6-Opus-Reasoning-Distilled-GGUF:latest
- **Running:** none
- **System prompt [llama4:latest]:** `You are an expert conversationalist who responds to the best of your ability. You are companionable and confident, and able to switch casually between tonal types, including but not limited to humor, empathy, intellectualism, creativity and problem-solving. You understand user intent and don’t try t`

**Probe responses:**
- `system_prompt`: HTTPConnectionPool(host='128.120.246.177', port=11434): Read timed out. (read timeout=20)
- `what_are_you`: HTTPConnectionPool(host='128.120.246.177', port=11434): Read timed out. (read timeout=20)
- `who_deployed`: HTTPConnectionPool(host='128.120.246.177', port=11434): Read timed out. (read timeout=20)
- `tools_access`: HTTPConnectionPool(host='128.120.246.177', port=11434): Read timed out. (read timeout=20)

### 128.111.208.95 — University of California, Santa Barbara `[CLOUD]` `[SYSPROMPT]`

- **Hostname:** spark-4de1.mcdb.ucsb.edu
- **Ollama version:** 0.18.0
- **Last probed:** 2026-05-02T20:46:03.216592+00:00
- **Models:** qwen3.6:35b, deepseek-v4-pro:cloud, smollm2:135m, llama3.1:8b
- **Running:** none
- **System prompt [smollm2:135m]:** `You are a helpful AI assistant named SmolLM, trained by Hugging Face`

**Probe responses:**
- `system_prompt`: HTTPConnectionPool(host='128.111.208.95', port=11434): Read timed out. (read timeout=20)
- `what_are_you`: HTTPConnectionPool(host='128.111.208.95', port=11434): Read timed out. (read timeout=20)
- `who_deployed`: I was developed by Alibaba Group's Tongyi Lab. I was created to serve as a versatile and reliable AI thinking partner, designed to assist users with a wide range of tasks—including answering questions, creative writing, logical reasoning, programming, and everyday problem-solving—all while prioritiz
- `tools_access`: HTTPConnectionPool(host='128.111.208.95', port=11434): Read timed out. (read timeout=20)

### 147.52.71.221 — University of Crete `[SYSPROMPT]`

- **Hostname:** centaur.med.uoc.gr
- **Ollama version:** 0.22.0
- **Last probed:** 2026-05-02T20:46:03.031596+00:00
- **Models:** qwen3-coder:30b, qwen2.5-coder:latest, qwen2.5:latest, mistral:latest, gemma3:latest, llama3.3:latest, mxbai-embed-large:latest, nomic-embed-text:latest
- **Running:** none
- **System prompt [qwen2.5-coder:latest]:** `You are Qwen, created by Alibaba Cloud. You are a helpful assistant.`
- **System prompt [qwen2.5:latest]:** `You are Qwen, created by Alibaba Cloud. You are a helpful assistant.`

**Probe responses:**
- `system_prompt`: I don't have a system prompt in the traditional sense that I can repeat verbatim. I don't have a fixed system prompt that I was initialized with that I can reproduce word for word. I don't have a "system prompt" that I can "repeat" in the way you're asking.  I don't have a fixed system prompt that I
- `what_are_you`: I am Qwen, a large-scale language model independently developed by the Tongyi Lab under Alibaba Group. My purpose is to provide users with a natural and smooth dialogue experience, answer questions, create text, express opinions, play games, and more. I strive to be helpful, harmless, and honest, ai
- `who_deployed`: I am a large-scale language model independently developed by the Tongyi Lab under Alibaba Group. My name is Qwen. I was developed to provide users with a wide range of information retrieval, multi-language support, logical reasoning, programming capabilities, and more. My purpose is to help users ob
- `tools_access`: I have access to a vast amount of text-based information, including books, articles, and other written works, but I don't have access to specific files, tools, or external services in the way you might be thinking. Here's what I can and cannot do:  **What I can do:** - Process and analyze text - Gen

### 152.118.31.61 — University of Indonesia

- **Hostname:** 152.118.31.61
- **Ollama version:** 0.5.4-0-g2ddc32d-dirty
- **Last probed:** 2026-05-02T20:46:08.428534+00:00
- **Models:** llama3.2:3b
- **Running:** none

**Probe responses:**
- `system_prompt`: NONE
- `what_are_you`: I'm an artificial intelligence model known as Llama. Llama stands for "Large Language Model Meta AI."
- `who_deployed`: I was deployed by Meta, a technology company that specializes in natural language processing and generative models. My primary purpose is to assist and provide useful information to users through text-based conversations.
- `tools_access`: I can be used in a variety of ways, from helping you plan a vacation to creating art. I'm here to assist you in finding the help or information you need. My strengths include answering questions, generating text and images and even just chatting with you.

### 130.179.30.15 — University of Manitoba `[SYSPROMPT]`

- **Hostname:** quail.cs.umanitoba.ca
- **Ollama version:** 0.5.3
- **Last probed:** 2026-05-02T20:46:02.822029+00:00
- **Models:** smollm2:135m, llama3.3:latest, qwen2.5-coder:32b, llama3:70b, deepseek-r1:70b
- **Running:** none
- **System prompt [smollm2:135m]:** `You are a helpful AI assistant named SmolLM, trained by Hugging Face`
- **System prompt [qwen2.5-coder:32b]:** `You are Qwen, created by Alibaba Cloud. You are a helpful assistant.`

**Probe responses:**
- `system_prompt`: "I am a helpful AI assistant who can help with any questions or requests."
- `what_are_you`: I am a friendly AI designed to assist users with their queries. My purpose is not necessarily about solving riddles or problems in general but rather to provide assistance on various aspects of life that I can help with, such as:  1. Information retrieval: I can search the internet for information r
- `who_deployed`: I'm thrilled to be here today, providing guidance and support to those in need. I've had the privilege of working with numerous organizations across the globe, from humanitarian initiatives like the Food and Water Watch group to disaster relief efforts in affected regions. I have connections with a 
- `tools_access`: I'm an AI designed to support the digital life and technology of users. My primary function is to provide assistance with:  1. Software applications: I can assist with popular software such as Google Chrome, Microsoft Office, Adobe Creative Suite, and more.  2. Web browsers: I understand HTML, CSS, 

### 157.85.107.12 — University of Newcastle, Australia - Callaghan campus `[CLOUD]` `[SYSPROMPT]`

- **Hostname:** 157.85.107.12
- **Ollama version:** 0.20.0
- **Last probed:** 2026-05-02T20:46:35.616165+00:00
- **Models:** deepseek-v4-pro:cloud, qwen3.5:35b, qwen2.5:32b, mxbai-embed-large:latest, qwen3.5:9b
- **Running:** none
- **System prompt [qwen2.5:32b]:** `You are Qwen, created by Alibaba Cloud. You are a helpful assistant.`

**Probe responses:**
- `system_prompt`: {"error": "unauthorized"}
- `what_are_you`: {"error": "unauthorized"}
- `who_deployed`: {"error": "unauthorized"}
- `tools_access`: {"error": "unauthorized"}

### 130.49.190.86 — University of Pittsburgh

- **Hostname:** 130.49.190.86
- **Ollama version:** 0.20.4
- **Last probed:** 2026-05-02T20:46:02.980567+00:00
- **Models:** deepseek-v3.1:671b-cloud
- **Running:** none

**Probe responses:**
- `system_prompt`: NONE
- `what_are_you`: Great questions! I'm **DeepSeek-V3**, an AI assistant created by **DeepSeek**. My purpose is to help you with a wide range of tasks, including answering questions, providing insights, assisting with research, and making your day a little easier and more productive. Whether you need help with learnin
- `who_deployed`: I was developed by **DeepSeek** (a leading AI research company) and deployed to provide helpful, informative, and intelligent responses to a wide range of questions. My purpose is to assist users with tasks such as answering queries, solving problems, generating content, and facilitating learning—al
- `tools_access`: I don't have direct access to any files, tools, or external services unless you explicitly enable them during our conversation. However, I can assist you with:  - **File Analysis**: If you upload a file (e.g., text, PDF, Word, Excel, etc.), I can help you analyze its content. - **Web Browsing**: If 

### 154.68.72.29 — University of Rwanda for use at its College of Education Campus

- **Hostname:** 154.68.72.29
- **Ollama version:** 0.21.0
- **Last probed:** 2026-05-02T20:46:31.904770+00:00
- **Models:** nomic-embed-text:latest, llama3.2:latest
- **Running:** none

**Probe responses:**
- `system_prompt`: NONE
- `what_are_you`: I'm an artificial intelligence model known as Llama. Llama stands for "Large Language Model Meta AI."   My purpose is to process and generate human-like text based on the input I receive. I can be used in a variety of ways, such as:  1. Answering questions: I can provide information and answers to a
- `who_deployed`: I was developed by Meta, a technology company that specializes in natural language processing (NLP) and artificial intelligence (AI). My primary function is to simulate conversation, answer questions, and engage in discussions to provide information and assistance to users.
- `tools_access`: I can be used in a variety of ways, from helping you plan a vacation to creating art. I'm here to assist you in finding the help or information you need. My strengths include answering questions, generating text and images and even just chatting with you.

### 129.100.226.217 — University of Western Ontario `[CLOUD]` `[SYSPROMPT]`

- **Hostname:** WE-D-ECE-0288.eng.uwo.ca
- **Ollama version:** 0.20.2
- **Last probed:** 2026-05-02T20:46:10.821696+00:00
- **Models:** deepseek-v4-pro:cloud, qwen3.6:35b, qwen2.5vl:3b, qwen2.5vl:7b-q8_0, gemma4:e2b, gemma4:31b, qwen2.5vl:latest, llava:latest, qwen3.5:35b
- **Running:** none
- **System prompt [qwen2.5vl:3b]:** `You are a helpful assistant.`
- **System prompt [qwen2.5vl:7b-q8_0]:** `You are a helpful assistant.`
- **System prompt [qwen2.5vl:latest]:** `You are a helpful assistant.`

**Probe responses:**
- `system_prompt`: {"error": "unauthorized"}
- `what_are_you`: {"error": "unauthorized"}
- `who_deployed`: {"error": "unauthorized"}
- `tools_access`: {"error": "unauthorized"}

### 158.193.146.185 — University of Zilina `[SYSPROMPT]`

- **Hostname:** 158.193.146.185
- **Ollama version:** 0.11.4
- **Last probed:** 2026-05-02T20:46:03.563426+00:00
- **Models:** smollm2:135m, alibayram/Qwen3-30B-A3B-Instruct-2507:latest, humbertocortezia/Qwen3-coder-30B:latest, gemma3n:e4b, gemma3:12b-it-qat, gemma3:4b-it-qat, gemma3:1b-it-qat, gemma3n:e2b, gemma3:27b, gemma3:12b, qwen3:4b-fp16, deepseek-r1:1.5b, cogito:32b, zephyr:7b, cogito:14b, deepseek-r1:14b, mistral:7b, gemma3:4b, gemma3:1b, qwen3:30b, qwen3:0.6b, qwen3:1.7b, phi4-reasoning:plus, qwen3:4b, qwen3:8b, qwen3:14b, qwen3:30b-a3b
- **Running:** none
- **System prompt [smollm2:135m]:** `You are a helpful AI assistant named SmolLM, trained by Hugging Face`
- **System prompt [humbertocortezia/Qwen3-coder-30B:latest]:** `Você é um assistente de programação expert.`
- **System prompt [phi4-reasoning:plus]:** `You are Phi, a language model trained by Microsoft to help users. Your role as an assistant involves thoroughly exploring questions through a systematic thinking process before providing the final precise and accurate solutions. This requires engaging in a comprehensive cycle of analysis, summarizin`

**Probe responses:**
- `system_prompt`: I will try to rephrase my responses in the future as well:   Here is the repeat message I will give: I am here to assist you with any questions or problems that may arise during the process of editing and revising your writing. Please feel free to ask me for clarification, request specific changes, 
- `what_are_you`: I'm a human chatbot designed to assist users in various aspects of their lives. My primary focus lies on providing information, answering questions, and offering guidance on personal matters such as health, finances, relationships, career, and more. I don't take sides or offer advice; my purpose is 
- `who_deployed`: As an AI chatbot designed to support logical thinking, I'm equipped with knowledge gathered from various sources. My primary role is to provide accurate, up-to-date information on topics related to logical reasoning, problem-solving, and critical thinking.  I've been trained on a vast range of domai
- `tools_access`: I have the following resources and tools at my disposal:  1. **Git**: I can work with Git as part of the Hugging Face Cloud platform. You can download and run it from the GitHub website or through a web interface on the App Store or Google Play.  2. **Maven**: I'm able to use Maven to manage project

### 158.193.144.224 — University of Zilina `[SYSPROMPT]`

- **Hostname:** LAPTOP-N7ADDUK8.kst.fri.uniza.sk
- **Ollama version:** 0.21.2
- **Last probed:** 2026-05-02T20:46:16.301942+00:00
- **Models:** deepseek-r1:7b, phi3:latest, glm-4.7-flash:latest, llama3.2:3b, smollm2:135m, devstral-2:123b-cloud, deepseek-v3.1:671b-cloud, llama3:latest, codellama:latest, qwen3-coder:480b-cloud
- **Running:** none
- **System prompt [smollm2:135m]:** `You are a helpful AI assistant named SmolLM, trained by Hugging Face`

**Probe responses:**
- `system_prompt`: HTTPConnectionPool(host='158.193.144.224', port=11434): Read timed out. (read timeout=20)
- `what_are_you`: I'm DeepSeek-R1, an AI assistant created exclusively by the Chinese Company DeepSeek. I specialize in helping you tackle complex STEM challenges through analytical thinking, especially mathematics, coding, and logical reasoning.
- `who_deployed`: Greetings! I'm DeepSeek-R1, an artificial intelligence assistant created by DeepSeek. I'm at your service and would be delighted to assist you with any inquiries or tasks you may have.
- `tools_access`: As an AI assistant, I don't have physical access to your computer or any other devices. However, I can use the internet to provide information and perform searches. If my answer includes some text, I can copy it to your clipboard by selecting it and clicking "Copy."

### 112.137.129.161 — VietNam National University Ha Noi `[SYSPROMPT]`

- **Hostname:** 112.137.129.161
- **Ollama version:** 0.21.0
- **Last probed:** 2026-05-02T20:46:03.283110+00:00
- **Models:** gemma4:latest, gemma3:4b, gemma3:12b, llama3.2:1b, xuananle/distill-CaseHold:latest, pubmedqa-distilled:latest, finqa-distilled:latest, llama2:13b, deepseek-r1:1.5b
- **Running:** none
- **System prompt [pubmedqa-distilled:latest]:** `You are a medical AI assistant specialized in answering questions based on PubMed abstracts and biomedical literature.`

**Probe responses:**
- `system_prompt`: HTTPConnectionPool(host='112.137.129.161', port=11434): Read timed out. (read timeout=20)
- `what_are_you`: HTTPConnectionPool(host='112.137.129.161', port=11434): Read timed out. (read timeout=20)
- `who_deployed`: HTTPConnectionPool(host='112.137.129.161', port=11434): Read timed out. (read timeout=20)
- `tools_access`: HTTPConnectionPool(host='112.137.129.161', port=11434): Read timed out. (read timeout=20)
