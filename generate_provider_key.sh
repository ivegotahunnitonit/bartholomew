#!/bin/bash
# generate_provider_key.sh
# Runs inside the akash provider container to generate a fresh wallet key
# and print both the address and the exported armored key to stdout

set -e

KEY_NAME="acn-provider"
KEY_PASS="AcnProvider2024!"
HOME_DIR="/tmp/akash-keygen"

mkdir -p "$HOME_DIR"

# Generate new key
echo "$KEY_PASS" | provider-services keys add "$KEY_NAME" \
  --home="$HOME_DIR" \
  --keyring-backend=test \
  --output=json 2>&1

# Get the address
ADDR=$(provider-services keys show "$KEY_NAME" -a \
  --home="$HOME_DIR" \
  --keyring-backend=test)
echo "PROVIDER_ADDRESS=$ADDR"

# Export armored key
echo "$KEY_PASS" | provider-services keys export "$KEY_NAME" \
  --home="$HOME_DIR" \
  --keyring-backend=test \
  --output-dir="$HOME_DIR" 2>&1 | tee /tmp/key-export.txt || true

# Try alternative export method
provider-services keys export "$KEY_NAME" \
  --home="$HOME_DIR" \
  --keyring-backend=test 2>&1 || true

echo "KEY_PASS=$KEY_PASS"
