import re

path = 'dashboard/orchestrator.html'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix 1: inf-type
content = re.sub(
    r'<select id="inf-type"([^>]*)>',
    r'<select id="inf-type" title="Task Type" aria-label="Task Type"\1>',
    content
)

# Fix 2: inf-tokens
content = re.sub(
    r'<input id="inf-tokens"([^>]*)>',
    r'<input id="inf-tokens" title="Max Tokens" aria-label="Max Tokens" placeholder="512"\1>',
    content
)

# Fix 3: inf-priority
content = re.sub(
    r'<select id="inf-priority"([^>]*)>',
    r'<select id="inf-priority" title="Priority" aria-label="Priority"\1>',
    content
)

# Fix 4: nt-type
content = re.sub(
    r'<select id="nt-type"([^>]*)>',
    r'<select id="nt-type" title="Document Category" aria-label="Document Category"\1>',
    content
)

# Fix 5: nt-tier
content = re.sub(
    r'<select id="nt-tier"([^>]*)>',
    r'<select id="nt-tier" title="Attestation Tier" aria-label="Attestation Tier"\1>',
    content
)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Accessibility attributes added to select and input elements in dashboard/orchestrator.html")
