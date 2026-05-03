#!/usr/bin/env python3
"""AI Application Platform deep probe.

Detects and enumerates exposed Flowise, Dify, AnythingLLM, LangFlow, n8n,
LibreChat, LM Studio, LocalAI, RAGFlow, Open WebUI, and other AI app platforms.

Pipeline: masscan -> aiapp-probe.py -> case study

Key finding classes:
  - Stored credentials (Flowise /api/v1/credentials, n8n /api/v1/credentials)
  - Conversation history (AnythingLLM workspace chats)
  - Admin claimable (Dify setup step="not_started")
  - Workflow exfil (n8n, Flowise chatflows)
  - Model file paths (LM Studio, LocalAI)
"""

import sys, json, re, argparse, concurrent.futures
from datetime import datetime
import requests
requests.packages.urllib3.disable_warnings()

TIMEOUT = 8
HEADERS = {"User-Agent": "Mozilla/5.0"}


def parse_masscan(path):
    hits = []
    with open(path) as f:
        for line in f:
            if line.startswith("#") or not line.strip():
                continue
            m = re.search(r"Host:\s+(\S+)\s+\(\)\s+Ports:\s+(\d+)/open", line)
            if m:
                hits.append((m.group(1), int(m.group(2))))
                continue
            m = re.match(r"Host:\s+(\S+)\s+.*Ports:\s+(\d+)/open", line)
            if m:
                hits.append((m.group(1), int(m.group(2))))
    return hits


def safe_get(url, **kw):
    try:
        return requests.get(url, timeout=TIMEOUT, verify=False, headers=HEADERS, **kw)
    except Exception:
        return None


def safe_post(url, **kw):
    try:
        return requests.post(url, timeout=TIMEOUT, verify=False, headers=HEADERS, **kw)
    except Exception:
        return None


def probe_flowise(base, result):
    """Flowise — port 3000 typical. Visual LLM workflow builder.
    Critical findings: /api/v1/credentials returns stored API keys."""
    # Definitive ping
    r = safe_get(f"{base}/api/v1/ping")
    if not r or r.status_code != 200 or "pong" not in r.text.lower():
        # Try alternate detection via root HTML
        r = safe_get(base)
        if not r or "flowise" not in r.text.lower():
            return False

    result["service"] = "Flowise"
    # Auth status determined by data endpoint responses, not /ping
    result["auth"] = "unknown"

    # Version (banner)
    r = safe_get(f"{base}/api/v1/version")
    if r and r.status_code == 200:
        try:
            data = r.json()
            result["version"] = data.get("version", "?")
        except Exception:
            pass

    # Chatflows — workflow definitions, often contain prompts and model refs
    r = safe_get(f"{base}/api/v1/chatflows")
    if r:
        result["endpoints"]["/api/v1/chatflows"] = r.status_code
        if r.status_code == 200:
            try:
                arr = r.json()
                if isinstance(arr, list):
                    result["auth"] = "none"
                    result["chatflows"] = [
                        {"id": c.get("id", "?"), "name": c.get("name", "?"),
                         "deployed": c.get("deployed", False)}
                        for c in arr[:50]
                    ]
                    if arr:
                        result["findings"].append({
                            "id": "F-FLOW", "title": f"{len(arr)} chatflows enumerable",
                            "severity": "HIGH",
                            "detail": "Workflow definitions readable: prompts, model references, integrations"
                        })
            except Exception:
                pass
        elif r.status_code in (401, 403):
            result["auth"] = "required"

    # Credentials — CRITICAL — stored API keys
    r = safe_get(f"{base}/api/v1/credentials")
    if r and r.status_code == 200:
        try:
            arr = r.json()
            if isinstance(arr, list):
                cred_summary = []
                for c in arr[:50]:
                    cred_summary.append({
                        "name": c.get("name", "?"),
                        "type": c.get("credentialName", "?"),
                        "id": c.get("id", "?")
                    })
                result["credentials"] = cred_summary
                result["endpoints"]["/api/v1/credentials"] = 200
                result["findings"].append({
                    "id": "F-CRED", "title": f"Stored credentials enumerable — {len(arr)} entries",
                    "severity": "CRITICAL",
                    "detail": "OpenAI/Anthropic/etc API keys may be retrievable. CVE-2024-36420 path traversal grants plaintext access on <1.8.2"
                })
        except Exception:
            pass

    # API keys
    r = safe_get(f"{base}/api/v1/apikey")
    if r and r.status_code == 200:
        try:
            arr = r.json()
            if isinstance(arr, list) and arr:
                result["api_keys_count"] = len(arr)
                result["findings"].append({
                    "id": "F-APIKEY", "title": f"{len(arr)} Flowise API keys enumerable",
                    "severity": "HIGH",
                    "detail": "Self-hosted API keys for chatflow invocation accessible"
                })
        except Exception:
            pass

    # Variables — environment variables stored in app
    r = safe_get(f"{base}/api/v1/variables")
    if r and r.status_code == 200:
        try:
            arr = r.json()
            if isinstance(arr, list) and arr:
                result["variables"] = [v.get("name", "?") for v in arr[:30]]
                result["findings"].append({
                    "id": "F-VAR", "title": f"{len(arr)} stored variables enumerable",
                    "severity": "MEDIUM",
                    "detail": "Application-level variables (may include secrets)"
                })
        except Exception:
            pass

    return True


def probe_dify(base, result):
    """Dify — port 80, 3000, 5001. AI app platform.
    Critical: /console/api/setup returning step='not_started' = admin claimable."""
    # Setup state probe
    r = safe_get(f"{base}/console/api/setup")
    if not r or r.status_code not in (200, 401):
        # Try root
        r = safe_get(base)
        if not r or "dify" not in r.text.lower():
            return False
    elif r.status_code == 200:
        try:
            data = r.json()
            step = data.get("step", "?")
            result["service"] = "Dify"
            result["dify_setup_step"] = step
            result["endpoints"]["/console/api/setup"] = 200

            if step == "not_started":
                result["auth"] = "none"
                result["findings"].append({
                    "id": "F-CLAIM", "title": "Dify admin claimable — setup not started",
                    "severity": "CRITICAL",
                    "detail": "First visitor to /install becomes admin. Claim by attacker = full app control."
                })
            elif step == "finished":
                result["auth"] = "configured"
        except Exception:
            pass

    # Detect via root if not yet
    if not result.get("service"):
        r = safe_get(base)
        if r and ("dify" in r.text.lower() or "<title>Dify</title>" in r.text):
            result["service"] = "Dify"
            result["auth"] = result.get("auth") or "unknown"
        else:
            return False

    # Version + system info
    r = safe_get(f"{base}/console/api/system-features")
    if r and r.status_code == 200:
        try:
            result["dify_features"] = r.json()
        except Exception:
            pass

    return True


def probe_anythingllm(base, result):
    """AnythingLLM — port 3001 typical. Personal/team LLM workspace.
    Findings: conversation history, vector DB references, system config."""
    r = safe_get(f"{base}/api/auth")
    if not r or r.status_code != 200:
        r = safe_get(base)
        if not r or "anythingllm" not in r.text.lower():
            return False
    else:
        try:
            data = r.json()
            if "authenticated" not in str(data).lower() and "multiUser" not in str(data):
                # Not AnythingLLM
                pass
            result["service"] = "AnythingLLM"
            result["anythingllm_auth_response"] = data
            result["endpoints"]["/api/auth"] = 200

            authenticated = data.get("authenticated", False)
            multi_user = data.get("multiUserMode", False)
            if not authenticated and not multi_user:
                result["auth"] = "none"
            elif multi_user:
                result["auth"] = "multi-user"
            else:
                result["auth"] = "single-user"
        except Exception:
            pass

    if not result.get("service"):
        return False

    # System info
    r = safe_get(f"{base}/api/v1/system")
    if r and r.status_code == 200:
        try:
            data = r.json()
            result["anythingllm_system"] = {
                "LLMProvider": data.get("LLMProvider"),
                "EmbeddingEngine": data.get("EmbeddingEngine"),
                "VectorDB": data.get("VectorDB"),
            }
            result["findings"].append({
                "id": "F-SYS", "title": "System config exposed",
                "severity": "MEDIUM",
                "detail": f"LLM={data.get('LLMProvider')}, Vector={data.get('VectorDB')}, Embed={data.get('EmbeddingEngine')}"
            })
        except Exception:
            pass

    # Workspaces — conversation containers
    r = safe_get(f"{base}/api/v1/workspaces")
    if r and r.status_code == 200:
        try:
            data = r.json()
            workspaces = data.get("workspaces", [])
            result["anythingllm_workspaces"] = [
                {"slug": w.get("slug"), "name": w.get("name"), "id": w.get("id")}
                for w in workspaces[:20]
            ]
            if workspaces:
                result["findings"].append({
                    "id": "F-WS", "title": f"{len(workspaces)} workspaces enumerable",
                    "severity": "HIGH",
                    "detail": "Workspace contents (RAG corpus, conversation history) potentially accessible"
                })

                # Try first workspace chat history
                first = workspaces[0].get("slug")
                if first:
                    r2 = safe_get(f"{base}/api/v1/workspace/{first}/chats")
                    if r2 and r2.status_code == 200:
                        try:
                            chats = r2.json().get("history", [])
                            if chats:
                                result["findings"].append({
                                    "id": "F-CHAT", "title": f"Conversation history accessible ({len(chats)} msgs in '{first}')",
                                    "severity": "CRITICAL",
                                    "detail": "User conversations readable without auth — privacy violation"
                                })
                        except Exception:
                            pass
        except Exception:
            pass

    return True


def probe_langflow(base, result):
    """LangFlow — port 7860 or 3000. LangChain visual builder."""
    r = safe_get(f"{base}/api/v1/flows/")
    if not r or r.status_code not in (200, 401, 403):
        # Try docs
        r = safe_get(f"{base}/docs")
        if not r or ("langflow" not in r.text.lower() and r.status_code != 200):
            return False

    if r and r.status_code == 200:
        try:
            data = r.json()
            if isinstance(data, list):
                result["service"] = "LangFlow"
                result["auth"] = "none"
                result["langflow_flows"] = [
                    {"id": f.get("id"), "name": f.get("name")}
                    for f in data[:30]
                ]
                result["endpoints"]["/api/v1/flows/"] = 200
                result["findings"].append({
                    "id": "F-LFLOW", "title": f"{len(data)} LangFlow flows enumerable",
                    "severity": "HIGH",
                    "detail": "Flow definitions readable — prompt configs, API references"
                })
        except Exception:
            pass

    if r and r.status_code in (401, 403):
        result["service"] = "LangFlow"
        result["auth"] = "required"

    if not result.get("service"):
        return False

    # API keys
    r = safe_get(f"{base}/api/v1/api_key/")
    if r and r.status_code == 200:
        try:
            data = r.json()
            keys = data.get("api_keys", []) if isinstance(data, dict) else data
            if keys:
                result["findings"].append({
                    "id": "F-LFKEY", "title": f"{len(keys)} LangFlow API keys enumerable",
                    "severity": "HIGH",
                    "detail": "Self-hosted API keys accessible"
                })
        except Exception:
            pass

    return True


def probe_n8n(base, result):
    """n8n — port 5678. Workflow automation, stores credentials for 200+ services."""
    r = safe_get(f"{base}/healthz")
    if not r or r.status_code != 200:
        r = safe_get(base)
        if not r or "n8n" not in r.text.lower():
            return False
    else:
        try:
            data = r.json()
            if data.get("status") != "ok":
                pass
        except Exception:
            return False

    result["service"] = "n8n"
    result["endpoints"]["/healthz"] = 200
    result["auth"] = "unknown"

    # Workflows
    r = safe_get(f"{base}/api/v1/workflows")
    if r:
        result["endpoints"]["/api/v1/workflows"] = r.status_code
        if r.status_code == 200:
            try:
                data = r.json()
                workflows = data.get("data", []) if isinstance(data, dict) else data
                if isinstance(workflows, list) and workflows:
                    result["auth"] = "none"
                    result["n8n_workflows_count"] = len(workflows)
                    result["findings"].append({
                        "id": "F-N8N-WF", "title": f"{len(workflows)} n8n workflows enumerable",
                        "severity": "HIGH",
                        "detail": "Workflow definitions readable — automation logic, integrations"
                    })
            except Exception:
                pass
        elif r.status_code in (401, 403):
            result["auth"] = "api-key-required"

    # Credentials
    r = safe_get(f"{base}/api/v1/credentials")
    if r and r.status_code == 200:
        try:
            data = r.json()
            creds = data.get("data", []) if isinstance(data, dict) else data
            if isinstance(creds, list) and creds:
                result["findings"].append({
                    "id": "F-N8N-CRED", "title": f"{len(creds)} n8n credentials enumerable",
                    "severity": "CRITICAL",
                    "detail": "n8n stores credentials for OAuth, API keys for 200+ services. Names/types accessible without auth."
                })
        except Exception:
            pass

    return True


def probe_librechat(base, result):
    """LibreChat — port 3080. Multi-LLM chat interface."""
    r = safe_get(f"{base}/api/config")
    if not r or r.status_code != 200:
        return False
    try:
        data = r.json()
        # LibreChat config has appTitle and endpoints
        if "appTitle" in data or "endpoints" in data:
            result["service"] = "LibreChat"
            result["auth"] = "none"  # /api/config is public by design
            result["librechat_config"] = {
                "appTitle": data.get("appTitle"),
                "endpoints": list((data.get("endpoints") or {}).keys()),
                "registrationEnabled": data.get("registrationEnabled"),
            }
            if data.get("registrationEnabled"):
                result["findings"].append({
                    "id": "F-LC-REG", "title": "LibreChat registration enabled",
                    "severity": "MEDIUM",
                    "detail": "Open user registration — anyone can create an account and consume LLM tokens"
                })
            return True
    except Exception:
        pass
    return False


def probe_lmstudio(base, result):
    """LM Studio — port 1234. Personal LLM serving.
    Definitive signature: /api/v0/models (LM Studio-specific extended endpoint)."""
    # Definitive — /api/v0/models is unique to LM Studio
    r2 = safe_get(f"{base}/api/v0/models")
    is_lmstudio = False
    if r2 and r2.status_code == 200:
        try:
            ext = r2.json().get("data", [])
            if ext and any("type" in m for m in ext):  # type field is LMS-specific
                is_lmstudio = True
                result["lmstudio_extended"] = [
                    {"id": m.get("id"), "type": m.get("type"),
                     "publisher": m.get("publisher"), "arch": m.get("arch"),
                     "loaded_context_length": m.get("loaded_context_length")}
                    for m in ext[:20]
                ]
        except Exception:
            pass

    if not is_lmstudio:
        return False

    # Confirmed LM Studio — pull standard model list
    r = safe_get(f"{base}/v1/models")
    if not r or r.status_code != 200:
        return False
    try:
        data = r.json()
        models = data.get("data", [])
        if not isinstance(models, list):
            return False

        result["service"] = "LM Studio"
        result["auth"] = "none"
        result["models"] = [m.get("id", "?") for m in models]
        result["endpoints"]["/v1/models"] = 200
        result["findings"].append({
            "id": "F-LMS", "title": f"LM Studio exposed — {len(models)} models",
            "severity": "HIGH",
            "detail": f"Models: {', '.join(result['models'][:5])}. Personal compute likely on residential ISP."
        })
        return True
    except Exception:
        return False


def probe_localai(base, result):
    """LocalAI — port 8080. Multi-model OpenAI-compat server with model download API."""
    r = safe_get(f"{base}/v1/models")
    if not r or r.status_code != 200:
        return False
    try:
        data = r.json()
        # LocalAI returns object=list with data array
        models = data.get("data", [])
        if not isinstance(models, list):
            return False

        # LocalAI signature: /readyz returns "OK", /metrics has localai_ prefix
        r2 = safe_get(f"{base}/readyz")
        is_localai = False
        if r2 and r2.status_code == 200 and "ok" in r2.text.lower():
            is_localai = True

        r3 = safe_get(f"{base}/metrics")
        if r3 and r3.status_code == 200 and "localai" in r3.text.lower():
            is_localai = True

        if not is_localai:
            return False

        result["service"] = "LocalAI"
        result["auth"] = "none"
        result["models"] = [m.get("id", "?") for m in models]
        result["endpoints"]["/v1/models"] = 200
        result["findings"].append({
            "id": "F-LAI", "title": f"LocalAI exposed — {len(models)} models",
            "severity": "HIGH",
            "detail": f"Models: {', '.join(result['models'][:5])}"
        })

        # Model gallery endpoint — can trigger model downloads (DoS / disk fill)
        r4 = safe_get(f"{base}/models/available")
        if r4 and r4.status_code == 200:
            result["findings"].append({
                "id": "F-LAI-GAL", "title": "LocalAI model gallery exposed",
                "severity": "HIGH",
                "detail": "POST /models/apply allows attacker-controlled model downloads (disk exhaustion / SSRF)"
            })
        return True
    except Exception:
        return False


def probe_openwebui(base, result):
    """Open WebUI — port 3000 typical. Web UI for Ollama/OpenAI."""
    r = safe_get(f"{base}/api/config")
    if not r or r.status_code != 200:
        r = safe_get(base)
        if not r or "open-webui" not in r.text.lower() and "open webui" not in r.text.lower():
            return False
    else:
        try:
            data = r.json()
            if "name" in data and ("Open WebUI" in str(data) or "open-webui" in str(data).lower()):
                result["service"] = "Open WebUI"
                result["openwebui_config"] = {
                    "name": data.get("name"),
                    "version": data.get("version"),
                    "default_locale": data.get("default_locale"),
                    "features": data.get("features"),
                }
                result["version"] = data.get("version", "?")
                features = data.get("features", {})
                if features.get("auth") is False:
                    result["auth"] = "none"
                    result["findings"].append({
                        "id": "F-OWUI-AUTH", "title": "Open WebUI auth disabled",
                        "severity": "CRITICAL",
                        "detail": "WEBUI_AUTH=False — anyone can use chats and models without account"
                    })
                elif features.get("enable_signup"):
                    result["auth"] = "open-signup"
                    result["findings"].append({
                        "id": "F-OWUI-SIG", "title": "Open WebUI signup enabled",
                        "severity": "MEDIUM",
                        "detail": "ENABLE_SIGNUP=True — anyone can register and consume LLM resources"
                    })
                else:
                    result["auth"] = "configured"
                return True
        except Exception:
            pass
    return False


def probe_ragflow(base, result):
    """RAGFlow — typically port 80/8080. Document Q&A platform."""
    r = safe_get(f"{base}/v1/user/info")
    if not r:
        return False
    if r.status_code == 200:
        try:
            data = r.json()
            if "data" in data or "code" in data:
                result["service"] = "RAGFlow"
                result["auth"] = "session-based"
                result["endpoints"]["/v1/user/info"] = 200
                # 401 means it exists but needs login
        except Exception:
            return False
    elif r.status_code == 401:
        # 401 also indicates RAGFlow exists
        try:
            j = r.json()
            if "code" in j and "message" in j:
                result["service"] = "RAGFlow"
                result["auth"] = "required"
                result["endpoints"]["/v1/user/info"] = 401
        except Exception:
            return False
    else:
        return False
    return True


def probe_jupyter(base, result):
    """Jupyter — port 8888. RCE if no token required."""
    r = safe_get(f"{base}/api/kernels")
    if not r:
        return False
    if r.status_code == 200:
        try:
            arr = r.json()
            if isinstance(arr, list):
                result["service"] = "Jupyter"
                result["auth"] = "none"
                result["jupyter_kernels"] = len(arr)
                result["findings"].append({
                    "id": "F-JUP-RCE", "title": "Jupyter unauthenticated — code execution",
                    "severity": "CRITICAL",
                    "detail": f"{len(arr)} active kernel(s). No token. Anyone gets a shell."
                })
                return True
        except Exception:
            pass
    elif r.status_code in (401, 403):
        result["service"] = "Jupyter"
        result["auth"] = "token-required"
        return True
    return False


def probe_litellm(base, result):
    """LiteLLM Proxy — port 4000. AI gateway storing all provider API keys.
    Critical: /key/list returns every key managed by the proxy."""
    r = safe_get(f"{base}/health")
    if not r:
        r = safe_get(f"{base}/health/liveliness")
    if not r or r.status_code != 200:
        return False
    try:
        data = r.json()
        if "status" not in data and "healthy_endpoints" not in data and "litellm" not in str(data).lower():
            return False
    except Exception:
        return False

    result["service"] = "LiteLLM"
    result["auth"] = "unknown"
    result["endpoints"]["/health"] = 200

    # Model list
    r = safe_get(f"{base}/v1/models")
    if r and r.status_code == 200:
        try:
            models = r.json().get("data", [])
            result["litellm_models"] = [m.get("id") for m in models[:30]]
            result["auth"] = "none"
            result["findings"].append({
                "id": "F-LLM-MOD", "title": f"LiteLLM {len(models)} models enumerable",
                "severity": "MEDIUM",
                "detail": f"Models: {', '.join(result['litellm_models'][:5])}"
            })
        except Exception:
            pass
    elif r and r.status_code in (401, 403):
        result["auth"] = "required"

    # Key list — CRITICAL — returns all API keys managed by this proxy
    r = safe_get(f"{base}/key/list")
    if r and r.status_code == 200:
        try:
            data = r.json()
            keys = data.get("keys", data) if isinstance(data, dict) else data
            if isinstance(keys, list):
                result["litellm_keys_count"] = len(keys)
                result["auth"] = "none"
                result["findings"].append({
                    "id": "F-LLM-KEYS", "title": f"LiteLLM /key/list exposed — {len(keys)} keys",
                    "severity": "CRITICAL",
                    "detail": "All provider API keys (OpenAI, Anthropic, etc.) managed by this proxy are enumerable"
                })
        except Exception:
            pass

    # Spend logs — usage data per key
    r = safe_get(f"{base}/spend/logs")
    if r and r.status_code == 200:
        result["findings"].append({
            "id": "F-LLM-SPEND", "title": "LiteLLM spend logs exposed",
            "severity": "HIGH",
            "detail": "Per-key spending logs readable — reveals usage patterns and key identifiers"
        })

    # Config — may contain raw API keys
    r = safe_get(f"{base}/config/yaml")
    if r and r.status_code == 200 and len(r.text) > 10:
        result["findings"].append({
            "id": "F-LLM-CFG", "title": "LiteLLM config.yaml exposed",
            "severity": "CRITICAL",
            "detail": "Full proxy config readable — may contain plaintext provider API keys"
        })

    return True


def probe_automatic1111(base, result):
    """AUTOMATIC1111 / Forge / ComfyUI — ports 7860 (A1111) and 8188 (ComfyUI).
    No auth by default. Compute abuse + model path disclosure."""
    # ComfyUI detection (port 8188 typically, but check here too)
    r = safe_get(f"{base}/system_stats")
    if r and r.status_code == 200:
        try:
            data = r.json()
            if "system" in data or "devices" in data:
                result["service"] = "ComfyUI"
                result["auth"] = "none"
                result["endpoints"]["/system_stats"] = 200
                devs = data.get("devices", [])
                result["comfyui_devices"] = devs
                if devs:
                    vram = devs[0].get("vram_total", 0)
                    result["findings"].append({
                        "id": "F-COMFY", "title": f"ComfyUI unauthenticated — {vram/1e9:.1f}GB VRAM",
                        "severity": "HIGH",
                        "detail": "Unauthenticated image generation. /prompt endpoint submits jobs."
                    })

                # Generation history — may contain sensitive prompts
                r2 = safe_get(f"{base}/history")
                if r2 and r2.status_code == 200:
                    try:
                        hist = r2.json()
                        if hist:
                            result["findings"].append({
                                "id": "F-COMFY-HIST", "title": f"ComfyUI generation history exposed ({len(hist)} entries)",
                                "severity": "MEDIUM",
                                "detail": "Past prompts and generated image paths readable"
                            })
                    except Exception:
                        pass
                return True
        except Exception:
            pass

    # AUTOMATIC1111 / Forge detection
    r = safe_get(f"{base}/sdapi/v1/options")
    if r and r.status_code == 200:
        try:
            data = r.json()
            if "sd_model_checkpoint" in data or "samples_dir" in data:
                result["service"] = "AUTOMATIC1111"
                result["auth"] = "none"
                result["endpoints"]["/sdapi/v1/options"] = 200
                result["a1111_model"] = data.get("sd_model_checkpoint", "?")
                result["a1111_samples_dir"] = data.get("samples_dir", "?")
                result["findings"].append({
                    "id": "F-A1111", "title": f"AUTOMATIC1111 unauthenticated — model={result['a1111_model']}",
                    "severity": "HIGH",
                    "detail": f"Full SD options exposed. Compute abuse via /sdapi/v1/txt2img. samples_dir={result['a1111_samples_dir']}"
                })

                # Model list
                r2 = safe_get(f"{base}/sdapi/v1/sd-models")
                if r2 and r2.status_code == 200:
                    models = r2.json()
                    if isinstance(models, list):
                        result["a1111_models"] = [m.get("model_name") for m in models[:20]]
                return True
        except Exception:
            pass

    # Gradio generic detection
    r = safe_get(base)
    if r and r.status_code == 200 and "gradio" in r.text.lower():
        result["service"] = "Gradio-app"
        result["auth"] = "none"
        result["findings"].append({
            "id": "F-GRADIO", "title": "Gradio application exposed",
            "severity": "MEDIUM",
            "detail": "Unidentified Gradio app — may be text-generation-webui, LangFlow, or custom ML demo"
        })
        return True

    return False


def probe_airflow(base, result):
    """Apache Airflow — port 8080. Unauth = full DAG/pipeline view + stored secrets.
    /api/v1/connections exposes database credentials, API keys, SSH keys."""
    # Health check — definitive Airflow signature
    r = safe_get(f"{base}/health")
    if r and r.status_code == 200:
        try:
            data = r.json()
            if "metadatabase" in data or "scheduler" in data:
                result["service"] = "Apache Airflow"
                result["endpoints"]["/health"] = 200
                result["airflow_health"] = data
            else:
                pass
        except Exception:
            pass

    if not result.get("service"):
        # Try root redirect
        r = safe_get(base)
        if r and ("airflow" in r.text.lower() or "airflow" in r.headers.get("server", "").lower()):
            result["service"] = "Apache Airflow"
        else:
            return False

    result["auth"] = "unknown"

    # DAG list — if 200, fully unauth
    r = safe_get(f"{base}/api/v1/dags")
    if r:
        result["endpoints"]["/api/v1/dags"] = r.status_code
        if r.status_code == 200:
            try:
                data = r.json()
                dags = data.get("dags", [])
                result["auth"] = "none"
                result["airflow_dags"] = [
                    {"dag_id": d.get("dag_id"), "is_active": d.get("is_active"),
                     "file_token": d.get("file_token")}
                    for d in dags[:30]
                ]
                result["findings"].append({
                    "id": "F-AF-DAGS", "title": f"Airflow {len(dags)} DAGs enumerable",
                    "severity": "HIGH",
                    "detail": "Full pipeline definitions readable without authentication"
                })
            except Exception:
                pass
        elif r.status_code in (401, 403):
            result["auth"] = "required"

    if result["auth"] != "none":
        return True

    # Variables — stored secrets
    r = safe_get(f"{base}/api/v1/variables")
    if r and r.status_code == 200:
        try:
            data = r.json()
            variables = data.get("variables", [])
            result["airflow_variables"] = [v.get("key") for v in variables[:50]]
            if variables:
                result["findings"].append({
                    "id": "F-AF-VARS", "title": f"Airflow variables exposed ({len(variables)} entries)",
                    "severity": "CRITICAL",
                    "detail": "Stored variables (often API keys, secrets) enumerable. Values may be in plaintext."
                })
        except Exception:
            pass

    # Connections — DB credentials, API keys, SSH keys
    r = safe_get(f"{base}/api/v1/connections")
    if r and r.status_code == 200:
        try:
            data = r.json()
            conns = data.get("connections", [])
            result["airflow_connections"] = [
                {"conn_id": c.get("connection_id"), "conn_type": c.get("conn_type"),
                 "host": c.get("host")}
                for c in conns[:30]
            ]
            if conns:
                result["findings"].append({
                    "id": "F-AF-CONN", "title": f"Airflow connections exposed ({len(conns)} entries)",
                    "severity": "CRITICAL",
                    "detail": "Database credentials, API connections, SSH keys enumerable via /api/v1/connections"
                })
        except Exception:
            pass

    return True


def probe_qdrant(base, result):
    """Qdrant — port 6333. Vector DB; unauth = full corpus queryable."""
    r = safe_get(f"{base}/collections")
    if not r:
        return False

    if r.status_code == 200:
        try:
            data = r.json()
            colls = data.get("result", {}).get("collections", [])
            result["service"] = "Qdrant"
            result["auth"] = "none"
            result["endpoints"]["/collections"] = 200
            result["qdrant_collections"] = [c.get("name") for c in colls]

            if colls:
                result["findings"].append({
                    "id": "F-QD-COLLS", "title": f"Qdrant {len(colls)} collections enumerable",
                    "severity": "HIGH",
                    "detail": f"Collections: {', '.join(result['qdrant_collections'][:5])}. Full vector corpus queryable."
                })

                # Try to scroll points from first collection — proves data exfil
                first = colls[0].get("name")
                if first:
                    r2 = safe_post(f"{base}/collections/{first}/points/scroll",
                                   json={"limit": 3, "with_payload": True})
                    if r2 and r2.status_code == 200:
                        pts = r2.json().get("result", {}).get("points", [])
                        if pts:
                            result["findings"].append({
                                "id": "F-QD-DATA", "title": f"Qdrant data exfil confirmed — {first}",
                                "severity": "CRITICAL",
                                "detail": f"Scrolled {len(pts)} points from '{first}' without auth. Document payloads accessible."
                            })
        except Exception:
            pass
        return True

    # Version/root check
    r = safe_get(base)
    if r and r.status_code == 200:
        try:
            data = r.json()
            if "title" in data and "qdrant" in data.get("title", "").lower():
                result["service"] = "Qdrant"
                result["version"] = data.get("version", "?")
                result["auth"] = "api-key-required"
                return True
        except Exception:
            pass
    return False


def probe_chromadb(base, result):
    """ChromaDB — port 8000. Vector DB; no auth by default."""
    # v1 API
    r = safe_get(f"{base}/api/v1/collections")
    if not r:
        # Try v2
        r = safe_get(f"{base}/api/v2/collections")
    if not r:
        return False

    if r.status_code == 200:
        try:
            colls = r.json()
            if not isinstance(colls, list):
                return False
            result["service"] = "ChromaDB"
            result["auth"] = "none"
            result["endpoints"]["/api/v1/collections"] = 200
            result["chroma_collections"] = [c.get("name") for c in colls[:30]]

            if colls:
                result["findings"].append({
                    "id": "F-CH-COLLS", "title": f"ChromaDB {len(colls)} collections enumerable",
                    "severity": "HIGH",
                    "detail": f"Collections: {', '.join(result['chroma_collections'][:5])}"
                })

                # Count + sample from first collection
                first = colls[0].get("name") or colls[0].get("id")
                if first:
                    r2 = safe_get(f"{base}/api/v1/collections/{first}/count")
                    if r2 and r2.status_code == 200:
                        count = r2.json()
                        result["findings"].append({
                            "id": "F-CH-DATA", "title": f"ChromaDB '{first}' — {count} documents",
                            "severity": "CRITICAL",
                            "detail": "Documents in vector store queryable without authentication"
                        })
        except Exception:
            return False
        return True

    # Heartbeat check
    r = safe_get(f"{base}/api/v1")
    if r and r.status_code == 200:
        try:
            data = r.json()
            if "nanosecond heartbeat" in data or "version" in data:
                result["service"] = "ChromaDB"
                result["auth"] = "none"
                result["version"] = data.get("version", "?")
                return True
        except Exception:
            pass
    return False


def probe_elasticsearch(base, result):
    """Elasticsearch / OpenSearch — port 9200. Unauth = all indices + data readable."""
    r = safe_get(base)
    if not r or r.status_code != 200:
        return False
    try:
        data = r.json()
        # Both ES and OpenSearch return cluster_name + version at root
        if "cluster_name" not in data and "version" not in data:
            return False
        dist = data.get("version", {}).get("distribution", "")
        name = "OpenSearch" if dist == "opensearch" or "opensearch" in str(data).lower() else "Elasticsearch"
        result["service"] = name
        result["version"] = data.get("version", {}).get("number", "?")
        result["es_cluster"] = data.get("cluster_name", "?")
        result["endpoints"]["/"] = 200
        result["auth"] = "none"
    except Exception:
        return False

    # Index inventory
    r = safe_get(f"{base}/_cat/indices?v&h=index,docs.count,store.size,health")
    if r and r.status_code == 200 and r.text.strip():
        lines = [l for l in r.text.strip().split("\n") if not l.startswith("index")]
        result["es_indices_count"] = len(lines)
        result["es_indices_sample"] = lines[:10]
        if lines:
            result["findings"].append({
                "id": "F-ES-IDX", "title": f"{name} {len(lines)} indices enumerable",
                "severity": "HIGH",
                "detail": f"Sample: {lines[0].split()[0] if lines else '?'}. All index names, doc counts, sizes readable."
            })
    elif r and r.status_code in (401, 403):
        result["auth"] = "required"
        return True

    # Check for ML indices (vector search) — higher severity
    if result.get("es_indices_sample"):
        ml_indices = [l for l in result["es_indices_sample"] if any(
            k in l for k in [".ml-", "embedding", "vector", "semantic", "elser", "knn", ".inference"]
        )]
        if ml_indices:
            result["findings"].append({
                "id": "F-ES-ML", "title": f"{name} ML/vector indices present ({len(ml_indices)})",
                "severity": "CRITICAL",
                "detail": f"ML pipeline indices found: {ml_indices[:3]}. Embedded document corpus may be readable."
            })

    # Sample a doc from first non-system index
    if result.get("es_indices_sample"):
        for line in result["es_indices_sample"]:
            idx = line.split()[0] if line.split() else ""
            if idx and not idx.startswith("."):
                r2 = safe_get(f"{base}/{idx}/_search?size=1")
                if r2 and r2.status_code == 200:
                    try:
                        hits = r2.json().get("hits", {}).get("hits", [])
                        if hits:
                            result["findings"].append({
                                "id": "F-ES-DATA", "title": f"{name} data exfil confirmed — index '{idx}'",
                                "severity": "CRITICAL",
                                "detail": "Documents retrievable without authentication"
                            })
                    except Exception:
                        pass
                break

    return True


# Per-port probe dispatch — only try probes whose typical port matches the hit
PORT_PROBES = {
    3000: ["probe_flowise", "probe_dify", "probe_openwebui", "probe_langflow"],
    3001: ["probe_anythingllm"],
    3080: ["probe_librechat"],
    4000: ["probe_litellm"],
    5678: ["probe_n8n"],
    6333: ["probe_qdrant"],
    7860: ["probe_automatic1111", "probe_langflow"],
    8000: ["probe_chromadb", "probe_localai", "probe_ragflow"],
    8080: ["probe_airflow", "probe_localai", "probe_ragflow", "probe_openwebui"],
    8188: ["probe_automatic1111"],
    8888: ["probe_jupyter"],
    9200: ["probe_elasticsearch"],
    1234: ["probe_lmstudio"],
    5001: ["probe_dify"],
}

ALL_PROBES = [
    probe_flowise, probe_dify, probe_anythingllm, probe_langflow,
    probe_n8n, probe_librechat, probe_lmstudio, probe_localai,
    probe_openwebui, probe_ragflow, probe_jupyter,
    probe_litellm, probe_automatic1111, probe_airflow,
    probe_qdrant, probe_chromadb, probe_elasticsearch,
]
PROBE_FNS = {fn.__name__: fn for fn in ALL_PROBES}


def probe(ip, port):
    base = f"http://{ip}:{port}"
    result = {
        "ip": ip, "port": port, "base_url": base,
        "service": None, "version": None, "auth": None,
        "endpoints": {}, "findings": [],
        "probed_at": datetime.utcnow().isoformat(),
    }

    if port in PORT_PROBES:
        for fn_name in PORT_PROBES[port]:
            try:
                if PROBE_FNS[fn_name](base, result):
                    return result
            except Exception:
                continue
    else:
        for fn in ALL_PROBES:
            try:
                if fn(base, result):
                    return result
            except Exception:
                continue
    return None


def main():
    p = argparse.ArgumentParser()
    p.add_argument("scan_files", nargs="+")
    p.add_argument("--workers", type=int, default=30)
    p.add_argument("--out", default="/tmp/aiapp-findings.json")
    p.add_argument("--filter-private", action="store_true", default=True)
    args = p.parse_args()

    private_prefixes = ("10.", "172.16.", "172.17.", "172.18.", "172.19.",
                        "172.20.", "172.21.", "172.22.", "172.23.", "172.24.",
                        "172.25.", "172.26.", "172.27.", "172.28.", "172.29.",
                        "172.30.", "172.31.", "192.168.", "127.")

    all_hits = []
    for f in args.scan_files:
        try:
            all_hits.extend(parse_masscan(f))
        except FileNotFoundError:
            print(f"[!] {f} not found", file=sys.stderr)

    seen = set()
    filtered = []
    for ip, port in all_hits:
        if args.filter_private and any(ip.startswith(p) for p in private_prefixes):
            continue
        key = (ip, port)
        if key not in seen:
            seen.add(key)
            filtered.append((ip, port))

    print(f"[*] {len(all_hits)} raw -> {len(filtered)} dedup", file=sys.stderr)
    if not filtered:
        sys.exit(0)

    results = []
    confirmed = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as ex:
        futs = {ex.submit(probe, ip, port): (ip, port) for ip, port in filtered}
        for i, fut in enumerate(concurrent.futures.as_completed(futs), 1):
            ip, port = futs[fut]
            try:
                r = fut.result()
                if r:
                    confirmed += 1
                    sev = max((f["severity"] for f in r["findings"]),
                              key=lambda s: {"CRITICAL":4,"HIGH":3,"MEDIUM":2,"LOW":1,"INFO":0}.get(s,0),
                              default="-")
                    print(f"[+] {ip}:{port} {r['service']} auth={r['auth']} {sev}",
                          file=sys.stderr)
                    results.append(r)
            except Exception as e:
                print(f"[-] {ip}:{port} {e}", file=sys.stderr)
            if i % 100 == 0:
                print(f"[.] {i}/{len(filtered)} probed, {confirmed} confirmed",
                      file=sys.stderr)

    with open(args.out, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\n[*] {confirmed} services confirmed -> {args.out}", file=sys.stderr)
    # By-service summary
    by_svc = {}
    for r in results:
        by_svc.setdefault(r["service"], 0)
        by_svc[r["service"]] += 1
    for svc, n in sorted(by_svc.items(), key=lambda x: -x[1]):
        print(f"    {svc}: {n}", file=sys.stderr)


if __name__ == "__main__":
    main()
