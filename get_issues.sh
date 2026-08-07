#!/bin/bash
set -e

# Extract token from ~/.git-credentials
token=$(cat ~/.git-credentials | grep -oP '(?<=ivegotahunnitonit:).*(?=@github.com)')

# Query GitHub API for all open issues
curl -s -H "Authorization: token $token" -H "User-Agent: curl" \
  "https://api.github.com/repos/moorcheh-ai/memanto/issues?state=open&per_page=100" > ~/open_issues.json

# Parse issues and filter out PRs
python3 -c "
import json
with open('/home/User/open_issues.json') as f:
    issues = json.load(f)
if isinstance(issues, dict):
    print('API Error:', issues)
else:
    only_issues = [i for i in issues if 'pull_request' not in i]
    print(json.dumps([{'number': i['number'], 'title': i['title'], 'url': i['html_url']} for i in only_issues], indent=2))
"
