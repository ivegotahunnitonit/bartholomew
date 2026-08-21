"""
Bartholomew VS Code / Cursor Extension Packager
==============================================
Packs the compiled extension into a standard .vsix / .zip archive.
"""

import os
import zipfile
import shutil

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXT_DIR = os.path.join(ROOT_DIR, "vscode-extension")
OUTPUT_VSIX = os.path.join(ROOT_DIR, "web", "public", "bartholomew.vsix")
OUTPUT_ZIP = os.path.join(ROOT_DIR, "web", "public", "bartholomew-vscode-extension.zip")

FILES_TO_PACK = [
    ("package.json", "extension/package.json"),
    ("dist/extension.js", "extension/dist/extension.js"),
    ("dist/extension.js.map", "extension/dist/extension.js.map"),
]

def pack_extension():
    os.makedirs(os.path.dirname(OUTPUT_VSIX), exist_ok=True)
    print(f"[*] Packaging VS Code / Cursor extension to {OUTPUT_VSIX}...")

    with zipfile.ZipFile(OUTPUT_VSIX, "w", zipfile.ZIP_DEFLATED) as zipf:
        for src_rel, dest_rel in FILES_TO_PACK:
            full_src = os.path.join(EXT_DIR, src_rel)
            if os.path.exists(full_src):
                zipf.write(full_src, dest_rel)

    shutil.copy2(OUTPUT_VSIX, OUTPUT_ZIP)
    size_kb = os.path.getsize(OUTPUT_VSIX) / 1024
    print(f"[OK] VS Code Extension Packaged: {size_kb:.2f} KB")

if __name__ == "__main__":
    pack_extension()
