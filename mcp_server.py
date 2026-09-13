#!/usr/bin/env python3
"""
Bartholomew Model Context Protocol (MCP) Server & Proxy Entrypoint
==================================================================
Direct root launcher for Bartholomew MCP transparent security proxy.
Safely wraps downstream MCP tool servers (Postgres, Filesystem, Terminal, GitHub)
for Claude Desktop, Cursor, Windsurf, and OpenAI Agents SDK.
"""

import sys
import os

root_dir = os.path.dirname(os.path.abspath(__file__))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)
src_dir = os.path.join(root_dir, "src")
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from src.mcp_gateway import main

if __name__ == "__main__":
    main()
