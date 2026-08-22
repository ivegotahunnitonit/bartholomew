"""
Bartholomew VS Code VSIX Extension Packager
===========================================
Packages the compiled extension into a standard Open Packaging Conventions
(OPC) .vsix archive compatible with Visual Studio Code and Cursor.
"""

import os
import zipfile
import json
from pathlib import Path

ROOT = Path(__file__).parent.parent
EXT_DIR = ROOT / "vscode-extension"
PUBLIC_OUT = ROOT / "web" / "public" / "bartholomew.vsix"
DIST_OUT = ROOT / "web" / "dist" / "bartholomew.vsix"

CONTENT_TYPES_XML = """<?xml version="1.0" encoding="utf-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="json" ContentType="application/json"/>
  <Default Extension="js" ContentType="application/javascript"/>
  <Default Extension="map" ContentType="application/json"/>
  <Default Extension="md" ContentType="text/markdown"/>
  <Default Extension="vsixmanifest" ContentType="text/xml"/>
</Types>
"""

VSIX_MANIFEST_XML = """<?xml version="1.0" encoding="utf-8"?>
<PackageManifest Version="2.0.0" xmlns="http://schemas.microsoft.com/developer/vsx-schema/2011">
  <Metadata>
    <Identity Id="bartholomew-guard-vscode" Version="2.2.0" Publisher="Bartholomew" />
    <DisplayName>Bartholomew Autonomous AI Guard</DisplayName>
    <Description xml:space="preserve">Sub-millisecond cryptographic attestation and invariant guard for Cursor and VS Code agent sessions.</Description>
    <Categories>Security,Machine Learning,Programming Languages</Categories>
    <License>extension/LICENSE.txt</License>
  </Metadata>
  <Installation>
    <InstallationTarget Id="Microsoft.VisualStudio.Code"/>
  </Installation>
  <Dependencies/>
  <Assets>
    <Asset Type="Microsoft.VisualStudio.Code.Manifest" Path="extension/package.json" Addressable="true" />
    <Asset Type="Microsoft.VisualStudio.Services.Content.Details" Path="extension/README.md" Addressable="true" />
  </Assets>
</PackageManifest>
"""

def build_vsix():
    print("[VSIX] Building Bartholomew VS Code Extension VSIX package...")
    PUBLIC_OUT.parent.mkdir(parents=True, exist_ok=True)
    DIST_OUT.parent.mkdir(parents=True, exist_ok=True)

    package_json = EXT_DIR / "package.json"
    extension_js = EXT_DIR / "dist" / "extension.js"
    readme_md = ROOT / "README.md"
    license_md = ROOT / "LICENSE.md"

    for target in [PUBLIC_OUT, DIST_OUT]:
        with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as z:
            z.writestr("[Content_Types].xml", CONTENT_TYPES_XML.strip())
            z.writestr("extension.vsixmanifest", VSIX_MANIFEST_XML.strip())
            z.write(package_json, "extension/package.json")
            z.write(extension_js, "extension/dist/extension.js")
            z.write(readme_md, "extension/README.md")
            z.write(license_md, "extension/LICENSE.txt")
        print(f"[VSIX] Generated: {target} ({target.stat().st_size} bytes)")

if __name__ == "__main__":
    build_vsix()
