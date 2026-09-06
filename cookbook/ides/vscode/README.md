# BTP Guard for VS Code

Install the official pre-packaged VSIX extension directly into VS Code or Cursor:

```bash
code --install-extension vscode-extension/bartholomew-guard-vscode-3.0.0.vsix
```

Or for Cursor:
```bash
cursor --install-extension vscode-extension/bartholomew-guard-vscode-3.0.0.vsix
```

### Features Enabled
- Real-time terminal command gating against destructive shell commands.
- Automatic Ed25519 signature verification on autonomous agent tool calls.
- In-IDE status bar indicator showing active threat entropy and quorum threshold status.
