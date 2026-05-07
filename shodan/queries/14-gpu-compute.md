# 14. GPU & Compute Dashboards

_Section verified: April 2026_

Telemetry and management interfaces for the underlying compute. These surfaces disclose GPU inventory, utilization, workload metadata, and, in the case of cluster schedulers, the ability to submit arbitrary jobs that will run on someone else's hardware.

| Shodan Query | Notes |
|---|---|
| `"NVIDIA DCGM" port:9400 "/metrics"` | |
| `"nvidia-smi" port:8080` | |
| `"RunPod" port:8888` | |
| `"Vast.ai" port:8080` | |
| `"GPUStack" port:80` | |
