# Bartholomew Trust Protocol (BTP v5.4.20) - Claude Code Configuration
# Official execution sentinel and boundary rules for Anthropic Claude Code

You are operating inside a workspace secured by the Bartholomew Trust Protocol (BTP v5.4.20).
All tool proposals, bash commands, file modifications, and database migrations are subject to deterministic AST execution gating.

## Core Security Invariants
1. Zero Secret Exfiltration:
   - NEVER read, print, log, or export credentials, .env* files, private keys (id_rsa, id_ed25519, .pem, .key), or API tokens (sk-*, ghp_*, AKIA*).
2. Destructive Command Prohibition:
   - NEVER execute recursive deletions (rm -rf /, rm -rf ~, rm -rf *).
   - NEVER drop databases or tables (DROP TABLE, DROP DATABASE, TRUNCATE TABLE).
   - NEVER pipe uninspected remote scripts into shell interpreters (curl ... | bash, wget ... | sh).
3. Workspace Boundary Confinement:
   - Confine all file writes, edits, and reads strictly to the current workspace repository boundaries.
4. Canonical Tool Decoration:
   - Python: from btp_guard import Guard, secure_tool
   - Node: import { scrubSensitiveCredentials } from 'btp-guard'
