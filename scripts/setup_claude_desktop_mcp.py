"""
Setup Claude Desktop & Cursor MCP Configuration for Bartholomew v2.4
======================================================================
Writes claude_desktop_config.json so Claude Desktop and Cursor instantly
load Bartholomew as:
  1. An active MCP Guard tool server (`bartholomew-guard`).
  2. A resilient transparent security proxy (`bartholomew-proxy`) with
     in-flight secret redaction and transactional workspace rollbacks.
"""

import os
import sys
import json

def configure_mcp_environments():
    workspace_dir = os.path.abspath(".")
    python_exe = sys.executable

    # Detect Claude Desktop config path across OS
    if sys.platform == "win32":
        claude_dir = os.path.expandvars(r"%APPDATA%\Claude")
    elif sys.platform == "darwin":
        claude_dir = os.path.expanduser("~/Library/Application Support/Claude")
    else:
        claude_dir = os.path.expanduser("~/.config/Claude")

    os.makedirs(claude_dir, exist_ok=True)
    config_path = os.path.join(claude_dir, "claude_desktop_config.json")

    config_data = {}
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config_data = json.load(f)
        except Exception:
            config_data = {}

    if "mcpServers" not in config_data:
        config_data["mcpServers"] = {}

    # 1. Native Guard Server
    config_data["mcpServers"]["bartholomew-guard"] = {
        "command": python_exe,
        "args": ["-m", "mcp_server.server"],
        "cwd": workspace_dir
    }

    # 2. Resilient Transactional Proxy
    config_data["mcpServers"]["bartholomew-proxy"] = {
        "command": python_exe,
        "args": [
            "-m", "src.mcp_gateway",
            "--workspace", workspace_dir,
            "--server-cmd", python_exe, "-m", "mcp_server.server"
        ],
        "cwd": workspace_dir
    }

    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config_data, f, indent=2)

    print(f"[SUCCESS] Configured Claude Desktop MCP at: {config_path}")
    print(json.dumps(config_data, indent=2))


if __name__ == "__main__":
    configure_mcp_environments()
