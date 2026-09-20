import os
import zipfile

def package_keystone_vsix():
    pkg_dir = os.path.abspath('packages/bartholomew-keystone')
    out_vsix = os.path.join(pkg_dir, 'bartholomew-keystone-1.0.0.vsix')

    content_types_xml = """<?xml version="1.0" encoding="utf-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension=".json" ContentType="application/json"/>
  <Default Extension=".vsixmanifest" ContentType="text/xml"/>
  <Default Extension=".js" ContentType="application/javascript"/>
  <Default Extension=".png" ContentType="image/png"/>
  <Default Extension=".md" ContentType="text/markdown"/>
  <Default Extension=".ts" ContentType="video/mp2t"/>
</Types>"""

    vsixmanifest_xml = """<?xml version="1.0" encoding="utf-8"?>
<PackageManifest Version="2.0.0" xmlns="http://schemas.microsoft.com/developer/vsx-schema/2011" xmlns:d="http://schemas.microsoft.com/developer/vsx-schema-design/2011">
  <Metadata>
    <Identity Language="en-US" Id="bartholomew-keystone" Version="1.0.0" Publisher="Bartholomew" />
    <DisplayName>Bartholomew Keystone — Agent Capability Passkey</DisplayName>
    <Description xml:space="preserve">Cryptographically signed clearance tokens granting autonomous AI agents scoped access across IDEs, programs, and web searches.</Description>
    <Tags>ai,agents,guardrails,passkey,security,cursor,copilot</Tags>
    <Categories>Machine Learning,Security,Other</Categories>
    <Icon>extension/icon.png</Icon>
    <License>extension/LICENSE</License>
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

        files_to_pack = [
            ('package.json', 'extension/package.json'),
            ('README.md', 'extension/README.md'),
            ('icon.png', 'extension/icon.png'),
            ('tsconfig.json', 'extension/tsconfig.json'),
            ('dist/extension.js', 'extension/dist/extension.js'),
            ('dist/keystone_passkey.js', 'extension/dist/keystone_passkey.js'),
            ('src/extension.ts', 'extension/src/extension.ts'),
            ('src/keystone_passkey.ts', 'extension/src/keystone_passkey.ts'),
        ]

        for src, arc in files_to_pack:
            p = os.path.join(pkg_dir, src)
            if os.path.exists(p):
                z.write(p, arc)

    size = os.path.getsize(out_vsix)
    print(f"[+] Successfully packaged {out_vsix} ({size:,} bytes)")

if __name__ == '__main__':
    package_keystone_vsix()
