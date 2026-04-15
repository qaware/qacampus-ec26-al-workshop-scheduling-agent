#!/usr/bin/env bash

# Script to decrypt an encrypted kubeconfig file
# Usage: ./decrypt-kubeconfig.sh <encrypted-file> <password> [output-file]

set -e

if [ -z "$1" ] || [ -z "$2" ]; then
  echo "Usage: $0 <encrypted-file> <password> [output-file]"
  echo ""
  echo "Arguments:"
  echo "  encrypted-file  Path to the encrypted .yaml.enc file"
  echo "  password        Password used during encryption"
  echo "  output-file     (Optional) Output file path. If not provided, prints to stdout"
  echo ""
  echo "Examples:"
  echo "  # Print to stdout"
  echo "  $0 kubeconfigs-encrypted/workshop-kubeconfig.yaml.enc my-password"
  echo ""
  echo "  # Save to file"
  echo "  $0 kubeconfigs-encrypted/workshop-kubeconfig.yaml.enc my-password kubeconfig.yaml"
  echo ""
  echo "  # Save and use directly"
  echo "  $0 kubeconfigs-encrypted/workshop-kubeconfig.yaml.enc my-password my-kubeconfig.yaml"
  echo "  export KUBECONFIG=my-kubeconfig.yaml"
  echo "  kubectl get nodes"
  exit 1
fi

ENCRYPTED_FILE="$1"
PASSWORD="$2"
OUTPUT_FILE="$3"

# Check if encrypted file exists
if [ ! -f "$ENCRYPTED_FILE" ]; then
  echo "✗ ERROR: File not found: $ENCRYPTED_FILE"
  exit 1
fi

# Decrypt the file using pbkdf2 key derivation
if [ -z "$OUTPUT_FILE" ]; then
  # Print to stdout
  openssl aes-256-cbc -d -a -pbkdf2 -pass "pass:$PASSWORD" -in "$ENCRYPTED_FILE"
else
  # Save to file
  openssl aes-256-cbc -d -a -pbkdf2 -pass "pass:$PASSWORD" -in "$ENCRYPTED_FILE" -out "$OUTPUT_FILE"
  echo "✓ Decrypted kubeconfig saved to: $OUTPUT_FILE"
  echo ""
  echo "To use this kubeconfig:"
  echo "  export KUBECONFIG=$OUTPUT_FILE"
  echo "  kubectl get nodes"
fi
