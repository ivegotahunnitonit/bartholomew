#!/bin/bash
set -e

token="YOUR_GITHUB_TOKEN_HERE"

cd ~/memanto

# Setup fork remote URL with credentials embedded
git remote remove my-fork || true
git remote add my-fork "https://ivegotahunnitonit:${token}@github.com/ivegotahunnitonit/memanto.git"

# Create and switch to new branch
git checkout -b fix-original-id-1335 || git checkout fix-original-id-1335

# Stage and commit
git add memanto/app/services/memory_read_service.py tests/test_unit.py
git commit -m "Fix update_memory overwriting original_id by preserving extra fields in format_memory_item" || echo "Nothing to commit"

# Push
git push -u my-fork fix-original-id-1335 --force
