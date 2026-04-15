# Workshop: Hands-on with the Agentic Layer

## Requirements

- `kubectl` installed and configured
- GitHub account

## Optional

- Local Kubernetes cluster (e.g., minikube, kind, Docker Desktop)
- [Tilt](https://tilt.dev/) for local development

## Local Development with Tilt

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

