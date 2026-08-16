import re
import os

path = 'dashboard/orchestrator.html'
if os.path.exists(path):
    with open(path, 'r', encoding='utf-8') as f:
        html = f.read()

    style_map = {}
    counter = 100

    def replace_inline_styles(content):
        global counter
        
        def replacer(match):
            global counter
            full_tag = match.group(0)
            style_m = re.search(r'style="([^"]+)"', full_tag)
            if not style_m:
                return full_tag
            
            style_str = style_m.group(1).strip()
            if style_str not in style_map:
                style_map[style_str] = f"orch-st-{counter}"
                counter += 1
            
            cls_name = style_map[style_str]
            tag_clean = re.sub(r'\s*style="[^"]+"', '', full_tag)
            
            if 'class="' in tag_clean:
                tag_clean = re.sub(r'class="([^"]+)"', r'class="\1 ' + cls_name + '"', tag_clean)
            else:
                tag_clean = re.sub(r'(/?>)$', r' class="' + cls_name + r'"\1', tag_clean)
            
            return tag_clean

        # Regex for any tag with a style attribute
        return re.sub(r'<[a-zA-Z0-9-]+[^>]*?\bstyle="[^"]+"[^>]*?>', replacer, content, flags=re.DOTALL)

    new_html = replace_inline_styles(html)

    if style_map:
        css_rules = "\n/* Orchestrator Cleaned Utility Classes */\n"
        for css, cls in style_map.items():
            css_rules += f".{cls} {{ {css} }}\n"
        
        if '</style>' in new_html:
            new_html = new_html.replace('</style>', css_rules + '</style>', 1)
        elif '</head>' in new_html:
            new_html = new_html.replace('</head>', f'<style>{css_rules}</style></head>', 1)

    with open(path, 'w', encoding='utf-8') as f:
        f.write(new_html)

    print(f"Cleaned {len(style_map)} inline style rules from {path}")
