import os
import re

ROOT_DIR = r"c:\Users\User\.gemini\antigravity\scratch\autonomous-circularity-network"

REPLACEMENTS = [
    (r'ghp_[A-Za-z0-9_]{30,}', 'YOUR_GITHUB_TOKEN_HERE'),
    (r'sk_live_[A-Za-z0-9_]{24,}', 'YOUR_STRIPE_SECRET_KEY_HERE'),
    (r'pk_live_[A-Za-z0-9_]{24,}', 'YOUR_STRIPE_PUBLISHABLE_KEY_HERE'),
]

EXCLUDE_DIRS = {'.git', 'node_modules', '.tempmediaStorage', '.system_generated'}
EXCLUDE_FILES = {'.env'}

def sanitize():
    sanitized_count = 0
    for root, dirs, files in os.walk(ROOT_DIR):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS and not d.startswith('.')]
        
        for file in files:
            if file in EXCLUDE_FILES or file.endswith('.exe') or file.endswith('.zip') or file.endswith('.pyc'):
                continue
            
            abs_path = os.path.join(root, file)
            
            try:
                with open(abs_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                new_content = content
                for pattern, replacement in REPLACEMENTS:
                    new_content = re.sub(pattern, replacement, new_content)
                
                if new_content != content:
                    with open(abs_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    print(f"Sanitized: {os.path.relpath(abs_path, ROOT_DIR)}")
                    sanitized_count += 1
            except Exception as e:
                print(f"Error processing {abs_path}: {e}")

    print(f"\nCompleted sanitization! Cleaned {sanitized_count} files.")

if __name__ == "__main__":
    sanitize()
