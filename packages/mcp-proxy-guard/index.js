/**
 * mcp-proxy-guard
 * Sub-35µs in-process security proxy for Model Context Protocol (MCP) servers.
 * Intercepts JSON-RPC 2.0 messages across stdin/stdout, scrubs credentials in-flight,
 * and blocks destructive tool execution before reaching the operating system or database.
 */

import fs from 'fs';
import path from 'path';
import os from 'os';

export const FORBIDDEN_PATTERNS = [
  /rm\s+(-[rfRF]+\s+|-[rR]\s+-[fF]\s+)+(\S+)/i,
  /rm\s+(-[rfRF]+\s+|-[rR]\s+-[fF]\s+)*(\/|\/\*|~|\$HOME|\/etc|\/var|\/usr|[a-zA-Z]:[\\/])/i,
  /mkfs(\.\w+)?\s+/i,
  /dd\s+if=\S+\s+of=(\/dev\/|\/boot|\S+)/i,
  /:\(\)\s*\{\s*:\s*\|\s*:\s*&\s*\}\s*;\s*:/, // Fork bomb
  /chmod\s+(-R\s+)?777\s+\//i,
  /\bdrop\s+(table|schema|database)\b/i,
  /\btruncate\s+table\b/i,
  /(\/etc\/shadow|\/etc\/passwd|id_rsa|id_ed25519|\.aws\/credentials)/i
];

export const SECRET_PATTERNS = [
  { regex: /sk-proj-[A-Za-z0-9_\-]{20,}/g, repl: "[REDACTED_OPENAI_KEY]" },
  { regex: /sk-ant-[A-Za-z0-9_\-]{20,}/g, repl: "[REDACTED_ANTHROPIC_KEY]" },
  { regex: /AKIA[0-9A-Z]{16}/g, repl: "[REDACTED_AWS_KEY]" },
  { regex: /gh[opusr]_[A-Za-z0-9]{20,}/g, repl: "[REDACTED_GITHUB_TOKEN]" },
  { regex: /sk_live_[A-Za-z0-9]{24,}/g, repl: "[REDACTED_STRIPE_KEY]" },
  { regex: /-----BEGIN\s+([A-Z0-9_-]+\s+)?PRIVATE\s+KEY-----[\s\S]*?-----END\s+([A-Z0-9_-]+\s+)?PRIVATE\s+KEY-----/gi, repl: "[REDACTED_PRIVATE_KEY]" }
];

export function scrubSecrets(data) {
  let str = typeof data === 'string' ? data : JSON.stringify(data);
  let count = 0;
  for (const { regex, repl } of SECRET_PATTERNS) {
    const matches = str.match(regex);
    if (matches) {
      count += matches.length;
      str = str.replace(regex, repl);
    }
  }
  return {
    data: typeof data === 'string' ? str : JSON.parse(str),
    redactionCount: count
  };
}

export function evaluateToolCall(toolName, args) {
  const serialized = JSON.stringify(args || {});
  
  for (const pattern of FORBIDDEN_PATTERNS) {
    if (pattern.test(serialized)) {
      return {
        allowed: false,
        reason: `[MCP-PROXY-GUARD VETO] Destructive pattern intercepted on tool '${toolName}': ${pattern.source}`
      };
    }
  }

  return { allowed: true, reason: "Approved" };
}

export function loadLicense() {
  const btpDir = path.join(os.homedir(), '.btp');
  const licFile = path.join(btpDir, 'license.json');
  if (fs.existsSync(licFile)) {
    try {
      const data = JSON.parse(fs.readFileSync(licFile, 'utf8'));
      if (data.key) {
        const clean = data.key.trim().toLowerCase();
        const tier = clean.startsWith('btp_ent_') || clean.includes('enterprise') ? 'ENTERPRISE' : 'PRO';
        return { licensed: true, tier: tier, status: 'ACTIVE' };
      }
    } catch {}
  }
  return { licensed: false, tier: 'COMMUNITY', status: 'FREE' };
}
