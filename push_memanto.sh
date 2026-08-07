#!/bin/bash
set -e

token="YOUR_GITHUB_TOKEN_HERE"

cd ~/memanto

# Configure Git identities
git config user.name "ivegotahunnitonit"
git config user.email "ivegotahunnitonit@users.noreply.github.com"

# Setup fork remote URL with credentials embedded
git remote remove my-fork || true
git remote add my-fork "https://ivegotahunnitonit:${token}@github.com/ivegotahunnitonit/memanto.git"

# Create and switch to new branch
git checkout -b fix-ambiguity-guard-1375 || git checkout fix-ambiguity-guard-1375

# Stage and commit
git add memanto/app/services/memory_parsing_service.py tests/test_memory_parsing.py
git commit -m "Fix ambiguity guard being bypassed by common auxiliary verbs" || echo "Nothing to commit"

# Push
git push -u my-fork fix-ambiguity-guard-1375 --force
