# 12. Container & Orchestration Infrastructure

_Expanded in v2 · Section verified: April 2026_

Modern AI stacks deploy container-first and k8s-first. The orchestration layer underneath the AI services is often the softer target, and compromise there gives you every workload on the cluster for free.

## Docker Runtime

| Shodan Query | Notes |
|---|---|
| `"Docker" port:2375 "api"` | Unauth Docker daemon, container escape + host RCE |
| `"Portainer" port:9000` | Default creds / signup-becomes-admin |

**Artifact stores** (Docker Registry v2, Harbor, MinIO) moved to §2 under Object Storage & Artifact Stores. This section covers container _runtime_ and orchestration surface only.

## Kubernetes

| Shodan Query | Notes |
|---|---|
| `port:6443 "kubernetes" "unauthorized"` | API server reachable, auth enforced |
| `port:6443 "/api/v1" -"unauthorized"` | Anonymous API access, full cluster read |
| `port:10250 "kubelet"` | Anonymous kubelet = exec into any pod = cluster-wide RCE |
| `port:10255 "kubelet"` | Read-only kubelet, pod/node enumeration |
| `port:2379 "etcd"` | Unauth etcd = full cluster state, including secrets |
| `"etcd" "v3" port:2379` | |
| `"Rancher" port:8443` | |
| `"k3s" port:6443` | |
| `"Kubernetes Dashboard" port:30000` | Exposed dashboard, skip-login option historically |

**Kubelet on 10250** with anonymous access enabled is functionally equivalent to cluster-wide RCE. The `/exec` and `/run` endpoints allow arbitrary command execution inside any pod on the node. This is still seen in the wild at material volume.

## Supporting Infrastructure

| Shodan Query | Notes |
|---|---|
| `"Consul" port:8500 "/v1/catalog"` | Service discovery, full topology |
| `"Vault" port:8200 "/v1/sys/health"` | Auth required; reachable surface for attacks |

**MinIO moved to §2 Object Storage & Artifact Stores.**
