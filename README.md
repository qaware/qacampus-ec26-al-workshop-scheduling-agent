# Workshop: Hands-on with the Agentic Layer

## Requirements

- `kubectl` installed and configured
- GitHub account

## Optional

- Local Kubernetes cluster (e.g., minikube, kind, Docker Desktop)
- [Tilt](https://tilt.dev/) for local development

## Option 1: Use the remote cluster

### Decrypt Kubeconfig

Use the included decryption script.

If using Windows, find another way to get the decoded file, e.g. via https://www.cryptool.org/en/cto/openssl/?tab=encryption 
Alternatively, use https://web.localsend.org/ and ask a friend.

1. Decrypt the kubeconfig (Kubernetes credentials file).
```bash
./decrypt-kubeconfig.sh kubeconfigs-encrypted/workshop-kubeconfig.yaml.enc <password-announced-during-workshop> kubeconfig.yaml
```

2. Connect to the cluster
    ```bash
    export KUBECONFIG=kubeconfig.yaml 
   
    kubectl get pods
    ```

## Option 2: Use a local cluster (with Tilt)

### Prerequisites

1. A running local Kubernetes cluster (e.g., minikube, kind, or Docker Desktop)
2. [Tilt](https://tilt.dev/) installed
3. A `.env` file in the project root with the following variables:

```env
GOOGLE_API_KEY=<your-google-api-key>
```

### Starting Tilt

```bash
tilt up
```

This will deploy the full stack locally, including:

- **Agent Runtime** — core runtime for the agentic layer
- **AI Gateway** — LLM proxy (LiteLLM-based)
- **Agent Gateway** — KrakenD-based API gateway
- **Tool Gateway** — MCP tool routing
- **EC Schedule MCP Server** — the MCP server for this project
- **Presidio** — PII guardrail
- **LibreChat** — chat UI for interacting with the agent
- **Testbench** — experiment runner
- **LGTM Stack** — observability (Grafana + Loki + Tempo + Mimir)

### Port Forwards

Once Tilt is running, the following services are available locally:

| Service                  | URL                        |
| ------------------------ | -------------------------- |
| LGTM (Grafana)           | http://localhost:11000      |
| AI Gateway               | http://localhost:11001      |
| Agent Gateway            | http://localhost:11002      |
| LibreChat                | http://localhost:11003      |
| Observability Dashboard  | http://localhost:11004      |
| Tool Gateway             | http://localhost:11005      |
| EC Schedule MCP Server   | http://localhost:11020      |

## Deploying Local Resources

The `deploy/local/` directory contains Kubernetes manifests managed with [Kustomize](https://kustomize.io/). These include:

- `guardrail-presidio.yaml` — PII guardrail
- `ai-gateway-pii.yaml` — AI Gateway PII configuration
- `ec-schedule-agent.yaml` — EC Schedule Agent
- `ec-schedule-agent-experiment.yaml` — EC Schedule Agent Experiment

## Apply resources

```bash
kubectl apply -k deploy/local/
```

### Apply a single resource

```bash
kubectl apply -f deploy/local/<filename>.yaml
```

### Remove all resources

```bash
kubectl delete -k deploy/local/
```

