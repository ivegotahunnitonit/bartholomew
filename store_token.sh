#!/bin/bash
set -e

# GitHub Personal Access Token (PAT)
TOKEN="YOUR_GITHUB_TOKEN_HERE"

# Configure credential helper to store credentials
git config --global credential.helper store

# Write credentials to ~/.git-credentials
cat > ~/.git-credentials <<EOF
https://git:${TOKEN}@github.com
EOF

echo "Git credentials stored successfully."
