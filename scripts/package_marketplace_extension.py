"""
Bartholomew Guard — Marketplace .vsix Packaging Script
======================================================
Builds an Open Packaging Conventions (OPC) compliant .vsix bundle
ready for immediate upload to Visual Studio Code Marketplace and Open VSX (Cursor).
"""

import os
import zipfile
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
EXT_DIR = BASE_DIR / "integrations" / "cursor-vscode-mcp"
DIST_DIR = BASE_DIR / "dist"
DIST_DIR.mkdir(parents=True, exist_ok=True)

with open(EXT_DIR / "package.json", "r", encoding="utf-8") as f:
    pkg = json.load(f)

version = pkg.get("version", "5.4.0")
vsix_filename = f"bartholomew-guard-{version}.vsix"
vsix_path = DIST_DIR / vsix_filename

# 1. Content Types XML
CONTENT_TYPES_XML = """<?xml version="1.0" encoding="utf-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="json" ContentType="application/json"/>
  <Default Extension="js" ContentType="application/javascript"/>
  <Default Extension="md" ContentType="text/markdown"/>
  <Default Extension="vsixmanifest" ContentType="text/xml"/>
</Types>
"""

# 2. VSIX Manifest XML
VSIX_MANIFEST_XML = f"""<?xml version="1.0" encoding="utf-8"?>
<PackageManifest Version="2.0.0" xmlns="http://schemas.microsoft.com/developer/vsx-schema/2011">
  <Metadata>
    <Identity Id="bartholomew-guard" Version="{version}" Publisher="bartholomew-security" Language="en-US"/>
    <DisplayName>{pkg.get('displayName')}</DisplayName>
    <Description>{pkg.get('description')}</Description>
    <Categories>Security,Linters,AI,Other</Categories>
  </Metadata>
  <Installation>
    <InstallationTarget Id="Microsoft.VisualStudio.Code"/>
  </Installation>
  <Dependencies/>
  <Assets>
    <Asset Type="Microsoft.VisualStudio.Code.Manifest" Path="extension/package.json" Addressable="true"/>
  </Assets>
</PackageManifest>
"""

print(f"Packaging {vsix_filename}...")
with zipfile.ZipFile(vsix_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
    zf.writestr("[Content_Types].xml", CONTENT_TYPES_XML.strip())
    zf.writestr("extension.vsixmanifest", VSIX_MANIFEST_XML.strip())
    
    # Add extension files
    for filename in ["package.json", "extension.js", "README.md"]:
        filepath = EXT_DIR / filename
        if filepath.exists():
            zf.write(filepath, arcname=f"extension/{filename}")

print(f"Successfully packaged: {vsix_path} ({os.path.getsize(vsix_path)} bytes)")
