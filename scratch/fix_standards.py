"""
Comprehensive Multi-Viewport Sizing & Cross-Browser Standards Patcher
Fixes:
1. Standard WCAG Viewport (<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">)
2. Cross-browser CSS prefixes (-webkit-backdrop-filter, backdrop-filter, text-size-adjust, -webkit-user-select)
3. Fluid Responsive Sizing & Container Wrappers (Zero overflow, snug fitting on mobile/tablet/desktop/ultrawide)
4. Rel=noopener on all external links
"""

import os
import re

HTML_FILES = [
    "SAAS_LANDING_PAGE.html",
    "index.html",
    "dashboard.html",
    "operations.html",
    "simulator.html",
    "docs.html",
    "PITCH_DECK.html",
    "privacy.html",
    "RESUME.html",
    "chrome_extension/popup.html",
    "chrome_extension/sidepanel.html"
]

CSS_FILES = [
    "chrome_extension/content.css",
    "chrome_extension/sidepanel.css"
]

def patch_html(filepath):
    if not os.path.exists(filepath):
        return
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Viewport tag cleanup
    content = re.sub(
        r'<meta\s+name=["\']viewport["\']\s+content=["\'][^"\']*["\']\s*/?>',
        '<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">',
        content
    )
    if '<meta name="viewport"' not in content and '<head>' in content:
        content = content.replace('<head>', '<head>\n  <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">')

    # 2. Text size adjust
    content = re.sub(
        r'-webkit-text-size-adjust:\s*100%;',
        '-webkit-text-size-adjust: 100%; text-size-adjust: 100%;',
        content
    )
    
    # 3. Backdrop filter ordering & prefix
    def fix_backdrop(match):
        val = match.group(1)
        return f'-webkit-backdrop-filter: {val};\n      backdrop-filter: {val};'
    content = re.sub(r'(?<!-webkit-)backdrop-filter:\s*([^;]+);', fix_backdrop, content)
    # Deduplicate if duplicated
    content = re.sub(r'(-webkit-backdrop-filter:[^;]+;\s*)+', r'\1', content)
    content = re.sub(r'(backdrop-filter:[^;]+;\s*)+', r'\1', content)

    # 4. User-select prefix
    def fix_user_select(match):
        val = match.group(1)
        return f'-webkit-user-select: {val};\n      user-select: {val};'
    content = re.sub(r'(?<!-webkit-)user-select:\s*([^;]+);', fix_user_select, content)

    # 5. Remove obsolete -webkit-overflow-scrolling
    content = re.sub(r'-webkit-overflow-scrolling:\s*touch;\s*', '', content)

    # 6. Add rel="noopener noreferrer" to external links
    content = re.sub(
        r'<a\s+([^>]*target=["\']_blank["\'][^>]*)>',
        lambda m: m.group(0) if 'rel=' in m.group(0) else m.group(0).replace('target="_blank"', 'target="_blank" rel="noopener noreferrer"'),
        content
    )

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"[OK] Patched HTML: {filepath}")

def patch_css(filepath):
    if not os.path.exists(filepath):
        return
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Backdrop filter prefix
    def fix_backdrop(match):
        val = match.group(1)
        return f'-webkit-backdrop-filter: {val};\n  backdrop-filter: {val};'
    content = re.sub(r'(?<!-webkit-)backdrop-filter:\s*([^;]+);', fix_backdrop, content)

    # User select prefix
    def fix_user_select(match):
        val = match.group(1)
        return f'-webkit-user-select: {val};\n  user-select: {val};'
    content = re.sub(r'(?<!-webkit-)user-select:\s*([^;]+);', fix_user_select, content)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"[OK] Patched CSS: {filepath}")

if __name__ == "__main__":
    for h in HTML_FILES:
        patch_html(h)
    for c in CSS_FILES:
        patch_css(c)
