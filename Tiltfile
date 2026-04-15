update_settings(max_parallel_updates=2, k8s_upsert_timeout_secs=600)

# Load .env file for environment variables
load('ext://dotenv', 'dotenv')
dotenv()

load('ext://helm_remote', 'helm_remote')

v1alpha1.extension_repo(name='agentic-layer', url='https://github.com/agentic-layer/tilt-extensions', ref='v0.14.0')

v1alpha1.extension(name='cert-manager', repo_name='agentic-layer', repo_path='cert-manager')
load('ext://cert-manager', 'cert_manager_install')
cert_manager_install()

v1alpha1.extension(name='agent-runtime', repo_name='agentic-layer', repo_path='agent-runtime')
load('ext://agent-runtime', 'agent_runtime_install')
agent_runtime_install(version='0.27.0')

v1alpha1.extension(name='ai-gateway-litellm', repo_name='agentic-layer', repo_path='ai-gateway-litellm')
load('ext://ai-gateway-litellm', 'ai_gateway_litellm_install')
ai_gateway_litellm_install(version='0.8.2', instance=False)

v1alpha1.extension(name='agent-gateway-krakend', repo_name='agentic-layer', repo_path='agent-gateway-krakend')
load('ext://agent-gateway-krakend', 'agent_gateway_krakend_install')
agent_gateway_krakend_install(version='0.6.6', instance=False)

v1alpha1.extension(name='tool-gateway-agentgateway', repo_name='agentic-layer', repo_path='tool-gateway-agentgateway')
load('ext://tool-gateway-agentgateway', 'tool_gateway_agentgateway_install')
tool_gateway_agentgateway_install(version='0.2.3', instance=False)

# Apply local Kubernetes manifests
k8s_yaml(kustomize('deploy/infra'))

# Build MCP server images from single Dockerfile, selecting the server via CMD
docker_build(
    'ec-schedule-mcp',
    context='./mcp-server',
)
k8s_resource('ec-schedule-mcp', port_forwards='11020:8000', labels=['showcase'], resource_deps=['agent-runtime'])
k8s_resource('ec-schedule-agent', labels=['showcase'], resource_deps=['agent-runtime', 'ec-schedule-mcp'])

# Presidio PII Guardrail
k8s_resource('presidio', labels=['agentic-layer'])

# Agentic Layer Components
k8s_resource('ai-gateway', labels=['agentic-layer'], resource_deps=['agent-runtime'], port_forwards=['11001:80'])
k8s_resource('agent-gateway', labels=['agentic-layer'], resource_deps=['agent-runtime'], port_forwards='11002:8080')
k8s_resource('tool-gateway', labels=['agentic-layer'], resource_deps=['agent-runtime'], port_forwards='11005:80')
k8s_resource('agent-runtime-configuration', labels=['agentic-layer'], resource_deps=['agent-runtime'])
k8s_resource('ai-gateway', labels=['agentic-layer'], resource_deps=['agent-runtime', 'presidio-guardrail'], port_forwards='11006:80')

# Monitoring
k8s_resource('lgtm', labels=['monitoring'], port_forwards=['11000:3000'])

# Secrets for LLM API keys
google_api_key = os.environ.get('GOOGLE_API_KEY', '')
if not google_api_key:
    warn('GOOGLE_API_KEY environment variable is not set. Please set it in your shell or .env file.')

# Create Kubernetes secrets from environment variables
load('ext://secret', 'secret_from_dict')
k8s_yaml(secret_from_dict(
    name = "api-key-secrets",
    namespace = "ai-gateway",
    # The ai-gateway expects the API key to be called <provider>_API_KEY
    inputs = { "GEMINI_API_KEY": google_api_key }
))

# Observability Dashboard
helm_remote(
    'observability-dashboard',
    repo_url='oci://ghcr.io/agentic-layer/charts',
    version='0.3.0',
    namespace='observability-dashboard',
)
k8s_resource('observability-dashboard', labels=['agentic-layer'], port_forwards='11004:8000')

# Testbench
v1alpha1.extension(name='testbench', repo_name='agentic-layer', repo_path='testbench')
load('ext://testbench', 'testbench_install')
testbench_install(version='0.8.0', operator_version='0.8.0')

k8s_resource('ec-schedule-agent-experiment', labels=['testing'], resource_deps=['testbench', 'ai-gateway'])

# LibreChat
v1alpha1.extension(name='librechat', repo_name='agentic-layer', repo_path='librechat')
load('ext://librechat', 'librechat_install')
librechat_install(port='11003')


k8s_yaml(kustomize('deploy/local'))

k8s_yaml(secret_from_dict(
    name = "api-key-secrets",
    namespace = "ec-schedule",
    # The ai-gateway expects the API key to be called <provider>_API_KEY
    inputs = { "GEMINI_API_KEY": google_api_key }
))

k8s_resource(
    objects=['presidio:guardrailprovider', 'pii-guard:guard'],
    new_name='presidio-guardrail',
    labels=['agentic-layer'],
    resource_deps=['agent-runtime', 'presidio']
)

k8s_resource('ai-gateway-pii', labels=['agentic-layer'], resource_deps=['agent-runtime', 'presidio-guardrail'])
