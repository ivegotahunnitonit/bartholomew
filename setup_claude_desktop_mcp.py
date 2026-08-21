"""
Setup Claude Desktop MCP Configuration for Bartholomew Guard
============================================================
Writes claude_desktop_config.json to %APPDATA%/Claude so Claude Desktop
instantly loads Bartholomew BTP Guard as an active tool.
"""

import os
import json

def configure_claude_desktop():
    claude_dir = os.path.expandvars(r"%APPDATA%\Claude")
    os.makedirs(claude_dir, exist_ok=True)
    config_path = os.path.join(claude_dir, "claude_desktop_config.json")

    workspace_dir = os.path.abspath(".")

    config_data = {}
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config_data = json.load(f)
        except Exception:
            config_data = {}

    if "mcpServers" not in config_data:
        config_data["mcpServers"] = {}

    config_data["mcpServers"]["bartholomew-guard"] = {
        "command": "python",
        "args": ["-m", "mcp_server.server"],
        "cwd": workspace_dir
    }

    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config_data, f, indent=2)

    print(f"[SUCCESS] Configured Claude Desktop MCP at: {config_path}")
    print("Configuration payload:")
    print(json.dumps(config_data, indent=2))

if __name__ == "__main__":
    configure_claude_desktop()
