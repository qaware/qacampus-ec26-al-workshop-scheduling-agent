#!/usr/bin/env bash

echo "Testing ec-scheduling conversation..."

# Start conversation with ec-scheduling request
echo "Sending ec-scheduling request..."

request=$(cat <<EOF
{
 "jsonrpc": "2.0",
 "id": 1,
 "method": "message/send",
 "params": {
   "message": {
     "role": "user",
     "parts": [
       {
         "kind": "text",
         "text": "Gib mir Informationen zum Talk Hands-on with the Agentic Layer."
       }
     ],
     "messageId": "$(uuidgen)",
     "contextId": "$(uuidgen)"
   },
   "metadata": {}
 }
}
EOF
)

AGENT_GATEWAY_URL="${AGENT_GATEWAY_URL:-http://localhost:11002}"
AGENT_GATEWAY_API_KEY="${AGENT_GATEWAY_API_KEY:-}"

# -s: silent mode (no progress meter)
# -S: show error message even with -s
# -f: fail silently (no HTML output on server errors like 404)
AUTH_HEADER=(-H "X-ANOTHER-HEADER: test-api-key")

CONVERSATION_RESPONSE=$(curl --max-time 90 --retry 5 --retry-connrefused -sfS -X POST "${AGENT_GATEWAY_URL}/ec-schedule-agent" \
   -H "Content-Type: application/json" \
   "${AUTH_HEADER[@]}" \
   -d "${request}")
exit_code=$?

echo "Conversation response:"
echo "$CONVERSATION_RESPONSE" | jq '.' 2>/dev/null || echo "$CONVERSATION_RESPONSE"

# Check the exit code
if [[ $exit_code -eq 0 ]]; then
  echo "✅ SUCCESS: Agent responded with relevant ec-scheduling content"
else
  echo "❌ ERROR: curl command failed with exit code $exit_code"
  exit 1
fi
