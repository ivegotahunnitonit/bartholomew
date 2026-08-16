#!/bin/bash
set -e

token="YOUR_GITHUB_TOKEN_HERE"

cd ~/memanto

# Setup fork remote URL with credentials embedded
git remote remove my-fork || true
git remote add my-fork "https://ivegotahunnitonit:${token}@github.com/ivegotahunnitonit/memanto.git"

# Create and switch to new branch
git checkout -b fix-agent-creation-1453 || git checkout fix-agent-creation-1453

# Stage and commit
git add memanto/app/utils/errors.py memanto/app/services/agent_service.py memanto/app/routes/sessions.py tests/test_unit.py
git commit -m "Fix agent creation limit conflict swallowing and standardize endpoint exception mapping" || echo "Nothing to commit"

# Push
git push -u my-fork fix-agent-creation-1453 --force
