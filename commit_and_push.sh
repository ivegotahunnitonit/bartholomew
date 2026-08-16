#!/bin/bash
set -e

cd ~/MisakaNet

# Update fork URL to clean HTTPS (no credentials embedded)
git remote remove fork || true
git remote add fork https://github.com/ivegotahunnitonit/MisakaNet.git

# Stage changes
git add .github/workflows/fatal-guard.yml

# Commit with DCO signoff
git commit -s -m "fix(ci): avoid fatal-guard false failure when no matching jobs run"

# Push to fork
git push -u fork fix/fatal-guard-false-failure-sleepywoody
