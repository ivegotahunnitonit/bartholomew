import re

path = 'dashboard/orchestrator.html'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Remove invalid CSS rules from <style> section
invalid_css_patterns = [
    r'\.u-st-97\{color:\$\{p\.available\?\'var\(--gr\)\':\'#ef4444\'\}\}\n?',
    r'\.u-st-99\{--ac:\$\{meta\.color\}\}\n?',
    r'\.u-st-101\{color:\$\{meta\.color\}\}\n?',
    r'\.u-st-105\{font-family:var\(--mo\);font-weight:700;color:\$\{meta\.color\}\}\n?'
]

for pat in invalid_css_patterns:
    content = re.sub(pat, '', content)

# 2. Restore inline styles in JS template literals
content = content.replace(
    '<span class="lh u-st-97">',
    '<span class="lh" style="color:${p.available?\'var(--gr)\':\'#ef4444\'}">'
)
content = content.replace(
    '<div class="sc u-st-99">',
    '<div class="sc" style="--ac:${meta.color}">'
)
content = content.replace(
    '<div class="sv u-st-101">',
    '<div class="sv" style="color:${meta.color}">'
)
content = content.replace(
    '<div class="u-st-105">',
    '<div style="font-family:var(--mo);font-weight:700;color:${meta.color}">'
)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Restored JS template literal inline styles and removed invalid CSS rules from <style>")
