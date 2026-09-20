"""
Bartholomew Emoji Stripper
==========================
Removes all emoji symbols from documentation, code, and frontend assets.
"""

import os
import unicodedata

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

EXTENSIONS = {
    ".md", ".txt", ".json", ".yaml", ".yml", ".py", ".ts", ".tsx", ".js", ".html", ".css"
}

IGNORE_DIRS = {
    ".git", "node_modules", ".venv", "__pycache__", "dist", ".pytest_cache"
}

def is_emoji(ch: str) -> bool:
    """Returns True if character is an emoji symbol or modifier."""
    code = ord(ch)
    # Check Unicode blocks for emojis and pictographs
    if (
        0x1F300 <= code <= 0x1F9FF or
        0x1FA00 <= code <= 0x1FAFF or
        0x2600 <= code <= 0x26FF or
        0x2700 <= code <= 0x27BF or
        0x1F600 <= code <= 0x1F64F or
        0x1F680 <= code <= 0x1F6FF or
        0x2B50 <= code <= 0x2B55 or
        0x2300 <= code <= 0x23FF or
        code == 0xFE0F or code == 0x200D
    ):
        return True
    
    cat = unicodedata.category(ch)
    if cat == "So": # Other Symbol
        if code > 0x2000:
            return True
    return False

def clean_file(filepath: str) -> bool:
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception:
        return False

    cleaned_chars = []
    for ch in content:
        if not is_emoji(ch):
            cleaned_chars.append(ch)
    
    cleaned = "".join(cleaned_chars)

    if cleaned != content:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(cleaned)
        return True
    return False

def run_cleanup():
    modified_count = 0
    for root, dirs, files in os.walk(ROOT_DIR):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        for f in files:
            ext = os.path.splitext(f)[1].lower()
            if ext in EXTENSIONS or f in ("LICENSE", "Dockerfile", "action.yml"):
                full_path = os.path.join(root, f)
                if clean_file(full_path):
                    print(f"[CLEANED] {os.path.relpath(full_path, ROOT_DIR)}")
                    modified_count += 1
    print(f"\n[DONE] Removed emojis across {modified_count} files.")

if __name__ == "__main__":
    run_cleanup()
