#!/bin/bash
set -e

# Extract token from ~/.git-credentials
token=$(cat ~/.git-credentials | grep -oP '(?<=ivegotahunnitonit:).*(?=@github.com)')

# Query GitHub API for MisakaNet Issue 514
curl -s -H "Authorization: token $token" -H "User-Agent: curl" \
  "https://api.github.com/repos/Ikalus1988/MisakaNet/issues/514" > ~/issue_514.json
