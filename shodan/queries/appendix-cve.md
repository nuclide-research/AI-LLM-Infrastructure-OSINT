# Appendix A: High-Severity CVE Cross-Reference

_New in v2 · Section verified: April 2026_

Queries where the exposure _is_ the vulnerability, matching a banner is already enough to flag the host for patching or further investigation. Prioritize these when triaging bulk results.

| Service | CVE | Class | Notes |
|---|---|---|---|
| Ray Dashboard | `CVE-2023-48022` | Unauth RCE | ShadowRay. Job submission API accepts arbitrary commands. Fix requires explicit `--disable-usage-stats` and auth config. |
| MLflow | `CVE-2024-37052` … `37060` | RCE via deserialization | Chain of model-loading vulnerabilities. Any exposed MLflow with write access to the model registry is RCE. |
| Flowise | `CVE-2024-36420` | Auth bypass | Path traversal grants unauth access to chatflow config, API keys. Affects < 1.8.2. |
| AnythingLLM | Multiple 2024–2025 | Auth bypass / SSRF | Recurring auth and SSRF issues, treat any exposed instance as suspect until version verified. |
| Ollama | `CVE-2024-37032` (Probllama) | Path traversal → RCE | Fixed in 0.1.34. Combined with the no-auth default this is remote code execution on any unpatched host. |
| n8n | Multiple RCE via node code | RCE by design | Workflow nodes can execute JS/shell. Write access = RCE. No CVE because it's the intended behavior. |
| Jupyter | Token-bypass misconfig | Unauth RCE | `--NotebookApp.token=""` is the historic footgun. Notebooks are shell. |
| ComfyUI + ComfyUI-Manager | Design-level RCE | RCE via custom nodes | Remote installation of custom Python nodes is intended behavior. Exposure + Manager = RCE. |
| Kubelet (10250) | Anonymous auth enabled | Cluster-wide RCE | `/exec` on any pod. Still seen in the wild at material volume. |
| Docker daemon (2375) | Design-level | Container escape + host RCE | Mount host filesystem into a privileged container, write to `/host/etc/cron.d/`, etc. |
| etcd (2379) | Anonymous access | Full cluster secret disclosure | All Kubernetes secrets, config, tokens readable. Effectively cluster takeover. |
