import os
import json
import zipfile
import shutil

def pack_package(pkg_dir, package_id, display_name, description):
    # Read version from package.json
    pkg_json_path = os.path.join(pkg_dir, 'package.json')
    version = "5.4.21"
    if os.path.exists(pkg_json_path):
        with open(pkg_json_path, 'r', encoding='utf-8') as f:
            vinfo = json.load(f)
            version = vinfo.get('version', version)

    out_vsix_name = f"{package_id}-{version}.vsix"
    out_vsix = os.path.join(pkg_dir, out_vsix_name)
    
    content_types_xml = """<?xml version="1.0" encoding="utf-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension=".json" ContentType="application/json"/>
  <Default Extension=".vsixmanifest" ContentType="text/xml"/>
  <Default Extension=".js" ContentType="application/javascript"/>
  <Default Extension=".png" ContentType="image/png"/>
  <Default Extension=".md" ContentType="text/markdown"/>
  <Default Extension=".ts" ContentType="video/mp2t"/>
</Types>"""

    vsixmanifest_xml = f"""<?xml version="1.0" encoding="utf-8"?>
<PackageManifest Version="2.0.0" xmlns="http://schemas.microsoft.com/developer/vsx-schema/2011">
  <Metadata>
    <Identity Language="en-US" Id="{package_id}" Version="{version}" Publisher="itsubsolomon" />
    <DisplayName>{display_name}</DisplayName>
    <Description xml:space="preserve">{description}</Description>
    <Tags>ai,security,agent,mcp,trust,guardrails,cursor,copilot</Tags>
    <Categories>Machine Learning,Security,Other</Categories>
    <Icon>extension/icon.png</Icon>
  </Metadata>
  <Installation>
    <InstallationTarget Id="Microsoft.VisualStudio.Code"/>
  </Installation>
  <Dependencies/>
  <Assets>
    <Asset Type="Microsoft.VisualStudio.Code.Manifest" Path="extension/package.json" Addressable="true" />
    <Asset Type="Microsoft.VisualStudio.Services.Icons.Default" Path="extension/icon.png" Addressable="true" />
  </Assets>
</PackageManifest>"""

    with zipfile.ZipFile(out_vsix, 'w', zipfile.ZIP_DEFLATED) as z:
        z.writestr('[Content_Types].xml', content_types_xml)
        z.writestr('extension.vsixmanifest', vsixmanifest_xml)
        for root, dirs, files in os.walk(pkg_dir):
            if 'node_modules' in root or '.git' in root or '.vsix' in root:
                continue
            for f in files:
                if f.endswith('.vsix'):
                    continue
                fp = os.path.join(root, f)
                rel = os.path.relpath(fp, pkg_dir)
                z.write(fp, 'extension/' + rel.replace('\\', '/'))

    size = os.path.getsize(out_vsix)
    print(f"[+] Successfully packaged {out_vsix} ({size:,} bytes)")
    
    # Also write 1.0.0 copy for any legacy CI/CD references
    legacy_vsix = os.path.join(pkg_dir, f"{package_id}-1.0.0.vsix")
    shutil.copyfile(out_vsix, legacy_vsix)
    print(f"[+] Synced legacy alias: {legacy_vsix}")
    return out_vsix

if __name__ == '__main__':
    root = os.path.abspath('.')
    pack_package(
        os.path.join(root, 'packages/bartholomew-keystone'),
        'bartholomew-keystone',
        'Bartholomew Keystone — Agent Capability Passkey',
        'Cryptographically signed clearance tokens granting autonomous AI agents scoped access across IDEs, programs, and web searches.'
    )
    pack_package(
        os.path.join(root, 'packages/vscode-extension'),
        'bartholomew-guard-vscode',
        'Bartholomew Autonomous AI Guard',
        'Sub-25µs in-process tool execution gateway, runtime dispatch seam, and AST security gate.'
    )
