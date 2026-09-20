#!/bin/bash
set -e

cd ~/MisakaNet

# Stash our modified fatal-guard.yml
git stash

# Checkout main and pull latest upstream
git checkout main
git pull origin main

# Create new branch
git checkout -b fix/fatal-guard-false-failure-sleepywoody

# Apply the stashed changes
git stash pop
